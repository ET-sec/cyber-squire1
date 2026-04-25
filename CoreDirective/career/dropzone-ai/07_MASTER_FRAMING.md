# Master Framing & Narrative — Dropzone AI

**Role:** Senior Security Engineer, Dropzone AI
**Comp:** $175k-$217k + equity, remote US
**Owner:** Investigation quality for an AI SOC Analyst (Python codebase)
**Anchor thesis:** Emmanuel is Dropzone's mirror. Dropzone builds AI agents that do investigation quality at scale. Emmanuel builds AI systems that investigate, AND he is a human analyst who has done investigation quality at the ground level. He has sat on both sides of the agent — as the one it must become, and as the one who keeps it honest.

**Red thread (memorize):**
> **"I care about investigation quality. I've done it as a human, I've built systems for it, and I want to ship it at scale to every SOC in the world."**

---

## Part 1: The Three Pitches

### 30-Second Pitch (Shaleena's opener)

> **"I'm Emmanuel Tigoue, AI Security Engineer at CoreDirective. I run a 13-container production stack on DigitalOcean with an n8n SOAR layer and a Claude Opus 4.7 gateway that I red teamed against the OWASP LLM Top 10. Before CoreDirective I was the security engineer at a Texaco franchise where I ran real investigations — packet capture, endpoint forensics, 8-hour containment down to 90 minutes. Dropzone is the exact intersection of those two jobs. That's why I'm in this room."**

Word count: 94. No em dashes. Lead is identity. Three proof points: production AI stack, red-teamed LLM gateway, real investigation work. One Dropzone hook: "exact intersection."

### 60-Second Pitch (deeper)

> **"I'm Emmanuel Tigoue, AI Security Engineer at CoreDirective. I own a 13-container production stack on DigitalOcean — PostgreSQL, n8n SOAR, Vault, Keycloak, Teleport, Falco, Datadog, a Claude Opus 4.7 gateway — all Python and Terraform, all governed by OPA/Rego policies that gate every deploy.**
>
> **On the AI side I red teamed the Claude gateway against the OWASP LLM Top 10 and MITRE ATLAS. Prompt injection, excessive agency, hallucination, output handling. Zero vulnerabilities across eight DAST categories. Four header misconfigurations found and fixed same day.**
>
> **On the investigation side, I was the security engineer at a Texaco franchise in Atlanta. One case I keep coming back to: a guest manager reported a card declining that shouldn't have. I pulled Wireshark captures, endpoint telemetry, and payment terminal logs. Found a point-of-sale skimmer routing card data to an external endpoint. Containment in 90 minutes. The investigation was the work.**
>
> **Dropzone hires for investigation quality on an AI SOC analyst. I've built AI systems that investigate, and I've done the investigation work myself. That's why this role."**

Word count: 181. Adds the POS skimmer story hook and the OpenClaw red-teaming hook.

### 2-Minute Pitch (hiring manager)

> **"I'm Emmanuel Tigoue, AI Security Engineer at CoreDirective in Atlanta. My work sits at the intersection of two things Dropzone cares about: AI systems that investigate, and the human craft of investigation itself.**
>
> **On the AI side, I run a 13-container production stack on DigitalOcean. PostgreSQL, n8n SOAR with 14 active workflows, HashiCorp Vault, Keycloak v26 for identity, Teleport v18 for privileged access, Falco for eBPF detection, Datadog for observability, and a Claude Opus 4.7 gateway I call OpenClaw. Python and Terraform throughout. Eight OPA/Rego policies gate every deploy, zero policy violations in production.**
>
> **The AI work is where it gets interesting for Dropzone. I red teamed OpenClaw against the OWASP LLM Top 10 and MITRE ATLAS — prompt injection, excessive agency, hallucination, insecure output handling, sensitive information disclosure. Zero vulnerabilities across eight DAST categories. I also designed a zero-egress inference path using Ollama and NeMo locally, specifically because sensitive triage data couldn't hit cloud endpoints. Data governance was the design constraint, not an afterthought.**
>
> **On the investigation side, before CoreDirective I was the security engineer at a Texaco franchise in Atlanta. Point-of-sale skimmer investigation using Wireshark plus endpoint forensics, 8-hour containment reduced to 90 minutes. Built a 6-step IR runbook that the staff still uses. Tuned Splunk correlation and, later, Falco eBPF rules — MTTD dropped from 48 hours to 4, alert volume from 200 a week to 12 high-fidelity ones. That's the investigation quality piece. I've done it with my own hands.**
>
> **Why Dropzone specifically: Edward Wu's ExtraHop detection-engine lineage tells me the product understands what good detection looks like. OSCAR as a methodology is real investigation practice, not playbook automation. Theory, Madrona, and IQT as investors, plus 11x ARR, tells me the market has validated execution. And the mandate for this role — own investigation quality on the AI SOC analyst — is the one part of your product where I can point to evidence on both sides of the agent.**
>
> **I graduate May 2026 with a dual degree in Cybersecurity and Business Economics. I'm US-based, clearance-eligible, no visa. I'm looking for a product-scale home where investigation quality is the mission, and Dropzone is the top of that list."**

