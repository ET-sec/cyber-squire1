# Dropzone Remaining Rounds Prep

Stage 3 with Eric Hammerle is done (May 7 to 8). Three rounds left.

1. Code interview (1 hour)
2. Deep security interview (1 hour)
3. AWS defense, which is the take-home walkthrough

This file is the focused prep for those three. Existing files in this folder you should reuse, not duplicate: `03_TECHNICAL_PREP.md`, `10_TECHNICAL_ROUND_GAMEPLAN.md`, `11_TAKE_HOME_DEFENSE.md`, `13_CAMPBELLTON_DRILL.md`.

---

## Round 1: Code Interview (1 hour Python)

### Most likely question types

Based on `00-market-truth/REAL-CODE-QUESTIONS-2026.md` and the Dropzone product (AI SOC analyst on top of LangChain agents):

1. Streaming log parsing with top-N. Read a multi-GB log as an iterator, return top-N source IPs or events. Use `collections.Counter` plus a heap. Handle malformed lines and rotation.
2. JSON event triage. Take a list of CloudTrail or generic security events, filter by criteria, group by field, return summary.
3. Build a small LangChain or LangGraph agent. State schema, tool node, conditional edge, simple persistence.
4. Regex on log lines. Extract structured fields, validate format, count anomalies.
5. Concurrent or async log fetcher. Use `asyncio` to fetch multiple endpoints, aggregate results.

### What to study tonight

In order, in 90 minute blocks:

1. `intensive-prep/01-code-fluency/CHEATSHEET.md`. Read once. Copy any pattern you do not recognize into Anki or a sticky note.
2. `intensive-prep/01-code-fluency/INTERVIEW-Qs.md`. Walk the 30 questions. Solve 5 by typing. Read solutions on the rest.
3. `intensive-prep/01-code-fluency/labs/day14_langgraph_security_agent.py`. Read it line by line. Then close it and rebuild the state schema and the conditional edge from memory.
4. Build the missing streaming top-N lab. Suggested filename: `01-code-fluency/labs/day_streaming_topN.py`. Counter approach, heap variant, malformed line handling, basic test.

### What to drill verbally

Memorize the 3 phrases that signal senior:

- "Let me clarify the input shape before I write anything." (ask about file size, encoding, malformed lines, rotation, concurrency)
- "I will start with the simplest version that runs and add edge cases as you push back."
- "I would unit test this by feeding it three lines: a normal one, a malformed one, and an empty file."

### Common traps

- Diving into code before clarifying requirements. Always ask 2 to 3 clarifying questions first.
- Premature optimization. Get correctness first. Talk about scale after.
- Not testing. Even if you do not write the test, name what you would test.
- Silence while thinking. Narrate. "I am thinking about whether this fits in memory, and if not what windowing would look like."
- Forgetting to handle the empty case and the malformed case.

### If you go blank

Stall with the clarifier. "Before I commit to an approach, what is the rough size of the input." That buys you 30 seconds and shows you think first.

---

## Round 2: Deep Security Interview (1 hour)

### Most likely question types

Based on `00-market-truth/REAL-AI-SECURITY-Qs-2026.md` and the Dropzone product (investigation quality on AI SOC analyst):

1. Walk me through OWASP LLM Top 10. Use the 2025 list. Lead with LLM01 prompt injection, LLM06 excessive agency, LLM02 sensitive info disclosure, LLM05 improper output handling.
2. How would you detect prompt injection at the gateway. Layered defense. Pre-filter for known patterns, then output validation, then tool call inspection, then anomaly detection on the audit log. Cite OpenClaw as your real implementation.
3. Threat model an AI SOC analyst. STRIDE plus ATLAS. Trust boundaries. Top threats. Mitigations. Residual risk.
4. Tell me about a vuln you found. Use the Falco tuning story or the Switch v3 bug story or the OpenClaw red team. Concrete, recent, with a fix.
5. Capital One kill chain. Walk through SSRF to IMDSv1 to role credentials to S3 exfil. Name the fixes at every layer.
6. How does your AI SOC analyst differ from a SIEM. SIEM correlates. AI SOC analyst investigates. SIEM gives you alerts, AI SOC analyst gives you triage decisions with evidence.
7. What is MITRE ATLAS, how does it differ from ATT&CK. ATLAS is the AI/ML version. AML.T0051 prompt injection, AML.T0048 external harms, AML.T0024 inference exfil. Name 3 to 5 IDs cold.
8. How do you reduce alert fatigue. Tuning, suppression, asset enrichment, severity scoring. Your Falco story is the proof.
9. Indirect prompt injection in RAG. The Greshake et al pattern. Hostile content ingested by retrieval, then acted on by the agent. Defenses: provenance tags on retrieved chunks, output validation, tool allowlist, human in the loop on high-risk actions.
10. What did you build in your stack to defend against this. Use OpenClaw, n8n SOAR, Vault, Keycloak, Falco. Be specific about the control, not the buzzword.

