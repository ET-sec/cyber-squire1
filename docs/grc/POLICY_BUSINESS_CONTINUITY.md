# Business Continuity Plan (BCP)

**Document ID:** GRC-BCP-001
**Version:** 1.0
**Classification:** Internal Use Only
**Effective Date:** 2026-03-11
**Review Cycle:** Annual (next review: 2027-03-11)
**Owner:** Information Security Officer
**NIST 800-53 Controls:** CP-1, CP-2, CP-3, CP-4, CP-6, CP-7, CP-8, CP-9, CP-10

---

## 1. Purpose

This Business Continuity Plan establishes the framework for maintaining and restoring critical security operations platform services following a disruption event. The plan defines business impact thresholds, recovery priorities, and operational procedures to minimize downtime and data loss across the Organization's containerized infrastructure.

This policy applies to all 14 services (13 Compose-managed containers plus 1 standalone service) operating on the production VPS (`alpha-node`), supporting infrastructure-as-code assets, CI/CD pipelines, and associated data stores.

---

## 2. Scope

This plan covers:

- All production services deployed on `alpha-node` (4 vCPU / 8 GB RAM, Ubuntu 24.04)
- Infrastructure-as-code definitions and remote state
- CI/CD pipeline configurations and security tooling
- Backup data stored on encrypted object storage
- Zero-trust tunnel and edge security configurations
- Audit log integrity and export mechanisms

---

## 3. Roles and Responsibilities

| Role | Responsibility |
|------|----------------|
| Information Security Officer | BCP ownership, activation authority, recovery coordination |
| System Owner | Technical recovery execution, service restoration, validation |
| Auditor | Post-incident review, compliance verification, testing observation |

---

## 4. Business Impact Analysis (BIA)

### 4.1 Service Impact Assessment

Each service has been evaluated for its impact on confidentiality, integrity, availability, and operational dependency.

#### Tier 1 - Critical (Maximum Tolerable Downtime: 1 hour)

| Service | Function | Impact of Loss |
|---------|----------|----------------|
| `svc-db` (PostgreSQL 16) | Persistent data store for workflow state, automation data, audit records | Complete platform data loss; all dependent services fail; audit trail integrity compromised |
| `svc-tunnel` | Zero-trust ingress; sole external access path to `svc-automation` and SSH | Total loss of remote management capability; no external access to any service |
| `svc-gateway` | SSH session gateway, session recording, JIT access provisioning | Loss of auditable access control; inability to grant or revoke privileged access |
| `svc-secrets` (secrets engine) | Runtime secret distribution, encryption-as-a-service | Services cannot retrieve secrets at startup; rotation and seal/unseal operations blocked |

#### Tier 2 - Important (Maximum Tolerable Downtime: 4 hours)

| Service | Function | Impact of Loss |
|---------|----------|----------------|
| `svc-automation` (SOAR engine) | Workflow orchestration, incident response automation, bot integrations | Automated response halted; manual intervention required for all operational tasks |
| `svc-identity` | Identity federation, SSO, role-based access (3 roles defined) | New authentication requests fail; existing sessions may persist but cannot be renewed |
| `svc-monitor` (observability agent) | Metrics collection, alerting, dashboard telemetry | Loss of visibility into platform health; degraded incident detection capability |
| `svc-detection` (eBPF runtime) | Kernel-level syscall monitoring, anomaly detection | Runtime threat detection disabled; container escape or privilege escalation may go undetected |
| `svc-detection-router` | Alert routing from detection engine to downstream consumers | Detection findings not forwarded; alerts silently dropped |

#### Tier 3 - Deferrable (Maximum Tolerable Downtime: 24 hours)

| Service | Function | Impact of Loss |
|---------|----------|----------------|
| `svc-llm` | Local LLM inference for automation workflows | AI-assisted tasks degrade to manual; no data leaves the platform |
| `svc-transcription` | Voice-to-text transcription | Audio processing unavailable; non-blocking for security operations |
| `Fluentd` | Log aggregation and forwarding to object storage | Log export delayed; local logs still written; integrity chain paused but not broken |
| `svc-event-shipper` | Audit event export from gateway to log pipeline | Audit events queued locally; export resumes on recovery |
| `svc-ai-gateway` | Standalone AI gateway for external model access | AI-assisted operations unavailable; no impact on core security functions |

### 4.2 Dependency Map

