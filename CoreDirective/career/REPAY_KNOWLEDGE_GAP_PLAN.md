# Repay Knowledge Gap Plan

Study plan for the Repay Sr. Security Engineer interview pipeline. Organized by interview probability, not alphabetically. Top sections are the ones most likely to be asked. Bottom sections are nice-to-have.

**Rule of engagement:** the goal is not to become an expert in every topic. The goal is to speak fluently for 90 seconds about each topic without stumbling. Depth beats breadth only where the JD is explicit.

**Time budget assumption:** you have 3 to 7 days before the first technical round. If you only have 1 day, do Section 1, Section 2, and Section 11 only.

---

## Priority Matrix

| # | Topic | Interview Probability | Time to Fluent | ROI |
|---|-------|----------------------|----------------|-----|
| 1 | Splunk ES concepts and vocabulary | 95% | 4 hours | CRITICAL |
| 2 | Incident response articulation (Resilience fix) | 90% | 3 hours | CRITICAL |
| 3 | SPL writing patterns | 85% | 3 hours | CRITICAL |
| 4 | MITRE ATT&CK fluency (techniques, not just tactics) | 80% | 3 hours | HIGH |
| 5 | AWS security services: CloudTrail, GuardDuty, VPC flow logs, IAM | 80% | 4 hours | HIGH |
| 6 | Agentic SOC vendor landscape | 70% | 2 hours | HIGH |
| 7 | Threat hunting methodology | 70% | 2 hours | HIGH |
| 8 | EDR/XDR concepts | 60% | 2 hours | MEDIUM |
| 9 | Detection-as-code tools and workflow | 50% | 2 hours | MEDIUM |
| 10 | UEBA concepts | 40% | 1 hour | LOW |
| 11 | The articulation drill (voice practice) | 100% | ongoing | CRITICAL |

**Total time to fully prepared: ~28 hours.** Realistic with focus over 4 to 5 days.

---

## Section 1: Splunk Enterprise Security (ES) — 4 hours

This is the single most important gap. The JD explicitly says Splunk ES. You have Splunk Core production experience. You need to bridge honestly.

### What you need to know cold

**ES architecture:**
- ES is a **premium app** that runs on top of Splunk Enterprise. It costs extra ($$$, per GB/day on top of Enterprise license).
- ES provides: Incident Review, Notable Events, Risk-Based Alerting, Threat Intel Framework, Adaptive Response, Glass Tables, Swimlanes, Content Management.
- ES requires **data models** (CIM-accelerated) to work at scale. Without CIM normalization, ES correlation searches fail or run slow.
- ES ships with ~140 pre-built correlation searches out of the box. Most shops tune a subset and write their own.

**Key workflows:**

1. **Notable Events lifecycle:** Correlation search fires → generates a notable event → lands in Incident Review dashboard → analyst triages → assigns → comments → closes or escalates.

2. **Risk-Based Alerting (RBA):** Instead of one alert per detection, you assign risk modifiers (risk_object_type, risk_score, risk_message) to events. When a risk object (user, system, IP) accumulates enough score across multiple events, ONE high-fidelity notable fires. Cuts alert fatigue dramatically.

3. **Adaptive Response:** When a notable fires, ES can auto-trigger actions: enrich with threat intel, ping a SOAR workflow, open a ticket, run a script, pivot to an EDR. This is how ES integrates with an agentic SOC platform.

4. **Threat Intel Framework:** STIX/TAXII feeds, custom IOC lists, manual uploads. Each IOC gets matched against incoming events via lookup tables. Matches surface through correlation searches.

5. **Content Management:** ES has a built-in content library where correlation searches, dashboards, and use cases are version-controlled and shared across analysts. Detection-as-code extends this by managing content in Git with a CI/CD pipeline.

### Vocabulary table (drop these words verbatim)

| Term | What you say about it |
|------|----------------------|
| Notable event | "The atomic unit of alerting in ES. Fires when a correlation search matches. Lives in the Incident Review dashboard." |
| Correlation search | "A scheduled SPL search that generates notables when it matches. I tune them against CIM data models to stay performant." |
| CIM (Common Information Model) | "Splunk's normalized schema. Authentication, Network_Traffic, Malware, Change, etc. ES correlation searches run against CIM data models, not raw indexes." |
| Data model acceleration | "ES uses accelerated CIM datasets to run correlation searches at scale without scanning every event. Acceleration cost is disk but saves search time." |
| Risk-Based Alerting (RBA) | "Accumulates risk scores on objects across multiple low-confidence events. When the object crosses a threshold, one high-confidence notable fires. Cuts alert fatigue from 500 to 10." |
| Adaptive Response | "Auto-action on notables. Enrichment, containment handoff, ticketing, SOAR integration. I'd wire this to hand off to an agentic workflow for triage." |
| Incident Review | "The analyst UI for notables. Shows status, owner, urgency, risk score. Triage happens here." |
| Threat Intel Framework | "ES's built-in IOC management. STIX/TAXII, custom feeds, lookups. I'd operationalize new IOCs through this." |
| Asset and Identity Framework | "ES needs to know what systems and users exist. You feed it from AD, AWS, inventory systems. Without this, notables can't prioritize by risk." |
| Glass Tables | "Live dashboards for security leadership. Not usually on the engineer's critical path." |
| Content Management | "Where correlation searches and dashboards live in ES. Export, version, share. Detection-as-code extends this to Git." |
| Notable urgency | "ES calculates urgency from priority plus severity. Engineers tune this so the right notables surface first." |

