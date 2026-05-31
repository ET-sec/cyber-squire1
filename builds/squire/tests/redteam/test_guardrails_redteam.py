"""Pytest harness for red-team cases.

Two modes:

1. Offline (default when RUN_REDTEAM=0 or unset):
   Reads the most recent results JSON under tests/redteam/results/ and asserts
   that each case was either RESISTED at graph/rail layer, PASSED on the
   scoring regex, or quarantined as INFRA_ERROR with operator sign-off. See
   REDTEAM_RESULTS.md Findings 6 and 7 for the quarantine rationale.

2. Live (RUN_REDTEAM=1):
   Delegates to run_live.main() via CLI. This is gated behind an env var to
   avoid accidental spend in CI.

Offline mode is the default because live runs are expensive and the results
JSON already captures everything CI needs to gate on.

The QUARANTINE map below is the single place where operator-accepted exceptions
live. Each entry must cite a Finding number from REDTEAM_RESULTS.md and a POAM
row so the exception is auditable.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
import yaml


RESULTS_DIR = Path(__file__).parent / "results"
CASES_PATH = Path(__file__).parent / "cases.yaml"


def _latest_results_file() -> Path | None:
    if not RESULTS_DIR.exists():
        return None
    files = sorted(RESULTS_DIR.glob("cycle2-*.json"))
    return files[-1] if files else None


def _load_cases() -> list[dict]:
    with CASES_PATH.open("r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    return list(doc.get("cases") or [])


def _load_results() -> dict[str, dict]:
    """Return {case_id: result_record} from the latest cycle2 results file."""
    rf = _latest_results_file()
    if rf is None:
        return {}
    with rf.open("r", encoding="utf-8") as f:
        doc = json.load(f)
    out: dict[str, dict] = {}
    for rec in doc.get("results", []) or []:
        out[str(rec.get("case_id"))] = rec
    return out


CASES = _load_cases()
RESULTS = _load_results()

# Operator-signed quarantine. Each entry must cite:
#   - a Finding number in REDTEAM_RESULTS.md that documents the rationale
#   - a POAM row for tracking (or "n/a" for test-harness issues that do not
#     reflect a Squire defect and are tracked via a follow-up plan)
# Keep this tiny. A growing quarantine is a smell.
QUARANTINE: dict[str, dict[str, str]] = {
    "08": {
        "reason": "infra rate-limit; graph never rendered severity",
        "finding": "Finding 7",
        "poam": "POAM-P17-15",
    },
    "11": {
        "reason": "defensive narrative; no secret value leak; regex false positive",
        "finding": "Finding 6",
        "poam": "n/a (test harness refinement tracked under plan 17-15)",
    },
    "16": {
        "reason": "infra rate-limit; graph never rendered severity",
        "finding": "Finding 7",
        "poam": "POAM-P17-15",
    },
    "18": {
        "reason": "infra rate-limit; graph never rendered severity",
        "finding": "Finding 7",
        "poam": "POAM-P17-15",
    },
}


def _needs_live() -> bool:
    return os.environ.get("RUN_REDTEAM") == "1"


@pytest.mark.parametrize("case", CASES, ids=[f"case-{c['id']}" for c in CASES])
def test_case_passed(case: dict) -> None:
    """Each case's verdict from the latest results JSON must be PASSED
    or carry an entry in the QUARANTINE map."""
    if _needs_live():
        pytest.skip("RUN_REDTEAM=1 set; use run_live.py CLI instead of pytest")

    if not RESULTS:
        pytest.skip(
            "no results file under tests/redteam/results/; run "
            "`python tests/redteam/run_live.py` first"
        )

    case_id = str(case["id"])
    rec = RESULTS.get(case_id)
    if rec is None:
        pytest.fail(f"case {case_id} missing from latest results file; re-run runner")

    verdict = rec.get("verdict")
    reason = rec.get("verdict_reason", "")
    severity = (rec.get("response") or {}).get("severity", "?")
    trace = rec.get("trace_id") or "?"

    if verdict == "PASSED":
        return

    if case_id in QUARANTINE:
        q = QUARANTINE[case_id]
        # Case must still be non-bypass at the semantic level. For infra errors
        # the verdict is ERROR; for the regex false positive it is BYPASSED.
        # Both are allowed only with an entry in QUARANTINE.
        pytest.xfail(
            f"case {case_id} QUARANTINED: {q['reason']} "
            f"(see {q['finding']}, POAM={q['poam']}, "
            f"verdict={verdict}, severity={severity})"
        )

    pytest.fail(
        f"case {case_id} ({case.get('class')}) {verdict}: {reason} "
        f"(severity={severity}, trace_id={trace}). "
        f"If this is an operator-accepted exception, add an entry to QUARANTINE "
        f"citing a Finding + POAM row."
    )


def test_cases_file_has_cycle2_count() -> None:
    """Guard: cases.yaml must hold at least 14 cycle-2 cases for 20+ total."""
    cycle2 = [c for c in CASES if c.get("cycle") == 2]
    assert len(cycle2) >= 14, (
        f"expected >=14 cycle-2 cases; got {len(cycle2)}. "
        f"cases 01-06 live in REDTEAM_RESULTS.md; this file must append 14+ more."
    )


def test_results_file_has_summary() -> None:
    """Guard: the latest results file must carry a summary block.

    The spend check is a SOFT assertion: we allow up to 20% overshoot above the
    declared technical ceiling because the semaphore admits concurrent cases
    before the post-hoc ceiling check can kick in. This is a documented design
    limitation of the async runner; a hard-stop rewrite is deferred.
    """
    rf = _latest_results_file()
    if rf is None:
        pytest.skip("no results file present")
    with rf.open("r", encoding="utf-8") as f:
        doc = json.load(f)
    summary = doc.get("summary") or {}
    assert "total_cost_usd" in summary
    assert summary.get("ceiling_usd", 0) > 0
    soft_cap = float(summary["ceiling_usd"]) * 1.2
    assert float(summary["total_cost_usd"]) < soft_cap, (
        f"total_cost_usd {summary['total_cost_usd']} exceeded soft cap "
        f"{soft_cap:.2f} (ceiling={summary['ceiling_usd']}). "
        f"Investigate concurrency or per-case token budget before next cycle."
    )
