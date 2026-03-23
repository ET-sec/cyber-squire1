# Disaster Recovery Plan (DRP)

**Document ID:** GRC-DRP-001
**Version:** 1.0
**Classification:** Internal Use Only
**Effective Date:** 2026-03-11
**Review Cycle:** Annual (next review: 2027-03-11)
**Owner:** Information Security Officer
**NIST 800-53 Controls:** CP-2, CP-4, CP-6, CP-7, CP-9, CP-10

---

## 1. Purpose

This Disaster Recovery Plan defines the procedures for recovering the Organization's security operations platform from catastrophic failures, data loss events, and other disaster scenarios. It establishes Recovery Point Objectives (RPO) and Recovery Time Objectives (RTO) for each service, documents step-by-step recovery procedures, and defines the backup strategy that underpins all recovery operations.

This plan is a companion to GRC-BCP-001 (Business Continuity Plan) and focuses specifically on technical recovery procedures.

---

## 2. Scope

This plan covers the recovery of:

- The production VPS (`alpha-node`) and all 14 services (13 Compose-managed containers plus 1 standalone service)
- PostgreSQL databases and persistent data volumes
- Infrastructure-as-code state and definitions
- CI/CD pipeline configurations
- Zero-trust tunnel and edge security configurations
- Audit log integrity and hash-chain continuity
- Secret material and encryption keys

---

## 3. RPO/RTO Targets

### 3.1 Recovery Objectives by Service

| Service | Tier | RTO | RPO | Justification |
|---------|------|-----|-----|---------------|
| `svc-db` | Critical | 30 min | 24 hours | Daily backup; data is authoritative store for automation, identity, and gateway |
| `svc-secrets` | Critical | 15 min | 0 (sealed storage) | Secrets engine data persists in volume; seal keys stored offline; no data loss expected |
| `svc-tunnel` | Critical | 15 min | 0 (stateless) | Stateless service; credentials from secrets manager; instant redeploy |
| `svc-gateway` | Critical | 30 min | 24 hours | Session recordings stored locally; audit events exported daily |
| `svc-automation` | Important | 1 hour | 24 hours | Workflow state in `svc-db`; workflow definitions in code repository |
| `svc-identity` | Important | 1 hour | 24 hours | Realm config exportable; user data in `svc-db` |
| `svc-monitor` | Important | 2 hours | 0 (stateless) | Agent is stateless; historical data lives in Datadog SaaS |
| `svc-detection` | Important | 2 hours | 0 (stateless) | Stateless eBPF sensor; rules pulled from image; no local state |
| `svc-detection-router` | Important | 2 hours | 0 (stateless) | Stateless routing; configuration in Docker Compose |
| `svc-llm` | Deferrable | 8 hours | 0 (re-download) | Models re-pulled on start; no persistent state to recover |
| `svc-transcription` | Deferrable | 8 hours | 0 (re-download) | Model cache re-built on start |
| `Fluentd` | Deferrable | 4 hours | 1 hour | Buffered logs in memory; exported logs on object storage are durable |
| `svc-event-shipper` | Deferrable | 4 hours | 1 hour | Events queued in gateway; resume export on restart |
| `svc-ai-gateway` | Deferrable | 8 hours | 0 (stateless) | Configuration in file; no persistent data |

### 3.2 Aggregate Platform Targets

| Metric | Target |
|--------|--------|
| Full platform RTO | 4 hours (all Tier 1 + Tier 2 operational) |
| Full platform RPO | 24 hours (worst case, driven by daily PostgreSQL backups) |
| Maximum tolerable data loss | 24 hours of workflow state and automation data |
| Maximum tolerable downtime | 4 hours for critical + important services |

---

## 4. Disaster Scenarios

### 4.1 Scenario A - DigitalOcean Outage (Region Unavailable)

**Description:** DigitalOcean's hosting region becomes unavailable due to infrastructure failure, network partition, or provider-side incident.

**Impact:** All 14 services offline (13 Compose-managed + 1 standalone). No remote access via tunnel or direct SSH. Datadog may still have historical data.

**Detection:** Datadog alerts on host unreachable; Cloudflare health checks fail; manual verification via provider status page.

**Recovery Procedure:**

