# Sr. Security Engineer (Splunk ES) — Study Plan

**Target role:** Sr. Security Engineer, financial services client via Expert Technical Solutions
**Stack you must own:** Splunk ES, detection engineering, threat hunting, agentic SOC, LLM/RAG automation, MITRE ATT&CK, IR
**Related files:**
- Job description: `~/Downloads/Sr. Security Engineer (Splunk Enterprise) Remote.docx`
- Screen prep (Paul Adams): `CoreDirective/career/EXPERT_TECH_SCREEN_PREP.md`
- Current resume: `~/Library/Mobile Documents/com~apple~CloudDocs/Emmanuel_Tigoue_AISecurity_Engineer.pdf`

---

## How To Use This File

This file is a **study plan + tracker**. You check boxes as you go. You do NOT read in order and nod along. Every day has a **deliverable** — if you can't produce it, you haven't done the day.

**Daily time budget:** 2-3 hours. Adjustable. If you have less, compress to the "minimum viable" line in each module.

**Three tracks — pick one based on interview date:**
- **SPRINT (7 days)** — interview this week. Hit Splunk ES Core + Agentic framing only.
- **STANDARD (14 days)** — interview next week. Adds threat hunting, detection-as-code, AppSec basics.
- **DEEP (21 days)** — interview in 3+ weeks. Full mastery including mock rounds.

**→ Tell me your actual interview date and I'll pick the track and set the daily cadence.**

**Interactive study modes — invoke me by typing one of these in chat:**
| Mode | What happens | When to use |
|------|-------------|-------------|
| `drill <topic>` | I Socratic-grill you on the topic. You answer, I correct. | End of day to test recall |
| `lab <module>` | I guide you through a hands-on build, step by step | Building the day's deliverable |
| `mock <type>` | I run a timed mock interview (tech / behavioral / system design) | End of week 1, 2, 3 |
| `teach <topic>` | You explain the topic to me. I find your gaps and fill them. | Strongest learning mode — use often |
| `flash <count>` | I throw N flashcards at you, you define each term | Morning warmup, 10 min |

---

## Honest Gap Analysis

### What you already have (lean into these)
- **LLM/AI security** — OWASP LLM Top 10, MITRE ATLAS, prompt injection red-teaming, NeMo sandboxing. This is your edge over the typical Splunk candidate.
- **SOAR building** — you've built n8n SOAR with 16 actions. That maps directly to "Agentic SOC platform engineering" in the JD.
- **Detection engineering mindset** — Falco eBPF tuning (200 → 12 alerts) is a real detection engineering story.
- **DevSecOps / detection-as-code primitives** — Trivy/Semgrep/Gitleaks/OPA pipeline, Cosign signing, SBOM.
- **IR fundamentals** — 6-step runbook, 8hr → 90min containment at Texaco.
- **GRC fluency** — 37 docs, NIST 800-53, AI RMF. Helps in FinServ compliance conversations.
- **Basic Splunk** — you deployed Splunk at Texaco for SIEM aggregation with correlation rules. You know the product shape.

### What you need to build (these are the gaps)
- **Splunk Enterprise Security (ES) the app** — ES is a paid premium app on top of Splunk Enterprise with its own constructs (CIM, data models, correlation searches, notable events, RBA, adaptive response, Asset & Identity framework). You did NOT run ES at Texaco. You ran core Splunk. Treat ES as a separate product to learn.
- **Risk-Based Alerting (RBA)** — the single most important ES concept for this role. Risk index, risk scores, risk modifiers, RBA aggregation rules. If you only learn one thing, learn this.
- **CIM normalization** — how raw logs get mapped to Common Information Model fields. Data models, datamodel acceleration, tstats.
- **Detection-as-code at scale** — Splunk security_content repo (ESCU), YAML detection schema, attack_range/attack_data testing, Sigma-to-SPL conversion.
- **MITRE ATT&CK fluency** — not just "I know the framework." Fluent means: tactics, techniques, sub-techniques, data sources, Navigator heatmaps, mapping any detection to a technique in under 30 seconds.
- **Threat hunting frameworks** — PEAK (Prepare/Execute/Act/Knowledge), TaHiTI, hunt loop, hypothesis-driven vs baseline hunting.
- **Agentic architecture fluency** — multi-agent patterns (supervisor, swarm, hierarchical), LangGraph/CrewAI/AutoGen, governance (HITL, guardrails, audit, least privilege for agents), eval harnesses. You build agents. You need to speak about agent architectures.
- **RAG pipeline depth** — embeddings, chunking strategies, vector stores, retrieval, reranking, eval for RAG.
- **Web app security for hunting** — OWASP Top 10 2021 not as a compliance checkbox but as "what does exploitation look like in logs." SSRF, IDOR, auth bypass, SSTI, XXE — what fields do you hunt on.
- **STRIDE threat modeling** — formal threat modeling, not just red teaming. DFDs, trust boundaries, threat per element.
- **Python for security automation at scale** — splunk-sdk, asyncio, rate-limited API work, structured logging. Your Texaco scripts are small. You need to speak about it in enterprise terms.

