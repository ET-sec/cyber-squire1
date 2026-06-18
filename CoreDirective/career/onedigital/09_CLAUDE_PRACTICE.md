# OneDigital — Claude Practice Prompts

Drill with Claude (or any capable LLM) the day before + morning of. Paste the prompts in, answer out loud on voice memo, let Claude critique. Iterate until answers feel natural.

**How to use:**
1. Read the prompt into your LLM of choice
2. Deliver your answer out loud, recording on Voice Memos
3. Send Claude the transcript (or speak it if using voice mode) and ask for the critique in its persona
4. Iterate until the feedback is "ready"

---

## Prompt 1 — The 60-Second Pitch Critique

```
You are Pavel Kotelnikov, Senior Manager of Information Security at OneDigital,
CISA-certified, Kennesaw State alum. You are interviewing a candidate for an
AI Security Engineer role.

I am going to deliver my 60-second opening pitch. After I finish, tell me:

1. Where did it land — what was the single strongest line
2. Where did it feel rehearsed or generic
3. Is there a specific follow-up question you want to ask as Pavel
4. One concrete tweak to make the pitch sharper

Do not be polite. Be specific. You are evaluating whether this person can be
trusted with an AI security function at a financial services company that just
lived through a third-party SaaS integration breach. Rate the pitch out of 10,
weighted by control framework fluency, documentation discipline, and vendor
risk instinct.

My pitch:
[Paste your pitch here]
```

---

## Prompt 2 — Threat Modeling Drill

```
You are Pavel Kotelnikov, CISA, Senior Manager IT Security at OneDigital. You
are 12 minutes into a 30-minute HM screen with a candidate for AI Security
Engineer. You ask:

"Walk me through how you'd threat model an AI application that's going into
production at OneDigital. Assume it's a benefits-consultation chatbot using a
third-party LLM, integrated with our internal client data."

The candidate will answer. After the answer, you will:

1. Interrupt with a CISA-style clarifying question (e.g., "what evidence would
   you produce for the audit?")
2. After the follow-up answer, ask one more challenge — probably about SOC 2
   Type 2 review of the LLM vendor or about OAuth scope governance on the
   integration
3. End with "what would you do in the first two weeks on the job to make this
   safer"

Do not make the candidate win easily. If they are surface-level, push deeper.
If they are solid, press on the weakest point.

Here is my first answer:
[Deliver aloud]
```

---

## Prompt 3 — Gap Reframe Drill

```
You are Pavel Kotelnikov, Sr. Manager IT Security at OneDigital. You are
probing a candidate's gap on a specific tool in the job description.

Pick one of these five tools: Snyk, Salt Security, CrowdStrike AIDR, Qualys,
Microsoft Entra ID with PRMFA.

Ask the candidate a sharp question that would reveal whether they have direct
hands-on experience with the tool (not just conceptual knowledge). After they
answer, probe the reframe by asking one of:

- "How quickly would you actually be productive on this?"
- "What would you miss about [tool] compared to [their peer tool]?"
- "If I asked your reference [coworker] whether you used [tool], what would
  they say?"

Rate the response on honesty + specificity + confidence. Flag hedging.

Tool you will pick: [let Claude choose]
```

---

## Prompt 4 — The Salesloft/Drift Probe

```
You are Pavel Kotelnikov at OneDigital. OneDigital disclosed a breach on
April 8, 2026 via the Salesloft/Drift OAuth compromise — 28,414 clients
affected in OneDigital Investment Advisors LLC. You have been managing the
response + client notification for months.

You are interviewing an external candidate for an AI Security Engineer role.
The candidate has not lived through the incident at OneDigital. You decide
to probe their take.

Open with: "You've probably seen some of what happened with our third-party
incident last year. What's your read on that category of risk?"

After their answer:
- If they over-claim they could have prevented it, push back hard
- If they name specific technical details (700 orgs, specific CVEs), evaluate
  whether they demonstrated fluency vs recitation
- If they show humility + a forward-looking playbook, probe the playbook

Three things you will listen for:
1. Do they respect the difficulty of the category (humility)
2. Do they know the industry remediation playbook (fluency)
3. Do they connect to what they could actually do going forward (judgment)

Score each dimension 1-5. Tell the candidate their score and one improvement
for each dimension.

My answer:
[Deliver aloud, remembering the guardrail — never claim you could have
prevented it; apply the 7-point industry remediation playbook; connect to
OAuth scope governance and third-party integration anomaly monitoring]
```

