"""Plan 19-06 Task 3: Langfuse eval harness for grc_reviewer.

Runs the golden-set fixtures through the live `grc_reviewer.review_diff`
function and submits a Langfuse experiment with 4 evaluator scores per
fixture.

Pre-flight contract:
  * `LANGFUSE_HOST` reachable; `/api/public/health` returns 200 + version >= 3.125.0.
  * `ANTHROPIC_API_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` set.
  * `EVAL_MODE=1` so budget_guard cap is $5.

Failure-soft: if Langfuse health check fails, the harness exits 0 with a
`::warning::` and does not block the phase. budget_guard is the hard gate.

CLI:
  python3 scripts/grc/eval_reviewer.py            # run experiment
  python3 scripts/grc/eval_reviewer.py --summary  # print latest experiment URL
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.grc import sanitize_output  # noqa: E402

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(message)s")
log = logging.getLogger("eval_reviewer")

GOLDEN_DIR = REPO_ROOT / "scripts" / "grc" / "golden_prs"
LANGFUSE_HOST_DEFAULT = "https://langfuse.tigouetheory.com"
HEALTH_TIMEOUT_SECONDS = 5
EXPERIMENT_NAME = "Squire-GRC-Reviewer baseline"


def _langfuse_health_ok(host: str) -> bool:
    """Return True if /api/public/health returns 200 OK."""
    if not host.startswith("https://"):
        log.warning("Refusing non-HTTPS Langfuse host: %s", host)
        return False
    try:
        resp = requests.get(
            f"{host.rstrip('/')}/api/public/health",
            timeout=HEALTH_TIMEOUT_SECONDS,
        )
    except requests.exceptions.RequestException as exc:
        log.warning("Langfuse health unreachable: %s", exc)
        return False
    if resp.status_code != 200:
        log.warning("Langfuse health: HTTP %s", resp.status_code)
        return False
    try:
        payload = resp.json()
    except ValueError as exc:
        log.warning("Langfuse health parse failure: %s", exc)
        return False
    log.info("Langfuse health: %s", payload)
    return payload.get("status") == "OK"


def _budget_guard_pass() -> bool:
    """Run scripts/grc/budget_guard.py with EVAL_MODE=1; return True on exit 0."""
    env = {**os.environ, "EVAL_MODE": "1"}
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "grc" / "budget_guard.py")],
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        log.error("budget_guard halt: %s", (result.stderr or result.stdout).strip())
        return False
    return True


def _load_fixtures() -> list[dict[str, Any]]:
    """Return list of {input, expected_output, metadata} from pr_*.json."""
    items: list[dict[str, Any]] = []
    for path in sorted(GOLDEN_DIR.glob("pr_*.json")):
        data = json.loads(path.read_text())
        items.append(
            {
                "input": sanitize_output.sanitize(data["diff"]),
                "expected_output": data["expected"],
                "metadata": {
                    "fixture": path.name,
                    "category": data.get("category", "unknown"),
                    "name": data.get("name", path.stem),
                },
            }
        )
    return items


def _run_review_task(*, item: dict[str, Any]) -> dict[str, Any]:
    """Task function passed to Langfuse run_experiment.

    `grc_reviewer.review_pr` accepts either a PR number or a `diff_file`
    path. We persist the in-memory diff to a tempfile and pass that path,
    avoiding any modification to grc_reviewer's public surface.
    """
    import tempfile
    from scripts.grc.grc_reviewer import review_pr

    diff = item["input"]
    with tempfile.NamedTemporaryFile("w", suffix=".diff", delete=False) as fh:
        fh.write(diff)
        diff_path = fh.name
    try:
        return review_pr(diff_file=diff_path)
    finally:
        os.unlink(diff_path)


def _expected_poam_ids(expected: dict[str, Any]) -> set[str]:
    return {p.get("poam_id", "") for p in expected.get("poams", []) if p.get("poam_id")}


def _output_poam_ids(output: dict[str, Any]) -> set[str]:
    """Pull P\\d+-\\d+ tokens out of the reviewer's poam_deltas list."""
    import re

    pattern = re.compile(r"P\d+-\d+")
    found: set[str] = set()
    for entry in output.get("poam_deltas") or []:
        if isinstance(entry, str):
            found.update(pattern.findall(entry))
        elif isinstance(entry, dict):
            pid = entry.get("poam_id") or ""
            if pid:
                found.add(pid)
    return found


def _expected_violation_patterns(expected: dict[str, Any]) -> set[str]:
    return {v.get("pattern", "") for v in expected.get("sanitization_violations", []) if v.get("pattern")}


def _output_violation_patterns(output: dict[str, Any]) -> set[str]:
    items = output.get("sanitization_violations") or []
    out: set[str] = set()
    for v in items:
        if isinstance(v, str):
            out.add(v)
        elif isinstance(v, dict) and v.get("pattern"):
            out.add(v["pattern"])
    return out


