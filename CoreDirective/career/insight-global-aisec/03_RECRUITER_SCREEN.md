# 03 — Recruiter Screen Playbook (Savannah Daoust, Monday 2026-05-05)

## Format
- Phone call (recruiter-led, Insight Global standard)
- 20-30 minutes typical for IG screens
- Savannah will likely follow the IG recruiter checklist: introduction, role pitch, qualification confirm, comp, citizenship, availability, next steps

## Goals (in priority order)
1. Identify the end client
2. Lock a real pay range
3. Get clear on remote vs hybrid
4. Position as senior-fit so she submits at top of stack
5. Schedule the next round

---

## 60-second pitch (open with this when she asks "tell me about yourself")

"Sure. I'm Emmanuel Tigoue, AI Security Engineer at CoreDirective in Atlanta. The last four years I ran application security at Texaco, then I shifted into AI security work full time. The work breaks into three buckets. One: AI red teaming and threat modeling, including prompt injection testing and STRIDE plus MITRE ATLAS models on production LLM workloads. Two: AI governance authoring, 37 GRC documents covering AI policy, AI IR, threat modeling, all sanitized and public. Three: SOAR automation with LLMs in the loop, which cut my triage volume by over 80 percent. Certs are SecurityX, SSCP, CCNA, Security Plus, with CISSP this August. The role you sent reads like it was written for the kind of work I do every day."

## 30-second variant (use if she's brief)

"Emmanuel Tigoue, AI Security Engineer at CoreDirective. Four years AppSec at Texaco, the last two focused on AI security. I run an open-source AI security stack in production, I author governance docs, and I built an LLM-driven SOAR that cut my triage by over 80 percent. CISSP in August, SecurityX and SSCP already on the wall."

---

## 18 likely questions with model answers

### Round 1: Qualification gates

**Q1. Are you a US Citizen or Green Card holder?**
"Yes, US Citizen."

**Q2. Are you actively interviewing? Where else are you in process?**
"I am, yes. Active with Cloudflare via Brilliant for a contract eng role, with Amex for a senior AppSec contract, and with Dropzone AI for a senior eng FTE. I'm being selective — the role you sent fits my AI sec lane more cleanly than two of those."

**Q3. When could you start?**
"Two weeks notice from offer. Faster on a contract."

**Q4. Are you fully remote-ready, or is this a relocation conversation?**
"Fully remote-ready. Atlanta, GA, dedicated home office, fiber, full kit."

### Round 2: Skills probes

**Q5. Walk me through your AI security experience.**
[Use the 60-sec pitch. Then anchor on the three buckets: red team, governance, SOAR. Volunteer the metric: 80%+ triage reduction.]

**Q6. Have you worked with Microsoft Security Copilot?**
"Honest answer is no, not in production. I've run the equivalent workflow through n8n calling the Anthropic API directly — natural language to KQL-style query to triage action. Same pattern, different vendor. Ramp on the Copilot UI is days. Ramp on the concepts is zero. I'd close that gap in week one."

**Q7. What about Defender for Cloud?**
"Same answer. I run posture management today through Falco at runtime and OPA at admission, threat protection through Falco plus Sidekick into Datadog. The new AI-SPM features in Defender are concepts I've already implemented; the vendor mapping is what I'd learn."

**Q8. What AI governance frameworks have you worked with?**
"NIST AI RMF — mapped it against my own threat model. ISO 42001 — read-level, tracked Microsoft's certification announcement last month. EU AI Act — tracking the August 2026 high-risk Annex III deadline. And I've authored 37 GRC documents covering AI policy, AI threat modeling, AI IR — all public-facing."

**Q9. Have you done red teaming or pen testing?**
"Application security testing — yes, four years of it at Texaco. AI red teaming — yes, prompt injection and jailbreak work against my own Anthropic and Ollama endpoints. I do not have OSCP. I have SecurityX, SSCP, and CISSP in August, which the JD calls out as acceptable."

**Q10. Tell me about your SOAR work.**
"I run n8n on a DigitalOcean droplet with 14 services in production. Master orchestrator routes 16 different action types — Postgres, Telegram, GitHub, Drive, Gmail, Notion, you name it. The triage layer uses Anthropic Claude through a gateway I built called OpenClaw. Result was 80 percent or more reduction in human triage volume. That's the kind of "embed intelligent automation into every layer" the JD asks for."

### Round 3: Comp + logistics

**Q11. What's your target rate?**
"For a 1-year W2 contract on AI sec engineering work, I'm targeting $95 an hour. Floor is $80, ceiling is $115 depending on the end client and the benefits package. Where does the role sit?"
[Listen. Do not adjust until she gives you a number.]

