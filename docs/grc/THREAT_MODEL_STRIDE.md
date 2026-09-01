# Threat Model - STRIDE Analysis

**Organization:** Organization Security Operations Platform
**Assessment Date:** 2026-03-12
**Assessor:** System Owner
**Methodology:** STRIDE (Microsoft Threat Modeling Framework) applied per NIST SP 800-154 (Data-Centric Threat Modeling)
**NIST 800-53 Controls:** RA-3 (Risk Assessment), RA-5 (Vulnerability Monitoring and Scanning), SA-11 (Developer Testing and Evaluation), SA-15 (Development Process, Standards, and Tools)
**OWASP References:** OWASP Threat Modeling Cheat Sheet, OWASP LLM Top 10 (2025)
**Classification:** Internal Use Only
**Version:** 1.1 (Phase 17 scope extension 2026-04-24)

> **Status note (2026-09-01):** this document describes the DigitalOcean-era baseline as assessed. That environment was retired 2026-08. The platform now runs on an Oracle Cloud (OCI) ARM instance with a partial stack (3 containers live); the remaining services are pending ARM rebuild. A re-baseline of this document is queued and tracked in the POA&M.

---

## Document Control

| Field | Value |
|-------|-------|
| Document ID | TM-STRIDE-001 |
| Version | 1.0 |
| Status | Approved |
| Last Revised | 2026-03-12 |
| Next Review | 2026-09-12 |
| Author | Information Security Officer |
| Approver | System Owner |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-03-12 | Information Security Officer | Initial STRIDE analysis across full architecture including AI systems |
| 1.1 | 2026-04-24 | Information Security Officer | Phase 17 scope extension added. STRIDE rows for Squire subsystem (svc-squire, svc-nemo, svc-langfuse family). Cross-ref to SQUIRE_THREAT_MODEL pending from 17-14. |

### Trust Boundary Architecture

The following diagram shows all seven trust boundaries (TB-1 through TB-7) overlaid on the platform architecture. Each boundary is annotated with the STRIDE threat categories that apply at that crossing point, based on the analysis in Sections 4-9 of this document.

