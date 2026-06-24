# Incident Response Playbook: Unauthorized Access

**Document ID:** IR-PLAY-004
**Version:** 1.0
**Last Updated:** 2026-03-11
**Owner:** Incident Commander
**Classification:** Internal Use Only
**NIST 800-53 Controls:** IR-4 (Incident Handling), IR-5 (Incident Monitoring), IR-6 (Incident Reporting), AC-2 (Account Management), AC-6 (Least Privilege), AU-6 (Audit Review)

---

### Investigation Flowchart

```
┌─────────────────────┐
│   ALERT TRIGGERED    │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│    VERIFY ALERT      │
│  (Confirm, not false │
│   positive or noise) │
└──────────┬──────────┘
           │
           v
┌─────────────────────────┐
│  IDENTIFY ACCESS VECTOR  │
├─────────┬───────┬────────┤
│         │       │        │
v         v       v        v
┌────────┐ ┌──────┐ ┌─────────┐ ┌───────────┐
│TUNNEL  │ │ SSH  │ │CONTAINER│ │CREDENTIAL │
│BREACH  │ │COMPRO│ │ ESCAPE  │ │  THEFT    │
│        │ │MISE  │ │         │ │           │
└───┬────┘ └──┬───┘ └────┬────┘ └─────┬─────┘
    │         │          │             │
    v         v          v             v
┌────────┐ ┌──────┐ ┌─────────┐ ┌───────────┐
│Check   │ │Check │ │Check    │ │Check      │
│Cloud-  │ │auth  │ │Falco    │ │login      │
│flare   │ │logs  │ │alerts   │ │history    │
│logs    │ │      │ │         │ │           │
└───┬────┘ └──┬───┘ └────┬────┘ └─────┬─────┘
    │         │          │             │
    v         v          v             v
┌────────┐ ┌──────┐ ┌─────────┐ ┌───────────┐
│Block   │ │Revoke│ │Isolate  │ │Rotate     │
│source  │ │keys  │ │host     │ │creds      │
│IP      │ │      │ │         │ │           │
└───┬────┘ └──┬───┘ └────┬────┘ └─────┬─────┘
    │         │          │             │
    v         v          v             v
┌────────┐ ┌──────┐ ┌─────────┐ ┌───────────┐
│Audit   │ │Session│ │Full     │ │Access     │
│session │ │review│ │forensics│ │review     │
└───┬────┘ └──┬───┘ └────┬────┘ └─────┬─────┘
    │         │          │             │
    └─────────┴──────┬───┴─────────────┘
                     │
                     v
        ┌────────────────────────┐
        │  IS ATTACKER STILL     │
        │  ACTIVE?               │
        ├────────────┬───────────┤
        │ YES        │ NO        │
        v            v           │
 ┌──────────────┐ ┌─────────────┐
 │ IMMEDIATE    │ │ FORENSIC    │
 │ CONTAINMENT  │ │ INVESTIGA-  │
 │ - Kill sessions│ │ TION       │
 │ - Lock accounts│ │ - Preserve │
 │ - Block IPs  │ │   evidence  │
 │              │ │ - Timeline  │
 └──────┬───────┘ └──────┬──────┘
        │                │
        └───────┬────────┘
                │
                v
   ┌────────────────────────────┐
   │  IS DATA EXFILTRATION      │
   │  CONFIRMED?                │
   ├──────────────┬─────────────┤
   │ YES          │ NO          │
   v              v             │
┌──────────────┐ ┌─────────────┐
│ ACTIVATE     │ │ CONTINUE    │
│ DATA BREACH  │ │ INVESTIGA-  │
│ PROCEDURE    │ │ TION        │
│ - Notify     │ │ - Scope     │
│   legal      │ │   impact    │
│ - Assess     │ │ - Trace     │
│   impact     │ │   access    │
└──────┬───────┘ └──────┬──────┘
       │                │
       └───────┬────────┘
               │
               v
  ┌────────────────────────────┐
  │  EVIDENCE OF PERSISTENCE?   │
  │  (backdoors, cron jobs,     │
  │   new accounts, rogue keys) │
  ├──────────────┬─────────────┤
  │ YES          │ NO          │
  v              v             │
┌──────────────┐ ┌─────────────┐
│ FULL REBUILD │ │ PATCH AND   │
│ - Rotate all │ │ MONITOR     │
│   keys/certs │ │ - Apply     │
│ - Rebuild    │ │   fixes     │
│   containers │ │ - Increase  │
│ - Reimage    │ │   logging   │
│   if needed  │ │ - Schedule  │
│              │ │   review    │
└──────┬───────┘ └──────┬──────┘
       │                │
       └───────┬────────┘
               │
               v
     ┌──────────────────────┐
     │  POST-INCIDENT       │
     │  REPORT (72 hours)   │
     └──────────────────────┘
```

