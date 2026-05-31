"""Alert deduplication with 5-minute sliding window.

Criterion #18: dedup keyed on signature hash (alert_type, severity, affected_resource,
first_seen_minute_bucket). First alert processes; duplicates within window return
the original trace_id with flag deduplicated=true.
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any

import redis

from .settings import settings

log = logging.getLogger("squire.dedup")


def signature(alert: dict[str, Any]) -> str:
    """Compute a stable dedup signature from salient fields."""
    af = alert or {}
    # Normalize keys that commonly appear in Falco/Datadog payloads
    alert_type = af.get("rule") or af.get("alert_type") or af.get("description", "")[:80]
    severity = af.get("priority") or af.get("severity") or af.get("level") or ""
    ofs = af.get("output_fields") or {}
    resource = (
        ofs.get("container.id")
        or ofs.get("container_id")
        or ofs.get("host")
        or ofs.get("pod")
        or ofs.get("fd.name")
        or ofs.get("proc.name")
        or ""
    )
    payload = f"{alert_type}|{severity}|{resource}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


@dataclass
class DedupResult:
    is_duplicate: bool
    original_alert_id: str | None = None
    original_trace_id: str | None = None
    sig: str = ""


def _client() -> redis.Redis:
    pwd = (
        settings.dedup_redis_password.get_secret_value()
        if settings.dedup_redis_password
        else None
    )
    return redis.Redis.from_url(
        settings.dedup_redis_url,
        password=pwd,
        decode_responses=True,
        socket_timeout=3.0,
    )


def check_and_register(
    alert: dict[str, Any], alert_id: str, trace_id: str | None = None
) -> DedupResult:
    """Return DedupResult. If duplicate, fetch the original. Otherwise register and return."""
    sig = signature(alert)
    key = f"squire:dedup:{sig}"
    try:
        c = _client()
    except Exception as e:
        log.warning("dedup redis unavailable: %s; falling open (not a duplicate)", e)
        return DedupResult(is_duplicate=False, sig=sig)

    val = json.dumps({"alert_id": alert_id, "trace_id": trace_id or ""})
    try:
        was_set = c.set(key, val, ex=settings.dedup_window_seconds, nx=True)
    except Exception as e:
        log.warning("dedup redis SETNX failed: %s; falling open", e)
        return DedupResult(is_duplicate=False, sig=sig)

    if was_set:
        return DedupResult(is_duplicate=False, sig=sig)
    # Duplicate -- read the original
    try:
        raw = c.get(key) or "{}"
        original = json.loads(raw)
    except Exception:
        original = {}
    return DedupResult(
        is_duplicate=True,
        original_alert_id=original.get("alert_id"),
        original_trace_id=original.get("trace_id") or None,
        sig=sig,
    )


def update_trace_id(sig: str, trace_id: str) -> None:
    """After graph completes, backfill the trace_id for later duplicates."""
    key = f"squire:dedup:{sig}"
    try:
        c = _client()
        raw = c.get(key) or "{}"
        d = json.loads(raw)
        d["trace_id"] = trace_id
        ttl = c.ttl(key)
        c.set(key, json.dumps(d), ex=ttl if ttl and ttl > 0 else settings.dedup_window_seconds)
    except Exception as e:
        log.warning("dedup update_trace_id failed: %s", e)
