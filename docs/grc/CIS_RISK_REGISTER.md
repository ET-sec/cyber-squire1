# CIS Docker Benchmark Risk Register

**Environment:** Organization Platform (DigitalOcean VPS alpha-node)
**Baseline Date:** 2026-03-11
**Last Scan:** 2026-03-11 (post-remediation)
**Next Review:** 2026-06-09 (90 days)

## Overview

This register documents all CIS Docker Bench for Security findings that cannot be remediated
in the current environment without breaking functionality. Each entry includes business
justification and compensating controls.

**Scan Summary (post-remediation):**
- PASS: 37 | WARN: 96 | INFO: 85 | NOTE: 10
- Compose-managed containers: 13 services hardened with resource limits, PIDs limits,
 no-new-privileges, healthchecks, log rotation, and read-only rootfs (where safe)
- AI gateway (standalone): not managed by compose, contributes residual WARNs

---

## Section 1: Host Configuration

### 1.1 - Ensure a separate partition for containers has been created

| Field | Value |
|-------|-------|
| **Finding ID** | 1.1 |
| **Section** | Host Configuration |
| **Result** | WARN |
| **Description** | Docker data should reside on a dedicated partition to prevent container disk usage from exhausting the root filesystem |
| **Business Justification** | DigitalOcean VPS uses a single 160GB disk. Repartitioning requires downtime and data migration. Current disk usage is under 30% with monitoring alerts at 80%. |
| **Compensating Control** | Datadog disk usage monitor (alert at 80% threshold). Log rotation configured on all containers (10MB x 3 files). Weekly cleanup of unused images via docker system prune. |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 1.5 - Ensure auditing is configured for the Docker daemon

| Field | Value |
|-------|-------|
| **Finding ID** | 1.5 |
| **Section** | Host Configuration |
| **Result** | WARN |
| **Description** | auditd rules should monitor the Docker daemon binary |
| **Business Justification** | auditd rules are host-level configuration, outside Docker Compose scope. Installing auditd adds overhead on a memory-constrained 8GB VPS. |
| **Compensating Control** | Falco (eBPF) provides syscall-level monitoring of all processes including dockerd. Runtime detection events route to Datadog via svc-detection-router. Covers the same detection surface as auditd with lower overhead. |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 1.6 - Ensure auditing is configured for /var/lib/docker

| Field | Value |
|-------|-------|
| **Finding ID** | 1.6 |
| **Section** | Host Configuration |
| **Result** | WARN |
| **Description** | auditd should monitor /var/lib/docker for unauthorized changes |
| **Business Justification** | Same as 1.5 -- auditd is host-level, not Docker Compose scope |
| **Compensating Control** | Runtime detection engine monitors file access patterns across all containers. Custom rules detect sensitive file reads and unauthorized writes. |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 1.7 - Ensure auditing is configured for /etc/docker

| Field | Value |
|-------|-------|
| **Finding ID** | 1.7 |
| **Section** | Host Configuration |
| **Result** | WARN |
| **Description** | auditd should monitor /etc/docker for configuration changes |
| **Business Justification** | Same as 1.5 -- auditd is host-level |
| **Compensating Control** | Runtime detection engine monitors /etc reads and writes. SSH access is the only administrative path (zero-trust tunnel + ed25519 key). |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 1.8 - Ensure auditing is configured for docker.service

| Field | Value |
|-------|-------|
| **Finding ID** | 1.8 |
| **Section** | Host Configuration |
| **Result** | WARN |
| **Description** | auditd should monitor the docker.service systemd unit |
| **Business Justification** | Same as 1.5 -- auditd is host-level |
| **Compensating Control** | Runtime detection engine detects systemd unit modifications. Datadog process agent monitors dockerd. |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 1.9 - Ensure auditing is configured for docker.socket

| Field | Value |
|-------|-------|
| **Finding ID** | 1.9 |
| **Section** | Host Configuration |
| **Result** | WARN |
| **Description** | auditd should monitor the docker.socket systemd unit |
| **Business Justification** | Same as 1.5 -- auditd is host-level |
| **Compensating Control** | Docker socket access monitored by Falco. Only Falco and the monitoring agent containers have socket access (read-only). |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

