# AI Security Engineer — Study & Apply List

Focused study list. Every topic must be studied **and** applied/tested against the live CoreDirective stack (DO droplet: n8n, Vault, Keycloak, Falco, Datadog, Teleport, OpenClaw). No passive reading.

---

## 1. OWASP Top 10 — Priority Four

Only these four. The rest of the OWASP family is reference material, not study material.

### 1.1 OWASP Web Application Top 10 (2021, 2025 update in progress)
- [ ] Read all 10 categories end-to-end
- [ ] **Apply:** Re-run OWASP ZAP against `n8n.tigouetheory.com` and map every finding to a Top 10 category
- [ ] **Test:** Write one detection rule per category for Falco or Datadog

### 1.2 OWASP API Security Top 10 (2023)
- [ ] Read all 10 — BOLA, broken auth, excessive data exposure, etc.
- [ ] **Apply:** Audit n8n webhook endpoints (`/webhook/master-cmd`, `/webhook/gmail-read-*`) against each item
- [ ] **Test:** Add auth + rate limiting to `/webhook/master-cmd`, verify with curl abuse tests

### 1.3 OWASP LLM Applications Top 10 (2025)
- [ ] Read all 10: prompt injection, insecure output handling, training data poisoning, model DoS, supply chain, sensitive info disclosure, insecure plugin design, excessive agency, overreliance, model theft
- [ ] **Apply:** Red-team your own OpenClaw gateway — prompt injection, tool abuse, scope creep
- [ ] **Test:** Build a guardrails layer (input filter + output filter) and log attempts to n8n/Postgres

### 1.4 OWASP MCP Top 10 (2025 beta)
MCP01 Token Exposure · MCP02 Prompt Injection · MCP03 Privilege Escalation (Scope Creep) · MCP04 Tool Poisoning · MCP05 Supply Chain · MCP06 Command Injection · MCP07 Intent Flow Expansion · MCP08 AuthN/AuthZ · MCP09 Audit/Telemetry · MCP10 Context Injection
- [ ] Read the full spec
- [ ] **Apply:** Audit every OpenClaw skill in `.skills-staging/` against all 10
- [ ] **Test:** Write a poisoned MCP tool in a sandbox, verify OpenClaw behavior, add detection

---

## 2. Splunk Enterprise Security + Detection Engineering

The other piece you flagged. Reference: `CoreDirective/career/SR_SPLUNK_ES_STUDY_PLAN.md` (full 14-day plan already written).

### Core Splunk
- [ ] Install Splunk Free locally: `docker run -d -p 8000:8000 -p 8088:8088 -e SPLUNK_START_ARGS=--accept-license -e SPLUNK_PASSWORD=changeme splunk/splunk:latest`
- [ ] SPL fluency: `index=... | stats count by ... | where ...`
- [ ] HEC (HTTP Event Collector) setup — push logs via token
- [ ] Search head / indexer / forwarder architecture

### Splunk ES (the paid premium app — separate product)
- [ ] **CIM (Common Information Model)** — standard field names across sources
- [ ] **Data models** — accelerated searches
- [ ] **Correlation searches** — the ES detection primitive
- [ ] **Notable events** — how alerts surface in ES
- [ ] **RBA (Risk-Based Alerting)** — modern ES detection pattern
- [ ] **Asset & Identity framework**
- [ ] **Adaptive Response** — ES → SOAR integration

### Detection Engineering
- [ ] **MITRE ATT&CK fluency** — tactics, techniques, sub-techniques, data sources, Navigator
- [ ] **Sigma** — vendor-neutral YAML detection rules, convert to SPL
- [ ] **ESCU (ES Content Update)** — Splunk's open detection repo
- [ ] **Attack Range / attack_data** — lab for testing detections
- [ ] **PEAK framework** — Splunk's hunt methodology (Prepare / Execute / Act / Knowledge)
- [ ] **Detection-as-code** — YAML rules, CI tests, version control

### Apply to your stack
- [ ] **Ship droplet logs to Splunk:** PostgreSQL, n8n, Falco, Teleport audit, Cloudflare Tunnel
- [ ] **Write 5 detections** mapped to ATT&CK:
  - Brute force on n8n login (T1110)
  - Unusual n8n workflow execution (T1059)
  - Credential access in Vault (T1555)
  - Privilege escalation in Keycloak (T1078)
  - Data exfil via Cloudflare Tunnel (T1567)
- [ ] **Falco → Splunk pipeline:** ship eBPF events, write correlation searches
- [ ] **Document the tuning story:** "200 alerts → 12 actionable" with Splunk evidence

---

## 3. Logging & Observability Fundamentals

Required context for Splunk/SIEM work. Skip only what you can already explain cold.

- [ ] **Log sources on the droplet:** map every service to where its logs live and what format
- [ ] **Structured logging** — JSON vs plain text, when each matters
- [ ] **Fluentd** (already running as `cd-service-fluentd`) — pipeline config, parser, output plugins
- [ ] **Datadog Logs** (already shipping) — pipelines, processors, facets, log-to-metric
- [ ] **Retention & compliance** — how long to keep what, SOC 2 / CMMC requirements
- [ ] **PII redaction** — mask emails, tokens, IPs before shipping
- [ ] **Falco outputs** — sidekick routing, priority, rule tuning

### Apply
- [ ] **Inventory:** one doc listing every container, its log path, format, destination
- [ ] **Normalize:** one Fluentd pipeline that tags every log with service/env/host
- [ ] **Test:** break a service, verify the alert path fires in Datadog AND Splunk

---

## 4. MITRE Frameworks (alongside ATT&CK)

- [ ] **MITRE ATT&CK** — core, already in detection engineering above
- [ ] **MITRE D3FEND** — defensive countermeasures mapped to ATT&CK
- [ ] **MITRE ATLAS** — adversarial ML threat matrix (pairs with OWASP LLM Top 10)
- [ ] **MITRE CAR (Cyber Analytics Repository)** — analytic library

### Apply
- [ ] Map every Falco rule and Splunk detection to an ATT&CK technique ID
- [ ] Map every OpenClaw guardrail to an ATLAS tactic

---

## Study method (every topic)

1. Read the official source, not a blog summary
2. Write a 2-paragraph "how I'd detect and prevent this" note in `CoreDirective/career/study-notes/`
3. Apply it to the CoreDirective stack — build, break, detect, fix
4. Capture evidence (screenshots, logs, queries) for resume/portfolio proof
5. Turn it into a LinkedIn post or Threat Brief episode
