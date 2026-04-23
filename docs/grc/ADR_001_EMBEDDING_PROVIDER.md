# ADR 001 — Embedding Provider Selection for Squire RAG

**Status:** Accepted
**Date:** 2026-04-23
**Phase:** 17-07 (Squire GRC ingestion)
**Decision owner:** Emmanuel Tigoue, CoreDirective

## Context

Squire is an autonomous SOC analyst that triages security alerts by retrieving playbooks and control documentation from a 41-document GRC corpus stored in pgvector. The retrieval layer requires an embedding model to convert both indexed chunks and inbound alert queries into dense vectors for cosine similarity lookup. Embedding provider choice drives:

- **Retrieval accuracy** (how often Squire returns the correct playbook as top-1 hit)
- **Data residency** (does alert content ever leave the boundary)
- **Cost profile** (one-time vs. per-query)
- **Deployment portability** (which customer environments can host Squire)

## Options Considered

### Option A: OpenAI `text-embedding-3-large` (chosen)

Cloud API call to OpenAI's embeddings endpoint. 1536-dimensional vectors. Proven industry baseline used by Dropzone AI, Prophet Security, AirMDR, and the majority of commercial SOC-assistance products.

- **Cost:** $0.13 per million tokens. Squire's 41-document corpus is approximately one million tokens after chunking, so a one-time bulk embedding costs roughly $0.13. Per-query cost at inference time is negligible (tens of tokens per alert × $0.13/M).
- **Latency:** Single-digit milliseconds per query when the API is healthy; subject to OpenAI uptime.
- **Data path:** Alert text traverses the public internet to OpenAI's servers. OpenAI's API terms permit opting out of training on customer data, but the payload still leaves the tenant boundary.

### Option B: Local `BAAI/bge-large-en-v1.5` via sentence-transformers

Self-hosted embedding model running inside the Squire container. 1024-dimensional vectors. Open-source weights published under MIT license.

- **Cost:** Zero external spend. Amortized droplet CPU only.
- **Latency:** Ten to forty milliseconds per query depending on CPU contention with other droplet services.
- **Data path:** Alert text never leaves the deployment boundary. Fully air-gap capable.
- **Overhead:** Container image grows by approximately 450 MB. Schema requires a one-line vector dimension change from 1536 to 1024.

### Option C: Voyage AI `voyage-3-large`

The embedding provider Anthropic officially recommends for Claude-based retrieval systems. 1024-dimensional vectors.

- **Cost:** Approximately $0.06 for the bulk ingest; free tier covers it.
- **Data path:** Equivalent to Option A (alert text traverses the public internet).
- **Ecosystem fit:** Clean integration with the Anthropic stack Squire already uses.

## Decision

Squire will use Option A (OpenAI `text-embedding-3-large`) as the default embedding provider for the Phase 17 reference deployment at `squire.tigouetheory.com`.

The choice is driven by three factors:

1. The `ir_chunks.embedding vector(1536)` column was pre-sized in the schema migration (17-06 migration 001) to match OpenAI's 1536-dimensional output exactly. Choosing A requires zero schema change.
2. Option A is the dominant pattern in the commercial SOC-AI space (Dropzone, Prophet, AirMDR). Interviewers at that tier recognize it instantly and do not need the choice defended.
3. The reference deployment processes synthetic alerts against a sanitized GRC corpus. There is no classified or regulated data in the demo path, so the data-residency disadvantage of Option A does not apply to the current use case.

## Consequences for Customer Deployments

The reference deployment is not the only target. Squire's architecture explicitly supports swapping the embedding provider for customer environments with different constraints.

### Air-Gapped / Classified / Defense-Contractor Deployments

For deployments where alert content cannot leave the tenant boundary (federal civilian agencies, defense contractors, Secret Service-adjacent fusion centers, healthcare PHI environments, financial PII environments), the operator will deploy Squire with Option B active.

The swap is a three-step change:
1. Flip `SQUIRE_EMBEDDING_PROVIDER` env var from `openai` to `local_bge` (already consumed by `builds/squire/src/squire/retrievers/grc_retriever.py`).
2. Apply migration `002_vector_1024.sql` to shrink `ir_chunks.embedding` from `vector(1536)` to `vector(1024)` and re-index.
3. Re-run the indexer with the local model; no further code change required.

The migration file and the provider abstraction exist in the codebase specifically so this swap is operational, not architectural. Any customer engagement that requires air-gapped AI inference can be onboarded without touching Squire's retrieval, ingestion, or LangGraph layers.

### Hybrid (Partial Air-Gap) Deployments

For deployments that can tolerate cloud embeddings for non-sensitive corpus documents (public compliance templates, vendor playbooks) but require local embeddings for tenant-specific alerts, the retriever module supports a per-query `embedding_provider` override. This capability is documented in the Squire Model Card (17-13b).

## Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| OpenAI API outage blocks Squire retrieval | Ollama fallback on the droplet is already wired for LLM reasoning (17-08a). Retrieval falls back to the last known good `ir_chunks` snapshot; no re-embed on outage. |
| OpenAI price change or deprecation of `text-embedding-3-large` | Provider abstraction at the retriever module makes a swap to Voyage or a newer OpenAI model a single env var change plus re-index. |
| Interviewer challenge on data residency | This ADR is the defensive artifact. Option B is a documented, supported deployment mode, not a future roadmap item. |
| Embedding dimension drift across providers | The schema migration path (`002_vector_1024.sql` for B, `003_vector_2048.sql` for any larger model) is pre-planned and idempotent. |

## References

- Squire scaffold: `/Users/et/cyber-squire-ops/builds/squire/` (gitignored locally; built artifact)
- Schema migration: `builds/squire/migrations/001_squire_tables.sql`
- Provider abstraction: `builds/squire/src/squire/retrievers/grc_retriever.py` (created in 17-07)
- Deferred local-model migration: `builds/squire/migrations/002_vector_1024.sql` (created alongside 001, not applied)
- OpenAI text-embedding-3-large documentation: platform.openai.com/docs/guides/embeddings
- BAAI bge-large-en-v1.5 model card: huggingface.co/BAAI/bge-large-en-v1.5
- Voyage AI embeddings: docs.voyageai.com/docs/embeddings