---

## 1. Purpose

This playbook provides step-by-step procedures for responding to unauthorized access to the Organization infrastructure. This includes unauthorized SSH sessions, unauthorized users in the identity provider, suspicious gateway sessions, compromised user accounts, or any access that violates the principle of least privilege.

---

## 2. Scope

Applies to all access paths into the Organization infrastructure:
- **svc-gateway**: SSH access, session recording, JIT (just-in-time) access requests, certificate-based authentication
- **svc-identity**: Identity provider, SSO, user management, role assignments
- **svc-tunnel**: Zero-trust tunnel ingress (`n8n.example-ops.com`, `ssh.example-ops.com`, `squire.example-ops.com` for the Phase 17 `/alert` webhook with `X-Squire-Token`, `langfuse.example-ops.com` for the Langfuse web UI)
- **Direct SSH**: Emergency/break-glass SSH access to `alpha-node`
- **svc-automation**: Web UI and API access to the orchestration platform
- **svc-db**: Direct database connections
- **svc-secrets**: Secrets engine access
- **Code repository platform**: Repository access, CI/CD pipeline access

---

## 3. Severity Classification

| Severity | Criteria |
|----------|----------|
| **SEV-1 (Critical)** | Confirmed unauthorized access to `svc-db`, `svc-secrets`, `svc-gateway` admin, or root SSH; evidence of data exfiltration or system modification |
| **SEV-2 (High)** | Unauthorized user account created in `svc-identity` or `svc-gateway`; suspicious gateway session with unexplained commands; compromised admin credential |
| **SEV-3 (Medium)** | Failed authentication attempts from unusual sources exceeding threshold; unauthorized access to non-sensitive service; JIT request from unknown identity |
| **SEV-4 (Low)** | Single failed authentication attempt from unknown source; user accessed a resource outside their normal pattern but within their permissions |

---

## 4. Detection Triggers

### 4.1 svc-gateway (Session and Access Monitoring)

- [ ] **Unexpected session initiated**: session from unrecognized user, IP, or certificate <!-- TODO(et): no Sigma rule for `event=session.start AND user NOT IN allowlist`; currently Datadog monitor only. Add Sigma rule. -->
- [ ] **Session from unusual geography**: login from a country or region with no authorized users
- [ ] **JIT access request from unknown identity**: access request submitted by a user not in the approved roster <!-- TODO(et): no Sigma rule on Teleport `access_request.create`. Add one. -->
- [ ] **Session with suspicious commands**: commands related to data exfiltration, privilege escalation, or reconnaissance detected in session recording
- [ ] **Certificate authentication failure**: attempts to use expired, revoked, or unknown certificates
- [ ] **Break-glass SSH access used**: direct root SSH login (bypassing gateway) detected <!-- TODO(et): no dedicated Sigma rule for `sshd Accepted publickey for root from <not-allowlisted-ip>`. Add one. -->


### 4.2 svc-identity (Identity Provider Audit Events)

- [ ] **New user account created**: admin event log shows user creation not initiated by System Owner <!-- TODO(et): add a Sigma rule on the Keycloak admin event for user CREATE outside the approved actor list (AC-2 critical). -->
- [ ] **Role escalation**: user assigned admin or elevated role without a corresponding change request <!-- TODO(et): add a Sigma rule on Keycloak admin events for role-mapping CREATE. -->
- [ ] **Password reset for admin account**: password change on privileged account not initiated by the account owner
- [ ] **SSO configuration changed**: SAML/OIDC provider settings modified
- [ ] **Brute force attempts**: multiple failed logins against the same or multiple accounts

### 4.3 svc-detection (eBPF Runtime Alerts)

- [ ] **SSH connection to non-standard port**: svc-detection detects SSH traffic on unexpected ports <!-- TODO(et): existing container-shell-spawn-restricted.yml does not cover host-level SSH. Add a dedicated Sigma rule. -->
- [ ] **Unauthorized SSH key usage**: SSH authentication using a key not in the approved key list
- [ ] **Privilege escalation in container**: `sudo`, `su`, or capability changes detected within a container
- [ ] **Unauthorized cron job or at job**: scheduled task created inside a container or on the host <!-- TODO(et): no Sigma rule for new cron entries in containers. Add one. -->


### 4.4 Monitoring Platform Alerts

- [ ] **Authentication failure spike**: multiple failed auth events across services in a short window
- [ ] **Unusual API access pattern**: API calls to `svc-automation` or `svc-secrets` at unusual times or frequencies

### 4.5 External / Manual Detection

