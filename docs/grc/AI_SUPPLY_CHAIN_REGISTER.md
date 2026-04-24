# AI Supply Chain Register

**Document ID:** SCR-AI-001
**Version:** 1.0
**Classification:** Internal Use Only
**Effective Date:** 2026-04-23
**Owner:** Information Security Officer
**Approved By:** System Owner
**Distinct From:** AI_SUPPLY_CHAIN_RISK.md (the policy). This document is the living asset register that the policy references.
**NIST 800-53 Controls:** CM-8 (System Component Inventory), SR-4 (Provenance), SR-11 (Component Authenticity)

---

## Document Control

| Field | Value |
|-------|-------|
| Document ID | SCR-AI-001 |
| Version | 1.0 |
| Status | Approved |
| Last Revised | 2026-04-23 |
| Next Review | 2026-06-23 (60-day cadence, aligned with token rotation) |
| Author | Information Security Officer |
| Approver | System Owner |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-23 | Information Security Officer | Initial register covering 14 components of Squire |

---

## 1. Purpose

This is the living asset register for every component in Squire's AI supply chain. The companion policy AI_SUPPLY_CHAIN_RISK.md defines how these components are evaluated and managed. This register is the source of truth for what those components actually are today.

Two documents, two jobs:

- AI_SUPPLY_CHAIN_RISK.md: policy, methodology, control framework
- AI_SUPPLY_CHAIN_REGISTER.md (this): inventory, versions, hashes, risk scores, review cadence

When a reader asks "what version of NeMo are we on," this register answers. When a reader asks "what is our position on vendor-hosted vs self-hosted model risk," the risk doc answers.

---

## 2. Register Schema

| Column | Meaning |
|--------|---------|
| Component | Canonical name |
| Version | Pinned version at time of entry |
| Provider | Upstream entity |
| License | License type |
| Hash / Digest | Where verifiable (container digest, model ID, package hash) |
| Updated | Date this row was last updated |
| Next Review | Scheduled review date |
| Risk Score | 1 (low) - 5 (critical), informed by criticality to Squire |
| Notes | Relevant operational context |

Risk Score rubric:

- 5: Single point of failure for the primary reasoning path. Outage halts Squire entirely without degraded-mode compensation.
- 4: Primary path participant, degraded-mode compensates but with meaningful quality loss.
- 3: Secondary path participant, outage impacts specific capabilities.
- 2: Support component, outage is inconvenient but not blocking.
- 1: Ancillary, fallback paths trivially cover.

---

## 3. Component Register

### 3.1 Foundation Models

| Component | Version | Provider | License | Hash / Digest | Updated | Next Review | Risk Score | Notes |
|-----------|---------|----------|---------|---------------|---------|-------------|------------|-------|
| claude-opus-4-7 | claude-opus-4-7 (2026 release) | Anthropic PBC | Proprietary (API ToS) | Provider-managed | 2026-04-23 | 2026-06-23 | 5 | Primary reasoning on investigate, draft, critique. Temperature param rejected by this model, APIBackend handles. |
| claude-sonnet-4-6 | claude-sonnet-4-6 | Anthropic PBC | Proprietary (API ToS) | Provider-managed | 2026-04-23 | 2026-06-23 | 4 | Classifier on classify node. Temperature accepted. |
| text-embedding-3-large | v3-large, 1536 dim | OpenAI | Proprietary (API ToS) | Provider-managed | 2026-04-23 | 2026-06-23 | 4 | Used at corpus embed time, not at runtime. Corpus rebuild required on provider drift. |

### 3.2 Orchestration and Observability

| Component | Version | Provider | License | Hash / Digest | Updated | Next Review | Risk Score | Notes |
|-----------|---------|----------|---------|---------------|---------|-------------|------------|-------|
| langgraph | 0.2.x | LangChain AI | MIT | pyproject pin `langgraph>=0.2` | 2026-04-23 | 2026-06-23 | 4 | State machine runtime. Breaking changes at major-version bumps. |
| langchain-anthropic | 0.3.x | LangChain AI | MIT | pyproject pin `langchain-anthropic>=0.3` | 2026-04-23 | 2026-06-23 | 3 | Anthropic connector. |
| langchain | 1.x | LangChain AI | MIT | pyproject pin `langchain>=1` | 2026-04-23 | 2026-06-23 | 3 | Transitive via langfuse.langchain. Version 1.0+ explicit after container runtime ImportError. |
| langfuse SDK | 3.14.6 | Langfuse GmbH | MIT | pypi langfuse-3.14.6 | 2026-04-23 | 2026-06-23 | 3 | Trace SDK. Version 3 series. |
| langfuse server (self-hosted) | v3 | Langfuse GmbH | MIT (OSS core) | Container digests captured in ROLLBACK_TAGS.md (droplet) | 2026-04-23 | 2026-06-23 | 3 | 4 containers: web, worker, ClickHouse, Redis. |

### 3.3 Guardrails

