# Incident Response Policy

**Document ID:** POL-IR-001
**Version:** 1.0
**Classification:** Internal Use Only
**Effective Date:** 2026-03-11
**Review Date:** 2027-03-11
**Owner:** Information Security Officer
**Approved By:** System Owner

---

## Document Control

| Field | Value |
|-------|-------|
| Policy Title | Incident Response Policy |
| Document ID | POL-IR-001 |
| Version | 1.0 |
| Status | Approved |
| Last Revised | 2026-03-11 |
| Next Review | 2027-03-11 |
| Author | Information Security Officer |
| Approver | System Owner |
| Distribution | All personnel with access to Organization infrastructure |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-03-11 | Information Security Officer | Initial policy creation |

---

## 1. Purpose

This policy establishes a structured and repeatable incident response capability for the Organization security operations platform. It defines the roles, responsibilities, procedures, and reporting requirements necessary to detect, respond to, contain, eradicate, and recover from security incidents affecting Organization infrastructure and services.

The objective is to minimize the impact of security incidents on operational continuity, protect the integrity of audit and forensic evidence, and ensure compliance with applicable regulatory and contractual obligations.

---

## 2. Scope

This policy applies to all systems, services, and personnel that interact with or operate within the Organization security operations platform. This includes but is not limited to:

- The primary compute node (`alpha-node`) and all containerized services hosted thereon
- Database services (`svc-db`), automation workflows (`svc-automation`), secrets management (`svc-secrets`), identity services (`svc-identity`), and the SSH gateway (`svc-gateway`)
- Runtime detection systems (`svc-detection`, `svc-detection-router`), log routing (`Fluentd`, `svc-event-shipper`), and Datadog (`svc-monitor`)
- Zero-trust network ingress (`svc-tunnel`) and the AI gateway (`svc-ai-gateway`)
- CI/CD pipelines, infrastructure-as-code configurations, and code repository platform integrations
- Remote state storage and immutable audit log archives in encrypted object storage
- All administrative, operational, and auditor access sessions regardless of access method

---

## 3. NIST 800-53 Control Alignment

This policy implements the following NIST 800-53 Rev. 5 controls:

| Control | Title | Implementation |
|---------|-------|----------------|
| **IR-1** | Incident Response Policy and Procedures | This document; reviewed annually; disseminated to all authorized personnel |
| **IR-2** | Incident Response Training | All personnel with infrastructure access receive incident response training upon onboarding and annually thereafter |
| **IR-3** | Incident Response Testing | Tabletop exercises conducted semi-annually; post-exercise findings documented and tracked |
| **IR-4** | Incident Handling | Defined phases from detection through recovery; evidence preservation mandated; containment decisions documented |
| **IR-5** | Incident Monitoring | Continuous monitoring via `svc-detection` (eBPF runtime analysis), `svc-monitor` (infrastructure telemetry), and CI/CD security scanning (static analysis, secret detection, vulnerability scanning) |
| **IR-6** | Incident Reporting | Internal escalation within 30 minutes of confirmed P1/P2; external notification per contractual obligations |
| **IR-7** | Incident Response Assistance | Information Security Officer serves as primary point of contact for incident coordination |
| **IR-8** | Incident Response Plan | Maintained as an operational companion to this policy; updated after each post-incident review |

---

## 4. Incident Classification

All suspected and confirmed incidents shall be classified using the following priority levels. Classification determines the response timeline, escalation path, and communication requirements.

### 4.1 Priority Definitions

| Priority | Severity | Description | Response SLA | Examples |
|----------|----------|-------------|-------------|----------|
| **P1** | Critical | Active exploitation, data exfiltration, or complete loss of security controls | Immediate (< 15 min) | Unauthorized root access to `alpha-node`; `svc-secrets` unsealed keys compromised; `svc-detection` disabled by adversary; credential exfiltration from `svc-db`; zero-trust tunnel (`svc-tunnel`) hijacked |
| **P2** | High | Confirmed unauthorized access attempt, security control degradation, or service compromise without confirmed exfiltration | Within 1 hour | Brute-force attack against `svc-identity` exceeding lockout threshold; unauthorized container deployed on `alpha-node`; `svc-gateway` session recording disabled; CI/CD pipeline secret leak detected by secrets scanner |
| **P3** | Medium | Suspicious activity, policy violations, or vulnerability requiring remediation | Within 4 hours | Runtime detection alert for unexpected process execution inside a container; failed MFA authentication spike; infrastructure policy violation in CI/CD pipeline; outdated container image with known CVE (CVSS >= 7.0) |
| **P4** | Low | Informational findings, minor policy deviations, or low-risk vulnerabilities | Within 24 hours | Container health check failure on non-critical service; log ingestion delay on `Fluentd`; CI/CD lint warnings; low-severity CVE in dependency (CVSS < 4.0) |

