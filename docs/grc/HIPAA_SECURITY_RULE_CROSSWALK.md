---
document_id: HIPAA-001
title: HIPAA Security Rule Crosswalk
doc_type: crosswalk
classification: CUI-INTERNAL
version: "1.0"
status: Approved
last_updated: 2026-05-25
next_review: 2026-11-25
owner: Information Security Officer
approver: System Owner (Authorizing Official)
frameworks:
  - HIPAA Security Rule (45 CFR Part 164, Subpart C)
  - HIPAA Breach Notification Rule (45 CFR Part 164, Subpart D)
  - NIST SP 800-66 Rev 2
  - NIST SP 800-53 Rev 5
related:
  - SSP-OPS-001
  - POL-AC-001
  - POL-IR-001
  - POL-SA-001
  - POL-RM-001
  - POL-BC-001
  - POL-DR-001
  - POL-AU-001
  - POL-CM-001
  - POL-VM-001
  - POAM-OPS-001
---

# HIPAA Security Rule Crosswalk

## Organization Security Operations Platform (OSOP)

**Document Identifier:** HIPAA-001
**Classification:** CONTROLLED UNCLASSIFIED - INTERNAL USE ONLY
**Version:** 1.0
**Status:** Approved
**Effective Date:** 2026-05-25
**Next Scheduled Review:** 2026-11-25
**Prepared By:** Information Security Officer
**Approved By:** System Owner (Authorizing Official)

---

## Document Control

| Field | Value |
|-------|-------|
| Document Title | HIPAA Security Rule Crosswalk |
| Document ID | HIPAA-001 |
| Version | 1.0 |
| Status | Approved |
| Effective Date | 2026-05-25 |
| Last Revised | 2026-05-25 |
| Next Review | 2026-11-25 |
| Author | Information Security Officer |
| Approver | System Owner (Authorizing Official) |
| Distribution | Information Security Officer, System Owner, prospective healthcare customer auditors under NDA |
| Source Authority | 45 CFR Part 164, Subpart C (Security Standards) |
| Implementation Guidance | NIST SP 800-66 Rev 2 (February 2024) |
| Control Baseline | NIST SP 800-53 Rev 5 Moderate (per SSP-OPS-001) |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-05-25 | Information Security Officer | Initial crosswalk. Maps every HIPAA Security Rule standard and implementation specification to existing OSOP NIST 800-53 Rev 5 controls. Establishes forward-looking compliance posture for healthcare customer onboarding. Identifies six (6) gaps requiring remediation prior to first Business Associate Agreement signing. |

---

## 1. Purpose

This crosswalk documents the Organization Security Operations Platform (OSOP) readiness against the HIPAA Security Rule (45 CFR Part 164, Subpart C). Each Administrative, Physical, and Technical Safeguard standard and implementation specification is mapped to the corresponding NIST SP 800-53 Rev 5 controls already implemented in OSOP and documented in the System Security Plan (SSP-OPS-001).

The Organization is not currently a Covered Entity or a Business Associate. OSOP does not receive, create, maintain, or transmit electronic protected health information (ePHI). This document does not certify compliance. It establishes the readiness posture that supports onboarding a healthcare customer once a Business Associate Agreement (BAA) is in place.

NIST SP 800-66 Rev 2, published February 2024, is the official NIST guidance for HIPAA Security Rule implementation. This crosswalk follows the methodology in NIST SP 800-66 Rev 2 Section 5, which maps each implementation specification to corresponding controls in NIST SP 800-53 Rev 5.

The audience for this document includes:

- The System Owner and Information Security Officer, for internal readiness tracking
- Prospective healthcare customers conducting vendor due diligence under NDA
- Healthcare-sector recruiters and hiring managers reviewing OSOP as a portfolio artifact
- Internal contributors who need a single source of truth for HIPAA control mapping

---

## 2. Scope

### 2.1 In Scope

This crosswalk covers the entire OSOP authorization boundary as defined in SSP-OPS-001 Section 1.2:

- One (1) cloud-hosted virtual private server running Ubuntu 24.04 LTS
- All containerized services within the Docker Compose stack
- One (1) standalone AI gateway container
- All Terraform-managed cloud resources
- CI/CD pipelines within the infrastructure-as-code repository
- The secrets management pipeline

### 2.2 Out of Scope

The following are outside the scope of this crosswalk:

- DigitalOcean physical infrastructure, hypervisor, and network backbone (inherited controls; subject to DigitalOcean BAA if applicable in the future)
- End-user workstations used to administer the system
- Third-party container registries from which base images are pulled
- Customer-side endpoints and customer-managed ePHI repositories
- Paper or hardcopy records (OSOP does not process physical media containing ePHI)

### 2.3 Regulatory Status Declaration

| Field | Value |
|-------|-------|
| Is the Organization a Covered Entity under HIPAA? | No |
| Is the Organization currently a Business Associate? | No |
| Does OSOP currently process, store, or transmit ePHI? | No |
| Has any BAA been executed by the Organization? | No |
| Has a healthcare customer been onboarded? | No |

OSOP is a security operations platform built as a portfolio artifact and a working production environment for the Organization's own security workloads. Until a healthcare customer signs a BAA and ePHI flows are established, the HIPAA Security Rule does not directly bind OSOP. This crosswalk establishes the readiness posture so that onboarding a healthcare customer becomes a configuration change plus a small set of documented additions, not a foundational architecture rebuild.

---

## 3. Applicability Conditions

The HIPAA Security Rule applies to OSOP only when one of the following conditions is met. Each condition is described with the triggering event, the entity relationship, and the date from which Security Rule obligations begin.

### 3.1 Business Associate by BAA Execution

| Condition | Detail |
|-----------|--------|
| Trigger | The Organization executes a written BAA with a Covered Entity or another Business Associate |
| Effective Date | The BAA effective date, regardless of whether ePHI has been transmitted |
| Obligations Begin | All Security Rule standards become binding on the BAA effective date per 45 CFR 164.314(a)(2) |
| Required Actions | Customer onboarding workflow (Section 13) executes within ten (10) business days of BAA execution |

### 3.2 Subcontractor of a Business Associate

| Condition | Detail |
|-----------|--------|
| Trigger | A Business Associate that the Organization serves engages the Organization to handle ePHI on its behalf |
| Effective Date | The downstream BAA effective date |
| Obligations Begin | Same as Section 3.1 |
| Required Actions | Same as Section 3.1, with documentation of the upstream BAA chain |

### 3.3 Customer Scenarios That Trigger ePHI Flow

| Customer Type | Trigger Action | Resulting ePHI Flow |
|---------------|---------------|---------------------|
| Healthcare provider (covered entity) | Ingests Falco runtime alerts from a workload that handles patient records | ePHI may appear inside alert payloads (filenames, process arguments, error messages) routed through `svc-automation` |
| Health insurer (covered entity) | Uses OSOP SOAR playbooks against systems that process claims data | ePHI in claims documents may appear in syscall arguments, file path strings, or HTTP request bodies captured by detection events |
| Health information exchange (covered entity) | Ships transcription jobs through `svc-transcription` for clinical voice recordings | Voice audio and transcripts contain ePHI by design |
| Healthcare SaaS vendor (business associate) | Routes their detection telemetry through OSOP for SOC-as-a-service | ePHI appears in customer alert payloads, log lines, and any retained query strings |
| Health analytics vendor (business associate) | Uses the OSOP AI gateway to summarize incident timelines that reference patient identifiers | ePHI appears in prompt text sent to the external AI provider |

