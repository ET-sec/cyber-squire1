# Risk Management Policy

**Document ID:** POL-RM-001
**Version:** 1.0
**Classification:** Internal Use Only
**Effective Date:** 2026-03-11
**Review Cycle:** Annual (next review: 2027-03-11)
**Owner:** Risk Manager
**Approved By:** System Owner
**NIST 800-53 Controls:** RA-1, RA-2, RA-3, PM-9

---

## Document Control

| Field | Value |
|-------|-------|
| **Policy Title** | Risk Management Policy |
| **Document ID** | POL-RM-001 |
| **Version** | 1.0 |
| **Status** | Approved |
| **Last Revised** | 2026-03-11 |
| **Next Review** | 2027-03-11 |
| **Author** | Risk Manager |
| **Approver** | System Owner |
| **Distribution** | All personnel with administrative access to Organization infrastructure |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-03-11 | Risk Manager | Initial policy creation |

---

## 1. Purpose and Scope

### 1.1 Purpose

This Risk Management Policy establishes the governance framework for identifying, assessing, responding to, and monitoring information security risks across the Organization security operations platform. It defines the organizational risk tolerance, assigns roles and responsibilities for risk decisions, and integrates risk management into the platform's operational lifecycle.

This policy satisfies the following NIST SP 800-53 Rev. 5 control requirements:

| Control | Title | Requirement |
|---------|-------|-------------|
| **RA-1** | Risk Assessment Policy and Procedures | Establish and maintain a risk assessment policy that addresses purpose, scope, roles, responsibilities, management commitment, coordination, and compliance |
| **RA-2** | Security Categorization | Categorize the system and the information it processes, stores, and transmits in accordance with FIPS 199 |
| **RA-3** | Risk Assessment | Conduct risk assessments that identify threats, vulnerabilities, likelihood, impact, and resulting risk to organizational operations and assets |
| **PM-9** | Risk Management Strategy | Develop a comprehensive strategy to manage risk to organizational operations, assets, and individuals |

### 1.2 Scope

This policy applies to all information systems, services, and data within the authorization boundary of the Organization security operations platform, including:

- The production VPS (`alpha-node`) and all thirteen (13) containerized services operating within the Docker Compose stack
- The standalone AI gateway container (`svc-ai-gateway`)
- Infrastructure-as-code definitions, CI/CD pipelines, and associated security scanning toolchains
- The external secrets management pipeline and credential lifecycle
- Zero-trust tunnel ingress, Cloudflare configurations, and DigitalOcean firewall rules
- All personnel with administrative, operational, or audit access to the platform

**Out of scope:** End-user workstations, third-party SaaS platforms beyond their integration points with the platform, and the physical security of DigitalOcean's data centers (governed by DigitalOcean's shared responsibility model).

### 1.3 Policy Statements

1. All identified risks to the Organization security operations platform SHALL be formally assessed, documented, and tracked through the risk management lifecycle defined in this policy.
2. Risk acceptance decisions SHALL be made only by personnel with the authority level defined in Section 6.
3. No system component SHALL be deployed to production without a risk assessment if the change qualifies as significant under the Change Management Policy (GRC-CM-001).
4. The risk register SHALL be reviewed on the schedule defined in Section 8 and updated upon any triggering event.
5. All risk management activities SHALL be documented with sufficient detail to support audit review.

---

## 2. NIST Framework Alignment

### 2.1 NIST SP 800-39 (Managing Information Security Risk)

This policy implements the four-tier risk management process defined in NIST SP 800-39:

```
+-------------------------------------------------------------+
|          RISK MANAGEMENT PROCESS          |
|           (NIST SP 800-39)             |
|                               |
|  +--------+  +--------+  +---------+  +---------+   |
|  | FRAME | -> | ASSESS | -> | RESPOND | -> | MONITOR |  |
|  +--------+  +--------+  +---------+  +---------+   |
|    |                      |     |
|    +-------------------------------------------+     |
|          Continuous Feedback Loop          |
+-------------------------------------------------------------+
```

### 2.2 NIST SP 800-30 Rev. 1 (Guide for Conducting Risk Assessments)

The risk assessment methodology follows NIST SP 800-30 Rev. 1, using a semi-quantitative 5x5 risk matrix. The methodology, likelihood and impact scales, and scoring thresholds are defined in the Risk Assessment (RA-2026-001, `docs/grc/RISK_ASSESSMENT.md`).

### 2.3 FIPS 199 (Security Categorization)

The system is categorized as **Moderate** overall per FIPS 199, as documented in the Risk Assessment (Section 1.3):

| Security Objective | Impact Level | Justification |
|-------------------|--------------|---------------|
| **Confidentiality** | Moderate | Platform processes API keys, credentials, and operational telemetry |
| **Integrity** | Moderate | Workflow logic and infrastructure state must remain trustworthy |
| **Availability** | Moderate | Single-operator platform; short outages are tolerable |

This categorization determines the baseline set of security controls applied from NIST SP 800-53 Rev. 5 and informs risk tolerance thresholds throughout this policy.

