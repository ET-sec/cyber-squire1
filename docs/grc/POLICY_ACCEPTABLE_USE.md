# Acceptable Use Policy

**Document ID:** POL-AU-001
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
| Policy Title | Acceptable Use Policy |
| Document ID | POL-AU-001 |
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

This policy defines the standards of acceptable and prohibited behavior for all personnel who access, operate, or administer the Organization security operations platform. It exists to protect the integrity, confidentiality, and availability of Organization systems and data; to establish clear expectations for responsible use; and to ensure compliance with applicable legal, regulatory, and contractual obligations.

All personnel granted access to Organization infrastructure accept the terms of this policy as a condition of that access.

---

## 2. Scope

This policy applies to:

- All personnel with any level of access to Organization infrastructure, regardless of role (admin, operator, auditor)
- All systems, services, and data within the Organization security operations platform, including the primary compute node (`alpha-node`) and all containerized services
- All access methods, including SSH via `svc-gateway`, web interfaces via `svc-tunnel`, direct break-glass access, CI/CD pipelines, and infrastructure-as-code platform operations
- All environments: production, staging, and development
- All devices used to access Organization infrastructure, whether Organization-owned or personal

---

## 3. NIST 800-53 Control Alignment

| Control | Title | Implementation |
|---------|-------|----------------|
| **PL-4** | Rules of Behavior | This document; signed acknowledgment required before access is provisioned; reviewed annually |
| **PL-4(1)** | Social Media and External Site/Application Usage Restrictions | Section 5.3 (restrictions on posting system information externally) |
| **AT-2** | Literacy Training and Awareness | All personnel receive security awareness training upon onboarding and annually; training covers this policy |
| **AT-2(2)** | Insider Threat | Personnel are made aware that all actions are logged, monitored, and subject to review (Section 10) |
| **AU-6** | Audit Record Review, Analysis, and Reporting | All user actions are logged via `svc-gateway` session recording, `svc-detection` runtime monitoring, and `svc-monitor` telemetry (Section 10) |
| **CM-7** | Least Functionality | Only authorized services and containers may run on Organization infrastructure (Section 8) |
| **SA-4** | Acquisition Process | Restrictions on introducing unauthorized software or services (Section 8) |
| **SC-4** | Information in Shared Resources | Data handling requirements for shared infrastructure (Section 6) |

---

## 4. Authorized Use of Systems

### 4.1 General Authorization

Organization infrastructure shall be used exclusively for authorized business purposes related to security operations, infrastructure management, automation workflows, and activities that directly support the Organization's mission. Access privileges are granted based on job function and the principle of least privilege as defined in the Access Control Policy (POL-AC-001).

### 4.2 Authorized Activities

The following activities are authorized within the bounds of the user's assigned role:

| Activity | Admin | Operator | Auditor |
|----------|:-----:|:--------:|:-------:|
| Managing and operating automation workflows in `svc-automation` | Permitted | Permitted | View only |
| Routine container management (restart, log review, health checks) | Permitted | Permitted | Denied |
| Reviewing monitoring dashboards and alerts on Datadog | Permitted | Permitted | Permitted |
| Reviewing session recordings and audit logs | Permitted | Own sessions | All sessions |
| Configuring security controls (`svc-detection` rules, `svc-identity` policies, `svc-secrets` configurations) | Permitted | Denied | Denied |
| Executing infrastructure-as-code plan and apply operations | Permitted | Denied | Denied |
| Managing CI/CD pipeline configurations and code repository platform settings | Permitted | Denied | Denied |
| Requesting JIT privilege escalation for documented emergency or maintenance tasks | N/A | Permitted | Denied |

### 4.3 Personal Use

Limited personal use of Organization systems is not permitted. Organization infrastructure exists exclusively for operational and business purposes. Personal projects, communications, file storage, or computing workloads shall not be run on Organization systems.

---

## 5. Prohibited Activities

The following activities are strictly prohibited on all Organization systems, regardless of the user's role or access level.

### 5.1 Security Prohibitions

