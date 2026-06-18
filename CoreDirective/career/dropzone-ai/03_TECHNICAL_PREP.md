# Dropzone AI — Technical Deep Dive Prep

**Role:** Senior Security Engineer
**Stage 1:** Recruiter screen with Shaleena Reyersbach (ex Bugcrowd, ex Cobalt). She knows the security space. She will spot faked depth.
**Stages 2+:** Engineering rounds. This doc hardens both.

---

## Section 1: Dropzone's Technical Architecture (Your Mental Model)

When a Dropzone investigation fires, the path from raw alert to auditable verdict runs through a disciplined agentic loop. Here is how I picture the end to end flow.

A customer SIEM, EDR, or identity platform emits an alert over a webhook or a polled connector. The ingestion layer normalizes the payload against a common schema. That schema has to absorb vendor variance like `src_ip` in Splunk CIM versus `sourceAddress` in ArcSight CEF versus `srcip` in Palo Alto logs. Field translation is a first class concern because a wrong mapping silently breaks every downstream inference. The normalized alert drops into an investigation context with tenant, asset, user, and network metadata attached, plus a correlation key so the agent can deduplicate follow on signals.

From there the agent runs OSCAR inside a ReAct loop. Observe pulls the alert and frames the hypothesis. Size up queries the customer environment for ground truth. Collect and corroborate is where tool use happens. The LLM calls typed tools with strict JSON Schema arguments, and each tool returns grounded evidence from Splunk, Sentinel, CrowdStrike, Okta, or a cloud audit log. This is classic function calling with RAG overlayed. The RAG side is not just document retrieval. It indexes vendor query syntax, field dictionaries, tenant specific integration docs, and prior investigation notes so the model does not invent column names.

The agent reasons step by step. Each reasoning step is logged. Each tool call, parameters, and response is logged. That log is the audit trail. A human can rerun any query verbatim and confirm the evidence. This is why Dropzone says investigations not pipelines. A pipeline hides logic. An investigation exposes it.

Guardrails sit around the loop. Tool allowlists prevent excessive agency. Output schemas force structured verdicts, severity, confidence, IOCs, and recommended actions. Input sanitization strips prompt injection payloads embedded in log content. Grounding checks require every factual claim to map to a tool response with a cited row. A confidence threshold gates auto close. Low confidence gets escalated to a human analyst. Token budgets cap context window blowout on long running investigations, and summarization compresses intermediate state without losing evidence pointers.

Finally the report renders in a stable template. Customer dashboards parse those fields, so any drift breaks ingestion downstream. The whole loop is instrumented with latency, cost per investigation, tool error rate, and a continuous eval harness comparing agent verdicts to a golden set of labeled historical alerts.

---

## Section 2: Investigation Quality — Operational Definition

"Investigation quality" is not vibes. It is a measurable property built from accuracy, grounding, completeness, latency, cost, and format stability. The ten failure modes below map to concrete tests and fixes.

