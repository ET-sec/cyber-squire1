# HIPAA ePHI Handling and Data Lifecycle

**Document ID:** HIPAA-002
**Version:** 1.0
**Classification:** Internal Use Only
**Effective Date:** 2026-05-25
**Owner:** Information Security Officer
**Approved By:** System Owner
**Pairs With:** HIPAA-001 (HIPAA Security Rule Crosswalk)
**NIST 800-53 Controls:** SC-8 (Transmission Confidentiality), SC-13 (Cryptographic Protection), SC-28 (Protection of Information at Rest), SC-28(1) (Cryptographic Protection), MP-6 (Media Sanitization), MP-7 (Media Use), AU-2 (Event Logging), AU-3 (Content of Audit Records), AU-9 (Protection of Audit Information), AU-11 (Audit Record Retention), AC-2 (Account Management), AC-3 (Access Enforcement), AC-6 (Least Privilege), IA-2 (Identification and Authentication)

---

## Document Control

| Field | Value |
|-------|-------|
| Document ID | HIPAA-002 |
| Version | 1.0 |
| Status | Approved |
| Last Revised | 2026-05-25 |
| Next Review | 2026-11-25 |
| Author | Information Security Officer |
| Approver | System Owner |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-05-25 | Information Security Officer | Initial ePHI handling and lifecycle document, forward-looking readiness, paired with HIPAA-001 |

---

## 1. Purpose

This document defines how the Organization Security Operations Platform (OSOP) would handle Electronic Protected Health Information (ePHI) if a covered entity or business associate engagement required it. It pairs with HIPAA-001 (HIPAA Security Rule Crosswalk) which maps the platform's existing technical, administrative, and physical safeguards to 45 CFR Part 164 Subpart C. HIPAA-001 answers "do the existing controls align to the Security Rule?" This document answers the operational question "what would change in OSOP the day a Business Associate Agreement is signed?"

OSOP does not process ePHI today. No covered entity is on the customer list, no Business Associate Agreement (BAA) is in place with the Organization, and no ePHI dataset has been ingested. The current data inventory is operational telemetry, security alert payloads, sanitized GRC reference content, and platform configuration. This document is a forward-looking readiness specification. It exists so that the controls, schema, and procedures are defined in advance and so a future BAA engagement does not start from zero.

The document also serves as evidence for a reviewer asking "would OSOP be HIPAA-ready in principle?" The answer is qualified yes, contingent on the gaps in section 14 closing before any ePHI is accepted.

---

## 2. ePHI Definition and Identifiers

### 2.1 Protected Health Information

Per 45 CFR 160.103, Protected Health Information (PHI) is individually identifiable health information held or transmitted by a covered entity or its business associate, in any form. Electronic PHI (ePHI) is PHI created, received, maintained, or transmitted in electronic media.

Three elements must combine for data to be ePHI:

1. It relates to past, present, or future physical or mental health, healthcare provision, or payment for healthcare
2. It identifies the individual or there is a reasonable basis to believe it could be used to identify the individual
3. It is held in electronic form

A health-related fact stripped of all identifiers is not ePHI. An identifier with no health context is not ePHI either. Both elements together inside an electronic store make a record ePHI.

### 2.2 The 18 HIPAA Identifiers

Per 45 CFR 164.514(b)(2)(i), the Safe Harbor method of de-identification requires removal of the following 18 identifiers of the individual, relatives, employers, and household members:

| # | Identifier | Examples relevant to OSOP |
|---|-----------|---------------------------|
| 1 | Names | Patient first/last, dependent names |
| 2 | Geographic subdivisions smaller than state | Street address, city, county, ZIP3 unless population > 20,000 |
| 3 | Dates (except year) directly related to individual | DOB, admission date, discharge date, death date |
| 4 | Telephone numbers | Cell, home, work phone |
| 5 | Fax numbers | Provider fax, patient fax |
| 6 | Email addresses | Patient portal email, provider contact email |
| 7 | Social Security Numbers | SSN in any field |
| 8 | Medical record numbers | MRN, EHR account ID |
| 9 | Health plan beneficiary numbers | Insurance member ID |
| 10 | Account numbers | Patient account, billing account |
| 11 | Certificate or license numbers | Provider license, professional cert |
| 12 | Vehicle identifiers and serial numbers | VIN, license plate |
| 13 | Device identifiers and serial numbers | Implant serial, monitoring device ID |
| 14 | Web URLs | Patient portal URL, telemedicine link |
| 15 | IP addresses | Source IP in patient session logs |
| 16 | Biometric identifiers | Fingerprint, voiceprint, retinal scan |
| 17 | Full-face photographic images and comparable images | Patient photo, intake camera capture |
| 18 | Any other unique identifying number, characteristic, or code | Tattoo description, rare condition combination |

Removal of all 18 plus the actual-knowledge clause ("the covered entity does not have actual knowledge that the information could be used alone or in combination to identify the individual") yields a Safe Harbor de-identified dataset. A dataset failing any one of the criteria is still PHI.

### 2.3 Limited Data Set vs De-Identified

Per 45 CFR 164.514(e), a Limited Data Set (LDS) permits retention of city, state, ZIP, elements of date (admission, discharge, service, DOB, death), and limited geographic subdivisions. An LDS is still PHI; it just may be used for research, public health, or healthcare operations under a Data Use Agreement. OSOP treats an LDS with the same controls as full ePHI.

### 2.4 Expert Determination

