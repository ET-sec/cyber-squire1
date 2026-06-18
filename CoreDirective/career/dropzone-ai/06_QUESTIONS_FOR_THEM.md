# Questions For Them: Dropzone AI Interview Playbook

**Candidate:** Emmanuel Tigoue
**Role:** Senior Security Engineer, Dropzone AI
**Stage status (2026-04-28):** Stage 1 + 2 DONE. **Stage 3 = Thu 2026-05-07, 12:45-1:30 PM EDT, with Eric Hammerle (Director of Engineering).**
**Context:** $37M Series B (July 2025), CEO Edward Wu (ex-ExtraHop NDR detection lead), autonomous AI SOC analyst category, competing with Simbian, Prophet, Crogl.

The questions a candidate asks are a mirror. Dropzone will read seniority by what you choose to dig into. Junior candidates ask about logistics. Senior candidates ask about quality bars, failure modes, and roadmap trade-offs.

---

## STAGE 3: QUESTIONS FOR ERIC HAMMERLE (Director of Engineering, May 7)

Eric runs engineering. He grades you on technical depth and judgment. Questions for him are a chance to demonstrate seniority by what you probe. Pick 4 to 5 from the ranked list below. The closer is non-negotiable.

The pattern across all of these: ask about quality bars, failure modes, rollout discipline, and team rhythm. Avoid logistics, comp, and anything Googleable. Below each question, "the bad version" shows the junior phrasing, "the good version" shows what to actually say.

### Investigation Quality (3)

#### Q1. How do you measure investigation quality on the agent today, and what's the target curve over the next two quarters?
- **Why this works:** Tests whether Dropzone has a metric culture or runs on vibes. The answer reveals whether you're inheriting a benchmark suite or building one. Either answer is useful, you just need to know which world you're walking into.
- **Signal it sends:** I think in measurable quality, not adjectives. I'd know what to ship in week 2.
- **The bad version:** "How do you know if the AI is good?"
- **The good version:** "How do you measure investigation quality on the agent today, is there a golden dataset, an LLM-as-judge layer, a customer feedback loop, or some combination? And what's the target curve over the next two quarters?"

#### Q2. Where does the agent hallucinate most, and how does that finding come back from customer to engineering?
- **Why this works:** Forces a war story. If Eric can name a specific failure mode and the loop that closes it, the team is mature. If he deflects, the feedback loop is broken or the team isn't honest about limits.
- **Signal it sends:** I expect production AI to fail and I want to see the operational reality, not the marketing version.
- **The bad version:** "Does the AI ever get things wrong?"
- **The good version:** "What's the biggest hallucination or scope-skip pattern you've seen in production, and what's the path from a customer flag back to a sprint commit?"

#### Q3. How do you evolve investigation logic for a new alert class without regressing the classes that already work?
- **Why this works:** This is the single hardest engineering problem in the role. Asking it shows you understand that in SOC tooling, regression is not cosmetic, it's a missed breach. The answer reveals whether they have a regression suite or whether they ship on hope.
- **Signal it sends:** I think in production stakes. I write regression tests before I write features.
- **The bad version:** "How do you make sure new code doesn't break old code?"
- **The good version:** "When you evolve investigation logic for a new alert class, what does the regression strategy look like for the classes already in production? Are you running a held-out set, shadow mode against live customer alerts, both?"

### Engineering Culture (3)

#### Q4. What's the rollout pattern for a new detection or agent change: canary, feature flag, shadow mode?
- **Why this works:** Tests production discipline. The answer tells you whether the team ships fast and recovers fast, or whether changes are scary events. Either is workable; you need to calibrate.
- **Signal it sends:** I respect production. I roll out slowly and I can undo what I ship.
- **The bad version:** "How do you deploy changes?"
- **The good version:** "What does the rollout pattern look like for a new agent change, feature flag, canary against a tenant subset, shadow mode for some window? And what's the typical time from merge to full rollout?"

#### Q5. How is the Python codebase structured today, and what's the team's opinion on lint, type checks, and test coverage?
- **Why this works:** Tests modernity and team discipline. Concrete and specific. "We're on 3.9, no type hints, tests are spotty" is one signal. "3.12, strict mypy in CI, 80% coverage gate" is another. Either way, you learn the day-one reality.
- **Signal it sends:** I write production Python and I have an opinion on tooling. I won't be surprised by what I find.
- **The bad version:** "What's your tech stack?"
- **The good version:** "How is the Python codebase structured, monorepo or service split, Python version, what's the team's opinion on Ruff, mypy, Pyright, and what's the test coverage bar before something can ship?"

