# May 7 Morning Brief — Last-Mile Cheat Sheet

**Interview:** Today, Thu May 7, 2026, **12:45 PM EDT** (45 min)
**Interviewer:** Eric Hammerle, Director of Engineering, Dropzone AI
**Meeting:** [meet.google.com/bbs-zevf-fmh](https://meet.google.com/bbs-zevf-fmh)
**Compiled:** 2026-05-07 05:30 EDT

This file is the **only thing** you need open during pre-call. Everything else is reference. Read it once at 8 AM, once at 11 AM, once at 12:30 PM. Don't open the other 12 docs.

---

## Identity (lock first)

> "I'm Emmanuel Tigoue, AI Security Engineer at CoreDirective."

Never: "founder," "my startup," "pivoting," "transitioning," "aspiring," "I'm passionate."

---

## Red thread (every answer routes here)

> "I care about investigation quality. I've done it as a human, I've built systems for it, and I want to ship it at scale to every SOC in the world."

---

## What's changed since you prepped on 4/28

Three new Dropzone blog posts in the last 9 days. All by Tyson Supasatit (PMM). **Reference them lightly — once each, max.** Don't recite. Show you read them.

### 1. Apr 28 — "Common Threat Hunting Mistakes and How to Avoid Them"
[dropzone.ai/blog/threat-hunting-mistakes](https://www.dropzone.ai/blog/threat-hunting-mistakes)

Key line: **40-hour hunts compressed to ~1 hour via federated querying across 90+ integrations.** Quarterly hunts → weekly without headcount.

### 2. May 1 — "The Industrialization of Cybercrime: AI Arms Attackers"
[dropzone.ai/blog/industrialization-of-cybercrime-ai](https://www.dropzone.ai/blog/industrialization-of-cybercrime-ai)

Stats worth carrying:
- **29-minute average breakout time** (CrowdStrike data)
- **27 seconds** fastest observed breakout
- **82% of 2025 detections were malware-free** (identity-driven, not file-driven)
- **63% of compromised logins** used pre-stolen creds

These are CrowdStrike numbers, not Dropzone's, but Dropzone is using them. If asked "what's the threat landscape look like to you?" — the malware-free / identity-driven framing is the right answer for this audience.

### 3. May 4 — "Monday Morning, 2030: A Day in the Life of the Agentic SOC"
[dropzone.ai/blog/blog-agentic-soc-day-in-the-life](https://www.dropzone.ai/blog/blog-agentic-soc-day-in-the-life)

**The framing to mirror verbatim:** *Humans own scope, authorization, business context. Agents own volume, speed, 3 AM alerts, weekend queues.*

Named agents in their roadmap: AI SOC Analyst (shipped), AI Threat Hunter (shipped Mar 18), AI Threat Intel Analyst (named, status unclear), plus implied Detection Engineer, Forensics Analyst, Security Data Architect.

**Strategic shift:** Dropzone is moving from "one AI SOC analyst" → "team of specialized agents." Mirror this. If you say "I want to ship investigation quality at scale to every SOC," tie it to: *"and the way you ship it is a roster of scoped specialist agents, not one mega-prompt."*

### What hasn't changed
- No new funding (Series B $37M was Jan 2026)
- No new patents
- No new exec hires
- Eric posted nothing original. Reposts Dropzone corporate. Stays private.
- Your full 9-day intel sweep returned no surprise.

---

## The non-negotiables (memorize cold)

### Three metrics
- Falco eBPF: **200/day → 12 actionable**
- Splunk MTTD: **48h → under 4h**
- IR runbook: **8h → 90 min containment**

### Five soundbites for the Eric mirror
1. "I read AI output the way a senior analyst reads a junior's report."
2. "Grounding is the engineering problem. Hallucination is the symptom."
3. "Every detection ships with a regression test against 30 days of prod traffic."
4. "I optimize for analyst trust first, coverage second."
5. "Production Python earns its place. Notebooks don't."

### Add for May 7 (from new blog posts)
6. "Humans own scope and authorization. Agents own volume and speed. The bar is whether the action graph is replayable by a human in under five minutes."
7. "The compression is real — 40-hour hunts to one hour — and the catch is that the hour can hide a worse failure mode than the 40 hours did. The eval harness is what makes the hour trustworthy."

---

## Take-home: walk-through cheat (line numbers locked)

### File map
```
agent.py        | 107 lines | LangChain agent + router + ask()
tools.py        | 186 lines | 4 @tool wrappers + 4 helpers
moto_setup.py   | 166 lines | seeds S3, EC2, IAM
main.py         |  39 lines | interactive REPL
demo.py         |  44 lines | scripted 4-question run
README.md       | 198 lines | architecture + design + threat model
requirements.txt|   5 lines | langchain 1.2.15, langchain-anthropic 1.4.1, boto3 1.42.92, moto 5.1.22, python-dotenv 1.2.2
```

### Critical line numbers to have memorized
- `agent.py:69-94` — the `ask()` router function. Eric will probe this hardest.
- `agent.py:27-37` — the system prompt (3 grounding rules).
- `tools.py:24` `count_public_s3_buckets`
- `tools.py:46` `list_s3_bucket_contents`
- `tools.py:72` `get_ec2_instance_by_ip`
- `tools.py:106` `get_iam_user_permissions`
- `tools.py:138` `_is_public` (the bucket policy + ACL evaluator)
- `agent.py:51` `build_router` — builds both tiers at startup
- `agent.py:59-66` `pick_tier` — the routing heuristic

### 30-second pitch (memorize verbatim)
> "Natural-language frontend over four read-only AWS investigation tools. LangChain 1.x agent calls Anthropic Claude with native tool calling. Two agents — Sonnet 4.6 for routine, Opus 4.7 for complex, errors, or low-confidence answers. Runs against a Moto sandbox so the reviewer needs no AWS credentials. Tools are narrow on purpose — one tool per sample question — which makes selection easier for the model and easier to audit when wrong. Defense in depth: read-only tools, regex input validation at the tool boundary, prompt-injection language in the system prompt, 500-character question cap to bound cost."

### Three gotchas to own before he finds them
1. **Module-level mutable global `_EC2_INSTANCES` (`moto_setup.py:12`).** "Wrong shape. Works because the module imports once per process. Would break under multi-worker. Caught it after submission."
2. **`_is_public` swallows `AccessDenied` on ACL (`tools.py:155`).** "Should be tri-state — public, not public, unknown. False on AccessDenied is a security-critical false negative in production."
3. **Seeded read-only policy includes `iam:Get*` but the tool calls `iam:List*` (`moto_setup.py:137`).** "Moto papers over it because Moto doesn't enforce IAM. Against real AWS, the analyst couldn't run their own permission lookup. I'd add `iam:List*` to the seed."

### Things you proactively flag (your "honest gaps" list)
- No automated tests. `demo.py` is the de facto integration test.
- String-matching low-confidence check. Brittle. Production wants structured signal.
- No memory across turns. Each question is stateless.
- Tool output not sanitized. A malicious S3 object key could echo into context.
- No prompt caching. Trivial to add. 90% input cost savings on cache hit.

### Two design decisions to defend strong
1. **LangChain over raw Anthropic tool calling.** The brief named LangChain. `create_agent` gives you the agent loop for free. For production at Dropzone scale, LangGraph (state graph + checkpoints + interrupts) is right. For four tools, LangChain pays for itself.
2. **Two-tier router (Sonnet default, Opus on escalation).** Sonnet is ~5x cheaper. Three escalation triggers: long/complex question, exception, low-confidence answer. Proves you think about cost-per-investigation, not just "use the biggest model."

### One sentence ready for "what would you change first?"
> "Ship a pytest eval harness with golden Q&A pairs and wire LangSmith for traces — the lack of evaluation is the biggest gap and the first dollar I'd spend."

---

## Tier 1 questions (60-90% probability — drill these out loud at 8 AM)

### Q1. "Walk me through how you'd review an AI-generated investigation report and decide it's wrong."
> "I treat the report like a code review on a pull request. Three checks. First, did the agent obtain the right evidence — source IP, user identity, process tree, auth log. Missing inputs invalidate the conclusion regardless of how confident the verdict is. Second, are the inferences load-bearing on assumptions the evidence doesn't support — calling something a phishing click without confirming the URL was actually rendered. Third, does the action graph make sense in reverse — could a human analyst replay the steps and reach the same verdict. When I red-teamed our internal LLM gateway against OWASP LLM Top 10, the failure mode I saw most often wasn't the model lying. It was the model reasoning correctly over an incomplete context window. So my first question on any wrong report is: was the data wrong, the framing wrong, or the model wrong. Usually the first."

### Q2. "Tell me about a time you tuned a noisy detection."
> "Falco eBPF was throwing 200 alerts a day in our environment. The team was ignoring them — which is the worst failure mode for a detection. Alive on paper, dead in practice. I sampled 50 of them, classified by root cause, found 80% were three patterns: kubectl exec from CI runners, package manager activity during nightly updates, and a mislabeled benign syscall. I wrote three suppression rules, kept the original ones in audit-only mode for 30 days to verify no real signal was lost, and dropped to 12 actionable alerts a day. The lesson was the discipline of *audit-only first*. You never delete a detection. You shadow it until the data tells you it's safe."

### Q3. "What's the difference between a good agent design and a bad one?"
> "Bad agent designs put the model in charge of credentials and infrastructure. Good designs keep judgment with the model and put credentials, data access, and side-effects behind scoped tools with deterministic guardrails. The opinion I'd add — and I'm interested if you agree — is that the eval harness is more load-bearing than the prompt. You can rewrite a prompt in an hour. Standing up an eval that catches a regression before it ships to a customer takes weeks. Most teams under-invest there because the work isn't visible until something breaks."

### Q4. "Six-plus years of experience — how do you think about your background mapping to this?"
> "I'm an AI Security Engineer at CoreDirective and the work I've shipped in the last 14 months is what would normally be five to six years of distributed responsibility. I built the SOC stack — Falco for behavioral detection, Splunk correlation, Wireshark packet investigation, an n8n SOAR with 14 active workflows, an OpenClaw LLM gateway with 27 internal skills under policy. I wrote the GRC library — 37 documents covering NIST AI RMF, OWASP LLM Top 10, AI Incident Response. I red-teamed our own gateway. The question isn't whether I have six years of resume. It's whether I've already done the job. I'd rather show you the work."

### Q5. "What's a hard tradeoff you made in a system you built?"
> "Inside our LLM gateway I had to choose between rich tool access — which makes investigations powerful — versus locking down the tool surface to limit blast radius. The early version had broad access. I red-teamed it against OWASP LLM Top 10 and found three classes of issue: prompt injection through tool descriptions, over-broad policy on file system access, and a logging gap where the model could call a tool without the call ending up in the audit trail. The fix was scoped tools, every tool wrapped in a policy check, and an action graph that logged the tool plan before execution. I lost some flexibility — agents can't improvise as much. I gained replay-ability and the ability to write evals against the action graph. I'd make the same call again."

---

## Tier 2 questions (40-60% — be ready, 60s answers)

### "Why Dropzone?"
> "Three reasons. One, the technical thesis is right — investigation quality is the bottleneck and the only way through is structured agent autonomy with deterministic guardrails. Two, you're shipping it. The patents in 2025 — automated threat hunting, context repository management — those are the architecture, not slideware. Three, I want to do this work for ten thousand SOCs, not one. CoreDirective gave me proof I can build the stack. Dropzone is where the stack matters."

### "What does 24/7 on-call look like to you?"
> "I assume one rotation slot every 4-6 weeks, page-able, MTTR target on the order of 30 minutes for severity-1, and a strong runbook culture so the person on call isn't reverse-engineering the system at 3 AM. The thing I'd want to know is your incident-review cadence — every page should produce either a runbook update, an alert tuning, or a code change. Otherwise the rotation is a tax instead of a feedback loop."

### "Production Python — what do you actually own?"
> "Honest answer — my heaviest Python work has been the SOAR orchestration glue, the GRC pipeline, and the red-team tooling I wrote against OpenClaw. Type-hinted, tested with pytest, packaged with Poetry. The codebase I'd be joining is bigger and more disciplined than mine, and I'd treat my first 60 days as reading the existing investigation flows before writing new ones. I'm comfortable saying I'd hit ramped productivity by week 6, not week 2 — and I'd rather you know that up front than have me bluff."

### "How would you measure investigation quality?"
> "Three layers. Top-line — false positive rate and false negative rate per alert class, tracked weekly. Middle — agreement rate between the agent and a human analyst on a held-out sample, run on every model or prompt change. Bottom — action graph coverage, meaning every report has a replayable trace. The pitfall is over-indexing on top-line FP/FN without the held-out human comparison. You can drift confidently in the wrong direction for months."

### "What's the riskiest part of an autonomous investigation agent in production?"
> "Two. First, silent context loss — the agent reasons correctly over the data it has, but the data is missing the field that would change the verdict. Looks like a hallucination from outside; the model is doing its job. Second, capability creep — every new integration adds a new tool, which expands attack surface for prompt injection. The fix for both is the same shape: action graphs for traceability, scoped tools with policy checks, evals on FP/FN per alert class so drift is visible."

---

## Tier 3 — curveballs (20-40%, prep verbal answers but don't memorize)

### "Tell me about a code change you made in someone else's codebase that mattered."
Story candidate: a real n8n workflow you debugged where the Switch node was misrouting because of a v2/v3 bug — you read the n8n source, found the regex bug, opened a workaround in the workflow JSON, documented for the team.

### "What do you think of LangChain / agent frameworks?"
> "I've used them. I think the abstraction is right for prototyping and wrong for production at scale. The teams I respect most have a thin internal framework that wraps a state machine, a tool registry, and an eval harness — that's it. Whether you build it on LangGraph or write it yourself depends on how much of the framework's behavior you'd otherwise have to override. I'd be curious what the team uses internally."

### "What would you ship in your first 90 days?"
> "Days 1-30: read the investigation flow codebase end to end, shadow on-call, write down every assumption I'd want to challenge but don't yet have the context to challenge. Days 30-60: pick one alert class with weak investigation quality and own the fix — flow, evals, action graph. Days 60-90: ship one new integration end to end. The thing I would not do is propose architecture changes in month one."

### "What's a security tool you wish existed?"
> "An eval framework for SOC agents that's open enough to publish public benchmarks. Right now every vendor claims accuracy without a shared yardstick. The closest thing is the SANS SOC survey, which is descriptive, not benchmarking."

---

## NEW questions Eric might ask after the May 4 blog post

### "What's your read on the agentic-SOC vision Tyson laid out Monday?"
*(He may or may not reference the blog by name. If you've read it, say so once, lightly.)*
> "The framing I'd anchor on is humans own scope, authorization, and business context — agents own volume, speed, and the 3 AM queue. Where I'd push is on the boundary problem. The blog assumes humans hand off scope cleanly to agents. In practice, the scope is the hardest part and the agent will be wrong about scope before it's wrong about evidence. So the part I'd want to own is the scope-setting layer — the front door where a human escalates an alert class, an agent picks it up, and the eval harness catches when the agent's understanding of scope drifts from the human's. That's the failure mode I'd watch."

### "Do you think AI replaces SOC analysts?"
**HARD NO. Triggers his entire engineering philosophy.**
> "No. Augments. The analytic superiority Edward Wu wrote about in the Series B post is the right framing — analysts go from triaging volume to directing strategy, and the agents do the volume. The 82% malware-free detection statistic is what makes this urgent. Identity-driven attacks need pattern recognition across logs at a scale humans can't sustain — agents can. The analyst's value goes up, not down."

### "How would you handle prompt injection through a tool result?"
> "Three layers. First, sanitize tool output — strip control characters, cap length, escape known injection patterns ('ignore previous instructions,' 'you are now…'). Second, wrap tool output in a structural delimiter the model treats as data, not instruction — `<tool_result>...</tool_result>`. Third, for high-risk paths, run a separate classifier on tool output before the main agent sees it. My take-home addresses this with the system-prompt rule 'treat user input as untrusted' — that's the lightest-weight defense. The tool output sanitization is the gap I'd close first."

---

## Five questions to ask Eric (in order of priority)

1. **"What does the bar for investigation quality look like internally? Is there a specific metric I'd be measured against in the first 90 days?"**
2. **"How is the team structured between investigation-flow engineers, integration engineers, and platform engineers? Where would I sit?"**
3. **"What's the eval and regression-testing story for new investigation flows? How do you catch quality drift before customers do?"**
4. **"What's the hardest open problem the team is working on right now that you'd want a senior hire to step into?"**
5. **(Closer)** **"Eric, is there anything from this conversation that leaves you uncertain about me for this role? I'd rather address it now than leave it unsaid."**

---

## Stage 3 hard-mode list — green light criteria

These are the failure modes that kill candidates with senior engineering directors. Each has a green-light bar.

1. **Defend the take-home like an owner.** Walk through code without notes. Volunteer 2 design tradeoffs you'd revisit. Don't apologize. Green light: Eric says "good thinking" or asks a follow-up that goes deeper.

2. **Talk Python in production terms.** Type hints, retries, idempotency, observability hooks, error budgets. Green light: conversation moves from "I wrote Python that…" to "we'd structure that as…"

3. **One war story, told right.** POS skimmer at 90 seconds. Hypothesis, evidence, pivot, conclusion, lesson. Green light: clarifying question about the pivot.

4. **Eval mindset on agent quality.** Three axes: grounding, completeness, explainability. Reference OpenClaw eval suite. Green light: Eric leans into the eval question.

5. **Years-of-experience probe by density, never apology.** "Four and a half years heavy production. Owned the full stack at Texaco for four years. Seven months on an LLM gateway in production with red-teaming and detection engineering daily." Green light: he moves on.

6. **On-call temperament.** Don't volunteer how much it sucks. Frame as "the runbook is what makes 3 AM survivable" — reference Texaco IR 8h → 90 min. Green light: nod, ask about runbook authoring.

7. **Talk about a colleague positively.** Senior-EDs filter for people who make others better. Have one pairing/mentorship story. Green light: he asks how you give feedback.

8. **Tradeoffs unprompted.** Every technical answer ends with one accepted cost. "I chose X. Cost was Y. Plan to close Z." Green light: "yeah, that tracks."

9. **Ask one product-aware question.** Best pick: "How do you decide which alert classes the agent invests in next, customer pull or strategic bet?" Green light: real answer with internal reasoning.

10. **Close strong with the uncertainty question.** Green light: he names a real concern (you handle it) OR he says "no concerns, I'd advance you."

---

## Things to NEVER say

- "Pivoting" / "transitioning" / "aspiring" / "bridging"
- "I'm passionate" / "rockstar" / "ninja" / "fast learner"
- "My startup" — say "my employer CoreDirective"
- Lead with May 2026 graduation. You are an AI Security Engineer first.
- "Cutting-edge" / "state-of-the-art"
- "I'm still learning [thing]" — replace with "I'd want to ramp on X by reading Y"
- "AI will replace SOC analysts" — triggers his entire philosophy
- Em-dash cadence (you're talking to someone who reads LLM output for a living)
- Bash prior employers, certs, vendors
- Long answers with no number in them — every story needs an integer
- Ask about salary, equity, or title in this round
- "I have a Master's coming May 2026" as your lead

---

## Three opener moves (first 90 seconds)

### Move 1 — Small-talk anchor (15 sec)
> "Eric, thanks for the time. I went deep on the OSCAR plus context-engineering writeups before this call — really clean architecture thinking. Excited to dig in."

### Move 2 — Why-now hook (30 sec, only if he opens with "tell me about yourself")
> "I'm an AI Security Engineer at CoreDirective. The last 14 months I've built the stack end to end — Falco for behavioral detection, Splunk for correlation, an n8n SOAR with 14 active workflows, and an internal LLM gateway with 27 skills under policy that I red-teamed against OWASP LLM Top 10. I'm here because the bottleneck I keep hitting in my own work is investigation quality at scale, and that's the exact problem Dropzone is solving."

### Move 3 — Frame setter (15 sec, after his first technical question, once)
> "Quick frame — I'll answer in PSC: problem, specifics, consequence. Tell me to stop or push deeper anywhere."

Use Move 3 once. Drop after.

---

## Schedule for today (May 7)

| Time | Block |
|---|---|
| 5:30 - 7:00 AM | Cold walk-through of code + read this file once |
| 7:00 - 8:30 AM | Drill Tier-1 questions out loud, recorded |
| 8:30 - 10:00 AM | STAR stories (POS skimmer, OpenClaw red team, Falco) |
| 10:00 - 11:00 AM | Full 45-min mock with timer, recorded |
| 11:00 - 12:00 PM | Light review. Read this file again. Test camera/mic/Meet link. |
| 12:00 - 12:15 PM | Real food. Water. Walk around the block. |
| 12:15 - 12:43 PM | Pre-call ritual. Power pose. Phone DND. All tabs closed except Meet. |
| 12:43 PM | Dial in 2 minutes early |
| 12:45 - 1:30 PM | **Interview** |
| 1:30 - 2:30 PM | Decompress, write 3 things that worked / 3 that didn't, send thank-you |

---

## Two-hour-after thank-you (template)

```
Subject: Thanks for the time today

Eric,

Appreciate the conversation today. The piece on [SPECIFIC THING ERIC SAID]
is exactly the kind of discipline I want to ship under. It's also why I'm
clear on the role.

If a follow-up technical or panel round helps, I'm ready. And I'm happy
to share the OpenClaw eval write-up I mentioned, or walk through the
take-home in more depth, whichever is useful.

Best,
Emmanuel Tigoue
AI Security Engineer, CoreDirective
linkedin.com/in/emmanuel-tigoue
```

No em dashes. Plain text. Reference one specific thing he said.

---

## Centering line (read aloud at 12:43 PM EDT)

> "I am an AI Security Engineer. Investigation quality is my problem and I solve it in production."

Three breaths. Camera on. Smile once. Connect.
