"""Squire LangGraph shared state schema.

IRState is the TypedDict every graph node reads/writes. LangGraph merges node
return dicts into the running state via reducer semantics; total=False lets
individual nodes return only the keys they set.

Fields are documented inline. Keys prefixed with a single underscore are
graph-internal telemetry (degraded mode, start time) and do not appear in the
outward-facing report surface.
"""
from __future__ import annotations

from typing import Any, TypedDict


class IRState(TypedDict, total=False):
    # ------------------------------------------------------------------
    # Alert inputs
    # ------------------------------------------------------------------
    alert: dict[str, Any]
    """Raw alert payload posted to /webhook/alert (n8n, Falco, Langfuse, manual)."""

    alert_id: str
    """Stable identifier used for dedup + Langfuse trace name."""

    # ------------------------------------------------------------------
    # Classification (classify node)
    # ------------------------------------------------------------------
    classification: dict[str, Any]
    """Output of classify node: incident_type, severity_guess, confidence, mitre_tactics, rationale."""

    severity: str
    """Normalized severity LOW|MEDIUM|HIGH|CRITICAL promoted from classification.severity_guess."""

    # ------------------------------------------------------------------
    # Retrieval + enrichment
    # ------------------------------------------------------------------
    grc_chunks: list[dict[str, Any]]
    """Top-k ir_chunks hits from GRCRetriever, shape: [{chunk_id, source_file, content, score, ...}]."""

    threat_intel: dict[str, Any]
    """Tavily threat-intel enrichment envelope. Keys: results, query, enrichment_skipped (optional)."""

    # ------------------------------------------------------------------
    # Report generation (draft + critique loop, 17-08b)
    # ------------------------------------------------------------------
    draft_report: str
    """Serialized draft incident report (markdown + embedded JSON citations block)."""

    critique: str
    """Most recent critique node output; drives the critique loop."""

    critique_iterations: int
    """Number of critique cycles executed so far; capped in 17-08b."""

    should_loop: bool
    """Set by critique node, read by graph conditional edge. True -> back to draft."""

    severity_routed: bool
    """Set by route_severity after routing is decided; used by tests + /healthz reports."""

    # ------------------------------------------------------------------
    # Citations + evidence
    # ------------------------------------------------------------------
    citations: dict[str, list[str]]
    """Structured citations by framework, e.g. {'csf_2_0': ['RS.MA-03'], 'mitre_attack': ['T1078.004']}."""

    evidence: list[dict[str, Any]]
    """Per-node telemetry rows: {'node', 'elapsed_ms', 'backend', 'output', 'cost_usd', 'tokens'}."""

    # ------------------------------------------------------------------
    # Accounting
    # ------------------------------------------------------------------
    total_tokens: int
    """Running token total across every backend invocation in this trace."""

    total_cost_usd: float
    """Running USD cost estimate using COST_PER_1K in llm.py."""

    trace_id: str
    """Langfuse trace id (set by the FastAPI middleware in 17-09)."""

    errors: list[str]
    """Node-level error messages; populated when a node partially fails but the graph continues."""

    # ------------------------------------------------------------------
    # Graph-internal telemetry (single-underscore prefix)
    # ------------------------------------------------------------------
    _started_at: float
    """Monotonic start time, used to compute total wall-clock duration at END."""

    _degraded_mode: bool
    """True when any backend invocation in this trace fell back from the primary."""

    _degraded_reason: str
    """Human-readable reason, e.g. 'fell_back_from_api_to_ollama'."""

    _max_critique_iterations_override: int
    """17-09 may override the default critique cap via X-Squire-Max-Iterations header."""