- [ ] **User reports account compromise**: an authorized user reports that their account was accessed without their knowledge
- [ ] **Code repository platform security alert**: new SSH key or PAT added to the Organization's repository account
- [ ] **Third-party notification**: credential dump or access sale report involving Organization credentials

---

## 5. Response Procedures

### Phase 1: Identification and Triage (0-15 minutes)

**Objective:** Confirm unauthorized access, identify the affected accounts and systems, and determine severity.

- [ ] **Step 1.1**: Gather initial information about the alert:
 - Which detection source triggered the alert?
 - What user, IP address, or certificate is involved?
 - What system or service was accessed?
 - When did the access occur?

- [ ] **Step 1.2**: Verify the access is unauthorized (rule out legitimate activity):

 **Check gateway session list:**
 ```bash
 docker exec svc-gateway tctl sessions ls --format=json | \
  jq '.[] | {id: .id, user: .parties[0].user, login: .parties[0].login, created: .created, server_hostname: .server_hostname}'
 ```

 **Check gateway audit log for the time window:**
 ```bash
 docker exec svc-gateway tctl events get --since=1h --format=json | \
  jq '.[] | select(.event == "session.start" or .event == "user.login") | {event: .event, user: .user, time: .time, addr: .addr_remote}'
 ```

 **Check identity provider admin events:**
 ```bash
 docker exec svc-identity /opt/svc-identity/bin/kcadm.sh get events/admin \
  --server http://localhost:<identity-port> \
  --realm master \
  --user admin 2>/dev/null | head -50
 ```

 **Check direct SSH auth log on the host. On Ubuntu 24.04, prefer journalctl; `/var/log/auth.log` exists only if rsyslog is installed.**
 ```bash
 # Preferred: journald (always present)
 ssh root@10.100.1.10 'journalctl -u ssh --since "1h ago" | grep -E "Accepted|Failed|Invalid"'

 # Fallback: rsyslog file
 ssh root@10.100.1.10 "grep -E 'Accepted|Failed|Invalid' /var/log/auth.log 2>/dev/null | tail -30"
 ```

- [ ] **Step 1.3**: Cross-reference the source IP against known authorized IPs:
 ```bash
 # Check if the IP is from an expected range
 # Compare against authorized user IP list
 whois <suspicious_ip>
 ```

- [ ] **Step 1.4**: Assign severity per Section 3.

- [ ] **Step 1.5**: Open an incident ticket:
 - Incident ID: `INC-YYYY-MM-DD-NNN`
 - Detection source and timestamp
 - User/identity involved
 - Affected systems
 - Severity

### Phase 2: Immediate Containment (5-30 minutes)

**Objective:** Terminate unauthorized access and prevent further unauthorized sessions.

- [ ] **Step 2.1**: **Terminate active unauthorized sessions:**

 **In svc-gateway:**
 ```bash
 # List active sessions
 docker exec svc-gateway tctl sessions ls

 # Kill a specific session by ID
 docker exec svc-gateway tctl sessions rm <session_id>
 ```

 **On the host (if break-glass SSH):**
 ```bash
 # List who is currently logged in via SSH, then identify the unauthorized
 # sshd process. Exclude the grep itself; distinguish the attacker session
 # from your own by source IP (from `who -u`) and PID.
 ssh root@10.100.1.10 "who -u"
 ssh root@10.100.1.10 "ps aux | grep '[s]shd:'"

 # Kill the session
 ssh root@10.100.1.10 "kill <pid>"
 ```

- [ ] **Step 2.2**: **Lock the compromised user account:**

 **In svc-gateway:** use the Teleport Lock resource (the canonical Teleport 14+ mechanism). A Lock persists across cert reissuance, which `tctl users update --set-locked` does not.
 ```bash
 # Create a persistent Lock on the user (per POLICY_INCIDENT_RESPONSE.md §6)
 docker exec svc-gateway tctl lock --user=<username> --message="Incident #<ID>" --ttl=24h

 # Also force-invalidate any active user certificates immediately. Use a
 # phased rotation with a zero grace period instead of `tctl auth sign --ttl=0`
 # (which sets DEFAULT TTL, not "expired").
 docker exec svc-gateway tctl auth rotate --type=user --grace-period=0
 ```

 **In svc-identity:**
 ```bash
 # Disable the user account
 docker exec svc-identity /opt/svc-identity/bin/kcadm.sh update users/<user_id> \
  --server http://localhost:<identity-port> \
  --realm master \
  --user admin \
  -s enabled=false
 ```

- [ ] **Step 2.3**: **Block the source IP:**

 **On the host firewall:**
 ```bash
 ssh root@10.100.1.10 "iptables -I INPUT -s <attacker_ip> -j DROP"
 ```

 **On Cloudflare (if attack comes through tunnel):**
 ```
 Cloudflare dashboard > Security > WAF > Tools > IP Access Rules
 - Add rule: Block <attacker_ip>
 ```

