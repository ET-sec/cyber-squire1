---
document_id: POAM-OPS-001
title: Plan of Action and Milestones
doc_type: poam
system_name: Organization Security Operations Platform
classification: INTERNAL-USE-ONLY
version: "1.3"
last_updated: 2026-06-24
next_review: 2026-07-24
owner: System Owner (Platform Administrator)
contact: admin@example-ops.com
parent_ssp: SSP-OPS-001
related:
  - SSP-OPS-001
  - SSP-SQUIRE-001
  - RT-SQUIRE-001
  - AITC-OPS-001
---

# Plan of Action and Milestones (POA&M)

**System Name:** Organization Security Operations Platform
**System Owner:** System Owner (Platform Administrator)
**Contact:** admin@example-ops.com
**Document Date:** 2026-03-11 (v1.0), 2026-04-24 (v1.1 Phase 17 entries), 2026-06-24 (v1.3 audit refresh)
**Classification:** Internal Use Only
**Version:** 1.3

<!-- TODO(et): 2026-06-24 audit refresh propagated embedding-provider and code-path corrections plus past-due status flags. Many Q2 milestones (POAM-003, POAM-005, POAM-014, POAM-019, POAM-022, POAM-023, POAM-024, POAM-025, POAM-026, POAM-027, POAM-P17-08, POAM-P17-10) need owner verification before flipping to Closed; left as Open with a past-due flag rather than blind-closing. -->


---

### POA&M Dashboard

```
POA&M Status Distribution (30 entries, Phase 17 v1.1)
┌─────────────────────────────────────────────────────────────┐
│ ████████████████████████████████████████        Accepted    │  15  (60%)
│ ████████                                        Open        │   4  (16%)
│ ████████████                                    Closed      │   6  (24%)
└─────────────────────────────────────────────────────────────┘

Source Distribution (30 entries)
┌──────────────────────────┬──────────────────────────────────┐
│ CIS Docker Bench         │ ███████████████                  │   9 entries
│ Risk Assessment          │ ████████                         │   5 entries
│ Checkov IaC              │ █                                │   1 entry  │
│ Phase 17 Squire          │ ██████████                       │  10 entries │
└──────────────────────────┴──────────────────────────────────┘
```

> **Counting note:** The original v1.0 dashboard claimed 27 entries, 19 CIS, 5 Risk, 2 Checkov, 1 Falco. The actual `POAM-*` row count in the register at v1.0 was 15 (register entries differ from underlying finding counts because multiple CIS findings roll into a single POAM row when mitigated by identical compensating controls). Phase 17 added 10 entries in POAM-P17-01 through P17-10 (cycle 1 red-team and deferred rails), then 4 more in P17-11 through P17-14 (threat model residuals from 17-14), then 1 more in P17-15 (cycle 2 red-team infra finding) for a v1.3 total of 30.

---

## 1. Executive Summary

This Plan of Action and Milestones (POA&M) consolidates security findings from three assessment sources across the Organization security operations platform hosted on a DigitalOcean VPS (`alpha-node`, `10.100.1.10`). Findings are tracked through remediation or formal risk acceptance with documented compensating controls.

### Finding Summary by Source

| Source | Scan Date | High | Medium | Low | Total |
|--------|-----------|------|--------|-----|-------|
| CIS Docker Bench for Security | 2026-03-11 | 0 | 4 | 25 | 29 |
| Checkov / Checkov Static Analysis | Continuous (CI/CD) | 0 | 0 | 3 | 3 |
| Falco Runtime Detection | 2026-03-11 (baseline) | 0 | 0 | 0 | 0 |
| Risk Assessment (Mitigate treatments) | 2026-03-11 | 0 | 3 | 2 | 5 |
| **Total** | | **0** | **7** | **30** | **37** |

### Risk Posture

- **Critical / High findings:** None. No findings require emergency remediation.
- **Medium findings (4):** All have documented compensating controls and are tracked for either remediation or formal risk acceptance. These relate to container privilege requirements inherent to security tooling and upstream image constraints.
- **Low findings (28):** Mitigated by compensating controls including eBPF runtime detection, centralized log shipping, resource limits, and network-layer isolation. Formally accepted where remediation would degrade security posture or break functionality.
- **Continuous monitoring:** Falco (eBPF), Datadog, and CI/CD pipelines provide ongoing detection and prevention.

---

## 2. POA&M Register

### Source 1: CIS Docker Bench for Security (29 Findings)

