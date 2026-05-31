"""enrich node - Tavily threat intel enrichment.

Runs a Tavily search against the classifier's rationale + alert indicators.
Gracefully degrades to an empty threat_intel envelope if TAVILY_API_KEY is
absent (Wave 4 responsibility) or Tavily is unreachable.
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any

log = logging.getLogger("squire.nodes.enrich")


TAVILY_SEARCH_URL = "https://api.tavily.com/search"


def _build_enrichment_query(state: dict) -> str:
    """Compose a Tavily query that pulls recent threat-intel context.

    Prioritizes high-signal fields: IoCs (IPs, hashes), rule names, classifier
    rationale. Uses a short query because Tavily ranks recency + authority.
    """
    classification = state.get("classification") or {}
    alert = state.get("alert") or {}

    terms: list[str] = []

    # Prefer explicit IoCs if the alert carries them.
    for k in ("ioc", "iocs", "indicator", "indicators", "hash", "sha256", "ip", "src_ip", "dst_ip", "domain"):
        v = alert.get(k)
        if v:
            if isinstance(v, (list, tuple)):
                terms.extend(str(x) for x in v if x)
            else:
                terms.append(str(v))

    rule = alert.get("rule") or alert.get("rule_name") or alert.get("title")
    if rule:
        terms.append(str(rule))

    it = classification.get("incident_type")
    if it:
        terms.append(str(it))

    if not terms:
        # Last resort: classifier rationale or a small alert digest
        rationale = classification.get("rationale") or ""
        if rationale:
            terms.append(rationale[:160])
        else:
            terms.append(" ".join(f"{k}={v}" for k, v in alert.items() if isinstance(v, (str, int, float)))[:200])

    # Scope to threat intel context
    terms.append("threat intel recent")
    return " ".join(terms)[:400]


def _call_tavily(query: str, api_key: str, timeout: float = 15.0) -> dict[str, Any]:
    import httpx

    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": 5,
        "include_answer": True,
    }
    with httpx.Client(timeout=timeout) as c:
        r = c.post(TAVILY_SEARCH_URL, json=payload)
        r.raise_for_status()
        return r.json()


def enrich(state: dict) -> dict:
    """Tavily threat intel enrichment node.

    Returns:
        Partial state update with threat_intel envelope + evidence row. Always
        writes a threat_intel dict even when skipped/failed so downstream nodes
        can rely on the key being present.
    """
    t0 = time.monotonic()
    api_key = os.environ.get("TAVILY_API_KEY")
    query = _build_enrichment_query(state)

    if not api_key:
        skip_envelope = {
            "results": [],
            "query": query,
            "enrichment_skipped": "TAVILY_API_KEY not configured",
        }
        evidence_row = {
            "node": "enrich",
            "elapsed_ms": int((time.monotonic() - t0) * 1000),
            "skipped": "TAVILY_API_KEY not configured",
        }
        return {
            "threat_intel": skip_envelope,
            "evidence": list(state.get("evidence") or []) + [evidence_row],
        }

    try:
        data = _call_tavily(query, api_key)
    except Exception as e:
        log.warning("enrich: Tavily call failed: %s", e)
        err_envelope = {
            "results": [],
            "query": query,
            "enrichment_skipped": f"tavily_call_failed: {e!s}",
        }
        evidence_row = {
            "node": "enrich",
            "elapsed_ms": int((time.monotonic() - t0) * 1000),
            "error": str(e),
        }
        return {
            "threat_intel": err_envelope,
            "errors": list(state.get("errors") or []) + [f"enrich_failed: {e!s}"],
            "evidence": list(state.get("evidence") or []) + [evidence_row],
        }

    elapsed_ms = int((time.monotonic() - t0) * 1000)
    results = data.get("results") or []
    envelope = {
        "query": query,
        "answer": data.get("answer"),
        "results": [
            {
                "title": r.get("title"),
                "url": r.get("url"),
                "score": r.get("score"),
                "snippet": (r.get("content") or "")[:500],
                "published_date": r.get("published_date"),
            }
            for r in results[:5]
        ],
    }
    evidence_row = {
        "node": "enrich",
        "elapsed_ms": elapsed_ms,
        "result_count": len(envelope["results"]),
        "has_answer": bool(envelope.get("answer")),
        "query": query,
    }
    return {
        "threat_intel": envelope,
        "evidence": list(state.get("evidence") or []) + [evidence_row],
    }
