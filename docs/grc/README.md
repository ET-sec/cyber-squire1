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
| Tabletop exercise | Semi-annual | TBD |

## Statistics

- **24 documents** in this library
- **~9,300 lines** of compliance documentation
- **170+ NIST 800-53 controls** mapped across 16 families
- **3 AI governance frameworks** mapped (ISO 42001, ISO 27701, NIST AI RMF)
- **22 POA&M entries** tracked (15 accepted, 6 open, 1 closed)
- **17 risk scenarios** assessed with MITRE ATT&CK mapping
- **4 IR playbooks** with step-by-step containment procedures
- **1 tabletop exercise** with 5-phase scenario and evaluation criteria