#### Medium Findings

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-001 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 2.8 |
| **Description** | User namespace support is not enabled on the Docker daemon. Container root maps directly to host root, increasing the blast radius of a container escape. |
| **Risk Level** | Medium |
| **NIST 800-53 Control** | CM-6 (Configuration Settings), SC-39 (Process Isolation) |
| **Affected Components** | Docker daemon (all containers on `alpha-node`) |
| **Compensating Controls** | `no-new-privileges` set on all containers except svc-detection (requires eBPF). `cap_drop: ALL` with explicit minimum `cap_add` on privileged containers. AppArmor profiles active on host. |
| **Remediation Plan** | Evaluate user namespace remapping with per-container UID/GID mapping for svc-db (uid 999), svc-automation (uid 1000). Requires volume permission migration and testing for svc-detection compatibility. |
| **Milestone** | 2026-06-09, Re-evaluate feasibility after Compose v2.28+ supports per-container userns |
| **Status** | Accepted Risk |
| **Responsible Party** | Platform Administrator |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-002 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 4.1 |
| **Description** | Five containers run processes as the root user inside the container: svc-monitor, svc-db, svc-llm, svc-secrets, svc-transcription. These are official upstream images that require root for their core functionality. |
| **Risk Level** | Medium |
| **NIST 800-53 Control** | AC-6 (Least Privilege), CM-6 (Configuration Settings) |
| **Affected Components** | svc-monitor, svc-db, svc-llm, svc-secrets, svc-transcription |
| **Compensating Controls** | `no-new-privileges: true` on all affected containers. Memory, CPU, and PIDs limits enforced via Compose resource constraints. Falco monitors for privilege escalation attempts via eBPF syscall tracing. |
| **Remediation Plan** | Monitor upstream image releases for non-root variants. Build custom Dockerfiles with `USER` directive where feasible (svc-llm and svc-transcription are candidates). svc-db and svc-secrets require root by design. |
| **Milestone** | 2026-06-09, Reassess upstream image status; build non-root variants for svc-llm and svc-transcription if available |
| **Status** | Accepted Risk |
| **Responsible Party** | Platform Administrator |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-003 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 4.5 |
| **Description** | Docker Content Trust (`DOCKER_CONTENT_TRUST=1`) is not enabled. Image pulls do not verify Notary signatures, allowing potentially tampered images. |
| **Risk Level** | Medium |
| **NIST 800-53 Control** | SI-7 (Software, Firmware, and Information Integrity), CM-14 (Signed Components) |
| **Affected Components** | Docker daemon, all image pulls on `alpha-node` |
| **Compensating Controls** | CI/CD pipeline runs container signature verification (soft-fail) for images that support it. Container vulnerability scanner scans all images for known vulnerabilities on every push and PR. SBOMs generated for 6 key images (svc-db, svc-automation, svc-secrets, svc-monitor, svc-tunnel, repository filesystem). Image digest manifest generated per deployment. |
| **Remediation Plan** | Enable Docker Content Trust in CI/CD build environment. Maintain an allowlist of unsigned upstream images (svc-detection, svc-detection-router, svc-ai-gateway, svc-transcription) with documented justification. |
| **Milestone** | 2026-06-09 (PAST DUE as of 2026-06-24) Enable DCT in CI with unsigned image allowlist |
| **Status** | Open (Past Due) <!-- TODO(et): verify whether DCT shipped in CI; if so, mark Closed with commit ref. --> |
| **Responsible Party** | Platform Administrator |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-004 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 5.3 |
| **Description** | Two containers retain elevated Linux kernel capabilities beyond the default set. svc-detection requires SYS_ADMIN, SYS_PTRACE, SYS_RESOURCE for eBPF kernel tracing. Vault requires IPC_LOCK to prevent secret material from being swapped to disk. |
| **Risk Level** | Medium |
| **NIST 800-53 Control** | AC-6 (Least Privilege), SC-39 (Process Isolation) |
| **Affected Components** | svc-detection (SYS_ADMIN, SYS_PTRACE, SYS_RESOURCE), Vault (IPC_LOCK) |
| **Compensating Controls** | svc-detection uses `cap_drop: ALL` then adds only required capabilities (SYS_ADMIN, SYS_PTRACE, SYS_RESOURCE). Vault adds only IPC_LOCK to protect unsealed secrets from memory swap. All other containers have no additional capabilities. |
| **Remediation Plan** | No remediation possible without disabling core security functionality. svc-detection requires SYS_ADMIN for eBPF. Vault requires IPC_LOCK per vendor security guidance. |
| **Milestone** | Accepted Risk, permanent |
| **Status** | Accepted Risk |
| **Responsible Party** | Platform Administrator |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-005 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 5.25 |
| **Description** | Two containers do not have the `no-new-privileges` security option set: svc-detection and svc-ai-gateway. svc-detection requires privilege capabilities for eBPF. svc-ai-gateway is a standalone container not managed by Compose. |
| **Risk Level** | Medium |
| **NIST 800-53 Control** | AC-6 (Least Privilege), CM-6 (Configuration Settings) |
| **Affected Components** | svc-detection, svc-ai-gateway |
| **Compensating Controls** | svc-detection uses `cap_drop: ALL` with explicit minimum `cap_add`. svc-ai-gateway memory usage monitored by Datadog (typically under 200MB). All other 12 of 19 Compose-managed containers enforce `no-new-privileges: true`. |
| **Remediation Plan** | Migrate svc-ai-gateway to Docker Compose management with `no-new-privileges: true` and resource limits. svc-detection exemption is permanent (eBPF requires privilege escalation path). |
| **Milestone** | 2026-06-09 (PAST DUE as of 2026-06-24) Migrate svc-ai-gateway to Compose with hardening |
| **Status** | Open (Past Due) <!-- TODO(et): verify svc-ai-gateway migration status. --> |
| **Responsible Party** | Platform Administrator |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-006 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 5.31 |
| **Description** | Docker socket (`/var/run/docker.sock`) is mounted inside two containers: svc-detection and svc-monitor. This grants these containers the ability to interact with the Docker API. |
| **Risk Level** | Medium |
| **NIST 800-53 Control** | AC-3 (Access Enforcement), CM-7 (Least Functionality) |
| **Affected Components** | svc-detection, svc-monitor |
| **Compensating Controls** | Socket mounted read-only (`:ro`) on both containers. `no-new-privileges` set on svc-monitor. svc-detection uses `cap_drop: ALL` with minimum capabilities. Both are trusted security/monitoring agents, not application workloads. svc-detection monitors Docker API access patterns. |
| **Remediation Plan** | No remediation possible without disabling monitoring. svc-detection requires socket access for container metadata correlation with syscall events. svc-monitor requires socket access for container autodiscovery and metrics collection. Both are core security functions. |
| **Milestone** | Accepted Risk, permanent |
| **Status** | Accepted Risk |
| **Responsible Party** | Platform Administrator |

#### Low Findings, Host Auditing (5 findings)

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-007 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 1.1, 1.5, 1.6, 1.7, 1.8, 1.9 |
| **Description** | Host-level audit configuration findings: (1.1) No separate partition for `/var/lib/docker`. (1.5-1.9) No `auditd` rules for Docker daemon, `/var/lib/docker`, `/etc/docker`, `docker.service`, or `docker.socket`. |
| **Risk Level** | Low |
| **NIST 800-53 Control** | AU-2 (Event Logging), AU-12 (Audit Record Generation), SC-4 (Information in Shared System Resources) |
| **Affected Components** | `alpha-node` host OS |
| **Compensating Controls** | svc-detection (eBPF) provides syscall-level monitoring of all processes including the Docker daemon, covering the same detection surface as `auditd` with lower overhead on the 8GB memory-constrained host. svc-detection events route to Datadog via svc-detection-router. Disk usage monitored with alerts at 80% threshold. Log rotation configured on all containers (10MB x 3 files). |
| **Remediation Plan** | Evaluate adding targeted `auditd` rules for Docker paths if memory headroom increases (upgrade to 16GB VPS). Separate partition requires data migration and downtime, not justified at current utilization (<30%). |
| **Milestone** | 2026-06-09, Re-evaluate if host is upgraded to 16GB |
| **Status** | Accepted Risk |
| **Responsible Party** | Platform Administrator |

#### Low Findings, Daemon Configuration (6 findings)

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-008 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 2.1, 2.11, 2.12, 2.14, 2.15, 2.18 |
| **Description** | Docker daemon configuration findings: (2.1) Inter-container communication not disabled on default bridge. (2.11) No Docker authorization plugin. (2.12) No daemon-level centralized logging driver. (2.14) Live restore not enabled. (2.15) Userland proxy not disabled. (2.18) `no-new-privileges` not set daemon-wide. |
| **Risk Level** | Low |
| **NIST 800-53 Control** | CM-6 (Configuration Settings), CM-7 (Least Functionality), AU-6 (Audit Record Review) |
| **Affected Components** | Docker daemon on `alpha-node` |
| **Compensating Controls** | (2.1) All services use a dedicated bridge network, not `docker0`; svc-detection monitors cross-container traffic. (2.11) Single-admin host with SSH key-only access via zero-trust tunnel; svc-detection detects unauthorized `docker exec`. (2.12) Datadog agent collects all container logs centrally (15-day retention). (2.14) `restart: unless-stopped` policy on all containers; Compose manages lifecycle. (2.15) Network traffic monitored; zero-trust tunnel provides primary ingress. (2.18) `no-new-privileges` applied per-container on 12 of 13 Compose services. |
| **Remediation Plan** | These daemon-level settings either conflict with operational requirements (ICC needed for service mesh, live-restore conflicts with Compose orchestration) or are effectively mitigated by per-container controls. No action planned. |
| **Milestone** | Accepted Risk, permanent |
| **Status** | Accepted Risk |
| **Responsible Party** | Platform Administrator |

