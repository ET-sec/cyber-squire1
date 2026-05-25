# Security Awareness and Training Policy

**Document ID:** GRC-SA-001
**Version:** 1.0
**Classification:** Internal Use Only
**Effective Date:** 2026-03-11
**Review Cycle:** Annual (next review: 2027-03-11)
**Owner:** Information Security Officer
**NIST 800-53 Controls:** AT-1, AT-2, AT-3, AT-4, PM-13

---

## 1. Purpose

This Security Awareness and Training Policy establishes the requirements for security education, training, and awareness across all roles that interact with the Organization's security operations platform. The policy ensures that all personnel understand their security responsibilities, can identify and report threats, and follow established procedures for secret handling, access management, and incident response.

Effective security awareness is a critical compensating control. Technical controls alone cannot prevent social engineering, credential mishandling, or procedural errors. This policy ensures the human element of security is addressed with the same rigor as technical controls.

---

## 2. Scope

This policy applies to all individuals who:

- Have access to `alpha-node` or any of the 19 containerized services
- Have access to the code repository platform, CI/CD pipelines, or infrastructure-as-code definitions
- Have access to the secrets manager, credential vault, or production secret material
- Manage, operate, or audit the security operations platform
- Have access to monitoring, detection, or audit log systems

---

## 3. Roles and Responsibilities

| Role | Training Responsibility |
|------|----------------------|
| Information Security Officer | Policy owner; training program design; training record maintenance; annual review |
| System Owner | Complete required training; maintain role-specific technical competencies |
| Auditor | Complete required training; verify training compliance; review training records |

---

## 4. Training Requirements by Role

### 4.1 Administrator Role

Personnel with the Administrator role have full access to all platform systems, including infrastructure provisioning, secret management, and access control configuration.

**Required Training:**

| Training Module | Frequency | Duration | Delivery Method |
|----------------|-----------|----------|-----------------|
| Security Fundamentals | On hire + annual refresh | 2 hours | Self-paced + assessment |
| Secret Management and Handling | On hire + annual refresh | 1 hour | Self-paced + practical exercise |
| Incident Response Procedures | On hire + annual refresh | 1 hour | Self-paced + tabletop exercise |
| Infrastructure-as-Code Security | On hire + annual refresh | 1 hour | Self-paced + assessment |
| Container Security Essentials | On hire + annual refresh | 1 hour | Self-paced + assessment |
| Change Management Process | On hire + annual refresh | 30 minutes | Policy review + acknowledgment |
| Social Engineering and Phishing Defense | On hire + semi-annual refresh | 30 minutes | Self-paced + simulated exercise |
| Physical Security Awareness | On hire + annual refresh | 30 minutes | Self-paced + assessment |
| Vulnerability Management Process | On hire + annual refresh | 30 minutes | Policy review + acknowledgment |
| Disaster Recovery Procedures | On hire + annual refresh | 1 hour | Self-paced + tabletop exercise |

**Total annual training commitment:** ~9 hours

### 4.2 Operator Role

Personnel with the Operator role interact with the platform through defined workflows. They use `svc-automation` for task execution, access systems through `svc-gateway` with session recording, and operate within JIT access windows.

**Required Training:**

| Training Module | Frequency | Duration | Delivery Method |
|----------------|-----------|----------|-----------------|
| Security Fundamentals | On hire + annual refresh | 2 hours | Self-paced + assessment |
| Secret Management and Handling | On hire + annual refresh | 1 hour | Self-paced + practical exercise |
| Incident Reporting Procedures | On hire + annual refresh | 30 minutes | Self-paced + assessment |
| Session Recording Awareness | On hire (one-time) | 15 minutes | Policy review + acknowledgment |
| JIT Access Procedures | On hire + annual refresh | 30 minutes | Self-paced + practical exercise |
| Social Engineering and Phishing Defense | On hire + semi-annual refresh | 30 minutes | Self-paced + simulated exercise |
| Physical Security Awareness | On hire + annual refresh | 30 minutes | Self-paced + assessment |
| Acceptable Use Policy | On hire + annual refresh | 15 minutes | Policy review + acknowledgment |

**Total annual training commitment:** ~5.5 hours

### 4.3 Auditor Role

Personnel with the Auditor role have read-only access to audit logs, monitoring dashboards, detection findings, and compliance documentation. They do not modify configurations or execute operational tasks.

**Required Training:**

