# Risk Assessment

**Organization:** Organization Security Operations Platform
**Assessment Date:** 2026-03-11
**Assessor:** System Owner
**Methodology:** NIST SP 800-30 Rev. 1 (Guide for Conducting Risk Assessments)
**NIST 800-53 Controls:** RA-1 (Risk Assessment Policy), RA-2 (Security Categorization), RA-3 (Risk Assessment), RA-5 (Vulnerability Monitoring and Scanning)
**Classification:** Internal Use Only
**Version:** 1.0

> **Status note (2026-09-01):** this document describes the DigitalOcean-era baseline as assessed. That environment was retired 2026-08. The platform now runs on an Oracle Cloud (OCI) ARM instance with a partial stack (3 containers live); the remaining services are pending ARM rebuild. A re-baseline of this document is queued and tracked in the POA&M.

---

## 1. Purpose and Scope

### 1.1 Purpose

This risk assessment identifies, analyzes, and evaluates information security risks to the Organization security operations platform. It provides a structured basis for risk treatment decisions and informs the Plan of Action and Milestones (POA&M) for residual findings.

### 1.2 Scope

This assessment covers the following assets and boundaries:

| Boundary | Description |
|----------|-------------|
| **Compute** | Single VPS (4 vCPU, 8 GB RAM, 160 GB disk) running Ubuntu 24.04 LTS |
| **Containers** | 20 containers across 3 Docker networks (net-core, net-ai, net-monitoring) |
| **Network** | Zero-trust tunnel (sole public ingress), cloud firewall (deny-all default) |
| **IAM** | 3-tier RBAC via svc-identity and svc-gateway |
| **Secrets** | External secrets manager injecting environment variables at runtime |
| **CI/CD** | 6 security scanners, 8 OPA (Rego) policies enforced on all pull requests |
| **Monitoring** | Observability agent, eBPF runtime detection, immutable audit log chain |
| **IaC** | Infrastructure-as-code with remote encrypted state |

**Out of scope:** End-user workstations, third-party SaaS platforms (beyond their integration points), and physical security of DigitalOcean's data centers.

### 1.3 Security Categorization (FIPS 199)

| Security Objective | Impact Level | Justification |
|-------------------|--------------|---------------|
| **Confidentiality** | Moderate | Platform processes API keys, credentials, and operational telemetry |
| **Integrity** | Moderate | Workflow logic and infrastructure state must remain trustworthy |
| **Availability** | Moderate | Single-operator platform; short outages are tolerable |

**Overall categorization:** Moderate

---

## 2. Risk Assessment Methodology

This assessment follows NIST SP 800-30 Rev. 1 using a semi-quantitative 5x5 risk matrix.

### 2.1 Likelihood Scale

| Rating | Value | Definition |
|--------|-------|------------|
| **Very Low** | 1 | Threat event is unlikely to occur (less than once per 5 years) |
| **Low** | 2 | Threat event could occur but is not expected (once per 1-5 years) |
| **Moderate** | 3 | Threat event is somewhat likely (once per year) |
| **High** | 4 | Threat event is likely to occur (multiple times per year) |
| **Very High** | 5 | Threat event is almost certain (monthly or more frequent) |

### 2.2 Impact Scale

| Rating | Value | Definition |
|--------|-------|------------|
| **Very Low** | 1 | Negligible effect on operations, assets, or individuals |
| **Low** | 2 | Limited adverse effect; minor degradation of capability |
| **Moderate** | 3 | Serious adverse effect; significant degradation of capability |
| **High** | 4 | Severe adverse effect; major damage to assets or operations |
| **Very High** | 5 | Catastrophic effect; complete loss of capability or major breach |

### 2.3 Risk Calculation

```
Risk Score = Likelihood x Impact
```

### 2.4 Risk Rating Thresholds

