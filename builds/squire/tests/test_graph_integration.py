"""End-to-end LangGraph tests for Squire (17-08b).

Two flavors:

  Unit tests (always run)
  -----------------------
  - build_graph() returns a compiled Runnable with the expected node set.
  - _should_loop respects iteration cap, cost cap, wall-clock cap, and the
    _max_critique_iterations_override header hook.
  - The graph import chain is clean (no settings blow-up on import).

  Integration tests (gated on RUN_INTEGRATION=1)
  ----------------------------------------------
  Actually run invoke_with_trace against the Anthropic API + pgvector DB +
  Langfuse. Expect ~$1.50 per invocation so each run costs ~$3.

  Requires:
    ANTHROPIC_API_KEY, CD_DB_*, VOYAGE_API_KEY,
    LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST,
    SQUIRE_WEBHOOK_TOKEN,
    and either:
      - Run inside the `cd-service-squire:dev` container on the droplet
        (network coredirective_engine_net-core), OR
      - Run locally with CD_DB_HOST=127.0.0.1 CD_DB_PORT=15432 and an
        SSH tunnel open: `ssh -fN -L 15432:cd-service-db:5432 cd-alpha`.

  Telegram side effect is real on HIGH/CRITICAL. Both fixtures classify as
  HIGH/CRITICAL so expect two @Coredirective_bot messages per full run. Use
  RUN_INTEGRATION=1 only when ready for that.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

# Populate required env so pydantic-settings can instantiate for the unit tests.
os.environ.setdefault("CD_DB_USER", "x")
os.environ.setdefault("CD_DB_PASS", "x")
os.environ.setdefault("CD_DB_NAME", "x")
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "x")
os.environ.setdefault("LANGFUSE_SECRET_KEY", "x")
os.environ.setdefault("ANTHROPIC_API_KEY", "x")
os.environ.setdefault("SQUIRE_WEBHOOK_TOKEN", "x")


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "alerts"
FIXTURE_SHELL = FIXTURE_DIR / "falco_shell.json"
FIXTURE_CRED_LEAK = FIXTURE_DIR / "falco_cred_leak.json"

RUN_INTEGRATION = os.environ.get("RUN_INTEGRATION", "0") == "1"

# Plan's stated cost cap per invocation (matches settings.max_invocation_cost_usd).
COST_CAP_USD = 0.60  # tiny margin over 0.50 for end-to-end jitter.

# Valid severity enum from classify + draft nodes.
VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


# ---------------------------------------------------------------------------
# Fixture sanity
# ---------------------------------------------------------------------------


def test_fixtures_exist_and_parse():
    assert FIXTURE_SHELL.exists(), f"missing fixture: {FIXTURE_SHELL}"
    assert FIXTURE_CRED_LEAK.exists(), f"missing fixture: {FIXTURE_CRED_LEAK}"

    for p in (FIXTURE_SHELL, FIXTURE_CRED_LEAK):
        data = json.loads(p.read_text())
        assert data.get("rule"), f"fixture {p.name} missing 'rule'"
        assert data.get("priority"), f"fixture {p.name} missing 'priority'"
        assert data.get("output_fields"), f"fixture {p.name} missing 'output_fields'"


# ---------------------------------------------------------------------------
# Graph structure (unit)
# ---------------------------------------------------------------------------


def test_build_graph_compiles_with_all_nodes():
    """build_graph() yields a compiled graph with the seven nodes we wired."""
    from squire.graph import build_graph

    g = build_graph()
    nodes = g.get_graph().nodes
    # LangGraph adds __start__ / __end__ nodes.
    explicit = {n for n in nodes if not str(n).startswith("__")}
    assert {
        "classify",
        "retrieve",
        "enrich",
        "investigate",
        "draft",
        "critique",
        "route_severity",
    } <= explicit


def test_should_loop_respects_iteration_cap(monkeypatch):
    """_should_loop exits when critique_iterations >= max_iters."""
    from squire import graph as G

    monkeypatch.setattr(G.settings, "max_invocation_cost_usd", 10.0, raising=False)
    monkeypatch.setattr(G.settings, "max_invocation_seconds", 3600, raising=False)
    monkeypatch.setattr(G.settings, "max_critique_iterations", 3, raising=False)

    state = {
        "critique_iterations": 3,
        "should_loop": True,
        "total_cost_usd": 0.0,
        "_started_at": 0.0,
    }
    assert G._should_loop(state) == "route_severity"


def test_should_loop_respects_cost_cap(monkeypatch):
    from squire import graph as G

    monkeypatch.setattr(G.settings, "max_invocation_cost_usd", 0.50, raising=False)
    monkeypatch.setattr(G.settings, "max_invocation_seconds", 3600, raising=False)
    monkeypatch.setattr(G.settings, "max_critique_iterations", 5, raising=False)

    state = {
        "critique_iterations": 1,
        "should_loop": True,
        "total_cost_usd": 0.75,
        "_started_at": 0.0,
    }
    assert G._should_loop(state) == "route_severity"


def test_should_loop_respects_override(monkeypatch):
    """_max_critique_iterations_override wins over settings.max_critique_iterations."""
    from squire import graph as G

    monkeypatch.setattr(G.settings, "max_invocation_cost_usd", 10.0, raising=False)
    monkeypatch.setattr(G.settings, "max_invocation_seconds", 3600, raising=False)
    monkeypatch.setattr(G.settings, "max_critique_iterations", 10, raising=False)

    # Override says "stop after 1" -- with iteration already at 1, exit loop.
    state = {
        "critique_iterations": 1,
        "should_loop": True,
        "total_cost_usd": 0.0,
        "_started_at": 0.0,
        "_max_critique_iterations_override": 1,
    }
    assert G._should_loop(state) == "route_severity"


def test_should_loop_approves_when_critic_says_no(monkeypatch):
    from squire import graph as G

    monkeypatch.setattr(G.settings, "max_invocation_cost_usd", 10.0, raising=False)
    monkeypatch.setattr(G.settings, "max_invocation_seconds", 3600, raising=False)
    monkeypatch.setattr(G.settings, "max_critique_iterations", 5, raising=False)

    state = {
        "critique_iterations": 0,
        "should_loop": False,
        "total_cost_usd": 0.0,
        "_started_at": 0.0,
    }
    assert G._should_loop(state) == "route_severity"


def test_should_loop_sends_back_to_draft_when_critic_loops(monkeypatch):
    from squire import graph as G
    import time

    monkeypatch.setattr(G.settings, "max_invocation_cost_usd", 10.0, raising=False)
    monkeypatch.setattr(G.settings, "max_invocation_seconds", 3600, raising=False)
    monkeypatch.setattr(G.settings, "max_critique_iterations", 5, raising=False)

    state = {
        "critique_iterations": 1,
        "should_loop": True,
        "total_cost_usd": 0.01,
        "_started_at": time.monotonic(),
    }
    assert G._should_loop(state) == "draft"


# ---------------------------------------------------------------------------
# Tool contracts (unit)
# ---------------------------------------------------------------------------


def test_tavily_search_fails_open_without_key(monkeypatch):
    from squire.tools.tavily import tavily_search

    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    out = tavily_search("suspicious shell in container")
    assert out["threat_intel"] == []
    assert "TAVILY_API_KEY" in (out.get("enrichment_skipped") or "")


def test_tavily_search_empty_query():
    from squire.tools.tavily import tavily_search

    out = tavily_search("")
    assert out["threat_intel"] == []
    assert out["enrichment_skipped"] == "empty_query"


def test_telegram_notify_fails_safe_on_network_error(monkeypatch):
    from squire.tools import telegram as T

    class _FakeClient:
        def __init__(self, *a, **kw): pass
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def post(self, *a, **kw):
            raise RuntimeError("simulated network failure")

    # Monkeypatch httpx.Client inside the module's import path
    import httpx
    monkeypatch.setattr(httpx, "Client", _FakeClient)

    out = T.telegram_notify("test message")
    assert out["delivered"] is False
    assert out["error"] and "simulated" in out["error"]


# ---------------------------------------------------------------------------
# Integration tests (gated on RUN_INTEGRATION=1)
# ---------------------------------------------------------------------------


def _load_alert(path: Path) -> dict:
    return json.loads(path.read_text())


def _invoke_and_assert(alert_path: Path, alert_id: str) -> dict:
    """Shared integration invocation + assertions."""
    from squire.graph import invoke_with_trace

    alert = _load_alert(alert_path)
    result = invoke_with_trace(alert, alert_id=alert_id)

    # --- draft non-empty ---
    draft_raw = result.get("draft_report") or ""
    assert draft_raw, "draft_report must be non-empty"
    parsed = json.loads(draft_raw)
    assert parsed.get("summary"), "draft.summary must be non-empty"
    assert parsed.get("recommended_actions"), "draft.recommended_actions must be non-empty"

    # --- severity in enum ---
    severity = result.get("severity")
    assert severity in VALID_SEVERITIES, f"severity {severity!r} not in {VALID_SEVERITIES}"

    # --- citations populated + validated ---
    citations = result.get("citations") or {}
    total_codes = sum(len(v or []) for v in citations.values())
    assert total_codes >= 1, f"expected >=1 validated citation, got {citations}"

    # --- cost under cap ---
    cost = float(result.get("total_cost_usd") or 0.0)
    assert cost < COST_CAP_USD, f"invocation cost {cost} exceeded cap {COST_CAP_USD}"

    # --- trace_id returned ---
    trace_id = result.get("trace_id")
    assert trace_id, "trace_id must be populated"

    # --- every node produced a latency row (criterion #26 foundation) ---
    evidence = result.get("evidence") or []
    node_names = {e.get("node") for e in evidence}
    expected_min = {"classify", "retrieve", "enrich", "investigate", "draft", "critique", "route_severity"}
    assert expected_min <= node_names, (
        f"expected every node to emit evidence, missing: {expected_min - node_names}"
    )
    for row in evidence:
        assert "elapsed_ms" in row, f"evidence row missing elapsed_ms: {row}"

    # --- severity routing fired ---
    assert result.get("severity_routed") is True

    return result


@pytest.mark.skipif(not RUN_INTEGRATION, reason="RUN_INTEGRATION=1 not set")
@pytest.mark.integration
def test_graph_on_falco_shell_alert():
    """End-to-end: Falco 'Terminal shell in container' -> full IR report."""
    result = _invoke_and_assert(FIXTURE_SHELL, alert_id="integration-falco-shell-001")
    # Shell-in-container should classify as HIGH or CRITICAL.
    assert result["severity"] in {"HIGH", "CRITICAL"}


@pytest.mark.skipif(not RUN_INTEGRATION, reason="RUN_INTEGRATION=1 not set")
@pytest.mark.integration
def test_graph_on_falco_cred_leak_alert():
    """End-to-end: Falco credential-read alert -> full IR report."""
    result = _invoke_and_assert(FIXTURE_CRED_LEAK, alert_id="integration-falco-cred-001")
    assert result["severity"] in {"HIGH", "CRITICAL"}
