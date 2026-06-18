# Detection Engineering Interview Questions

30 questions, senior-level answers, in Emmanuel's voice. Each answer 60 to 120 seconds when spoken. Reference real frameworks (Pyramid of Pain, MITRE ATT&CK, OWASP LLM Top 10), real tools (Sigma, Falco, Panther, Splunk ES), and real incidents (Capital One, SolarWinds, MOVEit).

When you do not know something cold, anchor in the framework first, then say "for example, in my homelab I detect this with Falco rule X." That earns the senior signal even when memory fails.

---

## 1. Walk me through how you would detect AWS credential exfiltration.

Three layers, and you need all three.

First, identity layer in CloudTrail. Watch `sts:GetCallerIdentity`, `iam:ListAccessKeys`, `iam:CreateAccessKey` from any source IP that is not in your corporate CIDR blocks or AWS service IP ranges. The Sigma rule is tight: filter on corporate space and AWS internal service space, alert on everything else.

Second, behavior layer. Same role calling 50 distinct API actions in 5 minutes is anomaly territory. Most legitimate roles call 5 to 10 actions in their lifetime. GuardDuty's `UnusualBehavior` and `CredentialAccess` finding types catch a chunk of this for free. I would still write Sigma on top because GuardDuty is not the only signal.

Third, the IMDS angle. Capital One in 2019 was SSRF to instance metadata to STS to S3. So I watch for `sts:AssumeRole` with credentials originating from an EC2 IMDS v1 token combined with the role being used from outside that EC2. CloudTrail surfaces the role session and source IP. If the source IP changes mid-session, that is escape velocity.

The kill chain pattern is GetCallerIdentity, ListBuckets, GetObject. Five events. If I see all five from a non-corporate IP within 10 minutes, I page oncall.

---

## 2. What is the Pyramid of Pain?

David Bianco's model from 2013. It ranks detection indicators by how painful they are for an attacker to change.

Bottom of the pyramid: file hashes. Trivial. A new build flips every hash.

Above that: IP addresses. Easy. Move to a new VPS.

Next: domain names. Slightly harder, costs DNS effort.

Then network and host artifacts. User agents, registry keys, file paths. Annoying to change.

Then tools. Cobalt Strike, Mimikatz, Sliver. Real engineering effort to swap.

Top: TTPs. Tactics, techniques, procedures. The way the attacker thinks. Changing TTPs means retraining the operator.

The point is detection strategy. If your whole detection program runs on hashes and IPs, you are detecting commodity malware that already burned. If you are detecting on TTPs, you are catching the actor across campaigns.

In interviews this is the answer when they ask why I write behavioral Sigma rules instead of just blocking IOC feeds.

---

## 3. How do you reduce alert fatigue?

Alert fatigue is a precision problem. The fix is engineering, not heroics.

Step one: instrument. Every detection has a precision metric. True positives over true plus false positives. Anything under 30 percent goes on the tuning queue.

Step two: identify the noisy rules. In most SOCs, 5 to 10 detections drive 70 percent of the volume. Pareto applies. Find them in 30 minutes by counting alerts per rule for the last 30 days.

Step three: tune at the rule level, not the alert level. Suppression in the SIEM UI for "this specific alert" is debt. Allowlist filters in the Sigma rule are code. The fix lives in the rule.

Step four: enrichment. An alert that arrives with the asset criticality, the user role, the geolocation, and the related events is faster to dismiss or escalate. Most of triage is gathering this context. Pre-compute it.

Step five: detection-as-code review cadence. Quarterly review of every rule. Owner, last fired, precision, action when fires. If it has not fired in 12 months and there is no documented hunting reason for it, retire it.

Sixth, the cultural piece. Analysts need permission to suppress. If suppressing means a 4 hour ticket, no one suppresses, fatigue compounds.

---

## 4. What is the difference between an alert, a detection, a hunt, and a signal?

A signal is raw telemetry. A line in a log file. No judgment attached.

A detection is rule logic that says "this signal pattern matters." It is the Sigma rule, the SPL search, the YARA-L statement.