| Training Module | Frequency | Duration | Delivery Method |
|----------------|-----------|----------|-----------------|
| Security Fundamentals | On hire + annual refresh | 2 hours | Self-paced + assessment |
| Secret Management and Handling | On hire + annual refresh | 30 minutes | Self-paced (awareness level, not practitioner) |
| Incident Reporting Procedures | On hire + annual refresh | 30 minutes | Self-paced + assessment |
| Audit Log Integrity and Interpretation | On hire + annual refresh | 1 hour | Self-paced + practical exercise |
| Session Recording Awareness | On hire (one-time) | 15 minutes | Policy review + acknowledgment |
| Social Engineering and Phishing Defense | On hire + semi-annual refresh | 30 minutes | Self-paced + simulated exercise |
| Physical Security Awareness | On hire + annual refresh | 30 minutes | Self-paced + assessment |
| GRC Policy Familiarization | On hire + annual refresh | 1 hour | Policy review + assessment |

**Total annual training commitment:** ~6.5 hours

---

## 5. Onboarding Training

### 5.1 Requirements

All new personnel SHALL complete the following onboarding training within 14 calendar days of receiving platform access:

1. **Security Fundamentals** - organizational security posture, threat landscape, defense-in-depth architecture
2. **Role-specific training modules** - all modules listed for the assigned role in Section 4
3. **Policy acknowledgment** - signed acknowledgment of all applicable GRC policies

### 5.2 Access Restriction

- Platform access SHALL NOT be granted until the Security Fundamentals module is completed
- Elevated access (Administrator role) SHALL NOT be granted until ALL administrator training modules are completed
- JIT access privileges SHALL NOT be granted until the JIT Access Procedures module is completed

### 5.3 Onboarding Checklist

| Step | Action | Completed By | Verified By |
|------|--------|-------------|-------------|
| 1 | Account created in `svc-identity` with appropriate role | Information Security Officer | - |
| 2 | Security Fundamentals training completed | New personnel | Information Security Officer |
| 3 | Role-specific training modules completed | New personnel | Information Security Officer |
| 4 | Secret handling procedures reviewed and acknowledged | New personnel | Information Security Officer |
| 5 | Session recording notification provided and acknowledged | New personnel | Information Security Officer |
| 6 | GRC policies reviewed and acknowledged | New personnel | Information Security Officer |
| 7 | Platform access activated in `svc-gateway` | Information Security Officer | - |
| 8 | First session conducted under supervision | New personnel | Information Security Officer |

---

## 6. Ongoing Training

### 6.1 Annual Refresh

All personnel SHALL complete an annual training refresh within 30 calendar days of their training anniversary date. The refresh covers:

- Updated threat landscape and emerging risks
- Changes to organizational policies since last training
- Lessons learned from incidents or near-misses in the preceding year
- Updated procedures for any modified platform capabilities

### 6.2 Semi-Annual Social Engineering Training

Social engineering and phishing defense training SHALL be delivered semi-annually (every 6 months) to all roles. This training SHALL include:

- Current social engineering tactics, techniques, and procedures (TTPs)
- Phishing email identification (header analysis, URL inspection, sender verification)
- Pretexting and impersonation scenarios relevant to security operations
- Reporting procedures for suspected social engineering attempts
- Simulated phishing exercises with tracking of response rates

### 6.3 Event-Triggered Training

Additional training SHALL be delivered when:

| Trigger | Training Required | Audience | Timeframe |
|---------|------------------|----------|-----------|
| Security incident occurs | Incident lessons learned briefing | All personnel | Within 14 days of incident closure |
| New service deployed | Service-specific operational training | Administrators, affected Operators | Before production access granted |
| Policy change | Updated policy review and acknowledgment | All personnel | Within 30 days of policy effective date |
| New vulnerability class identified | Targeted awareness briefing | Administrators | Within 14 days of identification |
| Failed phishing simulation | Remedial phishing awareness training | Affected individual | Within 7 days of failure |
| Role change | Training for new role | Affected individual | Before new role access granted |

---

## 7. Training Topics

### 7.1 Secret Management and Handling

**Objective:** Ensure all personnel understand how to safely access, use, and protect secret material.

**Topics covered:**

- Secrets manager architecture and usage (CLI-based secret injection and retrieval)
- Credential vault usage for offline secret storage
- Rules for secret handling:
 - NEVER echo, print, log, or display secret values
 - NEVER commit secrets to the code repository
 - NEVER include secrets in chat messages, emails, or documentation
 - NEVER store secrets in plaintext files on any system
 - Verify secret availability by checking existence, not value: `[ -n "$VAR" ] && echo "set"`
- Secret rotation procedures
- What to do if a secret is accidentally exposed (immediate rotation, incident report)
- How the credential scanner in the CI pipeline prevents committed secrets
- Environment variable safety (never run `env`, `printenv`, `export -p`, or `set`)

### 7.2 Incident Reporting Procedures

**Objective:** Ensure all personnel can recognize and report security incidents promptly.

**Topics covered:**

- Definition of a security incident vs. a security event
- Examples of reportable incidents:
 - Unauthorized access or access attempts
 - Suspected credential compromise
 - Unexpected system behavior or alerts
 - Social engineering attempts
 - Data loss or unauthorized data access
 - Detection engine alerts indicating compromise
