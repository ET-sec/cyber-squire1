# PROCESS: Live Threat Modeling in an Interview

This is the exact 7-phase process to run when an interviewer says "threat model this system for me". Total time budget: 25 to 30 minutes. Each phase has a target time and verbatim phrasing.

---

## The 90 Second Opening Monologue (memorize cold)

When the interviewer drops the prompt, do not start drawing yet. Take command of the conversation with this opening. It signals senior, slows the pace to your benefit, and sets the deliverable.

> "Before I draw anything, let me clarify the scope so we are solving the same problem. I am going to walk through this in seven phases. First I want to lock down what we are protecting and from whom. Second I will draw a level zero data flow diagram so we can both see the system. Third I will walk every trust boundary and apply STRIDE, and where this involves machine learning I will overlay MITRE ATLAS. Fourth I will rank threats by likelihood and impact. Fifth I will propose mitigations with cost and impact tradeoffs. Sixth I will state the residual risk in plain terms. Seventh I will propose detections that fire if a mitigation fails. I will narrate as I go. Stop me at any point and I will go deeper on whatever you care about most. Sound good?"

Why this works:
- It frames you as someone who has done this before.
- It surfaces the interviewer's hidden priorities ("actually I care most about residual risk").
- It buys 90 seconds of calm before you have to draw anything.
- It promises seven deliverables, which is more structure than 95 percent of candidates show up with.

If they say "skip the framework, just go", you reply: "Understood. I will collapse it but I am still going to clarify scope in 30 seconds because everything else depends on it." Hold the line.

---

## Phase 1: Clarify Scope (3 to 5 minutes)

Goal: leave this phase with three lists on the board. Assets, actors, data classes.

Verbatim openers:
- "What are we protecting? In other words, if a breach happened tomorrow and made the news, what would the headline be about?"
- "Who are the actors that touch this system? Customers, employees, partners, attackers from the internet, malicious insiders, supply chain?"
- "What data classes flow through this? PII, payment, health, source code, model weights, secrets, internal-only?"

Assumptions you state out loud (write them on the board):
- "I am assuming this is production, not pre-launch. Tell me if that is wrong."
- "I am assuming the threat actor is a financially motivated external attacker plus a curious insider, unless you want me to add nation-state."
- "I am assuming we want to optimize for business risk, not academic completeness."

Output of phase 1, written on the board:
```
ASSETS:        [3 to 5 items]
ACTORS:        [4 to 6 entities]
DATA CLASSES:  [3 to 5 categories with sensitivity ratings]
ASSUMPTIONS:   [the three you stated]
```

---

## Phase 2: Draw the Data Flow Diagram (5 to 8 minutes)

Notation rules (use these symbols, do not improvise):

```
External entity:   [ Rectangle ]
Process:           ( Rounded box ) or  O 
Data store:        =====
                   |   |    or  cylinder
                   =====
Data flow:         -------->
Trust boundary:    - - - - -
```

Procedure:
1. Start with external entities at the edges (left for users, right for upstream services, top for admins).
2. Draw processes in the middle, labeled with what they do and what tech they run on.
3. Draw data stores below their owning process.
4. Connect with arrows. Label each arrow with the data it carries (not the protocol).
5. Last step, drop the dashed trust boundary lines. Every external arrow crosses at least one boundary.

Verbatim while drawing:
- "I am putting the customer here on the left because that is the source of the most diverse input. Internal admin goes top right because that is privileged."
- "This dashed line is the internet boundary. Everything that crosses it must be authenticated and re-validated."
- "I will not draw protocols on the lines. I am drawing data classes because that is what attackers want."

Common mistakes to avoid:
- Do not draw infra boxes (load balancer, firewall) as their own processes. They are properties of an arrow, not nodes.
- Do not connect data stores to data stores directly.
- Do not skip the trust boundaries. The whole point of the next phase depends on them.

---

## Phase 3: Walk Each Trust Boundary, Apply STRIDE (8 to 10 minutes)

Procedure: point at each dashed line. For every flow that crosses it, ask the six STRIDE questions out loud.

Verbatim cadence per boundary:
- "At this boundary, can someone Spoof identity?"
- "Can someone Tamper with the data crossing it?"
- "If something bad happens here, would we have evidence? That is Repudiation."
- "Can data leak across this boundary in the wrong direction? That is Information disclosure."
- "Can someone deny service across this boundary?"
- "Can someone elevate privilege across this boundary?"

Capture format on the board:

| # | Boundary | STRIDE | Threat | Likelihood | Impact |
|---|----------|--------|--------|------------|--------|
| 1 | Internet to API | S | Forged JWT | M | H |
| 2 | API to DB | T | SQL injection | M | H |
| 3 | LLM to tool | E | Prompt injection invokes admin tool | H | H |

Aim for 10 to 15 threats. Quality beats quantity. If you hit 20 you are listing controls, not threats.