### 4.2 Classification Criteria

When classifying an incident, consider the following factors:

- **Confidentiality impact:** Was sensitive data (credentials, audit logs, personally identifiable information) accessed or exfiltrated?
- **Integrity impact:** Were configurations, container images, infrastructure-as-code state, or audit records modified without authorization?
- **Availability impact:** Are critical services (authentication, detection, secrets management, automation workflows) degraded or unavailable?
- **Scope of compromise:** Is the incident limited to a single container, or does it affect the host, the network, or multiple services?
- **Adversary persistence:** Is there evidence of persistent access mechanisms (backdoor accounts, modified SSH keys, unauthorized containers)?

---

## 5. Incident Response Team

### 5.1 Roles and Responsibilities

| Role | Responsibility | Current Assignment |
|------|---------------|--------------------|
| **Incident Commander (IC)** | Owns the incident lifecycle from declaration through closure. Makes containment and escalation decisions. Coordinates communication. | Information Security Officer |
| **Technical Lead** | Performs forensic analysis, containment actions, and eradication procedures. Operates security tooling. Documents technical findings. | Information Security Officer |
| **Communications Lead** | Manages internal status updates and external notifications. Maintains the incident timeline. Drafts post-incident communications. | System Owner |
| **Evidence Custodian** | Preserves and chains forensic artifacts. Ensures evidence integrity through hashing and secure storage. Documents chain of custody. | Information Security Officer |

In the current single-operator deployment, these roles are filled by the Information Security Officer and System Owner. As the organization scales, each role should be assigned to a distinct individual to maintain separation of duties in accordance with NIST AC-5.

### 5.2 Contact Information

| Role | Contact Method |
|------|---------------|
| Information Security Officer | `admin@example-ops.com` |
| System Owner | `admin@example-ops.com` |
| DigitalOcean Support | DigitalOcean support portal (priority support tier) |
| Edge Security Provider Support | Cloudflare dashboard |

---

## 6. Incident Response Phases

### Phase 1: Preparation

Preparation ensures the organization can respond effectively before an incident occurs.

**Standing Requirements:**

1. Maintain current access to all detection and monitoring systems (`svc-detection`, `svc-monitor`, `svc-event-shipper`)
2. Ensure `svc-gateway` session recording is operational and audit logs are flowing to Datadog
3. Verify immutable audit log export to encrypted object storage is functioning (hash chain integrity validated)
4. Maintain an up-to-date inventory of all containers, services, and their inter-dependencies
5. Ensure break-glass access credentials are current and securely stored in the credential vault
6. Validate that the CI/CD security pipeline (static analysis, secret detection, vulnerability scanning, infrastructure-as-code policy checks) is active on all branches
7. Conduct tabletop exercises semi-annually to test incident response procedures
8. Review and update this policy annually or after any P1/P2 incident

**Pre-Positioned Tools:**

| Tool | Location | Purpose |
|------|----------|---------|
| `svc-detection` | `alpha-node` container | eBPF-based runtime syscall analysis and anomaly detection |
| `svc-detection-router` | `alpha-node` container | Alert routing and enrichment from runtime detection |
| `svc-monitor` | `alpha-node` container | Infrastructure metrics, container telemetry, log aggregation |
| `svc-event-shipper` | `alpha-node` container | Audit event export from `svc-gateway` to centralized logging |
| `Fluentd` | `alpha-node` container | Log transformation and routing with mTLS transport |
| `svc-gateway` | `alpha-node` container | Session recording, access request audit trail, user lock capability |
| CI/CD Pipeline | Code repository platform | Trivy, Semgrep, Gitleaks, Checkov, policy engine (8 policies) |

### Phase 2: Detection and Analysis

**Detection Sources:**