1. **Unauthorized access attempts:** Attempting to access systems, services, data, or accounts for which the user is not authorized, including attempting to bypass access controls, exploit vulnerabilities, or escalate privileges outside of the approved JIT workflow
2. **Disabling security controls:** Stopping, modifying, or circumventing `svc-detection` (runtime detection), `svc-monitor` (monitoring agent), `svc-gateway` (session recording), or any other security control without documented authorization from the Information Security Officer
3. **Credential sharing:** Sharing passwords, MFA seeds, SSH keys, API keys, or any other authentication credential with another person, system, or service not authorized to receive them
4. **Unauthorized scanning:** Running vulnerability scanners, port scanners, or penetration testing tools against Organization infrastructure without prior written authorization
5. **Tampering with audit logs:** Deleting, modifying, or attempting to suppress audit records, session recordings, monitoring data, or immutable log exports
6. **Unauthorized network modification:** Modifying firewall rules, tunnel configurations, container network settings, or DNS records without authorization

### 5.2 Operational Prohibitions

1. **Unauthorized container deployment:** Deploying, running, or attaching to containers that are not part of the authorized service inventory without approval from the Information Security Officer
2. **Unauthorized software installation:** Installing software, packages, or tools on `alpha-node` or within containers without documented justification and approval
3. **Resource abuse:** Running cryptocurrency miners, torrent clients, proxy services, or any workload that consumes compute resources for purposes unrelated to Organization operations
4. **Data exfiltration:** Copying, transferring, or transmitting Organization data (including configurations, credentials, audit logs, and monitoring data) to unauthorized external systems or storage
5. **Destructive operations without safeguards:** Running `docker compose down` via the zero-trust tunnel (kills the tunnel container itself), using `docker volume rm` or the `-v` flag on production volumes, or executing `rm -rf` on critical paths without confirmation

### 5.3 Information Handling Prohibitions

1. **Public disclosure:** Posting internal system configurations, architecture details, IP addresses, service names, credential identifiers, or monitoring data on public forums, social media, or external platforms without sanitization review
2. **Secret exposure in communications:** Including credential values, API keys, tokens, or connection strings in email, chat messages, code reviews, pull request descriptions, or any communication channel that is not encrypted and access-controlled
3. **Unauthorized photography or recording:** Capturing screenshots, photographs, or recordings of administrative interfaces, terminal sessions, or monitoring dashboards for purposes not directly related to authorized work

---

## 6. Data Handling Requirements

### 6.1 Data Classification

| Classification | Description | Examples | Handling Requirements |
|---------------|-------------|----------|----------------------|
| **Confidential** | Data that would cause significant harm if disclosed. Access restricted to admin role. | Credentials, API keys, SSH private keys, `svc-secrets` sealed data, encryption keys, MFA seeds | Encrypted at rest and in transit. Never stored in plaintext. Never transmitted over unencrypted channels. Access logged. |
| **Internal** | Data intended for internal use only. Access restricted to authorized personnel. | Infrastructure configurations, audit logs, session recordings, monitoring dashboards, architecture documentation, incident reports | Stored on authorized systems only. Not to be shared externally without sanitization. Access logged. |
| **Public** | Data approved for public distribution. | Sanitized architecture diagrams, published blog content, public-facing documentation | No special handling required. Must be reviewed for accidental inclusion of internal data before publication. |

### 6.2 Data Handling Rules

1. **Encryption in transit:** All data in transit between components uses TLS 1.2 or higher. The zero-trust tunnel (`svc-tunnel`) provides transport encryption for all external access. mTLS is used for inter-service communication between `svc-event-shipper` and `Fluentd`.
2. **Encryption at rest:** Database volumes (`svc-db`), secrets storage (`svc-secrets`), and remote state files are encrypted. Immutable audit log exports to object storage use server-side encryption.
3. **Data retention:** Datadog retains logs for 15 days. Long-term audit logs are archived to encrypted object storage. Session recordings follow the same retention schedule. No data shall be retained beyond its useful life without documented justification.
4. **Data disposal:** When decommissioning storage volumes, cloud instances, or backup media, all data shall be securely erased or the underlying storage destroyed. Cloud provider volume deletion and snapshot removal shall be verified.

---

## 7. Secret and Credential Management Rules

Credential mishandling is one of the highest-risk threat vectors for the Organization platform. The following rules are mandatory and non-negotiable.

### 7.1 Mandatory Practices

1. **Use the secrets manager for all credentials:** All API keys, database passwords, tokens, and other secrets shall be stored in and retrieved from the secrets manager. The secrets manager is the single source of truth for runtime credential injection.
2. **Environment variable injection:** Secrets are injected into containers and processes via environment variables at runtime. The pattern is: `secrets-manager run -- <command>` or `secrets-manager get <KEY> --plain` for single-value retrieval.
3. **Credential vault as source of truth for rotation:** The credential vault stores the authoritative copy of each credential for rotation purposes. Secrets are synced from the credential vault to the secrets manager.
4. **Credential rotation schedule:** Follow the rotation schedule defined in the Access Control Policy (POL-AC-001, Section 10.3). Rotate immediately upon suspected compromise.
5. **Verification without exposure:** To verify a secret is loaded, check existence only: `[ -n "$VAR_NAME" ] && echo "set" || echo "unset"`. Never print, echo, or log the value itself.

