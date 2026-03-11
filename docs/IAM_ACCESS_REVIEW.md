# IAM Access Review Process

CoreDirective Infrastructure Identity and Access Management

**Last Review:** 2026-03-11
**Next Review:** 2026-04-11
**Owner:** Emmanuel Tigoue (etigoue@tigouetheory.com)
**NIST 800-53 Controls:** AC-2 (Account Management), AC-6 (Least Privilege), AU-6 (Audit Review)

---

## 1. Overview

This document defines the access review process for CoreDirective infrastructure. All privileged access follows the principle of least privilege with Just-In-Time (JIT) elevation for administrative tasks.

**Key principles:**
- Default access is read-only or operator-level (minimum required for daily work)
- Administrative access requires an explicit request with business justification
- All elevated sessions auto-expire after a maximum of 4 hours
- Every access request, approval, and session is audited
- Monthly reviews verify no unauthorized access persists

**Compliance alignment:**
| Control | Description | Implementation |
|---------|-------------|----------------|
| NIST AC-2 | Account Management | Teleport user lifecycle via `tctl users` commands |
| NIST AC-6 | Least Privilege | Operator role as default, admin requires JIT request |
| NIST AU-6 | Audit Review | Monthly review of access requests and session recordings |
| NIST AC-2(2) | Automated Temporary Account Removal | `max_session_ttl: 4h` auto-expires admin sessions |
| NIST AC-6(1) | Authorize Access to Security Functions | Admin role gated behind request/approve workflow |

---

## 2. Current Access Inventory

### Teleport-Managed Access

| User | System | Access Method | Roles | MFA | Session TTL | Purpose |
|------|--------|---------------|-------|-----|-------------|---------|
| etigoue | cd-alpha (161.35.0.184) | Teleport SSH | editor, access, operator | TOTP (OTP) | 8h | Daily operations, can request admin |
| event-handler | Teleport internal | Teleport service | event-handler | N/A | N/A | Audit event export |

### Non-Teleport Access Paths

| User | System | Access Method | Authentication | Restriction |
|------|--------|---------------|---------------|-------------|
| root | cd-alpha (161.35.0.184) | Direct SSH via Cloudflare Tunnel | ed25519 key (~/.ssh/id_ed25519) | Break-glass only, emergency use |
| etigoue | n8n (n8n.tigouetheory.com) | HTTPS via Cloudflare Tunnel | Password auth | Workflow management |
| admin | Keycloak (cd-service-keycloak) | Container-internal port 8080 | Username/password | SSO administration |

### Service-to-Service Access

| Service | Database/Resource | Method | Credential Source |
|---------|------------------|--------|-------------------|
| cd-service-n8n | cd-service-db (PostgreSQL) | Internal Docker network | .env (CD_DB_USER/CD_DB_PASS) |
| cd-service-datadog | Docker socket | Volume mount | API key in .env |
| cd-service-falco | Kernel (eBPF) | SYS_ADMIN capability | No credentials |
| openclaw-gateway | Anthropic API | HTTPS | OPENCLAW_ANTHROPIC_KEY in .env |

---

## 3. JIT Access Workflow

The Just-In-Time access model ensures administrative privileges are never persistent. The operator role can request temporary elevation to the admin role.

### Request Flow

```
  [1] Operator requests admin role
       tctl request create --roles=admin --reason="<justification>" etigoue
                    |
  [2] Request logged (state: PENDING)
       Request ID generated, expiry set to max_session_ttl (4h)
                    |
  [3] Approver reviews and approves
       tctl request approve <request-id>
                    |
  [4] Session active (state: APPROVED)
       Admin role granted, session begins
       All commands recorded (node-sync mode)
                    |
  [5] Session auto-expires after max_session_ttl (4h)
       Admin role automatically revoked
       No manual cleanup required
```

### Step-by-Step Commands

**Step 1 -- Create access request:**
```bash
# From local machine or via Teleport proxy
ssh cd-alpha 'docker exec cd-service-teleport tctl request create \
  --roles=admin \
  --reason="Emergency patch deployment for CVE-2026-XXXX" \
  etigoue'
# Returns: request ID (UUID)
```

