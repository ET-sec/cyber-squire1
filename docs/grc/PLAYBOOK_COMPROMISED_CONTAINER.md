# Incident Response Playbook: Compromised Container

**Document ID:** IR-PLAY-001
**Version:** 1.0
**Last Updated:** 2026-03-11
**Owner:** Incident Commander
**Classification:** Internal Use Only
**NIST 800-53 Controls:** IR-4 (Incident Handling), IR-5 (Incident Monitoring), IR-6 (Incident Reporting), SI-4 (Information System Monitoring), SI-7 (Software, Firmware, and Information Integrity)

---

### Incident Response Process Flow

```
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                    COMPROMISED CONTAINER RESPONSE WORKFLOW                  │
 └─────────────────────────────────────────────────────────────────────────────┘

 ┌───────────────────────┐
 │  DETECTION TRIGGER    │
 │  - Falco eBPF alert   │
 │  - Datadog anomaly    │
 │  - Manual report      │
 └──────────┬────────────┘
            │
            v
 ┌───────────────────────┐     ┌──────────────────────────────┐
 │  TRIAGE & CONFIRM     │     │  Assign severity:            │
 │  Verify alert is real │────>│  SEV-1/2: Immediate contain  │
 │  Check processes, net │     │  SEV-3/4: Gather more data   │
 └──────────┬────────────┘     └──────────────────────────────┘
            │
            v
 ┌───────────────────────┐
 │  Is container still   │
 │  running?             │
 └──────┬───────┬────────┘
    YES │       │ NO
        v       v
 ┌────────────┐ ┌────────────────────────┐
 │ Capture    │ │ Check available logs:  │
 │ live state:│ │ - docker logs          │
 │ - ps auxww │ │ - Falco event logs     │
 │ - ss -tulnp│ │ - Datadog metrics      │
 │ - docker   │ │ - Fluentd archives     │
 │   inspect  │ │ - Docker daemon journal│
 └─────┬──────┘ └───────────┬────────────┘
       │                    │
       └────────┬───────────┘
                │
                v
 ┌───────────────────────┐
 │  ISOLATE CONTAINER    │
 │  1. Disconnect from   │
 │     internal-net      │
 │  2. Apply iptables    │
 │     DROP rules        │
 │  3. Pause container   │
 │     (freeze state)    │
 └──────────┬────────────┘
            │
            v
 ┌───────────────────────┐
 │  Is lateral movement  │
 │  detected?            │
 └──────┬───────┬────────┘
    YES │       │ NO
        v       v
 ┌────────────────────┐  ┌───────────────────────┐
 │ ISOLATE NETWORK:   │  │ Continue single-      │
 │ - Scan ALL other   │  │ container investigation│
 │   containers for   │  │ and proceed to        │
 │   IOCs             │  │ evidence preservation │
 │ - Disconnect any   │  └───────────┬───────────┘
 │   additional       │              │
 │   compromised      │              │
 │   containers       │              │
 │ - Rotate all       │              │
 │   shared secrets   │              │
 └────────┬───────────┘              │
          │                          │
          └────────┬─────────────────┘
                   │
                   v
 ┌───────────────────────┐
 │  PRESERVE EVIDENCE    │
 │  1. Export filesystem  │
 │     (docker export)   │
 │  2. Save inspect JSON │
 │  3. Export all logs    │
 │  4. Capture Falco +   │
 │     Fluentd logs      │
 │  5. Host-level capture│
 │  6. SHA-256 manifest  │
 │  7. Transfer off-node │
 └──────────┬────────────┘
            │
            v
 ┌───────────────────────┐
 │  Can container be     │
 │  rebuilt from a clean │
 │  image?               │
 └──────┬───────┬────────┘
    YES │       │ NO
        v       v
 ┌────────────────────┐  ┌───────────────────────┐
 │ REPLACE:           │  │ DEEPER FORENSICS:     │
 │ 1. Stop + remove   │  │ 1. Analyze exported   │
 │    container       │  │    filesystem diff    │
 │ 2. Pull fresh image│  │ 2. Reverse-engineer   │
 │ 3. Trivy scan new  │  │    attack vector     │
 │    image for CVEs  │  │ 3. Check supply chain │
 │ 4. Harden config:  │  │    (dependencies,    │
 │    - no-new-privs  │  │    base image)       │
 │    - non-root user │  │ 4. Build custom clean │
 │    - read-only fs  │  │    image if needed   │
 └────────┬───────────┘  └───────────┬───────────┘
          │                          │
          └────────┬─────────────────┘
                   │
                   v
 ┌───────────────────────┐
 │  REMEDIATE            │
 │  1. Rotate ALL        │
 │     exposed secrets   │
 │  2. Update .env on    │
 │     alpha-node        │
 │  3. Rotate SSH keys   │
 │     if needed         │
 │  4. Patch vuln image  │
 │  5. Update detection  │
 │     rules             │
 └──────────┬────────────┘
            │
            v
 ┌───────────────────────┐
 │  RESTORE SERVICE      │
 │  1. docker compose up │
 │  2. Verify healthcheck│
 │  3. Confirm network   │
 │     connectivity      │
 │  4. Test end-to-end   │
 │     functionality     │
 │  5. Verify Falco      │
 │     monitoring active │
 │  6. Verify Datadog    │
 │     metrics flowing   │
 │  7. Remove iptables   │
 │     containment rules │
 └──────────┬────────────┘
            │
            v
 ┌───────────────────────┐
 │  LESSONS LEARNED      │
 │  (within 72 hours)    │
 │  1. Complete incident │
 │     timeline          │
 │  2. Root cause        │
 │     analysis          │
 │  3. Post-incident     │
 │     report            │
 │  4. Update detection  │
 │     rules + policies  │
 │  5. Schedule review   │
 │     meeting (5 days)  │
 │  6. Update this       │
 │     playbook          │
 └───────────────────────┘
```

