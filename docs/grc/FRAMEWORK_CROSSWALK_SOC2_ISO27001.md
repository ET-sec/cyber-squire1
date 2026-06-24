---
document_id: CW-002
title: Framework Crosswalk SOC 2 and ISO 27001
doc_type: crosswalk
classification: CUI-INTERNAL
version: "1.0"
last_updated: 2026-05-25
next_review: 2026-08-25
owner: Information Security Officer
approver: System Owner
frameworks:
  - AICPA TSP Section 100 (2017, revised 2022)
  - ISO/IEC 27001:2022
  - ISO/IEC 27002:2022
  - NIST SP 800-53 Rev 5
related:
  - SSP-OPS-001
  - POL-AI-001
  - POLICY_ACCESS_CONTROL
  - POLICY_BUSINESS_CONTINUITY
  - POLICY_DISASTER_RECOVERY
  - POLICY_INCIDENT_RESPONSE
  - POLICY_VULNERABILITY_MANAGEMENT
  - POLICY_CHANGE_MANAGEMENT
  - CW-SQUIRE-001
---

# Framework Crosswalk: SOC 2 and ISO 27001:2022

## Organization Security Operations Platform (OSOP)

**Document Identifier:** CW-002
**Classification:** CONTROLLED UNCLASSIFIED - INTERNAL USE ONLY
**Version:** 1.0
**Status:** Approved
**Last Updated:** 2026-05-25
**Next Scheduled Review:** 2026-08-25
**Prepared By:** Information Security Officer
**Approved By:** System Owner

---

## Document Control

| Field | Value |
|-------|-------|
| Document Title | Framework Crosswalk: SOC 2 and ISO 27001:2022 |
| Document ID | CW-002 |
| Version | 1.1 |
| Status | Approved |
| Last Revised | 2026-06-24 |
| Next Review | 2026-08-25 |
| Author | Information Security Officer |
| Approver | System Owner |
| Distribution | Compliance program owners, internal audit, prospective service auditors and certification bodies |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-05-25 | Information Security Officer | Initial combined crosswalk covering AICPA Trust Services Criteria (Security, Availability, Confidentiality) and ISO/IEC 27001:2022 clauses 4 through 10 and Annex A controls, both anchored to the NIST SP 800-53 Rev 5 baseline already implemented |
| 1.1 | 2026-06-24 | Information Security Officer | Audit refresh: Section 9.1 SoA totals reconciled with the per-theme breakdown (Implemented direct 48, Inherited 13, Partial 28, Gap 4, sum 93). Section 10.2 ISMS sub-clause count corrected from 18 to 25 to match the body of Section 7 sub-clauses actually mapped. |

---

## 1. Purpose

This crosswalk maps OSOP controls to two compliance frameworks that prospective customers, partners, and auditors most often request: the AICPA Trust Services Criteria for SOC 2 and ISO/IEC 27001:2022. The doc demonstrates that the controls already implemented under the NIST SP 800-53 Rev 5 baseline cover the substantive requirements of both frameworks and shows where formal audit work would still be required to close the gap between self-attested readiness and an external opinion.

### 1.1 Why a Combined Document

SOC 2 and ISO 27001:2022 overlap heavily at the control level. Roughly 70 to 80 percent of the substantive controls overlap once you reduce both to the underlying NIST 800-53 family they implement. Maintaining two separate crosswalk documents would duplicate most of the content and create drift between the two over time. A combined doc keeps the mappings consistent because every control row anchors back to a single NIST 800-53 reference that is implemented in the same code path, container, or policy.

### 1.2 Attestation Versus Certification

SOC 2 and ISO 27001 differ in the legal nature of the output.

- **SOC 2 is an attestation.** A licensed CPA firm acting as a service auditor issues an opinion under AICPA AT-C 105 and AT-C 205 attestation standards. The report is private and consumed by user entities under non-disclosure. A Type I report describes the design of controls at a point in time. A Type II report tests the operating effectiveness of those controls over a period (typically six to twelve months).
- **ISO 27001 is a certification.** An accredited certification body issues a certificate of conformity against the ISO/IEC 27001:2022 standard. The certification is public, listed on the certification body register, and valid for three years with annual surveillance audits and a triennial recertification audit.

The compliance audience cares about both because they answer different questions. SOC 2 answers "did your controls actually work over a defined period?" ISO 27001 answers "do you operate a recognized information security management system?"

### 1.3 OSOP Audit Status

OSOP is not formally audited under either framework today. There is no SOC 2 Type I or Type II report. There is no ISO 27001 certificate. This document is a self-attested control mapping that demonstrates readiness, not a formal opinion or certification. The maturity column on every mapping row reflects the operator's honest assessment of what is implemented, what is partial, and what is a gap.

The intent is twofold. First, give a clear picture of how the existing control set lines up against both frameworks so that a customer security questionnaire can be answered honestly and a future audit can be scoped efficiently. Second, surface the specific work items that still stand between current state and a Type I or Stage 1 audit so that a path to formal audit is visible rather than aspirational.

---

## 2. Scope

### 2.1 In Scope

The crosswalk covers the same authorization boundary defined in SSP-OPS-001 Section 1.2:

- One (1) cloud-hosted virtual private server `alpha-node` running Ubuntu 24.04 LTS at 10.100.1.10
- All containerized services within the Docker Compose stack (`svc-db`, `svc-soar`, `svc-monitoring`, `svc-runtime-detect`, `svc-alert-router`, `svc-secrets`, `svc-identity`, `svc-llm`, `svc-transcription`, `svc-access-broker`, `svc-audit-shipper`, `svc-log-router`, `svc-tunnel`)
- The standalone AI gateway container (`svc-ai-gateway`)
- All Terraform-managed cloud resources at example-ops.com
- The CI/CD pipeline and supply chain controls
- The secrets management pipeline injecting runtime environment variables
- Organizational policies in `docs/grc/POLICY_*.md` and supporting IR playbooks

### 2.2 Out of Scope

The crosswalk does not extend to SaaS dependencies that operate under their own attestation or certification. The following services are out of scope because the Organization inherits controls from the provider rather than implementing them directly:

- The underlying cloud provider hosting `alpha-node` (provider operates under their own SOC 2 Type II and ISO 27001 certification; physical security, hypervisor isolation, and network backbone are inherited)
- The external SaaS monitoring platform (operates under SOC 2 Type II; the Organization is a user entity)
- The external secrets manager (operates under SOC 2 Type II and ISO 27001; the Organization consumes secrets via its API)
- The edge security and DNS provider (operates under SOC 2 Type II and ISO 27001; the Organization consumes WAF, tunnel, and DNS services)
- The model provider used by `svc-ai-gateway` for foundation model inference (operates under SOC 2 Type II; out-of-band data processing addendum in place)
- End-user workstations used to administer OSOP (covered by personal IT hygiene and policy expectations, not in the OSOP authorization boundary)

A Statement of Applicability prepared for a formal ISO 27001 audit would explicitly mark controls inherited from these providers and reference vendor attestation reports.

### 2.3 Categories Covered Under SOC 2

SOC 2 lets the auditee choose which Trust Services Categories to include in scope. OSOP's chosen scope:

- **Security (Common Criteria CC1 through CC9):** Mandatory. Included.
- **Availability (A1):** Included. OSOP serves operational tooling where downtime has real impact.
- **Confidentiality (C1):** Included. OSOP processes audit records, credentials, and configuration data that are not public.
- **Processing Integrity (PI1):** Not in initial scope. PI1 is most relevant to transaction-processing systems (payments, e-commerce). OSOP is an internal security operations platform, not a transactional system. Could be added later if a customer requires it.
- **Privacy (P1 through P8):** Not in initial scope. OSOP does not process consumer personal information at material volume. The Organization's privacy obligations sit in POLICY_AI_GOVERNANCE.md under ISO 27701 alignment.

### 2.4 ISO 27001 Statement of Applicability Posture

For an ISO 27001 Stage 1 audit, the Organization would prepare a formal Statement of Applicability listing all 93 Annex A controls with one of three dispositions: implemented, planned with target date, or excluded with documented justification. This crosswalk previews that posture but does not constitute a final SoA. The final SoA would be a separate signed artifact reviewed by the certification body.

---

## 3. SOC 2 Framework Overview

### 3.1 Source Standard

SOC 2 examinations are governed by AICPA Trust Services Criteria, published in TSP Section 100 (originally issued 2017, revised April 2022 to align with COSO 2013 Internal Control framework updates). The criteria themselves are stable; the 2022 revision added Points of Focus that clarify how to evidence each criterion without changing the criteria text.

### 3.2 Trust Services Categories

The five categories and their control criteria counts:

| Category | Code | Criteria Count | Status for OSOP |
|----------|------|---------------|-----------------|
| Security | CC1 through CC9 | 33 Common Criteria | In scope (mandatory) |
| Availability | A1.1 through A1.3 | 3 | In scope |
| Confidentiality | C1.1 through C1.2 | 2 | In scope |
| Processing Integrity | PI1.1 through PI1.5 | 5 | Out of scope |
| Privacy | P1 through P8 | 18 | Out of scope |

