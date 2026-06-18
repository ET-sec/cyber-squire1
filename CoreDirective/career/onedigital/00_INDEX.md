# OneDigital AI Security Engineer — Interview Prep Index

**Interview:** Thursday 2026-04-23, 1:00 PM EDT, 30 minutes, Microsoft Teams
**Interviewer:** Pavel Kotelnikov, Sr. Manager Information Security at OneDigital, CISA
**Format:** Technical + behavioral mixed, hiring manager screen (not recruiter)

**Teams meeting:**
- [Join link](https://teams.microsoft.com/meet/27829678530426?p=U9EAXRGc39kUvB205y)
- Meeting ID: 278 296 785 304 26
- Passcode: zp95vw6y
- Dial-in backup: +1 872-240-8925 conference ID 391 817 090#

**Scheduled by:** Tommy Hauser (tommy.hauser@onedigital.com) — OneDigital internal coordinator
**Also CC'd:** Alex — role TBD, could be another team member or candidate coordinator

---

## The Non-Negotiables (memorize cold)

### Red Thread
**"AI security is governance plus operations. Do one without the other and you fail an audit or you fail an incident. I do both."**

### Identity (never hedge)
"Emmanuel Tigoue. AI Security Engineer at CoreDirective."

### Three Metrics (carry everywhere)
- **Falco eBPF** alerts tuned from **200/day → 12 actionable**
- **Splunk MTTD** cut from **48 hours → under 4 hours** (Texaco)
- **IR runbook** containment time from **8 hours → 90 minutes** (Texaco)
- Plus: **37 GRC documents** authored, including NIST 800-53 SSP + AI Governance policy + AI Incident playbook

### Pavel Profile
- CISA — ISACA audit/governance cert, not a pentester
- Kennesaw State alum — Atlanta local
- Interview style: control frameworks, documentation, evidence, vendor risk, policy alignment
- Will NOT grill on exploit dev, CTF, Burp macros

### OneDigital at a Glance (from verified research)
- 5,000+ employees, 250+ offices
- Founded 2000 in Atlanta by CEO Adam Bruckman
- HQ: 300 Galleria Parkway Suite 1100, Atlanta GA 30339 (Cumberland/Galleria)
- **NEW OWNERSHIP Dec 2025:** Stone Point Capital + CPP Investments majority, $7B+ transaction. Onex minority.
- **Active third-party breach:** Salesloft/Drift OAuth supply-chain compromise, 28,414 OneDigital clients affected, notifications sent April 8, 2026 (13 days ago)
- Top 20 US insurance broker since 2017
- 200+ acquisitions historically (roll-up model)
- Glassdoor: 3.1/5 (declined 6% in 12 months), 58.4% positive interview experience

---

## Document Map

| # | File | When to Read | Core Use |
|---|------|--------------|----------|
| 01 | `01_COMPANY_INTEL.md` | Wed evening first | OneDigital cold — verified company intel, new ownership, Salesloft breach timeline, culture metrics, Pavel profile, sources. Every fact is linked. |
| 02 | `02_ROLE_FIT.md` | Wed evening | JD line-by-line mapped to your evidence. Gap reframes. The one-paragraph mirror. Honest handling of tool gaps. |
| 03 | `03_TECHNICAL_PREP.md` | Thu morning | Full acronym glossary (LLM, OWASP LLM, MITRE ATLAS, SAST/DAST/SCA, Entra, PRMFA, SOC 2, CIS 18, etc.). Tool deep dives. 8 likely technical Q&A with answer frames. 3 scenario questions. NIST CSF 2.0 + 800-53 + ISO 42001. |
| 04 | `04_STAR_STORIES.md` | Wed evening heavy | 10 behavioral stories in STAR+PSC format. Pavel-adapted — lead with GRC + documentation discipline. Story-to-question mapping table. |
| 05 | `05_HM_SCREEN.md` | Wed evening + Thu AM | 20 likely Pavel questions with model answers. Opening pitch verbatim. Close sequence. Post-interview email template. |
| 06 | `06_QUESTIONS_FOR_THEM.md` | Wed evening | 12 questions for Pavel in 3 tiers. Pick 3-4. Never-ask list. Close-with questions. |
| 07 | `07_MASTER_FRAMING.md` | Wed evening first | Core paragraph, 3 pitches (30s / 60s / 2min), JD mirror language, 6 gap reframe templates (Snyk/Salt/AIDR/Qualys/Entra/CIS 18). |
| 08 | `08_HIRING_SIGNALS_AND_TRUST.md` | Wed evening + Thu AM | Pavel's decision framework weighted. 10 positive + 10 negative signals. 25 trust-building phrases. Trust killers. Compensation playbook. Centering ritual. Index card. |
| 09 | `09_CLAUDE_PRACTICE.md` | Thu morning | 12 Claude practice prompts to drill the pitch, threat modeling, gap reframes, Salesloft probe, tabletop, CIS 18 mapping, behavioral curveballs, voice delivery, sanity check. |

---

## Wednesday Evening Study Plan (2.5 hours)

**Block 1 — Frame first (45 min)**
- Read `07_MASTER_FRAMING.md` end to end
- Read `01_COMPANY_INTEL.md` sections 1-5 (company, ownership, M&A, leadership, Salesloft breach)
- Write the 30-second pitch on an index card in your own words

**Block 2 — Drill the pitch (30 min)**
- Memorize the 60-second pitch from `05_HM_SCREEN.md`
- Voice Memo recording x3. Listen, fix pacing + fillers
- Target: deliver without reading, energy at 7/10, natural

**Block 3 — Anchor the top 5 stories (45 min)**
- Read `04_STAR_STORIES.md` stories 1-5 (GRC library, OpenClaw red team, Falco tuning, POS skimmer IR, n8n SOAR)
- PSC-compress each to 60-75 seconds aloud
- Record story 1 (GRC library) on Voice Memo — your anchor Pavel story

**Block 4 — Pavel-specific prep (30 min)**
- Read `05_HM_SCREEN.md` end to end
- Read `06_QUESTIONS_FOR_THEM.md` — pick 3 questions for Pavel, write on index card in own words
- Read `08_HIRING_SIGNALS_AND_TRUST.md` — memorize the 25 trust phrases, internalize the trust killers

**Before sleep**
- Index card out loud one time
- Phone on silent, clothes laid out, water by bed, Teams app tested on laptop

---

## Thursday Morning Plan (90 min)

**3 hours before (10:00 ET) — Breakfast + wide read**
- Eat real food, low carb
- Read `05_HM_SCREEN.md` all 20 questions — say each model answer aloud once
- Flag 3 hardest, re-drill

**90 min before (11:30 ET) — Technical vocabulary**
- Read `03_TECHNICAL_PREP.md` Part 1 (acronym glossary) end to end
- Scan Part 2 (tool deep dives) — can you describe Snyk, Salt, AIDR, Qualys, Entra PRMFA in one sentence each

**60 min before (12:00 ET) — Claude drill**
- Open `09_CLAUDE_PRACTICE.md`
- Run Prompt 11 (voice delivery on the pitch) — 10 min
- Run Prompt 7 (uncomfortable silence) — 10 min
- Run Prompt 12 (sanity check) — 5 min

**30 min before (12:30 ET) — Focus**
- Review index card
- No more new content — you're ready

**15 min before (12:45 ET) — Centering**
- `08_HIRING_SIGNALS_AND_TRUST.md` 60-second centering ritual
- Water. Clean shirt. Camera tested. Teams meeting joined. Notepad + pen visible. Phone DND.

**At 12:58 ET — Dial in**
- Enter Teams meeting 2 minutes early
- Smile before you speak (changes voice even audio-only)
- Let Pavel lead. Answer in PSC format. 45-90 seconds per answer unless he invites deeper.

---

## Index Card (write down, keep visible during call)

```
RED THREAD: AI security is governance + operations.
           Do one without the other and you fail audit or incident.

IDENTITY: AI Security Engineer at CoreDirective.

TOP METRICS:
  Falco eBPF 200/day -> 12 actionable
  Splunk MTTD 48h -> <4h
  IR runbook 8h -> 90min containment
  37 GRC documents (NIST 800-53 SSP + AI Governance)

ANCHOR STORIES:
  1. 37 GRC docs authored (Pavel's favorite — lead here if choice)
  2. OpenClaw red team vs OWASP LLM Top 10 + MITRE ATLAS
  3. Falco tuning 200 -> 12
  4. POS skimmer IR with documented runbook
  5. n8n SOAR 80% triage reduction

3 QUESTIONS FOR PAVEL:
  1. Maturity gap in AI governance program?
  2. Build vs run weighting day-to-day?
  3. Audit cadence + target frameworks?

GAP REFRAMES (days to ramp):
  Snyk -> Semgrep+Trivy+Gitleaks
  Salt -> Cloudflare+Terraform IaC
  AIDR -> Falco+Datadog
  Entra (week) -> Keycloak+Teleport+Cloudflare Zero Trust

COMP: $125K anchor. Not going first. Floor $120K.

CLOSE: "Based on what we've talked through, is there anything
       that leaves you uncertain about me for this role?"

IF SALESLOFT COMES UP: industry playbook, OAuth scope governance,
       not claiming to have prevented what no one prevented.
```

---

## Never Say

- "Pivoting" / "transitioning" / "aspiring" / "bridging"
- "My startup" — say "my employer CoreDirective"
- "Passionate" / "rockstar" / "ninja" / "fast learner"
- Lead with May 2026 graduation — you are an AI Security Engineer first
- Specific "28,414" figure unless Pavel says it first
- "Salesloft" or "Drift" unprompted
- "Onex owns OneDigital" — outdated (Stone Point + CPP since Dec 2025)
- Em dashes in any written follow-up

---

## The Standard

Every answer: 45-90 seconds. PSC format. Specific numbers. Named tools. One lesson.

Every story: real. Verifiable. The metric at the end.

Every question for Pavel: couldn't have been Googled. Invites his real priority.

Every gap: honest + reframe + ramp time + foundational skill.

Every trust phrase woven in naturally, not stuffed.

**You don't need to be perfect. You need to be present, specific, and the same person on the call that you are in your work.**
