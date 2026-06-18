# ADHD Learning Protocol — Technical Curriculum at $200K Pace

This is the operating protocol for retaining technical material under ADHD constraints, built on Russell Barkley's executive-function research, Anders Ericsson's deliberate practice, the Pomodoro technique evidence base, ADDitude's clinical guidance, and Andrew Huberman's focus protocols. Tuned for one specific candidate: 4 hours of sleep, full-time job hunt, AI security curriculum to absorb in weeks not years.

The protocol is honest about what 4 hours of sleep costs you. Sections at the bottom address the sleep penalty directly.

---

## Part 1. Time Block Length — 25 to 50 minutes, not 90

The 90-minute "ultradian rhythm" block is a productivity-blog myth for ADHD brains. Evidence:

- Pomodoro's original 25-minute block was selected by Francesco Cirillo because it matched the average sustained-attention window for adult learners. Subsequent research by Newport, ADDitude, and clinical CBT-for-ADHD literature backs this for ADHD specifically.
- Barkley's executive function research shows ADHD attention is "interest-driven" not "duration-driven". You can run 4 hours on a hyperfocus surge, then crash for 2 days. Pretending the second day exists is the failure mode.
- Huberman's focus protocols recommend 90-minute blocks for neurotypical deep work. For ADHD, halve it.

**Block format that works:**

| Block | Length | What |
|-------|--------|------|
| Sprint | 25 min | Single concept, single artifact, no tabs |
| Break | 5 min | Stand, water, walk, no phone |
| Sprint | 25 min | Same concept, deeper |
| Break | 5 min | Same |
| Sprint | 25 min | Apply concept to a lab or write a paragraph |
| Long break | 20 min | Walk outside, real food |

Three sprints + breaks = ~85 minutes total, 75 minutes of actual work. Two cycles per day is the realistic ceiling on 4 hours sleep. One cycle on bad days is still progress.

If you can run 50-minute blocks instead of 25, do it. Ericsson's deliberate practice research suggests longer is better when the block is structured. The constraint is whether attention holds, and 4-hours-of-sleep ADHD attention does not hold for 50.

---

## Part 2. Break Structure — Movement, Water, No Screens

The break is not a reward, it is a state reset. Rules:

1. Stand up. Sitting break does not count.
2. Water or unsweetened tea. Sugar crash kills the next sprint.
3. No phone. No Slack. No "quick check". The dopamine hit from social media flattens the next sprint's curiosity drive.
4. 90 seconds of sunlight if available (Huberman: morning sun in the eyes regulates focus and sleep, even via window).
5. Optional: 4-7-8 breathing for one minute. Drops sympathetic tone, easier re-entry.

---

## Part 3. Body Doubling — Free Force Multiplier

Body doubling is the single highest-ROI ADHD tactic that costs nothing. Mechanism: parallel presence of another working human silences the procrastination loop. ADDitude documents this as one of the top three evidence-backed ADHD productivity tactics.

Implementation options that have worked:

- Focusmate (paid, $5/mo) — books a stranger to body double on video for 25 or 50 minutes
- Discord study servers (free) — DEFCON, blackhat, security study groups have voice channels
- Coffee shop or library (free) — physical body doubling, no interaction required
- Twitch "study with me" streams (free) — passive body doubling

Stack with Pomodoro: announce the goal at minute 0, work silently, report at minute 25. The social commitment closes the loop.

---

## Part 4. Externalize Memory — Notes, Voice Memos, Anki

ADHD working memory is not the deficit, it is the leak. Every concept that does not get written down gets lost. Treat the laptop and phone as your working memory, not your brain.

Required externalization stack:

1. **Anki** — spaced repetition for facts, IDs, command syntax. Setup: 20-card daily review cap, new cards 5/day max. Add cards live during sprints. https://apps.ankiweb.net/
2. **Voice memos** — for concepts you cannot type fast enough. Whisper transcribe later. iPhone Voice Memos > Otter > paper.
3. **A single markdown notes file per topic** — never search Slack or browser history for a previously-learned concept. Notes file or it didn't happen.
4. **A "questions to research" parking lot** — open in every sprint, dump every tangent into it, never chase the tangent during the sprint.