The alternative to Safe Harbor is Expert Determination under 45 CFR 164.514(b)(1): a qualified statistician determines that the risk of re-identification is very small. OSOP does not currently retain a qualified expert and treats Safe Harbor as the only operational de-identification path.

### 2.5 Designated Record Set

Per 45 CFR 164.501, a Designated Record Set (DRS) is the medical records and billing records used to make decisions about individuals. Patients have access and amendment rights to a DRS. OSOP, as a hypothetical business associate, would not maintain a DRS in the traditional sense, but ePHI passed through OSOP for security analysis would inherit the access and amendment obligations of the upstream covered entity. The BAA governs the propagation of these obligations.

---

## 3. Current ePHI Posture

OSOP processes zero ePHI as of the effective date of this document. The current data inventory is:

| Category | Description | Sensitivity | ePHI Risk |
|---------|-------------|-------------|-----------|
| Security alert payloads | Falco events, gitleaks findings, Datadog signals routed through svc-automation | Internal | None today; some payloads could contain PII from log content if a customer's app logs PII |
| Investigation records | Squire ir_investigations rows, severity, citations, recommended actions | Internal | None today |
| Trace data | Langfuse spans for AI invocations | Internal | None today |
| Chunk embeddings | Vector representations of sanitized GRC corpus | Public-equivalent (sanitized) | None |
| Platform telemetry | Container metrics, host metrics, service logs | Internal | None |
| Identity records | svc-identity user accounts, role assignments, session records | Confidential | None |
| Secrets | Vault-stored API keys, credentials | Restricted | None |
| Backup archives | CD_BACKUPS volume with pg_dump and configuration snapshots | Confidential | None |

No customer in the current OSOP customer list is a covered entity under HIPAA. No upstream system from which OSOP ingests data routes ePHI today. The current GLiNER PII detector configuration scans for generic PII patterns (SSN, email, phone, credit card) but is not tuned for ePHI-specific identifier classes such as MRN format variants or health plan beneficiary numbers.

The honest summary is that OSOP is HIPAA-adjacent in technical maturity (it has the encryption, audit logging, RBAC, and segmentation needed) but has not crossed the operational threshold of accepting ePHI under a BAA.

---

## 4. ePHI Onboarding Decision Gate

Before OSOP accepts any ePHI, the following gate must complete. Each item is a hard requirement, not a checklist suggestion. A single missing item blocks ingest.

### 4.1 Required Items

| # | Item | Owner | Evidence |
|---|------|-------|----------|
| 1 | Signed Business Associate Agreement with the covered entity | System Owner | Counter-signed BAA filed in legal records, hash recorded in audit log |
| 2 | Signed Business Associate Agreement with every downstream subprocessor that may touch ePHI (Anthropic, Cloudflare, Datadog, DigitalOcean) | System Owner | Counter-signed BAAs filed per subprocessor |
| 3 | Sub-flow mapping document identifying every ePHI ingress, processing step, storage location, and egress | Information Security Officer | Sub-flow doc reviewed, approved, version-controlled in docs/grc/ |
| 4 | Dedicated ePHI schema provisioned in svc-db with row-level security policies attached | Information Security Officer | Schema migration applied, schema name `ephi_<tenant>`, RLS policies attested via psql `\dp` output |
| 5 | Vault Transit secrets engine configured with a dedicated ePHI encryption key, key rotation schedule defined | Information Security Officer | Vault policy attached to ephi-operator role, transit key version captured |
| 6 | GLiNER detector tuned for ePHI-specific identifier classes (MRN patterns, beneficiary IDs, diagnosis-code-adjacent text) | Information Security Officer | Detector ruleset versioned, false-positive and false-negative rates baselined against test corpus |
| 7 | ephi-operator role created in svc-identity, distinct from existing admin/operator/auditor roles | Information Security Officer | Role exists, no person assigned by default |
| 8 | Teleport JIT request template configured for ephi-operator access including mandatory minimum-necessary justification field | Information Security Officer | Template visible in Teleport config, JIT request UI surfaces the justification field |
| 9 | Datadog HIPAA-eligible workspace confirmed, Sensitive Data Scanner rules deployed to scrub ePHI from log streams that could traverse svc-monitor | Information Security Officer | Datadog account status verified as HIPAA-eligible, scanner rules version-pinned |
| 10 | Cold-storage retention extended from current default to minimum 6 years for any ePHI-related audit record | Information Security Officer | Object Lock policy on Spaces archive prefix shows 6-year governance window |
| 11 | Breach detection runbook updated to include ePHI-specific notification paths (HHS OCR, individual, media) | Information Security Officer | Runbook section added, contact list verified, internal escalation chain tested |
| 12 | Incident response tabletop run against an ePHI breach scenario | System Owner | Tabletop report filed in incident-response evidence folder |
| 13 | Training acknowledgment from every person who could touch ePHI (currently the System Owner and any Information Security Officer assignee) | System Owner | Signed training acknowledgments in HR-equivalent records |
| 14 | Risk assessment performed against the specific ePHI workload, results integrated into the platform Risk Assessment | Information Security Officer | Updated risk register entry, severity rating, treatment plan |
| 15 | Sub-flow walkthrough demonstration delivered to the covered entity's privacy officer | System Owner | Walkthrough completed, written acceptance recorded |

### 4.2 Gate Outcome

The gate is binary. All 15 items present and verified means ePHI ingestion may begin under the scope defined in the BAA. Any item missing means no ePHI may enter the platform. There is no partial-acceptance mode.