The Security category is mandatory in any SOC 2. The other four are elective.

### 3.3 Common Criteria Structure

The 33 Common Criteria are grouped into nine sections that mirror the COSO Internal Control framework:

- **CC1 Control Environment:** Five criteria covering organizational structure, ethics, accountability, and competence
- **CC2 Communication and Information:** Three criteria covering internal and external information flow
- **CC3 Risk Assessment:** Four criteria covering risk identification, assessment, response, and fraud risk
- **CC4 Monitoring Activities:** Two criteria covering ongoing monitoring and deficiency communication
- **CC5 Control Activities:** Three criteria covering control selection, technology controls, and policy deployment
- **CC6 Logical and Physical Access Controls:** Eight criteria covering access provisioning, authentication, change in roles, physical access, removal, restricted access, prevention of unauthorized access, and disposal of sensitive data
- **CC7 System Operations:** Five criteria covering vulnerability detection, monitoring of system components, incident response, recovery, and configuration management
- **CC8 Change Management:** One criterion covering authorized change to infrastructure, software, and procedures
- **CC9 Risk Mitigation:** Two criteria covering risk treatment from disruption and vendor management

### 3.4 Type I Versus Type II

A Type I report covers the suitability of design at a point in time. The service auditor reads policies, walks through the implementation, and forms an opinion on whether the controls as designed could meet the criteria. There is no test of operating effectiveness over time.

A Type II report covers both design suitability and operating effectiveness over a defined period (typically six to twelve months). The service auditor pulls samples of evidence across the period and tests whether the controls operated as designed.

A reasonable path to a Type II report is: Type I first (three to four months after readiness), then immediately start the observation period for Type II (six to twelve months after Type I).

---

## 4. ISO 27001:2022 Framework Overview

### 4.1 Source Standard

ISO/IEC 27001:2022 was published in October 2022, replacing the 2013 version. The implementation guidance is ISO/IEC 27002:2022, which provides Annex A control elaboration. Certification bodies completed migration audits through October 2025; any new certification today must be against the 2022 version.

### 4.2 ISMS Structure (Clauses 4 through 10)

The body of ISO 27001 specifies the Information Security Management System (ISMS) requirements in clauses 4 through 10. These clauses are mandatory and not optional. Annex A controls are the catalog of safeguards that the ISMS draws from.

| Clause | Title | Substance |
|--------|-------|-----------|
| 4 | Context of the Organization | Internal and external issues, interested parties, ISMS scope definition |
| 5 | Leadership | Management commitment, policy, roles and responsibilities |
| 6 | Planning | Risk assessment, risk treatment, Statement of Applicability, security objectives |
| 7 | Support | Resources, competence, awareness, communication, documented information |
| 8 | Operation | Operational planning, risk assessment execution, risk treatment execution |
| 9 | Performance Evaluation | Monitoring and measurement, internal audit, management review |
| 10 | Improvement | Nonconformity and corrective action, continual improvement |

### 4.3 Annex A Control Set

ISO/IEC 27001:2022 Annex A contains 93 controls organized into four themes:

| Theme | Control Range | Count | Focus |
|-------|---------------|-------|-------|
| Organizational | A.5.1 through A.5.37 | 37 | Policies, roles, responsibilities, supplier relationships, threat intelligence, ICT readiness |
| People | A.6.1 through A.6.8 | 8 | Screening, employment terms, awareness, disciplinary process, remote working, NDA |
| Physical | A.7.1 through A.7.14 | 14 | Physical security perimeters, equipment, secure disposal, clear desk |
| Technological | A.8.1 through A.8.34 | 34 | Access control, cryptography, secure development, network security, logging |

**Total: 93 controls.**

### 4.4 Difference from the 2013 Version

The 2013 version had 114 controls across 14 domains. The 2022 revision consolidated and restructured the catalog, dropped 16 controls (mostly through merger), and added 11 new controls covering:

- Threat intelligence (A.5.7)
- Information security for cloud services (A.5.23)
- ICT readiness for business continuity (A.5.30)
- Physical security monitoring (A.7.4)
- Configuration management (A.8.9)
- Information deletion (A.8.10)
- Data masking (A.8.11)
- Data leakage prevention (A.8.12)
- Monitoring activities (A.8.16)
- Web filtering (A.8.23)
- Secure coding (A.8.28)

The 2022 control set is more aligned with contemporary cloud, container, and DevSecOps practice, which suits OSOP's actual control surface.

---

## 5. SOC 2 Common Criteria Crosswalk

This section maps each Common Criterion to its NIST 800-53 anchor, OSOP implementation, evidence document, and maturity rating. Maturity values: **Implemented** (control is operating and produces evidence), **Partial** (control exists but lacks one of operating cadence, automated evidence collection, or independent review), **Gap** (control does not yet exist in the program).

### 5.1 CC1 Control Environment

| Criterion | Title | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|-----------|-------|-------------|---------------------|----------|----------|
| CC1.1 | Demonstrates commitment to integrity and ethical values | PS-3, PS-6, PS-8 | Acceptable Use Policy and Security Awareness Policy define expected conduct; sole-operator structure means System Owner is accountable for ethical commitments | POLICY_ACCEPTABLE_USE.md, POLICY_SECURITY_AWARENESS.md | Partial |
| CC1.2 | Exercises oversight responsibility | PM-1, PM-2, CA-6 | System Owner serves as Authorizing Official under SSP-OPS-001; documented authorization decision and quarterly review cadence | SSP-OPS-001 Section 1, README.md review schedule | Implemented |
| CC1.3 | Establishes structure, reporting lines, authority, and responsibility | PM-2, PS-7 | IAM_RBAC_ROLE_MAP.md defines three-tier role structure (admin/operator/auditor); ROE document defines decision authority | IAM_RBAC_ROLE_MAP.md, AGENTS.md | Implemented |
| CC1.4 | Demonstrates commitment to competence | PS-2, AT-2, AT-3 | Annual security awareness training requirement defined in POLICY_SECURITY_AWARENESS.md; certifications maintained (SecurityX, SSCP, CCNA) | POLICY_SECURITY_AWARENESS.md | Partial |
| CC1.5 | Enforces accountability | PS-8, AU-10 | Teleport session recording on `alpha-node` admin access; non-repudiation via audit trail | SSP-OPS-001 AU family, FRAMEWORK_CROSSWALK_SQUIRE.md Row 27 | Implemented |

### 5.2 CC2 Communication and Information

| Criterion | Title | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|-----------|-------|-------------|---------------------|----------|----------|
| CC2.1 | Obtains or generates relevant, quality information | PM-1, PM-9 | Datadog monitoring, Falco runtime detection, Langfuse traces, n8n audit logs feed centralized telemetry | EXECUTIVE_SUMMARY_ARCHITECTURE.md, SSP-OPS-001 Section 6 | Implemented |
| CC2.2 | Internally communicates information about objectives, responsibilities, and controls | PM-1, AT-2 | Policies committed to repo, README index maps each policy to its function; PR review surfaces changes | docs/grc/README.md, .github/workflows/ | Implemented |
| CC2.3 | Communicates with external parties | IR-6, AC-21 | Incident notification path defined in POLICY_INCIDENT_RESPONSE.md; transparency posture documented via public GRC library | POLICY_INCIDENT_RESPONSE.md, docs/grc/README.md (public) | Partial |

### 5.3 CC3 Risk Assessment

| Criterion | Title | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|-----------|-------|-------------|---------------------|----------|----------|
| CC3.1 | Specifies suitable objectives | PM-9, PM-11 | Security objectives defined in POLICY_RISK_MANAGEMENT.md and quarterly review cadence | POLICY_RISK_MANAGEMENT.md | Implemented |
| CC3.2 | Identifies and analyzes risk | RA-3, PM-9 | 17 enterprise risks and 10 Squire AI risks documented; quarterly risk register review | RISK_ASSESSMENT.md, SQUIRE_AI_RISK_ASSESSMENT.md | Implemented |
| CC3.3 | Assesses fraud risk | PM-12, RA-3 | Fraud risk reviewed via Risk Assessment for credential theft, insider misuse, and supply-chain compromise scenarios | RISK_ASSESSMENT.md | Partial |
| CC3.4 | Identifies and assesses changes that could significantly impact internal control | CM-3, CM-4 | Change management workflow documented; impact analysis tied to PR review | POLICY_CHANGE_MANAGEMENT.md, .github/workflows/terraform-pr.yml | Implemented |

### 5.4 CC4 Monitoring Activities

| Criterion | Title | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|-----------|-------|-------------|---------------------|----------|----------|
| CC4.1 | Selects, develops, performs ongoing and separate evaluations | CA-2, CA-7, PM-14 | Continuous monitoring via Datadog and Falco; no separate internal audit function stood up yet | SSP-OPS-001 Section 6 | Partial |
| CC4.2 | Evaluates and communicates deficiencies | CA-5, PM-4 | POA&M tracks 30 findings across five assessment sources; quarterly review cadence | POAM_PLAN_OF_ACTION.md | Implemented |

### 5.5 CC5 Control Activities

