# Incident Response Playbook: DDoS / Service Degradation

**Document ID:** IR-PLAY-003
**Version:** 1.0
**Last Updated:** 2026-03-11
**Owner:** Incident Commander
**Classification:** Internal Use Only
**NIST 800-53 Controls:** IR-4 (Incident Handling), IR-5 (Incident Monitoring), IR-6 (Incident Reporting), SC-5 (Denial of Service Protection), CP-10 (Information System Recovery)

---

### Incident Response Process Flow

```
 ┌──────────────────────┐
 │   ALERT TRIGGERED    │
 │  (Datadog/Cloudflare/ │
 │   Manual Detection)  │
 └──────────┬───────────┘
            │
            v
 ┌──────────────────────┐
 │  ASSESS SEVERITY     │
 │  P1: All services    │
 │      unreachable     │
 │  P2: Multiple svc    │
 │      degraded        │
 │  P3: Single svc      │
 │      affected        │
 └──────────┬───────────┘
            │
            v
 ┌──────────────────────────────────────────┐
 │  DECISION: Volumetric or App-Layer?      │
 └─────┬──────────────────────────┬─────────┘
       │                          │
       v                          v
 ┌─────────────┐          ┌──────────────────┐
 │ VOLUMETRIC  │          │ APPLICATION-LAYER│
 │ (L3/L4)     │          │ (L7)             │
 │             │          │                  │
 │ Contact DO  │          │ Enable "Under    │
 │ support for │          │ Attack" mode on  │
 │ upstream    │          │ Cloudflare       │
 │ mitigation  │          │                  │
 └──────┬──────┘          └────────┬─────────┘
        │                          │
        └────────────┬─────────────┘
                     │
                     v
          ┌──────────────────────┐
          │ ENGAGE CLOUDFLARE WAF│
          │ + Custom WAF rules   │
          │ + Block bad UAs,     │
          │   paths, patterns    │
          └──────────┬───────────┘
                     │
                     v
          ┌──────────────────────┐
          │ APPLY RATE LIMITING  │
          │ >100 req/min per IP  │
          │ = block 10 min       │
          │ + iptables on origin │
          └──────────┬───────────┘
                     │
                     v
          ┌──────────────────────┐
          │ TRAFFIC ANALYSIS     │
          │ Source IPs, geo,     │
          │ attack vectors,      │
          │ bandwidth profile    │
          └──────────┬───────────┘
                     │
                     v
  ┌──────────────────────────────────────────┐
  │  DECISION: Is Cloudflare blocking it?    │
  └─────┬──────────────────────────┬─────────┘
        │                          │
        v                          v
  ┌───────────┐           ┌────────────────┐
  │ YES       │           │ NO             │
  │           │           │                │
  │ Continue  │           │ ESCALATE:      │
  │ monitoring│           │ - DO support   │
  │ Datadog + │           │ - Additional   │
  │ Cloudflare│           │   iptables     │
  │ analytics │           │ - Restrict     │
  │           │           │   tunnel       │
  └─────┬─────┘           └───────┬────────┘
        │                         │
        └────────────┬────────────┘
                     │
                     v
          ┌──────────────────────┐
          │ MITIGATION APPLIED   │
          │ Attack neutralized   │
          │ or degradation       │
          │ contained            │
          └──────────┬───────────┘
                     │
                     v
  ┌──────────────────────────────────────────┐
  │  DECISION: Service recovered?            │
  └─────┬──────────────────────────┬─────────┘
        │                          │
        v                          v
  ┌───────────┐           ┌────────────────┐
  │ YES       │           │ NO             │
  │           │           │                │
  │ DOCUMENT: │           │ FAILOVER:      │
  │ - Timeline│           │ - Stop non-    │
  │ - Impact  │           │   critical svcs│
  │ - Lessons │           │ - Graceful     │
  │           │           │   degradation  │
  │           │           │   (see Sec. 9) │
  │           │           │ - Re-assess    │
  └─────┬─────┘           └───────┬────────┘
        │                         │
        └────────────┬────────────┘
                     │
                     v
          ┌──────────────────────┐
          │ RECOVERY             │
          │ - Verify all svcs up │
          │ - Disable "Under     │
          │   Attack" mode       │
          │ - Remove temp        │
          │   iptables rules     │
          │ - Monitor 30 min     │
          └──────────┬───────────┘
                     │
                     v
          ┌──────────────────────┐
          │ POST-INCIDENT        │
          │ - Report within 72h  │
          │ - Root cause analysis│
          │ - Update resource    │
          │   limits / WAF rules │
          │ - Update this        │
          │   playbook           │
          └──────────────────────┘
```