#### Q6. What's the on-call rotation actually like: frequency, what typically pages, and is it a system-health page or a detection-correctness page?
- **Why this works:** Practical. Reveals the real burden of the role and what the team treats as a production incident. Distinguishes between "the platform is broken" pages and "the agent got an investigation wrong" pages, those are very different jobs.
- **Signal it sends:** I take on-call seriously, I want to understand the rotation before I sign, and I won't complain about it.
- **The bad version:** "Is on-call bad?"
- **The good version:** "What's the on-call rotation actually like, frequency per engineer, what typically pages, and is it more a health-of-system page or a detection-correctness page when it fires?"

### Architectural Altitude (3)

#### Q7. How is the investigation pipeline structured in code: agent loops, tool abstractions, retries, partial failures?
- **Why this works:** Separates "I used LangChain once" from "I've reasoned about agent orchestration at scale." Eric will know within ten seconds whether you've built this kind of thing or just read about it. Asking the question shows you care about architecture, not just output.
- **Signal it sends:** I've built agent systems. I think in graphs, not scripts.
- **The bad version:** "How does the AI work?"
- **The good version:** "How is the investigation pipeline structured in code, what does the agent loop look like, how are tools abstracted, and how do you handle retries and partial failures in a multi-step investigation that might run for minutes?"

#### Q8. What's the philosophy on integration depth versus breadth: go wide to win deals, or deep on a core set to own the investigation quality story?
- **Why this works:** This is a strategy question disguised as an architecture question. Reveals the team's theory of the market and what kind of engineering work the role will actually involve. Wide-and-shallow integrations is a different job than deep-and-canonical investigations.
- **Signal it sends:** I think like an operator, not just an engineer. I read the JD as a strategy artifact.
- **The bad version:** "How many integrations do you have?"
- **The good version:** "You support 90+ integrations. What's the philosophy on depth versus breadth, go wide to win deals, or go deep on a core set to own the investigation quality story across the most common alert sources?"

#### Q9. What's the biggest piece of technical debt or unsolved problem the team is actively working on right now?
- **Why this works:** Tests honesty. Every team has one. If Eric can name it specifically, the team is self-aware and you'll know what you're walking into. If he deflects, that's also data.
- **Signal it sends:** I want to walk in knowing the real terrain, not the recruiting brochure.
- **The bad version:** "Are there any problems with the codebase?"
- **The good version:** "What's the biggest technical debt or unsolved engineering problem the team is actively working on right now? Not the JD version, the actual one."

### Career Growth at Dropzone (1)

#### Q10. If I joined and 90 days in had added significant leverage: real, measurable: what does that look like to you?
- **Why this works:** Forces Eric to describe success in concrete terms. You get a preview of the 90-day review before you sign. Surfaces mismatched expectations early. This is the single best Director-level question.
- **Signal it sends:** I hold myself to a 90-day bar. I want clarity on what "good" looks like before I sign on.
- **The bad version:** "What are the expectations for this role?"
- **The good version:** "If I joined and 90 days in had added significant leverage, real, measurable, the kind you'd point to in a review, what does that look like to you?"

### Hiring / Team (2)

#### Q11. Where would this role sit in the org, and what's the split between customer-driven work and longer-term engineering bets?
- **Why this works:** You need the org chart. Where the role lives determines what you can influence. The customer/bet split tells you whether engineers ship strategy or run a ticket factory. Both can be fine, you need to know.
- **Signal it sends:** I think about leverage and where my work flows. I'm not just looking for a seat.
- **The bad version:** "Who would I report to?"
- **The good version:** "Where would this role sit in the engineering org day to day, and what's the split between customer-driven work, bug a customer hit, integration they requested, versus longer-term bets the team initiates on its own?"

#### Q12 (Closer, non-negotiable). Eric, is there anything from this conversation that leaves you uncertain about me for this role? I'd rather address it now than leave it unsaid.
- **Why this works:** Three reasons. Most candidates won't ask. It surfaces objections while you can still answer them. It reframes you as a collaborator, not a supplicant. It is the single highest-leverage question in any interview.
- **Signal it sends:** I can handle direct feedback. I treat the interview as a partnership, not a verdict.
- **The bad version:** "Do you have any concerns about me?"
- **The good version:** "Eric, before we wrap, is there anything from this conversation that leaves you uncertain about me for the role? I'd rather address it now than leave it unsaid."
- **What to do with the answer:** If he names a real concern, acknowledge cleanly, give the 30-second mitigation, move on. Do not over-explain. "That's fair. Here's how I'd close that gap in the first 60 days." If he says "no concerns," thank him and close.

