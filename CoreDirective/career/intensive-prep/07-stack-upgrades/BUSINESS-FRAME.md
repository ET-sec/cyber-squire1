# Business Framing Drills: 10 Director-Level Talking Points

**Frame.** These answers belong in front of a Director of Engineering, a CISO, or a hiring manager who is screening for the senior tier. Numbers come from the real stack. The voice is direct, calm, and ownership-forward. No founder language. No "passionate about." No em dashes.

**Cadence.** 60 to 120 seconds spoken, each. Practice out loud. Time them.

---

## 1. "Tell me about your business case for AI security investment."

> "The business case starts with where the AI sits in the workflow. At CoreDirective, the AI is between an analyst and a finding. That's a high-trust position. If I don't invest in security around it, the model becomes the soft target in the stack. So my business case is three lines. One: every AI control I add is cheaper than the bad outcome it prevents. The bad outcome on a leaked client tax record is a six-figure event for a small accounting firm. The control is a few hundred dollars of engineering time and a NeMo Guardrails container. Two: AI security is the differentiator that lets me sell to a regulated client at all. Without the AI Governance policy and the eval harness, I don't get past the first compliance question. Three: the AI controls I build serve double duty as detection signal. The Promptfoo eval runs in CI and tells me the model's posture every commit. The prompt-injection classifier is also a detection event in Datadog. So every control is also a sensor. That's the math: cost a few thousand, prevents a six-figure incident, opens a market I couldn't enter without it, and produces telemetry I'd otherwise have to buy."

---

## 2. "How do you justify X in dollars."

> "I justify dollars by mapping the spend to a closed loop: cost of the control, cost of the bad outcome it prevents, probability of the bad outcome on my actual surface. CoreDirective Engine costs 48 dollars a month to run. The vendor SOAR I priced against was 5,000 a month at the low end. Over 12 months that's a 60,000 dollar avoidance. The OPA policy gate cost me four hours of engineering. It has blocked two PRs that would have shipped a public-read Spaces bucket and a DNS record outside the zone. Each of those is a reportable event in a regulated context. So the four hours bought me indefinite avoidance of two specific incidents. I keep the math at that resolution because that's what a CFO can read. If I can't say which specific dollar an investment saves, I haven't earned the budget."

---

## 3. "How do you communicate risk to executives."

> "I write one-pagers, not slides. The format is the same every time: top of the page is the decision the executive needs to make. Middle of the page is three to five lines of evidence: the threat, the surface, the control or fix, the cost, the residual risk. Bottom of the page is the recommendation in a single sentence. When I scoped AI services for the accounting client, the partner wanted hybrid cloud-LLM on cost grounds. I sent a one-pager that said 'recommend local Ollama on a dedicated host' with the cost delta in dollars, the residency guarantee in plain English, and the policy reference. The decision changed in 24 hours. Executives don't want a security education. They want a clear ask, a defensible recommendation, and the cost of being wrong. The AI Governance policy in my GRC corpus exists because that one-pager became repeatable."

---

## 4. "Walk me through your security roadmap."

> "Three horizons. Horizon one is the next 90 days, all detection and prevention controls that have a CI gate behind them. Promptfoo on every OpenClaw commit. Falco rules tuned for agentic abuse. Sigma library for portability. AI Bill of Materials. That's the substrate. Horizon two is six months: a real-time prompt-injection classifier inline at the gateway, a LangGraph triage agent reading Falco alerts, NeMo Guardrails at the n8n LLM boundary. Each one ships independently and earns its keep on the day it ships. Horizon three is twelve months: SOC2 readiness with the GRC corpus as the working SSP, a coverage matrix mapping every detection rule to ATT&CK, ATLAS, and SOC2 CC, and Chainguard base images across the custom containers for the supply-chain story. The order is detection first because detection earns trust, then prevention, then audit. Reverse that order and you spend two years on compliance and never catch anything."

---

## 5. "What is your stance on build vs buy."

> "Default to buy when the vendor solves a problem you'll never need to differentiate on, and the data stays on a substrate you can move. Build when the substrate matters, when the integrations are part of your moat, or when the lock-in cost in two years is more than the build cost today. SOAR I built. n8n self-hosted, 14 workflows, 48 dollars a month. The vendor option was 5,000 to 50,000 a month and irreversible lock-in. SBOM I bought, Trivy in CI, free, exports clean to my GRC corpus. Authentication I bought, Keycloak, because identity isn't a moat for me. The pattern: build the layer where I'm the operator, buy the layer where I'm just a consumer. When I can't tell which I am, I prototype both for a week and pick the one that survives a real workload."