### What you NEVER fake in the interview
- Never claim you ran Splunk ES at Texaco. You ran core Splunk with alerts. ES is a separate app. Lying here gets caught in 30 seconds by any ES engineer.
- Never claim years of CIM/RBA/notable event experience. Say "I've studied deeply and built test content against it, production experience is where I'm ramping."
- Never claim MITRE ATT&CK Evaluations exposure unless you actually read the reports.
- Never claim production agentic SOC at enterprise scale. Claim: "I've built the SOAR layer in n8n and I'm building an agentic triage layer on top of OpenClaw."

**The play:** position your AI/agentic/SOAR depth as the future of SOC engineering, and your Splunk ramp as fast and intentional. You're not pretending to be a 10-year Splunk ES veteran. You're the security engineer who already understands where SOCs are going.

---

## Core Vocabulary — Daily Flashcard Drill (10 min)

Run `flash 15` in chat every morning. I'll quiz you on 15 of these. Aim for instant recall.

### Splunk Core
| Term | Definition |
|------|-----------|
| **SPL** | Search Processing Language. Splunk's query language. `index=... | stats ... | where ...` |
| **Index** | Bucket of data on disk. Think "database table." |
| **Source / sourcetype / host** | Metadata fields: where data came from, format type, origin host |
| **Forwarder (UF / HF)** | Universal Forwarder ships raw logs; Heavy Forwarder parses before shipping |
| **Search head / indexer / deployment server** | Tiers in a distributed Splunk architecture |
| **Bucket** | Time-ordered storage unit: hot, warm, cold, frozen (lifecycle) |
| **Summary index** | Pre-computed search results stored in a separate index for fast dashboards |
| **Accelerated data model** | Pre-summarized datamodel using tsidx files for fast `| tstats` queries |
| **Props.conf / transforms.conf** | Parse-time config: field extraction, sourcetype assignment, routing |
| **HEC** | HTTP Event Collector. Push logs to Splunk over HTTPS. Token-authed. |

### Splunk ES (THE ONES THAT MATTER)
| Term | Definition |
|------|-----------|
| **ES (Enterprise Security)** | Premium paid app on Splunk Enterprise. Adds SIEM-specific frameworks. |
| **CIM** | Common Information Model. Standard field names so detections work across sources. Ex: `src_ip`, `dest_ip`, `user`, `action`. |
| **Data model** | Hierarchical schema mapping raw logs to CIM fields. Powers correlation searches via tstats. |
| **Notable event** | The alert record ES creates when a correlation search fires. Lives in `notable` index. |
| **Correlation search** | Scheduled SPL query that, when it matches, creates a notable event and/or a risk modifier. |
| **Adaptive response action** | Automated action triggered by a notable: run a search, ping an API, create a ticket, isolate a host |
| **RBA (Risk-Based Alerting)** | Paradigm: don't alert on every event. Assign risk scores to events/users/assets, aggregate risk, alert only when aggregated risk crosses threshold. Reduces noise massively. |
| **Risk index / risk object / risk modifier** | RBA primitives. Modifier = "user X did suspicious thing Y worth 20 risk points." Object = user X. Index = where risk events live. |
| **Asset & Identity framework** | ES module that enriches events with asset (host) and identity (user) context for correlation |
| **Threat intel framework** | ES module ingesting STIX/TAXII feeds, IOCs, used to enrich/match events |
| **ESCU (ES Content Update)** | Free Splunk-published detection content repo. Learn this — it's how you speak detection-as-code in Splunk. |
| **Glass table** | ES visualization layer: real-time operational dashboards with risk/notable widgets |
| **Investigation** | ES case management primitive — timeline of a suspected incident |