A gate completion record is written to the audit log as a single immutable event with the hash of every supporting artifact. This record is the entry point for any future audit asking "when did OSOP start handling ePHI for tenant X, and under what controls."

---

## 5. Data Classification Levels

OSOP uses four classification tiers. The Regulated tier is new and exists specifically for ePHI and any other data class requiring statutory protection.

### 5.1 Public

Data approved for public disclosure. Examples: sanitized GRC corpus, published architecture diagrams, blog posts.

- No confidentiality requirement
- Integrity protected by source control
- No special storage or transmission controls beyond normal hygiene

### 5.2 Internal

Default classification for operational data. Examples: alert payloads, investigation records, container metrics, service logs.

- Confidentiality: restricted to authorized personnel, encrypted in transit and at rest
- Integrity: change tracking, append-only where applicable
- Logging: standard audit trail per AU-2 and AU-3

### 5.3 Confidential

Sensitive operational and identity data. Examples: identity records, session recordings, backup archives, secret material in Vault.

- Confidentiality: encrypted in transit and at rest, access restricted to specific roles
- Integrity: tamper-evident logging, separation of duties for changes
- Logging: enhanced audit trail with retention 1 year minimum

### 5.4 Regulated

Data subject to statutory protection. ePHI is the primary example. Personal data of EU residents (under GDPR) and U.S. financial account data (under GLBA) would also fall in this tier when those scopes apply.

- Marked **Required** when a BAA is active for the data
- Confidentiality: encrypted in transit using TLS 1.3, encrypted at rest using AES-256 with keys held in Vault Transit, mTLS for inter-service hops where the data crosses the bridge network
- Integrity: full append-only audit trail with tamper-evident storage, 6-year retention
- Access: ephi-operator role only, JIT via Teleport, mandatory minimum-necessary justification, session recording
- Processing: on-premises inference only via svc-llm, no third-party AI API without BAA
- Lifecycle: ingestion gated by BAA, sanitization per NIST 800-88, cryptographic erasure via Vault key destruction on disposal

The Regulated tier inherits all Confidential tier controls and layers additional requirements on top. A Regulated dataset is always treated as the highest-sensitivity item in any composite store.

---

## 6. Permitted and Prohibited ePHI Locations

This section governs where ePHI may and may not reside within OSOP. The list is exhaustive for current services; any new service introduced after this document is published must add a row here as part of its change-management review.

### 6.1 Permitted Locations

| Service | Permitted Use | Required Controls |
|---------|--------------|-------------------|
| svc-db (PostgreSQL) | Storage in dedicated `ephi_<tenant>` schema only | Row-level security policies enforcing tenant isolation; ephi-operator role granted SELECT, INSERT, UPDATE on schema; service role granted INSERT only; daily RLS policy verification; encryption at rest via filesystem-level AES-256 |
| svc-secrets (Vault) | ePHI encryption keys via Transit secrets engine | Dedicated transit key per tenant; key rotation every 90 days; access policy limited to ephi-operator role; audit device emitting to immutable log |
| svc-llm (Ollama, on-premises) | ePHI processing for inference (minimum necessary satisfied by on-prem execution) | Container runs in net-ai network with `internal: true`; no internet egress; model files signed; prompt and completion logs subject to AU-2 retention but stored in ephi-isolated schema |
| svc-tunnel (Cloudflare Tunnel) | ePHI transport between authenticated client and OSOP, conditional on Cloudflare BAA being active | Cloudflare BAA on file; tunnel restricted to ePHI-authorized hostnames; TLS 1.3 minimum at edge; log entries scrubbed of ePHI by Cloudflare Logpush filter |
| CD_BACKUPS volume | Storage of encrypted ePHI backups | Backups encrypted with AES-256 using key derived from Vault Transit; key rotation propagated to backup encryption; backup verification test monthly; physical access controlled by hypervisor provider attestation |
| DO Spaces archive prefix | Cold storage of ePHI-related audit records | Server-side encryption enabled; Object Lock in compliance mode with 6-year governance window; access via Teleport-mediated presigned URL only; manifest hashes verified quarterly |

### 6.2 Prohibited Locations

| Service | Why Prohibited | Compensating Path |
|---------|---------------|-------------------|
| svc-ai-gateway (OpenClaw bridge to Claude API) | No BAA between Organization and Anthropic at this time | Route ePHI inference exclusively through svc-llm on-premises; if Anthropic BAA is signed, this row moves to permitted with conditions |
| Any third-party AI provider API (OpenAI embeddings, Tavily search, perplexity) | No BAA in place with these vendors for the Organization | Use only sanitized derivatives that have passed the GLiNER ePHI ruleset for any inputs leaving the platform; full ePHI never leaves |
| svc-monitor (Datadog) logs and metrics | Logs traverse Datadog ingest pipeline; default Datadog tenancy is not HIPAA-eligible | Datadog Sensitive Data Scanner rules must be deployed to strip ePHI patterns before transmission; if Datadog HIPAA workspace is provisioned and BAA signed, scanner rules remain mandatory as defense-in-depth |
| Application logs at INFO level or higher | Log statements may inadvertently include ePHI from in-flight records | Logger configuration enforces structured logging with explicit allow-list of safe fields; any DEBUG-level statement potentially containing ePHI is gated by a feature flag disabled in production |
| Container stdout/stderr without filtering | Captured by Fluentd and forwarded; filtering occurs downstream which is too late | Code-level prohibition on raw record printing; static analysis rule in CI to flag `print(record)` or equivalent |
| Local developer laptops | Development environment is not under platform controls | ePHI never copied to laptops; debugging uses synthetic data; production access is via Teleport JIT only |
| External email (SMTP, Gmail, third-party mail providers) | Email is unencrypted end-to-end without explicit recipient encryption | ePHI never transmitted via email; notifications about ePHI use record IDs, not record contents |
| Telegram or any consumer messaging platform | No BAA available with consumer messaging providers | ePHI never routed through Telegram; ADHD Commander and other Telegram-integrated workflows are blocked from reading ephi_* schemas |