Word count: 376. Covers identity, AI security work, detection engineering, investigation quality, why Dropzone.

---

## Part 2: "I Am Your Solution" Value Prop Matrix

| Dropzone Need | Emmanuel's Evidence | Proof Metric |
|---|---|---|
| Accuracy of AI investigations | Red teamed Claude Opus 4.7 gateway (OpenClaw) against OWASP LLM Top 10 + MITRE ATLAS for hallucination, excessive agency, prompt injection, insecure output handling | Zero vulns across 8 DAST categories, 4 header misconfigs fixed same-day |
| Investigation methodology (OSCAR-style) | 6-step IR runbook built and operated at Texaco Atlanta — observe, scope, contain, analyze, remediate, lessons-learned | 8hr → 90min mean containment; POS skimmer case closed in one shift |
| Detection engineering | Splunk correlation rules tuned at Texaco; Falco eBPF rules + Falco Sidekick → Datadog at CoreDirective | MTTD 48hr → 4hr; alert volume 200/week → 12 high-fidelity |
| Production Python | Texaco Python + PowerShell automation; n8n Code nodes across 14 workflows; OpenClaw gateway; custom SOAR orchestrator | 12 hrs/week recovered on repetitive triage; 14 workflows shipped |
| Integration building | MASTER_ORCHESTRATOR_V1 integrates 16 services with webhook-driven architecture (Postgres, Telegram, GitHub, Drive, Tasks, Sheets, Docs, Gmail, Slides, Gumroad, Ollama, Cloudflare, Notion, Tavily, Workspace Admin, Excel) | 20+ credentials wired; 10+ webhooks in production |
| Startup speed | Built 13-container production stack solo in 7 months from empty droplet to full SOC-style telemetry | 37 GRC docs + n8n SOAR + OpenClaw gateway + IAM layer + network segmentation + IaC with OPA gates |
| Customer obsession / data governance | Designed NeMo + Ollama local inference path because sensitive triage data cannot leave the tenant boundary | Zero-egress data architecture; Vault-backed secrets; Teleport PAM + JIT |
| Security rigor | OPA/Rego policies gate every Terraform deploy — IAM, network, storage, tagging, encryption | 8 policies in production, zero policy violations merged |
| Writing + documentation quality | 37-document sanitized GRC library covering SSP, POA&M, risk assessment, 10 policies, 5 IR playbooks, 6 threat modeling docs | ~15,000 lines of published writing; every alert and policy has a documented rationale |
| Identity + access architecture | Keycloak v26 RBAC + Teleport v18 for PAM/JIT across the stack | Every human and agent action is logged to a SIEM-shippable audit trail |
| Multi-agent orchestration | Telegram Supervisor Agent, MASTER_ORCHESTRATOR_V1, OpenClaw skills framework — multiple AI agents acting under human governance | 27 OpenClaw skills staged; autonomous agents with human-in-the-loop checkpoints |
| AI threat modeling | Built threat models specifically for LLM systems covering prompt injection, data exfiltration, model denial of service, training-data poisoning, insecure plugin design | 6 threat modeling docs; documented mitigations per OWASP LLM Top 10 |

---

## Part 3: Dropzone Mirror Language — 12 Hooks

Every one of these is a phrase from Dropzone's public material (product pages, blog, founder talks, hiring posts). Each has Emmanuel's parallel story ready to deploy.

1. **Dropzone:** "Investigations, not data pipelines."
   **Emmanuel:** "At Texaco I didn't run queries to check a box. I ran investigations. Wireshark packet capture on the POS skimmer wasn't a report. It was an investigation that found the attacker's exfiltration endpoint."

