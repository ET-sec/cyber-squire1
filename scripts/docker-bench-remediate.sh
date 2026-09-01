#!/usr/bin/env bash
# docker-bench-remediate.sh -- One-shot remediation report for CIS Docker Bench findings
# Run after applying compose changes to document what was fixed and what was not.
#
# This script is documentation only -- the actual fixes are in docker-compose.yaml.
# The unfixable findings are documented in docs/CIS_RISK_REGISTER.md.
set -euo pipefail

cat << 'REPORT'
=== Docker Bench CIS Remediation Report ===
Date: 2026-03-11
Baseline scan: bench-2026-03-11T15-39-48Z.log

REMEDIATED (docker-compose.yaml changes):
  [5.10] Memory limits
    - Added deploy.resources.limits.memory to ALL containers
    - db:1G  n8n:2G  ollama:3G  whisper:1G  vault:512M  keycloak:1G
    - datadog:512M  falco:512M(already)  falcosidekick:256M(already)  tunnel:256M

  [5.11] CPU limits
    - Added deploy.resources.limits.cpus to ALL containers
    - db:1.00  n8n:2.00  ollama:2.00  whisper:1.00  vault:0.50  keycloak:1.00
    - datadog:0.50  falco:0.50(already)  falcosidekick:0.25(already)  tunnel:0.25

  [5.12] Read-only rootfs (where safe)
    - tunnel-cyber-squire: read_only:true + tmpfs:/tmp
    - falcosidekick: read_only:true + tmpfs:/tmp
    - NOT applied to: db, n8n, ollama, whisper, vault, keycloak, datadog, falco
      (these need writable rootfs for data, logs, or runtime files)

  [5.14] Restart policy
    - Changed ALL containers from restart:always to restart:unless-stopped
    - unless-stopped prevents infinite restart loops while maintaining resilience

  [5.25] No-new-privileges
    - Added security_opt: no-new-privileges:true to ALL containers EXCEPT:
    - Falco: needs SYS_ADMIN capability escalation for eBPF (accepted risk)

  [5.26] Health checks at runtime
    - Added healthcheck to: n8n (wget /healthz), falco (pid check),
      falcosidekick (wget /ping), datadog (agent health), tunnel (pgrep)
    - Already had healthcheck: db, whisper, vault, keycloak

  [5.28] PIDs limit
    - Added pids_limit to ALL containers:
    - db:256  n8n:512  ollama:256  whisper:256  vault:128  keycloak:256
    - datadog:256  falco:128  falcosidekick:64  tunnel:64

  [General] Logging limits
    - Added json-file logging with max-size:10m max-file:3 to ALL containers
    - Prevents unbounded log growth consuming disk

NOT REMEDIATED (see docs/CIS_RISK_REGISTER.md for full justification):
  [1.1]  Separate partition for containers -- single-disk cloud VM (DigitalOcean at time of remediation)
  [1.5-1.9] Docker daemon audit rules -- requires host-level auditd, not compose scope
  [2.1]  Network traffic between containers -- services need inter-container communication
  [2.8]  User namespace support -- breaks volume permissions for PostgreSQL, n8n
  [2.11] Docker client authorization -- single-admin host, SSH access only
  [2.12] Centralized logging -- Datadog agent collects all container logs already
  [2.14] Live restore -- conflicts with compose orchestration model
  [2.15] Userland proxy -- required for port forwarding to work correctly
  [2.18] Default no-new-privileges -- set per-container instead of daemon-wide
  [4.1]  Non-root container user -- upstream images (postgres, datadog) require root
  [4.5]  Content trust -- breaks normal image pulls; compensated by Cosign in CI
  [4.6]  HEALTHCHECK in Dockerfile -- upstream image responsibility; compose healthchecks compensate
  [5.2]  SELinux -- Ubuntu uses AppArmor, not SELinux (passes 5.1 AppArmor check)
  [5.3]  Capabilities restriction -- Falco needs SYS_ADMIN for eBPF monitoring
  [5.6]  SSH in containers -- Datadog agent design includes sshd for remote checks
  [5.9]  Host network namespace -- tunnel requires host networking for port forwarding
  [5.13] Wildcard IP binding -- n8n/OpenClaw need local access; firewall restricts external
  [5.15] Host PID namespace -- Datadog process agent requires pid:host for monitoring
  [5.31] Docker socket mounted -- Falco and Datadog need socket for container awareness
REPORT

echo ""
echo "Remediation applied: $(date -u)"
echo "Run docker-bench-weekly.sh again to compare before/after counts."
