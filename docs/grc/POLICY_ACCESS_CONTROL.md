# Access Control Policy

**Document ID:** POL-AC-001
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
| Policy Title | Access Control Policy |
| Document ID | POL-AC-001 |
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

This policy establishes the access control framework for the Organization security operations platform. It defines requirements for identity management, authentication, authorization, privilege escalation, session management, and access review. The intent is to enforce the principle of least privilege across all infrastructure components, ensure that every access decision is auditable, and prevent unauthorized access to systems, data, and security controls.

---

## 2. Scope

This policy governs access to all components of the Organization security operations platform, including:

- The primary compute node (`alpha-node`) and all containerized services
- The identity provider (`svc-identity`) and SSH gateway (`svc-gateway`)
- Secrets management (`svc-secrets`), database services (`svc-db`), and automation workflows (`svc-automation`)
- Runtime detection (`svc-detection`), monitoring (`svc-monitor`), and log routing services (`Fluentd`, `svc-event-shipper`, `svc-detection-router`)
- Zero-trust tunnel (`svc-tunnel`) and AI gateway (`svc-ai-gateway`)
- CI/CD pipelines, infrastructure-as-code platform configurations, and code repository platform resources
- Encrypted remote state and object storage containing immutable audit logs
- All administrative interfaces, APIs, and command-line tools used to manage the above

This policy applies to all personnel, service accounts, and automated processes that access Organization infrastructure.

---

## 3. NIST 800-53 Control Alignment

| Control | Title | Implementation |
|---------|-------|----------------|
| **AC-1** | Access Control Policy and Procedures | This document; reviewed annually; disseminated to all authorized personnel |
| **AC-2** | Account Management | `svc-identity` manages all user accounts. Registration disabled (`registrationAllowed: false`). Admin-only account creation. |
| **AC-2(2)** | Automated Temporary Account Removal | JIT-elevated admin sessions auto-expire after 4 hours via `svc-gateway` `max_session_ttl` enforcement |
| **AC-3** | Access Enforcement | `svc-gateway` enforces SSH access by role. `svc-identity` enforces service access by realm role. Both default-deny. |
| **AC-4** | Information Flow Enforcement | Container network isolation via dedicated bridge network. No containers on the default bridge. `svc-tunnel` restricts ingress to authorized hostnames only. |
| **AC-5** | Separation of Duties | Three-tier RBAC model (admin/operator/auditor). Auditors cannot modify systems. Operators cannot approve their own escalation requests. |
| **AC-6** | Least Privilege | Operator role is the default working role. Admin access requires JIT request with time-bound TTL. Root SSH access restricted to admin role only. |
| **AC-6(1)** | Authorize Access to Security Functions | Only admin role can modify `svc-identity` realm settings, `svc-gateway` cluster configuration, `svc-detection` rules, and `svc-secrets` policies |
| **AC-6(2)** | Non-Privileged Access for Non-Security Functions | Operator role used for workflow management and routine container operations. No security function access. |
| **AC-7** | Unsuccessful Logon Attempts | `svc-identity` brute-force protection: 5 failed attempts trigger 15-minute account lockout |
| **AC-8** | System Use Notification | Login banners displayed on `svc-gateway` SSH sessions and `svc-identity` authentication pages |
| **AC-9** | Previous Logon Notification | `svc-identity` displays last successful login timestamp upon authentication |
| **AC-10** | Concurrent Session Control | `svc-gateway` enforces maximum concurrent sessions per role. Admin role limited to one concurrent session. |
| **AC-11** | Session Lock | `svc-identity` SSO idle timeout: 30 minutes. `svc-gateway` certificate-based sessions enforce idle timeout via TTL. |
| **AC-12** | Session Termination | Admin role: 4-hour maximum session. Operator role: 8-hour maximum session. `svc-identity` maximum session lifespan: 10 hours. Automatic termination enforced. |

---

## 4. Role-Based Access Control

### 4.1 Role Definitions

The Organization implements a three-tier RBAC model enforced across two identity systems: `svc-identity` (authentication and user management) and `svc-gateway` (authorization and session management).