### If There's Time (3)

These are bonus questions if Eric runs short on the agenda and asks for more, or if there's natural conversational space. Do not force them.

- **"What's the worst customer-facing miss the agent has had, and what changed in engineering as a result?"**, pulls a war story without sounding accusatory.
- **"What does a great Senior Security Engineer at Dropzone look like 12 months in, what are they known for on the team?"**, gives Eric a chance to describe his ideal hire in his own words, which gives you a script for behavior in the loop.
- **"What's something about the team or the codebase that you wish you'd known before you joined?"**, invites honesty by inverting the question. Often produces the most useful answer of the call.

### Do NOT Ask These (3)

- **"What's the comp band?"**. Already on the JD ($175-217k). Asking signals you didn't read it. Shaleena is the comp channel, not Eric.
- **"How much PTO do you get?"**. Logistics. Not for the technical round. Not for any round before offer.
- **"Are you worried about Simbian / Prophet / Crogl as competitors?"**. Sounds like you're testing him on something he's already heard a hundred times, and it can read as gotcha. The strategic version of this question (Q8 above) is the better play.

---

## Section 1: Recruiter Screen (Shaleena): 5 Primary + Alternates

Shaleena is G&A talent, not technical. She is screening for fit, compensation alignment, timeline, and whether you will carry yourself well through the loop. Keep questions respectful of her role. Do not grill her on Python or agent architecture. Ask what she actually knows and can influence.

### 1. "Can you walk me through the interview loop after this? Who would I meet, and roughly what does each round focus on?"
**Why this works:** Signals you are planning, not just reacting. Gives you names to research before the next round. Recruiters appreciate candidates who treat the loop like a structured process, because it makes their job easier when you show up prepared.

### 2. "How does the team think about seniority here? What does a Senior Security Engineer at Dropzone look like six months in: what have they shipped, what are they owning?"
**Why this works:** Forces a concrete answer about the bar. You learn whether "Senior" means IC depth, cross-team leverage, or leading a squad. Also tells you if they have thought about onboarding or if new hires flounder for a quarter.

### 3. "What is the bar for shipping investigation quality improvements? How does the team measure it internally?"
**Why this works:** This is the core of the role. Even if Shaleena cannot answer in technical depth, her answer tells you whether the company has a clear metric culture or whether it is vibes-driven. Her framing ("the team uses X dashboard" vs. "I think they have benchmarks") is a signal.

### 4. "What is your honest take on what makes someone thrive at Dropzone, and what makes someone struggle?"
**Why this works:** Recruiters see the full funnel. They know who got promoted, who left after four months, and why. Asking for the honest version invites a real answer instead of marketing copy. Use the word "honest", it gives permission.

### 5. "What is the timing on a decision here? I have one other active conversation and I want to sequence things respectfully on both sides."
**Why this works:** Establishes you are a wanted candidate without being aggressive. Forces Shaleena to commit to a timeline, which benefits you in offer negotiation. The phrase "respectfully on both sides" is key, it positions you as considerate, not transactional.

### Alternates (pick based on flow)

- **"What has changed at Dropzone since the Series B closed in July? Hiring, product priorities, anything noticeable from inside?"**. Shows you did your homework on the funding event and treat it as a business signal, not trivia.
- **"What is the compensation band for this role, and how does Dropzone think about equity refresh for senior ICs?"**. Ask this near the end. Gets the number on the table early so no one wastes cycles if it is misaligned. Framing the equity question shows you know Series B equity matters more than base.
- **"Is the role Seattle-based, hybrid, or fully remote? What is the expectation on travel or in-person for team offsites?"**. Only ask if it is not already clear. Do not ask if it is posted on the job page.

---

## Section 2: Technical Screen + Panel Rounds: 15 Questions

Grouped by theme. Do not ask all 15 in one round. Pick 3-5 per conversation based on who you are talking to. An engineer wants to talk codebase and failure modes. A PM wants product strategy. A director wants team and roadmap.

### Product + Investigation Quality (5)

**1. How do you measure investigation accuracy today? Is there a golden dataset the agents run against, an LLM-as-judge layer, customer feedback loop, or some combination?**
Asks the one question every AI product team is wrestling with. Shows you understand that "the AI is accurate" is marketing language and that real teams have an eval harness. Tells them you will not join and then ask what a benchmark is.