| Source | Detection Capability | Alert Mechanism |
|--------|---------------------|-----------------|
| `svc-detection` (eBPF runtime analysis) | Unauthorized process execution, privilege escalation, sensitive file access, unexpected network connections, container escape attempts | Alerts forwarded via `svc-detection-router` to Datadog |
| `svc-monitor` | Container health degradation, resource exhaustion, service downtime, log anomalies | Dashboard alerts, threshold-based notifications |
| `svc-gateway` | Failed authentication attempts, unauthorized access requests, session anomalies | Audit events exported via `svc-event-shipper` and `Fluentd` |
| `svc-identity` | Brute-force login attempts (5 failures trigger 15-minute lockout), unauthorized account creation attempts | Identity provider admin events to Datadog |
| CI/CD Pipeline | Secret exposure in commits, known CVEs in container images, IaC misconfigurations, SAST findings | Pipeline failure notifications to code repository platform |
| Manual Report | Personnel observation of unusual behavior, third-party vulnerability disclosure, external threat intelligence | Direct communication to Information Security Officer |

**Analysis Procedures:**

1. **Triage:** Upon receiving an alert, determine whether the event constitutes a confirmed incident, a suspected incident, or a false positive. Document the determination and rationale.
2. **Classify:** Assign a priority level (P1-P4) per Section 4.
3. **Scope:** Determine which services, containers, and data stores are affected. Use `svc-monitor` dashboards and `svc-detection` alert correlation to map the blast radius.
4. **Timeline:** Establish a preliminary timeline using audit logs from `svc-gateway`, `svc-detection`, and `svc-monitor`. Identify the earliest indicator of compromise.
5. **Indicators of Compromise (IOCs):** Extract and document IOCs including process names, file hashes, IP addresses, user accounts, and command sequences.

### Phase 3: Containment

Containment prevents the incident from spreading while preserving evidence for forensic analysis.

**Short-Term Containment (Immediate):**

| Action | Command / Procedure | When to Use |
|--------|-------------------|-------------|
| Lock a user account | `tctl lock --user=<username> --message="Incident #<ID>" --ttl=24h` via `svc-gateway` | Compromised or suspected-compromised account |
| Isolate a container | Stop the affected container; do NOT remove it (preserves filesystem for forensics) | Compromised application container |
| Revoke active sessions | Restart `svc-gateway` to invalidate all active certificates | Widespread session compromise |
| Block network ingress | Modify DigitalOcean firewall rules to restrict inbound traffic | External attack in progress |
| Disable CI/CD pipeline | Pause pipeline execution in code repository platform | Supply chain compromise suspected |

**Long-Term Containment:**

1. Deploy a replacement container from a known-good image while the compromised container is preserved for analysis
2. Rotate all credentials that may have been exposed (API keys, database passwords, SSH keys, MFA seeds)
3. Update Cloudflare tunnel configuration if tunnel integrity is in question
4. Apply emergency infrastructure policy updates to CI/CD if the attack vector is IaC-related

**Containment Decision Matrix:**

| Scenario | Containment Action | Approval Required |
|----------|-------------------|-------------------|
| Single container compromise | Stop container, preserve filesystem | Incident Commander |
| Compromised user account | Lock user via `svc-gateway`, rotate credentials | Incident Commander |
| Host-level compromise | Isolate `alpha-node` via DigitalOcean firewall, preserve disk snapshot | System Owner |
| CI/CD pipeline compromise | Pause all pipelines, revoke code repository platform tokens | Incident Commander |
| Zero-trust tunnel compromise | Rotate tunnel token, revoke tunnel credentials at Cloudflare | System Owner |

### Phase 4: Eradication

Eradication removes the root cause and all artifacts of the compromise from the environment.

1. **Identify root cause:** Determine the vulnerability, misconfiguration, or credential compromise that enabled the incident
2. **Remove adversary artifacts:** Delete unauthorized accounts, containers, SSH keys, cron jobs, and any persistent access mechanisms
3. **Patch the vulnerability:** Apply security patches, update container images, or modify configurations to close the attack vector
4. **Rotate credentials:** Regenerate all potentially exposed secrets through the secrets manager. Update the credential vault. Propagate new credentials to affected services.
5. **Update detection rules:** Add new runtime detection rules, infrastructure policies, or Datadog alerts to detect recurrence of the same or similar attack
6. **Validate eradication:** Run `svc-detection` custom rules targeting the specific IOCs. Verify no residual artifacts remain.

### Phase 5: Recovery

Recovery restores affected services to normal operation with enhanced monitoring.