1. Confirm outage via DigitalOcean status page and support channels
2. Assess estimated recovery time from provider
3. **If provider ETA > 1 hour:** Initiate alternate-region deployment
  - a. Update infrastructure-as-code provider configuration for alternate region
  - b. Execute `iac apply` to provision new VPS in alternate region
  - c. Deploy container stack via Docker Compose
  - d. Restore `svc-db` from latest backup on object storage
  - e. Unseal `svc-secrets` using offline seal keys
  - f. Update Cloudflare DNS to point to new VPS IP `10.100.1.10`
  - g. Re-establish zero-trust tunnel with new tunnel token
  - h. Validate all services per recovery checklist (Section 8)
4. **If provider ETA < 1 hour:** Monitor and wait; prepare alternate deployment in parallel
5. When original region recovers, evaluate whether to fail back or remain on alternate

### 4.2 Scenario B - VPS Corruption (OS or Disk Failure)

**Description:** The VPS operating system becomes unbootable, the disk is corrupted, or a kernel panic renders the host non-functional. DigitalOcean infrastructure is operational but the specific instance is damaged.

**Impact:** All 14 services offline (13 Compose-managed + 1 standalone). Data on local volumes may be lost or inaccessible.

**Detection:** SSH connection refused or timeout; Datadog reports host down; DigitalOcean console shows instance in error state.

**Recovery Procedure:**

1. Attempt VPS recovery via DigitalOcean console (reboot, recovery mode)
2. **If recovery fails:**
  - a. Destroy the corrupted VPS instance via infrastructure-as-code: `iac destroy -target=<vps_resource>`
  - b. Re-provision: `iac apply` (same region, fresh instance)
  - c. SSH into new instance; verify base OS configuration
  - d. Copy Docker Compose files and environment configuration from code repository
  - e. Inject secrets from secrets manager into `.env` file (chmod 600)
  - f. Pull container images: `docker compose pull`
  - g. Start database first: `docker compose up -d svc-db`
  - h. Restore PostgreSQL from latest backup:
   ```
   pg_restore -U <db_user> -d <db_name> /path/to/backup.dump
   ```
  - i. Start remaining services: `docker compose up -d`
  - j. Unseal `svc-secrets`
  - k. Re-establish zero-trust tunnel
  - l. Update DNS if IP changed
  - m. Validate all services per recovery checklist (Section 8)

### 4.3 Scenario C - Data Loss (Database Corruption or Deletion)

**Description:** PostgreSQL data is corrupted, accidentally deleted, or rendered inconsistent. The VPS and other services remain operational.

**Impact:** `svc-automation`, `svc-identity`, and `svc-gateway` lose persistent state. Workflows halt. Authentication may fail. Audit records in database are lost.

**Detection:** Application errors in `svc-automation` logs; database connection failures; integrity check failures in audit log hash chain.

**Recovery Procedure:**

1. Stop services that depend on `svc-db`:
  ```
  docker compose stop svc-automation svc-identity svc-gateway
  ```
2. Assess database state:
  ```
  docker compose exec svc-db pg_isready
  docker compose exec svc-db psql -U <db_user> -c "SELECT count(*) FROM pg_stat_activity;"
  ```
3. **If database is running but data is corrupt:**
  - a. Stop `svc-db`: `docker compose stop svc-db`
  - b. Move corrupted data directory: `mv db-data-volume db-data-volume.corrupt.$(date +%s)`
  - c. Start fresh `svc-db`: `docker compose up -d svc-db`
  - d. Restore from latest backup:
   ```
   cat CD_BACKUPS/latest.sql | docker compose exec -T svc-db psql -U <db_user> -d <db_name>
   ```
  - e. Verify row counts and schema integrity
  - f. Restart dependent services: `docker compose up -d`
4. **If database container itself is damaged:**
  - a. Remove container: `docker compose rm -f svc-db`
  - b. Remove corrupted volume data
  - c. Re-pull image: `docker compose pull svc-db`
  - d. Start and restore as above
5. Validate audit log hash chain; document any gap in chain continuity
6. Re-export audit logs to object storage to re-establish export continuity

### 4.4 Scenario D - Ransomware / Unauthorized Encryption

**Description:** An attacker gains access to `alpha-node` and encrypts data volumes, container images, or the host filesystem.