**2. When an investigation conclusion turns out to be wrong, either a miss or a confident wrong call, how does that come back to engineering? What is the feedback path from customer SOC to your sprint?**
Senior engineers think in loops. This question reveals whether the company has tight feedback cycles or whether errors die in a CS ticket queue. The answer also tells you how hard your job will actually be.

**3. How do you decide which alert classes to invest in next, phishing, lateral movement, cloud IAM, DLP? Is it customer-driven volume, strategic bet, or something else?**
Tests their prioritization framework. The category is wide and you cannot cover all of it at once. Their answer reveals whether product strategy is disciplined or reactive.

**4. What is the biggest hallucination or failure mode you have seen in production, and how did the team mitigate it?**
This is the single best question to ask. It forces a war story. If they cannot answer or deflect, they either have not shipped to real customers or they are not honest about limits. Senior engineers reward candor with their own candor.

**5. How do you evolve investigation logic without regressing existing customers on alert classes that already work well? What does your regression test strategy look like for agents?**
Shows you understand the stakes of a production AI system. In SOC tooling, a regression is not a cosmetic bug, it is a missed breach. Asking this tells them you have thought about the operational reality, not just the happy path.

### Python Codebase + Engineering (4)

**6. Can you describe the Python codebase? Monorepo or multi-service, Python version, what tooling for lint and type checks. Ruff, mypy, Pyright?**
Concrete, senior, specific. You are checking whether the codebase is modern and whether the team has an opinion. If the answer is "we are on 3.9 and there are no type hints," that is a signal. If the answer is "3.12, Ruff, strict mypy in CI," that is also a signal.

**7. How is the investigation pipeline structured in code? Agent loops, tool abstractions, how do you handle retries and partial failures in a multi-step investigation?**
Shows you have built agent systems yourself and care about the architecture, not just the output. This is the question that separates "I used LangChain once" candidates from ones who have reasoned about orchestration at scale.

**8. What is the on-call rotation like, frequency per engineer, what typically pages, is it a health-of-the-system page or a detection-correctness page?**
Practical. Reveals the real burden of the role. Also tells you what the team considers a production incident, which tells you what they actually value.

**9. What is the code review and shipping cadence? Trunk-based with feature flags, review SLAs, how fast can an engineer get a change to production?**
Tests velocity and discipline. Fast shipping with no review is chaos. Slow shipping with heavy review is molasses. Senior engineers want to know which end of the spectrum the team lives on so they can calibrate.

### Team + Culture (3)

**10. How is the engineering team structured, feature squads, platform teams, detection pods, something else? Where would this role sit and who would I work with day to day?**
You need the org chart. Where a role lives determines what you can influence. "Platform" roles have different leverage than "detection" roles.

**11. What is the split between customer-driven work, new integration requested by a customer, a bug they hit, versus longer-term engineering bets the team initiates?**
Reveals whether engineers have room to build or whether they are a customer-request factory. Both can be fine in different companies, but you need to know which one you are signing up for.

**12. What is the biggest technical debt or unsolved problem the team is actively working on right now?**
Gets at honesty. Every team has one. If they cannot name it, they are either hiding something or they lack self-awareness. The specific answer also gives you a concrete thing to discuss in a follow-up.

### Strategy + Growth (3)

**13. You just launched the Threat Hunter agent and Intel Analyst is coming Summer 2026. How does the product roadmap shape hiring priorities for this role and the next few hires after?**
Shows you read the press releases and treat them as signals about engineering investment. Forces them to connect hiring to product strategy, which is a test of whether leadership is aligned.

**14. You support 90-plus integrations and the list is growing. What is the philosophy on integration depth versus breadth, do you go wide to win deals, or deep on a core set to own the investigation quality story?**
This is a CEO-level strategy question. Shows you understand that in SOC tooling, depth and breadth are a real trade-off and that the answer reveals the company's theory of the market.

**15. The AI SOC analyst category is getting crowded. Simbian, Prophet, Crogl, Radiant, others. How does the team think about the moat, is it model quality, integration surface, investigation accuracy, customer lock-in, something else?**
Asking about the moat tests the company's self-awareness. A strong answer is specific and defensible. A weak answer is "we are faster" or "we have better AI." This question also signals you think like an operator, not just an engineer.

---

## Section 3: Hiring Manager: 5 Sharper Questions

These are meatier and designed to test how the manager thinks, not just what they know. Use these in the HM round specifically. They respect the manager's time and invite real conversation.

### 1. "If you could wave a wand and fix one thing about how we investigate a specific alert class today, what would it be?"
Forces a concrete answer. Managers who have their hands in the product will name a specific gap. Managers who are detached will give a generic answer. Either way you learn something useful.

