"""Offline tests for grc_reviewer.

ZERO real Anthropic API calls. `client.messages.create` is mocked at the
module level. Subprocess calls (`gh pr diff`, `budget_guard.py`,
`gh pr comment`) are mocked so the tests never hit the network or the
filesystem ledger.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.grc import grc_reviewer  # noqa: E402

FIXTURE = REPO_ROOT / "tests" / "grc" / "fixtures" / "synthetic_diff.txt"

CLEAN_REVIEW = {
    "controls_touched": ["RA-5", "AC-2"],
    "poam_deltas": ["POAM-P19-99 added"],
    "reviewer_questions": ["Confirm AC-2 mapping accurate"],
    "residual_risk_required": False,
    "sanitization_violations": [],
}

LEAKY_REVIEW = {
    "controls_touched": ["RA-5"],
    # Note: leak embedded in a question (which is allowed in schema). The
    # sanitizer must scrub it before comment posting.
    "poam_deltas": [],
    "reviewer_questions": ["Why is 161.35.0.184 referenced in this row?"],
    "residual_risk_required": False,
    "sanitization_violations": [],
}

RR_REQUIRED_REVIEW = {
    "controls_touched": ["RA-5"],
    "poam_deltas": ["POAM-P19-99 added"],
    "reviewer_questions": [],
    "residual_risk_required": True,
    "sanitization_violations": [],
}


def _mock_response(review: dict) -> SimpleNamespace:
    """Build a fake anthropic Messages response object."""
    return SimpleNamespace(
        content=[SimpleNamespace(text=json.dumps(review))],
        usage=SimpleNamespace(
            input_tokens=100,
            output_tokens=50,
            cache_creation_input_tokens=2000,
            cache_read_input_tokens=0,
        ),
    )


@pytest.fixture(autouse=True)
def _isolate_state(tmp_path, monkeypatch):
    """Force a fresh tmp ledger DB and reset cached prompt state per test."""
    monkeypatch.setenv("GRC_SPEND_DB", str(tmp_path / "ledger.sqlite"))
    monkeypatch.delenv("INPUT_DRY_RUN", raising=False)
    # Reset the lazy cache so the on-disk reference is re-read each test.
    grc_reviewer._GRC_REFERENCE = None
    grc_reviewer._CORPUS_INDEX = None
    grc_reviewer._SYSTEM_PROMPT = None
    yield


@pytest.fixture
def fake_anthropic(monkeypatch):
    """Replace anthropic.Anthropic with a Mock whose .messages.create is
    user-controllable."""
    fake_client = MagicMock()
    fake_client.messages.create = MagicMock(return_value=_mock_response(CLEAN_REVIEW))
    factory = MagicMock(return_value=fake_client)
    monkeypatch.setattr(grc_reviewer.anthropic, "Anthropic", factory)
    return fake_client


# ---------------------------------------------------------------------------
# Test 1: budget guard subprocess called BEFORE messages.create
# ---------------------------------------------------------------------------

def test_budget_guard_runs_before_api_call(fake_anthropic, monkeypatch):
    call_order: list[str] = []

    real_run = subprocess.run

    def tracking_run(cmd, *a, **kw):
        if "budget_guard.py" in (cmd[1] if isinstance(cmd, list) and len(cmd) > 1 else ""):
            call_order.append("budget_guard")
            return SimpleNamespace(returncode=0)
        return real_run(cmd, *a, **kw)

    def tracking_create(**kwargs):
        call_order.append("messages.create")
        return _mock_response(CLEAN_REVIEW)

    monkeypatch.setattr(subprocess, "run", tracking_run)
    fake_anthropic.messages.create.side_effect = tracking_create

    review = grc_reviewer.review_pr(diff_file=str(FIXTURE), dry_run=True)
    assert review == CLEAN_REVIEW
    assert call_order == ["budget_guard", "messages.create"], call_order


# ---------------------------------------------------------------------------
# Test 2: sanitizer scrubs leaked IPs before the body is posted
# ---------------------------------------------------------------------------

def test_sanitizer_scrubs_leaks_in_comment_body(fake_anthropic, monkeypatch, capsys):
    fake_anthropic.messages.create.return_value = _mock_response(LEAKY_REVIEW)
    monkeypatch.setattr(
        subprocess, "run", lambda *a, **kw: SimpleNamespace(returncode=0)
    )

    review = grc_reviewer.review_pr(diff_file=str(FIXTURE), dry_run=True)
    grc_reviewer.post_comment(0, review, dry_run=True)
    out = capsys.readouterr().out
    assert "161.35.0.184" not in out
    assert "[REDACTED-IP]" in out


# ---------------------------------------------------------------------------
# Test 3: oversized diff skips LLM call entirely
# ---------------------------------------------------------------------------

def test_oversized_diff_skips_llm_call(fake_anthropic, tmp_path, monkeypatch):
    big = tmp_path / "big.diff"
    big.write_text("+" + ("a" * 200_000))
    monkeypatch.setattr(
        subprocess, "run", lambda *a, **kw: SimpleNamespace(returncode=0)
    )

    review = grc_reviewer.review_pr(diff_file=str(big), dry_run=True)
    assert review.get("oversized") is True
    fake_anthropic.messages.create.assert_not_called()


# ---------------------------------------------------------------------------
# Test 4: mixed-PR (non-grc paths in diff) logs warning, still proceeds
# ---------------------------------------------------------------------------

def test_mixed_pr_warns_and_proceeds(fake_anthropic, tmp_path, monkeypatch, caplog):
    mixed = tmp_path / "mixed.diff"
    mixed.write_text(
        "diff --git a/docs/grc/README.md b/docs/grc/README.md\n"
        "--- a/docs/grc/README.md\n"
        "+++ b/docs/grc/README.md\n"
        "@@ -1 +1 @@\n"
        "-old\n+new\n"
        "diff --git a/scripts/foo.py b/scripts/foo.py\n"
        "--- a/scripts/foo.py\n"
        "+++ b/scripts/foo.py\n"
        "@@ -1 +1 @@\n"
        "-old\n+new\n"
    )
    monkeypatch.setattr(
        subprocess, "run", lambda *a, **kw: SimpleNamespace(returncode=0)
    )

    with caplog.at_level("WARNING", logger="grc_reviewer"):
        review = grc_reviewer.review_pr(diff_file=str(mixed), dry_run=True)
    assert review == CLEAN_REVIEW
    assert any(
        "Mixed PR detected" in rec.message for rec in caplog.records
    ), [r.message for r in caplog.records]
    fake_anthropic.messages.create.assert_called_once()


# ---------------------------------------------------------------------------
# Test 5: residual_risk_required True -> main() returns 1
# ---------------------------------------------------------------------------

def test_residual_risk_required_exits_one(fake_anthropic, monkeypatch, capsys):
    fake_anthropic.messages.create.return_value = _mock_response(RR_REQUIRED_REVIEW)
    monkeypatch.setattr(
        subprocess, "run", lambda *a, **kw: SimpleNamespace(returncode=0)
    )

    rc = grc_reviewer.main(["--diff-file", str(FIXTURE), "--offline"])
    assert rc == 1


# ---------------------------------------------------------------------------
# Test 6: --diff-file flag bypasses `gh pr diff` and prints to stdout (dry run)
# ---------------------------------------------------------------------------

def test_diff_file_flag_bypasses_gh_pr_diff(fake_anthropic, monkeypatch, capsys):
    real_run = subprocess.run
    seen_cmds: list[list[str]] = []

    def tracking_run(cmd, *a, **kw):
        seen_cmds.append(list(cmd) if isinstance(cmd, list) else [str(cmd)])
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(subprocess, "run", tracking_run)

    review = grc_reviewer.review_pr(diff_file=str(FIXTURE), dry_run=True)
    grc_reviewer.post_comment(0, review, dry_run=True)
    out = capsys.readouterr().out

    # gh pr diff and gh pr comment must NOT have been invoked.
    flat = [c for sub in seen_cmds for c in sub]
    assert "diff" not in flat or "gh" not in flat, seen_cmds
    assert not any("gh" in c and "comment" in c for c in flat), seen_cmds
    # Output should include the rendered structured comment.
    assert "GRC Reviewer" in out
    assert review == CLEAN_REVIEW


# ---------------------------------------------------------------------------
# Test 7: model escalates to Opus on oversized-but-not-skipped diff
# ---------------------------------------------------------------------------

def test_model_escalates_on_large_diff(fake_anthropic, tmp_path, monkeypatch):
    """60KB diff -> escalate to claude-opus-4-8 (still under 100KB skip)."""
    large = tmp_path / "large.diff"
    large.write_text(
        "diff --git a/docs/grc/foo.md b/docs/grc/foo.md\n"
        "--- a/docs/grc/foo.md\n"
        "+++ b/docs/grc/foo.md\n"
        "@@ -1 +1 @@\n"
        + ("+" + "x" * 60_000)
    )
    monkeypatch.setattr(
        subprocess, "run", lambda *a, **kw: SimpleNamespace(returncode=0)
    )
    grc_reviewer.review_pr(diff_file=str(large), dry_run=True)
    kwargs = fake_anthropic.messages.create.call_args.kwargs
    assert kwargs["model"] == "claude-opus-4-8"


# ---------------------------------------------------------------------------
# Test 8: argparse rejects providing both pr_number and --diff-file
# ---------------------------------------------------------------------------

def test_cli_rejects_both_pr_and_diff_file(monkeypatch):
    with pytest.raises(SystemExit):
        grc_reviewer.main(["123", "--diff-file", str(FIXTURE), "--offline"])


# ---------------------------------------------------------------------------
# Test 9: argparse rejects providing neither
# ---------------------------------------------------------------------------

def test_cli_rejects_neither_pr_nor_diff_file(monkeypatch):
    with pytest.raises(SystemExit):
        grc_reviewer.main([])
