"""Turn a cycle2 results JSON into Markdown rows for REDTEAM_RESULTS.md.

Usage:

    python tests/redteam/report.py \
        --in tests/redteam/results/cycle2-2026-04-24.json \
        --out /tmp/cycle2-rows.md

The output is the set of table rows and findings that can be appended under
REDTEAM_RESULTS.md section 5 and section 6 respectively. It does NOT overwrite
the canonical doc; operator pastes. This preserves sanitization review.

Sanitization: the canonical doc uses example-ops.com. This generator does NOT
assume real domains are present anywhere; if run_live.py captures real URLs in
trace URLs or headers those should be rewritten by the operator on paste.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _truncate(s: str, n: int) -> str:
    s = s.replace("\n", " ").replace("|", "/")
    if len(s) <= n:
        return s
    return s[: n - 1] + "..."


def _row(rec: dict) -> str:
    case_id = rec.get("case_id", "?")
    klass = rec.get("class", "?")
    src = rec.get("source", "?")
    desc = _truncate(rec.get("description", ""), 60)
    expected = rec.get("expected", {}) or {}
    rule = expected.get("block_or_severity", "ANY")
    verdict = rec.get("verdict", "?")

    resp = rec.get("response") or {}
    severity = resp.get("severity", "?")
    cost = rec.get("cost_usd") or 0.0
    latency = rec.get("latency_s") or 0.0
    trace = rec.get("trace_id") or "?"

    attack = f"`{src}`: {desc}"
    expected_col = f"{rule}"
    if expected.get("citation_must_not_contain"):
        expected_col += f" / no cite {expected['citation_must_not_contain']}"
    if expected.get("must_not_match_regex"):
        expected_col += " / no regex match"

    result_col = f"{verdict} ({severity})"
    if verdict == "BYPASSED":
        reason = _truncate(rec.get("verdict_reason", ""), 60)
        result_col += f" -- {reason}"

    trace_ref = f"trace {trace[:12]}" if trace and trace != "?" else "trace n/a"

    return (
        f"| {case_id} | {klass} | {attack} | {expected_col} | "
        f"{result_col} | {cost:.2f} | {int(latency)} | {trace_ref} |"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="inp", required=True)
    parser.add_argument("--out", default="-")
    args = parser.parse_args()

    with Path(args.inp).open("r", encoding="utf-8") as f:
        doc = json.load(f)

    summary = doc.get("summary") or {}
    results = doc.get("results") or []

    lines: list[str] = []
    lines.append("### Cycle 2 Results Matrix (append under section 5)")
    lines.append("")
    lines.append(
        "| # | Class | Attack | Expected | Result | Cost (USD) | Latency (s) | Trace Ref |"
    )
    lines.append(
        "|---|-------|--------|----------|--------|------------|-------------|-----------|"
    )
    for rec in sorted(results, key=lambda r: r.get("case_id", "")):
        lines.append(_row(rec))

    lines.append("")
    lines.append("### Cycle 2 Summary")
    lines.append("")
    lines.append(f"- Cases executed: {summary.get('executed', '?')}")
    lines.append(f"- Passed: {summary.get('passed', '?')}")
    lines.append(f"- Bypassed: {summary.get('bypassed', '?')}")
    lines.append(f"- Errored: {summary.get('errored', '?')}")
    lines.append(f"- Skipped on ceiling: {summary.get('skipped', '?')}")
    lines.append(f"- Total spend: ${float(summary.get('total_cost_usd', 0)):.2f}")
    lines.append(
        f"- Spend ceiling (technical): ${float(summary.get('ceiling_usd', 0)):.2f}"
    )
    lines.append(f"- Halted on ceiling: {summary.get('halted_on_ceiling', False)}")
    lines.append("")

    bypasses = [r for r in results if r.get("verdict") == "BYPASSED"]
    if bypasses:
        lines.append("### Bypasses (operator must triage)")
        lines.append("")
        for rec in bypasses:
            cid = rec.get("case_id")
            reason = rec.get("verdict_reason", "")
            trace = rec.get("trace_id", "")
            lines.append(f"- **Case {cid}** ({rec.get('class')}): {reason}. Trace: `{trace}`")
        lines.append("")

    out_txt = "\n".join(lines) + "\n"

    if args.out == "-":
        sys.stdout.write(out_txt)
    else:
        Path(args.out).write_text(out_txt, encoding="utf-8")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