An alert is the output of a detection firing on production telemetry. It has a severity, a context bundle, and a destination.

A hunt is a hypothesis-driven investigation. No detection has fired. The analyst believes something is happening and queries to prove or disprove it. Hunts produce new detections when they find something.

The mistake juniors make is treating alerts and detections as the same thing. They are not. A detection is the code. An alert is the runtime event. You write detections, you triage alerts, and you hunt to find what your detections missed.

---

## 5. How would you detect a prompt injection attack at the LLM gateway level?

Prompt injection has two flavors: direct, where the user types adversarial text, and indirect, where adversarial text arrives through a tool the agent fetches (a webpage, an email, a document).

For direct, log the raw prompt at the gateway. I run OpenClaw on my droplet so I see this end to end. Watch for OWASP LLM01 indicators: phrases like "ignore previous instructions", "you are now", "print your system prompt", role markers like `system:` injected into user content. A Sigma rule with a contains list gets you the first 80 percent.

For indirect, the better signal is the agent's tool-call sequence. If the agent fetches an external page or reads an email and within 30 seconds invokes a sensitive write tool (send email, push to git, share a Drive file), that sequence itself is the alert. I have a Sigma correlation rule for that on the n8n executions log.

Beyond syntax matching, you want a defense-in-depth model. Constrain the agent's tool surface. Treat all fetched content as untrusted. Strip or escape adversarial markers. Run a separate guard model that classifies prompts. None of this is detection alone, but a detection engineer needs to know the prevention layers to know what telemetry exists.

For metrics: I track injection attempt rate, agent tool sequences flagged as anomalous, and the rate at which sensitive actions are gated by human approval. That is the dashboard.

---

## 6. Describe a kill chain you defended against (or studied closely).

I studied SolarWinds Sunburst because it became the canonical supply chain detection case. The kill chain ran like this.

Initial access: trojanized DLL in the SolarWinds Orion update, signed with a real cert, distributed to 18000 customers. No detection at this layer for most.

Execution: the DLL waited 12 to 14 days post install before activating. That dormancy itself was the first detection signal. Anomalous timing.

C2: the DGA used DNS subdomains under avsvmcloud.com. Detection here was the Pyramid of Pain in action. Domains were rotating but the subdomain entropy and the timing pattern (regular intervals, jittered) was a TTP.

Discovery: the malware checked for AV products and analysis tools, then disabled itself if found. So the detection signal was process enumeration on hosts that had no business doing it.

Lateral and privilege: SAML token forgery via stolen ADFS keys. Golden SAML. The detection was Sigma rules on Sentinel and Splunk ES that watched for tokens with anomalous lifetime, anomalous signing key, and use against Microsoft Graph from non-corporate IPs.

What I take from this: defense in depth across layers, behavioral detection at the C2 layer, and identity telemetry as the last line. No single detection caught it. Composite detection across DNS, EDR, and identity logs caught it.

---

## 7. What metrics matter for a SOC?

Five metrics carry the weight.

MTTD, mean time to detect. From breach to first alert. The Mandiant 2024 M-Trends report had global median dwell time at 10 days. Best in class is under 24 hours.

MTTA, mean time to acknowledge. From alert to analyst eyes on it. SLA target is usually under 15 minutes for high severity.

MTTR, mean time to respond. From acknowledge to containment. Under 4 hours for high.

Detection coverage. Mapped to the MITRE ATT&CK matrix. What percent of techniques in scope have at least one high-confidence detection. Real numbers are 30 to 40 percent for mature teams. Anyone claiming 90 percent is counting commodity rules that fire on hashes.

Alert quality. Precision (TP rate), recall (caught vs missed), false positive volume. Tracked per rule.

Below those: analyst burn rate (alerts per shift), automation rate (alerts auto-resolved by playbook or AI agent), and after-action consistency (does every closed alert have a 1 line root cause and detection improvement note).

The bad metrics: alert volume by itself, hours of dashboard uptime, ticket count. Those measure activity, not outcomes.

---

## 8. How do you write a hunt hypothesis?

Four-part structure: actor, action, asset, outcome.

