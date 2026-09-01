# Incident Response Playbook: Leaked Credential

**Document ID:** IR-PLAY-002
**Version:** 1.0
**Last Updated:** 2026-03-11
**Owner:** Incident Commander
**Classification:** Internal Use Only
**NIST 800-53 Controls:** IR-4 (Incident Handling), IR-5 (Incident Monitoring), IR-6 (Incident Reporting), IA-5 (Authenticator Management), SC-28 (Protection of Information at Rest)

> **Status note (2026-09-01):** this document describes the DigitalOcean-era baseline as assessed. That environment was retired 2026-08. The platform now runs on an Oracle Cloud (OCI) ARM instance with a partial stack (3 containers live); the remaining services are pending ARM rebuild. A re-baseline of this document is queued and tracked in the POA&M.

---

### Credential Rotation Decision Tree

```
┌─────────────────────────────────────┐
│         LEAK DETECTED               │
│  (Gitleaks, manual report, alert)   │
└──────────────────┬──────────────────┘
                   │
                   v
┌─────────────────────────────────────┐
│    IDENTIFY CREDENTIAL TYPE         │
│  API key? DB cred? SSH key? Token?  │
└──────────────────┬──────────────────┘
                   │
        ┌──────────┼──────────────┬────────────────────┐
        │          │              │                     │
        v          v              v                     v
┌─────────────┐┌──────────────┐┌──────────────┐┌──────────────────┐
│  API KEY    ││  DB CRED     ││  SSH KEY     ││  TUNNEL TOKEN    │
└──────┬──────┘└──────┬───────┘└──────┬───────┘└────────┬─────────┘
       │              │               │                  │
       v              v               v                  v
┌─────────────┐┌──────────────┐┌──────────────┐┌──────────────────┐
│ Revoke in   ││ Reset pass-  ││ Revoke key   ││ Rotate in        │
│ provider    ││ word in DB   ││ (remove from ││ provider         │
│ dashboard   ││              ││ authorized_  ││ dashboard        │
│ or CLI      ││              ││ keys)        ││                  │
└──────┬──────┘└──────┬───────┘└──────┬───────┘└────────┬─────────┘
       │              │               │                  │
       v              v               v                  v
┌─────────────┐┌──────────────┐┌──────────────┐┌──────────────────┐
│ Generate    ││ Update all   ││ Generate new ││ Update container │
│ new key     ││ connection   ││ ed25519      ││ env with new     │
│             ││ strings      ││ keypair      ││ token value      │
└──────┬──────┘└──────┬───────┘└──────┬───────┘└────────┬─────────┘
       │              │               │                  │
       v              v               v                  v
┌─────────────┐┌──────────────┐┌──────────────┐┌──────────────────┐
│ Update      ││ Restart      ││ Deploy pub   ││ Restart tunnel   │
│ secrets     ││ services +   ││ key to all   ││ container        │
│ manager     ││ test DB      ││ authorized_  ││                  │
│             ││ connectivity ││ keys hosts   ││                  │
└──────┬──────┘└──────┬───────┘└──────┬───────┘└────────┬─────────┘
       │              │               │                  │
       v              v               v                  v
┌─────────────┐┌──────────────┐┌──────────────┐┌──────────────────┐
│ Verify API  ││ Verify app   ││ Verify SSH   ││ Verify tunnel    │
│ calls work  ││ queries work ││ login works  ││ routes are live  │
└──────┬──────┘└──────┬───────┘└──────┬───────┘└────────┬─────────┘
       │              │               │                  │
       └──────────────┴───────┬───────┴──────────────────┘
                              │
                              v
               ┌──────────────────────────────┐
               │  WAS CREDENTIAL USED         │
               │  MALICIOUSLY?                │
               └──────────────┬───────────────┘
                     ┌────────┴────────┐
                     │                 │
                     v                 v
              ┌────────────┐   ┌─────────────┐
              │  YES       │   │  NO          │
              └─────┬──────┘   └──────┬──────┘
                    │                 │
                    v                 v
              ┌────────────┐   ┌─────────────┐
              │ Escalate   │   │ Rotation    │
              │ to FULL IR │   │ complete.   │
              │ (Phase 3+) │   │ Log and     │
              │            │   │ close.      │
              └─────┬──────┘   └─────────────┘
                    │
                    v
               ┌──────────────────────────────┐
               │  IS CREDENTIAL IN            │
               │  GIT HISTORY?                │
               └──────────────┬───────────────┘
                     ┌────────┴────────┐
                     │                 │
                     v                 v
              ┌────────────┐   ┌─────────────┐
              │  YES       │   │  NO          │
              └─────┬──────┘   └──────┬──────┘
                    │                 │
                    v                 v
              ┌────────────┐   ┌─────────────┐
              │ Rotate +   │   │ Rotation    │
              │ scrub git  │   │ is          │
              │ history    │   │ sufficient. │
              │ (BFG +     │   │             │
              │ force push)│   │             │
              └────────────┘   └─────────────┘
```

