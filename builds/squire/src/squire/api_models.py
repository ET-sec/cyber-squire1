"""Pydantic request/response models for the Squire FastAPI surface (17-09)."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AlertRequest(BaseModel):
    """POST /alert body.

    `alert` is the raw payload from whichever upstream posted it (Falco,
    Datadog, n8n, a human demo). Squire does not validate its shape; the
    classify node is tolerant.
    """

    alert: dict[str, Any]
    alert_id: str | None = None
    source: str | None = Field(default=None, description="falco | datadog | webhook | manual")


class AlertResponse(BaseModel):
    """Successful /alert response body."""

    alert_id: str
    severity: str
    report: dict[str, Any]
    citations: dict[str, list[str]] = Field(default_factory=dict)
    trace_id: str | None = None
    trace_url: str | None = None
    duration_ms: int = 0
    cost_usd: float = 0.0

    # Dedup signaling (criterion #18)
    deduplicated: bool = False
    original_alert_id: str | None = None
    original_trace_id: str | None = None

    # Degraded-mode signaling (criterion #19)
    degraded_mode: bool = False
    degraded_reason: str | None = None
    footer: str | None = None
