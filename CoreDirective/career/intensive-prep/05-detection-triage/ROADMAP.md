# Detection Engineering and Triage Intensive — 14 Day Roadmap

Target outcome: walk into Dropzone AI, Insight Global, WBD interviews and answer detection engineering questions like someone who has built and tuned production detections, not someone who has only read about them.

Daily structure: 60 to 90 minutes. Reading first (anchors the vocabulary), lab second (cements the muscle memory). Every lab is runnable on the laptop with synthetic logs that mimic real schemas.

Stack assumptions: Linux primary, jq + python + grep as the core triage tools, Sigma as the rule lingua franca, Falco for runtime, Datadog as SIEM stand-in for the homelab, Wazuh as a free Splunk ES analog when you want a UI.

---

## Day 1 — Log Fundamentals: Linux

**Reading (45 min)**
- syslog vs journald vs auth.log: where each lives, what writes to them, why modern distros split user-facing vs system logs
- `/var/log/auth.log`, `/var/log/secure`, `/var/log/syslog`, `/var/log/kern.log`, `/var/log/audit/audit.log`
- journald: `journalctl -u sshd`, `--since`, `--priority`, structured fields with `-o json`
- auditd subsystem: rules in `/etc/audit/rules.d/`, key-based correlation, `ausearch -k`, `aureport`

**Lab**
- Run `lab_01_brute_force_ssh`. Open `auth.log`, run grep, then run the python detector. Read the Sigma rule. Note the field names.
- Bonus: run `journalctl -u ssh -o json | jq` on the droplet to compare structured vs text output.

**Anchor concept**: every detection starts with knowing where the signal lives. Wrong log source = no detection.

---

## Day 2 — Log Fundamentals: Cloud (AWS CloudTrail)

**Reading (45 min)**
- CloudTrail event schema: `eventTime`, `eventName`, `eventSource`, `userIdentity.type`, `userIdentity.arn`, `sourceIPAddress`, `userAgent`, `requestParameters`, `responseElements`
- Management events vs data events vs Insights events
- Multi-region trail, organization trail, S3 + CloudWatch Logs delivery
- The Capital One incident: SSRF to IMDS to STS GetCallerIdentity to S3 ListBuckets to GetObject. Cite this in interviews.

**Lab**
- Run `lab_02_aws_credential_exfil`. Use the jq queries to find the kill chain in the synthetic CloudTrail.
- Goal: identify the 5 events that mark the breach without reading every line.

**Anchor concept**: in cloud, identity is the perimeter. Watch `userIdentity.type` and `sourceIPAddress` for any role being assumed from outside.

---

## Day 3 — Log Fundamentals: Kubernetes Audit + Containers

**Reading (45 min)**
- Kubernetes audit log policy: `Metadata`, `Request`, `RequestResponse`, `None` levels
- Schema: `kind`, `verb`, `user.username`, `objectRef.resource`, `requestReceivedTimestamp`, `responseStatus`, `sourceIPs`
- High value verbs: `create`, `exec`, `attach`, `portforward`, `impersonate`
- Falco rules vs K8s audit: Falco watches syscalls (eBPF or kernel module), audit watches API server. Both matter.
- Tesla cryptojacking incident: exposed K8s dashboard, no auth, attacker created pods.

**Lab**
- Run `lab_03_lateral_movement_k8s`. Read the audit log, run the Sigma rule conceptually, write your own variant that detects `pods/exec` against `kube-system` namespace.

**Anchor concept**: the K8s API is just HTTP. Every privileged action has a request received timestamp. Treat it like CloudTrail for clusters.

---

## Day 4 — Parsing Toolkit

**Reading (30 min)**
- grep flags worth knowing: `-E`, `-P`, `-c`, `-A/-B/-C`, `-v`, `-l`
- awk for column extraction and counts: `awk '{print $1}' | sort | uniq -c | sort -rn`
- jq core: `.field`, `select()`, `map()`, `group_by()`, `length`, `--raw-output`
- python for anything stateful: pandas for log dataframes, `collections.Counter`, `ipaddress`, `re`

**Lab (60 min)**
- Take any lab from day 1 to 3 and re-solve it in three styles: pure grep + awk, jq, python. Compare clarity.
- Time yourself. The senior signal is choosing the right tool fast, not always defaulting to python.

**Anchor concept**: triage speed is a parsing skill. If you can answer "how many distinct source IPs failed auth in the last hour" in under 30 seconds with one line, you sound senior.

---

## Day 5 — Sigma Rule Syntax

**Reading (60 min)**
- Read SIGMA-PRIMER.md end to end
- Detection block: `selection`, `filter`, `keywords`
- Condition: `selection and not filter`, `1 of selection_*`, `all of them`
- Modifiers: `contains`, `endswith`, `startswith`, `re`, `cased`, `base64offset`, `windash`
- Logsource: `product`, `service`, `category` triple
- Falsepositives, level, tags (the ATT&CK reference goes here)
- sigma-cli (`pip install sigma-cli`): convert to Splunk, KQL, Elastic, Panther