Each scenario above changes the data flow classification documented in `SQUIRE_DATA_FLOW_CLASSIFICATION.md` from operational and security-only data to data that includes ePHI. The data classification update is the trigger for the customer onboarding workflow in Section 13.

---

## 4. HIPAA Security Rule Structure Overview

The HIPAA Security Rule is codified at 45 CFR Part 164, Subpart C. Including the Organizational Requirements at 164.314 and the Policies, Procedures, and Documentation Requirements at 164.316, the Rule contains a total of twenty-two (22) standards and forty-six (46) implementation specifications across five sections. Implementation specifications are labeled either Required or Addressable. Required specifications must be implemented as written. Addressable specifications must be implemented if reasonable and appropriate. If a Covered Entity or Business Associate determines that an Addressable specification is not reasonable and appropriate, the entity must document why and implement an equivalent alternative that meets the standard.

| Safeguard Category | 45 CFR Section | Standards | Implementation Specifications |
|--------------------|---------------|-----------|------------------------------|
| Administrative Safeguards | 164.308 | 9 | 21 (8 Required, 13 Addressable) |
| Physical Safeguards | 164.310 | 4 | 10 (4 Required, 6 Addressable) |
| Technical Safeguards | 164.312 | 5 | 9 (4 Required, 5 Addressable) |
| Organizational Requirements | 164.314 | 2 | 4 (4 Required) |
| Policies and Procedures, Documentation | 164.316 | 2 | 2 (1 Required, 1 Addressable) |

This crosswalk follows the order above. Each subsection identifies the standard, lists each implementation specification with its Required or Addressable status, maps to the OSOP implementation, and cites the NIST SP 800-53 Rev 5 controls already documented in SSP-OPS-001.

---

## 5. Administrative Safeguards Crosswalk (45 CFR 164.308)

### 5.1 Security Management Process (45 CFR 164.308(a)(1))

**Standard.** Implement policies and procedures to prevent, detect, contain, and correct security violations.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Risk Analysis | Required | 164.308(a)(1)(ii)(A) | Risk Assessment (RA-2026-001) covers 17 enterprise threats plus 10 Squire-specific AI risks using a 5x5 semi-quantitative matrix per NIST 800-30 Rev 1. Reviewed quarterly per [POLICY_RISK_MANAGEMENT.md](POLICY_RISK_MANAGEMENT.md). <!-- TODO(et): verify the "17 enterprise + 10 Squire-specific" counts against the current RISK_ASSESSMENT.md; update if drifted. --> | RA-1, RA-3, RA-3(1) |
| Risk Management | Required | 164.308(a)(1)(ii)(B) | Risk treatment tracked in the Plan of Action and Milestones (POAM-OPS-001). Thirty entries across CIS Docker Bench, Checkov IaC, Falco runtime, and Phase 17 Squire cluster. Treatment decisions recorded per [POLICY_RISK_MANAGEMENT.md](POLICY_RISK_MANAGEMENT.md) Section 6. | RA-1, RA-3, PM-9, PM-28 |
| Sanction Policy | Required | 164.308(a)(1)(ii)(C) | Acceptable use violations and disciplinary actions are documented in [POLICY_ACCEPTABLE_USE.md](POLICY_ACCEPTABLE_USE.md) Section 6 (Enforcement). Workforce sanction tied to HR process. **Gap:** Standalone sanction policy not yet drafted (see Section 12, Gap G-04). | PS-8, PL-4 |
| Information System Activity Review | Required | 164.308(a)(1)(ii)(D) | Continuous monitoring per [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) Section 6. Audit log review cadence in [POLICY_INCIDENT_RESPONSE.md](POLICY_INCIDENT_RESPONSE.md). Falco runtime events shipped to Datadog. Session recordings via `svc-gateway`. Quarterly audit log sampling. | AU-2, AU-6, AU-6(1), AU-12, CA-7, SI-4 |

### 5.2 Assigned Security Responsibility (45 CFR 164.308(a)(2))

**Standard.** Identify the security official who is responsible for the development and implementation of the policies and procedures required by this subpart.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Identify Security Official | Required | 164.308(a)(2) | The Information Security Officer is named in every GRC policy as the security official. Role responsibilities are documented in [POLICY_AI_GOVERNANCE.md](POLICY_AI_GOVERNANCE.md) Section 5.1, [POLICY_ACCESS_CONTROL.md](POLICY_ACCESS_CONTROL.md), and [POLICY_INCIDENT_RESPONSE.md](POLICY_INCIDENT_RESPONSE.md). In a single-operator environment, the System Owner also holds the Information Security Officer responsibilities. Compensating controls per [POLICY_AI_GOVERNANCE.md](POLICY_AI_GOVERNANCE.md) Section 5.2. | PM-2, PM-3 |

### 5.3 Workforce Security (45 CFR 164.308(a)(3))

**Standard.** Implement policies and procedures to ensure that all members of the workforce have appropriate access to ePHI and to prevent those who do not have access from obtaining it.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Authorization and Supervision | Addressable | 164.308(a)(3)(ii)(A) | Three-tier RBAC role map in [IAM_RBAC_ROLE_MAP.md](IAM_RBAC_ROLE_MAP.md). `svc-gateway` enforces just-in-time elevation with session recording. Access requests reviewed by the Information Security Officer. | AC-2, AC-3, AC-5, AC-6, PS-2, PS-3 |
| Workforce Clearance Procedure | Addressable | 164.308(a)(3)(ii)(B) | Background screening for personnel with access to administrative interfaces. Single-operator scope today; multi-person scaling triggers [POLICY_ACCESS_CONTROL.md](POLICY_ACCESS_CONTROL.md) Section on screening. | PS-2, PS-3 |
| Termination Procedures | Addressable | 164.308(a)(3)(ii)(C) | Access revocation via `svc-gateway` role removal, Doppler service token revocation, SSH key removal from `alpha-node`. Procedure documented in [POLICY_ACCESS_CONTROL.md](POLICY_ACCESS_CONTROL.md). Quarterly access review per [IAM_ACCESS_REVIEW.md](IAM_ACCESS_REVIEW.md). | PS-4, PS-5, AC-2(13) |

### 5.4 Information Access Management (45 CFR 164.308(a)(4))

**Standard.** Implement policies and procedures for authorizing access to ePHI that are consistent with the applicable requirements of subpart E.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Isolating Health Care Clearinghouse Functions | Required | 164.308(a)(4)(ii)(A) | Not applicable. OSOP is not a health care clearinghouse. If OSOP were to onboard a clearinghouse customer, container-level network segmentation (`net-core`, `net-ai`, `net-monitoring` per [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) Section 2.1) would isolate the clearinghouse function from other workloads. | AC-4, SC-7, SC-7(5) |
| Access Authorization | Addressable | 164.308(a)(4)(ii)(B) | Access decisions tied to RBAC roles in [IAM_RBAC_ROLE_MAP.md](IAM_RBAC_ROLE_MAP.md). Minimum necessary principle enforced at role design time. All ePHI flows would be restricted to a dedicated role with documented justification. | AC-2, AC-3, AC-6, AC-6(7) |
| Access Establishment and Modification | Addressable | 164.308(a)(4)(ii)(C) | Access changes follow [POLICY_CHANGE_MANAGEMENT.md](POLICY_CHANGE_MANAGEMENT.md). Quarterly access review per [IAM_ACCESS_REVIEW.md](IAM_ACCESS_REVIEW.md). All access modifications logged via `svc-gateway` and shipped to Datadog. | AC-2, AC-2(3), AC-2(4) |