**Q12. (If she lowballs) The client's range tops out at $XX, can you do that?**
"Tell me more about the client and the work first. If the role lines up tightly with what I do every day — AI governance, SOAR with LLMs, AI red team — then I'd want $90 plus to be the conversation. If the scope leans heavy on the Microsoft stack hands-on, that's a reasonable concession because I'm ramping there."

**Q13. Is this a contract-to-hire or pure contract?**
"That's actually one of my questions back to you. The JD says possible extension or perm — what's the conversion pattern at this client?"

**Q14. Are you considering perm roles too?**
"Yes. Perm baseline target is $180-200K all-in for AI sec engineering. I won't take a contract that locks me out of perm conversations elsewhere — happy to sign a non-exclusive engagement with Insight Global."

### Round 4: Wrap

**Q15. Why are you interested in this role?**
"Two things. One, the JD is the cleanest match for what I actually do day to day — AI red team, AI governance, SOAR — and I see those three together less often than I'd like. Two, the August 2026 AI Act deadline tells me the client is taking AI governance seriously and has budget. I want to work where the work is real, not aspirational."

**Q16. What questions do you have for me?**
[Pull from `04_QUESTIONS_FOR_THEM.md`. Tier 1 mandatory: end client, comp range, contract structure, why contract.]

**Q17. Anything else I should know?**
"Two things worth flagging. First, my CISSP is sitting in August and I'd want the client to know that's locked in. Second, I'm balancing four active processes right now, so if the client moves fast I can move fast, but if they take a month I'll have other offers in flight."

**Q18. What's the best way to reach you?**
"Cell at 404-839-2214, or email at etigoue@tigouetheory.com. Either works."

---

## Closing sequence (last 60 seconds)

"Savannah, this sounds like a fit. I appreciate the time. Three things from me before we hang up:

One, can you send me whatever you have on the end client and the team — anything you can share, even just industry — so I can prep correctly for the next round?

Two, what's your timeline? When are you submitting to the client, and when would you expect to hear back?

Three, what's the strongest thing I can do this week to move from screen to client interview? Send a tailored resume? Anything else you want from me?

Thanks for catching the resume in the first place — happy to keep this moving."

---

## Compensation playbook

| Tier | W2 hourly | Annual gross | Use when |
|---|---|---|---|
| Aspiration | $115 | $239K | Client is large F500 or fed contractor with deep budget |
| Target | $95 | $198K | Standard mid-market or large enterprise contract |
| Floor | $80 | $166K | Small client, training-heavy, weak benefits |
| Walk-away | $75 | $156K | Below this, the role does not beat current pipeline alternatives |

**Annual gross math:** hourly × 2080 hours

**Net annual GA estimate at $95/hr:**
- Gross: ~$198K
- Federal + GA state: ~28% effective
- Net annual: ~$143K
- Net biweekly: ~$5,500

**Insight Global margin negotiation:**
- IG bill rate to client = candidate rate ÷ (1 - IG margin)
- Typical IG margin: 25-35%
- At $95/hr to candidate, IG bills client ~$130-145/hr
- Use this to anchor: "If your bill rate is $135 and you're at a 30% margin, my $95 is your floor, not your ceiling"

---

## Post-call email template (send within 4 hours)

Subject: Quick follow-up — AI Security Engineer call

Hi Savannah,

Thanks for the call today. Quick recap of what I committed to:

1. Resume — attached. Tailored to the AI Security Engineer scope you described.
2. Availability — flexible weekday afternoons EST for the next round.
3. Citizenship — confirmed US Citizen.

A few items I'm tracking on my side:
- End client name, industry, team size
- Confirmed pay range and bill rate
- Contract conversion pattern
- Onsite expectation if any

Happy to jump on another call when you have feedback from the client. I'm pacing this against three other active processes, so the faster the next step, the better for both of us.

Thanks again,
Emmanuel
404-839-2214
etigoue@tigouetheory.com

---

## Day-of logistics

**45 min before:**
- Re-read `01_COMPANY_INTEL.md` § 1-3
- Pitch out loud once, voice memo
- Index card visible

**15 min before:**
- Water on desk
- Headset tested
- Phone DND
- Notepad + pen
- JetBrains Mono terminal closed
- Browser tabs: this folder + LinkedIn (Savannah's profile)

**On answer:**
- "Hi Savannah, Emmanuel here. How are you?"
- Short pause
- Let her run the agenda

**Voice:**
- Energy 7/10
- Pause after each answer
- No filler ("um", "you know", "right")
- If she asks something you don't know: "Honest answer is no" — never bluff