2. **Dropzone:** "Full reasoning transparency — the glass box."
   **Emmanuel:** "Every OPA/Rego policy I wrote is explainable. Every Falco rule has a documented rationale. Every GRC control maps to a framework clause. Auditability is how I've worked from day one."

3. **Dropzone:** "Environment mapping → documentation learning → behavior modeling."
   **Emmanuel:** "That is exactly how I approached OpenClaw red teaming. I mapped the inference graph, learned the skill documentation, modeled what an adversary would do, then attacked. Same methodology."

4. **Dropzone:** "Autonomous investigations, not SOAR playbooks."
   **Emmanuel:** "I've built both. The n8n workflows are playbooks. OpenClaw is autonomous. Playbooks are deterministic and brittle. Autonomous agents generalize and need a different governance model. I've written that governance model."

5. **Dropzone:** "Investigation quality is the mission."
   **Emmanuel:** "That is the line I wrote my cover letter around. I care about investigation quality. I've done it as a human, I've built systems for it, and I want to ship it at scale."

6. **Dropzone:** "AI that handles Tier 1 so humans work on real threats."
   **Emmanuel:** "That is the exact pattern I built at CoreDirective to cover accounting and compliance work. AI handles the repetitive tier, humans govern and escalate. I'll walk through that one in detail."

7. **Dropzone:** "Detection-engine lineage." (Edward Wu, ExtraHop)
   **Emmanuel:** "Detection engineering is my background. Splunk correlation at Texaco. Falco eBPF at CoreDirective. MTTD 48 hours to 4. That lineage maps."

8. **Dropzone:** "Context, not just alerts."
   **Emmanuel:** "I tuned Falco to drop 188 alerts per week by giving the rules environmental context — process parent, image hash, egress destination. Context-rich detection is the only kind worth shipping."

9. **Dropzone:** "Customer-obsessed engineering."
   **Emmanuel:** "When my business partner's accounting workload was killing her week, I didn't build what was fun. I built what removed the pain. Same instinct applies to a SOC analyst drowning at 2 a.m."

10. **Dropzone:** "Production Python, not notebooks."
    **Emmanuel:** "Everything on my stack runs production. n8n Code nodes, FastAPI-style endpoints on the gateway, cron-scheduled health checks, Postgres-backed state. Nothing in a notebook."

11. **Dropzone:** "Ship fast, but never ship sloppy."
    **Emmanuel:** "I shipped 13 containers in 7 months. And every one passed Trivy, Semgrep, Gitleaks, and an OPA policy gate before it merged. Speed and rigor aren't opposites on my stack."

12. **Dropzone:** "We want engineers who would use our product."
    **Emmanuel:** "I'd buy Dropzone for my own stack tomorrow. Falco Sidekick routes alerts to Datadog right now. The Tier 1 triage on those alerts is my weekend tax. That tax is exactly what Dropzone removes."

---

## Part 4: The CoreDirective Accounting AI Story — Anchor Story #2

This is the second anchor story (the POS skimmer is the first). It maps directly to Dropzone's thesis: AI handles the repetitive work so humans focus on real threats and higher-value projects. Fill in the bracketed fields tonight.