### 5.5 Security Awareness and Training (45 CFR 164.308(a)(5))

**Standard.** Implement a security awareness and training program for all members of the workforce (including management).

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Security Reminders | Addressable | 164.308(a)(5)(ii)(A) | Monthly security reminders per [POLICY_SECURITY_AWARENESS.md](POLICY_SECURITY_AWARENESS.md). Reminders include phishing examples, credential hygiene, and any recently observed threats. | AT-2, AT-2(1), AT-2(2) |
| Protection from Malicious Software | Addressable | 164.308(a)(5)(ii)(B) | Trivy CVE scanning on all container images. Cosign signature verification before deployment. Falco runtime detection for malicious behavior. Endpoint protection on administrative workstations. | SI-3, SI-2, SI-7 |
| Log-in Monitoring | Addressable | 164.308(a)(5)(ii)(C) | Authentication failures logged via `svc-gateway` and shipped to Datadog. Failed login thresholds trigger alerts per [POLICY_INCIDENT_RESPONSE.md](POLICY_INCIDENT_RESPONSE.md). | AC-7, AU-2, AU-6, IA-2 |
| Password Management | Addressable | 164.308(a)(5)(ii)(D) | Doppler-managed secrets with quarterly rotation. TOTP for human authentication to `svc-gateway`. Password complexity per [POLICY_ACCESS_CONTROL.md](POLICY_ACCESS_CONTROL.md). | IA-5, IA-5(1), IA-5(2) |

### 5.6 Security Incident Procedures (45 CFR 164.308(a)(6))

**Standard.** Implement policies and procedures to address security incidents.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Response and Reporting | Required | 164.308(a)(6)(ii) | Full incident response program per [POLICY_INCIDENT_RESPONSE.md](POLICY_INCIDENT_RESPONSE.md). Five (5) playbooks: [PLAYBOOK_COMPROMISED_CONTAINER.md](PLAYBOOK_COMPROMISED_CONTAINER.md), [PLAYBOOK_LEAKED_CREDENTIAL.md](PLAYBOOK_LEAKED_CREDENTIAL.md), [PLAYBOOK_DDOS_SERVICE_DEGRADATION.md](PLAYBOOK_DDOS_SERVICE_DEGRADATION.md), [PLAYBOOK_UNAUTHORIZED_ACCESS.md](PLAYBOOK_UNAUTHORIZED_ACCESS.md), and [PLAYBOOK_AI_INCIDENT.md](PLAYBOOK_AI_INCIDENT.md). <!-- TODO(et): confirm all 5 playbook files exist at docs/grc/; update list if any have been renamed or consolidated. --> Tabletop exercise documented in [TABLETOP_EXERCISE.md](TABLETOP_EXERCISE.md). Breach Notification Rule alignment in Section 10. | IR-1, IR-4, IR-4(1), IR-5, IR-6, IR-7, IR-8 |

### 5.7 Contingency Plan (45 CFR 164.308(a)(7))

**Standard.** Establish (and implement as needed) policies and procedures for responding to an emergency or other occurrence (for example, fire, vandalism, system failure, and natural disaster) that damages systems that contain ePHI.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Data Backup Plan | Required | 164.308(a)(7)(ii)(A) | Nightly `pg_dump` of all PostgreSQL databases to DigitalOcean Spaces object storage with 14-day retention. Weekly droplet snapshot retained for 4 weeks. Backup procedure per [POLICY_BUSINESS_CONTINUITY.md](POLICY_BUSINESS_CONTINUITY.md). | CP-9, CP-9(1), CP-9(8) |
| Disaster Recovery Plan | Required | 164.308(a)(7)(ii)(B) | Disaster recovery procedures per [POLICY_DISASTER_RECOVERY.md](POLICY_DISASTER_RECOVERY.md). Recovery Time Objective (RTO) and Recovery Point Objective (RPO) defined per service tier. Recovery tested semi-annually. | CP-2, CP-7, CP-10, CP-10(2) |
| Emergency Mode Operation Plan | Required | 164.308(a)(7)(ii)(C) | Degraded operation procedures defined in [POLICY_BUSINESS_CONTINUITY.md](POLICY_BUSINESS_CONTINUITY.md). For AI workloads, the Squire degraded mode fallback to local Ollama inference is documented in [FRAMEWORK_CROSSWALK_SQUIRE.md](FRAMEWORK_CROSSWALK_SQUIRE.md) Row 19. | CP-2, CP-2(3), CP-10 |
| Testing and Revision Procedures | Addressable | 164.308(a)(7)(ii)(D) | Semi-annual recovery test per [POLICY_DISASTER_RECOVERY.md](POLICY_DISASTER_RECOVERY.md). Tabletop exercise per [TABLETOP_EXERCISE.md](TABLETOP_EXERCISE.md). Findings drive plan revisions. | CP-3, CP-4, CP-4(1) |
| Applications and Data Criticality Analysis | Addressable | 164.308(a)(7)(ii)(E) | Service tier classification documented in [POLICY_BUSINESS_CONTINUITY.md](POLICY_BUSINESS_CONTINUITY.md). Tier 1 services (`svc-gateway`, `svc-db`, `svc-tunnel`) have the lowest RTO targets. | CP-2, RA-2 |

### 5.8 Evaluation (45 CFR 164.308(a)(8))

**Standard.** Perform a periodic technical and nontechnical evaluation, based initially upon the standards implemented under this rule and, subsequently, in response to environmental or operational changes affecting the security of ePHI, that establishes the extent to which an entity's security policies and procedures meet the requirements of this subpart.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Periodic Evaluation | Required | 164.308(a)(8) | Continuous monitoring strategy in [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) Section 6. Quarterly POA&M review. Annual policy review. Semi-annual SSP review. DAST scans quarterly per [DAST_METHODOLOGY.md](DAST_METHODOLOGY.md). Annual pen test self-assessment per [PENTEST_SELF_ASSESSMENT.md](PENTEST_SELF_ASSESSMENT.md). When the first BAA is signed, an external HIPAA-focused evaluation will be added to the annual cadence. | CA-2, CA-5, CA-7, CA-7(1), PM-14 |

### 5.9 Business Associate Contracts and Other Arrangements (45 CFR 164.308(b))

**Standard.** A covered entity may permit a business associate to create, receive, maintain, or transmit ePHI on the covered entity's behalf only if the covered entity obtains satisfactory assurances, in accordance with 164.314(a), that the business associate will appropriately safeguard the information.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Written Contract or Other Arrangement | Required | 164.308(b)(3) | **Gap:** BAA template not yet drafted (see Section 12, Gap G-02). When drafted, the BAA template will reference the safeguards documented in this crosswalk and the SSP. Upstream BAAs with DigitalOcean and Anthropic will be evaluated at the time of first customer onboarding. | SA-9, SA-9(2), SR-2, SR-3 |

---

## 6. Physical Safeguards Crosswalk (45 CFR 164.310)

OSOP operates entirely on cloud-hosted virtual infrastructure. The Organization does not own or operate a physical data center. Physical safeguards over the underlying hardware are inherited from DigitalOcean. The cloud provider's SOC 2 Type II report serves as the assurance artifact for inherited physical controls. The crosswalk below documents both the inherited posture and the controls that the Organization owns directly (workstation use, device and media handling on administrator endpoints).

### 6.1 Facility Access Controls (45 CFR 164.310(a)(1))