---

## Section 2: Docker Daemon Configuration

### 2.1 - Ensure network traffic is restricted between containers on the default bridge

| Field | Value |
|-------|-------|
| **Finding ID** | 2.1 |
| **Section** | Docker Daemon Configuration |
| **Result** | WARN |
| **Description** | Inter-container communication should be disabled on the default bridge |
| **Business Justification** | Services require inter-container communication: automation platform connects to PostgreSQL, svc-detection routes to svc-detection-router, monitoring agent autodiscovers containers. Disabling ICC breaks the entire stack. |
| **Compensating Control** | All services use a dedicated net-core bridge (not docker0). Runtime detection engine monitors all network connections between containers. No containers are exposed to the default bridge. |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 2.8 - Enable user namespace support

| Field | Value |
|-------|-------|
| **Finding ID** | 2.8 |
| **Section** | Docker Daemon Configuration |
| **Result** | WARN |
| **Description** | Docker should use user namespace remapping to isolate container root from host root |
| **Business Justification** | User namespace remapping breaks volume permissions for PostgreSQL (uid 999), svc-automation (uid 1000), and Falco (needs real root for eBPF). Enabling requires complex UID mapping for every volume. |
| **Compensating Control** | no-new-privileges set on all containers except svc-detection. Falco uses cap_drop ALL + explicit cap_add for minimum required capabilities. AppArmor profiles active. |
| **Risk Level** | Medium |
| **Review Date** | 2026-06-09 |

### 2.11 - Ensure that authorization for Docker client commands is enabled

| Field | Value |
|-------|-------|
| **Finding ID** | 2.11 |
| **Section** | Docker Daemon Configuration |
| **Result** | WARN |
| **Description** | Docker authorization plugin should restrict Docker API access |
| **Business Justification** | Single-admin host. Only root has Docker access. SSH access restricted to ed25519 key via zero-trust tunnel. Authorization plugin adds complexity with no additional security on a single-user system. |
| **Compensating Control** | SSH key-only access. Cloudflare zero-trust tunnel restricts network access. Runtime detection engine detects docker exec and unauthorized container operations. |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 2.12 - Ensure centralized and remote logging is configured

| Field | Value |
|-------|-------|
| **Finding ID** | 2.12 |
| **Section** | Docker Daemon Configuration |
| **Result** | WARN |
| **Description** | Docker daemon should use a centralized logging driver (syslog, splunk, etc.) |
| **Business Justification** | CIS Docker Bench checks for daemon-level log driver configuration. Containers use json-file driver with rotation limits. Logs are collected centrally by monitoring agent. |
| **Compensating Control** | Monitoring agent collects all container logs (DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL=true). Logs shipped to datadoghq.com for centralized analysis. 15-day retention on Datadog. |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 2.14 - Ensure live restore is Enabled

| Field | Value |
|-------|-------|
| **Finding ID** | 2.14 |
| **Section** | Docker Daemon Configuration |
| **Result** | WARN |
| **Description** | Docker live restore keeps containers running during daemon restart |
| **Business Justification** | Live restore conflicts with Docker Compose orchestration. Compose expects to manage container lifecycle. Enabling live-restore can cause orphaned containers and state inconsistency after daemon restart. |
| **Compensating Control** | All containers have restart:unless-stopped policy. Docker Compose handles service orchestration. Datadog monitors container uptime with alerts for service downtime. |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 2.15 - Ensure Userland Proxy is Disabled

| Field | Value |
|-------|-------|
| **Finding ID** | 2.15 |
| **Section** | Docker Daemon Configuration |
| **Result** | WARN |
| **Description** | Docker should use iptables hairpin NAT instead of userland proxy for port forwarding |
| **Business Justification** | Disabling userland proxy can break port forwarding in some network configurations. Current proxy overhead is minimal on 4-vCPU VPS. |
| **Compensating Control** | Network traffic monitored by Falco. Port bindings limited to required services only. Zero-trust tunnel provides primary ingress (not Docker port mapping). |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 2.18 - Ensure containers are restricted from acquiring new privileges

