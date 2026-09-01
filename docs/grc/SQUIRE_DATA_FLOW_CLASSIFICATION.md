# Squire Data Flow and Data Classification

**Document ID:** DFC-SQUIRE-001
**Version:** 1.0
**Classification:** Internal Use Only
**Effective Date:** 2026-04-23
**Owner:** Information Security Officer
**Approved By:** System Owner

> **Status note (2026-09-01):** this document describes the DigitalOcean-era baseline as assessed. That environment was retired 2026-08. The platform now runs on an Oracle Cloud (OCI) ARM instance with a partial stack (3 containers live); the remaining services are pending ARM rebuild. A re-baseline of this document is queued and tracked in the POA&M.

---

## Document Control

| Field | Value |
|-------|-------|
| Document ID | DFC-SQUIRE-001 |
| Version | 1.0 |
| Status | Approved |
| Last Revised | 2026-04-23 |
| Next Review | 2026-10-23 |
| Author | Information Security Officer |
| Approver | System Owner |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-23 | Information Security Officer | Initial data classification for Squire alert pipeline |

---

## 1. Purpose

This document classifies every data element that flows through Squire, names the sources and sinks, sets retention windows, and specifies sanitization and encryption controls. It pairs with `docs/grc/diagrams/squire-data-flow.png` which gives the visual topology.

This is the authoritative source for "where does this data live" questions. POLICY_AI_GOVERNANCE.md references this doc for AI-specific data handling.

---

## 2. Data Classes

Squire handles four primary data classes. Each is covered in its own section below.

| ID | Class | Sensitivity | Example |
|----|-------|-------------|---------|
| DC-1 | Alert Payloads | High (may contain secrets in worst case) | Falco shell_in_container event |
| DC-2 | Investigation Records | Medium | ir_investigations row with severity, citations, recommended actions |
| DC-3 | Trace Data | Medium | Langfuse span captures per-node latency, tokens, cost |
| DC-4 | Chunk Embeddings | Low (sanitized GRC corpus) | vector(1024) row with chunk text and source ref |

Sensitivity is ranked relative to the Squire trust boundary. All four classes are classified Internal Use Only at the organization level.

---

## 3. DC-1: Alert Payloads

### 3.1 Sources

- svc-n8n workflows (Falco alert router, gitleaks webhook handler, Datadog signal forwarder)
- Cloudflare Tunnel from external integrations hitting https://squire.example-ops.com/alert
- Per-interview demo clients authenticated with ephemeral tokens

### 3.2 Shape

JSON envelope with:
- `alert_id` (deterministic hash, used for dedup)
- `source` (falco, gitleaks, datadog, manual)
- `severity_hint` (optional, classifier does not trust it)
- `payload` (arbitrary JSON, typically the upstream alert body)
- `timestamp`

### 3.3 Storage

- Primary: `ir_investigations.alert_json` column in svc-db (Postgres 16 + pgvector)
- Secondary: Langfuse input envelope on the root trace (masked)
- Tertiary: Application logs fed to Datadog via fluentd (masked)

### 3.4 Retention

<!-- TODO(et): Verify nightly pg_dump cron is currently scheduled and running. -->
90 days hot in Postgres. Weekly pg_dump to DO Spaces `nightly/` prefix with 14-day retention. Indefinite cold storage via monthly aggregation to DO Spaces `archive/` prefix (Phase 7 procedure preserved).

### 3.5 Sanitization

Two layers before the payload reaches the LLM:

1. `pre_graph_pii.py` regex scanner strips SSN, Luhn-valid credit card, email, phone number. Substitutions are logged to `state.sanitization_events[]`.
2. NeMo input rail applies presidio PII detection at the draft and critique node boundary.

The two layers are deliberate. NeMo v0.21.0 only fronts the nodes configured in its flow; defense-in-depth covers the gap.

### 3.6 Encryption

<!-- TODO(et): DigitalOcean block storage is encrypted at rest by DO by default. Distinguish DO-side encryption from LUKS-on-volume in this line. -->
- At rest: Postgres filesystem volume on alpha-node, LUKS-capable but not currently encrypted at the block layer; Docker Compose volume permissions are 999:999 mode 700.
- In transit: Cloudflare Tunnel terminates TLS at the edge; internal hop from tunnel to svc-squire is HTTP on the Docker bridge network (trust boundary: the host itself).