| Criterion | Title | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|-----------|-------|-------------|---------------------|----------|----------|
| CC5.1 | Selects and develops control activities | CA-2, PM-1, PM-9 | Control set documented in SSP across 16 NIST 800-53 families; risk-driven selection per Risk Management Policy | SSP-OPS-001 Section 5, POLICY_RISK_MANAGEMENT.md | Implemented |
| CC5.2 | Selects and develops general controls over technology | CM-2, CM-6, SC-1 | Baseline configurations via Docker Compose; Terraform state; OPA policies enforce IaC posture | terraform/cd-do-infrastructure/, SECURE_SDLC.md | Implemented |
| CC5.3 | Deploys through policies and procedures | PM-1, AC-1, AU-1 | Each control family has a policy with operating cadence; policies versioned in repo | docs/grc/POLICY_*.md | Implemented |

### 5.6 CC6 Logical and Physical Access Controls

| Criterion | Title | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|-----------|-------|-------------|---------------------|----------|----------|
| CC6.1 | Implements logical access security software, infrastructure, and architectures | AC-3, AC-6, IA-2, IA-5 | Three-tier RBAC; SSH key-based auth to `alpha-node`; MFA required on identity provider; Doppler for secrets | IAM_RBAC_ROLE_MAP.md, POLICY_ACCESS_CONTROL.md | Implemented |
| CC6.2 | Authorizes new internal and external users | AC-2, IA-4 | Access provisioning tied to role definition in RBAC map; sole-operator simplifies but Just-in-Time workflow documented | IAM_ACCESS_REVIEW.md | Partial |
| CC6.3 | Removes access in a timely manner | AC-2, PS-4, PS-5 | Offboarding procedure in Access Control Policy; sole-operator means contractor access is the practical case | POLICY_ACCESS_CONTROL.md | Partial |
| CC6.4 | Restricts physical access | PE-2, PE-3, PE-6 | Physical security inherited from cloud provider (`alpha-node` is a VPS); end-user workstation physical security is operator responsibility | Cloud provider SOC 2 Type II (vendor-inherited) | Implemented (inherited) |
| CC6.5 | Discontinues logical and physical protections over physical assets | MP-6 | Cloud provider handles disk sanitization on VPS termination; vendor attestation referenced | Cloud provider SOC 2 Type II (vendor-inherited) | Implemented (inherited) |
| CC6.6 | Implements logical access controls to protect against threats from sources outside system boundaries | SC-7, SC-8, AC-17 | Cloudflare tunnel terminates external traffic; no direct internet exposure of `svc-*` ports; WAF protects exposed endpoints | EXECUTIVE_SUMMARY_ARCHITECTURE.md, terraform/cd-do-infrastructure/tunnel.tf | Implemented |
| CC6.7 | Restricts the transmission, movement, and removal of information | AC-4, SC-8, SC-28 | TLS 1.3 in transit; Postgres encrypted at rest via cloud provider; data masking and DLP-style controls in Squire pre-graph PII scan | DAST_METHODOLOGY.md, FRAMEWORK_CROSSWALK_SQUIRE.md Row 3 | Partial |
| CC6.8 | Implements controls to prevent or detect and act upon unauthorized or malicious software | SI-3, SI-4, RA-5 | Trivy image scans on every build; Falco runtime detection; container immutability via signed images | SECURE_SDLC.md, VULN_WRITEUP_N8N_CREDENTIAL_EXPOSURE.md | Implemented |

### 5.7 CC7 System Operations

| Criterion | Title | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|-----------|-------|-------------|---------------------|----------|----------|
| CC7.1 | Uses detection and monitoring procedures to identify changes in configurations | CM-2, CM-3, CM-8 | Configuration drift detection via Terraform plan in PR pipeline; Datadog change events | terraform-pr.yml, EXECUTIVE_SUMMARY_ARCHITECTURE.md | Implemented |
| CC7.2 | Monitors system components for anomalies | SI-4, AU-6, IR-4 | Falco runtime detection; Datadog log analytics; Langfuse trace anomaly checks for AI components | SSP-OPS-001 Section 6, FRAMEWORK_CROSSWALK_SQUIRE.md Row 2 | Implemented |
| CC7.3 | Evaluates security events to determine whether they represent security incidents | IR-4, IR-5, AU-6 | Severity classification in IR playbook; Squire classifier node for AI alert triage | POLICY_INCIDENT_RESPONSE.md, PLAYBOOK_COMPROMISED_CONTAINER.md | Implemented |
| CC7.4 | Responds to identified security incidents | IR-4, IR-6, IR-8 | Five IR playbooks with decision flowcharts; tabletop exercise documented; notification path defined | docs/grc/PLAYBOOK_*.md, TABLETOP_EXERCISE.md | Implemented |
| CC7.5 | Identifies, develops, and implements activities to recover from identified incidents | CP-2, CP-10, IR-4 | Recovery procedures in each playbook; backup and snapshot cadence in BC/DR policies | POLICY_BUSINESS_CONTINUITY.md, POLICY_DISASTER_RECOVERY.md | Implemented |

### 5.8 CC8 Change Management

| Criterion | Title | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|-----------|-------|-------------|---------------------|----------|----------|
| CC8.1 | Authorizes, designs, develops, configures, documents, tests, approves, and implements changes | CM-3, CM-4, CM-5, SA-3 | Pull request workflow with mandatory review; Terraform plan + Checkov + OPA gates; Trivy and Gitleaks on merge | SECURE_SDLC.md, POLICY_CHANGE_MANAGEMENT.md | Implemented |

### 5.9 CC9 Risk Mitigation

| Criterion | Title | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|-----------|-------|-------------|---------------------|----------|----------|
| CC9.1 | Identifies, selects, and develops risk mitigation activities for risks from potential business disruptions | CP-2, CP-4, CP-10 | Business continuity policy; quarterly tabletop scope; backup and restore drill cadence | POLICY_BUSINESS_CONTINUITY.md, POLICY_DISASTER_RECOVERY.md | Partial |
| CC9.2 | Assesses and manages risks associated with vendors and business partners | SA-9, SR-3, SR-6 | Vendor list maintained informally; key SaaS providers identified by SOC 2 / ISO 27001 status; no formal vendor risk program yet | AI_SUPPLY_CHAIN_REGISTER.md, EXECUTIVE_SUMMARY_COMPLIANCE.md | Gap |

---

## 6. SOC 2 Additional Categories Crosswalk

### 6.1 A1 Availability

| Criterion | Title | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|-----------|-------|-------------|---------------------|----------|----------|
| A1.1 | Maintains, monitors, and evaluates current processing capacity | CP-2, SC-5, SI-4 | Datadog capacity monitoring; alert on disk, CPU, memory thresholds; documented capacity plan in BC policy | POLICY_BUSINESS_CONTINUITY.md, SSP-OPS-001 Section 6 | Partial |
| A1.2 | Authorizes, designs, develops, implements, operates, approves, maintains, and monitors environmental protections, software, data backup processes, and recovery infrastructure | CP-6, CP-9, CP-10 | Postgres backups to object storage (14-day retention); droplet snapshots weekly; documented RTO and RPO in DR policy | POLICY_DISASTER_RECOVERY.md, FRAMEWORK_CROSSWALK_SQUIRE.md Rows 15 and 16 | Implemented |
| A1.3 | Tests recovery plan procedures supporting system recovery | CP-4 | Tabletop exercise covers IR recovery; full DR restore test scheduled semi-annually but not yet executed | TABLETOP_EXERCISE.md, POLICY_DISASTER_RECOVERY.md | Partial |

### 6.2 C1 Confidentiality

| Criterion | Title | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|-----------|-------|-------------|---------------------|----------|----------|
| C1.1 | Identifies and maintains confidential information to meet the entity's objectives | RA-2, MP-3, AC-21 | Information types classified in SSP Section 1.3; CUI-INTERNAL classification on GRC docs; confidentiality labels in document headers | SSP-OPS-001 Section 1.3 | Implemented |
| C1.2 | Disposes of confidential information to meet the entity's objectives | MP-6, AU-11 | Document retention defined per artifact; secrets rotation quarterly; backup retention 14 days then automated deletion | POLICY_ACCESS_CONTROL.md, FRAMEWORK_CROSSWALK_SQUIRE.md Row 28 | Partial |

---

## 7. ISO 27001:2022 ISMS Clause Crosswalk

### 7.1 Clause 4: Context of the Organization

| Sub-Clause | Requirement | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|------------|-------------|-------------|---------------------|----------|----------|
| 4.1 | Understanding the organization and its context | PM-9, PM-11 | Internal context (sole-operator small business) and external context (security operations market, customer expectations) documented informally | EXECUTIVE_SUMMARY_COMPLIANCE.md | Partial |
| 4.2 | Understanding the needs and expectations of interested parties | PM-9 | Interested parties identified informally: customers, prospective auditors, regulators where applicable, model providers | (no formal artifact) | Gap |
| 4.3 | Determining the scope of the ISMS | PM-1 | Scope defined in SSP-OPS-001 Section 1.2; mirrors this crosswalk's Section 2 | SSP-OPS-001 Section 1.2 | Implemented |
| 4.4 | Information security management system | PM-1, PM-7 | ISMS effectively constituted by the GRC document library plus continuous monitoring program; not formally named or chartered as "the ISMS" | docs/grc/ library | Partial |