### 2.4 NIST 800-53 Control Mapping

| Control | Title | How This Policy Satisfies |
|---------|-------|--------------------------|
| RA-1 | Risk Assessment Policy and Procedures | Sections 1, 4, 5, 11 establish the policy framework |
| RA-2 | Security Categorization | Section 2.3 references the FIPS 199 categorization |
| RA-3 | Risk Assessment | Sections 3, 5 define the assessment methodology and process |
| PM-9 | Risk Management Strategy | Section 3 defines the four-tier strategy; Section 6 defines risk tolerance |

---

## 3. Risk Management Framework

### 3.1 Frame - Establish Risk Context

The framing step establishes the context, assumptions, and constraints under which all risk management activities are conducted.

**Risk context:**

- The Organization security operations platform is a single-node, containerized infrastructure supporting security orchestration, automation, and response (SOAR) for the Organization.
- The platform operates within a DigitalOcean environment under a shared responsibility model.
- The system is classified as FIPS 199 Moderate, requiring controls commensurate with protecting the confidentiality and integrity of credentials, automation logic, and audit data.

**Assumptions:**

1. DigitalOcean maintains physical security, hypervisor integrity, and network backbone availability per their published SLA (99.99% uptime).
2. The external secrets manager and external Datadog operate under their respective security certifications and shared responsibility agreements.
3. The zero-trust tunnel and Cloudflare mitigate the majority of network-layer threats at the perimeter before traffic reaches the VPS.
4. A single-operator environment reduces insider threat likelihood but does not eliminate it; all administrative sessions are recorded.

**Constraints:**

1. The platform operates on a resource-constrained VPS (4 vCPU, 8 GB RAM), which limits the ability to deploy certain compensating controls (e.g., full `auditd` alongside eBPF monitoring).
2. Single-node architecture precludes automatic failover; availability risk is accepted as Low impact per FIPS 199 categorization.
3. Budget constraints limit the platform to a single DigitalOcean region; multi-region redundancy is documented as a future enhancement.

**Risk tolerance statement:**

The Organization accepts Low-rated residual risks (scores 1-6) as part of normal operations. Moderate residual risks (scores 7-14) require documented compensating controls and active remediation plans. High residual risks (scores 15-19) require immediate mitigation action and documented justification if any remain open beyond 30 days. Critical residual risks (scores 20-25) are not acceptable without executive-level approval and may require halting affected operations.

### 3.2 Assess - Identify and Evaluate Risks

The assessment step identifies threats and vulnerabilities, evaluates existing controls, and calculates residual risk. The full assessment methodology is documented in the Risk Assessment (RA-2026-001, `docs/grc/RISK_ASSESSMENT.md`).

**Threat identification sources:**

| Source | Type | Frequency |
|--------|------|-----------|
| CI/CD security scanners (Trivy, Gitleaks, Semgrep, Checkov, Cosign, OPA) | Automated | Every pull request and push |
| CIS Docker Bench for Security | Automated/Manual | Monthly scan, findings tracked in CIS Risk Register |
| eBPF runtime detection (`svc-detection`) | Continuous | Real-time syscall and network monitoring |
| Datadog alerts | Continuous | Infrastructure metrics, container health, log anomalies |
| Vulnerability databases (CVE, NVD) | External intelligence | Continuous via Trivy image scanning |
| Incident post-mortems | Event-driven | After every Severity 1 or 2 incident |
| Industry threat intelligence | Manual | Semi-annual threat catalog update |

**Assessment methodology summary:**

1. Identify threat sources and events using the threat catalog (Risk Assessment, Section 3)
2. Identify vulnerabilities in affected components
3. Evaluate existing controls and their effectiveness
4. Calculate inherent risk using the 5x5 matrix: `Risk Score = Likelihood x Impact`
5. Apply control effectiveness to derive residual risk
6. Classify residual risk by threshold: Low (1-6), Moderate (7-14), High (15-19), Critical (20-25)
7. Document findings in the risk register with recommended treatment

### 3.3 Respond - Select and Implement Risk Treatment

For each identified risk, one of four treatment strategies SHALL be selected:

| Strategy | Definition | When Applied |
|----------|------------|-------------|
| **Accept** | Acknowledge the risk and continue operations without additional controls | Residual risk falls within organizational risk tolerance; compensating controls are sufficient |
| **Mitigate** | Implement additional controls to reduce likelihood or impact | Residual risk exceeds tolerance and can be reduced by feasible controls |
| **Transfer** | Shift risk to a third party through insurance, contract, or service agreement | Risk is better managed by an external party (e.g., DigitalOcean SLA, cyber insurance) |
| **Avoid** | Eliminate the risk by removing the threat source or vulnerable component | Risk cannot be acceptably mitigated and the affected capability is not essential |

**Treatment selection requirements:**