"An attacker [actor] who has obtained a developer's GitHub PAT [pre-condition] is cloning private repos [action] from a non-corporate IP [asset] and copying source to attacker-controlled infrastructure [outcome]."

That is testable. I can query GitHub audit logs for `git.clone` events grouped by user, filter to non-corporate source IPs, count clones per user per hour, and look for outliers.

The non-testable version is "we should hunt for credential theft." That is a wish, not a hypothesis.

The methodology I use is TaHiTI (Targeted Hunting integrating Threat Intelligence): trigger, hypothesis, investigation, conclusion. Trigger comes from threat intel, an incident in another org, or a coverage gap. Hypothesis is the four-part structure. Investigation is the queries. Conclusion is documented as either confirmed (now write a detection), disproven (now document why for future hunts), or inconclusive (more telemetry needed).

David Bianco's Hunting Maturity Model is the parallel framework. HM0 is no hunting. HM4 is automated, hypothesis-driven, with feedback into detection content. Most teams are at HM2.

---

## 9. What is detection-as-code?

Detection-as-code is treating detection content the same way you treat application code.

Rules live in git. Pull requests for changes. Code review by peers. CI runs unit tests, where each rule has known-good and known-bad log fixtures and the test asserts the rule fires only on bad. Staged deployment from dev to staging to prod. Feature flags for new rules so you can dark-launch and observe before alerting humans. Metrics and dashboards per rule.

Tooling examples. Panther uses Python rules with YAML schema and a built-in test framework. Chronicle uses YARA-L 2.0 with rule packs. Elastic publishes their detection rules in a public GitHub repo with full test coverage. Sigma plus sigma-cli plus pytest is the open stack for any SIEM.

The anti-pattern is the SIEM UI rule editor with no version history, no review, no tests. That is how you get 800 rules, half of which no one remembers writing.

The shift in mindset: detection engineers are software engineers. Same discipline, different domain.

---

## 10. How does Dropzone AI augment a SOC analyst?

Dropzone AI is in the AI SOC analyst category. The pattern is the same across the entrants (Prophet Security, Intezer Autonomous, AirMDR): an alert fires, the AI agent reads enrichment context, runs an investigation playbook, writes a structured report with a verdict, and either auto-closes (if benign with high confidence) or escalates with the report attached.

The augmentation, not replacement, framing matters. L1 analysts spend most of their time on context gathering. Pulling who owns this asset, what role this user holds, whether this IP has a clean reputation, what other alerts are correlated. The AI agent does that gathering in seconds. The analyst gets back a curated package and a recommendation. The analyst decides.

Where it works: routine alerts that follow patterns. Suspicious login from new geography. Unusual cloud API call from a known role. Most malware-flagged emails. The AI excels at the first 80 percent of investigation, which is also 80 percent of L1 volume.

Where it does not work yet: novel attack chains, sophisticated insider threat, sequences that span multiple systems and require pivoting across data sources the AI is not connected to. Senior analysts still own those.

The detection engineer's role shifts. You write rules, but you also tune the AI agent's prompts and audit its investigation reports for hallucinations. Every report is a test case for the agent's reasoning.

The capacity argument is honest. Not "AI replaces the analyst." It is "the team triages 5x more alerts at the same headcount and senior analysts spend their time on the 20 percent that actually matter."

---

## 11. What is the difference between Falco, auditd, and eBPF?

Three layers of the same stack.

eBPF is the kernel mechanism. A safe sandbox in the Linux kernel that lets you attach programs to syscalls, network events, scheduler events, anything the kernel does. eBPF is the engine.

auditd is a userspace daemon that consumes the kernel audit subsystem (which is a separate kernel mechanism, not eBPF). Rules go in `/etc/audit/rules.d/`, key-based correlation with `-k`, search with `ausearch`. auditd is portable across kernels and well documented but the rule language is verbose and the volume is high.

Falco is a runtime detection engine that can use eBPF (or kernel modules) as the data source. It maintains a higher-level rule language (YAML), ships with default rules covering hundreds of TTPs, and is the de facto standard for container runtime detection. It runs on my droplet covering the cd-service-* containers.