### 2. "How do you evaluate your own AI agents' output? What is your quality bar in production, and how do you enforce it when releases are on the line?"
Tests their personal standard. A good manager has a view that is clearer than the company metric. Shows you care how decisions get made under deadline pressure.

### 3. "If I joined and ninety days in had added significant leverage: real, measurable: what would that look like to you?"
Makes them describe success in concrete terms. You get a preview of the 90-day review before you sign the offer. Also surfaces mismatched expectations early.

### 4. "What is the hardest engineering problem you are recruiting for this role to solve? Not the job description version, the actual one."
Invites honesty. The "actual one" phrasing gives permission to drop the marketing. Good managers respect the directness. Bad managers get defensive, which is also useful data.

### 5. "What is your philosophy on balancing investigation accuracy versus latency in a SOC context? When do you accept a slower, more thorough answer, and when do you ship a faster, less certain one?"
This is the core engineering trade-off in the product. Shows you have thought about the operational reality. The manager's answer tells you how they reason about trade-offs in general, which is the single most useful thing to know about a future boss.

---

## Section 4: Avoid These: They Signal Junior

Any question that fits these patterns will cost you points. If you feel one coming, rephrase or skip.

- **"What are your hours?"**. Sounds clock-punching. If you need to know, ask "What does a typical week look like for someone in this role?" instead.
- **"Do you offer a training budget?"**. Fine question, wrong time. Ask in the offer stage, not the interview.
- **"What is your tech stack?"**. You should have Googled this. Asking signals you did not prepare. If you want depth, ask question 6 above instead.
- **"Is there a dress code?"**. Never ask. Figure it out from the team's LinkedIn photos.
- **Anything starting with "do you..." in a binary yes or no way.** Binary questions produce binary answers. Open questions produce signal. Rephrase "Do you have a QA process?" into "How does QA work for agent output?"
- **Anything you could answer in ten seconds on the Dropzone website, blog, or job posting.** If it is on the careers page, you are burning their time and yours.
- **"Why should I work here?"**. Puts them on defense. Inverts the interview. Ask instead "What has made you stay?" or "What is the best thing about the team that is not on the careers page?"

---

## Section 5: The Closing Question That Lands Every Time

At the end of any round, recruiter, technical, hiring manager, panel, use this single question:

> **"Based on what I have shared so far, is there anything about my background that leaves you uncertain about this role? I would rather address it now than leave it unsaid."**

### Why it works

Three reasons.

**It shows courage.** Most candidates will not ask. They are afraid of the answer. Asking signals you can handle direct feedback, which is a senior trait.

**It surfaces objections while you can still answer them.** If an interviewer is worried you lack a specific tool, or they misread a bullet on the resume, you get one shot to clarify. Without the question, their doubt goes into the debrief unchallenged and you lose.

**It reframes you as a collaborator, not a supplicant.** The phrasing "leave it unsaid" treats the interviewer as a partner in the decision, not a judge. That is the posture of a senior hire.

### When to deploy

Every round. Vary the phrasing slightly so it does not sound rehearsed if interviewers compare notes.

- **With Shaleena (recruiter):** "Is there anything from my background you think I should be ready to address in the next round?"
- **With a technical interviewer:** "Is there any gap in my technical background from our conversation that you would want me to clarify?"
- **With the hiring manager:** The full version above.
- **With a panel:** Ask one person, not the whole panel. Pick the one who seemed most skeptical.

### What to do with the answer

If they name a real concern, acknowledge it cleanly, give the 30-second version of why it is manageable, and move on. Do not over-explain. Do not apologize. "That is fair. Here is how I would close that gap in the first sixty days..." is the right shape.

If they say "no concerns," thank them and close. That is also useful data, it means you are through to the next round on merit.

---

## Quick Reference Card

| Round | Open With | Close With |
|-------|-----------|------------|
| Recruiter (Shaleena) | Loop walkthrough question | Timing question |
| Technical screen | Codebase + quality metric | Closing question (technical version) |
| Hiring manager | Hardest problem question | Closing question (full version) |
| Panel | Team structure + roadmap alignment | Closing question (aimed at skeptic) |

**Rule of thumb:** Ask two to four questions per round. Not more. You are evaluating them, but they are also evaluating how you steward time. A senior candidate does not interrogate, they probe the two or three things that actually matter.

**Final note:** Write the answers down after each round. Patterns across interviewers tell you more about the company than any single conversation will.