| Risk Score | Rating | Action Required |
|-----------|--------|----------------|
| 1 - 6 | **Low** | Accept with documentation; monitor during regular reviews |
| 7 - 14 | **Moderate** | Mitigate within 90 days; document compensating controls |
| 15 - 19 | **High** | Mitigate within 30 days; escalate to System Owner |
| 20 - 25 | **Critical** | Immediate action required; halt affected operations if necessary |

---

## 3. Threat Catalog

### 3.1 External Threats

| ID | Threat | Description | MITRE ATT&CK |
|----|--------|-------------|---------------|
| T-01 | Distributed Denial of Service | Volumetric or application-layer attack against public ingress | T1498, T1499 |
| T-02 | Brute Force / Credential Stuffing | Automated attempts against authentication endpoints | T1110 |
| T-03 | Supply Chain Compromise (Container Images) | Malicious code injected into upstream base images | T1195.002 |
| T-04 | Web Application Exploitation | Injection, SSRF, or deserialization attacks against automation webhooks | T1190 |
| T-05 | Credential Theft (Phishing / Social Engineering) | Targeted attack to obtain operator credentials | T1566 |
| T-06 | Zero-Day Exploitation | Exploitation of unknown vulnerability in exposed services | T1068 |

### 3.2 Internal Threats

| ID | Threat | Description | MITRE ATT&CK |
|----|--------|-------------|---------------|
| T-07 | Container Misconfiguration | Overly permissive capabilities, missing security flags, exposed ports | T1610 |
| T-08 | Privilege Escalation | Container breakout or escalation from operator to root | T1068, T1611 |
| T-09 | Insider Threat | Malicious or negligent action by authorized user | T1078 |
| T-10 | Accidental Secret Exposure | Credentials committed to code repository or leaked in logs | T1552 |
| T-11 | Unauthorized Configuration Change | Unreviewed modification to IaC, Docker Compose, or firewall rules | T1562 |

### 3.3 Environmental Threats

| ID | Threat | Description |
|----|--------|-------------|
| T-12 | DigitalOcean Outage | Availability zone or regional outage affecting the VPS |
| T-13 | Hardware Failure | Disk corruption, memory failure, or hypervisor fault |
| T-14 | Data Loss | Loss of persistent volumes (database, svc-secrets, configurations) |

### 3.4 Compliance Threats

| ID | Threat | Description |
|----|--------|-------------|
| T-15 | Regulatory / Framework Changes | New compliance requirements requiring architectural changes |
| T-16 | Audit Finding Remediation Failure | Failure to close POA&M items within documented timelines |
| T-17 | Breach Notification Obligation | Legal requirement to notify affected parties after a data breach |

---

## 4. Risk Register

### 4.1 External Threats

| Risk ID | Threat | Threat Source | Vulnerability | Affected Assets | Likelihood | Impact | Inherent Risk | Current Controls | Residual Likelihood | Residual Impact | Residual Risk |
|---------|--------|---------------|---------------|-----------------|------------|--------|---------------|-----------------|-------------------|----------------|---------------|
| R-01 | DDoS (T-01) | External adversary | Single VPS, single ingress point | svc-tunnel, all services | 3 | 3 | **9 (Mod)** | Cloudflare DDoS protection; cloud firewall deny-all; rate limiting at tunnel | 2 | 3 | **6 (Low)** |
| R-02 | Brute Force (T-02) | External adversary | Authentication endpoints exposed via tunnel | svc-automation, svc-gateway | 4 | 3 | **12 (Mod)** | TOTP MFA on svc-gateway; password policy in svc-identity; session TTL limits; fail2ban equivalent at tunnel | 2 | 3 | **6 (Low)** |
| R-03 | Supply Chain - Container Images (T-03) | Nation-state / organized crime | Use of upstream Docker images | All 19 containers | 2 | 5 | **10 (Mod)** | Container image CVE scanning in CI; container signing tool; pinned image digests; SAST scanner on Dockerfiles | 1 | 5 | **5 (Low)** |
| R-04 | Webhook Exploitation (T-04) | External adversary | Automation platform accepts webhook payloads from internet | svc-automation, svc-tunnel | 3 | 4 | **12 (Mod)** | Webhook authentication tokens; input validation in workflow logic; svc-detection monitors for shell spawns; no-new-privileges on container | 2 | 4 | **8 (Mod)** |
| R-05 | Credential Phishing (T-05) | External adversary | Human factor - operator targeted | Operator credentials, MFA seeds | 2 | 4 | **8 (Mod)** | TOTP MFA (hardware token recommended); session recording; JIT admin with 4h TTL; credential vault with biometric lock | 1 | 4 | **4 (Low)** |
| R-06 | Zero-Day Exploit (T-06) | Nation-state / advanced adversary | Unpatched vulnerabilities in exposed services | svc-tunnel, svc-automation | 1 | 5 | **5 (Low)** | Minimal attack surface (only tunnel exposed); eBPF runtime detection; immutable audit logs; container isolation | 1 | 5 | **5 (Low)** |

