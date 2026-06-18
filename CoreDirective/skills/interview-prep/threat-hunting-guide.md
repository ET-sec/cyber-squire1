# Threat Hunting & Threat Intelligence — Interview Prep Guide
# Role: Cybersecurity Engineer (Attack Surface Management)

---

## 1. The 30-Second Pitch

Memorize this. Say it exactly like this:

> "Threat hunting is the proactive search for adversaries that have already bypassed your automated controls. Unlike alerting, which waits for a signature to fire, hunting starts with a hypothesis — 'what if an attacker is already inside?' — and then actively looks for evidence to confirm or deny it. The goal is to find what your SIEM missed and then turn those findings into new automated detections."

That answer covers the definition, the distinction from passive tools, and shows you understand the feedback loop. It will land.

---

## 2. Threat Hunting vs. Alerting vs. Incident Response

This is a very common interview question. The distinction matters.

| | Alerting | Threat Hunting | Incident Response |
|---|---|---|---|
| **Trigger** | System detects anomaly | Analyst initiates | Alert or hunt finding |
| **Posture** | Reactive | Proactive | Reactive |
| **Starting point** | Known rule/signature | Hypothesis or intel | Confirmed or suspected incident |
| **Who drives it** | Automated system | Analyst | IR team |
| **Output** | Alert ticket | New detection or confirmed clear | Remediation + report |

The key point interviewers are probing for: **alerting tells you what it knows. Hunting finds what it doesn't know yet.**

Your story: you tuned alerts from 200+ down to 12 actionable alerts. That is alert optimization — you eliminated noise so the signal matters. Hunting is what you do with the signal that never fires.

---

## 3. The Hunting Loop

Every hunt follows this cycle. Reference it by name in interviews — it shows structured methodology.

```
Hypothesis
    |
    v
Collect (pull logs, telemetry, network data)
    |
    v
Analyze (look for evidence that confirms/denies hypothesis)
    |
    v
Conclude (adversary present / clean / more data needed)
    |
    v
Automate (if you found something, write a detection so the SIEM catches it next time)
    |
    v
(new hypothesis)
```

The **Automate** step is what separates mature hunters from beginners. If you hunt for something and find it manually, you have failed to make your organization more resilient unless you automate that detection. Interviewers love this answer.

---

## 4. Three Types of Hunts

### Hypothesis-Driven
Start with an ATT&CK technique and ask: "Could this be happening in our environment?"

Example: T1059 (Command and Script Interpreter) — an attacker who compromised an AI gateway container might spawn a shell inside it to move laterally. You build a hunt around that assumption and look for evidence.

### IOC-Driven
Start with a known bad indicator (IP address, domain, file hash) from threat intel, then search your logs for any match.

Example: AlienVault OTX publishes a C2 IP used in a recent campaign targeting cloud infrastructure. You search Datadog and Cloudflare logs for any outbound connections to that IP.

### Anomaly-Driven
Establish a baseline of normal behavior, then look for statistical outliers.

Example: Outbound bytes from `cd-service-n8n` average 50KB/day. You notice a day where it sent 2.3GB. That's not a signature match — it's a deviation. You investigate.

---

## 5. Forming a Hunting Hypothesis

A good hypothesis is specific, testable, and grounded in your actual environment. Generic hypotheses waste time.

**Format:** "If [attack scenario], we would expect to see [observable behavior] in [data source]."

### Hypothesis 1 — Lateral Movement via Docker Socket
> "An attacker who gained initial access to the OpenClaw gateway container would attempt to escape to the host or move laterally by accessing the Docker socket, which would manifest as unexpected Docker API calls or process spawning from within the container."

**Where to look:** Falco logs (rule: `Unexpected process spawned in container`), Docker daemon logs on the host.

### Hypothesis 2 — Credential-Based Intrusion
> "Compromised n8n or PostgreSQL credentials would produce login activity at unusual times or from unexpected source IPs that differ from the Cloudflare tunnel's egress range."

**Where to look:** PostgreSQL `pg_log`, n8n audit trail, Cloudflare Access logs.

### Hypothesis 3 — PostgreSQL Data Exfiltration
> "An attacker with database access would attempt to dump large tables, which would show as queries selecting full tables without WHERE clauses, or unusually high row counts returned per session."

**Where to look:** PostgreSQL statement logs (`log_statement = all`), Datadog APM query metrics, pg_stat_activity.