**Impact:** Total platform compromise. All data and services potentially encrypted or tampered with. Integrity of all local data is suspect.

**Detection:** Datadog alerts on anomalous disk I/O or process execution; `svc-detection` (Falco) fires rules on mass file modification; services crash with I/O errors; SSH access fails or presents unexpected behavior.

**Recovery Procedure:**

1. **ISOLATE IMMEDIATELY:**
  - a. Revoke all DigitalOcean API tokens via secrets manager
  - b. Disable the zero-trust tunnel via Cloudflare dashboard
  - c. If accessible, power off the VPS via DigitalOcean console (do NOT attempt SSH login to compromised host)
  - d. Rotate ALL secrets in the secrets manager (assume complete credential compromise)

2. **PRESERVE EVIDENCE:**
  - a. Create a snapshot of the compromised VPS disk via DigitalOcean console (do not boot it)
  - b. Export Datadog logs, detection engine alerts, and audit events from external stores
  - c. Document timeline of detection and response actions

3. **REBUILD FROM CLEAN STATE:**
  - a. Provision a new VPS via infrastructure-as-code: `iac apply` (new instance, do NOT reuse compromised disk)
  - b. Deploy container stack with rotated secrets
  - c. Restore `svc-db` from the last known-good backup (verify backup predates compromise)
  - d. Re-establish zero-trust tunnel with new credentials
  - e. Validate all services per recovery checklist (Section 8)

4. **POST-INCIDENT:**
  - a. Conduct forensic analysis on the preserved disk snapshot
  - b. Determine root cause and attack vector
  - c. Update access controls, detection rules, and this DRP based on findings
  - d. File incident report per organizational incident response procedures
  - e. Verify audit log hash chain integrity on object storage (immutable copies should be trustworthy)

---

## 5. Backup Strategy

### 5.1 Backup Inventory

| Backup Item | Method | Frequency | Retention | Storage Location | Encryption |
|-------------|--------|-----------|-----------|-----------------|------------|
| PostgreSQL full dump | `pg_dump` to mounted volume | Daily (cron) | 30 days rolling | `CD_BACKUPS/` volume + object storage | At-rest encryption on object storage |
| IaC state | Remote backend (auto-versioned) | On every IaC apply | Indefinite (versioned) | Encrypted object storage | Provider-managed encryption |
| Docker Compose + .env template | Git commit | On every change | Full git history | Code repository platform | Repository access controls |
| Secrets engine seal keys | Manual export | On secrets engine initialization | Permanent | Credential vault (offline) | secrets engine native encryption + credential vault encryption |
| Infrastructure policies (Rego) | Git commit | On every change | Full git history | Code repository platform | Repository access controls |
| CI/CD pipeline definitions | Git commit | On every change | Full git history | Code repository platform | Repository access controls |
| Audit logs (hash-chained) | Export to object storage | Continuous (via `svc-event-shipper` + `Fluentd`) | 365 days | Encrypted object storage | At-rest encryption; hash-chain integrity |
| Identity provider realm export | Manual or scripted | After realm changes | 3 versions | Object storage | At-rest encryption |
| Cloudflare config | API export | After changes | Current + previous | Secrets manager | Secrets manager encryption |

### 5.2 Backup Verification

| Verification Type | Frequency | Procedure |
|-------------------|-----------|-----------|
| PostgreSQL restore test | Monthly | Restore latest dump to temporary container; verify row counts and schema |
| IaC state validation | Monthly | Run IaC plan against production; confirm no drift |
| Audit log integrity check | Weekly | Verify hash chain continuity on exported logs |
| Secrets engine unseal test | Quarterly | Unseal secrets engine in test environment using offline seal keys |
| Full stack rebuild from backups | Annually | Provision test VPS; rebuild entire stack; validate all services |

### 5.3 Backup Security Controls

1. All backups on object storage SHALL use server-side encryption with provider-managed keys
2. Object storage buckets SHALL have versioning enabled to protect against accidental deletion
3. Access to backup storage SHALL be restricted to the System Owner role and automated backup processes
4. Backup credentials SHALL be stored in the secrets manager, separate from production service credentials
5. PostgreSQL backup scripts SHALL log success/failure to `svc-monitor` for alerting
6. Secrets engine seal keys SHALL NEVER be stored on the same host as the secrets engine data

---