---

## 1. Purpose

This playbook provides step-by-step procedures for responding to a leaked credential. A leaked credential is any API key, database password, SSH key, token, or other secret that has been exposed through code commits, log files, error messages, screenshots, or any other unauthorized disclosure channel.

---

## 2. Scope

Applies to all secrets managed by the Organization, including but not limited to:
- Database credentials (`svc-db`)
- API keys (DigitalOcean, Cloudflare, Datadog, code repository platform)
- SSH keys and certificates
- Automation workflow encryption keys and JWT secrets
- Bot tokens (messaging platform integrations)
- Gateway and identity provider credentials
- Infrastructure-as-code platform tokens
- Any secret stored in the secrets manager or credential vault

---

## 3. Severity Classification

| Severity | Criteria |
|----------|----------|
| **SEV-1 (Critical)** | Database credentials, SSH private keys, secrets manager master token, gateway CA private key, or DigitalOcean API token exposed publicly |
| **SEV-2 (High)** | API keys with write access (code repository, edge security, monitoring) exposed publicly or to unauthorized party |
| **SEV-3 (Medium)** | API keys with read-only access, bot tokens, or secrets exposed in internal logs or private channels |
| **SEV-4 (Low)** | Expired or already-rotated credential found in old commits or logs; no active risk |

---

## 4. Detection Triggers

### 4.1 Automated Detection

- [ ] **Gitleaks CI scan failure**: secret pattern detected in a commit during CI/CD pipeline
- [ ] **Code repository platform secret scanning alert**: platform-native secret detection on push
- [ ] **Datadog alert**: secret pattern detected in log output (regex-based alert rule) <!-- TODO(et): verify the Datadog log monitor for secret patterns actually exists. If not, this trigger is aspirational. -->
- [ ] **Pre-commit hook failure**: Gitleaks pre-commit hook blocked a commit containing a secret
- [ ] **Secrets manager audit log**: unusual access pattern (unexpected IP, time, or frequency) <!-- TODO(et): confirm Doppler audit log is shipped to Datadog so this trigger fires. -->


### 4.2 Manual / External Detection

- [ ] **Developer self-report**: engineer realizes they committed or logged a secret
- [ ] **Peer code review**: secret spotted during pull request review
- [ ] **Third-party notification**: vendor reports that a credential associated with the Organization was found on a public paste site, repository, or dark web
- [ ] **Unauthorized usage alert**: unexpected API calls or logins using a credential that suggest it was obtained by an unauthorized party <!-- TODO(et): specify the alert source (Datadog on auth logs, Vault audit, cloud provider audit trail) so this row is actionable. -->


---

## 5. Response Procedures

### Phase 1: Identification and Triage (0-5 minutes)

**CRITICAL: Time is the primary factor. Every minute a credential remains active after exposure increases risk. Revoke first, investigate second.**

- [ ] **Step 1.1**: Identify the exposed credential:
 - What type of credential is it? (API key, password, SSH key, token, certificate)
 - Which service or system does it authenticate to?
 - What level of access does it grant? (read, write, admin)