| Field | Value |
|-------|-------|
| **Finding ID** | 2.18 |
| **Section** | Docker Daemon Configuration |
| **Result** | WARN |
| **Description** | Docker daemon should set no-new-privileges by default for all containers |
| **Business Justification** | Setting daemon-wide no-new-privileges would break Falco (needs SYS_ADMIN for eBPF). Applied per-container instead of daemon-wide. |
| **Compensating Control** | no-new-privileges:true set explicitly on 12 of 13 compose-managed containers. Only svc-detection (Falco) exempted (requires capability escalation for eBPF kernel tracing). |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

---

## Section 4: Container Images and Build File

### 4.1 - Ensure a user for the container has been created

| Field | Value |
|-------|-------|
| **Finding ID** | 4.1 |
| **Section** | Container Images |
| **Result** | WARN |
| **Description** | Containers should not run as root |
| **Affected containers** | svc-monitor, svc-db, svc-llm, svc-secrets, svc-transcription |
| **Business Justification** | These are official upstream images that require root: PostgreSQL (file ownership), monitoring agent (host monitoring), secrets engine (IPC_LOCK), LLM engine (model management), transcription engine (model loading). Cannot override without custom Dockerfiles. |
| **Compensating Control** | no-new-privileges set on all affected containers. Resource limits (memory, CPU, PIDs) prevent resource abuse. Runtime detection engine monitors for privilege escalation attempts inside containers. |
| **Risk Level** | Medium |
| **Review Date** | 2026-06-09 |

### 4.5 - Ensure Content trust for Docker is Enabled

| Field | Value |
|-------|-------|
| **Finding ID** | 4.5 |
| **Section** | Container Images |
| **Result** | WARN |
| **Description** | DOCKER_CONTENT_TRUST should be set to 1 to verify image signatures |
| **Business Justification** | Many upstream images (Falco, svc-detection-router, AI gateway, transcription engine) do not publish Docker Content Trust signatures. Enabling breaks normal image pulls for unsigned images. |
| **Compensating Control** | CI pipeline includes container signature verification (soft-fail) for images that support it (Phase 6). CVE scanner scans all images for vulnerabilities. SBOMs generated for 5 key images. |
| **Risk Level** | Medium |
| **Review Date** | 2026-06-09 |

### 4.6 - Ensure HEALTHCHECK instructions have been added to the container image

| Field | Value |
|-------|-------|
| **Finding ID** | 4.6 |
| **Section** | Container Images |
| **Result** | WARN |
| **Description** | Dockerfile should include HEALTHCHECK instruction |
| **Affected images** | tunnel-agent, automation-engine, llm-engine, database-engine, detection-engine, detection-router, transcription-engine, secrets-engine, identity-engine |
| **Business Justification** | This checks the Dockerfile-level HEALTHCHECK, not runtime healthchecks. Upstream images don't include HEALTHCHECK directives. Building custom images just to add HEALTHCHECK adds maintenance burden. |
| **Compensating Control** | Runtime healthchecks configured in docker-compose.yaml for all services. Datadog monitors container health status. Unhealthy containers trigger alerts. |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

---

## Section 5: Container Runtime

### 5.2 - Ensure SELinux security options are set, if applicable

| Field | Value |
|-------|-------|
| **Finding ID** | 5.2 |
| **Section** | Container Runtime |
| **Result** | WARN |
| **Affected containers** | svc-ai-gateway (standalone) |
| **Description** | SELinux labels should be set on containers |
| **Business Justification** | Ubuntu 24.04 uses AppArmor, not SELinux. CIS check 5.1 (AppArmor) passes. SELinux and AppArmor are mutually exclusive LSMs. |
| **Compensating Control** | AppArmor profiles active (CIS 5.1 PASS). Runtime detection engine provides additional runtime security monitoring via eBPF. |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 5.3 - Ensure Linux Kernel Capabilities are restricted within containers