- Reporting channels and escalation path
- Information to include in an incident report
- Preservation of evidence (do not modify affected systems)
- Non-retaliation policy for good-faith reporting

### 7.3 Acceptable Use

**Objective:** Define permitted and prohibited uses of the security operations platform.

**Topics covered:**

- Platform systems are for authorized operational purposes only
- Personal use of platform resources is prohibited
- All sessions through `svc-gateway` are recorded and subject to review
- JIT access is granted for specific tasks and time windows; access beyond the granted window is prohibited
- Modification of detection rules, monitoring configuration, or audit logs outside the change management process is prohibited
- Use of `svc-llm` or `svc-ai-gateway` is restricted to authorized operational tasks
- Sharing of credentials, tokens, or access methods is prohibited

### 7.4 Social Engineering and Phishing Defense

**Objective:** Build resilience against human-targeted attack vectors.

**Topics covered:**

- Common social engineering tactics:
 - Phishing (email, SMS, voice)
 - Pretexting and impersonation
 - Baiting (USB drops, malicious downloads)
 - Tailgating and physical social engineering
- Red flags in communications:
 - Urgency or pressure to bypass procedures
 - Requests for credentials or secret material
 - Unexpected attachments or links
 - Sender address discrepancies
- Verification procedures:
 - Out-of-band verification for sensitive requests
 - URL inspection before clicking
 - Attachment scanning before opening
- Reporting suspected social engineering (even if uncertain)

### 7.5 Physical Security Awareness

**Objective:** Protect physical access to systems and workstations that can access the platform.

**Topics covered:**

- Workstation lock requirements (screen lock when unattended)
- Clean desk policy (no secrets, credentials, or access notes visible)
- Secure disposal of printed material containing operational information
- Visitor awareness in work areas
- Reporting lost or stolen devices that have platform access (SSH keys, VPN configs, credential vault access)
- Multi-factor authentication requirements for platform access
- Travel security (VPN requirements, public Wi-Fi risks, device encryption)

### 7.6 Session Recording Awareness

**Objective:** Ensure all personnel understand that their privileged sessions are recorded.

**Topics covered:**

- All SSH sessions through `svc-gateway` are recorded (video and command log)
- Session recordings are stored as immutable audit logs
- Recordings are used for:
 - Post-incident forensic analysis
 - Compliance audit evidence
 - Operational troubleshooting (with authorization)
- Recordings are NOT used for performance monitoring
- Personnel have been notified and acknowledge recording (this training constitutes notification)
- Recordings are retained per the Organization's data retention schedule

### 7.7 JIT Access Procedures

**Objective:** Ensure personnel understand the just-in-time access model.

**Topics covered:**

- Access is not standing; it must be requested for each session
- JIT request includes: resource, justification, and duration
- Access is automatically revoked when the time window expires
- If more time is needed, a new request must be submitted (do not extend by other means)
- All JIT requests are logged and auditable
- Requests for access beyond the minimum necessary will be denied
- Emergency access procedures (documented in GRC-CM-001, Section 9)

---

## 8. Training Delivery Methods

### 8.1 Self-Paced Modules

- Delivered via documentation, recorded presentations, or interactive content
- Include knowledge assessment (minimum passing score: 80%)
- May be repeated until passing score is achieved
- Completion is automatically recorded

### 8.2 Practical Exercises

- Hands-on exercises in a non-production environment
- Examples:
 - Rotate a secret using the secrets manager
 - File a simulated incident report
 - Request and use JIT access through `svc-gateway`
 - Identify a phishing email from a set of samples
- Completion verified by instructor or automated system

### 8.3 Tabletop Exercises

- Scenario-based group discussions
- Used for incident response and disaster recovery training
- Facilitated by the Information Security Officer
- Documented with attendance, scenario, discussion points, and action items

### 8.4 Simulated Exercises

- Phishing simulations conducted semi-annually
- Metrics tracked: click rate, report rate, time to report
- Personnel who fail simulations receive targeted remedial training within 7 days

---

## 9. Training Records

### 9.1 Record Requirements (NIST 800-53 AT-4)

The Organization SHALL maintain training records for all personnel. Records SHALL include:

| Field | Description |
|-------|-------------|
| Personnel identifier | Name or unique identifier |
| Role | Administrator, Operator, or Auditor |
| Training module | Name and version of the completed module |
| Completion date | Date the module was completed |
| Assessment score | Score on knowledge assessment (if applicable) |
| Delivery method | Self-paced, practical, tabletop, or simulated |
| Expiration date | Date by which the next refresh is required |
| Acknowledgments | Policy acknowledgments signed |

### 9.2 Record Retention