---

## 1. Purpose

This playbook provides step-by-step procedures for responding to a compromised container within the Organization infrastructure. A compromised container may exhibit unauthorized processes, reverse shells, cryptominers, data exfiltration, or other indicators of compromise (IOCs).

---

## 2. Scope

Applies to all 19 containers running on the `alpha-node` VPS (4vCPU/8GB) connected via the `internal-net` bridge network. Includes but is not limited to: `svc-db`, `svc-automation`, `svc-llm`, `svc-transcription`, `svc-secrets`, `svc-identity`, `svc-gateway`, `svc-monitor`, `svc-detection`, `svc-detection-router`, `Fluentd`, `svc-event-shipper`, `svc-tunnel`, `svc-ai-gateway`, and the Phase 17 Squire stack (`svc-squire`, `svc-nemo`, `svc-langfuse-web`, `svc-langfuse-worker`, `svc-langfuse-clickhouse`, `svc-langfuse-redis`, `svc-teleport-event-handler`).

---

## 3. Severity Classification

| Severity | Criteria |
|----------|----------|
| **SEV-1 (Critical)** | `svc-db`, `svc-secrets`, `svc-identity`, or `svc-gateway` compromised; evidence of data exfiltration or lateral movement |
| **SEV-2 (High)** | `svc-automation`, `svc-tunnel`, or `svc-ai-gateway` compromised; no confirmed data exfiltration |
| **SEV-3 (Medium)** | Auxiliary service compromised (`svc-llm`, `svc-transcription`, `svc-monitor`); contained to single container |
| **SEV-4 (Low)** | Suspicious activity detected but not yet confirmed as compromise |

---

## 4. Detection Triggers

### 4.1 svc-detection (eBPF Runtime Security) Alerts