### Detection Engineering / Threat Hunting
| Term | Definition |
|------|-----------|
| **Detection-as-code** | Detections in git, YAML schema, CI tests, versioned, peer-reviewed. Sigma and ESCU are examples. |
| **Sigma** | Vendor-neutral detection rule format (YAML). Converts to SPL, KQL, etc. |
| **Attack Range / attack_data** | Splunk OSS project that spins up a lab, runs attacks, captures data for detection testing |
| **True positive / false positive / benign true positive** | TP = real bad. FP = not bad. BTP = real activity matching the rule but authorized (admin did it, ignore). |
| **MITRE ATT&CK** | Framework of adversary TTPs organized as Tactics (why) → Techniques (how) → Sub-techniques (specifics) |
| **TTP** | Tactic, Technique, Procedure. Ascending specificity. |
| **PEAK framework** | Splunk's hunting methodology: Prepare / Execute / Act / Knowledge |
| **Hypothesis-driven hunt** | Start from a theory ("attacker using T1059.001 PowerShell"), search data for evidence |
| **Pyramid of Pain** | Hash < IP < Domain < Artifact < Tool < TTP. Higher = more expensive for attacker to evade. |
| **Diamond Model** | Adversary / Capability / Infrastructure / Victim — for incident analysis |

### Agentic SOC / AI
| Term | Definition |
|------|-----------|
| **Agentic AI** | LLM-powered agents with tools, memory, and planning loops. Can take multi-step action autonomously. |
| **Tool calling / function calling** | LLM emits a structured call to a named tool with args; orchestrator runs it; result goes back to the LLM |
| **ReAct** | Reason + Act loop: LLM thinks, picks a tool, observes, thinks again, acts again |
| **Multi-agent patterns** | Supervisor (one router), swarm (peer-to-peer), hierarchical (tree), pipeline (sequential) |
| **LangGraph / CrewAI / AutoGen** | Multi-agent orchestration frameworks. LangGraph is the most SOC-relevant. |
| **RAG** | Retrieval-Augmented Generation. Search a vector store for relevant context, inject into prompt. |
| **Vector store** | DB of embeddings. Examples: Pinecone, Weaviate, pgvector, Chroma |
| **Embedding** | Numerical vector representation of text. Similar meaning → similar vector. |
| **Chunking** | Splitting documents into retrievable pieces. Strategy matters (fixed size vs semantic). |
| **Reranker** | Second-stage model that re-scores top-k retrieval results for relevance |
| **HITL (Human-in-the-loop)** | Agent pauses for human approval at defined decision points |
| **Guardrails** | Input/output filters: topic restriction, PII redaction, toxicity, prompt injection detection |
| **Eval harness** | Automated scoring of agent outputs against golden answers, hallucination checks |

---

## Track A — SPRINT (7 days)

Minimum viable prep. Interview this week.

### Day 1 — Splunk ES Lab Setup + SPL Refresh
**Goal:** Working Splunk instance you can query + SPL recall.

**Do:**
- [ ] Install Splunk Enterprise Free on your Mac: `docker run -d -p 8000:8000 -p 8088:8088 -e SPLUNK_START_ARGS=--accept-license -e SPLUNK_PASSWORD=changeme splunk/splunk:latest`
- [ ] Download BOTS v3 dataset (Splunk Boss of the SOC, free): `https://github.com/splunk/botsv3`
- [ ] Ingest the dataset. Verify `index=botsv3` returns events.
- [ ] Run 10 SPL queries from memory: stats, timechart, eval, where, rex, join, lookup, dedup, sort, rename.

**Minimum viable:** Splunk running, BOTS indexed, you can run `index=botsv3 sourcetype=stream:http | stats count by src`.

**Prove it:** Post a screenshot OR paste output of `index=botsv3 | stats count by sourcetype` here and I'll check.

**Then:** `drill splunk spl` to grill me on SPL.

---

### Day 2 — CIM, Data Models, Correlation Searches
**Goal:** Understand what ES actually does on top of Splunk core.