Anki cards that work for security:

- Front: "OWASP LLM01" / Back: "Prompt Injection — user or upstream input alters intended behavior"
- Front: "ATLAS technique for tool poisoning" / Back: "AML.T0110 AI Agent Tool Poisoning"
- Front: "Trivy version to avoid in 2026" / Back: "0.69.4 (malicious release 2026-03-19)"

Cards that fail: long prose, multiple facts per card, ambiguous prompts. One fact per card.

---

## Part 5. Novelty as Dopamine Fuel

ADHD brains run on novelty, not discipline. This is a feature, not a bug. Stop fighting it.

Tactics that channel novelty:

- **Vary the medium.** Video for hour 1, hands-on lab for hour 2, written summary for hour 3. Same concept, three modalities. Triples retention vs. reading the same chapter three times.
- **Switch tools.** Same content in a different IDE, different terminal theme, different physical location. Reset costs 30 seconds, buys an hour of attention.
- **Adversarial framing.** "How would an attacker abuse this?" turns boring documentation into a thriller. Works for protocols, frameworks, even compliance.
- **Teach it back.** Record a 60-second video explaining what you just learned. The performance is the dopamine hit. Even if no one watches it.

---

## Part 6. Why Labs Beat Reading

Cognitive load research (Sweller) and deliberate practice research (Ericsson) converge on one thing: passive consumption is the lowest-retention learning mode for skill acquisition. Active retrieval is the highest. Labs force active retrieval.

Hierarchy of retention (high to low):

1. Build a toy version from scratch (90% retained at 1 week)
2. Modify a working version to break it, then fix it (75%)
3. Pair on it with someone who knows it (65%)
4. Walk through a documented lab (50%)
5. Watch someone else do it (25%)
6. Read about it (10%)

Default to tier 1 or 2 for anything you'll be tested on. Reserve reading (tier 6) for survey-level orientation only.

For AI security specifically, the labs that map to interview questions:

- flAWS challenges (flaws.cloud, flaws2.cloud) — AWS pentest by puzzle
- CloudGoat — AWS attack scenarios with documented walkthroughs
- HackTheBox AI/ML modules — adversarial AI labs
- TryHackMe AI tracks — beginner-friendly AI security paths
- Build a vulnerable LLM agent locally and Garak it — best ROI for prompt-injection fluency

---

## Part 7. The "Boring Fundamentals" Problem (Python Basics)

Hyperfocus brains hate fundamentals. The problem: skipping fundamentals later breaks every advanced topic. Solution: never learn fundamentals in isolation.

Anti-pattern: "I will spend a month on Python basics, then move to LangChain."

Pattern that works: pick a project at the level you want to operate (a Garak custom probe, a LangGraph agent, a Pydantic-validated tool spec). When you hit a syntax wall, fix that one piece and return to the project. The project provides dopamine. The fundamentals get learned just-in-time and stick because they were attached to a real artifact.

Concretely:

- Day 1: clone a working LangGraph agent example, run it, change the prompt, observe break
- Day 2: extend it to call a custom tool, hit a Pydantic error, learn just enough Pydantic v2 to fix
- Day 3: add Garak probes against it, hit an async error, learn just enough asyncio to fix

After two weeks of this, the "Python basics" got covered without ever being labeled as Python basics.

The ones you cannot skip:

- Functions, classes, dict/list comprehensions
- Async/await basics (LangGraph, Anthropic SDK both async)
- Type hints (Pydantic and modern code rely on them)
- Virtualenvs and pip / uv

That is roughly 3 hours of total content. Compress, do not stretch.

---

## Part 8. Spaced Repetition + Feynman + Building

The retention stack that beats raw study time:

1. **Anki for facts** (10 minutes daily, never skip — even on sick days, even on 4 hours sleep, especially then)
2. **Feynman technique for concepts** — at the end of any topic, write a 1-paragraph explanation aimed at a junior. If you can't, you don't know it.
3. **Toy build for skills** — every topic ends with the smallest possible working artifact. 30 lines of code, one diagram, one paragraph that demonstrates the concept