- [ ] `Terminal shell in container`: interactive shell spawned inside a running container
- [ ] `Unexpected outbound connection`: container initiating connections to unknown external IPs
- [ ] `Unexpected process spawned`: process not part of the container's expected process tree
- [ ] `Write below /etc`: unauthorized modification of system configuration files
- [ ] `Read sensitive file`: access to `/etc/shadow`, `/etc/passwd`, or credential files
- [ ] `Mkdir binary dirs`: creation of directories in `/bin`, `/sbin`, `/usr/bin`
- [ ] `Launch privileged container`: container running with elevated privileges
- [ ] `Bulk data archive`: `tar`, `zip`, `gzip` operations on large data sets (exfiltration indicator)
- [ ] `Vault unseal key access`: access to Vault unseal key material (critical severity, see `detections/sigma/infra/vault-unseal-key-access.yml`)

<!-- TODO(et): the current detections/sigma/infra/container-shell-spawn-restricted.yml allowlists shell-spawn alerts to PostgreSQL, Vault, Tunnel, Keycloak, Falco, OpenClaw. n8n (svc-automation) is NOT in that allowlist, so a shell spawned in n8n will not currently match. Either add n8n to the allowlist or adjust playbook references that assume the n8n shell-spawn fires this rule. -->
<!-- TODO(et): Sigma rule gaps to backfill: bulk-archive-creation.yml, unexpected-outbound-generic.yml, mkdir-binary-dirs.yml, launch-privileged-container.yml. -->


### 4.2 Monitoring Platform Alerts

- [ ] CPU spike in a container that should be idle or low-usage
- [ ] Anomalous network traffic volume from a specific container
- [ ] Container restart loop (crash-and-recover pattern)
- [ ] Memory usage spike inconsistent with workload

### 4.3 Manual / External Reports

- [ ] Abuse report from DigitalOcean
- [ ] Upstream vendor notification of compromised dependency
- [ ] Unusual output or behavior observed during routine operations

---

## 5. Response Procedures

### Phase 1: Identification and Triage (0-15 minutes)

**Objective:** Confirm the compromise and determine severity.

- [ ] **Step 1.1**: Acknowledge the alert in Datadog. Record the timestamp, alert name, affected container, and alert source.

- [ ] **Step 1.2**: Verify the alert is not a false positive. Check the container's expected behavior against the alert. Many production containers (Teleport, Fluentd, Falcosidekick) ship as distroless or read-only and do not have `ps`, `ss`, or `netstat` available. Use host-side equivalents as a fallback.
 ```bash
 # Check running processes from the host (works even for distroless containers)
 docker top <container_name>

 # Fallback inside the container (will fail silently on distroless images)
 docker exec <container_name> ps auxww 2>/dev/null || echo "(ps unavailable; container may be distroless)"

 # Check network connections from the host using nsenter (does not rely on container binaries)
 PID=$(docker inspect -f '{{.State.Pid}}' <container_name>)
 nsenter -t "$PID" -n ss -tulnp

 # Review recent container logs
 docker logs --since 30m <container_name>
 ```

- [ ] **Step 1.3**: Check svc-detection logs for correlated alerts:
 ```bash
 docker logs --since 1h svc-detection 2>&1 | grep -i "<container_name>"
 docker logs --since 1h svc-detection-router 2>&1 | grep -i "critical\|high\|warning"
 ```

- [ ] **Step 1.4**: Check Datadog container metrics for the affected container: CPU, memory, network I/O, and disk I/O anomalies.

- [ ] **Step 1.5**: Assign severity per Section 3. If SEV-1 or SEV-2, immediately proceed to containment. If SEV-3 or SEV-4, gather additional evidence before containment.

- [ ] **Step 1.6**: Open an incident ticket. Record:
 - Incident ID (format: `INC-YYYY-MM-DD-NNN`)
 - Detection source and timestamp
 - Affected container(s)
 - Assigned severity
 - Incident Commander name

### Phase 2: Containment (15-45 minutes)

**Objective:** Isolate the compromised container without destroying forensic evidence.

