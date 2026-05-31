-- Squire Phase 17 initial schema
-- Target: Postgres with pgvector extension; database name from CD_DB_NAME env var
--
-- Creates 4 tables for Squire investigation pipeline:
--   ir_investigations -- one row per alert that reached the graph
--   ir_evidence       -- intermediate evidence collected during graph traversal
--   ir_citations      -- GRC doc + incident citations attached to the final report
--   ir_chunks         -- RAG corpus chunks with embedding vector(1536)
--
-- The v1 table ir_incidents (Phase 7 era, if present) is NOT touched.
-- pgvector extension is assumed present (installed in 17-03).

BEGIN;

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ----------------------------------------------------------------------------
-- ir_investigations: one row per alert Squire ran the graph on
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ir_investigations (
    id                  UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_id            TEXT        NOT NULL,
    alert_signature     VARCHAR(64) NOT NULL,
    alert_source        TEXT        NOT NULL,          -- falco | datadog | webhook
    alert_payload       JSONB       NOT NULL,
    severity            TEXT,
    status              TEXT        NOT NULL DEFAULT 'open',  -- open | resolved | suppressed | dedup
    trace_id            TEXT,                                  -- Langfuse trace id
    dedup_of            UUID        REFERENCES ir_investigations(id) ON DELETE SET NULL,
    report              JSONB,
    cost_usd            NUMERIC(10,4) NOT NULL DEFAULT 0,
    tokens_prompt       INTEGER     NOT NULL DEFAULT 0,
    tokens_completion   INTEGER     NOT NULL DEFAULT 0,
    model_profile       TEXT,                                  -- quality | fast | ollama
    latency_ms          INTEGER,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ir_investigations_created_at_idx ON ir_investigations (created_at DESC);
CREATE INDEX IF NOT EXISTS ir_investigations_signature_idx  ON ir_investigations (alert_signature);
CREATE INDEX IF NOT EXISTS ir_investigations_status_idx     ON ir_investigations (status);

-- ----------------------------------------------------------------------------
-- ir_evidence: intermediate evidence collected per investigation
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ir_evidence (
    id                UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    investigation_id  UUID        NOT NULL REFERENCES ir_investigations(id) ON DELETE CASCADE,
    kind              TEXT        NOT NULL,   -- log | process | network | container | grc_doc | history
    source            TEXT        NOT NULL,
    content           JSONB       NOT NULL,
    collected_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ir_evidence_investigation_idx ON ir_evidence (investigation_id);
CREATE INDEX IF NOT EXISTS ir_evidence_kind_idx          ON ir_evidence (kind);

-- ----------------------------------------------------------------------------
-- ir_citations: GRC doc and incident citations attached to the final report
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ir_citations (
    id                UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    investigation_id  UUID        NOT NULL REFERENCES ir_investigations(id) ON DELETE CASCADE,
    citation_type     TEXT        NOT NULL,   -- grc_doc | incident | runbook | external
    source_path       TEXT        NOT NULL,
    chunk_id          UUID,                    -- optional FK to ir_chunks
    excerpt           TEXT,
    relevance_score   NUMERIC(6,4),
    validated         BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ir_citations_investigation_idx ON ir_citations (investigation_id);
CREATE INDEX IF NOT EXISTS ir_citations_type_idx          ON ir_citations (citation_type);

-- ----------------------------------------------------------------------------
-- ir_chunks: RAG corpus chunks with embedding vector(1536)
-- Dim 1536 matches Anthropic / OpenAI text-embedding-3-large defaults.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ir_chunks (
    id             UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_path    TEXT        NOT NULL,
    source_kind    TEXT        NOT NULL,          -- grc_doc | incident | runbook
    chunk_index    INTEGER     NOT NULL,
    content        TEXT        NOT NULL,
    content_hash   VARCHAR(64) NOT NULL,
    token_count    INTEGER,
    embedding      vector(1536),
    metadata       JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source_path, chunk_index)
);

CREATE INDEX IF NOT EXISTS ir_chunks_source_path_idx ON ir_chunks (source_path);
CREATE INDEX IF NOT EXISTS ir_chunks_source_kind_idx ON ir_chunks (source_kind);
CREATE INDEX IF NOT EXISTS ir_chunks_hash_idx        ON ir_chunks (content_hash);

-- HNSW index for cosine similarity over the embedding column.
-- m=16, ef_construction=64 are pgvector 0.8 defaults tuned for quality+speed.
CREATE INDEX IF NOT EXISTS ir_chunks_embedding_hnsw_idx
    ON ir_chunks
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- FK from citations -> chunks (added now that both tables exist)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ir_citations_chunk_id_fkey'
    ) THEN
        ALTER TABLE ir_citations
            ADD CONSTRAINT ir_citations_chunk_id_fkey
            FOREIGN KEY (chunk_id) REFERENCES ir_chunks(id) ON DELETE SET NULL;
    END IF;
END $$;

COMMIT;
