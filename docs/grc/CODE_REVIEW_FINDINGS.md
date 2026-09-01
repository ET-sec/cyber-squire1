# Security Code Review Findings

**Organization:** Organization Security Operations Platform
**Assessment Date:** 2026-03-22
**Assessor:** System Owner
**Methodology:** Manual Security Code Review, OWASP Code Review Guide v2.0, CWE/SANS Top 25
**NIST 800-53 Controls:** SA-11 (Developer Testing and Evaluation), SA-15 (Development Process, Standards, and Tools), RA-5 (Vulnerability Monitoring and Scanning), CM-6 (Configuration Settings)
**Classification:** Internal Use Only
**Version:** 1.1

> **Status note (2026-08-31):** infrastructure has since migrated to Oracle Cloud (OCI); see docs/architecture/ for the current stack. Findings below describe the environment as assessed on the assessment date, including the object storage state backend then in use. The 19-service compose environment reviewed here was retired with the DigitalOcean host in 2026-08; open items roll into the OCI re-baseline.

---

## Document Control

| Field | Value |
|-------|-------|
| Document ID | CR-001 |
| Version | 1.1 |
| Status | Approved |
| Last Revised | 2026-06-24 |
| Next Review | 2026-09-22 |
| Author | Information Security Officer |
| Approver | System Owner |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-03-15 | Information Security Officer | Initial release, 5 findings |
| 1.1 | 2026-06-24 | Information Security Officer | Audit refresh: secret count standardized to 44 (matches Doppler `<SECRETS_PROJECT>/<CONFIG>` live state). Remediation Tracking section flagged Past Due where target dates have lapsed without confirmed completion. |

---

## 1. Executive Summary

This document presents the results of a manual security code review conducted against the Organization's infrastructure codebase, including Docker Compose configurations, Terraform definitions, CI/CD pipeline configurations, and n8n workflow automation. The review focused on secret management patterns, input validation boundaries, credential lifecycle practices, and configuration security.

Five findings were identified:

| Severity | Count | Remediated | Accepted | Open |
|----------|-------|------------|----------|------|
| HIGH | 1 | 1 | 0 | 0 |
| MEDIUM | 3 | 0 | 3 | 0 |
| LOW | 1 | 0 | 1 | 0 |
| **Total** | **5** | **1** | **4** | **0** |

The single HIGH finding (environment variable credential exposure in svc-automation) was remediated the same day. Three MEDIUM findings were accepted with documented compensating controls and remediation paths tracked in the POA&M. One LOW finding was accepted with compensating controls.

---

## 2. Scope

### 2.1 Artifacts Reviewed

| Artifact | Location | Description |
|----------|----------|-------------|
| Docker Compose configuration | `primary-node:/opt/platform/docker-compose.yaml` | 19-service container orchestration definition |
| Environment file | `primary-node:/opt/platform/.env` | 44 secrets injected at container startup (matches `doppler secrets list` against the live `<SECRETS_PROJECT>/<CONFIG>` config) |
| Terraform IaC | Repository: `terraform/infrastructure/` | 19 `.tf` files defining Cloud Provider infrastructure |
| OPA policies | Repository: `terraform/infrastructure/policies/` | 8 Rego policy files enforcing infrastructure guardrails |
| CI/CD pipelines | Repository: `.github/workflows/` | 2 workflow files (PR pipeline, merge pipeline) |
| n8n workflows | svc-automation runtime | 16 active workflows including Master Orchestrator |
| Cloudflare Tunnel config | `primary-node:/opt/platform/.cloudflared/config.yml` | Tunnel routing and ingress rules |
| OpenClaw gateway config | `primary-node:/opt/ai-gateway/config/openclaw.json` | AI gateway routing and model configuration |

### 2.2 Review Methodology

The review followed a structured approach:

1. **Configuration analysis** of all deployment artifacts for secret exposure, default credentials, and insecure defaults
2. **Data flow tracing** following secrets from source (external secrets manager, `.env`) through injection points to consumption endpoints
3. **Trust boundary analysis** at each network segment, container boundary, and application interface
4. **Input validation review** for all externally accessible endpoints (webhooks, APIs, tunnel ingress)
5. **Privilege analysis** of service accounts, API key scopes, and credential access patterns

### 2.3 Out of Scope