| # | Failure Mode | Test | Fix |
|---|--------------|------|-----|
| 1 | Hallucinated IOC. Agent claims an IP or hash is malicious with no source. | Grounding test. Every factual assertion must cite a tool response ID. Run an automated extractor that flags claims without citations. | Citation requirement in the output schema. Post generation grounding check that rejects the verdict if any IOC has no source. Retrieval guardrail that blocks tool free conclusions. |
| 2 | Premature conclusion. Verdict before evidence complete. | Minimum evidence rule per alert class. For phishing, require at least URL reputation, sender reputation, and user click telemetry. | Checklist gating in the prompt plus a programmatic pre-verdict validator. Refuse to emit a verdict if required evidence slots are empty. |
| 3 | Missed pivot. SIEM fired but no EDR check. | Alert class to required pivot map. For endpoint alerts, EDR process tree is mandatory. Eval flags any investigation that skipped a required pivot. | Explicit tool call graph per alert class. The agent cannot write a verdict until the required tools fire. Treat the graph as code, version it, review it. |
| 4 | Field mapping error. Agent queries `src_ip` when customer's index uses `client_ip`. | Per tenant integration test that probes every expected field against a synthetic query. Alert on schema drift. | Tenant specific field dictionary in the RAG index, pinned at query build time. Fail closed if a field resolves to null across more than one alert. |
| 5 | Base rate fallacy. Benign but unusual flagged as malicious. | Eval dataset that includes rare but benign patterns. Track false positive rate per alert class. | Prior probability context injected into the prompt. Tune the threshold. Add a "rare but explained" verdict class. |
| 6 | Overconfident benign verdict that hides an APT. | Red team eval with known APT traces seeded in the dataset. Track recall on malicious. | Dual model pass with an adversarial prompt on high confidence benign verdicts. Force a second look with "what would an attacker hide here." |
| 7 | Tool misuse. Wrong SPL for a customer's custom index. | Per tenant synthetic queries run in CI. Validate return shape and row count sanity. | Tool schemas scoped per tenant. Query templates parameterized. Lint SPL or KQL before execution, reject on syntax errors. |
| 8 | Context window blowout on long investigations. | Token length tracker with a hard ceiling. Flag investigations that exceed a threshold. | Incremental summarization with evidence pointer preservation. Move old tool outputs to an evidence store, replace with a reference. |
| 9 | Regression on edge case alerts after prompt or model update. | Regression eval suite of 500+ labeled historical investigations run on every change. Gate merges on delta. | Canary release. Shadow mode new prompt for a week. Diff verdicts against prod. Promote only on green metrics. |
| 10 | Report format drift that breaks customer dashboards. | Schema validator at the boundary. JSON Schema check on every report. | Structured output enforcement via function calling. Never let the model free form the final payload. Contract test the shape. |

---

## Section 3: 30 Technical Q&A

### Python

**1. How do you structure a production Python codebase for a multi-tenant agent platform?**
I lean on dataclasses or Pydantic models for every boundary. Models for inbound alerts, for tool schemas, for verdicts. Pure functions where possible, dependency injection for the I/O layer so tests can swap in fakes. Config via Pydantic Settings reading env vars. Package layout separates `core` (orchestration), `tools` (integrations), `models` (schemas), `evals`. I keep agent logic free of vendor SDK leakage, which lets me mock every external call in tests.

**2. Pydantic v2 vs dataclasses — when do you pick which?**
Dataclasses are free. I use them for internal pure data that stays inside one process. Pydantic I reach for at boundaries. Anything that parses JSON from an LLM, an HTTP payload, or a webhook goes through Pydantic because I want validation, coercion, and clear error messages. For LLM tool call arguments I always validate with Pydantic before executing a tool. The schema doubles as the function calling definition.

**3. How do you handle retries and idempotency in a SOAR workflow?**
Every outbound call gets a retry policy with exponential backoff and jitter. I use `tenacity` when I want declarative retries or hand roll it for surgical control. Idempotency comes from stable keys. Every ServiceNow ticket creation goes through an idempotency key derived from the alert correlation ID so a retry cannot duplicate. I log the key and the result in Postgres, so a replay is a lookup, not a new side effect.

**4. Async versus threads for integration I/O?**
For fan out to 10 or 20 vendor APIs per investigation, `asyncio` with `httpx.AsyncClient` is the right shape. One event loop, bounded concurrency with a semaphore, per tenant rate limit buckets. Threads I use for SDKs that are sync only and CPU light. I avoid mixing unless I am wrapping a sync SDK with `asyncio.to_thread`. For truly CPU bound work, multiprocessing or a worker queue.

**5. Rate limiting across 90+ integrations — how?**
A token bucket per tenant per integration. Redis backed for coordination across workers. Each tool call acquires a token before executing, blocks or fails based on policy. I add jitter to avoid thundering herds. On 429, back off and respect `Retry-After`. Metrics on bucket drain rate tell me which integrations need higher paid tiers.

**6. Pagination patterns you actually use?**
Cursor based is ideal when vendors offer it, which most modern APIs do. Offset pagination is a trap on large sets because of drift. For Splunk I stream search results. For Microsoft Graph I chase `@odata.nextLink`. For Okta I follow `link: next`. I abstract all of this behind a `paginate(fetch_page, extract_cursor)` helper that returns an async generator so the investigation code consumes one unified stream.