### 7.2 Absolute Prohibitions

The following actions constitute policy violations regardless of intent:

1. **Never hardcode credentials:** Secrets shall never appear in source code, configuration files checked into version control, container image layers, infrastructure-as-code definitions, or CI/CD pipeline definitions. Use variable references only.
2. **Never log secrets:** Secret values shall never appear in application logs, container logs, CI/CD pipeline output, monitoring dashboards, or debug output. Logging frameworks shall be configured to redact known secret patterns.
3. **Never print environment variables in bulk:** Commands that dump all environment variables (`env`, `printenv`, `export -p`, `set`) are prohibited on systems where secrets are injected, as they expose all loaded credentials to terminal output and session recordings.
4. **Never include secrets in commit messages or pull requests:** Commit messages, PR titles, PR descriptions, code review comments, and issue descriptions shall never contain credential values.
5. **Never transmit secrets in plaintext:** Secrets shall not be sent via email, chat, SMS, or any unencrypted communication channel. If a secret must be shared (e.g., during onboarding), use the credential vault's secure sharing mechanism.
6. **Never store secrets on local workstations:** Secrets shall not be persisted in local files, shell history, clipboard managers, or note-taking applications. Secrets loaded into memory via the secrets manager are acceptable during active sessions but shall be cleared when the session ends.

---

## 8. Container and Infrastructure Rules

### 8.1 Authorized Container Inventory

Only the following containers are authorized to run on `alpha-node`:

| Container | Service | Authorization |
|-----------|---------|---------------|
| `svc-db` | PostgreSQL 16 | Authorized -- production database |
| `svc-automation` | SOAR platform | Authorized -- workflow orchestration |
| `svc-secrets` | Secrets engine | Authorized -- secrets management |
| `svc-identity` | Identity provider (v26) | Authorized -- authentication and SSO |
| `svc-gateway` | SSH gateway (v18) | Authorized -- access control and session recording |
| `svc-monitor` | Observability agent | Authorized -- monitoring and log collection |
| `svc-detection` | eBPF runtime detection | Authorized -- syscall-level threat detection |
| `svc-detection-router` | Alert routing | Authorized -- detection event enrichment and forwarding |
| `Fluentd` | Log transformation | Authorized -- structured log routing with mTLS |
| `svc-event-shipper` | Audit event export | Authorized -- `svc-gateway` audit log shipping |
| `svc-llm` | Local LLM inference | Authorized -- local language model inference |
| `svc-transcription` | Voice-to-text processing | Authorized -- audio transcription service |
| `svc-tunnel` | Zero-trust tunnel | Authorized -- Cloudflare ingress |
| `svc-ai-gateway` | AI model gateway | Authorized -- standalone AI inference endpoint |

### 8.2 Container Governance Rules

1. **No unauthorized containers:** Deploying containers not listed in the authorized inventory requires written approval from the Information Security Officer. Unauthorized containers will be terminated upon discovery.
2. **No disabling security constraints:** The following container security configurations shall not be removed or weakened without documented justification and approval:
  - `no-new-privileges: true` (set on all containers except `svc-detection`)
  - `cap_drop: ALL` with explicit `cap_add` for required capabilities only
  - Memory, CPU, and PIDs resource limits
  - Healthcheck definitions
  - Log rotation settings (`max-size: 10m`, `max-file: 3`)
  - Read-only root filesystem (where configured)
3. **No privileged containers:** No container shall run with `--privileged` flag. `svc-detection` uses explicit capability grants (`SYS_ADMIN`, `SYS_PTRACE`, `SYS_RESOURCE`) instead of full privilege.
4. **No host namespace sharing** beyond what is authorized: Only `svc-tunnel` (host network) and `svc-monitor` (host PID namespace) are authorized for host namespace access. Other containers are prohibited from using `--net=host`, `--pid=host`, or `--ipc=host`.
5. **Docker socket access restriction:** Only `svc-detection` and `svc-monitor` are authorized to mount the Docker socket, and only in read-only mode (`:ro`).

### 8.3 Infrastructure-as-Code Rules