- [ ] **Step 2.4**: **If an unauthorized user account was created, disable it immediately:**

 **In svc-gateway:**
 ```bash
 docker exec svc-gateway tctl users rm <unauthorized_username>
 ```

 **In svc-identity:**
 ```bash
 docker exec svc-identity /opt/svc-identity/bin/kcadm.sh delete users/<user_id> \
  --server http://localhost:<identity-port> \
  --realm master \
  --user admin
 ```

- [ ] **Step 2.5**: **If SSH keys are compromised, remove them.** `authorized_keys` stores the public key blob; the fingerprint is not in the file. List fingerprints with `ssh-keygen -lf`, then remove by line number or by matching the unique part of the public key blob.
 ```bash
 ssh root@10.100.1.10 << 'EOF'
 # First, list authorized keys with their fingerprints (fingerprint -> key)
 ssh-keygen -lf ~/.ssh/authorized_keys

 # Remove the specific key by line number (after identifying it)
 sed -i '<line_number>d' ~/.ssh/authorized_keys

 # Or remove by matching a unique substring of the public-key blob
 # sed -i "/<unique_pubkey_prefix>/d" ~/.ssh/authorized_keys
 EOF
 ```

- [ ] **Step 2.6**: **If the break-glass SSH path was used without authorization, add additional restrictions.** On Ubuntu 24.04, cloud-init drops overrides into `/etc/ssh/sshd_config.d/50-cloud-init.conf` which take precedence over `/etc/ssh/sshd_config`. Update both. The service unit is `ssh` on Ubuntu 24.04, not `sshd`.
 ```bash
 ssh root@10.100.1.10 << 'EOF'
 # Restrict SSH to key-only auth in the main config
 sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
 sed -i 's/^#*PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config

 # And override in any sshd_config.d snippet that may carry weaker defaults
 if [ -d /etc/ssh/sshd_config.d ]; then
   for f in /etc/ssh/sshd_config.d/*.conf; do
     [ -f "$f" ] || continue
     sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' "$f"
     sed -i 's/^#*PermitRootLogin.*/PermitRootLogin prohibit-password/' "$f"
   done
 fi
 systemctl restart ssh
 EOF
 ```

- [ ] **Step 2.7**: **If lateral movement is suspected, review all active sessions across all services.** Distroless containers (Teleport, Fluentd, Falcosidekick) ship without `ss`. Use `nsenter` from the host so the check is binary-agnostic.
 ```bash
 # Check all container network connections from the host
 ssh root@10.100.1.10 << 'EOF'
 for c in $(docker ps --format '{{.Names}}'); do
  echo "=== $c ==="
  PID=$(docker inspect -f '{{.State.Pid}}' "$c" 2>/dev/null)
  [ -n "$PID" ] && nsenter -t "$PID" -n ss -tulnp 2>/dev/null || echo "(nsenter unavailable)"
 done
 EOF
 ```

### Phase 3: Investigation (30-120 minutes)

**Objective:** Determine the full scope of the unauthorized access, what was accessed, and how the attacker gained entry.

- [ ] **Step 3.1**: **Review gateway session recordings:**

 The gateway records all SSH sessions. This is the primary forensic artifact.

 ```bash
 # List sessions for the time window of the incident
 docker exec svc-gateway tctl sessions ls --from=<incident_start_time> --to=<incident_end_time>

 # Play back a specific session recording
 docker exec svc-gateway tctl play <session_id>

 # Export session recording for evidence
 docker exec svc-gateway tctl play <session_id> > /tmp/evidence_session_<session_id>.txt
 ```

- [ ] **Step 3.2**: **Review JIT access request logs:**
 ```bash
 # Check access requests (approved and denied)
 docker exec svc-gateway tctl requests ls --format=json | \
  jq '.[] | {id: .id, user: .user, roles: .roles, state: .state, created: .created}'
 ```

- [ ] **Step 3.3**: **Review identity provider admin audit events:** <!-- TODO(et): verify Keycloak v26 still supports `kcadm.sh get events/admin` as written; Keycloak 22+ moved some admin event APIs. -->

 ```bash
 # Check for account creation, role changes, password resets
 docker exec svc-identity /opt/svc-identity/bin/kcadm.sh get events/admin \
  --server http://localhost:<identity-port> \
  --realm master \
  --user admin \
  --format json 2>/dev/null | \
  jq '.[] | select(.time >= "<incident_start_epoch>") | {operationType, resourceType, representation}'
 ```

