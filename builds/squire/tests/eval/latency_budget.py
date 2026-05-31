"""Per node latency budget enforcement for plan 17-12.

Triggers N synthetic alerts against the live endpoint, then reads the
ir_evidence table to compute observed p95 per node. Compares observed values
against the target budgets in latency_budget.yaml. Exits non zero when any
node breaches its budget.

Inputs:
  ENV  SQUIRE_ENDPOINT          default https://squire.example-ops.com/alert
  ENV  SQUIRE_WEBHOOK_TOKEN     required
  ENV  SQUIRE_PG_CONNINFO       libpq style; route via SSH tunnel for safety
  ENV  LATENCY_N                default 50

Outputs:
  docs/grc/SQUIRE_LATENCY_BUDGET.md
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import httpx
import psycopg
import yaml

ENDPOINT = os.environ.get("SQUIRE_ENDPOINT", "https://squire.example-ops.com/alert")
TOKEN = os.environ.get("SQUIRE_WEBHOOK_TOKEN", "")
CONNINFO = os.environ.get("SQUIRE_PG_CONNINFO", "")
HERE = Path(__file__).resolve().parent
BUDGET = yaml.safe_load((HERE / "latency_budget.yaml").read_text())
FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "alerts" / "falco_shell.json"


def trigger(n: int) -> None:
    if not TOKEN:
        raise SystemExit("SQUIRE_WEBHOOK_TOKEN missing")
    fixture = json.loads(FIXTURE_PATH.read_text()) if FIXTURE_PATH.exists() else {
        "rule": "Terminal shell in container",
        "output_fields": {"user_name": "root", "container.image.repository": "svc-db", "proc.cmdline": "sh -i"},
    }
    for i in range(n):
        httpx.post(
            ENDPOINT,
            headers={"X-Squire-Token": TOKEN, "Content-Type": "application/json"},
            json={"alert": fixture, "alert_id": f"lat-{int(time.time())}-{i}"},
            timeout=90,
        )


def gather_latencies() -> dict[str, list[int]]:
    if not CONNINFO:
        raise SystemExit("SQUIRE_PG_CONNINFO missing; open SSH tunnel and inject via doppler run")
    out: dict[str, list[int]] = {}
    with psycopg.connect(CONNINFO) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT e.kind, (e.content->>'elapsed_ms')::int
            FROM ir_evidence e
            JOIN ir_investigations i ON e.investigation_id = i.id
            WHERE i.alert_id LIKE 'lat-%'
              AND e.content ? 'elapsed_ms'
            """
        )
        for kind, ms in cur.fetchall():
            if ms is not None:
                out.setdefault(kind, []).append(int(ms))
    return out


def p95(xs: list[int]) -> int:
    if not xs:
        return 0
    xs = sorted(xs)
    idx = max(0, int(round(len(xs) * 0.95)) - 1)
    return xs[idx]


def main() -> int:
    n = int(os.environ.get("LATENCY_N", "50"))
    print(f"triggering {n} synthetic invocations")
    trigger(n)
    lat = gather_latencies()

    lines = [
        "# Squire Per Node Latency Budget",
        "",
        f"Sample size: {n} synthetic invocations",
        "",
        "| Node | Target p95 ms | Observed p95 ms | Samples | Status |",
        "|------|----------------|------------------|---------|--------|",
    ]
    breaches: list[str] = []
    for node, budget_ms in BUDGET.items():
        samples = lat.get(node, [])
        observed = p95(samples)
        status = "PASS"
        if samples and observed > budget_ms:
            status = "BREACH"
            breaches.append(f"{node}: observed {observed} ms exceeds budget {budget_ms} ms")
        lines.append(f"| {node} | {budget_ms} | {observed} | {len(samples)} | {status} |")

    lines.append("")
    lines.append("## Breaches")
    lines.append("(none)" if not breaches else "\n".join(f"- {b}" for b in breaches))
    lines.append("")
    lines.append("## Criterion #26 verdict")
    lines.append("PASS" if not breaches else "FAIL: see breaches above")

    out = Path("/Users/et/cyber-squire-ops/docs/grc/SQUIRE_LATENCY_BUDGET.md")
    out.write_text("\n".join(lines) + "\n")
    print(f"wrote {out}; breaches: {len(breaches)}")
    return 0 if not breaches else 2


if __name__ == "__main__":
    sys.exit(main())