1. Each risk treatment decision SHALL be documented in the risk register with the rationale for the selected strategy.
2. For **Accept** decisions, compensating controls SHALL be documented and validated during the next review cycle.
3. For **Mitigate** decisions, specific remediation actions SHALL be recorded in the POA&M (`docs/grc/POAM_PLAN_OF_ACTION.md`) with assigned owners, milestones, and target dates.
4. For **Transfer** decisions, the transferring mechanism (contract, SLA, insurance policy) SHALL be documented and its coverage validated annually.
5. For **Avoid** decisions, the decommission or removal plan SHALL follow the Change Management Policy (GRC-CM-001).

### 3.4 Monitor - Ongoing Risk Surveillance

Risk monitoring ensures that risk conditions, control effectiveness, and the threat landscape are continuously evaluated. Monitoring activities are organized into three tiers:

**Tier 1 - Continuous (Automated):**

| Activity | Mechanism | Response |
|----------|-----------|----------|
| Container vulnerability scanning | Trivy in CI/CD pipeline | Block merge on HIGH/CRITICAL CVE; create POA&M item for MEDIUM |
| Secret leak detection | Gitleaks in CI/CD pipeline | Block merge; initiate credential rotation procedure |
| Static code analysis | Semgrep in CI/CD pipeline | Block merge on high-confidence findings |
| Infrastructure policy enforcement | 8 OPA (Rego) policies in CI/CD | Block merge on policy violation |
| Runtime threat detection | `svc-detection` (eBPF) with 8 custom rules | Alert to Datadog; trigger incident response if threshold met |
| Infrastructure monitoring | Datadog agent (`svc-monitor`) | Alert on metric thresholds (CPU >85%, memory >85%, disk >80%) |

**Tier 2 - Periodic (Scheduled):**

| Activity | Frequency | Owner | Reference |
|----------|-----------|-------|-----------|
| POA&M status review | 90 days | Risk Manager | POAM_PLAN_OF_ACTION.md, Section 5 |
| Risk register review | Quarterly | Risk Manager | RISK_ASSESSMENT.md, Section 8 |
| CIS Docker Bench scan | Monthly | System Administrator | CIS_RISK_REGISTER.md |
| IAM access review | Monthly | Risk Manager | IAM_ACCESS_REVIEW.md |
| Tabletop exercise | Semi-annual | Risk Manager | TABLETOP_EXERCISE.md |
| Full risk assessment | Annual | Risk Manager | RISK_ASSESSMENT.md |
| Threat catalog update | Semi-annual | Risk Manager | RISK_ASSESSMENT.md, Section 3 |

**Tier 3 - Triggered (Event-Driven):**

| Trigger | Required Action |
|---------|----------------|
| Security incident (Severity 1 or 2) | Out-of-cycle risk assessment of affected components; update risk register |
| Significant architectural change | Risk assessment before deployment per Change Management Policy |
| New regulatory or compliance requirement | Gap analysis against current controls; update risk register |
| Critical vulnerability disclosure (CVSS >= 9.0) in deployed component | Immediate vulnerability assessment; emergency POA&M entry if applicable |
| Cloud provider security advisory | Evaluate applicability; update risk register if threat model changes |
| Change in organizational mission or data sensitivity | Reassess FIPS 199 categorization; adjust control baseline |

---

## 4. Roles and Responsibilities

| Role | Responsibilities |
|------|-----------------|
| **Risk Manager (System Owner)** | Owns the risk management program and risk register. Conducts and approves risk assessments. Approves risk acceptance decisions for Moderate and High risks. Reviews POA&M status on the defined schedule. Ensures risk management activities are documented for audit. Reports risk posture metrics. |
| **System Administrator** | Identifies and reports risks encountered during daily operations. Implements approved risk mitigations and compensating controls. Executes vulnerability remediation within POA&M timelines. Maintains security scanning toolchains and monitoring configurations. Accepts Low-level risks with documentation. |
| **Auditor** | Reviews risk acceptance decisions for completeness and compliance with this policy. Validates that compensating controls are implemented and effective. Reviews POA&M completion rates and overdue items. Verifies risk assessment methodology is consistently applied. Provides independent assessment during tabletop exercises. |

### 4.1 Segregation of Duties

In the current single-operator environment, the Risk Manager and System Administrator roles are performed by the same individual. To maintain accountability:

1. All risk acceptance decisions SHALL be documented with written justification, compensating controls, and a defined review date.
2. The Auditor role SHALL be performed independently (either by an external party or through a structured self-audit process using the documented checklists in the GRC framework).
3. Session recordings via `svc-gateway` provide an immutable audit trail of all administrative actions, compensating for the lack of a separate reviewer.
4. If the organization expands beyond a single operator, the Risk Manager and System Administrator roles SHALL be assigned to separate individuals.

---

## 5. Risk Assessment Process

### 5.1 Assessment Frequency

| Assessment Type | Frequency | Scope | Deliverable |
|----------------|-----------|-------|-------------|
| **Comprehensive risk assessment** | Annual | Full authorization boundary | Updated Risk Assessment (RA-2026-001) |
| **Quarterly risk register review** | Every 90 days | All open and accepted risks | Updated risk register entries; POA&M status |
| **Triggered reassessment** | Event-driven (see Section 3.4, Tier 3) | Affected components only | Addendum to Risk Assessment or new risk register entries |