**Do:**
- [ ] Install Splunk Common Information Model add-on (free): `https://splunkbase.splunk.com/app/1621`
- [ ] Read the CIM docs for 3 data models you'll hunt: Authentication, Network_Traffic, Endpoint
- [ ] Map 3 BOTS sourcetypes to their CIM data models. Example: `stream:http` → Web data model.
- [ ] Write a correlation search as a saved search with an email alert action. Query: failed logins > 5 in 5 min by same src_ip against Authentication data model using `| tstats`.
- [ ] Clone `https://github.com/splunk/security_content` (ESCU). Read 5 detections. Notice the YAML structure: `name / description / search / how_to_implement / known_false_positives / references / tags with mitre_attack_id`.

**Minimum viable:** You can explain CIM in one sentence and point to the data model fields `Authentication.user`, `Authentication.action`, `Authentication.src`.

**Prove it:** `teach cim` — explain CIM to me. I'll find your gaps.

---

### Day 3 — RBA Deep Dive (the biggest single concept)
**Goal:** You can walk through RBA end-to-end on a whiteboard.

**Do:**
- [ ] Read: Splunk's RBA whitepaper (`https://www.splunk.com/en_us/pdfs/resources/whitepaper/risk-based-alerting-whitepaper.pdf`)
- [ ] Read: Haylee Mills' RBA blog series on Splunk blog (she literally invented the framework at TD Ameritrade). Search "Haylee Mills RBA Splunk."
- [ ] In your Splunk, create a `risk` index manually.
- [ ] Create a saved search that writes risk modifiers: when a user triggers a suspicious search, append an event to the risk index with `risk_score=20, risk_object=user, risk_object_type=user, source=name_of_rule`.
- [ ] Create a meta-alert: aggregated risk score > 100 in 24h for the same user → notable.
- [ ] Write down the answer to: "Why is RBA better than one-alert-per-event?" (Answer: reduces alert fatigue, surfaces patterns that individual events miss, aligns severity with cumulative suspicion.)

**Minimum viable:** You can say the sentence: "RBA aggregates risk modifiers against a risk object over a window, and only fires a notable when the cumulative score crosses a threshold, which cuts alert noise by 70-90% in published case studies."

**Prove it:** `teach rba` — walk me through RBA soup-to-nuts.

---

### Day 4 — MITRE ATT&CK Fluency
**Goal:** You can map any event to a technique ID in under 30 seconds and explain the tactic.

**Do:**
- [ ] Open ATT&CK Navigator: `https://mitre-attack.github.io/attack-navigator/`
- [ ] Memorize the 14 enterprise tactics in order (Reconnaissance → Impact).
- [ ] For each tactic, memorize ONE technique you can talk about deeply. Suggested: T1566 Phishing, T1078 Valid Accounts, T1059.001 PowerShell, T1055 Process Injection, T1021.001 RDP, T1003 Credential Dumping, T1071.001 Web Protocol C2, T1486 Ransomware.
- [ ] For each of those 8, know: the data source, the log fields you'd hunt on, one detection pattern, one evasion method.
- [ ] Build a Navigator heatmap of the 8 techniques. Export as JSON.

**Minimum viable:** You can name all 14 tactics in order and give one technique per tactic.

**Prove it:** `drill attack` — I'll give you 10 rapid-fire scenarios, you call the technique ID.

---

### Day 5 — Agentic SOC Landscape + Architecture
**Goal:** You speak about agentic SOC like you've been watching this space (you have — own it).

**Do:**
- [ ] Read landing pages + demo videos for: Dropzone AI, Prophet Security, Simbian, Torq HyperSOC, Crogl, Radiant Security. Take notes on what each claims to automate.
- [ ] Read one LangGraph tutorial. Understand: nodes = steps, edges = transitions, state = shared memory, tools = functions agents can call.
- [ ] Sketch a 3-agent SOC triage pipeline on paper: **Enrichment agent** (pulls WHOIS, VT, asset context) → **Triage agent** (classifies severity using ATT&CK + historical cases via RAG) → **Recommender agent** (proposes containment actions, writes to HITL queue).
- [ ] Write down how you'd do governance: audit log every tool call, HITL gate before any write action, guardrail on prompt injection in input, eval harness comparing agent verdicts to analyst verdicts weekly.
- [ ] Connect this to what you already built: OpenClaw gateway as the LLM endpoint, n8n as the orchestration layer, Telegram as the HITL channel, Ollama for sensitive triage data that can't go to Claude.