| Role | Description | Default Assignment | Persistence |
|------|-------------|-------------------|-------------|
| **Admin** | Full administrative access to all infrastructure components, security controls, and identity management. Reserved for emergency and elevated operations. | Not permanently assigned | JIT-only; 4-hour TTL with automatic revocation |
| **Operator** | Day-to-day operational access. Can manage automation workflows, perform routine container operations, and monitor system health. Can request JIT escalation to admin. | Primary working role | Permanent assignment; 8-hour session TTL |
| **Auditor** | Read-only access to audit logs, session recordings, compliance dashboards, and monitoring data. Cannot modify any system or configuration. | Assigned for compliance activities | Permanent assignment; 12-hour session TTL |

### 4.2 Permission Matrix

| Action | Admin | Operator | Auditor |
|--------|:-----:|:--------:|:-------:|
| SSH to `alpha-node` (root login) | Permitted | Denied | Denied |
| SSH to `alpha-node` (standard login) | Permitted | Permitted (via `svc-gateway`) | Denied |
| Container lifecycle management (start/stop/restart) | Permitted | Permitted | Denied |
| Container creation or removal | Permitted | Denied | Denied |
| `svc-automation` workflow creation and editing | Permitted | Permitted | Denied |
| `svc-automation` workflow viewing | Permitted | Permitted | Permitted |
| `svc-identity` admin console access | Permitted | Denied | Denied |
| `svc-identity` user account management | Permitted | Denied | Denied |
| `svc-secrets` access and policy management | Permitted | Denied | Denied |
| Datadog dashboards (full access) | Permitted | Permitted | Permitted |
| Datadog alert configuration | Permitted | Permitted | Denied |
| `svc-detection` rule management | Permitted | Denied | Denied |
| `svc-gateway` cluster configuration | Permitted | Denied | Denied |
| Session recording playback (own sessions) | Permitted | Permitted | Permitted |
| Session recording playback (all sessions) | Permitted | Denied | Permitted |
| Full audit log access | Permitted | Denied | Permitted |
| Access request approval/denial | Permitted | Denied | Denied |
| Infrastructure-as-code plan and apply | Permitted | Denied | Denied |
| CI/CD pipeline configuration | Permitted | Denied | Denied |
| Code repository platform administration | Permitted | Denied | Denied |

### 4.3 Identity System Role Mapping

| `svc-identity` Realm Role | `svc-gateway` Role(s) | Session TTL | Requestable Roles |
|---------------------------|----------------------|-------------|-------------------|
| `cd-admin` | admin | 4h | None (highest privilege) |
| `cd-operator` | operator, editor, access | 8h | Can request `admin` |
| `cd-auditor` | auditor | 12h | None |

---

## 5. Account Lifecycle Management

### 5.1 Account Creation

1. All account creation requests must be submitted to the Information Security Officer with business justification
2. Accounts are created in `svc-identity` by an administrator. Self-registration is disabled.
3. Initial role assignment follows the principle of least privilege: the operator role is assigned unless a different role is specifically justified
4. The admin role is never permanently assigned to any account
5. Multi-factor authentication (TOTP) enrollment is mandatory at the time of account creation in `svc-gateway`
6. A corresponding user record is created in `svc-gateway` with the appropriate role mapping

### 5.2 Account Modification

1. Role changes require documented approval from the Information Security Officer
2. Temporary role elevation follows the JIT procedure defined in Section 7
3. All role changes are logged in `svc-identity` admin events and forwarded to Datadog
4. Changes to authentication mechanisms (password reset, MFA re-enrollment) require identity verification

### 5.3 Account Suspension

1. Accounts shall be suspended immediately upon:
  - Termination of the individual's relationship with the Organization
  - Suspected account compromise (per Incident Response Policy POL-IR-001)
  - Failure to complete required security training within the designated timeframe
  - Extended absence exceeding 90 days without prior authorization
2. Suspension in `svc-gateway` is performed via user lock: `tctl lock --user=<username> --message="<reason>"`
3. Suspension in `svc-identity` is performed by disabling the user account in the realm administration console