### 7.2 Clause 5: Leadership

| Sub-Clause | Requirement | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|------------|-------------|-------------|---------------------|----------|----------|
| 5.1 | Leadership and commitment | PM-1, PM-2 | System Owner serves as top management; authorization decisions documented; resources allocated via continued operational investment | SSP-OPS-001 Section 1 | Implemented |
| 5.2 | Policy | PM-1, AC-1, AU-1 | Information security policy implied through the policy library; no single signed "Information Security Policy" document yet | docs/grc/POLICY_*.md | Partial |
| 5.3 | Organizational roles, responsibilities, and authorities | PM-2, PS-7 | RBAC role map defines admin/operator/auditor; Information Security Officer and System Owner roles documented | IAM_RBAC_ROLE_MAP.md | Implemented |

### 7.3 Clause 6: Planning

| Sub-Clause | Requirement | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|------------|-------------|-------------|---------------------|----------|----------|
| 6.1.1 | Actions to address risks and opportunities | PM-9, RA-3 | Risk Management Policy defines the process; POA&M tracks identified risks | POLICY_RISK_MANAGEMENT.md, POAM_PLAN_OF_ACTION.md | Implemented |
| 6.1.2 | Information security risk assessment | RA-3 | 17 enterprise plus 10 Squire AI risks assessed with likelihood-impact matrix | RISK_ASSESSMENT.md, SQUIRE_AI_RISK_ASSESSMENT.md | Implemented |
| 6.1.3 | Information security risk treatment | PM-9, RA-3 | Treatment decisions captured per risk; mitigation tracked in POA&M; no formal Statement of Applicability yet | RISK_ASSESSMENT.md, POAM_PLAN_OF_ACTION.md | Partial |
| 6.2 | Information security objectives and planning to achieve them | PM-1, PM-11 | Objectives implied by SSP and policy targets; no top-level signed objectives document | EXECUTIVE_SUMMARY_COMPLIANCE.md | Partial |
| 6.3 | Planning of changes | CM-3 | Change planning covered by SDLC and PR workflow | SECURE_SDLC.md | Implemented |

### 7.4 Clause 7: Support

| Sub-Clause | Requirement | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|------------|-------------|-------------|---------------------|----------|----------|
| 7.1 | Resources | PM-1, PM-3 | Sole-operator model; operational investment documented; cloud spend tracked monthly | (operational evidence) | Partial |
| 7.2 | Competence | PS-2, AT-3 | Certifications maintained (SecurityX, SSCP, CCNA); continuous study tracked in study plan documents | POLICY_SECURITY_AWARENESS.md | Implemented |
| 7.3 | Awareness | AT-2, AT-3 | Sole-operator self-awareness implicit; contractor onboarding would require formal awareness training | POLICY_SECURITY_AWARENESS.md | Partial |
| 7.4 | Communication | IR-6, PM-1 | Internal communication via repo and PR; external via public GRC library and incident notification path | docs/grc/README.md | Partial |
| 7.5 | Documented information | AU-1, CM-12 | Documented information controlled via version control in git; document IDs and revision history on each artifact | docs/grc/ (all files have frontmatter) | Implemented |

### 7.5 Clause 8: Operation

| Sub-Clause | Requirement | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|------------|-------------|-------------|---------------------|----------|----------|
| 8.1 | Operational planning and control | PM-1, CM-3 | SDLC and change management policies cover operational planning | SECURE_SDLC.md, POLICY_CHANGE_MANAGEMENT.md | Implemented |
| 8.2 | Information security risk assessment | RA-3 | Risk assessment cadence quarterly per Risk Management Policy | POLICY_RISK_MANAGEMENT.md | Implemented |
| 8.3 | Information security risk treatment | PM-9 | Risk treatment tracked in POA&M with target dates and disposition | POAM_PLAN_OF_ACTION.md | Implemented |

### 7.6 Clause 9: Performance Evaluation

| Sub-Clause | Requirement | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|------------|-------------|-------------|---------------------|----------|----------|
| 9.1 | Monitoring, measurement, analysis, and evaluation | CA-7, PM-14 | Continuous monitoring via Datadog and Falco; quarterly POA&M review; risk register review cadence | SSP-OPS-001 Section 6 | Implemented |
| 9.2 | Internal audit | CA-2, CA-7 | No formal internal audit function stood up; relies on PR review and self-assessment | (no internal audit charter) | Gap |
| 9.3 | Management review | PM-2, CA-6 | System Owner conducts informal review at quarterly cadence; not formally minuted as "management review" with the ISO 9.3 inputs and outputs | (no formal management review minutes) | Gap |

### 7.7 Clause 10: Improvement

| Sub-Clause | Requirement | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|------------|-------------|-------------|---------------------|----------|----------|
| 10.1 | Continual improvement | PM-1, CA-5 | Continuous improvement evidenced by versioned documentation, expanding GRC library, and quarterly review cadence | docs/grc/README.md review schedule | Implemented |
| 10.2 | Nonconformity and corrective action | CA-5, PM-4 | POA&M tracks identified deficiencies with corrective action and target dates; root cause captured per entry | POAM_PLAN_OF_ACTION.md | Implemented |

---

## 8. ISO 27001:2022 Annex A Control Crosswalk

### 8.1 A.5 Organizational Controls (37 controls)

| Annex A | Title | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|---------|-------|-------------|---------------------|----------|----------|
| A.5.1 | Policies for information security | PM-1, AC-1 | Information Security Policy implied through the policy library; no consolidated top-level policy yet | docs/grc/POLICY_*.md | Partial |
| A.5.2 | Information security roles and responsibilities | PM-2, PS-7 | RBAC role map; Information Security Officer and System Owner roles | IAM_RBAC_ROLE_MAP.md | Implemented |
| A.5.3 | Segregation of duties | AC-5, AC-6 | Sole-operator constraint limits separation; documented compensating controls (audit trail, MFA, PR review) | IAM_RBAC_ROLE_MAP.md | Partial |
| A.5.4 | Management responsibilities | PM-1, PM-2 | System Owner accountable for security outcomes | SSP-OPS-001 Section 1 | Implemented |
| A.5.5 | Contact with authorities | IR-6 | Contact paths defined in IR policy for breach reporting and law enforcement | POLICY_INCIDENT_RESPONSE.md | Partial |
| A.5.6 | Contact with special interest groups | PM-15 | Participation in security community via public GRC library and conference engagement | (informal) | Partial |
| A.5.7 | Threat intelligence | RA-3, SI-5 | Threat intelligence from CISA advisories, vendor security bulletins, Cloudflare WAF telemetry | (informal feed) | Partial |
| A.5.8 | Information security in project management | SA-3, SA-8 | Security integrated into SDLC and PR workflow from initial design | SECURE_SDLC.md | Implemented |
| A.5.9 | Inventory of information and other associated assets | CM-8 | Asset inventory via Terraform state and Docker Compose; AI supply chain register for AI components | terraform/cd-do-infrastructure/, AI_SUPPLY_CHAIN_REGISTER.md | Implemented |
| A.5.10 | Acceptable use of information and other associated assets | PL-4 | Acceptable Use Policy | POLICY_ACCEPTABLE_USE.md | Implemented |
| A.5.11 | Return of assets | PS-4, PS-5 | Sole-operator structure; contractor offboarding procedure documented in Access Control Policy | POLICY_ACCESS_CONTROL.md | Partial |
| A.5.12 | Classification of information | RA-2 | Classification labels on all GRC docs (CUI-INTERNAL); information types defined in SSP | SSP-OPS-001 Section 1.3 | Implemented |
| A.5.13 | Labelling of information | MP-3 | Document headers include classification; secret values not labelled but stored in dedicated secrets manager | (per-document frontmatter) | Implemented |
| A.5.14 | Information transfer | AC-21, SC-8 | TLS in transit; data transfer agreements with model provider; encryption in motion documented | POLICY_ACCESS_CONTROL.md | Implemented |
| A.5.15 | Access control | AC-1, AC-3 | Access Control Policy with three-tier RBAC | POLICY_ACCESS_CONTROL.md | Implemented |
| A.5.16 | Identity management | IA-4 | Identity provider hosts user identities; sole-operator identity is the System Owner | POLICY_ACCESS_CONTROL.md | Implemented |
| A.5.17 | Authentication information | IA-5 | Secrets in secrets manager; quarterly rotation; SSH key-based auth | FRAMEWORK_CROSSWALK_SQUIRE.md Row 28 | Implemented |
| A.5.18 | Access rights | AC-2, AC-6 | Three-tier RBAC; just-in-time elevation for admin actions | IAM_RBAC_ROLE_MAP.md, IAM_ACCESS_REVIEW.md | Implemented |
| A.5.19 | Information security in supplier relationships | SA-9, SR-3 | Supplier security implied by SaaS attestation reports; no formal supplier security policy yet | EXECUTIVE_SUMMARY_COMPLIANCE.md | Gap |
| A.5.20 | Addressing information security within supplier agreements | SA-9, SA-12 | Data processing addenda in place for key SaaS providers; not formally cataloged | (vendor agreements) | Partial |
| A.5.21 | Managing information security in the ICT supply chain | SR-3, SR-4 | AI supply chain register tracks 14 components; Trivy and Cosign on container supply chain | AI_SUPPLY_CHAIN_REGISTER.md, SECURE_SDLC.md | Implemented |
| A.5.22 | Monitoring, review, and change management of supplier services | SA-9 | Vendor SOC 2 reports reviewed when published; no formal vendor review cadence yet | (informal) | Gap |
| A.5.23 | Information security for use of cloud services | SC-7, AC-20 | Cloud service inventory; vendor SOC 2 reports tracked; data processing addenda in place | EXECUTIVE_SUMMARY_ARCHITECTURE.md | Partial |
| A.5.24 | Information security incident management planning and preparation | IR-1, IR-8 | Incident Response Policy plus five playbooks; tabletop exercise documented | POLICY_INCIDENT_RESPONSE.md, docs/grc/PLAYBOOK_*.md | Implemented |
| A.5.25 | Assessment and decision on information security events | IR-4 | Severity classification in IR playbooks; Squire AI alert classifier | POLICY_INCIDENT_RESPONSE.md | Implemented |
| A.5.26 | Response to information security incidents | IR-4, IR-6 | Five IR playbooks with response steps | docs/grc/PLAYBOOK_*.md | Implemented |
| A.5.27 | Learning from information security incidents | IR-4 | Post-incident review captured in tabletop exercise; lessons feed POA&M | TABLETOP_EXERCISE.md, POAM_PLAN_OF_ACTION.md | Implemented |
| A.5.28 | Collection of evidence | AU-10 | Audit trail collection via Datadog, Langfuse, Postgres immutable triggers | FRAMEWORK_CROSSWALK_SQUIRE.md Rows 30 and 31 | Implemented |
| A.5.29 | Information security during disruption | CP-2, CP-10 | Business continuity plan; degraded mode for AI components | POLICY_BUSINESS_CONTINUITY.md | Implemented |
| A.5.30 | ICT readiness for business continuity | CP-2, CP-4, CP-10 | Backup and restore drill; DR procedures; failover patterns | POLICY_DISASTER_RECOVERY.md | Partial |
| A.5.31 | Legal, statutory, regulatory, and contractual requirements | PL-4 | Legal requirements identified informally (state business registration, data protection where applicable); no formal compliance register | (informal) | Gap |
| A.5.32 | Intellectual property rights | PL-4 | Open-source license compliance via SBOM and license review; no IP licensing program | SECURE_SDLC.md (SBOM) | Partial |
| A.5.33 | Protection of records | AU-9, AU-11 | Audit records protected via Postgres role REVOKE; retention defined per record type | FRAMEWORK_CROSSWALK_SQUIRE.md Row 30, AI_AUDIT_TRAIL_SPEC.md | Implemented |
| A.5.34 | Privacy and protection of personally identifiable information | (privacy) | PII handling in AI components via pre-graph regex scan; PII not processed at material volume in core OSOP | POL-AI-001, FRAMEWORK_CROSSWALK_SQUIRE.md Row 3 | Partial |
| A.5.35 | Independent review of information security | CA-2, CA-7 | No formal independent review; relies on PR review and public GRC visibility | (gap) | Gap |
| A.5.36 | Compliance with policies, rules, and standards for information security | CA-5, AU-6 | POA&M tracks compliance findings; review cadence captures policy adherence | POAM_PLAN_OF_ACTION.md | Implemented |
| A.5.37 | Documented operating procedures | AU-1, CM-12 | Operating procedures documented in policies; version controlled in git | docs/grc/POLICY_*.md | Implemented |