**Minimum viable:** You can draw a 3-agent pipeline on a whiteboard and name the governance controls for each node.

**Prove it:** `teach agentic-soc` — draw it for me in ASCII, explain the flow.

---

### Day 6 — Story Bank + Behavioral
**Goal:** Every resume bullet is a STAR-format story ready for "tell me about a time when..."

**Do:**
- [ ] For each of the 10 AI Security Engineer bullets and 8 Texaco bullets, write a STAR: Situation / Task / Action / Result / Lesson.
- [ ] Map each STAR to at least one JD requirement. Mark any JD line without a matching STAR — those are your weak spots to prep talking points for.
- [ ] Write the 3 "killer stories" — rehearse out loud:
  - **Noise reduction story:** 200 → 12 Falco alerts. Ties to detection tuning, RBA mindset.
  - **SOAR automation story:** n8n cut triage 80%. Ties to agentic SOC + automation.
  - **IR runbook story:** 8hr → 90min at Texaco. Ties to IR rotation + operational maturity.
- [ ] Write one "failure story" — something that broke, how you recovered, what you learned. Interviewers always ask this.
- [ ] Write your 90-second "tell me about yourself" opener.

**Minimum viable:** 3 killer stories rehearsed out loud and timed under 2 min each.

**Prove it:** `mock behavioral` — 20 min behavioral mock, I'll score.

---

### Day 7 — Full Mock Interview + Q&A Polish
**Goal:** Dry run of the real thing + questions to ask them.

**Do:**
- [ ] `mock tech` — 45 min timed technical mock. I play the interviewer. Cold start.
- [ ] `mock behavioral` — 20 min behavioral. Separate session.
- [ ] Review scorecard, note the 3 weakest answers, rewrite them.
- [ ] Write 6 questions to ask them (3 technical, 3 team/culture). Examples:
  - "What's the current RBA maturity? Are you still running notable-per-event or have you moved to risk aggregation?"
  - "How is the agentic SOC platform vendor-built vs in-house? Which multi-agent framework?"
  - "What does detection-as-code look like today? Is content in git with CI, or still manual in the ES UI?"
  - "Where does the financial services compliance layer sit — SOX controls, PCI scoping, NYDFS 500?"
  - "How does the on-call rotation work? What's the escalation ladder?"
  - "What would success look like in the first 90 days?"
- [ ] Test your setup: camera angle, mic, lighting, backdrop, water, notes out of frame.
- [ ] Sleep 8 hours the night before. Seriously.

**Minimum viable:** One full tech mock completed, 6 questions drafted.

---

## Track B — STANDARD (14 days) — adds on top of Sprint

Days 1-7 as above. Then:

### Day 8 — Detection-as-Code Pipeline
- [ ] Fork `splunk/security_content`. Read the YAML schema in detail.
- [ ] Write one ESCU-style detection for your BOTS data: "Unusual PowerShell execution."
- [ ] Set up a GitHub Action that lints detection YAML on PR (splunk-validate or yamllint).
- [ ] Read about attack_range: `https://github.com/splunk/attack_range`. You don't need to run it — know what it is.
- [ ] Convert one Sigma rule to SPL by hand using `https://github.com/SigmaHQ/sigma`.

**Deliverable:** One YAML detection in your fork, passing lint, with ATT&CK tagging.
**Prove it:** `teach detection-as-code` — walk me through the pipeline.

### Day 9 — Threat Hunting with PEAK
- [ ] Read Splunk's PEAK framework blog posts (free, Splunk blog).
- [ ] Pick T1059.001 PowerShell. Write a full hunt:
  - **Prepare:** what data sources, what fields, what hypothesis
  - **Execute:** SPL queries, baseline vs anomaly
  - **Act:** what do you do with findings (notable, detection, RBA modifier)
  - **Knowledge:** document for next hunt
- [ ] Run the hunt in your Splunk against BOTS data.
- [ ] Produce a 1-page hunt report.