### 5.4 Account Termination

1. Terminated accounts shall be removed from both `svc-identity` and `svc-gateway` within 24 hours
2. All active sessions for the terminated account shall be revoked immediately
3. SSH keys, certificates, and MFA seeds associated with the account shall be invalidated
4. Service accounts owned by the terminated individual shall be reassigned or decommissioned
5. A final access review shall confirm no residual access persists

### 5.5 Account Review

Monthly access reviews are conducted on the first business day of each month. The review process is documented in the IAM Access Review Process and includes:

1. Verification that only authorized users exist in `svc-identity` and `svc-gateway`
2. Validation that role assignments match the current permission matrix
3. Review of all access requests from the previous 30 days for appropriateness
4. Spot-check review of at least two session recordings from elevated (admin) sessions
5. Verification that break-glass SSH keys have not been used outside of documented emergencies
6. Confirmation that service account credentials have not been modified without authorization

---

## 6. Authentication Requirements

### 6.1 Password Policy

All passwords for `svc-identity` managed accounts shall comply with the following requirements, enforced at the realm level:

| Requirement | Specification | Enforcement |
|-------------|--------------|-------------|
| Minimum length | 12 characters | `svc-identity` password policy: `length(12)` |
| Uppercase characters | At least 1 | `svc-identity` password policy: `upperCase(1)` |
| Lowercase characters | At least 1 | `svc-identity` password policy: `lowerCase(1)` |
| Numeric characters | At least 1 | `svc-identity` password policy: `digits(1)` |
| Special characters | At least 1 | `svc-identity` password policy: `specialChars(1)` |
| Username prohibition | Password cannot contain username | `svc-identity` password policy: `notUsername` |
| Password history | Cannot reuse last 5 passwords | `svc-identity` password policy configuration |
| Maximum age | 90 days | Enforced via `svc-identity` credential policy |

### 6.2 Multi-Factor Authentication

MFA is mandatory for all interactive access to Organization infrastructure.

| Access Method | MFA Type | Enforcement Point |
|---------------|----------|-------------------|
| SSH via `svc-gateway` | TOTP (time-based one-time password) | `svc-gateway` per-session MFA challenge |
| `svc-identity` web console | TOTP or WebAuthn | `svc-identity` required action on login |
| `svc-automation` dashboard | Password + session cookie via `svc-tunnel` | Cloudflare access policy |
| Code repository platform | Platform-native MFA | Code repository platform account settings |
| Cloud provider console | Platform-native MFA | Cloud provider account settings |

### 6.3 Authentication Failure Handling

| Event | Response | Control Reference |
|-------|----------|-------------------|
| 5 failed login attempts within 15 minutes | Account locked for 15 minutes | `svc-identity` brute-force protection (`failureFactor: 5`, `maxFailureWaitSeconds: 900`) |
| 10 failed login attempts within 1 hour | Account locked for 1 hour; alert generated | `svc-identity` escalated lockout + Datadog alert |
| Failed MFA challenge | Session denied; event logged | `svc-gateway` audit trail |
| Authentication from unexpected location | Event logged; manual review triggered | Datadog anomaly detection |

---

## 7. Privileged Access Management

### 7.1 Just-in-Time Escalation

Administrative access is never permanently assigned. The operator role includes the ability to request temporary elevation to the admin role through `svc-gateway`'s access request system.

**JIT Workflow:**

1. **Request:** Operator submits an access request specifying the admin role and a mandatory business justification
2. **Logging:** The request is recorded with a unique ID, requestor identity, requested role, reason, and timestamp
3. **Approval:** An authorized approver (admin role holder or Information Security Officer) reviews and approves or denies the request
4. **Grant:** Upon approval, the admin role is granted with a maximum session TTL of 4 hours
5. **Execution:** All actions performed during the elevated session are recorded (full terminal I/O via `svc-gateway` session recording in node-sync mode)
6. **Expiration:** The admin role is automatically revoked after 4 hours. No manual cleanup is required. The operator cannot extend the session.