> **WARNING:** Do NOT run `docker rm`, `docker compose down`, or `docker stop` on the compromised container before evidence is preserved. Do NOT run `docker compose down` via `svc-tunnel`; doing so will kill the tunnel and lock you out.

- [ ] **Step 2.1**: Disconnect the compromised container from all networks to stop lateral movement:
 ```bash
 docker network disconnect internal-net <container_name>
 ```

- [ ] **Step 2.2**: If the container is making active outbound connections, apply iptables rules on the host to block its traffic:
 ```bash
 # Get the container's IP before disconnecting (if not already disconnected)
 docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container_name>

 # Block all outbound from that container IP
 iptables -I FORWARD -s <container_ip> -j DROP
 iptables -I FORWARD -d <container_ip> -j DROP
 ```

- [ ] **Step 2.3**: Pause the container to freeze its state (preserves memory, processes, filesystem):
 ```bash
 docker pause <container_name>
 ```

- [ ] **Step 2.4**: If the compromise involves `svc-tunnel` or `svc-gateway`, ensure you have direct SSH access to `alpha-node` before taking any action:
 ```bash
 # Verify direct SSH access works (not through the tunnel)
 ssh -o ConnectTimeout=5 root@10.100.1.10
 ```

- [ ] **Step 2.5**: If lateral movement is suspected, check all other containers for IOCs. Use `docker top` from the host because distroless containers (Teleport, Fluentd, Falcosidekick) do not ship with `ps`.
 ```bash
 # Use docker top from the host; works regardless of in-container binaries
 for c in $(docker ps --format '{{.Names}}'); do
  echo "=== $c ==="
  docker top "$c" 2>/dev/null | grep -v -E '(UID|PID)' | grep -v -E '(ps|grep|docker top)'
 done
 ```

- [ ] **Step 2.6**: Rotate any secrets the compromised container had access to. Check the compose environment for which secrets the container consumed:
 ```bash
 # List environment variables the container was started with (names only, NOT values)
 docker inspect <container_name> --format '{{range .Config.Env}}{{println .}}{{end}}' | cut -d= -f1
 ```

### Phase 3: Evidence Preservation (30-60 minutes)

**Objective:** Capture all forensic artifacts before eradication.

- [ ] **Step 3.1**: Export the full container filesystem:
 ```bash
 docker export <container_name> > /tmp/evidence_<container_name>_$(date +%Y%m%d_%H%M%S).tar
 ```

- [ ] **Step 3.2**: Save container metadata and configuration:
 ```bash
 docker inspect <container_name> > /tmp/evidence_<container_name>_inspect.json
 ```

- [ ] **Step 3.3**: Export all container logs:
 ```bash
 docker logs <container_name> > /tmp/evidence_<container_name>_logs.txt 2>&1
 ```

- [ ] **Step 3.4**: Capture svc-detection events for the incident window:
 ```bash
 docker logs --since 24h svc-detection > /tmp/evidence_detection_events.txt 2>&1
 docker logs --since 24h svc-detection-router > /tmp/evidence_detection_router.txt 2>&1
 ```

- [ ] **Step 3.5**: Capture Fluentd and svc-event-shipper logs:
 ```bash
 docker logs --since 24h Fluentd > /tmp/evidence_log_router.txt 2>&1
 docker logs --since 24h svc-event-shipper > /tmp/evidence_event_shipper.txt 2>&1
 ```

- [ ] **Step 3.6**: If `svc-gateway` session recordings exist for the compromise window, export them. Teleport ships as a distroless image; verify the exact subcommand for the deployed version before relying on this in front of an interviewer.
 ```bash
 # List recent sessions (Teleport v18+)
 docker exec svc-gateway tctl sessions ls
 # If the deployed version differs, alternatives include:
 # docker exec svc-gateway tctl get sessions
 ```