- [ ] **Step 1.2**: Determine the exposure vector:
 - Committed to a public or private repository?
 - Logged to application logs, Datadog, or CI output?
 - Shared in a message, email, or document?
 - Found on an external site or paste?

- [ ] **Step 1.3**: Determine the exposure window:
 - When was the credential first exposed?
 - When was the exposure detected?
 - Is the exposure ongoing (e.g., still in a public repo)?

- [ ] **Step 1.4**: Assign severity per Section 3.

- [ ] **Step 1.5**: Open an incident ticket:
 - Incident ID: `INC-YYYY-MM-DD-NNN`
 - Credential type and associated service
 - Exposure vector and window
 - Severity

### Phase 2: Immediate Containment (5-15 minutes)

**Objective:** Revoke the exposed credential immediately. Do not wait for investigation to complete.

- [ ] **Step 2.1**: **Revoke / disable the credential at its source:**

 **Database credentials (`svc-db`):**
 ```bash
 # Connect to the database and change the password immediately
 docker exec svc-db psql -U "$CD_DB_USER" -c \
   "ALTER USER <compromised_user> WITH PASSWORD '<new_password>';"

 # ALTER USER does NOT terminate existing sessions. Force them closed:
 docker exec svc-db psql -U "$CD_DB_USER" -c \
   "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE usename = '<compromised_user>';"

 # Restart EVERY service that consumes this credential. The svc-db instance
 # hosts both the n8n database and the Langfuse database (see compose
 # DATABASE_URL for svc-langfuse-worker / svc-langfuse-web), so all of the
 # following must restart after rotation:
 docker compose restart svc-automation svc-identity svc-langfuse-worker svc-langfuse-web svc-squire
 ```

 **Cloud provider API token:**
 ```bash
 # Revoke via DigitalOcean dashboard or CLI
 # Generate a new token immediately
 # Update in secrets manager (Doppler is the source of truth)
 ```

 **Cloudflare API key:**
 ```bash
 # Regenerate the API key in the Cloudflare dashboard
 # Update in Doppler
 ```

 **Code repository platform token:**
 ```bash
 # Before revoking the old token, capture its scope set so the replacement
 # can be issued with identical scopes (screenshot the scopes screen).
 # Revoke the token in code repository platform settings > Developer settings > Tokens
 # Generate a new token with the same scopes
 # Update in Doppler
 ```

 **SSH private key:**
 ```bash
 # Standard rotation order: generate the NEW key, deploy it, verify the new
 # key works, then remove the OLD key. Reversing the order risks lockout.
 #
 # 1. Generate the new keypair (omit -N for prompt, or use -N '' for unattended)
 ssh-keygen -t ed25519 -f ~/.ssh/<new_key_name> -C "admin@example-ops.com"

 # 2. Deploy the new public key
 ssh-copy-id -i ~/.ssh/<new_key_name>.pub root@10.100.1.10

 # 3. Verify the new key authenticates BEFORE removing the old one
 ssh -i ~/.ssh/<new_key_name> root@10.100.1.10 'echo "new key works"'

 # 4. Identify the compromised key on the host. authorized_keys stores the
 #    PUBLIC KEY, not the fingerprint, so `sed -i '/<fingerprint>/d'` will
 #    not match. List fingerprints, then remove by matching the public-key
 #    blob prefix (unique portion of the ssh-ed25519 or ssh-rsa string).
 ssh root@10.100.1.10 'ssh-keygen -lf ~/.ssh/authorized_keys'
 ssh root@10.100.1.10 'sed -i "/<unique_pubkey_prefix>/d" ~/.ssh/authorized_keys'

 # 5. Reconfirm the new key still works after the old key is removed
 ssh -i ~/.ssh/<new_key_name> root@10.100.1.10 'echo "still working"'
 ```

 **Bot token (messaging platform):**
 ```bash
 # Revoke the token via the bot platform's BotFather or admin panel
 # Generate a new token
 # Update in Doppler and restart the consuming service
 docker compose restart svc-automation
 ```

 **Gateway or identity provider credentials:**
 ```bash
 # Rotate via the respective admin interfaces. Teleport `tctl auth rotate`
 # initiates a multi-phase rotation: init, update_clients, update_servers,
 # standby. New certs are issued during the grace period; old certs are
 # revoked at grace expiry.
 docker exec svc-gateway tctl auth rotate --type=host --grace-period=12h
 ```

