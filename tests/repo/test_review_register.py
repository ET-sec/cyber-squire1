"""Fixture tests for scripts/repo/review_register.py.

Four of the five cases build a throwaway register under ``tmp_path`` and pass an
explicit environment into ``main``, so nothing here depends on the shell that
ran pytest and nothing here can be turned green by a stray TRIGGER_ variable.

The fifth case is the link test and it reads the two real files. A register item
whose repository variable is never passed into the workflow can never fire, and
nothing else in the system would ever say so: the register would look complete,
the job would run nightly, and the item would sit dark forever. That is the
failure this file exists to prevent, so it is written first.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.repo import review_register  # noqa: E402

REGISTER = REPO_ROOT / "docs" / "REVIEW_REGISTER.yaml"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "drift-check.yml"
JOB = "review-register"


def base_items() -> list[dict]:
    """Two complete items, as plain dicts so a test can bend one of them."""
    return [
        {
            "id": "first_event",
            "flag": "TRIGGER_FIRST",
            "what": "The first thing.",
            "why_now": "Because the first event happened.",
            "affects": ["docs/first.md"],
            "action": "Do the first thing.",
        },
        {
            "id": "second_event",
            "flag": "TRIGGER_SECOND",
            "what": "The second thing.",
            "why_now": "Because the second event happened.",
            "affects": ["docs/second.md", "scripts/second.py"],
            "action": "Do the second thing.",
        },
    ]


def write_register(tmp_path: Path, items: list[dict]) -> Path:
    path = tmp_path / "register.yaml"
    path.write_text(
        yaml.safe_dump({"version": 1, "items": items}, sort_keys=False),
        encoding="utf-8",
    )
    return path


def run(register: Path, env: dict[str, str], fmt: str = "text") -> int:
    return review_register.main(
        ["--register", str(register), "--format", fmt], env=env
    )


# --------------------------------------------------------------------------
# 5. The link test: every register flag reaches the workflow
# --------------------------------------------------------------------------
def test_every_register_flag_is_wired_into_the_workflow():
    register = yaml.safe_load(REGISTER.read_text(encoding="utf-8"))
    items = register["items"]
    assert len(items) >= 5, "the register must carry at least five event items"

    flags = {item["flag"] for item in items}
    assert all(flag.startswith("TRIGGER_") for flag in flags)

    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    assert JOB in workflow["jobs"], f"{WORKFLOW.name} has no {JOB} job"

    job = workflow["jobs"][JOB]
    passed: set[str] = set()
    for step in job["steps"]:
        passed.update(step.get("env", {}))

    missing = sorted(flags - passed)
    assert not missing, (
        f"register flags never passed into the {JOB} job, so they can never "
        f"fire: {', '.join(missing)}"
    )

    # The job must also stay free of the cloud identity the drift job needs,
    # or a Terraform failure could take the register down with it.
    assert "needs" not in job
    assert "permissions" not in job


# --------------------------------------------------------------------------
# 1. Nothing set
# --------------------------------------------------------------------------
def test_no_flag_set_prints_nothing_and_exits_zero(tmp_path, capsys):
    register = write_register(tmp_path, base_items())
    code = run(register, {})
    assert code == 0
    assert capsys.readouterr().out == ""


# --------------------------------------------------------------------------
# 2. One flag set
# --------------------------------------------------------------------------
def test_one_flag_set_prints_exactly_that_block(tmp_path, capsys):
    register = write_register(tmp_path, base_items())
    code = run(register, {"TRIGGER_SECOND": "true"})
    out = capsys.readouterr().out

    assert code == 0
    assert "second_event (TRIGGER_SECOND)" in out
    assert "Do the second thing." in out
    assert "scripts/second.py" in out
    assert "first_event" not in out

    report = json.loads(
        _capture_json(register, {"TRIGGER_SECOND": "true"}, capsys)
    )
    assert report["count"] == 1
    assert [item["id"] for item in report["fired"]] == ["second_event"]


def _capture_json(register: Path, env: dict[str, str], capsys) -> str:
    run(register, env, fmt="json")
    return capsys.readouterr().out


# --------------------------------------------------------------------------
# 3. False and empty are not fired
# --------------------------------------------------------------------------
def test_false_and_empty_do_not_fire(tmp_path, capsys):
    register = write_register(tmp_path, base_items())
    code = run(register, {"TRIGGER_FIRST": "false", "TRIGGER_SECOND": ""})
    assert code == 0
    assert capsys.readouterr().out == ""


# --------------------------------------------------------------------------
# 4. A malformed item is a configuration error
# --------------------------------------------------------------------------
def test_item_without_a_flag_is_exit_two(tmp_path, capsys):
    items = base_items()
    del items[0]["flag"]
    register = write_register(tmp_path, items)

    code = run(register, {"TRIGGER_SECOND": "true"})
    captured = capsys.readouterr()

    assert code == 2
    assert "flag" in captured.err
    # A configuration error must not leak a half-evaluated alert.
    assert captured.out == ""