### 6.3 Network-Level Enforcement

Beyond service-level rules, network policy enforces locations:

- net-ai network (`internal: true`) hosts svc-llm and is the only network permitted to receive ePHI inference requests
- net-core hosts svc-db with the ephi_* schemas behind row-level security
- net-monitoring carries scrubbed telemetry only; firewall rules drop any payload matching ePHI patterns at the egress interface (defense-in-depth even with Sensitive Data Scanner upstream)

---

## 7. Encryption Requirements

### 7.1 At Rest

All ePHI at rest uses AES-256. The implementation layers:

- Filesystem encryption on the alpha-node host disk (LUKS-capable; activation pending the gate item in section 4)
- Application-layer field encryption for designated ePHI columns using a Vault Transit key, so even a database backup leak preserves cyphertext
- Backup archives encrypted independently with a separate Vault Transit key, scoped to the backup operator role

Key material lives only in Vault. Application services never see raw key material; they call the Vault Transit endpoint for encrypt and decrypt operations and receive only the cyphertext or cleartext result. Vault audit device records every encrypt and decrypt call with the requesting principal, the key version, and a timestamp.

NIST 800-53 controls satisfied: SC-13, SC-28, SC-28(1).

### 7.2 In Transit

TLS 1.3 is the minimum version for any ePHI in transit. TLS 1.2 is prohibited even where supported by the peer; the configuration explicitly refuses negotiation below 1.3.

Inter-service traffic on the Docker bridge network uses mTLS where the traffic crosses a trust boundary in the platform's DFD. svc-tunnel to svc-automation, svc-automation to svc-db, and svc-llm to svc-db are the relevant hops. The mTLS rollout is partial today and is called out in section 14.

External transit (svc-tunnel ingress, DO Spaces upload) uses TLS 1.3 enforced by configuration. The Cloudflare edge terminates TLS at the perimeter; the re-encrypted hop from edge to svc-tunnel is itself TLS 1.3 over the Cloudflare-managed tunnel.

NIST 800-53 control satisfied: SC-8.

### 7.3 In Use

Confidential computing (encrypted memory, hardware-attested enclaves) is not currently implemented. ePHI in process memory during a Vault decrypt or an Ollama inference is in cleartext within the container's address space.

This is a known gap. The current compensating controls are:

- Container runtime hardening (CIS Docker Benchmark Level 1 applied)
- Restricted host access via Teleport
- Runtime detection via Falco watching for process injection and unexpected memory reads
- Minimal data residency in memory; records are decrypted at the moment of use and dereferenced immediately

Future enhancement: evaluate hardware enclave deployment (Intel TDX, AMD SEV-SNP) on a successor host class. This is tracked in the platform roadmap as a Phase 20+ item, not immediate.

---

## 8. Access Controls for ePHI

### 8.1 The ephi-operator Role

ePHI access is gated by a single role: ephi-operator. This role is distinct from the existing admin, operator, and auditor roles. The separation is deliberate: an admin can change platform configuration but cannot read ePHI without explicitly assuming the ephi-operator role through a JIT request. An auditor can review audit records about ePHI access but cannot read ePHI itself.

### 8.2 Just-In-Time Access

All ephi-operator access is JIT, mediated by Teleport. The JIT flow:

1. Requestor opens a Teleport access request specifying the role (ephi-operator), the target service, the time window (default 1 hour, maximum 4 hours), and the minimum-necessary justification text
2. Justification text is mandatory and free-form, but must reference the specific record set, the patient or record identifier scope, and the operational reason
3. Approver (System Owner or designated alternate) reviews and approves or denies within the platform; auto-approval is disabled for ephi-operator
4. On approval, the role is attached to the requestor's certificate for the time window; session recording is mandatory and engages automatically
5. On expiration, the role is removed; any continuing session is terminated

### 8.3 Session Recording

Every ephi-operator session is recorded. Recordings include keystrokes, terminal output, and any file operations. Recordings are stored in the Teleport session recording backend, which writes to the DO Spaces audit prefix with Object Lock applied. Recording duration matches the audit retention requirement (6 years).

### 8.4 Minimum Necessary

The Minimum Necessary standard (45 CFR 164.502(b)) requires that ePHI access be limited to the smallest amount needed to accomplish the purpose. OSOP enforces this through:

- Per-request justification (already described)
- Schema-level partitioning so an ephi-operator working with tenant A cannot inadvertently query tenant B's data
- Query auditing that flags broad scans (e.g., `SELECT * FROM ephi_<tenant>.records` without a WHERE clause) for post-hoc review
- Periodic access review covering every ephi-operator session executed in the prior quarter

### 8.5 Separation from Admin

A System Owner acting as platform admin cannot read ePHI by virtue of admin role. The ephi-operator role assignment is a separate JIT request that goes through the same approval flow as any other access request. This means an admin investigating a database issue does not see ePHI unless they explicitly request and justify ephi-operator access.