**Constraints:**

| Safeguard | Implementation |
|-----------|---------------|
| Time-bound | Admin role auto-expires after 4 hours |
| Reason required | `--reason` parameter is mandatory for all requests |
| Full recording | All SSH sessions during escalation are recorded with terminal I/O capture |
| Audit trail | Request, approval, session, and expiry events are forwarded to Datadog |
| No self-approval | In multi-operator deployments, the requestor cannot approve their own request |
| No agent forwarding | `forward_agent: false` on all custom roles prevents SSH agent forwarding |

### 7.2 Standing Privileges

No standing administrative privileges are permitted. The following restrictions apply:

1. The admin role shall not be permanently assigned to any user account in `svc-gateway`
2. Root login on `alpha-node` is restricted to the admin role in `svc-gateway` and to break-glass access only
3. Direct SSH access (bypassing `svc-gateway`) is classified as break-glass and subject to the emergency access procedure in Section 12
4. Service account privileges are scoped to the minimum required for the specific service function

---

## 8. Session Management

### 8.1 Session Timeouts

| Parameter | Admin | Operator | Auditor | Enforcement |
|-----------|-------|----------|---------|-------------|
| Maximum session TTL | 4 hours | 8 hours | 12 hours | `svc-gateway` role-level `max_session_ttl` |
| SSO idle timeout | 30 minutes | 30 minutes | 30 minutes | `svc-identity` `ssoSessionIdleTimeout: 1800` |
| SSO maximum lifespan | 10 hours | 10 hours | 10 hours | `svc-identity` `ssoSessionMaxLifespan: 36000` |
| Certificate-based session expiry | Per TTL above | Per TTL above | Per TTL above | `svc-gateway` X.509 certificate `NotAfter` |

### 8.2 Session Recording

All SSH sessions through `svc-gateway` are recorded with the following characteristics:

| Property | Setting |
|----------|---------|
| Recording mode | `node-sync` (resilient -- recording persists even if proxy disconnects) |
| Content captured | Full terminal input and output (stdin, stdout, stderr) |
| Storage | Local on `svc-gateway`, exported via `svc-event-shipper` and `Fluentd` to Datadog |
| Playback access | Admin (all sessions), Operator (own sessions only), Auditor (all sessions) |
| Retention | Per Datadog retention policy (15 days online) + encrypted object storage (long-term) |
| Integrity | Session events included in hash chain export to immutable object storage |

### 8.3 Session Monitoring

Active sessions are subject to the following monitoring controls:

1. `svc-detection` (eBPF) monitors all process execution, file access, and network connections within SSH sessions
2. `svc-monitor` tracks session duration, resource consumption, and anomalous command patterns
3. Alerts are generated for: sessions exceeding expected duration, execution of security-sensitive commands, and access to restricted files

---

## 9. Remote Access

### 9.1 Zero-Trust Network Access

All remote access to Organization infrastructure transits through a zero-trust tunnel (`svc-tunnel`) provided by Cloudflare. The following principles govern remote access:

1. **No direct public access:** The compute node (`alpha-node`) has no publicly exposed ports. All ingress flows through Cloudflare's tunnel.
2. **Application-layer routing:** The tunnel routes specific hostnames to specific internal services. Only pre-configured routes are permitted.
3. **Transport encryption:** All traffic through the tunnel is encrypted end-to-end between Cloudflare's network and the local tunnel agent.
4. **Authentication at the edge:** Cloudflare enforces access policies before traffic reaches the tunnel.

### 9.2 SSH Access Architecture

```
Remote User
  |
  v
Edge Security Provider (zero-trust tunnel)
  |
  v
svc-tunnel (on alpha-node, host network)
  |
  v
svc-gateway -- authentication, MFA, session recording
  |
  v
alpha-node (SSH session with role-appropriate login)
```

1. Direct SSH to `alpha-node` bypassing `svc-gateway` is prohibited except under break-glass conditions (Section 12)
2. All SSH sessions through `svc-gateway` require TOTP MFA
3. SSH agent forwarding is disabled on all custom roles
4. Port forwarding is restricted by role: admin may forward ports; operator and auditor may not

