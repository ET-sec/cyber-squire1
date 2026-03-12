# GRC Documentation Library

Governance, Risk, and Compliance documentation for the Organization Security Operations Platform.

All documents are sanitized for public repository safety. No real IPs, domains, service names, or credentials appear in any file. See `SANITIZATION_KEY.md` (gitignored, local only) for the reverse mapping.

## Framework Alignment

- **NIST SP 800-53 Rev. 5** — Moderate baseline, 16 control families
- **NIST SP 800-30 Rev. 1** — Risk assessment methodology
- **NIST SP 800-39** — Risk management framework
- **NIST AI RMF (AI 100-1)** — AI risk management framework
- **ISO/IEC 42001:2023** — AI management system
- **ISO/IEC 27701:2019** — Privacy information management
- **OWASP LLM Top 10 (2025)** — LLM-specific threat taxonomy
- **MITRE ATLAS v4** — Adversarial ML threat framework
- **NIST SP 800-154** — Data-centric threat modeling
- **FIPS 199** — Security categorization (Moderate)
- **CIS Docker Benchmark** — Container hardening benchmark

## Document Index

### Executive Summaries

| Document | Description |
|----------|-------------|
| [EXECUTIVE_SUMMARY_SECURITY_POSTURE.md](EXECUTIVE_SUMMARY_SECURITY_POSTURE.md) | Security posture one-pager — controls, findings, defense-in-depth |
| [EXECUTIVE_SUMMARY_ARCHITECTURE.md](EXECUTIVE_SUMMARY_ARCHITECTURE.md) | Architecture one-pager — trust zones, service inventory, IaC |
| [EXECUTIVE_SUMMARY_COMPLIANCE.md](EXECUTIVE_SUMMARY_COMPLIANCE.md) | Compliance readiness one-pager — framework coverage, evidence, review cadence |

### Core Plans

| Document | Description |
|----------|-------------|
| [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) | System Security Plan — NIST 800-53 control mapping (16 families, 170+ controls) |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | Plan of Action & Milestones — 22 entries from CIS/IaC scanner/runtime detection |
| [RISK_ASSESSMENT.md](RISK_ASSESSMENT.md) | Risk Assessment — 17 threats, 5x5 matrix, MITRE ATT&CK mapping |

### Policies

| Document | Framework Controls |
|----------|-------------------|
| [POLICY_RISK_MANAGEMENT.md](POLICY_RISK_MANAGEMENT.md) | RA-1/2/3, PM-9 |
| [POLICY_ACCESS_CONTROL.md](POLICY_ACCESS_CONTROL.md) | AC-1 through AC-12 |
| [POLICY_CHANGE_MANAGEMENT.md](POLICY_CHANGE_MANAGEMENT.md) | CM-1 through CM-8 |
| [POLICY_VULNERABILITY_MANAGEMENT.md](POLICY_VULNERABILITY_MANAGEMENT.md) | RA-5, SI-2, SI-5 |
| [POLICY_INCIDENT_RESPONSE.md](POLICY_INCIDENT_RESPONSE.md) | IR-1 through IR-8 |
| [POLICY_BUSINESS_CONTINUITY.md](POLICY_BUSINESS_CONTINUITY.md) | CP-1 through CP-10 |
| [POLICY_DISASTER_RECOVERY.md](POLICY_DISASTER_RECOVERY.md) | CP-2/4/6/7/9/10 |
| [POLICY_ACCEPTABLE_USE.md](POLICY_ACCEPTABLE_USE.md) | PL-4, AT-2 |
| [POLICY_SECURITY_AWARENESS.md](POLICY_SECURITY_AWARENESS.md) | AT-1 through AT-4 |
| [POLICY_AI_GOVERNANCE.md](POLICY_AI_GOVERNANCE.md) | ISO 42001, ISO 27701, NIST AI RMF |

### IAM

| Document | Description |
|----------|-------------|
| [IAM_RBAC_ROLE_MAP.md](IAM_RBAC_ROLE_MAP.md) | 3-tier RBAC role map (admin/operator/auditor) |
| [IAM_ACCESS_REVIEW.md](IAM_ACCESS_REVIEW.md) | Access review process with JIT workflow |

### Threat Modeling