### 5.2 Methodology

Risk assessments SHALL follow NIST SP 800-30 Rev. 1 using the semi-quantitative 5x5 matrix defined in the Risk Assessment (RA-2026-001, `docs/grc/RISK_ASSESSMENT.md`, Section 2).

**Likelihood Scale (1-5):**

| Rating | Value | Definition |
|--------|-------|------------|
| Very Low | 1 | Unlikely to occur (less than once per 5 years) |
| Low | 2 | Could occur but not expected (once per 1-5 years) |
| Moderate | 3 | Somewhat likely (once per year) |
| High | 4 | Likely to occur (multiple times per year) |
| Very High | 5 | Almost certain (monthly or more frequent) |

**Impact Scale (1-5):**

| Rating | Value | Definition |
|--------|-------|------------|
| Very Low | 1 | Negligible effect on operations, assets, or individuals |
| Low | 2 | Limited adverse effect; minor degradation of capability |
| Moderate | 3 | Serious adverse effect; significant degradation of capability |
| High | 4 | Severe adverse effect; major damage to assets or operations |
| Very High | 5 | Catastrophic effect; complete loss of capability or major breach |

**Risk Scoring:**

```
Risk Score = Likelihood x Impact
```

**Risk Rating Thresholds:**

| Risk Score | Rating | Action Required | Remediation Timeline |
|-----------|--------|-----------------|---------------------|
| 1 - 6 | **Low** | Accept with documentation; monitor during regular reviews | N/A (accepted) or 1 year |
| 7 - 14 | **Moderate** | Mitigate within 90 days; document compensating controls | 90 days |
| 15 - 19 | **High** | Mitigate within 30 days; escalate to Risk Manager | 30 days |
| 20 - 25 | **Critical** | Immediate action required; halt affected operations if necessary | Immediate |

### 5.3 Threat Identification Sources

Risk assessments SHALL draw threat and vulnerability data from the following sources:

| Source Category | Specific Sources | Data Type |
|----------------|-----------------|-----------|
| **CI/CD findings** | Trivy, Gitleaks, Semgrep, Checkov, Cosign, policy engine | Automated vulnerability and policy violation data |
| **Runtime detection** | `svc-detection` (eBPF) with 8 custom rules, `svc-detection-router` alert routing | Syscall-level behavioral anomalies, container escape attempts, unauthorized access |
| **CIS benchmarks** | CIS Docker Bench for Security (monthly scans) | Configuration compliance findings (96 WARN items tracked in CIS Risk Register) |
| **Vulnerability intelligence** | CVE/NVD databases via Trivy, vendor security advisories | Known vulnerability disclosures affecting deployed components |
| **Monitoring telemetry** | Datadog metrics, logs, and APM data | Infrastructure anomalies, performance degradation, resource exhaustion |
| **Incident data** | Post-incident reviews, forensic analysis | Realized threats and control failures |
| **External intelligence** | MITRE ATT&CK framework, industry threat reports | Threat actor TTPs relevant to containerized infrastructure |

### 5.4 Assessment Procedure

1. **Scope definition:** Define assessment boundaries aligned with the authorization boundary (Section 1.2).
2. **Asset inventory:** Enumerate all components within scope using the system architecture documentation (SSP-OPS-001, `docs/grc/SSP_SYSTEM_SECURITY_PLAN.md`, Section 2).
3. **Threat identification:** Catalog applicable threats using the threat catalog (Risk Assessment, Section 3) and the data sources in Section 5.3 above.
4. **Vulnerability identification:** Map vulnerabilities to each threat-asset pair using scan results, benchmark findings, and configuration reviews.
5. **Control evaluation:** Document existing controls for each vulnerability and assess their effectiveness in reducing likelihood or impact.
6. **Risk calculation:** Calculate inherent risk (before controls) and residual risk (after controls) using the 5x5 matrix.
7. **Risk prioritization:** Rank risks by residual risk score; identify top risks requiring treatment.
8. **Treatment recommendation:** Recommend a treatment strategy (Accept, Mitigate, Transfer, Avoid) for each risk.
9. **Documentation:** Record all findings in the risk register and update the POA&M for any items requiring remediation.
10. **Approval:** Risk Manager reviews and approves the assessment; Auditor validates methodology compliance.

---

## 6. Risk Acceptance Criteria

### 6.1 Acceptance Authority

Risk acceptance decisions SHALL be made only by personnel with authority commensurate with the risk level:

| Risk Rating | Acceptance Authority | Requirements |
|------------|---------------------|--------------|
| **Low (1-6)** | System Administrator | Document the risk, compensating controls, and next review date |
| **Moderate (7-14)** | Risk Manager | Document business justification, compensating controls, residual risk score, and next review date |
| **High (15-19)** | Risk Manager with documented justification | Written business justification, compensating controls, mitigation plan with milestones, 30-day review commitment |
| **Critical (20-25)** | Not acceptable without executive approval | Formal risk acceptance memorandum, executive sign-off, immediate compensating controls, continuous monitoring, 7-day review cycle until mitigated |