### 3.7 Access

Teleport-gated SSH to alpha-node is the only path to raw alert payloads. No direct exposure of svc-db beyond the bridge network.

---

## 4. DC-2: Investigation Records

### 4.1 Shape

Row in `ir_investigations` with:
- `investigation_id` (uuid)
- `alert_id` (FK back to DC-1)
- `severity` (LOW|MEDIUM|HIGH|CRITICAL)
- `mitre_techniques[]`
- `csa_manage_codes[]`
- `citations` (JSON array of chunk references)
- `recommended_actions` (rewritten through the allow-list)
- `cost_usd`, `latency_ms`, `trace_id`
- `critique_iterations`, `backend`, `backend_degraded`

### 4.2 Storage

svc-db `ir_investigations` table. Trace correlation via `trace_id` column that points into Langfuse project Squire.

### 4.3 Retention

90 days hot. Monthly aggregate to DO Spaces cold storage preserves the structured record indefinitely for audit.

### 4.4 Sanitization

Recommended actions go through `actions.yml` rewrite enforcement. Forbidden autonomous verbs are prepended with `RECOMMEND: human operator should ...`. This is the single most load-bearing sanitization in the pipeline and is covered under POLICY_AI_GOVERNANCE.md control AI-3.

### 4.5 Access

Same as DC-1 (Teleport to alpha-node). Langfuse UI at https://langfuse.example-ops.com is OAuth-gated for trace correlation.

---

## 5. DC-3: Trace Data

### 5.1 Shape

Langfuse v3 span hierarchy: root LangGraph trace, 7 per-node spans (classify, retrieve, enrich, investigate, draft, critique, route_severity), plus internal `_should_loop` decisions. Each span carries input, output, tokens, cost, latency, and metadata.

### 5.2 Storage

- svc-langfuse-web (ingest), svc-langfuse-worker (async processing)
- svc-langfuse-clickhouse (columnar store, 90-day TTL)
- svc-langfuse-redis (hot cache)

ClickHouse is the long-term trace store. Raw JSON mirrored to DO Spaces `langfuse-traces/` monthly.

### 5.3 Retention

90 days in ClickHouse. Indefinite in DO Spaces (cold).

### 5.4 Sanitization

<!-- TODO(et): Verify Langfuse v3 mask option is actually configured in squire app code. -->
Langfuse masks known secret patterns (`sk-ant-`, `sk-oat-`, bearer tokens, `AKIA` prefixes) at ingest via the SDK's built-in masker. Input envelopes referencing DC-1 payloads inherit the DC-1 sanitization chain.

### 5.5 Encryption

ClickHouse volume is on the same alpha-node disk as svc-db. TLS on the Langfuse UI via Cloudflare Tunnel.

### 5.6 Access

Langfuse UI at https://langfuse.example-ops.com. OAuth via Langfuse's own auth. Owner account only today; team expansion deferred.

---

## 6. DC-4: Chunk Embeddings

### 6.1 Shape

Row in `ir_chunks`:
- `chunk_id` (uuid)
- `doc_id` (source document filename)
- `chunk_text` (cleartext slice, typically 300-800 tokens)
- `embedding vector(1024)` (voyage-3-large output)
- `metadata` (section, category, last_embedded)

HNSW index on `embedding` with `vector_cosine_ops`, `m=16, ef_construction=64`.

### 6.2 Source

Embeddings come from the 31 sanitized GRC documents under `docs/grc/`. Re-embedding is manual today; drift monitoring is called out in section 3.3 of AI_AUDIT_TRAIL_SPEC.md.

### 6.3 Retention

Indefinite. Rebuilt from source on any doc change.

### 6.4 Sanitization

The source documents are already sanitized per SANITIZATION_KEY.md (local, gitignored). Chunks inherit that sanitization; no additional cleaning is applied.

### 6.5 Access

Bridge network only. pgvector query surface is svc-squire exclusively.

---

## 7. Cross-Border Transfer