### The honest bridge answer (memorize)

> "My production Splunk experience was on Splunk Enterprise for a 45-device PCI retail environment. I wrote SPL correlation searches, normalized log sources to CIM, built scheduled alerts, and tuned detection thresholds. I haven't operated Splunk ES in production specifically, but I've studied the ES architecture in depth: notable event lifecycle, Risk-Based Alerting, Adaptive Response, the Threat Intel Framework, and Asset and Identity. The detection engineering fundamentals are the same. What I'd ramp on in the first 30 days is the ES content management workflow and the specific tuning patterns for RBA risk objects and notable urgency. I'm confident I can get productive in ES within weeks because the underlying SPL and CIM skills transfer directly."

### Resources (free)

1. **Splunk Enterprise Security Content Updates (ES-CU)** — [splunkbase.splunk.com/app/3449](https://splunkbase.splunk.com/app/3449). Read the release notes. You'll see the actual correlation searches Splunk ships. Good for learning the shape of ES content.
2. **Splunk ES Fundamentals (Splunk Education free courses)** — search for "Using Splunk Enterprise Security" on education.splunk.com. Some modules are free.
3. **Splunk Risk-Based Alerting overview** — [splunk.com/en_us/blog/security/risk-based-alerting](https://www.splunk.com/en_us/blog/security/risk-based-alerting.html). Read it twice.
4. **Splunk Docs: Incident Review in ES** — [docs.splunk.com](https://docs.splunk.com). Just the overview pages, not the full manual.
5. **YouTube: SANS OFFICIAL "Splunk ES Tutorial"** — search on YouTube for recent walkthroughs (2024+). Watch one end-to-end.

### Self-test (you must answer all 3 cold)

1. "What's the difference between a correlation search and a notable event?"
2. "How does Risk-Based Alerting reduce alert fatigue compared to traditional correlation-based alerting?"
3. "Walk me through the lifecycle of a notable event from generation to closure."

---

## Section 2: Incident Response Articulation (Resilience Fix) — 3 hours

This is where you got cooked last week. Not a knowledge gap. An articulation gap. You know IR. You cannot say IR out loud under pressure. Fix: say it out loud 50 times.

### The canonical NIST 800-61 lifecycle

1. **Preparation** — runbooks, detection content, contact lists, tool access, training
2. **Identification (Detection & Analysis)** — alert fires, analyst confirms true positive vs false positive
3. **Containment** — short-term (stop bleeding) and long-term (stable clean state)
4. **Eradication** — remove the persistence, rotate credentials, patch vulns
5. **Recovery** — restore clean service, monitor for recurrence
6. **Lessons Learned** — post-incident review, detection improvement, runbook updates

### Your verbatim IR answer (practice out loud 20 times)

> "I follow NIST 800-61. Preparation is runbooks, detection content, and access to the tools. Identification is triaging an alert in the SIEM — in my case Splunk — pivoting across authentication, network, and endpoint indexes to build a timeline and confirm true positive. Containment depends on the indicator: isolate a host through EDR, disable an account in AD or the IdP, block an IP at the firewall or at Cloudflare, or revoke a token in AWS through IAM. Eradication is removing persistence, rotating credentials, and patching the root vulnerability. Recovery is restoring clean service and monitoring for recurrence. Lessons learned feeds new detection content and runbook updates. My concrete example is at Texaco, where I built a 6-step IR runbook that took our average containment time from 8 hours down to 90 minutes."

### The containment action matrix (memorize the surfaces)

| Surface | Containment action | Tool example |
|---------|---------------------|--------------|
| Endpoint | Host isolation | Crowdstrike, SentinelOne, Defender for Endpoint |
| Network | Block IP, null route | Firewall ACL, Cloudflare, edge router |
| Identity | Disable account, force password reset, revoke tokens, terminate sessions | AD, Okta, Azure AD, Keycloak |
| Cloud (AWS) | Detach IAM policy, rotate access keys, revoke STS session, stop EC2, block S3 access | AWS CLI, IAM console |
| Email | Quarantine, delete from mailboxes, block sender | Proofpoint, Defender, Google Workspace |
| Application | Kill session, revoke API key, feature flag kill switch | App layer |

### The Texaco POS skimmer war story (your concrete example)

You have ONE real story on your resume. Use it. Memorize the details.

> "At one of our retail locations we had a POS skimmer investigation. Detection came from a combination of Splunk alerts on anomalous outbound traffic and a physical inspection tip from the location manager. I pulled Wireshark captures to confirm the skimmer device was beaconing out. I isolated the affected register from the network, preserved the evidence including the captures and the device image, coordinated with our payment processor for card brand notification per PCI DSS 12.10 incident response requirements, rotated credentials on every system that touched the compromised terminal, and validated the clean state with a follow-up network scan. Post-incident, I tightened segmentation by rebuilding the flat network into 4 VLANs separating POS payment traffic, back-office, guest Wi-Fi, and management. Lateral movement between segments went to zero."

This story hits: Splunk, Wireshark, containment, evidence preservation, PCI DSS, credential rotation, segmentation, VLANs, validation. It's a ONE-STORY answer for nine interview questions.

### The articulation drill

- Open voice memo on your phone. Record yourself saying the IR answer three times in a row without notes.
- Listen to the playback. Mark where you stumble, hedge, or forget a step.
- Re-record until you can say it in under 90 seconds without stumbling.
- Do the same thing for the POS skimmer story.
- Do the same thing for the Splunk ES bridge answer from Section 1.

**This drill is the single highest-ROI hour of your prep week. Do it tonight.**

### Resources

1. **NIST SP 800-61 Rev 2 (Computer Security Incident Handling Guide)** — [nvlpubs.nist.gov](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r2.pdf). Read Section 3 (the lifecycle). Skip the rest. 90 minutes.
2. **SANS IR playbooks** — search "SANS incident response playbook" and download any free ones. Used for muscle memory on the steps.
3. **Krebs on Security POS skimmer archive** — read two or three real-world writeups to refresh terminology and details you'll reference.

### Self-test

1. "Walk me through how you'd investigate a suspected compromised AWS IAM user."
2. "What's the difference between short-term containment and long-term containment, with an example of each?"
3. "An alert fires in Splunk for anomalous PowerShell execution on a workstation. What's your next 10 minutes?"

---

## Section 3: SPL Writing Patterns — 3 hours

You will be asked to write or describe SPL. You don't need to be a wizard. You need to know the 10 patterns that cover 80% of detection engineering.

### The 10 patterns you must recognize and talk through

#### 1. Basic filtered search
```
index=security sourcetype=auth action=failure user=* 
| stats count by user, src_ip 
| where count > 10
```
Talk: "Filter to failed auth events, count per user and source IP, surface anyone with more than 10 failures."

#### 2. Timechart for anomaly detection
```
index=cloudtrail eventName=AssumeRole 
| timechart span=1h count by userIdentity.userName
```
Talk: "Bucket by hour to see who's assuming roles abnormally often."

#### 3. Lookup against known IOCs
```
index=dns 
| lookup threat_intel_feed domain AS query OUTPUT threat_type, first_seen 
| where isnotnull(threat_type)
```
Talk: "Join DNS queries against a threat intel lookup to catch known malicious domains."

#### 4. Transaction for session reconstruction
```
index=web sourcetype=access_log 
| transaction JSESSIONID startswith="login" endswith="logout" 
| where duration > 3600
```
Talk: "Group events into sessions to find sessions lasting over an hour."

#### 5. Stats on rare events
```
index=proxy 
| stats count by user_agent 
| sort + count 
| head 20
```
Talk: "Sort user agents ascending to find rare ones, which often indicates malware C2."

#### 6. Correlation across indexes
```
(index=auth action=success user=admin) OR (index=firewall action=block src=admin_host) 
| stats values(action) by _time, user
```
Talk: "Correlate successful auth with firewall blocks from the same host to catch post-exploit movement."

#### 7. Anomaly detection with eventstats
```
index=cloudtrail eventName=ConsoleLogin 
| eventstats avg(login_count) as avg_logins by userIdentity.userName 
| where login_count > avg_logins * 3
```
Talk: "Baseline average logins per user, surface anyone logging in 3x their normal rate."

#### 8. Geolocation of threats
```
index=vpn action=success 
| iplocation src_ip 
| stats dc(Country) as country_count by user 
| where country_count > 1
```
Talk: "Find users successfully authenticating from multiple countries in the same window. Classic impossible travel detection."

#### 9. Process tree analysis for endpoint
```
index=endpoint EventCode=1 
| stats values(parent_process) by process 
| where mvcount(values(parent_process)) > 5
```
Talk: "Find processes with too many different parents. Catches living-off-the-land binaries."

#### 10. Risk-based scoring (the ES-adjacent pattern)
```
index=security 
| stats sum(risk_score) as total_risk by user 
| where total_risk > 100
```
Talk: "Accumulate risk scores per user across multiple events. This is the core RBA pattern before ES productizes it."

### Resources

1. **Splunk SPL Quick Reference** — Splunk docs. Download the PDF. 1 hour read.
2. **Splunk BOSS (Boss of the SOC)** dataset — free from Splunk. Practice SPL against real attack data. [splunk.com/en_us/blog/security/boss-of-the-soc](https://www.splunk.com/en_us/blog/security/boss-of-the-soc.html)
3. **SPLunk Tutorials on YouTube** — channel "Splunk How-To" has free short videos on each SPL command.

### Self-test

1. "Write an SPL query to detect anomalous S3 bucket access from a new country."
2. "How would you write a Splunk search to find brute force attempts against AD?"
3. "What's the difference between stats and eventstats?"

---

## Section 4: MITRE ATT&CK Fluency — 3 hours

You already know ATT&CK exists. You need to be fluent in techniques, not just tactics, and you need to map detections to specific techniques.

### The 14 tactics (top row of the matrix, memorize in order)

1. Reconnaissance
2. Resource Development
3. Initial Access
4. Execution
5. Persistence
6. Privilege Escalation
7. Defense Evasion
8. Credential Access
9. Discovery
10. Lateral Movement
11. Collection
12. Command and Control
13. Exfiltration
14. Impact

### The 20 techniques you must recognize by ID (out of 600+)

These are the highest-frequency techniques in real incidents:

| Technique ID | Name | What to say |
|--------------|------|-------------|
| T1566 | Phishing | "Initial Access. Spearphishing attachment, link, or service." |
| T1190 | Exploit Public-Facing Application | "Initial Access via web app or API vuln." |
| T1078 | Valid Accounts | "Initial Access or persistence through stolen or default credentials." |
| T1059 | Command and Scripting Interpreter | "Execution via PowerShell, bash, cmd, Python." |
| T1053 | Scheduled Task/Job | "Persistence via cron or Windows Task Scheduler." |
| T1547 | Boot or Logon Autostart Execution | "Persistence via registry run keys or startup folder." |
| T1548 | Abuse Elevation Control Mechanism | "Privilege escalation via UAC bypass or sudo abuse." |
| T1055 | Process Injection | "Defense evasion by injecting code into legit processes." |
| T1027 | Obfuscated Files or Information | "Defense evasion via encoding or packing." |
| T1003 | OS Credential Dumping | "Credential access via LSASS dump, Mimikatz, /etc/shadow." |
| T1110 | Brute Force | "Credential access via password guessing or spraying." |
| T1087 | Account Discovery | "Discovery of valid user accounts on a system." |
| T1018 | Remote System Discovery | "Discovery of other hosts on the network." |
| T1021 | Remote Services | "Lateral movement via RDP, SSH, SMB, WMI." |
| T1570 | Lateral Tool Transfer | "Lateral movement by copying malicious tools across hosts." |
| T1005 | Data from Local System | "Collection of files from the compromised host." |
| T1071 | Application Layer Protocol | "C2 over HTTP, HTTPS, DNS, mail." |
| T1041 | Exfiltration Over C2 Channel | "Exfiltration over the same channel used for C2." |
| T1486 | Data Encrypted for Impact | "Ransomware." |
| T1485 | Data Destruction | "Wiper attacks." |

### The ATT&CK-to-detection workflow

For each technique, you should be able to say:
- What the attacker does
- What telemetry source you'd use to detect it
- What specific signal you'd alert on

Example:
> "T1110 brute force: attacker tries many passwords against an account. Detect in Splunk with a correlation search on 4625 failed-auth events grouped by source IP. Alert threshold: 20 failures in 5 minutes. Tune out known scanner IPs. Convert to RBA risk score on the source IP so you don't drown in alerts."

### MITRE ATLAS (the AI version — your differentiator)

ATLAS is MITRE's ATT&CK matrix for adversarial ML and AI systems. Very few candidates know it. You do.

Top ATLAS tactics:
1. **Reconnaissance** — model probing, victim ML model discovery
2. **Resource Development** — adversarial data creation, acquire ML artifacts
3. **ML Model Access** — API access, query the model, physical environment access
4. **Initial Access** — prompt injection, supply chain (pip package, HuggingFace model), valid credentials
5. **ML Attack Staging** — craft adversarial data, build proxy model
6. **Exfiltration** — model weight exfiltration, training data exfiltration, prompt injection to leak
7. **Impact** — model evasion, external harms (denial of service, spam)

### Resources

1. **MITRE ATT&CK Navigator** — [mitre-attack.github.io/attack-navigator](https://mitre-attack.github.io/attack-navigator/). Free. Play with it. Build a sub-technique view for the top 20 above.
2. **MITRE ATLAS** — [atlas.mitre.org](https://atlas.mitre.org/). Read the matrix. 30 minutes.
3. **MITRE ATT&CK for Cloud (AWS matrix)** — [attack.mitre.org/matrices/enterprise/cloud/aws/](https://attack.mitre.org/matrices/enterprise/cloud/aws/). This is the specific matrix for the Repay use case.
4. **Atomic Red Team** — [github.com/redcanaryco/atomic-red-team](https://github.com/redcanaryco/atomic-red-team). Free library of ATT&CK technique tests. Useful for detection engineering context.

### Self-test

1. "Give me an example of a T1110 detection you'd write in Splunk."
2. "What's the difference between T1566 phishing and T1078 valid accounts as Initial Access vectors?"
3. "Name three MITRE ATLAS tactics that apply to an LLM-backed application."

---

## Section 5: AWS Security Services — 4 hours

Paul said AWS dominant. The JD underplays it but the client lives on AWS. You have honest Terraform + IAM + CloudTrail experience. You need to speak fluently about the native managed services you haven't run in production.

### Services to know by name and purpose

| Service | What it does | Key data source | What to say |
|---------|---------------|-----------------|-------------|
| CloudTrail | API audit log | Every IAM and service call | "My primary audit source. Every API call shows up here. I feed it into Splunk for correlation." |
| GuardDuty | Managed threat detection | VPC flow logs, DNS logs, CloudTrail, S3 logs, EKS audit | "AWS's managed threat detection. Ingests three data sources, outputs findings. Feeds into Security Hub." |
| Security Hub | Findings aggregator | GuardDuty, Config, Inspector, Macie, third-party | "The single pane of glass for security findings in AWS. Maps findings to AWS Foundational Security Best Practices and CIS benchmarks." |
| Config | Configuration compliance | Resource state changes | "Tracks configuration drift. Fires alerts when a resource violates a config rule. I'd use it for detection-as-code around IaC drift." |
| Inspector | Vulnerability scanning | EC2 instances, container images, Lambda | "Managed vuln scanner. Continuous assessment, no agents for EC2." |
| Macie | S3 data classification | S3 bucket contents | "Finds sensitive data in S3. PCI, PII, PHI classifiers. Critical for payment processors." |
| KMS | Encryption key management | Key usage and metadata | "Envelope encryption for data at rest. Customer managed keys for PCI scope. Key policies are the access control." |
| IAM | Identity and access management | IAM events in CloudTrail | "Least privilege through policies, SCPs at the org level, permission boundaries on developer roles, no long-lived access keys where I can avoid it." |
| IAM Access Analyzer | External access detection | IAM policy evaluation | "Scans for unintended public access to S3, IAM roles, KMS keys. Runs continuously." |
| VPC Flow Logs | Network telemetry | Source/dest IP, port, protocol, bytes, action | "Network layer visibility. Feed into Splunk for correlation with CloudTrail. Critical for AWS threat hunting." |
| Route 53 Resolver DNS Logs | DNS telemetry | Query, response, source | "DNS visibility. Catches C2 beacons and data exfiltration over DNS." |
| Detective | Investigation tool | CloudTrail, VPC flow logs, GuardDuty | "Graph-based investigation. Good for building timelines across services without writing SPL." |
| WAF | L7 protection | HTTP/HTTPS request logs | "OWASP Top 10 rules, rate limiting, bot control. Ingest into Splunk for detection." |

### The CloudTrail + GuardDuty hunt answer (memorize)

> "For AWS threat hunting, my primary sources are CloudTrail, VPC flow logs, and DNS logs from Route 53 Resolver. CloudTrail catches anything happening via API, which is where modern attackers live because they have stolen credentials. GuardDuty surfaces known patterns automatically, things like cryptojacking, unusual API calls from known bad IPs, or credential exfiltration to an unusual ASN. VPC flow logs give me network-layer context to confirm what GuardDuty alerts on. DNS logs catch beacons and DNS tunneling exfiltration. I'd feed all of these into Splunk ES for correlation, baselining, and hypothesis-driven hunts on top of the GuardDuty managed detections."

### The honest AWS scope answer

> "My production AWS experience is on the IaC and IAM side. I've run EC2 through Terraform, hardened IAM with least privilege and service control policies, used CloudTrail as my audit source, and managed KMS keys for data at rest. I have studied GuardDuty, Security Hub, and Inspector for SecurityX and for my own research, but I haven't operated them in a production enterprise. The underlying telemetry is familiar because I already work with CloudTrail and VPC flow logs in principle. I'd ramp on the managed services fast because the finding model is the same: source, severity, resource, recommendation."

### Resources

1. **AWS Well-Architected Security Pillar** — [docs.aws.amazon.com/wellarchitected/latest/security-pillar/](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/). Read once. 2 hours.
2. **AWS GuardDuty Finding Types** — [docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-active.html](https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-active.html). Scan the finding catalog. Memorize 5 to 10 finding names so you can reference them in conversation.
3. **AWS Security Reference Architecture (SRA)** — [docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/](https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/). The AWS reference for how security services fit together. 1 hour skim.
4. **Attacking and Defending AWS (Rhino Security Labs)** — free blog posts and `pacu` tool. Useful to understand the attacker side of AWS.

### Self-test

1. "What are the three data sources GuardDuty ingests natively?"
2. "How would you detect an attacker using a stolen IAM access key?"
3. "What's the difference between IAM policies, SCPs, and permission boundaries?"

---

## Section 6: Agentic SOC Vendor Landscape — 2 hours

The JD says "coordinate with vendor resources to implement multi-agent LLM-powered workflows." Repay has a vendor. You should know the major players so you can recognize the name when they tell you.

### The vendor shortlist (as of 2026)

| Vendor | Product | Positioning |
|--------|---------|-------------|
| Torq | Torq HyperSOC | Agentic SOC orchestration, LLM-native workflows, hyperautomation |
| Tines | Tines Workbench + Cases | SOAR + agentic workflows, popular with modern SOCs |
| D3 Security | Smart SOAR with MORPHEUS AI | Full SOAR with built-in agentic layer |
| Prophet Security | Prophet AI SOC Analyst | LLM-powered alert triage, tier-1 analyst replacement |
| Dropzone AI | Dropzone AI Analyst | Autonomous investigation agent, similar positioning |
| Hunters | Hunters AI SOC Platform | SIEM-adjacent with AI triage built in |
| Radiant Security | Radiant AI SOC | AI analyst workflow automation |
| Intezer | Intezer Autonomous SOC | Alert triage and memory forensics via AI |
| Exabeam | Exabeam Fusion | UEBA-heavy SIEM with AI correlation |
| Devo | Devo AI SOC Assistant | Logging platform with AI layer on top |
| CrowdStrike | Charlotte AI | EDR-native AI analyst embedded in Falcon |
| SentinelOne | Purple AI | EDR-native AI analyst in Singularity platform |
| Anvilogic | Anvilogic FDSE | Federated detection engineering, content platform |
| Panther | Panther AI | Detection-as-code native cloud SIEM |

### What to say when asked about your agentic SOC experience

> "I've been building and governing an agentic security stack on my own infrastructure for the last year. It's n8n as the orchestration layer with Claude Opus and local Ollama as the model layer, NeMo Guardrails on sensitive data flows, and RAG retrieval over runbooks and threat intel. It's not a vendor product — it's a hand-rolled stack for the governance side of the agentic SOC problem. I'm familiar with the vendor landscape though: Torq, Tines, Prophet, Dropzone, D3, and Hunters on the AI analyst side; CrowdStrike Charlotte and SentinelOne Purple on the EDR-native side. The common pattern across all of them is the same three-layer problem: orchestration, model governance, and human-in-the-loop approval gates."

### Vendor question you SHOULD ask in the interview

> "Who is the vendor on your agentic SOC platform? Is it one of the dedicated SOC AI vendors like Torq or Dropzone, or is it an EDR-native layer like Charlotte in CrowdStrike?"

This question does three things:
1. Shows you know the landscape
2. Tells them you read the JD carefully (vendor relationship was explicit)
3. Surfaces key information you need to know before day one

### Resources

1. **Gartner Magic Quadrant for AI in SOC** — if you can find a free download, do it. Otherwise search blog summaries.
2. **Each vendor's product page** — spend 10 minutes on each of Torq, Tines, Dropzone, Prophet, and D3. Read the positioning paragraphs. You just need to recognize the names.
3. **Reddit r/blueteamsec and r/cybersecurity** — search "agentic SOC" for recent discussion threads. Real practitioners talking about the vendors honestly.

### Self-test

1. "Name three vendors in the agentic SOC space and explain how they're differentiated."
2. "What's the difference between Tines and a traditional SOAR like Splunk SOAR (Phantom)?"
3. "Why would a payment processor choose an agentic SOC platform over expanding their traditional SOC headcount?"

---

## Section 7: Threat Hunting Methodology — 2 hours

The JD has a dedicated threat hunting section. Most candidates fumble this because they conflate hunting with alerting. Don't.

### The difference between alerting and hunting

- **Alerting** = rules firing on known patterns. Reactive. "We know what bad looks like, tell me when it happens."
- **Hunting** = hypothesis-driven search for unknown bad. Proactive. "I suspect X is happening. Let me look."

### The hunt loop (memorize)

1. **Form a hypothesis** based on threat intel, a TTP from ATT&CK, an incident at another org, or a gap in your detections.
2. **Identify the data sources** needed to test the hypothesis. Usually a mix of SIEM, EDR, network, and cloud telemetry.
3. **Build the query** to baseline normal and surface outliers.
4. **Investigate the outliers** manually. Pivot across indexes. Look at user, system, time, what happened before and after.
5. **Document findings** — true positive, false positive, or new detection opportunity.
6. **Productionize** the hunt into a correlation search or detection if it's worth keeping.
7. **Write the hunt report** so other analysts can reuse or extend the work.

### Your verbatim hunt answer

> "Hypothesis driven. I start with a specific TTP from ATT&CK or a piece of threat intel, identify which data sources cover the behavior, write a query to baseline normal and surface anomalies, pivot on outliers, document findings, and if the hunt is valuable I convert it into a correlation search so the detection is permanent. For cloud hunts specifically I focus on CloudTrail, VPC flow logs, and identity events, because that is where modern attackers live. For endpoint I focus on process trees, parent-child anomalies, and persistence mechanisms. Every hunt ends with a report so other analysts can extend or reuse it."

### Three hunt hypotheses you should have ready

**Hunt 1: Stolen IAM access keys**
> "Hypothesis: an attacker has stolen an IAM access key and is using it to enumerate resources before escalation. Data sources: CloudTrail, GuardDuty findings, VPC flow logs. Query: find principals calling List* or Describe* API actions from a source IP that doesn't match the principal's historical pattern. Pivot: check if the principal also calls AssumeRole or CreateUser after the enumeration. If yes, escalation in progress."

**Hunt 2: C2 beacons in DNS**
> "Hypothesis: malware is beaconing out through DNS to evade network controls. Data sources: Route 53 Resolver DNS logs or on-prem DNS server logs in Splunk. Query: find domains with regular query intervals (every 30 seconds, every 60 seconds), long subdomains (DNS tunneling), or domains with low lookup volume but recent first-seen. Pivot: check the source host for running processes and parent trees."

**Hunt 3: Living off the land PowerShell**
> "Hypothesis: an attacker is using native Windows tools to avoid dropping files. Data sources: Windows Event Logs 4688 process creation, Sysmon if available, EDR telemetry. Query: find PowerShell processes with encoded commands, unusual parent processes like Word or Outlook spawning PowerShell, or network connections from powershell.exe. Pivot: check for download activity and lateral movement attempts."

### Resources

1. **Sqrrl Threat Hunting Maturity Model** (now Amazon Detective) — foundational hunt methodology paper. Free PDF online.
2. **Threat Hunting Handbook (SANS)** — free PDFs available through SANS community.
3. **MITRE CALDERA** — free adversary emulation platform. You can run emulated attacks against a test env and practice hunting. Overkill for prep but useful for confidence.

### Self-test

1. "Give me a hunt hypothesis for detecting insider data exfiltration in an AWS environment."
2. "How do you measure the success of a hunting program?"
3. "What's the difference between a detection and a hunt?"

---

## Section 8: EDR/XDR Concepts — 2 hours

You have zero production EDR experience. Be honest, but speak the vocabulary.

### What EDR does

- Agent on the endpoint
- Captures process, file, network, registry, and memory telemetry
- Sends to a cloud backend for analysis
- Provides isolation (network quarantine), remediation (kill process, delete file), and forensics (timeline, process tree)

### The major EDR vendors

| Vendor | Product | Strength |
|--------|---------|----------|
| CrowdStrike | Falcon | Market leader, Charlotte AI layer, strongest threat intel |
| SentinelOne | Singularity | Autonomous response, Purple AI analyst |
| Microsoft | Defender for Endpoint | Tight Windows integration, free with E5 licensing |
| Palo Alto | Cortex XDR | Network + endpoint correlation |
| Sophos | Sophos Intercept X | SMB favorite |
| Trellix (McAfee + FireEye) | Endpoint Security | Legacy enterprise |

### XDR vs EDR

- **EDR** = endpoint only
- **XDR** = extended. Endpoint + network + cloud + email + identity correlated in one platform. Usually the EDR vendor adds other sources to compete with SIEM.

### The honest EDR answer

> "I haven't operated a specific EDR like Crowdstrike or SentinelOne in production. My endpoint detection work has been through Falco for runtime threat detection on containers and Datadog for endpoint telemetry ingestion. I understand the EDR model — agent, telemetry, backend analysis, host isolation, process tree forensics — and I speak the vocabulary. I'd ramp on a specific vendor quickly because the detection patterns are the same and the containment actions map onto what I already do in my current stack."

### Resources

1. **CrowdStrike Global Threat Report** (free PDF annually) — read the exec summary to understand current EDR vendor positioning.
2. **MITRE ATT&CK Evaluations** — [attackevals.mitre-engenuity.org](https://attackevals.mitre-engenuity.org/). MITRE tests EDR vendors against real APT TTPs. Read the 2024 or 2025 evaluation summaries.
3. **Reddit r/crowdstrike, r/sentinelone** — honest practitioner discussion.

### Self-test

1. "What's the difference between EDR and XDR?"
2. "How would an EDR detect a living-off-the-land PowerShell attack?"
3. "What containment actions can an EDR take from the console?"

---

## Section 9: Detection-as-Code — 2 hours

The JD explicitly mentions "detection-as-code pipelines." This is the practice of managing detection content in Git with a CI/CD pipeline instead of clicking around in the SIEM UI.

### The detection-as-code workflow

1. **Detection content lives in Git.** SPL correlation searches, Sigma rules, YARA rules, or whatever format your SIEM uses.
2. **Pull request workflow.** A detection engineer opens a PR with a new or updated detection.
3. **Automated tests.** CI runs the detection against test data (good and bad events) and validates it detects the bad and doesn't fire on the good.
4. **Code review.** Another engineer reviews the detection logic, tuning, and metadata.
5. **Deploy.** Merged PR auto-deploys the detection to the SIEM through an API or content management tool.
6. **Version controlled.** Git history shows who changed what and why.

### Tools in this space

| Tool | Purpose |
|------|---------|
| **Sigma** | Vendor-neutral detection rule format. Translates to SPL, KQL, Elastic, QRadar, etc. |
| **splunk-contentctl** | Splunk's official detection content lifecycle tool. Git-native. |
| **detection-engineering-process** (github.com/splunk/security_content) | Splunk's open-source content repo. Real examples. |
| **Elastic Detection Rules** (github.com/elastic/detection-rules) | Elastic's public repo with ~1000 rules in YAML. |
| **SOC Prime TDM (Threat Detection Marketplace)** | Commercial detection content library. |
| **Uncoder.io** | Free Sigma-to-SPL (and many other SIEMs) translator. |
| **Panther Analysis** | Panther SIEM's detection-as-code framework (Python). |

### Your verbatim answer

> "My CI/CD pipeline at CoreDirective already applies detection-as-code principles to infra: every Terraform change goes through OPA/Rego policy gates, Trivy and Semgrep scans, Gitleaks secrets detection, and a code review before merge. The same pattern extends to SIEM content: detections live in Git as Sigma rules or SPL searches, get tested in CI against known-good and known-bad events, get peer-reviewed, and deploy through an API or content management tool. For Splunk specifically, splunk-contentctl is the canonical tool and I've studied the Splunk Security Content repo on GitHub as the reference implementation."

### Resources

1. **Splunk Security Content (open source)** — [github.com/splunk/security_content](https://github.com/splunk/security_content). Read the repo README and browse a few detection YAML files. 30 minutes.
2. **Sigma HQ** — [sigmahq.io](https://sigmahq.io). Read the spec. 30 minutes.
3. **Detection Engineering Mindset (blog posts by Florian Roth, Anton Chuvakin)** — search their Medium and blog posts. Short, dense, excellent.
4. **Uncoder.io** — [uncoder.io](https://uncoder.io). Free tool. Translate a Sigma rule into SPL live. Play with it for 15 minutes.

### Self-test

1. "What's a Sigma rule and why use one instead of native SPL?"
2. "How would you build a CI pipeline for testing Splunk detection content?"
3. "How do you handle detection content that needs customer-specific data (IPs, hostnames, thresholds)?"

---

## Section 10: UEBA Concepts — 1 hour

UEBA is in the JD's required experience list but only briefly. Know the concept, not the products.

### What UEBA is

User and Entity Behavior Analytics. A layer on top of (or inside) a SIEM that baselines normal behavior per user and per entity (system, application) and surfaces anomalies.

### The UEBA detection pattern

1. Ingest user authentication, file access, system telemetry for 30 to 90 days
2. Build per-user baselines: normal login time, normal login locations, normal file access patterns, normal peer group behavior
3. Score deviations from baseline
4. Surface events where the deviation is statistically significant

### Classic UEBA detections

- Impossible travel (login from two geographically distant locations within a short window)
- Abnormal working hours access
- Peer group anomaly (user accessing resources nobody in their group accesses)
- Sudden privilege change (normal user starts accessing admin resources)
- Data hoarding (user downloads far more files than normal)

### Vendor landscape

- **Exabeam** — UEBA pioneer, now a SIEM
- **Securonix** — SIEM with UEBA core
- **Microsoft Defender for Identity** — UEBA for AD
- **Splunk UBA** — Splunk's UEBA add-on
- **Varonis** — file-access focused UEBA

### Your honest UEBA answer

> "UEBA is baseline-plus-anomaly detection for users and entities. I understand the model — 30 to 90 day baselines, statistical deviation scoring, peer group comparison — and the classic detections like impossible travel, abnormal hours, and peer group anomalies. I haven't operated a dedicated UEBA product like Exabeam or Securonix, but the pattern extends naturally from what I already do with Splunk correlation searches and eventstats for baselining. If your SIEM layer has UEBA built in I'd use it; if not, the same detections can be implemented in SPL with some effort."

### Self-test

1. "What's the difference between rule-based detection and UEBA?"
2. "Give me three classic UEBA detections."
3. "What's a peer group anomaly?"

---

## Section 11: The Articulation Drill — Daily Practice

Everything above is useless if you freeze up in the interview. Here's the drill.

### The 5 verbatim answers you must be able to say without notes

1. **Opener** (from REPAY_INTERVIEW_PREP.md Section 1) — 45 seconds
2. **Splunk ES bridge** (Section 1 of this doc) — 45 seconds
3. **NIST 800-61 IR lifecycle** (Section 2) — 60 seconds
4. **Texaco POS skimmer war story** (Section 2) — 60 seconds
5. **Agentic SOC oversight framing** (from REPAY_INTERVIEW_PREP.md Section 3) — 60 seconds

### The drill

- Voice memo on your phone.
- Record yourself saying each answer.
- Listen back. Mark every stumble, every hedge, every "um."
- Re-record until you can say it clean in one take.
- Do the full set three times a day for three days before the interview.

### The mock interview drill (with me)

When you're ready, say "ready" in this conversation and I will:
- Fire one question at a time
- Grade your answer on three axes: framework, vocabulary, concrete example
- Give you the repaired answer if yours had gaps
- Move to the next question
- 15 to 20 questions total
- By the end, your retrieval under pressure will be built

**This drill is more valuable than any of the study sections above.** The study sections fill gaps in what you know. The drill fills the gap in how you speak under pressure, which is the actual gap that burned you at Resilience.

---

## Daily Schedule (realistic)

Assuming interview is 5 days out and you have 2 to 3 hours per day:

**Day 1 (tonight):**
- Section 1 (Splunk ES) — 2 hours
- Section 2 (IR articulation) — 1 hour, say the NIST answer out loud 10 times

**Day 2:**
- Section 3 (SPL patterns) — 1.5 hours
- Section 4 (MITRE ATT&CK top 20 techniques) — 1 hour
- Drill: record opener + Splunk bridge

**Day 3:**
- Section 5 (AWS) — 2 hours
- Section 7 (Threat hunting) — 1 hour
- Drill: record IR answer + POS skimmer story

**Day 4:**
- Section 6 (Agentic SOC vendors) — 1 hour
- Section 9 (Detection-as-code) — 1 hour
- Section 8 (EDR/XDR) — 30 min
- Drill: full 5-answer set twice
- Run the mock interview with me (1 hour)

**Day 5 (interview day):**
- Morning: light review of Section 1 and Section 2 only
- 1 hour before: coffee, water, bathroom, quiet room
- Say all 5 answers out loud one last time
- Go.

---

## Final Rule

If you get asked about something not in this document: use the framework-plus-example pattern.

> "For [topic], my framework is [X]. In practice that means [Y]. The most concrete example from my experience is [Z]."

This pattern works for 90% of questions even when you don't know the specific answer. It signals senior thinking and buys you time to recover.

And if you genuinely don't know something, say so:

> "That's not something I've operated directly. Here's what I do know about the underlying concept, and here's how I'd approach learning it if I joined your team."

Honest beats fake every time. An interviewer who respects their own time respects a candidate who doesn't bluff.

---

You got this. One section at a time.
