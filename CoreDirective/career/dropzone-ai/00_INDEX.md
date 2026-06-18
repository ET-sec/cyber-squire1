# Dropzone AI Interview: Study Plan & Index

**Status as of 2026-04-28:**
- **Stage 1. Recruiter screen DONE** 2026-04-17 with Shaleena Reyersbach (Sr Talent Acquisition Partner). PASSED.
- **Stage 2. Take-home coding DONE** submitted 2026-04-21 6:09 PM. Passed. Moved forward 2026-04-28.
- **Stage 3. Hiring Manager Technical Interview** Thu **2026-05-07, 12:45 to 1:30 PM EDT**. Google Meet (`meet.google.com/bbs-zevf-fmh`). 1:1 with **Eric Hammerle, Director of Engineering**. 45 minutes.
- **Stage 4 (likely)** Panel + founder/exec round. TBD.

**Role:** Senior Security Engineer (Remote US, $175-217k + above-market equity)
**Candidate:** Emmanuel Tigoue, AI Security Engineer at CoreDirective

---

## The Non-Negotiables (Memorize Cold)

### Red Thread (every round, every answer routes here)
> **"I care about investigation quality. I've done it as a human, I've built systems for it, and I want to ship it at scale to every SOC in the world."**

### Identity (never hedge)
"I'm Emmanuel Tigoue, AI Security Engineer at CoreDirective."

### The Three Metrics Carried Into Every Story
- Falco eBPF alerts **200 per day to 12 actionable**
- Splunk MTTD **48 hours to under 4 hours**
- IR runbook **8 hours to 90 minutes containment**

### The Role Decoded
"Own investigation quality" means *read what the AI SOC Analyst produces and call BS when it's wrong*. That is exactly what Emmanuel does when he red teams OpenClaw against OWASP LLM Top 10 and MITRE ATLAS.

---

## Document Map

| # | File | When to read | Core use |
|---|---|---|---|
| 00 | `00_JOB_DESCRIPTION.md` | First thing every session | Locked JD. Eric Hammerle confirmed as hiring manager. |
| 01 | `01_COMPANY_INTEL.md` | Apr 29 (foundation) | Edward Wu / ExtraHop / NDR lineage, $37M Series B, 11x ARR, OSCAR methodology, competitive field, customer voice |
| 02 | `02_ROLE_FIT.md` | Apr 29 + May 4 | JD-aligned evidence map for the technical round. Investigation quality deep dive. |
| 03 | `03_TECHNICAL_PREP.md` | May 1 (technical drill) | 30 Q&A, 10 scenario walkthroughs, vocabulary sheet, 10 AI failure modes |
| 04 | `04_STAR_STORIES.md` | Apr 29 + May 4 | 12 behavioral stories. Leads: POS skimmer, OpenClaw red team, Falco tuning, n8n SOAR |
| 05 | `05_RECRUITER_SCREEN.md` | Reference only (Stage 1 done) | Archived. Pull only if Eric circles back to comp framing. |
| 06 | `06_QUESTIONS_FOR_THEM.md` | May 4 + May 7 morning | Stage 3 Eric-tailored questions at top. 12 ranked. |
| 07 | `07_MASTER_FRAMING.md` | Apr 29 + May 6 | Stage 3 framing at top: 30s, 60s, 2min for technical Director audience. |
| 08 | `08_HIRING_SIGNALS_AND_TRUST.md` | Apr 29 + May 7 morning | Director-tier signals at top. 60-sec centering ritual for May 7. |
| 09 | `09_ERIC_HAMMERLE_INTEL.md` | Apr 29 + May 6 | Eric's background, public footprint, technical signals to mirror, 5 minutes-of-Eric soundbites |
| 10 | `10_TECHNICAL_ROUND_GAMEPLAN.md` | May 1 + May 4 | Minute-by-minute 45-min gameplan, opener, story sequencing, fallback paths |
| 11 | `11_TAKE_HOME_DEFENSE.md` | May 1 (heavy) | Walk-through of LangChain + boto3 + Moto submission, design choices, what to volunteer, what to defend |
| 12 | `12_BEHAVIORAL_BANK.md` | May 4 (full mock) | 8 director-tier behavioral prompts with PSC answers, on-call temperament, mentorship, ambiguity |
| 13 | `13_MAY7_MORNING_BRIEF.md` | **May 7 — only file open during prep** | Day-of consolidated cheat sheet. Fresh intel since 4/28, code gotchas, drill questions, schedule, centering line. |

---

## Multi-Day Study Plan (Apr 28 to May 7)

### Wednesday Apr 29: Foundation (2.5 hours)

**Block 1 (45 min). Eric Hammerle intel**
- Read `09_ERIC_HAMMERLE_INTEL.md` end to end
- Capture 5 "minutes-of-Eric" soundbites Emmanuel can mirror without sounding rehearsed
- Note one hook from his public footprint to reference once if natural

**Block 2 (45 min). Refresh framing for Director audience**
- Read `07_MASTER_FRAMING.md` Stage 3 section at top
- Memorize the 60-second technical Director pitch verbatim
- Cut anything that sounds recruiter-tuned (no "looking forward to learn", no comp framing)