Stack discipline: one Anki review session in the morning (post-coffee, pre-real-work), one Feynman writeup at the end of the day, one toy build per concept per week. Deviations are fine, abandonment is not.

---

## Part 9. The 4-Hour Sleep Penalty (Be Honest)

Four hours of sleep cuts working memory, error correction, and emotional regulation by measurable amounts. Walker's "Why We Sleep" cites:

- Working memory: ~30% reduction after one night of <5 hours
- Reaction time: equivalent to 0.08 BAC after 17–19 hours awake
- Mood regulation: amygdala reactivity ~60% higher
- Glymphatic clearance: severely impaired, accelerates cognitive aging if chronic

This is non-negotiable biology. Pretending you can outwork it ends in burnout and missed interviews.

**Mitigations that actually work:**

1. **Caffeine timing.** First coffee 90 minutes after waking (let cortisol peak first, builds tolerance more slowly). Last coffee 8+ hours before target sleep time. 200mg max per dose, 400mg/day ceiling.
2. **20-minute nap, not 90.** A 20-minute nap restores alertness without sleep inertia. Set an alarm. Nap before 3pm.
3. **Triage ruthlessly.** On a 4-hour-sleep day, pick the ONE highest-leverage thing and do it. Skip Anki review at your peril, but skip everything else without guilt.
4. **Front-load the day.** Hardest cognitive work in the first 3 hours after waking. By hour 6, you are running on cortisol and willpower, both finite.
5. **Get sun in your eyes within 30 minutes of waking.** 5–10 minutes outside. The most underrated focus protocol on the list. Costs nothing.
6. **Protein + fat breakfast, not carbs.** Carbs at breakfast spike then crash glucose. Eggs, yogurt, leftover meat, anything with 30g+ protein.
7. **Sleep is the product.** 6 hours regularly beats 4 hours regularly. If a deadline forces 4 hours for one night, accept it. If 4 hours becomes the pattern, the curriculum loses to biology.

The honest read: a candidate at 4 hours of sleep over weeks is operating at roughly 60–70% of cognitive capacity. The protocol above recovers some of that. Sleeping 6 hours recovers all of it. If both can happen, choose sleep.

---

## Part 10. Daily Structure That Survives Real Life

A reference structure that has worked for similar profiles. Adapt to circumstances:

```
06:30  Wake, sun, water (no phone)
07:00  Coffee + protein
07:15  Anki review (10 min)
07:30  Sprint cycle 1 (25-5-25-5-25-20) — hardest material
09:00  Real life break (60–120 min: gym, errands, calls, food)
11:00  Sprint cycle 2 — second-hardest material
12:30  Lunch + walk
14:00  Sprint cycle 3 — labs / hands-on (lower energy required)
15:30  Job apps, recruiter calls, interviews
17:00  Done with focused work. Buffer / family / content / rest.
21:00  Feynman writeup of today's topic (10 min, in bed)
22:00  Sleep target
```

Three sprint cycles = roughly 4–5 hours of high-quality work. That is enough to absorb the AI security curriculum in 8–10 weeks.

Nothing about this protocol is gentle. ADHD plus 4 hours of sleep plus job hunt plus AI security curriculum is a hard problem. The protocol is the difference between progress and collapse.

---

## Citations and primary sources

- Russell A. Barkley — "Taking Charge of Adult ADHD" (executive function model, interest vs. duration attention)
- Anders Ericsson — "Peak: Secrets from the New Science of Expertise" (deliberate practice, structured blocks)
- Francesco Cirillo — Pomodoro Technique (25-minute block)
- Matthew Walker — "Why We Sleep" (cognitive cost of <5h sleep)
- Andrew Huberman — Huberman Lab podcast, focus and dopamine episodes
- ADDitude Magazine — clinical ADHD productivity coverage (additudemag.com)
- Sweller, J. — Cognitive Load Theory papers