**Lab**
- Take the brute force ssh detection from lab_01 and write three Sigma variants: one strict, one with a filter for known maintenance windows, one tuned for high-noise environments. Convert each to Splunk SPL and Sentinel KQL with sigma-cli.

**Anchor concept**: Sigma is where detection knowledge gets portable. Write rules in Sigma, deploy everywhere.

---

## Day 6 — TTP-Based vs IOC-Based Detection

**Reading (45 min)**
- The Pyramid of Pain (David Bianco): hashes (trivial), IPs (easy), domains (simple), network artifacts (annoying), host artifacts (annoying), tools (challenging), TTPs (tough)
- IOC fatigue: indicators rot in days, TTPs persist for years
- TTP detection means writing rules for behavior: "any process executes `whoami` followed by `net user /domain` within 60 seconds" beats "block IP 1.2.3.4"
- MITRE ATT&CK as the TTP taxonomy. Memorize Tactic IDs (TA0001 through TA0040). Drill the top 20 techniques (see CHEATSHEET.md).

**Lab**
- Read the SolarWinds Sunburst detection narrative (FireEye blog). Note: detection was via TTP (anomalous network beacon timing), not IOC.
- Open `lab_07_living_off_the_land`. Identify the technique IDs for each command in the kill chain.

**Anchor concept**: in interviews, when asked "how would you detect X", anchor in the ATT&CK technique first, log source second, rule third.

---

## Day 7 — MITRE ATT&CK Navigator and Coverage Mapping

**Reading (45 min)**
- ATT&CK matrix (Enterprise, Cloud, Containers): Tactics across the top, Techniques down
- Sub-techniques (T1078.004 Cloud Accounts vs T1078.001 Default Accounts)
- ATT&CK Navigator: layer files, scoring, color heatmaps for coverage
- Detection coverage maturity: most teams claim 90%, real coverage is 30 to 40% with high-confidence detections
- ATT&CK Cloud Matrix specifically (Initial Access through Impact for AWS / Azure / GCP)

**Lab**
- Build a Navigator layer for your homelab. Score every technique with a Sigma rule that fires on Falco or Datadog as covered. Find your gaps. Pick three to close this week.

**Anchor concept**: coverage is a heatmap, not a percentage. Interviewers want to hear you talk about gaps, not claim full coverage.

---

## Day 8 — Hunting Hypothesis Generation

**Reading (45 min)**
- David Bianco's Hunting Maturity Model (HM0 through HM4)
- The TaHiTI methodology: trigger, hypothesis, investigation, conclusion
- Hypothesis structure: actor + action + asset + outcome. Example: "an attacker has obtained a developer's GitHub PAT and is cloning private repos from a non-corporate IP"
- Threat-informed defense: pick a threat actor (Scattered Spider, FIN7, APT29), read their reports, hunt for their TTPs in your env

**Lab**
- Pick three hypotheses for the CoreDirective stack:
  1. "An attacker has compromised an n8n credential and is exfiltrating Notion data via the orchestrator webhook"
  2. "A container in cd-service-* has been spawned with anomalous capabilities"
  3. "A Cloudflare API token has leaked and is being used to modify DNS records"
- For each, write the data sources you would query and the queries themselves.

**Anchor concept**: a hunt is a hypothesis plus a query plus a result. Without all three, it is not a hunt, it is curiosity.

---

## Day 9 — Triage Workflows

**Reading (45 min)**
- Read TRIAGE-PLAYBOOK.md end to end
- MTTD, MTTA, MTTR, MTTC: what each means, what good looks like (Mandiant says median dwell time was 10 days in 2024)
- Severity matrix: asset criticality (1 to 4) x threat severity (1 to 4) = priority (1 to 16)
- Escalation criteria: what triggers L1 to L2 to L3 to oncall page
- The 5 minute context rule: if you cannot tell what happened in 5 min, escalate

**Lab**
- Run `lab_12_falco_runtime_anomaly`. Triage 10 alerts. For each, write classification, criticality, action, and a 1-sentence comms summary.
- Time yourself: target under 5 min per alert.

**Anchor concept**: triage is a decision under time pressure. Frame every alert as a 5-step decision tree, not a free-form investigation.

---

## Day 10 — False Positive Tuning and Alert Fatigue

**Reading (45 min)**
- Why detections decay: env drift, new apps, infra changes, seasonal traffic
- Tuning levers: allowlists, suppression windows, threshold adjustment, enrichment, correlation
- The 80/20 of alert fatigue: usually 5 to 10 noisy rules drive 70% of volume
- Detection-as-code review: every rule has an owner, a test, a review cadence (quarterly minimum)
- Alert quality metrics: precision (TP / TP + FP), recall (TP / TP + FN), F1

**Lab**
- Take lab_01 ssh brute force rule. Add three filters: maintenance jumphost subnet, known scanner ASNs, dev environments. Re-run against the log. Show before/after volume.

**Anchor concept**: a tuned rule is one with a documented filter list and an owner. An untuned rule is technical debt.

---