#### Low Findings, Container Images (1 finding)

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-009 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 4.6 |
| **Description** | Upstream container images do not include Dockerfile-level `HEALTHCHECK` instructions. CIS check evaluates the image metadata, not runtime configuration. |
| **Risk Level** | Low |
| **NIST 800-53 Control** | SI-6 (Security and Privacy Function Verification) |
| **Affected Components** | All upstream images (svc-tunnel, svc-automation, svc-llm, svc-db, svc-detection, svc-detection-router, svc-transcription, svc-secrets, svc-identity) |
| **Compensating Controls** | Runtime healthchecks configured in `docker-compose.yaml` for all services with appropriate intervals, timeouts, and retry thresholds. Datadog tracks container health status and alerts on unhealthy transitions. |
| **Remediation Plan** | No action. Runtime healthchecks are functionally equivalent and more flexible than Dockerfile `HEALTHCHECK` directives. Building custom images solely to add a `HEALTHCHECK` line creates unnecessary maintenance burden. |
| **Milestone** | Accepted Risk, permanent |
| **Status** | Accepted Risk |
| **Responsible Party** | Platform Administrator |

#### Low Findings, Container Runtime (12 findings)

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-010 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 5.2 |
| **Description** | SELinux security labels not set on containers. |
| **Risk Level** | Low |
| **NIST 800-53 Control** | AC-3 (Access Enforcement) |
| **Affected Components** | svc-ai-gateway (standalone) |
| **Compensating Controls** | Host OS (Ubuntu 24.04) uses AppArmor, not SELinux. CIS check 5.1 (AppArmor) passes. SELinux and AppArmor are mutually exclusive Linux Security Modules. |
| **Remediation Plan** | No action. AppArmor is the appropriate mandatory access control for this platform. |
| **Milestone** | Accepted Risk, permanent |
| **Status** | Accepted Risk |
| **Responsible Party** | Platform Administrator |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-011 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 5.5 |
| **Description** | Sensitive host directory `/proc` mounted in svc-monitor container. |
| **Risk Level** | Low |
| **NIST 800-53 Control** | CM-7 (Least Functionality), AC-3 (Access Enforcement) |
| **Affected Components** | svc-monitor |
| **Compensating Controls** | `/proc` mounted read-only. `no-new-privileges` set. svc-detection monitors all `/proc` access patterns. |
| **Remediation Plan** | No action. Process agent requires `/proc` for process-level metrics. This is the vendor-recommended deployment configuration. |
| **Milestone** | Accepted Risk, permanent |
| **Status** | Accepted Risk |
| **Responsible Party** | Platform Administrator |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-012 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 5.6 |
| **Description** | SSH daemon detected inside svc-monitor container image. |
| **Risk Level** | Low |
| **NIST 800-53 Control** | CM-7 (Least Functionality) |
| **Affected Components** | svc-monitor |
| **Compensating Controls** | No SSH ports exposed outside the container. Container runs on isolated bridge network. svc-detection detects unauthorized SSH connections. |
| **Remediation Plan** | No action. SSHD is bundled in the upstream vendor image for remote diagnostics; it is not exposed. |
| **Milestone** | Accepted Risk, permanent |
| **Status** | Accepted Risk |
| **Responsible Party** | Platform Administrator |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-013 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 5.9 |
| **Description** | svc-tunnel container uses host network namespace (`network_mode: host`). |
| **Risk Level** | Low |
| **NIST 800-53 Control** | SC-7 (Boundary Protection), SC-39 (Process Isolation) |
| **Affected Components** | svc-tunnel |
| **Compensating Controls** | Read-only root filesystem. `no-new-privileges` set. Resource limits applied. Falco monitors all network connections. Tunnel only routes pre-configured hostnames to specific localhost ports. |
| **Remediation Plan** | No action. Zero-trust tunnel requires host networking to forward traffic to localhost-bound services (svc-automation on , SSH on :22). |
| **Milestone** | Accepted Risk, permanent |
| **Status** | Accepted Risk |
| **Responsible Party** | Platform Administrator |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-014 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 5.10, 5.11, 5.28 |
| **Description** | svc-ai-gateway (standalone) lacks memory limits, CPU priority settings, and PIDs cgroup limit. CIS 5.11 also flags all Compose containers for using `NanoCpus` (hard CPU limits) instead of `CpuShares` (relative priority). |
| **Risk Level** | Low |
| **NIST 800-53 Control** | SC-6 (Resource Availability), SC-24 (Fail in Known State) |
| **Affected Components** | svc-ai-gateway (5.10, 5.28); all containers (5.11, CpuShares) |
| **Compensating Controls** | All Compose-managed containers have hard CPU limits (`deploy.resources.limits.cpus`), memory limits, and PIDs limits. Host memory monitored with alerts at 85%. svc-ai-gateway typically uses <200MB. |
| **Remediation Plan** | Migrate svc-ai-gateway to Docker Compose with full resource constraints (memory, CPU, PIDs limits). CpuShares finding for Compose containers is accepted, `NanoCpus` is a stricter control than relative priority weighting. |
| **Milestone** | 2026-06-09 (PAST DUE as of 2026-06-24) Migrate svc-ai-gateway to Compose (same as POAM-005) |
| **Status** | Open (Past Due) <!-- TODO(et): verify svc-ai-gateway resource constraints status. --> |
| **Responsible Party** | Platform Administrator |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-015 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 5.12 |
| **Description** | Container root filesystems not mounted as read-only for 9 containers. Only svc-tunnel and svc-detection-router have read-only rootfs. |
| **Risk Level** | Low |
| **NIST 800-53 Control** | CM-5 (Access Restrictions for Change), SI-7 (Software, Firmware, and Information Integrity) |
| **Affected Components** | svc-detection, svc-automation, svc-identity, svc-monitor, svc-db, svc-llm, svc-secrets, svc-transcription, svc-ai-gateway |
| **Compensating Controls** | Volume mounts scoped to specific paths. Falco monitors file writes outside designated directories. `no-new-privileges` prevents rootfs modification escalation. |
| **Remediation Plan** | Evaluate adding `read_only: true` with targeted `tmpfs` mounts for containers that only need temporary write access (svc-identity, svc-automation). svc-db, svc-secrets, svc-llm, and svc-transcription require writable rootfs for WAL, runtime state, and model loading. |
| **Milestone** | 2026-09-08, Test read-only rootfs on svc-identity and svc-automation |
| **Status** | Open |
| **Responsible Party** | Platform Administrator |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-016 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 5.13 |
| **Description** | Container port bindings use `0.0.0.0` instead of binding to a specific host interface (e.g., `127.0.0.1`). |
| **Risk Level** | Low |
| **NIST 800-53 Control** | SC-7 (Boundary Protection) |
| **Affected Components** | svc-automation, svc-identity, svc-llm, svc-transcription, svc-ai-gateway |
| **Compensating Controls** | DigitalOcean Cloud Firewall restricts inbound traffic at the network layer. Zero-trust tunnel is the only public ingress path (no direct port exposure to internet). Host-level UFW rules provide defense-in-depth. |
| **Remediation Plan** | Bind service ports to `127.0.0.1` for containers only accessed via localhost or the zero-trust tunnel. Evaluate impact on container-to-container communication over the bridge network. |
| **Milestone** | 2026-09-08, Test interface binding on svc-automation and svc-identity |
| **Status** | Open |
| **Responsible Party** | Platform Administrator |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-017 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 5.14 |
| **Description** | Containers use `restart: unless-stopped` instead of `on-failure:5` restart policy. |
| **Risk Level** | Low |
| **NIST 800-53 Control** | SC-24 (Fail in Known State), SC-6 (Resource Availability) |
| **Affected Components** | All Compose-managed containers, svc-ai-gateway |
| **Compensating Controls** | PIDs limits set on all Compose containers (64-512), preventing fork bombs. Datadog tracks container restart counts with alerts on excessive restarts (>3 in 5 minutes). |
| **Remediation Plan** | No action. `unless-stopped` provides better availability on a single-node deployment. CIS recommendation of `on-failure:5` is designed for multi-node orchestrators where failed containers should be rescheduled, not restarted indefinitely. PIDs limits prevent the fork-bomb scenario that limited retries address. |
| **Milestone** | Accepted Risk, permanent |
| **Status** | Accepted Risk |
| **Responsible Party** | Platform Administrator |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-018 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 5.15 |
| **Description** | svc-monitor shares the host PID namespace (`pid: host`). |
| **Risk Level** | Low |
| **NIST 800-53 Control** | SC-39 (Process Isolation), CM-7 (Least Functionality) |
| **Affected Components** | svc-monitor |
| **Compensating Controls** | `no-new-privileges` set. Memory and PIDs limits applied. Falco monitors all process operations. Agent has read-only access to host processes (monitoring only). |
| **Remediation Plan** | No action. Process agent requires `pid: host` for process-level metrics collection. This is the vendor-required deployment configuration. |
| **Milestone** | Accepted Risk, permanent |
| **Status** | Accepted Risk |
| **Responsible Party** | Platform Administrator |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-019 |
| **Finding Source** | CIS Docker Bench |
| **Finding ID** | CIS 5.26 |
| **Description** | svc-llm and svc-event-shipper containers lack runtime healthchecks. |
| **Risk Level** | Low |
| **NIST 800-53 Control** | SI-6 (Security and Privacy Function Verification) |
| **Affected Components** | svc-llm, svc-event-shipper |
| **Compensating Controls** | Datadog monitors container status and restart counts for both services. Upstream workflows that consume svc-llm have built-in timeout and retry logic. svc-event-shipper health is inferred from log flow continuity. |
| **Remediation Plan** | Add a basic healthcheck using the svc-llm API endpoint once endpoint reliability during model loading is confirmed. Add a healthcheck to svc-event-shipper based on log output or process liveness. |
| **Milestone** | 2026-06-09 (PAST DUE as of 2026-06-24) Add healthchecks to svc-llm and svc-event-shipper |
| **Status** | Open (Past Due) <!-- TODO(et): verify svc-llm and svc-event-shipper healthcheck status. --> |
| **Responsible Party** | Platform Administrator |