| Field | Value |
|-------|-------|
| **Finding ID** | 5.3 |
| **Section** | Container Runtime |
| **Result** | WARN |
| **Affected containers** | svc-detection (SYS_ADMIN, SYS_PTRACE, SYS_RESOURCE), Vault (IPC_LOCK) |
| **Description** | Containers should drop all capabilities and add only required ones |
| **Business Justification** | Falco requires SYS_ADMIN for eBPF kernel tracing, SYS_PTRACE for process inspection, SYS_RESOURCE for buffer allocation. The secrets engine requires IPC_LOCK to prevent memory from being swapped (protects unsealed secrets). |
| **Compensating Control** | Falco uses cap_drop: ALL then adds only required capabilities. The secrets engine adds only IPC_LOCK. All other containers have no additional capabilities. |
| **Risk Level** | Medium |
| **Review Date** | 2026-06-09 |

### 5.5 - Ensure sensitive host system directories are not mounted on containers

| Field | Value |
|-------|-------|
| **Finding ID** | 5.5 |
| **Section** | Container Runtime |
| **Result** | WARN |
| **Affected containers** | svc-monitor (/proc mounted) |
| **Description** | Host directories like /proc should not be mounted into containers |
| **Business Justification** | Datadog process agent requires /proc access for process-level metrics and container monitoring. This is the standard monitoring agent deployment pattern. |
| **Compensating Control** | /proc mounted read-only. no-new-privileges set. Runtime detection engine monitors all /proc access patterns. |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 5.6 - Ensure ssh is not run within containers

| Field | Value |
|-------|-------|
| **Finding ID** | 5.6 |
| **Section** | Container Runtime |
| **Result** | WARN |
| **Affected containers** | svc-monitor |
| **Description** | sshd should not run inside containers |
| **Business Justification** | Monitoring agent includes sshd as part of its standard image for remote diagnostics. It is not exposed outside the container. |
| **Compensating Control** | No ports exposed for SSH. Container runs on isolated net-core bridge. Runtime detection engine detects any unauthorized SSH connections. |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 5.9 - Ensure the host's network namespace is not shared

| Field | Value |
|-------|-------|
| **Finding ID** | 5.9 |
| **Section** | Container Runtime |
| **Result** | WARN |
| **Affected containers** | svc-tunnel |
| **Description** | Containers should not use host network namespace |
| **Business Justification** | Zero-trust tunnel requires host networking to forward traffic to localhost services (automation platform on , SSH on :22). Without host networking, the tunnel cannot reach host-bound services. |
| **Compensating Control** | Tunnel container is read-only rootfs. no-new-privileges set. Resource limits applied. Runtime detection engine monitors all network connections. Tunnel only routes pre-configured hostnames (automation.example-ops.com, ssh.example-ops.com). |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 5.10 - Ensure memory usage for container is limited

| Field | Value |
|-------|-------|
| **Finding ID** | 5.10 |
| **Section** | Container Runtime |
| **Result** | WARN |
| **Affected containers** | svc-ai-gateway (standalone) |
| **Description** | All containers should have memory limits |
| **Business Justification** | AI gateway is managed outside Docker Compose (standalone docker run). Memory limits are set on all compose-managed containers. |
| **Compensating Control** | Datadog monitors host memory usage. Alert triggers at 85% memory utilization. AI gateway memory usage is typically under 200MB. |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 5.11 - Ensure CPU priority is set appropriately on the container

| Field | Value |
|-------|-------|
| **Finding ID** | 5.11 |
| **Section** | Container Runtime |
| **Result** | WARN |
| **Affected containers** | All compose containers + svc-ai-gateway |
| **Description** | CpuShares should be set (not default 1024) for CPU priority weighting |
| **Business Justification** | CIS Docker Bench checks CpuShares (relative CPU priority), not NanoCpus (absolute CPU limit). Our containers use deploy.resources.limits.cpus which sets NanoCpus -- a stricter control than CpuShares. CpuShares is only meaningful under contention and is less useful than hard CPU limits. |
| **Compensating Control** | All compose containers have deploy.resources.limits.cpus set (hard CPU limits). NanoCpus verified at runtime. Datadog monitors CPU usage per container. |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 5.12 - Ensure the container's root filesystem is mounted as read only