NIST 800-53 controls satisfied: AC-2, AC-3, AC-6, IA-2.

---

## 9. Audit and Logging for ePHI

### 9.1 What Is Logged

Every ePHI touch is logged with the following fields:

| Field | Description |
|-------|-------------|
| `event_id` | UUIDv7 monotonic identifier |
| `principal` | Authenticated user or service principal performing the action |
| `action` | One of: read, write, update, delete, decrypt, export |
| `record_scope` | Tenant identifier plus record identifier or query predicate |
| `record_count` | Number of records touched |
| `justification` | Free-text minimum-necessary justification copied from the JIT request |
| `source_ip` | IP address of the originating session (post-Teleport translation) |
| `session_id` | Teleport session correlation |
| `timestamp` | UTC, monotonic |
| `result` | success or failure with failure reason |
| `vault_key_version` | If a Vault Transit decrypt was performed, the key version used |

The record contents themselves are not logged. Only metadata about the access is captured. This satisfies the HIPAA access tracking requirement without creating a secondary copy of ePHI in the audit store.

### 9.2 Where Logs Live

Three storage tiers, mirroring the broader audit pattern in AI_AUDIT_TRAIL_SPEC.md:

| Tier | Store | Purpose | Retention |
|------|-------|---------|-----------|
| Hot | svc-db `ephi_audit` table (separate from ephi_<tenant> data schemas) | Query and review | 90 days |
| Warm | Datadog log archive (with HIPAA-eligible workspace and Sensitive Data Scanner rules) | Operational correlation | 1 year |
| Cold | DO Spaces audit prefix with Object Lock | Tamper-evident long-term retention | 6 years per 45 CFR 164.530(j) |

The 6-year requirement comes from 45 CFR 164.530(j)(2), which requires that policies, procedures, and required documentation be retained for 6 years from the date of creation or the date when last in effect, whichever is later. Audit records about ePHI access are required documentation in this sense.

### 9.3 Tamper Evidence

Cold storage uses Object Lock in compliance mode. Once written, a record cannot be deleted or modified for the duration of the retention period, even by the platform owner. The retention period is set at upload time to a date 6 years in the future.

Before Object Lock engages, a SHA-256 manifest is written over the upload batch. Any future tampering with cold-storage objects would mismatch the manifest. The manifest itself is signed with a cosign key held by the System Owner; the public key is published in a known location so an external auditor can verify the signature.

NIST 800-53 controls satisfied: AU-2, AU-3, AU-9, AU-11.

### 9.4 AI-Specific Audit

When ePHI is processed by svc-llm, the additional AI-specific audit captures from AI_AUDIT_TRAIL_SPEC.md apply on top of the ePHI-specific fields above. Input prompts and output completions are captured in the ephi_audit store rather than the standard ir_investigations store, so that ePHI-touching AI invocations are kept inside the regulated tier from end to end.

---

## 10. ePHI Lifecycle

### 10.1 Ingestion

ePHI enters OSOP only through a BAA-covered channel. The supported ingest channels are:

- HTTPS from the covered entity's authorized endpoint, terminating at svc-tunnel, with mutual TLS at the application layer
- Authenticated file upload to a dedicated DO Spaces bucket scoped to the tenant, with server-side encryption enabled and access via Vault-issued credentials

At ingest, the data is immediately classified. A pre-storage hook tags the payload with the tenant identifier, a record identifier (if known from the upstream context), and the Regulated classification marker. The hook writes the cyphertext to svc-db `ephi_<tenant>` and the metadata to `ephi_audit`. Failure to tag results in rejection; the platform does not store ePHI that cannot be classified.

### 10.2 Storage

Storage is in svc-db `ephi_<tenant>` schema with row-level security policies. Each row carries:

- A primary key (UUID, generated at ingest)
- The tenant identifier
- The encrypted record body (cyphertext from Vault Transit)
- A separate column for non-sensitive metadata that does not require decryption to query (e.g., record category, ingest timestamp)
- An RLS policy that gates SELECT on the requesting role and tenant context

No cross-tenant query path exists. Even if a query is malformed to omit the tenant predicate, the RLS policy returns zero rows for any tenant the requester is not bound to.

### 10.3 Processing

Processing occurs exclusively on svc-llm (Ollama, on-premises). The flow:

1. ephi-operator initiates a processing task with a justified scope
2. Application fetches the cyphertext from svc-db and calls Vault Transit to decrypt in memory
3. Cleartext is passed to svc-llm via the net-ai internal network
4. svc-llm runs the inference; the model file is local, no internet egress
5. Output is captured and classified; if the output contains ePHI (and most processing outputs would), it is re-encrypted via Vault Transit and stored back to svc-db
6. Cleartext is dereferenced from memory; the buffer is overwritten

The GLiNER PII detector runs on both input and output. Detected identifiers are logged to the audit trail as confirmation that the platform is processing ePHI as expected. No alert fires on expected ePHI; an alert fires only if ePHI is detected in an unexpected location (e.g., a log line where it should have been redacted).

### 10.4 Transmission

ePHI in transit follows the encryption requirements in section 7.2. The transmission boundaries:

- svc-tunnel ingress: TLS 1.3
- svc-tunnel to svc-automation or svc-automation to svc-db: mTLS within the platform
- svc-automation to svc-llm via net-ai: TLS within the internal network
- svc-db to backup destination: encrypted backup using Vault Transit before transit, then TLS 1.3 to DO Spaces
- No transmission to any external API outside the BAA-covered set