| Component | Version | Provider | License | Hash / Digest | Updated | Next Review | Risk Score | Notes |
|-----------|---------|----------|---------|---------------|---------|-------------|------------|-------|
| nemoguardrails | 0.21.0 | NVIDIA | Apache 2.0 | pypi nemoguardrails-0.21.0 | 2026-04-23 | 2026-06-23 | 4 | Input rail on draft and critique. Presidio extra `[sdd]` required. |
| presidio-analyzer | Bundled via `nemoguardrails[sdd]` | Microsoft | MIT | Transitive pin | 2026-04-23 | 2026-06-23 | 4 | PII detection engine. Uses spaCy en_core_web_lg (~560 MB). |
| spaCy en_core_web_lg | 3.7.x | Explosion AI | MIT | Downloaded at container build | 2026-04-23 | 2026-06-23 | 3 | Loaded by presidio. Container RSS 1018 MiB steady-state. |
| GLiNER (optional, pinned) | community release | Community | Apache 2.0 | TBD: pinned but currently unloaded | 2026-04-23 | 2026-06-23 | 2 | Deferred integration. Phase 17 locked on presidio only. |
| Lakera Guard | N/A | Lakera AG | Commercial | TBD: deferred | 2026-04-23 | 2026-06-23 | 2 | LAKERA_API_KEY not provisioned. Deferred per orchestrator decision. |

### 3.4 Data and Infrastructure

| Component | Version | Provider | License | Hash / Digest | Updated | Next Review | Risk Score | Notes |
|-----------|---------|----------|---------|---------------|---------|-------------|------------|-------|
| pgvector | pg16 | pgvector contributors | PostgreSQL License (permissive, BSD-style) | Image `pgvector/pgvector:pg16` digest in ROLLBACK_TAGS.md | 2026-04-23 | 2026-06-23 | 5 | Embeddings store. vector(1536) + HNSW index. Swap from Alpine to Debian/glibc pg16 preserved. |
| PostgreSQL | 16.13 | PostgreSQL Global Development Group | PostgreSQL License | Bundled with pgvector image | 2026-04-23 | 2026-06-23 | 5 | Persistent store for workflow and Squire `ir_*` tables. |
| ClickHouse | 24.11 alpine | ClickHouse Inc. | Apache 2.0 | Container digest in ROLLBACK_TAGS.md | 2026-04-23 | 2026-06-23 | 3 | Langfuse span store. pids cap 2048, low-resources override required. |
| Redis | 7.x | Redis (new Redis Source Available License as of 2024) | TBD: verify RSAL vs BSD for the pinned minor | 2026-04-23 | 2026-06-23 | 2 | Hot cache for Langfuse and dedup. Verify pin is pre-RSAL or compliant post-RSAL. |
| Tavily | commercial API | Tavily | Commercial (ToS-governed) | Provider-managed | 2026-04-23 | 2026-06-23 | 3 | Enrich node web search. Fails open to empty results. |
| OpenClaw | v2026.4.21 | Anthropic or upstream vendor | TBD: verify license for v2026.x series | 2026-04-23 | 2026-06-23 | 2 | Gateway fronting Telegram, n8n, Claude Desktop. Squire APIBackend currently bypasses OpenClaw for Anthropic calls; one-line switch to route through it. |

---

## 4. TBD Items

Items flagged TBD in the register above:

- **GLiNER version pin**: currently unloaded; version is noted as "community release". When integration lands in a Phase 17 follow-up, a specific commit or tag needs to be pinned and recorded here.
- **Lakera Guard deployment state**: LAKERA_API_KEY is not provisioned. If Lakera is later adopted, license terms and the specific product tier (free vs commercial) need to be captured.
- **Redis license**: Redis transitioned to Redis Source Available License in 2024. Version 7.x is the pinned minor; the specific sub-version needs to be verified to determine whether this entry is under RSAL or the earlier BSD. This affects redistribution posture.
- **OpenClaw license for v2026.x series**: the v2026.x series license terms are to be verified from the upstream distribution.

Each TBD is an action item on the 60-day review cycle. Leaving a TBD un-resolved past two cycles escalates to the system owner for disposition.

---

## 5. Review Cadence

### 5.1 Scheduled

Every 60 days, the register is walked top to bottom:

- Versions confirmed against `pyproject.toml`, `docker-compose.yaml`, and provider announcements
- Container digests re-pulled and compared to ROLLBACK_TAGS.md
- License statements reconfirmed against upstream (particularly for items with shifting license terms like Redis)
- Risk scores re-evaluated against operational evidence from the prior period

### 5.2 Event-Driven

The register is updated outside the scheduled cycle whenever:

- A new component is introduced into the pipeline
- A component is removed
- A component version is changed
- A provider makes a material change (license, pricing, ToS, end-of-life announcement)
- A supply chain incident (CVE, compromise, leaked signing key) affects an entry

Event-driven updates are logged in the revision history and reviewed at the next scheduled cycle.

---

## 6. Cross-References

- AI_SUPPLY_CHAIN_RISK.md (companion policy; methodology and controls)
- SQUIRE_MODEL_CARD.md (intended use per component)
- SQUIRE_DATA_FLOW_CLASSIFICATION.md (data flow across the same components)
- AI_AUDIT_TRAIL_SPEC.md (how component use is audited)
- HITL_POLICY.md (human gates on the output of these components)
- ADR_001_EMBEDDING_PROVIDER.md (embedding provider selection rationale for text-embedding-3-large)
- POLICY_AI_GOVERNANCE.md (parent governance)
- ROLLBACK_TAGS.md (droplet-side ledger of container digests; referenced here, not duplicated)