---

## 6. "How do you measure security ROI."

> "Three metrics. One: avoided incidents per dollar invested, measured over a horizon long enough that the noise smooths out. The OPA gate cost me four engineering hours and has blocked two specific misconfig PRs. Two: control coverage as a percentage of the surface, with a bias toward depth at the highest-risk surface. My Promptfoo harness covers ten OWASP LLM Top 10 categories on the AI gateway because that's the highest-risk surface in the stack. Three: time from detection to action, because a control that detects late is a control that didn't fire. Falco to Telegram to incident draft is currently under five minutes for a medium-severity alert. The trap I avoid is reporting controls deployed as if it were progress. Controls deployed without coverage data is theater. ROI shows up in the second derivative: how much the bad-outcome rate changes after the control lands."

---

## 7. "Tell me about a tradeoff you made between security and speed."

> "On the migration from AWS to DigitalOcean. I had 48 hours to move the stack because the AWS account was being suspended for nonpayment. Every part of me wanted to bring up Vault and Keycloak first because that's the proper order. But the master orchestrator was offline and the bots were dead. So I made a tradeoff explicit: I brought up the n8n SOAR layer first with .env-file secrets, and I committed in writing that Vault and Keycloak would land within 14 days. Wrote the commitment into the project memory. Set a calendar alarm. Hit the deadline at day 11. The principle: you can take on security debt as long as you account for it the same way you account for technical debt. Write it down, schedule the payback, ship the payback. The mistake is to take debt and pretend it isn't debt. The second mistake is to refuse the debt and lose the system."

---

## 8. "What metrics do you track for an AI system."

> "Four families. One: input quality, measured by the prompt-injection classifier score distribution. Anomalies in the input distribution are usually the first sign that something is off. Two: output quality, measured by the eval harness. Promptfoo runs on every commit, scoring grounding, completeness, and adversarial-resistance. If the score drops below threshold, the build fails. Three: behavior, measured by tool-call patterns. If the agent invoked GitHub-write and the user prompt was about Tavily search, that's a behavioral anomaly and I want a Datadog event. Four: cost and latency. Inference cost per workflow, p95 latency, and tokens per response. Cost is a security signal too: a sudden spike in tokens often means somebody is exfiltrating context. The point of metrics for an AI system is the same as metrics for any system: they tell you when reality has diverged from your model of reality. The earlier you catch the divergence, the cheaper the fix."

---

## 9. "How does compliance fit into your AI security program."

> "Compliance is a customer of the security program, not the boss of it. The GRC corpus at CoreDirective is 37 documents because the engineering work generated the evidence and I documented it. Not the other way around. The AI Governance policy doesn't tell engineering what to do; it describes what engineering already does. NIST AI RMF, NIST CSF 2.0, OWASP LLM Top 10, MITRE ATLAS are the frameworks I map to because they map cleanly back to controls I'd run anyway. The benefit of doing it in this order: when an auditor asks for evidence on a control, the evidence already exists in the form of a CI run, a Falco event, a Datadog query, an OPA gate decision. I don't write evidence after the fact. I write evidence as a side effect of running the system. That's the only compliance program that scales with one operator."

---

## 10. "How do you operate as a one-person security team."

> "Three principles. One: every system I run has to be readable at 2am on four hours of sleep. If a runbook isn't in the corpus, the system isn't ready. The runbook is the deliverable, the deployment is the byproduct. Two: leverage every CI gate, every policy-as-code rule, every Falco rule as a force multiplier. The OPA policies in my Terraform pipeline are eight rules that act like an extra reviewer on every PR. The Promptfoo harness is a red team I don't have to schedule. Three: I architect for the team I don't have yet. Every secret in Vault, every policy in Rego, every workflow in version control, every doc in the GRC corpus, every change in a commit message that an outsider could read. The day a second engineer joins, they can read everything. That's the only way one operator can run a 13-service production stack with an AI gateway and a SOAR layer at 48 dollars a month: by treating the system as if it has to survive me."

---

## Drilling protocol

**Solo drill (15 min).**
- Pick three of the ten. Read aloud at speaking pace. Time each one.
- Repeat each three times. Drop any phrase that catches your tongue.

**Pair drill (30 min).**
- Have someone else read the question. Answer cold. No notes.
- They cut you off at 120 seconds. Note where you ran out of time.
- Iterate the answer down. Density wins over breadth.

**Voice memo drill (10 min, daily).**
- Record one of the ten on your phone every morning.
- Play it back while making coffee. Listen for AI tells, hedging, and where you trailed off.
- The goal is your speaking voice landing in 90 seconds without rehearsal.