### 4.2 Internal Threats

| Risk ID | Threat | Threat Source | Vulnerability | Affected Assets | Likelihood | Impact | Inherent Risk | Current Controls | Residual Likelihood | Residual Impact | Residual Risk |
|---------|--------|---------------|---------------|-----------------|------------|--------|---------------|-----------------|-------------------|----------------|---------------|
| R-07 | Container Misconfiguration (T-07) | Operator error | Docker Compose complexity; 19 services to configure | All containers | 3 | 3 | **9 (Mod)** | CIS Docker Bench scans (37 PASS); OPA (Rego) policies (8 rules); no-new-privileges on 18/19 containers; resource limits; Checkov in CI | 2 | 3 | **6 (Low)** |
| R-08 | Privilege Escalation (T-08) | External/internal adversary | Container with elevated capabilities (svc-detection requires SYS_ADMIN) | svc-detection, host kernel | 2 | 5 | **10 (Mod)** | Only svc-detection has SYS_ADMIN (required for eBPF); all others run no-new-privileges; PID limits; read-only rootfs where feasible; Teleport session recording on SSH | 1 | 5 | **5 (Low)** |
| R-09 | Insider Threat (T-09) | Authorized user | Single-operator environment limits but does not eliminate risk | All infrastructure | 1 | 5 | **5 (Low)** | Session recording on all SSH; immutable audit log with hash chain; JIT admin access (4h TTL); monthly access reviews | 1 | 4 | **4 (Low)** |
<!-- TODO(et): "log rotation (10MB x 3)" bounds local cache size only and does not prevent secret exposure. Reword control or remove. -->
| R-10 | Accidental Secret Exposure (T-10) | Operator error | Secrets in environment variables could leak via logs or debug output | API keys, database credentials, tokens | 3 | 5 | **15 (High)** | External secrets manager (never hardcoded); Gitleaks in CI; log rotation (10MB x 3); .gitignore for sensitive files; env var validation (existence checks only) | 2 | 5 | **10 (Mod)** |
| R-11 | Unauthorized Config Change (T-11) | Operator error / adversary | IaC state drift or unreviewed changes | Infrastructure-as-code state, Docker Compose, firewall | 2 | 4 | **8 (Mod)** | IaC remote state with encryption; mandatory PR reviews; Checkov + Terraform linter in CI; policy engine enforcement | 1 | 4 | **4 (Low)** |

### 4.3 Environmental Threats

