"""Embed and upsert the GRC corpus into ir_chunks.

Runs as a one-shot CLI:
    python -m squire.ingest.grc_indexer [--dry-run] [--grc-dir PATH]

Flow:
    1. Walk SQUIRE_GRC_DIR for *.md (excludes README.md; includes subdirs none today).
    2. Chunk each file via squire.ingest.chunker.chunk_document.
    3. Batch-embed chunks via the configured provider (voyage by default).
    4. DELETE FROM ir_chunks before insert, then bulk INSERT with embeddings.

Provider = voyage (ADR 001):
    - Endpoint:  https://api.voyageai.com/v1/embeddings via voyageai Python SDK
    - Model:     voyage-3-large (1024 dim, cosine)
    - Batch cap: 128 inputs / 32k tokens per call
    - Auth:      VOYAGE_API_KEY (Doppler)
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from pathlib import Path
from typing import Iterable, Sequence

from sqlalchemy import text

from ..db import get_engine
from ..settings import get_settings
from .chunker import GRCChunk, chunk_document

logger = logging.getLogger("squire.ingest.grc_indexer")

# Voyage API batching.
# - Free-tier Voyage accounts (no payment method) are capped at 3 RPM + 10K TPM.
# - Paid accounts go to 300 RPM + 1M TPM.
# VOYAGE_BATCH_SIZE and VOYAGE_MIN_INTERVAL_S are tunable via env so the indexer
# can run fast on a paid key and slow on a free-tier key without code changes.
VOYAGE_BATCH_SIZE = int(os.environ.get("VOYAGE_BATCH_SIZE", "30"))
VOYAGE_MIN_INTERVAL_S = float(os.environ.get("VOYAGE_MIN_INTERVAL_S", "21"))


# ---------------------------------------------------------------------------
# Embedder providers
# ---------------------------------------------------------------------------


class VoyageEmbedder:
    """Thin wrapper around the voyageai Python SDK.

    Exposes embed(texts) -> list[list[float]] plus total_tokens accounting.
    """

    def __init__(self, api_key: str, model: str, expected_dim: int):
        # Import late so unit tests that never hit Voyage don't need the package.
        import voyageai  # type: ignore

        self._client = voyageai.Client(api_key=api_key)
        self._model = model
        self._expected_dim = expected_dim
        self.total_tokens: int = 0
        self.total_calls: int = 0
        self._last_call_epoch: float = 0.0

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []

        # Respect the per-call floor so free-tier 3 RPM does not 429.
        now = time.perf_counter()
        elapsed = now - self._last_call_epoch
        if self._last_call_epoch > 0 and elapsed < VOYAGE_MIN_INTERVAL_S:
            wait = VOYAGE_MIN_INTERVAL_S - elapsed
            logger.info("rate-limit floor: sleeping %.2fs", wait)
            time.sleep(wait)

        t0 = time.perf_counter()
        result = self._client.embed(texts=list(texts), model=self._model)
        self._last_call_epoch = time.perf_counter()
        self.total_calls += 1
        # voyageai returns an EmbeddingsObject with .embeddings and .total_tokens.
        embeddings: list[list[float]] = list(result.embeddings)
        self.total_tokens += int(getattr(result, "total_tokens", 0))
        dt_ms = int((time.perf_counter() - t0) * 1000)
        logger.info(
            "voyage.embed batch=%d tokens=%s dt_ms=%d call_no=%d",
            len(texts),
            getattr(result, "total_tokens", "?"),
            dt_ms,
            self.total_calls,
        )
        for vec in embeddings:
            if len(vec) != self._expected_dim:
                raise RuntimeError(
                    f"voyage returned dim={len(vec)}, expected {self._expected_dim}; "
                    "check SQUIRE_EMBEDDING_MODEL / SQUIRE_EMBEDDING_DIM alignment"
                )
        return embeddings


def _build_embedder():
    s = get_settings()
    provider = s.squire_embedding_provider.lower()
    if provider == "voyage":
        key = s.voyage_api_key.get_secret_value() if s.voyage_api_key else None
        if not key:
            raise RuntimeError(
                "VOYAGE_API_KEY not set but SQUIRE_EMBEDDING_PROVIDER=voyage"
            )
        return VoyageEmbedder(
            api_key=key,
            model=s.squire_embedding_model,
            expected_dim=s.squire_embedding_dim,
        )
    raise RuntimeError(
        f"Unsupported embedding provider: {provider!r}. "
        "Only 'voyage' is implemented (see ADR 001)."
    )


# ---------------------------------------------------------------------------
# Chunk collection
# ---------------------------------------------------------------------------


def _iter_grc_files(grc_dir: Path) -> Iterable[Path]:
    """Yield .md files under grc_dir. Excludes README.md and diagram files."""
    for p in sorted(grc_dir.rglob("*.md")):
        # Skip diagram notes / README that aren't useful as retrieval targets.
        if p.name == "README.md":
            continue
        yield p


def _collect_chunks(grc_dir: Path) -> list[GRCChunk]:
    chunks: list[GRCChunk] = []
    doc_count = 0
    for md_path in _iter_grc_files(grc_dir):
        doc_chunks = chunk_document(md_path)
        if not doc_chunks:
            logger.warning("no chunks produced for %s", md_path)
            continue
        chunks.extend(doc_chunks)
        doc_count += 1
        logger.info("chunked %s -> %d chunks", md_path.name, len(doc_chunks))
    logger.info("collected %d chunks across %d docs", len(chunks), doc_count)
    return chunks


# ---------------------------------------------------------------------------
# Insertion
# ---------------------------------------------------------------------------


_INSERT_SQL = text(
    """
    INSERT INTO ir_chunks (
        source_path,
        source_kind,
        chunk_index,
        content,
        content_hash,
        token_count,
        embedding,
        metadata
    ) VALUES (
        :source_path,
        :source_kind,
        :chunk_index,
        :content,
        :content_hash,
        :token_count,
        CAST(:embedding AS vector),
        CAST(:metadata AS jsonb)
    )
    """
)


def _serialize_vector(vec: Sequence[float]) -> str:
    """Format for pgvector text input: '[0.1,0.2,...]'."""
    return "[" + ",".join(f"{x:.7f}" for x in vec) + "]"


def _merge_metadata(chunk: GRCChunk) -> dict:
    md = dict(chunk.metadata)
    md["source_file"] = chunk.source_file
    md["doc_type"] = chunk.doc_type
    md["h1"] = chunk.h1
    md["h2"] = chunk.h2
    md["h3"] = chunk.h3
    md["citation_string"] = chunk.citation_string()
    return md


def index_corpus(grc_dir: Path, dry_run: bool = False) -> dict:
    """Run the full index pipeline. Returns a stats dict."""
    chunks = _collect_chunks(grc_dir)
    if not chunks:
        raise RuntimeError(f"No chunks collected from {grc_dir}")

    if dry_run:
        logger.info("dry-run: skipping embedding + insert (chunks=%d)", len(chunks))
        return {
            "chunks": len(chunks),
            "distinct_docs": len({c.source_file for c in chunks}),
            "dry_run": True,
            "tokens": 0,
        }

    embedder = _build_embedder()
    engine = get_engine()

    t_embed_start = time.perf_counter()
    embeddings: list[list[float]] = []
    for i in range(0, len(chunks), VOYAGE_BATCH_SIZE):
        batch = chunks[i : i + VOYAGE_BATCH_SIZE]
        batch_embs = embedder.embed([c.content for c in batch])
        embeddings.extend(batch_embs)
    t_embed_ms = int((time.perf_counter() - t_embed_start) * 1000)

    if len(embeddings) != len(chunks):
        raise RuntimeError(
            f"embedding count mismatch: {len(embeddings)} embeddings for {len(chunks)} chunks"
        )

    # Idempotent: wipe then insert.
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM ir_chunks"))
        rows = []
        import json as _json
        for chunk, vec in zip(chunks, embeddings):
            rows.append(
                {
                    "source_path": chunk.source_file,
                    "source_kind": chunk.doc_type,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "content_hash": chunk.content_hash,
                    "token_count": chunk.token_count,
                    "embedding": _serialize_vector(vec),
                    "metadata": _json.dumps(_merge_metadata(chunk)),
                }
            )
        conn.execute(_INSERT_SQL, rows)

    return {
        "chunks": len(chunks),
        "distinct_docs": len({c.source_file for c in chunks}),
        "embed_ms": t_embed_ms,
        "voyage_calls": embedder.total_calls,
        "voyage_tokens": embedder.total_tokens,
        "dry_run": False,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Index GRC corpus into ir_chunks")
    parser.add_argument(
        "--grc-dir",
        default=None,
        help="Override GRC corpus directory (defaults to SQUIRE_GRC_DIR)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Chunk without embedding or inserting",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Python logging level (default INFO)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    s = get_settings()
    grc_dir = Path(args.grc_dir or s.squire_grc_dir)
    if not grc_dir.exists():
        logger.error("GRC dir does not exist: %s", grc_dir)
        return 2

    stats = index_corpus(grc_dir, dry_run=args.dry_run)
    logger.info("index complete: %s", stats)
    print(stats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