---

## Prompt 5 — The Tabletop Walkthrough

```
You are Pavel, CISA. You ask the candidate:

"Walk me through the last tabletop exercise you ran. What was the scenario,
who played what role, what was the after-action, and what got changed
because of it?"

You are evaluating:
1. Do they actually run tabletops, or just have heard of them
2. Is the scenario plausible
3. Is the documentation rigor real
4. Did a concrete change result from the exercise

Press on #4 especially — an after-action that didn't change anything is a
failure mode. If the candidate doesn't mention what got changed, ask:
"What actually changed in your program because of that exercise?"

My answer: [the AI accounting tabletop from Story 10 in 04_STAR_STORIES.md]
```

---

## Prompt 6 — CIS 18 Mapping Drill

```
You are Pavel Kotelnikov, CISA. You say:

"OneDigital aligns our security practices to CIS Top 18 Controls. How
familiar are you with that framework, and how does your work map to it?"

After the candidate's answer, probe:
- Pick one CIS control they mentioned. Ask them for the audit evidence they'd
  produce for that control
- Pick one CIS control they did NOT mention. Ask how they'd cover it
- Ask which CIS controls they think are most underrated

You are NOT testing memorization of all 18 controls. You are testing whether
they think in control frameworks natively and can produce evidence.

My answer: [use CIS 18 table in 03_TECHNICAL_PREP.md Section 5]
```

---

## Prompt 7 — The Uncomfortable Silence

```
You are Pavel Kotelnikov. You've asked the candidate a question. They've
answered. You do NOT respond immediately. You let 5-7 seconds of silence
elapse on the call.

Some candidates will re-start and try to fill the silence with additional
content — often weaker than their original answer.

I will demonstrate how I would handle your silence. Tell me:
1. Did I hold the silence appropriately, or did I ramble
2. If I added content, did it improve or dilute my answer
3. What should I have done instead

Here's my first answer to "tell me about a security incident you handled."
After you receive it, respond ONLY with: "..."

Then I will respond to your silence. Evaluate me then.

My answer:
[Deliver the POS skimmer story from 04_STAR_STORIES.md Story 4]
```

---

## Prompt 8 — The Behavioral Curveball

```
You are Pavel Kotelnikov, Sr. Manager IT Security at OneDigital. You ask a
less-typical behavioral question — something that tests operational judgment
under ambiguity.

Pick ONE of these to ask me:

A) "Tell me about a time you had to push back on a leader you respected."
B) "Describe a security decision you got wrong."
C) "Walk me through a time when you said 'no' to a business request and
    it went poorly."
D) "Tell me about the last time you were genuinely surprised by a security
    finding in your own environment."

After my answer, evaluate:
1. Specificity of the story (or generic frame)
2. Honesty of the self-assessment
3. Quality of the lesson named
4. Whether the story ported naturally to what the OneDigital role requires

My answer: [let the question pick itself, respond live]
```

---

## Prompt 9 — The Vendor Review Scenario

```
You are Pavel Kotelnikov. You present this scenario:

"OneDigital's benefits consulting team wants to adopt a new AI coaching
chatbot. The vendor is a Series B startup with 40 employees. They have a
SOC 2 Type 1 report from six months ago but not a Type 2. They want to
integrate via OAuth into our Entra tenant and pull employee demographic
data. Walk me through your review process."

You are testing:
1. Framework discipline (SOC 2 review, vendor risk process)
2. Judgment (Type 1 vs Type 2 gap, startup maturity signal)
3. Identity + integration thinking (OAuth scopes, data classification)
4. Forward-looking controls (what to require before approval)

If the candidate says "just approve it" — push on compliance gaps.
If the candidate says "never approve this" — push on the business need.
You want them to find the middle: "Here's what I'd require before approval."

My answer: [deliver a 7-point review using 03_TECHNICAL_PREP.md Scenario S1]
```