**Deliverable:** PowerShell hunt report with screenshots.
**Prove it:** `teach peak` — walk me through your hunt.

### Day 10 — Web App Security for Hunters
- [ ] Re-skim OWASP Top 10 2021: A01 Broken Access Control, A02 Crypto Failures, A03 Injection, A04 Insecure Design, A05 Security Misconfig, A06 Vulnerable Components, A07 Auth Failures, A08 Integrity Failures, A09 Logging/Monitoring Failures, A10 SSRF.
- [ ] For each, write ONE line: "how does exploitation look in a web access log" — i.e., what fields/patterns you'd hunt.
- [ ] Read one SSRF writeup and one IDOR writeup on HackerOne.
- [ ] Stand up DVWA or Juice Shop locally. Exploit one SQLi. Capture the attack log in Splunk. Write a detection.

**Deliverable:** One web detection from a real exploit you ran.
**Prove it:** `drill owasp-hunting` — I'll give you log patterns, you call the vuln class.

### Day 11 — RAG Pipeline Deep Dive
- [ ] Build a small RAG pipeline on your Mac: chunk your GRC docs → embed with `text-embedding-3-small` → store in Chroma → retrieve top-5 for a query → inject into a Claude prompt.
- [ ] Learn: chunking strategies (fixed, recursive, semantic), embedding model tradeoffs, hybrid search (BM25 + vector), reranking with Cohere reranker or cross-encoder.
- [ ] Eval it: 10 questions about your own GRC docs, score precision@5.

**Deliverable:** Working RAG CLI that answers questions from your SSP.
**Prove it:** `teach rag` — architecture walkthrough.

### Day 12 — Multi-Agent Build with LangGraph
- [ ] Install LangGraph. Build the 3-agent triage pipeline you sketched on Day 5, pointing at a mock alert (JSON file).
- [ ] Agent 1: enrichment (simulate WHOIS + VT with canned responses). Agent 2: triage (classify using ATT&CK). Agent 3: recommender (output containment plan).
- [ ] Add a HITL checkpoint before the recommender commits.
- [ ] Log every tool call with timestamps and inputs/outputs. This IS the audit trail.

**Deliverable:** Running LangGraph demo against one test alert, audit log captured.
**Prove it:** `teach multi-agent` — explain the flow and the governance layer.

### Day 13 — STRIDE Threat Modeling
- [ ] Learn STRIDE: Spoofing, Tampering, Repudiation, Information disclosure, DoS, Elevation of privilege.
- [ ] Pick a target: your OpenClaw gateway. Draw a DFD with trust boundaries: client → Cloudflare tunnel → gateway → Claude API / local tools.
- [ ] For each element (process, data store, data flow, external entity), list STRIDE threats. Write mitigations.
- [ ] Bonus: do the same for the agentic SOC pipeline from Day 12, now using MITRE ATLAS for AI-specific threats.

**Deliverable:** One STRIDE threat model doc.
**Prove it:** `teach stride` — walk me through your OpenClaw model.

### Day 14 — Mock Round 2 + Iteration
- [ ] `mock tech` — second tech mock, deeper. I'll push harder on weak spots from round 1.
- [ ] `mock behavioral` — round 2 with curveballs.
- [ ] Write a delta-plan: what got better, what's still weak, last-mile fixes.

---

## Track C — DEEP (21 days) — adds on top of Standard

### Day 15 — Splunk Cybersecurity Defense Analyst (SPLK-5001) Exam Objectives
- [ ] Read the official SPLK-5001 exam blueprint.
- [ ] Do the free Splunk Fundamentals 1 eLearning.
- [ ] Work 3 TryHackMe Splunk rooms: SOC L1, Investigating with Splunk, BOTS v1.

**Deliverable:** TryHackMe room completions + notes.

### Day 16 — Financial Services Compliance Layer
- [ ] PCI DSS 4.0 (you know 3.2 from Texaco) — read the delta to 4.0: targeted risk analysis, authenticated vuln scans, MFA for all system access. Especially note requirement 10 (logging) and 11 (testing).
- [ ] NYDFS Part 500 — cybersecurity requirements for FinServ. Know: Section 500.16 (IR plan), 500.17 (notice of cyber event within 72h), MFA requirements, CISO certification.
- [ ] SOX IT general controls — logical access, change management, ops. FinServ cares because auditors care.
- [ ] FFIEC CAT — cybersecurity assessment tool.