### 6.2 Acceptance Documentation Requirements

Every risk acceptance decision SHALL include the following documentation:

| Field | Required For | Description |
|-------|-------------|-------------|
| **Risk ID** | All levels | Unique identifier from the risk register (e.g., R-01) |
| **Risk description** | All levels | Clear statement of the threat, vulnerability, and potential impact |
| **Residual risk score** | All levels | Calculated score after existing controls |
| **Business justification** | Moderate, High, Critical | Why the risk cannot be fully mitigated or avoided |
| **Compensating controls** | All levels | Controls that reduce the risk to an acceptable level |
| **Control validation** | Moderate, High, Critical | Evidence that compensating controls are implemented and functioning |
| **Accepting authority** | All levels | Name and role of the person accepting the risk |
| **Acceptance date** | All levels | Date the acceptance decision was made |
| **Maximum acceptance period** | All levels | Mandatory reassessment deadline (see Section 6.3) |
| **Conditions for revocation** | High, Critical | Events that would void the acceptance and require re-evaluation |

### 6.3 Maximum Acceptance Periods

Risk acceptance is not permanent. All accepted risks SHALL be reassessed on the following schedule:

| Risk Rating | Maximum Acceptance Period | Reassessment Trigger |
|------------|--------------------------|---------------------|
| **Low (1-6)** | 1 year | Annual risk assessment or triggering event |
| **Moderate (7-14)** | 90 days | Quarterly review cycle or triggering event |
| **High (15-19)** | 30 days | Monthly review or triggering event |
| **Critical (20-25)** | 7 days | Weekly review until mitigated below Critical |

If a risk acceptance expires without reassessment, the risk SHALL be escalated to the Risk Manager for immediate review. Expired acceptances are reported as overdue items in the risk posture metrics (Section 10).

### 6.4 Current Risk Acceptance Posture

As of the effective date of this policy, the following risk acceptances are active (reference: Risk Assessment RA-2026-001, Section 7):

| Category | Count | Risk IDs |
|----------|-------|----------|
| **Accepted (Low)** | 10 | R-01, R-02, R-03, R-05, R-06, R-07, R-08, R-09, R-11, R-13 |
| **Accepted (Low, compliance)** | 2 | R-15, R-17 |
| **Mitigating (Moderate)** | 3 | R-04, R-10, R-14 |
| **Mitigating (Low)** | 2 | R-12, R-16 |

Additionally, the CIS Risk Register (`docs/grc/CIS_RISK_REGISTER.md`) documents 15 formally accepted findings from the CIS Docker Bench assessment (4 Medium, 11 Low), each with documented compensating controls and 90-day review dates.

---

## 7. Risk Register Management

### 7.1 Risk Tracking Instruments

Risks are tracked using two complementary instruments:

| Instrument | Location | Purpose |
|-----------|----------|---------|
| **Risk Assessment Register** | `docs/grc/RISK_ASSESSMENT.md`, Section 4 | Tracks 17 organizational risks (R-01 through R-17) across external, internal, environmental, and compliance threat categories |
| **CIS Risk Register** | `docs/grc/CIS_RISK_REGISTER.md` | Tracks 29 CIS Docker Bench findings with compensating controls and review dates |
| **POA&M** | `docs/grc/POAM_PLAN_OF_ACTION.md` | Tracks 27 entries (POAM-001 through POAM-027) consolidating findings from 4 assessment sources from CIS Docker Bench, IaC compliance scanning, runtime detection baseline, and Risk Assessment mitigate treatments, with remediation milestones |

### 7.2 Required Fields for Risk Register Entries

Every risk register entry SHALL include the following fields:

| Field | Description |
|-------|-------------|
| Risk ID | Unique identifier (e.g., R-01, POAM-001) |
| Threat | Reference to threat catalog entry (e.g., T-01 through T-17) |
| Threat source | Category of threat actor or event (external adversary, operator error, environmental) |
| Vulnerability | Specific weakness exploited by the threat |
| Affected assets | Components within the authorization boundary impacted |
| Likelihood (inherent) | Score 1-5 before controls |
| Impact (inherent) | Score 1-5 before controls |
| Inherent risk score | Likelihood x Impact |
| Current controls | Controls in place that reduce likelihood or impact |
| Likelihood (residual) | Score 1-5 after controls |
| Impact (residual) | Score 1-5 after controls |
| Residual risk score | Likelihood x Impact (after controls) |
| Risk rating | Low, Moderate, High, or Critical |
| Treatment strategy | Accept, Mitigate, Transfer, or Avoid |
| Treatment details | Specific actions, compensating controls, or transfer mechanism |
| Owner | Role responsible for the risk (Risk Manager, System Administrator) |
| Status | Current lifecycle stage (see Section 7.3) |
| Target date | Remediation milestone (for Mitigate/Transfer/Avoid) or next review (for Accept) |
| NIST 800-53 mapping | Applicable control family(ies) |

