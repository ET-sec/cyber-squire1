# IAM Access Review Process

Organization Infrastructure Identity and Access Management

**Last Review:** 2026-04-24
**Next Review:** 2026-09-24
**Cadence:** Quarterly
**Owner:** System Owner (admin@example-ops.com)
**NIST 800-53 Controls:** AC-2 (Account Management), AC-6 (Least Privilege), AU-6 (Audit Review)

---

## 1. Overview

This document defines the access review process for Organization infrastructure. All privileged access follows the principle of least privilege with Just-In-Time (JIT) elevation for administrative tasks.

**Key principles:**
- Default access is read-only or operator-level (minimum required for daily work)
- Administrative access requires an explicit request with business justification
- All elevated sessions auto-expire after a maximum of 4 hours
- Every access request, approval, and session is audited
- Quarterly reviews verify no unauthorized access persists

**Compliance alignment:**
| Control | Description | Implementation |
|---------|-------------|----------------|
| NIST AC-2 | Account Management | Access gateway user lifecycle via `tctl users` commands |
| NIST AC-6 | Least Privilege | Operator role as default, admin requires JIT request |
| NIST AU-6 | Audit Review | Quarterly review of access requests and session recordings |
| NIST AC-2(2) | Automated Temporary Account Removal | `max_session_ttl: 4h` auto-expires admin sessions |
| NIST AC-6(1) | Authorize Access to Security Functions | Admin role gated behind request/approve workflow |

---

## 2. Current Access Inventory

### Gateway-Managed Access

| User | System | Access Method | Roles | MFA | Session TTL | Purpose |
|------|--------|---------------|-------|-----|-------------|---------|
| sysadmin | alpha-node (10.100.1.10) | Access gateway SSH | editor, access, operator | TOTP (OTP) | 8h | Daily operations, can request admin |
| event-handler | Access gateway internal | Access gateway service | event-handler | N/A | N/A | Audit event export |

### Non-Gateway Access Paths

| User | System | Access Method | Authentication | Restriction |
|------|--------|---------------|---------------|-------------|
| root | alpha-node (10.100.1.10) | Direct SSH via zero-trust tunnel | ed25519 key (~/.ssh/id_ed25519) | Break-glass only, emergency use |
| sysadmin | Automation (automation.example-ops.com) | HTTPS via zero-trust tunnel | Password auth | Workflow management |
| admin | Identity provider (svc-identity) | Container-internal | Username/password | SSO administration |

### Service-to-Service Access

| Service | Database/Resource | Method | Credential Source |
|---------|------------------|--------|-------------------|
| svc-automation | svc-db (PostgreSQL) | Internal Docker network | .env (DB_USER/DB_PASS) |
| svc-monitor | Docker socket plus filesystem mounts (`/proc`, `/sys/fs/cgroup`, `/etc/os-release`, `/var/log`, observability conf.d) | Docker socket plus filesystem mounts | `DD_API_KEY` env var |
| svc-detection | Kernel (eBPF) | SYS_ADMIN capability | No credentials |
| svc-ai-gateway | AI provider API | HTTPS | `OPENCLAW_ANTHROPIC_KEY` env var |

---

## 3. JIT Access Workflow

The Just-In-Time access model ensures administrative privileges are never persistent. The operator role can request temporary elevation to the admin role.

### Request Flow

```
 [1] Operator requests admin role
    tctl request create --roles=admin --reason="<justification>" sysadmin
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

**Step 1. Create access request:**
```bash
# From local machine or via access gateway proxy
ssh alpha-node 'docker exec svc-gateway tctl request create \
 --roles=admin \
 --reason="Emergency patch deployment for CVE-2026-XXXX" \
 sysadmin'