**Step 2 -- List pending requests:**
```bash
ssh cd-alpha 'docker exec cd-service-teleport tctl request ls'
# Shows: Token, Requestor, Roles, Status, Reason
```

**Step 3 -- Approve the request:**
```bash
ssh cd-alpha 'docker exec cd-service-teleport tctl request approve <request-id>'
```

**Step 4 -- Verify approval and expiry:**
```bash
ssh cd-alpha 'docker exec cd-service-teleport tctl request ls --format=json'
# Verify: state=2 (APPROVED), expires field shows ~4h from approval
```

**Step 5 -- Deny a request (if inappropriate):**
```bash
ssh cd-alpha 'docker exec cd-service-teleport tctl request deny <request-id>'
```

### Audit Trail

Every access request generates a retrievable record:
```bash
# View specific request details
ssh cd-alpha 'docker exec cd-service-teleport tctl get access_request/<request-id> --format=yaml'

# Fields captured:
# - user: who requested
# - roles: what was requested
# - request_reason: business justification
# - state: 1=PENDING, 2=APPROVED, 3=DENIED
# - created: request timestamp
# - expires: auto-expiry timestamp
# - session_ttl: maximum session duration
```

---

## 4. Role Definitions

### Teleport Custom Roles

| Role | Purpose | Node Access | Admin Access | Session TTL | Requestable |
|------|---------|-------------|--------------|-------------|-------------|
| **operator** | Daily operations | `env: production` nodes, root login | None | 8h | Can request `admin` |
| **admin** | Elevated JIT access | All nodes (`*: *`), root login | All resources, all verbs | 4h | Granted via JIT only |

### Teleport Built-in Roles

| Role | Purpose | Permissions | Session TTL |
|------|---------|-------------|-------------|
| **editor** | Resource management | Create/read/update Teleport resources | 30h |
| **access** | SSH/app/db access | Connect to registered resources | 30h |
| **auditor** | Audit and compliance | Read sessions, events, alerts, reports | 30h |

### Role Assignment Matrix

| User | editor | access | operator | admin | auditor |
|------|--------|--------|----------|-------|---------|
| etigoue | Assigned | Assigned | Assigned | JIT only | Available |

**Key constraints:**
- `admin` role is never permanently assigned -- only accessible via JIT request
- `operator` role includes `request.roles: ['admin']` enabling JIT elevation
- `forward_agent: false` on all custom roles prevents SSH agent forwarding attacks
- Session recordings use `node-sync` mode for resilient capture

---

## 5. Review Schedule

### Monthly Access Review Checklist

Perform on the first business day of each month. Document findings in this file.

**5.1 Teleport User Audit**
```bash
# List all Teleport users and their roles
ssh cd-alpha 'docker exec cd-service-teleport tctl users ls'
```
- [ ] Verify only authorized users exist
- [ ] Verify role assignments match the Role Assignment Matrix (Section 4)
- [ ] Remove any users no longer requiring access: `tctl users rm <username>`

**5.2 Role Configuration Audit**
```bash
# List all roles and verify definitions
ssh cd-alpha 'docker exec cd-service-teleport tctl get roles --format=json'

# Verify admin role TTL is still 4h
ssh cd-alpha 'docker exec cd-service-teleport tctl get role/admin --format=yaml' | grep max_session_ttl

# Verify operator role TTL is still 8h
ssh cd-alpha 'docker exec cd-service-teleport tctl get role/operator --format=yaml' | grep max_session_ttl
```
- [ ] Verify no unauthorized roles were created
- [ ] Verify admin role `max_session_ttl` remains `4h0m0s`
- [ ] Verify operator role `max_session_ttl` remains `8h0m0s`
- [ ] Verify operator can only request `admin` (no additional roles)

**5.3 Access Request History Review**
```bash
# List all access requests (active and expired)
ssh cd-alpha 'docker exec cd-service-teleport tctl request ls'

# Get detailed request information
ssh cd-alpha 'docker exec cd-service-teleport tctl get access_request/<id> --format=yaml'
```
- [ ] Review all access requests from the past 30 days
- [ ] Verify each request had a valid business justification
- [ ] Flag any requests without reasons or with suspicious patterns
- [ ] Verify expired requests were not manually extended