| Document | Description |
|----------|-------------|
| [DATA_FLOW_DIAGRAM.md](DATA_FLOW_DIAGRAM.md) | DFD Levels 0–2 — 30 data flows, 9 data stores, 11 external entities, 7 trust boundaries |
| [THREAT_MODEL_STRIDE.md](THREAT_MODEL_STRIDE.md) | STRIDE analysis — 29 threats across 6 categories with AI extensions, mapped to NIST 800-53 |
| [ATTACK_TREE_AI_PIPELINE.md](ATTACK_TREE_AI_PIPELINE.md) | Attack tree — 4 paths to compromise AI inference pipeline, MITRE ATLAS / OWASP LLM mapping |
| [AI_THREAT_CATALOG.md](AI_THREAT_CATALOG.md) | AI threat catalog — 10 threats mapped to OWASP LLM Top 10, MITRE ATLAS, NIST AI RMF, ISO 42001 |
| [AI_SUPPLY_CHAIN_RISK.md](AI_SUPPLY_CHAIN_RISK.md) | AI supply chain risk assessment — model provenance, ML-BOM, integrity verification, vendor risk for 3 AI systems |
| [AI_RED_TEAM_PLAN.md](AI_RED_TEAM_PLAN.md) | AI adversarial testing plan — 25 test cases across 6 categories, OWASP LLM / MITRE ATLAS mapped, quarterly cadence |

### Risk Register

| Document | Description |
|----------|-------------|
| [CIS_RISK_REGISTER.md](CIS_RISK_REGISTER.md) | CIS Docker Bench findings with compensating controls |

### Incident Response Playbooks

| Document | Scenario |
|----------|----------|
| [PLAYBOOK_COMPROMISED_CONTAINER.md](PLAYBOOK_COMPROMISED_CONTAINER.md) | Container compromise detection and containment |
| [PLAYBOOK_LEAKED_CREDENTIAL.md](PLAYBOOK_LEAKED_CREDENTIAL.md) | Credential exposure response and rotation |
| [PLAYBOOK_DDOS_SERVICE_DEGRADATION.md](PLAYBOOK_DDOS_SERVICE_DEGRADATION.md) | DDoS/service degradation mitigation |
| [PLAYBOOK_UNAUTHORIZED_ACCESS.md](PLAYBOOK_UNAUTHORIZED_ACCESS.md) | Unauthorized access investigation |
| [PLAYBOOK_AI_INCIDENT.md](PLAYBOOK_AI_INCIDENT.md) | AI system compromise — prompt injection, excessive agency, data exfiltration, model supply chain |

### Exercises

| Document | Description |
|----------|-------------|
| [TABLETOP_EXERCISE.md](TABLETOP_EXERCISE.md) | Operation Phantom Container — 5-phase TTX scenario |

## Review Schedule

| Activity | Frequency | Next Date |
|----------|-----------|-----------|
| Full SSP review | Semi-annual | 2026-09-11 |
| POA&M status review | Quarterly (90-day cycle) | 2026-06-09 |
| Risk register review | Quarterly | 2026-06-11 |
| CIS Docker Bench rescan | Monthly | 2026-04-11 |
| Policy review | Annual | 2027-03-11 |
| DFD review | Semi-annual | 2026-09-12 |
| Threat model review | Semi-annual | 2026-09-12 |
| AI threat catalog review | Semi-annual | 2026-09-12 |
| AI supply chain risk review | Semi-annual | 2026-09-12 |
| AI adversarial testing | Quarterly | 2026-06-02 |
| Tabletop exercise | Semi-annual | TBD |

## Statistics

- **31 documents** in this library
- **~15,000 lines** of compliance documentation
- **170+ NIST 800-53 controls** mapped across 16 families
- **5 AI/ML frameworks** mapped (ISO 42001, ISO 27701, NIST AI RMF, OWASP LLM Top 10, MITRE ATLAS)
- **30 data flows** mapped across 7 trust boundaries and 3 Docker networks
- **29 STRIDE threats** analyzed with AI-specific extensions
- **10 AI threats** cataloged with cross-framework traceability
- **4 attack paths** decomposed for AI inference pipeline compromise
- **25 adversarial test cases** across 6 categories with quarterly execution cadence
- **15 supply chain risks** assessed across 3 AI systems with ML-BOM and integrity verification procedures
- **22 POA&M entries** tracked (15 accepted, 6 open, 1 closed)
- **17 risk scenarios** assessed with MITRE ATT&CK mapping
- **5 IR playbooks** with step-by-step containment procedures
- **1 tabletop exercise** with 5-phase scenario and evaluation criteria