- [ ] **Step 2.2**: Update the new credential in the secrets manager. Doppler is the source of truth (44 secrets in `<SECRETS_PROJECT>/<CONFIG>`).
 ```bash
 # Update the secret in Doppler. Verify without echoing the value.
 doppler secrets set <KEY> "<new value>" --project <SECRETS_PROJECT> --config prd
 doppler secrets get <KEY> --plain | wc -c   # length sanity check only; never print value
 ```

- [ ] **Step 2.3**: Update the credential on `alpha-node`:
 ```bash
 # Update the .env file on the node
 ssh root@10.100.1.10 "vim /opt/platform/.env"
 # OR run with Doppler injection so the value never lands on disk:
 # doppler run --project <SECRETS_PROJECT> --config prd, docker compose up -d
 ```

- [ ] **Step 2.4**: Restart all services that consume the rotated credential:
 ```bash
 docker compose restart <service1> <service2> <service3>
 ```

- [ ] **Step 2.5**: Verify services are operational with the new credential:
 ```bash
 docker compose ps
 # Check healthchecks
 docker inspect --format='{{.State.Health.Status}}' <container_name>
 ```

### Phase 3: Investigation (15-60 minutes)

**Objective:** Determine the full scope of exposure and whether the credential was used by an unauthorized party.

- [ ] **Step 3.1**: Determine all systems and services that used the compromised credential:
 ```bash
 # Search compose files for the credential's environment variable name
 grep -r "<SECRET_VAR_NAME>" /opt/platform/
 ```

- [ ] **Step 3.2**: Review audit logs for unauthorized use during the exposure window:

 **Database access logs:**
 ```bash
 docker logs --since "<exposure_start_time>" svc-db 2>&1 | grep -i "auth\|login\|connection"
 ```

 **Cloud provider audit trail:**
 ```bash
 # Check DigitalOcean dashboard > Audit Log for the exposure window
 ```

 **Code repository platform audit log:**
 ```bash
 # Check code repository platform Settings > Security log
 # Filter by the exposure window
 ```

 **Gateway session audit:**
 ```bash
 docker exec svc-gateway tctl sessions ls --from=<exposure_start_time>
 ```

- [ ] **Step 3.3**: Check if the credential was used from any unauthorized IP addresses or at unusual times.

- [ ] **Step 3.4**: Determine if the credential exposure led to secondary compromise:
 - Were other secrets accessible through the compromised credential?
 - Was any data read, modified, or exfiltrated?
 - Were any new accounts or access keys created?

- [ ] **Step 3.5**: If the credential was committed to a repository, determine the commit and exposure scope:
 ```bash
 # Find the commit(s) containing the secret
 git log --all --oneline -- <file_with_secret>

 # Check if the commit was pushed to a public remote
 git branch -r --contains <commit_hash>
 ```

### Phase 4: Repository Cleanup (If credential was committed to git)

**Objective:** Remove the credential from all git history.

> **WARNING:** This phase involves rewriting git history. Coordinate with all contributors. Anyone with a local clone will need to re-clone or rebase.

- [ ] **Step 4.1**: Remove the secret from the current codebase first:
 ```bash
 # Edit the file to remove the hardcoded secret
 # Replace with environment variable reference or secrets manager lookup
 git add <file>
 git commit -m "fix: remove hardcoded credential from <file>"
 ```