```
svc-tunnel (ingress)
 --> svc-automation --> svc-db
 --> svc-gateway --> svc-db
 --> svc-identity --> svc-db
 --> svc-secrets (independent, sealed storage)
 --> svc-monitor (independent, pushes to Datadog)
 --> svc-detection --> svc-detection-router --> Fluentd --> object storage
 --> svc-event-shipper --> Fluentd
```

**Key dependency:** `svc-db` is a single point of failure for `svc-automation`, `svc-gateway`, and `svc-identity`. Its recovery is prerequisite to all Tier 1 and Tier 2 services.

---

## 5. Recovery Priorities

Recovery SHALL proceed in strict tier order. Within each tier, services are restored in the sequence listed below to satisfy dependencies.

### Phase 1 - Critical Services (Target: 0–60 minutes)

1. **`svc-db`** - Restore PostgreSQL from backup or redeploy with empty schema
2. **`svc-secrets`** - Unseal Vault; verify seal keys are available offline
3. **`svc-tunnel`** - Re-establish zero-trust tunnel for remote access
4. **`svc-gateway`** - Restore SSH gateway and session recording

### Phase 2 - Important Services (Target: 1–4 hours)

5. **`svc-identity`** - Restore identity provider with realm configuration
6. **`svc-automation`** - Redeploy SOAR engine; verify workflow state in `svc-db`
7. **`svc-detection`** - Restart runtime detection with eBPF driver loaded
8. **`svc-detection-router`** - Reconnect detection alert routing
9. **`svc-monitor`** - Restore observability agent and verify telemetry flow

### Phase 3 - Deferrable Services (Target: 4–24 hours)

10. **`Fluentd`** - Restore log aggregation pipeline
11. **`svc-event-shipper`** - Resume audit event export
12. **`svc-llm`** - Redeploy LLM inference container
13. **`svc-transcription`** - Redeploy transcription service
14. **`svc-ai-gateway`** - Redeploy AI gateway

---

## 6. Recovery Strategies

### 6.1 Infrastructure-as-Code Rebuild

The primary recovery strategy is full infrastructure rebuild from version-controlled IaC definitions.

**Procedure:**
1. Provision a new VPS instance from the infrastructure-as-code platform using remote state stored on encrypted object storage
2. Execute the IaC apply command against the production workspace; the remote state file defines the complete infrastructure specification
3. Verify VPS provisioning, network configuration, firewall rules, and DNS records
4. Deploy container stack using Docker Compose definitions from the code repository

**Prerequisites:**
- Access to the code repository containing IaC definitions and Compose files
- Access to the secrets manager or offline copy of production secrets
- Access to encrypted object storage for IaC remote state
- SSH key material available locally or in the credential vault

### 6.2 Backup Restoration

| Backup Type | Location | Frequency | Retention | Restoration Method |
|-------------|----------|-----------|-----------|-------------------|
| PostgreSQL dumps | `CD_BACKUPS/` volume mount + object storage | Daily | 30 days | `pg_restore` into fresh `svc-db` container |
| IaC state | Encrypted object storage (versioned) | On every `apply` | Indefinite (versioned) | Pull from remote backend |
| Docker Compose | Code repository | On every merge | Full git history | `git clone` + `docker compose up -d` |
| Secrets engine seal keys | Offline storage (credential vault) | On initialization | Permanent | Manual unseal after container restart |
| Infrastructure policies | Code repository | On every merge | Full git history | Restored with IaC pipeline |
| Tunnel credentials | Secrets manager | On rotation | Current + previous | Re-inject into container environment |

### 6.3 Container Re-Pull Strategy

All containers are defined in Docker Compose with pinned image references. Recovery does not require building images from source.

```
Recovery sequence:
1. docker compose pull     # Pull all 13 images from registries
2. docker compose up -d svc-db # Start database first
3. [restore PostgreSQL backup]
4. docker compose up -d     # Start remaining services
5. [unseal svc-secrets]
6. [verify svc-tunnel connectivity]
```

### 6.4 Alternate Site Strategy

If the primary DigitalOcean region is unavailable:

1. Deploy IaC to an alternate region or provider using the same infrastructure-as-code definitions (provider block override)
2. Update Cloudflare DNS records to point to the new IP
3. Re-establish the zero-trust tunnel with new tunnel credentials
4. Restore data from the most recent backup on object storage (cross-region accessible)

---

## 7. Communication Plan