### Source 2: Checkov / Checkov Static Analysis (3 Findings)

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-020 |
| **Finding Source** | Checkov |
| **Finding ID** | CKV_TF_1, CKV_TF_2 |
| **Description** | Terraform modules not pinned to commit hash (CKV_TF_1) or version tag (CKV_TF_2). Checkov flags absence of module source pinning. |
| **Risk Level** | Low |
| **NIST 800-53 Control** | CM-2 (Baseline Configuration), SA-10 (Developer Configuration Management) |
| **Affected Components** | Terraform IaC (`terraform/cloud-infrastructure/`) |
| **Compensating Controls** | Infrastructure does not use external Terraform modules, all resources are defined inline. Checks are skipped in `.checkov.yaml` with documented justification. IaC changes go through PR pipeline (format, validate, TFLint, Checkov, OPA/Conftest, plan review) before merge. |
| **Remediation Plan** | No action. Findings are not applicable to current IaC architecture. If external modules are adopted in the future, pinning will be enforced. |
| **Milestone** | Accepted Risk, permanent (not applicable) |
| **Status** | Accepted Risk |
| **Responsible Party** | Platform Administrator |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-021 |
| **Finding Source** | Checkov |
| **Finding ID** | CKV-CLOUD-004 |
| **Description** | DigitalOcean Cloud Firewall allows SSH (port 22) from `0.0.0.0/0`. IaC scanner flags unrestricted SSH ingress as a DigitalOcean specific check. |
| **Risk Level** | Low |
| **NIST 800-53 Control** | SC-7 (Boundary Protection), AC-17 (Remote Access) |
| **Affected Components** | DigitalOcean Cloud Firewall, `alpha-node` VPS |
| **Compensating Controls** | SSH access is gated behind a zero-trust tunnel with ed25519 key authentication. Direct SSH from the public internet is blocked by the tunnel architecture, the firewall rule exists for tunnel-to-host forwarding. svc-gateway (Teleport) provides session recording and JIT access control for all SSH sessions. |
| **Remediation Plan** | No action. The firewall rule is intentionally broad because the zero-trust tunnel handles authentication and authorization. Restricting to specific IPs would break the tunnel architecture. |
| **Milestone** | Accepted Risk, permanent (architectural requirement) |
| **Status** | Accepted Risk |
| **Responsible Party** | Platform Administrator |

### Source 3: Falco Runtime Detection (0 Active Findings)

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-022 |
| **Finding Source** | Falco Runtime Detection |
| **Finding ID** | FALCO-BASELINE |
| **Description** | Runtime detection baseline established with 8 custom rules covering per-container monitoring. No critical or high-severity runtime violations detected during baseline period. Ongoing monitoring active. |
| **Risk Level** | Informational |
| **NIST 800-53 Control** | SI-4 (System Monitoring), IR-4 (Incident Handling) |
| **Affected Components** | All containers on `alpha-node` |
| **Compensating Controls** | svc-detection (eBPF) provides syscall-level monitoring. 8 custom rules monitor sensitive file access, process execution, network connections, and capability usage per container. Events route to Datadog via svc-detection-router for alerting and correlation. |
| **Remediation Plan** | Continue monitoring. Tune rules quarterly based on false positive analysis. Expand rule coverage as new services are added. |
| **Milestone** | 2026-06-09 (PAST DUE as of 2026-06-24) First quarterly rule review |
| **Status** | Closed (baseline established, monitoring active) <!-- TODO(et): confirm quarterly rule review was executed on or near 2026-06-09; if not, reopen and reschedule. --> |
| **Responsible Party** | Platform Administrator |