1. **Restore from known-good state:**
  - Redeploy affected containers from verified images (validated by CI/CD CVE scan and SBOM)
  - Restore database from backup if data integrity is compromised (`svc-db` backup archives)
  - Re-import infrastructure-as-code state from encrypted remote state if IaC state was modified

2. **Validate service integrity:**
  - Verify all container healthchecks are passing
  - Confirm `svc-detection` is operational and generating baseline alerts
  - Confirm `svc-gateway` session recording is active
  - Verify audit log pipeline is flowing: `svc-gateway` to `svc-event-shipper` to `Fluentd` to Datadog
  - Run CI/CD pipeline on current main branch to confirm no regressions

3. **Enhanced monitoring period:**
  - Implement a 72-hour enhanced monitoring window after recovery
  - Lower alert thresholds on Datadog dashboards
  - Review `svc-detection` alerts twice daily during the enhanced monitoring period
  - Verify no recurrence of IOCs identified during the incident

4. **Return to normal operations:**
  - Restore standard alert thresholds
  - Document the recovery completion timestamp
  - Update the incident record with final status

### Phase 6: Post-Incident Activity (Lessons Learned)

A post-incident review shall be conducted for all P1 and P2 incidents within 5 business days of incident closure. P3 incidents shall be reviewed monthly in aggregate.

**Post-Incident Review Agenda:**

1. Incident timeline reconstruction (from first indicator to full recovery)
2. What detection sources triggered, and were they timely?
3. Were containment actions effective and proportionate?
4. Was evidence properly preserved and documented?
5. What was the root cause, and has it been fully eradicated?
6. What policy, procedural, or technical changes are recommended?
7. Were communication procedures followed appropriately?
8. What metrics resulted (MTTD, MTTR, scope, impact)?

**Required Outputs:**

| Artifact | Description | Retention |
|----------|-------------|-----------|
| Post-Incident Report | Formal written report covering all agenda items | 3 years minimum |
| Updated Risk Register | CIS risk register updated with new findings and compensating controls | Continuous |
| Corrective Action Items | Tracked to completion with owner and due date | Until closure |
| Updated Detection Rules | New or modified runtime detection rules, infrastructure policies, or monitoring alerts | Permanent |
| Policy Updates | Revisions to this or related policies if gaps were identified | Per review cycle |

---

## 7. Communication Plan

### 7.1 Internal Notification Chain

| Priority | Notification Timeline | Method | Recipient |
|----------|----------------------|--------|-----------|
| **P1** | Immediate (< 15 min) | Direct message + incident channel | System Owner, Information Security Officer |
| **P2** | Within 1 hour | Direct message | Information Security Officer |
| **P3** | Within 4 hours | Standard notification | Information Security Officer |
| **P4** | Next business day | Weekly status report | Information Security Officer |

### 7.2 Status Update Cadence

| Priority | Update Frequency |
|----------|-----------------|
| **P1** | Every 30 minutes until contained; every 2 hours until resolved |
| **P2** | Every 2 hours until contained; every 4 hours until resolved |
| **P3** | Daily until resolved |
| **P4** | As needed |

### 7.3 External Notification

External notification is required when:

- A data breach affecting third-party data is confirmed
- Contractual obligations mandate disclosure (client SLAs, vendor agreements)
- Law enforcement engagement is warranted
- Regulatory reporting thresholds are met

External notifications shall be drafted by the Communications Lead, reviewed by the System Owner, and transmitted only after explicit approval. No external communication shall occur without documented authorization.

---

## 8. Evidence Preservation

### 8.1 Evidence Collection Procedures

All evidence collection shall follow these principles:

1. **Volatile first:** Collect volatile data (running processes, network connections, memory state) before non-volatile data (disk images, log files)
2. **Minimize modification:** Use read-only access methods wherever possible. Do not run unnecessary commands on compromised systems.
3. **Document everything:** Record every action taken on evidence systems, including the timestamp, command executed, and output observed
4. **Hash all artifacts:** Generate SHA-256 hashes of all collected evidence immediately upon acquisition

### 8.2 Evidence Types and Collection Methods