**Standard.** Implement policies and procedures to limit physical access to its electronic information systems and the facility or facilities in which they are housed, while ensuring that properly authorized access is allowed.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Contingency Operations | Addressable | 164.310(a)(2)(i) | Recovery procedures per [POLICY_DISASTER_RECOVERY.md](POLICY_DISASTER_RECOVERY.md). Inherited from DigitalOcean data center contingency operations. | PE-1, CP-2, CP-7 |
| Facility Security Plan | Addressable | 164.310(a)(2)(ii) | Inherited from DigitalOcean SOC 2 controls. Organization does not own a data center facility. | PE-1, PE-2 |
| Access Control and Validation Procedures | Addressable | 164.310(a)(2)(iii) | Inherited from DigitalOcean. Personnel access to the OSOP cloud account is gated by multi-factor authentication and IP allow-listing. | PE-2, PE-3, AC-2 |
| Maintenance Records | Addressable | 164.310(a)(2)(iv) | Inherited from DigitalOcean for the underlying hardware. Container image maintenance and rebuild events recorded in CI/CD pipeline logs and git history. | PE-1, MA-2, CM-3 |

### 6.2 Workstation Use (45 CFR 164.310(b))

**Standard.** Implement policies and procedures that specify the proper functions to be performed, the manner in which those functions are to be performed, and the physical attributes of the surroundings of a specific workstation or class of workstation that can access ePHI.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Workstation Use Policy | Required | 164.310(b) | Acceptable use of administrator workstations documented in [POLICY_ACCEPTABLE_USE.md](POLICY_ACCEPTABLE_USE.md). Specifies endpoint protection, full disk encryption, screen lock, and prohibited activities. ePHI handling rules will be added to this policy at the time of first BAA signing. | AC-19, AC-20, PL-4 |

### 6.3 Workstation Security (45 CFR 164.310(c))

**Standard.** Implement physical safeguards for all workstations that access ePHI, to restrict access to authorized users.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Workstation Security | Required | 164.310(c) | Administrator workstations require full disk encryption (FileVault on macOS, LUKS on Linux), automatic screen lock after 5 minutes of inactivity, biometric or strong password unlock, and endpoint protection. Documented in [POLICY_ACCEPTABLE_USE.md](POLICY_ACCEPTABLE_USE.md). | AC-19, MP-7, SC-28 |

### 6.4 Device and Media Controls (45 CFR 164.310(d))

**Standard.** Implement policies and procedures that govern the receipt and removal of hardware and electronic media that contain ePHI into and out of a facility, and the movement of these items within the facility.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Disposal | Required | 164.310(d)(2)(i) | DigitalOcean handles physical media disposal per their SOC 2 controls. Droplet destruction triggers cryptographic erasure of the underlying storage. Administrator endpoint disposal follows NIST SP 800-88 Rev 1 media sanitization (cryptographic erase plus a verification overwrite). | MP-6, MP-6(1), MP-6(2) |
| Media Re-use | Required | 164.310(d)(2)(ii) | Cloud storage volume re-use is handled by DigitalOcean. The Organization does not re-use physical media that has held ePHI. | MP-6, MP-6(1) |
| Accountability | Addressable | 164.310(d)(2)(iii) | All OSOP infrastructure assets are tracked in Terraform state. Administrator endpoints are inventoried in a workstation register. **Gap:** Asset disposal log for administrator endpoints is informal; will be formalized at first BAA signing (see Section 12, Gap G-05). | CM-8, MP-4 |
| Data Backup and Storage | Addressable | 164.310(d)(2)(iv) | Backup procedures per [POLICY_BUSINESS_CONTINUITY.md](POLICY_BUSINESS_CONTINUITY.md). Backups encrypted at rest with provider-managed keys. Movement of backups between regions or accounts triggers a change ticket per [POLICY_CHANGE_MANAGEMENT.md](POLICY_CHANGE_MANAGEMENT.md). | CP-9, CP-9(8), SC-28 |

---

## 7. Technical Safeguards Crosswalk (45 CFR 164.312)

### 7.1 Access Control (45 CFR 164.312(a)(1))

**Standard.** Implement technical policies and procedures for electronic information systems that maintain ePHI to allow access only to those persons or software programs that have been granted access rights as specified in 164.308(a)(4).

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Unique User Identification | Required | 164.312(a)(2)(i) | Every human user has a unique account in `svc-gateway` (Teleport identity). No shared accounts. Service-to-service authentication uses dedicated service tokens managed in Doppler. Container processes run as non-root users with unique UIDs per [FRAMEWORK_CROSSWALK_SQUIRE.md](FRAMEWORK_CROSSWALK_SQUIRE.md) Row 21. | IA-2, IA-2(1), IA-2(2), IA-4 |
| Emergency Access Procedure | Required | 164.312(a)(2)(ii) | Break-glass procedure documented in [POLICY_ACCESS_CONTROL.md](POLICY_ACCESS_CONTROL.md). Emergency root SSH key sealed in 1Password under a separate vault entry. Use triggers a notification and a post-incident review. Procedure tested semi-annually. | AC-2(7), AC-6(2), IR-4 |
| Automatic Logoff | Addressable | 164.312(a)(2)(iii) | `svc-gateway` (Teleport) sessions terminate after 8 hours of inactivity. Administrator workstation screen lock activates after 5 minutes per [POLICY_ACCEPTABLE_USE.md](POLICY_ACCEPTABLE_USE.md). Web sessions to `svc-automation` terminate after 30 minutes of inactivity. | AC-11, AC-11(1), AC-12 |
| Encryption and Decryption | Addressable | 164.312(a)(2)(iv) | Current state: DigitalOcean provider-managed AES-256 disk encryption on the block storage backing `alpha-node`. PostgreSQL transparent data encryption is not enabled; field-level encryption via Vault Transit is a Phase 17+ ePHI-readiness item and is not active for non-ePHI workloads today. LUKS on the droplet root volume is not available on DigitalOcean; LUKS on attached volumes is planned for ePHI data paths before any ingest. **Gap:** Dedicated ePHI customer-managed key (CMK) workflow not yet implemented; will be added if a healthcare customer requires CMK (see Section 12, Gap G-01). | SC-13, SC-28, SC-28(1) |

### 7.2 Audit Controls (45 CFR 164.312(b))

**Standard.** Implement hardware, software, and procedural mechanisms that record and examine activity in information systems that contain or use ePHI.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Audit Controls | Required | 164.312(b) | Multi-layer audit architecture per [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) Section 6 and [AI_AUDIT_TRAIL_SPEC.md](AI_AUDIT_TRAIL_SPEC.md). Falco for syscall and runtime events. `svc-gateway` for session recordings. Application logs from all services routed through the log shipper to Datadog. Database query logs for `svc-db`. AI-specific Langfuse traces per [GUARDRAILS_CONFIGURATION.md](GUARDRAILS_CONFIGURATION.md). Cold storage Object Lock retention is 7 years per AI_AUDIT_TRAIL_SPEC Section 4, which exceeds the HIPAA 6-year minimum at 164.316(b)(2)(i). **Gap:** Application log retention currently 90 days online plus 1 year archive; Datadog archive must be extended to 6 years for ePHI-tagged streams. Extended retention plan in Section 12, Gap G-03. | AU-2, AU-3, AU-3(1), AU-6, AU-9, AU-11, AU-12 |

### 7.3 Integrity (45 CFR 164.312(c))