### 10.5 Retention

Default retention is 6 years from the date of last activity on the record, per the HIPAA documentation requirement carried over to record-level handling. A BAA may specify shorter or longer retention; if specified, the BAA controls. If the BAA is silent, the 6-year default applies.

Retention is enforced by:

- A scheduled job that scans `ephi_<tenant>` schemas for records past the retention horizon
- A pre-purge review that confirms the BAA terms and any litigation hold flags
- A destruction step (section 10.7) executed under ephi-operator authority with a signed approval

### 10.6 Sanitization

When ePHI must be sanitized (for de-identification, for sharing with non-BAA-covered parties, or for derived analytics), the procedure follows NIST 800-88:

- Clear: software-based overwrite of the storage location. Suitable for SSD-backed svc-db rows when the underlying storage device is not being repurposed.
- Purge: cryptographic erasure via destruction of the Vault Transit key. Once the key is destroyed, the cyphertext is computationally infeasible to recover. Suitable as the standard destruction mechanism.
- Destroy: physical destruction of the storage media. Applicable only if a host is decommissioned and the media leaves Organization control. Provider attestation is required from the hypervisor operator (DigitalOcean) confirming media handling on instance termination.

NIST 800-53 controls satisfied: MP-6.

### 10.7 Destruction

Destruction of ePHI is performed by cryptographic erasure as the standard path. The procedure:

1. ephi-operator initiates a destruction request specifying the tenant, the record set, and the justification (retention expiration, BAA termination, or covered-entity request)
2. System Owner approves the destruction
3. Vault Transit key version associated with the record set is destroyed (Vault supports key version deletion via the `delete-key-version` operation, gated by an explicit policy)
4. With the key gone, the cyphertext in svc-db is permanently undecryptable
5. The cyphertext rows themselves are then deleted from svc-db; this step is bookkeeping, since the data is already unrecoverable
6. A destruction event is written to the audit log with the tenant, record count, key version destroyed, and timestamp; this event is immutable in cold storage

Cryptographic erasure satisfies NIST 800-88 Purge for the encrypted records. Physical media destruction would only apply if the underlying disk left Organization control, in which case the hypervisor provider's media handling attestation governs.

NIST 800-53 controls satisfied: MP-6, MP-7.

---

## 11. Breach Detection and Response

### 11.1 What Counts as a Breach

Per 45 CFR 164.402, a breach is the acquisition, access, use, or disclosure of ePHI in a manner not permitted under the Privacy Rule which compromises the security or privacy of the ePHI. A risk assessment based on four factors determines whether an impermissible use or disclosure rises to the level of a breach:

1. The nature and extent of the ePHI involved, including the types of identifiers and the likelihood of re-identification
2. The unauthorized person who used the ePHI or to whom the disclosure was made
3. Whether the ePHI was actually acquired or viewed
4. The extent to which the risk to the ePHI has been mitigated

If the risk assessment concludes a low probability that ePHI has been compromised, the incident is not a reportable breach. Otherwise it is, and notification obligations follow.

### 11.2 Detection Surface

ePHI breach detection ties into the existing OSOP detection stack:

- Falco rules tuned for ephi_* schema access patterns; unexpected access from a non-ephi-operator role triggers a high-severity alert
- Datadog Sensitive Data Scanner monitoring for ePHI patterns appearing in log streams outside the regulated tier (a defense-in-depth indicator that something has leaked)
- Vault Transit decrypt operations exceeding a baseline rate trigger alert (potential mass exfiltration)
- GLiNER detector firing on outputs from any service not on the permitted-locations list

### 11.3 Response Ties

Response procedures use the existing playbooks with ePHI-specific overlays:

- PLAYBOOK_LEAKED_CREDENTIAL.md handles credential compromise that could grant ePHI access; the ePHI overlay adds steps to rotate Vault Transit keys, force-revoke active Teleport certificates, and begin the breach risk assessment
- POLICY_INCIDENT_RESPONSE.md governs the overall incident lifecycle; for ePHI incidents, the System Owner must be informed within 1 hour of detection (faster than the standard incident timeline)
- A dedicated ePHI breach playbook is a section 14 gap; it will inherit from these playbooks and add the HIPAA-specific notification steps

### 11.4 Notification Obligations

If a breach occurs, the following notification obligations apply per 45 CFR 164.404 through 164.410:

| Recipient | Trigger | Timeline | Method |
|-----------|---------|----------|--------|
| Affected individuals | Any breach of unsecured ePHI | Without unreasonable delay, no later than 60 calendar days after discovery | Written notice (first-class mail or email if individual consented), with content per 164.404(c) |
| HHS Office for Civil Rights | Breach affecting fewer than 500 individuals | Annual report, no later than 60 days after the end of the calendar year in which the breach was discovered | Submission via HHS breach reporting portal |
| HHS Office for Civil Rights | Breach affecting 500 or more individuals | Without unreasonable delay, no later than 60 calendar days after discovery | Submission via HHS breach reporting portal |
| Prominent media outlets serving the state or jurisdiction | Breach affecting 500 or more individuals in a state or jurisdiction | Without unreasonable delay, no later than 60 calendar days after discovery | Press release to prominent media outlets |
| Business associate notification to covered entity | Business associate breach of unsecured ePHI | Without unreasonable delay, no later than 60 calendar days after discovery | Written notice with content per 164.410(c) |

For OSOP in a business-associate role, the most relevant obligation is notification to the covered entity within 60 days. The covered entity then carries the individual and HHS notification obligation, though OSOP would assist with the underlying facts and risk assessment.

