"""Tavily threat-intel HTTP wrapper.

Fail-open design: when TAVILY_API_KEY is absent or Tavily is unreachable, returns
an envelope with `threat_intel: []` and an `enrichment_skipped` reason so
downstream nodes can still run (criterion: "graceful degradation on external
service failure").

Used by the `investigate` node in 17-08b. The enrich node shipped in 17-08a
already inlines its own Tavily call for the enrichment step; this tool exists
so the investigate node can pull additional targeted intel mid-graph without
re-running the full enrichment query.
"""
from __future__ import annotations

import logging
import os
from typing import Any

log = logging.getLogger("squire.tools.tavily")

TAVILY_SEARCH_URL = "https://api.tavily.com/search"
DEFAULT_TIMEOUT = 15.0


def tavily_search(
    query: str,
    *,
    api_key: str | None = None,
    max_results: int = 5,
    search_depth: str = "basic",
    include_answer: bool = True,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Run a Tavily search. Always returns a dict with a `threat_intel` list.

    Args:
        query: free-text query string.
        api_key: optional override; defaults to env TAVILY_API_KEY.
        max_results: Tavily result cap (default 5).
        search_depth: "basic" or "advanced".
        include_answer: ask Tavily for a synthesized answer.
        timeout: HTTP timeout in seconds.

    Returns:
        {
            "threat_intel": [...],          # per-result list, shape below
            "query": "...",                 # the query actually sent
            "answer": "<string or None>",   # Tavily synthesized answer when available
            "enrichment_skipped": "<reason>" # only set when we skipped / failed
        }

        Per-result shape:
            {"title", "url", "score", "snippet", "published_date"}

    Fail-open: missing key, network error, non-2xx response all return an
    envelope with threat_intel=[] and enrichment_skipped set to a reason string.
    The caller never needs to try/except.
    """
    q = (query or "").strip()
    key = api_key or os.environ.get("TAVILY_API_KEY")

    if not q:
        return {
            "threat_intel": [],
            "query": "",
            "answer": None,
            "enrichment_skipped": "empty_query",
        }

    if not key:
        return {
            "threat_intel": [],
            "query": q,
            "answer": None,
            "enrichment_skipped": "TAVILY_API_KEY not configured",
        }

    try:
        import httpx  # local import; httpx is in the pinned deps

        payload = {
            "api_key": key,
            "query": q,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_answer": include_answer,
        }
        with httpx.Client(timeout=timeout) as client:
            r = client.post(TAVILY_SEARCH_URL, json=payload)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        log.warning("tavily_search failed: %s", e)
        return {
            "threat_intel": [],
            "query": q,
            "answer": None,
            "enrichment_skipped": f"tavily_call_failed: {e!s}",
        }

    results = data.get("results") or []
    return {
        "threat_intel": [
            {
                "title": r.get("title"),
                "url": r.get("url"),
                "score": r.get("score"),
                "snippet": (r.get("content") or "")[:500],
                "published_date": r.get("published_date"),
            }
            for r in results[:max_results]
        ],
        "query": q,
        "answer": data.get("answer"),
    }