---

## 1. Purpose

This playbook provides step-by-step procedures for responding to distributed denial-of-service (DDoS) attacks or severe service degradation affecting the Organization infrastructure. This includes both malicious external attacks and organic failures (resource exhaustion, misconfiguration, disk full, runaway processes).

---

## 2. Scope

Applies to all services hosted on `alpha-node` (4vCPU/8GB VPS), the `svc-tunnel` zero-trust ingress, and Cloudflare layer protecting `example-ops.com`. Covers:
- Layer 3/4 DDoS attacks (volumetric, protocol-based)
- Layer 7 DDoS attacks (application-layer floods)
- Resource exhaustion (CPU, memory, disk, I/O)
- Cascading container failures
- Network connectivity loss
- Cloudflare or DigitalOcean outages

---

## 3. Severity Classification

| Severity | Criteria |
|----------|----------|
| **SEV-1 (Critical)** | All services unreachable; `svc-tunnel` down; complete loss of connectivity to `alpha-node` |
| **SEV-2 (High)** | Multiple services degraded or down; user-facing services (`svc-automation`, `svc-gateway`) impacted |
| **SEV-3 (Medium)** | Single service degraded; intermittent latency; non-user-facing service affected |
| **SEV-4 (Low)** | Elevated resource usage detected but no service impact; proactive alert |

---

## 4. Detection Triggers

### 4.1 Monitoring Platform Alerts

- [ ] **High CPU utilization** -- sustained >85% across the VPS for >5 minutes
- [ ] **High memory utilization** -- sustained >90% or OOM killer invoked
- [ ] **Disk space critical** -- root or data volume >90% full
- [ ] **Container restart loop** -- any container restarting >3 times in 10 minutes
- [ ] **High network I/O** -- inbound/outbound traffic >5x normal baseline
- [ ] **Service latency** -- response time >5x normal for `svc-automation` or `svc-gateway`
- [ ] **Connection timeout** -- Datadog loses contact with `svc-monitor` agent

### 4.2 Edge Security Provider Alerts

- [ ] **DDoS attack detected** -- Cloudflare dashboard shows active mitigation
- [ ] **Firewall event spike** -- WAF blocking anomalous volume of requests
- [ ] **Origin unreachable** -- Cloudflare reports 522/523/524 errors to origin

### 4.3 External / Manual Detection

- [ ] **User reports** -- services at `automation.example-ops.com` unreachable or slow
- [ ] **SSH timeout** -- unable to connect via `ssh.example-ops.com` or direct IP
- [ ] **Health check failure** -- automated health check workflow reports failure
- [ ] **Cloud provider status page** -- DigitalOcean reports infrastructure incident in the affected region

---

## 5. Response Procedures

### Phase 1: Assessment and Triage (0-15 minutes)

**Objective:** Determine whether this is a DDoS attack, organic degradation, or external outage, and assign severity.

- [ ] **Step 1.1** -- Check if the issue is DDoS or degradation:

 **Check Cloudflare status:**
 ```bash
 # Check Cloudflare dashboard for attack indicators
 # Look for: DDoS mitigation active, WAF event spike, origin errors
 # URL: Cloudflare dashboard > Analytics > Security
 ```

 **Check if the VPS is reachable:**
 ```bash
 # Try direct SSH (not through tunnel)
 ssh -o ConnectTimeout=10 root@10.100.1.10 "uptime && free -h && df -h / && docker ps --format 'table {{.Names}}\t{{.Status}}'"
 ```

 **Check if it's a DigitalOcean outage:**
 ```bash
 # Check DigitalOcean status page
 # Check Datadog status page
 # Check Cloudflare status page (cloudflarestatus.com equivalent)
 ```

