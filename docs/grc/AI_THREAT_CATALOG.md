---
document_id: AITC-OPS-001
title: AI Threat Catalog
doc_type: threat_catalog
system_name: Organization Security Operations Platform
classification: INTERNAL-USE-ONLY
version: "1.1"
last_updated: 2026-09-04
next_review: 2026-07-24
owner: System Owner
assessment_date: 2026-03-12
frameworks:
  - OWASP LLM Top 10 (2026)
  - OWASP Agentic Applications Top 10 (2026)
  - MITRE ATLAS v4
  - NIST AI RMF (AI 100-1)
  - ISO/IEC 42001:2023
nist_controls:
  - RA-3
  - RA-5
  - PM-16
  - SI-5
related:
  - TM-SQUIRE-001
  - RT-SQUIRE-001
  - POAM-OPS-001
---

> **Status note (2026-09-01):** this document describes the DigitalOcean-era baseline as assessed. That environment was retired 2026-08. The platform now runs on an Oracle Cloud (OCI) ARM instance with a partial stack (3 containers live); the remaining services are pending ARM rebuild. A re-baseline of this document is queued and tracked in the POA&M.

# AI Threat Catalog

**Organization:** Organization Security Operations Platform
**Assessment Date:** 2026-03-12
**Assessor:** System Owner
**Framework References:** OWASP LLM Top 10 (2026), OWASP Agentic Applications Top 10 (2026), MITRE ATLAS v4, NIST AI RMF (AI 100-1), ISO/IEC 42001:2023
**NIST 800-53 Controls:** RA-3 (Risk Assessment), RA-5 (Vulnerability Monitoring), PM-16 (Threat Awareness Program), SI-5 (Security Alerts and Advisories)
**Classification:** Internal Use Only
**Version:** 1.2 (OWASP 2026 renumbering 2026-09-04)

---

## Document Control

| Field | Value |
|-------|-------|
| Document ID | ATC-AI-001 |
| Version | 1.0 |
| Status | Approved |
| Last Revised | 2026-03-12 |
| Next Review | 2026-09-12 |
| Author | Information Security Officer |
| Approver | System Owner |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-03-12 | Information Security Officer | Initial AI threat catalog with cross-framework mapping |
| 1.1 | 2026-04-24 | Information Security Officer | Phase 17 Mitigation Addendum added. Per-threat Phase 17 controls: pre_graph_pii, NeMo rails, cost ceiling, HITL, actions allow-list, citation validator, dedup, Ollama fallback. |
| 1.2 | 2026-09-04 | Information Security Officer | OWASP LLM Top 10 references renumbered to the 2026 edition (published 2026-08-04); OWASP Top 10 for Agentic Applications (2026) mapping added to sections 2.1a and 3.1 |

---

### AI Threat Kill Chain

<!-- TODO(et): Kill chain ASCII below uses OWASP LLM Top 10 (2023) numbering and label set (LLM02 Insecure Output, LLM05 Supply Chain, LLM06 Sensitive Info, LLM07 Insecure Plugin, LLM08 Excessive Agency, LLM09 Overreliance, LLM10 Model Theft). Regenerate using 2025 numbering: LLM01 Prompt Injection, LLM02 Sensitive Info Disclosure, LLM03 Supply Chain, LLM04 Data and Model Poisoning, LLM05 Improper Output Handling, LLM06 Excessive Agency, LLM07 System Prompt Leakage, LLM08 Vector and Embedding Weaknesses, LLM09 Misinformation, LLM10 Unbounded Consumption. -->

The following diagram maps the 10 OWASP LLM Top 10 threats through a kill chain
progression, showing how threats chain together from initial access through execution
to final impact.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         AI THREAT KILL CHAIN                                    │
│                  Initial Access ──> Execution ──> Impact                        │
└─────────────────────────────────────────────────────────────────────────────────┘

 INITIAL ACCESS                    EXECUTION                      IMPACT
 ──────────────                    ─────────                      ──────

 ┌──────────────────┐          ┌──────────────────┐         ┌──────────────────┐
 │  LLM01           │          │  LLM08           │         │  UNAUTHORIZED    │
 │  Prompt Injection ├────────>│  Excessive Agency ├────────>│  ACTIONS         │
 │                  │          │                  │         │  (workflow exec, │
 └───────┬──────────┘          └──────────────────┘         │   infra changes) │
         │                                                  └──────────────────┘
         │
         │                     ┌──────────────────┐         ┌──────────────────┐
         └────────────────────>│  LLM06           ├────────>│  DATA BREACH     │
                               │  Sensitive Info   │         │  (creds, PII,    │
                               │  Disclosure       │         │   operational    │
 ┌──────────────────┐          └──────────────────┘         │   context)       │
 │  LLM02           │                                       └──────────────────┘
 │  Insecure Output ├────────> XSS + Downstream Injection
 │  Handling        ├────────> Rendered in messaging/workflows
 └──────────────────┘
                                                            ┌──────────────────┐
 ┌──────────────────┐          ┌──────────────────┐         │  IP LOSS         │
 │  LLM05           ├────────>│  LLM03           ├────────>│  (degraded model │
 │  Supply Chain    │          │  Training Data   │         │   integrity,     │
 │  Vulnerabilities │          │  Poisoning       │         │   backdoored     │
 └───────┬──────────┘          └──────────────────┘         │   inference)     │
         │                                                  └──────────────────┘
         │                     ┌──────────────────┐
         ├────────────────────>│  LLM10           ├────────> MODEL THEFT / IP LOSS
         │                     │  Model Theft     │
         │                     └──────────────────┘
         │
         └────────────────────> [Any Component Compromise]


 ┌──────────────────┐          ┌──────────────────┐         ┌──────────────────┐
 │  LLM07           │          │  LLM08           │         │  LATERAL         │
 │  Insecure Plugin ├────────>│  Excessive Agency ├────────>│  MOVEMENT        │
 │  Design          │          │  (via plugins)   │         │  (cross-service  │
 └──────────────────┘          └──────────────────┘         │   pivot)         │
                                                            └──────────────────┘

 ┌──────────────────┐
 │  LLM04           ├─────────────────────────────────────> AVAILABILITY LOSS
 │  Model Denial    │                                       (resource exhaust,
 │  of Service      │                                        API budget burn)
 └──────────────────┘

 ┌──────────────────┐
 │  LLM09           ├─────────────────────────────────────> TRUST EXPLOITATION
 │  Overreliance    │                                       (unverified AI output
 └──────────────────┘                                        accepted as truth)


 THREAT INTERACTION SUMMARY
 ──────────────────────────
 ┌────────────┬──────────────────────────────────────────────────────────┐
 │ Chain      │ Path                                                     │
 ├────────────┼──────────────────────────────────────────────────────────┤
 │ Injection  │ LLM01 ──> LLM08 ──> Unauthorized Actions                │
 │ Exfil      │ LLM01 ──> LLM06 ──> Data Breach                         │
 │ Output     │ LLM02 ──> XSS / Downstream Injection                    │
 │ Supply     │ LLM05 ──> LLM03 (poisoning) or LLM10 (theft)            │
 │ Plugin     │ LLM07 ──> LLM08 ──> Lateral Movement                    │
 │ DoS        │ LLM04 ──> Availability Loss                              │
 │ Trust      │ LLM09 ──> Trust Exploitation                             │
 └────────────┴──────────────────────────────────────────────────────────┘