**Deliverable:** 1-pager mapping your GRC work to FinServ frameworks.

### Day 17 — Python for Security at Scale
- [ ] Build a splunk-sdk script: auth, run a search, iterate results, write notables to a file.
- [ ] Refactor using asyncio for concurrent API calls.
- [ ] Add structured logging with `structlog` and retry with backoff using `tenacity`.
- [ ] Write 3 unit tests with pytest.

**Deliverable:** Python tool you can show on GitHub.

### Day 18 — Incident Response Deep Dive
- [ ] Review NIST SP 800-61r2 IR lifecycle: Prep / Detection & Analysis / Containment-Eradication-Recovery / Post-Incident.
- [ ] Write one full IR playbook for "suspected credential compromise in Okta" using the lifecycle.
- [ ] Tabletop it solo: walk through the steps, time them, note gaps.

**Deliverable:** Playbook + tabletop after-action.

### Day 19 — Architecture + System Design Prep
- [ ] Practice: "Design a SIEM ingestion pipeline for 500GB/day from 50 sources including AWS CloudTrail, EDR, Okta, GitHub audit logs."
- [ ] Practice: "Design an agentic triage layer on top of an existing Splunk ES deployment."
- [ ] Practice: "How would you migrate from traditional notable-event alerting to RBA?"

**Deliverable:** 3 whiteboard designs drawn on paper.

### Day 20 — Story Bank Polish + Dry Run
- [ ] Record yourself answering the 3 killer stories. Watch back. Fix pacing, ums, filler.
- [ ] Reduce each story to a hook sentence ("The time I cut Falco noise from 200 to 12").
- [ ] Rehearse questions to ask them out loud.

### Day 21 — Final Mock + Rest
- [ ] One final full-loop mock: 90 min covering tech + behavioral + system design.
- [ ] Review, no new material.
- [ ] Sleep. Eat. Show up.

---

## Daily Rhythm (regardless of track)

**Morning (15 min)** — wake up, open this file, run `flash 15` in chat. Fast recall drill.

**Core session (90-120 min)** — the day's module. Run `lab <module>` if you want me to guide the hands-on. Don't skip the deliverable.

**Evening (20-30 min)** — run `teach <today's topic>`. Explaining it back is how it sticks. If you can't teach it, you don't know it.

**Weekly (Sunday)** — review the week, run one `mock`, update gap notes.

---

## How To Invoke Study Modes (Examples)

```
flash 15
→ I throw 15 flashcards at you from the vocab tables, you type each answer, I grade
```

```
drill rba
→ I grill you on risk-based alerting: 10 questions, increasing difficulty, I correct gaps
```

```
lab day 3
→ I guide you step-by-step through the Day 3 RBA lab in your real Splunk
```

```
teach cim
→ You explain CIM to me in your own words. I interrupt when you're wrong or thin.
```

```
mock tech
→ I run a 45 min timed tech interview, then score you across: Splunk ES depth, detection eng,
  agentic SOC, AI security, threat hunting, communication, confidence
```

```
mock behavioral
→ 20 min, 8 behavioral questions including the curveball failure question, STAR scoring
```

---

## Red Flags / Traps To Avoid

1. **Don't confuse Splunk core with Splunk ES.** ES is a paid app. ES has CIM, data models, notable events, correlation searches, RBA, Asset & Identity framework. If an interviewer asks "walk me through ES," they mean the app's frameworks, not SPL basics.
2. **Don't describe every alert as a "correlation search."** In ES, a correlation search is a specific Splunk primitive with a specific lifecycle.
3. **Don't claim you've done RBA in production.** Say "I've studied the framework deeply, built test content against it, and I can speak to the risk modifier / risk object / threshold model."
4. **Don't call generic Python scripting "security automation engineering."** For this role, that phrase implies Splunk SDK, detection CI, Sigma conversion, attack_range testing, API-driven content deployment.
5. **Don't pretend ATLAS and ATT&CK are the same.** ATT&CK = traditional adversary TTPs. ATLAS = adversarial threats to AI systems.
6. **Don't forget the client is financial services.** Weave in compliance awareness without making it the whole answer.
7. **Don't oversell agentic SOC as replacing analysts.** The interviewer is one of those analysts. Position it as a force multiplier with HITL gates.
8. **Don't wing the RBA question.** If they ask "why RBA over notable-per-event" and you flinch, you're done. Memorize the sentence on Day 3.