# Returns: request ID (UUID)
```

**Step 2. List pending requests:**
```bash
ssh alpha-node 'docker exec svc-gateway tctl request ls'
# Shows: Token, Requestor, Roles, Status, Reason
```

**Step 3. Approve the request:**
```bash
ssh alpha-node 'docker exec svc-gateway tctl request approve <request-id>'
```

**Step 4. Verify approval and expiry:**
```bash
ssh alpha-node 'docker exec svc-gateway tctl request ls --format=json'
# Verify: state=2 (APPROVED), expires field shows ~4h from approval
```

**Step 5. Deny a request (if inappropriate):**
```bash
ssh alpha-node 'docker exec svc-gateway tctl request deny <request-id>'
```

### Audit Trail

Every access request generates a retrievable record:
```bash
# View specific request details
ssh alpha-node 'docker exec svc-gateway tctl get access_request/<request-id> --format=yaml'

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

### Access Gateway Custom Roles

| Role | Purpose | Node Access | Admin Access | Session TTL | Requestable |
|------|---------|-------------|--------------|-------------|-------------|
| **operator** | Daily operations | `env: production` nodes, root login | None | 8h | Can request `admin` |
| **admin** | Elevated JIT access | All nodes (`*: *`), root login | All resources, all verbs | 4h | Granted via JIT only |
| **auditor** | Compliance review | `env: production` (read sessions only) | None | 12h | Not requestable; assigned directly |

**Phase 17 Squire roles:** SOC Analyst (HITL Reviewer), Squire Operator, and Interview Presenter are defined in `IAM_RBAC_ROLE_MAP.md` Section 21 and are not duplicated here. The 60-day audit cadence for those roles is covered in Section 5.7 below.

### Access Gateway Built-in Roles

| Role | Purpose | Permissions | Session TTL |
|------|---------|-------------|-------------|
| **editor** | Resource management | Create/read/update access gateway resources | 30h |
| **access** | SSH/app/db access | Connect to registered resources | 30h |
| **auditor** | Audit and compliance | Read sessions, events, alerts, reports | 30h |

### Role Assignment Matrix

| User | editor | access | operator | admin | auditor |
|------|--------|--------|----------|-------|---------|
| sysadmin | Assigned | Assigned | Assigned | JIT only | Available |

**Key constraints:**
- `admin` role is never permanently assigned. Access is granted only via JIT request
- `operator` role includes `request.roles: ['admin']` enabling JIT elevation
- `forward_agent: false` on all custom roles prevents SSH agent forwarding attacks
- Session recordings use `node-sync` mode for resilient capture

---

## 5. Review Schedule

### Quarterly Access Review Checklist

Perform on the first business day of each quarter. Document findings in this file.

**5.1 Access Gateway User Audit**
```bash
# List all access gateway users and their roles
ssh alpha-node 'docker exec svc-gateway tctl users ls'
```
- [ ] Verify only authorized users exist
- [ ] Verify role assignments match the Role Assignment Matrix (Section 4)
- [ ] Remove any users no longer requiring access: `tctl users rm <username>`

**5.2 Access Gateway Role Configuration Audit**
```bash
# List all roles and verify definitions
ssh alpha-node 'docker exec svc-gateway tctl get roles --format=json'

# Verify admin role TTL is still 4h
ssh alpha-node 'docker exec svc-gateway tctl get role/admin --format=yaml' | grep max_session_ttl

# Verify operator role TTL is still 8h
ssh alpha-node 'docker exec svc-gateway tctl get role/operator --format=yaml' | grep max_session_ttl
```
- [ ] Verify no unauthorized roles were created
- [ ] Verify admin role `max_session_ttl` remains `4h0m0s`
- [ ] Verify operator role `max_session_ttl` remains `8h0m0s`
- [ ] Verify operator can only request `admin` (no additional roles)

**5.3 Access Request History Review**
```bash
# List all access requests (active and expired)
ssh alpha-node 'docker exec svc-gateway tctl request ls'

# Get detailed request information
ssh alpha-node 'docker exec svc-gateway tctl get access_request/<id> --format=yaml'
```
- [ ] Review all access requests from the past 90 days
- [ ] Verify each request had a valid business justification
- [ ] Flag any requests without reasons or with suspicious patterns
- [ ] Verify expired requests were not manually extended