### Hypothesis 4 — Cloudflare Tunnel Abuse
> "A threat actor who discovered the Cloudflare tunnel URL would probe it with automated tools, producing a burst of 4xx/5xx responses, unusual User-Agent strings, or high request rates from a single ASN."

**Where to look:** Cloudflare Analytics, Datadog HTTP metrics from the tunnel container logs.

### Hypothesis 5 — Container Escape Attempt
> "An attacker inside any container would attempt privilege escalation or host filesystem access, which Falco would capture as attempts to mount the host `/proc`, `/sys`, or `/var/run/docker.sock`."

**Where to look:** Falco alerts (rules: `Container Escape`, `Write to etc directory`, `Symlink Created Over Sensitive Files`).

---

## 6. Five Practical Hunts Using Your Stack

### Hunt 1: Unexpected Process Spawning (T1059 — Command Execution)

**Tool:** Falco + Datadog

**What you're looking for:** A process running inside a container that has no business being there. Web servers should not spawn `/bin/bash`. AI gateway containers should not run `wget` or `curl` to external hosts.

**Query approach:**
```
# Falco would fire on this — but for hunting, review historical Falco logs:
# Look for: proc.name in (bash, sh, python3) AND container.name = openclaw-gateway
# AND evt.type = execve

# In Datadog Logs:
service:falco "proc.name" ("bash" OR "sh" OR "python") container_name:openclaw-gateway
```

**What a clean result looks like:** Only the expected startup process tree. The container's entrypoint process with no unexpected children.

**What a hit looks like:** A `bash` process spawned from within `openclaw-gateway` at 2 AM with a network connection shortly after.

---

### Hunt 2: Unusual Outbound Connections from Containers (T1071 — Application Layer Protocol)

**Tool:** Datadog Network Performance Monitoring

**What you're looking for:** Any container making outbound connections to destinations that are not in the expected list (Anthropic API, Cloudflare, DigitalOcean metadata). C2 traffic often mimics normal HTTPS but goes to unexpected ASNs or newly registered domains.

**Query approach in Datadog:**
```
# Network map: source = cd-service-* → destination NOT IN [api.anthropic.com, cloudflare.com]
# Look for: unusual destination ASNs, connections to IPs less than 30 days old
# Metric: aws.network.bytes_out per container, flag anything > 2 std deviations above baseline
```

**Pivot:** If you find an unusual destination IP, run it through VirusTotal or AlienVault OTX. A clean IP does not mean clean traffic — look at timing and volume.

---

### Hunt 3: PostgreSQL Unusual Query Patterns (Data Exfiltration)

**Tool:** PostgreSQL logs + Datadog

**What you're looking for:** SELECT queries pulling entire tables, queries from unexpected users (anyone other than `cd_n8n_user`), or sessions with unusually high rows_returned counts.

**Query approach:**
```sql
-- In pg_stat_statements (if enabled):
SELECT query, calls, rows, total_time
FROM pg_stat_statements
WHERE rows / calls > 10000  -- queries averaging >10k rows returned
ORDER BY rows DESC;

-- In pg_log, grep for:
-- "SELECT" without WHERE clause on large tables
-- login from source IP that is not 172.17.0.x (Docker bridge)
```

**Datadog metric to watch:** `postgresql.rows_fetched` — spike in rows fetched without a corresponding spike in application requests is a red flag.

---

### Hunt 4: Cloudflare Tunnel Reconnaissance (T1595 — Active Scanning)

**Tool:** Cloudflare Analytics + Datadog

**What you're looking for:** Bursts of requests to paths that don't exist (404s), probing of common admin paths (`/admin`, `/api/v1`, `/.env`, `/wp-admin`), or requests with unusual or empty User-Agent strings.

**Query approach in Cloudflare:**
```
# Cloudflare Security tab → Firewall Events
# Filter: Action = Block or Challenge, last 7 days
# Look for: repeated requests from same IP, path enumeration patterns

# In Datadog (if you're piping Cloudflare logs):
@cf.status_code:404 | stats count by @cf.clientip | sort count desc
```

**What it means:** A consistent stream of 404s from one IP hitting `/api`, `/admin`, `/config` in sequence is automated reconnaissance. Not necessarily a breach, but a signal to block and monitor.

---

### Hunt 5: Container Escape Attempts (T1611 — Escape to Host)

**Tool:** Falco (primary), Datadog (secondary)

**What you're looking for:** Any attempt to access the host filesystem from inside a container, escalate to root (if containers run as non-root), or interact with `/var/run/docker.sock`.