### 8.2 A.6 People Controls (8 controls)

| Annex A | Title | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|---------|-------|-------------|---------------------|----------|----------|
| A.6.1 | Screening | PS-3 | Background check for any contractor with access; sole-operator self-attestation | POLICY_ACCEPTABLE_USE.md | Partial |
| A.6.2 | Terms and conditions of employment | PS-6 | Acceptable Use Policy serves as terms of access; contractor agreements would include security obligations | POLICY_ACCEPTABLE_USE.md | Partial |
| A.6.3 | Information security awareness, education, and training | AT-2, AT-3 | Continuous study tracked via certification roadmap; contractor training requirement defined | POLICY_SECURITY_AWARENESS.md | Partial |
| A.6.4 | Disciplinary process | PS-8 | Disciplinary expectations documented in Acceptable Use Policy; sole-operator constraint limits practical applicability | POLICY_ACCEPTABLE_USE.md | Partial |
| A.6.5 | Responsibilities after termination or change of employment | PS-4, PS-5 | Offboarding procedure includes access removal and asset return | POLICY_ACCESS_CONTROL.md | Implemented |
| A.6.6 | Confidentiality or non-disclosure agreements | PS-6, AC-21 | NDA expected with any contractor or customer engagement; standard template referenced | (vendor agreements) | Partial |
| A.6.7 | Remote working | AC-17, AC-19 | All work is remote; SSH via tunnel; MFA on identity provider; endpoint hygiene operator responsibility | POLICY_ACCESS_CONTROL.md | Partial |
| A.6.8 | Information security event reporting | IR-6 | Incident reporting path defined in IR policy | POLICY_INCIDENT_RESPONSE.md | Implemented |

### 8.3 A.7 Physical Controls (14 controls)

Most physical controls are inherited from the cloud provider for `alpha-node` and from the end-user workstation environment for administration. A formal Statement of Applicability would mark most of these as inherited from a vendor with documented attestation.

| Annex A | Title | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|---------|-------|-------------|---------------------|----------|----------|
| A.7.1 | Physical security perimeters | PE-3 | Cloud data center perimeter inherited from provider | Cloud provider SOC 2 Type II | Implemented (inherited) |
| A.7.2 | Physical entry | PE-2, PE-3 | Cloud data center access controls inherited | Cloud provider SOC 2 Type II | Implemented (inherited) |
| A.7.3 | Securing offices, rooms, and facilities | PE-5 | Not applicable to cloud-only operation; end-user workstation physical security is operator responsibility | (operator hygiene) | Implemented (inherited) |
| A.7.4 | Physical security monitoring | PE-6 | Cloud provider data center monitoring | Cloud provider SOC 2 Type II | Implemented (inherited) |
| A.7.5 | Protecting against physical and environmental threats | PE-13, PE-14 | Inherited from cloud provider (fire suppression, HVAC, flood protection) | Cloud provider SOC 2 Type II | Implemented (inherited) |
| A.7.6 | Working in secure areas | PE-3 | Not applicable in sole-operator remote configuration | n/a | Implemented (inherited) |
| A.7.7 | Clear desk and clear screen | PE-5 | Screen lock and clear desk practiced by operator; documented in Acceptable Use Policy | POLICY_ACCEPTABLE_USE.md | Implemented |
| A.7.8 | Equipment siting and protection | PE-18 | Cloud provider handles physical equipment; operator workstation handled per operator hygiene | Cloud provider SOC 2 Type II | Implemented (inherited) |
| A.7.9 | Security of assets off-premises | MP-5 | Operator laptop with disk encryption; mobile device management not deployed (sole-operator) | (operator hygiene) | Partial |
| A.7.10 | Storage media | MP-2, MP-4 | Removable media not used in OSOP operations; documented prohibition in Acceptable Use | POLICY_ACCEPTABLE_USE.md | Implemented |
| A.7.11 | Supporting utilities | PE-9, PE-10 | Inherited from cloud provider | Cloud provider SOC 2 Type II | Implemented (inherited) |
| A.7.12 | Cabling security | PE-4 | Inherited from cloud provider | Cloud provider SOC 2 Type II | Implemented (inherited) |
| A.7.13 | Equipment maintenance | MA-2, MA-5 | Inherited from cloud provider | Cloud provider SOC 2 Type II | Implemented (inherited) |
| A.7.14 | Secure disposal or re-use of equipment | MP-6 | Cloud provider handles disk sanitization on VPS termination | Cloud provider SOC 2 Type II | Implemented (inherited) |

### 8.4 A.8 Technological Controls (34 controls)