### 7.3 Risk Status Lifecycle

Each risk follows a defined lifecycle from identification through closure:

```
+------------+   +-----------+   +-------------------+   +-------------+   +------------------+
| IDENTIFIED | --> | ASSESSED | --> | TREATMENT     | --> | IMPLEMENTED | --> | CLOSED      |
|      |   |      |   | SELECTED     |   |       |   | (or ACCEPTED)  |
+------------+   +-----------+   +-------------------+   +-------------+   +------------------+
   ^                    |                      |
   |                    v                      |
   |               +-------------------+                 |
   +------------------------------| REASSESSMENT   |<--------------------------------+
                  | REQUIRED      |
                  +-------------------+
```

| Status | Definition | Transition Criteria |
|--------|-----------|-------------------|
| **Identified** | Risk has been discovered but not yet assessed | Assigned to assessor; awaiting likelihood/impact evaluation |
| **Assessed** | Likelihood, impact, and risk score have been calculated | Treatment strategy selected by appropriate authority |
| **Treatment Selected** | Accept, Mitigate, Transfer, or Avoid decision documented | For Mitigate/Transfer/Avoid: POA&M entry created. For Accept: documentation complete |
| **Implemented** | Mitigation controls deployed or transfer mechanism activated | Control effectiveness validated; residual risk recalculated |
| **Closed** | Risk has been eliminated or mitigated to within tolerance | Verified by Auditor; no further action required |
| **Accepted** | Risk formally accepted per Section 6 criteria | Acceptance documentation complete; subject to periodic reassessment |
| **Reassessment Required** | Acceptance period expired or triggering event occurred | Returns to Assessed status for re-evaluation |

---

## 8. Risk Monitoring

### 8.1 Continuous Monitoring

The following automated mechanisms provide continuous risk monitoring:

| Mechanism | Components | Risk Categories Monitored |
|-----------|-----------|--------------------------|
| CI/CD security pipeline | Trivy, Gitleaks, Semgrep, Checkov, Cosign, policy engine | Supply chain (R-03), secret exposure (R-10), configuration drift (R-11) |
| eBPF runtime detection | `svc-detection` with 8 custom rules, `svc-detection-router` | Container escape (R-08), unauthorized access (R-09), process anomalies |
| Datadog | `svc-monitor` agent, infrastructure dashboards | Resource exhaustion, service health, availability (R-12, R-13) |
| Zero-trust tunnel metrics | Cloudflare analytics | DDoS (R-01), brute force (R-02), web exploitation (R-04) |
| Immutable audit log chain | `svc-gateway` session recordings, `svc-event-shipper` log shipping | Insider threat (R-09), unauthorized changes (R-11), forensic evidence |

### 8.2 Periodic Reviews

| Activity | Frequency | Owner | Deliverable |
|----------|-----------|-------|-------------|
| POA&M status review | Every 90 days | Risk Manager | Updated POA&M with status changes, new milestones |
| Risk register review | Quarterly | Risk Manager | Updated risk scores, new risks added, closed risks archived |
| CIS Docker Bench rescan | Monthly | System Administrator | Delta report comparing to previous scan; new findings added to CIS Risk Register |
| IAM access review | Monthly | Risk Manager | Access review report; JIT access compliance verification |
| Full risk assessment | Annual | Risk Manager | Comprehensive Risk Assessment document update |
| Tabletop exercise | Semi-annual | Risk Manager | Exercise report with identified gaps; risk register updates |
| Threat catalog update | Semi-annual | Risk Manager | Revised threat catalog with new threat sources and MITRE ATT&CK mappings |

### 8.3 Triggered Reviews

A risk review SHALL be initiated outside the scheduled cycle when any of the following occur:

1. **Post-incident:** Any security incident classified as Severity 1 or Severity 2 per the Incident Response Policy (POL-IR-001, `docs/grc/POLICY_INCIDENT_RESPONSE.md`)
2. **Major architecture change:** Addition or removal of services, provider migration, network topology changes, or team expansion (per Change Management Policy GRC-CM-001)
3. **New compliance requirement:** Regulatory change, new contractual obligation, or framework update affecting the platform
4. **Critical vulnerability:** Disclosure of a vulnerability with CVSS >= 9.0 in any deployed component
5. **Control failure:** Discovery that a compensating control is not functioning as documented
6. **Cloud provider advisory:** Security bulletin from DigitalOcean affecting the VPS, network, or storage services

---

## 9. Integration with Other Processes

### 9.1 Change Management (GRC-CM-001)

- **Significant changes** (as defined in the Change Management Policy) SHALL require a risk assessment before deployment approval.
- The risk assessment SHALL evaluate whether the proposed change introduces new risks, alters existing risk scores, or invalidates current compensating controls.
- Changes that increase any risk score above the current residual level require Risk Manager approval before implementation.
- Emergency changes follow the Change Management Policy's emergency procedures but SHALL receive a post-implementation risk assessment within 72 hours.

