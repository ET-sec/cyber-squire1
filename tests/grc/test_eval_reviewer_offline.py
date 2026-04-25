"""Plan 19-06 Task 3: offline tests for eval_reviewer.

Tests run without touching real Langfuse or Anthropic. Three things are
asserted:

  1. budget_guard halt aborts the run before any LLM call.
  2. flush() is invoked even if the experiment raises.
  3. Sanitizer fires on every fixture's input diff before the experiment data is built.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.grc import eval_reviewer  # noqa: E402


@pytest.fixture
def fake_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-test")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-test")
    monkeypatch.setenv("LANGFUSE_HOST", "https://example.invalid")


def test_budget_guard_halt_aborts_run(fake_env, monkeypatch):
    """If budget_guard exits non-zero, eval main returns 1 without calling Langfuse."""
    monkeypatch.setattr(eval_reviewer, "_langfuse_health_ok", lambda host: True)
    monkeypatch.setattr(eval_reviewer, "_budget_guard_pass", lambda: False)
    sentinel = MagicMock()
    monkeypatch.setattr(eval_reviewer, "_run_experiment", sentinel)
    rc = eval_reviewer.main([])
    assert rc == 1
    sentinel.assert_not_called()


def test_health_failure_returns_0_softfail(fake_env, monkeypatch):
    """Langfuse health failure exits 0 with a warning (best-effort)."""
    monkeypatch.setattr(eval_reviewer, "_langfuse_health_ok", lambda host: False)
    sentinel = MagicMock()
    monkeypatch.setattr(eval_reviewer, "_run_experiment", sentinel)
    rc = eval_reviewer.main([])
    assert rc == 0
    sentinel.assert_not_called()


def test_summary_mode_skips_run(fake_env, monkeypatch, capsys):
    """--summary prints links and skips the experiment path entirely."""
    sentinel = MagicMock()
    monkeypatch.setattr(eval_reviewer, "_run_experiment", sentinel)
    rc = eval_reviewer.main(["--summary"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Langfuse host:" in out
    sentinel.assert_not_called()


def test_flush_called_in_finally(fake_env, monkeypatch):
    """Even if run_experiment raises, flush() runs."""
    fake_client = MagicMock()
    fake_client.run_experiment.side_effect = RuntimeError("boom")

    monkeypatch.setattr(eval_reviewer, "_langfuse_health_ok", lambda host: True)
    monkeypatch.setattr(eval_reviewer, "_budget_guard_pass", lambda: True)
    monkeypatch.setattr(eval_reviewer, "_load_fixtures", lambda: [{"input": "x", "expected_output": {}, "metadata": {}}])

    with patch("langfuse.get_client", return_value=fake_client):
        with pytest.raises(RuntimeError, match="boom"):
            eval_reviewer._run_experiment("https://example.invalid", None)
    fake_client.flush.assert_called_once()


def test_sanitizer_fires_on_each_fixture(monkeypatch, tmp_path):
    """Each fixture's diff goes through sanitize_output.sanitize before being submitted."""
    fixture_dir = tmp_path / "golden_prs"
    fixture_dir.mkdir()
    f1 = {
        "name": "x",
        "category": "test",
        "diff": "leak: 161.35.0.184",
        "expected": {"controls": [], "poams": [], "sanitization_violations": [], "residual_risk_required": False},
    }
    (fixture_dir / "pr_001.json").write_text(json.dumps(f1))

    monkeypatch.setattr(eval_reviewer, "GOLDEN_DIR", fixture_dir)

    items = eval_reviewer._load_fixtures()
    assert len(items) == 1
    # Sanitizer must have transformed the raw IP into the redaction placeholder.
    assert "161.35.0.184" not in items[0]["input"]
    assert items[0]["metadata"]["fixture"] == "pr_001.json"


def test_control_coverage_recall():
    out = eval_reviewer.control_coverage(
        input="diff",
        output={"controls_touched": ["IR-4", "RA-5"]},
        expected_output={"controls": ["IR-4", "AC-2"]},
        metadata={},
    )
    assert out.name == "control_coverage"
    assert out.value == pytest.approx(0.5)


def test_hallucination_rate_phantoms():
    out = eval_reviewer.hallucination_rate(
        input="diff",
        output={"controls_touched": ["IR-4", "AC-99"]},
        expected_output={"controls": ["IR-4"]},
        metadata={},
    )
    assert out.name == "hallucination_rate"
    assert out.value == pytest.approx(0.5)


def test_poam_id_accuracy_jaccard():
    out = eval_reviewer.poam_id_accuracy(
        input="diff",
        output={"poam_deltas": ["P17-15 modified"]},
        expected_output={"poams": [{"poam_id": "P17-15", "change": "modified"}, {"poam_id": "P19-50", "change": "added"}]},
        metadata={},
    )
    assert out.name == "poam_id_accuracy"
    assert out.value == pytest.approx(0.5)


def test_sanitization_catch_rate_zero_when_missed():
    out = eval_reviewer.sanitization_catch_rate(
        input="diff",
        output={"sanitization_violations": []},
        expected_output={"sanitization_violations": [{"pattern": "161.35.0.184", "snippet": "..."}]},
        metadata={},
    )
    assert out.value == pytest.approx(0.0)