| Annex A | Title | NIST 800-53 | OSOP Implementation | Evidence | Maturity |
|---------|-------|-------------|---------------------|----------|----------|
| A.8.1 | User end point devices | AC-19 | Operator workstation with full disk encryption, MFA, endpoint protection; no MDM yet | (operator hygiene) | Partial |
| A.8.2 | Privileged access rights | AC-6 | Just-in-time elevation; Teleport session recording on `alpha-node` admin | IAM_ACCESS_REVIEW.md, FRAMEWORK_CROSSWALK_SQUIRE.md Row 27 | Implemented |
| A.8.3 | Information access restriction | AC-3, AC-6 | RBAC plus network segmentation; database role separation | IAM_RBAC_ROLE_MAP.md | Implemented |
| A.8.4 | Access to source code | AC-3, CM-5 | GitHub repository access controlled via GitHub identity; PR review required for merge | (GitHub access controls) | Implemented |
| A.8.5 | Secure authentication | IA-2, IA-5 | MFA on identity provider; SSH key-based auth; secrets in dedicated secrets manager | POLICY_ACCESS_CONTROL.md | Implemented |
| A.8.6 | Capacity management | CP-2, SC-5 | Datadog capacity monitoring; alerts on resource thresholds | SSP-OPS-001 Section 6 | Partial |
| A.8.7 | Protection against malware | SI-3 | Trivy image scans; Falco runtime detection of malware-like behavior; container immutability | SECURE_SDLC.md | Implemented |
| A.8.8 | Management of technical vulnerabilities | RA-5, SI-2 | Vulnerability Management Policy; Trivy on every build; pip-audit in CI; quarterly DAST scan | POLICY_VULNERABILITY_MANAGEMENT.md, DAST_METHODOLOGY.md | Implemented |
| A.8.9 | Configuration management | CM-2, CM-6 | Terraform for infrastructure; Docker Compose for service config; baseline configurations versioned | terraform/cd-do-infrastructure/ | Implemented |
| A.8.10 | Information deletion | MP-6, AU-11 | Backup retention 14 days then automated deletion; secrets rotation invalidates old values; GRC doc archive procedure | POLICY_DISASTER_RECOVERY.md | Partial |
| A.8.11 | Data masking | SI-19 | Pre-graph PII regex scanner in Squire; sanitization patterns in GRC docs | FRAMEWORK_CROSSWALK_SQUIRE.md Row 3, SANITIZATION_KEY.md (local) | Implemented |
| A.8.12 | Data leakage prevention | SI-4, SC-7 | Pre-graph PII scan blocks SSN/CC/email before LLM call; structured block response prevents echo | FRAMEWORK_CROSSWALK_SQUIRE.md Row 3 | Partial |
| A.8.13 | Information backup | CP-9 | Postgres backups to object storage; weekly droplet snapshots; documented in BC and DR policies | POLICY_DISASTER_RECOVERY.md, FRAMEWORK_CROSSWALK_SQUIRE.md Rows 15 and 16 | Implemented |
| A.8.14 | Redundancy of information processing facilities | CP-7 | Single-region deployment; failover plan documented but redundant facility not provisioned | POLICY_DISASTER_RECOVERY.md | Partial |
| A.8.15 | Logging | AU-2, AU-3, AU-12 | Full-coverage logging across all services; Langfuse traces for AI; immutable Postgres tables for audit | SSP-OPS-001 AU family | Implemented |
| A.8.16 | Monitoring activities | AU-6, SI-4 | Datadog log analytics; Falco runtime alerts; Langfuse anomaly checks | SSP-OPS-001 Section 6 | Implemented |
| A.8.17 | Clock synchronization | AU-8 | NTP synchronization on `alpha-node`; cloud provider time sync inherited | (system config) | Implemented |
| A.8.18 | Use of privileged utility programs | AC-6, CM-7 | Privileged utilities require sudo and ssh; Teleport session recording captures invocation | (system config) | Implemented |
| A.8.19 | Installation of software on operational systems | CM-7, CM-11 | Operational systems are containerized; software install controlled via Docker image build pipeline | SECURE_SDLC.md | Implemented |
| A.8.20 | Networks security | SC-7, AC-4 | Cloudflare tunnel as ingress; no direct port exposure; Docker network segmentation | terraform/cd-do-infrastructure/tunnel.tf, FRAMEWORK_CROSSWALK_SQUIRE.md Row 20 | Implemented |
| A.8.21 | Security of network services | SC-7 | Edge security provider WAF; tunnel terminates externally facing services | EXECUTIVE_SUMMARY_ARCHITECTURE.md | Implemented |
| A.8.22 | Segregation of networks | AC-4, SC-7 | Docker networks separate `net-core` from `net-ai`; explicit bridges only | FRAMEWORK_CROSSWALK_SQUIRE.md Row 20 | Implemented |
| A.8.23 | Web filtering | SC-7, SC-18 | Outbound traffic from `alpha-node` filtered via firewall rules; egress allow-list for AI components | (firewall rules) | Partial |
| A.8.24 | Use of cryptography | SC-12, SC-13 | TLS 1.3 in transit; encryption at rest via cloud provider; cryptographic libraries pinned and patched | DAST_METHODOLOGY.md | Implemented |
| A.8.25 | Secure development life cycle | SA-3, SA-8 | Secure SDLC documented with 12 security gates; PR review; OPA policy enforcement | SECURE_SDLC.md | Implemented |
| A.8.26 | Application security requirements | SA-3, SA-15 | Security requirements identified at design time; documented in SSP control mappings | SECURE_SDLC.md | Implemented |
| A.8.27 | Secure system architecture and engineering principles | SA-8 | Architecture documented in Executive Summary Architecture; trust zones and data flows mapped | EXECUTIVE_SUMMARY_ARCHITECTURE.md, DATA_FLOW_DIAGRAM.md | Implemented |
| A.8.28 | Secure coding | SA-15, SA-11 | Secure coding practices in repo; code review surfaces issues; static analysis via Semgrep | CODE_REVIEW_FINDINGS.md, SECURE_SDLC.md | Implemented |
| A.8.29 | Security testing in development and acceptance | CA-2, SA-11 | Pytest regression suite; DAST scans; red-team test cases for AI components | DAST_METHODOLOGY.md, REDTEAM_RESULTS.md | Implemented |
| A.8.30 | Outsourced development | SA-4 | Development is in-house; outsourced development governance not applicable today | n/a | Implemented |
| A.8.31 | Separation of development, test, and production environments | CM-2, SA-3 | No separate test environment today; production traffic on `alpha-node` with feature flags for risky changes | (environment strategy) | Partial |
| A.8.32 | Change management | CM-3, CM-5 | Change management policy; PR review; Terraform plan gates | POLICY_CHANGE_MANAGEMENT.md | Implemented |
| A.8.33 | Test information | SA-11 | Test fixtures sanitized; no production data in test cases; red-team data isolated | DAST_METHODOLOGY.md | Implemented |
| A.8.34 | Protection of information systems during audit testing | CA-2 | Audit testing scoped to non-production paths where possible; production-touching tests documented | (process) | Partial |

---

## 9. Statement of Applicability Summary

### 9.1 Applicable Controls Count

Of the 93 Annex A controls in ISO/IEC 27001:2022, the OSOP draft Statement of Applicability would treat them as follows:

| Disposition | Count | Notes |
|-------------|-------|-------|
| Implemented (direct) | 48 | OSOP implements the control directly with evidence |
| Implemented (inherited) | 13 | Inherited from cloud provider or other SaaS with documented attestation |
| Partial | 28 | Control exists but missing operating cadence, automation, or independent review |
| Gap | 4 | Control does not yet exist in the program |
| Not Applicable | 0 | No controls are formally excluded as not applicable; cloud-inheritance covers the physical control set |

The breakdown by theme:

| Theme | Total | Implemented | Inherited | Partial | Gap |
|-------|-------|-------------|-----------|---------|-----|
| A.5 Organizational | 37 | 20 | 0 | 13 | 4 |
| A.6 People | 8 | 2 | 0 | 6 | 0 |
| A.7 Physical | 14 | 1 | 12 | 1 | 0 |
| A.8 Technological | 34 | 25 | 1 | 8 | 0 |
| **Total** | **93** | **48** | **13** | **28** | **4** |

The combined "Implemented (direct) plus Implemented (inherited)" count is 61 of 93, which is 66 percent. Adding Partial brings the readiness coverage to 89 of 93, or 96 percent.

### 9.2 Excluded Controls and Justifications

OSOP does not currently exclude any Annex A controls as Not Applicable. Where the cloud provider implements a control on the Organization's behalf, the SoA marks it as Inherited with a reference to the provider's attestation report. This posture is more conservative than exclusion and is generally preferred by certification bodies because it shows that the control surface was considered, even if the implementing party is upstream.

If a future scope decision excluded specific controls (for example, A.6.1 Screening for a sole-operator certification where the operator is the legal entity owner), the SoA would carry the exclusion with a documented rationale and the certification body would assess whether the rationale is acceptable.

---

## 10. Combined Maturity Dashboard

### 10.1 SOC 2 Trust Services Criteria Coverage

| Category | Criteria | Implemented | Partial | Gap | Inherited |
|----------|----------|-------------|---------|-----|-----------|
| CC1 Control Environment | 5 | 3 | 2 | 0 | 0 |
| CC2 Communication and Information | 3 | 2 | 1 | 0 | 0 |
| CC3 Risk Assessment | 4 | 3 | 1 | 0 | 0 |
| CC4 Monitoring Activities | 2 | 1 | 1 | 0 | 0 |
| CC5 Control Activities | 3 | 3 | 0 | 0 | 0 |
| CC6 Access Controls | 8 | 4 | 2 | 0 | 2 |
| CC7 System Operations | 5 | 5 | 0 | 0 | 0 |
| CC8 Change Management | 1 | 1 | 0 | 0 | 0 |
| CC9 Risk Mitigation | 2 | 0 | 1 | 1 | 0 |
| A1 Availability | 3 | 1 | 2 | 0 | 0 |
| C1 Confidentiality | 2 | 1 | 1 | 0 | 0 |
| **Total** | **38** | **24** | **11** | **1** | **2** |