- [ ] **Step 1.2** -- If the VPS is reachable, collect diagnostic data:
 ```bash
 ssh root@10.100.1.10 << 'DIAG'
 echo "=== UPTIME ==="
 uptime

 echo "=== MEMORY ==="
 free -h

 echo "=== DISK ==="
 df -h /

 echo "=== TOP CPU PROCESSES ==="
 ps aux --sort=-%cpu | head -15

 echo "=== TOP MEMORY PROCESSES ==="
 ps aux --sort=-%mem | head -15

 echo "=== DOCKER CONTAINERS ==="
 docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

 echo "=== NETWORK CONNECTIONS ==="
 ss -s

 echo "=== DOCKER EVENTS (last 30 min) ==="
 docker events --since 30m --until 0s --format '{{.Time}} {{.Type}} {{.Action}} {{.Actor.Attributes.name}}' 2>/dev/null | tail -50
 DIAG
 ```

- [ ] **Step 1.3** -- Identify the root cause category:

 | Indicator | Likely Cause |
 |-----------|-------------|
 | Cloudflare shows active DDoS mitigation | **DDoS Attack** |
 | High inbound connections from many IPs, high bandwidth | **DDoS Attack** |
 | Single container consuming all CPU/memory | **Runaway Process / Bug** |
 | Disk at 100% | **Disk Exhaustion** |
 | All containers healthy but services slow | **Network / DNS issue** |
 | OOM kills in `dmesg` | **Memory Exhaustion** |
 | Cloud provider status page shows incident | **Provider Outage** |

- [ ] **Step 1.4** -- Assign severity per Section 3 and open an incident ticket.

### Phase 2: Containment -- DDoS Attack (15-45 minutes)

**Use this section if the root cause is a DDoS attack.**

- [ ] **Step 2.1** -- Verify Cloudflare DDoS protection is active:
 ```
 Cloudflare dashboard > Security > DDoS
 - Confirm "Under Attack" mode is available
 - Check if automatic mitigation is handling the attack
 ```

- [ ] **Step 2.2** -- If the attack is bypassing automatic mitigation, enable "Under Attack" mode:
 ```
 Cloudflare dashboard > Overview > Under Attack Mode > ON
 ```
 This adds a JavaScript challenge to all visitors, which stops most L7 attacks.

- [ ] **Step 2.3** -- Implement rate limiting on Cloudflare:
 ```
 Cloudflare dashboard > Security > WAF > Rate Limiting Rules
 - Add rule: If requests from single IP > 100/minute to automation.example-ops.com, block for 10 minutes
 ```

- [ ] **Step 2.4** -- If the attack targets specific endpoints, add Cloudflare WAF rules:
 ```
 Cloudflare dashboard > Security > WAF > Custom Rules
 - Block specific User-Agents, paths, or query patterns used in the attack
 ```

- [ ] **Step 2.5** -- If the tunnel is overwhelmed, restrict tunnel ingress:
 ```bash
 # On alpha-node, add iptables rules to limit connections to the tunnel
 ssh root@10.100.1.10 << 'EOF'
 # Limit new connections per source IP
 iptables -A INPUT -p tcp --dport <automation-port> -m connlimit --connlimit-above 20 -j DROP
 iptables -A INPUT -p tcp --dport <automation-port> -m state --state NEW -m limit --limit 50/min --limit-burst 100 -j ACCEPT
 EOF
 ```

- [ ] **Step 2.6** -- If the VPS itself is being directly targeted (bypassing edge security):
 ```bash
 # Check if attackers know the origin IP
 ssh root@10.100.1.10 "ss -tulnp | grep -v '127.0.0.1\|::1' | grep LISTEN"

 # Ensure only the tunnel and SSH are listening on public interfaces
 # All services should be on net-core only
 # If services are exposed on 0.0.0.0, fix the compose binding immediately
 ```

- [ ] **Step 2.7** -- Contact DigitalOcean support if the attack is volumetric and affecting the hypervisor:
 ```
 Cloud provider support ticket:
 - VPS ID / Instance ID
 - Description of the attack
 - Request: Enable DDoS mitigation or null-route the IP temporarily
 ```

### Phase 3: Containment -- Service Degradation (15-45 minutes)

**Use this section if the root cause is organic degradation (not a DDoS attack).**

#### 3A: CPU Exhaustion

- [ ] **Step 3A.1** -- Identify the container consuming excessive CPU:
 ```bash
 docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | sort -k2 -rn | head -10
 ```

- [ ] **Step 3A.2** -- If a non-critical container is consuming CPU, restart it:
 ```bash
 docker compose restart <service_name>
 ```

