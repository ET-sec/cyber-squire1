"""LangGraph nodes for the Squire IR assistant.

Every node is a pure function `node(state: IRState) -> dict`. Nodes return a
partial state dict that LangGraph merges into the running IRState. Node-level
errors go into `state["errors"]` rather than raising; the orchestration layer
in 17-08b decides when to short-circuit.
"""
from __future__ import annotations

from .classify import classify  # noqa: F401
from .critique import critique  # noqa: F401
from .draft import draft_report  # noqa: F401
from .enrich import enrich  # noqa: F401
from .investigate import investigate  # noqa: F401
from .retrieve import retrieve  # noqa: F401
from .route import route_severity  # noqa: F401

__all__ = [
    "classify",
    "critique",
    "draft_report",
    "enrich",
    "investigate",
    "retrieve",
    "route_severity",
]
