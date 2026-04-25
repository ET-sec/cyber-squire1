"""Tests for budget_guard.py and spend_ledger.py.

ZERO real API calls. Admin API path is exercised via `monkeypatch` of the
`urllib.request.urlopen` callable. Ledger paths are exercised by pointing
GRC_SPEND_DB at a tmp_path SQLite file.
"""

from __future__ import annotations

import io
import os
import subprocess
import sys
import urllib.error
from pathlib import Path
from unittest.mock import patch

import pytest

# Make repo root importable for `scripts.grc.*` style imports.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.grc import budget_guard, spend_ledger  # noqa: E402


# ---------------------------------------------------------------------------
# spend_ledger pricing math
# ---------------------------------------------------------------------------

def test_pricing_math_sonnet_basic():
    # 1M input + 1M output Sonnet = $3 + $15 = $18
    cost = spend_ledger.compute_cost(
        "claude-sonnet-4-6",
        {"input_tokens": 1_000_000, "output_tokens": 1_000_000},
    )
    assert cost == pytest.approx(18.0, abs=1e-6)


def test_pricing_math_with_cache():
    # Sonnet: 100k input ($0.30) + 50k output ($0.75)
    #       + 200k cache write at 1.25x base in (200k * 3/M * 1.25 = $0.75)
    #       + 500k cache read at 0.1x base in (500k * 3/M * 0.1 = $0.15)
    # Total = 0.30 + 0.75 + 0.75 + 0.15 = $1.95
    cost = spend_ledger.compute_cost(
        "claude-sonnet-4-6",
        {
            "input_tokens": 100_000,
            "output_tokens": 50_000,
            "cache_creation_input_tokens": 200_000,
            "cache_read_input_tokens": 500_000,
        },
    )
    assert cost == pytest.approx(1.95, abs=1e-6)


def test_pricing_opus_and_haiku():
    opus_cost = spend_ledger.compute_cost(
        "claude-opus-4-7",
        {"input_tokens": 1_000_000, "output_tokens": 1_000_000},
    )
    haiku_cost = spend_ledger.compute_cost(
        "claude-haiku-4-5",
        {"input_tokens": 1_000_000, "output_tokens": 1_000_000},
    )
    assert opus_cost == pytest.approx(90.0, abs=1e-6)   # 15 + 75
    assert haiku_cost == pytest.approx(6.0, abs=1e-6)   # 1 + 5


def test_pricing_unknown_model_raises():
    with pytest.raises(KeyError):
        spend_ledger.compute_cost("gpt-4", {"input_tokens": 100})


# ---------------------------------------------------------------------------
# Ledger record + total
# ---------------------------------------------------------------------------

def test_record_call_and_total(tmp_path, monkeypatch):
    db = tmp_path / "ledger.sqlite"
    monkeypatch.setenv("GRC_SPEND_DB", str(db))

    cost1 = spend_ledger.record_call(
        "claude-sonnet-4-6",
        {"input_tokens": 100_000, "output_tokens": 0},
    )
    cost2 = spend_ledger.record_call(
        "claude-sonnet-4-6",
        {"input_tokens": 0, "output_tokens": 50_000},
    )
    total = spend_ledger.today_total_usd()
    assert db.exists()
    # 100k @ $3/M = $0.30; 50k @ $15/M = $0.75
    assert cost1 == pytest.approx(0.30, abs=1e-6)
    assert cost2 == pytest.approx(0.75, abs=1e-6)
    assert total == pytest.approx(1.05, abs=1e-6)


# ---------------------------------------------------------------------------
# budget_guard exit codes
# ---------------------------------------------------------------------------

def test_budget_guard_under_limit(tmp_path, monkeypatch, capsys):
    db = tmp_path / "ledger.sqlite"
    monkeypatch.setenv("GRC_SPEND_DB", str(db))
    monkeypatch.setenv("DAILY_LIMIT_USD", "1.00")
    monkeypatch.delenv("EVAL_MODE", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    spend_ledger.record_call(
        "claude-sonnet-4-6",
        {"input_tokens": 50_000, "output_tokens": 0},  # $0.15
    )
    rc = budget_guard.main()
    out = capsys.readouterr()
    assert rc == 0
    assert "Budget OK" in out.out
    assert "BUDGET BLOCK" not in out.err


def test_budget_guard_over_limit(tmp_path, monkeypatch, capsys):
    db = tmp_path / "ledger.sqlite"
    monkeypatch.setenv("GRC_SPEND_DB", str(db))
    monkeypatch.setenv("DAILY_LIMIT_USD", "0.10")
    monkeypatch.delenv("EVAL_MODE", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    spend_ledger.record_call(
        "claude-sonnet-4-6",
        {"input_tokens": 100_000, "output_tokens": 0},  # $0.30 > $0.10
    )
    rc = budget_guard.main()
    out = capsys.readouterr()
    assert rc == 1
    assert "BUDGET BLOCK" in out.err
    # Stdout MUST stay clean on the failure path (CI greppability).
    assert "Budget OK" not in out.out


def test_budget_guard_admin_api_404_falls_back(tmp_path, monkeypatch, capsys):
    """When admin API errors (any flavour), reviewer should use ledger."""
    db = tmp_path / "ledger.sqlite"
    monkeypatch.setenv("GRC_SPEND_DB", str(db))
    monkeypatch.setenv("DAILY_LIMIT_USD", "1.00")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-fake")
    monkeypatch.delenv("EVAL_MODE", raising=False)

    spend_ledger.record_call(
        "claude-sonnet-4-6",
        {"input_tokens": 10_000, "output_tokens": 0},  # $0.03
    )

    def fake_urlopen(req, timeout=None):
        raise urllib.error.HTTPError(
            url="x", code=404, msg="Not Found", hdrs=None, fp=io.BytesIO(b"")
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    rc = budget_guard.main()
    out = capsys.readouterr()
    assert rc == 0
    assert "Budget OK" in out.out


def test_budget_guard_never_echoes_api_key(tmp_path, monkeypatch, capsys):
    db = tmp_path / "ledger.sqlite"
    monkeypatch.setenv("GRC_SPEND_DB", str(db))
    monkeypatch.setenv("DAILY_LIMIT_USD", "1.00")
    secret = "sk-ant-do-not-leak-this"
    monkeypatch.setenv("ANTHROPIC_API_KEY", secret)

    def fake_urlopen(req, timeout=None):
        raise urllib.error.HTTPError(
            url="x", code=401, msg="Unauthorized", hdrs=None, fp=io.BytesIO(b"")
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    rc = budget_guard.main()
    out = capsys.readouterr()
    assert rc == 0
    assert secret not in out.out
    assert secret not in out.err