- Third-party application source code (n8n, Vault, Keycloak, Falco, Terraform providers)
- Cloud Provider platform internals
- Cloudflare infrastructure
- End-user client applications

---

## 3. Findings

---

### Finding CR-001-F1: Environment Variable Credential Exposure in svc-automation

| Field | Value |
|-------|-------|
| **Finding ID** | CR-001-F1 |
| **Severity** | HIGH |
| **CVSS 3.1 Score** | 8.1 (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N) |
| **CWE** | CWE-200 (Exposure of Sensitive Information to an Unauthorized Actor), CWE-269 (Improper Privilege Management) |
| **OWASP** | A01:2025 Broken Access Control |
| **NIST 800-53** | AC-6 (Least Privilege), AC-6(1) (Authorize Access to Security Functions), SC-28 (Protection of Information at Rest) |
| **Status** | REMEDIATED |

#### Description

n8n (svc-automation) Code nodes execute arbitrary JavaScript in a Node.js context that inherits the full process environment. By default, n8n does not restrict `process.env` access from Code nodes. Any authenticated n8n user can create a Code node that enumerates and reads all 44 environment variables, including database credentials, API keys for cloud and SaaS providers, bot tokens, tunnel tokens, and encryption material.

#### Evidence

A test workflow containing the following Code node was created and executed:

```javascript
// Test Code node, sanitized output
const envKeys = Object.keys(process.env);
return [{ json: { count: envKeys.length } }];
```

Output confirmed: `{ "count": 44 }`.

A second test confirmed full value access:

```javascript
// Targeted extraction test
const dbPass = process.env['DB_PASS'];
return [{ json: { db_pass_length: dbPass.length, db_pass_set: true } }];
```

Output confirmed the database password was fully readable from a Code node.

#### Impact Analysis

| Dimension | Impact |
|-----------|--------|
| Confidentiality | All 44 secrets exposed to any authenticated n8n user via Code node execution |
| Integrity | Stolen credentials enable database modification, workflow tampering, infrastructure reconfiguration, and DNS manipulation |
| Financial | Unauthorized consumption of LLM API credits, cloud resources, and SaaS subscriptions |
| Lateral Movement | Database credentials provide access to n8n's internal credential store. Cloud provider token enables infrastructure-level pivoting. |

#### Remediation

Applied `N8N_RESTRICT_ENVIRONMENT_VARIABLES_ACCESS=true` in the svc-automation container environment configuration. Verified that `process.env` returns an empty object from Code nodes after restart.

**Time to remediation:** 45 minutes from discovery.

#### Cross-References

- Full writeup: [VULN_WRITEUP_N8N_CREDENTIAL_EXPOSURE.md](VULN_WRITEUP_N8N_CREDENTIAL_EXPOSURE.md)
- Policy: [POLICY_ACCESS_CONTROL.md](POLICY_ACCESS_CONTROL.md) (AC-6)
- Risk: [RISK_ASSESSMENT.md](RISK_ASSESSMENT.md)

---

### Finding CR-001-F2: Secrets in Docker Compose Environment Variables

| Field | Value |
|-------|-------|
| **Finding ID** | CR-001-F2 |
| **Severity** | MEDIUM |
| **CVSS 3.1 Score** | 5.5 (AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N) |
| **CWE** | CWE-312 (Cleartext Storage of Sensitive Information), CWE-522 (Insufficiently Protected Credentials) |
| **OWASP** | A02:2025 Security Misconfiguration |
| **NIST 800-53** | SC-28 (Protection of Information at Rest), SC-12 (Cryptographic Key Establishment and Management), IA-5 (Authenticator Management) |
| **Status** | ACCEPTED (with compensating controls) |

#### Description

The Docker Compose deployment passes all secrets to containers via environment variables defined in a `.env` file. This is the standard pattern for Docker Compose deployments, but it has known security limitations:

1. Environment variables are visible to any process running inside the container
2. Environment variables appear in `docker inspect` output for any user with Docker socket access
3. Environment variables persist in the process table and can be read from `/proc/<pid>/environ` on the host
4. Child processes inherit the full environment by default
5. Crash dumps and core files may contain environment variable contents

All 20 containers receive their secrets through this mechanism. The `.env` file contains 44 secrets in cleartext.

#### Evidence

On the host (`primary-node`), the following commands confirm environment variable visibility:

```bash
# Environment variables visible via docker inspect (requires Docker socket access)
docker inspect svc-automation --format '{{.Config.Env}}' | wc -w
# Output: 44+ environment variables listed

# Environment variables visible from host /proc filesystem
cat /proc/$(docker inspect svc-automation --format '{{.State.Pid}}')/environ | tr '\0' '\n' | wc -l
# Output: 44+ environment variables
```

The `.env` file permissions are correctly set to `chmod 600`, limiting read access to root. However, any process with root-equivalent access on the host (including the Docker daemon itself) can read all secrets.

#### Impact Analysis

| Dimension | Impact |
|-----------|--------|
| Confidentiality | Secrets readable by any process with Docker socket access or host-level root access |
| Integrity | An attacker with host-level access could modify `.env` and restart containers with altered credentials |
| Scope | All 20 containers, all 44 secrets |

#### Risk Decision: ACCEPTED

This finding is accepted with compensating controls for the following reasons:

1. **Industry standard practice.** Docker Compose environment variable injection is the documented and supported method for single-host deployments. The alternative (Docker Secrets) requires Docker Swarm mode, which is not appropriate for a single-node deployment.
2. **Host-level access prerequisite.** Exploiting this finding requires root-level access to `primary-node`. If an attacker has host-level root access, the `.env` file exposure is one of many available attack paths and not the primary risk.
3. **Compensating controls are in place** (see below).

#### Compensating Controls

| Control | Description |
|---------|-------------|
| File permissions | `.env` file permissions set to `chmod 600` (root read/write only) |
| Git exclusion | `.env` file is listed in `.gitignore` and is not tracked in version control |
| Source of truth | The managed secrets platform is the source of truth for all 44 runtime credentials. The `.env` file is a deployment artifact, not the canonical store. |
| Rotation capability | Secrets can be rotated through the external secrets manager and redeployed without manual editing of the `.env` file |
| SSH access control | Host access requires SSH with ed25519 key authentication through a zero-trust tunnel. No password-based SSH. |
| Runtime detection | Falco (svc-detection) monitors for sensitive file reads on the host, including reads of `.env` and `/proc/*/environ` |
| Container isolation | Containers run with `no-new-privileges`, resource limits, PIDs limits, and read-only root filesystems (where application compatibility allows) |

#### Remediation Path

Migrate to HashiCorp Vault (svc-secrets) AppRole authentication with dynamic, time-limited credentials. Each container would authenticate to Vault using a unique AppRole identity and receive only the secrets it needs, with automatic expiration and renewal. This is tracked as a POA&M item with a 90-day target.

#### Cross-References

- Policy: [POLICY_ACCESS_CONTROL.md](POLICY_ACCESS_CONTROL.md) (AC-6, SC-28)
- POA&M: [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) (Vault migration item)
- Risk Register: [CIS_RISK_REGISTER.md](CIS_RISK_REGISTER.md)
- Playbook: [PLAYBOOK_LEAKED_CREDENTIAL.md](PLAYBOOK_LEAKED_CREDENTIAL.md)

---

### Finding CR-001-F3: Terraform State File Exposure Risk

| Field | Value |
|-------|-------|
| **Finding ID** | CR-001-F3 |
| **Severity** | MEDIUM |
| **CVSS 3.1 Score** | 5.3 (AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:L/A:N) |
| **CWE** | CWE-311 (Missing Encryption of Sensitive Data), CWE-522 (Insufficiently Protected Credentials) |
| **OWASP** | A02:2025 Security Misconfiguration |
| **NIST 800-53** | SC-28 (Protection of Information at Rest), SC-13 (Cryptographic Protection), AU-9 (Protection of Audit Information) |
| **Status** | ACCEPTED (with compensating controls) |

#### Description

Terraform state is stored remotely in a Cloud Provider object storage bucket (S3-compatible). The state file contains sensitive outputs including:

- Resource IPs and identifiers
- Security group rule definitions (port ranges, allowed sources)
- Instance metadata (region, size, image, SSH key fingerprints)
- DNS record values
- Firewall rule configurations

The state backend is configured with access credentials injected through CI/CD pipeline secrets. During CI/CD execution, the Terraform process reads and writes state over HTTPS. The state file itself is stored as a versioned object in the bucket.

The risk is twofold:

1. **State file contents are sensitive.** Anyone with bucket read access can extract infrastructure topology, IP addresses, security group rules, and resource identifiers.
2. **CI/CD credential scope.** The Spaces access keys used for state operations have write access to the bucket, meaning a compromised CI/CD environment could tamper with state.

#### Evidence

Terraform backend configuration (sanitized):

```hcl
terraform {
  backend "s3" {
    endpoints = {
      s3 = "https://region.cloud-provider-spaces.example.com"
    }
    bucket = "org-terraform-state"
    key    = "terraform.tfstate"
    region = "us-east-1"

    skip_credentials_validation = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true
    skip_s3_checksum            = true
  }
}
```

OPA policy enforcing bucket versioning (sanitized):

```rego
deny_no_encryption[msg] {
  resource := input.resource_changes[_]
  resource.type == "cloud_provider_spaces_bucket"
  not resource.change.after.versioning[_].enabled
  msg := sprintf("Spaces bucket %s must have versioning enabled", [resource.address])
}
```

The OPA policy enforces versioning but does not enforce encryption at rest or access logging.

#### Impact Analysis

| Dimension | Impact |
|-----------|--------|
| Confidentiality | State file reveals full infrastructure topology: IPs, security groups, firewall rules, resource names, SSH key fingerprints |
| Integrity | Write access to state could enable state poisoning, causing Terraform to make unintended infrastructure changes on next apply |
| Scope | Limited to infrastructure metadata. No application-layer secrets are stored in Terraform outputs. |

#### Risk Decision: ACCEPTED

This finding is accepted because:

1. **Bucket access requires specific credentials.** The Spaces access keys are stored in the external secrets manager and injected only during CI/CD execution. They are not present in the `.env` file on `primary-node`.
2. **OPA policy enforcement.** The `deny_no_encryption` policy ensures versioning is enabled on the state bucket, providing change history and rollback capability.
3. **CI/CD pipeline isolation.** Terraform operations run in ephemeral CI/CD runners, not on the production host.

#### Compensating Controls

| Control | Description |
|---------|-------------|
| Credential scoping | Spaces access keys are scoped to state bucket operations only, stored in the external secrets manager, and injected only during CI/CD runs |
| Bucket versioning | Enforced by OPA policy. Provides state history and rollback capability. |
| PR review gate | All Terraform changes require PR review. The `terraform plan` output is posted as a PR comment for review before merge. |
| OPA policy enforcement | 8 Rego policies evaluated on every PR, blocking non-compliant changes before apply |
| Pipeline security scans | Checkov scans IaC for misconfigurations. Trivy scans for vulnerabilities. Both run on every PR. |
| State not on host | State file is not stored on `primary-node`. Local `.terraform` directory is gitignored. |

#### Remediation Path

1. Enable server-side encryption on the Spaces bucket (AES-256)
2. Enable access logging on the Spaces bucket to track all read/write operations
3. Add OPA policy to enforce encryption-at-rest on all storage resources
4. Consider implementing state locking with a DynamoDB-compatible backend

#### Cross-References

- Policy: [POLICY_CHANGE_MANAGEMENT.md](POLICY_CHANGE_MANAGEMENT.md) (CM-3, CM-6)
- Risk: [RISK_ASSESSMENT.md](RISK_ASSESSMENT.md) (infrastructure compromise scenario)
- POA&M: [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md)

---

### Finding CR-001-F4: Webhook Input Validation Gap in Master Orchestrator

| Field | Value |
|-------|-------|
| **Finding ID** | CR-001-F4 |
| **Severity** | MEDIUM |
| **CVSS 3.1 Score** | 5.4 (AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N) |
| **CWE** | CWE-20 (Improper Input Validation), CWE-862 (Missing Authorization) |
| **OWASP** | A05:2025 Injection |
| **NIST 800-53** | SI-10 (Information Input Validation), AC-3 (Access Enforcement), SC-7 (Boundary Protection) |
| **Status** | ACCEPTED (with compensating controls) |

#### Description

The Master Orchestrator workflow (svc-automation) exposes a webhook endpoint at `/webhook/<redacted-route>` that accepts POST requests with a JSON body containing an `action` parameter. This parameter routes the request to one of 16 service integration handlers:

```
postgres, telegram, github, drive, tasks, sheets, docs, slides,
gumroad, cloudflare, notion, tavily, gmail, workspace_admin, excel, ollama
```