### What to study tonight

1. `intensive-prep/03-llm-ai-security/CHEATSHEET.md`. Read twice.
2. `intensive-prep/03-llm-ai-security/INTERVIEW-Qs.md`. Walk the 35 questions. Read each answer out loud once.
3. `intensive-prep/03-llm-ai-security/THREAT-MODELS.md`. Read the SOC triage agent threat model. Memorize the top 5 threats and mitigations.
4. `intensive-prep/04-threat-modeling/PROCESS.md`. Memorize the 7-phase opener.
5. `intensive-prep/04-threat-modeling/HIS-STACK.md`. Read the threat model of your own stack. This is your second strongest asset after Story 13.
6. `intensive-prep/05-detection-triage/INTERVIEW-Qs.md`. Skim. Pull anything on TTP vs IOC and Pyramid of Pain.

### What to drill verbally

Three phrases that signal senior:

- The 7-phase opener for threat modeling (verbatim from `04-threat-modeling/PROCESS.md`).
- Prevent vs contain vs detect. "HITL is the prevent. JIT is the contain. Audit log is the detect. Three layers, three roles, no overlap."
- "I will end with residual risk explicitly because that is what differentiates a useful threat model from a checklist."

### Common traps

- Mixing OWASP LLM Top 10 numbers with the older 2023 list. Use the 2025 names: LLM01, LLM02, LLM05, LLM06, LLM10. The fix is in `intensive-prep/05-detection-triage/INTERVIEW-Qs.md`.
- Saying "Capital One settled with the FTC." It was the OCC. $80M civil money penalty 2020. $190M class action 2022. Federal Reserve consent order separate.
- Calling kubectl exec ATT&CK T1610. It is T1609. T1610 is Deploy Container.
- Naming Garak as something you have running. You do not. The audit caught this. If they ask about Garak, say "Promptfoo I run, Garak I plan to add."
- Naming Vault dynamic secrets as something you have. Vault is not initialized. Say "Vault is in the stack as a secrets store, dynamic secrets is a planned upgrade."
- OpenClaw version drift. It is `v2026.4.21`, not `v2026.3.8`.

### If you go blank on a question

The framework: clarify, frame, answer, residual.

- Clarify: ask one question to scope.
- Frame: name the framework you will use (STRIDE, OWASP LLM, ATLAS, MITRE ATT&CK).
- Answer: 60 to 90 seconds, structured.
- Residual: name what you did not solve and why that is acceptable for the threat model.

---

## Round 3: AWS Take-Home Defense

The take-home is at `dropzone-ai/code/takehome/`. AWS Q&A chatbot. LangChain agents. Two-tier model routing (Sonnet 4.6 default, Opus 4.7 escalation). Moto for AWS mocking. Tools wrapping boto3.

### Architecture decisions you must defend

Existing prep is at `11_TAKE_HOME_DEFENSE.md`. Re-read it. The questions Eric and the next interviewer are most likely to ask:

1. Why two-tier routing instead of one model. Sonnet for routine read calls, Opus for ambiguous questions or low-confidence retries. Cost savings, faster default path, fallback for hard cases.
2. Why LangChain agents instead of LangGraph. LangChain agents fit the simple ask-then-call pattern. LangGraph is better when you need state, branching, persistence, or human-in-the-loop. For this take-home, the simpler primitive was right. For a production AI SOC analyst, LangGraph would win.
3. Why Moto instead of a real AWS account. Reproducibility. No cost, no credentials, no risk. Reviewers can run the demo on a coffee shop wifi. Production would test against real AWS in a sandbox account, not Moto.
4. Tool design. Why each tool exists, why they return what they do, where you bounded the agent's authority.
5. Prompt injection defenses. What you did at the agent layer. What you would add at the gateway layer in production.
6. Cost analysis. Roughly $0.02 to $0.05 per run per the README. How that scales to 1000 questions per day, 10K, 100K.
7. Production deltas. What would change. Real AWS read-only role with permission boundary. CloudTrail logging. Per-user rate limit. Output redaction for sensitive fields. Audit log of every Q and A.
8. Security of the chatbot itself. What if a user asks it to delete a bucket. Tool allowlist, scope limited to read APIs, refuse on write intent.
9. AWS-specific knowledge they will probe. How to find public S3 buckets (BlockPublicAccess, bucket policy, ACL, presigned URLs). How to check IAM user permissions (managed plus inline plus group memberships). How EC2 metadata works (IMDSv2 hop limit, instance role).