- [ ] **Step 3A.3** -- If `svc-llm` or `svc-transcription` is the bottleneck (compute-intensive by nature), consider temporarily stopping it:
 ```bash
 docker compose stop svc-llm # or svc-transcription
 # These are non-critical and can be restarted later
 ```

- [ ] **Step 3A.4** -- Set CPU limits on the offending container to prevent recurrence:
 ```yaml
 # In docker-compose.yaml, add:
 deploy:
  resources:
   limits:
    cpus: '1.0' # Limit to 1 CPU core
 ```

#### 3B: Memory Exhaustion

- [ ] **Step 3B.1** -- Check for OOM kills:
 ```bash
 dmesg | grep -i "oom\|killed process" | tail -20
 docker events --since 30m --filter event=oom
 ```

- [ ] **Step 3B.2** -- Identify memory-heavy containers:
 ```bash
 docker stats --no-stream --format "{{.Name}}\t{{.MemUsage}}" | sort -k2 -rn
 ```

- [ ] **Step 3B.3** -- Restart the offending container:
 ```bash
 docker compose restart <service_name>
 ```

- [ ] **Step 3B.4** -- If memory is critically low, free memory by stopping non-critical services:
 ```bash
 # Stop in priority order (least critical first)
 docker compose stop svc-llm
 docker compose stop svc-transcription
 docker compose stop svc-ai-gateway
 ```

- [ ] **Step 3B.5** -- Clear Docker build cache and unused images:
 ```bash
 docker system prune -f --volumes=false
 # WARNING: Do NOT use --volumes flag -- it will delete persistent data
 ```

#### 3C: Disk Exhaustion

- [ ] **Step 3C.1** -- Identify what is consuming disk space:
 ```bash
 du -sh /opt/platform/volumes/*/ | sort -rh
 du -sh /var/lib/docker/
 docker system df
 ```

- [ ] **Step 3C.2** -- Clean Docker artifacts:
 ```bash
 # Remove unused images (NOT running images)
 docker image prune -f

 # Remove old container logs
 truncate -s 0 /var/lib/docker/containers/*/*-json.log

 # Remove unused networks
 docker network prune -f
 ```

- [ ] **Step 3C.3** -- If PostgreSQL WAL/data is consuming disk:
 ```bash
 docker exec svc-db psql -U <admin_user> -c "SELECT pg_size_pretty(pg_database_size('<db_name>'));"
 # Consider running VACUUM FULL if bloat is the issue
 docker exec svc-db psql -U <admin_user> -c "VACUUM FULL;"
 ```

- [ ] **Step 3C.4** -- If logs are the issue, implement log rotation:
 ```bash
 # Add to Docker daemon config /etc/docker/daemon.json
 {
  "log-driver": "json-file",
  "log-opts": {
   "max-size": "10m",
   "max-file": "3"
  }
 }
 systemctl restart docker
 ```

#### 3D: Container Crash Loop

- [ ] **Step 3D.1** -- Identify the crashing container:
 ```bash
 docker ps -a --filter "status=restarting" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
 ```

- [ ] **Step 3D.2** -- Check the container logs for crash reason:
 ```bash
 docker logs --tail 100 <container_name>
 ```

- [ ] **Step 3D.3** -- Check if a dependency is down:
 ```bash
 # If svc-db is down, many services will fail
 docker compose ps svc-db
 docker exec svc-db pg_isready -U <admin_user>
 ```

- [ ] **Step 3D.4** -- If the container depends on a healthy volume:
 ```bash
 # Check volume permissions
 ls -la /opt/platform/volumes/<service>/
 ```

- [ ] **Step 3D.5** -- Restart the container with fresh state (if safe):
 ```bash
 docker compose up -d --force-recreate <service_name>
 ```

### Phase 4: Recovery (30-60 minutes)

**Objective:** Restore full service and verify stability.

- [ ] **Step 4.1** -- Verify all containers are running and healthy:
 ```bash
 docker compose ps
 # All should show "Up" and "healthy"
 ```

- [ ] **Step 4.2** -- Check service endpoints are responding:
 ```bash
 # Automation platform
 curl -sf -o /dev/null -w "%{http_code}" http://localhost:<automation-port>/healthz

 # Gateway
 docker exec svc-gateway tctl status

 # Database
 docker exec svc-db pg_isready -U <admin_user>
 ```