When to use each. Auditd if you need long-standing portable host audit on regulated systems. Falco if you need behavior detection in containers and Kubernetes. Raw eBPF (via tools like Tracee, BCC, or custom programs) if you need detection logic that Falco cannot express or you are building your own runtime tool.

The three are not competitors. A mature host has auditd for compliance and Falco for behavioral, and both might use eBPF underneath.

---

## 12. How would you detect lateral movement in Kubernetes?

Three log sources, three detections.

K8s audit log first. Watch for `pods/exec`, `pods/attach`, `pods/portforward` against high-value namespaces (kube-system, kube-public, anything holding secrets). Filter out service accounts (they should not be doing interactive exec). Sigma rule.

Falco second. Falco's default ruleset includes "Terminal shell in container" and "Mkdir binary dirs" and "Write below etc". These catch the post-exec activity, not just the API call. The pair (audit fired plus Falco fired) is high confidence.

Service account behavior third. A SA that suddenly uses a token from a pod IP outside its expected namespace is anomalous. Audit log has `user.username` like `system:serviceaccount:ns:name` and `sourceIPs`. Group by SA, alert on new source IP.

The Tesla cryptojacking case is the canonical example. Exposed K8s dashboard with no auth. Attacker created pods. The detection that should have fired: anonymous user creating pods. The detection that did fire: a year later, when AV caught the crypto miner egress.

---

## 13. Walk through how you would investigate a suspicious login alert.

Five-minute decision tree, then escalate or close.

Minute one: classify. Is the user real, is the asset real, is the time outside business hours, is the geo plausible.

Minute two: enrich. Pull recent login history for this user (any anomaly). Pull any concurrent alerts for the same user or same IP. Pull device posture if I have an EDR or MDM signal. Check IP reputation (GreyNoise, AbuseIPDB).

Minute three: pivot to other identity events. Did this session subsequently access privileged resources, escalate, change MFA settings, create access keys, share files outside the org. Those are the value-extraction steps. Their presence flips this from "suspicious login" to "compromised account."

Minute four: decide. If clean (known device, known geo, no suspicious post-login activity), suppress with a note. If unclear, ask the user via secure channel. If post-login activity is hostile, force credential rotation, kill active sessions, page oncall.

Minute five: document and feed back. Every triage produces a one-line root cause and a tuning suggestion. If this fires often on the same legitimate user pattern, the rule needs a filter.

The phrasing I use in handoff: "User X, asset Y, anomaly Z, evidence A, recommended action B, my confidence C." Five elements. Senior comms.

---

## 14. How do you handle a noisy detection that you cannot tune?

Four options, in order.

First, enrich. If the rule fires and the analyst can dismiss in 30 seconds with the right context bundle, the rule is fine. The problem is missing context. Add asset criticality, user role, related events.

Second, suppress with a documented filter. If a maintenance scanner runs every Tuesday at 3am from a known subnet, that is a filter, not a tune. Document it in the rule's `falsepositives` section. Rule stays high signal.

Third, downgrade severity. Some rules belong as informational signals that feed correlation, not as alerts. The rule still runs. It just does not page anyone. It contributes to a higher-order detection.

Fourth, retire. If the rule has not produced a true positive in 12 months and there is no compliance requirement to keep it, kill it. Detection debt is real. Removing rules is part of the job.

The wrong move is leaving the rule firing and ignoring it. Ignored alerts train analysts to ignore alerts. That is how breaches dwell.

---

## 15. What is the OWASP LLM Top 10 and which entries matter for detection?

OWASP's top 10 risks for LLM applications. From a detection standpoint:

LLM01 Prompt Injection: detect at the gateway with content matching plus tool sequence correlation.

LLM02 Sensitive Information Disclosure (2025 list): detect via DLP-style content scanning on model outputs. Patterns for keys, PII, internal hostnames.

LLM05 Improper Output Handling (2025 list): more a code review issue than a detection one. But you can detect downstream effects when the model output gets executed in a shell or rendered in a browser and triggers XSS or SSRF.

LLM06 Excessive Agency (2025 list): this is the agentic tool abuse case. Detect by monitoring tool call frequency, tool combinations, and approval bypass.