- [ ] **Step 3.4**: **Review Falco alerts for the incident window:**
 ```bash
 docker logs --since "<incident_start_time>" svc-detection 2>&1 | \
  grep -i "ssh\|login\|exec\|shell\|privilege\|escalation"

 docker logs --since "<incident_start_time>" svc-detection-router 2>&1 | \
  grep -i "critical\|high"
 ```

- [ ] **Step 3.5**: **Check host authentication logs:**
 ```bash
 ssh root@10.100.1.10 << 'EOF'
 # SSH authentication events
 grep -E "sshd.*(Accepted|Failed|Invalid)" /var/log/auth.log | \
  awk -v start="<incident_start_time>" '$0 >= start' | tail -50

 # Sudo usage
 grep "sudo" /var/log/auth.log | tail -20

 # User account modifications
 grep -E "useradd|usermod|userdel|passwd|groupadd" /var/log/auth.log | tail -20
 EOF
 ```

- [ ] **Step 3.6**: **Check what the attacker accessed or modified:**
 ```bash
 # Check recently modified files on the host
 ssh root@10.100.1.10 "find / -mmin -120 -type f -not -path '/proc/*' -not -path '/sys/*' -not -path '/var/lib/docker/*' 2>/dev/null | head -50"

 # Check for new cron jobs
 ssh root@10.100.1.10 "crontab -l 2>/dev/null; ls -la /etc/cron.d/ /etc/cron.daily/"

 # Check for new authorized SSH keys
 ssh root@10.100.1.10 "cat ~/.ssh/authorized_keys"

 # Check for new users
 ssh root@10.100.1.10 "awk -F: '\$3 >= 1000 {print \$1, \$3, \$7}' /etc/passwd"
 ```

- [ ] **Step 3.7**: **Check for data exfiltration indicators.** `pg_stat_statements` is not enabled by default in the pgvector/Postgres 16 image; if `shared_preload_libraries` does not include it, the query returns an error. Verify before relying on this in a live runbook.
 ```bash
 # Check outbound network connections during incident window
 ssh root@10.100.1.10 "ss -tulnp"

 # Check Docker container network activity
 docker logs --since "<incident_start_time>" svc-event-shipper 2>&1 | tail -50

 # Confirm pg_stat_statements is loaded before querying it
 docker exec svc-db psql -U "$CD_DB_USER" -tAc \
  "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname='pg_stat_statements');"
 # If true, then:
 docker exec svc-db psql -U "$CD_DB_USER" -c \
  "SELECT query, calls, mean_exec_time FROM pg_stat_statements ORDER BY calls DESC LIMIT 20;"
 # Otherwise fall back to the database log review.
 ```

- [ ] **Step 3.8**: **Determine the initial access vector:**
 - Was a credential compromised? (check Playbook IR-PLAY-002)
 - Was a vulnerability exploited? (check container image CVEs)
 - Was social engineering used?
 - Was a valid session hijacked?
 - Was break-glass SSH used with a stolen key?

- [ ] **Step 3.9**: **Check code repository platform for unauthorized changes.** Use the `gh` CLI when authenticated for repeatable evidence capture.
 ```bash
 # Deploy keys and user-level keys
 gh api /repos/<owner>/<repo>/keys
 gh api /user/keys

 # Recent webhook deliveries
 gh api /repos/<owner>/<repo>/hooks
 ```

### Phase 4: Eradication (30-90 minutes)

**Objective:** Remove all unauthorized access, accounts, keys, and backdoors.

- [ ] **Step 4.1**: **Remove all unauthorized user accounts:**

 **From svc-gateway:**
 ```bash
 # List all users
 docker exec svc-gateway tctl users ls

 # Remove unauthorized users
 docker exec svc-gateway tctl users rm <unauthorized_user>
 ```

 **From svc-identity:**
 ```bash
 # List all users
 docker exec svc-identity /opt/svc-identity/bin/kcadm.sh get users \
  --server http://localhost:<identity-port> \
  --realm master \
  --user admin

 # Delete unauthorized users
 docker exec svc-identity /opt/svc-identity/bin/kcadm.sh delete users/<user_id> \
  --server http://localhost:<identity-port> \
  --realm master \
  --user admin
 ```

- [ ] **Step 4.2**: **Remove unauthorized SSH keys from all locations:**
 ```bash
 ssh root@10.100.1.10 << 'EOF'
 # Review and clean authorized_keys
 cat ~/.ssh/authorized_keys
 # Remove any unrecognized keys
 # Keep only keys with known fingerprints

 # Check other user accounts
 for user_home in /home/*/; do
  echo "=== $user_home ==="
  cat "${user_home}.ssh/authorized_keys" 2>/dev/null || echo "(none)"
 done
 EOF
 ```

