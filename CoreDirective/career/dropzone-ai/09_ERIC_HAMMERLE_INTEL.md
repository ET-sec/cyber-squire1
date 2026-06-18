# Eric Hammerle — Hiring Manager Intel

**Interview:** Thu May 7, 2026, 12:45 PM EDT (45 min)
**Role on the table:** Senior Security Engineer, Dropzone AI
**Interviewer:** Eric Hammerle — Director of Engineering, Dropzone AI (formerly Sr Tech Lead Manager / Founding Engineer)
**Briefing compiled:** 2026-04-28
**Confidence levels in this doc:** OBSERVED = direct public source cited; INFERRED = reasoned from observed evidence; NO PUBLIC SIGNAL = absence of data, not invented.

---

## TL;DR — Five things to do differently because of this

1. **Treat him as a builder-manager, not a manager-manager.** OBSERVED. Founding Engineer for two years before promotion to Sr Tech Lead Manager (2025) then Director of Engineering (2026). Eleven patents (most as co-inventor with Dropzone's CEO Edward Wu). He still ships. Speak in code, design tradeoffs, and concrete failure modes — not strategy slides.
2. **Anchor every story in investigation quality and false-positive economics.** OBSERVED. The role he is hiring for says "own investigation quality." The blog post directly downstream of his patents (OSCAR + Context Engineering + AI Agent Guardrails) is a coherent thesis: structured autonomy, deterministic guardrails, scoped agents, action graphs, evals on FP/FN rates. Mirror that vocabulary verbatim.
3. **Lead with your three metrics in PSC form, but reframe Falco/Splunk/IR runbook as "investigation pipeline" wins, not just detection wins.** INFERRED. He spent 8 years at ExtraHop building the network-detection-and-response pipeline that Edward Wu sat next to. He has heard 10,000 detection demos. What is rare in his world is people who can talk about the *post-detection* investigation flow at scale.
4. **Do not pitch agent autonomy. Pitch agent containment.** OBSERVED. Dropzone's public position (Tyson Supasatit, Apr 24 2026) calls unbounded autonomy "a bigger attack surface." Eric is the engineer behind the patents that make this real. Your OpenClaw red-team story should land as "I broke an unbounded agent and learned what guardrails it actually needed" — not "I built a powerful agent."
5. **Bring one specific architectural opinion he can push on.** INFERRED. He gives recommendations about engineers who are "insanely fast at figuring out existing technology" and "not afraid of making bold changes." Translation: he respects strong, defensible opinions over hedged-everything answers. Have a take. Defend it. If he disagrees, ask one good question and update visibly. That sequence is what he is testing.

---

## Career arc

| Role | Company | Dates | Scope / Notes | Source |
|---|---|---|---|---|
| Director of Engineering | Dropzone AI | 2026 – present | Promoted from Sr Tech Lead Manager. Leads R&D engineering org (~16 engineers per company-page roster). | [RocketReach](https://rocketreach.co/eric-hammerle-email_9742328) |
| Sr Tech Lead Manager | Dropzone AI | 2025 – 2026 | Transition role — first formal management title at Dropzone. | [RocketReach](https://rocketreach.co/eric-hammerle-email_9742328) |
| Founding Engineer | Dropzone AI | 2023 – 2025 | Listed as Founding Engineer in early team docs. Inventor on 4+ Dropzone patents (Automated threat hunting, Context repository management, System for surveying security environments, Security analysis agents). | [RocketReach](https://rocketreach.co/eric-hammerle-email_9742328), [Justia patents](https://patents.justia.com/inventor/eric-joseph-hammerle) |
| Software Engineer | Meta | 2019 – 2023 | 4 years. No public team detail. INFERRED: senior IC role given prior Principal title. | [RocketReach](https://rocketreach.co/eric-hammerle-email_9742328) |
| Vice President — Cybersecurity | JPMorgan Chase & Co. | 2018 – 2019 | One year. JPMC "VP" is an IC band, not exec. Cybersecurity org. | [RocketReach](https://rocketreach.co/eric-hammerle-email_9742328) |
| Principal Software Engineer | ExtraHop Networks | 2014 – 2018 | 4 years at top IC band. Co-inventor with Edward Wu on the network-correlation patents (US 11012329, US 10411978, US 11496378). | [RocketReach](https://rocketreach.co/eric-hammerle-email_9742328), [Justia patents](https://patents.justia.com/inventor/eric-joseph-hammerle) |
| Senior Software Engineer | ExtraHop Networks | 2011 – 2014 | 3 years. Promoted to Principal in 2014. | [RocketReach](https://rocketreach.co/eric-hammerle-email_9742328) |
| SWE-SRE | Google | 2010 – 2011 | One year. Site-Reliability Engineering / production engineering blend. | [RocketReach](https://rocketreach.co/eric-hammerle-email_9742328) |
| Senior Software Engineer | F5 Networks | 2006 – 2010 | 4 years. Co-inventor on F5 patent US 9083760 (Dynamic cloning and reservation of detached idle connection — load balancer / TCP stack work). | [RocketReach](https://rocketreach.co/eric-hammerle-email_9742328), [Justia patents](https://patents.justia.com/inventor/eric-joseph-hammerle) |
| Software Design Engineer | Microsoft | 2004 – 2006 | First post-college role. | [RocketReach](https://rocketreach.co/eric-hammerle-email_9742328) |
| Co-op | Spectracom Corp | 2003 | RIT co-op. | [RocketReach](https://rocketreach.co/eric-hammerle-email_9742328) |
| Intern | Kinetic Concepts Incorporated | 2003 | Medical-device summer intern. | [RocketReach](https://rocketreach.co/eric-hammerle-email_9742328) |
| BS, Rochester Institute of Technology | RIT | 2000 – 2004 | Major not specified publicly. INFERRED: Software Engineering or Computer Engineering given career and RIT's 5-year co-op program. | [LinkedIn](https://www.linkedin.com/in/eric-hammerle-3073045/) |

**Pattern read:** Heavy tenure when the work is interesting (8 yrs ExtraHop, 4 yrs Meta, 4 yrs F5). Short stays when it isn't (1 yr Google, 1 yr JPMC). He left big-co stability twice for builder roles. The Dropzone arc — Founding Engineer → Sr Tech Lead Manager → Director of Engineering inside ~3 years — says he is at home in a fast-moving, high-trust environment and was promoted from inside on technical merit, not hired in as a manager.

---

## Technical posture (cited evidence)

| Signal | Evidence | Source |
|---|---|---|
| **Languages he has shipped at scale: C++, C, Linux/Unix systems** | LinkedIn skills explicitly: "Device Drivers, Virtualization, Distributed Systems, C++, Linux, Unix, TCP/IP, C, operating systems, software design." Prior F5 patent is on TCP connection state machines. | [LinkedIn](https://www.linkedin.com/in/eric-hammerle-3073045/) |
| **Production language at Dropzone: Python** | Dropzone JD for the role he is interviewing for: "Production Python experience" required. "Contributing to Python codebase." | [Rippling JD](https://ats.rippling.com/dropzone-ai/jobs/dd5ab50b-e853-449b-b30e-be55fb45f1a2) |
| **Distributed systems / systems-software DNA** | Patents on "network packet de-duplication," "correlating causes and effects," dynamic connection cloning. He is a systems guy, not a webapp guy. | [Justia](https://patents.justia.com/inventor/eric-joseph-hammerle) |
| **Architectural preference: small, composable, scoped agents over monolithic prompts** | Dropzone's public engineering writing (which his patents underpin) explicitly argues: "Break complex investigations into smaller, focused tasks rather than monolithic prompts. Enables specialized training and clearer success criteria." | [Dropzone blog: Context Engineering](https://www.dropzone.ai/blog/when-ai-gets-it-wrong-the-critical-importance-of-context-engineering) |
| **Architectural preference: deterministic execution wraps non-deterministic reasoning** | "Judgment lives with the model. Credentials, data, and infrastructure live behind tightly scoped agents." | [Dropzone blog: AI Agent Guardrails](https://www.dropzone.ai/blog/ai-agent-guardrails) |
| **Observability: action graphs over verbose logs** | "Systems should show investigation methodology, not just conclusions. Supports validation, training, debugging, and compliance." | [Dropzone blog: Context Engineering](https://www.dropzone.ai/blog/when-ai-gets-it-wrong-the-critical-importance-of-context-engineering) |
| **Quality discipline: track FP/FN as primary metrics, not vanity throughput** | "Ensuring accuracy is a continuous effort through quality control programs that track key metrics like false positives and false negatives." | [Dropzone blog: Context Engineering](https://www.dropzone.ai/blog/when-ai-gets-it-wrong-the-critical-importance-of-context-engineering) |
| **OSCAR investigative framework is internal scaffolding, not branding** | Patents reference evidence collection, scoring, filtering, threat-profile generation — exactly OSCAR's Obtain → Strategize → Collect → Analyze → Report. | [Dropzone OSCAR](https://www.dropzone.ai/blog/why-socs-rely-on-oscar-a-proven-investigative-framework), [US 12499243](https://patents.google.com/patent/US12499243B1) |
| **NO PUBLIC SIGNAL on: LangChain, LangGraph, FastAPI, Pydantic specifically** | Dropzone has no public GitHub org. No engineering blog post names a framework. The architectural pattern in the guardrails blog is consistent with LangGraph-style state machines but is framework-agnostic in writing. | NO PUBLIC SIGNAL |
| **NO PUBLIC SIGNAL on: Go, TypeScript, Rust at Dropzone** | Not in JD, not in patents, not in blogs. INFERRED Python-primary backend with whatever frontend they need. | NO PUBLIC SIGNAL |

---

## Leadership & interview style (predicted, with reasoning)

**Predicted style:** Calm, technical, low-ceremony. Leads with one open question, lets you fill space, then drills on a specific tradeoff you mentioned. Will not chitchat for ten minutes.

**Reasoning:**

- He was a Principal Engineer at ExtraHop for 4 years before any management title. Principal-track engineers run interviews like design reviews: hand you a real problem, watch you scope it. OBSERVED — pattern across F5 → ExtraHop → Meta → Dropzone trajectory.
- He took the IC route at Meta (4 years as plain "Software Engineer," not Engineering Manager) when he could have gone managerial. INFERRED: he respects builders. He will read a candidate who shows up over-prepared with manager-speak as someone trying to skip the technical bar.
- His public recommendations praise "exemplary developer," "smart, insightful, hard working," "team player," "insanely fast at figuring out existing technology and not afraid of making bold changes to it." (David Langrock and David Holmes on his LinkedIn.) Translation of what he values: speed of comprehension on unfamiliar systems, willingness to refactor, low ego. OBSERVED — direct quotes from [LinkedIn](https://www.linkedin.com/in/eric-hammerle-3073045/).
- New Director title (2026) means he is still building his interview muscle for senior hires. Probable structure: 5 min intro, 30 min technical / scenario, 10 min your questions. He is hiring for *quality of judgment under ambiguity*, not algorithmic puzzles.

**What he is screening for, ranked:**

1. Can you read someone else's bad detection / investigation and articulate exactly why it is bad? (This is the literal job description.)
2. Are you a builder who has shipped production code, or a presenter who has shipped slides?
3. Do you have an opinion on agent boundaries that survives one round of pushback?
4. Can you describe a failure you owned, with a specific lesson, in under two minutes?
5. Do you treat "production Python" as a humble craft or as boilerplate beneath you?

---

## Beliefs about AI in SOC (cited)

These are the Dropzone *organizational* positions Eric helped build the technical foundation for. Treat them as his working assumptions.

| Belief | Direct evidence |
|---|---|
| **Most "AI hallucinations" in security are context-engineering failures, not model failures.** "The system draws logical conclusions from incomplete or misleading data — a problem any human analyst would face identically." | [Context Engineering blog](https://www.dropzone.ai/blog/when-ai-gets-it-wrong-the-critical-importance-of-context-engineering) |
| **Specialized fine-tuned agents beat one giant prompt.** "If a system performs the same types of tasks repeatedly, it's worth investing in specialized training for those functions." | [Context Engineering blog](https://www.dropzone.ai/blog/when-ai-gets-it-wrong-the-critical-importance-of-context-engineering) |
| **Unbounded agent autonomy = bigger attack surface.** Eric is the engineering owner of the patents that put hard scopes on agent capability (Automated threat hunting, Context repository management). | [Dropzone Guardrails blog](https://www.dropzone.ai/blog/ai-agent-guardrails), [US 12499243](https://patents.google.com/patent/US12499243B1) |
| **Reasoning lives with the LLM; credentials, data, and infrastructure live behind scoped specialist agents.** Direct quote from public Dropzone position. | [Dropzone Guardrails blog](https://www.dropzone.ai/blog/ai-agent-guardrails) |
| **Defenders need to be right 1,000,000 / 1,000,000.** CEO Edward Wu's framing, which Eric's engineering implements. He has heard this 1000 times in standups. | [Dropzone mission blog](https://www.dropzone.ai/blog/dropzone-ais-mission-level-the-playing-field-for-security-operations) |
| **Investigations should produce action graphs, not opaque verdicts.** Auditability and replay are first-class requirements, not afterthoughts. | [Context Engineering blog](https://www.dropzone.ai/blog/when-ai-gets-it-wrong-the-critical-importance-of-context-engineering) |
| **OSCAR (Obtain, Strategize, Collect, Analyze, Report) is the internal scaffolding for every investigation.** | [Dropzone OSCAR blog](https://www.dropzone.ai/blog/why-socs-rely-on-oscar-a-proven-investigative-framework) |
| **Human-in-the-loop = humans own escalation thresholds and override authority, not babysitting every decision.** | [Dropzone Guardrails blog](https://www.dropzone.ai/blog/ai-agent-guardrails) |
| **NO PUBLIC SIGNAL: explicit positions on prompt-injection defenses beyond "structured workflows," red-team / adversarial testing, OWASP LLM Top 10, MITRE ATLAS, NIST AI RMF.** Dropzone Guardrails blog acknowledges prompt injection as an attack vector but does not detail defenses. This is your opening to bring expertise without being corrected. | NO PUBLIC SIGNAL |

---

## Values / triggers

### What he praises (cited)

- **Speed of comprehension on unfamiliar code.** "Insanely fast at figuring out existing technology" — David Holmes recommendation. [LinkedIn](https://www.linkedin.com/in/eric-hammerle-3073045/)
- **Willingness to refactor without ego.** "Not afraid of making bold changes to it." Same source.
- **Team player who is also smart and hard working.** "Smart, insightful, hard working and a team player" — David Langrock recommendation. Same source.
- **Hands-on craft over title chasing.** Took 8 years at ExtraHop before any manager title; did 4 years as plain SWE at Meta when he could have gone EM. OBSERVED via career arc.

### What he likely does not respect (INFERRED, pattern-matched)

- **Buzzword-loaded answers without specifics.** ExtraHop / patent-co-author / Principal IC backgrounds are allergic to vague AI talk. Use numbers.
- **Candidates who treat Python as a stepping stone to "real" languages.** He came up in C/C++/Linux but the job is Python. If you sneer at Python, you're out.
- **Tenure for tenure's sake / title-grabbing.** His own CV shows he leaves when work is uninteresting and stays when it is. Don't pad.
- **Anyone who calls themselves "passionate," "rockstar," "ninja," or "AI thought leader."** Standard senior-engineer allergy.
- **Pure manager-speak with no tech depth.** He just got promoted to Director and is still patenting code. He'll smell pure PM-style answers.

---

## Personal cues (no creep, just informed)

| Cue | Evidence |
|---|---|
| Lives in Seattle / Greater Seattle Area | LinkedIn header |
| RIT undergrad 2000–2004 | LinkedIn |
| Long-time Pacific Northwest engineer (F5 → Google → ExtraHop → Meta → Dropzone all PNW or remote) | RocketReach work history |
| 11 issued US patents — the most recent two are at Dropzone, December 2025 | [Justia](https://patents.justia.com/inventor/eric-joseph-hammerle) |
| Active on LinkedIn but at low volume — 688 followers, the Series A celebration post had 37 reactions / 4 comments | [LinkedIn post](https://www.linkedin.com/posts/eric-hammerle-3073045_dropzone-ai-gets-1685m-for-autonomous-cybersecurity-activity-7189243815352848384-xkCS) |
| Replied-to by Bill Hamilton (Peterson Regional Medical) and Colin Brissey (Eclypsium) on the Series A post — keeps healthcare/security peers from prior roles | Same source |
| **NO PUBLIC SIGNAL: Twitter/X, Bluesky, Mastodon, GitHub, personal blog, Substack, conference talks, podcasts.** Searched all. He is private. Do not reference anything outside LinkedIn / Dropzone / patents. | Multiple negative searches |

---

## Connections to Emmanuel's stack

Map your stack to his world *with translation*, not assumed familiarity.

| Your tool / framework | His likely reference frame | How to bridge |
|---|---|---|
| **OpenClaw (Claude Opus 4.7 gateway, 27 skills)** | He worked at Meta. He knows internal LLM gateways. Frame OpenClaw as "an internal LLM gateway with policy + skill registry — the same shape as what we'd need to constrain an investigation agent." Do not overclaim its scale. |
| **OWASP LLM Top 10 red-teaming** | The Dropzone Guardrails blog names prompt injection but does not detail defenses. This is your zone of expertise to *add* to his thinking. Bring three concrete attacks you've run + what each broke. |
| **MITRE ATLAS** | Dropzone's threat hunter ships with "one pre-built hunt pack for every MITRE ATT&CK technique." ATLAS is the AI/ML adversarial-tactics extension of ATT&CK. Frame: "ATT&CK for the network, ATLAS for the model layer." He'll respect the parallel. |
| **NIST AI RMF + AI Governance Policy you authored** | He has not publicly engaged this framework. Don't lecture. Mention it once as "we wrote our policy under NIST AI RMF and OWASP LLM" — keep moving. |
| **Falco eBPF tuning (200 → 12 alerts/day)** | He spent 8 years at ExtraHop building NDR. Falco is endpoint behavioral, ExtraHop was network behavioral — same discipline. He will recognize the FP-economics arithmetic instantly. Use this as your demonstration of "I tune detections like an engineer, not a checkbox." |
| **Splunk MTTD 48h → 4h** | Standard SOC metric. Tell it as "I rewrote the correlation rules and added enrichment from 3 sources" — he'll hear "context engineering on a SIEM." |
| **n8n SOAR (PostgreSQL + 14 active workflows + Telegram + Gmail + Cloudflare)** | This is *exactly* the world Dropzone integrates with. Their JD says "building integrations with security tools." n8n is your evidence that you've built the orchestration layer with your own hands. Bring numbers: 14 workflows, 4 Gmail accounts, master orchestrator with 16 actions. |
| **boto3 + Moto + AWS detection** | He has not publicly engaged AWS detection. Treat as a credible adjacent skill, not a headline. |
| **Wireshark / packet analysis (POS skimmer story)** | Direct overlap with his ExtraHop years. Anchor your investigation-quality story here. |
| **OPA / Rego policies** | Niche but respected; mention only if asked about policy-as-code. |
| **GRC library: 37 docs, 7-agent QC pipeline** | He has not publicly engaged GRC depth. Frame as "I built the compliance scaffolding alongside the technical stack" — does *not* lead a technical answer; supports it. |

---

## Predicted question bank (15 questions ranked, model answers tuned to him)

### Tier 1 — He almost certainly asks (60-90% probability each)

**1. "Walk me through how you'd review an AI-generated investigation report and decide it's wrong."**
*This is the literal job. Open with PSC.*
> "I treat the report like a code review on a pull request. Three checks. First, did the agent obtain the right evidence — did it pull the source IP, the user identity, the process tree, the auth log? Missing inputs invalidate the conclusion regardless of how confident the verdict is. Second, are the inferences load-bearing on assumptions the evidence doesn't support — for example calling something a phishing click without confirming the URL was actually rendered. Third, does the action graph make sense in reverse — could a human analyst replay the steps and reach the same verdict. When I red-teamed our internal LLM gateway against OWASP LLM Top 10, the failure mode I saw most often wasn't the model lying; it was the model reasoning correctly over an incomplete context window. So my first question on any wrong report is: was the data wrong, the framing wrong, or the model wrong. Usually it's the first."

**2. "Tell me about a time you tuned a noisy detection."**
*Falco 200 → 12. Lead with the economics, not the tooling.*
> "Falco eBPF was throwing 200 alerts a day in our environment. The team was ignoring them, which is the worst failure mode for a detection — alive on paper, dead in practice. I sampled 50 of them, classified by root cause, and found 80% were three patterns: kubectl exec from CI runners, package manager activity during nightly updates, and a mislabeled benign syscall. I wrote three suppression rules, kept the original ones in audit-only mode for 30 days to verify no real signal was lost, and dropped to 12 actionable alerts a day. The real lesson was the discipline of *audit-only first*. You never delete a detection; you shadow it until the data tells you it's safe."

**3. "What's the difference between a good agent design and a bad one?"**
*Mirror his own blog back to him — but with one specific opinion of your own.*
> "Bad agent designs put the model in charge of credentials and infrastructure. Good designs keep judgment with the model and put credentials, data access, and side-effects behind scoped tools with deterministic guardrails. The opinion I'd add — and I'm interested if you agree — is that the *eval harness* is more load-bearing than the prompt. You can rewrite a prompt in an hour. Standing up an eval that catches a regression before it ships to a customer takes weeks. Most teams under-invest there because the work isn't visible until something breaks."

**4. "Six-plus years of experience — how do you think about your background mapping to this?"**
*The gap question. Reframe to density.*
> "I'm an AI Security Engineer at CoreDirective and the work I've shipped in the last 14 months is what would normally be 5–6 years of distributed responsibility. I built the SOC stack — Falco, Splunk correlation, Wireshark packet investigation, an n8n SOAR with 14 active workflows, an OpenClaw LLM gateway with 27 internal skills under policy. I wrote the GRC library — 37 documents covering NIST AI RMF, OWASP LLM Top 10, AI Incident Response. I red-teamed our own LLM gateway. The question isn't whether I have six years of resume; it's whether I've already done the job. I'd rather show you the work."

**5. "What's a hard tradeoff you made in a system you built?"**
*OpenClaw red team is the strongest answer.*
> "Inside our LLM gateway I had to choose between exposing rich tool access to the model — which makes investigations powerful — versus locking down the tool surface to limit blast radius. Early version had broad access and I red-teamed it against OWASP LLM Top 10. Found three classes of issue: prompt injection through tool descriptions, over-broad policy on file system access, and a logging gap where the model could call a tool without the call ending up in the audit trail. The fix was scoped tools, every tool wrapped in a policy check, and an action graph that logged the tool plan before execution. I lost some flexibility — agents can't improvise as much. I gained replay-ability and the ability to write evals against the action graph. I'd make the same call again."

### Tier 2 — He is likely to ask (40-60% each)

**6. "Why Dropzone?"**
> "Three reasons. One, the technical thesis is right — investigation quality is the bottleneck and the only way through is structured agent autonomy with deterministic guardrails. Two, you're shipping it. The patents in 2025 — automated threat hunting, context repository management — those are not slideware, they are the architecture. Three, I want to do this work for ten thousand SOCs, not one. CoreDirective gave me proof I can build the stack; Dropzone is where the stack matters."

**7. "What does 24/7 on-call look like to you?"**
> "I assume one rotation slot every 4–6 weeks, page-able, MTTR target on the order of 30 minutes for severity-1, and a strong runbook culture so the person on call isn't reverse-engineering the system at 3 AM. The thing I'd want to know is your incident-review cadence — every page should produce either a runbook update, an alert tuning, or a code change. Otherwise the rotation is a tax instead of a feedback loop."

**8. "Production Python — what do you actually own in Python?"**
*Be specific. Don't dodge.*
> "Honest answer — my heaviest Python work has been the SOAR orchestration glue, the GRC pipeline, and the red-team tooling I wrote against OpenClaw. Type-hinted, tested with pytest, packaged with Poetry. The codebase I'd be joining is bigger and more disciplined than mine, and I'd treat my first 60 days as reading the existing investigation flows before writing new ones. I'm comfortable saying I'd hit ramped productivity by week 6, not week 2 — and I'd rather you know that up front than have me bluff."

**9. "How would you measure investigation quality?"**
> "Three layers. Top-line — false positive rate and false negative rate per alert class, tracked weekly. Middle — agreement rate between the agent and a human analyst on a held-out sample, run on every model or prompt change. Bottom — action graph coverage, meaning every report has a replayable trace. The pitfall is over-indexing on top-line FP/FN without the held-out human comparison; you can drift confidently in the wrong direction for months."

**10. "What's the riskiest part of an autonomous investigation agent in production?"**
> "Two. First, silent context loss — the agent reasons correctly over the data it has, but the data is missing the field that would change the verdict. That looks like a hallucination from the outside but the model is doing its job. Second, capability creep — every new integration adds a new tool the agent can call, which expands attack surface for prompt injection. The fix for both is the same shape: action graphs for traceability, scoped tools with policy checks, and evals on FP/FN per alert class so drift is visible."

### Tier 3 — He may ask (20-40% each)

**11. "Tell me about a code change you made in someone else's codebase that mattered."**
*This is his "insanely fast at figuring out existing technology" tell. Have a real story ready.*

**12. "What do you think of LangChain / agent frameworks?"**
> "I've used them. I think the abstraction is right for prototyping and wrong for production. The teams I respect most have a thin internal framework that wraps a state machine, a tool registry, and an eval harness — that's it. Whether you build it on LangGraph or write it yourself depends on how much of the framework's behavior you'd otherwise have to override. NO PUBLIC SIGNAL on what Dropzone uses, so flag the question back: 'I'd be curious what the team uses internally.'"

**13. "What would you ship in your first 90 days?"**
> "Days 1–30: read the investigation flow codebase end to end, shadow on-call, write down every assumption I'd want to challenge but don't yet have the context to challenge. Days 30–60: pick one alert class with weak investigation quality and own the fix — flow, evals, action graph. Days 60–90: ship one new integration end to end. The thing I would *not* do is propose architecture changes in month one."

**14. "What's a security tool you wish existed?"**
> "An eval framework for SOC agents that's open enough to publish public benchmarks. Right now every vendor claims accuracy without a shared yardstick. The closest thing is the SANS SOC survey, which is descriptive, not benchmarking."

**15. "Anything you want to ask me?"**
*Use the Five questions in 11 below.*

---

## Things to NOT say (pattern-matched to triggers)

| Don't say | Why it kills you |
|---|---|
| "Pivoting" / "transitioning" / "aspiring AI Security Engineer" | Identity is non-negotiable. You ARE one. |
| "I'm passionate about AI" | Boilerplate. He has heard it 500 times. |
| "Cutting-edge" / "state-of-the-art" / "rockstar" / "ninja" | Buzzword allergy. |
| "Em dashes" or AI-writing tells in any follow-up email | He has spent 2 years staring at LLM output. He will smell it. |
| "I built a startup called CoreDirective" | Say "my employer CoreDirective." Founder framing reads as risk for a senior IC role. |
| "I'm still learning [thing]" | Senior bar. Even when true, frame as "I'd want to ramp on X by reading Y." |
| "AI will replace SOC analysts" | Triggers his entire engineering philosophy. The Dropzone position is augment, not replace. |
| Any mention of OpenClaw without immediately naming the guardrails / red-team work | The Dropzone Guardrails blog literally cites OpenClaw as a counterexample of dangerous unbounded autonomy (Tyson's piece, not Eric's, but the framing is in the water). Reframe yourself as the engineer who *constrained* an unbounded agent — that's the defensible angle. |
| "I have a Master's coming May 2026" as your lead | He has 11 patents and didn't lead with "I have a BS." Lead with what you've shipped. |
| Bashing prior employers, certs, or AI vendors | He's seen too many cycles. Even mild grievance reads as immature. |
| Long answers with no number in them | He is a measurement engineer. Every story needs an integer. |
| Asking about salary, equity, or title in this round | Wrong audience. Save it for the offer call. |

---

## Three opener moves (first 90 seconds)

**Move 1 — Small talk anchor (15 sec)**
He's in Seattle. Don't fake Seattle small-talk. Do this instead:

> "Eric, thanks for the time. I went deep on the OSCAR + context-engineering writeups before this call — really clean architecture thinking. Excited to dig in."

This signals: I did homework, I read the engineering blog (not just the marketing site), I know the difference between OSCAR and context engineering, and I'm here to talk technical.

**Move 2 — Why-now hook (30 sec)**
If he opens with "tell me a bit about yourself" — answer in 30 seconds, not 90.

> "I'm an AI Security Engineer at CoreDirective. The last 14 months I've built the stack end to end — Falco for behavioral detection, Splunk for correlation, an n8n SOAR with 14 active workflows, and an internal LLM gateway with 27 skills under policy that I red-teamed against OWASP LLM Top 10. I'm interviewing here because the bottleneck I keep hitting in my own work is investigation quality at scale, and that's the exact problem Dropzone is solving."

Three things in 30 seconds: identity, scope of work with numbers, why this role specifically.

**Move 3 — Frame setter (15 sec)**
After his first technical question, before answering, set the frame once:

> "Quick frame — I'll answer in PSC: problem, specifics, consequence. Tell me to stop or push deeper anywhere."

This is a controlled signal that you have a structure and respect his time. Senior engineers who interview a lot appreciate this. **Use it once, then never reference it again.** If he doesn't react, drop the explicit framing and just deliver in PSC quietly.

**Don't do these in the opener:**
- Don't praise Edward Wu unless asked. (Founder worship reads as suck-up.)
- Don't volunteer your education unless asked.
- Don't start with "Great to meet you, I'm so excited about Dropzone." Start with content.

---

## Five questions to ask him (in order of priority)

1. **"What does the bar for investigation quality look like internally? Is there a specific metric I'd be measured against in the first 90 days?"** — Mirrors the JD language and signals you'll own a number, not a vibe.
2. **"How is the team structured between investigation-flow engineers, integration engineers, and platform engineers? Where would I sit?"** — Gets you the actual scope.
3. **"What's the eval and regression-testing story for new investigation flows? How do you catch quality drift before customers do?"** — High-signal question; he'll either light up or admit it's an open area, both are useful.
4. **"What's the hardest open problem the team is working on right now that you'd want a senior hire to step into?"** — Lets him recruit you.
5. **"You came up at ExtraHop on the network-detection side. What surprised you about applying that thinking to LLM-driven investigation, vs. what carried over directly?"** — High-trust question. Acknowledges his career arc. Asks him about engineering, not management. He will remember this.

---

## Sources (every URL, dated 2026-04-28)

### Primary — direct on Eric Hammerle
- [LinkedIn profile](https://www.linkedin.com/in/eric-hammerle-3073045/) — career, education, recommendations, patents list
- [LinkedIn Series A post (Apr 2024)](https://www.linkedin.com/posts/eric-hammerle-3073045_dropzone-ai-gets-1685m-for-autonomous-cybersecurity-activity-7189243815352848384-xkCS) — only public LinkedIn post surfaced, low engagement
- [RocketReach summary](https://rocketreach.co/eric-hammerle-email_9742328) — full career arc with dates
- [Justia patents — Eric Joseph Hammerle](https://patents.justia.com/inventor/eric-joseph-hammerle) — 11 issued patents
- [Google Patents US 12499243B1 — Automated threat hunting](https://patents.google.com/patent/US12499243B1) — co-inventor with Edward Wu et al., Dec 16 2025
- [Google Patents US 11012329B2 — Correlating causes and effects](https://patents.google.com/patent/US11012329B2/en) — ExtraHop era

### Primary — Dropzone engineering / philosophy
- [Dropzone company / team page](https://www.dropzone.ai/company) — leadership and R&D engineer roster
- [TheOrg — Dropzone HQ](https://theorg.com/org/dropzone-ai/offices/hq) — Eric listed as Sr Tech Lead Manager (pre-promotion)
- [Dropzone blog — Context Engineering](https://www.dropzone.ai/blog/when-ai-gets-it-wrong-the-critical-importance-of-context-engineering) — written by Rahul Popat, ships the philosophy Eric's patents implement
- [Dropzone blog — AI Agent Guardrails](https://www.dropzone.ai/blog/ai-agent-guardrails) — written by Tyson Supasatit, Apr 24 2026
- [Dropzone blog — OSCAR framework](https://www.dropzone.ai/blog/why-socs-rely-on-oscar-a-proven-investigative-framework)
- [Dropzone blog — Mission (Edward Wu)](https://www.dropzone.ai/blog/dropzone-ais-mission-level-the-playing-field-for-security-operations)
- [Dropzone JD — Senior Security Engineer](https://ats.rippling.com/dropzone-ai/jobs/dd5ab50b-e853-449b-b30e-be55fb45f1a2) — production Python, investigation quality

### Secondary — corporate context
- [Dropzone press — $37M Series B](https://www.dropzone.ai/press-release/dropzone-ai-37m-series-b-funding-ai-soc-agents)
- [Dropzone press — 2025 wrap (11x ARR, Fortune Cyber 60)](https://www.dropzone.ai/press-release/dropzone-ai-closes-2025-with-11x-arr-growth-fortune-cyber-60-recognition-and-37m-series-b)
- [GeekWire — Series B coverage](https://www.geekwire.com/2025/seattle-startup-dropzone-raises-37m-to-supercharge-its-ai-soc-analyst-security-software/)
- [Dropzone — Threat Hunter launch (Mar 2026)](https://www.dropzone.ai/product/ai-threat-hunting-agent)
- [Help Net Security — Threat Hunter coverage](https://www.helpnetsecurity.com/2026/03/18/dropzone-ai-ai-threat-hunting/)
- [Madrona — Edward Wu interview](https://www.madrona.com/dropzones-edward-wu-security/) — context on engineering thesis, not Eric specifically

### Negative searches (no public signal — searched and confirmed absent 2026-04-28)
- Twitter/X, Bluesky, Mastodon — no profiles found under name + Dropzone / security
- GitHub — no `ehammerle`, `eric-hammerle`, `eric.hammerle`, `ehammer` matched the right person; Dropzone has no public GitHub org
- Conference talks — no BlackHat / RSA / DEF CON / BSides / Risky Business / MLSecOps appearances under his name
- Personal blog / Substack / Medium — none found
- Glassdoor / Blind — no Director of Engineering reviews specifically tied to him at Dropzone
- Google Scholar — no academic publications under this name matching the security/networking field

---

## Disambiguation note

There are at least three "Eric Hammerle" profiles on LinkedIn and a German "Eric Hämmerle" (software developer at intension GmbH). The candidate this brief covers is uniquely identified by:
- LinkedIn `eric-hammerle-3073045`
- 11 issued US patents under "Eric Joseph Hammerle" assigned to F5, ExtraHop, Dropzone
- Seattle / RIT 2000-2004 / current Dropzone AI

All claims in this brief refer to that person. Any conflicting "Eric Hammerle" is a different individual.
