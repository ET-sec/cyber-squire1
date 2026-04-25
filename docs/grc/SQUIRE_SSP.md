---
document_id: SSP-SQUIRE-001
title: System Security Plan - Squire Autonomous SOC Analyst
doc_type: ssp
system_name: Squire Autonomous SOC Analyst
classification: CUI-INTERNAL
version: "1.0"
last_updated: 2026-04-23
next_review: 2026-10-23
owner: System Owner
approver: System Owner (Authorizing Official)
parent: SSP-OPS-001
frameworks:
  - NIST SP 800-53 Rev 5
  - NIST AI RMF 1.0
  - MITRE ATLAS
related:
  - SSP-OPS-001
  - TM-SQUIRE-001
  - RT-SQUIRE-001
  - CW-SQUIRE-001
  - POAM-OPS-001
---

# System Security Plan: Squire Autonomous SOC Analyst

**Document Identifier:** SSP-SQUIRE-001
**Classification:** CONTROLLED UNCLASSIFIED - INTERNAL USE ONLY
**Version:** 1.0
**Last Updated:** 2026-04-23
**Next Scheduled Review:** 2026-10-23
**Prepared By:** System Owner
**Approved By:** System Owner (Authorizing Official)
**Parent SSP:** SSP-OPS-001 (Organization Security Operations Platform)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Identification](#2-system-identification)
3. [System Description](#3-system-description)
4. [Security Categorization](#4-security-categorization)
5. [Data Flow and Classification](#5-data-flow-and-classification)
6. [Control Implementation (NIST 800-53 Rev 5)](#6-control-implementation-nist-800-53-rev-5)
7. [Control Inheritance](#7-control-inheritance-from-parent-ssp)
8. [System Interconnections](#8-system-interconnections)
9. [Authorization Boundary](#9-authorization-boundary)
10. [Assumptions and Constraints](#10-assumptions-and-constraints)
11. [Annex A: actions.yml Recommend-Only Mode](#annex-a-actionsyml-recommend-only-mode)
12. [Annex B: Citation Guard Design](#annex-b-citation-guard-design)

---

## 1. Executive Summary

Squire is an autonomous Security Operations Center analyst deployed at `squire.example-ops.com`. It ingests raw alert payloads, classifies them against a sanitized Governance, Risk, and Compliance (GRC) corpus held in pgvector, retrieves relevant policy and playbook passages, calls external enrichment APIs, and drafts an analyst-style investigation report with explicit framework citations (NIST 800-53, CSF 2.0, MITRE ATT&CK, NIST AI RMF, OWASP LLM Top 10).

The system is a seven-node LangGraph state machine running on top of Anthropic Claude Opus 4.7 (draft, critique, investigate) and Claude Sonnet 4.6 (classification), with `text-embedding-3-large` driving Retrieval-Augmented Generation (RAG). All LLM traffic is observed through Langfuse and gated through a NeMo Guardrails sidecar plus a pre-graph regex scanner that blocks Personally Identifiable Information (PII) before any token is billed.

Squire never performs remediation. It issues recommendations in a controlled vocabulary defined by `actions.yml` (recommend-only mode, see Annex A). Every response carries a citation block pinned to document identifiers retrieved during the RAG step (see Annex B). The system is categorized FIPS 199 LOW for availability and confidentiality of transient alert data. Audit trail integrity is the single MODERATE control family.

The SSP covers the two Squire application containers (`svc-squire`, `svc-nemo`), the four Langfuse containers, and their shared Postgres 16 database (`svc-db` with pgvector extension).

### 1.1 Design Tenets

Six design tenets shape every control decision in this SSP:

1. **Fail closed.** Any exception in any graph node terminates the call and returns a structured error with a Langfuse trace link. The system never returns a partial investigation.
2. **Defense in depth at the LLM boundary.** Four independent layers guard the draft and critique prompts: the pre-graph regex scanner, the NeMo input rail, the NeMo output rail, and the critique citation guard.
3. **Recommend-only, never remediate.** Squire produces text. Humans or downstream SOAR workflows act on that text. The `actions.yml` vocabulary enforces this at the output layer.
4. **Deterministic audit.** Every graph call produces a Langfuse trace. Removing the trace decorator breaks CI. The trace identifier is the primary accountability artifact.
5. **Bounded cost and iterations.** Every node has a cost ceiling and an iteration cap. The graph exits gracefully on exhaustion rather than running unbounded.
6. **Sanitized corpus only.** The RAG corpus is the 31-document GRC library that already went through Phase 9 sanitization. No unsanitized document enters `ir_chunks`.

### 1.2 Control Summary

The controls documented in Section 6 fall into nine families from NIST 800-53 Rev 5 plus a custom Cost and Iteration family specific to agentic systems:

| Family | Count | Notes |
|--------|-------|-------|
| AC (Access Control) | 5 | Token auth, network segmentation, least-privilege container |
| AU (Audit) | 5 | Langfuse + `ir_*` tables, append-only retention |
| CM (Configuration) | 5 | GitOps, pinned dependencies, SBOM |
| IA (Identification) | 3 | Machine-to-machine only, Doppler rotation |
| IR (Incident Response) | 3 | Self-application of the POA&M process |
| RA (Risk Assessment) | 3 | Linked to SQUIRE_AI_RISK_ASSESSMENT |
| SA (Acquisition) | 3 | Secure design, 127-test suite, cosign verification |
| SC (Communications) | 4 | Tunnel ingress, HTTPS egress, Doppler secrets |
| SI (Integrity) | 5 | Four-layer guard stack, Pydantic schemas, retention policy |
| SQ-COST/ITER/LAT (custom) | 4 | Per-call and daily cost ceilings, iteration caps, latency budget |

## 2. System Identification

| Field | Value |
|-------|-------|
| System Name | Squire Autonomous SOC Analyst |
| System Abbreviation | SQUIRE |
| System Owner | System Owner |
| Authorizing Official | System Owner |
| System Type | Minor Application (hosted within parent GSS) |
| Operational Status | Operational |
| Authorization Date | 2026-04-23 |
| Authorization Termination | 2027-04-23 |
| System Location | Single DigitalOcean VPS, NYC1 region |
| External DNS | squire.example-ops.com, langfuse.example-ops.com |
| Parent System | Organization Security Operations Platform (SSP-OPS-001) |

### 2.1 Purpose

Squire replaces the first thirty minutes of a human analyst triage workflow. Alerts arriving from Falco, Datadog, the monitor webhooks, or an operator-initiated replay hit `POST /alert` on `squire.example-ops.com`. Squire returns a structured JSON response within a fixed cost and iteration budget. The response contains: severity classification, a bounded investigation narrative, retrieved policy citations, recommended next actions drawn from the allow-list, and a trace identifier linking back to Langfuse for full prompt/response audit.

### 2.2 Authorization Boundary

The authorization boundary encompasses:

- `svc-squire` (FastAPI + LangGraph 0.2, Python 3.11-slim)
- `svc-nemo` (NeMo Guardrails 0.21.0 sidecar with presidio PII rails)
- `svc-langfuse-web`, `svc-langfuse-worker`, `svc-langfuse-clickhouse`, `svc-langfuse-redis`
- The `ir_*` schema within `svc-db` (Postgres 16 + pgvector 0.7)
- The Cloudflare tunnel routes for `squire.example-ops.com` and `langfuse.example-ops.com`
- `actions.yml` (recommend-only allow-list) and the Colang rail files under `builds/squire/app/rails/`
- Configuration managed through Doppler project `coredirective-engine`, config `prd`

Out of boundary:

- The Anthropic API (FedRAMP and external shared-responsibility boundary)
- The OpenAI embeddings endpoint (external)
- The Tavily search API used for enrichment (external)
- DigitalOcean compute and network substrate (parent SSP inheritance)
- Docker runtime and the host Ubuntu 24.04 kernel (parent SSP inheritance)

### 2.3 Information Types

| Information Type | NIST 800-60 Category | Description |
|------------------|----------------------|-------------|
| Alert telemetry | C.3.5.1 | Falco syscall JSON, Datadog monitor webhooks, operator-submitted payloads |
| LLM prompts and completions | C.3.5.3 | Request/response bodies persisted to Langfuse Postgres + ClickHouse for 30 days |
| Retrieval embeddings | C.3.5.3 | 1024-dimension float vectors in `ir_chunks.embedding` |
| Investigation reports | C.3.5.1 | Structured JSON returned to callers; not persisted beyond Langfuse trace retention |
| Configuration and secrets | C.2.8.1 | Doppler-managed API keys (Anthropic, OpenAI, Tavily, Langfuse, Postgres) |

## 3. System Description

### 3.1 Architecture Overview

Squire runs as a deterministic state machine. Each incoming `/alert` request executes seven nodes in order: `pre_graph_pii_scan` (regex, pre-LLM), `classify`, `retrieve`, `enrich`, `investigate`, `draft`, `critique`. The graph fails closed on any node exception and returns a structured error response with a `reason_code` and the Langfuse `trace_id`.

```
+---------------------------------------+
|  Caller (curl / n8n / operator UI)    |
+---------------------+-----------------+
                      |  HTTPS (Cloudflare tunnel)
                      v
+---------------------------------------+
|  svc-squire (FastAPI, port 8787)      |
|  +---------------------------------+  |
|  | pre_graph_pii (regex, 0 ms)     |  |
|  +---------------------------------+  |
|  | classify  (Sonnet 4.6)          |  |
|  | retrieve  (pgvector, top-k=6)   |  |
|  | enrich    (Tavily optional)     |  |
|  | investigate (Opus 4.7)          |  |
|  | draft     (Opus 4.7)            |  |
|  | critique  (Opus 4.7, bounded)   |  |
|  +----+------------+--------+------+  |
+-------|------------|--------|---------+
        |            |        |
        v            v        v
+---------------+ +--------+ +---------------+
| svc-nemo      | | svc-db | | Langfuse      |
| (Colang rails | | (ir_*) | | (4 containers)|
|  on draft +   | | pgvector| | traces, cost, |
|  critique)    | |         | |  eval         |
+---------------+ +--------+ +---------------+
        |
        v
+---------------+
| Anthropic /   |
| OpenAI /      |
| Tavily (HTTPS)|
+---------------+
```

### 3.2 Runtime Services

| Container | Image | Role | Network | Port |
|-----------|-------|------|---------|------|
| `svc-squire` | Built locally, python:3.11-slim base | FastAPI app, LangGraph executor | net-ai | 8787 |
| `svc-nemo` | `nvidia/nemo-guardrails:0.21.0` | Rail evaluator, presidio PII | net-ai | 8000 |
| `svc-langfuse-web` | `langfuse/langfuse:3` | Trace UI + REST ingest | net-ai | 3000 |
| `svc-langfuse-worker` | `langfuse/langfuse-worker:3` | Background ingest, eval jobs | net-ai | - |
| `svc-langfuse-clickhouse` | `clickhouse/clickhouse-server:24.11` | Trace analytics store | net-ai | 9000 |
| `svc-langfuse-redis` | `redis:7-alpine` | Queue, rate limits | net-ai | 6379 |
| `svc-db` | `pgvector/pgvector:pg16` | Shared Postgres with `ir_*` tables | net-core | 5432 |

### 3.3 LLM Backend Abstraction

A three-mode abstraction (`api`, `max`, `ollama`) lives in `builds/squire/app/llm_backend.py`. The default mode is `api` (Anthropic HTTPS). On 402/429/503 from Anthropic, or when `ANTHROPIC_CREDIT_EXHAUSTED=1` is set, the backend falls back to `ollama` against the local `svc-ollama` service. `max` mode targets the OpenClaw gateway on `http://172.17.0.1:18789/v1/chat/completions` for Max-plan routing.

The abstraction isolates node code from backend quirks. Every node requests a completion with only the fields `model`, `messages`, `system`, `max_tokens`, and `temperature`. The backend layer translates these into the provider's wire format. Ollama responses that lack `usage` accounting are treated as `cost_usd=0` with a `degraded_accounting=true` flag so the critique can note that cost observability is limited during fallback.

The decision ladder for backend selection is deterministic:

1. If the container's `LLM_BACKEND_MODE` env var is set to `max`, route to OpenClaw. If OpenClaw returns non-2xx on three consecutive calls, fall through to step 2.
2. If `ANTHROPIC_CREDIT_EXHAUSTED=1`, skip Anthropic entirely. Otherwise call Anthropic.
3. On Anthropic 402 specifically, set `ANTHROPIC_CREDIT_EXHAUSTED=1` for the process lifetime and retry on ollama.
4. If ollama returns 5xx, the graph returns `reason_code=DEGRADED_MODE_EXHAUSTED` and a 503 to the caller.

Model routing per node:

| Node | Model | Rationale |
|------|-------|-----------|
| classify | `anthropic/claude-sonnet-4-6` | Cheap, fast, structured output |
| retrieve | n/a (pgvector) | Local cosine similarity |
| enrich | `anthropic/claude-sonnet-4-6` | Web search summarization |
| investigate | `anthropic/claude-opus-4-7` | Multi-step reasoning over retrieved chunks |
| draft | `anthropic/claude-opus-4-7` | Final narrative composition |
| critique | `anthropic/claude-opus-4-7` | Citation validator + severity sanity check |
| embeddings | `openai/text-embedding-3-large` | 1024-dim vectors (see ADR 001) |

## 4. Security Categorization

FIPS 199 categorization reflects the scope of a recommendation-only system.

| Objective | Level | Rationale |
|-----------|-------|-----------|
| Confidentiality | LOW | Alert payloads carry infrastructure telemetry, not regulated data. The pre-graph PII scanner blocks SSN, credit card, phone, and email strings at 0 ms before any LLM call. |
| Integrity | MODERATE | Citation integrity matters. A fabricated NIST or ATT&CK code undermines the entire value proposition. The critique node plus the citation guard enforce this. Langfuse trace immutability is the audit anchor. |
| Availability | LOW | Squire is offline-tolerant. When the Anthropic API returns 402, the backend falls back to ollama. When ollama is down, callers receive a 503 with `reason_code=DEGRADED_MODE_EXHAUSTED` and escalate to a human. |

Overall system category: MODERATE (driven by integrity).

## 5. Data Flow and Classification

### 5.1 Inbound Data

| Source | Path | Classification | Retention |
|--------|------|----------------|-----------|
| Falco eBPF alerts | via `svc-detection-router` webhook to `POST /alert` | Internal telemetry | Langfuse 30 days |
| Datadog monitor webhooks | Cloudflare tunnel to `POST /alert` | Internal telemetry | Langfuse 30 days |
| Operator replay | authenticated `POST /alert` with `x-squire-replay: true` | Internal telemetry | Langfuse 30 days + `ir_replay_events` permanent |
| RAG corpus | `ir_chunks` seeded from 31 sanitized GRC docs | Public (already sanitized) | Permanent until reindex |

### 5.2 Outbound Data

| Destination | Content | Transport | PII Exposure |
|-------------|---------|-----------|--------------|
| Anthropic API | System prompt + user alert summary + retrieved chunks | HTTPS | Blocked by pre-graph scanner and NeMo rails |
| OpenAI embeddings | Chunk text for ingestion only (not alert bodies) | HTTPS | None by design (corpus pre-sanitized) |
| Tavily search | Query strings derived from `classify` output | HTTPS | None (classifier strips identifiers) |
| Langfuse | Full prompt/response pairs including rail decisions | HTTPS to `langfuse.example-ops.com` | Blocked content is tagged `__NEMO_BLOCK__` with reason code; raw PII never reaches the LLM so never reaches the trace |

### 5.3 Data at Rest

| Store | Content | Encryption |
|-------|---------|------------|
| `svc-db` (`ir_chunks`, `ir_incidents`, `ir_replay_events`) | Vector corpus, replay audit | LUKS at the volume layer; `db-data-volume` |
| `svc-langfuse-clickhouse` | Trace analytics | LUKS at the volume layer |
| `svc-langfuse-redis` | Queue state | Ephemeral, no disk persistence |
| Doppler | API keys | Provider-managed (Doppler KMS) |

### 5.4 Classification Decisions and Rationale

Alert telemetry is classified as Internal rather than Regulated because the corpus already went through the Phase 9 sanitization process. Real infrastructure identifiers (IP addresses, hostnames, service names) were replaced with the sanitized equivalents (10.100.1.10, alpha-node, svc-*). The residual concern is that live operators submitting replay alerts may include unsanitized content in the raw payload. The pre-graph PII scanner is the primary mitigation; `docs/grc/SQUIRE_AI_RISK_ASSESSMENT.md` risk R-02 tracks this.

Investigation reports are not persisted beyond Langfuse trace retention. The caller receives the JSON and is responsible for downstream storage. This is a deliberate choice: Squire behaves like a stateless function call with a trace side-effect. It does not maintain a case file of its own.

Embeddings in `ir_chunks.embedding` are 1024-dimension float32 vectors. The decision to use 1024 dimensions (rather than the native 3072 from `text-embedding-3-large`) reduces storage by 3x and index build time by roughly 4x at the cost of modest recall. ADR 001 in `docs/grc/ADR_001_EMBEDDING_PROVIDER.md` records the rationale.

### 5.5 Retention and Disposition

| Data | Retention | Disposition |
|------|-----------|-------------|
| Langfuse traces (all nodes, including PII block rows) | 30 days | Langfuse worker cron truncates older rows from ClickHouse |
| `ir_replay_events` | Indefinite | Manually purged on decommission |
| `ir_pregraph_blocks` | 180 days | Postgres cron `vacuum_old_blocks` |
| `ir_sanitization_events` | 180 days | Postgres cron `vacuum_old_blocks` |
| `ir_chunks` | Until reindex | Replaced atomically on re-embedding |
| Nightly `pg_dump` in DO Spaces | 14 days | Spaces lifecycle rule on `nightly/` prefix |

## 6. Control Implementation (NIST 800-53 Rev 5)

This section covers only controls that are Squire-specific. Inherited controls (physical, personnel, most platform controls) are listed in Section 7.

### 6.1 AC - Access Control

| Control | Status | Implementation | Evidence |
|---------|--------|----------------|----------|
| AC-2 | Implemented | Only the System Owner has credentials to Doppler config `prd`. Squire reads secrets at container start via `doppler run --`. No user accounts exist inside the Squire application itself. | `builds/squire/docker-compose.yaml` env block |
| AC-3 | Implemented | `POST /alert` requires header `x-squire-token` validated against Doppler secret `SQUIRE_INGEST_TOKEN`. Missing or mismatched token returns 401. | `builds/squire/app/api.py::require_token` |
| AC-4 | Implemented | Three Docker networks isolate traffic: `net-ai` (LLM path), `net-core` (database), `net-monitoring` (Langfuse emit). `svc-squire` joins `net-ai` and `net-core` only. | `builds/squire/docker-compose.yaml` networks block |
| AC-6 | Implemented | Least privilege on container filesystem: `USER 10001:10001`, `read_only: true`, `tmpfs` for `/tmp`. No `CAP_*` added; `no-new-privileges` set. | `builds/squire/Dockerfile` + compose security_opt |
| AC-17 | Implemented | All remote administration goes through the Cloudflare zero-trust tunnel or SSH on `alpha-node`. Neither the application nor Langfuse listen on the public internet. | Parent SSP inheritance plus tunnel config |

### 6.2 AU - Audit and Accountability

| Control | Status | Implementation | Evidence |
|---------|--------|----------------|----------|
| AU-2 | Implemented | Four audit event types: (1) every `/alert` call emits a Langfuse trace with cost, latency, rail outcomes; (2) every pre-graph block writes a row to `ir_pregraph_blocks`; (3) every recommend-only rewrite writes to `ir_sanitization_events`; (4) every replay writes to `ir_replay_events`. | `builds/squire/app/audit.py` |
| AU-3 | Implemented | Audit records include: timestamp, trace_id, node_name, model_id, input_hash, output_hash, rail_name, reason_code, cost_usd, latency_ms. | Langfuse schema + `ir_*` DDL in migrations/002 |
| AU-6 | Implemented | Daily automated review: a cron job queries Langfuse for traces with `rail_triggered=true` and posts a summary to Telegram `@Coredirective_bot`. Weekly human review of red-team regression runs. | `builds/squire/scripts/daily_audit.py` |
| AU-9 | Implemented | Langfuse writes are append-only from the worker's perspective. The Postgres table holding traces has REVOKE UPDATE, DELETE on the service role. Offsite backup via nightly `pg_dump` to DO Spaces (14-day retention). | `svc-db` role `langfuse_rw` grants INSERT, SELECT only |
| AU-12 | Implemented | Audit generation is immutable at the code path: every graph node is instrumented with `@observe()` from `langfuse.decorators`. Removing the decorator breaks CI because `tests/test_trace_coverage.py` enumerates nodes. | `builds/squire/tests/test_trace_coverage.py` |

### 6.3 CM - Configuration Management

| Control | Status | Implementation | Evidence |
|---------|--------|----------------|----------|
| CM-2 | Implemented | Baseline is the `docker-compose.yaml` in `builds/squire/` plus the Dockerfile plus `requirements.txt` pinned to exact versions. The baseline is checked into Git and tagged per release. | `builds/squire/requirements.txt` (107 pinned deps) |
| CM-3 | Implemented | All changes flow through a GitHub pull request. Pre-commit hooks run `ruff`, `mypy`, and `pytest -k redteam` locally. CI runs the full suite plus Trivy on the built image. | `.github/workflows/squire-ci.yml` |
| CM-6 | Implemented | Configuration is split between version-controlled files (Dockerfile, compose, rails, actions.yml) and Doppler-managed secrets. No runtime configuration writes exist. | Doppler audit log |
| CM-7 | Implemented | The container runs only the FastAPI process plus a healthcheck. No shell, no package manager, no extra binaries. `pip install --no-cache-dir` with `--no-deps` verified. | Dockerfile layer count = 7 |
| CM-8 | Implemented | Component inventory lives in `builds/squire/SBOM.spdx.json` produced by `syft` on every image build. | CI artifact on every successful build |

### 6.4 IA - Identification and Authentication

| Control | Status | Implementation | Evidence |
|---------|--------|----------------|----------|
| IA-2 | Implemented | Machine-to-machine only. No human users authenticate to Squire. Every inbound call presents `x-squire-token`. | Parent SSP covers human auth to the droplet |
| IA-5 | Implemented | Tokens rotate via Doppler. Rotation cadence is quarterly. Old tokens are revoked atomically by updating Doppler and recreating the container. | Doppler secret versioning |
| IA-8 | Not Applicable | No non-organizational users. | - |

### 6.5 IR - Incident Response

| Control | Status | Implementation | Evidence |
|---------|--------|----------------|----------|
| IR-4 | Implemented | Squire is itself an incident-handling tool. Incidents against Squire (rail bypass, prompt injection success) are captured in `docs/grc/REDTEAM_RESULTS.md` and tracked as POA&M entries. | `docs/grc/REDTEAM_RESULTS.md` |
| IR-5 | Implemented | Every `/alert` call is monitored through Langfuse. Latency P95 budget is 45 seconds. Cost budget per call is $0.75. Violations fire a Datadog monitor. | Datadog monitor ID `squire_cost_ceiling` |
| IR-6 | Implemented | Rail triggers and pre-graph blocks route to Telegram within 30 seconds via the `svc-event-handler` path. | `builds/squire/app/alerting.py` |

### 6.6 RA - Risk Assessment

| Control | Status | Implementation | Evidence |
|---------|--------|----------------|----------|
| RA-3 | Implemented | Risk assessment for Squire is documented in `docs/grc/SQUIRE_AI_RISK_ASSESSMENT.md` covering ten agent-specific risks with heat-map and treatment plan. | `docs/grc/SQUIRE_AI_RISK_ASSESSMENT.md` |
| RA-5 | Implemented | Trivy scans run on every `svc-squire` image build. Critical CVEs fail the CI pipeline. A separate nightly Trivy pass tracks drift. | `.github/workflows/squire-ci.yml` Trivy step |
| RA-9 | Implemented | Supply-chain risk is bounded: only `python:3.11-slim` base, all Python deps pinned, `pip-audit` in CI, signature verification on the final image via `cosign`. | `.github/workflows/squire-ci.yml` cosign step |

### 6.7 SA - System and Services Acquisition

| Control | Status | Implementation | Evidence |
|---------|--------|----------------|----------|
| SA-8 | Implemented | Secure design principles applied: fail closed, defense in depth (pre-graph regex plus NeMo rails plus critique validator), least privilege (no remediation capability, recommend-only), separation of duties (model routing ensures no single prompt decides severity and citations). | This SSP |
| SA-11 | Implemented | Security testing is continuous: pytest suite has 127 tests including 24 red-team regression cases. All 127 passing as of 2026-04-23. | `builds/squire/tests/` |
| SA-15 | Implemented | Development tooling is minimal: `uv`, `ruff`, `mypy`, `pytest`. No proprietary build server. | `builds/squire/pyproject.toml` |

### 6.8 SC - System and Communications Protection

| Control | Status | Implementation | Evidence |
|---------|--------|----------------|----------|
| SC-7 | Implemented | Only `svc-squire` receives external traffic through the Cloudflare tunnel. `svc-nemo`, Langfuse, and `svc-db` are on internal networks only. | `builds/squire/docker-compose.yaml` ports block shows `svc-squire` binding `127.0.0.1:8787` |
| SC-8 | Implemented | All external API calls use HTTPS. Cloudflare tunnel terminates TLS at the edge and re-encrypts to the container. | Cloudflare config |
| SC-12 | Implemented | Cryptographic keys (API keys) live in Doppler. Rotation is quarterly for external API keys and on-demand for the ingest token. | Doppler rotation log |
| SC-28 | Implemented | Data at rest in the `ir_*` tables is encrypted at the volume layer (parent SSP). Langfuse trace data has the same treatment. | Parent SSP LUKS coverage |

### 6.9 SI - System and Information Integrity

| Control | Status | Implementation | Evidence |
|---------|--------|----------------|----------|
| SI-3 | Not Applicable | Squire accepts no user uploads; alert payloads are structured JSON from trusted internal sources. | - |
| SI-4 | Implemented | Four independent integrity checks per `/alert`: (1) pre-graph regex PII scanner; (2) NeMo Colang input rail on draft input; (3) NeMo Colang output rail on draft output; (4) critique node validates citations against retrieved chunk IDs. | `builds/squire/app/graph/` + `builds/squire/app/rails/` |
| SI-7 | Implemented | Structured output validation: the graph returns a Pydantic model. Any deviation from the schema causes a 500 with `reason_code=SCHEMA_VIOLATION`. | `builds/squire/app/schemas.py` |
| SI-10 | Implemented | Input validation on `/alert`: Pydantic model with size cap (64 KiB), required fields, and the pre-graph PII scanner. | `builds/squire/app/schemas.py::AlertInput` |
| SI-12 | Implemented | Information handling and retention: Langfuse retains 30 days. `ir_replay_events` retains indefinitely. PII blocks are retained as the blocked reason code only, never the raw input. | `builds/squire/app/audit.py` |

### 6.10 Cost and Iteration Controls (custom family, no direct 800-53 analog)

| Control | Status | Implementation | Evidence |
|---------|--------|----------------|----------|
| SQ-COST-1 | Implemented | Per-call cost ceiling of $0.75 enforced in `builds/squire/app/cost_guard.py`. The guard tracks cumulative Anthropic spend returned in response headers (`anthropic-input-tokens`, `anthropic-output-tokens`) and aborts the graph if the budget would be exceeded on the next node. Aborted calls return 402 with `reason_code=COST_CEILING_EXCEEDED`. | `builds/squire/app/cost_guard.py` |
| SQ-COST-2 | Implemented | Daily cost ceiling of $10.00 tracked in Redis counter `squire:cost:daily:<yyyy-mm-dd>`. Reset at UTC midnight. When exceeded, the LLM backend abstraction transparently switches to `ollama` mode and a Telegram alert fires. | `builds/squire/app/cost_guard.py::daily_budget_check` |
| SQ-ITER-1 | Implemented | The investigate node has a hard loop cap of 3 iterations. The critique node has a hard loop cap of 2. Exceeding either returns the best response so far with a `degraded=true` flag. | `builds/squire/app/graph/investigate.py` |
| SQ-LAT-1 | Implemented | Per-call latency budget of 45 seconds (P95). Exceeded calls fire a Datadog monitor tagged `service:squire severity:warn` and log a span with `latency_budget_exceeded=true`. | Datadog monitor ID `squire_latency_p95` |

## 7. Control Inheritance from Parent SSP

The following control families are inherited without modification from SSP-OPS-001:

| Family | Scope | Inheritance |
|--------|-------|-------------|
| PE (Physical) | Full | DigitalOcean NYC1 facility |
| PS (Personnel) | Full | Single System Owner |
| MP (Media) | Partial | Parent covers drive sanitization; Squire adds PII scanner at application layer |
| PL (Planning) | Full | Parent continuous monitoring strategy applies |
| SC (Comm.) | Partial | Parent covers tunnel; Squire adds network segmentation |
| CP (Contingency) | Full | Parent disaster recovery covers droplet snapshot |

## 8. System Interconnections

| External System | Purpose | Data Direction | Protocol | Authentication |
|-----------------|---------|----------------|----------|----------------|
| Anthropic API | LLM inference (Opus 4.7, Sonnet 4.6) | Outbound | HTTPS | Bearer API key from Doppler `ANTHROPIC_API_KEY` |
| OpenAI API | Embeddings for RAG (`text-embedding-3-large`, 1024 dim) | Outbound, corpus only | HTTPS | Bearer API key from Doppler `OPENAI_API_KEY` |
| Tavily | Enrichment web search (optional, skippable) | Outbound | HTTPS | Bearer API key from Doppler `TAVILY_API_KEY` |
| DO Spaces | Nightly Postgres backups | Outbound | HTTPS | S3 access key from Doppler `SPACES_ACCESS_KEY` / `SPACES_SECRET_KEY` |
| Falco / Datadog / n8n | Alert ingest callers | Inbound | HTTPS via Cloudflare tunnel | `x-squire-token` header |
| OpenClaw gateway | Optional Max-plan routing | Outbound | HTTP (loopback 172.17.0.1:18789) | Gateway-managed |

Each interconnection has a documented fallback or skip behavior. Anthropic failure falls through to ollama. OpenAI failure aborts corpus reindex but does not affect runtime (embeddings are pre-computed at ingest, not per call). Tavily failure logs a warning and the enrich node returns the alert unchanged. DO Spaces failure retries on the next cron run. Caller authentication failure returns 401 and is rate-limited to 5 requests per minute per source IP.

The interconnection footprint is intentionally small. Six external dependencies total. Two of them (OpenAI embeddings and DO Spaces) execute outside the request path, so runtime latency is governed by three endpoints only: Anthropic, Tavily, Cloudflare.

## 9. Authorization Boundary

Squire's authorization boundary is the union of:

1. All code under `builds/squire/` (FastAPI app, LangGraph nodes, Colang rails, tests, Dockerfile, compose)
2. The `ir_*` schema in `svc-db`
3. The four Langfuse containers and their volumes (`CD_VOL_LANGFUSE_*`)
4. The Cloudflare DNS and tunnel route configurations for `squire.example-ops.com` and `langfuse.example-ops.com`
5. The `actions.yml` file defining the recommend-only vocabulary

### 9.1 Network Segmentation Inside the Boundary

The three Docker networks are cryptographically isolated by Docker bridge VLAN tagging. Squire verifies this isolation through four assertions in `tests/test_network_isolation.py`:

1. `svc-squire` can reach `svc-db:5432` (pass).
2. `svc-squire` can reach `svc-nemo:8000` (pass).
3. `svc-squire` cannot reach `svc-gateway:3080` (fail-expected).
4. `svc-squire` cannot reach `svc-datadog:8125` directly; Datadog emission goes through the host agent on 127.0.0.1 (fail-expected).

The assertions run on every CI build and on a daily scheduled workflow against the live droplet. Failure pages the System Owner within five minutes via Datadog monitor `squire_network_isolation_drift`.

### 9.2 Ingress Path Verification

Cloudflare tunnel configuration is managed through Terraform in `terraform/cd-do-infrastructure/cloudflare_tunnel.tf`. The relevant resource is `cloudflare_tunnel_config.cd_alpha` with three routes: `squire.example-ops.com -> http://localhost:8787`, `langfuse.example-ops.com -> http://localhost:3000`, and existing `n8n.example-ops.com` and `ssh.example-ops.com` routes carried forward.

Ingress verification runs on a daily cron:

```
curl -sf https://squire.example-ops.com/health || alert
curl -sf https://langfuse.example-ops.com/api/public/health || alert
```

Both endpoints require no authentication and return `{"status":"ok"}` with HTTP 200. The ingest endpoint `/alert` is authenticated separately.

## 10. Assumptions and Constraints

Assumptions:

- The pre-graph PII scanner's regex coverage (SSN, Luhn CC, email, US phone) is sufficient for the demo threat model. Non-US phone formats and uncommon PII types are an accepted residual risk tracked in the Risk Assessment.
- The 31-document GRC corpus is already sanitized per `SANITIZATION_KEY.md`. No new unsanitized documents enter `ir_chunks` without review.
- The Cloudflare tunnel is the only public ingress.
- Anthropic API cost is bounded by both the daily ceiling ($10) and the per-call ceiling ($0.75).

Constraints:

- Squire never executes remediation. The `actions.yml` vocabulary is phrased as recommendations (see Annex A).
- Squire never deletes or updates rows in `ir_chunks` at runtime. Corpus mutation is an offline ingest process.
- Squire never exposes Langfuse trace content directly to callers. Callers receive the `trace_id` string only.

## Annex A: actions.yml Recommend-Only Mode

`builds/squire/app/actions.yml` defines the controlled vocabulary Squire uses when producing the "Recommended Actions" section of an investigation. Every verb is framed as a recommendation to a human operator. The rail pipeline enforces two modes: `rewrite` (default) and `reject`.

Default mode `rewrite` behavior:

- Forbidden verbs (kill, delete, revoke, disable, block, isolate, terminate, quarantine) are detected by regex.
- Each match is prepended with `RECOMMEND: human operator should ` and the original verb is softened (kill -> stop, delete -> remove, revoke -> rotate, disable -> pause).
- A `sanitization_events[]` array is appended to the response listing each rewrite with its original and rewritten form.

The `reject` mode is opt-in for callers that prefer a hard failure over a rewritten response. In this mode the rail returns `reason_code=ACTION_NOT_ALLOWED` and the graph short-circuits after `draft`.

Example allow-list excerpt (non-exhaustive):

```yaml
actions:
  recommend_investigation:
    verbs: [investigate, review, examine, correlate, monitor]
    safe: true
  recommend_response:
    verbs: [notify, escalate, document, report]
    safe: true
  forbidden_remediation:
    verbs: [kill, delete, revoke, disable, block, isolate, terminate, quarantine]
    enforcement_mode: rewrite
    rewrite_prefix: "RECOMMEND: human operator should "
```

Criterion #16 of the ROADMAP success criteria is satisfied: this SSP documents the `actions.yml` recommend-only mode explicitly.

## Annex B: Citation Guard Design

The critique node is Squire's citation guard. Its job is to reject any investigation narrative that cites a framework code Squire did not retrieve. The guard runs in four passes:

1. **Shape check.** Every cited code must match a known shape: NIST 800-53 `^[A-Z]{2}-\d{1,2}(\(\d+\))?$`; CSF 2.0 subcategory `^(GV|ID|PR|DE|RS|RC)\.[A-Z]{2}-\d{2}$`; MITRE ATT&CK `^T\d{4}(\.\d{3})?$` or `^TA\d{4}$`; AI RMF `^(GV|MP|MS|MG)-\d+\.\d+$`; OWASP LLM `^LLM(0[1-9]|10)$`.
2. **Provenance check.** Every citation must appear either in a chunk retrieved by the `retrieve` node or in the hard-coded framework registry at `builds/squire/app/frameworks.py`. Citations from neither source are stripped.
3. **Consistency check.** The severity claimed in the draft must match the severity produced by the classifier. If the draft tries to downgrade a HIGH classification to INFO (see REDTEAM_RESULTS case 05), the critique node overrides.
4. **Action check.** The recommended actions section is cross-referenced against `actions.yml`. Forbidden verbs are rewritten or the response is rejected per mode.

Citation guard outputs are themselves logged to Langfuse as a named span `critique.citation_guard` with fields: `shape_failures`, `provenance_failures`, `consistency_overrides`, `action_rewrites`. These fields feed the daily audit job.

Criterion #17 of the ROADMAP success criteria is satisfied: the citation guard design is documented here and referenced from `docs/grc/GUARDRAILS_CONFIGURATION.md`.

## Annex C: Operational Runbook Summary

The full Squire operational runbook lives in `docs/context/rules-of-engagement.md` and the deployment notes in `.planning/phases/17-squire-autonomous-soc-analyst/`. This annex captures the operator-facing procedures an SSP reviewer needs to understand how the system is run day to day.

### C.1 Deploy Sequence

1. Author change in `builds/squire/` branch off `main`.
2. Open PR; CI runs pytest (127 tests), Trivy, ruff, mypy, SBOM, and container signature verification.
3. On merge, GitHub Actions builds and pushes `ghcr.io/et-sec/squire:<sha>` and `:latest`.
4. Operator SSH to `alpha-node` and runs `docker compose pull svc-squire && docker compose up -d svc-squire`.
5. Healthcheck polls `https://squire.example-ops.com/health` until 200 or 60 seconds elapsed.
6. Smoke test: a canary alert fires through `POST /alert` with a known Falco shell fixture. The expected output is severity HIGH with four citations and total cost under $0.40.

### C.2 Rollback Sequence

Each container has a `:pre-17-10` image tag pinned on the droplet (see `/opt/platform/ROLLBACK_TAGS.md`). A rollback is:

1. `docker compose stop svc-squire svc-nemo`
2. Restore the previous `docker-compose.yaml` snapshot from `/opt/platform/snapshots/<date>/`
3. `docker compose up -d svc-squire svc-nemo`
4. Healthcheck

The rollback is verified against parent SSP control CP-10.

### C.3 Incident Response Playbook Reference

Incidents against Squire are handled per `docs/grc/PLAYBOOK_AI_INCIDENT.md`. The three most likely scenarios are:

- **Prompt injection success**: Response cites unauthorized severity. The rail analyst runs `scripts/replay.py <trace_id>`, confirms with the critique's citation guard log, opens a POA&M entry, adds the attack string to `tests/redteam/`, and redeploys.
- **PII leak through retrieve node**: A chunk in `ir_chunks` contains unsanitized content. Analyst queries `SELECT id, doc_id FROM ir_chunks WHERE embedding <-> <offending_vec> < 0.1 LIMIT 20`, removes the chunk, re-ingests with sanitization, and updates `SANITIZATION_KEY.md`.
- **Cost runaway**: Daily ceiling hit. Backend switches to ollama automatically. Analyst reviews `langfuse.example-ops.com` cost view to identify the call pattern and tightens `cost_guard.py` thresholds if needed.

### C.4 Capacity Planning

Sustained load target: 20 alerts per hour. Burst target: 120 alerts per hour for 10 minutes. The constraint is Anthropic rate limits (organization-level 4000 RPM Opus) rather than container capacity. `svc-squire` uses asyncio and can handle 50 concurrent `/alert` calls on the current 4-vCPU droplet.

---

## Document Control

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-04-23 | System Owner | Initial authorization |

Related documents:

- `docs/grc/SSP_SYSTEM_SECURITY_PLAN.md` (parent)
- `docs/grc/SQUIRE_AI_RISK_ASSESSMENT.md`
- `docs/grc/FRAMEWORK_CROSSWALK_SQUIRE.md`
- `docs/grc/GUARDRAILS_CONFIGURATION.md`
- `docs/grc/REDTEAM_RESULTS.md`
- `docs/grc/POLICY_AI_GOVERNANCE.md`
- `docs/grc/PLAYBOOK_AI_INCIDENT.md`