Input validation for the `action` parameter occurs inside the n8n workflow at the Switch node, not at the webhook entry point. This means:

1. The webhook accepts any POST body without validating the `action` value before processing begins
2. Additional parameters (e.g., `query`, `text`, `chat_id`) are passed through to service handlers without sanitization at the webhook layer
3. There is no authentication or authorization check at the webhook endpoint itself

An attacker who discovers the webhook URL can send crafted payloads to probe action handlers and potentially trigger unintended operations.

#### Evidence

The webhook node configuration (sanitized) shows no input validation:

```json
{
  "webhookId": "[redacted]",
  "path": "<redacted-route>",
  "httpMethod": "POST",
  "responseMode": "lastNode",
  "options": {}
}
```

The Switch node evaluates `{{ $json.action }}` against a static list of known values. Unknown actions fall through to a default branch that returns an error. However, valid actions are processed without further validation of their payload parameters.

Example of a probing request:

```bash
# Probe with a valid action and crafted payload
curl -X POST https://automation.example-ops.com/webhook/<redacted-route> \
  -H "Content-Type: application/json" \
  -d '{"action": "postgres", "query": "SELECT version()"}'
```

If the webhook URL is known, this request would execute against the database without authentication.

#### Impact Analysis

| Dimension | Impact |
|-----------|--------|
| Confidentiality | Low. An attacker could read data through the `postgres` action or enumerate connected services. |
| Integrity | Low. An attacker could send messages through the `telegram` action, create documents through `docs`/`sheets`, or modify Cloudflare settings. |
| Availability | None directly. However, abuse of the `postgres` action with resource-intensive queries could degrade database performance. |
| Likelihood | Low. The webhook URL is not publicly documented, and discovery requires either internal knowledge or brute-force URL enumeration against the Cloudflare Tunnel. |

#### Risk Decision: ACCEPTED

This finding is accepted for the following reasons:

1. **Webhook URL obscurity.** The path is redacted in this public copy; the accepted risk is tracked pending the auth-header remediation.
2. **Cloudflare Tunnel restriction.** The webhook is only accessible through the Cloudflare Tunnel, which limits the attack surface to traffic routed through `automation.example-ops.com`.
3. **Switch node validation.** While validation occurs late in the processing chain, the Switch node does reject unknown action values. Only the 16 defined actions are processed.

#### Compensating Controls

| Control | Description |
|---------|-------------|
| URL obscurity | Path is redacted in this public copy; the accepted risk is tracked pending the auth-header remediation |
| Cloudflare Tunnel | Traffic restricted to tunnel-routed requests only. No direct port exposure. |
| Switch node validation | Unknown `action` values are rejected at the Switch node with an error response |
| Rate limiting | Cloudflare provides DDoS protection and rate limiting at the tunnel edge |
| Execution logging | n8n logs all webhook executions with timestamps, input payloads, and execution results |

#### Remediation Path

1. **Webhook-level action allowlist.** Add a Function node immediately after the webhook that validates the `action` parameter against a hardcoded allowlist before the Switch node processes the request.
2. **Authentication header.** Require a shared secret in a custom header (e.g., `X-Orchestrator-Key`) validated at the webhook entry point.
3. **Input sanitization.** Add parameter-specific validation for each action handler (e.g., SQL query allowlist for the `postgres` action, message length limits for `telegram`).
4. **Webhook IP allowlist.** Configure Cloudflare Access to restrict webhook access to known source IPs.

#### Cross-References

- Architecture: [DATA_FLOW_DIAGRAM.md](DATA_FLOW_DIAGRAM.md) (Level 2 automation data flows)
- Threat Model: [THREAT_MODEL_STRIDE.md](THREAT_MODEL_STRIDE.md) (tampering and information disclosure at automation boundary)
- Policy: [POLICY_ACCESS_CONTROL.md](POLICY_ACCESS_CONTROL.md) (AC-3, SC-7)
- Policy: [POLICY_VULNERABILITY_MANAGEMENT.md](POLICY_VULNERABILITY_MANAGEMENT.md) (remediation SLA)

---

### Finding CR-001-F5: Single Point of Compromise via Tunnel Token