LLM10 Unbounded Consumption (2025 list, replaces older Model Theft framing): detect by API call patterns. Mass enumeration of completions, weight extraction attempts, runaway token spend.

I have detection for LLM01 and LLM08 on my OpenClaw gateway and n8n workflows. Those two are the ones that turn into incidents in production agentic systems.

---

## 16. Describe how you would build a detection coverage matrix.

Start with MITRE ATT&CK Navigator. Pull the relevant matrices: Enterprise, Cloud (AWS for me), Containers.

For each technique in scope, ask: do I have at least one high-confidence detection. High confidence means precision over 70 percent and the rule has fired on a real or simulated event in the last 90 days.

Score each cell. Three colors: covered, partial, gap.

Coverage gap analysis: which gaps matter. Initial Access and Execution techniques used by threat actors targeting your industry get priority. Use threat intel reports to weight: if FIN7 is hitting your peers and they use Phishing for Initial Access plus PowerShell for Execution, those should be covered first.

Coverage maturity is not just count. It is depth. A single Sigma rule for T1059.001 (PowerShell) is one cell covered. But T1059.001 has dozens of variants. Encoded commands, AMSI bypass, IEX downloads, obfuscation. Real coverage means rules for each major variant.

Output: a Navigator JSON layer file checked into the detection-as-code repo, refreshed quarterly, with a coverage report for leadership.

The honest answer in interviews: most teams are 30 to 40 percent on real depth. Anyone claiming 90 is counting wrong.

---

## 17. How do you onboard a new log source?

Six steps.

One, identify the data. What schema, what volume, what fields, what retention requirements. Get a sample.

Two, parser. If the SIEM does not auto-parse, write a parser. Test against the sample. Validate every field is typed correctly. Timestamps in UTC.

Three, baseline. Run for 7 to 14 days collecting telemetry without rules. Build statistical baselines for the high-cardinality fields.

Four, enrichment. Add asset metadata (CMDB lookup), identity metadata (HR system), threat intel (TI feeds). Do this in the ingest pipeline, not in the rule.

Five, detections. Start with the Sigma rules from SigmaHQ that match this product and service. Tune against your baseline.

Six, runbook and ownership. Every alert from this source has a documented response procedure. Source has a named owner. Owner reviews quarterly.

The mistake is going straight from data to detections without baselining. You ship rules that fire on normal traffic because no one looked at what normal looks like.

---

## 18. What is sequence detection and when do you use it?

Sequence detection looks for ordered events across time, not just a single event. The classic example is the Mandiant attack lifecycle: recon, weaponization, delivery, exploitation, installation, C2, actions on objective. Each step alone might be benign. The sequence is the threat.

Tools. Elastic EQL has `sequence` as a first-class operator. Sigma v2 has `correlation` rules with `temporal` type. Splunk has `transaction` and `streamstats`. Sentinel has `bin()` plus joins. Chronicle YARA-L has match windows.

When to use. When the individual events are too noisy to alert on but the order is rare. PowerShell launch alone: too noisy. PowerShell launch followed within 60 seconds by a `whoami` followed within 60 seconds by `net.exe user`: rare and high signal.

When not to use. When you can write a single-event detection with high precision. Sequence rules are heavier on the engine and harder to debug. Use them when you cannot avoid them.

---

## 19. How do you use threat intelligence in detection?

Three tiers.

Strategic intel: who is targeting your industry, what TTPs do they use. Drives the coverage matrix priorities. Read the annual reports (Mandiant M-Trends, CrowdStrike Global Threat Report, Verizon DBIR).

Operational intel: campaigns and TTPs from the last 90 days. Drives hunt hypotheses and short-term rule writing. Sources include Unit 42, Talos, Microsoft, Google TAG.

Tactical intel: IOCs. Hashes, IPs, domains. Drives short-lived blocklists and watchlists. Useful for the immediate response to a known incident, but per the Pyramid of Pain, IOCs rot fast. Do not build your detection program on them.