1. **All infrastructure changes through IaC:** Manual changes to DigitalOcean resources (compute instances, firewalls, DNS, object storage) are prohibited except during documented emergencies. All changes shall be defined in the infrastructure-as-code platform and applied through the CI/CD pipeline.
2. **Policy-as-code enforcement:** All infrastructure-as-code changes are subject to 8 policy engine rules (Rego) in CI. IaC compliance scanning validates security posture before apply. Failing policy checks block the merge.
3. **State file protection:** Remote state is stored in encrypted object storage with versioning enabled. Direct modification of state files is prohibited. State operations (`import`, `taint`, `untaint`, `mv`) require documentation.
4. **No secrets in IaC:** Infrastructure-as-code files shall reference secrets by variable name only. Secret values are injected at plan/apply time via the secrets manager.

---

## 9. Code Repository Rules

### 9.1 Commit and Push Requirements

1. **No secrets in commits:** Every commit is scanned by the secrets scanner in the CI/CD pipeline. Commits containing detected secrets will block the pipeline. If a secret is accidentally committed, it shall be considered compromised and rotated immediately -- removing it from git history alone is insufficient.
2. **Mandatory security scanning:** All pull requests trigger the following automated scans before merge is permitted:
  - **CVE scanner:** Container image vulnerability scanning (CVE detection)
  - **SAST scanner:** Static application security testing (SAST)
  - **Secrets scanner:** Secret and credential detection in source code
  - **Checkov:** Infrastructure-as-code security and compliance scanning
  - **Policy engine (Rego):** 8 custom policies for infrastructure governance
  - **IaC validate, fmt, lint:** Infrastructure-as-code syntax, formatting, and lint
3. **No bypassing pipeline checks:** Force-merging pull requests that fail security scans is prohibited. Pipeline bypass requires documented approval from the Information Security Officer.
4. **Branch protection:** The main branch is protected. Direct pushes to main are prohibited. All changes enter through pull requests with required status checks.

### 9.2 Repository Hygiene

1. **No sensitive files in version control:** The following file types shall never be committed: `.env` files, private keys (`.pem`, `.key`), credential files (`credentials.json`, `token.json`), IaC state files (`*.tfstate`), and vault data directories.
2. **`.gitignore` maintenance:** The repository `.gitignore` shall be maintained to exclude all sensitive file patterns. Changes to `.gitignore` that remove exclusions for sensitive patterns require review.
3. **Signed commits:** Commit signing is encouraged and may be required in future policy revisions.

---

## 10. Monitoring Acknowledgment

### 10.1 Consent to Monitoring

By accessing Organization infrastructure, all personnel acknowledge and consent to the following:

1. **All SSH sessions are recorded.** `svc-gateway` captures full terminal input and output for every SSH session. Recordings are stored, exported to Datadog, and archived to encrypted object storage.
2. **All system calls are monitored.** `svc-detection` (eBPF) monitors process execution, file access, network connections, and privilege operations across all containers and the host.
3. **All infrastructure events are logged.** `svc-monitor` collects container metrics, host metrics, log data, and application performance data. This data is transmitted to the centralized Datadog.
4. **All authentication events are logged.** `svc-identity` logs all login attempts (successful and failed), password changes, MFA events, and administrative actions.
5. **All access requests are logged.** `svc-gateway` records all JIT access requests, approvals, denials, and session activity associated with elevated privileges.
6. **All CI/CD operations are logged.** Pipeline executions, code repository platform events, and infrastructure-as-code operations are recorded and retained.

### 10.2 No Expectation of Privacy

Personnel shall have no expectation of privacy when using Organization systems. All data stored on, processed by, or transmitted through Organization infrastructure is subject to monitoring, review, and audit at any time without prior notice.

### 10.3 Monitoring Data Usage

Monitoring data is used exclusively for:

- Security incident detection and response
- Access review and compliance verification
- Performance analysis and capacity planning
- Policy compliance enforcement
- Forensic investigation following confirmed or suspected incidents

Monitoring data shall not be used for purposes unrelated to security and operational management.

---

## 11. Violations and Enforcement

### 11.1 Violation Categories