| Field | Value |
|-------|-------|
| **Finding ID** | 5.12 |
| **Section** | Container Runtime |
| **Result** | WARN |
| **Affected containers** | svc-detection, svc-automation, svc-identity, monitoring agent, svc-db, svc-llm, svc-secrets, svc-transcription, svc-ai-gateway |
| **Description** | Container rootfs should be read-only to prevent runtime modifications |
| **Business Justification** | These containers require writable rootfs: PostgreSQL (WAL, temp files), svc-automation (workflow execution, temp), secrets engine (runtime state), identity provider (cache, temp), LLM engine (model loading), transcription engine (model cache), monitoring agent (agent state), svc-detection (eBPF maps). Tunnel and svc-detection-router ARE read-only. |
| **Compensating Control** | Volume mounts are scoped to specific paths. Runtime detection engine monitors file writes outside designated directories. no-new-privileges prevents rootfs modification escalation. |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 5.13 - Ensure incoming container traffic is bound to a specific host interface

| Field | Value |
|-------|-------|
| **Finding ID** | 5.13 |
| **Section** | Container Runtime |
| **Result** | WARN |
| **Affected containers** | svc-automation, svc-identity, svc-llm, svc-transcription, svc-ai-gateway |
| **Description** | Ports should bind to specific interface (e.g., 127.0.0.1) not 0.0.0.0 |
| **Business Justification** | Automation platform must be accessible from zero-trust tunnel (localhost) and internal network. Binding to 127.0.0.1 would prevent container-to-container communication on net-core bridge. DigitalOcean Cloud Firewall restricts external access. |
| **Compensating Control** | DigitalOcean Cloud Firewall restricts inbound traffic. Zero-trust tunnel is the only public ingress path. UFW rules on the VPS provide defense-in-depth. |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 5.14 - Ensure 'on-failure' container restart policy is set to '5'

| Field | Value |
|-------|-------|
| **Finding ID** | 5.14 |
| **Section** | Container Runtime |
| **Result** | WARN |
| **Affected containers** | All compose containers + svc-ai-gateway |
| **Description** | Restart policy should be on-failure with max retry count of 5 |
| **Business Justification** | CIS requires restart:on-failure:5. We use restart:unless-stopped which provides better availability -- services restart after any failure without a retry limit. For a single-node deployment, availability outweighs the fork-bomb prevention benefit of limited retries. PIDs limits prevent fork bombs. |
| **Compensating Control** | PIDs limits set on all compose containers (64-512). Datadog monitors container restart counts. Alert triggers on excessive restarts (>3 in 5 minutes). |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 5.15 - Ensure the host's process namespace is not shared

| Field | Value |
|-------|-------|
| **Finding ID** | 5.15 |
| **Section** | Container Runtime |
| **Result** | WARN |
| **Affected containers** | svc-monitor |
| **Description** | Containers should not share the host PID namespace |
| **Business Justification** | Datadog process agent requires pid:host to collect process-level metrics (CPU, memory, open files per process). This is the standard and required monitoring agent deployment configuration. |
| **Compensating Control** | no-new-privileges set. Memory and PIDs limits applied. Runtime detection engine monitors all process operations. Monitoring agent is read-only for host processes (monitoring only, no write access). |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 5.25 - Ensure the container is restricted from acquiring additional privileges

| Field | Value |
|-------|-------|
| **Finding ID** | 5.25 |
| **Section** | Container Runtime |
| **Result** | WARN |
| **Affected containers** | svc-detection, svc-ai-gateway |
| **Description** | All containers should have no-new-privileges security option |
| **Business Justification** | Falco requires privilege capabilities (SYS_ADMIN) for eBPF kernel tracing -- no-new-privileges would prevent this. AI gateway is standalone and not managed by compose. All other 12 compose containers have no-new-privileges set. |
| **Compensating Control** | Falco uses cap_drop:ALL then adds only minimum required capabilities. AppArmor set to unconfined only for svc-detection. Resource limits restrict blast radius. |
| **Risk Level** | Medium |
| **Review Date** | 2026-06-09 |