**Falco rules that matter here:**
```yaml
# These should already be in your Falco ruleset:
- rule: Detect Container Escape via Docker Socket
  condition: fd.name = /var/run/docker.sock AND NOT proc.name in (dockerd)

- rule: Write to sensitive directory
  condition: evt.type = mkdir AND fd.name startswith /etc AND container.id != host

- rule: Unexpected privileged container process
  condition: container.privileged=true AND NOT proc.name in (expected_processes)
```

**How to hunt proactively:** Review `falco.log` for any `WARNING` or `CRITICAL` events in the last 30 days that were not responded to. Many teams have Falco running but nobody reviewing the logs. That gap is the hunt.

---

## 7. Threat Intelligence Basics

### What Threat Feeds Are

Threat feeds are curated lists of known bad indicators — IPs, domains, file hashes, URLs — that have been observed in attacks. They range from free community feeds to expensive enterprise subscriptions.

| Feed | Type | Best For |
|------|------|----------|
| AlienVault OTX | Free, community | Broad IOC coverage, pulse-based intel |
| abuse.ch (Feodo, URLhaus) | Free, focused | Banking trojans, botnet C2, malware URLs |
| MISP | Open source platform | Sharing structured threat intel within orgs |
| Shodan Monitor | Paid | Tracking your own exposure, alert when assets appear on Shodan |
| GreyNoise | Paid/free tier | Separating internet background noise from targeted scanning |

### How Threat Intel Informs a Hunt

Raw IOC: "IP 185.220.101.45 is a known Tor exit node used in credential stuffing."

Hunt action: Search Cloudflare tunnel logs and PostgreSQL auth logs for any login attempts originating from that IP. If found, check what was accessed, when, and whether any succeeded.

TTP-based intel: "TA0043 (Reconnaissance) actors targeting cloud infrastructure are using Shodan to identify exposed Docker APIs."

Hunt action: Check if port 2375 or 2376 is exposed anywhere, search for any connection attempts to those ports in Cloudflare and host firewall logs.

### IOC vs TTP — Know This Cold

**IOC (Indicator of Compromise):** A specific artifact — an IP address, a domain, a file hash, a registry key. Fast to search for. Short shelf life because attackers rotate infrastructure constantly.

**TTP (Tactics, Techniques, Procedures):** How an adversary operates. Not what they used, but how they think. T1059 (command execution) is a TTP — attackers will always need to run commands, even if the specific malware hash changes.

**Interview answer when asked "what's the difference":**
> "IOCs are like a mugshot — useful if the person shows up again, but useless if they change their appearance. TTPs are like behavioral patterns — an attacker's methodology doesn't change often, so hunting for TTPs gives you more durable detections."

---

## 8. Datadog as a Hunting Platform

Datadog is more than a monitoring tool. It is a hunting platform if you use it correctly.

### Log Queries for Hunting

Datadog Log Search syntax for hunting patterns:

```
# Find all container logs with "exec" events (potential command execution):
service:falco evt.type:execve -proc.name:expected_process

# Find unusual outbound bytes:
@network.bytes_out:>1000000 service:cd-service-*

# Find failed auth attempts:
status:error ("authentication failed" OR "invalid password" OR "permission denied")

# Find requests to sensitive paths:
@http.url_details.path:("/admin" OR "/.env" OR "/wp-admin" OR "/api/v1/config")
```

### Building a Hunting Dashboard

Maintain a dashboard in Datadog specifically for hunting review — not operational monitoring. Include:

- Top 10 external IPs connecting to the tunnel (last 7 days)
- Container network bytes out over time, per container (look for spikes)
- Falco alert count over time (look for sudden silence — could mean Falco is broken, or attacker killed it)
- PostgreSQL connections by source (anything outside 172.17.0.x is anomalous)
- Failed authentications by service and source IP

### From Hunt to Automated Detection

This is the discipline that impresses interviewers. After every hunt:

1. If you confirmed the hypothesis (found something): write a Datadog monitor that fires automatically when the same pattern recurs. Document the threshold, the context, and the response procedure.
2. If you rejected the hypothesis (clean): document what normal looks like. That baseline becomes valuable later.
3. If you couldn't determine (insufficient data): identify the missing data source and instrument it.

Your alert reduction from 200+ to 12 actionable alerts is an example of this discipline applied to alerting. Frame it that way: "I applied the same rigor to alert tuning that you would apply to post-hunt automation — every alert either maps to a real threat or gets eliminated."