- Training records SHALL be retained for a minimum of 3 years after the personnel's last active date
- Records of policy acknowledgments SHALL be retained for the life of the policy version plus 1 year
- Records SHALL be stored in a location accessible to the Information Security Officer and Auditor
- Records SHALL be included in the Organization's backup strategy

### 9.3 Compliance Monitoring

The Information Security Officer SHALL review training compliance monthly:

- Identify personnel with overdue training
- Issue reminders at 14 days before expiration
- Escalate non-compliance at 30 days past expiration
- Platform access MAY be suspended for personnel more than 60 days past training expiration

---

## 10. Security Awareness Program (NIST 800-53 PM-13)

### 10.1 Program Objectives

The Organization's security awareness program aims to:

1. Establish a security-conscious culture where all personnel consider security implications in their daily operations
2. Reduce the likelihood of successful social engineering attacks
3. Ensure timely incident reporting
4. Maintain procedural compliance with secret handling and access management policies
5. Keep personnel informed of evolving threats relevant to the platform

### 10.2 Awareness Activities

In addition to formal training, the following awareness activities SHALL be conducted:

| Activity | Frequency | Description |
|----------|-----------|-------------|
| Threat intelligence briefing | Monthly | Summary of relevant threats, vulnerabilities, and incidents affecting similar organizations |
| Lessons learned distribution | After incidents | Anonymized incident summaries with actionable takeaways |
| Policy reminder communications | Quarterly | Brief reminders of key policies and procedures |
| Phishing simulation results | Semi-annual | Aggregated results (not individual) shared to raise awareness |
| New vulnerability advisories | As needed | Targeted alerts when critical vulnerabilities affect deployed software |

### 10.3 Program Effectiveness Measurement

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Training completion rate | 100% within required timeframe | Training record review |
| Phishing simulation click rate | < 5% | Simulation platform reporting |
| Phishing simulation report rate | > 80% | Simulation platform reporting |
| Mean time to report simulated phishing | < 30 minutes | Simulation platform reporting |
| Incident reporting rate | Trending upward (indicates awareness, not weakness) | Incident log review |
| Policy acknowledgment rate | 100% | Training record review |

---

## 11. Policy Violations

### 11.1 Non-Compliance Consequences

Failure to complete required training or comply with security awareness requirements may result in:

| Non-Compliance | Consequence |
|---------------|-------------|
| Training overdue by 30 days | Written reminder and escalation to Information Security Officer |
| Training overdue by 60 days | Platform access suspended pending completion |
| Repeated failure of phishing simulations (3+ consecutive) | Mandatory one-on-one remedial training |
| Deliberate policy violation (e.g., sharing credentials) | Access revocation; investigation per incident response procedures |
| Failure to report a known security incident | Review by Information Security Officer; potential access revocation |

### 11.2 Good-Faith Reporting Protection

Personnel who report security incidents, policy violations, or concerns in good faith SHALL NOT face negative consequences, even if:

- The report turns out to be a false alarm
- The reporter was involved in the incident (self-reporting is encouraged)
- The report reveals a gap in existing controls

---

## 12. Policy Review and Updates

### 12.1 Review Schedule

This policy SHALL be reviewed:

- Annually (at minimum)
- After any security incident that reveals a training gap
- When new services are added to the platform
- When roles or access models change
- When regulatory or compliance requirements change

### 12.2 Review Process

1. Information Security Officer initiates review
2. Training effectiveness metrics are analyzed (Section 10.3)
3. Incident reports are reviewed for training-related root causes
4. Training content is updated to address identified gaps
5. Updated policy is distributed per change management process (GRC-CM-001)

---

## 13. Coordination with Other Policies

| Policy | Relationship |
|--------|-------------|
| GRC-CM-001 (Change Management) | Training on change management process is required for Administrators |
| GRC-BCP-001 (Business Continuity) | Disaster recovery tabletop exercises serve as both BCP testing and training |
| GRC-DRP-001 (Disaster Recovery) | Recovery procedures training ensures personnel can execute playbooks |
| GRC-VM-001 (Vulnerability Management) | Training includes vulnerability reporting procedures and secure development |

---

## 14. Document Control

| Field | Value |
|-------|-------|
| Document ID | GRC-SA-001 |
| Version | 1.0 |
| Status | Approved |
| Author | Information Security Officer |
| Approved By | System Owner |
| Effective Date | 2026-03-11 |
| Next Review | 2027-03-11 |
| Classification | Internal Use Only |
| Distribution | Information Security Officer, System Owner, Auditor |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-03-11 | Information Security Officer | Initial release |

---

*This document is the property of the Organization. Unauthorized distribution is prohibited.*

---

## Cross-References

| Document | Relationship |
|----------|-------------|
| [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) | System Security Plan with NIST 800-53 control mapping |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | Tracks findings and remediation milestones |
| [README.md](README.md) | GRC library index and reading guide |