### 9.2 Incident Response (POL-IR-001)

- All security incidents SHALL be evaluated for risk register impact during the post-incident review phase.
- Incidents that reveal previously unidentified threats or vulnerabilities SHALL result in new risk register entries.
- Incidents that demonstrate control failures SHALL trigger reassessment of affected risk entries and their compensating controls.
- Incident frequency data feeds into likelihood scoring during the annual risk assessment.

### 9.3 Vulnerability Management (POL-VM-001)

- Vulnerability scan findings from CI/CD pipelines and CIS benchmarks flow into the POA&M as trackable findings.
- CRITICAL and HIGH vulnerabilities (Trivy) blocked at merge create immediate POA&M entries.
- MEDIUM vulnerabilities are tracked in the POA&M with 90-day remediation timelines.
- The CIS Risk Register (`docs/grc/CIS_RISK_REGISTER.md`) tracks benchmark findings separately, with cross-references to the POA&M for items requiring remediation.

### 9.4 Business Continuity and Disaster Recovery (POL-BC-001, POL-DR-001)

- The risk register informs Business Impact Analysis (BIA) priorities by identifying the highest-impact threats to platform availability and data integrity.
- Environmental risks (R-12: DigitalOcean outage, R-13: hardware failure, R-14: data loss) directly feed into recovery planning.
- Recovery Time Objective (RTO) and Recovery Point Objective (RPO) targets are informed by the impact scores in the risk register.
- Disaster recovery testing validates that risk mitigations for data loss and provider outage scenarios function as documented.

### 9.5 Access Control (POL-AC-001)

- IAM access reviews (`docs/grc/IAM_ACCESS_REVIEW.md`) validate that the 3-tier RBAC model implemented in `svc-identity` and `svc-gateway` effectively mitigates privilege escalation risks (R-08) and insider threat risks (R-09).
- JIT administrative access with 4-hour TTL reduces the window of exposure for credential theft (R-05).
- Changes to RBAC roles or access policies require risk assessment per the Change Management integration (Section 9.1).

### 9.6 Process Integration Map

```
+---------------------------+    +---------------------------+
|  Change Management   |    |  Incident Response    |
|  (GRC-CM-001)      |    |  (POL-IR-001)      |
|              |    |              |
| Significant changes   |    | Post-incident reviews  |
| require risk assessment |    | update risk register   |
+-------------|-------------+    +-------------|-------------+
       |                  |
       v                  v
+-------------------------------------------------------------+
|         RISK MANAGEMENT PROGRAM           |
|           (POL-RM-001)               |
|                                |
|  Risk Register <--> POA&M <--> CIS Risk Register    |
+--------|------------------------------|----------------------+
     |               |
     v               v
+---------------------------+ +---------------------------+
| Vulnerability Management | | Business Continuity /  |
| (POL-VM-001)       | | Disaster Recovery    |
|              | | (POL-BC/DR-001)     |
| Scan findings flow    | | Risk register informs  |
| to POA&M         | | BIA and RTO/RPO     |
+---------------------------+ +---------------------------+
```

---

## 10. Metrics and Reporting

### 10.1 Key Risk Indicators (KRIs)

The following metrics SHALL be tracked and reported quarterly to measure the effectiveness of the risk management program:

| Metric | Formula | Target | Current Baseline |
|--------|---------|--------|-----------------|
| **Open risks by severity** | Count of risks at each rating level | 0 Critical, 0 High | 0 Critical, 0 High (achieved) |
| **Risk treatment completion rate** | (Closed + Accepted) / Total risks | >= 80% | 82% (14 of 17 risks accepted; 3 in active mitigation) |
| **Overdue POA&M items** | Count of POA&M items past target date | 0 | 0 (baseline) |
| **Mean time to mitigate (Moderate)** | Average days from Identified to Closed for Moderate risks | <= 90 days | N/A (no completed mitigations yet) |
| **Mean time to mitigate (High)** | Average days from Identified to Closed for High risks | <= 30 days | N/A (no High residual risks) |
| **Risk acceptance expiration compliance** | Accepted risks reviewed before expiration / Total accepted | 100% | N/A (first review at 2026-06-09) |
| **CIS benchmark delta** | Change in WARN count between monthly scans | Decreasing or stable | 96 WARN (baseline) |
| **CI/CD security gate blocks** | Count of PRs blocked by security scanners per quarter | Trending downward | Baseline to be established Q2 2026 |

### 10.2 Risk Trend Tracking

Risk trends SHALL be documented at each quarterly review using the following format:

| Quarter | Total Risks | Critical | High | Moderate | Low | New | Closed | Net Change |
|---------|------------|----------|------|----------|-----|-----|--------|------------|
| Q1 2026 (baseline) | 17 | 0 | 0 | 3 | 14 | 17 | 0 | +17 |

### 10.3 Reporting Schedule