| Field | Value |
|-------|-------|
| **Finding ID** | CR-001-F5 |
| **Severity** | LOW |
| **CVSS 3.1 Score** | 3.4 (AV:L/AC:H/PR:H/UI:N/S:U/C:L/I:L/A:L) |
| **CWE** | CWE-522 (Insufficiently Protected Credentials) |
| **OWASP** | A07:2025 Authentication Failures |
| **NIST 800-53** | IA-5 (Authenticator Management), SC-12 (Cryptographic Key Establishment and Management), SC-23 (Session Authenticity) |
| **Status** | ACCEPTED (with compensating controls) |

#### Description

The Cloudflare Tunnel (svc-tunnel) authenticates to the Cloudflare edge network using a single tunnel token stored in the `.env` file on `primary-node`. This token is passed to the svc-tunnel container as an environment variable at startup.

Compromise of this token would allow an attacker to:

1. Register a competing tunnel connector that could intercept traffic destined for `automation.example-ops.com` or `ssh.example-ops.com`
2. Reconfigure tunnel ingress rules to redirect traffic to attacker-controlled endpoints
3. Deregister the legitimate tunnel connector, causing a service outage

The token is a long-lived credential. There is no automatic rotation schedule, and the token does not expire unless manually revoked through the Cloudflare dashboard.

#### Evidence

The tunnel token is injected via Docker Compose environment variable (sanitized):

```yaml
svc-tunnel:
  image: cloudflare/cloudflared:latest
  command: tunnel --no-autoupdate run --token ${TUNNEL_TOKEN}
  restart: unless-stopped
  network_mode: host
```

The token is a single string value. There is no certificate-based mutual authentication or secondary verification mechanism. The tunnel container runs with `network_mode: host`, giving it direct access to all host network interfaces.

#### Impact Analysis

| Dimension | Impact |
|-----------|--------|
| Confidentiality | Low. A competing tunnel connector could intercept traffic, but all tunnel traffic is encrypted with TLS. Interception would require active MITM at Cloudflare edge. |
| Integrity | Low. Tunnel route reconfiguration could redirect traffic, but the Cloudflare dashboard shows active connectors and route changes. |
| Availability | Low. Tunnel deregistration would cause a service outage for all tunnel-routed services (svc-automation web interface, SSH access). Direct IP access would remain unaffected. |
| Likelihood | Very Low. Token compromise requires host-level root access to `primary-node`. If an attacker already has root access to the host, the tunnel token is a minor concern compared to the full system compromise already achieved. |

#### Risk Decision: ACCEPTED

This finding is accepted because the prerequisite for exploitation (host-level root access) implies a broader compromise that renders the tunnel token risk immaterial in isolation. The finding is documented for completeness and to inform the long-term credential management strategy.

#### Compensating Controls

| Control | Description |
|---------|-------------|
| File permissions | `.env` file set to `chmod 600`, restricting access to root |
| SSH hardening | Host access requires ed25519 key authentication through zero-trust tunnel. No password-based SSH. |
| Secrets management | Tunnel token stored in the external secrets manager with rotation capability. `.env` is a deployment artifact. |
| Dashboard monitoring | Cloudflare dashboard displays tunnel health, active connectors, and route configuration. Anomalous connectors would be visible. |
| Runtime detection | Falco monitors for sensitive file reads on the host, including `.env` access |
| Git exclusion | `.env` is gitignored and not tracked in version control |

#### Remediation Path

No immediate remediation required. Long-term improvements:

1. Implement tunnel token rotation on a quarterly schedule through the external secrets manager
2. Configure Cloudflare notification alerts for tunnel connector registration events
3. Evaluate migration to certificate-based tunnel authentication when available

#### Cross-References

- Architecture: [DATA_FLOW_DIAGRAM.md](DATA_FLOW_DIAGRAM.md) (trust boundary at tunnel ingress)
- Threat Model: [THREAT_MODEL_STRIDE.md](THREAT_MODEL_STRIDE.md) (spoofing at tunnel boundary)
- Playbook: [PLAYBOOK_LEAKED_CREDENTIAL.md](PLAYBOOK_LEAKED_CREDENTIAL.md) (credential rotation procedure)
- Risk Register: [CIS_RISK_REGISTER.md](CIS_RISK_REGISTER.md) (network configuration findings)
- Policy: [POLICY_ACCESS_CONTROL.md](POLICY_ACCESS_CONTROL.md) (AC-6, IA-5)

