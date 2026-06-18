# Final Chart — Read at 11 AM and 12:30 PM EDT

**Interview:** Thu May 7, 2026, 12:45 PM EDT (Eastern Daylight Time)
**Interviewer:** Eric Hammerle, Director of Engineering, Dropzone AI
**Meeting:** [meet.google.com/bbs-zevf-fmh](https://meet.google.com/bbs-zevf-fmh)

---

## 1. Identity (locked)

| Field | Answer |
|---|---|
| Name | Emmanuel Tigoue |
| Title | AI Security Engineer at CoreDirective |
| Employer framing | "My employer CoreDirective" — never "my startup" or "my company" |
| What CoreDirective is | "An AI security practice. We anchor on an accounting firm client and serve SMB and mid-market on the same problem you solve for the enterprise. I'm the engineer." |
| If asked if you own it | "I'm the founding engineer and the practice operates as my LLC (Limited Liability Company)." Do not volunteer. |
| Years framing | "Four and a half years direct security engineering. Eight years total IT (Information Technology). Density over tenure." |
| Cert stack | CISSP (Certified Information Systems Security Professional) in progress. SecurityX (CompTIA Advanced Security Practitioner). SSCP (Systems Security Certified Practitioner). CCNA (Cisco Certified Network Associate). Sec+ (CompTIA Security Plus). |
| Education | May 2026 graduation. Do not lead with this. |

---

## 2. Red thread + three metrics

| Item | Memorize verbatim |
|---|---|
| Red thread | "I care about investigation quality. I've done it as a human, I've built systems for it, and I want to ship it at scale to every SOC (Security Operations Center) in the world." |
| Metric 1 | Falco eBPF (extended Berkeley Packet Filter): 200/day to 12 actionable |
| Metric 2 | Splunk MTTD (Mean Time To Detect): 48 hours to under 4 |
| Metric 3 | IR (Incident Response) runbook: 8 hours to 90 minutes containment |

---

## 3. Acronyms — spelled out

| Acronym | Spelled out | Quick context |
|---|---|---|
| AI | Artificial Intelligence | |
| ARN | Amazon Resource Name | AWS resource identifier |
| ATLAS | Adversarial Threat Landscape for Artificial-Intelligence Systems | MITRE framework, AI/ML version of ATT&CK |
| ATT&CK | Adversarial Tactics, Techniques, and Common Knowledge | MITRE framework for adversary behavior |
| AWS | Amazon Web Services | |
| BIN | Bank Identification Number | First 6 digits of card |
| CASP+ | CompTIA Advanced Security Practitioner Plus | Renamed SecurityX |
| CCNA | Cisco Certified Network Associate | |
| CIS | Center for Internet Security | |
| CISSP | Certified Information Systems Security Professional | |
| DAST | Dynamic Application Security Testing | |
| DHCP | Dynamic Host Configuration Protocol | |
| DNS | Domain Name System | |
| DoS | Denial of Service | |
| eBPF | extended Berkeley Packet Filter | Kernel level event tracing |
| EC2 | Elastic Compute Cloud | AWS virtual machines |
| EDR | Endpoint Detection and Response | |
| FP/FN | False Positive / False Negative | |
| FTE | Full Time Equivalent | |
| GA | Generally Available | Product launch state |
| GRC | Governance, Risk, and Compliance | |
| IAM | Identity and Access Management | |
| IC | Individual Contributor | Non-manager engineer |
| IPv4 | Internet Protocol version 4 | |
| IR | Incident Response | |
| JD | Job Description | |
| JSON | JavaScript Object Notation | |
| LLC | Limited Liability Company | |
| LLM | Large Language Model | |
| MITRE | Not an acronym | Federally funded R&D corporation |
| MTTD | Mean Time To Detect | |
| MTTR | Mean Time To Respond / Recover | |
| NDR | Network Detection and Response | ExtraHop's category |
| NeMo | NVIDIA Neural Modules | LLM toolkit and guardrails |
| NIST AI RMF | National Institute of Standards and Technology AI Risk Management Framework | |
| OPA | Open Policy Agent | Policy as code engine, uses Rego |
| OSCAR | Obtain, Strategize, Collect, Analyze, Report | Dropzone's investigation framework |
| OWASP LLM Top 10 | Open Worldwide Application Security Project Large Language Model Top 10 | |
| PCI DSS | Payment Card Industry Data Security Standard | |
| PII | Personally Identifiable Information | |
| PMM | Product Marketing Manager | Tyson Supasatit's role |
| POA&M | Plan of Action and Milestones | GRC artifact |
| POS | Point of Sale | |
| PSC | Problem, Specifics, Consequence | Your answer structure |
| RSAC | RSA Conference | RSA Security's annual conference |
| S3 | Simple Storage Service | AWS object storage |
| SaaS | Software as a Service | |
| SIEM | Security Information and Event Management | |
| SOAR | Security Orchestration, Automation, and Response | |
| SOC | Security Operations Center | |
| SSCP | Systems Security Certified Practitioner | ISC2 cert |
| SSP | System Security Plan | GRC artifact |
| STAR | Situation, Task, Action, Result | Behavioral story format |
| STRIDE | Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege | Threat modeling framework |
| TLS | Transport Layer Security | |
| TTL | Time To Live | Cache expiry |
| VLAN | Virtual Local Area Network | |
| VP | Vice President | At JPMC (JPMorgan Chase) it's an IC band, not exec |
| WHOIS | Who Is | Domain registration lookup |

---

## 4. Five step triage (OSCAR underneath)

| Step | Verb | What you do | Exit condition |
|---|---|---|---|
| 1. Scope the signal | Obtain | Read the alert, name the entities, flag missing data | One sentence with entities named |
| 2. Hypothesize before query | Strategize | Three working theories. Most likely, second, worst case | Three hypotheses + one query plan |
| 3. Collect cheapest first | Collect | Run query that disqualifies the most | Two of three hypotheses ruled out by evidence |
| 4. Analyze with evidence in front | Analyze | Quote the exact log, packet, or policy | Every claim points to evidence |
| 5. Report and act | Report | Verdict, evidence, action, replay path | Another analyst can replay in under 5 minutes |

---

## 5. STAR stories — deploy chart

| Story | Deploy when Eric asks | Locked numbers | Takeaway |
|---|---|---|---|
| 1. POS skimmer | Investigation, ambiguous alert, what is investigation quality | Zero additional cards. 8h to 90 min. 6 step runbook. | Investigation quality starts with the human signal. |
| 2. OpenClaw red team | AI quality, hard problem, set your own bar | Zero confirmed injections in 90 days. 2 regressions caught pre-deploy. 10 attack classes. | AI quality means a regression suite for behavior, not just code. |
| 3. Falco tuning | False positives, signal to noise, alert fatigue | 200 to 12 daily. 78% noise from 3 rules. 14 day baseline. | Tuning is precision, not deletion. If analysts tune out, detection is dead. |
| 4. n8n SOAR | Shipping under ambiguity, startup velocity | 14 workflows in under a month. 16 services. 20+ credentials. | In a startup the guardrail that matters is the error path. |
| 5. Splunk MTTD (backup) | Measurable detection outcome | 48h to under 4h. Under 5% FP rate. 30 day baseline. | A good rule lets analysts stop investigating alphabetically and start investigating the business. |
| 12. n8n DB debug (backup) | Deep debugging, reading code you didn't write | 14 workflows clean on first run after fix. | When UI, API, and CLI agree and runtime disagrees, truth is in the database. |

---

## 6. Code defense priority order

| Probe | Lead with | Anchor |
|---|---|---|
| Why two tier router | Cost-per-investigation | Sonnet ~5x cheaper than Opus. Three escalation triggers. |
| Why narrow tools | Selection clarity + audit | One tool per question shape. Mirror Eric's "small composable scoped agents" blog. |
| Why read only | Defense in depth | No Create, Delete, Put. Successful injection has no destructive path. |
| Why client inside tool | Mock interception | Moto only intercepts post-activation. Same code works real AWS by removing wrapper. |
| Why input validation | Fail fast | Regex bucket names + IAM users. ipaddress for IPv4. Bad input never reaches AWS. |
| Why temperature 0 | Reproducibility | Same question, same answer. Security wants determinism. |
| Why LangChain | Brief named it | create_agent gives the loop for free. LangGraph is right for production scale. |

---

## 7. Three code gotchas to OWN before he finds them

| File:line | What's wrong | Your defense |
|---|---|---|
| `moto_setup.py:12` | Module level mutable global `_EC2_INSTANCES` | "Wrong shape. Works because module imports once per process. Would break under multi-worker. Caught after submission." |
| `tools.py:155` | `_is_public` swallows AccessDenied silently on ACL | "Should be tri-state. Public, not public, unknown. False on AccessDenied is a security-critical false negative in production." |
| `moto_setup.py:137` | Read-only IAM policy has `iam:Get*` but tool calls `iam:List*` | "Moto papers over it. Real AWS the analyst couldn't run their own permission lookup. I'd add iam:List* to the seed." |

---

## 8. Tier 1 question hooks — first sentence each

| Question | First sentence (memorize) |
|---|---|
| Walk me through reviewing an AI report | "I treat the report like a code review on a pull request. Three checks." |
| Time you tuned a noisy detection | "Falco was throwing 200 alerts a day. The team was ignoring them, which is the worst failure mode for a detection." |
| Difference between good and bad agent design | "Bad designs put the model in charge of credentials and infrastructure. Good designs keep judgment with the model." |
| Six plus years gap | "Density over tenure. Last fourteen months I shipped what would normally be five to six years of distributed responsibility." |
| Hard tradeoff in a system you built | "Inside our LLM gateway I had to choose between rich tool access and locking the surface to limit blast radius." |

---

## 9. Five questions to ask Eric (in order)

| # | Question |
|---|---|
| 1 | What does the bar for investigation quality look like internally? Is there a specific metric I'd be measured against in the first 90 days? |
| 2 | How is the team structured between investigation flow engineers, integration engineers, and platform engineers? Where would I sit? |
| 3 | What's the eval and regression testing story for new investigation flows? How do you catch quality drift before customers do? |
| 4 | What's the hardest open problem the team is working on right now that you'd want a senior hire to step into? |
| 5 (closer) | Eric, is there anything from this conversation that leaves you uncertain about me for this role? I'd rather address it now than leave it unsaid. |

---

## 10. Never say

| Bad phrase | Why it kills you |
|---|---|
| "Pivoting" / "transitioning" / "aspiring" | Identity is non-negotiable. You ARE one. |
| "I'm passionate about AI" | Boilerplate. He has heard it 500 times. |
| "Cutting edge" / "state of the art" / "rockstar" / "ninja" | Buzzword allergy. |
| "My startup" | Say "my employer CoreDirective." |
| "I'm still learning [X]" | Senior bar. Replace with "I'd want to ramp on X by reading Y." |
| "AI will replace SOC analysts" | Triggers his entire engineering philosophy. Augments, not replaces. |
| "I have a Master's coming May 2026" as your lead | He has 11 patents and didn't lead with "I have a BS." |
| Bashing prior employers, certs, or AI vendors | Reads as immature. |
| Long answers with no number | He is a measurement engineer. Every story needs an integer. |
| Salary, equity, title questions | Wrong audience. Save for offer call. |
| Em dashes in the thank-you note | He reads LLM output for a living. He will smell it. |

---

## 11. Soundbites to land (use 3 of these in 45 minutes)

| # | Soundbite |
|---|---|
| 1 | "I read AI output the way a senior analyst reads a junior's report." |
| 2 | "Grounding is the engineering problem. Hallucination is the symptom." |
| 3 | "Every detection ships with a regression test against 30 days of production traffic." |
| 4 | "I optimize for analyst trust first, coverage second." |
| 5 | "Production Python earns its place. Notebooks don't." |
| 6 | "Humans own scope and authorization. Agents own volume and speed. The bar is whether the action graph is replayable by a human in under five minutes." |
| 7 | "The compression is real, 40 hour hunts to one hour, and the catch is the hour can hide a worse failure mode than the 40 hours did. The eval harness is what makes the hour trustworthy." |
| 8 | "Investigation quality is not about the alert that fires. It is about the one customer who tells you something is wrong." |
| 9 | "Tuning is not deleting rules. It is writing them with enough precision that a human can trust the feed." |
| 10 | "AI earns production access when it has a review gate, a log, and a kill switch. Anything less is a demo pretending to be a workflow." |

---

## 12. How you keep up with the field (lock this answer)

> "Three sources. One, I red team my own gateway every week. Fastest way to know what's broken in a model is to break it yourself. Two, primary sources. Anthropic engineering blog, OWASP LLM Top 10 updates, MITRE ATLAS, AISI evals when they publish. Three, narrow follow list of practitioners. Simon Willison on tooling, Riley Goodside on prompting failure modes, LangChain release notes. I do not read TechCrunch. I read what the people building the thing publish."

> "On the security side specifically: Lakera research, Pinokio jailbreak corpus, MITRE ATLAS technique adds. I keep a private repo of every prompt injection that worked against my own gateway. The list is short and embarrassing."

---

## 13. Schedule (today)

| Time EDT | Block |
|---|---|
| 5:30 - 7:00 AM | Code walk-through + read 13_MAY7_MORNING_BRIEF.md once |
| 7:00 - 8:30 AM | STAR drill (POS, OpenClaw, Falco) at 90s each, three rounds |
| 8:30 - 10:00 AM | Code defense probes (5 of them, with Claude) |
| 10:00 - 11:00 AM | Curveballs not in your prep |
| 11:00 - 12:00 PM | Light review. Read this chart. Test camera, mic, Meet link. |
| 12:00 - 12:15 PM | Real food. Water. Walk around the block. |
| 12:15 - 12:43 PM | Pre call. Power pose. Phone DND (Do Not Disturb). All tabs closed except Meet. |
| 12:43 PM | Dial in 2 minutes early |
| 12:45 - 1:30 PM | LIVE |
| 1:30 - 2:30 PM | Decompress. Three things that worked, three that didn't. Send thank you. |

---

## 14. Compensation playbook (only if Eric brings it up)

| Item | Number |
|---|---|
| JD posted band | $175,000 to $217,000 base + above market new hire equity |
| Range you gave Shaleena | $185,000 to $210,000 |
| Working target | $200,000 base |
| Floor | $185,000 base, only below if equity covers gap |
| If asked at offer stage | "Two hundred on base feels right given the stated range and what I'd bring day one. Flexible on mix. Happy to trade some base for stronger equity if your band has room. What are you working with?" |

Do not negotiate with Eric. Save it for HR or hiring manager at offer stage.

---

## 15. Centering line (read aloud at 12:43 PM EDT)

> "I am an AI Security Engineer. Investigation quality is my problem and I solve it in production."

Three breaths. Camera on. Smile once. Connect.