**Standard.** Implement policies and procedures to protect ePHI from improper alteration or destruction.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Mechanism to Authenticate ePHI | Addressable | 164.312(c)(2) | Container image integrity verified via Cosign signatures. SBOMs generated for every container image. Database write integrity protected by PostgreSQL WAL with checksumming enabled. Audit log integrity protected by REVOKE UPDATE/DELETE on log tables per [FRAMEWORK_CROSSWALK_SQUIRE.md](FRAMEWORK_CROSSWALK_SQUIRE.md) Row 30. Backup integrity verified via SHA-256 checksum at backup time and at restore time. | SI-7, SI-7(1), SI-7(5), AU-9, AU-9(2) |

### 7.4 Person or Entity Authentication (45 CFR 164.312(d))

**Standard.** Implement procedures to verify that a person or entity seeking access to ePHI is the one claimed.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Person or Entity Authentication | Required | 164.312(d) | Human authentication: `svc-gateway` (Teleport Community Edition) with TOTP plus password. <!-- TODO(et): verify Teleport `cap` output; if FIDO2 hardware-key MFA is enabled, restore the FIDO2 reference here. As of last verification, only TOTP is configured. --> Service authentication: mutual TLS where supported, service tokens elsewhere, all secrets managed in Doppler with quarterly rotation. API authentication: bearer tokens, HMAC-signed webhook payloads, and IP allow-listing per route. | IA-2, IA-2(1), IA-2(2), IA-2(8), IA-3, IA-5 |

### 7.5 Transmission Security (45 CFR 164.312(e))

**Standard.** Implement technical security measures to guard against unauthorized access to ePHI that is being transmitted over an electronic communications network.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Integrity Controls | Addressable | 164.312(e)(2)(i) | All ingress through `svc-tunnel` (Cloudflare Tunnel) uses TLS 1.3. Internal service-to-service calls use TLS where supported. Webhook payloads are HMAC-signed to detect tampering. Database connections use TLS. | SC-8, SC-8(1), SC-23, SI-7 |
| Encryption | Addressable | 164.312(e)(2)(ii) | TLS 1.3 enforced for all external ingress and egress. Database connections require TLS. AI provider API calls use HTTPS only. Cipher suite hardening verified by `testssl.sh` quarterly per [DAST_METHODOLOGY.md](DAST_METHODOLOGY.md). | SC-8, SC-8(1), SC-12, SC-13 |

---

## 8. Organizational Requirements (45 CFR 164.314)

### 8.1 Business Associate Contracts or Other Arrangements (45 CFR 164.314(a))

**Standard.** The contract or other arrangement between the covered entity and the business associate must comply with the requirements at 164.314(a)(2).

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Business Associate Contracts | Required | 164.314(a)(2)(i) | **Gap:** BAA template not yet drafted (Section 12, Gap G-02). The template will require Business Associates and Subcontractors to: (a) comply with the Security Rule, (b) report security incidents per Section 10, (c) ensure any Subcontractor agrees to the same obligations in writing, (d) make documentation available to the Secretary of HHS upon request, (e) return or destroy ePHI at termination of the arrangement. | SA-9, SA-9(2), SR-2 |
| Other Arrangements | Required | 164.314(a)(2)(ii) | If a customer is a government entity, equivalent arrangements (memoranda of understanding) will be substituted for a traditional BAA. Template will support both forms. | SA-9, PS-7 |
| Subcontractors | Required | 164.314(a)(2)(iii) | OSOP's downstream service providers that would handle ePHI (currently DigitalOcean for infrastructure, Anthropic for AI inference if AI workloads touch ePHI, Cloudflare for transit, Datadog for telemetry) would be evaluated for HIPAA capability. DigitalOcean offers a BAA for eligible customers. Anthropic's Enterprise contract supports BAAs. Cloudflare's BAA is Enterprise-tier only. Datadog's BAA is on the HIPAA-eligible workspace tier. Current Organization accounts with these vendors are on tiers that do not include a BAA today; tier upgrades are documented as a precondition for first BAA signing. At first BAA signing, downstream BAAs will be executed before ePHI flows. | SA-9, SA-9(2), SR-3, SR-3(1) |

### 8.2 Requirements for Group Health Plans (45 CFR 164.314(b))

**Standard.** A group health plan must amend its plan documents to incorporate certain requirements.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Group Health Plan Requirements | Required | 164.314(b)(2) | Not applicable. The Organization is not and does not operate a group health plan. If a customer that is a group health plan onboards, customer-side plan document amendments are the customer's responsibility. The Organization will provide the BAA and the assurances required at 164.314(b)(2)(i)-(iv). | n/a |

---

## 9. Policies and Procedures and Documentation Requirements (45 CFR 164.316)

### 9.1 Policies and Procedures (45 CFR 164.316(a))

**Standard.** Implement reasonable and appropriate policies and procedures to comply with the standards, implementation specifications, or other requirements of this subpart.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Policies and Procedures | Required | 164.316(a) | Ten (10) policies in the GRC library covering risk management, access control, change management, vulnerability management, incident response, business continuity, disaster recovery, acceptable use, security awareness, and AI governance. All policies use the same structure: purpose, scope, framework alignment, requirements, roles, enforcement, related documents. Annual review cadence. | PL-1, PL-2, AC-1, AT-1, AU-1, CM-1, CP-1, IA-1, IR-1, MA-1, MP-1, PE-1, PS-1, RA-1, SA-1, SC-1, SI-1 |

### 9.2 Documentation (45 CFR 164.316(b))

**Standard.** Maintain the policies and procedures implemented to comply with this subpart and, if an action, activity or assessment is required by this subpart to be documented, maintain a written (which may be electronic) record of the action, activity, or assessment.

| Implementation Specification | Status | 45 CFR | OSOP Implementation | NIST 800-53 Controls |
|------------------------------|--------|--------|---------------------|----------------------|
| Time Limit | Required | 164.316(b)(2)(i) | All policy documents are version-controlled in the GRC library with full history retained indefinitely in git. **Gap:** Audit log online retention is shorter than the six-year HIPAA requirement (see Section 12, Gap G-03). Policies, risk assessments, and POA&M records do meet the six-year requirement via git history. | AU-11, SI-12 |
| Availability | Addressable | 164.316(b)(2)(ii) | Policies are available to all personnel with administrative access. The repository is the single source of truth. Policies are also distributed to customers and auditors under NDA upon request. | PL-1, AT-3 |
| Updates | Addressable | 164.316(b)(2)(iii) | Annual policy review cadence documented in each policy. Out-of-cycle updates triggered by material changes (new threats, new regulations, infrastructure changes). All changes recorded in the Revision History table of each document and in git commit history. | PL-1, CM-3, CA-7 |

---

## 10. Breach Notification Rule (45 CFR Part 164, Subpart D)

The Breach Notification Rule is separate from the Security Rule but is closely tied to it. A breach of unsecured ePHI requires notification to affected individuals, to HHS, and in some cases to the media, within specified timeframes. While OSOP does not currently process ePHI, the incident response program is structured to support breach notification obligations from day one of any future BAA.

### 10.1 Breach Notification Workflow Alignment