**7. How do you test a function that wraps a vendor SDK?**
Never hit the real API in unit tests. I wrap every SDK call in a thin port. Tests inject a fake port returning fixture payloads captured from real responses. I use `pytest` parametrize to cover success, 429, 500, partial data, and malformed JSON. Integration tests run against sandboxed vendor accounts on a cron, not on every commit.

**8. Logging and observability for an agent?**
Structured JSON logs, one event per step. Correlation ID is the investigation ID. Every log line carries tenant, alert class, step name, tool name, token counts, latency. Ship to Datadog. Traces with OpenTelemetry span the agent loop, with each tool call as a child span. That single change lets you spot where investigations stall or balloon in cost.

**9. How do you version tool schemas?**
The schema is code. Semantic versioning. Backward compatible additions go in as new optional fields. Breaking changes get a new tool name and a deprecation window. I run a compatibility eval on every schema change to confirm older prompts still resolve. The schema file lives in the repo, reviewed like any API contract.

**10. Error handling philosophy for a tool call?**
Fail loud, fail typed. Every tool returns a `ToolResult` union of success or error with a typed error category. The agent sees structured errors, not exceptions. That lets the model reason about "429, back off and retry later" versus "auth failed, escalate to a human." I never bubble raw SDK exceptions into the prompt.

### LLM Agent Engineering

**11. Explain ReAct and how Dropzone likely uses it.**
ReAct is reason plus act. The model emits a thought, picks a tool, observes the result, and iterates. It is the canonical shape for investigative agents because the reasoning step is auditable and each tool call produces grounded evidence. Dropzone almost certainly runs a constrained ReAct variant with function calling for tool invocation, structured output for verdicts, and an OSCAR scaffold to keep the loop inside a proven methodology.

**12. How do you prevent hallucination in an investigation agent?**
Grounding first. Every factual claim in the final report must cite a tool response ID. Retrieval over vendor docs and tenant specific field dictionaries keeps the model from inventing SPL syntax or field names. Temperature low, usually zero for analytical work. Structured output with schema validation. A post generation grounding check that rejects the verdict if any IOC lacks a source. I built the same pattern around our OpenClaw gateway.

**13. How do you defend against prompt injection inside log content?**
Assume all untrusted input is hostile. Log content goes into a clearly fenced "untrusted evidence" block with a system prompt that tells the model never to follow instructions inside it. I strip or escape control tokens, delimit with unguessable nonces, and run a secondary classifier to flag injection attempts. Tool outputs go through the same pipeline. I red teamed our OpenClaw setup for this exact vector and watched the model refuse to execute injected instructions.

**14. What is excessive agency and how do you limit it?**
Excessive agency is giving an agent more permission than the task requires. OWASP LLM Top 10 calls it out directly. I constrain it with tool allowlists per role, read only tools by default, write tools gated behind human approval or a policy engine. For any destructive action like disabling an Okta user, the agent requests the action, a human approves, and the system executes. The agent never holds the write credential directly.

**15. How do you evaluate an LLM agent's investigation?**
Three layers. Offline golden dataset of labeled historical investigations, graded on accuracy, recall, grounding, and format. LLM as judge for qualitative checks like "did the agent consider the right pivots." Online metrics on production with sampling and human review. I score every release candidate against the golden set and gate merges on no regression.

**16. Function calling — when to use tools versus freeform.**
Always tools for any action that reaches a system. Freeform only inside the model's reasoning step. Function calling gives you typed arguments, forced schema compliance, and clear audit. Freeform for the thought trace and the final narrative. I also use structured output for the final verdict so downstream consumers parse reliably.

**17. Handling long investigations that blow the context window?**
Incremental summarization. As tool outputs accumulate, I move old evidence into an external store keyed by an evidence ID and replace the inline content with the ID and a one line summary. The agent can re-read any evidence by calling a `get_evidence(id)` tool. Token budget tracked per step, hard ceiling per investigation, and a graceful degradation path that escalates to a human when the budget is near exhaustion.