---

## Resources

**Splunk ES & RBA**
- Haylee Mills RBA blog series (Splunk blog) — the foundational RBA content
- Splunk ES docs: `https://docs.splunk.com/Documentation/ES/latest/User/Howtouse`
- Splunk Security Content (ESCU): `https://github.com/splunk/security_content`
- Splunk Attack Range: `https://github.com/splunk/attack_range`
- BOTS v3 dataset: `https://github.com/splunk/botsv3`
- Splunk Fundamentals 1 (free eLearning, 4 hours)

**Detection Engineering**
- Sigma repo: `https://github.com/SigmaHQ/sigma`
- Red Canary Threat Detection Report (annual, free) — gold standard detection writeups
- The DFIR Report: `https://thedfirreport.com/` — real incident walkthroughs with detection opportunities
- Anton Chuvakin's blog — SIEM + detection philosophy

**MITRE ATT&CK**
- ATT&CK Navigator: `https://mitre-attack.github.io/attack-navigator/`
- MITRE ATT&CK for Dummies (MITRE's own intro, free)
- Cyber Kill Chain vs ATT&CK — know the difference

**Threat Hunting**
- Splunk PEAK framework blog posts (search "Splunk PEAK hunting")
- TaHiTI methodology PDF (free)
- "The Threat Hunter's Playbook" (OTRF) — free GitHub content

**Agentic SOC**
- Dropzone AI, Prophet Security, Simbian, Torq HyperSOC, Crogl — read their landing pages and blogs
- LangGraph docs: `https://langchain-ai.github.io/langgraph/`
- Anthropic's "Building Effective Agents" blog post
- Google's agent architectures paper (AgentOps)

**AI Security**
- OWASP Top 10 for LLM Applications (you know this)
- MITRE ATLAS: `https://atlas.mitre.org/`
- NIST AI RMF (you know this)
- Anthropic's Constitutional AI paper

**Web App Security**
- OWASP Top 10 2021
- PortSwigger Web Security Academy (free) — best in class, pick 5 labs
- HackerOne Hacktivity — real bug reports

**Financial Services Compliance**
- PCI DSS 4.0 quick reference
- NYDFS Part 500 text
- FFIEC Cybersecurity Assessment Tool

**Certs aligned to this role (you don't need them for the interview, just know they exist)**
- Splunk Core Certified User → Power User → Enterprise Admin → ES Admin
- Splunk Certified Cybersecurity Defense Analyst (SPLK-5001) — most relevant, $130, no prereqs
- Splunk SOAR Certified Automation Developer
- GIAC GCIA (intrusion analyst), GCDA (detection analyst), GCIH (incident handler), GCTI (threat intel)

---

## Progress Log

Keep this updated so you can see momentum.

- [ ] Interview date set
- [ ] Track picked (Sprint / Standard / Deep)
- [ ] Splunk lab running
- [ ] BOTS dataset ingested
- [ ] First correlation search written
- [ ] First RBA risk modifier written
- [ ] ATT&CK Navigator heatmap built
- [ ] LangGraph triage pipeline running
- [ ] Killer stories rehearsed and timed
- [ ] Mock tech 1 completed
- [ ] Mock behavioral 1 completed
- [ ] Mock tech 2 completed (Standard+)
- [ ] Mock behavioral 2 completed (Standard+)
- [ ] Final mock completed (Deep)
- [ ] Questions-to-ask list finalized
- [ ] Interview done

---

## Quick Start (right now, today)

1. **Tell me your interview date.** I'll pick the track and set the cadence.
2. **Install Splunk** (the one command in Day 1) — start this in the background while we talk.
3. **Run `flash 15`** — 10 min vocab warmup. We'll see where you stand.
4. **Run `teach splunk-es`** — explain Splunk ES to me in 5 minutes. I'll map your current knowledge and mark the hot spots.

After those three, I'll have a concrete read on your starting level and can trim or expand the plan to fit.