| Breach Notification Requirement | 45 CFR | OSOP Implementation |
|---------------------------------|--------|---------------------|
| Breach assessment and risk determination | 164.402 | Incident severity assessment per [POLICY_INCIDENT_RESPONSE.md](POLICY_INCIDENT_RESPONSE.md). Risk of compromise evaluation modeled on the four-factor analysis: (1) nature and extent of ePHI involved, (2) unauthorized person who used or received the ePHI, (3) whether ePHI was actually acquired or viewed, (4) extent to which risk has been mitigated. |
| Notification to individuals without unreasonable delay and no later than 60 days | 164.404 | Incident response playbooks include customer and individual notification steps. The 60-day clock starts on the day the breach is discovered or, with reasonable diligence, would have been discovered. OSOP detection latency is monitored to support meeting this timeline. |
| Notification to HHS within 60 days for breaches affecting 500+ individuals (or annual log for breaches affecting fewer than 500) | 164.408 | HHS notification process referenced in incident response. The annual log for sub-500 breaches will be maintained from the date of the first BAA. |
| Notification to media for breaches affecting 500+ individuals in a single state or jurisdiction | 164.406 | Media notification template will be added to [PLAYBOOK_LEAKED_CREDENTIAL.md](PLAYBOOK_LEAKED_CREDENTIAL.md) at first BAA signing. |
| Documentation of all breach assessments and notifications | 164.414 | All incident records retained per the policy retention schedule. Documentation includes breach assessment, notification timeline, notification content, and recipient list. |

### 10.2 Mapping to OSOP Incident Response Playbooks

| Breach Scenario | Applicable Playbook |
|-----------------|---------------------|
| ePHI exfiltration via compromised container | [PLAYBOOK_COMPROMISED_CONTAINER.md](PLAYBOOK_COMPROMISED_CONTAINER.md) |
| ePHI exposure via leaked credential or token | [PLAYBOOK_LEAKED_CREDENTIAL.md](PLAYBOOK_LEAKED_CREDENTIAL.md) |
| Unauthorized access to systems containing ePHI | [PLAYBOOK_UNAUTHORIZED_ACCESS.md](PLAYBOOK_UNAUTHORIZED_ACCESS.md) |
| AI system disclosure of ePHI via prompt injection or hallucination | [PLAYBOOK_AI_INCIDENT.md](PLAYBOOK_AI_INCIDENT.md) |
| ePHI loss due to ransomware or destructive attack | [PLAYBOOK_COMPROMISED_CONTAINER.md](PLAYBOOK_COMPROMISED_CONTAINER.md) plus [POLICY_DISASTER_RECOVERY.md](POLICY_DISASTER_RECOVERY.md) |

---

## 11. Implementation Maturity Assessment

The following table scores each safeguard category against the four maturity levels defined for this assessment. Scoring is based on the controls cited in this crosswalk and the evidence available in the GRC library.

### 11.1 Maturity Levels

| Level | Definition |
|-------|------------|
| Implemented | All standards and required implementation specifications are in place. Addressable specifications are either implemented or have a documented alternative. Evidence exists in the GRC library. |
| Partial | Most controls are in place but at least one Required specification needs additional documentation or operational maturity. |
| Not Applicable | The standard does not apply to OSOP given current scope (for example, clearinghouse isolation since OSOP is not a clearinghouse). |
| Gap | A Required specification is missing or substantively incomplete. Tracked in Section 14. |

### 11.2 Per-Category Score

| Safeguard Category | Score | Notes |
|--------------------|-------|-------|
| Administrative Safeguards (164.308) | Partial | 8 of 9 standards Implemented. Gap on sanction policy formalization (G-04). BAA template (G-02) classified separately under Organizational Requirements but contributes to overall Administrative maturity. |
| Physical Safeguards (164.310) | Implemented | Inherited from DigitalOcean for facility-level controls. Workstation and device controls implemented. One minor gap on asset disposal log formalization (G-05). |
| Technical Safeguards (164.312) | Partial | Access Control, Audit Controls, Authentication, and Transmission Security all Implemented. Audit log retention gap (G-03). Customer-managed key option not yet implemented (G-01). |
| Organizational Requirements (164.314) | Gap | BAA template missing (G-02). |
| Policies and Procedures (164.316) | Partial | Policies and Availability and Updates all Implemented. Time Limit retention gap on audit logs (G-03). |
| Breach Notification (164 Subpart D) | Partial | Incident response program supports breach notification workflow. Media notification template and HHS annual log will be added at first BAA signing. |

### 11.3 Overall Readiness

OSOP can support a healthcare customer BAA signing once the six gaps in Section 14 are closed. Estimated effort: approximately 80 hours of dedicated work across documentation, configuration, and process formalization. Five of the six gaps are documentation-only. One gap (audit log retention extension) requires storage configuration and budget review.

---

## 12. Gaps and Remediation Plan

The following gaps were identified during the readiness assessment. Each gap has an owner, a target close date, and a remediation approach. Gaps are tracked in the Plan of Action and Milestones (POAM-OPS-001) as separate entries beginning with the prefix HIPAA-G-.

| Gap ID | Description | HIPAA Reference | NIST 800-53 | Severity | Target Close | Owner |
|--------|-------------|-----------------|-------------|----------|--------------|-------|
| G-01 | Customer-managed encryption key (CMK) workflow not implemented. Cloud provider key encryption is in place but a customer that requires its own KMS hold cannot be onboarded today. | 164.312(a)(2)(iv) | SC-12, SC-13, SC-28(1) | Medium | 2026-09-25 | Information Security Officer |
| G-02 | BAA template not yet drafted. No template exists to extend to a prospective Covered Entity customer or downstream Subcontractor. | 164.308(b)(3), 164.314(a)(2) | SA-9, SR-2 | High | 2026-07-25 | Information Security Officer |
| G-03 | Audit log retention online plus archive does not meet the 6-year HIPAA documentation retention requirement. Application logs retained 15 days online plus 1 year archive. Policy documents do meet 6 years via git. | 164.312(b), 164.316(b)(2)(i) | AU-11, SI-12 | High | 2026-08-25 | Information Security Officer |
| G-04 | Sanction policy not formalized as a standalone document. Disciplinary consequences are referenced inside the Acceptable Use Policy but a discrete sanction policy with offense classification and corrective actions is missing. | 164.308(a)(1)(ii)(C) | PS-8, PL-4 | Medium | 2026-08-25 | Information Security Officer |
| G-05 | Workstation asset disposal log is informal. Disposal events are tracked in personal notes but not in a structured register that an auditor could review at year-end. | 164.310(d)(2)(iii) | MP-4, CM-8 | Low | 2026-09-25 | Information Security Officer |
| G-06 | ePHI data classification framework not defined. The existing data classification in [SQUIRE_DATA_FLOW_CLASSIFICATION.md](SQUIRE_DATA_FLOW_CLASSIFICATION.md) covers operational and security data classes. An ePHI class with handling rules has not been added because no ePHI flow exists today. | 164.308(a)(4)(ii)(B), 164.312(b) | AC-6(7), AC-21, SI-19 | Medium | 2026-08-25 | Information Security Officer |

### 12.1 Remediation Approach by Gap

**G-01 (CMK workflow).** Evaluate DigitalOcean customer-managed key options and AWS KMS bring-your-own-key. If DigitalOcean cannot meet a customer's CMK requirement, document a clear architecture for routing ePHI workloads to a cloud region that does. Estimated effort: 20 hours including documentation, testing, and key rotation drill.

**G-02 (BAA template).** Draft BAA template based on the HHS sample BAA provisions at https://www.hhs.gov/hipaa/for-professionals/covered-entities/sample-business-associate-agreement-provisions/index.html. Engage legal review at first signing event. Estimated effort: 12 hours including drafting, internal review, and legal review intake.