### 9.3 Service Dashboard Access

| Service | Access URL | Authentication | Transport |
|---------|-----------|----------------|-----------|
| `svc-automation` | `https://automation.example-ops.com` | Username/password | Cloudflare tunnel (HTTPS) |
| `svc-identity` | Container-internal (internal identity port) | Admin credentials | No external exposure; accessed via SSH tunnel only |
| Datadog | `https://monitoring.example-ops.com` (external SaaS) | Platform-native SSO + MFA | Direct HTTPS |

---

## 10. Service Account Management

### 10.1 Principles

1. Service accounts shall be scoped to the minimum permissions required for their function
2. Service account credentials shall never be hardcoded in source code, container images, or infrastructure-as-code files
3. All service account credentials are managed through the secrets manager and injected via environment variables at runtime
4. Service accounts shall not have interactive login capability

### 10.2 Current Service Accounts

| Service | Credential Type | Source | Scope |
|---------|----------------|--------|-------|
| `svc-automation` to `svc-db` | Database username/password | Secrets manager (env var injection) | Read/write to automation database only |
| `svc-monitor` | API key | Secrets manager (env var injection) | Container autodiscovery, log collection, metric submission |
| `svc-detection` | Docker socket (read-only) | Volume mount | Container metadata correlation |
| `svc-event-shipper` | mTLS certificate | Generated certificate pair | `svc-gateway` event stream subscription |
| `svc-ai-gateway` | API key | Secrets manager (env var injection) | External AI model API access |
| `svc-tunnel` | Tunnel token | Secrets manager (env var injection) | Cloudflare tunnel authentication |
| CI/CD pipeline | Platform token | Code repository platform secrets | Repository access, artifact publishing |

### 10.3 Credential Rotation

| Credential Type | Rotation Frequency | Rotation Method |
|----------------|-------------------|-----------------|
| Database passwords | 90 days | Update in secrets manager; restart dependent services |
| API keys | 90 days or upon suspected compromise | Regenerate at provider; update in secrets manager |
| mTLS certificates | 365 days or upon suspected compromise | Regenerate certificate pair; update affected services |
| Tunnel tokens | Upon suspected compromise only | Regenerate at Cloudflare; update secrets manager |
| SSH keys (break-glass) | 180 days or upon use | Generate new key pair; update authorized_keys; store in credential vault |

---

## 11. Access Review Schedule

| Review Activity | Frequency | Responsible Party | Reference |
|----------------|-----------|-------------------|-----------|
| Full user account audit (`svc-identity` + `svc-gateway`) | Monthly | Information Security Officer | IAM Access Review Process |
| Role assignment validation | Monthly | Information Security Officer | Section 4.2 Permission Matrix |
| JIT access request history review | Monthly | Information Security Officer | `svc-gateway` access request logs |
| Session recording spot-check (admin-elevated sessions) | Monthly | Information Security Officer | `svc-gateway` recording playback |
| Break-glass SSH key usage review | Monthly | Information Security Officer | Cloudflare access logs |
| Service account credential age review | Quarterly | Information Security Officer | Secrets manager audit |
| Code repository platform access audit | Quarterly | Information Security Officer | Code repository platform admin |
| Full policy review and update | Annual | Information Security Officer | This document |

---

## 12. Emergency Access (Break-Glass Procedure)

### 12.1 Purpose

The break-glass procedure provides emergency access to Organization infrastructure when the standard access path (`svc-gateway` and/or `svc-identity`) is unavailable due to service failure, misconfiguration, or security incident.

### 12.2 Break-Glass Access Path

```
Remote User (Information Security Officer or System Owner only)
  |
  v
Edge Security Provider (zero-trust tunnel -- SSH route)
  |
  v
svc-tunnel (host network mode)
  |
  v
alpha-node (direct SSH, bypassing svc-gateway)
  Authentication: ed25519 SSH key stored in credential vault
```

### 12.3 Authorization

Break-glass access is authorized only under the following conditions:

