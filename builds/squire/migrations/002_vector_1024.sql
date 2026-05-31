-- Squire Phase 17 plan 17-07: shift ir_chunks.embedding from vector(1536) to vector(1024)
--
-- Rationale: ADR 001 chose Voyage AI voyage-3-large over OpenAI text-embedding-3-large
-- because OpenClaw gateway does not route /v1/embeddings, and the direct Voyage API
-- probe returned HTTP 200 with 1024-dim vectors at 266 ms. voyage-3-large produces
-- 1024-dim vectors by default (not 1536), so the column type and HNSW index must be
-- resized to match.
--
-- Preconditions verified on droplet 2026-04-23:
--   - ir_chunks row count = 0 (safe to ALTER in place)
--   - HNSW index exists on (embedding vector_cosine_ops)
--
-- Order of operations:
--   1. Drop HNSW index (cannot ALTER column type while an index depends on it).
--   2. ALTER COLUMN embedding TYPE vector(1024).
--   3. Recreate HNSW index with identical m / ef_construction tuning.

BEGIN;

DROP INDEX IF EXISTS ir_chunks_embedding_hnsw_idx;

ALTER TABLE ir_chunks
    ALTER COLUMN embedding TYPE vector(1024);

CREATE INDEX IF NOT EXISTS ir_chunks_embedding_hnsw_idx
    ON ir_chunks
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

COMMIT;