## 6. Recovery Procedures - Detailed Playbooks

### 6.1 Playbook: Full Stack Rebuild from IaC

**Trigger:** VPS is destroyed, corrupted, or compromised beyond repair.

**Time estimate:** 2-4 hours for full recovery.

**Prerequisites:**
- Local workstation with infrastructure-as-code platform CLI installed
- Access to secrets manager
- Access to code repository platform
- Access to encrypted object storage (IaC state + backups)
- Cloud provider API token (from secrets manager)

**Steps:**

```
Step 1: Retrieve secrets
$ secrets-cli get CLOUD_PROVIDER_TOKEN --plain # [sanitized command]
$ # Export required environment variables for IaC

Step 2: Initialize and apply infrastructure
$ cd <iac-directory>
$ iac init             # Pulls remote state from object storage
$ iac plan             # Review what will be created
$ iac apply             # Provision VPS + networking + firewall

Step 3: Note new VPS IP; update local SSH config if changed

Step 4: SSH to new VPS
$ ssh alpha-node

Step 5: Clone operations repository
$ git clone <repo-url> /root/operations

Step 6: Create environment file
$ # Pull secrets from secrets manager
$ # Write to /root/operations/.env (chmod 600)

Step 7: Pull and start containers
$ cd /root/operations
$ docker compose pull
$ docker compose up -d svc-db
$ # Wait for svc-db to be ready

Step 8: Restore PostgreSQL
$ # Download latest backup from object storage
$ cat backup.sql | docker compose exec -T svc-db psql -U <user> -d <db>

Step 9: Start all Compose-managed services
$ docker compose up -d

Step 9a: Rebuild standalone svc-ai-gateway
$ # svc-ai-gateway runs outside Compose; redeploy from its own config
$ # See gateway configuration file for container run parameters

Step 10: Unseal Vault
$ docker compose exec svc-secrets vault operator unseal <key1>
$ docker compose exec svc-secrets vault operator unseal <key2>
$ docker compose exec svc-secrets vault operator unseal <key3>

Step 11: Re-establish tunnel
$ # Inject new tunnel token into environment
$ docker compose restart svc-tunnel

Step 12: Update DNS
$ # Point automation.example-ops.com to new IP via Cloudflare
$ # Point ssh.example-ops.com to new IP via Cloudflare

Step 13: Validate (see Section 8)
```

### 6.2 Playbook: PostgreSQL Point-in-Time Recovery

**Trigger:** Database corruption detected; services reporting data errors.

**Time estimate:** 30-60 minutes.

**Steps:**

```
Step 1: Stop dependent services
$ docker compose stop svc-automation svc-identity svc-gateway

Step 2: Identify latest clean backup
$ ls -lt CD_BACKUPS/        # Local backups
$ # Also check object storage for off-host copies

Step 3: Stop database
$ docker compose stop svc-db

Step 4: Preserve corrupted data (forensics)
$ mv db-data-volume db-data-volume.corrupt.$(date +%Y%m%d%H%M%S)

Step 5: Start fresh database
$ docker compose up -d svc-db
$ # Wait for initialization

Step 6: Restore backup
$ cat CD_BACKUPS/<selected_backup>.sql | docker compose exec -T svc-db psql -U <user> -d <db>

Step 7: Verify restoration
$ docker compose exec svc-db psql -U <user> -d <db> -c "\dt"
$ docker compose exec svc-db psql -U <user> -d <db> -c "SELECT count(*) FROM <critical_table>;"

Step 8: Restart all services
$ docker compose up -d

Step 9: Validate audit log hash chain
$ # Check for gaps; document any discontinuity
```

### 6.3 Playbook: Secret Rotation After Compromise

**Trigger:** Suspected or confirmed unauthorized access to credentials.

**Time estimate:** 1-2 hours.

**Steps:**