---

## 4. Summary of Risk Decisions

| Finding | Severity | Status | Risk Decision | Compensating Controls | Remediation Target |
|---------|----------|--------|---------------|----------------------|-------------------|
| CR-001-F1 | HIGH | REMEDIATED | N/A | N/A | Complete |
| CR-001-F2 | MEDIUM | ACCEPTED | Environment variable injection is industry standard for single-host Docker Compose. Host-level access required for exploitation. | `.env` chmod 600, External secrets manager as source of truth, Falco monitoring, Git exclusion | 90 days (Vault AppRole migration) |
| CR-001-F3 | MEDIUM | ACCEPTED | State bucket access requires specific credentials not present on production host. OPA enforces versioning. | Scoped credentials, OPA policies, PR review gate, CI/CD isolation | 90 days (encryption at rest) |
| CR-001-F4 | MEDIUM | ACCEPTED | Webhook URL not publicly discoverable. Cloudflare Tunnel limits access. Switch node rejects unknown actions. | URL obscurity, tunnel restriction, Switch validation, execution logging | 60 days (webhook auth) |
| CR-001-F5 | LOW | ACCEPTED | Token compromise requires host root access, which implies broader compromise. | `.env` permissions, External secrets manager rotation, dashboard monitoring, Falco detection | Quarterly rotation |

---

## 5. NIST 800-53 Control Mapping

The following table maps each finding to the NIST 800-53 Rev. 5 controls that are relevant for remediation and ongoing monitoring.

| Control | Title | Findings | Implementation Notes |
|---------|-------|----------|---------------------|
| AC-3 | Access Enforcement | F4 | Webhook lacks authentication. Switch node provides late-stage validation. |
| AC-6 | Least Privilege | F1, F2 | F1 remediated with env var restriction. F2 accepted, all containers receive all secrets. |
| AC-6(1) | Authorize Access to Security Functions | F1 | Code nodes had unrestricted access to security-relevant environment variables |
| CM-6 | Configuration Settings | F1, F2 | F1 caused by insecure default. F2 is an architectural pattern requiring migration. |
| IA-5 | Authenticator Management | F5 | Long-lived tunnel token without rotation schedule |
| RA-5 | Vulnerability Monitoring and Scanning | All | Manual code review supplements automated scanning (Trivy, Semgrep, Gitleaks) |
| SA-11 | Developer Testing and Evaluation | All | This code review satisfies SA-11 for manual security testing |
| SC-7 | Boundary Protection | F4 | Input validation gap at webhook trust boundary |
| SC-12 | Cryptographic Key Establishment | F3, F5 | State encryption gap and token lifecycle management |
| SC-13 | Cryptographic Protection | F3 | State bucket lacks encryption-at-rest enforcement |
| SC-28 | Protection of Information at Rest | F1, F2, F3 | Secrets accessible in cleartext from process environment and state files |
| SI-10 | Information Input Validation | F4 | Webhook accepts unvalidated input before routing |

---

## 6. Remediation Tracking

> Status as of 2026-06-24 audit refresh: all OPEN items below have crossed their original target date and carry a Past Due flag. With the reviewed environment retired in 2026-08, remaining open items roll into the OCI re-baseline rather than being closed against the old host.

| Finding | Action Item | Owner | Target Date | Status |
|---------|------------|-------|-------------|--------|
| CR-001-F1 | Enable `N8N_RESTRICT_ENVIRONMENT_VARIABLES_ACCESS=true` | System Owner | 2026-03-22 | COMPLETE |
| CR-001-F2 | Migrate to Vault AppRole dynamic credentials | System Owner | 2026-06-22 | OPEN (POA&M, Past Due) |
| CR-001-F3 | Enable Spaces bucket encryption at rest | System Owner | 2026-06-22 | OPEN (POA&M, Past Due) |
| CR-001-F3 | Add OPA policy for storage encryption enforcement | System Owner | 2026-06-22 | OPEN (POA&M, Past Due) |
| CR-001-F3 | Enable Spaces bucket access logging | System Owner | 2026-06-22 | OPEN (POA&M, Past Due) |
| CR-001-F4 | Add webhook authentication header validation | System Owner | 2026-05-22 | OPEN (Past Due) |
| CR-001-F4 | Add action allowlist validation at webhook entry | System Owner | 2026-05-22 | OPEN (Past Due) |
| CR-001-F4 | Add per-action parameter validation | System Owner | 2026-06-22 | OPEN (Past Due) |
| CR-001-F5 | Implement quarterly tunnel token rotation | System Owner | 2026-06-22 | OPEN (Past Due) |
| CR-001-F5 | Configure Cloudflare connector registration alerts | System Owner | 2026-05-22 | OPEN (Past Due) |