| Risk ID | Threat | Threat Source | Vulnerability | Affected Assets | Likelihood | Impact | Inherent Risk | Current Controls | Residual Likelihood | Residual Impact | Residual Risk |
|---------|--------|---------------|---------------|-----------------|------------|--------|---------------|-----------------|-------------------|----------------|---------------|
| R-12 | DigitalOcean Outage (T-12) | Cloud provider | Single VPS, single region, no failover | All services | 2 | 4 | **8 (Mod)** | Datadog alerts on host downtime; documented recovery procedures; IaC enables rapid redeployment to alternate region | 2 | 3 | **6 (Low)** |
| R-13 | Hardware Failure (T-13) | Infrastructure | Hypervisor-managed hardware; limited control | VPS, persistent volumes | 1 | 4 | **4 (Low)** | Cloud provider SLA (99.99%); automated backups of database; IaC for infrastructure rebuild | 1 | 3 | **3 (Low)** |
<!-- TODO(et): "PostgreSQL backup scripts (CD_BACKUPS volume)" verify backup cron actually runs against current stack. Compose only mounts ./CD_BACKUPS:/backups:z; script source not confirmed. -->
| R-14 | Data Loss (T-14) | Multiple (failure, attack, error) | Single-node persistent volumes; no off-site replication | svc-db data, svc-secrets data, configurations | 2 | 5 | **10 (Mod)** | PostgreSQL backup scripts (CD_BACKUPS volume); secrets stored in external manager (authoritative copy outside VPS); IaC for config rebuild; no automated off-site replication yet | 2 | 4 | **8 (Mod)** |

### 4.4 Compliance Threats

| Risk ID | Threat | Threat Source | Vulnerability | Affected Assets | Likelihood | Impact | Inherent Risk | Current Controls | Residual Likelihood | Residual Impact | Residual Risk |
|---------|--------|---------------|---------------|-----------------|------------|--------|---------------|-----------------|-------------------|----------------|---------------|
| R-15 | Regulatory Changes (T-15) | Government / industry bodies | Architecture may not meet new requirements | Platform design, documentation | 2 | 3 | **6 (Low)** | Modular architecture supports component replacement; quarterly framework review; NIST 800-53 alignment provides broad coverage | 2 | 2 | **4 (Low)** |
<!-- TODO(et): "96 CIS Docker Bench WARNs with 29 documented compensating controls" reflects 2026-03-11 baseline. Stack added Squire/NeMo/Langfuse/Teleport/Vault containers since; re-run CIS Bench and refresh. -->
| R-16 | POA&M Remediation Failure (T-16) | Process gap | 96 CIS Docker Bench WARNs with 29 documented compensating controls | Compliance posture, audit readiness | 3 | 3 | **9 (Mod)** | CIS Risk Register with documented compensating controls; 90-day review cycle; POA&M tracking | 2 | 3 | **6 (Low)** |
| R-17 | Breach Notification (T-17) | Data breach event | No formal incident notification procedure for external parties | Legal compliance, reputation | 1 | 5 | **5 (Low)** | Incident response procedure documented; tabletop exercises (semi-annual); audit log preservation for forensics | 1 | 4 | **4 (Low)** |

---

## 5. Risk Heat Map

```
               I M P A C T
       Very Low (1)  Low (2)  Moderate (3)  High (4)  Very High (5)
      +------------+-----------+--------------+-----------+--------------+
 Very    |      |      |       |      |       |
 High (5)  |      |      |       |      |       |
      +------------+-----------+--------------+-----------+--------------+
      |      |      |       |  R-04  |       |
 High (4)  |      |      |       | (resid) |       |
      +------------+-----------+--------------+-----------+--------------+
      |      |      | R-01 R-07  |  R-04  | R-10    |
 Moderate  |      |      | R-02 R-16  |      | (inherent)  |
 (3)    |      |      | (inherent)  | (inherent)|       |
      +------------+-----------+--------------+-----------+--------------+
      |      |      | R-01 R-02  |  R-05  | R-03 R-08 |
 Low (2)  |      |      | R-07 R-16  |  R-11  | R-10 R-14 |
      |      |      | (residual)  |  R-12  | (residual)  |
      +------------+-----------+--------------+-----------+--------------+
      |      |      |       |  R-09  | R-06 R-13 |
 Very    |      | R-15   |       |  R-17  | R-08 R-03 |
 Low (1)  |      | (resid)  |       | (residual)| R-09 R-06 |
      +------------+-----------+--------------+-----------+--------------+

LEGEND:
 Likelihood is on the Y-axis (rows), Impact on the X-axis (columns).
 Risks shown at their INHERENT position unless marked (residual) or (resid).
 Multiple risks may share a cell.

RISK RATING:
 [1-6]  Low    - within acceptance threshold
 [7-14] Moderate  - mitigate within 90 days
 [15-19] High    - mitigate within 30 days
 [20-25] Critical  - immediate action required
```