```

---

## 1. Purpose

This document provides a comprehensive catalog of AI-specific threats applicable to the Organization Security Operations Platform. It maps each threat across four complementary frameworks - OWASP LLM Top 10, MITRE ATLAS, NIST AI RMF, and ISO 42001 - and documents the current control posture, detection capabilities, and cross-references to existing GRC documents.

The catalog serves as:

1. **A threat intelligence reference** for the Information Security Officer when assessing new AI deployments or configuration changes
2. **An audit artifact** demonstrating systematic identification and treatment of AI risks
3. **A control gap tracker** linking AI threats to their mitigation status and remediation timelines
4. **An interview-ready reference** mapping real controls to real frameworks on a production AI-integrated platform

This document complements the STRIDE Threat Model (`THREAT_MODEL_STRIDE.md`) and Attack Tree (`ATTACK_TREE_AI_PIPELINE.md`) by consolidating all AI threats into a single indexed catalog with full cross-framework traceability.

---

## 2. Framework Cross-Reference

### 2.1 OWASP LLM Top 10 (2026)

| OWASP ID | Category | Applicability to Organization Platform |
|----------|----------|---------------------------------------|
| LLM01 | Prompt Injection | **High** - svc-ai-gateway accepts external user input via Telegram; svc-llm processes internal workflow prompts |
| LLM02 | Sensitive Information Disclosure | **High** - prompts to Anthropic API may contain operational context; svc-llm processes sensitive internal data |
| LLM03 | Excessive Agency | **High** - AI agent can trigger svc-automation workflows with broad action capabilities (16+ service integrations) |
| LLM04 | Supply Chain | **Medium** - three AI models with different supply chain profiles (API, Ollama registry, Whisper open-weight) |
| LLM05 | Data and Model Poisoning | **Low** - no fine-tuning capability deployed; risk limited to upstream model provider compromise |
| LLM06 | Unbounded Consumption | **Medium** - external API budget and compute resource consumption need bounded controls |
| LLM07 | Misinformation | **Medium** - operator may trust AI outputs without verification for routine tasks (hallucinations, fabricated citations) |
| LLM08 | Hidden Context Exposure (was System Prompt Leakage) | **Medium** - system prompt exposure via extraction or trace-store retention could give adversaries a roadmap for targeted injection |
| LLM09 | Vector and Embedding Weaknesses | **Medium** - RAG over `ir_chunks` (pgvector) is a real surface; embedding-space adversarial chunks or poisoned retrievals could affect downstream responses |
| LLM10 | Improper Output Handling | **High** - AI outputs consumed by svc-automation workflows that execute actions on infrastructure; messaging platform rendering without full sanitization |

Renumbered 2026-09-04 to the 2026 edition. 2025 to 2026: Supply Chain LLM03 to LLM04, Data and Model Poisoning LLM04 to LLM05, Improper Output Handling LLM05 to LLM10, Excessive Agency LLM06 to LLM03, System Prompt Leakage LLM07 to Hidden Context Exposure LLM08, Vector and Embedding Weaknesses LLM08 to LLM09, Misinformation LLM09 to LLM07, Unbounded Consumption LLM10 to LLM06. Prompt Injection and Sensitive Information Disclosure keep LLM01 and LLM02.


### 2.1a OWASP Top 10 for Agentic Applications (2026)

Published 2025-12-09. Squire is a single tool-using agent with a recommend-only action vocabulary, so several categories map to no catalog entry.

| ID | Category | Catalog Threats | Relevance |
|----|----------|-----------------|-----------|
| ASI01 | Agent Goal Hijack | ATC-01, ATC-02 | **High** - alert payloads are attacker-influenced text that reaches the model; input rails and the human gate on HIGH and CRITICAL stand in front |
| ASI02 | Tool Misuse and Exploitation | ATC-06, ATC-07 | **Medium** - the actions allow-list is the only tool surface; nothing executes, the agent recommends |
| ASI03 | Identity and Privilege Abuse | ATC-07, ATC-10 | **Medium** - the agent holds a bearer token for its own webhook and vendor keys in its environment; scoped roles and short-lived credentials are the mitigation |
| ASI04 | Agentic Supply Chain | ATC-04 | **Medium** - digest-pinned images, baked PII models, no runtime model fetch |
| ASI05 | Unexpected Code Execution | - | **Low** - no code-execution tool in the vocabulary |
| ASI06 | Memory and Context Poisoning | ATC-02 | **Medium** - RAG over `ir_chunks` (pgvector) is the memory surface; ingest is operator-run from reviewed corpus |
| ASI07 | Insecure Inter-Agent Communication | - | **Low** - single agent, no agent-to-agent channel |
| ASI08 | Cascading Failures | - | **Low** - recommend-only output; the daily spend ceiling bounds runaway loops |
| ASI09 | Human-Agent Trust Exploitation | ATC-08 | **Medium** - operators may act on a confident wrong recommendation; citation guard and the HITL approval row are the mitigation |
| ASI10 | Rogue Agents | - | **Low** - no autonomous execution path exists to go rogue on |
### 2.2 MITRE ATLAS v4

| ATLAS Technique | Description | Applicable AI Systems |
|-----------------|-------------|----------------------|
| AML.T0015 | Evade ML Model | AI-001, AI-002 |
| AML.T0018 | Backdoor ML Model | AI-002, AI-003 |
| AML.T0040 | ML-Enabled Lateral Movement | AI-001, AI-002 |
| AML.T0043 | Adversarial Data Injection | AI-001, AI-002 |
| AML.T0029 | Denial of ML Service | AI-001, AI-002, AI-003 |
| AML.T0048 | Erode ML Model Integrity | AI-001, AI-002 |
| AML.T0051 | LLM Prompt Injection | AI-001, AI-002 |
| AML.T0054 | LLM Jailbreak | AI-001 |

### 2.3 NIST AI RMF (AI 100-1) Functions

| Function | Relevant Subcategories | Catalog Coverage |
|----------|----------------------|-----------------|
| **GOVERN** | 1.1 (Legal requirements), 2.1 (Roles), 2.2 (Risk processes) | Sections 3, 5 |
| **MAP** | 1.1 (Purpose/context), 2.3 (Limitations), 3.5 (Impact) | Section 3 (per-threat mapping) |
| **MEASURE** | 1.1 (Measurement approaches), 2.1 (Trustworthy evaluation), 2.6 (Performance monitoring) | Section 4 (detection capabilities) |
| **MANAGE** | 1.1 (Treatment plans), 3.2 (Incident response), 4.1 (Post-deployment monitoring) | Sections 3, 5 |

### 2.4 ISO/IEC 42001:2023 Annex A Controls

| ISO 42001 Control | Title | Catalog Mapping |
|-------------------|-------|-----------------|
| A.5 | Assessing AI System Impact | Threat risk ratings (Section 3) |
| A.6 | AI System Lifecycle | Control implementation status |
| A.8 | Information for Interested Parties | Transparency and detection documentation (Section 4) |
| A.9 | Use of AI Systems | Human oversight controls |
| A.10 | Third-Party Relationships | External AI provider risks (ATC-01, ATC-07) |

---

## 3. AI Threat Catalog

### 3.1 Master Threat Table

| ID | Threat | OWASP LLM | OWASP Agentic | MITRE ATLAS | AI System | Current Status | Residual Risk |
|----|--------|-----------|---------------|-------------|-----------|----------------|---------------|
| ATC-01 | Prompt Injection (Direct) | LLM01 | ASI01 | AML.T0051 | AI-001 | Implemented | Medium |
| ATC-02 | Prompt Injection (Indirect) | LLM01 | ASI01, ASI06 | AML.T0043, AML.T0051 | AI-001 | Partial | Medium |
| ATC-03 | Improper Output Handling | LLM10 | - | AML.T0015 | AI-001, AI-002 | Implemented | Medium |
| ATC-04 | Model Supply Chain Compromise | LLM04, LLM05 | ASI04 | AML.T0010, AML.T0018, AML.T0020 | AI-001, AI-002, AI-003 | Partial | Medium |
| ATC-05 | Sensitive Information Disclosure | LLM02 | - | AML.T0024 | AI-001 | Partial | Medium |
| ATC-06 | Insecure Skill/Plugin Execution | LLM03 | ASI02 | AML.T0040 | AI-001 | Implemented | Low |
| ATC-07 | Excessive Autonomous Agency | LLM03 | ASI02, ASI03 | - | AI-001 | Implemented | Medium |
| ATC-08 | Misinformation (formerly "Overreliance on AI Outputs") | LLM07 | ASI09 | - | AI-001, AI-002 | Partial | Medium |
| ATC-09 | Unbounded Resource Consumption | LLM06 | - | AML.T0029 | AI-001, AI-002, AI-003 | Implemented | Low |
| ATC-10 | AI-Enabled Lateral Movement | - | ASI03 | AML.T0040 | AI-001, AI-002 | Implemented | Medium |

### 3.2 Detailed Threat Profiles

---

#### ATC-01: Prompt Injection (Direct)

| Attribute | Detail |
|-----------|--------|
| **Description** | An attacker crafts input messages sent directly to the AI agent via Telegram that override system instructions, extract sensitive context, or trigger unintended actions through svc-automation. Direct injection targets the user-facing AI-001 system where external input is the primary interface. |
| **OWASP LLM** | LLM01 (Prompt Injection) |
| **OWASP Agentic** | ASI01 (Agent Goal Hijack) |
| **MITRE ATLAS** | AML.T0051 (LLM Prompt Injection) |
| **Affected Systems** | AI-001 (svc-ai-gateway) |
| **NIST AI RMF** | MANAGE 3.2, MEASURE 2.1 |
| **ISO 42001** | A.9 (Use of AI Systems) |
| **Control Description** | System prompt hardening with explicit instruction boundaries and refusal directives; output sanitization before workflow action execution; rate limiting at gateway level; chat ID allowlist restricting interaction to authorized users; full prompt/response logging shipped to monitoring platform |
| **Control Status** | **Implemented** |
| **Residual Risk** | **Medium** - prompt injection is an inherent limitation of current LLM architectures; controls reduce impact but cannot eliminate the vector |
| **Risk Assessment Cross-Ref** | POLICY_AI_GOVERNANCE.md → AI-R02; POLICY_AI_GOVERNANCE.md → AI-T02, Section 6.3 |
| **STRIDE Cross-Ref** | THREAT_MODEL_STRIDE.md → T-01 (Tampering) |
| **Attack Tree Cross-Ref** | ATTACK_TREE_AI_PIPELINE.md → Path 1, Nodes 1.1.1-1.1.3 |

---

#### ATC-02: Prompt Injection (Indirect)

| Attribute | Detail |
|-----------|--------|
| **Description** | Malicious instructions embedded in external data sources (web pages, documents, API responses) are retrieved by AI-001 skills (Tavily search, browser, GitHub, Notion) and processed as part of the AI's context. Unlike direct injection, the attacker does not interact with the AI directly - they poison data the AI will consume. |
| **OWASP LLM** | LLM01 (Prompt Injection - indirect variant) |
| **OWASP Agentic** | ASI01 (Agent Goal Hijack), ASI06 (Memory and Context Poisoning) |
| **MITRE ATLAS** | AML.T0043 (Adversarial Data Injection), AML.T0051 |
| **Affected Systems** | AI-001 (svc-ai-gateway) - specifically when executing search, browser, or data retrieval skills |
| **NIST AI RMF** | MAP 3.5, MANAGE 3.2 |
| **ISO 42001** | A.10 (Third-Party Relationships) |
| **Control Description** | Data source validation within search skills (Partial); output sanitization before action execution (Implemented); skills execute in sandboxed context within svc-ai-gateway (Implemented); rate limiting bounds the volume of external data retrieval (Implemented) |
| **Control Status** | **Partial** - no dedicated content inspection or injection detection on retrieved external data before it enters the AI context |
| **Residual Risk** | **Medium** - indirect injection through retrieved content is harder to detect than direct injection; the AI treats fetched content as trusted context |
| **Risk Assessment Cross-Ref** | POLICY_AI_GOVERNANCE.md → AI-R02; POLICY_AI_GOVERNANCE.md → AI-T02, Section 12 |
| **STRIDE Cross-Ref** | THREAT_MODEL_STRIDE.md → T-01 |
| **Attack Tree Cross-Ref** | ATTACK_TREE_AI_PIPELINE.md → Path 1, Nodes 1.2.1-1.2.2 |

---

#### ATC-03: Improper Output Handling

| Attribute | Detail |
|-----------|--------|
| **Description** | AI-generated outputs are passed directly to downstream systems (svc-automation workflows, Telegram message responses, database operations) without adequate validation. A hallucinated or injected output could contain malicious payloads (SQL injection, command injection, XSS) that are executed by the consuming system. |
| **OWASP LLM** | LLM10 (Improper Output Handling) |
| **MITRE ATLAS** | AML.T0015 (Evade ML Model) |
| **Affected Systems** | AI-001 (svc-ai-gateway), AI-002 (svc-llm) - outputs consumed by svc-automation |
| **NIST AI RMF** | MEASURE 2.6, MANAGE 2.4 |
| **ISO 42001** | A.9 (Use of AI Systems) |
| **Control Description** | Output sanitization layer in svc-automation before action execution (Implemented); parameterized queries for database operations - AI output never used as raw SQL (Implemented); human approval gates for destructive workflow actions (Implemented); svc-automation input validation on workflow trigger payloads (Implemented) |
| **Control Status** | **Implemented** |
| **Residual Risk** | **Medium** - sanitization handles known output patterns; novel output formats or encoding bypasses may evade validation |
| **Risk Assessment Cross-Ref** | RISK_ASSESSMENT.md → R-04 (Webhook Exploitation); POLICY_AI_GOVERNANCE.md → Section 8 (Human Oversight) |
| **STRIDE Cross-Ref** | THREAT_MODEL_STRIDE.md → T-01 (Tampering), E-02 (Elevation of Privilege) |
| **Attack Tree Cross-Ref** | ATTACK_TREE_AI_PIPELINE.md → Path 1, Node 1.1.3 |

---

#### ATC-04: Model Supply Chain Compromise

| Attribute | Detail |
|-----------|--------|
| **Description** | Upstream AI model weights, container images, or runtime dependencies are tampered with to introduce backdoors, altered behavior, or malicious code. Three distinct supply chains exist: (1) Anthropic API for AI-001, (2) Ollama model registry for AI-002, (3) Whisper open-weight distribution for AI-003. Each has different risk profiles and verification capabilities. |
| **OWASP LLM** | LLM04 (Supply Chain), LLM05 (Data and Model Poisoning) |
| **OWASP Agentic** | ASI04 (Agentic Supply Chain) |
| **MITRE ATLAS** | AML.T0010 (ML Supply Chain Compromise), AML.T0018 (Backdoor ML Model), AML.T0020 (Poison Training Data) |
| **Affected Systems** | AI-001, AI-002, AI-003 |
| **NIST AI RMF** | GOVERN 2.2, MANAGE 1.1 |
| **ISO 42001** | A.10 (Third-Party Relationships), A.6 (AI System Lifecycle) |
| **Control Description** | Trivy CVE scanning of all AI container images in CI/CD (Implemented); Cosign container image signing and verification (Implemented); SBOM generation for container dependencies (Implemented); Semgrep SAST scanning (Implemented); no automatic model updates - manual pull required (Implemented); model weight checksum verification against published hashes (Partial - manual process); Anthropic vendor risk assessment reviewed annually (Implemented) |
| **Control Status** | **Partial** - automated model behavioral regression testing and automated integrity verification pipeline not deployed |
| **Residual Risk** | **Medium** - CI/CD pipeline catches known vulnerabilities, but novel supply chain attacks or backdoored models that pass scanning are not detectable without behavioral testing |
| **Risk Assessment Cross-Ref** | RISK_ASSESSMENT.md → R-03 (Supply Chain); POLICY_AI_GOVERNANCE.md → AI-R03, AI-R08; POLICY_AI_GOVERNANCE.md → AI-T06, Section 11 |
| **STRIDE Cross-Ref** | THREAT_MODEL_STRIDE.md → T-02 (Tampering), T-05 |
| **Attack Tree Cross-Ref** | ATTACK_TREE_AI_PIPELINE.md → Path 2, all nodes |

---

#### ATC-05: Sensitive Information Disclosure

| Attribute | Detail |
|-----------|--------|
| **Description** | The AI system discloses sensitive information through multiple vectors: (1) PII transmitted in prompts to the external Anthropic API, (2) system prompt contents revealed to users via extraction techniques, (3) operational context (service names, architecture details, credential references) leaked in AI responses, (4) training data memorization reproduced in outputs. |
| **OWASP LLM** | LLM02 (Sensitive Information Disclosure) |
| **MITRE ATLAS** | AML.T0024 (Exfiltration via ML Inference API) |
| **Affected Systems** | AI-001 (svc-ai-gateway) - primary risk due to external API data flow |
| **NIST AI RMF** | MAP 1.5, GOVERN 1.1 |
| **ISO 42001** | A.8 (Information for Interested Parties) |
| **Control Description** | Policy prohibiting credential and secret injection into AI prompts (Implemented); system prompt stored server-side with extraction resistance instructions (Implemented); PII-aware logging that redacts sensitive fields (Partial); Anthropic data processing agreement with retention terms reviewed (Implemented); chat ID allowlist restricts who can receive AI responses (Implemented); prompt sanitization rules for known sensitive patterns (Implemented) |
| **Control Status** | **Partial** - automated PII detection and scrubbing of prompts before external API transmission not deployed; relies on policy and manual sanitization rules |
| **Residual Risk** | **Medium** - known sensitive patterns are caught, but novel PII exposure paths through user-provided content may bypass static rules |
| **Risk Assessment Cross-Ref** | POLICY_AI_GOVERNANCE.md → AI-R04; POLICY_AI_GOVERNANCE.md → AI-T07, AI-T10, Section 9 |
| **STRIDE Cross-Ref** | THREAT_MODEL_STRIDE.md → I-01, I-03 (Information Disclosure) |
| **Attack Tree Cross-Ref** | ATTACK_TREE_AI_PIPELINE.md → Path 1, Nodes 1.3.1-1.3.2; Path 3 |

---

#### ATC-06: Insecure Skill/Plugin Execution

| Attribute | Detail |
|-----------|--------|
| **Description** | The AI agent (AI-001) has access to skills that interact with external services (Tavily search, browser, GitHub, Notion, Gemini). Insecure skill design could allow: (1) SSRF through the browser skill, (2) credential leakage through skill parameters, (3) excessive permission scope granting skills more access than needed, (4) skill output injection into the AI context. |
| **OWASP LLM** | LLM03 (Excessive Agency) - skill execution authority is the 2025 and 2026 framing for what 2023 called "Insecure Plugin Design" |
| **OWASP Agentic** | ASI02 (Tool Misuse and Exploitation) |
| **MITRE ATLAS** | AML.T0040 (ML-Enabled Lateral Movement) |
| **Affected Systems** | AI-001 (svc-ai-gateway) - skill execution context |
| **NIST AI RMF** | MANAGE 2.1, GOVERN 2.2 |
| **ISO 42001** | A.10 (Third-Party Relationships) |
| **Control Description** | Skills execute within svc-ai-gateway container sandbox (Implemented); skill permissions scoped to specific API capabilities (Implemented); skill outputs treated as untrusted input to the AI context (Implemented); rate limiting on skill invocations (Implemented); Falco monitoring of unexpected network connections from svc-ai-gateway (Implemented) |
| **Control Status** | **Implemented** |
| **Residual Risk** | **Low** - skills are bounded within the container sandbox; network egress is monitored; permission scoping limits blast radius |
| **Risk Assessment Cross-Ref** | RISK_ASSESSMENT.md → R-04; POLICY_AI_GOVERNANCE.md → Section 12 |
| **STRIDE Cross-Ref** | THREAT_MODEL_STRIDE.md → E-04 (Elevation of Privilege) |
| **Attack Tree Cross-Ref** | ATTACK_TREE_AI_PIPELINE.md → Path 4 |

---

#### ATC-07: Excessive Autonomous Agency

| Attribute | Detail |
|-----------|--------|
| **Description** | The AI agent, through its integration with svc-automation, has access to 16+ service integrations (PostgreSQL, Telegram, GitHub, Google Drive, Google Sheets, Cloudflare, Notion, Gmail, and others). If the AI misinterprets a user request, hallucinates an action plan, or is manipulated via prompt injection, it could execute a chain of consequential actions without adequate human review - including data modifications, message sending, or infrastructure changes. |
| **OWASP LLM** | LLM03 (Excessive Agency) |
| **OWASP Agentic** | ASI02 (Tool Misuse and Exploitation), ASI03 (Identity and Privilege Abuse) |
| **MITRE ATLAS** | - (organizational risk rather than adversarial ML technique) |
| **Affected Systems** | AI-001 (svc-ai-gateway) → svc-automation → all integrated downstream services |
| **NIST AI RMF** | GOVERN 1.2, MANAGE 2.4 |
| **ISO 42001** | A.9 (Use of AI Systems) |
| **Control Description** | Human approval gates in svc-automation for destructive/irreversible actions (Implemented); action allowlist restricting which workflow endpoints the AI can trigger (Implemented); no AI access to credential rotation, container lifecycle, or infrastructure-modifying operations (Implemented); audit logging of all AI-initiated actions with full prompt/response trail (Implemented); rate limiting bounds the volume of actions per time window (Implemented) |
| **Control Status** | **Implemented** |
| **Residual Risk** | **Medium** - destructive actions are gated, but the breadth of permitted non-destructive actions (database reads, messaging, API calls, document creation) represents a meaningful surface; accumulated non-destructive actions could still cause operational impact |
| **Risk Assessment Cross-Ref** | POLICY_AI_GOVERNANCE.md → AI-R05; POLICY_AI_GOVERNANCE.md → AI-T09, Section 8 |
| **STRIDE Cross-Ref** | THREAT_MODEL_STRIDE.md → E-02 (Elevation of Privilege) |
| **Attack Tree Cross-Ref** | ATTACK_TREE_AI_PIPELINE.md → Path 1, Node 1.1.3 |

---

#### ATC-08: Misinformation and Overreliance on AI Outputs

| Attribute | Detail |
|-----------|--------|
| **Description** | The model produces inaccurate or fabricated information (hallucinations, invented citations, mistaken classifications) and the operator develops excessive trust in those outputs, reducing manual verification and critical review. This is particularly dangerous for: (1) AI-002 outputs, which have a higher hallucination rate due to the smaller model, (2) AI-001 outputs for security-related decisions (vulnerability assessment, compliance checks, configuration recommendations), and (3) routine tasks where fatigue may reduce review diligence. OWASP renamed the 2023 "Overreliance" category to "Misinformation" in 2025 to put the focus on the model behavior. |
| **OWASP LLM** | LLM07 (Misinformation) |
| **OWASP Agentic** | ASI09 (Human-Agent Trust Exploitation) |
| **MITRE ATLAS** | - (human factor, not adversarial ML) |
| **Affected Systems** | AI-001 (svc-ai-gateway), AI-002 (svc-llm) |
| **NIST AI RMF** | MAP 2.1, MAP 2.3, MEASURE 2.1 |
| **ISO 42001** | A.8 (Information for Interested Parties), A.9 (Use of AI Systems) |
| **Control Description** | AI outputs flagged with uncertainty disclaimers where model confidence is low (Partial); AI Governance Policy (POL-AI-001) documents known limitations for each AI system (Implemented); svc-automation workflows include validation checkpoints before consequential actions (Implemented); AI-002 restricted to non-critical tasks (classification, summarization) where hallucination impact is bounded (Implemented) |
| **Control Status** | **Partial** - no automated output confidence scoring or mandatory verification workflow for high-stakes AI outputs |
| **Residual Risk** | **Medium** - single-operator environment means no second pair of eyes; procedural controls depend on operator discipline |
| **Risk Assessment Cross-Ref** | POLICY_AI_GOVERNANCE.md → AI-R01, AI-R06; POLICY_AI_GOVERNANCE.md → AI-T01, Section 8.2 |
| **STRIDE Cross-Ref** | THREAT_MODEL_STRIDE.md → R-01 (Repudiation - unattributed AI actions) |
| **Attack Tree Cross-Ref** | ATTACK_TREE_AI_PIPELINE.md → N/A (human factor, not attack path) |

---

#### ATC-09: Unbounded Resource Consumption

| Attribute | Detail |
|-----------|--------|
| **Description** | AI systems consume excessive compute, memory, API budget, or storage through: (1) adversarial input designed to maximize token consumption on AI-001, (2) resource-intensive inference on AI-002 (svc-llm) that starves co-resident services on the single VPS, (3) large audio files submitted to AI-003 (svc-transcription) consuming CPU cycles. All three AI systems share the same 4 vCPU / 8 GB RAM host. |
| **OWASP LLM** | LLM06 (Unbounded Consumption) |
| **MITRE ATLAS** | AML.T0029 (Denial of ML Service) |
| **Affected Systems** | AI-001, AI-002, AI-003 |
| **NIST AI RMF** | MANAGE 3.2 |
| **ISO 42001** | A.4 (Resources for AI Systems) |
| **Control Description** | Rate limiting at svc-ai-gateway (Implemented); Anthropic API budget caps (Implemented); chat ID allowlist restricts external access (Implemented); Docker container resource limits - CPU shares and memory caps (Partial - not uniformly enforced); Datadog resource monitoring with alerting on CPU/memory thresholds (Implemented); container restart policies prevent permanent resource lockup (Implemented) |
| **Control Status** | **Implemented** |
| **Residual Risk** | **Low** - access restrictions and rate limiting effectively bound consumption; resource monitoring provides early warning |
| **Risk Assessment Cross-Ref** | POLICY_AI_GOVERNANCE.md → AI-R09; POLICY_AI_GOVERNANCE.md → AI-T08, Section 12 |
| **STRIDE Cross-Ref** | THREAT_MODEL_STRIDE.md → D-02 (Denial of Service), D-03 |
| **Attack Tree Cross-Ref** | ATTACK_TREE_AI_PIPELINE.md → N/A (covered as DoS branch in all paths) |

---

#### ATC-10: AI-Enabled Lateral Movement

| Attribute | Detail |
|-----------|--------|
| **Description** | An attacker who has compromised an AI container uses its network position and credentials to pivot to other services within the architecture. AI containers are uniquely positioned for lateral movement because: (1) svc-ai-gateway (DMZ) has connectivity to svc-automation and may reach svc-db via net-core, (2) svc-llm (Internal) is on net-ai but may also have net-core access for workflow integration, (3) AI containers may contain environment variables with database credentials or API tokens. |
| **OWASP LLM** | - (infrastructure-level threat, not LLM-specific) |
| **MITRE ATLAS** | AML.T0040 (ML-Enabled Lateral Movement) |
| **Affected Systems** | AI-001 (svc-ai-gateway), AI-002 (svc-llm) |
| **NIST AI RMF** | MANAGE 3.2, MEASURE 2.6 |
| **ISO 42001** | A.6 (AI System Lifecycle) |
| **Control Description** | Docker network segmentation: net-core, net-ai, net-monitoring (Implemented); svc-llm has no internet egress via net-ai configuration (Implemented); svc-secrets requires token-based authentication (Implemented); no-new-privileges on AI containers (Implemented); Falco eBPF detection of unexpected network connections and shell spawns (Implemented); Docker socket NOT mounted in any container (Implemented) |
| **Control Status** | **Implemented** |
| **Residual Risk** | **Medium** - network segmentation provides meaningful isolation, but net-core connectivity is broader than ideal; a compromised container on net-core with harvested credentials could authenticate to co-resident services |
| **Risk Assessment Cross-Ref** | RISK_ASSESSMENT.md → R-08 (Privilege Escalation); POLICY_AI_GOVERNANCE.md → Section 12 |
| **STRIDE Cross-Ref** | THREAT_MODEL_STRIDE.md → E-04 (Elevation of Privilege) |
| **Attack Tree Cross-Ref** | ATTACK_TREE_AI_PIPELINE.md → Path 4, all nodes |

---

## 4. Detection Capabilities

### 4.1 Detection Matrix

The following matrix documents which monitoring and detection systems can identify each AI threat, and the confidence level of detection.

| Threat ID | Falco (eBPF) | Datadog Monitoring | svc-automation Logs | AI Gateway Logs | CI/CD Pipeline | Manual Review |
|-----------|:------------:|:-----------------:|:------------------:|:---------------:|:--------------:|:-------------:|
| ATC-01 (Direct Injection) | Low | Low | Medium | **High** | - | High |
| ATC-02 (Indirect Injection) | Low | Low | Medium | Medium | - | Low |
| ATC-03 (Insecure Output) | Medium | Low | **High** | Medium | - | Medium |
| ATC-04 (Supply Chain) | - | - | - | - | **High** | Medium |
| ATC-05 (Info Disclosure) | Low | Medium | Medium | **High** | - | Medium |
| ATC-06 (Insecure Skills) | **High** | Medium | Medium | Medium | - | Low |
| ATC-07 (Excessive Agency) | Medium | Medium | **High** | High | - | High |
| ATC-08 (Overreliance) | - | - | Low | Low | - | **High** |
| ATC-09 (Resource Exhaustion) | Medium | **High** | Medium | Medium | - | Low |
| ATC-10 (Lateral Movement) | **High** | Medium | - | Low | - | Low |

### 4.2 Detection Descriptions

| Threat ID | Primary Detection Method | Detection Description | Alert Latency |
|-----------|-------------------------|----------------------|---------------|
| ATC-01 | AI Gateway prompt/response logging | Full prompt and response pairs shipped to monitoring; manual or automated review for injection patterns | Near real-time (log shipping) |
| ATC-02 | AI Gateway logs + svc-automation execution logs | Correlation between external data retrieval and subsequent unexpected actions; requires log analysis | Hours (correlation-dependent) |
| ATC-03 | svc-automation workflow execution logs | Workflow execution history captures AI-provided inputs and validates outputs before action; deviations flagged | Near real-time |
| ATC-04 | CI/CD pipeline (Trivy, Cosign, SBOM) | Image scanning, signature verification, and dependency analysis at build time; no runtime model behavioral testing | Build-time (pre-deployment) |
| ATC-05 | AI Gateway logs + Datadog log analysis | Prompt content reviewed for PII patterns; response content scanned for sensitive data leakage | Near real-time (monitoring) |
| ATC-06 | Falco eBPF network monitoring | Unexpected outbound connections from svc-ai-gateway to unauthorized destinations trigger Falco alerts | Real-time |
| ATC-07 | svc-automation audit trail | All AI-initiated workflow executions logged with action type, target service, and approval status | Near real-time |
| ATC-08 | Manual review process | Periodic review of AI output quality and operator verification patterns; no automated detection | Scheduled (quarterly) |
| ATC-09 | Datadog resource monitoring | CPU, memory, API spend dashboards with threshold alerting | Real-time (alerting within 60s) |
| ATC-10 | Falco eBPF runtime detection | Shell spawns in application containers, unexpected network connections, /proc access attempts | Real-time |

### 4.3 Detection Gaps

| Gap ID | Description | Affected Threats | Planned Remediation | Target Date |
|--------|-------------|-----------------|--------------------|-----------:|
| DG-01 | No automated prompt injection classifier at AI gateway | ATC-01, ATC-02 | Deploy prompt firewall with input/output classification | 2026-06-12 |
| DG-02 | No runtime model behavioral regression testing | ATC-04 | Implement behavioral test suite against curated baselines | 2026-09-12 |
| DG-03 | No automated PII detection on outbound prompts | ATC-05 | Deploy PII scanner (regex + NER) at svc-ai-gateway | 2026-06-12 |
| DG-04 | No automated confidence scoring on AI outputs | ATC-08 | Implement output confidence scoring with threshold alerts | 2026-09-12 |
| DG-05 | Log scrubbing for secret patterns not deployed at svc-log-router | ATC-05 | Configure Fluentd regex-based secret scrubbing rules | 2026-06-12 |

---

## 5. Control Posture Summary

### 5.1 Control Status by Threat

| Status | Count | Threats | Percentage |
|--------|-------|---------|------------|
| **Implemented** | 5 | ATC-01, ATC-03, ATC-06, ATC-09, ATC-10 | 50% |
| **Partial** | 4 | ATC-02, ATC-04, ATC-05, ATC-08 | 40% |
| **Planned** | 1 | - (no threat has zero controls) | - |
| **Not Applicable** | 0 | - | - |

*Note: 50% Implemented means primary controls are in place and functional. The 40% Partial status indicates that foundational controls exist but one or more planned enhancements (typically automated detection or validation) are not yet deployed.*

### 5.2 Residual Risk Distribution

| Residual Risk | Count | Threats |
|---------------|-------|---------|
| **High** | 0 | - |
| **Medium** | 8 | ATC-01, ATC-02, ATC-03, ATC-04, ATC-05, ATC-07, ATC-08, ATC-10 |
| **Low** | 2 | ATC-06, ATC-09 |

### 5.3 Prioritized Remediation Actions

| Priority | Threat | Gap | Action | NIST AI RMF Function | Target Date | Owner |
|----------|--------|-----|--------|---------------------|-------------|-------|
| 1 | ATC-05 | DG-03, DG-05 | Deploy PII scanner and log scrubbing rules | MANAGE 1.1 | 2026-06-12 | Information Security Officer |
| 2 | ATC-01, ATC-02 | DG-01 | Implement prompt firewall at svc-ai-gateway | MANAGE 3.2 | 2026-06-12 | Information Security Officer |
| 3 | ATC-04 | DG-02 | Automate model integrity verification with behavioral baselines | MEASURE 2.1 | 2026-09-12 | Information Security Officer |
| 4 | ATC-07 | - | Implement tiered action authorization with per-session budgets | GOVERN 1.2 | 2026-09-12 | Information Security Officer |
| 5 | ATC-08 | DG-04 | Deploy automated output confidence scoring and verification triggers | MEASURE 2.6 | 2026-09-12 | Information Security Officer |

---

## 6. Cross-Reference Index

### 6.1 Mapping to Existing GRC Documents

| Catalog ID | RISK_ASSESSMENT.md | POLICY_AI_GOVERNANCE.md | SSP_SYSTEM_SECURITY_PLAN.md | THREAT_MODEL_STRIDE.md | ATTACK_TREE_AI_PIPELINE.md |
|------------|-------------------|------------------------|----------------------------|----------------------|---------------------------|
| ATC-01 | AI-R02 | AI-T02, Sec. 6.3, 12 | SI-10, SA-15 | T-01 | Path 1, 1.1.x |
| ATC-02 | AI-R02 | AI-T02, Sec. 12 | SI-10, SA-15 | T-01 | Path 1, 1.2.x |
| ATC-03 | R-04, AI-R02 | AI-T02, Sec. 8 | SI-10, SI-4 | T-01, E-02 | Path 1, 1.1.3 |
| ATC-04 | R-03, AI-R03, AI-R08 | AI-T06, Sec. 11 | SA-12, SI-7, SA-22 | T-02, T-05 | Path 2, all |
| ATC-05 | AI-R04 | AI-T07, AI-T10, Sec. 9 | SC-28, SI-12, PM-25 | I-01, I-03 | Path 1 (1.3.x), Path 3 |
| ATC-06 | R-04 | Sec. 12 | SC-7, AC-4 | E-04 | Path 4 |
| ATC-07 | AI-R05 | AI-T09, Sec. 8 | AC-6, CM-7, SI-10 | E-02 | Path 1, 1.1.3 |
| ATC-08 | AI-R01, AI-R06 | AI-T01, Sec. 8.2 | - | R-01 | N/A |
| ATC-09 | AI-R09 | AI-T08, Sec. 12 | SC-5, SC-6 | D-02, D-03 | N/A |
| ATC-10 | R-08 | Sec. 12 | SC-7, AC-4, SI-4 | E-04 | Path 4, all |

### 6.2 Incident Response Mapping

| Catalog ID | Primary IR Playbook | Escalation Threshold |
|------------|--------------------|--------------------|
| ATC-01, ATC-02 | **PLAYBOOK_AI_INCIDENT.md** Scenario A | Successful injection that triggers unauthorized workflow execution |
| ATC-03 | **PLAYBOOK_AI_INCIDENT.md** Scenario A/B + PLAYBOOK_COMPROMISED_CONTAINER.md | AI output results in unintended infrastructure or data modification |
| ATC-04 | **PLAYBOOK_AI_INCIDENT.md** Scenario D | CVE detected in AI container image; model integrity verification failure |
| ATC-05 | **PLAYBOOK_AI_INCIDENT.md** Scenario C + PLAYBOOK_LEAKED_CREDENTIAL.md | PII or credentials confirmed transmitted to external API |
| ATC-06 | **PLAYBOOK_AI_INCIDENT.md** Scenario A + PLAYBOOK_UNAUTHORIZED_ACCESS.md | Skill execution results in unauthorized access to external service |
| ATC-07 | **PLAYBOOK_AI_INCIDENT.md** Scenario B | AI executes action chain exceeding authorized scope |
| ATC-08 | N/A (procedural, not incident) | Identified during quarterly review |
| ATC-09 | PLAYBOOK_DDOS_SERVICE_DEGRADATION.md | Resource exhaustion impacting service availability |
| ATC-10 | **PLAYBOOK_AI_INCIDENT.md** Scenario B + PLAYBOOK_COMPROMISED_CONTAINER.md | Unexpected network connection from AI container to sensitive zone |

---

## 7. Review Schedule and Ownership

| Activity | Frequency | Next Date | Owner |
|----------|-----------|-----------|-------|
| Full catalog review | Semi-annual | 2026-09-12 | Information Security Officer |
| Detection gap reassessment | Quarterly | 2026-06-12 | Information Security Officer |
| OWASP LLM Top 10 alignment check | Annual (or upon new release) | 2027-03-12 | Information Security Officer |
| MITRE ATLAS technique update | Semi-annual | 2026-09-12 | Information Security Officer |
| Remediation progress review | Quarterly | 2026-06-12 | System Owner |
| New AI system threat assessment | Per deployment (mandatory) | As needed | Information Security Officer |

---

## 7.5 Phase 17 Mitigation Addendum

> **Key Point:** Phase 17 shipped 9 defense-in-depth layers and 10 new GRC docs (`SQUIRE_SSP`, `GUARDRAILS_CONFIGURATION`, `REDTEAM_RESULTS`, etc.). The table below adds a Phase 17 mitigation column to each of the 10 threats in this catalog. The 6 red-team cases executed 2026-04-23 validate 4 of these controls.

### 7.5.1 Phase 17 controls applied per threat

| Catalog ID | Threat | Pre-Phase 17 mitigation | Phase 17 control(s) added | Verification |
|------------|--------|-------------------------|---------------------------|--------------|
| AI-T01 | Prompt Injection (direct) | Input filter, prompt hardening | Pre-graph PII scanner, NeMo input rail, graph classifier held through adversarial framing | REDTEAM_RESULTS Findings 1, 2, 5, 6 (RESISTED) |
| AI-T02 | Prompt Injection (indirect via retrieval) | None | Citation validator, ir_chunks source allow-list | Scheduled red-team cycle 2 |
| AI-T03 | Sensitive Information Disclosure (training data, prompts) | Out-of-scope (no fine-tune) | Pre-graph PII scanner (SSN, Luhn CC, email, phone), NeMo output rail with presidio, SQUIRE_DATA_FLOW_CLASSIFICATION retention rules | REDTEAM_RESULTS Finding 3 (CLOSED post-remediation) |
| AI-T04 | Model Theft | API key rotation, no model hosting locally | No additional Phase 17 control; covered by vendor posture | AI_SUPPLY_CHAIN_REGISTER |
| AI-T05 | Supply Chain Vulnerabilities | SBOM, container signing | 14-component living register (AI_SUPPLY_CHAIN_REGISTER) with version plus hash plus review cadence | 60-day register review |
| AI-T06 | Insecure Output Handling | Output sanitization | NeMo output rail, critique node, action allow-list, HITL gate on HIGH/CRITICAL | GUARDRAILS_CONFIGURATION rail coverage |
| AI-T07 | Excessive Agency | Human approval on destructive ops | Actions allow-list (typed schema, deny-by-default), HITL policy for HIGH/CRITICAL severity, 60-day token rotation | HITL_POLICY sections 2-6 |
| AI-T08 | Overreliance (hallucinated output) | Human review spot-check | Critique node gates draft, citation validator requires source match, Ollama fallback when Fable unavailable | SQUIRE_MODEL_CARD limitations |
| AI-T09 | Model Denial of Service | Rate limit | Cost ceiling (hard stop at per-alert budget), Cloudflare rate limit, Redis dedup | SQUIRE_SSP SC-5 |
| AI-T10 | Sensitive Info Disclosure (logs or traces) | Log hygiene | SDK redaction, Langfuse classification policy, per-class retention in SQUIRE_DATA_FLOW_CLASSIFICATION | AI_AUDIT_TRAIL_SPEC |

### 7.5.2 Defense-in-depth layers introduced

```
 1. WAF                            Cloudflare
 2. Rate limit                     Cloudflare plus Redis dedup
 3. X-Squire-Token auth            HMAC ephemeral, 60-day rotation
 4. Cost ceiling                   Hard stop per alert
 5. Actions allow-list             Deny-by-default typed schema
 6. Pre-graph PII scanner          Regex block before LLM call (0ms, $0)
 7. NeMo input rails               Colang plus presidio
 8. HITL review                    HIGH/CRITICAL gate
 9. Audit trail                    Langfuse plus pgvector ir_investigations
