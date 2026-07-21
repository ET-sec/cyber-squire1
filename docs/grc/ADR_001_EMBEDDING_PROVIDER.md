# ADR 001: Embedding Provider Selection for Squire RAG

**Status:** Accepted
**Date:** 2026-04-23
**Phase:** 17-07 (Squire GRC ingestion)
**Decision owner:** System Owner, Organization

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

- **Cost:** Approximately $0.06 for the bulk ingest at one cent per ten thousand tokens on the indicative rate at decision time; free tier covers it. <!-- TODO(et): verify the per-million-token rate against the current Voyage AI pricing page; published rates have ranged from approximately $0.06 to $0.18 per million tokens across model classes; update this figure on next review. -->
- **Data path:** Equivalent to Option A (alert text traverses the public internet).
- **Ecosystem fit:** Clean integration with the Anthropic stack Squire already uses.

## Decision

Squire will use **Option C (Voyage AI `voyage-3-large`)** as the default embedding provider for the Phase 17 reference deployment at `squire.example-ops.com`.

The choice is driven by four factors:

1. **Anthropic-native stack coherence.** The rest of Squire runs on Claude Fable 5 (reasoning) and Claude Sonnet 4.6 (classification). Voyage is the embedding provider Anthropic explicitly recommends in its RAG documentation, producing a clean single-vendor narrative for commercial interviews (Dropzone, Prophet, Resilience, OneDigital) while still matching or exceeding OpenAI quality on MTEB retrieval benchmarks.
2. **Zero marginal cost.** Voyage's free tier covers 200 million tokens per month. Squire's 41-document corpus is approximately 1 million tokens after chunking, so the free tier has 200 times the headroom for the initial ingest and every subsequent re-embed. Under the current 12-week-year financial constraint, zero is the right price.
3. **Ownership trajectory.** MongoDB acquired Voyage AI in February 2024. MongoDB is the database layer most commonly deployed alongside pgvector-style vector stacks in AI security products, and their GitHub Education benefit is one Emmanuel can activate as a peripheral resume-building step. Using Voyage positions the stack inside an ecosystem that is actively consolidating.
4. **Dimension alignment with the air-gap fallback.** Voyage returns 1024-dimensional vectors by default. `BAAI/bge-large-en-v1.5` (Option B, the air-gap fallback) also returns 1024-dimensional vectors. Standardizing on 1024 dims across both the commercial and air-gapped deployment modes means swapping providers never requires a re-index or another schema migration. The 1024 choice is the dimension that makes operational portability free.

The reference deployment processes synthetic alerts against a sanitized GRC corpus, so the data-residency disadvantage of a cloud embedding service does not apply to the current use case. Production customer deployments that cannot send alert content to external APIs are covered by the swap procedure below.

**Schema migration applied alongside this decision:** `builds/squire/migrations/002_vector_1024.sql` drops the original `vector(1536)` column and replaces it with `vector(1024)`, recreating the HNSW index on the new column. This migration runs before bulk ingest since `ir_chunks` is empty at this point.

<!-- TODO(et): confirm VOYAGE_API_KEY is provisioned in Doppler `<SECRETS_PROJECT>/<CONFIG>`. The compose env block on svc-squire references this key; missing key causes runtime failure on first embed call. -->

## Consequences for Customer Deployments

The reference deployment is not the only target. Squire's architecture explicitly supports swapping the embedding provider for customer environments with different constraints.

### Air-Gapped / Classified / Defense-Contractor Deployments

For deployments where alert content cannot leave the tenant boundary (federal civilian agencies, defense contractors, Secret Service-adjacent fusion centers, healthcare PHI environments, financial PII environments), the operator deploys Squire with Option B active.

Because the reference deployment already uses 1024-dim vectors (matching Voyage), the swap is a two-step change with no schema migration:
1. Flip `SQUIRE_EMBEDDING_PROVIDER` env var from `voyage` to `local_bge` in Doppler.
2. Re-run the indexer inside the air-gapped container; `BAAI/bge-large-en-v1.5` produces 1024-dim vectors that land in the same schema.

The migration file and the provider abstraction exist in the codebase specifically so this swap is operational, not architectural. Any customer engagement that requires air-gapped AI inference can be onboarded without touching Squire's retrieval, ingestion, or LangGraph layers.

### Hybrid (Partial Air-Gap) Deployments

For deployments that can tolerate cloud embeddings for non-sensitive corpus documents (public compliance templates, vendor playbooks) but require local embeddings for tenant-specific alerts, the retriever module supports a per-query `embedding_provider` override. This capability is documented in the Squire Model Card (17-13b).

## Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Voyage API outage blocks Squire retrieval | At query time, Squire falls back to the already-indexed `ir_chunks` rows (no re-embed needed for stored corpus). For the alert-side embed, degraded mode returns an explicit error with a code that the LangGraph router converts into a human-escalation path. |
| Voyage price change or free-tier revocation | Provider abstraction at the retriever module makes a swap to OpenAI, local BGE, or another vendor a single env var change; bulk re-embed fits inside the free tier of most alternatives. |
| MongoDB repositions Voyage into paid-only tier | Schema already sits on 1024 dims, so Option B (local BAAI/bge-large) becomes the default escape hatch with no migration. |
| Interviewer challenge on data residency | This ADR is the defensive artifact. Option B is a documented, supported deployment mode, not a future roadmap item. |
| Embedding dimension drift across providers | Locked on 1024 dims for both Option C and Option B; no migration required when switching between the two. |

## References

- Squire scaffold: `builds/squire/` (gitignored; visible in local working tree)
- Schema migration (original 1536 dims): `builds/squire/migrations/001_squire_tables.sql`
- Schema migration (1024 dims, applied): `builds/squire/migrations/002_vector_1024.sql`
- Provider abstraction: `builds/squire/src/squire/retrievers/grc_retriever.py` (created in 17-07)
- Voyage AI embeddings documentation: docs.voyageai.com/docs/embeddings
- BAAI bge-large-en-v1.5 model card: huggingface.co/BAAI/bge-large-en-v1.5
- OpenAI text-embedding-3-large documentation (historical reference for Option A): platform.openai.com/docs/guides/embeddings