- [ ] **Step 4.3**: **Remove unauthorized cron jobs, systemd services, or backdoors.** `debsums` is not installed by default on Ubuntu 24.04 cloud images; install on demand or skip if unavailable.
 ```bash
 ssh root@10.100.1.10 << 'EOF'
 # Check for rogue cron jobs
 crontab -l
 ls -la /etc/cron.d/ /etc/cron.daily/ /etc/cron.hourly/

 # Check for rogue systemd services
 systemctl list-units --type=service --state=running | grep -v -E "(docker|ssh|systemd|cron|cloud)"

 # Check for unusual listening ports
 ss -tulnp | grep -v -E "(docker-proxy|sshd|systemd)"

 # Check for modified system binaries (install debsums if absent and policy allows)
 if command -v debsums >/dev/null 2>&1; then
   debsums -c 2>/dev/null | head -20
 else
   echo "(debsums not installed; install with apt-get install debsums if policy permits)"
 fi
 EOF
 ```

- [ ] **Step 4.4**: **Rotate SSH host keys if the host was compromised.** The Ubuntu 24.04 service unit is `ssh`, not `sshd`.
 ```bash
 ssh root@10.100.1.10 << 'EOF'
 rm /etc/ssh/ssh_host_*
 ssh-keygen -A
 systemctl restart ssh
 EOF

 # Update known_hosts on the management workstation
 ssh-keygen -R 10.100.1.10
 ssh-keyscan 10.100.1.10 >> ~/.ssh/known_hosts
 ```

- [ ] **Step 4.5**: **Rotate gateway CA certificates if the gateway was compromised.** `tctl auth rotate` initiates a multi-phase rotation: init, update_clients, update_servers, standby. New certs issue during the grace period; old certs are revoked at grace expiry.
 ```bash
 docker exec svc-gateway tctl auth rotate --type=host --grace-period=24h
 docker exec svc-gateway tctl auth rotate --type=user --grace-period=24h
 ```

 > **WARNING:** CA rotation invalidates all existing certificates. Set an appropriate grace period and re-issue certificates to all authorized users.

- [ ] **Step 4.6**: **Rotate all credentials that the attacker could have accessed:**
 - Database passwords (if attacker had access to `svc-db` or `.env`)
 - API keys stored in environment variables
 - Bot tokens
 - Any secret the attacker could have read from the compromised session

 Reference Playbook IR-PLAY-002 for credential rotation procedures.

- [ ] **Step 4.7**: **If a container was used as an entry point, rebuild it:**
 ```bash
 docker compose pull <service_name>
 docker compose up -d --force-recreate <service_name>
 ```

### Phase 5: Recovery and Verification (30-60 minutes)

**Objective:** Restore normal access controls and verify the integrity of all access paths.

- [ ] **Step 5.1**: **Verify only authorized users exist in svc-gateway:**
 ```bash
 docker exec svc-gateway tctl users ls
 # Cross-reference against the approved user roster
 ```

- [ ] **Step 5.2**: **Verify only authorized users exist in svc-identity:**
 ```bash
 docker exec svc-identity /opt/svc-identity/bin/kcadm.sh get users \
  --server http://localhost:<identity-port> \
  --realm master \
  --user admin \
  --format json | jq '.[].username'
 ```

- [ ] **Step 5.3**: **Verify role assignments are correct:**
 ```bash
 # Gateway roles
 docker exec svc-gateway tctl get roles --format=json | \
  jq '.[] | {name: .metadata.name, allow_logins: .spec.allow.logins}'

 # Verify JIT roles are properly configured
 docker exec svc-gateway tctl get roles --format=json | \
  jq '.[] | select(.spec.allow.request) | {name: .metadata.name, requestable: .spec.allow.request.roles}'
 ```

- [ ] **Step 5.4**: **Verify SSH configuration is hardened:**
 ```bash
 ssh root@10.100.1.10 << 'EOF'
 sshd -T | grep -E "passwordauthentication|permitrootlogin|pubkeyauthentication|maxauthtries"
 # Expected:
 # passwordauthentication no
 # permitrootlogin prohibit-password
 # pubkeyauthentication yes
 # maxauthtries 3
 EOF
 ```

- [ ] **Step 5.5**: **Verify authorized_keys contains only known keys:**
 ```bash
 ssh root@10.100.1.10 "ssh-keygen -l -f ~/.ssh/authorized_keys"
 # Cross-reference fingerprints against the approved key list
 ```

- [ ] **Step 5.6**: **Verify svc-detection is monitoring all access paths:**
 ```bash
 docker logs --tail 20 svc-detection 2>&1 | grep -i "ssh\|exec\|shell"
 docker logs --tail 20 svc-detection-router 2>&1
 ```

- [ ] **Step 5.7**: **Verify Datadog is receiving auth events:**
 Check the Datadog dashboard for:
 - SSH authentication events flowing
 - Gateway session events flowing
 - Identity provider audit events flowing

