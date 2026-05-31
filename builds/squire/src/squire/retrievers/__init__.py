"""Squire retrievers subpackage.

Modules:
  grc_retriever -- pgvector cosine similarity search over ir_chunks with
                   filters for doc_type, NIST controls, and MITRE tactics.
"""

from .grc_retriever import GRCChunkHit, GRCRetriever  # re-export for callers

__all__ = ["GRCChunkHit", "GRCRetriever"]