**5.4 Session Recording Review**
```bash
# List recorded sessions
ssh cd-alpha 'docker exec cd-service-teleport tctl recordings ls'
```
- [ ] Spot-check at least 2 admin-elevated sessions
- [ ] Verify session recordings are being stored correctly
- [ ] Check for unusual command patterns in elevated sessions

**5.5 Break-Glass SSH Key Audit**
- [ ] Verify direct SSH key (`~/.ssh/id_ed25519`) is only used for emergencies
- [ ] Review Cloudflare Tunnel access logs for direct SSH connections
- [ ] Confirm no additional SSH keys were added to the droplet: `ssh cd-alpha 'cat ~/.ssh/authorized_keys'`

**5.6 Service Account Review**
- [ ] Verify n8n dashboard password was not changed without authorization
- [ ] Verify Keycloak admin credentials are current
- [ ] Review Docker container access (no new privileged containers)
- [ ] Verify `.env` file permissions remain `chmod 600`: `ssh cd-alpha 'stat -c %a /root/COREDIRECTIVE_ENGINE/.env'`

---

## 6. Escalation Path

### Access Revocation

**Remove a user entirely:**
```bash
ssh cd-alpha 'docker exec cd-service-teleport tctl users rm <username>'
```

**Remove a role from a user:**
```bash
ssh cd-alpha 'docker exec cd-service-teleport tctl users update <username> --set-roles=<remaining-roles>'
```

**Lock a user (immediate, preserves account):**
```bash
ssh cd-alpha 'docker exec cd-service-teleport tctl lock --user=<username> --message="Security incident" --ttl=24h'
```

**Deny a pending access request:**
```bash
ssh cd-alpha 'docker exec cd-service-teleport tctl request deny <request-id>'
```

**Delete an access request:**
```bash
ssh cd-alpha 'docker exec cd-service-teleport tctl request rm <request-id>'
```

### Emergency Procedures

**Suspected compromise -- immediate lockout:**
1. Lock the user account: `tctl lock --user=<username> --message="Suspected compromise"`
2. Revoke all active sessions (restart Teleport if needed)
3. Rotate Teleport CA certificates: `tctl auth rotate --type=user`
4. Review session recordings for the locked user
5. Change break-glass SSH key if SSH access may be compromised
6. Notify security contact (etigoue@tigouetheory.com)

**Teleport service failure -- break-glass access:**
1. Use direct SSH via Cloudflare Tunnel: `ssh cd-alpha`
2. Check Teleport container: `docker logs cd-service-teleport --tail 50`
3. Restart Teleport: `docker compose restart cd-service-teleport`
4. Document the incident and review what caused the failure

---

## 7. Enterprise Upgrade Path

The current Teleport Community Edition provides solid JIT access controls. The following features require Teleport Enterprise and are documented as future enhancements:

| Feature | Edition Required | Benefit |
|---------|-----------------|---------|
| OIDC/SAML SSO | Enterprise | Integrate with Keycloak for centralized identity |
| Resource-level access requests | Enterprise | Request access to specific nodes, not just roles |
| ChatOps approval (Slack/Teams) | Enterprise | Approve requests from messaging platforms |
| Access Request plugins | Enterprise | PagerDuty, ServiceNow, Jira integration |
| FedRAMP compliance mode | Enterprise | Additional audit controls for government work |
| Hardware key support (PIV) | Enterprise | YubiKey-based MFA instead of TOTP |
| Session lock (concurrent limit) | Enterprise | Limit concurrent admin sessions |

**Current limitations (Community Edition):**
- Access requests can only be approved via `tctl` CLI (no web UI approval)
- Self-approval is possible (single-operator environment) -- mitigated by audit trail
- No OIDC/SAML connector for Keycloak integration
- No dual-approval workflow (requires Enterprise with approval thresholds)

**Recommended upgrade trigger:** When a second operator joins the team, upgrade to Enterprise for dual-approval workflows and SSO integration.

---

## Review History

| Date | Reviewer | Findings | Actions Taken |
|------|----------|----------|---------------|
| 2026-03-11 | Emmanuel Tigoue | Initial review -- baseline established | Created operator/admin/auditor roles, tested JIT workflow, documented process |