**5.4 Session Recording Review**
```bash
# List recorded sessions
ssh alpha-node 'docker exec svc-gateway tctl recordings ls'
```
- [ ] Spot-check at least 2 admin-elevated sessions
- [ ] Verify session recordings are being stored correctly
- [ ] Check for unusual command patterns in elevated sessions

**5.5 Break-Glass SSH Key Audit**
- [ ] Verify direct SSH key (`~/.ssh/id_ed25519`) is only used for emergencies
- [ ] Review zero-trust tunnel access logs for direct SSH connections
- [ ] Confirm no additional SSH keys were added to the VPS: `ssh alpha-node 'cat ~/.ssh/authorized_keys'`

**5.6 Service Account Review**
- [ ] Verify automation dashboard password was not changed without authorization
- [ ] Verify identity provider admin credentials are current
- [ ] Review Docker container access (no new privileged containers)
- [ ] Verify `.env` file permissions remain `chmod 600`: `ssh alpha-node 'stat -c %a /opt/platform/.env'`
- [ ] Verify n8n MCP token (`N8N_MCP_TOKEN` in Doppler) has been rotated within the past quarter

### 5.7 Squire Subsystem Access Review (Phase 17, 60-day cadence)

> **Key Point:** Phase 17 introduces ephemeral HMAC tokens for Squire `/alert` ingress, plus per-interview tokens for the interview-presenter demo path. Token lifecycle is audited on a 60-day cycle per `HITL_POLICY.md` section 6. The SQUIRE_INTERVIEW_TOKENS rotation pattern is the authoritative per-interview cadence.

| Activity | Frequency | Next Date | Evidence |
|----------|-----------|-----------|----------|
| HITL production token rotation audit | 60 days | 2026-06-22 | `ir_rotation_events` table, HITL_POLICY section 6 |
| Per-interview token issuance audit | Per-interview plus monthly aggregate | Monthly first business day | Issued and revoked list in `ir_rotation_events` |
| Squire actions allow-list audit | 60 days | 2026-06-22 | `actions.yml` git log, change control record |
| NeMo rail config audit | 60 days | 2026-06-22 | `svc-nemo-config` git log |
| AI supply chain register review | 60 days | 2026-06-22 | AI_SUPPLY_CHAIN_REGISTER.md |

<!-- TODO(et): verify the `squire` database/user exists in svc-db with the credentials referenced in the commands below; confirm gateway-config.yaml on production still has operator request.roles: ['admin']. Last verified 2026-03-11. -->

**5.7.1 Phase 17 token rotation check commands**

```bash
# Verify ir_rotation_events log has entries for the window
ssh host-alpha 'docker exec svc-db psql -U squire -d squire -c "SELECT token_id, event_type, created_at FROM ir_rotation_events WHERE created_at > NOW() - INTERVAL '\''60 days'\'' ORDER BY created_at DESC;"'

# Verify interview tokens are revoked within 24h of use
ssh host-alpha 'docker exec svc-db psql -U squire -d squire -c "SELECT token_id, issued_at, revoked_at, (revoked_at - issued_at) AS lifetime FROM ir_rotation_events WHERE token_class = '\''interview'\'' AND revoked_at IS NOT NULL;"'
```

- [ ] Every production token issuance has a paired rotation event within 60 days
- [ ] Every interview token has a revocation event within 24h of issuance
- [ ] No orphan tokens (issued with no matching audit row)
- [ ] Squire Operator role not granted outside documented JIT windows

---

## 6. Escalation Path

### Access Revocation

**Remove a user entirely:**
```bash
ssh alpha-node 'docker exec svc-gateway tctl users rm <username>'
```

**Remove a role from a user:**
```bash
ssh alpha-node 'docker exec svc-gateway tctl users update <username> --set-roles=<remaining-roles>'
```

**Lock a user (immediate, preserves account):**
```bash
ssh alpha-node 'docker exec svc-gateway tctl lock --user=<username> --message="Security incident" --ttl=24h'
```