**Block 3 (45 min). Refresh role fit through Eric's lens**
- Read `02_ROLE_FIT.md` Stage 3 evidence map
- Pick the 3 strongest evidence rows. Internalize the 30-second answer for each.
- Read the "Investigation quality deep dive" section

**Wind-down:**
- Read the Stage 3 hard mode list at the bottom of this index. Sleep on it.

### Friday May 1: Technical Drill (3 hours)

**Block 1 (60 min). Take-home defense**
- Read `11_TAKE_HOME_DEFENSE.md`
- Open the actual submitted code. Walk through it line by line out loud.
- Anticipated probes: why LangChain, why Moto over real AWS, retry strategy, prompt design, eval approach
- Have the repo open in second monitor for May 7

**Block 2 (60 min). Investigation flows + agent architecture**
- Read `03_TECHNICAL_PREP.md` sections on agent loops, retry logic, tool abstractions
- Read `10_TECHNICAL_ROUND_GAMEPLAN.md` minute-by-minute plan
- Practice 90-second walkthrough of OpenClaw skill execution flow

**Block 3 (60 min). Whiteboard scenarios**
- Pick 3 scenarios from `03_TECHNICAL_PREP.md`: phishing investigation logic, lateral movement detection across cloud + on-prem, regression-test strategy for an agent
- Talk through each one out loud at 5 minutes apiece. Record. Listen for filler.

### Monday May 4: Full Mock (2.5 hours)

**Block 1 (45 min). Behavioral bank**
- Read `12_BEHAVIORAL_BANK.md`
- For each of the 8 prompts, deliver the PSC answer aloud at 60-90 seconds
- Flag the 2 weakest. Re-drill.

**Block 2 (60 min). Full 45-minute mock**
- Set a timer. Use `10_TECHNICAL_ROUND_GAMEPLAN.md` as the script.
- Open with the 60-second pitch. Take 2 technical questions. 1 design question. 1 behavioral. End with questions for Eric.
- Record the whole thing on Voice Memos. Listen back. Mark the 3 worst moments. Fix tomorrow.

**Block 3 (45 min). Questions for Eric**
- Read `06_QUESTIONS_FOR_THEM.md` Stage 3 section
- Pick the 4 questions that fit Emmanuel's voice. Write them on the index card.
- Practice the closing question: "Is there anything from this conversation that leaves you uncertain about me for the role?"

### Wednesday May 6: Light Review (60 min)

- Read `09_ERIC_HAMMERLE_INTEL.md` once more
- Read `07_MASTER_FRAMING.md` Stage 3 section once more
- Run the 60-second pitch 3 times standing up
- Run the closing question once
- Lay out clothes. Test camera, mic, lighting. Check `meet.google.com/bbs-zevf-fmh` link works.
- In bed by 11 PM EDT.

### Thursday May 7: Game Day

**Morning (8:00 to 9:00 AM EDT). Prime, do not cram**
- Coffee. Real food.
- Read the index card aloud once.
- Run the 60-second pitch once standing up.
- Read the Stage 3 hard mode list at the bottom of this file.
- Close all docs. Walk for 20 minutes. No phone.

**11:00 AM EDT. Last-mile prep**
- Re-read `09_ERIC_HAMMERLE_INTEL.md` 5 minutes-of-Eric soundbites
- Re-read `11_TAKE_HOME_DEFENSE.md` design-choice section
- Confirm Google Meet, camera, headset, lighting

**12:15 PM EDT. 30-min pre-call**
- `08_HIRING_SIGNALS_AND_TRUST.md` Section "60-second centering ritual for May 7"
- Stand. Breathe. Power pose.
- Read out loud: "I am an AI Security Engineer. Investigation quality is my problem and I solve it in production."
- Water on desk. Notepad open. Index card visible.
- Phone on do-not-disturb. Slack closed. Browser tabs closed except Meet.

**12:43 PM EDT. Dial in**
- Enter the meeting 2 minutes early.
- Camera on. Smile once before the connect ping.
- First words: "Hey Eric, good to meet you. Thanks for the time."
- Let him lead. PSC every answer.

**After the call:**
- Send a clean thank-you within 2 hours. Reference one specific thing he said. No marketing language.

---

## Index Card (Write This Down for May 7)

