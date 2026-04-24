# AI Audit Trail Specification

**Document ID:** AUDIT-AI-001
**Version:** 1.0
**Classification:** Internal Use Only
**Effective Date:** 2026-04-23
**Owner:** Information Security Officer
**Approved By:** System Owner
**NIST 800-53 Controls:** AU-2 (Event Logging), AU-3 (Content of Audit Records), AU-4 (Audit Log Storage Capacity), AU-6 (Audit Record Review), AU-9 (Protection of Audit Information), AU-11 (Audit Record Retention)

---

## Document Control

| Field | Value |
|-------|-------|
| Document ID | AUDIT-AI-001 |
| Version | 1.0 |
| Status | Approved |
| Last Revised | 2026-04-23 |
| Next Review | 2026-10-23 |
| Author | Information Security Officer |
| Approver | System Owner |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-23 | Information Security Officer | Initial audit trail specification for Squire |

---

## 1. Purpose

This specification defines the audit trail for Squire's AI operations. It covers what events are captured, where they are stored, how long they are retained, what integrity properties they hold, who can access them, and how to replay a historical investigation.

Scope is limited to Squire AI-specific evidence. Platform-wide audit requirements (SSH access, container lifecycle, Teleport session records) are handled by the existing platform logging chain and referenced here where they intersect.

---

## 2. Events Captured

Per-invocation audit row is written for every call to `/alert`. The row is the join key across three stores.

### 2.1 Required Fields

| Field | Source | Notes |
|-------|--------|-------|
| `investigation_id` | app generated | UUIDv7, monotonic |
| `alert_id` | dedup hash of input | Same alert retrying hits the dedup cache |
| `trace_id` | Langfuse SDK | Correlation into ClickHouse spans |
| `backend` | LLMBackend active | `api`, `max`, `ollama` |
| `backend_degraded` | Boolean | `true` whenever Ollama fallback fired |
| `severity` | classify node output | LOW, MEDIUM, HIGH, CRITICAL |
| `mitre_techniques[]` | investigate node output | Regex-validated T-codes |
| `csa_manage_codes[]` | investigate node output | CSA Agentic allow-list |
| `citations[]` | draft node output | Chunk references |
| `recommended_actions[]` | draft + actions.yml | Post-rewrite |
| `sanitization_events[]` | pre_graph_pii + NeMo | Pattern, count, node |
| `cost_usd` | sum of node token costs | Enforced against cost ceiling |
| `latency_ms_total`, `latency_ms_per_node` | LangGraph callbacks | Per-node captured |
| `critique_iterations` | _should_loop counter | 0-3 |
| `hitl_gate_triggered` | severity + policy | Boolean |
| `hitl_approver` | populated on approval | User principal |
| `created_at`, `completed_at` | timestamps | UTC |

### 2.2 Rail Events

When a NeMo rail fires, a row is written to `ir_rail_events`:

| Field | Notes |
|-------|-------|
| `investigation_id` | FK to ir_investigations |
| `rail_name` | `input`, `output` |
| `rule_name` | e.g. `presidio_pii` |
| `reason_code` | `PII_DETECTED`, `POLICY_VIOLATION` |
| `snippet_sha256` | SHA-256 of the offending span, never the raw text |
| `node` | `classify`, `draft`, `critique` |

The snippet is never logged in cleartext. Only the SHA-256 digest is kept so the rail firing is verifiable without preserving the leaked content.

### 2.3 HITL Events

When a HITL gate is triggered or resolved:

| Field | Notes |
|-------|-------|
| `event_type` | `requested`, `approved`, `rejected`, `timed_out` |
| `approver` | Principal (from Teleport session or n8n auth context) |
| `reason` | Free text, required on reject |
| `created_at` | UTC |

See HITL_POLICY.md for the lifecycle model.

---

## 3. Storage Locations

Three stores, each with a distinct purpose. Redundancy is deliberate because the risk surface of a single-store design is unacceptable for audit integrity.

### 3.1 Langfuse (Primary Trace)

- svc-langfuse-web (ingest), svc-langfuse-worker (async processing)
- svc-langfuse-clickhouse (columnar span store)
- svc-langfuse-redis (hot cache)

Captures input, output, token counts, cost, latency, and per-node breakdowns. Traces findable by `sessionId` equal to `alert_id`.

