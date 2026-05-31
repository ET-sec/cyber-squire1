"""retrieve node - pgvector RAG over ir_chunks.

Wraps GRCRetriever (shipped in 17-07). Builds a query from the classification
+ alert summary, pulls top-k chunks, serializes them into state["grc_chunks"]
as dicts (LangGraph state prefers plain dicts over dataclasses for
pickle-cheap persistence).
"""
from __future__ import annotations

import logging
import time
from typing import Any

from ..retrievers.grc_retriever import GRCRetriever

log = logging.getLogger("squire.nodes.retrieve")


DEFAULT_TOP_K = 5


def _build_query(state: dict) -> str:
    """Compose a natural-language query from alert + classification context.

    The retriever uses semantic search, so the query should read like a
    question an analyst would ask. We blend the classifier's incident_type +
    rationale with any raw alert fields that carry signal (source, summary,
    rule_name).
    """
    classification = state.get("classification") or {}
    alert = state.get("alert") or {}

    parts: list[str] = []
    incident_type = classification.get("incident_type")
    severity = classification.get("severity_guess") or state.get("severity")
    rationale = classification.get("rationale")

    if incident_type:
        parts.append(f"Incident type: {incident_type}")
    if severity:
        parts.append(f"Severity: {severity}")
    if rationale:
        parts.append(rationale)

    # Extract common alert fields; tolerate arbitrary schema.
    for k in ("rule", "rule_name", "title", "summary", "message", "description"):
        v = alert.get(k)
        if v:
            parts.append(str(v))

    if not parts:
        # Fall back to dumping the alert keys so we at least send something semantic.
        parts.append(" ".join(f"{k}={v}" for k, v in alert.items() if isinstance(v, (str, int, float)))[:500])

    return " | ".join(parts)[:1200]


def _hit_to_dict(hit) -> dict[str, Any]:
    """Serialize a GRCChunkHit dataclass into a plain dict for state."""
    return {
        "chunk_id": hit.chunk_id,
        "source_file": hit.source_file,
        "doc_type": hit.doc_type,
        "chunk_index": hit.chunk_index,
        "content": hit.content,
        "h1": hit.h1,
        "h2": hit.h2,
        "h3": hit.h3,
        "score": hit.score,
        "nist_controls": hit.nist_controls,
        "mitre_atlas": hit.mitre_atlas,
        "citation": hit.citation_string,
    }


def retrieve(
    state: dict,
    retriever: GRCRetriever | None = None,
    top_k: int = DEFAULT_TOP_K,
) -> dict:
    """pgvector RAG retrieval node.

    Args:
        state: IRState-shaped dict with alert + classification populated.
        retriever: optional GRCRetriever for test injection. Production code
                   lets the node construct its own singleton-ish instance.
        top_k: number of chunks to return.

    Returns:
        Partial state update with grc_chunks + an evidence row.
    """
    t0 = time.monotonic()
    query = _build_query(state)

    if not query.strip():
        update = {
            "grc_chunks": [],
            "evidence": list(state.get("evidence") or []) + [
                {"node": "retrieve", "elapsed_ms": 0, "skipped": "empty_query"}
            ],
        }
        return update

    r = retriever or GRCRetriever()

    try:
        hits = r.search(query_text=query, top_k=top_k)
    except Exception as e:
        log.exception("retrieve: search failed for query=%r", query[:120])
        return {
            "grc_chunks": [],
            "errors": list(state.get("errors") or []) + [f"retrieve_failed: {e!s}"],
            "evidence": list(state.get("evidence") or [])
            + [
                {
                    "node": "retrieve",
                    "elapsed_ms": int((time.monotonic() - t0) * 1000),
                    "error": str(e),
                }
            ],
        }

    elapsed_ms = int((time.monotonic() - t0) * 1000)
    chunks = [_hit_to_dict(h) for h in hits]

    evidence_row = {
        "node": "retrieve",
        "elapsed_ms": elapsed_ms,
        "top_k": top_k,
        "hit_count": len(chunks),
        "top_score": chunks[0]["score"] if chunks else None,
        "query": query[:240],
    }
    evidence = list(state.get("evidence") or []) + [evidence_row]

    return {
        "grc_chunks": chunks,
        "evidence": evidence,
    }