| Evidence Type | Source | Collection Method | Storage |
|---------------|--------|-------------------|---------|
| Container filesystem | Compromised container (stopped, not removed) | `docker export <container> > evidence-<ID>.tar` | Encrypted object storage |
| Container logs | `svc-monitor` or `docker logs` | Export to file with timestamps | Encrypted object storage |
| Session recordings | `svc-gateway` | Export via gateway recording retrieval | Encrypted object storage |
| Runtime detection alerts | `svc-detection` via `svc-detection-router` | Export from Datadog | Datadog retention (15 days) + encrypted object storage |
| Access request history | `svc-gateway` | `tctl get access_request` | Encrypted object storage |
| Host filesystem artifacts | `alpha-node` | Disk snapshot via DigitalOcean API | Cloud provider snapshot storage |
| CI/CD pipeline logs | Code repository platform | Export workflow run logs | Code repository platform retention |
| Network metadata | `svc-monitor` | Export network flow data from Datadog | Datadog retention |
| Infrastructure-as-code state | Encrypted remote state storage | Copy state file with hash verification | Encrypted object storage (separate bucket) |

### 8.3 Chain of Custody

Every evidence artifact shall be logged in a chain of custody record containing:

- Evidence identifier (unique ID)
- Description of the artifact
- Date and time of acquisition
- SHA-256 hash at time of acquisition
- Name of the person who collected the artifact
- Storage location
- Every subsequent access to the artifact (who, when, why)

---

## 9. Metrics and Key Performance Indicators

The following metrics shall be tracked for all incidents and reviewed quarterly.

| Metric | Definition | Target |
|--------|-----------|--------|
| **Mean Time to Detect (MTTD)** | Time from incident occurrence to first detection alert | P1: < 5 min; P2: < 30 min; P3: < 4 hours |
| **Mean Time to Respond (MTTR)** | Time from detection to containment completion | P1: < 1 hour; P2: < 4 hours; P3: < 24 hours |
| **Mean Time to Recover** | Time from containment to full service restoration | P1: < 4 hours; P2: < 12 hours; P3: < 48 hours |
| **Incident Volume** | Total incidents per month by priority level | Trending downward quarter-over-quarter |
| **False Positive Rate** | Percentage of alerts that are false positives | < 20% |
| **Post-Incident Review Completion** | Percentage of P1/P2 incidents with completed reviews | 100% |
| **Corrective Action Closure Rate** | Percentage of corrective actions completed by due date | > 90% |
| **Detection Coverage** | Percentage of infrastructure services with active detection | 100% |

Metrics shall be reported to the System Owner quarterly and included in the annual policy review.

---

## 10. Policy Review Schedule

| Review Activity | Frequency | Responsible Party |
|----------------|-----------|-------------------|
| Full policy review and update | Annual (or after any P1 incident) | Information Security Officer |
| Tabletop exercise | Semi-annual | Information Security Officer |
| Metrics review | Quarterly | Information Security Officer |
| Detection rule effectiveness review | Quarterly | Information Security Officer |
| Contact information validation | Quarterly | Information Security Officer |
| Post-incident review (P1/P2) | Within 5 business days of closure | Incident Commander |
| Aggregate incident review (P3/P4) | Monthly | Information Security Officer |

---

## 11. Related Documents

| Document | Relationship |
|----------|-------------|
| POL-AC-001 (Access Control Policy) | Defines access controls referenced in containment procedures |
| POL-AU-001 (Acceptable Use Policy) | Defines acceptable use standards; violations may trigger incidents |
| IAM & RBAC Role Map | Defines roles and permissions referenced in evidence collection |
| IAM Access Review Process | Defines access review procedures used during post-incident review |
| CIS Docker Benchmark Risk Register | Documents accepted risks and compensating controls |

---

## 12. Enforcement

Failure to comply with this policy may result in disciplinary action up to and including revocation of system access. All personnel with access to Organization infrastructure are expected to understand their responsibilities under this policy and to cooperate fully during incident response activities.

---

## 13. Definitions

| Term | Definition |
|------|-----------|
| **Incident** | A confirmed or suspected violation of security policy, unauthorized access, or disruption to service availability or integrity |
| **Event** | An observable occurrence in an information system that may or may not indicate an incident |
| **Indicator of Compromise (IOC)** | An artifact or observable that indicates a system has been compromised |
| **Containment** | Actions taken to limit the scope and impact of an incident |
| **Eradication** | Removal of the root cause and all adversary artifacts from the environment |
| **Recovery** | Restoration of affected systems to normal operational status |
| **Break-glass** | Emergency access procedure that bypasses standard authentication controls |
| **JIT (Just-in-Time)** | Temporary privilege elevation with automatic expiration |

---

*Policy ID: POL-IR-001 | Version 1.0 | Classification: Internal Use Only*