### 7.1 Internal Notification

| Trigger | Action | Channel | Timeframe |
|---------|--------|---------|-----------|
| Service disruption detected | Information Security Officer notified | Datadog alert + automated messaging | Immediate |
| BCP activated | Stakeholders informed | Secure messaging channel | Within 15 minutes |
| Recovery milestone reached | Status update distributed | Secure messaging channel | At each phase completion |
| Full recovery confirmed | All-clear notification | Secure messaging channel + email | Upon validation |

### 7.2 External Communication

| Audience | Trigger | Channel | Owner |
|----------|---------|---------|-------|
| Dependent service consumers | Extended outage (>1 hour) | Status page or direct notification | System Owner |
| Cloud provider support | Provider-side incident suspected | Provider support portal | System Owner |
| Compliance stakeholders | Data loss or integrity event | Written incident report | Information Security Officer |

### 7.3 Escalation Matrix

| Elapsed Time | Action |
|--------------|--------|
| 0–15 minutes | System Owner begins triage; automated alerts fire |
| 15–30 minutes | BCP activation decision; Information Security Officer notified |
| 30–60 minutes | Phase 1 recovery underway; external communication if needed |
| 1–4 hours | Phase 2 recovery; situation report prepared |
| 4+ hours | Alternate site strategy evaluated; extended outage procedures |

---

## 8. Testing Schedule

### 8.1 Test Types

| Test Type | Description | Frequency | Participants |
|-----------|-------------|-----------|-------------|
| **Tabletop Exercise** | Walk through disaster scenarios against this plan; identify gaps | Semi-annual | Information Security Officer, System Owner |
| **Component Recovery Test** | Restore a single service (e.g., `svc-db` from backup) in isolation | Quarterly | System Owner |
| **Full Recovery Test** | Tear down and rebuild the entire stack from IaC + backups on a test instance | Annual | System Owner, Information Security Officer |
| **Backup Verification** | Verify backup integrity by restoring to a temporary environment | Monthly | System Owner |
| **Failover Test** | Simulate DigitalOcean region failure; deploy to alternate region | Annual | System Owner |

### 8.2 Test Documentation Requirements

Each test SHALL produce:

1. Test date and participants
2. Scenario description
3. Expected vs. actual recovery time
4. Issues encountered and resolution
5. Corrective actions identified
6. Sign-off by Information Security Officer

### 8.3 Plan Update Triggers

This plan SHALL be updated when:

- A new service is added to or removed from the platform
- A test reveals a gap or inaccuracy
- A real disruption occurs and lessons learned are identified
- Infrastructure architecture changes materially (e.g., provider migration, multi-node deployment)
- Annually, regardless of other triggers

---

## 9. Plan Activation Criteria

The BCP SHALL be activated when any of the following conditions are met:

1. **Complete VPS loss** - `alpha-node` is unreachable and DigitalOcean confirms host failure
2. **Data corruption** - `svc-db` data is confirmed corrupted or unrecoverable
3. **Ransomware/compromise** - Evidence of unauthorized encryption or persistent unauthorized access
4. **Cloud provider outage** - Provider region is unavailable for more than 30 minutes
5. **Zero-trust tunnel failure** - `svc-tunnel` is down and cannot be re-established within 15 minutes, AND direct SSH is also unavailable

**Activation authority:** Information Security Officer (primary), System Owner (alternate)

---

## 10. Recovery Validation Checklist

Before declaring recovery complete, the following validations SHALL be performed:

- [ ] `svc-db` is accepting connections; data integrity verified against last known good state
- [ ] `svc-secrets` is unsealed and serving secrets
- [ ] `svc-tunnel` is operational; `automation.example-ops.com` resolves and responds
- [ ] `svc-gateway` is recording sessions; JIT access flow functional
- [ ] `svc-automation` workflows are active and processing
- [ ] `svc-identity` authentication flow succeeds for all three roles
- [ ] `svc-detection` is generating kernel-level events
- [ ] `svc-monitor` is reporting metrics to Datadog
- [ ] Audit log hash chain is intact or re-initialized with documented gap
- [ ] Cloudflare DNS records point to correct endpoint
- [ ] All 13 Compose-managed containers show healthy status in `docker compose ps`; standalone `svc-ai-gateway` verified separately

---

## 11. Document Control

| Field | Value |
|-------|-------|
| Document ID | GRC-BCP-001 |
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