### Risk Distribution Summary

| Rating | Count (Inherent) | Count (Residual) |
|--------|-----------------|-----------------|
| **Critical (20-25)** | 0 | 0 |
| **High (15-19)** | 1 (R-10) | 0 |
| **Moderate (7-14)** | 11 (R-01, R-02, R-03, R-04, R-05, R-07, R-08, R-11, R-12, R-14, R-16) | 3 (R-04, R-10, R-14) |
| **Low (1-6)** | 5 (R-06, R-09, R-13, R-15, R-17) | 14 |

---

## 6. Top Risks Summary

The following five risks carry the highest residual risk scores after current controls are applied.

### Rank 1: R-10 - Accidental Secret Exposure (Residual: 10 - Moderate)

**Why it matters:** Secrets injected as environment variables are accessible to any process inside a container. A debug command, misconfigured log level, or core dump could expose credentials to logs or monitoring streams.

**Recommended actions:**
1. Implement runtime secrets injection via mounted files (tmpfs) rather than environment variables
2. Deploy log scrubbing rules in Fluentd to redact patterns matching API keys and tokens
3. Add automated secret scanning to container runtime logs (not just CI)
4. Establish a credential rotation runbook with maximum 24-hour rotation SLA after suspected exposure

### Rank 2: R-04 - Webhook Exploitation (Residual: 8 - Moderate)

**Why it matters:** The automation platform accepts webhook payloads through the zero-trust tunnel. A crafted payload exploiting a deserialization or injection flaw could achieve remote code execution inside the automation container, which has database credentials in its environment.

**Recommended actions:**
1. Implement webhook payload schema validation at the tunnel layer (before reaching the automation container)
2. Deploy a WAF rule set at Cloudflare for webhook endpoints
3. Restrict automation container's network egress to only required destinations (svc-db, specific API endpoints)
4. Implement webhook request signing with HMAC verification

### Rank 3: R-14 - Data Loss (Residual: 8 - Moderate)

**Why it matters:** Database volumes and secrets engine data exist on a single VPS with no automated off-site replication. A simultaneous disk failure and backup corruption would result in permanent data loss.

**Recommended actions:**
1. Implement automated daily database backups to encrypted object storage (off-VPS)
2. Add backup integrity verification (restore testing) on a monthly schedule
3. Document Recovery Point Objective (RPO) and Recovery Time Objective (RTO) targets
4. Implement volume snapshot scheduling at DigitalOcean level

### Rank 4: R-12 - DigitalOcean Outage (Residual: 6 - Low)

**Why it matters:** All 19 services run on a single VPS in a single region. A prolonged regional outage would render the entire platform unavailable with no automatic failover.

**Recommended actions:**
1. Document a warm-standby deployment procedure for an alternate region using IaC
2. Pre-stage encrypted database backups in a second region
3. Define and test RTO targets (current estimated RTO: 2-4 hours for IaC redeployment)
4. Evaluate multi-region architecture as the platform scales

### Rank 5: R-16 - POA&M Remediation Failure (Residual: 6 - Low)

**Why it matters:** The CIS Docker Bench scan identified 96 WARN findings. While 29 have documented compensating controls, the remaining findings require either remediation or formal risk acceptance. Drift from the remediation schedule erodes the compliance posture.