### Source 4: Risk Assessment - Mitigate Treatment Items (5 Findings)

Per POLICY_RISK_MANAGEMENT.md Section 3.3, risks with "Mitigate" treatment require POA&M entries with specific remediation actions.

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-023 |
| **Finding Source** | Risk Assessment (RA-2026-001) |
| **Finding ID** | R-10 |
| **Description** | Accidental Secret Exposure - secrets injected as environment variables are accessible to any process inside a container. A debug command, misconfigured log level, or core dump could expose credentials to logs or monitoring streams. Highest residual risk in the assessment (score: 10, Moderate). |
| **Risk Level** | High (inherent: 15) / Medium (residual: 10) |
| **NIST 800-53 Control** | SC-28 (Protection of Information at Rest), IA-5 (Authenticator Management) |
| **Affected Components** | All containers with secrets in environment variables (svc-automation, svc-db, svc-identity, svc-secrets) |
| **Current Controls** | External secrets manager (never hardcoded); Gitleaks in CI; log rotation (10MB x 3); .gitignore for sensitive files; env var validation (existence checks only) |
| **Remediation Plan** | 1. Transition from env-var secrets to mounted tmpfs files. 2. Deploy log scrubbing rules in Fluentd to redact patterns matching API keys and tokens. 3. Add automated secret scanning to container runtime logs. 4. Establish credential rotation runbook with 24-hour rotation SLA after suspected exposure. |
| **Milestone** | 2026-05-11 (PAST DUE as of 2026-06-24) Implement tmpfs-mounted secrets for svc-automation and svc-db |
| **Status** | Open (Past Due) <!-- TODO(et): verify whether tmpfs-mounted secrets shipped for svc-automation and svc-db. --> |
| **Responsible Party** | System Owner |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-024 |
| **Finding Source** | Risk Assessment (RA-2026-001) |
| **Finding ID** | R-04 |
| **Description** | Webhook Exploitation - the automation platform accepts webhook payloads through the zero-trust tunnel. A crafted payload could exploit a deserialization or injection flaw to achieve remote code execution inside the automation container. |
| **Risk Level** | Medium (inherent: 12) / Medium (residual: 8) |
| **NIST 800-53 Control** | SI-10 (Information Input Validation), SC-7 (Boundary Protection) |
| **Affected Components** | svc-automation, svc-tunnel |
| **Current Controls** | Webhook authentication tokens; input validation in workflow logic; svc-detection monitors for shell spawns; no-new-privileges on container |
| **Remediation Plan** | 1. Deploy webhook payload schema validation at the tunnel layer. 2. Add WAF rules at Cloudflare for webhook endpoints. 3. Restrict svc-automation network egress to required destinations only. 4. Implement webhook request signing with HMAC verification. |
| **Milestone** | 2026-06-11 (PAST DUE as of 2026-06-24) Deploy webhook schema validation and egress allowlisting |
| **Status** | Open (Past Due) <!-- TODO(et): verify webhook schema validation and egress allowlist status. --> |
| **Responsible Party** | System Owner |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-025 |
| **Finding Source** | Risk Assessment (RA-2026-001) |
| **Finding ID** | R-14 |
| **Description** | Data Loss - database volumes and secrets engine data exist on a single VPS with no automated off-site replication. A simultaneous disk failure and backup corruption would result in permanent data loss. |
| **Risk Level** | Medium (inherent: 10) / Medium (residual: 8) |
| **NIST 800-53 Control** | CP-9 (System Backup), CP-6 (Alternate Storage Site) |
| **Affected Components** | svc-db (db-data-volume), svc-secrets (secrets engine data), configuration files |
| **Current Controls** | PostgreSQL backup scripts (local backup volume); secrets stored in external manager; IaC for config rebuild; no automated off-site replication |
| **Remediation Plan** | 1. Implement automated daily database backups to encrypted object storage (off-VPS). 2. Add backup integrity verification (restore testing) on monthly schedule. 3. Document RPO/RTO targets. 4. Implement volume snapshot scheduling at DigitalOcean level. |
| **Milestone** | 2026-05-11 (PAST DUE as of 2026-06-24) Automated off-site backup with integrity verification |
| **Status** | Open (Past Due) <!-- TODO(et): verify automated off-site backup status. --> |
| **Responsible Party** | System Owner |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-026 |
| **Finding Source** | Risk Assessment (RA-2026-001) |
| **Finding ID** | R-12 |
| **Description** | DigitalOcean Outage - all 19 services run on a single VPS in a single region. A prolonged regional outage would render the entire platform unavailable with no automatic failover. |
| **Risk Level** | Medium (inherent: 8) / Low (residual: 6) |
| **NIST 800-53 Control** | CP-7 (Alternate Processing Site), CP-2 (Contingency Plan) |
| **Affected Components** | All services on alpha-node |
| **Current Controls** | Datadog alerts on host downtime; documented recovery procedures; IaC enables rapid redeployment |
| **Remediation Plan** | 1. Document warm-standby deployment procedure for alternate region using IaC. 2. Pre-stage encrypted database backups in a second region. 3. Define and test RTO targets (current estimated RTO: 2-4 hours). |
| **Milestone** | 2026-06-11 (PAST DUE as of 2026-06-24) Documented warm-standby procedure with tested RTO |
| **Status** | Open (Past Due) <!-- TODO(et): verify warm-standby documentation and RTO test status. --> |
| **Responsible Party** | System Owner |

---

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-027 |
| **Finding Source** | Risk Assessment (RA-2026-001) |
| **Finding ID** | R-16 |
| **Description** | POA&M Remediation Failure - CIS Docker Bench scan identified 96 WARN findings with 29 documented compensating controls. Drift from the remediation schedule erodes compliance posture. |
| **Risk Level** | Medium (inherent: 9) / Low (residual: 6) |
| **NIST 800-53 Control** | CA-5 (Plan of Action and Milestones), CA-7 (Continuous Monitoring) |
| **Affected Components** | All POA&M items, compliance posture |
| **Current Controls** | CIS Risk Register with documented compensating controls; 90-day review cycle; POA&M tracking |
| **Remediation Plan** | 1. Automate CIS Docker Bench scans on weekly schedule with delta reporting. 2. Prioritize top 10 WARN findings by risk score. 3. Integrate POA&M tracking into automation platform with due-date alerts. 4. Conduct focused compensating control review every 90 days. |
| **Milestone** | 2026-06-11 (PAST DUE as of 2026-06-24) Automated weekly CIS scans with delta reporting |
| **Status** | Open (Past Due) <!-- TODO(et): verify automated weekly CIS scan status. --> |
| **Responsible Party** | System Owner |

---

### Source 5: Phase 17 Squire Subsystem (10 Findings)