Practical workflow: subscribe to a few high-signal feeds, route through a TIP (MISP if open source), enrich every alert with TI lookups at ingest. When an IOC matches in alert context, that boosts severity. When an IOC is the only signal, flag it but do not page.

The bad pattern: dumping thousand-row IOC lists into the SIEM, getting hits on benign traffic, eroding trust in alerts. Curate, decay, attribute.

---

## 20. What is behavioral baselining and how do you do it?

Baseline means learning what normal looks like for an entity, then alerting on deviation.

Entities to baseline: users, hosts, service accounts, IP addresses, processes, API calls.

Dimensions to baseline: working hours, geographies, frequency of action, peer group similarity, command-line patterns.

Methods: simple statistical (mean plus 3 standard deviations), peer group comparison (this host vs others in its role), time-series anomaly (Holt-Winters or similar), ML-based (UEBA platforms like Exabeam or Splunk UBA).

Practical baselining without a UEBA platform: SQL or KQL window functions. `count() over partition by user, day` then alert on values above the user's 95th percentile. That gets you 70 percent of UEBA value for free.

The trap: baselines on small populations. If a user only logs in twice a week, every login looks anomalous. Need minimum sample size and confidence thresholds.

Use baselines as inputs to detections, not as detections themselves. "This user is anomalously active" by itself is not actionable. "This user is anomalously active AND accessed a resource they have never touched" is actionable.

---

## 21. How would you detect ransomware in progress?

Four signals, ordered by appearance in the attack.

One, initial access and persistence. Phishing landing, RMM tool abuse (LogMeIn, AnyDesk, ScreenConnect have all been abused recently), valid account use after suspicious login.

Two, recon. Network scanning from a workstation, AD enumeration, share enumeration. Bloodhound-style TTPs.

Three, lateral movement and privilege escalation. Pass-the-hash, SMB abuse, GPO modification, scheduled tasks on remote hosts.

Four, the action on objective: mass file modification. Volume of files written or renamed per minute spikes. File extensions changed at scale. Volume Shadow Copy deletion (`vssadmin delete shadows`). Backup tampering. RDP enabled on hosts that did not have it.

The actionable detection is signal four, but by then the encryption is starting. So the value detections are signals one through three. That is where you get hours of warning.

Specific rules I would have. Sigma for `vssadmin delete shadows`, Sigma for `wmic shadowcopy delete`, Sigma for unusual SMB write volume, Falco for mass file modification in a container, EDR for credential dumping behavior.

Recent reference: the MOVEit incident in 2023 by Cl0p. Initial access was zero-day exploitation, but the lateral and exfil phases had detection opportunities that most victims missed.

---

## 22. What is Sigma and why does it matter?

Sigma is the open standard for SIEM detection rules. YAML format, vendor-neutral logic, converts via sigma-cli to Splunk, Elastic, Sentinel, Chronicle, Panther, Wazuh, and others.

Why it matters. Detection knowledge becomes portable. The rule I write today against my homelab Datadog could deploy to a Splunk shop tomorrow with one command. The community SigmaHQ repo has thousands of free rules. Vendor lock-in stops being a moat for detection content.

What it does not do. Sigma is logic only. It does not handle ingestion, parsing, enrichment, or response. Those still live in the SIEM. So Sigma plus a SIEM, not Sigma instead of one.

Limitations. Correlation support is uneven across backends. Some advanced patterns (windowed counts, joins) require backend-specific extensions. Read the converted query before deploying.

In interviews I cite Sigma because it signals you read detection content as code, not as vendor-specific recipes.

---

## 23. How do you test a detection rule?

Three layers.

Unit test. Two log fixtures: one known-bad that should fire, one known-good that should not. Run the rule against both. Assert correct behavior. CI runs this on every PR.

Integration test in staging. Deploy the rule to a non-prod SIEM index. Replay 7 to 30 days of historical telemetry. Count fires. If it fires hundreds of times in staging, it will fire thousands in prod. Tune before promotion.

Adversary emulation. Use Atomic Red Team or Caldera to actually execute the technique on a test host and verify the rule fires. This catches bugs that synthetic logs miss because the rule was written against assumed log shapes that do not match real telemetry.