- [ ] **Step 4.2**: Use BFG Repo Cleaner to remove the secret from all history. The canonical BFG flow uses a **bare mirror clone**, not the working tree. Even after BFG plus force push, assume the secret was harvested during the exposure window: the rotation in Phase 2 is the actual defense, not history scrubbing.
 ```bash
 # 1. Mirror clone (bare repo for BFG)
 git clone --mirror git@github.com:<org>/<repo>.git /tmp/<repo>.git

 # 2. Write the secret value to a scrub list
 echo "<secret_value>" > /tmp/secrets_to_remove.txt

 # 3. Run BFG against the bare clone
 bfg --replace-text /tmp/secrets_to_remove.txt /tmp/<repo>.git

 # 4. Aggressively GC the bare repo
 cd /tmp/<repo>.git
 git reflog expire --expire=now --all
 git gc --prune=now --aggressive

 # 5. Force push the rewritten history
 git push

 # 6. Securely delete the scrub list
 shred -u /tmp/secrets_to_remove.txt || rm -P /tmp/secrets_to_remove.txt
 ```

- [ ] **Step 4.3**: Force push from the bare mirror (already done in Step 4.2 if the mirror flow was followed). For normal working copies the equivalent is:
 ```bash
 git push --force --all
 git push --force --tags
 ```

- [ ] **Step 4.4**: Verify the secret is no longer in any branch or tag:
 ```bash
 git log --all -p | grep -c "<partial_secret_pattern>"
 # Should return 0
 ```

- [ ] **Step 4.5**: Invalidate code repository platform caches:
 - Contact code repository platform support if the repo is public and the secret may be cached
 - Note: Even after force push, the commit may be accessible via its SHA for up to 90 days on some platforms
 - Treat the secret as compromised regardless of cleanup success; Phase 2 rotation is the real control

- [ ] **Step 4.6**: Notify all contributors to re-clone:
 ```
 The repository history has been rewritten to remove a leaked credential.
 Please delete your local clone and re-clone from the remote.
 Do NOT push any local branches that were created before this cleanup.
 ```

### Phase 5: Recovery and Verification (30-60 minutes)

**Objective:** Confirm all systems work with new credentials and no unauthorized access occurred.

- [ ] **Step 5.1**: Verify all services are healthy with the new credential:
 ```bash
 docker compose ps
 # All services should show "Up" and "healthy"
 ```

- [ ] **Step 5.2**: Test critical integrations end-to-end:
 - Database connectivity from automation workflows
 - Edge security tunnel connectivity
 - Code repository platform API access
 - Datadog agent reporting
 - Bot responsiveness

- [ ] **Step 5.3**: Verify CI/CD pipeline passes with updated credentials.

- [ ] **Step 5.4**: Confirm Gitleaks rules would catch this pattern:
 ```bash
 # Run secrets scanner on the repository
 gitleaks detect --source <repo_path> -v
 ```

- [ ] **Step 5.5**: Verify the old credential no longer works (it should be revoked):
 ```bash
 # Attempt to authenticate with the old credential (in a safe, logged manner)
 # Should return authentication failure
 ```

### Phase 6: Post-Incident (Within 72 hours)

**Objective:** Document, learn, and prevent recurrence.

- [ ] **Step 6.1**: Complete the incident timeline:
 - When was the credential first exposed?
 - When was the exposure detected?
 - Time from exposure to revocation (target: <5 minutes after detection)
 - Was the credential used by an unauthorized party? If so, what was accessed?

- [ ] **Step 6.2**: Identify root cause:
 - Developer committed a secret directly?
 - Secret was logged by an application?
 - Secret was included in an error message or stack trace?
 - Secret was shared via an insecure channel?
 - Pre-commit hooks not installed or bypassed?

- [ ] **Step 6.3**: Write a post-incident report containing:
 - Executive summary
 - Timeline of events
 - Credential type and scope of access
 - Exposure window and vector
 - Whether unauthorized use was confirmed
 - Remediation actions taken
 - Lessons learned
 - Action items with owners and due dates