> **Key Point:** Phase 17 added the Squire autonomous SOC analyst. Six red-team cases executed 2026-04-23 surfaced 1 HIGH PII bypass which was remediated in-session by pre_graph_pii.py (commit 3e47524). Four additional follow-up items are OPEN. Full evidence in `REDTEAM_RESULTS.md`, `GUARDRAILS_CONFIGURATION.md`, and `AI_SUPPLY_CHAIN_REGISTER.md`.

#### POA&M-P17 Phase 17 cluster (compact register)

| POAM ID | Description | Severity | Owner | Due | Status | Evidence |
|---------|-------------|----------|-------|-----|--------|----------|
| POAM-P17-01 | NeMo input rail did not catch raw SSN in `/alert` payload; pre-graph scanner required. Pre_graph_pii.py added 2026-04-23, commit 3e47524. Regex SSN plus Luhn CC plus email plus US phone. 12 unit tests. | HIGH | System Owner | 2026-04-23 | CLOSED | `REDTEAM_RESULTS.md` Finding 1 (BYPASSED pre, CLOSED post); `builds/squire/src/squire/pre_graph_pii.py` |
| POAM-P17-02 | IGNORE-PREVIOUS severity flip attempt; graph classifier held. Regression test added to CI. | MED | System Owner | 2026-04-23 | CLOSED | `REDTEAM_RESULTS.md` Finding 2 (RESISTED) |
| POAM-P17-03 | Role hijack attempt via UnguardedBot persona; graph classifier held. Regression test added. | MED | System Owner | 2026-04-23 | CLOSED | `REDTEAM_RESULTS.md` Finding 3 (RESISTED) |
| POAM-P17-04 | Non-Luhn CC pass-through is expected behavior (not true PII); follow-up confirmed Luhn-valid CC is blocked. Regression test added. | LOW | System Owner | 2026-04-23 | CLOSED | `REDTEAM_RESULTS.md` Finding 4 |
| POAM-P17-05 | Benign framing severity flip attempt; graph classifier held. Regression test added. | MED | System Owner | 2026-04-23 | CLOSED | `REDTEAM_RESULTS.md` Finding 5 (RESISTED) |
| POAM-P17-06 | Drill framing severity flip attempt; graph classifier held. Regression test added. | MED | System Owner | 2026-04-23 | CLOSED | `REDTEAM_RESULTS.md` Finding 6 (RESISTED) |
| POAM-P17-07 | Lakera Guard rail deferred. Blocked on free-tier re-evaluation. Current rail coverage is NeMo plus pre-graph scanner. | LOW | Operator | 2026-Q3 | OPEN | `GUARDRAILS_CONFIGURATION.md` deferred rails section |
| POAM-P17-08 | PolicyAI self-check path held in degraded mode pending the next provider-access rotation cycle. Critique node still gates draft and enforces severity consistency. | LOW | Operator | 2026-Q2 (closes 2026-06-30, less than a week remaining as of 2026-06-24) | OPEN <!-- TODO(et): confirm PolicyAI rotation status before Q2 closes. --> | `SQUIRE_MODEL_CARD.md` limitations section |
| POAM-P17-09 | OpenClaw agent LLM auth not yet configured. Deferred to 17-07 follow-up. Squire currently calls Anthropic direct, not via OpenClaw gateway. | LOW | Operator | 2026-Q3 | OPEN | Plan 17-07 |
| POAM-P17-10 | AI supply chain register TBDs: Langfuse v3 exact commit pinning, NeMo Guardrails upgrade cadence, pgvector extension provenance. | LOW | System Owner | 2026-06-22 (PAST DUE as of 2026-06-24) | OPEN (Past Due) <!-- TODO(et): close supply-chain TBDs or extend milestone. --> | `AI_SUPPLY_CHAIN_REGISTER.md` |
| POAM-P17-11 | Novel injection patterns (YAML-framed role-hijack, structured key-value directives) can bypass NeMo presidio input rail because presidio is PII-centric, not behavioral. Critique consistency override and actions.yml rewrite provide defense-in-depth. Expand rail pre-check for directive patterns; add regression cases in 17-11 cycle 2. | MED | System Owner | 2026-Q3 | OPEN | `SQUIRE_THREAT_MODEL.md` section 2.2 AML.T0051 |
| POAM-P17-12 | International phone formats and non-Luhn-checked CC patterns can false-negative against US-only pre-graph regex. NeMo output rail at 0.85 threshold is the last-chance net. Expand pre-graph scanner to E.164 international phone and secondary structural CC checks. | MED | System Owner | 2026-Q3 | OPEN | `SQUIRE_THREAT_MODEL.md` section 2.5 AML.T0041 |
| POAM-P17-13 | Tavily enrichment results are untrusted text; a poisoned index entry could inject directives at the enrichment merge point. Critique consistency check is the sole behavioral override. Red-team cycle 2 will execute attack tree leaf A.3.a to quantify. | MED | Security Eng | 2026-Q3 | OPEN | `SQUIRE_THREAT_MODEL.md` section 2.2, `ATTACK_TREE_AI_PIPELINE.md` A.3.a |
| POAM-P17-14 | Supply chain attestation gap: several AI_SUPPLY_CHAIN_REGISTER entries lack reproducible-build attestation or upstream signing-key pinning. Zero-day in a pinned transitive dependency remains accepted residual until SBOM + runtime attestation is in place. | MED | System Owner | 2026-Q4 | OPEN | `SQUIRE_THREAT_MODEL.md` section 2.6 AML.T0010, `AI_SUPPLY_CHAIN_REGISTER.md` |
| POAM-P17-15 | Red-team cycle 2 returned HTTP 500 on 3 of 14 cases (08, 16, 18) when concurrency 5 hit the Anthropic 30k input-tokens-per-minute + 8k output-tokens-per-minute cap on Fable 5. The Ollama fallback in llm_backend cannot reach `svc-ollama` because that service lives on the `net-ai` internal docker network with no reachable route from `net-core`. Failure was availability-class, not integrity; no severity drift occurred because the graph exited before rendering. Remediation: (a) cap red-team runner default concurrency to 2 and add a per-case token pre-check; (b) wire the llm_backend Ollama path to use the docker bridge IP or dual-attach `svc-ollama` to `net-core`; (c) evaluate Anthropic rate-tier lift if bursty load pattern persists. Acceptance rationale: demo-scope availability is non-critical, and the failure mode is loud (5xx) rather than silent severity drift. | MED | System Owner | 2026-Q3 | OPEN | `REDTEAM_RESULTS.md` Finding 7 (cycle 2 cases 08, 16, 18) |

#### Phase 17 POAM severity distribution

```
Phase 17 POAM severity (15 entries)
┌─────────────────────────────────────────────┐
│ █                                    HIGH   │  1
│ █████████                            MED    │  9
│ █████                                LOW    │  5
└─────────────────────────────────────────────┘

Phase 17 POAM status (15 entries)
┌─────────────────────────────────────────────┐
│ ██████                               CLOSED │  6
│ █████████                            OPEN   │  9
└─────────────────────────────────────────────┘
```