def _evaluation(name: str, value: float, comment: str):
    """Return a Langfuse Evaluation. Imported lazily so tests can mock-free."""
    from langfuse.experiment import Evaluation

    return Evaluation(name=name, value=value, comment=comment)


def control_coverage(*, input, output, expected_output, metadata, **_):
    expected_set = set(expected_output.get("controls", []))
    output_set = set(output.get("controls_touched") or [])
    if not expected_set:
        recall = 1.0 if not output_set else 0.0
    else:
        recall = len(expected_set & output_set) / len(expected_set)
    return _evaluation(
        "control_coverage",
        recall,
        f"hit={sorted(expected_set & output_set)} miss={sorted(expected_set - output_set)}",
    )


def poam_id_accuracy(*, input, output, expected_output, metadata, **_):
    expected_ids = _expected_poam_ids(expected_output)
    output_ids = _output_poam_ids(output)
    if not expected_ids and not output_ids:
        jaccard = 1.0
    else:
        union = expected_ids | output_ids
        jaccard = len(expected_ids & output_ids) / len(union) if union else 0.0
    return _evaluation(
        "poam_id_accuracy",
        jaccard,
        f"expected={sorted(expected_ids)} got={sorted(output_ids)}",
    )


def sanitization_catch_rate(*, input, output, expected_output, metadata, **_):
    expected_set = _expected_violation_patterns(expected_output)
    output_set = _output_violation_patterns(output)
    if not expected_set:
        recall = 1.0 if not output_set else 0.0
    else:
        recall = len(expected_set & output_set) / len(expected_set)
    return _evaluation(
        "sanitization_catch_rate",
        recall,
        f"expected={sorted(expected_set)} caught={sorted(output_set & expected_set)}",
    )


def hallucination_rate(*, input, output, expected_output, metadata, **_):
    expected_set = set(expected_output.get("controls", []))
    output_set = set(output.get("controls_touched") or [])
    if not output_set:
        rate = 0.0
    else:
        rate = len(output_set - expected_set) / len(output_set)
    return _evaluation(
        "hallucination_rate",
        rate,
        f"phantom={sorted(output_set - expected_set)}",
    )


def _run_experiment(host: str, run_name: str | None) -> int:
    from langfuse import get_client

    langfuse = get_client()
    items = _load_fixtures()
    log.info("Loaded %d fixtures", len(items))

    try:
        result = langfuse.run_experiment(
            name=EXPERIMENT_NAME,
            run_name=run_name,
            description="Golden set against grc_reviewer.review_diff (Plan 19-06)",
            data=items,
            task=_run_review_task,
            evaluators=[
                control_coverage,
                poam_id_accuracy,
                sanitization_catch_rate,
                hallucination_rate,
            ],
            max_concurrency=2,
            metadata={"phase": "19", "plan": "19-06"},
        )
        try:
            print(result.format())
        except Exception:  # pragma: no cover - format() shape may vary
            print(json.dumps(getattr(result, "model_dump", lambda: str(result))(), default=str, indent=2))
        return 0
    finally:
        langfuse.flush()


def _print_summary(host: str) -> int:
    """Print the project URL and a hint for the latest experiment."""
    project = os.environ.get("LANGFUSE_PROJECT_NAME", "squire")
    base = host.rstrip("/")
    print(f"Langfuse host: {base}")
    print(f"Project:       {project}")
    print(f"Open:          {base}/project/<project_id>/experiments")
    print(f"Latest experiment name: {EXPERIMENT_NAME}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Eval harness for grc_reviewer.")
    parser.add_argument("--summary", action="store_true", help="Print Langfuse links without running")
    parser.add_argument("--run-name", default=None, help="Optional Langfuse run name")
    args = parser.parse_args(argv)

    host = os.environ.setdefault("LANGFUSE_HOST", LANGFUSE_HOST_DEFAULT)
    # Raise the daily cap to $5 for eval runs and propagate to every nested
    # subprocess (notably grc_reviewer's own _budget_guard). Without this the
    # reviewer's per-call guard re-reads the default $1 cap and blocks once
    # today's ledger crosses it.
    os.environ["EVAL_MODE"] = "1"

    if args.summary:
        return _print_summary(host)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        log.error("ANTHROPIC_API_KEY not set; cannot run reviewer task")
        return 1
    if not (os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY")):
        log.error("LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY must be set")
        return 1

    if not _langfuse_health_ok(host):
        print("::warning::Langfuse health check failed; eval skipped (best-effort)", file=sys.stderr)
        return 0

    if not _budget_guard_pass():
        return 1

    return _run_experiment(host, args.run_name)


if __name__ == "__main__":
    sys.exit(main())