**Deny a pending access request:**
```bash
ssh alpha-node 'docker exec svc-gateway tctl request deny <request-id>'
```

**Delete an access request:**
```bash
ssh alpha-node 'docker exec svc-gateway tctl request rm <request-id>'
```

### Emergency Procedures

**Suspected compromise (immediate lockout):**
1. Lock the user account: `tctl lock --user=<username> --message="Suspected compromise"`
2. Revoke all active sessions (restart access gateway if needed)
3. Rotate access gateway CA certificates: `tctl auth rotate --type=user`
4. Review session recordings for the locked user
5. Change break-glass SSH key if SSH access may be compromised
6. Notify security contact (admin@example-ops.com)

**Access gateway service failure (break-glass access):**
1. Use direct SSH via zero-trust tunnel: `ssh alpha-node`
2. Check access gateway container: `docker logs svc-gateway --tail 50`
3. Restart access gateway: `docker compose restart svc-gateway`
4. Document the incident and review what caused the failure

---

## 7. Enterprise Upgrade Path

The current access gateway Community Edition provides solid JIT access controls. The following features require an enterprise license and are documented as future enhancements:

| Feature | Edition Required | Benefit |
|---------|-----------------|---------|
| OIDC/SAML SSO | Enterprise | Integrate with identity provider for centralized identity |
| Resource-level access requests | Enterprise | Request access to specific nodes, not just roles |
| ChatOps approval (Slack/Teams) | Enterprise | Approve requests from messaging platforms |
| Access Request plugins | Enterprise | PagerDuty, ServiceNow, Jira integration |
| FedRAMP compliance mode | Enterprise | Additional audit controls for government work |
| Hardware key support (PIV) | Enterprise | YubiKey-based MFA instead of TOTP |
| Session lock (concurrent limit) | Enterprise | Limit concurrent admin sessions |

**Current limitations (Community Edition):**
- Access requests can only be approved via `tctl` CLI (no web UI approval)
- Self-approval is possible in the single-operator environment. The audit trail is the compensating control.
- No OIDC/SAML connector for identity provider integration
- No dual-approval workflow (requires Enterprise with approval thresholds)

**Recommended upgrade trigger:** When a second operator joins the team, upgrade to Enterprise for dual-approval workflows and SSO integration.

---

## Review History

| Date | Reviewer | Findings | Actions Taken |
|------|----------|----------|---------------|
| 2026-03-11 | System Owner | Initial review, baseline established | Created operator/admin/auditor roles, tested JIT workflow, documented process |
| 2026-04-24 | System Owner | Phase 17 extension, 60-day Squire token rotation audit cadence added | Section 5.7 added. SOC Analyst, Squire Operator, Interview Presenter roles referenced in IAM_RBAC_ROLE_MAP. |
| 2026-06-24 | System Owner | Review extended pending Phase 17 IAM updates; cadence formalized as quarterly; auditor 12h TTL row, Phase 17 cross-reference, n8n MCP token rotation check, and Doppler-aligned service credential references added | Header updated to 2026-04-24 / Next 2026-09-24; Section 2 svc-monitor and svc-ai-gateway rows aligned to real Doppler key names; double-hyphen patterns replaced; Section 5.6 n8n MCP token line added |

---

## Cross-References

| Document | Relationship |
|----------|-------------|
| [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) | System Security Plan with NIST 800-53 control mapping |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | Tracks findings and remediation milestones |
| [IAM_RBAC_ROLE_MAP.md](IAM_RBAC_ROLE_MAP.md) | Core 3-tier RBAC plus Phase 17 Squire roles |
| [HITL_POLICY.md](HITL_POLICY.md) | Section 6: HITL production and per-interview token rotation |
| [SQUIRE_SSP.md](SQUIRE_SSP.md) | Squire subsystem SSP with AC-1, AC-2, AC-3 controls |
| [README.md](README.md) | GRC library index and reading guide |