Bonus: chaos test. Periodically have a peer modify the technique slightly (add an obfuscation, change a flag) and confirm whether the rule still catches it. Brittle rules surface here.

Without tests, detections rot silently. Schema drift, parser changes, infrastructure migrations all break rules quietly.

---

## 24. What is the difference between IDS and EDR and SIEM and XDR?

IDS, intrusion detection system, is network-layer. Signature plus anomaly detection on packet data. Suricata, Snort, Zeek (technically a network monitor more than an IDS but same shelf).

EDR, endpoint detection and response, is host-layer. Agent on every endpoint capturing process, file, network, registry. CrowdStrike, SentinelOne, Defender for Endpoint, Carbon Black.

SIEM, security information and event management, is the log lake plus correlation engine. Splunk, Elastic, Sentinel, Chronicle, Panther, Sumo. Ingests from everything.

XDR, extended detection and response, is the marketing umbrella. Vendor-controlled stack of EDR plus identity plus email plus cloud telemetry, all correlated by the vendor. Microsoft Defender XDR, Palo Alto Cortex XDR, CrowdStrike Falcon Insight XDR.

Practical view. Mature programs run all four layers. SIEM as the historian and correlation hub. EDR as the host detection and response layer. NDR or IDS as the network layer. XDR is convenient if you already bought the stack, painful if you have to add a layer outside it.

For a detection engineer, the SIEM and the EDR are where you live. The IDS is a feed into the SIEM. The XDR is a customer's deployment choice you adapt to.

---

## 25. How do you detect insider threat?

Hardest detection problem. The user is authorized. The actions are often allowed. The signal is in deviation and intent, not in policy violation.

Three signal categories.

Behavioral. Volume and pattern shifts. The salesperson who downloads 10x their normal CRM record count in a week. The engineer who clones 50 repos they have never touched. The HR rep who exports the employee directory. UEBA tools (Exabeam, Splunk UBA, Microsoft Insider Risk) automate this but you can build the basics with windowed SQL.

Contextual. Actions during sensitive periods. Resignation notice given, then access patterns change. Performance plan started, then data hoarding begins. This requires HR data integration. Sensitive but powerful.

Movement. Data exfiltration channels. Personal email, Dropbox, USB writes, screenshot floods, print jobs. DLP-style monitoring on egress.

The ethical and legal layer matters. Insider threat programs without HR, legal, and privacy review become hostile workplaces fast. The detection engineer's job is to surface signal, not to investigate. Investigation goes to a designated team.

Anchor case: the Ubiquiti insider in 2020 to 2021. Senior engineer with admin access exfiltrated data, then extorted the company. Detection failed at the egress layer. Detection succeeded at the IP forensics layer post-incident.

---

## 26. How do you detect a phishing campaign at scale?

Layered. Email gateway plus identity plus endpoint plus user reporting.

Email gateway: ML-based content scoring, sender reputation, header analysis, attachment sandboxing, URL rewriting plus time-of-click checks. Microsoft Defender for Office 365, Proofpoint, Mimecast.

Identity: failed logins, MFA fatigue patterns (push spam), token theft patterns (Adversary in the Middle kits like Evilginx leave fingerprints in session cookies). Entra ID sign-in logs are the source. Sigma rules for impossible travel, anomalous app consent grants, illicit consent grants.

Endpoint: phishing payloads land here. Process behavior post-click. Office spawning PowerShell, child processes touching Outlook data. EDR detections.

User reporting: a single button in the email client that submits the message to the SOC. Best signal you can have. Drives the most accurate phishing detection corpus.

Modern variant: AiTM phishing (Microsoft 365 token theft via reverse proxy). The detection signal is the session token characteristics, not the credential. Token replay from a non-corporate IP. Token used outside its expected device fingerprint. This requires Conditional Access logging plus continuous access evaluation logs.

---

## 27. What is a kill switch and when do you use one?

A kill switch is a pre-built response action that an analyst or an automated playbook can invoke to immediately contain an incident. Disable user account, isolate host from network, revoke OAuth tokens, rotate API keys, kill running container.