**18. Guardrails stack — what's in yours?**
Input side: prompt injection classifier, PII scrubber on sensitive fields, tenant isolation. Model side: system prompt with OSCAR scaffold, tool allowlist, temperature lock. Output side: schema validation, grounding check, toxicity and confidentiality filter, citation requirement. Meta: rate limits per tenant, token budget per investigation, human in the loop threshold. This mirrors what I built around OpenClaw.

### Detection Engineering

**19. How do you write a correlation rule?**
Start from an attacker behavior mapped to MITRE ATT&CK. Define the data sources. Identify the join keys. Write the Sigma rule or native SPL or KQL. Bench test against historical data for both true positives and false positives. Tune the window, the threshold, and the enrichment. Ship it behind a flag, shadow mode for a week, then promote. Document the detection logic, the expected alert rate, and the recommended investigation playbook.

**20. Splunk CIM — why does it matter here?**
CIM normalizes fields across sources. `src_ip`, `dest_ip`, `user`, `action`. Writing against CIM means one detection can cover fifteen log sources. For an AI SOC analyst this is load bearing. Without normalization the agent has to learn every vendor's field names from scratch. With CIM, the agent queries once and the customer gets coverage across their whole stack. Dropzone's field translation layer is solving the same problem for environments that did not normalize upstream.

**21. What is Sigma and why care?**
Sigma is a YAML based, vendor neutral detection format. Write once, translate to SPL, KQL, ES QL, or whatever the target is. Great for portability across customers. For an AI SOC platform, Sigma plus a translator lets the agent reason about detection logic at a layer above any one SIEM. I would push every net new detection through Sigma first and let the backend compile per tenant.

**22. False positive tuning — your method?**
Measure first, tune second. Baseline the alert rate per rule over two weeks. Group by asset, user, and time to find the noise sources. Add exclusions for known benign patterns, not for specific hosts. Raise thresholds only when the data says the signal is drowning in noise. I took our Falco eBPF alerts from 200 a day to 12 by adding asset aware exclusions and tuning thresholds around real baselines.

**23. Detection as code — what does that look like?**
Detections live in git. Every rule is a YAML or Sigma file with metadata, MITRE mapping, data sources, and test fixtures. PRs run a linter, a schema check, and a backtest against historical data. Merged changes deploy via CI to the SIEM or detection engine. Version control gives you rollback, peer review, and an audit trail. I run this pattern for our OPA policies and it is the right shape for detections.

### Investigation Methodology

**24. Phishing alert lands. Walk me through it.**
Observe the alert: sender, recipient, URL, timestamp, mail gateway verdict. Size up: check URL reputation across VirusTotal, Cisco Talos, and internal threat intel. Pull sender domain age and SPF, DKIM, DMARC. Collect: did the user click, via proxy logs or EDR. Did they submit credentials, via identity provider auth logs. Corroborate with any lateral attempts from the user in the next hour. Analyze: if clicked and credentialed, treat as compromise, disable the account, force reauth, isolate the endpoint. Report: verdict, evidence citations, recommended actions. Close as malicious only with evidence. Benign only after ruling out each pivot.

**25. When do you escalate versus close as benign?**
Confidence threshold and blast radius. High confidence benign with full evidence and no missed pivots, auto close. Low confidence, escalate. Any signal touching a privileged account, a crown jewel asset, or an outside tenant boundary, escalate regardless of confidence. Novel patterns not in the eval set, escalate and flag for dataset inclusion. The rule is when in doubt, hand to a human and capture the decision as training data.

**26. How do you pivot from a SIEM alert to EDR and identity?**
SIEM tells you something happened. EDR tells you what process did it. Identity tells you who authorized it. A network connection alert in the SIEM pivots to EDR on the source host for the process tree, then to the identity provider for the user's recent auth events and MFA posture. Each pivot is a tool call with a clear join key — IP, host, user. The agent's tool call graph encodes these mandatory pivots per alert class.

### Threat Hunting