### 3.2 Postgres svc-db (Structured Record)

- `ir_investigations` for the row described above
- `ir_rail_events` for rail firings
- `ir_hitl_events` for HITL lifecycle

This is the structured query surface. When an analyst asks "how many HIGH severity invocations in the last 30 days with a NeMo rail firing," this is the store that answers.

### 3.3 Datadog Tier 1 (Operational)

Container logs, latency histograms, error rates. Shipped via fluentd. Structured event objects for `investigation_created`, `cost_ceiling_hit`, `rail_fired`, `backend_degraded`. Scope is limited to operational correlation, not evidence preservation.

---

## 4. Retention

| Store | Hot | Cold |
|-------|-----|------|
| Langfuse ClickHouse | 90 days TTL | Monthly export to DO Spaces `langfuse-traces/` (indefinite) |
| svc-db `ir_*` tables | 90 days retained | Nightly pg_dump to DO Spaces `nightly/` (14 days), monthly snapshot to `archive/` (indefinite) |
| Datadog | 15 days indexed, 1 year archived | Covered by Datadog plan |

### 4.1 Cold Storage Path

Phase 7 established the immutable log export path. Same path is reused here:

1. Monthly cron dumps `ir_*` tables as SQL to `/var/backups/platform/<month>/`
2. `aws s3 cp` uploads to DO Spaces `archive/ir/<month>/`
3. Spaces Object Lock governs the `archive/` prefix with retention set to Retain Until date equal to 7 years from upload
4. SHA-256 manifest written to `archive/ir/<month>/MANIFEST.sha256` before Object Lock engages

### 4.2 Deletion

Deletion events are themselves audited (section 4.3 of SQUIRE_DATA_FLOW_CLASSIFICATION.md). A delete of an `ir_investigations` row writes a tombstone row to `ir_tombstones` with the original `investigation_id`, the deleting principal, and the justification. The tombstone is immutable and survives the 90-day window.

---

## 5. Integrity

Audit integrity follows an append-only-with-witnesses pattern. Not every row is append-only, but every mutation is witnessed.

### 5.1 Append-Only Operations

| Operation | Append-Only | Enforcement |
|-----------|-------------|-------------|
| INSERT into `ir_investigations` | Yes | No UPDATE or DELETE granted to svc-squire role; schema has `CHECK` constraint preventing backdated `created_at` |
| INSERT into `ir_rail_events` | Yes | Same role constraints |
| INSERT into `ir_hitl_events` | Yes | Same role constraints |
| INSERT into `ir_tombstones` | Yes | Same role constraints |
| Langfuse span ingest | Yes | ClickHouse merge tree, no row-level updates |

### 5.2 Mutable Operations

| Operation | Allowed | Notes |
|-----------|---------|-------|
| UPDATE `ir_investigations` SET `completed_at`, `cost_usd`, `latency_ms_total` on same row | Yes | Only between create and close transitions, enforced by status column |
| UPDATE for HITL approval state | Yes | Via `ir_hitl_events` append, not `ir_investigations` update |
| DELETE `ir_investigations` | No direct delete | Delete path writes tombstone + archive, then removes |

### 5.3 Witness Mechanisms

- Langfuse `trace_id` is generated client-side before the first node runs. Retroactively creating a trace would require forging a `trace_id` that matches a persisted row, which would still leave the raw row in cold storage as a witness.
- Monthly manifest in cold storage is SHA-256 over the SQL dump; any after-the-fact row edit would mismatch the manifest.
- Datadog receives a duplicate event stream for operational ops. Divergence between Datadog and svc-db counts is a tripwire.

Full cryptographic notarization (e.g. via a separate append-only log with per-row signatures) is a Phase 18+ hardening target and is called out as a current gap.

---

## 6. Access Control

| Actor | Path | Controls |
|-------|------|----------|
| System owner | Teleport to alpha-node, direct psql | Teleport RBAC, session recording |
| Langfuse UI user | https://langfuse.example-ops.com | Langfuse OAuth, project-scoped |
| Datadog user | us5.datadoghq.com | SSO, role-based |
| svc-squire (application) | psql role `squire_app` | INSERT + limited UPDATE only |
| Auditor (external) | Cold storage read-only presigned URLs | Time-bound, IP-scoped |