### 11.5 Discovery Definition

A breach is treated as discovered as of the first day on which the breach is known, or by exercising reasonable diligence would have been known, to any person other than the person committing the breach. This definition matters because the 60-day clock starts at discovery, not at the breach event itself. The detection surface in section 11.2 is engineered to minimize the gap between event and discovery.

---

## 12. Business Associate Sub-flows

When OSOP uses subprocessors that touch ePHI, those subprocessors are themselves business associates of the Organization (which is itself a business associate of the covered entity). HIPAA propagates obligations downstream.

### 12.1 Subprocessor BAA Requirement

Per 45 CFR 164.502(e)(1)(ii), a business associate may permit a subcontractor to create, receive, maintain, or transmit ePHI on its behalf only if the subcontractor agrees in writing to the same restrictions and conditions that apply to the business associate. In practical terms, every downstream service that handles ePHI must have a signed BAA with the Organization.

### 12.2 Subprocessor Inventory

| Subprocessor | Function | ePHI Exposure | BAA Status |
|-------------|----------|---------------|-----------|
| DigitalOcean | Hypervisor for alpha-node, Spaces for backup and archive | Underlying compute and storage; cyphertext only if encryption is correctly applied | Required before any ePHI ingest; not currently in place |
| Cloudflare | Edge security and tunnel | Transit-only exposure of ePHI cyphertext | Required before any ePHI ingest; Cloudflare offers a BAA |
| Anthropic | Claude API via svc-ai-gateway | Would expose ePHI to Anthropic's processing | Required if ePHI inference routes to Anthropic; if no BAA, route exclusively through svc-llm |
| Datadog | Log and metric ingest | Should not see ePHI if scrubbing works; BAA required as defense-in-depth | Required before any ePHI ingest; Datadog offers a BAA for the HIPAA-eligible workspace tier |
| HashiCorp Vault (self-hosted on alpha-node) | Encryption key custody | Vault sees key material, not ePHI itself; self-hosted so no third-party BAA needed | Internal to Organization; not a subprocessor for BAA purposes |

### 12.3 Vendor Risk Assessment

Each subprocessor is subject to a vendor risk assessment before ePHI ingest. The assessment covers:

- BAA terms reviewed against the Organization's standard BAA template
- Subprocessor's published security posture (SOC 2 Type II, HITRUST, or equivalent)
- Subprocessor's breach history and disclosure practices
- Geographic location of data processing (relevant for state law overlays)
- Subprocessor's own subcontractor inventory (sub-sub-processors that may touch ePHI)

A subprocessor failing any assessment criterion is either remediated through contract or removed from the ePHI flow. There is no risk acceptance path that allows a non-compliant subprocessor to touch ePHI.

### 12.4 Change Notification

Each BAA includes a clause requiring the subprocessor to notify the Organization in writing within 30 days of any material change to its subcontractor inventory that would affect ePHI handling. Failure to notify is a contract breach and triggers a Risk Assessment update.

---

## 13. Implementation Maturity

| Capability | Current Maturity | Target for ePHI Ingest | Notes |
|-----------|------------------|------------------------|-------|
| Encryption at rest (filesystem) | Partial (Docker volume permissions hardened; LUKS not engaged) | Full LUKS on alpha-node disk | Engagement requires host reboot; planned in next maintenance window after the gate items are otherwise complete |
| Encryption at rest (application field) | Not implemented | Vault Transit with per-tenant key | Requires schema change; tracked in gap section |
| Encryption in transit (TLS 1.3 external) | Implemented (Cloudflare edge enforces) | No change | Verified via SSL Labs scan |
| Encryption in transit (mTLS internal) | Partial (some hops mTLS, some plaintext on bridge network) | Full mTLS on all ePHI-carrying hops | Service-mesh proposal under review |
| Confidential computing (in use) | Not implemented | Not required for initial ingest; future enhancement | Hardware enclave evaluation deferred to Phase 20+ |
| RBAC (admin/operator/auditor) | Implemented | ephi-operator role added | Schema for role exists; assignment is empty |
| JIT access via Teleport | Implemented | ephi-operator integrated | JIT template needs the minimum-necessary justification field |
| Session recording | Implemented | No change | Already mandatory for elevated sessions |
| Audit logging (Squire AI events) | Implemented per AI_AUDIT_TRAIL_SPEC.md | Extended to ephi_audit table | Requires schema migration and ingest hook |
| Tamper-evident cold storage | Implemented (Object Lock on archive prefix) | Retention extended from 3 years to 6 years | Object Lock policy update needed |
| PII detection (generic) | Implemented (GLiNER) | Extended for ePHI identifier classes | Ruleset versioning needed; baseline scoring on ePHI test corpus |
| Breach detection (Falco) | Implemented for general detection | Rules tuned for ephi_* schema access | Rule development needed |
| BAA template | Not drafted | Drafted and reviewed by legal | Tracked in gap section |
| Subprocessor BAAs | None in place | All required subprocessors signed | Tracked in gap section |
| Incident response playbook | Implemented (POLICY_INCIDENT_RESPONSE.md, PLAYBOOK_LEAKED_CREDENTIAL.md) | ePHI-specific overlay added | Tracked in gap section |
| Training records | Existing personnel are trained on platform security | Training updated for HIPAA-specific obligations | Annual refresher cycle established |

---

## 14. Open Gaps

This section is the honest inventory. Each gap is a hard blocker for ePHI ingest until closed.