```
RED THREAD: Investigation quality, human + systems + scale

IDENTITY: AI Security Engineer at CoreDirective

STAGE 3 SOUNDBITES (Eric mirror):
  1. "I read AI output the way a senior analyst reads a junior's report."
  2. "Grounding is the engineering problem. Hallucination is the symptom."
  3. "Every detection ships with a regression test against 30 days of prod traffic."
  4. "I optimize for analyst trust first, coverage second."
  5. "Production Python earns its place. Notebooks don't."

TOP 3 ARCHITECTURAL SOUNDBITES:
  1. OpenClaw red team: OWASP LLM Top 10 + MITRE ATLAS, 8 DAST categories, zero injection
  2. n8n MASTER_ORCHESTRATOR_V1: 16 services, webhook fan-out, sub-workflow architecture
  3. Zero-egress inference for sensitive triage: Ollama + NeMo, Vault-backed secrets, mTLS

TOP 3 STAR STORIES FOR MAY 7:
  1. POS skimmer (investigation discipline, hypothesis pivot, 90-min containment)
  2. OpenClaw red team (eval harness, prompt injection through tool use, guardrail change)
  3. Take-home walkthrough (LangChain + boto3 + Moto, design tradeoffs)

4 QUESTIONS FOR ERIC:
  1. How do you measure investigation quality on the agent today?
  2. What does the rollout pattern look like, canary, feature flag, shadow mode?
  3. Where does the agent hallucinate most, and how do you catch it before customer?
  4. (Closer) Anything from this conversation that leaves you uncertain about me?

DO NOT SAY:
  "Pivoting" / "transitioning" / "aspiring" / "founder" / "my startup"
  "I'm passionate" / "rockstar" / "fast learner"
  "I don't have 6 years", never volunteer the gap
  Don't lead with certs or graduation
```

---

## Stage 3 Hard Mode List: 10 Things Emmanuel Must NAIL on May 7

These are the failure modes that kill technical-round candidates with senior engineering directors. Each one has a green-light bar.

1. **Defend the take-home like an owner.** Walk through the code without notes. Volunteer the 2 design tradeoffs you'd revisit. Don't apologize for choices, explain them. Green light: Eric says "good thinking" or asks a follow-up that goes deeper.

2. **Talk Python in production terms, not script terms.** Type hints, retries, idempotency, observability hooks, error budgets. Green light: the conversation moves from "I wrote Python that..." to "we'd structure that as..."

3. **Show investigation discipline through one war story, told right.** POS skimmer: hypothesis, evidence, pivot, conclusion, what you learned. 90 seconds. Green light: Eric asks a clarifying question about the pivot.

4. **Demonstrate an eval mindset.** When asked about agent quality, name three axes: grounding, completeness, explainability. Reference your OpenClaw eval suite. Green light: Eric leans into the eval question instead of changing topic.

5. **Handle the "we want 6+ years" probe by density, never apology.** "Four and a half years heavy production. Owned the full stack at Texaco for 4 years. Seven months on an LLM gateway in production with red-teaming and detection engineering daily." Green light: he moves on without re-asking.

6. **Show on-call temperament.** Don't volunteer how much on-call sucks. Frame it as "the runbook is what makes 3 AM survivable" and reference cutting Texaco IR from 8 hours to 90 minutes. Green light: Eric nods and asks about runbook authoring.

7. **Talk about a colleague's work positively.** Senior engineering directors filter for people who make others better. Have one story of pairing or mentorship ready (the canary disagreement story works, colleague proposed shipping without canary, you brought historical data, compromise landed and caught two edge cases). Green light: he asks how you give feedback.

8. **Trade-offs unprompted.** Every technical answer ends with one accepted cost. "I chose X. The cost was Y. I planned to close that gap by Z." Green light: he says "yeah, that tracks."

9. **Ask one question that proves you've thought about Dropzone the product, not just the role.** Top pick: "How do you decide which alert classes the agent invests in next, customer pull or strategic bet?" Green light: he gives you a real answer with internal reasoning.

10. **Close strong with the uncertainty question.** "Eric, is there anything from this conversation that leaves you uncertain about me for this role? I'd rather address it now than leave it unsaid." Green light: he names a real concern (and you handle it cleanly) OR he says "no concerns, I'd advance you."

---

## Trust-Building Discipline (Every Answer)

**PSC: Problem. Specifics. Consequence.**

- **P**roblem: one sentence about the situation
- **S**pecifics: exact tools, decisions, tradeoffs, numbers, the bulk
- **C**onsequence: the metric + the lesson you named from it

Every answer. Every time. 45 to 90 seconds.

---

## Things to Never Say (Stage 3)

- "Pivoting" / "transitioning" / "aspiring" / "bridging"
- "I'm still learning" / "sorry, this is new to me"
- "My startup", say "my employer CoreDirective"
- Lead with May 2026 graduation, you are an AI Security Engineer first
- "I'm passionate" / "rockstar" / "ninja" / "fast learner"
- Em dashes anywhere, written or spoken cadence
- "I don't have 6 years", never volunteer the gap
- "I think I could", replace with "I've done" or "Here's how I'd structure that"
- Founder language about CoreDirective. Emmanuel works at CoreDirective, full stop

---

## Two Hours After the Call

Send this thank-you. Plain text. No em dashes. Reference one specific thing Eric said.

```
Subject: Thanks for the time today

Eric,

Appreciate the conversation today. The piece on [SPECIFIC THING ERIC SAID, e.g.
"how you're rolling out the new alert class behind shadow mode for two weeks
before any customer sees it"] is exactly the kind of discipline I want to ship
under. It's also why I'm clear on the role.

If a follow-up technical or panel round helps, I'm ready. And I'm happy to share
the OpenClaw eval write-up I mentioned, or walk through the take-home in more
depth, whichever is useful.

Best,
Emmanuel Tigoue
AI Security Engineer, CoreDirective
linkedin.com/in/emmanuel-tigoue
```