**27. How do you run hypothesis driven threat hunting?**
Start with a hypothesis tied to a MITRE technique the team has not actively hunted. Example, T1078 valid accounts via service principal abuse in Azure. Define the data sources, write the query, run it in a Jupyter notebook with pandas for aggregation. Look for outliers, enrich with threat intel, confirm or reject. If confirmed, turn it into a detection. If rejected, document the coverage claim. The output is either a new rule or a signed statement that the technique is covered.

**28. MITRE ATT&CK chaining — how does an agent benefit?**
Attackers rarely stop at one technique. A phishing T1566 leads to execution T1059, credential access T1555, lateral movement T1021. An agent that knows the chain can proactively look for the next step after detecting the first. That turns a single alert into a full campaign investigation. I would encode common chains as playbooks the agent consults during the Collect phase of OSCAR.

### SOAR and Orchestration

**29. When a playbook breaks at 3am, what's your first move?**
Stop the bleeding. Flip the playbook off for the affected integrations. Check the last 15 minute error rate by tool and by tenant. Look at the diff since the last green run. Ninety percent of 3am breaks are a vendor schema change, an expired token, or a rate limit. Reproduce against a staging tenant with a captured payload. Ship a narrow fix behind a flag, verify on one tenant, roll forward. Write the postmortem the next morning, not at 3am.

**30. Feature flags and canary rollouts for investigation logic?**
Every change goes behind a flag. Two dials per flag: tenant allowlist and rollout percentage. Canary a new prompt or a new detection on internal tenants first, then 1 percent, 5 percent, 25 percent, 100 percent. Compare eval metrics and production metrics against control at each step. If the delta exceeds a threshold on accuracy, latency, or cost, auto pause. This is how you evolve a shared platform without breaking customers.

---

## Section 4: 10 Scenario Walkthroughs

### S1. Add a new alert class to the investigation pipeline.

First I define the alert class with stakeholders. What does a "cloud IAM privilege escalation" alert look like across AWS, Azure, and GCP. What fields are required. What verdict options are valid. I build a canonical schema and a field translation map per source. Next, the investigation logic. I write the required tool call graph — identity logs, CloudTrail or Azure Activity, role assumption history, MFA posture, recent policy changes. I encode this as an OSCAR scaffold for that class. I assemble a golden dataset of 100 labeled historical examples across clouds, including hard negatives. I wire the class into the dispatcher behind a flag, shadow it for a week, compare to analyst verdicts. If grounding and accuracy clear the bar, canary to 1 percent of tenants, then widen. I document the class, its pivots, and its eval results. My n8n MASTER_ORCHESTRATOR_V1 with 16 services taught me the value of treating new action types as first class contracts, not stitched on.

### S2. Customer says our AI closed a real APT as benign. Investigate.

Pull the investigation. Read the full reasoning trace and tool call log. Three questions: did the agent have the evidence, did the agent see the evidence, did the agent reason correctly about it. If evidence was missing, it is an integration or schema gap. If evidence was present but not retrieved, it is a tool call graph gap. If evidence was retrieved but dismissed, it is a reasoning or prompt issue. I reproduce in shadow mode with the exact payload. I add the case to the regression set. Fix sequence depends on root cause. Evidence gap, fix the integration. Pivot gap, update the tool graph. Reasoning gap, adjust the prompt and add a dual pass adversarial check on high confidence benign verdicts in that alert class. Post fix, I replay the last 90 days of similar alerts to find any other misses, then tell the customer exactly what we found and what we changed.

### S3. Design an eval harness for investigation quality.

Datasets first. A golden set of 500 to 2000 labeled historical investigations, stratified by alert class, tenant type, and outcome. A red team set with seeded adversarial traces. A regression set that grows with every customer reported miss. Metrics: accuracy, recall on malicious, grounding rate, average pivot completeness, format validity, latency, cost per investigation. Runner: containerized, deterministic, replays each investigation with pinned model, prompt, and tool versions. Scoring: exact match where possible, LLM as judge for narrative quality with a calibrated rubric, human spot check on 5 percent. CI integration: every prompt or model change runs the harness, blocks merge on regression beyond a tolerance. Dashboard tracks metrics over time per alert class. This mirrors how I would run security regressions for a product pipeline and how I ran our Trivy, Semgrep, Gitleaks CI.