- [ ] **Step 3.7**: Capture host-level evidence:
 ```bash
 # Host process list
 ps auxww > /tmp/evidence_host_processes.txt

 # Host network connections
 ss -tulnp > /tmp/evidence_host_connections.txt

 # Docker daemon logs (use .service suffix on Ubuntu 24.04)
 journalctl -u docker.service --since "24 hours ago" > /tmp/evidence_docker_daemon.txt
 ```

- [ ] **Step 3.8**: Create a SHA-256 hash manifest of all evidence files:
 ```bash
 sha256sum /tmp/evidence_* > /tmp/evidence_manifest_sha256.txt
 ```

- [ ] **Step 3.9**: Transfer evidence to a secure off-node location (e.g., secure workstation or encrypted storage). Do NOT store evidence solely on the potentially compromised host.

### Phase 4: Eradication (45-90 minutes)

**Objective:** Remove the threat and rebuild from known-good state.

- [ ] **Step 4.1**: Stop and remove the compromised container:
 ```bash
 docker unpause <container_name> # If paused in Step 2.3
 docker stop <container_name>
 docker rm <container_name>
 ```

- [ ] **Step 4.2**: Remove the compromised image and pull a fresh, known-good image:
 ```bash
 docker rmi <image_name>:<tag>
 docker compose pull <service_name>
 ```

- [ ] **Step 4.3**: If the compromise vector was a vulnerable image, verify the new image against known CVEs:
 ```bash
 # Run a vulnerability scan on the new image (using CI/CD scanner or local tool)
 trivy image <image_name>:<tag>
 ```

- [ ] **Step 4.4**: Rotate ALL secrets the compromised container had access to:
 1. Identify all secrets from Step 2.6
 2. Generate new credentials in the secrets manager (Doppler is the source of truth: `doppler secrets set <KEY> "<new value>" --project coredirective-engine --config prd`)
 3. Update the compose `.env` file on `alpha-node` if a non-Doppler value is involved
 4. Update all consuming services

- [ ] **Step 4.5**: If SSH keys or gateway CA certificates are suspected compromised, rotate them. To rotate existing SSH host keys (not just fill gaps) the existing key files must be removed first; `ssh-keygen -A` only generates host keys that are missing.
 ```bash
 # Rotate SSH host keys (remove then regenerate)
 rm /etc/ssh/ssh_host_*
 ssh-keygen -A
 systemctl restart ssh

 # Rotate gateway CA (Teleport phased rotation: init, update_clients, update_servers, standby)
 docker exec svc-gateway tctl auth rotate --type=host
 ```

- [ ] **Step 4.6**: Review and harden the container's configuration. Reference CIS_RISK_REGISTER.md for accepted exceptions (e.g., `svc-falco` requires SYS_ADMIN and is excepted from no-new-privileges).
 - Ensure `no-new-privileges` security option is set
 - Verify the container runs as a non-root user where possible
 - Confirm read-only filesystem where applicable
 - Validate network policies restrict unnecessary inter-container communication

### Phase 5: Recovery (60-120 minutes)

**Objective:** Restore normal operations and verify integrity.

- [ ] **Step 5.1**: Redeploy the service using Docker Compose:
 ```bash
 docker compose up -d <service_name>
 ```

- [ ] **Step 5.2**: Verify the container starts and passes healthchecks:
 ```bash
 docker compose ps <service_name>
 docker inspect --format='{{.State.Health.Status}}' <container_name>
 ```

- [ ] **Step 5.3**: Verify the container is connected to `internal-net` and can communicate with required peers:
 ```bash
 docker network inspect internal-net --format '{{range .Containers}}{{.Name}} {{end}}'
 ```

- [ ] **Step 5.4**: Test service functionality end-to-end:
 - If `svc-db`: verify database connectivity and data integrity
 - If `svc-automation`: verify webhook endpoints respond and workflows execute
 - If `svc-tunnel`: verify `n8n.example-ops.com` resolves and proxies correctly
 - If `svc-gateway`: verify SSH sessions and session recording work