**G-03 (audit log retention).** Extend Datadog archive retention from 1 year to 6 years for HIPAA-tagged log streams. Cost impact estimated at $40 per month per healthcare customer based on current log volume. Alternative: shift older logs to object storage with retrieval contract. Estimated effort: 16 hours including configuration, cost modeling, and procedure documentation.

**G-04 (sanction policy).** Draft a discrete Sanction Policy covering offense classification (negligent, willful, malicious), corrective actions (warning, suspension, termination), documentation requirements, and notification. Cross-reference from POLICY_ACCEPTABLE_USE.md. Estimated effort: 8 hours.

**G-05 (asset disposal log).** Stand up a simple structured register (spreadsheet or markdown table in the GRC library) covering asset ID, model, acquisition date, disposal date, disposal method, and witness. Backfill from existing records. Estimated effort: 4 hours.

**G-06 (ePHI data classification).** Add an ePHI class to the data classification framework with handling rules covering encryption at rest, encryption in transit, access control, audit log mandate, retention, sanitization before any export. Estimated effort: 12 hours.

Total estimated remediation effort: 72 hours. Buffer for legal review and unexpected dependencies brings the budgeted effort to approximately 80 hours.

---

## 13. Customer Onboarding Workflow

This section describes what would happen if a healthcare customer signs a BAA tomorrow. The workflow is designed so that the first BAA can be executed with confidence that the Security Rule obligations can be met within the legally required timeframes.

### 13.1 Pre-Signing Activities

Performed before any BAA is signed. These steps surface blocking issues early.

| # | Activity | Owner | Duration |
|---|----------|-------|----------|
| 1 | Customer security questionnaire review | Information Security Officer | 4 hours |
| 2 | Scope confirmation (which OSOP services will touch ePHI; volume estimate) | Information Security Officer | 2 hours |
| 3 | Gap assessment against this crosswalk for the customer's specific scope | Information Security Officer | 4 hours |
| 4 | Confirm downstream BAA availability with DigitalOcean and Anthropic (if AI workloads will touch ePHI) | Information Security Officer | 4 hours |
| 5 | Pricing model that accounts for incremental compliance cost (extended log retention, additional review cadence) | System Owner | 2 hours |
| 6 | Legal review of customer BAA terms vs. OSOP template | Outside counsel | varies |

### 13.2 Day-Of Signing Activities

| # | Activity | Owner | Duration |
|---|----------|-------|----------|
| 1 | Execute BAA | System Owner | n/a |
| 2 | Record BAA effective date and key terms in the customer register | Information Security Officer | 1 hour |
| 3 | Begin the 10-business-day technical onboarding clock | Information Security Officer | n/a |

### 13.3 Within 10 Business Days of BAA Signing

| # | Activity | Owner | Duration |
|---|----------|-------|----------|
| 1 | Update [SQUIRE_DATA_FLOW_CLASSIFICATION.md](SQUIRE_DATA_FLOW_CLASSIFICATION.md) to add the new ePHI data flow | Information Security Officer | 2 hours |
| 2 | Tag all log streams that touch the customer's data with `hipaa=true` for extended retention | System Owner | 2 hours |
| 3 | Provision a dedicated RBAC role per [IAM_RBAC_ROLE_MAP.md](IAM_RBAC_ROLE_MAP.md) with the minimum necessary access | Information Security Officer | 2 hours |
| 4 | Update [POLICY_ACCEPTABLE_USE.md](POLICY_ACCEPTABLE_USE.md) to add ePHI handling rules for administrators | Information Security Officer | 2 hours |
| 5 | Execute downstream BAAs with DigitalOcean and Anthropic if not already executed | System Owner | 4 hours |
| 6 | Run an end-to-end test with synthetic ePHI to validate access controls, audit logging, and encryption | Information Security Officer | 4 hours |
| 7 | Update the AI System Inventory in [POLICY_AI_GOVERNANCE.md](POLICY_AI_GOVERNANCE.md) Section 4 if AI workloads will touch ePHI | Information Security Officer | 2 hours |
| 8 | Customer-facing security documentation pack delivered (this crosswalk, SSP, applicable policies) | Information Security Officer | 2 hours |

### 13.4 Within 30 Days of BAA Signing

| # | Activity | Owner | Duration |
|---|----------|-------|----------|
| 1 | First quarterly access review covering the new role | Information Security Officer | 4 hours |
| 2 | Tabletop exercise focused on ePHI breach scenario | Information Security Officer | 6 hours |
| 3 | Update the Risk Assessment to add ePHI-specific threat scenarios | Information Security Officer | 4 hours |
| 4 | Schedule the first annual external HIPAA evaluation | System Owner | 1 hour |

### 13.5 Ongoing Activities

| # | Activity | Cadence |
|---|----------|---------|
| 1 | ePHI access audit log review | Monthly |
| 2 | Risk Assessment update for ePHI scope | Quarterly |
| 3 | Breach assessment readiness drill | Semi-annual |
| 4 | External HIPAA evaluation | Annual |
| 5 | BAA renewal and review | Per BAA terms |

---

## 14. Cross-References

### 14.1 Internal GRC Documents

| Document | Relationship |
|----------|-------------|
| [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) | Primary control implementation reference. Every NIST 800-53 control cited in this crosswalk is documented in the SSP. |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | The six gaps in Section 12 will be added as POA&M entries with prefix HIPAA-G-. |
| [POLICY_RISK_MANAGEMENT.md](POLICY_RISK_MANAGEMENT.md) | Risk Analysis (164.308(a)(1)(ii)(A)) and Risk Management (164.308(a)(1)(ii)(B)) are governed by this policy. |
| [POLICY_ACCESS_CONTROL.md](POLICY_ACCESS_CONTROL.md) | Workforce Security, Information Access Management, and Access Control standards are governed by this policy. |
| [POLICY_CHANGE_MANAGEMENT.md](POLICY_CHANGE_MANAGEMENT.md) | Access Establishment and Modification, Maintenance Records, and Updates are governed by this policy. |
| [POLICY_VULNERABILITY_MANAGEMENT.md](POLICY_VULNERABILITY_MANAGEMENT.md) | Protection from Malicious Software is governed by this policy. |
| [POLICY_INCIDENT_RESPONSE.md](POLICY_INCIDENT_RESPONSE.md) | Security Incident Procedures and the Breach Notification Rule alignment are governed by this policy. |
| [POLICY_BUSINESS_CONTINUITY.md](POLICY_BUSINESS_CONTINUITY.md) | Contingency Plan standards are governed by this policy. |
| [POLICY_DISASTER_RECOVERY.md](POLICY_DISASTER_RECOVERY.md) | Disaster Recovery Plan and Testing and Revision Procedures are governed by this policy. |
| [POLICY_ACCEPTABLE_USE.md](POLICY_ACCEPTABLE_USE.md) | Workstation Use, Workstation Security, and Sanction Policy references are in this policy. |
| [POLICY_SECURITY_AWARENESS.md](POLICY_SECURITY_AWARENESS.md) | Security Awareness and Training standard is governed by this policy. |
| [POLICY_AI_GOVERNANCE.md](POLICY_AI_GOVERNANCE.md) | AI-specific governance overlay. Relevant if AI workloads touch ePHI. |
| [IAM_RBAC_ROLE_MAP.md](IAM_RBAC_ROLE_MAP.md) | Role definitions for ePHI access. |
| [IAM_ACCESS_REVIEW.md](IAM_ACCESS_REVIEW.md) | Quarterly access review process. |
| [PLAYBOOK_COMPROMISED_CONTAINER.md](PLAYBOOK_COMPROMISED_CONTAINER.md) | Container compromise response, including ePHI exfiltration scenarios. |
| [PLAYBOOK_LEAKED_CREDENTIAL.md](PLAYBOOK_LEAKED_CREDENTIAL.md) | Credential exposure response, including BAA notification obligations. |
| [PLAYBOOK_UNAUTHORIZED_ACCESS.md](PLAYBOOK_UNAUTHORIZED_ACCESS.md) | Unauthorized access response. |
| [PLAYBOOK_AI_INCIDENT.md](PLAYBOOK_AI_INCIDENT.md) | AI-specific incident response covering ePHI disclosure via prompt injection or hallucination. |
| [AI_AUDIT_TRAIL_SPEC.md](AI_AUDIT_TRAIL_SPEC.md) | AI-specific audit trail specification. |
| [SQUIRE_DATA_FLOW_CLASSIFICATION.md](SQUIRE_DATA_FLOW_CLASSIFICATION.md) | Data classification framework. ePHI class will be added per Gap G-06. |
| [GUARDRAILS_CONFIGURATION.md](GUARDRAILS_CONFIGURATION.md) | Pre-graph PII scanner, NeMo input and output rails. Same controls would apply to ePHI detection. |
| [FRAMEWORK_CROSSWALK_SQUIRE.md](FRAMEWORK_CROSSWALK_SQUIRE.md) | Squire-scope cross-framework mapping. |
| [DAST_METHODOLOGY.md](DAST_METHODOLOGY.md) | Quarterly DAST scans, including cipher suite verification for transmission security. |
| [PENTEST_SELF_ASSESSMENT.md](PENTEST_SELF_ASSESSMENT.md) | Annual pen test self-assessment that contributes to Evaluation (164.308(a)(8)). |
| [TABLETOP_EXERCISE.md](TABLETOP_EXERCISE.md) | Tabletop exercise template; ePHI-specific scenario will be added at first BAA signing. |