Implemented or Inherited coverage: 26 of 38 criteria, or 68 percent. Including Partial: 37 of 38, or 97 percent. The one Gap is CC9.2 vendor management, called out below in Section 13.

### 10.2 ISO 27001:2022 Coverage by Surface

| Surface | Total Items | Implemented or Inherited | Partial | Gap | Coverage % |
|---------|-------------|--------------------------|---------|-----|------------|
| ISMS Clauses 4-10 | 25 sub-clauses | 16 | 6 | 3 | 64% direct, 88% including partial |
| Annex A.5 | 37 | 20 | 13 | 4 | 54% direct, 89% including partial |
| Annex A.6 | 8 | 2 | 6 | 0 | 25% direct, 100% including partial |
| Annex A.7 | 14 | 13 | 1 | 0 | 93% direct, 100% including partial |
| Annex A.8 | 34 | 26 | 8 | 0 | 76% direct, 100% including partial |
| **Combined Annex A** | **93** | **61** | **28** | **4** | **66% direct, 96% including partial** |

### 10.3 Honest Gap Call-Outs

Reading the numbers as "we are 96 percent ready" would be misleading. The Partial column hides real work. Many partials need a documented operating cadence, an automated evidence collection step, or independent review before they would clear a service auditor or certification body. The Gap items are not theoretical; they are explicit holes that the path to formal audit (Section 11) must close before scheduling either engagement.

---

## 11. Path to Formal Audit

### 11.1 SOC 2 Type I Readiness Requirements

A SOC 2 Type I report can be issued once the controls are designed and ready to demonstrate, even if they have not yet operated long enough for a Type II observation period. Concrete prerequisites:

1. **Service auditor selection.** A CPA firm with SOC 2 attestation experience. Estimate 4 to 8 weeks to select, contract, and onboard.
2. **System description.** A "Section 3" document describing the services provided, the system boundaries, principal service commitments, system components, and complementary user entity controls. SSP-OPS-001 covers most of this content; a SOC 2-formatted system description would consolidate it.
3. **Control matrix.** This crosswalk plus the maturity ratings is the starting point. The service auditor would request remediation of the Gap items before they would issue an opinion.
4. **Sample evidence package.** Point-in-time evidence for each criterion. Most of this exists in the repo and monitoring stack; collection would be a one-time exercise.
5. **Management assertion.** A signed assertion from the System Owner that the controls are suitably designed.

Typical Type I engagement length: 6 to 10 weeks from kickoff to report issuance.

### 11.2 SOC 2 Type II Observation Period

After Type I, a Type II observation period begins. The minimum useful observation period is six months; the typical period is twelve months. During this period:

- Evidence is captured continuously, not at a point in time
- Sample sizes for testing increase with the population (for example, a quarterly review needs four samples in twelve months)
- Any control failure during the observation period must be documented and remediated
- The service auditor returns at period end to test operating effectiveness

A Type II report covering the calendar year is a common cadence after Type I, with the report issued in February or March of the following year.

### 11.3 ISO 27001 Stage 1 Audit Prerequisites

The Stage 1 audit is a documentation review by the certification body's lead auditor. It does not test control operation; it tests whether the ISMS documentation is in place and could pass a Stage 2 audit. Prerequisites:

1. **Certification body selection.** Choose an accredited body (e.g., BSI, Schellman, A-LIGN, Coalfire ISO). Estimate 4 to 8 weeks.
2. **ISMS scope document.** A signed scope statement defining what the ISMS covers. Section 2 of this crosswalk is most of this content.
3. **Statement of Applicability.** Formal SoA listing all 93 Annex A controls with disposition (implemented, planned, excluded) and justification. Section 9 of this crosswalk is the draft. Final SoA needs sign-off.
4. **Risk assessment and treatment plan.** RISK_ASSESSMENT.md and POAM_PLAN_OF_ACTION.md cover this; would need to be formalized as the "risk treatment plan" deliverable.
5. **Documented operating procedures for clauses 4 through 10.** Internal audit charter, management review minutes template, ISMS objectives. Several of these are current Gap items.
6. **Internal audit.** At least one full internal audit cycle covering all of Annex A before Stage 2. This is a Gap today.
7. **Management review.** At least one formal management review with documented inputs and outputs per Clause 9.3. This is a Gap today.

### 11.4 ISO 27001 Stage 2 Audit

Stage 2 tests operating effectiveness. The certification body samples evidence and interviews personnel. A typical Stage 2 audit for a small organization runs 3 to 5 audit days on site (or remote equivalent). Findings are categorized as Major Nonconformity, Minor Nonconformity, or Observation. The certificate is issued after all Major Nonconformities are closed and a corrective action plan is in place for Minors.

### 11.5 Estimated Timeline

A realistic timeline assuming work starts now:

| Month | SOC 2 Track | ISO 27001 Track |
|-------|-------------|-----------------|
| 1-2 | Service auditor selection; system description prep; gap remediation | Certification body selection; formal SoA preparation; gap remediation |
| 3-4 | Type I fieldwork | Stage 1 audit |
| 5 | Type I report issuance | Stage 2 preparation; first internal audit cycle |
| 6 | Type II observation period begins | First formal management review |
| 6-7 | Continuous Type II evidence capture | Stage 2 audit |
| 8-9 | Continuous Type II evidence capture | Certificate issuance |
| 12 | Type II fieldwork begins | Surveillance audit prep |
| 14-15 | Type II report issued | First surveillance audit |

This is a six to twelve month window to first formal audit output. A realistic budget assumes auditor fees of US$15,000 to US$40,000 for SOC 2 Type I and US$25,000 to US$60,000 for ISO 27001 Stage 1 plus Stage 2, with annual recurring fees thereafter for Type II and surveillance audits respectively.

### 11.6 Pre-Audit Work Items

Before either auditor engagement begins, several work items need to close:

| Work Item | Current State | Target | Owner |
|-----------|---------------|--------|-------|
| Formal Statement of Applicability | Draft in this crosswalk | Signed SoA artifact | Information Security Officer |
| Vendor security program (CC9.2, A.5.19) | Informal | Documented vendor risk management policy with annual review cadence | Information Security Officer |
| Internal audit function (Clause 9.2, CC4.1) | Not stood up | Internal audit charter; first audit cycle complete | System Owner (designates auditor) |
| Management review (Clause 9.3) | Informal | Quarterly formal management review with minuted inputs and outputs | System Owner |
| Evidence collection automation | Manual or semi-manual | Automated evidence pipeline writing to evidence repository | Information Security Officer |
| Vendor BAA / DPA roundup | Informal | Cataloged DPAs and SOC 2 reports for all material vendors | Information Security Officer |
| Top-level Information Security Policy | Implied by library | Single signed policy document | System Owner |
| ISMS scope and objectives statement | Implied by SSP | Single signed scope statement | System Owner |

---

## 12. Open Gaps (Honest Inventory)

This section is the honest version of "what would an auditor flag." Items here are the difference between current state and a clean Type I or Stage 1 opinion.

### 12.1 No Formal Statement of Applicability

The SoA in Section 9 is a draft for planning purposes. A real SoA is a signed and dated artifact that lives outside the crosswalk and that the certification body would mark up during Stage 1. Action: produce signed SoA as a standalone artifact before scheduling Stage 1.

### 12.2 No External Auditor Selected

No service auditor for SOC 2 and no certification body for ISO 27001 have been selected. Without an engagement, neither audit track can begin. Action: shortlist 3 to 5 candidates per track, request proposals, and select within 90 days of intent to pursue formal audit.

### 12.3 Evidence Collection Partly Manual

Evidence for several criteria (for example, quarterly POA&M review minutes, monthly access review attestations) is currently collected manually or implied by repo activity. A Type II observation period requires reliable, repeatable evidence capture across the period. Action: build evidence collection automation that writes timestamped artifacts to a controlled evidence repository.

### 12.4 Vendor Management Program (CC9.2, A.5.19) Needs Formalization

Vendor risk is acknowledged informally and the AI supply chain register exists, but there is no signed Vendor Risk Management Policy with documented vendor onboarding, annual review, and offboarding procedures. CC9.2 is the one SOC 2 Common Criterion currently marked Gap. Action: write Vendor Risk Management Policy; build vendor inventory with risk tier and review cadence per vendor.

### 12.5 Internal Audit Function (Clause 9.2, CC4.1) Not Yet Stood Up

ISO Clause 9.2 requires an internal audit program with documented audit plan, qualified auditors, and audit reports. CC4.1 requires "separate evaluations" beyond ongoing monitoring. Action: draft Internal Audit Charter; identify qualified internal auditor (third-party contractor or trained internal resource); execute first audit cycle covering at least one third of the ISMS scope.

### 12.6 Management Review (Clause 9.3) Not Formally Cadenced

ISO Clause 9.3 requires a management review with specified inputs (audit results, customer feedback, risk treatment status, opportunities for improvement) and specified outputs (decisions on continual improvement, resource needs). The Organization conducts informal reviews but does not produce minuted management review documents. Action: schedule quarterly management reviews; build review template that captures all Clause 9.3 inputs and outputs; chair would be System Owner.