**Recommended actions:**
1. Prioritize the top 10 WARN findings by risk score and create remediation tickets
2. Automate CIS Docker Bench scans on a weekly schedule with delta reporting
3. Integrate POA&M tracking into the automation platform with due-date alerts
4. Conduct a focused review of compensating controls every 90 days

---

## 7. Risk Treatment Plan

| Risk ID | Risk Rating (Residual) | Treatment | Action | Owner | Target Date | Status |
|---------|----------------------|-----------|--------|-------|-------------|--------|
| R-01 | Low (6) | **Accept** | Existing controls are sufficient. Monitor edge provider metrics for volumetric anomalies. | System Owner | N/A | Accepted |
| R-02 | Low (6) | **Accept** | MFA and session limits provide adequate protection. Review authentication logs monthly. | System Owner | N/A | Accepted |
| R-03 | Low (5) | **Accept** | CI scanning and image signing reduce supply chain risk to acceptable levels. | System Owner | N/A | Accepted |
<!-- TODO(et): R-04 / R-10 / R-12 / R-14 / R-16 target dates (2026-04-11 through 2026-06-11) past due. Confirm Open status or record closure. -->
| R-04 | Moderate (8) | **Mitigate** | Deploy webhook schema validation and edge WAF rules. Restrict container network egress. | System Owner | 2026-06-11 | Open |
| R-05 | Low (4) | **Accept** | MFA and JIT access provide adequate protection. Evaluate hardware token adoption. | System Owner | N/A | Accepted |
| R-06 | Low (5) | **Accept** | Minimal attack surface and runtime detection are the appropriate controls for zero-days. | System Owner | N/A | Accepted |
| R-07 | Low (6) | **Accept** | CIS scanning and infrastructure policies enforce configuration standards. Continue 90-day review cycle. | System Owner | N/A | Accepted |
| R-08 | Low (5) | **Accept** | Only one container requires elevated capabilities (svc-detection, by design). Documented in POA&M. | System Owner | N/A | Accepted |
| R-09 | Low (4) | **Accept** | Single-operator environment with full session recording. Re-evaluate if team grows. | System Owner | N/A | Accepted |
| R-10 | Moderate (10) | **Mitigate** | Transition from env-var secrets to mounted tmpfs files. Deploy log scrubbing rules. | System Owner | 2026-05-11 | Open |
| R-11 | Low (4) | **Accept** | IaC with encrypted remote state and mandatory PR reviews are sufficient. | System Owner | N/A | Accepted |
| R-12 | Low (6) | **Mitigate** | Document warm-standby procedure and pre-stage backups in second region. | System Owner | 2026-06-11 | Open |
| R-13 | Low (3) | **Accept** | Cloud provider SLA and IaC rebuild capability are sufficient. | System Owner | N/A | Accepted |
| R-14 | Moderate (8) | **Mitigate** | Implement automated off-site backups with integrity verification. | System Owner | 2026-05-11 | Open |
| R-15 | Low (4) | **Accept** | Modular architecture and NIST alignment provide flexibility. Quarterly review. | System Owner | N/A | Accepted |
| R-16 | Low (6) | **Mitigate** | Automate CIS scans with delta reporting. Prioritize top 10 WARN findings. | System Owner | 2026-06-11 | Open |
| R-17 | Low (4) | **Accept** | Incident response and tabletop exercises address notification procedures. | System Owner | N/A | Accepted |

### Treatment Summary

| Treatment | Count | Risks |
|-----------|-------|-------|
| **Accept** | 12 | R-01, R-02, R-03, R-05, R-06, R-07, R-08, R-09, R-11, R-13, R-15, R-17 |
| **Mitigate** | 5 | R-04, R-10, R-12, R-14, R-16 |
| **Transfer** | 0 | - |
| **Avoid** | 0 | - |