| Category | Description | Examples | Consequence |
|----------|-------------|----------|-------------|
| **Critical** | Actions that result in confirmed data breach, credential compromise, or destruction of security controls | Exfiltrating credentials, disabling `svc-detection`, deploying unauthorized containers with host-level access, tampering with audit logs | Immediate access revocation. Incident response initiated per POL-IR-001. |
| **Major** | Actions that create significant risk or violate core security principles | Hardcoding secrets in source code, sharing credentials, bypassing CI/CD security checks, running unauthorized software on `alpha-node` | Access suspended pending investigation. Written incident report required. |
| **Minor** | Actions that deviate from policy but do not create immediate risk | Failing to rotate credentials on schedule, minor documentation gaps, non-compliance with naming conventions | Written warning. Corrective action plan with deadline. |

### 11.2 Enforcement Procedures

1. **Detection:** Violations may be detected through automated monitoring (`svc-detection`, `svc-monitor`, CI/CD pipeline), manual audit review, or personnel reporting.
2. **Investigation:** The Information Security Officer investigates the violation, including review of session recordings, audit logs, and relevant monitoring data.
3. **Determination:** The Information Security Officer determines the violation category and recommends consequences.
4. **Action:** The System Owner approves and implements the recommended action.
5. **Documentation:** All violations are documented, including: the nature of the violation, evidence, investigation findings, action taken, and preventive measures implemented.
6. **Appeal:** Personnel may appeal enforcement actions to the System Owner within 5 business days.

### 11.3 Reporting Violations

Personnel who become aware of a policy violation -- whether committed by themselves or by another individual -- shall report it to the Information Security Officer immediately. Self-reporting of accidental violations (e.g., accidentally committing a secret to version control) is encouraged and will be considered a mitigating factor in enforcement decisions. Failure to report a known violation is itself a policy violation.

---

## 12. Policy Review Schedule

| Review Activity | Frequency | Responsible Party |
|----------------|-----------|-------------------|
| Full policy review and update | Annual | Information Security Officer |
| Authorized container inventory update | Quarterly (or when services are added/removed) | Information Security Officer |
| Prohibited activities list review | Annual | Information Security Officer |
| Security awareness training (includes AUP review) | Annual | Information Security Officer |
| New personnel acknowledgment | Upon onboarding (before access provisioned) | Information Security Officer |

---

## 13. Acknowledgment

All personnel must acknowledge this policy before access to Organization infrastructure is provisioned. Acknowledgment confirms that the individual has read, understood, and agrees to comply with all provisions of this policy.

| Field | Value |
|-------|-------|
| Name | ________________________________ |
| Role | ________________________________ |
| Date | ________________________________ |
| Signature | ________________________________ |

Acknowledgment records are maintained by the Information Security Officer and reviewed during the annual policy review.

---

## 14. Related Documents

| Document | Relationship |
|----------|-------------|
| POL-IR-001 (Incident Response Policy) | Defines incident response procedures triggered by AUP violations |
| POL-AC-001 (Access Control Policy) | Defines the access control framework within which acceptable use operates |
| IAM & RBAC Role Map | Technical implementation of roles and permissions referenced in Section 4 |
| IAM Access Review Process | Monthly review procedures that verify AUP compliance |
| CIS Docker Benchmark Risk Register | Documents accepted risks and compensating controls for container configuration |

---

## 15. Definitions

| Term | Definition |
|------|-----------|
| **Acceptable use** | Activities that fall within the authorized purposes, comply with all policy provisions, and do not create unreasonable risk to Organization systems or data |
| **Secrets manager** | The centralized system used to store, retrieve, and inject credentials into runtime environments |
| **Credential vault** | The encrypted, access-controlled system that serves as the source of truth for credential rotation and long-term credential storage |
| **Infrastructure-as-code (IaC)** | The practice of managing infrastructure through machine-readable definition files rather than manual configuration |
| **Policy-as-code** | Security and compliance rules expressed as programmatic policies (policy engine / Rego) that are evaluated automatically in CI/CD pipelines |
| **Break-glass** | Emergency access procedure that bypasses standard controls; see Access Control Policy (POL-AC-001) for full procedure |
| **JIT (Just-in-Time)** | Temporary privilege elevation with automatic expiration; defined in Access Control Policy (POL-AC-001) |
| **eBPF** | Extended Berkeley Packet Filter; a Linux kernel technology used by `svc-detection` to monitor system calls without modifying the kernel |
| **mTLS** | Mutual Transport Layer Security; bidirectional certificate-based authentication between services |
| **Zero-trust** | Security architecture that requires verification for every access request and assumes no implicit trust based on network location |
| **SAST** | Static Application Security Testing; automated analysis of source code for security vulnerabilities |

---

*Policy ID: POL-AU-001 | Version 1.0 | Classification: Internal Use Only*
