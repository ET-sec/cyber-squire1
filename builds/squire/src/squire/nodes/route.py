"""route_severity node - final node before END.

Responsibilities:
  1. Normalize severity (defensive, in case earlier nodes left it unset).
  2. On HIGH or CRITICAL, send a Telegram notification via the n8n webhook.
     Failure is non-fatal: it's logged to state.errors and the graph still exits.
  3. Always set state.severity_routed = True so the FastAPI layer can confirm
     the graph ran end-to-end rather than short-circuiting on an error.

By the time this node runs, the draft is already persisted in state; this node
does not re-enter the drafting surface. Keep it cheap.
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

from ..tools import telegram_notify

log = logging.getLogger("squire.nodes.route")


_HIGH_CRIT = {"HIGH", "CRITICAL"}


def _build_telegram_message(state: dict) -> str:
    """Concise Telegram message. Limited to ~1000 chars so we don't hit Telegram caps."""
    alert = state.get("alert") or {}
    classification = state.get("classification") or {}
    severity = state.get("severity", "UNKNOWN")
    alert_id = state.get("alert_id", "unknown")

    # Prefer parsed draft summary over truncated JSON.
    draft_raw = state.get("draft_report") or ""
    summary = ""
    try:
        parsed = json.loads(draft_raw) if draft_raw else {}
        summary = str(parsed.get("summary") or "")[:300]
    except Exception:
        summary = draft_raw[:300]

    rule = alert.get("rule") or alert.get("rule_name") or alert.get("title") or "alert"
    incident_type = classification.get("incident_type") or "uncategorized"

    # Flatten citations into a compact list (top 3 per framework).
    citations = state.get("citations") or {}
    cite_lines: list[str] = []
    for fw, codes in citations.items():
        if codes:
            cite_lines.append(f"{fw}: {', '.join(codes[:3])}")
    cite_block = "\n".join(cite_lines[:4])

    msg = (
        f"[Squire] {severity} incident: {rule}\n"
        f"Type: {incident_type}\n"
        f"Alert ID: {alert_id}\n"
    )
    if summary:
        msg += f"Summary: {summary}\n"
    if cite_block:
        msg += f"Citations:\n{cite_block}\n"
    return msg[:1000]


def route_severity(state: dict) -> dict:
    """Severity routing node.

    On HIGH/CRITICAL: POST a compact incident card to Telegram via n8n.
    On LOW/MEDIUM: no side effect.
    Always records an evidence row with outcome + any error.
    """
    t0 = time.monotonic()

    severity = str(state.get("severity", "")).strip().upper() or "UNKNOWN"
    delivered = False
    delivery_error: str | None = None

    if severity in _HIGH_CRIT:
        message = _build_telegram_message(state)
        result = telegram_notify(message)
        delivered = bool(result.get("delivered"))
        delivery_error = result.get("error")
        if not delivered:
            log.warning(
                "route_severity: Telegram delivery failed severity=%s error=%s",
                severity,
                delivery_error,
            )

    evidence_row = {
        "node": "route_severity",
        "elapsed_ms": int((time.monotonic() - t0) * 1000),
        "severity": severity,
        "telegram_attempted": severity in _HIGH_CRIT,
        "telegram_delivered": delivered,
    }
    if delivery_error:
        evidence_row["telegram_error"] = delivery_error
    evidence = list(state.get("evidence") or []) + [evidence_row]

    update: dict[str, Any] = {
        "severity": severity,
        "severity_routed": True,
        "evidence": evidence,
    }
    if delivery_error:
        update["errors"] = list(state.get("errors") or []) + [
            f"telegram_delivery_failed: {delivery_error}"
        ]
    return update