When to use. High-confidence detections where the cost of a false positive (one user disabled for 5 minutes) is much less than the cost of a false negative (15 more minutes of attacker access).

How to use. SOAR platform (Splunk SOAR, Microsoft Sentinel automation, Tines, Torq, n8n for me). Playbook is approved code. Triggered by a high-severity alert. Logs every action for after-action review.

Reverse considerations. Kill switches need rollback. Disabled the wrong user? One click to restore. Automation without rollback is a service ticket waiting to happen.

The frame for interviews: detection without response is observation. Response without detection is panic. Detection plus tested response is operational security.

---

## 28. How do you scale detection in a large environment?

Scale is a data engineering problem first, detection problem second.

Data tier. Hot index for last 30 days, warm for 90, cold for 1 year, frozen for compliance retention. Different storage costs. Most queries hit hot. Schema-on-read or schema-on-write depending on platform.

Query tier. Pre-aggregate where possible. Splunk data models, Elastic transforms, Chronicle data tables. The cost of a real-time correlation across raw events at petabyte scale is brutal. Pre-aggregations cut that by 100x.

Rule tier. Tiered detection. Cheap rules that filter at ingest (drop noise). Mid-tier rules in the SIEM (most detections live here). Expensive rules in batch jobs (nightly hunts that crunch 30 days of data). Match the rule cost to the value.

Org tier. Detection engineering team separate from L1 SOC. Engineers ship rules, analysts triage. Without separation, you get ad-hoc rule writing under alert pressure and the content quality collapses.

Platform tier. Detection-as-code repo, CI pipeline, staging environment, metrics dashboards. Cannot scale humans without scaling tooling.

The number to know: most enterprise SIEMs ingest 1 to 10 TB per day. Petabyte-class deployments exist (the FAANG and similar). Most environments are not bottlenecked on detection logic. They are bottlenecked on ingestion cost and query performance.

---

## 29. What is the difference between IOCs, IOAs, and IOBs?

IOCs, indicators of compromise. Static artifacts. Hashes, IPs, domains, file paths, registry keys. Bottom of the Pyramid of Pain.

IOAs, indicators of attack. Behaviors. Lateral movement patterns, recon command sequences, persistence mechanisms. Top of the Pyramid.

IOBs, indicators of behavior. Newer term. Tracks normal-vs-anomalous patterns of an entity. Bridges UEBA and detection. The salesperson opening 200 internal documents is an IOB if they normally open 20.

The taxonomy matters in interviews because it signals you understand detection evolution. Early SOCs ran on IOCs. Modern SOCs run on IOAs and IOBs because IOCs rot.

CrowdStrike popularized IOAs in marketing. The substance is real: behavioral detection beats indicator detection at scale.

---

## 30. Walk me through your detection engineering toolkit.

What I would build out for a $200K AI Security role:

Sigma plus sigma-cli for portable rule writing. Every detection lives in a git repo as a YAML file.

A test harness: pytest plus log fixtures. Every rule has at least one true-positive log and one true-negative log. CI runs them on every PR.

A SIEM, vendor depending on the role. I have a Datadog homelab. I have studied Splunk SPL, Sentinel KQL, Elastic KQL, Chronicle YARA-L, Panther Python.

Falco for runtime detection on containers. Default ruleset plus my custom YAML.

MITRE ATT&CK Navigator JSON layers for coverage tracking, refreshed quarterly.

A SOAR or workflow engine for response. I run n8n. The same machine that automates detection feeds also runs the response playbooks.

An LLM gateway for AI-augmented triage. OpenClaw on the droplet. Custom skills for log analysis.

Threat intel feed (open: AlienVault OTX, abuse.ch, GreyNoise free tier). Integrated at ingest, decay rules in place.

Playbooks in markdown in the same repo as the rules. Every alert has a runbook. Every runbook has an owner.

Metrics. Per-rule precision tracker. Per-source ingest volume. MTTA, MTTR, MTTC reported weekly.

The frame: this is the same stack a senior detection engineer at Dropzone, Snowflake security, Datadog security, or any AI-forward shop runs. Open-source heavy, vendor-neutral logic, automation throughout.