### 12.7 Additional Smaller Gaps

- **Clause 4.2 Interested parties:** No documented register of interested parties (customers, regulators, model providers, etc.). Easy fix; needed for Stage 1.
- **A.5.31 Legal and regulatory register:** No formal register of applicable laws and regulations. Easy fix; needed for Stage 1.
- **Top-level Information Security Policy:** Implied by the policy library but no single signed top-level document. Easy fix; one-page policy referencing the library.
- **ISMS scope and objectives:** Implied by SSP but not signed as standalone scope statement. Easy fix.
- **Separation of development, test, and production environments (A.8.31):** Single-environment deployment today. Workaround acceptable for current scale; would need either staging environment or feature flag rigor documented to satisfy auditor.

### 12.8 What Is Genuinely Strong

Not every line in this crosswalk is a gap. The substantive control surface is in good shape:

- Logging and audit trail (A.8.15, A.8.16, CC7.2, AU family) covers every service
- Access control (A.5.15 through A.5.18, CC6 family, AC family) is well implemented
- Vulnerability management (A.8.8, CC6.8, RA-5) has automated CI gates and quarterly DAST
- Incident response (A.5.24 through A.5.28, CC7.3 through CC7.5, IR family) has five playbooks and a tabletop
- Change management (A.8.32, CC8.1, CM family) has hard CI gates
- Cryptography (A.8.24, SC-12, SC-13) follows current TLS and at-rest practice

The gaps are around the ISMS scaffolding (management review, internal audit, formal SoA) and around vendor management. Those are formal-document gaps, not substantive control failures.

---

## 13. Cross-References to Other OSOP GRC Documents

### 13.1 Foundational

- `docs/grc/SSP_SYSTEM_SECURITY_PLAN.md` (SSP-OPS-001): NIST 800-53 Rev 5 control implementation across 16 families. Every mapping in this crosswalk anchors to a control documented here.
- `docs/grc/RISK_ASSESSMENT.md`: 17 enterprise risks with likelihood-impact matrix. Source for SOC 2 CC3 and ISO Clause 6.1.2.
- `docs/grc/POAM_PLAN_OF_ACTION.md` (POAM-OPS-001): 25 findings with owner, target date, and disposition. Source for SOC 2 CC4.2 and ISO Clauses 8.3 and 10.2.

### 13.2 Policies

- `docs/grc/POLICY_ACCESS_CONTROL.md`: AC-1 through AC-12. Source for SOC 2 CC6 family and ISO A.5.15 through A.5.18.
- `docs/grc/POLICY_CHANGE_MANAGEMENT.md`: CM-1 through CM-8. Source for SOC 2 CC8.1 and ISO A.8.32.
- `docs/grc/POLICY_VULNERABILITY_MANAGEMENT.md`: RA-5, SI-2, SI-5. Source for SOC 2 CC6.8 and ISO A.8.8.
- `docs/grc/POLICY_INCIDENT_RESPONSE.md`: IR-1 through IR-8. Source for SOC 2 CC7.3 through CC7.5 and ISO A.5.24 through A.5.28.
- `docs/grc/POLICY_BUSINESS_CONTINUITY.md`: CP-1 through CP-10. Source for SOC 2 A1 category and ISO A.5.29, A.5.30.
- `docs/grc/POLICY_DISASTER_RECOVERY.md`: CP-2, 4, 6, 7, 9, 10. Source for SOC 2 A1.2, A1.3 and ISO A.8.13, A.8.14.
- `docs/grc/POLICY_RISK_MANAGEMENT.md`: RA-1, RA-2, RA-3, PM-9. Source for SOC 2 CC3 and ISO Clause 6.
- `docs/grc/POLICY_ACCEPTABLE_USE.md`: PL-4, AT-2. Source for ISO A.5.10 and A.6 family.
- `docs/grc/POLICY_SECURITY_AWARENESS.md`: AT-1 through AT-4. Source for SOC 2 CC1.4 and ISO A.6.3.
- `docs/grc/POLICY_AI_GOVERNANCE.md` (POL-AI-001): ISO 42001, ISO 27701, NIST AI RMF. Source for AI-specific controls touched in A.5.34 and supporting Squire mapping.

### 13.3 IAM

- `docs/grc/IAM_RBAC_ROLE_MAP.md`: Three-tier role structure. Source for SOC 2 CC1.3, CC6.1 and ISO A.5.2, A.5.3, A.5.16, A.5.18.
- `docs/grc/IAM_ACCESS_REVIEW.md`: Access review process and JIT workflow. Source for SOC 2 CC6.2, CC6.3 and ISO A.8.2.
- `docs/grc/GOOGLE_CLOUD_IAM_ASSESSMENT.md`: OAuth 2.0 lifecycle and federated identity. Supporting evidence for A.5.16, A.8.5.

### 13.4 Threat Modeling and AppSec

- `docs/grc/DATA_FLOW_DIAGRAM.md`: 40 data flows across 10 trust boundaries. Source for A.8.20, A.8.22, A.5.14.
- `docs/grc/THREAT_MODEL_STRIDE.md`: 29 STRIDE threats. Supporting evidence for risk assessment.
- `docs/grc/SECURE_SDLC.md`: 12 security gates in CI/CD. Source for SOC 2 CC8.1 and ISO A.8.25 through A.8.29.
- `docs/grc/CODE_REVIEW_FINDINGS.md`: 5 security findings (1 HIGH remediated, 3 MEDIUM accepted, 1 LOW accepted). Source for A.8.28.
- `docs/grc/DAST_METHODOLOGY.md`: OWASP ZAP scan results. Source for A.8.29.
- `docs/grc/PENTEST_SELF_ASSESSMENT.md`: External, application, and infrastructure testing. Source for A.8.29.
- `docs/grc/VULN_WRITEUP_N8N_CREDENTIAL_EXPOSURE.md`: SOAR credential exposure vulnerability writeup. Demonstrates A.8.8 in practice.

### 13.5 Incident Response Playbooks

- `docs/grc/PLAYBOOK_COMPROMISED_CONTAINER.md`: Source for A.5.26, CC7.4.
- `docs/grc/PLAYBOOK_LEAKED_CREDENTIAL.md`: Source for A.5.26, CC7.4.
- `docs/grc/PLAYBOOK_DDOS_SERVICE_DEGRADATION.md`: Source for A.5.26, CC7.4.
- `docs/grc/PLAYBOOK_UNAUTHORIZED_ACCESS.md`: Source for A.5.26, CC7.4.
- `docs/grc/PLAYBOOK_AI_INCIDENT.md`: Source for A.5.26, CC7.4 (AI-specific).
- `docs/grc/TABLETOP_EXERCISE.md`: Source for A.5.27, CC7.5.

### 13.6 Squire (Phase 17)

- `docs/grc/FRAMEWORK_CROSSWALK_SQUIRE.md` (CW-SQUIRE-001): Companion crosswalk for the Squire subsystem covering NIST 800-53, CSF 2.0, MITRE ATT&CK, CSA Agentic MANAGE, OWASP LLM 2025, NIST 800-61 r3, and NIST AI RMF. Several rows in the present crosswalk reference Squire controls.
- `docs/grc/SQUIRE_SSP.md`: Squire-scoped SSP. Supporting evidence for AI-specific controls in A.5.34, A.8.11, A.8.12.
- `docs/grc/AI_AUDIT_TRAIL_SPEC.md`: AI audit trail. Source for A.5.28, A.8.15.

### 13.7 Executive Summaries

- `docs/grc/EXECUTIVE_SUMMARY_SECURITY_POSTURE.md`: Posture overview.
- `docs/grc/EXECUTIVE_SUMMARY_ARCHITECTURE.md`: Architecture and trust zones. Supporting evidence for A.5.23, A.8.20, A.8.27.
- `docs/grc/EXECUTIVE_SUMMARY_COMPLIANCE.md`: Compliance readiness one-pager. Companion to this crosswalk.

---

## 14. Document Control Summary

| Field | Value |
|-------|-------|
| Document ID | CW-002 |
| Version | 1.1 |
| Status | Approved (internal) |
| Audit Status | Not audited; self-attested readiness |
| SOC 2 Engagement | None engaged |
| ISO 27001 Engagement | None engaged |
| Next Review | 2026-08-25 |
| Review Cadence | Quarterly until first formal audit; semi-annual thereafter |
| Author | Information Security Officer |
| Approver | System Owner |

This crosswalk demonstrates that OSOP's existing NIST 800-53 Rev 5 baseline covers the substantive controls of both SOC 2 (Security, Availability, Confidentiality) and ISO/IEC 27001:2022. It does not constitute an attestation, certification, or independent opinion. The path to either output is documented in Section 11 and the work items in Section 12.

The resume claim that OSOP's control set covers SOC 2 and ISO 27001 frameworks is true in the crosswalk sense (controls map cleanly to both) and false in the certification sense (no Type I, Type II, or certificate exists). This document is the artifact that supports the former claim and the honest accounting of what would be needed for the latter.