- [ ] **Step 5.5**: Confirm svc-detection is monitoring the new container. Falco emits structured events only when rules fire; a quiet log does not mean monitoring is off. Confirm rule registration instead.
 ```bash
 # Confirm rules are loaded
 docker exec svc-detection falco --list 2>&1 | head -5
 # Optional: review recent emitted events if any
 docker logs --since 5m svc-detection 2>&1 | grep "<container_name>"
 ```

- [ ] **Step 5.6**: Verify Datadog is receiving metrics from the new container.

- [ ] **Step 5.7**: Validate no lateral movement occurred by reviewing all other containers:
 ```bash
 # Check image digests match expected values
 docker images --digests --format "{{.Repository}}:{{.Tag}} {{.Digest}}"
 ```

- [ ] **Step 5.8**: Remove iptables rules added during containment:
 ```bash
 iptables -D FORWARD -s <container_ip> -j DROP
 iptables -D FORWARD -d <container_ip> -j DROP
 ```

### Phase 6: Post-Incident (Within 72 hours)

**Objective:** Document the incident, identify root cause, and improve defenses.

- [ ] **Step 6.1**: Complete the incident timeline:
 - When was the container first compromised (based on evidence)?
 - When was the compromise detected?
 - Detection-to-containment time (target: <15 minutes)
 - Containment-to-eradication time
 - Total incident duration

- [ ] **Step 6.2**: Identify root cause:
 - Vulnerable application code?
 - Unpatched container image?
 - Misconfigured permissions or network policy?
 - Compromised dependency (supply chain)?
 - Leaked credential that granted access?

- [ ] **Step 6.3**: Write a post-incident report containing:
 - Executive summary
 - Timeline of events
 - Impact assessment (data affected, services disrupted, duration)
 - Root cause analysis
 - Remediation actions taken
 - Lessons learned
 - Action items with owners and due dates

- [ ] **Step 6.4**: Update detection rules if the compromise was not caught by existing rules:
 ```bash
 # Review and update svc-detection custom rules
 # Add new rules to detect the specific attack pattern
 ```

- [ ] **Step 6.5**: Update infrastructure policies if a policy gap contributed to the compromise.

- [ ] **Step 6.6**: Schedule a post-incident review meeting within 5 business days.

- [ ] **Step 6.7**: Update this playbook with any lessons learned.

---

## 6. Communication Requirements

| Audience | When | Method | Content |
|----------|------|--------|---------|
| Incident Commander | Immediately on detection | Direct message / phone | Alert details, severity |
| System Owner | Within 15 minutes of confirmed compromise | Direct message / phone | Incident ID, affected service, containment status |
| DigitalOcean | If provider-level action needed | Support ticket | Abuse report response or resource isolation request |
| Affected users (if any) | Within 24 hours of confirmed data impact | Email from `admin@example-ops.com` | Nature of incident, impact, remediation steps |

---

## 7. Evidence Preservation Checklist

| Artifact | Location | Collected? |
|----------|----------|------------|
| Container filesystem export | `/tmp/evidence_<container>_*.tar` | [ ] |
| Container inspect JSON | `/tmp/evidence_<container>_inspect.json` | [ ] |
| Container logs | `/tmp/evidence_<container>_logs.txt` | [ ] |
| svc-detection event logs | `/tmp/evidence_detection_events.txt` | [ ] |
| svc-detection-router logs | `/tmp/evidence_detection_router.txt` | [ ] |
| Fluentd logs | `/tmp/evidence_log_router.txt` | [ ] |
| svc-event-shipper logs | `/tmp/evidence_event_shipper.txt` | [ ] |
| Teleport session recordings | Exported from gateway | [ ] |
| Host process list | `/tmp/evidence_host_processes.txt` | [ ] |
| Host network connections | `/tmp/evidence_host_connections.txt` | [ ] |
| Docker daemon logs | `/tmp/evidence_docker_daemon.txt` | [ ] |
| SHA-256 hash manifest | `/tmp/evidence_manifest_sha256.txt` | [ ] |
| Datadog dashboards | Screenshots / exported data | [ ] |