1. `svc-gateway` is unresponsive and cannot be recovered remotely within 30 minutes
2. A P1 or P2 security incident requires immediate action that cannot be performed through `svc-gateway`
3. Infrastructure recovery requires direct host access (e.g., `svc-gateway` container restart)

### 12.4 Procedure

1. **Document the justification** before initiating break-glass access. Record the timestamp, reason, and expected actions.
2. **Retrieve the SSH key** from the credential vault
3. **Connect via the Cloudflare tunnel** SSH route to `alpha-node`
4. **Perform only the minimum actions** required to resolve the emergency
5. **Verify `svc-gateway` recovery** if the break-glass was triggered by gateway failure. Restart the container if necessary.
6. **Document all actions taken** during the break-glass session, including commands executed and their output
7. **File a post-break-glass report** within 24 hours, including: justification, actions taken, duration, and any follow-up items
8. **Evaluate key rotation:** If the break-glass SSH key may have been exposed during the emergency, rotate immediately

### 12.5 Post-Break-Glass Audit

Every use of break-glass access triggers:

1. Review of Cloudflare tunnel access logs for the break-glass session
2. Review of `alpha-node` auth.log and shell history for actions taken
3. Verification that no unauthorized changes persist (accounts, SSH keys, containers, configurations)
4. Documentation in the access review record
5. Incident report if the break-glass was triggered by a security event

---

## 13. Policy Review Schedule

| Review Activity | Frequency | Responsible Party |
|----------------|-----------|-------------------|
| Full policy review and update | Annual (or after any P1 incident involving access control failure) | Information Security Officer |
| Permission matrix validation against infrastructure changes | Quarterly | Information Security Officer |
| Role definition review | Annual | Information Security Officer |
| Authentication requirement review (password policy, MFA standards) | Annual | Information Security Officer |
| Break-glass procedure test | Semi-annual | Information Security Officer |

---

## 14. Related Documents

| Document | Relationship |
|----------|-------------|
| POL-IR-001 (Incident Response Policy) | References access control procedures during containment and evidence collection |
| POL-AU-001 (Acceptable Use Policy) | Defines acceptable use of access privileges granted under this policy |
| IAM & RBAC Role Map | Detailed technical implementation of the roles defined in this policy |
| IAM Access Review Process | Operational procedures for monthly access reviews mandated by this policy |
| CIS Docker Benchmark Risk Register | Documents compensating controls for container-level access findings |

---

## 15. Enforcement

Violation of this policy, including but not limited to unauthorized privilege escalation, sharing of credentials, disabling of security controls, or use of break-glass access without justification, will result in disciplinary action up to and including immediate revocation of all system access.

All access-related events are logged, correlated, and subject to review. Personnel should have no expectation of privacy when using Organization systems.

---

## 16. Definitions

| Term | Definition |
|------|-----------|
| **JIT (Just-in-Time)** | Temporary privilege elevation that is requested, approved, granted for a fixed duration, and automatically revoked upon expiration |
| **TTL (Time-to-Live)** | The maximum duration for which a session or role grant remains valid before automatic expiration |
| **RBAC (Role-Based Access Control)** | An access control model where permissions are assigned to roles, and users are assigned to roles, rather than granting permissions directly to users |
| **MFA (Multi-Factor Authentication)** | Authentication requiring two or more independent factors: something you know (password), something you have (TOTP device), or something you are (biometric) |
| **Break-glass** | An emergency access procedure that bypasses standard authentication and authorization controls, subject to post-access audit |
| **Least privilege** | The principle that every user, process, and service account operates with the minimum set of permissions required to perform its function |
| **Zero-trust** | A security model that does not implicitly trust any user, device, or network segment, and requires continuous verification for every access request |
| **TOTP** | Time-based One-Time Password; a 6-digit code generated by a shared secret and the current time, valid for 30 seconds |
| **mTLS** | Mutual Transport Layer Security; both client and server present certificates to authenticate each other |

---

*Policy ID: POL-AC-001 | Version 1.0 | Classification: Internal Use Only*