| Data Class | Leaves the Host | Destination | Legal Basis |
|------------|-----------------|-------------|-------------|
| DC-1 | Yes | Anthropic API (US) as part of prompt context | Anthropic Data Processing Addendum |
| DC-1 | Yes | Voyage AI (US) as part of embedding request (only if new corpus ingested) | Voyage AI Data Processing Addendum (Voyage AI Inc., acquired by MongoDB 2025, US data residency) |
| DC-1 | Yes | Tavily API (US) for enrich-node web search on the `source` field only | Tavily ToS |
| DC-2 | No | N/A | N/A |
| DC-3 | No | N/A (self-hosted Langfuse) | N/A |
| DC-4 | Yes (during embedding only) | Voyage AI (US) | Voyage AI DPA |

No EU-origin personal data is expected in the current demo operating mode. Any expansion to EU-origin data requires a DPIA update before routing through third-party APIs.

---

## 8. PII Handling Matrix

| PII Type | Pre-Graph Regex | NeMo Presidio | Outcome |
|----------|-----------------|---------------|---------|
| SSN | Yes | Yes | Redacted to `[SSN]` |
| CC (Luhn-valid) | Yes | Yes | Redacted to `[CREDIT_CARD]` |
| Email | Yes | Yes | Redacted to `[EMAIL]` |
| Phone | Yes | Yes | Redacted to `[PHONE_NUMBER]` |
| IP address | No | Partial | Passes through (alert signals need IPs) |
| Process path | No | No | Passes through (needed for triage) |

Any sanitization event is logged to `ir_investigations.sanitization_events`.

---

## 9. Deletion Cascade

| Trigger | Deletes |
|---------|---------|
| `DELETE /alert/<id>` (HITL-authorized, not yet implemented) | DC-2 row, linked DC-3 trace by sessionId, DC-1 payload column |
| 90-day retention tick | DC-1 and DC-2 rows older than 90d, DC-3 spans via ClickHouse TTL |
| Doc removal from `docs/grc/` | Corresponding DC-4 rows on next re-embed |

Deletion events are themselves logged to DC-3 (trace of the delete operation) to preserve the audit trail. See AI_AUDIT_TRAIL_SPEC.md section 4.3.

---

## 10. Trust Boundaries

Squire's data flow crosses four trust boundaries. Each is called out here because the control posture differs at each.

### 10.1 External to Cloudflare Tunnel

Any caller hitting https://squire.example-ops.com/alert crosses the first boundary. TLS terminates at Cloudflare's edge. Tunnel authentication on the alpha-node side rejects traffic not carrying a signed tunnel envelope. From the application's perspective, the tunnel is trusted as far as the edge termination goes; the edge itself is Cloudflare's trust domain.

### 10.2 Tunnel to svc-squire

Inside the host, the tunnel decrypts and forwards to svc-squire over HTTP on the Docker bridge network. The boundary here is authentication: the token check (`SQUIRE_WEBHOOK_TOKEN` or an entry in `SQUIRE_INTERVIEW_TOKENS`) is enforced at the FastAPI layer. A caller who reached this point without a valid token receives 401 and is logged.

### 10.3 svc-squire to svc-db and svc-langfuse

Internal service-to-service traffic on the Docker bridge. No TLS, no token. Trust comes from the bridge being host-local and the compose network topology restricting inbound access. The psql role `squire_app` is the granular control; application-layer compromise of svc-squire would still be constrained by role permissions on svc-db.

### 10.4 svc-squire to External AI Providers

Outbound HTTPS to api.anthropic.com and api.voyageai.com. Trust anchored in certificate pinning (Docker base image CA bundle) and provider API key. Defense-in-depth: the pre-graph PII scanner and NeMo rail ensure that even compromised outbound requests do not exfiltrate raw sensitive payloads.

---

## 11. Cross-References

- `docs/grc/diagrams/squire-data-flow.png` (visual topology)
- SQUIRE_MODEL_CARD.md (what the models do with this data)
- AI_AUDIT_TRAIL_SPEC.md (logging specifics)
- HITL_POLICY.md (human gates on DC-2 actions)
- AI_SUPPLY_CHAIN_REGISTER.md (third-party APIs listed in section 7)
- POLICY_AI_GOVERNANCE.md (parent policy)
- DATA_FLOW_DIAGRAM.md (platform-wide data flow, predates Squire)