### 5.26 - Ensure container health is checked at runtime

| Field | Value |
|-------|-------|
| **Finding ID** | 5.26 |
| **Section** | Container Runtime |
| **Result** | WARN |
| **Affected containers** | svc-llm, svc-event-shipper |
| **Description** | All containers should have healthcheck configured |
| **Business Justification** | svc-llm (LLM engine) does not expose a health endpoint in its default configuration. Adding a healthcheck would require installing curl/wget in the LLM engine image or custom scripting. The API endpoint (http://localhost:<llm-port>) can be unreliable during model loading. svc-event-shipper is a log-forwarding sidecar with no built-in health endpoint. |
| **Compensating Control** | Datadog monitors container status and restart counts for both services. Automation workflows that use svc-llm have built-in timeout and retry logic. svc-event-shipper health is inferred from log flow continuity. |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 5.28 - Ensure PIDs cgroup limit is used

| Field | Value |
|-------|-------|
| **Finding ID** | 5.28 |
| **Section** | Container Runtime |
| **Result** | WARN |
| **Affected containers** | svc-ai-gateway (standalone) |
| **Description** | All containers should have PIDs limit to prevent fork bombs |
| **Business Justification** | AI gateway is managed outside Docker Compose. All compose-managed containers have PIDs limits set (verified at runtime). |
| **Compensating Control** | Host-level process monitoring via Datadog. Runtime detection engine detects unusual process spawning. AI gateway typically runs 2-3 processes. |
| **Risk Level** | Low |
| **Review Date** | 2026-06-09 |

### 5.31 - Ensure the Docker socket is not mounted inside any containers

| Field | Value |
|-------|-------|
| **Finding ID** | 5.31 |
| **Section** | Container Runtime |
| **Result** | WARN |
| **Affected containers** | svc-detection, svc-monitor |
| **Description** | Docker socket should not be mounted in containers |
| **Business Justification** | Falco needs Docker socket to correlate syscall events with container metadata (names, labels, images). Monitoring agent needs Docker socket for container autodiscovery and metrics. Both are security/monitoring tools that require this access by design. |
| **Compensating Control** | Socket mounted read-only (:ro) on both containers. no-new-privileges set on monitoring agent. Falco cap_drop:ALL with explicit minimum capabilities. These are trusted monitoring agents, not application containers. |
| **Risk Level** | Medium |
| **Review Date** | 2026-06-09 |

---

## Risk Summary

| Risk Level | Count | Findings |
|------------|-------|----------|
| **High** | 0 | -- |
| **Medium** | 4 | 2.8 (user namespace), 4.1 (root user), 4.5 (content trust), 5.3 (capabilities), 5.25 (no-new-privileges), 5.31 (docker socket) |
| **Low** | 25 | All remaining findings |

## Compensating Controls Cross-Reference

| Control | Findings Covered |
|---------|-----------------|
| **Runtime detection (eBPF) monitoring** | 1.5-1.9, 2.1, 5.2, 5.3, 5.5, 5.6, 5.9, 5.12, 5.13, 5.15, 5.25, 5.31 |
| **Datadog container monitoring** | 1.1, 2.12, 5.10, 5.11, 5.14, 5.15, 5.26, 5.28 |
| **no-new-privileges (per-container)** | 2.18, 4.1, 5.12, 5.25 |
| **Resource limits (CPU/mem/PIDs)** | 4.1, 5.10, 5.11, 5.14, 5.28 |
| **CI pipeline security (Trivy, Cosign, SBOM)** | 4.5, 4.6 |
| **Zero-trust tunnel (network isolation)** | 2.11, 5.9, 5.13 |
| **Read-only socket mounts** | 5.31 |
| **DigitalOcean Cloud Firewall** | 5.13 |

---

*This register feeds Phase 9 GRC documentation (POA&M). Review cycle: 90 days.*
*Last updated: 2026-03-11*