### 14.1 ePHI Schema Not Provisioned

No `ephi_<tenant>` schema exists in svc-db today. The schema migration, RLS policies, and the corresponding application-layer hooks for tag-on-ingest and decrypt-on-read are not written. This is the largest single gap.

Estimated effort: 2 to 3 days of focused work. Dependency: BAA signed (so the tenant naming is known) and ephi-operator role created in svc-identity.

### 14.2 BAA Template Not Drafted

The Organization does not have a counter-signing BAA template ready. The template must cover the required HIPAA clauses (use and disclosure restrictions, safeguard obligations, subcontractor flow-down, breach notification timelines, term and termination, return or destruction of ePHI at termination).

Estimated effort: 1 to 2 weeks of legal review. The template can be drafted from publicly available BAA examples and then reviewed by counsel; the Organization does not have ongoing legal counsel on retainer, which extends the timeline.

### 14.3 GLiNER ePHI Ruleset Not Tuned

The GLiNER PII detector is configured for generic identifier classes. ePHI-specific patterns are not tuned. Specifically missing:

- MRN format variants (vary by EHR vendor)
- Health plan beneficiary number patterns
- Diagnosis-code-adjacent text (ICD-10 codes alone are not ePHI but become ePHI in combination with other identifiers)
- Device serial number formats common to implants and monitoring devices

Estimated effort: 1 week to baseline against a synthetic test corpus, plus ongoing tuning as false positives surface during BAA-covered operations.

### 14.4 Retention Not Extended

The current cold-storage Object Lock retention is 3 years for general audit records. The HIPAA documentation requirement is 6 years (45 CFR 164.530(j)). The Object Lock policy must be updated, and the change must propagate to any existing audit records that would fall within an ePHI scope.

Estimated effort: under 1 day, but requires verification that the existing policy update path works as documented in the DO Spaces console.

### 14.5 Subprocessor BAAs Not Initiated

No BAA outreach has begun with DigitalOcean, Cloudflare, Datadog, or Anthropic. Each requires individual contract negotiation with attendant timelines (typically 4 to 8 weeks per vendor for a small organization). This is the longest-lead gap.

Estimated effort: 8 to 16 weeks elapsed, low active work per week.

### 14.6 ePHI Incident Response Playbook

A dedicated ePHI breach playbook is not written. The existing playbooks cover the foundational response but do not include the HIPAA-specific notification workflow, the breach risk assessment template, or the legal coordination steps.

Estimated effort: 3 to 5 days. Dependency: BAA template (so the customer notification path is known).

### 14.7 mTLS Coverage Incomplete

mTLS is implemented on some inter-service hops but not all. Full coverage on ePHI-carrying hops is required.

Estimated effort: 1 week. Dependency: service-mesh proposal under review.

### 14.8 LUKS Not Engaged

Host-level disk encryption via LUKS is supported but not engaged. The reboot to engage it must be coordinated with maintenance windows.

Estimated effort: under 1 day of work, scheduling-dependent on maintenance window.

### 14.9 Confidential Computing Roadmap

In-use encryption via hardware enclaves is not a blocker for initial ePHI ingest but is the next logical hardening step. The roadmap entry needs to be formalized.

Estimated effort: 1 day to formalize; multi-quarter to implement.

---

## 15. Cross-References

- HIPAA-001 (HIPAA Security Rule Crosswalk) - the companion document mapping existing controls to 45 CFR Part 164 Subpart C
- SQUIRE_DATA_FLOW_CLASSIFICATION.md - the broader data classification framework that this document extends with the Regulated tier
- DATA_FLOW_DIAGRAM.md - the platform DFD whose trust boundaries this document constrains for ePHI
- AI_AUDIT_TRAIL_SPEC.md - the audit pattern this document reuses for ePHI-specific events
- POLICY_ACCESS_CONTROL.md - the RBAC foundation that the ephi-operator role extends
- POLICY_INCIDENT_RESPONSE.md - the incident lifecycle that ePHI breaches inherit
- PLAYBOOK_LEAKED_CREDENTIAL.md - the credential compromise response, with ePHI-specific overlays in section 11.3
- POLICY_AI_GOVERNANCE.md - the AI governance framework that constrains svc-llm usage on ePHI
- POAM_PLAN_OF_ACTION.md - the gap items in section 14 feed into the platform POA&M
- RISK_ASSESSMENT.md - any ePHI workload triggers a Risk Assessment update per section 4.1 item 14

### Framework Citations

- 45 CFR Part 160, 162, 164 (HIPAA Administrative Simplification)
- 45 CFR 160.103 (definitions)
- 45 CFR 164.402 (breach definition)
- 45 CFR 164.404 through 164.410 (breach notification)
- 45 CFR 164.501 (designated record set)
- 45 CFR 164.502(b) (minimum necessary)
- 45 CFR 164.502(e) (business associate contracts)
- 45 CFR 164.514(b)(1) (expert determination de-identification)
- 45 CFR 164.514(b)(2)(i) (safe harbor 18 identifiers)
- 45 CFR 164.514(e) (limited data set)
- 45 CFR 164.530(j) (documentation retention)
- NIST SP 800-66 Rev 2 (Implementing the HIPAA Security Rule)
- NIST SP 800-122 (Guide to Protecting the Confidentiality of PII)
- NIST SP 800-88 Rev 1 (Guidelines for Media Sanitization)
- NIST SP 800-53 Rev 5 (Security and Privacy Controls)