---

## 9. Splunk Hunting (From Texaco)

### Core SPL Commands for Hunting

**stats — aggregate and count**
```spl
index=endpoint sourcetype=sysmon EventCode=1
| stats count by ParentImage, Image, ComputerName
| sort -count
| where count > 100
```
Use this to find processes that spawn children more often than expected. Normal systems have predictable parent-child relationships.

**timechart — time-based anomaly detection**
```spl
index=network sourcetype=firewall action=allowed dest_port=443
| timechart span=1h count by src_ip
| where count > 2 * avg(count)
```
Use this to find IPs generating traffic spikes. A host that normally makes 200 connections per hour but suddenly makes 5,000 is worth investigating.

**transaction — correlate related events**
```spl
index=auth sourcetype=linux_secure
| transaction host maxspan=5m
| where eventcount > 20 AND duration < 60
| table _time, host, user, src, eventcount, duration
```
Use this to find brute force patterns — many auth events in a short window from the same source.

**Hunting for lateral movement (Pass-the-Hash pattern):**
```spl
index=windows sourcetype=WinEventLog:Security EventCode=4624
| where Logon_Type=3 AND NOT Account_Name="*$"
| stats dc(host) as unique_hosts by Account_Name, src_ip
| where unique_hosts > 5
```
An account authenticating to more than 5 distinct hosts in a short window is a lateral movement signal.

### Building a Hunting Dashboard in Splunk

Structure it in three panels:

1. **Outlier Panel** — processes, accounts, or IPs that appear in the top 1% of frequency or volume
2. **New/First-Seen Panel** — entities that appeared for the first time in the last 24h (new processes, new user accounts, new external IPs)
3. **Correlation Panel** — events that match known ATT&CK patterns (e.g., `net.exe` running followed by SMB connections)

---

## 10. Interview Questions — Answers You Should Have Ready

### "Walk me through your last threat hunt."

Structure: Hypothesis → Data source → Query or method → Finding → Action taken.

**Your answer (based on your infrastructure):**

> "I was reviewing Falco logs after deploying a new version of the OpenClaw gateway container and noticed the ruleset had not been updated to reflect the new process tree. That gap — a window where the detection would have missed a legitimate attack — prompted a hypothesis: what if unexpected processes had run during that window and Falco missed them? I pulled Docker daemon logs from the host for the 72-hour window before the rule update and correlated process start events with the expected startup sequence. Everything was clean, but the exercise identified two other containers that also had stale Falco rules. I updated all rules and documented the expected process tree for each container so future hunts have a verified baseline."

This answer is honest, uses your actual infrastructure, shows methodology, and demonstrates that a clean result still produced value.

---

### "You see an unusual outbound connection from a container. Walk me through your investigation."

Step-by-step:

1. **Preserve:** Do not kill the container. Capture the connection state first (`ss -tnp`, `netstat -tnp` inside the container, or from the host via `nsenter`).
2. **Identify:** What container, what process (PID), what destination IP and port. Look it up in VirusTotal, Shodan, and GreyNoise immediately.
3. **Scope:** Check Datadog for how long this connection has existed and whether any other containers are also connecting to the same destination.
4. **Context:** Was there a deploy recently? Did someone push a new image? Check the Docker image digest and compare to known-good.
5. **Decide:** If the IP is clean and the connection maps to a known integration — close the hunt, document it. If the IP is flagged or the connection is unexplained — isolate the container (disconnect from the network bridge), notify the team, begin IR.

Key phrase for the interview: **"I never kill a running container during investigation — that destroys volatile evidence. I isolate it from the network first, then investigate."**

---

### "How do you decide what to hunt for?"

Three inputs, in priority order:

1. **Threat intelligence relevant to your environment.** If a campaign targeting Docker environments or AI infrastructure is reported, that is your first hypothesis.
2. **Gaps in your detection coverage.** Review your MITRE ATT&CK coverage map. Any technique with no detection = a hunting target.
3. **Environmental changes.** New containers, new integrations, new open ports. Every change is an opportunity for a misconfiguration or an attacker to hide in the noise of the change.

---

### "What's the difference between an IOC and a TTP?"

Already covered in Section 7. Short version:

> "IOCs are specific artifacts that expire quickly as attackers rotate infrastructure. TTPs are behavioral patterns that are durable because they reflect how an attacker thinks, not just what tool they used. I prioritize TTP-based hunting because a detection built on TTPs is still valid six months later."

