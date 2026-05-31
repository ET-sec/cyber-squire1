"""Unit tests for cost_ceiling.consult() decision logic.

These tests stub today_spend_usd() so the decision tree can be exercised
without a live Postgres.
"""
from __future__ import annotations

import os

os.environ.setdefault("CD_DB_USER", "x")
os.environ.setdefault("CD_DB_PASS", "x")
os.environ.setdefault("CD_DB_NAME", "x")
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "x")
os.environ.setdefault("LANGFUSE_SECRET_KEY", "x")
os.environ.setdefault("ANTHROPIC_API_KEY", "x")
os.environ.setdefault("SQUIRE_WEBHOOK_TOKEN", "x")

from squire import cost_ceiling  # noqa: E402
from squire.settings import settings  # noqa: E402


def test_no_breach_below_ceiling(monkeypatch):
    monkeypatch.setattr(cost_ceiling, "today_spend_usd", lambda: 0.0)
    monkeypatch.setattr(settings, "anthropic_daily_ceiling_usd", 5.0, raising=False)
    monkeypatch.setattr(settings, "cost_breach_mode", "ollama", raising=False)
    action = cost_ceiling.consult()
    assert action.breach is False
    assert action.backend_override is None


def test_refuse_mode_sets_no_override(monkeypatch):
    monkeypatch.setattr(cost_ceiling, "today_spend_usd", lambda: 10.0)
    monkeypatch.setattr(settings, "anthropic_daily_ceiling_usd", 5.0, raising=False)
    monkeypatch.setattr(settings, "cost_breach_mode", "refuse", raising=False)
    action = cost_ceiling.consult()
    assert action.breach is True
    assert action.mode == "refuse"
    assert action.backend_override is None
    assert "daily_cost_ceiling_reached" in action.reason


def test_ollama_mode_forces_backend_override(monkeypatch):
    monkeypatch.setattr(cost_ceiling, "today_spend_usd", lambda: 10.0)
    monkeypatch.setattr(settings, "anthropic_daily_ceiling_usd", 5.0, raising=False)
    monkeypatch.setattr(settings, "cost_breach_mode", "ollama", raising=False)
    action = cost_ceiling.consult()
    assert action.breach is True
    assert action.mode == "ollama"
    assert action.backend_override == "ollama"
    assert "degraded_to_ollama" in action.reason


def test_warn_only_mode_allows_through(monkeypatch):
    monkeypatch.setattr(cost_ceiling, "today_spend_usd", lambda: 10.0)
    monkeypatch.setattr(settings, "anthropic_daily_ceiling_usd", 5.0, raising=False)
    monkeypatch.setattr(settings, "cost_breach_mode", "warn_only", raising=False)
    action = cost_ceiling.consult()
    assert action.breach is True
    assert action.mode == "warn_only"
    assert action.backend_override is None


def test_unknown_mode_falls_through_to_warn(monkeypatch):
    monkeypatch.setattr(cost_ceiling, "today_spend_usd", lambda: 10.0)
    monkeypatch.setattr(settings, "anthropic_daily_ceiling_usd", 5.0, raising=False)
    monkeypatch.setattr(settings, "cost_breach_mode", "explode_please", raising=False)
    action = cost_ceiling.consult()
    assert action.breach is True
    # Unknown modes should be treated as warn_only -- no override, no refuse.
    assert action.backend_override is None


def test_today_spend_failopen_on_db_error(monkeypatch):
    """today_spend_usd should return 0.0 when the DB is unreachable."""

    class _Broken:
        def __enter__(self):
            raise RuntimeError("no db")

        def __exit__(self, *a):  # pragma: no cover
            return False

    def _broken_connect(*a, **kw):
        raise RuntimeError("no db")

    monkeypatch.setattr(cost_ceiling.psycopg, "connect", _broken_connect)
    assert cost_ceiling.today_spend_usd() == 0.0