Teleport session recordings are the primary control for cold-storage read events. Any psql dump, any archive download, any Langfuse export is recorded under the actor's session.

---

## 7. Replay Procedure

Given an `investigation_id`, a full replay reconstructs every input, every intermediate state, and every output.

### 7.1 Steps

1. `SELECT *` from `ir_investigations`, `ir_rail_events`, `ir_hitl_events` where `investigation_id = ?`
2. Pull Langfuse trace by `sessionId = alert_id` to get per-node inputs and outputs
3. Pull referenced `ir_chunks` rows to verify citations still match
4. If the investigation is older than 90 days, pull from cold storage using the month manifest

### 7.2 Replay Fidelity

| Element | Replayable | Notes |
|---------|------------|-------|
| Raw alert payload | Yes | Stored in `alert_json` column |
| Per-node prompts | Yes | Langfuse captures input envelope |
| Per-node outputs | Yes | Langfuse captures output |
| Model version | Yes | Langfuse model metadata |
| Backend mode | Yes | `backend` column |
| Exact temperature | Not always | Opus 4.7 rejects the parameter; replay shows default |

### 7.3 Re-Execution

Re-running the same alert through a live Squire is not guaranteed to produce the same output because foundation models drift between provider releases. Replay is for evidence, not reproducibility. For regression testing, canonical fixtures in `builds/squire/tests/fixtures/` are the reference.

---

## 8. Evidence Preservation Procedure

Given a request for audit evidence covering a specific investigation or a time window, the following procedure returns a self-contained evidence bundle suitable for external audit.

### 8.1 Bundle Contents

1. `manifest.json` listing every file in the bundle with SHA-256 digests
2. `investigations.csv` row for each investigation in scope
3. `rail_events.csv` with associated rail firings
4. `hitl_events.csv` with HITL lifecycle events
5. `traces/<trace_id>.jsonl` per-investigation trace export from Langfuse
6. `chunks/<chunk_id>.md` materialized citation chunks
7. `README.md` describing the evidence scope and any redactions

### 8.2 Procedure

Commands run from a Teleport-gated session with the auditor-facing role:

1. Authenticate to Teleport, verify the session is recording
2. Run the evidence export script with the scope window: `python -m squire.audit.export --start YYYY-MM-DD --end YYYY-MM-DD --out /tmp/evidence/`
3. Script pulls the structured rows from svc-db, the trace JSONL from Langfuse, and the referenced chunks from `ir_chunks`
4. Script computes SHA-256 over every file and writes `manifest.json`
5. Bundle is tar.gz'd and signed with a cosign key held by the system owner
6. Signed bundle uploaded to DO Spaces `audit-bundles/<requestor>/<date>.tar.gz.sig`
7. Presigned URL returned to the auditor with a 7-day expiration

The signing step is the evidence authenticity anchor. Any tampering with a file in the bundle invalidates the cosign signature. Storage side, Object Lock governs the bundle to prevent in-place modification.

### 8.3 Partial Redaction

When the auditor is not authorized to see certain fields (e.g. raw alert payloads from production integrations during a targeted investigation of a single HITL event), the export script takes a `--redact` flag. Redacted fields are replaced with `[REDACTED]` and the redaction is logged in the bundle's `README.md` with the justification. Redaction does not alter the row hash calculation; the hash is over the post-redaction content, and the unredacted content remains in the live stores for owner-scoped access.

---

## 9. Monitoring

- Datadog monitor on `rail_fired` rate (alert at sustained > 10% of invocations)
- Datadog monitor on `backend_degraded = true` rate (alert at any sustained Ollama fallback)
- Langfuse score distribution review weekly
- Cold storage manifest verification quarterly

---

## 10. Cross-References

- SQUIRE_MODEL_CARD.md (what the evidence proves)
- SQUIRE_DATA_FLOW_CLASSIFICATION.md (where the data comes from)
- HITL_POLICY.md (human-gate events)
- AI_SUPPLY_CHAIN_REGISTER.md (components whose outputs are audited)
- POLICY_AI_GOVERNANCE.md (parent governance)
- PENTEST_SELF_ASSESSMENT.md (audit trail is evidence for pen-test reproducibility)