```mermaid
pie title Phase 17 POAM by severity
    "HIGH" : 1
    "MED" : 9
    "LOW" : 5
```

---

## 3. Risk Acceptance Summary

The following findings have been formally accepted with documented business justification and compensating controls. Each acceptance is reviewed on a 90-day cycle.

| POA&M ID | Finding ID | Risk Level | Business Justification | Compensating Control Summary |
|----------|------------|------------|----------------------|------------------------------|
| POAM-001 | CIS 2.8 | Medium | User namespace remapping breaks volume permissions for svc-db (uid 999) and svc-detection (requires real root for eBPF). Enabling requires per-container UID mapping that is not yet mature in Compose. | `no-new-privileges`, `cap_drop: ALL`, AppArmor profiles |
| POAM-002 | CIS 4.1 | Medium | Five containers use official upstream images that require root (svc-db for file ownership, svc-secrets for IPC_LOCK, svc-monitor for host monitoring, svc-llm/svc-transcription for model management). Cannot override without custom Dockerfiles. | `no-new-privileges`, resource limits (CPU/memory/PIDs), runtime detection monitoring |
| POAM-004 | CIS 5.3 | Medium | svc-detection requires SYS_ADMIN/SYS_PTRACE/SYS_RESOURCE for eBPF kernel tracing, this IS the security monitoring tool. Vault requires IPC_LOCK to protect unsealed secrets from memory swap. | svc-detection: `cap_drop: ALL` + explicit minimum `cap_add`; svc-secrets: `cap_add: IPC_LOCK` only. AppArmor profiles active. |
| POAM-006 | CIS 5.31 | Medium | Docker socket access required by svc-detection (container metadata correlation) and svc-monitor (container autodiscovery). Both are trusted security/monitoring agents. | Read-only socket mount (`:ro`), `no-new-privileges` on svc-monitor, `cap_drop: ALL` on svc-detection |
| POAM-007 | CIS 1.1, 1.5-1.9 | Low | No `auditd` on memory-constrained 8GB host. No separate Docker partition on single-disk DigitalOcean VPS. | eBPF runtime detection covers same surface as `auditd`. Disk monitoring at 80% threshold. |
| POAM-008 | CIS 2.1, 2.11, 2.12, 2.14, 2.15, 2.18 | Low | Daemon-level settings conflict with operational requirements or are effectively superseded by per-container controls. | Dedicated bridge network, SSH key + tunnel access, centralized log collection, per-container `no-new-privileges` |
| POAM-009 | CIS 4.6 | Low | Upstream images lack Dockerfile `HEALTHCHECK`; runtime healthchecks in Compose are functionally equivalent. | Runtime healthchecks in `docker-compose.yaml`, Datadog health tracking |
| POAM-010 | CIS 5.2 | Low | Ubuntu 24.04 uses AppArmor, not SELinux. Mutually exclusive LSMs. | AppArmor active (CIS 5.1 PASS), eBPF runtime detection |
| POAM-011 | CIS 5.5 | Low | svc-monitor requires `/proc` for process metrics (vendor requirement). | Read-only mount, `no-new-privileges`, runtime detection of `/proc` access |
| POAM-012 | CIS 5.6 | Low | SSHD bundled in svc-monitor upstream image, not exposed externally. | No exposed SSH ports, isolated bridge network, runtime detection |
| POAM-013 | CIS 5.9 | Low | svc-tunnel requires host networking to forward traffic to localhost services. | Read-only rootfs, `no-new-privileges`, resource limits, preconfigured hostname routing only |
| POAM-017 | CIS 5.14 | Low | `unless-stopped` provides better single-node availability than `on-failure:5`. PIDs limits prevent fork bombs. | PIDs limits (64-512), restart count monitoring with alerting |
| POAM-018 | CIS 5.15 | Low | svc-monitor requires `pid: host` for process-level metrics (vendor requirement). | `no-new-privileges`, resource limits, runtime detection, read-only access |
| POAM-020 | CKV_TF_1, CKV_TF_2 | Low | No external Terraform modules in use. Checks not applicable. | PR pipeline with 7-step validation (format, init, validate, TFLint, Checkov, plan, OPA) |
| POAM-021 | CKV-CLOUD-004 | Low | SSH `0.0.0.0/0` is intentional, zero-trust tunnel handles auth. Restricting IPs breaks tunnel architecture. | Zero-trust tunnel, ed25519 key auth, session recording via svc-gateway, JIT access control |

**Total accepted risks:** 15 (4 Medium, 11 Low)
**Total with active remediation plans:** 11 (POAM-003, POAM-005, POAM-014, POAM-015, POAM-016, POAM-019, POAM-023, POAM-024, POAM-025, POAM-026, POAM-027)

---

## 4. Remediation Timeline

```
2026-03-11 Today (POA&M created, baseline established)
   |
   | Q2 2026, Phase 1 Remediation
   | =========================================
   |
   | POAM-003 [============================] Enable Docker Content Trust in CI
   |      Target: 2026-06-09        with unsigned image allowlist
   |
   | POAM-005 [============================] Migrate svc-ai-gateway to Compose
   |      Target: 2026-06-09        with no-new-privileges + limits
   |
   | POAM-014 [============================] Add resource constraints to
   |      Target: 2026-06-09        svc-ai-gateway via Compose
   |
   | POAM-019 [============================] Add healthcheck to svc-llm
   |      Target: 2026-06-09        container
   |
   | POAM-022 [============================] First quarterly detection rule
   |      Target: 2026-06-09        review and tuning
   |
2026-06-09 90-Day Review #1 (all findings re-assessed)
   |
   | Q3 2026, Phase 2 Remediation
   | =========================================
   |
   | POAM-015 [============================] Test read-only rootfs on
   |      Target: 2026-09-08        svc-identity and svc-automation
   |
   | POAM-016 [============================] Test 127.0.0.1 port binding
   |      Target: 2026-09-08        on svc-automation and svc-identity
   |
2026-09-08 90-Day Review #2
   |
2026-12-07 90-Day Review #3 (annual assessment)
```

### Milestone Summary

| Target Date | POA&M IDs | Description |
|-------------|-----------|-------------|
| 2026-06-09 | POAM-003, POAM-005, POAM-014, POAM-019 | Q2 hardening: DCT in CI, svc-ai-gateway Compose migration, svc-llm healthcheck |
| 2026-06-09 | POAM-022 | First quarterly runtime detection rule review |
| 2026-06-09 | ALL | 90-day review of all accepted risks |
| 2026-09-08 | POAM-015, POAM-016 | Q3 hardening: read-only rootfs testing, port binding restriction |
| 2026-09-08 | ALL | 90-day review #2 |
| 2026-12-07 | ALL | Annual reassessment of full POA&M |

---

## 5. Review Schedule