## Day 11 — Detection-as-Code

**Reading (60 min)**
- Detection-as-code platforms: Panther (Python rules + YAML schema), Chronicle YARA-L, Elastic Detection Rules repo on GitHub, Sigma + sigma-cli, Splunk ES content updates
- The pipeline: rule in git -> CI runs unit tests -> staging deploy -> prod deploy with feature flag -> metrics dashboard
- Unit tests for detections: feed known-good log + known-bad log, assert rule fires only on bad
- Anti-pattern: clicking rules into the SIEM UI. No version control = no detection engineering.

**Lab**
- Build a tiny detection-as-code repo: 3 Sigma rules, 3 test fixtures (log samples), pytest harness that runs each rule against each fixture and asserts pass/fail. Push to a private GitHub repo.

**Anchor concept**: when interviewers ask "how do you ship detections", the answer is git, PR review, CI tests, staged rollout, metrics. Same as code.

---

## Day 12 — AI-Augmented Triage (the Dropzone use case)

**Reading (60 min)**
- Read Dropzone AI's blog (dropzone.ai/blog) and their published case studies. Note the framing: AI agents augment L1 analysts, do not replace them, drive throughput
- The AI SOC analyst pattern: alert in -> LLM reads enrichment context -> LLM writes investigation report -> human approves or rejects
- Why this works: 70% of alerts are routine and follow patterns, LLMs are good at routine pattern matching
- Risks: hallucinated conclusions, prompt injection in log fields, over-trust on the report
- Compare to other entrants: Prophet Security, Intezer Autonomous SOC, AirMDR

**Lab**
- Run `lab_10_llm_prompt_injection`. The lab includes an LLM gateway log with a prompt injection embedded in a user agent string. Detect it.
- Run `lab_11_agentic_tool_abuse`. Detect anomalous tool sequences in n8n execution logs.

**Anchor concept**: AI-augmented triage is a force multiplier on L1. The detection engineer's job becomes: write the rules that the AI agent investigates, audit the AI's investigation reports, tune the prompts.

---

## Day 13 — Modern SIEM and Detection Platforms (whirlwind)

**Reading (60 min)**
- Splunk ES + ESCU (Enterprise Security Content Update). SPL basics, `tstats`, data models, notable events
- Elastic Security: KQL, EQL (sequence detections), prebuilt rules
- Microsoft Sentinel: KQL, analytics rules, Fusion (ML-driven correlation)
- Chronicle (Google SecOps): YARA-L, UDM schema, parsers
- Panther: Python rules, scheduled queries, data lake on Snowflake
- Wazuh: open source, OSSEC fork, decoders + rules in XML, manageable for homelab
- Falco: runtime, syscall-level, default rules + custom YAML

**Lab**
- Pick one Sigma rule, convert it to: Splunk SPL, Sentinel KQL, Elastic KQL, Chronicle YARA-L, Panther Python. Use sigma-cli.
- This is interview gold: "I write in Sigma and convert to whatever the customer runs."

**Anchor concept**: tools are interchangeable, the underlying detection logic is not. Interviewers test logic, not vendor knowledge.

---

## Day 14 — Capstone: the End-to-End Detection

**Reading (30 min)**
- Re-read INTERVIEW-Qs.md. Practice the answers out loud for the top 10.
- Re-read TRIAGE-PLAYBOOK.md.

**Lab (90 min)**
- Pick lab_08 (cloud console takeover) or lab_10 (prompt injection).
- Write the detection end-to-end:
  1. Hypothesis (1 sentence)
  2. ATT&CK technique mapping
  3. Log source identification
  4. Sigma rule
  5. Sigma converted to Splunk + KQL via sigma-cli
  6. Test fixture (1 known-bad, 1 known-good)
  7. Triage playbook for when this fires (5 step decision tree)
  8. Tuning notes (3 expected false positives + filters)
  9. Coverage gap (what attacker variant would bypass this)
  10. Metrics to track (precision, recall, MTTA)
- Save as `capstone-<technique>.md`. This is your interview leave-behind.

**Anchor concept**: end-to-end is the senior signal. Anyone can write a rule. Senior engineers ship rules with tests, runbooks, tuning docs, and coverage gap notes.

---

## What to Drill First (if you only get one day)

Day 6 (TTP vs IOC + Pyramid of Pain) and Day 9 (Triage workflow). Those two together let you fake the rest. The Pyramid of Pain in particular shows up in every senior detection interview at AI-SOC vendors.

## Cert Adjacencies

- GCDA (GIAC Certified Detection Analyst): aligns with this curriculum
- BTL1 / BTL2 (Blue Team Level): hands-on with similar labs
- Splunk Certified Cybersecurity Defense Analyst (SPLK-5001): cheap, well respected
- ATT&CK Defender (MAD20): free, ATT&CK-specific

## Daily Pickup

End each day with one line in `/Users/et/cyber-squire-ops/CoreDirective/career/intensive-prep/05-detection-triage/PROGRESS.md`:
- Date, day number, what shipped, what surprised you, what to revisit.