---

## 7. Review and Retest Schedule

| Activity | Frequency | Next Date |
|----------|-----------|-----------|
| Full code review retest | Semi-annual | 2026-09-22 |
| Accepted finding review | Quarterly | 2026-06-22 |
| POA&M status check | Monthly | 2026-04-22 |
| Remediation verification (F1) | Complete | N/A |
| New finding triage | Continuous | Ongoing |

---

## 8. Methodology Notes

### 8.1 Scoring Approach

All findings are scored using CVSS v3.1 base metrics. Environmental and temporal metrics are not applied because the Organization is a single-operator environment where environmental factors are consistent across all findings.

### 8.2 Risk Acceptance Criteria

Findings are accepted when:

1. The residual risk after compensating controls is within the Organization's risk tolerance (as defined in [POLICY_RISK_MANAGEMENT.md](POLICY_RISK_MANAGEMENT.md))
2. Compensating controls demonstrably reduce the likelihood or impact of exploitation
3. A remediation path exists and is tracked in the POA&M with a defined target date
4. The risk acceptance is reviewed and approved by the System Owner

### 8.3 Limitations

This review is a point-in-time assessment. New findings may emerge from:

- Application updates that change default configurations
- New workflow additions that introduce untested input paths
- Infrastructure changes that alter trust boundaries
- New vulnerabilities disclosed in third-party components

Automated scanning (Trivy, Semgrep, Gitleaks, Checkov) provides continuous coverage for known vulnerability patterns. Manual code reviews should be conducted semi-annually to identify logic-level and configuration-level findings that automated tools miss.

---

## 9. Cross-References

| Document | Relevance |
|----------|-----------|
| [VULN_WRITEUP_N8N_CREDENTIAL_EXPOSURE.md](VULN_WRITEUP_N8N_CREDENTIAL_EXPOSURE.md) | Detailed writeup for Finding CR-001-F1 |
| [POLICY_ACCESS_CONTROL.md](POLICY_ACCESS_CONTROL.md) | AC-6 (Least Privilege) and AC-3 (Access Enforcement) implementation |
| [POLICY_VULNERABILITY_MANAGEMENT.md](POLICY_VULNERABILITY_MANAGEMENT.md) | Vulnerability classification, remediation SLAs, exception handling |
| [POLICY_CHANGE_MANAGEMENT.md](POLICY_CHANGE_MANAGEMENT.md) | Change control for remediation deployments |
| [POLICY_RISK_MANAGEMENT.md](POLICY_RISK_MANAGEMENT.md) | Risk acceptance criteria and tolerance thresholds |
| [RISK_ASSESSMENT.md](RISK_ASSESSMENT.md) | Platform risk assessment with threat scenarios |
| [CIS_RISK_REGISTER.md](CIS_RISK_REGISTER.md) | Container hardening findings, accepted risks |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | Remediation tracking for open items |
| [DATA_FLOW_DIAGRAM.md](DATA_FLOW_DIAGRAM.md) | Trust boundaries and data flow context for each finding |
| [THREAT_MODEL_STRIDE.md](THREAT_MODEL_STRIDE.md) | STRIDE threat analysis informing finding severity |
| [PLAYBOOK_LEAKED_CREDENTIAL.md](PLAYBOOK_LEAKED_CREDENTIAL.md) | Response procedure for credential exposure |
| [AI_THREAT_CATALOG.md](AI_THREAT_CATALOG.md) | LLM07 Insecure Plugin Design parallel for F1 |

---

## 10. Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Author | Information Security Officer | 2026-03-22 | /s/ |
| Reviewer | System Owner | 2026-03-22 | /s/ |
| Approver | System Owner | 2026-03-22 | /s/ |

---

*This document is classified as Internal Use Only. Distribution is limited to personnel with a need to know. Do not share outside the Organization without written authorization from the System Owner.*