---

## Prompt 10 — The Close Close

```
You are Pavel Kotelnikov. You've reached 25 minutes of a 30-minute HM
screen with the candidate. You are about to say "any last questions for
me" and wrap.

Imagine the candidate asks: "Based on what we've talked through, is there
anything that leaves you uncertain about me for this role?"

Depending on your actual internal assessment, you would either:
A) Give them a concrete objection to address
B) Politely deflect ("no, we covered good ground")
C) Change the subject ("let me tell you about next steps")

Simulate giving an honest objection in scenario A. Pick the most likely
concern a CISA-trained hiring manager would have about the candidate
(likely the tool gap on Snyk/Salt/AIDR/Qualys, OR the "six months at
current role" tenure, OR the CISSP in progress commitment).

After you give the objection, I will respond. Evaluate whether my response:
1. Addressed the actual concern (not a deflection)
2. Offered concrete evidence or next steps
3. Closed the loop without over-apologizing

Give me your honest objection now, as Pavel.
```

---

## Prompt 11 — The Voice Delivery Critique

```
This is a meta-prompt for when you want voice delivery feedback, not content
feedback.

I am going to record myself delivering [PITCH / STORY X]. I will transcribe
it and paste it below, along with my perception of how it sounded.

Critique only the DELIVERY, not the content. Tell me:
1. Where I used filler words ("um," "like," "basically," "actually")
2. Where the pacing felt rushed
3. Where I lost energy or volume
4. Whether the story landed with natural emphasis on the right words
5. Whether I sounded like the content was true to me or like I was reciting

Specific brand note: Emmanuel streams weekly technical content on YouTube
and TikTok. Fluency with voice is his baseline. The goal is not "don't sound
scripted" — it's "sound like you on your best day."

Transcript:
[Paste]

My self-perception:
[What I thought went well / badly]
```

---

## Prompt 12 — The Day-Of Reality Check

```
This prompt is for Wednesday evening or Thursday morning. Use it to
pressure-test readiness.

You are a career coach + interview prep specialist who has worked with
hundreds of senior security engineers. I have an HM screen Thursday at
1 PM ET with Pavel Kotelnikov, CISA, Senior Manager IT Security at
OneDigital.

Ask me 5 rapid-fire sanity check questions. I will answer each in under
30 seconds. Score me at the end.

Examples of the kinds of questions you might ask:
- "What's OneDigital's current ownership structure?"
- "Who is the CEO?"
- "What's one thing you will NEVER say in the interview?"
- "What are your 3 questions for Pavel?"
- "What's your floor on compensation?"
- "What's the audit-register phrase you'll use 3+ times?"

Start now.
```

---

## Drill Schedule (Wednesday and Thursday)

**Wednesday evening (45 min):**
- Prompt 1 (pitch critique) — 10 min
- Prompt 2 (threat modeling) — 15 min
- Prompt 4 (Salesloft probe) — 15 min
- Prompt 12 (sanity check) — 5 min

**Thursday morning (30 min):**
- Prompt 11 (voice delivery) on the pitch — 10 min
- Prompt 7 (uncomfortable silence) — 10 min
- Prompt 12 (sanity check, again) — 5 min
- Review the index card from `08_HIRING_SIGNALS_AND_TRUST.md` — 5 min

**30 minutes before call:**
- Centering ritual from `08_HIRING_SIGNALS_AND_TRUST.md`
- Water, clean shirt, meeting joined
- No more drilling. You are ready.

---

## Quality Bar for "Ready"

You are ready when:
- The 60-second pitch feels like breathing, not reciting
- You can name Snyk's SAST/SCA/Container/IaC pillars without hesitation
- You can deliver the 7-point vendor AI review in 60 seconds
- You can say "I haven't used [X] hands-on. What I've used is [Y]" without flinching
- You can resist the urge to fill silence after Pavel stops talking
- Your three questions for Pavel are written on your index card in your own words
- Your compensation floor is non-negotiable in your head — $120K

If any of these feel shaky Wednesday night, drill that one Thursday morning before the call.
