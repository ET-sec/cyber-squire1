"""GRC retriever -- pgvector cosine similarity over ir_chunks.

Public API (consumed by 17-08 LangGraph agent):

    retriever = GRCRetriever()                 # defaults: reuses squire engine + voyage
    hits = retriever.search(
        query_text="compromised container triage",
        top_k=5,
        doc_type="playbook",                   # optional filter
        nist_controls=["IR-4"],                # optional filter (any-match)
        mitre_tactics=["AML.T0040"],           # optional filter (any-match)
    )
    for h in hits:
        print(h.citation_string, h.score, h.source_file)

Notes:
  - Cosine distance via the `<=>` operator; score = 1 - distance (higher is better).
  - Filters compose with AND. Each filter is implemented with JSONB containment
    against ir_chunks.metadata so the HNSW index stays on the main ORDER BY.
  - The embed call is delegated to the same Voyage provider the indexer used so
    retrieval embeddings match corpus embeddings.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Iterable, Optional, Sequence

from sqlalchemy import text
from sqlalchemy.engine import Engine

from ..db import get_engine
from ..settings import get_settings

logger = logging.getLogger("squire.retrievers.grc_retriever")


@dataclass
class GRCChunkHit:
    """One row of retrieval output."""

    chunk_id: str
    source_file: str
    doc_type: str
    chunk_index: int
    content: str
    h1: Optional[str]
    h2: Optional[str]
    h3: Optional[str]
    score: float                 # cosine similarity (1 - distance)
    nist_controls: list[str]
    mitre_atlas: list[str]
    metadata: dict

    @property
    def citation_string(self) -> str:
        parts = [p for p in (self.h1, self.h2, self.h3) if p]
        if not parts:
            return self.source_file
        return f"{self.source_file} §{' > '.join(parts)}"


class GRCRetriever:
    """pgvector cosine retriever over ir_chunks."""

    def __init__(
        self,
        engine: Engine | None = None,
        embedder=None,
    ):
        self._engine = engine or get_engine()
        self._embedder = embedder  # lazy

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search(
        self,
        query_text: str,
        top_k: int = 5,
        doc_type: str | None = None,
        nist_controls: Sequence[str] | None = None,
        mitre_tactics: Sequence[str] | None = None,
    ) -> list[GRCChunkHit]:
        if not query_text or not query_text.strip():
            return []

        t0 = time.perf_counter()
        query_vec = self._embed_query(query_text)
        t_embed_ms = int((time.perf_counter() - t0) * 1000)

        sql, params = self._build_sql(
            query_vec=query_vec,
            top_k=top_k,
            doc_type=doc_type,
            nist_controls=nist_controls,
            mitre_tactics=mitre_tactics,
        )

        t1 = time.perf_counter()
        with self._engine.connect() as conn:
            rows = conn.execute(sql, params).mappings().all()
        t_query_ms = int((time.perf_counter() - t1) * 1000)

        logger.info(
            "grc_retriever.search top_k=%d embed_ms=%d query_ms=%d hits=%d",
            top_k,
            t_embed_ms,
            t_query_ms,
            len(rows),
        )

        return [self._row_to_hit(r) for r in rows]

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _embed_query(self, query_text: str) -> list[float]:
        if self._embedder is None:
            # Build lazily so retriever import is cheap and tests can inject a mock.
            from ..ingest.grc_indexer import _build_embedder

            self._embedder = _build_embedder()
        embs = self._embedder.embed([query_text])
        if not embs or len(embs[0]) == 0:
            raise RuntimeError("embedder returned empty vector for query")
        return embs[0]

    @staticmethod
    def _vector_literal(vec: Iterable[float]) -> str:
        return "[" + ",".join(f"{x:.7f}" for x in vec) + "]"

    def _build_sql(
        self,
        *,
        query_vec: Sequence[float],
        top_k: int,
        doc_type: str | None,
        nist_controls: Sequence[str] | None,
        mitre_tactics: Sequence[str] | None,
    ):
        # Filter clauses. We use JSONB containment where possible so the embedding
        # ORDER BY stays the selective operator on the HNSW index.
        where_clauses: list[str] = []
        params: dict = {
            "query_vec": self._vector_literal(query_vec),
            "top_k": top_k,
        }

        if doc_type:
            where_clauses.append("source_kind = :doc_type")
            params["doc_type"] = doc_type

        if nist_controls:
            # any-match: metadata->'nist_controls' ?| ARRAY[...]
            where_clauses.append(
                "metadata->'nist_controls' ?| :nist_controls"
            )
            params["nist_controls"] = list(nist_controls)

        if mitre_tactics:
            where_clauses.append(
                "metadata->'mitre_atlas' ?| :mitre_tactics"
            )
            params["mitre_tactics"] = list(mitre_tactics)

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        sql = text(
            f"""
            SELECT
                id,
                source_path AS source_file,
                source_kind AS doc_type,
                chunk_index,
                content,
                metadata,
                1 - (embedding <=> CAST(:query_vec AS vector)) AS score
            FROM ir_chunks
            {where_sql}
            ORDER BY embedding <=> CAST(:query_vec AS vector)
            LIMIT :top_k
            """
        )
        return sql, params

    @staticmethod
    def _row_to_hit(row) -> GRCChunkHit:
        md = row["metadata"] or {}
        return GRCChunkHit(
            chunk_id=str(row["id"]),
            source_file=row["source_file"],
            doc_type=row["doc_type"],
            chunk_index=row["chunk_index"],
            content=row["content"],
            h1=md.get("h1"),
            h2=md.get("h2"),
            h3=md.get("h3"),
            score=float(row["score"]),
            nist_controls=list(md.get("nist_controls") or []),
            mitre_atlas=list(md.get("mitre_atlas") or []),
            metadata=md,
        )