### 14.2 External Standards and Guidance

| Standard | Title | Use in This Crosswalk |
|----------|-------|----------------------|
| 45 CFR Part 164, Subpart C | HIPAA Security Standards | Source authority for every standard and implementation specification mapped in this document. |
| 45 CFR Part 164, Subpart D | HIPAA Breach Notification Rule | Source authority for Section 10. |
| NIST SP 800-66 Rev 2 | Implementing the Health Insurance Portability and Accountability Act (HIPAA) Security Rule: A Cybersecurity Resource Guide | Primary mapping methodology. NIST 800-53 control selections in this crosswalk follow the recommendations in NIST 800-66 Rev 2 Section 5. |
| NIST SP 800-53 Rev 5 | Security and Privacy Controls for Information Systems and Organizations | Source for every NIST 800-53 control ID cited. |
| NIST SP 800-30 Rev 1 | Guide for Conducting Risk Assessments | Risk Analysis methodology cited under 164.308(a)(1)(ii)(A). |
| NIST SP 800-61 Rev 3 | Computer Security Incident Handling Guide | Incident response methodology cited under 164.308(a)(6). |
| NIST SP 800-88 Rev 1 | Guidelines for Media Sanitization | Media disposal methodology cited under 164.310(d)(2)(i). |
| HHS Sample BAA Provisions | Sample Business Associate Agreement Provisions | Source for BAA template draft under Gap G-02. |

### 14.3 Enforcement Authority

The HHS Office for Civil Rights (OCR) is the federal enforcement body for the HIPAA Security Rule and the Breach Notification Rule. OCR investigates complaints, conducts compliance reviews, and may impose civil monetary penalties on Covered Entities, Business Associates, and Subcontractors that violate the rules. Penalty tiers range from approximately $137 per violation for unknowing violations to over $2 million per year for willful neglect not corrected, as updated annually per 45 CFR 102.3. Criminal penalties under 42 USC 1320d-6 may apply for knowing misuse of identifiable health information.

OSOP's compliance posture is designed to demonstrate good-faith compliance such that any future enforcement action would find clear evidence of policies, procedures, monitoring, and remediation. The honest gap disclosure in Section 12 supports this posture.

---

## 15. Definitions

| Term | Definition |
|------|-----------|
| Addressable | An implementation specification that a Covered Entity or Business Associate must evaluate. If reasonable and appropriate, implement as written. If not, document why and implement an equivalent measure that meets the standard. |
| Authorization Boundary | The set of information systems for which the organization claims responsibility, as defined in NIST SP 800-37 Rev 2. |
| Breach | An impermissible use or disclosure under the HIPAA Privacy Rule that compromises the security or privacy of protected health information, except as otherwise provided in 164.402. |
| Business Associate (BA) | A person or entity that performs certain functions or activities that involve the use or disclosure of protected health information on behalf of, or provides services to, a Covered Entity. |
| Business Associate Agreement (BAA) | A written contract between a Covered Entity and a Business Associate that establishes the permitted and required uses and disclosures of PHI by the Business Associate, per 164.504(e) and 164.314(a). |
| Covered Entity (CE) | A health plan, a health care clearinghouse, or a health care provider that transmits any health information in electronic form in connection with a transaction covered by HIPAA. |
| ePHI (electronic protected health information) | Individually identifiable health information that is transmitted by or maintained in electronic media. |
| HHS | United States Department of Health and Human Services. |
| HHS OCR | HHS Office for Civil Rights, the enforcement body for HIPAA Privacy, Security, and Breach Notification Rules. |
| HIPAA | Health Insurance Portability and Accountability Act of 1996, as amended by the HITECH Act of 2009 and subsequent regulations. |
| Implementation Specification | Specific requirements or instructions for implementing a standard, classified as either Required or Addressable. |
| Minimum Necessary | The principle that uses, disclosures, and requests for PHI must be limited to the minimum necessary to accomplish the intended purpose. |
| Required | An implementation specification that must be implemented as written. |
| Standard | A high-level requirement in the HIPAA Security Rule that prescribes a security objective. |
| Subcontractor | A person or entity to whom a Business Associate delegates a function, activity, or service involving the use or disclosure of PHI. Subcontractors are themselves Business Associates under HIPAA. |
| Unsecured PHI | PHI that is not rendered unusable, unreadable, or indecipherable to unauthorized persons through the use of a technology or methodology specified by HHS guidance. |

---

## 16. Document Control Summary

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-05-25 | Information Security Officer | Initial HIPAA Security Rule crosswalk covering all standards in 45 CFR 164.308, 164.310, 164.312, 164.314, 164.316, and 164 Subpart D, mapped to existing NIST SP 800-53 Rev 5 controls in OSOP. Six gaps identified with target close dates. Customer onboarding workflow defined. |

Next scheduled review: 2026-11-25 (semi-annual cadence). Out-of-cycle review triggered by: first BAA signing event, material infrastructure change affecting ePHI handling capability, HHS rulemaking update to 45 CFR Part 164, or significant change to NIST 800-66 or NIST 800-53.

---

*Document ID: HIPAA-001 | Version 1.0 | Classification: CONTROLLED UNCLASSIFIED - INTERNAL USE ONLY*

*This crosswalk is a forward-looking compliance readiness artifact. The Organization is not a Covered Entity or a Business Associate as of the effective date. The Security Rule does not bind OSOP today. This document supports rapid onboarding of a healthcare customer once a Business Associate Agreement is in place.*
