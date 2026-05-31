"""Squire LangGraph assembly.

Topology:
    classify -> retrieve -> enrich -> investigate -> draft -> critique
                                                                 |
           +-------------------------------+---------------------+
           | critique.should_loop == True  | should_loop == False |
           v                               v
         draft (loop, capped)          route_severity -> END

`_should_loop(state)` exits the loop early when ANY of these fire:
  - critique_iterations >= max_critique_iterations (default 3; overridable via
    state._max_critique_iterations_override from the X-Squire-Max-Iterations
    header in 17-09),
  - total_cost_usd >= settings.max_invocation_cost_usd,
  - wall-clock since _started_at >= settings.max_invocation_seconds,
  - critique.should_loop is falsy (critic said APPROVED).

`invoke_with_trace(alert, alert_id, max_iterations_override=None)` is the
public entrypoint. It attaches a Langfuse v3 CallbackHandler, runs the graph,
and returns the final state with trace_id populated.
"""
from __future__ import annotations

import logging
import time
from typing import Any

from langgraph.graph import END, StateGraph

from .nodes.classify import classify
from .nodes.critique import critique
from .nodes.draft import draft_report
from .nodes.enrich import enrich
from .nodes.investigate import investigate
from .nodes.retrieve import retrieve
from .nodes.route import route_severity
from .settings import settings
from .state import IRState

log = logging.getLogger("squire.graph")


# ----------------------------------------------------------------------
# Conditional edge
# ----------------------------------------------------------------------


def _effective_max_iters(state: dict) -> int:
    """Return the iteration cap, honoring the header override when set."""
    override = state.get("_max_critique_iterations_override")
    if override is not None and isinstance(override, int) and override >= 0:
        return override
    try:
        return int(settings.max_critique_iterations)
    except Exception:
        return 3


def _should_loop(state: dict) -> str:
    """Conditional edge: 'draft' (loop) or 'route_severity' (exit)."""
    now = time.monotonic()
    max_iters = _effective_max_iters(state)

    iters = int(state.get("critique_iterations", 0) or 0)
    if iters >= max_iters:
        log.info("critique loop exit: iteration cap %d reached", max_iters)
        return "route_severity"

    cost = float(state.get("total_cost_usd", 0.0) or 0.0)
    if cost >= float(settings.max_invocation_cost_usd):
        log.info("critique loop exit: cost cap $%.4f reached", cost)
        return "route_severity"

    started = state.get("_started_at") or now
    elapsed = now - started
    if elapsed >= float(settings.max_invocation_seconds):
        log.info("critique loop exit: wall-clock cap %.1fs reached", elapsed)
        return "route_severity"

    if not state.get("should_loop"):
        return "route_severity"

    return "draft"


# ----------------------------------------------------------------------
# Compilation
# ----------------------------------------------------------------------


def build_graph():
    """Wire the seven-node state machine. Pure function; no IO."""
    g = StateGraph(IRState)

    g.add_node("classify", classify)
    g.add_node("retrieve", retrieve)
    g.add_node("enrich", enrich)
    g.add_node("investigate", investigate)
    g.add_node("draft", draft_report)
    g.add_node("critique", critique)
    g.add_node("route_severity", route_severity)

    g.set_entry_point("classify")
    g.add_edge("classify", "retrieve")
    g.add_edge("retrieve", "enrich")
    g.add_edge("enrich", "investigate")
    g.add_edge("investigate", "draft")
    g.add_edge("draft", "critique")
    g.add_conditional_edges(
        "critique",
        _should_loop,
        {"draft": "draft", "route_severity": "route_severity"},
    )
    g.add_edge("route_severity", END)

    return g.compile()


# ----------------------------------------------------------------------
# Public entrypoint
# ----------------------------------------------------------------------


def _make_langfuse_handler(alert_id: str):
    """Build a Langfuse v3 CallbackHandler tied to this invocation.

    v3 reads public_key/secret_key/host from LANGFUSE_* env vars automatically;
    we just pass a public_key override to tag the run.  Returns (handler, client)
    so the caller can flush + grab last_trace_id cleanly.
    """
    import os

    # Langfuse v3 reads env vars; if they aren't populated yet, populate from
    # settings so the handler can self-initialize.
    if not os.environ.get("LANGFUSE_PUBLIC_KEY"):
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key.get_secret_value()
    if not os.environ.get("LANGFUSE_SECRET_KEY"):
        os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key.get_secret_value()
    if not os.environ.get("LANGFUSE_HOST"):
        os.environ["LANGFUSE_HOST"] = settings.langfuse_host

    from langfuse import get_client
    from langfuse.langchain import CallbackHandler

    client = get_client()
    handler = CallbackHandler()
    return handler, client


def invoke_with_trace(
    alert: dict,
    alert_id: str,
    max_iterations_override: int | None = None,
) -> dict:
    """Run the graph for a single alert and return the final state.

    Args:
        alert: raw alert payload dict.
        alert_id: stable identifier (webhook body hash + timestamp).
        max_iterations_override: optional critic-loop cap override (from
            X-Squire-Max-Iterations header in 17-09).

    Returns:
        Final IRState dict. Keys include:
            draft_report (JSON string)
            severity, citations, critique_iterations
            total_tokens, total_cost_usd
            trace_id, evidence[], errors[]
            severity_routed (True when route_severity ran)
            _degraded_mode, _degraded_reason (when any backend fell back)
    """
    handler, client = _make_langfuse_handler(alert_id)
    graph = build_graph()

    initial: dict[str, Any] = {
        "alert": alert,
        "alert_id": alert_id,
        "evidence": [],
        "critique_iterations": 0,
        "total_tokens": 0,
        "total_cost_usd": 0.0,
        "citations": {},
        "errors": [],
        "_started_at": time.monotonic(),
        "_degraded_mode": False,
        "_degraded_reason": "",
    }
    if max_iterations_override is not None:
        initial["_max_critique_iterations_override"] = int(max_iterations_override)

    config: dict[str, Any] = {
        "callbacks": [handler],
        "metadata": {
            "langfuse_session_id": alert_id,
            "alert_id": alert_id,
        },
    }

    result = dict(graph.invoke(initial, config=config))

    # Flush + pull trace_id. Langfuse v3 surfaces it on handler.last_trace_id.
    try:
        if client is not None:
            client.flush()
    except Exception as e:
        log.warning("langfuse client flush failed: %s", e)

    trace_id = getattr(handler, "last_trace_id", None) or alert_id
    result["trace_id"] = trace_id

    return result