**Situation.** CoreDirective had **[WHO — business partner's name or role, e.g. "my business partner Linda, who runs operations"]** handling **[WHAT — e.g. "monthly bookkeeping, invoice reconciliation, 1099 vendor compliance, and quarterly tax prep"]** manually. It consumed **[TIME PER WEEK — e.g. "roughly 10-12 hours a week"]** and created risk because **[SPECIFIC RISK — e.g. "we were missing vendor W-9 collection deadlines, and late-stage reconciliation meant we were catching expense misclassifications after they had already hit the books. IRS exposure on the 1099 side and clean-audit risk on the books side."]**.

**Task.** Build an AI stack that could handle **[SPECIFIC TASKS — e.g. "invoice ingestion from Gmail, line-item categorization against our chart of accounts, 1099 vendor tracking, and monthly reconciliation reports"]** with **[ACCURACY TARGET — e.g. "95%+ categorization accuracy on seen vendor patterns, 100% flag rate on anything below that confidence threshold for human review"]** while meeting **[COMPLIANCE RULE — e.g. "GAAP classification, IRS 1099 thresholds, and PII handling for vendor SSNs / EINs — anything with tax identifiers had to stay on-prem"]**.

**Action.**
- **[STACK — e.g. "n8n workflow triggered by Gmail webhook on new invoice; Ollama local inference for any document containing a tax identifier (zero-egress); Claude API for general categorization and narrative summary generation; Notion as the system of record; Sheets mirror for my accountant"]**
- **[HUMAN-IN-THE-LOOP — e.g. "Anything under 85% confidence routes to Telegram for human approval before booking. Anything over 95% books directly but is logged with the prompt, the model response, and the confidence score for audit. The middle band gets batched for weekly review."]**
- **[GOVERNANCE — e.g. "Vault-backed API keys, Teleport-gated human access to the Notion workspace, all agent actions logged through MASTER_ORCHESTRATOR_V1 to Postgres, 30-day retention, Datadog dashboard tracking categorization drift over time"]**
- **[ACCURACY TESTING — e.g. "I held out 60 days of manually-categorized invoices as a test set, ran the pipeline against them in shadow mode for two weeks, measured agreement rate, tuned prompts and confidence thresholds, then cut over"]**
- **[OBSERVABILITY — e.g. "Datadog dashboard with per-category confidence distribution, weekly drift report, token cost per invoice, human override rate per vendor"]**
- **[RED TEAMING — e.g. "I ran prompt injection tests — forged invoices with adversarial text in the line-item description trying to reroute the booking, inflate the total, or leak earlier conversation context. Pipeline held. Any attempt to exfil context failed because each invoice runs in an isolated agent session with no cross-invoice memory."]**

**Result.**
- **[TIME SAVED — e.g. "10 hours a week back on her calendar"]**
- **[ERRORS CAUGHT — e.g. "Caught two vendor misclassifications from the prior quarter during the shadow-mode test that had slipped through manually"]**
- **[COMPLIANCE STATUS — e.g. "Zero missed 1099 deadlines since cutover, clean audit trail for every booking"]**
- **[COST PER TRANSACTION — e.g. "Roughly $0.03 in API spend per invoice, compared to a blended $15 of human time"]**
- **[SATISFACTION — e.g. "She told me the week I turned it on was the first week in eighteen months she didn't dread Sunday night"]**

**Lesson / bridge to Dropzone.**
> **"That is the exact pattern Dropzone runs at scale. AI handles high-volume investigation work, humans govern the escalations, and observability on the agent itself is a first-class concern. I've built it small-scale for one business. I want to ship it at customer scale — every SOC in the world instead of one back office."**

---

## Part 5: The Unique Edge — What Only Emmanuel Brings

**Dual degree in Cybersecurity and Business Economics.** The economics side is not decoration. Dropzone is a product company with real unit economics. Token cost per investigation, human time saved per alert, margin per seat, churn driven by false-positive rate. Emmanuel reads a P&L and translates it into a detection budget. Most security engineers cannot do that. Most economists cannot debug a Terraform plan. He does both.

**Real investigation-quality experience as a human analyst.** Not from a book, not from a lab, not from a bootcamp. He ran the Wireshark session that found the POS skimmer. He wrote the 6-step IR runbook that shift managers still pick up today. He tuned the Splunk correlation that dropped MTTD from 48 hours to 4. When Dropzone's AI agent produces an investigation report, Emmanuel knows whether it's a good one because he has written the human version of that same report by hand.

**He has red teamed AI agents against OWASP LLM Top 10 professionally.** This is rare in 2026. Most resumes claim "AI security" by listing a prompt injection blog post they read. Emmanuel has eight DAST categories of evidence on his own production gateway, plus a threat model with documented mitigations, plus a zero-egress inference architecture designed specifically for sensitive triage data. He has built the thing Dropzone's adversaries will attack.

**Built a 13-container production stack solo in 7 months.** Startup-ready from day one. No hand-holding, no waiting for platform team, no "we'll tackle observability in Q3." PostgreSQL, n8n, Vault, Keycloak, Teleport, Falco, Datadog, Ollama, Whisper, OpenClaw, Cloudflare Tunnel, all running, all monitored, all governed by IaC with OPA gates. This is a Senior Security Engineer who operates like a founding engineer because he has been one.

**He writes.** 37 GRC documents, roughly 15,000 lines, all sanitized and publishable. Investigation quality is a writing problem as much as a detection problem. An AI SOC analyst that cannot narrate its reasoning clearly is a failed product. Emmanuel ships prose that a CISO can hand to a board.

**Clearance-eligible, US-based, no visa issues.** Dropzone sells to regulated customers. Some engagements require US persons. Emmanuel clears that filter on day zero.

---

## Part 6: Why Now, Why Dropzone

### Why this role for me now?

> **"I finish a dual degree in Cybersecurity and Business Economics in May 2026. I have 4.5 years of hands-on security work behind me, I own a production AI stack I built myself, and I've done the investigation craft with my own hands. I'm ready for product-scale and a team to ship with. I'm already an AI Security Engineer. Dropzone is the next logical home — same job, bigger blast radius, better team, real customers."**

No "pivoting" language. No "finishing my degree" as a lead. The degree is a closing detail, not an apology.

### Why Dropzone over Prophet, Simbian, Crogl, and the rest?

> **"Four reasons. First, Edward Wu's ExtraHop detection-engine lineage — the founder has shipped real detection at scale before, which is rare in this category. Second, the architecture is autonomous investigations, not SOAR playbooks. Playbooks are table stakes; autonomous agents with reasoning transparency is a genuinely harder engineering problem and a higher bar. Third, the investor signal — Theory, Madrona, IQT — isn't chasing hype; those are operators who pick for execution. Fourth, 11x ARR proves the product is actually working in customer environments, not just in demos. And the role mandate — own investigation quality on the AI SOC analyst — is the one part of your product where I can show evidence on both sides of the agent. It's not a stretch. It's a match."**

---

## Part 7: The Red Thread

**Every answer returns to this line:**

> **"I care about investigation quality. I've done it as a human, I've built systems for it, and I want to ship it at scale to every SOC in the world."**

**How to weave it into every answer:**

- **Behavioral / STAR:** End every story with one sentence that ties the work back to investigation quality. Example: "That's why I still care about MTTD numbers — because every hour an attacker is in the environment is an hour the investigation should have started."
- **Technical deep-dive:** Frame every technical choice as a quality decision, not a tech decision. Example: "I chose Falco over auditd because Falco gives me context-rich rules, and context is what makes an investigation credible."
- **AI / LLM questions:** Frame every AI answer through governance and accuracy, not capability. Example: "The model can do the work. The question is whether the investigation holds up under review. That's where the engineering lives."
- **Culture / team questions:** Tie team-building to the same value. Example: "I want to work with engineers who argue about alert quality at 11 p.m. That's the signal that the mission is real."
- **Close of every interview:** Restate the red thread verbatim. Shaleena hears it, Julia hears it, Edward Wu hears it. Same sentence. Three times. They remember it.

---

## Part 8: What Not to Say — Framing Violations

**Banned phrases:**
- "I'm pivoting into AI security." He is already there. Claim the role.
- "Bridging the gap." No gaps to bridge.
- "Transitioning." No.
- "Aspiring." Never.
- "My startup" when referring to CoreDirective. Say **"my employer CoreDirective"** or **"where I work as AI Security Engineer."**
- "I'm finishing my degree" as a lead. The degree closes the pitch, it never opens it.
- "I don't have 6 years but…" Never lead with the gap. Never apologize for experience shape.
- "Tell me if I'm on the right track." Undermines authority. Ask specific technical questions instead.
- "I think I could…" Replace with "I've done…" or "Here's how I'd do that…"
- "Just a…" (as in "just a Texaco gig") — every engagement counts, stated flat.

**Banned writing patterns:**
- Em dashes. None. Period + next sentence, or comma + clause.
- Juxtaposition phrasing: "Not X. Y." Banned.
- "It's not just X, it's Y." Banned.
- Robotic compound descriptions: "seamlessly integrate," "leverage synergies," "holistic approach." Banned.
- Apologies of any kind. None.

**Banned framings:**
- Leading with certifications before identity.
- Leading with school before identity.
- Listing tools before context.
- Ranking Dropzone against other offers ("you're one of three I'm considering"). If asked, say: **"Dropzone is the top of my list. The role is a match on both sides of the agent, and that's rare."**
- Disclosing current comp unprompted.
- Negotiating against oneself.

---

## Final Note — How to Use This Doc

Read it once tonight. Mark the bolded lines. Those are memorize-verbatim. Rehearse the 30-second pitch out loud until it is boring. Rehearse the 2-minute pitch until it fits in 1:50. Fill in the CoreDirective Accounting AI bracketed fields before Shaleena's call. Print the Value Prop Matrix and pin it above the monitor.

Every question she asks, every question Julia asks, every question Edward Wu asks — the answer routes through the red thread. If the answer does not end at investigation quality, the answer is wrong.

Walk in as the AI Security Engineer who is also the investigator. Walk out with the offer.