| Report | Frequency | Audience | Content |
|--------|-----------|----------|---------|
| Risk posture dashboard | Quarterly | Risk Manager, System Administrator | KRI metrics, risk heat map, trend chart |
| POA&M status report | Every 90 days | Risk Manager, Auditor | Open items, overdue items, completion rate |
| Annual risk assessment report | Annual | Risk Manager, Auditor | Full risk assessment with year-over-year comparison |
| Tabletop exercise after-action report | Semi-annual | Risk Manager, Auditor | Findings, gaps identified, risk register updates |

---

## 11. Policy Review Schedule

### 11.1 Scheduled Review

This policy SHALL be reviewed annually by the Risk Manager. The next scheduled review date is **2027-03-11**.

The review SHALL evaluate:

1. Whether the risk management framework remains appropriate for the platform's security categorization and operational context
2. Whether risk tolerance thresholds require adjustment based on organizational changes
3. Whether roles and responsibilities reflect the current organizational structure
4. Whether the assessment methodology is producing actionable and accurate risk data
5. Whether integration points with other processes are functioning effectively
6. Whether metrics and KRIs provide meaningful visibility into risk posture

### 11.2 Triggered Review

This policy SHALL be reviewed outside the annual cycle when any of the following occur:

- A major security incident that reveals a gap in the risk management framework
- Significant architectural change to the platform (e.g., migration to orchestration platform, multi-region deployment, new public-facing services)
- Change in organizational structure (e.g., team expansion beyond single operator)
- New regulatory or compliance requirement that affects risk management obligations
- Audit finding related to risk management deficiencies

### 11.3 Review Approval

Policy updates SHALL be approved by the System Owner before taking effect. Material changes (new risk tolerance thresholds, role changes, methodology changes) SHALL be communicated to all personnel with platform access within 5 business days of approval.

---

## 12. References

### Internal Documents

| Document | Identifier | Relationship |
|----------|-----------|-------------|
| Risk Assessment | RA-2026-001 (`docs/grc/RISK_ASSESSMENT.md`) | Implements the assessment methodology defined in this policy |
| Plan of Action and Milestones | POAM-2026-001 (`docs/grc/POAM_PLAN_OF_ACTION.md`) | Tracks remediation for risks with Mitigate treatment |
| CIS Docker Benchmark Risk Register | (`docs/grc/CIS_RISK_REGISTER.md`) | Tracks benchmark findings with compensating controls |
| System Security Plan | SSP-OPS-001 (`docs/grc/SSP_SYSTEM_SECURITY_PLAN.md`) | Defines system boundary and control implementation |
| Change Management Policy | GRC-CM-001 (`docs/grc/POLICY_CHANGE_MANAGEMENT.md`) | Change-driven risk assessment requirements |
| Incident Response Policy | POL-IR-001 (`docs/grc/POLICY_INCIDENT_RESPONSE.md`) | Incident-to-risk register feedback loop |
| Vulnerability Management Policy | POL-VM-001 (`docs/grc/POLICY_VULNERABILITY_MANAGEMENT.md`) | Vulnerability finding flow to POA&M |
| Business Continuity Policy | POL-BC-001 (`docs/grc/POLICY_BUSINESS_CONTINUITY.md`) | Risk-informed BIA and continuity planning |
| Disaster Recovery Policy | POL-DR-001 (`docs/grc/POLICY_DISASTER_RECOVERY.md`) | Risk-informed recovery objectives |
| Access Control Policy | POL-AC-001 (`docs/grc/POLICY_ACCESS_CONTROL.md`) | IAM controls mitigating access-related risks |
| IAM Access Review Process | (`docs/grc/IAM_ACCESS_REVIEW.md`) | Periodic access review feeding risk monitoring |
| IAM RBAC Role Map | (`docs/grc/IAM_RBAC_ROLE_MAP.md`) | Role definitions referenced in access-related risks |
| Tabletop Exercise | (`docs/grc/TABLETOP_EXERCISE.md`) | Semi-annual exercise validating risk mitigations |

### External Standards

| Standard | Title | Relevance |
|----------|-------|-----------|
| NIST SP 800-39 | Managing Information Security Risk | Foundation for the four-tier risk management framework |
| NIST SP 800-30 Rev. 1 | Guide for Conducting Risk Assessments | Assessment methodology (5x5 matrix, likelihood/impact scales) |
| NIST SP 800-53 Rev. 5 | Security and Privacy Controls | Control families RA, PM referenced throughout |
| NIST SP 800-37 Rev. 2 | Risk Management Framework for Information Systems | System lifecycle integration |
| FIPS 199 | Standards for Security Categorization | System categorization (Moderate) |
| FIPS 200 | Minimum Security Requirements | Baseline control selection criteria |
| CIS Docker Benchmark | v1.6.0 | Container configuration assessment standard |
| MITRE ATT&CK | Enterprise Framework | Threat catalog TTP mapping |

---

*This policy is reviewed annually or upon significant change to the platform architecture, threat landscape, organizational structure, or regulatory environment. All personnel with administrative access to the Organization security operations platform are responsible for understanding and complying with this policy.*