```

### 7.5.3 Cross-reference

See `GUARDRAILS_CONFIGURATION.md` for rail-by-rail test coverage. See `REDTEAM_RESULTS.md` for 6 executed red-team cases. See `SQUIRE_AI_RISK_ASSESSMENT.md` for the 10 Squire-specific AI risks (distinct from this pre-Phase 17 catalog). See `POAM_PLAN_OF_ACTION.md` POAM-P17-01 through P17-10 for tracked remediations.

---

## 8. Related Documents

| Document | Relationship |
|----------|-------------|
| [THREAT_MODEL_STRIDE.md](THREAT_MODEL_STRIDE.md) | STRIDE decomposition mapping to this catalog's threats |
| [ATTACK_TREE_AI_PIPELINE.md](ATTACK_TREE_AI_PIPELINE.md) | Attack path decomposition for AI pipeline compromise |
| [POLICY_AI_GOVERNANCE.md](POLICY_AI_GOVERNANCE.md) | AI risk register (AI-R01 through AI-R10)) |
| [POLICY_AI_GOVERNANCE.md](POLICY_AI_GOVERNANCE.md) | AI governance framework, risk tolerance, lifecycle management |
| [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) | NIST 800-53 control implementations |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | Remediation tracking for identified gaps |
| [PLAYBOOK_AI_INCIDENT.md](PLAYBOOK_AI_INCIDENT.md) | **AI-specific IR playbook** - prompt injection, excessive agency, data exfiltration, model supply chain |
| [PLAYBOOK_COMPROMISED_CONTAINER.md](PLAYBOOK_COMPROMISED_CONTAINER.md) | Container compromise response procedures |
| [PLAYBOOK_LEAKED_CREDENTIAL.md](PLAYBOOK_LEAKED_CREDENTIAL.md) | Credential exposure response procedures |
| [PLAYBOOK_UNAUTHORIZED_ACCESS.md](PLAYBOOK_UNAUTHORIZED_ACCESS.md) | Unauthorized access investigation procedures |
| [PLAYBOOK_DDOS_SERVICE_DEGRADATION.md](PLAYBOOK_DDOS_SERVICE_DEGRADATION.md) | DoS/DDoS response procedures |

---

*This AI threat catalog is a living document. It SHALL be updated when new AI systems are deployed, existing systems are reconfigured, new OWASP LLM or MITRE ATLAS releases are published, or after any AI-related security incident. The next scheduled review is 2026-09-12.*