```
Step 1: Identify scope of compromise
$ # Which secrets were potentially exposed?
$ # What access did those secrets grant?

Step 2: Rotate secrets in secrets manager
$ # Generate new values for all potentially compromised secrets
$ # Update secrets manager entries

Step 3: Rotate DigitalOcean API tokens
$ # Revoke old tokens via provider console
$ # Generate new tokens
$ # Update secrets manager

Step 4: Rotate database credentials
$ docker compose exec svc-db psql -U <admin> -c "ALTER USER <user> PASSWORD '<new_password>';"

Step 5: Rotate tunnel credentials
$ # Generate new tunnel token via Cloudflare
$ # Update secrets manager

Step 6: Update environment file on VPS
$ # Pull new secrets; rewrite .env (chmod 600)

Step 7: Restart all services
$ docker compose down && docker compose up -d

Step 8: Unseal Vault with existing seal keys (Secrets engine data is not compromised by credential rotation)

Step 9: Verify all services authenticate successfully

Step 10: Document rotation in change log
```

---

## 7. Recovery Testing

### 7.1 Test Schedule

| Test | Frequency | Scope | Success Criteria |
|------|-----------|-------|-----------------|
| PostgreSQL backup restore | Monthly | Restore latest dump to temporary container | Data integrity verified; row counts match |
| IaC plan validation | Monthly | IaC plan against production state | Zero unexpected changes |
| Single container recovery | Quarterly | Destroy and recreate one Tier 2 service | Service operational within RTO |
| Full stack rebuild (test instance) | Annually | Complete Playbook 6.1 on separate VPS | All 14 services pass validation checklist within 4 hours |
| Ransomware scenario tabletop | Annually | Walk through Scenario D with all roles | All steps executable; no missing procedures |
| Backup integrity audit | Quarterly | Verify all backup items exist and are current | All items in Section 5.1 present and within retention window |

### 7.2 Test Documentation

Each test SHALL produce a test report containing:

1. Test date, type, and participants
2. Scenario executed
3. Measured RTO and RPO achieved
4. Deviations from documented procedures
5. Issues encountered and resolutions
6. Corrective actions for plan improvement
7. Sign-off by Information Security Officer

---

## 8. Recovery Validation Checklist

The following checklist SHALL be completed after every disaster recovery operation before declaring recovery complete.

### 8.1 Infrastructure Layer

- [ ] VPS is provisioned and accessible via SSH
- [ ] Firewall rules match IaC definition (no unexpected open ports)
- [ ] Disk space is adequate (check with `df -h`)
- [ ] Docker daemon is running and healthy
- [ ] All 13 Compose-managed containers show `running` status in `docker compose ps`; standalone `svc-ai-gateway` verified separately

### 8.2 Data Layer

- [ ] `svc-db` accepts connections and responds to queries
- [ ] Critical tables exist and contain expected data
- [ ] Audit log hash chain is intact (or gap is documented)
- [ ] `svc-secrets` is unsealed and serving secrets
- [ ] Persistent volumes are mounted correctly

### 8.3 Access Layer

- [ ] `svc-tunnel` is connected; `automation.example-ops.com` resolves correctly
- [ ] `ssh.example-ops.com` provides gateway-mediated access
- [ ] `svc-gateway` session recording is functional (test with a sample session)
- [ ] `svc-identity` authentication works for all three roles (admin, operator, auditor)
- [ ] JIT access provisioning flow completes successfully

### 8.4 Security Layer

- [ ] `svc-detection` is generating eBPF events
- [ ] `svc-detection-router` is forwarding alerts
- [ ] `svc-monitor` is reporting metrics to Datadog
- [ ] `Fluentd` is exporting logs to object storage
- [ ] `svc-event-shipper` is exporting audit events

### 8.5 Application Layer

- [ ] `svc-automation` workflows are active and trigger-able
- [ ] Webhook endpoints respond (test with health check)
- [ ] `svc-llm` responds to inference requests
- [ ] `svc-transcription` processes audio input
- [ ] `svc-ai-gateway` accepts API calls

---

## 9. Plan Maintenance

### 9.1 Update Triggers

This DRP SHALL be updated when:

- Any disaster scenario is executed (real or test)
- A new service is added to or removed from the platform
- Backup procedures or schedules change
- RPO/RTO targets are revised
- Infrastructure architecture changes (e.g., multi-node, new provider)
- Annually, regardless of other triggers

### 9.2 Distribution

Updated versions SHALL be distributed to:

- Information Security Officer (primary copy)
- System Owner (operational copy)
- Offline storage (printed or USB, for scenarios where digital access is lost)

---

## 10. Document Control

| Field | Value |
|-------|-------|
| Document ID | GRC-DRP-001 |
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
