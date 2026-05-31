"""Postgres persistence for Squire investigations.

Writes one ir_investigations row per /alert invocation plus N ir_evidence rows
(per-node telemetry captured during graph traversal) and M ir_citations rows
(from the post-validated citations dict).

Design notes:
  - Uses raw psycopg (not SQLAlchemy ORM) so failures surface immediately and
    schema drift is loud. The schema is small and stable.
  - All writes run inside a single transaction. Partial failure rolls back the
    whole investigation row so operators never see orphaned evidence.
  - `load_alert(alert_id)` returns the most recent stored alert_payload for the
    /replay endpoint.
  - cost_usd column matches the ir_investigations schema from migration 001
    (plain NUMERIC; not total_cost_usd).

Schema reference (migration 001):
  ir_investigations(id, alert_id, alert_signature, alert_source, alert_payload,
                    severity, status, trace_id, dedup_of, report, cost_usd,
                    tokens_prompt, tokens_completion, model_profile, latency_ms,
                    created_at, updated_at)
  ir_evidence(id, investigation_id, kind, source, content, collected_at)
  ir_citations(id, investigation_id, citation_type, source_path, chunk_id,
               excerpt, relevance_score, validated, created_at)
"""
from __future__ import annotations

import json
import logging
from typing import Any

import psycopg
from psycopg.types.json import Jsonb

from .dedup import signature as alert_signature
from .settings import settings

log = logging.getLogger("squire.persist")


def _conninfo() -> str:
    return (
        f"host={settings.cd_db_host} port={settings.cd_db_port} "
        f"user={settings.cd_db_user} password={settings.cd_db_pass.get_secret_value()} "
        f"dbname={settings.cd_db_name}"
    )


def _parse_report(raw: Any) -> dict[str, Any]:
    """Graph stores draft_report as a JSON string; tolerate a dict too."""
    if isinstance(raw, dict):
        return raw
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {"raw": str(raw)[:4000]}


def save_investigation(
    alert_id: str,
    state: dict[str, Any],
    duration_ms: int,
    alert_payload: dict[str, Any] | None = None,
    source: str = "webhook",
) -> str | None:
    """Persist one investigation with evidence + citations.

    Returns the UUID string of the inserted ir_investigations row, or None on
    failure (errors are logged; the /alert response path should not be killed
    by a persistence hiccup).
    """
    payload = alert_payload if alert_payload is not None else state.get("alert", {}) or {}
    report = _parse_report(state.get("draft_report"))
    citations = state.get("citations") or report.get("citations") or {}
    evidence_rows = state.get("evidence") or []
    severity = state.get("severity") or report.get("severity") or "UNKNOWN"
    trace_id = state.get("trace_id")
    cost = float(state.get("total_cost_usd", 0.0) or 0.0)
    tokens = int(state.get("total_tokens", 0) or 0)
    sig = alert_signature(payload)

    # Split tokens 50/50 when the state only carries the aggregate count.
    tokens_prompt = tokens // 2
    tokens_completion = tokens - tokens_prompt

    try:
        with psycopg.connect(_conninfo(), connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO ir_investigations
                        (alert_id, alert_signature, alert_source, alert_payload,
                         severity, status, trace_id, report, cost_usd,
                         tokens_prompt, tokens_completion, model_profile, latency_ms)
                    VALUES
                        (%s, %s, %s, %s, %s, 'open', %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        alert_id,
                        sig,
                        source,
                        Jsonb(payload),
                        severity,
                        trace_id,
                        Jsonb(report),
                        cost,
                        tokens_prompt,
                        tokens_completion,
                        settings.squire_llm_backend,
                        duration_ms,
                    ),
                )
                inv_id = cur.fetchone()[0]

                if evidence_rows:
                    cur.executemany(
                        """
                        INSERT INTO ir_evidence
                            (investigation_id, kind, source, content)
                        VALUES (%s, %s, %s, %s)
                        """,
                        [
                            (
                                inv_id,
                                str(ev.get("node") or ev.get("kind") or "node"),
                                str(ev.get("backend") or ev.get("source") or "graph"),
                                Jsonb(ev),
                            )
                            for ev in evidence_rows
                        ],
                    )

                # Flatten citations dict -> rows
                flat_cites = []
                for fw, codes in (citations or {}).items():
                    for c in codes or []:
                        flat_cites.append((inv_id, "framework", f"{fw}:{c}", c, True))
                if flat_cites:
                    cur.executemany(
                        """
                        INSERT INTO ir_citations
                            (investigation_id, citation_type, source_path, excerpt, validated)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        flat_cites,
                    )
            conn.commit()
            return str(inv_id)
    except Exception as e:
        log.exception("save_investigation failed for alert_id=%s: %s", alert_id, e)
        return None


def load_alert(alert_id: str) -> dict[str, Any] | None:
    """Fetch the most recent alert_payload for a given alert_id (for /replay)."""
    try:
        with psycopg.connect(_conninfo(), connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT alert_payload FROM ir_investigations "
                    "WHERE alert_id = %s ORDER BY created_at DESC LIMIT 1",
                    (alert_id,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                payload = row[0]
                if isinstance(payload, (bytes, str)):
                    return json.loads(payload)
                return payload or {}
    except Exception as e:
        log.warning("load_alert(%s) failed: %s", alert_id, e)
        return None