---

## 8. NIST 800-53 Control Mapping

| Control | Description | Playbook Phase |
|---------|-------------|----------------|
| IR-4 | Incident Handling | All phases |
| IR-4(1) | Automated Incident Handling Processes | Phase 1 (detection alerts) |
| IR-5 | Incident Monitoring | Phase 1 (svc-detection, Datadog) |
| IR-6 | Incident Reporting | Phase 6 (post-incident report) |
| IR-6(1) | Automated Reporting | Phase 1 (alert routing via svc-detection-router) |
| SI-4 | Information System Monitoring | Phase 1 (continuous monitoring) |
| SI-4(2) | Automated Tools for Real-Time Analysis | Phase 1 (eBPF-based detection) |
| SI-4(5) | System-Generated Alerts | Phase 1 (detection triggers) |
| SI-7 | Software, Firmware, and Information Integrity | Phase 4 (image verification) |
| AU-6 | Audit Review, Analysis, and Reporting | Phase 3 (evidence preservation) |
| AU-9 | Protection of Audit Information | Phase 3 (hash manifest) |
| SC-7 | Boundary Protection | Phase 2 (network isolation) |
| CP-10 | Information System Recovery | Phase 5 (service restoration) |

---

## 9. Quick Reference Card

**For use during an active incident, tear-off summary:**

```
1. CONFIRM:  Check svc-detection logs and container processes (use docker top for distroless)
2. ISOLATE:  docker network disconnect internal-net <container>
3. PAUSE:    docker pause <container>
4. EXPORT:   docker export <container> > /tmp/evidence_<container>.tar
5. ROTATE:   Rotate all secrets the container accessed (Doppler)
6. REMOVE:   docker stop and docker rm <container>
7. REBUILD:  docker compose pull <service> and docker compose up -d <service>
8. VERIFY:   Healthchecks, monitoring, detection coverage
9. REPORT:   Incident timeline and post-incident report within 72h
```

---

## When the incident involves Squire subsystem (Phase 17)

> **Key Point:** The Phase 17 Squire containers (svc-squire, svc-nemo, svc-langfuse-web, svc-langfuse-worker, svc-langfuse-clickhouse, svc-langfuse-redis) follow this parent playbook plus Squire-specific evidence capture. Langfuse trace data is high-value forensic evidence.

Standard container compromise response applies to all Squire containers. In addition, the responder:

1. Before container isolation, exports Langfuse trace IDs for the affected window (`ir_investigations` query, then Langfuse UI export).
2. Captures `ir_alerts`, `ir_chunks`, `ir_investigations`, `ir_rotation_events` table state before any container state change.
3. For svc-nemo compromise, treats the rail config (`/opt/platform/nemo-config`) as untrusted until rebuilt from git.
4. For svc-langfuse-clickhouse compromise, the trace data itself may be tampered; cross-check against SDK-side trace IDs captured by the Squire app log.
5. For svc-squire compromise, revokes all X-Squire-Tokens immediately (HITL_POLICY section 6).

Cross-reference: `PLAYBOOK_AI_INCIDENT.md` for AI-specific response; `AI_AUDIT_TRAIL_SPEC.md` for trace capture; `HITL_POLICY.md` for token revocation.

---

## Cross-References

| Document | Relationship |
|----------|-------------|
| [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) | System Security Plan with NIST 800-53 control mapping |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | Tracks findings and remediation milestones |
| [PLAYBOOK_AI_INCIDENT.md](PLAYBOOK_AI_INCIDENT.md) | AI-specific incident playbook including Squire section |
| [AI_AUDIT_TRAIL_SPEC.md](AI_AUDIT_TRAIL_SPEC.md) | Langfuse trace retention and replay |
| [README.md](README.md) | GRC library index and reading guide |