### What to study tonight

1. Re-read `11_TAKE_HOME_DEFENSE.md`. If anything is stale, fix it now.
2. Re-read your own `code/takehome/README.md` and the comments in `agent.py`, `tools.py`, `moto_setup.py`. Be ready to explain every function in 20 seconds.
3. Run the demo end to end on your laptop. Confirm the 4 sample questions still work. Capture the actual output.
4. `intensive-prep/02-aws-security/INTERVIEW-Qs.md`. Walk Q1 through Q15 (IAM and S3). These are the AWS questions most likely paired with the take-home.
5. `intensive-prep/02-aws-security/CHEATSHEET.md`. Memorize the Capital One pattern and the IAM evaluation order.

### What to drill verbally

- The 60-second architecture summary. "I built an LLM agent that answers AWS account questions in plain English. Two-tier routing: Sonnet 4.6 default, Opus 4.7 escalation. Moto sandboxes AWS. LangChain agents wrap boto3 read tools. The agent is bounded to read APIs by tool allowlist, never write. The interesting design call was the fallback to Opus when confidence is low or Sonnet errors, which traded a small cost increase for a much higher answer quality on edge cases."
- The "what would I do differently in production" answer. Always have one ready.
- The "what is the threat model of this chatbot" answer. Walk it: prompt injection from the user, prompt injection from data the chatbot retrieves, tool abuse, sensitive data leak in answers, cost bomb. Each gets a defense.

### Common traps

- Defending every choice as if you would never change it. Senior signal is "for this scope I made these choices, here is what I would change at production scale."
- Saying "LangGraph would have been better" without being able to articulate why. Know when each fits.
- Not knowing your own code. Open it tonight, walk through it line by line.
- Promising what you did not build. If they ask "is there a streaming variant," say "no, this version returns the full answer at once. Streaming would be a 30 minute add."
- Letting a question about AWS pull you off the take-home. Bridge back. "In this take-home I bounded the answer to read APIs. The same pattern in your product would extend to detection rules and SOC playbooks."

### If you go blank

The framework: scope, choice, tradeoff, evolution.

- Scope: what you bounded the work to.
- Choice: what you picked.
- Tradeoff: why, with the cost of the alternative.
- Evolution: what would change at production scale.

---

## Combined Drilling Schedule

If all three rounds are within 7 days, this is the order:

### Tonight (3 hours max)

1. `13_CAMPBELLTON_DRILL.md` 90-second script x 5 reads. Time it.
2. `intensive-prep/03-llm-ai-security/CHEATSHEET.md` x 2 reads.
3. `intensive-prep/04-threat-modeling/PROCESS.md` 7-phase opener x 5 reads out loud.
4. Open `code/takehome/agent.py` and `tools.py`. Read line by line.

### Tomorrow morning (90 min)

1. `intensive-prep/01-code-fluency/INTERVIEW-Qs.md` walk 10 questions. Solve 3 by typing.
2. Build the streaming top-N lab if you have not. 60 minutes.
3. Run the take-home demo end to end. 15 minutes.

### Tomorrow afternoon (90 min)

1. `intensive-prep/03-llm-ai-security/INTERVIEW-Qs.md` walk 10 questions, read answers out loud.
2. `intensive-prep/04-threat-modeling/HIS-STACK.md` read once.

### Tomorrow night (60 min)

1. Mock interview yourself. Pick one threat-modeling drill from `intensive-prep/04-threat-modeling/drills/`. Talk through it on a whiteboard or paper. Time it at 30 minutes.
2. Then do one Python coding question untimed.

### Day before any round

1. One 90-second script pass on Story 13 Campbellton.
2. One read of the relevant Round prep section above.
3. Stop by 9 PM. Sleep above 7 hours.

---

## What Not To Do

- Do not study every gap before the round fires. Study what maps to the round.
- Do not memorize. Drill the structure. Names of frameworks, sequence of steps, key numbers. The words come from your own voice, not from a script.
- Do not pretend on tooling you have not run. If asked about Garak, say "I have Promptfoo running, Garak is the next add." Honest beats canned.
- Do not skip sleep the night before. The cognitive cost is bigger than any extra hour of cram.
- Do not over-rehearse the day of. One pass on the prep, then walk away.