---

## 8. Review Schedule

<!-- TODO(et): Quarterly risk register review (2026-06-11), monthly POAM review (2026-04-11), and monthly CIS scan (2026-04-11) are all past due. Refresh next-date column. -->

| Activity | Frequency | Next Date | Owner |
|----------|-----------|-----------|-------|
| Full risk assessment | Annual | 2027-03-11 | System Owner |
| Risk register review | Quarterly | 2026-06-11 | System Owner |
| POA&M status review | Monthly | 2026-04-11 | System Owner |
| Vulnerability scan review | Weekly (automated) | Continuous | CI/CD Pipeline |
| CIS Docker Bench scan | Monthly | 2026-04-11 | System Owner |
| Threat catalog update | Semi-annual | 2026-09-11 | System Owner |

### Triggers for Out-of-Cycle Reassessment

- Any security incident classified as Severity 1 or 2
- Significant architectural change (new public-facing service, provider migration, team expansion)
- New regulatory requirement affecting the platform
- Discovery of a critical vulnerability (CVSS >= 9.0) in a deployed component
- Change in threat landscape (targeted attacks against similar platforms)

---

## 9. Document Control

| Field | Value |
|-------|-------|
| **Document ID** | RA-2026-001 |
| **Version** | 1.0 |
| **Status** | Approved |
| **Author** | System Owner |
| **Approver** | System Owner |
| **Classification** | Internal Use Only |
| **Created** | 2026-03-11 |
| **Last Updated** | 2026-03-11 |
| **Next Review** | 2027-03-11 |

### Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-11 | System Owner | Initial risk assessment |

### References

| Document | Identifier |
|----------|-----------|
| NIST SP 800-30 Rev. 1 | Guide for Conducting Risk Assessments |
| NIST SP 800-53 Rev. 5 | Security and Privacy Controls (RA family) |
| FIPS 199 | Standards for Security Categorization |
| CIS Docker Benchmark Risk Register | Internal - docs/grc/CIS_RISK_REGISTER.md |
| IAM RBAC Role Map | Internal - docs/grc/IAM_RBAC_ROLE_MAP.md |
| IAM Access Review | Internal - docs/grc/IAM_ACCESS_REVIEW.md |

---

*This document is reviewed annually or upon significant change to the platform architecture, threat landscape, or regulatory environment.*

---

## Cross-References

<!-- TODO(et): Add Phase 17 + 19 doc cross-refs (SQUIRE_AI_RISK_ASSESSMENT, SQUIRE_THREAT_MODEL, AI_SUPPLY_CHAIN_RISK, AI_THREAT_CATALOG, ATTACK_TREE_AI_PIPELINE) so readers can navigate from parent RA to AI risks. -->

| Document | Relationship |
|----------|-------------|
| [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) | System Security Plan with NIST 800-53 control mapping |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | Tracks findings and remediation milestones |
| [SQUIRE_AI_RISK_ASSESSMENT.md](SQUIRE_AI_RISK_ASSESSMENT.md) | Child RA covering AI subsystem (Squire SOC analyst) risks R-01 through R-13 |
| [SQUIRE_THREAT_MODEL.md](SQUIRE_THREAT_MODEL.md) | STRIDE plus MITRE ATLAS threat model for Squire components |
| [AI_SUPPLY_CHAIN_RISK.md](AI_SUPPLY_CHAIN_RISK.md) | AI supply chain risk policy (AI-001/002/003 systems) |
| [AI_THREAT_CATALOG.md](AI_THREAT_CATALOG.md) | Platform-wide AI threat catalog (ATC-01 through ATC-10) |
| [ATTACK_TREE_AI_PIPELINE.md](ATTACK_TREE_AI_PIPELINE.md) | Attack-tree decomposition for AI pipeline (Paths 1 through 4) |
| [README.md](README.md) | GRC library index and reading guide |