```
Legend
------
[EE]  = External Entity (outside authorization boundary)
[P]   = Process (containerized service)
[DS]  = Data Store
[TB-N]= Trust Boundary
S=Spoofing  T=Tampering  R=Repudiation  I=Info Disclosure  D=DoS  E=Elevation of Privilege


                        ┌─────────────────────────────────┐
                        │         INTERNET (Untrusted)     │
                        │                                  │
                        │  [EE] User         [EE] Anthropic│
                        │  (Telegram)        API           │
                        │      │                 ▲         │
                        │      │ [DF-01]         │ [DF-02] │
                        │      │                 │         │
                        └──────┼─────────────────┼─────────┘
                               │                 │
 ══════════════════════════════╪═════════════════╪══════════════════════════════════
  [TB-7] Telegram API entry    │                 │  [TB-5] AI Gateway to external
  Threats: S, T, I, D, E      │                 │  Threats: T, I, D
 ══════════════════════════════╪═════════════════╪══════════════════════════════════
                               │                 │
                               ▼                 │
┌──────────────────────────────────────────────────────────────────────────────────┐
│  PUBLIC ZONE - Cloudflare Edge                                                  │
│                                                                                 │
│  [P-01] Edge Security Provider (Cloudflare WAF + DDoS + Tunnel Management)      │
│      │                                                                          │
│      │  HTTPS inspection, rate limiting, bot filtering, DDoS absorption         │
│      │                                                                          │
└──────┼──────────────────────────────────────────────────────────────────────────┘
       │ [DF-09] Authenticated HTTPS
       │
 ══════╪══════════════════════════════════════════════════════════════════════════
  [TB-1] Internet to Cloudflare Edge
  Threats: S, T, D
  - S: Spoofed webhook requests, forged origin headers
  - T: Payload manipulation before edge inspection
  - D: Volumetric DDoS, application-layer floods
 ══════╪══════════════════════════════════════════════════════════════════════════
       │
       ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│  DMZ - net-core (ingress segment)                                               │
│                                                                                 │
│  [P-02] svc-tunnel (Cloudflare Tunnel connector)                                │
│      │                                                                          │
│      ├──[DF-10]──► [P-03] svc-automation (n8n SOAR)                             │
│      │                  │         │                                              │
│      └──[DF-12]──► [P-04] svc-ai-gateway (OpenClaw) ────── [DF-02] ──► (TB-5)  │
│                         │         │                                              │
└─────────────────────────┼─────────┼──────────────────────────────────────────────┘
                          │         │
 ═════════════════════════╪═════════╪═══════════════════════════════════════════════
  [TB-2] Cloudflare Tunnel to net-core DMZ services
  Threats: S, T, R, I, D, E
  - S: Spoofed webhook payloads impersonating GitHub/Telegram/Gumroad
  - T: Modified tunnel traffic, injected workflow parameters
  - R: Unsigned webhook calls with no audit trail
  - I: Credential leakage through error responses
  - D: Webhook flooding, resource exhaustion on svc-automation
  - E: Workflow injection escalating to internal service access
 ═════════════════════════╪═════════╪═══════════════════════════════════════════════
                          │         │
        ┌─────────────────┘         │
        │                           │
        ▼                           ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│  INTERNAL ZONE                                                                  │
│                                                                                 │
│  net-core:                          net-ai (internal: true, no internet):        │
│  ┌────────────────────────┐         ┌────────────────────────────────┐           │
│  │ [DS-01] svc-db         │         │ [P-06] svc-llm (Ollama)       │           │
│  │ (PostgreSQL 16)        │         │    Local inference only        │           │
│  │                        │         │                                │           │
│  │ [DS-02] db-data-volume │         │ [P-07] svc-transcription      │           │
│  │                        │         │ (Whisper)                      │           │
│  └────────────────────────┘         │    Local inference only        │           │
│           ▲                         └────────────────────────────────┘           │
│           │ [DF-15]                          ▲                                   │
│           │                                  │ [DF-16]                           │
└───────────┼──────────────────────────────────┼───────────────────────────────────┘
            │                                  │
 ═══════════╪══════════════════════════════════╪════════════════════════════════════
  [TB-3] net-core DMZ to net-ai / Internal zone
  Threats: S, T, I, E
  - S: Compromised DMZ container impersonating legitimate service via Docker DNS
  - T: Prompt injection through svc-automation into svc-llm inference pipeline
  - I: PII or secrets leaked through AI model responses or error messages
  - E: Container escape from DMZ to internal network, pivoting to svc-db
 ═══════════╪══════════════════════════════════╪════════════════════════════════════
            │                                  │
            │         ┌────────────────────────┘
            │         │
            ▼         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│  SENSITIVE ZONE (net-core, restricted access)                                   │
│                                                                                 │
│  [P-08] svc-secrets (HashiCorp Vault) ◄─── [DF-17] secret lookups              │
│      Token-based authentication, audit logging                                  │
│                                                                                 │
│  [P-09] svc-identity (Keycloak v26)   ◄─── [DF-18] authentication requests     │
│      SSO, RBAC policy enforcement                                               │
│                                                                                 │
│  [P-10] svc-gateway (Teleport v18)    ◄─── [DF-19] session access requests     │
│      PAM, JIT access, session recording                                         │
│                                                                                 │
└──────────────────────────────────────────────────────────────────────────────────┘
            ▲                   ▲
            │                   │
 ═══════════╪═══════════════════╪═══════════════════════════════════════════════════
  [TB-6] Services to secrets engine (svc-secrets)
  Threats: S, T, I, E
  - S: Stolen Vault token used from unauthorized container
  - T: Secret values modified during transit (env var injection)
  - I: Secrets exposed through container environment inspection or core dumps
  - E: Vault policy bypass granting access to secrets outside service scope
 ═══════════╪═══════════════════╪═══════════════════════════════════════════════════
            │                   │
 ═══════════╪═══════════════════╪═══════════════════════════════════════════════════
  [TB-5] Services to database (svc-db)
  Threats: S, T, R, I
  - S: Credential theft allowing unauthorized database connections
  - T: SQL injection modifying workflow state or n8n credential storage
  - R: Database modifications without application-layer audit trail
  - I: Bulk data exfiltration through compromised database credentials
 ═══════════╪═══════════════════╪═══════════════════════════════════════════════════
            │                   │
            │                   │
┌──────────────────────────────────────────────────────────────────────────────────┐
│  MONITORING ZONE (net-monitoring)                                               │
│                                                                                 │
│  [P-11] svc-detection ──► [P-12] svc-detection-router ──► [EE] Monitoring      │
│  (Falco eBPF)              (Falcosidekick)                  Platform (Datadog)  │
│                                                                  ▲              │
│  [P-13] svc-monitor (Datadog Agent) ────────────────────────────┘               │
│                                            ▲                                    │
│  [P-15] svc-log-router (Fluentd) ─────────┘ [DF-23]                            │
│                                            ▲                                    │
│  [P-16] svc-event-shipper ─────────────────┘ [DF-24]                            │
│  (Teleport Event Handler)                                                       │
│                                                                                 │
└──────────────────────────────────────────────────────────────────────────────────┘
                                                    │
 ═══════════════════════════════════════════════════╪════════════════════════════════
  [TB-4] net-core to net-monitoring / Monitoring zone to Datadog SaaS
  Threats: S, T, R, I, D
  - S: Forged log entries injected into Fluentd pipeline
  - T: Alert suppression by modifying Falcosidekick routing rules
  - R: Deleted or overwritten audit logs destroying forensic evidence
  - I: Sensitive data leaked through verbose logging to external SaaS
  - D: Log flooding overwhelming monitoring pipeline, causing alert blindness
 ═══════════════════════════════════════════════════╪════════════════════════════════
                                                    │
                                                    ▼
                                        [EE] Monitoring Platform
                                        (Datadog SaaS - External)


 ┌─────────────────────────────────────────────────────────────────────────────────┐
 │  TRUST BOUNDARY SUMMARY                                                        │
 │                                                                                │
 │  Boundary │ Crossing                            │ STRIDE Threats               │
 │  ─────────┼─────────────────────────────────────┼──────────────────────────────│
 │  TB-1     │ Internet to Cloudflare edge          │ S, T, D                      │
 │  TB-2     │ Cloudflare tunnel to DMZ services    │ S, T, R, I, D, E             │
 │  TB-3     │ DMZ to Internal zone (net-ai)        │ S, T, I, E                   │
 │  TB-4     │ net-core to net-monitoring / SaaS     │ S, T, R, I, D               │
 │  TB-5     │ Services to database (svc-db)        │ S, T, R, I                   │
 │  TB-6     │ Services to secrets engine (Vault)   │ S, T, I, E                   │
 │  TB-7     │ Telegram API to AI gateway           │ S, T, I, D, E               │
 │                                                                                │
 │  Highest-risk boundaries: TB-2 (all 6 STRIDE categories), TB-7 (5 categories) │
 │  These correspond to the two primary ingress paths into the platform.          │
 └─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Purpose

This document applies the STRIDE threat modeling methodology to the Organization Security Operations Platform. STRIDE decomposes threats into six categories - Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege - and maps them to specific services, trust boundaries, and data flows within the authorization boundary.

The analysis extends traditional STRIDE with AI-specific threat extensions addressing prompt injection, model poisoning, PII leakage through inference pipelines, and excessive autonomous agency. These extensions align with the OWASP LLM Top 10 (2025), MITRE ATLAS, and the AI threat categories defined in the AI Governance Policy (POL-AI-001, Section 6.1).

This threat model complements the Risk Assessment (`RISK_ASSESSMENT.md`) by providing a structured decomposition of HOW threats manifest, whereas the Risk Assessment quantifies the likelihood and impact of WHAT could go wrong.

## 2. Scope and Architecture Reference

### 2.1 Authorization Boundary

The threat model covers all assets within the authorization boundary as defined in the System Security Plan (SSP-OPS-001):

- One (1) VPS (4 vCPU, 8 GB RAM, 160 GB disk) running Ubuntu 24.04 LTS
- Fourteen (14) containerized services across three segmented Docker networks
- Infrastructure-as-code (Terraform) with CI/CD security pipeline
- External integrations (Anthropic API, Cloudflare edge, Datadog SaaS, Telegram API)

### 2.2 Trust Zones

| Zone | Services | Trust Level | Network |
|------|----------|-------------|---------|
| **Public** | Cloudflare edge (CDN, WAF, DDoS protection) | Untrusted | Internet-facing |
| **DMZ** | svc-automation (n8n SOAR), svc-ai-gateway (OpenClaw) | Low Trust | net-core (ingress via svc-tunnel) |
| **Internal** | svc-db (PostgreSQL), svc-llm (Ollama), svc-transcription (Whisper) | Medium Trust | net-core, net-ai |
| **Sensitive** | svc-secrets (HashiCorp Vault), svc-identity (Keycloak), svc-gateway (Teleport) | High Trust | net-core (restricted) |
| **Monitoring** | svc-detection (Falco), svc-detection-router (Falcosidekick), svc-monitor (Datadog), svc-log-router (Fluentd), svc-event-shipper | High Trust | net-monitoring |

### 2.3 Trust Boundaries

| Boundary | From → To | Data Crossing |
|----------|-----------|---------------|
| **TB-1** | Internet → Cloudflare edge | User requests, webhook payloads |
| **TB-2** | Cloudflare edge → svc-tunnel → DMZ | Authenticated HTTPS traffic |
| **TB-3** | DMZ → Internal zone | Workflow queries, AI inference requests |
| **TB-4** | DMZ → Sensitive zone | Authentication requests, secret lookups |
| **TB-5** | svc-ai-gateway → Anthropic API (external) | Prompts containing operational context; responses |
| **TB-6** | Monitoring zone → Datadog SaaS (external) | Metrics, logs, traces, Falco alerts |
| **TB-7** | Telegram API → svc-tunnel → svc-ai-gateway | User messages from external messaging platform |

---

## 3. STRIDE Methodology

### 3.1 Approach

Each STRIDE category is analyzed against the architecture by:

1. Identifying the trust boundary or data flow where the threat applies
2. Mapping specific threats to affected services using sanitized names
3. Documenting current controls with an honest assessment of implementation status (Implemented, Partial, Planned)
4. Rating residual risk as High, Medium, or Low based on the 5x5 matrix in the Risk Assessment
5. Recommending additional mitigations where residual risk exceeds organizational tolerance

### 3.2 STRIDE Category Definitions

| Category | Property Violated | Question |
|----------|-------------------|----------|
| **S** - Spoofing | Authentication | Can an attacker pretend to be a legitimate user, service, or system? |
| **T** - Tampering | Integrity | Can an attacker modify data in transit, at rest, or processing logic? |
| **R** - Repudiation | Non-repudiation | Can an attacker deny performing an action without a verifiable audit trail? |
| **I** - Information Disclosure | Confidentiality | Can an attacker gain access to data they are not authorized to see? |
| **D** - Denial of Service | Availability | Can an attacker degrade or eliminate access to a service? |
| **E** - Elevation of Privilege | Authorization | Can an attacker gain capabilities beyond their authorized level? |

---

## 4. Spoofing (S)

Threats where an attacker impersonates a legitimate entity to bypass authentication controls.

### S-01: Spoofed Webhook Requests to svc-automation

**Trust Boundary:** TB-2 (Cloudflare edge → DMZ)
**Affected Services:** svc-automation, svc-tunnel
**Description:** An attacker crafts HTTP requests that impersonate legitimate webhook callers (GitHub, Telegram, Gumroad) to trigger workflow execution. If webhook authentication is weak or absent on specific endpoints, the attacker can inject arbitrary payloads into automation workflows.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Webhook authentication tokens on registered endpoints (Implemented); Cloudflare WAF rules on tunnel ingress (Implemented); IP allowlisting not feasible due to dynamic webhook source IPs (N/A) |
| **Control Status** | Implemented |
| **Residual Risk** | **Medium** - token-based auth is effective but relies on per-endpoint configuration; new webhooks created without tokens would be exposed |
| **Recommended Mitigation** | Implement HMAC signature verification for all webhook endpoints; enforce a policy that no webhook endpoint may be activated without authentication |

### S-02: Telegram User Impersonation to AI Agent

**Trust Boundary:** TB-7 (Telegram API → svc-ai-gateway)
**Affected Services:** svc-ai-gateway, svc-automation
**Description:** An attacker sends messages via Telegram that appear to originate from authorized users. The AI gateway processes these as legitimate commands, potentially triggering privileged workflow actions through svc-automation.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Telegram bot token authentication (Implemented); chat ID allowlist restricting which Telegram users can interact with the bot (Implemented); rate limiting at svc-ai-gateway (Implemented) |
| **Control Status** | Implemented |
| **Residual Risk** | **Low** - chat ID allowlist effectively restricts interaction to authorized users; Telegram API guarantees sender identity within its trust model |
| **Recommended Mitigation** | Add command-level authorization for destructive actions (require explicit confirmation token for operations that modify infrastructure state) |

### S-03: Service Identity Spoofing on Internal Network

**Trust Boundary:** TB-3 (DMZ → Internal zone)
**Affected Services:** svc-db, svc-secrets, svc-identity
**Description:** A compromised DMZ container impersonates a legitimate internal service to access sensitive resources. Docker internal DNS resolution relies on container names, and services authenticate to svc-db and svc-secrets using credentials passed via environment variables.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Docker network segmentation (net-core, net-ai, net-monitoring) restricts which containers can reach which services (Implemented); svc-db requires credential authentication (Implemented); svc-secrets uses token-based auth (Implemented) |
| **Control Status** | Implemented |
| **Residual Risk** | **Medium** - network segmentation limits blast radius, but a compromised container on net-core with access to environment variables could authenticate as the legitimate service |
| **Recommended Mitigation** | Implement mutual TLS (mTLS) between services; migrate from environment variable credentials to svc-secrets dynamic secrets with short-lived tokens |

### S-04: Forged Audit Log Entries

**Trust Boundary:** TB-6 (Monitoring zone → Datadog SaaS)
**Affected Services:** svc-log-router, svc-monitor
**Description:** An attacker with container access injects fabricated log entries into the Fluentd pipeline to create false audit trails or mask malicious activity. If svc-log-router does not validate log source integrity, forged entries would be indistinguishable from legitimate ones.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Fluentd source tagging by container ID (Implemented); Datadog log pipeline with source metadata (Implemented); Teleport session recording provides independent audit trail (Implemented) |
| **Control Status** | Partial - log integrity verification (cryptographic signing of log entries) is not implemented |
| **Residual Risk** | **Medium** - independent audit trails via svc-gateway make complete evidence destruction difficult, but log injection remains possible |
| **Recommended Mitigation** | Implement log entry signing at svc-log-router; deploy append-only log storage with tamper detection |

### S-05: Spoofed Cloudflare Tunnel Origin

**Trust Boundary:** TB-1 (Internet → Cloudflare edge)
**Affected Services:** svc-tunnel
**Description:** An attacker attempts to establish a rogue tunnel endpoint that impersonates the legitimate Cloudflare Tunnel connector, redirecting traffic to an attacker-controlled server.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Tunnel connector authenticates to Cloudflare using a unique token bound to the tunnel ID (Implemented); Cloudflare manages tunnel routing on their infrastructure (Implemented) |
| **Control Status** | Implemented |
| **Residual Risk** | **Low** - tunnel token compromise would require access to the container environment or secrets store; Cloudflare's infrastructure prevents unauthorized tunnel registration |
| **Recommended Mitigation** | Rotate tunnel token on a semi-annual schedule; monitor for tunnel connector reconnection events in Cloudflare dashboard |

---

## 5. Tampering (T)

Threats where an attacker modifies data, code, or system state to alter intended behavior.

### T-01: Prompt Injection via External Messaging (AI-Specific)

**Trust Boundary:** TB-7 (Telegram → svc-ai-gateway → svc-automation)
**Affected Services:** svc-ai-gateway (AI-001), svc-automation
**OWASP LLM:** LLM01 (Prompt Injection)
**Description:** An attacker crafts Telegram messages containing adversarial prompts designed to override the AI agent's system instructions. Successful injection could cause the AI to execute unintended svc-automation workflows, disclose system prompt contents, or generate harmful outputs that bypass safety controls.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | System prompt hardening with explicit instruction boundaries (Implemented); output sanitization before workflow action execution (Implemented); human approval gates for destructive actions in svc-automation (Implemented); Falco behavioral monitoring of svc-ai-gateway container (Implemented); rate limiting (Implemented) |
| **Control Status** | Implemented |
| **Residual Risk** | **Medium** - prompt injection is an inherent limitation of current LLM architectures; controls reduce impact but cannot eliminate the attack vector entirely |
| **Recommended Mitigation** | Implement a prompt firewall (input/output classifier) at svc-ai-gateway; deploy canary tokens in system prompts to detect extraction attempts; add output schema validation for workflow-triggering responses |

### T-02: Model Weight Poisoning via Supply Chain (AI-Specific)

**Trust Boundary:** External model registries → svc-llm (AI-002)
**Affected Services:** svc-llm
**OWASP LLM:** LLM03 (Supply Chain)
**MITRE ATLAS:** AML.T0018 (Backdoor ML Model)
**Description:** An attacker compromises upstream model weights (e.g., through a poisoned Ollama model registry entry or a tampered Hugging Face checkpoint). The poisoned model produces subtly altered outputs - biased classifications, hidden trigger phrases, or backdoored behavior - that are consumed by downstream svc-automation workflows.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Trivy CVE scanning of Ollama container image (Implemented); model weight checksum verification against published hashes (Partial - manual process); no automatic model updates (Implemented); SBOM generation for container dependencies (Implemented) |
| **Control Status** | Partial - automated model integrity verification pipeline not yet deployed |
| **Residual Risk** | **Medium** - manual checksum verification reduces risk but is operationally fragile; no behavioral testing of model outputs against known baselines |
| **Recommended Mitigation** | Implement automated model integrity verification in CI/CD; deploy behavioral regression testing with curated prompt/response baselines; pin model versions to verified checksums in IaC |

### T-03: Infrastructure-as-Code State Tampering

**Trust Boundary:** CI/CD pipeline → Terraform state → cloud resources
**Affected Services:** All Terraform-managed resources
**Description:** An attacker modifies Terraform state or IaC configuration to alter infrastructure (firewall rules, DNS records, container configurations) in ways that weaken security posture. This could occur via compromised CI/CD credentials, direct state file manipulation, or a malicious pull request that bypasses review.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Remote encrypted state storage (Implemented); mandatory PR reviews with Checkov + TFLint + OPA policy checks (Implemented); Gitleaks scanning for secrets in commits (Implemented); Cosign container signing (Implemented); branch protection rules (Implemented) |
| **Control Status** | Implemented |
| **Residual Risk** | **Low** - multi-layer CI/CD security pipeline provides defense-in-depth; state encryption prevents direct manipulation |
| **Recommended Mitigation** | Implement Terraform state drift detection with automated alerting; add OPA policy for maximum blast radius per apply (limit resources created/destroyed per run) |

### T-04: Database Record Manipulation

**Trust Boundary:** TB-3 (DMZ → Internal zone)
**Affected Services:** svc-db (PostgreSQL), svc-automation
**Description:** An attacker with access to svc-automation (via webhook exploitation or container compromise) uses the database credentials present in the container environment to directly modify svc-db records - altering workflow state, credential references, or audit entries stored in PostgreSQL.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Database authentication required (Implemented); svc-automation database user has limited schema permissions (Partial - currently uses a shared credential); svc-detection monitors for unexpected database connections (Implemented); database backup scripts (Implemented) |
| **Control Status** | Partial - least-privilege database roles not fully implemented |
| **Residual Risk** | **Medium** - shared database credentials between services increase blast radius if any single service is compromised |
| **Recommended Mitigation** | Implement per-service database credentials with minimum necessary permissions; deploy svc-secrets dynamic database credentials with automatic rotation; enable PostgreSQL audit logging |

### T-05: Container Image Tampering in CI/CD Pipeline

**Trust Boundary:** Container registry → Docker runtime
**Affected Services:** All 20 containers
**Description:** An attacker compromises a container image in the build pipeline or at the registry layer, injecting malicious code into an image that passes initial scanning but activates post-deployment.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Trivy CVE scanning in CI (Implemented); Cosign container image signing (Implemented); SBOM generation and tracking (Implemented); Semgrep SAST scanning (Implemented); pinned image digests in Docker Compose (Partial - not all images pinned by digest) |
| **Control Status** | Implemented |
| **Residual Risk** | **Low** - multi-scanner CI pipeline with image signing provides strong integrity guarantees |
| **Recommended Mitigation** | Pin all container images by SHA256 digest rather than tag; implement runtime image verification at container start |

---

## 6. Repudiation (R)

Threats where an attacker performs actions that cannot be reliably attributed or audited.

### R-01: Unattributed AI Agent Actions

**Trust Boundary:** TB-7 (Telegram → svc-ai-gateway → svc-automation)
**Affected Services:** svc-ai-gateway, svc-automation
**Description:** The AI agent executes svc-automation workflows on behalf of users, but the action attribution chain (user → AI decision → workflow execution) may lack sufficient granularity to determine whether a specific action was explicitly requested, inferred by the AI, or triggered by prompt injection.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Full prompt/response logging at svc-ai-gateway (Implemented); svc-automation execution logs with workflow IDs (Implemented); Falco audit trail for container-level actions (Implemented); svc-gateway session recording (Implemented) |
| **Control Status** | Partial - logs capture the WHAT but not always the WHY (AI reasoning chain not always preserved) |
| **Residual Risk** | **Medium** - reconstructing the decision chain from prompt to action requires correlating multiple log sources |
| **Recommended Mitigation** | Implement structured decision logging at svc-ai-gateway that captures: input prompt hash, AI reasoning summary, selected action, confidence score, and approval status; correlate with svc-automation execution ID |

### R-02: SSH Session Activity Without Granular Attribution

**Trust Boundary:** TB-2 (Cloudflare → svc-tunnel → host)
**Affected Services:** svc-gateway (Teleport), host OS
**Description:** In the single-operator environment, all SSH sessions are attributed to the same user. If operator credentials are compromised, an attacker's SSH session would be indistinguishable from legitimate activity at the identity level (though behavioral anomalies would differ).

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Teleport session recording with full terminal replay (Implemented); JIT admin access with 4-hour TTL (Implemented); MFA (TOTP) required for SSH (Implemented); immutable audit log shipping to Datadog (Implemented) |
| **Control Status** | Implemented |
| **Residual Risk** | **Low** - session recording provides forensic evidence; JIT TTL limits exposure window; behavioral analysis of session content can distinguish legitimate from anomalous activity |
| **Recommended Mitigation** | Implement session anomaly detection rules (unexpected commands, off-hours access, rapid privilege escalation patterns) in Datadog |

### R-03: Workflow Modification Without Change Trail

**Trust Boundary:** svc-automation internal state
**Affected Services:** svc-automation
**Description:** An operator or compromised process modifies n8n workflow logic directly via the UI or API without creating a traceable change record. Since svc-automation maintains its own workflow state in svc-db, changes made outside the IaC pipeline may not be captured in version control.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | svc-automation maintains workflow_history in svc-db (Implemented); exported workflow JSONs committed to version control (Partial - not automated); svc-gateway session recording captures UI interactions (Implemented) |
| **Control Status** | Partial - no automated workflow change detection or alerting |
| **Residual Risk** | **Medium** - manual workflow exports mean drift between deployed and version-controlled state can occur undetected |
| **Recommended Mitigation** | Implement automated workflow export and diff detection on a daily schedule; alert on workflow modifications not preceded by a version control commit |

### R-04: Falco Rule Modification to Suppress Detection

**Trust Boundary:** net-monitoring
**Affected Services:** svc-detection (Falco), svc-detection-router (Falcosidekick)
**Description:** An attacker with host access modifies Falco detection rules to suppress alerts for their malicious activity, then restores the original rules after completing their objective. Without integrity monitoring on the rule files, this modification would leave no trace.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Falco rules deployed via Docker Compose volume mount (Implemented); svc-detection-router forwards all alerts to Datadog (Implemented); svc-gateway session recording captures host-level file modifications (Implemented) |
| **Control Status** | Partial - no file integrity monitoring on Falco rule files |
| **Residual Risk** | **Medium** - session recording provides forensic evidence but does not prevent or detect real-time rule tampering |
| **Recommended Mitigation** | Implement file integrity monitoring (FIM) on Falco rule directories; deploy a canary rule that generates a periodic heartbeat alert - absence of the heartbeat indicates rule tampering |

---

## 7. Information Disclosure (I)

Threats where an attacker gains unauthorized access to confidential data.

### I-01: PII Leakage Through AI Inference Pipeline (AI-Specific)

**Trust Boundary:** TB-5 (svc-ai-gateway → Anthropic API)
**Affected Services:** svc-ai-gateway (AI-001)
**OWASP LLM:** LLM02 (Sensitive Information Disclosure)
**Description:** User prompts processed by AI-001 may contain personally identifiable information (PII), operational secrets, or sensitive system context. This data is transmitted to the Anthropic API for inference, creating an external data flow that crosses the authorization boundary. Anthropic's data retention and processing practices determine the exposure window.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Prompt sanitization rules preventing credential injection (Implemented); PII-aware logging that redacts sensitive fields before persistence (Partial); Anthropic data processing agreement reviewed (Implemented); no credential or secret values included in AI prompts by policy (Implemented) |
| **Control Status** | Partial - automated PII detection and scrubbing of prompts before external transmission not yet deployed |
| **Residual Risk** | **Medium** - policy controls are effective for known sensitive data patterns, but novel PII exposure paths (e.g., user-provided PII in Telegram messages) may not be caught by static rules |
| **Recommended Mitigation** | Deploy automated PII detection (regex + NER-based) at svc-ai-gateway before prompts are sent to external APIs; implement prompt content classification with configurable sensitivity thresholds |

### I-02: Environment Variable Exposure via Container Logs

**Trust Boundary:** Container runtime → svc-log-router → svc-monitor
**Affected Services:** All containers (especially svc-automation)
**Description:** Secrets injected as environment variables are accessible to any process within the container. A debug log statement, stack trace, core dump, or misconfigured verbose logging level could write secrets to container stdout/stderr, which svc-log-router ships to external monitoring (Datadog).

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Local log rotation (10MB x 3 files) bounds on-disk cache before shipping, not a prevention control (Implemented); Gitleaks scanning in CI prevents hardcoded secrets (Implemented); .gitignore for sensitive files (Implemented); external secrets manager as authoritative source (Implemented); log level restricted to info/warn in production (Implemented) |
| **Control Status** | Partial - no runtime log scrubbing for secret patterns at svc-log-router |
| **Residual Risk** | **Moderate** (aligned with R-10 in RISK_ASSESSMENT.md as the authoritative source). This remains the highest residual Information Disclosure threat in the model, but the rating harmonizes with the parent risk register. |
| **Recommended Mitigation** | Implement regex-based secret scrubbing rules in Fluentd configuration; migrate from environment variable secrets to mounted tmpfs files; add automated secret pattern scanning on log streams |

### I-03: System Prompt Extraction via AI Agent (AI-Specific)

**Trust Boundary:** TB-7 (Telegram → svc-ai-gateway)
**Affected Services:** svc-ai-gateway (AI-001)
**OWASP LLM:** LLM01 (Prompt Injection)
**Description:** An attacker crafts messages designed to cause the AI agent to reveal its system prompt, which may contain operational context, service names, capability descriptions, or security control details that aid further attacks.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | System prompt stored server-side, not embedded in user-visible context (Implemented); system prompt instructs the model not to disclose its instructions (Implemented); rate limiting prevents mass extraction attempts (Implemented); chat ID allowlist restricts who can query the agent (Implemented) |
| **Control Status** | Implemented |
| **Residual Risk** | **Low** - the combination of access restriction and prompt hardening makes extraction difficult; even successful extraction reveals limited operational detail due to sanitized prompt content |
| **Recommended Mitigation** | Deploy canary tokens within system prompts to detect extraction; implement output filtering that detects and blocks responses containing system prompt fragments |

### I-04: Database Credential Exposure via svc-automation Code Nodes

**Trust Boundary:** svc-automation container runtime
**Affected Services:** svc-automation, svc-db
**Description:** svc-automation's Code (JavaScript) nodes execute arbitrary code within the n8n container. These nodes have access to all environment variables, including database credentials, API keys, and tokens. A misconfigured or malicious Code node could read and exfiltrate these values via webhook response, log output, or database write.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Workflow access restricted to authenticated operators (Implemented); svc-detection monitors for unexpected network connections from svc-automation (Implemented); Code node outputs logged in workflow execution history (Implemented) |
| **Control Status** | Partial - no sandbox isolation of Code node execution environment from container environment variables |
| **Residual Risk** | **Medium** - any workflow with a Code node can access all secrets in the container's environment |
| **Recommended Mitigation** | Restrict environment variable visibility in svc-automation Code nodes; implement svc-secrets dynamic credential injection scoped to individual workflow needs; deploy egress network policy on svc-automation limiting outbound destinations |

### I-05: Monitoring Data Exfiltration via Compromised Datadog Agent

**Trust Boundary:** TB-6 (Monitoring zone → Datadog SaaS)
**Affected Services:** svc-monitor (Datadog Agent)
**Description:** Datadog Agent collects metrics, logs, traces, and Falco alerts from all containers. If the Datadog API key is compromised, an attacker could query the Datadog API to access the full operational telemetry of the platform - including log contents, performance metrics, and security alerts.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Datadog API key stored in external secrets manager (Implemented); separate API keys for different integrations (Implemented); Datadog RBAC restricts dashboard access (Implemented) |
| **Control Status** | Implemented |
| **Residual Risk** | **Low** - key compromise would require breaching the secrets manager or container environment; Datadog access controls provide defense-in-depth |
| **Recommended Mitigation** | Implement Datadog API key rotation on a quarterly cadence; configure Datadog audit logging to detect anomalous API access patterns |

---

## 8. Denial of Service (D)

Threats where an attacker degrades or eliminates service availability.

### D-01: Volumetric DDoS Against Tunnel Ingress

**Trust Boundary:** TB-1 (Internet → Cloudflare edge)
**Affected Services:** svc-tunnel, all services behind tunnel
**Description:** An attacker launches a volumetric DDoS attack against the public-facing Cloudflare Tunnel endpoint. While Cloudflare absorbs volumetric attacks, application-layer floods targeting specific webhook endpoints could exhaust svc-automation resources.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Cloudflare DDoS protection (automatic L3/L4 mitigation) (Implemented); Cloudflare WAF with rate limiting rules (Implemented); cloud firewall deny-all default (only tunnel traffic allowed) (Implemented) |
| **Control Status** | Implemented |
| **Residual Risk** | **Low** - Cloudflare's edge network absorbs volumetric attacks; application-layer attacks are rate-limited at the WAF |
| **Recommended Mitigation** | Configure Cloudflare Bot Management for webhook endpoints; implement circuit breaker patterns in svc-automation for high-volume webhook ingestion |

### D-02: AI Service Exhaustion via Adversarial Input Flooding

**Trust Boundary:** TB-7 (Telegram → svc-ai-gateway)
**Affected Services:** svc-ai-gateway (AI-001), Anthropic API budget
**OWASP LLM:** LLM10 (Unbounded Consumption)
**Description:** An attacker floods the AI agent with high-complexity prompts designed to maximize token consumption, exhausting the Anthropic API budget or triggering rate limits that deny service to legitimate users. Resource exhaustion of the local svc-ai-gateway container is also possible.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Rate limiting at svc-ai-gateway (Implemented); Anthropic API budget caps (Implemented); chat ID allowlist restricts access to authorized users (Implemented); container resource limits (CPU/memory) on svc-ai-gateway (Implemented) |
| **Control Status** | Implemented |
| **Residual Risk** | **Low** - the combination of access restriction and rate limiting effectively bounds resource consumption |
| **Recommended Mitigation** | Implement per-user daily token budget tracking; add prompt length validation before API submission; configure alerting on API spend anomalies |

### D-03: Resource Exhaustion on Shared Compute

**Trust Boundary:** Host OS resource allocation
**Affected Services:** All containers (single-node constraint)
**Description:** A misbehaving or compromised container consumes excessive CPU, memory, or disk I/O on the single VPS, starving other containers. The svc-llm (Ollama) service is particularly resource-intensive during inference and could crowd out critical services like svc-db or svc-detection.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Docker resource limits (CPU shares, memory limits) on most containers (Partial - not all containers have hard limits); container restart policies (Implemented); Datadog resource monitoring with alerting thresholds (Implemented) |
| **Control Status** | Partial - resource limits not uniformly enforced across all 20 containers |
| **Residual Risk** | **Medium** - svc-llm inference can spike to 4+ GB RAM; without hard limits, OOM conditions could affect co-resident services |
| **Recommended Mitigation** | Enforce hard memory limits and CPU quotas on all containers via Docker Compose; implement OOM priority scoring to protect critical services (svc-db, svc-detection, svc-tunnel) |

### D-04: PostgreSQL Connection Exhaustion

**Trust Boundary:** TB-3 (DMZ → Internal zone)
**Affected Services:** svc-db, svc-automation, svc-identity
**Description:** Multiple services connect to svc-db (PostgreSQL). A connection leak in svc-automation workflows or a flood of concurrent requests could exhaust the PostgreSQL connection pool, denying database access to all services including svc-identity (authentication) and svc-gateway (audit logging).

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | PostgreSQL max_connections configured (Implemented); svc-automation connection pooling (Implemented); Datadog PostgreSQL monitoring with connection count alerting (Implemented) |
| **Control Status** | Implemented |
| **Residual Risk** | **Low** - connection monitoring provides early warning; connection limits prevent unbounded growth |
| **Recommended Mitigation** | Implement per-service connection limits at the PostgreSQL level using role-based connection quotas; deploy PgBouncer for connection pooling if connection pressure increases |

### D-05: Cloudflare Tunnel Disruption

**Trust Boundary:** svc-tunnel → Cloudflare edge
**Affected Services:** svc-tunnel, all externally-accessible services
**Description:** If svc-tunnel loses its connection to Cloudflare (misconfiguration, token revocation, container crash), all external access to the platform is severed - including svc-automation webhooks, SSH access, and AI agent interactions. Since svc-tunnel is the sole public ingress, this is a single point of failure.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Container restart policy (always) for svc-tunnel (Implemented); Datadog monitoring of tunnel container health (Implemented); Cloudflare dashboard tunnel status visibility (Implemented); direct SSH as out-of-band access path (Implemented) |
| **Control Status** | Implemented |
| **Residual Risk** | **Low** - automatic restart handles transient failures; direct SSH provides recovery path; Cloudflare infrastructure has high availability |
| **Recommended Mitigation** | Implement tunnel health check endpoint with external uptime monitoring; document and test the out-of-band SSH recovery procedure quarterly |

---

## 9. Elevation of Privilege (E)

Threats where an attacker gains capabilities beyond their authorized level.

### E-01: Container Breakout via Kernel Exploit

**Trust Boundary:** Container runtime → host OS
**Affected Services:** All containers (especially svc-detection which has SYS_ADMIN capability)
**Description:** An attacker who has compromised a container exploits a kernel vulnerability or Docker runtime flaw to escape the container and gain host-level access. From the host, the attacker has unrestricted access to all container volumes, Docker socket, and secrets.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | no-new-privileges on 18/19 containers (Implemented); only svc-detection has SYS_ADMIN (required for eBPF, documented exception) (Implemented); PID limits (Implemented); read-only rootfs where feasible (Partial); Docker socket not mounted into non-privileged containers (Implemented); Falco eBPF detection of container escape attempts (Implemented) |
| **Control Status** | Implemented |
| **Residual Risk** | **Medium** - svc-detection's SYS_ADMIN capability is the highest-risk container; a kernel zero-day combined with SYS_ADMIN could enable breakout |
| **Recommended Mitigation** | Evaluate gVisor or Kata Containers for high-risk workloads; implement host-level seccomp profiles; maintain aggressive kernel patching cadence |

### E-02: Excessive AI Agent Autonomy (AI-Specific)

**Trust Boundary:** svc-ai-gateway → svc-automation → all integrated services
**Affected Services:** svc-ai-gateway (AI-001), svc-automation
**OWASP LLM:** LLM06 (Excessive Agency)
**Description:** The AI agent, through its integration with svc-automation, has access to multiple downstream actions (database queries, Telegram messaging, GitHub operations, cloud infrastructure management). If the AI makes an incorrect decision or is manipulated via prompt injection, it could execute privileged actions beyond what the user intended - including infrastructure modifications, data deletion, or credential operations.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Human approval gates for destructive actions in svc-automation (Implemented); action allowlist restricting which workflows the AI can trigger (Implemented); AI-initiated actions logged with full audit trail (Implemented); no AI access to credential rotation or container lifecycle operations (Implemented) |
| **Control Status** | Implemented |
| **Residual Risk** | **Medium** - the allowlist reduces scope, but the breadth of available non-destructive actions (database reads, messaging, API calls) still represents a meaningful privilege surface |
| **Recommended Mitigation** | Implement tiered action authorization: Level 1 (read-only, no approval needed), Level 2 (state-changing, requires user confirmation), Level 3 (infrastructure-affecting, requires MFA); add per-session action budgets to limit blast radius of a single compromised interaction |

### E-03: Privilege Escalation via svc-identity Misconfiguration

**Trust Boundary:** TB-4 (DMZ → Sensitive zone)
**Affected Services:** svc-identity (Keycloak), svc-gateway (Teleport)
**Description:** A misconfiguration in Keycloak RBAC - such as an overly permissive client scope, a misconfigured mapper, or a default role assignment - could grant an attacker elevated privileges. In combination with svc-gateway, this could escalate from read-only auditor access to administrative SSH.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | 3-tier RBAC model (admin/operator/auditor) documented in IAM RBAC Role Map (Implemented); monthly access reviews (Implemented); JIT admin access with 4-hour TTL via svc-gateway (Implemented); Keycloak admin console access restricted (Implemented) |
| **Control Status** | Implemented |
| **Residual Risk** | **Low** - the single-operator environment limits the attack surface for role misconfiguration; JIT access prevents persistent privilege |
| **Recommended Mitigation** | Implement automated Keycloak configuration drift detection; add alerting on role assignment changes; document and test the RBAC model quarterly |

### E-04: Lateral Movement from AI Container to Sensitive Zone

**Trust Boundary:** net-ai → net-core → Sensitive zone
**Affected Services:** svc-llm (AI-002), svc-ai-gateway (AI-001), svc-secrets, svc-identity
**MITRE ATLAS:** AML.T0040 (ML-Enabled Lateral Movement)
**Description:** An attacker who has compromised an AI container (via model exploit, prompt injection leading to code execution, or supply chain attack) uses the container's network position to reach services in other trust zones. If network segmentation is incomplete, the compromised AI container could access svc-secrets or svc-identity.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Docker network segmentation: net-ai isolated from net-monitoring (Implemented); svc-llm has no internet egress (Implemented); svc-secrets requires token-based authentication (Implemented); Falco detects unexpected network connections (Implemented) |
| **Control Status** | Implemented |
| **Residual Risk** | **Medium** - net-core connects DMZ and Internal services; a compromised container on net-core has a broader lateral movement surface than desired |
| **Recommended Mitigation** | Implement micro-segmentation within net-core to restrict inter-service communication to documented data flows only; deploy network policies that enforce a zero-trust model between containers |

### E-05: Host Root Access via Docker Socket Exposure

**Trust Boundary:** Container runtime → host OS
**Affected Services:** Host OS, Docker daemon
**Description:** If the Docker socket (`/var/run/docker.sock`) is mounted into any container, that container effectively has root access to the host - it can create new privileged containers, access any volume, and modify the Docker runtime configuration.

| Attribute | Assessment |
|-----------|------------|
| **Current Controls** | Docker socket is NOT mounted into any application container (Implemented); only the Docker daemon process on the host has socket access (Implemented); svc-detection uses eBPF (kernel-level) rather than Docker socket for monitoring (Implemented) |
| **Control Status** | Implemented |
| **Residual Risk** | **Low** - the Docker socket is not exposed to any container; this is a critical control that is verified in CIS Docker Bench scans |
| **Recommended Mitigation** | Add an OPA policy to the CI/CD pipeline that blocks any Docker Compose change introducing a Docker socket mount; include Docker socket verification in monthly CIS scans |

---

## 10. AI-Specific STRIDE Extensions

The following threats are AI-specific extensions of traditional STRIDE categories, mapped to the three AI systems in the inventory.

### 10.1 Summary of AI Threat Mapping to STRIDE

| AI Threat | Primary STRIDE Category | Secondary Category | AI System | Reference |
|-----------|------------------------|-------------------|-----------|-----------|
| Prompt Injection | **Tampering** (T-01) | Elevation of Privilege | AI-001 | OWASP LLM01, AI-T02 |
| Model Weight Poisoning | **Tampering** (T-02) | Information Disclosure | AI-002 | OWASP LLM03 (Supply Chain), LLM04 (Data and Model Poisoning), AI-T06, AML.T0018 |
| PII Leakage in Prompts | **Information Disclosure** (I-01) | Repudiation | AI-001 | OWASP LLM02 (Sensitive Information Disclosure), AI-T07 |
| System Prompt Extraction | **Information Disclosure** (I-03) | Spoofing | AI-001 | OWASP LLM07 (System Prompt Leakage), AI-T10 |
| Excessive Autonomous Agency | **Elevation of Privilege** (E-02) | Tampering | AI-001 | OWASP LLM06 (Excessive Agency), AI-T09 |
| AI Denial of Service | **Denial of Service** (D-02) | - | AI-001, AI-002 | OWASP LLM10 (Unbounded Consumption), AI-T08 |
| Hallucination-Driven Actions | **Tampering** | Repudiation | AI-001, AI-002 | OWASP LLM09 (Misinformation), AI-T01 |
| Training Data Extraction | **Information Disclosure** | - | AI-001 | OWASP LLM02 (Sensitive Information Disclosure), AI-T10 |
| AI-Enabled Lateral Movement | **Elevation of Privilege** (E-04) | - | AI-001, AI-002 | AML.T0040 |
| Improper Output Handling | **Tampering** | Elevation of Privilege | AI-001 | OWASP LLM05 (Improper Output Handling) |

### 10.2 Control Coverage for AI STRIDE Threats

| AI STRIDE Threat | Prevention Controls | Detection Controls | Response Controls | Gap |
|------------------|--------------------|--------------------|-------------------|-----|
| Prompt Injection | System prompt hardening; input validation; output sanitization | Falco behavioral monitoring; prompt/response logging | Rate limiting; chat ID allowlist; human approval gates | Automated prompt firewall (Planned) |
| Model Poisoning | Trivy scanning; SBOM; no auto-updates | Checksum verification (manual) | Model rollback to known-good version | Automated integrity pipeline (Planned) |
| PII Leakage | Policy prohibition; prompt sanitization rules | PII-aware logging (Partial) | Incident response per POL-IR-001 | Automated PII scrubbing (Planned) |
| Excessive Agency | Action allowlist; human approval gates; no destructive AI access | Audit logging of all AI-initiated actions | Action budget enforcement; session termination | Tiered authorization model (Planned) |
| AI DoS | Rate limiting; budget caps; access restrictions | Datadog resource monitoring; API spend alerting | Fallback to svc-llm; circuit breaker | Per-user token budgets (Planned) |

---

## 11. Threat-Control Mapping

The following table maps every STRIDE threat identified in this analysis to the NIST 800-53 controls documented in the SSP (SSP-OPS-001) and the AI Governance Policy (POL-AI-001).

| Threat ID | STRIDE | Threat Name | NIST 800-53 Controls | SSP Reference | Status |
|-----------|--------|-------------|---------------------|---------------|--------|
| S-01 | Spoofing | Webhook Request Spoofing | IA-2, IA-8, SC-23 | AC/IA families | Implemented |
| S-02 | Spoofing | Telegram User Impersonation | IA-2, IA-4, AC-3 | AC/IA families | Implemented |
| S-03 | Spoofing | Internal Service Identity Spoofing | IA-3, SC-8, SC-23 | SC family | Partial (mTLS planned) |
| S-04 | Spoofing | Forged Audit Log Entries | AU-10, AU-3, SI-4 | AU family | Partial |
| S-05 | Spoofing | Cloudflare Tunnel Origin Spoofing | IA-3, SC-7, SC-8 | SC family | Implemented |
| T-01 | Tampering | Prompt Injection (AI) | SI-10, SA-15, SI-4 | POL-AI-001 Sec. 12 | Implemented |
| T-02 | Tampering | Model Weight Poisoning (AI) | SA-12, SI-7, SA-22 | POL-AI-001 Sec. 11 | Partial |
| T-03 | Tampering | IaC State Tampering | CM-3, CM-5, SI-7 | CM family | Implemented |
| T-04 | Tampering | Database Record Manipulation | AC-3, AC-6, AU-12 | AC/AU families | Partial |
| T-05 | Tampering | Container Image Tampering | SI-7, SA-12, SA-22 | SA/SI families | Implemented |
| R-01 | Repudiation | Unattributed AI Agent Actions | AU-2, AU-3, AU-12 | AU family, POL-AI-001 Sec. 13 | Partial |
| R-02 | Repudiation | SSH Session Non-Attribution | AU-2, AU-14, AC-2 | AU family | Implemented |
| R-03 | Repudiation | Workflow Modification | AU-12, CM-3, CM-5 | CM family | Partial |
| R-04 | Repudiation | Falco Rule Suppression | AU-9, SI-4, SI-7 | SI family | Partial |
| I-01 | Info Disclosure | PII Leakage via AI Pipeline (AI) | SC-28, SI-12, PM-25 | POL-AI-001 Sec. 9 | Partial |
| I-02 | Info Disclosure | Env Variable Secret Exposure | SC-28, SC-4, SI-11 | SC family | Partial |
| I-03 | Info Disclosure | System Prompt Extraction (AI) | AC-3, SC-7, SI-10 | POL-AI-001 Sec. 12 | Implemented |
| I-04 | Info Disclosure | Code Node Credential Access | AC-6, SC-4, CM-7 | AC family | Partial |
| I-05 | Info Disclosure | Monitoring Data Exfiltration | SC-8, IA-2, AC-3 | SC family | Implemented |
| D-01 | Denial of Service | DDoS via Tunnel Ingress | SC-5, SC-7, CP-2 | SC/CP families | Implemented |
| D-02 | Denial of Service | AI Input Flooding (AI) | SC-5, SI-10, CP-2 | POL-AI-001 Sec. 12 | Implemented |
| D-03 | Denial of Service | Resource Exhaustion | SC-5, SC-6, CP-2 | SC family | Partial |
| D-04 | Denial of Service | Database Connection Exhaustion | SC-5, SC-6, CP-2 | SC family | Implemented |
| D-05 | Denial of Service | Tunnel Disruption | CP-2, CP-7, SC-7 | CP family | Implemented |
| E-01 | Elevation of Privilege | Container Breakout | AC-6, SC-39, SI-7 | AC/SC families | Implemented |
| E-02 | Elevation of Privilege | Excessive AI Agency (AI) | AC-6, CM-7, SI-10 | POL-AI-001 Sec. 8 | Implemented |
| E-03 | Elevation of Privilege | RBAC Misconfiguration | AC-2, AC-3, AC-6 | AC family | Implemented |
| E-04 | Elevation of Privilege | Lateral Movement from AI Container | SC-7, AC-4, SI-4 | SC family, POL-AI-001 | Implemented |
| E-05 | Elevation of Privilege | Docker Socket Exposure | AC-6, CM-7, SC-39 | AC/CM families | Implemented |

---

## 12. Summary and Prioritized Actions

### 12.1 Risk Distribution

| Residual Risk | Count | Percentage |
|---------------|-------|------------|
| **High** | 1 (I-02) | 3% |
| **Medium** | 14 | 48% |
| **Low** | 14 | 48% |

### 12.2 Top 5 Prioritized Actions

| Priority | Threat | Action | Target Date | Owner |
|----------|--------|--------|-------------|-------|
| 1 | I-02 (Env Variable Exposure) | Deploy Fluentd log scrubbing rules for secret patterns; migrate to tmpfs-mounted secrets | 2026-06-12 | Information Security Officer |
| 2 | T-01 (Prompt Injection) | Implement prompt firewall with input/output classification at svc-ai-gateway | 2026-06-12 | Information Security Officer |
| 3 | E-02 (Excessive AI Agency) | Deploy tiered action authorization model with per-session action budgets | 2026-09-12 | Information Security Officer |
| 4 | T-02 (Model Poisoning) | Automate model integrity verification pipeline with behavioral regression testing | 2026-09-12 | Information Security Officer |
| 5 | S-03 (Service Identity Spoofing) | Implement mTLS between services; migrate to svc-secrets dynamic credentials | 2026-09-12 | Information Security Officer |

---

## 12.5 Phase 17 Scope Extension: Squire Subsystem STRIDE

> **Key Point:** The Squire autonomous SOC analyst subsystem introduces 6 new components. STRIDE rows below map each Squire component to each STRIDE category with the Phase 17 control that resists the threat. `SQUIRE_THREAT_MODEL.md` is the integrated authoritative Squire-scope threat view.

<!-- TODO(et): "patched Langfuse v3" in svc-langfuse-web row is vague. Cite the specific Langfuse v3 minor and the CVE-XXXX-NNNN that motivated the patch. -->
<!-- TODO(et): Section 12.5 Squire/NeMo/Langfuse components live as an addendum here but are not yet integrated into Section 2 Trust Zones / Authorization Boundary. Integrate or formally call out the scope split. -->

### 12.5.1 Squire components x STRIDE

| Component | S (Spoofing) | T (Tampering) | R (Repudiation) | I (Info Disclosure) | D (Denial of Service) | E (Elevation) |
|-----------|--------------|---------------|-----------------|---------------------|------------------------|---------------|
| svc-squire | Threat: forged X-Squire-Token. Control: HMAC token, ephemeral, 60-day rotation (HITL_POLICY 6). | Threat: modified alert payload. Control: pre-graph PII scanner plus NeMo input rail. | Threat: missing audit trail. Control: Langfuse trace every invocation (AI_AUDIT_TRAIL_SPEC). | Threat: PII in logs. Control: pre-graph block returns reason_code only, no raw payload. | Threat: runaway alert flood. Control: Cloudflare rate limit, cost ceiling. | Threat: privileged action without HITL. Control: actions allow-list plus HITL gate on HIGH/CRITICAL. |
| svc-nemo | Threat: Colang bypass. Control: deny-by-default, tested rail coverage. | Threat: rail config tamper. Control: read-only mount, change control via git. | Threat: rail decision not logged. Control: rail invocation trace to Langfuse. | Threat: rail output exposes secrets. Control: output rail presidio PII strip. | Threat: rail overload. Control: NeMo worker pool sized for peak load. | Threat: rail escape to host. Control: container non-root, read-only rootfs. |
| svc-langfuse-web | Threat: fake trace ingest. Control: project-scoped API key. | Threat: trace body modified. Control: ClickHouse immutable append. | Threat: gap in trace chain. Control: span parent ID enforcement. | Threat: trace data contains PII. Control: SDK sanitize plus classification per SQUIRE_DATA_FLOW_CLASSIFICATION. | Threat: trace backlog. Control: worker auto-scale, Redis dedup. | Threat: admin UI RCE. Control: least-privilege role, patched Langfuse v3. |
| svc-langfuse-worker | Threat: worker impersonation. Control: dedicated network, no public ingress. | Threat: processed span rewrite. Control: worker writes append-only to ClickHouse. | Threat: lost span. Control: Redis dedup plus retry with backoff. | Threat: worker logs leak. Control: log level INFO, redact at SDK. | Threat: worker saturation. Control: horizontal worker scaling. | Threat: worker privilege drift. Control: read-only rootfs, minimal syscalls. |
| svc-langfuse-clickhouse | Threat: query injection. Control: parameterized queries only. | Threat: trace row mutation. Control: append-only semantics. | Threat: schema drift. Control: migration review in change control. | Threat: dump via malformed query. Control: role-scoped DB user. | Threat: storage exhaustion. Control: 90-day retention plus disk alert. | Threat: ClickHouse admin access. Control: no external ingress, admin over bastion only. |
| svc-langfuse-redis | Threat: key collision. Control: dedicated DB index. | Threat: cache poison. Control: short TTL 24h, dedup-only use. | Threat: lost replay token. Control: primary writes to ClickHouse, Redis is cache only. | Threat: Redis exposes dedup keys. Control: internal network only. | Threat: Redis memory blow. Control: maxmemory-policy allkeys-lru. | Threat: Redis command abuse. Control: no CONFIG, no FLUSH in ACL. |

### 12.5.2 Cross-reference

See `ATTACK_TREE_AI_PIPELINE.md` Phase 17 Scope Extension for the 3 new Squire-specific attack roots. See `AI_THREAT_CATALOG.md` Phase 17 Mitigation Addendum for per-threat Phase 17 controls. See `SQUIRE_SSP.md` for the 36 Squire control implementations. See `REDTEAM_RESULTS.md` for 6 executed red-team cases.

---

## 13. Related Documents

| Document | Relationship |
|----------|-------------|
| [RISK_ASSESSMENT.md](RISK_ASSESSMENT.md) | Quantitative risk analysis (17 scenarios); this STRIDE model provides structural decomposition |
| [ATTACK_TREE_AI_PIPELINE.md](ATTACK_TREE_AI_PIPELINE.md) | Attack tree for AI inference pipeline compromise, detailed path analysis |
| [AI_THREAT_CATALOG.md](AI_THREAT_CATALOG.md) | Comprehensive AI threat catalog with OWASP/MITRE/NIST mapping |
| [POLICY_AI_GOVERNANCE.md](POLICY_AI_GOVERNANCE.md) | AI governance policy including AI risk register (AI-R01 through AI-R10) |
| [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) | Control implementations referenced in the Threat-Control Mapping (Section 11) |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | Tracks remediation actions for identified gaps |
| [PLAYBOOK_COMPROMISED_CONTAINER.md](PLAYBOOK_COMPROMISED_CONTAINER.md) | Response procedures for threats E-01, E-04, T-04 |
| [PLAYBOOK_LEAKED_CREDENTIAL.md](PLAYBOOK_LEAKED_CREDENTIAL.md) | Response procedures for threats I-02, I-04 |

## Phase 20.1 Mitigation Update (2026-09-01)

Five controls shipped in Phase 20.1 close attack paths identified in this model. Implementation detail lives in the Terraform repo; residual items are tracked in the POA&M.

| # | New control | Attack path closed | STRIDE category |
|---|-------------|--------------------|-----------------|
| 1 | Remote Terraform state in versioned, locked OCI Object Storage | State file in git exposing credentials and topology | Information Disclosure |
| 2 | GitHub OIDC token exchange for CI, zero stored cloud keys | Theft of long-lived CI cloud keys | Elevation of Privilege |
| 3 | Customer-managed key (CMK) envelope encryption on state and backup buckets | Provider-default-only encryption at rest | Information Disclosure |
| 4 | Retention-locked immutable backups with monthly timed restores | Ransomware deleting backups before detonation | Tampering |
| 5 | Nightly drift detection with Telegram alerting | Unreviewed console changes persisting undetected; window now under 24 hours | Tampering |

---

*This threat model is a living document. It SHALL be reviewed semi-annually or after any significant architectural change, new service deployment, or security incident. The next scheduled review is 2026-09-12.*