---

### "How do you turn a successful hunt into an automated detection?"

> "After a hunt confirms a threat pattern, I extract the minimum set of observable conditions that reliably identify that pattern with acceptable false positive rates. Then I build a detection rule or monitor — in Datadog that's a log-based monitor or security signal rule, in Splunk that's a saved search with alerting. I document the expected false positive rate, the response procedure, and the ATT&CK technique it maps to. Then I verify it would have fired on the original finding. If it fires on the right things and ignores the right noise, it graduates from hunt to automated detection."

This answer maps directly to what you did going from 200+ alerts to 12 — you just applied it in reverse (pruning alerts that didn't meet the standard).

---

## 11. What Can Go Wrong — Know These and Have Answers

### Hunting in Production Without Coordination

Running resource-intensive queries against production databases or generating unusual network traffic patterns during a hunt can trigger alerts from your own monitoring or impact availability. Always notify the team before a hunt that involves active probing, heavy log queries, or network scanning.

**How to avoid:** Use a change window or a hunting time when traffic is low. In your case, the Cloudflare tunnel carries real traffic — a hunt that involves replaying requests or port scanning should happen off-hours.

---

### Chasing False Positives for Hours

Without a clear hypothesis and exit criteria, hunting becomes chasing shadows. You open a log, see something unusual, chase it for two hours, and discover it was a scheduled backup job.

**How to avoid:** Before starting a hunt, write down what a positive finding looks like and what you will accept as a "clean" result. Set a time box — if you have not found confirming evidence in 2 hours, document your methodology, call it clean, and move on. Hypothesis-driven hunting with exit criteria prevents rabbit holes.

---

### Not Documenting Findings

A hunt that finds nothing and produces no documentation is wasted work. The next analyst has no baseline, no record of what was checked, and might hunt the same hypothesis again.

**What to document, always:**
- Hypothesis stated
- Time window examined
- Data sources queried
- Result (positive, negative, inconclusive)
- If negative: what "normal" looks like for that data source
- If positive: detection written, ticket opened, timeline

---

### Missing Context (The Deploy Problem)

You notice a spike in outbound connections from `cd-service-n8n` at 3 AM. You spend 45 minutes investigating before finding out that's when n8n runs its daily cron jobs — Gumroad Solvency check and API Health Check.

**How to avoid:** Before calling anything anomalous, check the change log. In your environment that means:
- Check n8n workflow execution history
- Check Docker container restart times
- Check `cron` / `systemd timer` schedules on the host
- Check recent git commits (a new workflow being tested)

The alert context that gets built over time from tuning is exactly the institutional knowledge that prevents this. Your 200 → 12 alert reduction means you understand what normal looks like — lean on that in your answers.

---

## Quick-Reference Card (Print or Memorize)

| Term | One-line definition |
|------|---------------------|
| Threat hunting | Proactive analyst-led search for threats that evade automated detection |
| IOC | Specific artifact (IP, hash, domain) that indicates compromise |
| TTP | Behavioral pattern (ATT&CK technique) — durable, not easily rotated |
| Hypothesis | Testable assumption: "If X attacked, we'd see Y in Z" |
| Hunting loop | Hypothesis → Collect → Analyze → Conclude → Automate |
| ATT&CK | MITRE framework mapping adversary TTPs to observable behaviors |
| Threat feed | Curated list of IOCs from external sources (OTX, abuse.ch, MISP) |
| SIEM | Central log aggregation and correlation platform (Splunk, Datadog) |
| Detection engineering | Writing rules that automate what a hunter found manually |

---

## Your Story Arc for the Interview

If asked "tell me about your security experience" or "what does your security posture look like," here is the narrative:

> "I run a production Docker environment with 13 services — AI inference, workflow automation, SOAR, identity management, and a Cloudflare zero-trust tunnel. I deployed Falco for runtime detection, which covers container behavior at the kernel level using eBPF. I feed alerts into Datadog, where I built dashboards and monitors to track security-relevant events across the stack. At Texaco I worked with Splunk for log aggregation and built searches and dashboards for operational visibility. One of the things I focused on was alert quality — I reduced alert volume from over 200 to 12 actionable detections by applying the same rigor to tuning that you'd apply to threat hunting: if you can't explain exactly what threat a rule catches and how you'd respond to it, it shouldn't fire."

That answer covers detection engineering, runtime security, SIEM experience, and threat hunting methodology without you having to be prompted for each separately.