- [ ] **Step 5.8**: **Test that authorized access still works correctly.** Never disable host key checking in a security runbook; `accept-new` is the safer Ubuntu 22.04+ default.
 ```bash
 # Test gateway SSH access
 ssh -o StrictHostKeyChecking=accept-new <authorized_user>@ssh.example-ops.com

 # Test automation platform access
 curl -sf -o /dev/null -w "%{http_code}" https://n8n.example-ops.com/healthz

 # Test JIT access request flow (if applicable). <!-- TODO(et): confirm the
 # exact request subcommand for the deployed Teleport version (v18+ may
 # require `tsh request create` from a client rather than `tctl request create`). -->
 docker exec svc-gateway tctl request create --roles=admin --reason="Post-incident access test"
 ```

- [ ] **Step 5.9**: **Re-enable any services or accounts that were disabled during containment** (only after eradication is confirmed complete).

### Phase 6: Post-Incident (Within 72 hours)

**Objective:** Document the incident, identify root cause, and strengthen access controls.

- [ ] **Step 6.1**: Complete the incident timeline:
 - When did unauthorized access first occur?
 - When was it detected?
 - Detection-to-containment time (target: <15 minutes)
 - What systems were accessed during the unauthorized session?
 - What data was potentially viewed, copied, or modified?

- [ ] **Step 6.2**: Identify the initial access vector:
 - Compromised credential (how was it obtained?)
 - Stolen SSH key (from where?)
 - Exploited vulnerability (which CVE?)
 - Social engineering (what technique?)
 - Insider threat (which user?)
 - Misconfigured access control (what was misconfigured?)

- [ ] **Step 6.3**: Write a post-incident report containing:
 - Executive summary
 - Timeline of events with exact timestamps
 - Access vector and attack chain
 - Systems and data affected
 - Session recording summary (what commands were executed)
 - Impact assessment
 - Remediation actions taken
 - Lessons learned
 - Action items with owners and due dates

- [ ] **Step 6.4**: Update access controls and detection:
 - [ ] Review and tighten gateway role definitions
 - [ ] Review JIT access policies: are time windows appropriate?
 - [ ] Add detection rules for the specific attack pattern
 - [ ] Update svc-detection rules if the activity was not caught
 - [ ] Review SSH hardening (disable password auth, restrict key algorithms)
 - [ ] Implement or review IP allowlisting for admin access
 - [ ] Review certificate TTLs: are they too long?

- [ ] **Step 6.5**: Conduct an access review:
 - [ ] Audit all users in svc-gateway
 - [ ] Audit all users in svc-identity
 - [ ] Audit all SSH keys on all hosts
 - [ ] Audit all API tokens and their scopes
 - [ ] Remove any stale or unnecessary accounts/keys
 - [ ] Document the current access roster with justification for each entry

- [ ] **Step 6.6**: Review and update the break-glass procedure: <!-- TODO(et): confirm BREAK_GLASS.md (or equivalent) exists in docs/grc/ or runbooks; if not, this step is aspirational and should be backfilled. -->
 - Is break-glass SSH access properly documented?
 - Is there an alert when break-glass access is used?
 - Is the break-glass key stored securely?

- [ ] **Step 6.7**: Schedule the next periodic access review (recommend quarterly).

- [ ] **Step 6.8**: Update this playbook with any lessons learned.

---

## 6. Communication Requirements

| Audience | When | Method | Content |
|----------|------|--------|---------|
| Incident Commander | Immediately on detection | Direct message / phone | Alert details, suspected unauthorized user |
| System Owner | Within 10 minutes | Direct message / phone | Scope of access, containment status |
| Affected account owner | Within 30 minutes (if legitimate user compromised) | Direct message / phone | Account locked, credential rotation required |
| Cloud provider | If provider access was involved | Support ticket | Request audit logs, report unauthorized access |
| Code repository platform | If repo access was compromised | Support ticket / dashboard | Revoke tokens, request audit trail |
| Legal / compliance | If data breach confirmed (SEV-1) | Email to `admin@example-ops.com` | Incident summary, data affected, breach notification requirements |

---

## 7. Evidence Preservation Checklist

