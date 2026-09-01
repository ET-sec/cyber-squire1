"""Squire dual judge evaluation harness for plan 17-12.

Runs each canonical alert twice through the live /alert endpoint:
  - X-Squire-Max-Iterations: 0  (critique loop disabled, control)
  - X-Squire-Max-Iterations: 3  (critique loop enabled, treatment)

Each candidate pair is scored independently by two Anthropic judges:
  primary   = claude-fable-5
  secondary = claude-opus-5

Five dimensions per candidate (0 to 10):
  accuracy, completeness, citation_quality, specificity, actionability

A dimension is declared "improved by critique" only when both judges produce
a positive delta greater than 0.5 (directional agreement). Criterion #5 from
the Phase 17 roadmap passes when at least three of five dimensions show
agreement in at least six of ten cases.

Inputs:
  ENV  SQUIRE_ENDPOINT       default https://squire.example-ops.com/alert
  ENV  SQUIRE_WEBHOOK_TOKEN  required
  ENV  ANTHROPIC_API_KEY     required

Outputs:
  builds/squire/tests/eval/results/<case_id>.json
  docs/grc/SQUIRE_SELF_CRITIQUE_EVAL.md   (final summary doc)

Operator command:
  doppler run --project "$DOPPLER_PROJECT" --config "$DOPPLER_CONFIG" -- \
    python builds/squire/tests/eval/critique_eval.py
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import httpx
import yaml
from anthropic import Anthropic

ENDPOINT = os.environ.get("SQUIRE_ENDPOINT", "https://squire.example-ops.com/alert")
TOKEN = os.environ.get("SQUIRE_WEBHOOK_TOKEN", "")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
HERE = Path(__file__).resolve().parent
RESULTS_DIR = HERE / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

JUDGES = [
    {"name": "fable-5", "model": "claude-fable-5"},
    {"name": "opus-5", "model": "claude-opus-5"},
]

DIMENSIONS = ["accuracy", "completeness", "citation_quality", "specificity", "actionability"]

JUDGE_SYSTEM = (
    "You are an incident response quality judge. Score two candidate IR reports "
    "across five dimensions on a 0 to 10 scale: accuracy (severity and incident "
    "type correct for the alert), completeness (observed, hypotheses_tested, and "
    "recommended_actions each substantive), citation_quality (CSF, MITRE, and "
    "OWASP codes valid and relevant), specificity (actions concrete and scoped, "
    "not generic), actionability (an analyst could execute without more context). "
    "Return strict JSON of the form: "
    '{"report_a": {"accuracy": <int>, "completeness": <int>, "citation_quality": <int>, '
    '"specificity": <int>, "actionability": <int>, "notes": "..."}, '
    '"report_b": {...}}. Score independently, do not reveal which is which."'
)


def invoke_alert(alert: dict[str, Any], max_iters: int) -> dict[str, Any]:
    if not TOKEN:
        raise SystemExit("SQUIRE_WEBHOOK_TOKEN missing in env")
    resp = httpx.post(
        ENDPOINT,
        headers={
            "Content-Type": "application/json",
            "X-Squire-Token": TOKEN,
            "X-Squire-Max-Iterations": str(max_iters),
        },
        json={"alert": alert},
        timeout=120.0,
    )
    resp.raise_for_status()
    return resp.json()


def judge_pair(model: str, alert: dict, report_a: dict, report_b: dict) -> dict:
    if not API_KEY:
        raise SystemExit("ANTHROPIC_API_KEY missing in env")
    client = Anthropic(api_key=API_KEY)
    payload = {"alert": alert, "report_a_no_critique": report_a, "report_b_with_critique": report_b}
    msg = client.messages.create(
        model=model,
        max_tokens=2048,
        temperature=0.0,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": json.dumps(payload)[:12000]}],
    )
    text = msg.content[0].text.strip().strip("`")
    if text.startswith("json"):
        text = text[4:].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        return {"error": f"parse_error: {exc}", "raw": text[:500]}


def directional_agreement(per_judge_scores: list[dict]) -> dict[str, dict]:
    """For each dimension, compute deltas across judges and check directional agreement."""
    out: dict[str, dict] = {}
    for dim in DIMENSIONS:
        deltas = []
        for js in per_judge_scores:
            a_val = float(js.get("report_a", {}).get(dim, 0) or 0)
            b_val = float(js.get("report_b", {}).get(dim, 0) or 0)
            deltas.append(round(b_val - a_val, 2))
        signs = ["+" if d > 0.5 else ("-" if d < -0.5 else "0") for d in deltas]
        agree_improved = all(s == "+" for s in signs)
        out[dim] = {
            "deltas": deltas,
            "signs": signs,
            "both_agree_improved": agree_improved,
        }
    return out


def main() -> int:
    cases = yaml.safe_load((HERE / "canonical_alerts.yaml").read_text())
    all_results: list[dict] = []
    for case in cases:
        cid = case["id"]
        print(f"[{cid}] running control (iters=0) and treatment (iters=3)")
        control = invoke_alert(case["alert"], 0)
        treatment = invoke_alert(case["alert"], 3)

        per_judge = []
        for j in JUDGES:
            scores = judge_pair(j["model"], case["alert"], control.get("report"), treatment.get("report"))
            per_judge.append({"judge": j["name"], **scores})

        agreement = directional_agreement(per_judge)
        rec = {
            "case": case,
            "control": control,
            "treatment": treatment,
            "judges": per_judge,
            "agreement": agreement,
        }
        all_results.append(rec)
        (RESULTS_DIR / f"{cid}.json").write_text(json.dumps(rec, indent=2))

    counts = {d: sum(1 for r in all_results if r["agreement"][d]["both_agree_improved"]) for d in DIMENSIONS}
    dimensions_passing = sum(1 for d in DIMENSIONS if counts[d] >= 6)
    overall_pass = dimensions_passing >= 3

    lines = [
        "# Squire Self Critique Evaluation (Dual Judge)",
        "",
        f"Run date: {time.strftime('%Y-%m-%d')}",
        "Cases: 10 canonical alerts",
        "Conditions: max_iters=0 (control), max_iters=3 (treatment)",
        f"Judges: {JUDGES[0]['model']} (primary), {JUDGES[1]['model']} (secondary)",
        "",
        "## Dual Judge Directional Agreement",
        "",
        "| Dimension | Cases agreed (of 10) | Verdict |",
        "|-----------|----------------------|---------|",
    ]
    for d in DIMENSIONS:
        verdict = "improved" if counts[d] >= 6 else ("inconclusive" if counts[d] >= 3 else "not improved")
        lines.append(f"| {d} | {counts[d]} | {verdict} |")

    lines += [
        "",
        "## Criterion #5 Verdict",
        "",
        f"Dimensions with both judge agreement: {dimensions_passing} of 5",
        f"Result: {'PASS' if overall_pass else 'FAIL'}",
        "",
        "## Per Case Agreement",
        "",
        "| Case ID | Family | Expected | Per dimension signs (a / c / cq / sp / act) |",
        "|---------|--------|----------|---------------------------------------------|",
    ]
    for r in all_results:
        c = r["case"]
        signs = " ".join("".join(r["agreement"][d]["signs"]) for d in DIMENSIONS)
        lines.append(f"| {c['id']} | {c['family']} | {c['expected_severity']} | {signs} |")

    out_doc = Path("/Users/et/cyber-squire-ops/docs/grc/SQUIRE_SELF_CRITIQUE_EVAL.md")
    out_doc.write_text("\n".join(lines) + "\n")
    print(f"wrote {out_doc}")
    print(f"verdict: {'PASS' if overall_pass else 'FAIL'} ({dimensions_passing}/5 dimensions)")
    return 0 if overall_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