For LLM systems, after STRIDE add an ATLAS pass:
- "Now I am going to overlay ATLAS for the ML-specific surface."
- "AML.T0051 prompt injection at this boundary."
- "AML.T0024 model exfiltration via inference queries here."
- "AML.T0020 training data poisoning if we ever fine-tune on this corpus."

---

## Phase 4: Prioritize (3 minutes)

Two acceptable ranking methods. Pick one and stick with it.

**Option A: HML matrix (preferred for live sessions)**

| Likelihood \\ Impact | Low | Medium | High |
|---------------------|-----|--------|------|
| High                | M   | H      | H    |
| Medium              | L   | M      | H    |
| Low                 | L   | L      | M    |

**Option B: DREAD (use only if interviewer asks)**
Score each threat 1 to 10 on Damage, Reproducibility, Exploitability, Affected users, Discoverability. Average. Above 7 is High, 4 to 7 Medium, below 4 Low.

Verbatim to introduce:
- "I am going to rank with a simple high-medium-low matrix because DREAD scoring tends to invent precision that is not really there. If you want DREAD I can pivot."

---

## Phase 5: Propose Mitigations With Tradeoffs (3 to 4 minutes)

Rule: every High threat gets a primary control plus a compensating control. Every Medium gets at least one. Lows get an acceptance rationale.

Phrasing template:
- "For threat X, the primary control is [thing]. That costs roughly [time or dollars]. It blocks the attack but it does not catch it if it happens. So the compensating control is [detection]."

Three control categories you should name in conversation:
- **Preventive**: stops the threat (auth, validation, encryption, isolation).
- **Detective**: notices the threat (logs, alerts, anomaly detection).
- **Corrective**: contains and recovers (rollback, key rotation, incident response runbook).

Senior-sounding tradeoff phrases:
- "This is the right control but it adds 50 to 100ms of latency. Worth it on auth flows, not worth it on read-only public endpoints."
- "We could enforce this at the WAF or at the application. WAF is cheaper to deploy, application is more accurate. I would do both with the WAF as the broad net."
- "I would rather pay engineering cost once on a strong primary control than pay perpetual operations cost on a weak detective control."

---

## Phase 6: State Residual Risk Explicitly (2 minutes)

This is the phase where most candidates lose senior signal. They wave their hands. Do not do that.

Rule: residual risk is what is left after controls are in place. State it in three dimensions: severity, ownership, acceptance.

Verbatim template:
- "After mitigations, the residual risk profile is [count] HIGH, [count] MEDIUM, [count] LOW. The HIGHs are accepted because [rationale or compensating control]. The MEDIUMs are accepted because [scope, exposure, or schedule]. Anything I cannot defend acceptance for, I would treat as a stop-ship."

If the interviewer pushes ("would you ship with that?"):
- "I would ship with the MEDIUMs because they have monitoring on them. I would not ship with a HIGH that has no compensating control. That is the line."

---

## Phase 7: Propose Detections If Mitigation Fails (3 minutes)

For every High and Medium threat, name a detection. This is where senior candidates separate themselves.

Pattern:
- "Mitigation X is in place. If it fails, here is the signal that fires: [log, metric, anomaly]. The signal goes to [SIEM, on-call, page]. The runbook is [linked or named]."

Examples to keep in your head:
- Forged JWT: detection is auth-failure rate by IP, alert at 10x baseline, runbook is rotate signing key.
- Prompt injection bypass: detection is critique-loop disagreement rate, alert at 5 percent over 1 hour window, runbook is freeze the agent and snapshot transcripts.
- Container escape: detection is Falco unexpected syscall, alert immediate, runbook is isolate node and dump forensics.

Closing line for the whole session:
> "That is the threat model. Top three risks I would track personally are X, Y, Z. The residual risk position is acceptable because every HIGH has a compensating control and every MEDIUM has an owner. Where do you want me to go deeper?"

---

## Time budget cheat sheet

| Phase | Target | Hard cap |
|-------|--------|----------|
| Opening monologue | 90s | 2m |
| 1 Scope | 3m | 5m |
| 2 DFD | 6m | 8m |
| 3 STRIDE walk | 8m | 10m |
| 4 Prioritize | 2m | 3m |
| 5 Mitigations | 3m | 4m |
| 6 Residual | 2m | 3m |
| 7 Detections | 3m | 3m |
| Total | 28m | 38m |

If they cut you off at minute 15, you must have at least covered phases 1, 2, 3 with 5 threats ranked. Practice running the loop in 15 minutes.

---

## Anti-patterns to avoid

- Drawing infra (LB, WAF) as DFD boxes. They belong on the arrows.
- Listing controls in phase 3 instead of threats. STRIDE is for threats. Controls come in phase 5.
- Giving DREAD scores to 1 decimal place. False precision is junior.
- Saying "we would just rate-limit" without naming the threshold or fallback.
- Forgetting LLM-specific threats on AI systems. If the prompt mentions LLM, RAG, or agent and you do not say "prompt injection" in the first 5 minutes, you have lost.
- Ending without stating residual risk. Every senior threat model ends with "what is left and why we accept it".