| Artifact | Location | Collected? |
|----------|----------|------------|
| Gateway session recording | `tctl play <session_id>` | [ ] |
| Gateway audit events | `tctl events get` | [ ] |
| Gateway user list (at time of incident) | `tctl users ls` | [ ] |
| Gateway access request logs | `tctl requests ls` | [ ] |
| Identity provider admin audit events | Keycloak admin events API | [ ] |
| Host auth log | `/var/log/auth.log` | [ ] |
| Host authorized_keys (at time of incident) | `~/.ssh/authorized_keys` | [ ] |
| svc-detection alerts | `docker logs svc-detection` | [ ] |
| svc-detection-router events | `docker logs svc-detection-router` | [ ] |
| svc-event-shipper logs | `docker logs svc-event-shipper` | [ ] |
| Datadog auth dashboards | Screenshots from monitoring UI | [ ] |
| Network connections during incident | `ss -tulnp` output | [ ] |
| Recently modified files on host | `find` output | [ ] |
| New cron jobs or systemd services | `crontab -l`, `systemctl list-units` | [ ] |
| WHOIS data for attacker IP | `whois <ip>` output | [ ] |
| Code repository platform security log | Platform settings export | [ ] |
| SHA-256 hash manifest of all evidence | `/tmp/evidence_manifest_sha256.txt` | [ ] |

---

## 8. NIST 800-53 Control Mapping

| Control | Description | Playbook Phase |
|---------|-------------|----------------|
| IR-4 | Incident Handling | All phases |
| IR-5 | Incident Monitoring | Phase 1 (detection triggers) |
| IR-6 | Incident Reporting | Phase 6 (post-incident report) |
| AC-2 | Account Management | Phase 4 (remove unauthorized accounts), Phase 5 (access review) |
| AC-2(4) | Automated Audit Actions | Phase 1 (identity provider audit events) |
| AC-3 | Access Enforcement | Phase 2 (terminate sessions, lock accounts) |
| AC-6 | Least Privilege | Phase 6 (role review, JIT policy review) |
| AC-6(1) | Authorize Access to Security Functions | Phase 4 (admin role audit) |
| AC-7 | Unsuccessful Logon Attempts | Phase 1 (brute force detection) |
| AC-12 | Session Termination | Phase 2 (kill unauthorized sessions) |
| AU-2 | Audit Events | Phase 3 (session recording, audit logs) |
| AU-6 | Audit Review, Analysis, and Reporting | Phase 3 (log investigation) |
| AU-9 | Protection of Audit Information | Phase 3 (evidence preservation) |
| AU-12 | Audit Generation | Phase 1 (gateway session recording) |
| IA-2 | Identification and Authentication | Phase 4 (certificate/key rotation) |
| IA-4 | Identifier Management | Phase 4 (user account cleanup) |
| IA-5 | Authenticator Management | Phase 4 (SSH key rotation, CA rotation) |
| SC-7 | Boundary Protection | Phase 2 (IP blocking, tunnel restriction) |

---

## 9. Access Path Diagram

```
EXTERNAL
  |
  v
[Edge Security Provider]: L3/L4/L7 protection, WAF
  |
  v
[svc-tunnel]: Zero-trust tunnel, only public ingress
  |
  +--> [n8n.example-ops.com] --> [svc-automation]
  +--> [ssh.example-ops.com] --> [svc-gateway]
  +--> [squire.example-ops.com] --> [svc-squire /alert]
  +--> [langfuse.example-ops.com] --> [svc-langfuse-web]
                    |
                    v
                 [Session Recording]
                    |
                    v
                [alpha-node services]
                (svc-db, svc-secrets, etc.)

BREAK-GLASS PATH (emergency only):
  Direct SSH to root@10.100.1.10 (bypasses tunnel and gateway)
  MUST generate alert when used
```

---

## 10. Quick Reference Card

**For use during an active incident, tear-off summary:**

```
1. CONFIRM: Check gateway sessions: tctl sessions ls
        Check host auth log: journalctl -u ssh | grep -E "Accepted|Failed|Invalid"
        Check identity provider admin events

2. KILL:    Terminate session: tctl sessions rm <session_id>
        Kill host SSH: kill <pid>

3. LOCK:    Persistent Lock: tctl lock --user=<user> --message="Incident #<ID>"
        Disable user in identity provider
        Block IP: iptables -I INPUT -s <ip> -j DROP

4. REVIEW:  Play back session recording: tctl play <session_id>
        Check for new accounts, SSH keys, cron jobs, backdoors

5. REMOVE:  Delete unauthorized accounts, SSH keys, cron jobs
        Rotate compromised credentials (see IR-PLAY-002)

6. ROTATE:  SSH host keys (rm then ssh-keygen -A, systemctl restart ssh)
        Gateway CA (set grace period before running)
        All credentials the attacker could have seen

7. VERIFY:  Only authorized users remain
        Only authorized SSH keys remain
        Roles and permissions are correct
        Detection and monitoring are active

8. REPORT:  Post-incident report within 72 hours
        Schedule access review
```

---

## Cross-References

| Document | Relationship |
|----------|-------------|
| [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) | System Security Plan with NIST 800-53 control mapping |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | Tracks findings and remediation milestones |
| [README.md](README.md) | GRC library index and reading guide |