### S4. Teach an AI agent to query a customer's custom Splunk index.

Discovery first. Introspect the customer's Splunk for indexes, sourcetypes, and field extractions. Capture samples per sourcetype. Build a field dictionary that maps semantic fields — source IP, user, action — to the customer's actual field names. Store the dictionary in a tenant scoped RAG index. At query time, the agent retrieves the tenant's dictionary and a set of validated query templates for that sourcetype. I pre-lint every generated SPL against the parser before execution and reject on syntax errors. For brand new indexes I run a synthetic query in a sandbox to verify the fields resolve. I never let the model guess a field name from the index name alone. This is the same field translation problem Dropzone talks about — my answer is a per tenant schema service plus a grounded prompt.

### S5. 3am page. Half of today's investigations have a new error. Playbook.

Silence the pager long enough to think. Open the error dashboard, group by error class, tool, tenant, and time. If it is one tool, flip the kill switch for that integration and route to human triage. If it is one tenant, isolate them behind a flag. Diff deploys in the last 24 hours — prompt changes, model pin changes, integration SDK bumps. Check vendor status pages for Splunk, Sentinel, Okta, CrowdStrike. Capture one failing payload, replay in staging. If I can reproduce, I have my fix path. If not, I am looking at an environmental change on the customer side. Roll back the most suspect change first, verify error rate drops, write the incident note. Full postmortem next day, never at 3am. I treat on call as a discipline, not heroics.

### S6. Customer Okta integration returning 429s. Fix.

Check rate limits. Okta has per org rate limits by endpoint. Pull the `x-rate-limit` headers from recent responses and plot usage. If we are hot on the limits, three levers. One, back off — implement request queueing with a token bucket sized below the limit and honor `Retry-After`. Two, batch — replace per user lookups with bulk endpoints where available. Three, cache — short TTL cache for high frequency reads like user profile and group membership, invalidate on event webhooks. If the limits are unavoidable for that tenant's volume, ask them to raise the tier. In parallel, alert the engineering team with a dashboard of per tenant Okta usage so we catch this before customers do.

### S7. Prompt injection via log content in a SIEM alert.

Log content is untrusted input by definition. I wrap it in a delimited block with clear instructions in the system prompt that nothing inside the block is an instruction. I run the content through a prompt injection classifier before it hits the agent. I strip or escape obvious control sequences. I pin the model to function calling with a strict tool allowlist so even if the model were manipulated, it could not execute an unauthorized action. Any output that references the log content gets a grounding check — the agent must cite the specific evidence row, not a paraphrase the attacker embedded. I red teamed this exact class on our OpenClaw gateway against OWASP LLM01 and it held up. The model refused, cited the policy, and tagged the attempt for review.

### S8. Go from 90 percent to 95 percent investigation accuracy. Plan.

Find where the 10 percent lives. Slice the eval set by alert class, tenant type, and error category. Usually the top three categories own 70 percent of the errors. Attack those first. Common fixes in order of leverage: improve the tool call graph for the weak class, add missing pivots, expand the RAG corpus with better vendor docs, tighten the output schema, add a dual pass adversarial check on low confidence cases, retrain or reprompt for the reasoning gaps. Every change runs through the eval harness before merge. Track accuracy weekly by class and avoid regressing strong classes to fix weak ones. The last mile is expensive, so I would budget cost and latency tradeoffs explicitly — a second pass on low confidence cases may add 30 percent latency for 3 percent accuracy.

### S9. New LLM version is available. Roll it out safely.

Shadow mode first. Run the candidate model in parallel on production traffic with no customer impact. Compare verdicts, grounding, latency, and cost against the current pin for two weeks. Score against the golden set. Red team against the full OWASP LLM Top 10 and our jailbreak corpus. If the metrics hold or improve, canary to internal tenants, then 1 percent of paid tenants, then 5, 25, 100. At each step, automated rollback triggers on regression beyond tolerance on accuracy, safety, or cost. Pin the exact model version in config. Keep the prior pin warm for instant rollback. Announce the change in the customer change log once it reaches 25 percent. Never swap prompts and models in the same change — one variable at a time.