- [ ] **Step 4.3** -- Verify the tunnel is operational:
 ```bash
 # From external: test that automation.example-ops.com resolves and responds
 curl -sf -o /dev/null -w "%{http_code}" https://automation.example-ops.com/healthz

 # Check tunnel container
 docker logs --tail 10 svc-tunnel
 ```

- [ ] **Step 4.4** -- Check Datadog is receiving data:
 ```bash
 docker logs --tail 10 svc-monitor
 # Verify metrics are flowing to the monitoring dashboard
 ```

- [ ] **Step 4.5** -- Verify svc-detection is operational:
 ```bash
 docker logs --tail 10 svc-detection
 docker logs --tail 10 svc-detection-router
 ```

- [ ] **Step 4.6** -- If non-critical services were stopped during containment, restart them:
 ```bash
 docker compose up -d svc-llm svc-transcription svc-ai-gateway
 ```

- [ ] **Step 4.7** -- If iptables rules were added during DDoS containment, evaluate whether to keep or remove them:
 ```bash
 iptables -L INPUT -n --line-numbers | grep -i "connlimit\|limit"
 # Remove if attack has subsided:
 iptables -D INPUT <rule_number>
 ```

- [ ] **Step 4.8** -- If "Under Attack" mode was enabled on Cloudflare, disable it once the attack subsides:
 ```
 Cloudflare dashboard > Overview > Under Attack Mode > OFF
 ```

- [ ] **Step 4.9** -- Monitor for 30 minutes to confirm stability:
 ```bash
 # Watch container resource usage
 watch -n 10 'docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"'
 ```

### Phase 5: Post-Incident (Within 72 hours)

**Objective:** Document, analyze, and harden against recurrence.

- [ ] **Step 5.1** -- Complete the incident timeline:
 - When did degradation / attack begin?
 - When was it detected?
 - Detection-to-mitigation time
 - Total service impact duration
 - Which services were affected and for how long?

- [ ] **Step 5.2** -- For DDoS attacks, analyze the attack profile:
 - Attack type (volumetric, protocol, application-layer)
 - Peak bandwidth / request rate
 - Source geography and IP distribution
 - Targeted endpoints or services
 - Effectiveness of Cloudflare mitigation

- [ ] **Step 5.3** -- For degradation incidents, identify root cause:
 - Resource leak in application code?
 - Insufficient resource limits on containers?
 - Missing log rotation?
 - Database bloat?
 - Unexpected traffic pattern (non-malicious)?

- [ ] **Step 5.4** -- Write a post-incident report containing:
 - Executive summary
 - Timeline of events
 - Impact assessment (services affected, duration, users impacted)
 - Root cause analysis
 - Remediation actions taken
 - Lessons learned
 - Action items with owners and due dates

- [ ] **Step 5.5** -- Implement preventive measures:
 - [ ] Review and update resource limits in `docker-compose.yaml` for all services
 - [ ] Implement or verify Docker log rotation (`max-size`, `max-file`)
 - [ ] Set up monitoring alerts for disk >80%, CPU >80% sustained, memory >85%
 - [ ] Review Cloudflare rate limiting and WAF rules
 - [ ] Consider adding a database backup rotation / cleanup cron
 - [ ] Document baseline resource usage for future comparison

- [ ] **Step 5.6** -- Capacity planning:
 - Is the current 4vCPU/8GB VPS sufficient for the workload?
 - Should any services be moved to separate infrastructure?
 - Are there containers that can be removed or consolidated?

- [ ] **Step 5.7** -- Update this playbook with any lessons learned.

---

## 6. Communication Requirements

| Audience | When | Method | Content |
|----------|------|--------|---------|
| Incident Commander | Immediately on detection | Direct message / phone | Service status, severity, suspected cause |
| System Owner | Within 15 minutes | Direct message / phone | Impact scope, ETA for resolution |
| Cloud provider | If provider-level action needed | Support ticket | Instance ID, description of issue |
| Cloudflare | If attack bypasses mitigation | Support ticket / dashboard | Attack characteristics, request enhanced mitigation |
| End users (if applicable) | If outage >30 minutes | Status page or email | Acknowledgement, ETA, updates |

---

## 7. Evidence Preservation Checklist