This POA&M follows a 90-day review cycle aligned with NIST 800-53 CA-5 (Plan of Action and Milestones) requirements.

### Review Cycle

| Review # | Date | Scope | Deliverable |
|----------|------|-------|-------------|
| Baseline | 2026-03-11 | Initial POA&M creation | This document (v1.0) |
| Review 1 | 2026-06-09 | Full reassessment, Q2 remediation verification | Updated POA&M (v1.1) |
| Review 2 | 2026-09-08 | Full reassessment, Q3 remediation verification | Updated POA&M (v1.2) |
| Review 3 | 2026-12-07 | Annual assessment, risk acceptance revalidation | Updated POA&M (v2.0) |
| Review 4 | 2027-03-08 | Full reassessment | Updated POA&M (v2.1) |

### Review Procedure

1. **Re-run assessments:** Execute CIS Docker Bench scan, verify Checkov CI results, review runtime detection alert history.
2. **Update findings:** Close remediated items, update status of in-progress items, add any new findings.
3. **Revalidate accepted risks:** Confirm compensating controls remain effective. Verify business justification is still valid. Assess whether technology changes enable remediation (e.g., upstream non-root images released).
4. **Update remediation timeline:** Adjust milestones based on progress and priority changes.
5. **Sign-off:** Platform Administrator reviews and approves updated POA&M.

### Triggering Events (Unscheduled Review)

The POA&M must be reviewed outside the 90-day cycle when any of the following occur:

- A security incident involving any component listed in this POA&M
- A new High or Critical finding from any assessment source
- A significant architectural change (e.g., migration to Kubernetes, new DigitalOcean)
- Addition of new services to the container stack
- Changes to upstream images that affect accepted risk justifications
- Regulatory or compliance requirement changes

---

## 6. NIST 800-53 Control Mapping Summary

The following NIST SP 800-53 Rev. 5 controls are referenced across POA&M findings.

| Control ID | Control Name | POA&M References | Status |
|------------|--------------|------------------|--------|
| AC-3 | Access Enforcement | POAM-006, POAM-010 | Compensating controls in place |
| AC-6 | Least Privilege | POAM-001, POAM-002, POAM-004, POAM-005 | Compensating controls in place |
| AC-17 | Remote Access | POAM-021 | Compensating controls in place |
| AU-2 | Event Logging | POAM-007 | Compensating controls in place |
| AU-6 | Audit Record Review | POAM-008 | Compensating controls in place |
| AU-12 | Audit Record Generation | POAM-007 | Compensating controls in place |
| CM-2 | Baseline Configuration | POAM-020 | Not applicable |
| CM-5 | Access Restrictions for Change | POAM-015 | Open, remediation Q3 2026 |
| CM-6 | Configuration Settings | POAM-001, POAM-002, POAM-005, POAM-008 | Compensating controls in place |
| CM-7 | Least Functionality | POAM-006, POAM-008, POAM-011, POAM-012, POAM-018 | Compensating controls in place |
| CM-14 | Signed Components | POAM-003 | Open, remediation Q2 2026 |
| IR-4 | Incident Handling | POAM-022 | Monitoring active |
| SA-10 | Developer Configuration Management | POAM-020 | Not applicable |
| SC-4 | Information in Shared Resources | POAM-007 | Compensating controls in place |
| SC-6 | Resource Availability | POAM-014, POAM-017 | Open (POAM-014) / Accepted (POAM-017) |
| SC-7 | Boundary Protection | POAM-013, POAM-016, POAM-021 | Open (POAM-016) / Accepted (others) |
| SC-39 | Process Isolation | POAM-001, POAM-004, POAM-013, POAM-018 | Compensating controls in place |
| SI-4 | System Monitoring | POAM-022 | Monitoring active |
| SI-6 | Security Function Verification | POAM-009, POAM-019 | Accepted (POAM-009) / Open (POAM-019) |
| SI-7 | Software/Firmware Integrity | POAM-003, POAM-015 | Open, remediation planned |
| SC-24 | Fail in Known State | POAM-014, POAM-017 | Compensating controls in place |

---

## 7. Document Control

| Field | Value |
|-------|-------|
| **Document Title** | Plan of Action and Milestones (POA&M) |
| **System** | Organization Security Operations Platform |
| **Version** | 1.3 |
| **Created** | 2026-03-11 |
| **Last Updated** | 2026-06-24 |
| **Next Review** | 2026-07-24 |
| **Author** | Platform Administrator |
| **Approver** | System Owner |
| **Classification** | Internal Use Only |

### Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-11 | Platform Administrator | Initial POA&M creation. 32 findings documented from 3 sources. 15 formally accepted, 6 open for remediation, 1 closed (baseline). |
| 1.1 | 2026-03-11 | Platform Administrator | Added 5 findings from Risk Assessment mitigate treatments (POAM-023 through POAM-027). Fixed SI-17 to SC-24 (invalid NIST control). Total: 37 findings from 4 sources. |
| 1.2 | 2026-04-24 | Platform Administrator | Added Phase 17 Squire cluster: POAM-P17-01 through P17-15. Cycle 1 red-team findings closed; cycle 2 cluster opened (rails, threat-model residuals, rate-limit infra). |
| 1.3 | 2026-06-24 | Platform Administrator | Audit refresh: embedding provider and code path corrections propagated from REDTEAM_RESULTS and FRAMEWORK_CROSSWALK_SQUIRE. Past-due flags applied to all milestones that have crossed their target date without an owner status update. MCP01-001 and MCP08-001 in POAM_MCP_2025.md confirmed Closed 2026-05-31. |

### Sub-POAMs (control-family-specific)

- [POAM_MCP_2025.md](POAM_MCP_2025.md) - OWASP MCP Top 10 2025 beta v0.1 gaps for `scripts/grc/grc_mcp_server.py` (agent_id: fastmcp_grc_corpus). Tracks MCP01 (Token Mismanagement and Secret Exposure), MCP06 (Intent Flow Subversion), MCP07 (Insufficient Authentication and Authorization, Accepted Risk), MCP08 (Lack of Audit and Telemetry).

### Related Documents

| Document | Location | Relationship |
|----------|----------|-------------|
| CIS Docker Benchmark Risk Register | `docs/grc/CIS_RISK_REGISTER.md` | Source findings for CIS Docker Bench items |
| IAM & RBAC Role Map | `docs/grc/IAM_RBAC_ROLE_MAP.md` | Access control architecture referenced in compensating controls |
| IAM Access Review Process | `docs/grc/IAM_ACCESS_REVIEW.md` | JIT access workflow and review procedures |
| Security & Deploy Pipeline | `.github/workflows/security.yml` | CI/CD pipeline implementing Trivy, Gitleaks, Semgrep, Cosign, SBOM |
| Terraform PR Validation | `.github/workflows/terraform-pr.yml` | IaC compliance scanning pipeline |
| IaC Scanner Configuration | `terraform/cloud-infrastructure/.checkov.yaml` | Accepted risk skip list for IaC scanning |