### S10. Regression test suite for investigation accuracy.

Layered. Layer one, a unit eval of 2000 historical labeled investigations covering every alert class at representative distribution. Runs on every PR, blocks merge on regression greater than tolerance per class. Layer two, a red team suite of 300 adversarial cases including prompt injection, jailbreak, APT hidden in benign patterns, novel TTPs. Runs on every prompt or model change. Layer three, a production shadow replay on the last 72 hours of real investigations comparing candidate output to production. Layer four, human review sampling on 2 percent of production verdicts per week, fed back into the golden set. Each layer has a dashboard and a clear owner. Results are versioned alongside the code. I would not accept "trust the vibes" at any layer.

---

## Section 5: Vocabulary Sheet — Sound Like An Insider

| Term | One-line definition |
|------|---------------------|
| Notable event | A Splunk ES term for a correlated alert created from one or more events that match a correlation search. |
| Correlation search | A scheduled search in Splunk or similar that joins across data sources and emits a notable when conditions match. |
| CIM | Splunk Common Information Model. A normalized schema with canonical field names like `src`, `dest`, `user`, `action`. |
| ReAct | Reason plus Act loop where an LLM interleaves thought steps and tool calls until it reaches a conclusion. |
| Tool use | General term for an LLM invoking external functions to fetch data or take action. |
| Function calling | The structured API where a model emits a JSON tool name and arguments validated against a schema. |
| Grounding | Requirement that model claims trace back to retrieved or tool returned evidence. |
| Hallucination | Model output that is fluent but not supported by evidence. |
| Eval harness | Automated system that scores model or agent output against a labeled dataset and metric suite. |
| Gold-standard set | Curated, expert labeled dataset used as ground truth for evaluation. |
| Golden dataset | Same as gold-standard set, the reference corpus eval runs score against. |
| LLM-as-judge | Using a strong model with a rubric to grade another model's output on qualitative criteria. |
| Prompt injection | Attack where untrusted input contains instructions meant to hijack the model's behavior. |
| Jailbreak | Technique to bypass a model's alignment or policy constraints. |
| Excessive agency | OWASP LLM Top 10 item for giving an agent more permission or autonomy than the task requires. |
| MITRE ATT&CK | Knowledge base of adversary tactics and techniques used to classify detections and behaviors. |
| MITRE ATLAS | ATT&CK for AI systems, cataloguing adversarial ML tactics and techniques. |
| OWASP LLM Top 10 | Industry list of top security risks for LLM applications, including injection and excessive agency. |
| RAG | Retrieval Augmented Generation, where the model is given retrieved documents as grounded context. |
| Guardrails | Input, model, and output controls that constrain agent behavior to a safe policy. |
| Constitutional AI | Anthropic method of aligning models using a written set of principles the model critiques itself against. |
| Chain of thought | Intermediate reasoning steps a model emits before answering, useful for auditability. |
| Agentic workflow | Multi step process where a model iteratively plans, acts, and observes toward a goal. |
| Multi-agent orchestration | Coordinating multiple specialized agents with distinct roles under a supervisor or planner. |
| Tool schema | JSON Schema definition of a tool's name, arguments, and return shape used by function calling. |
| Structured output | Model responses forced to conform to a schema, typically via JSON mode or function calling. |

---

## Quick Hooks for the Recruiter Screen

Shaleena was at Bugcrowd and Cobalt. Bug bounty and pentest world. She respects real hands on security work. Anchor points:

- "I red teamed our OpenClaw Claude Opus 4 gateway against OWASP LLM Top 10 and MITRE ATLAS."
- "Prompt injection, jailbreaks, excessive agency, data exfil — tested each one with evidence."
- "Splunk detection engineering took our MTTD from 48 hours to 4 hours."
- "Falco eBPF tuning took alert volume from 200 to 12 per day without losing coverage."
- "My n8n MASTER_ORCHESTRATOR_V1 integrates 16 services under one webhook contract."
- "I think in investigations, not pipelines. Every action I ship is auditable."

Keep it concrete. Numbers, tools, and the specific thing that went from noise to signal.