- [ ] **Step 6.4**: Implement preventive measures:
 - [ ] Verify Gitleaks pre-commit hook is installed on all developer machines
 - [ ] Update Gitleaks config (.gitleaks.toml) if the pattern was not caught
 - [ ] Update CI/CD Gitleaks rules
 - [ ] Add Datadog alert for the credential pattern in logs
 - [ ] Review and enforce the "never hardcode secrets" policy
 - [ ] Verify secrets manager is the sole source of truth for all credentials

- [ ] **Step 6.5**: If the leak was due to a process failure, update developer onboarding and training materials.

- [ ] **Step 6.6**: Update this playbook with any lessons learned.

---

## 6. Communication Requirements

| Audience | When | Method | Content |
|----------|------|--------|---------|
| Incident Commander | Immediately on detection | Direct message / phone | Credential type, exposure vector |
| System Owner | Within 5 minutes | Direct message / phone | What was exposed, revocation status |
| Affected third parties | Within 24 hours (if applicable) | Email from `admin@example-ops.com` | Nature of exposure, steps taken, whether their data was at risk |
| Cloud / API providers | If token was used for unauthorized actions | Support ticket | Request audit logs, report unauthorized usage |

---

## 7. Evidence Preservation Checklist

| Artifact | Location | Collected? |
|----------|----------|------------|
| Git commit containing the secret | `git show <commit_hash>` | [ ] |
| Git log showing when secret was introduced | `git log --all -- <file>` | [ ] |
| Audit logs from affected service | Service-specific | [ ] |
| Cloud provider audit trail | Cloud provider dashboard | [ ] |
| Code repository platform security log | Platform settings | [ ] |
| Datadog logs for exposure window | Monitoring dashboard | [ ] |
| Gateway session logs | `svc-gateway` | [ ] |
| Screenshot of exposure (if applicable) | Saved to evidence directory | [ ] |
| BFG Repo Cleaner output | Terminal output | [ ] |
| Secrets manager audit log | Secrets manager dashboard | [ ] |

---

## 8. NIST 800-53 Control Mapping

| Control | Description | Playbook Phase |
|---------|-------------|----------------|
| IR-4 | Incident Handling | All phases |
| IR-5 | Incident Monitoring | Phase 1 (automated detection) |
| IR-6 | Incident Reporting | Phase 6 (post-incident report) |
| IA-5 | Authenticator Management | Phase 2 (credential rotation) |
| IA-5(1) | Password-Based Authentication | Phase 2 (password rotation) |
| IA-5(7) | No Embedded Unencrypted Static Authenticators | Phase 4 (repo cleanup), Phase 6 (prevention) |
| SC-28 | Protection of Information at Rest | Phase 2 (secrets manager usage) |
| AU-6 | Audit Review, Analysis, and Reporting | Phase 3 (log review) |
| AU-12 | Audit Generation | Phase 3 (audit trail review) |
| CM-3 | Configuration Change Control | Phase 4 (repository cleanup) |
| SA-11 | Developer Security Testing | Phase 6 (Gitleaks, pre-commit hooks) |
| AT-2 | Security Awareness Training | Phase 6 (training reminder) |

---

## 9. Quick Reference Card

**For use during an active incident, tear-off summary:**

```
1. REVOKE:  Disable or regenerate the credential AT ITS SOURCE immediately
2. ROTATE:  Generate new credential and write to Doppler
3. UPDATE:  Push new credential to .env (or doppler run) for all consumers
4. RESTART: docker compose restart <affected_services> (include n8n, keycloak, langfuse-worker, langfuse-web, squire for db creds)
5. VERIFY:  Confirm services healthy with new credential
6. AUDIT:   Review logs for unauthorized use during exposure window
7. CLEAN:   BFG repo cleaner (bare mirror flow) if committed to git, then force push
8. REPORT:  Post-incident report within 72 hours
```

**Remember: REVOKE FIRST, INVESTIGATE SECOND. Every minute counts.**

---

## Cross-References

| Document | Relationship |
|----------|-------------|
| [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) | System Security Plan with NIST 800-53 control mapping |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | Tracks findings and remediation milestones |
| [README.md](README.md) | GRC library index and reading guide |