| Artifact | Location | Collected? |
|----------|----------|------------|
| Datadog dashboards (screenshot) | Datadog UI | [ ] |
| Cloudflare analytics (screenshot) | Cloudflare dashboard | [ ] |
| Docker stats snapshot | Terminal output | [ ] |
| System resource data (top, free, df) | Terminal output | [ ] |
| Container logs for affected services | `docker logs <container>` | [ ] |
| Docker events log | `docker events` output | [ ] |
| iptables rules added | `iptables -L -n` | [ ] |
| Network connection summary | `ss -s` output | [ ] |
| dmesg OOM messages (if applicable) | `dmesg` output | [ ] |
| Cloud provider support ticket ID | Support dashboard | [ ] |

---

## 8. NIST 800-53 Control Mapping

| Control | Description | Playbook Phase |
|---------|-------------|----------------|
| IR-4 | Incident Handling | All phases |
| IR-5 | Incident Monitoring | Phase 1 (detection, triage) |
| IR-6 | Incident Reporting | Phase 5 (post-incident report) |
| SC-5 | Denial of Service Protection | Phase 2 (edge security, rate limiting) |
| SC-5(1) | Restrict Internal Users | Phase 3 (resource limits) |
| SC-5(2) | Excess Capacity / Bandwidth / Redundancy | Phase 5 (capacity planning) |
| SC-7 | Boundary Protection | Phase 2 (tunnel, WAF) |
| SI-4 | Information System Monitoring | Phase 1 (Datadog alerts) |
| CP-2 | Contingency Plan | Phase 3 (graceful degradation) |
| CP-10 | Information System Recovery | Phase 4 (service restoration) |
| AU-6 | Audit Review, Analysis, and Reporting | Phase 5 (log analysis) |
| PE-11 | Emergency Power | N/A (cloud-hosted) |

---

## 9. Service Priority for Graceful Degradation

When resources are constrained, maintain services in this priority order:

| Priority | Service | Reason |
|----------|---------|--------|
| 1 (Critical) | `svc-tunnel` | Only public ingress; losing it means total lockout if direct SSH is unavailable |
| 2 (Critical) | `svc-db` | All stateful services depend on it |
| 3 (High) | `svc-gateway` | SSH access, session recording, identity verification |
| 4 (High) | `svc-automation` | Core orchestration and workflow engine |
| 5 (High) | `svc-detection` | Security monitoring must remain active during incidents |
| 6 (Medium) | `svc-monitor` | Observability; can tolerate brief gaps |
| 7 (Medium) | `svc-identity` | SSO/IdP; needed for user auth |
| 8 (Medium) | `svc-secrets` | Secrets engine; not needed if secrets are already in env |
| 9 (Medium) | `svc-detection-router` | Event routing; detection still logs locally |
| 10 (Medium) | `Fluentd` | Log aggregation; can buffer |
| 11 (Medium) | `svc-event-shipper` | Audit shipping; can buffer |
| 12 (Low) | `svc-ai-gateway` | AI inference; non-essential |
| 13 (Low) | `svc-llm` | Local LLM; non-essential, high resource usage |
| 14 (Low) | `svc-transcription` | Voice transcription; non-essential |

**Stop services from the bottom up** to free resources while preserving critical functionality.

---

## 10. Quick Reference Card

**For use during an active incident -- tear-off summary:**

```
1. ASSESS: Is it DDoS or degradation?
       - Check edge security dashboard for active attacks
       - SSH direct to 10.100.1.10 and run: uptime && free -h && df -h && docker stats --no-stream

2. DDoS:  Edge security handles L3/L4 automatically
       - Enable "Under Attack" mode if L7 attack
       - Add rate limiting rules
       - Do NOT expose origin IP

3. DEGRADE: Identify bottleneck (CPU/mem/disk)
       - Stop non-critical services: svc-llm, svc-transcription, svc-ai-gateway
       - Restart offending container
       - Clean disk: docker image prune -f && truncate logs

4. RECOVER: docker compose ps (all healthy?)
       - Restart stopped services
       - Disable "Under Attack" mode when safe
       - Monitor 30 minutes for stability

5. REPORT: Post-incident report within 72 hours
```

---

## Cross-References

| Document | Relationship |
|----------|-------------|
| [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) | System Security Plan with NIST 800-53 control mapping |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | Tracks findings and remediation milestones |
| [README.md](README.md) | GRC library index and reading guide |
