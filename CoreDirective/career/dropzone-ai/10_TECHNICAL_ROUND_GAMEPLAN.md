# Dropzone AI — Technical Round Gameplan

**Interviewer:** Eric Hammerle, Director of Engineering
**Date/Time:** Thu 2026-05-07, 12:45 – 1:30 PM EDT (45 min)
**Format:** Google Meet 1:1 — meet.google.com/bbs-zevf-fmh
**Stage:** Round 2 of 4 (recruiter passed, take-home passed, this round, then panel + founder)
**Owner of this gameplan:** Emmanuel Tigoue
**Red thread (memorize):** *I care about investigation quality. I've done it as a human, I've built systems for it, and I want to ship it at scale to every SOC in the world.*

---

## 1. The 45-Minute Clock

| Block | Min | Cumulative | What's happening |
|---|---|---|---|
| Intro + rapport | 3 | 0:00 – 0:03 | Eric opens. Two sentences from him on Dropzone, two from you on background. Don't pitch yet. |
| Take-home walkthrough | 10 | 0:03 – 0:13 | Eric drives — reads code on his screen, asks "why this." You explain decisions, not lines. |
| Technical extension on the take-home | 15 | 0:13 – 0:28 | "If you had two more days, what would you add?" or "What breaks at 100 tools?" or "Add memory across turns." Live thinking. |
| Architecture / methodology deep dive | 10 | 0:28 – 0:38 | Investigation pipeline, eval harness, observability. Whiteboard or word-diagram. |
| Q&A from you | 7 | 0:38 – 0:45 | 3 sharp questions, ~2 min each. Closer in last 90 seconds. |

**Why this split.** Eric is Director of Engineering, not an HR screen. He has read the take-home. He is hiring for Investigation Quality on the AI SOC Analyst — that means most of his 45 minutes will probe (a) the code you submitted and (b) how you'd extend it. The 15-minute extension block is the load-bearing piece — that's where senior gets separated from mid. The 10-min architecture block lets you go up to system altitude on his terms, not yours. Q&A at the end, not throughout, so you don't burn his time with questions he was about to answer himself.

**Adjustments if Eric runs hot or cold:**
- If he opens with a "tell me about yourself" longer than 3 minutes — shrink the pitch to 30 seconds, hand the clock back fast.
- If he never pulls up the code — pull it up yourself at minute 4: "Want me to share my screen and walk the agent loop?"
- If he hits the architecture deep dive in the first 15 minutes — go with him. The clock is a guide, not a script.

---

## 2. First 90 Seconds

**Camera on. Headset on. Notebook visible but not in shot. Smile when his video appears.**

**Opener (verbatim):**
> "Eric, thanks for the time. I'm ready to drive into whatever you want to dig into — the take-home, architecture, investigation quality, whichever order works for you. I'll let you steer."

That's it. No pitch yet. He's the Director of Engineering, he's interviewed dozens of people, he knows the script. Handing him the wheel signals seniority. Most candidates immediately launch a pitch. Don't.

**Energy:** warm, not hot. Lean forward in the chair. Eyes on the camera lens, not the preview window. Voice a half-step lower than normal.

**Do:**
- Have the take-home repo open in a second window, ready to share-screen in two clicks
- Have a single index card with three numbers visible: 200→12 (Falco), 48hr→4hr (Splunk MTTD), 8hr→90min (POS containment)
- Have a glass of water within arm's reach, drunk to half
- Mute notifications, Slack, Telegram, calendar — everything

**Don't:**
- Pre-launch a pitch. He'll ask if he wants one.
- Apologize for anything (the room, the lighting, your dog, the connection). If something breaks, fix it in one sentence and move on.
- Open with "great to meet you, I've been a fan of Dropzone for…" — sounds like every candidate.
- Reference Edward Wu in the first 5 minutes unless Eric brings him up.
- Say "I'm pivoting into AI security" — you're already there. (Memory: feedback_no_pivoting_framing.)

---

## 3. The Pitch (60 seconds, on demand)

Eric has read the resume. Don't recite it. Build context for what he hasn't seen.

### Variant A — code-bias Eric (he opens with the take-home or asks about the architecture)

> "Quick context so the take-home makes sense. I run a 13-container production stack at CoreDirective — Postgres, n8n SOAR, Vault, Keycloak, Teleport, Falco, Datadog, and a Claude Opus 4.7 gateway I call OpenClaw. The whole thing is Python and Terraform, gated by OPA policies. The take-home was a small version of the same pattern — tools, structured prompts, a router, defense layers. The piece I leaned on most for it was the OpenClaw red team work — I attacked my own gateway against the OWASP LLM Top 10, so the threat model on the take-home wasn't theoretical. Happy to walk the code."

Word count: 110. Lands the production AI work, lands the red team experience, hands him the wheel.

### Variant B — leadership-bias Eric (he opens with "tell me about your background" or "walk me through your career")

> "Two things I want you to have before the technical depth. One, I've run the human side of investigation quality — at Texaco I owned IR across 3 PCI sites, drove containment on a POS skimmer from eight hours to ninety minutes using Wireshark and endpoint forensics, dropped Splunk MTTD from 48 hours to under four. Two, I've built the AI side — a 13-container stack with an autonomous agent gateway I red teamed against the OWASP LLM Top 10, and an n8n SOAR layer with a routed LLM triage path. Investigation quality on an AI SOC Analyst is the intersection of those two jobs. That's why I'm in this room."

Word count: 132. Lands the human-investigator credibility first (because Eric will weight that for a Director hire), then the AI engineering, then the role-fit close.

**In both variants:** stop talking when you finish the last word. Don't taper into "so… yeah, that's me." Just stop.

---

## 4. Three Architectural Soundbites

These are pre-built, memorized, ready to deploy when conversation drifts to "how would you build investigation quality at scale." Use the word-diagrams — Eric is on Google Meet, you don't need a real whiteboard, just describe the boxes in order.

### Soundbite 1: Investigation pipeline (alert ingest → enrichment → reasoning → verdict → human handoff)

```
[SIEM/EDR/IdP]──webhook──>[Normalizer]──>[Enrichment]──>[OSCAR Agent]──>[Verdict + Schema]──>[Human Tier]
   (Splunk,            CIM/CEF→canonical   threat intel,  ReAct loop      JSON Schema       only on
   Sentinel,           schema; tenant      asset graph,   typed tools     forced output;    low-conf
   CrowdStrike,        scoping; correlation prior cases   per OSCAR phase; grounding check  or high
   Okta)               key for dedup       (RAG)         token budget    citation required blast-radius
```

**Spoken version (45 seconds):**
> "Five stages. Alert lands on a webhook from the SIEM, EDR, identity provider. Normalizer maps vendor fields to a canonical schema — `src_ip` in CIM, `sourceAddress` in CEF, `srcip` in Palo Alto — because a wrong field mapping silently breaks every downstream inference. Enrichment pulls threat intel, asset metadata, prior similar cases from a tenant-scoped RAG index. The agent runs OSCAR inside a constrained ReAct loop with typed tool calls, one tool per pivot, token budget per investigation. Verdict comes back through a forced JSON schema with citation IDs on every factual claim. Anything low confidence or touching a privileged asset gets routed to human tier. The audit trail is the path itself — every step is replayable."

### Soundbite 2: Eval harness (golden set, regression, A/B, customer-specific drift)

```
                  ┌──────────────────────────────────────────────┐
                  │         EVAL HARNESS (CI-gated)              │
                  │                                              │
[PR / model bump]>│  Layer 1: Golden Set     2000 labeled cases  │
                  │  Layer 2: Red Team       300 adversarial     │
                  │  Layer 3: Shadow Replay  72hr prod traffic   │
                  │  Layer 4: Human Sample   2% weekly review    │
                  │                                              │
                  │  Per-tenant drift: weekly per alert class    │
                  └────────────────────┬─────────────────────────┘
                                       │
                                       v
                          [Block merge if regression > tolerance]
```

**Spoken version (45 seconds):**
> "Four layers, all CI-gated. Golden set of two thousand labeled historical investigations stratified by alert class and tenant type — every PR runs against this and blocks merge on regression beyond tolerance. Red team set of three hundred adversarial cases including prompt injection, jailbreak, APT seeds — runs on every prompt or model change. Shadow replay against the last 72 hours of production traffic — candidate output diffed against production. Human sample of 2 percent of production verdicts weekly, fed back into the golden set. Per-tenant drift is its own dashboard — same prompt, different customer schemas, different drift profile. I ran the same shape for our Trivy/Semgrep/Gitleaks CI gates and for the OpenClaw pre-deploy check on model upgrades."

### Soundbite 3: AI agent observability

```
[Agent Loop]──one structured event per step──>[Datadog / OTel]
   │                                           │
   │  per-step fields:                         │
   │   - investigation_id (correlation key)    │
   │   - tenant_id                             │
   │   - alert_class                           │
   │   - step_name (observe/strategize/...)    │
   │   - tool_name + args + response_id        │
   │   - tokens_in / tokens_out / cost_usd     │
   │   - latency_ms                            │
   │   - confidence_band                       │
   │   - failure_taxonomy_code (if any)        │
   v
[Failure taxonomy]
   01 Hallucinated IOC          06 Tool misuse
   02 Premature conclusion      07 Context blowout
   03 Missed pivot              08 Format drift
   04 Field mapping error       09 Prompt injection
   05 Base rate fallacy         10 Excessive agency attempt
```

**Spoken version (45 seconds):**
> "One structured event per agent step. Investigation ID is the correlation key. Every event carries tenant, alert class, step name, tool name with arguments and response ID, tokens in and out, dollar cost, latency, confidence band, and a failure taxonomy code if anything tripped. Ship to Datadog over OpenTelemetry, each tool call as a child span. The failure taxonomy is the load-bearing piece — ten codes I'd lift straight from the failure-mode table I built for the prep doc — hallucinated IOC, premature conclusion, missed pivot, field mapping error, prompt injection attempt, excessive agency attempt. Once you have a taxonomy, you can SLO each one. Without it, observability is a graph nobody reads."

---

## 5. Top 5 STAR Stories Ranked for THIS Round

A Director of Engineering audience weights different signals than the recruiter screen did. Director cares about: ship velocity, code quality at the boundary, owning a system end-to-end, debugging under pressure, system thinking. He cares less about: incident war stories told for color, GRC volume.

| Rank | Story | Use this if Eric asks about... | Why this rank |
|---|---|---|---|
| **1** | **OpenClaw Red Team** (Story 2) | "How do you think about quality of an AI system?" / "How do you test an agent?" / "How would you evaluate Dropzone's investigation quality?" / "Hard technical problem you solved recently" | Direct mirror of his hire mandate. You shipped a regression harness for AI behavior, caught two model-upgrade regressions before cutover. This is the closest analog to his job in your portfolio. |
| **2** | **Falco 200→12** (Story 3) | "How do you reduce false positives without losing coverage?" / "Detection engineering example" / "What does signal-to-noise mean to you?" / "Walk me through a tuning win" | Director-level signal: you tuned by writing more precise rules, not by deleting them. Mapped to ATT&CK, added a weekly diff job to catch new clusters joining the noise floor. Operator hygiene. |
| **3** | **n8n SOAR From Zero** (Story 4) | "Tell me about shipping under ambiguity" / "Biggest system you've built solo" / "How do you decide good-enough?" / "Startup speed example" | Shows founding-engineer instincts: typed contracts on every workflow, error handler workflow as a first-class object, secrets in a credential store from day one. 14 workflows in under a month. |
| **4** | **POS Skimmer Investigation** (Story 1) | "Tell me about a real investigation" / "What does investigation quality mean to you?" / "How do you handle ambiguous alerts" | Anchor story for the human-investigator credential. Use it once, early, and make it short. Director won't sit through a 3-minute war story — 75 seconds, lands the Wireshark + isolation + processor coordination, moves on. |
| **5** | **CoreDirective Accounting AI** (Story 6) | "Tell me about using AI for a real business problem" / "How do you think about AI governance" / "Example of human-in-the-loop you actually built" | Ties directly to Dropzone's "AI handles tier 1 so humans focus on real threats" thesis. Has the kill switch, the human review gate, the audit log — the same governance pattern Dropzone needs at customer scale. |

**Stories deliberately demoted for this round:**
- **Splunk MTTD 48→4** — same shape as Falco; pick Falco because it's at CoreDirective (more recent, more relevant tools).
- **37 GRC Docs** — Director of Engineering is not the audience for a documentation volume story. Save for the founder round if Wu asks about writing.
- **PCI Cross-Functional / Wi-Fi Disagreement** — culture stories. Eric may probe leadership but the OpenClaw + n8n stories already carry that signal at the technical layer.

**Delivery rules for all five:**
- 60–75 seconds, not 90. Director tolerance is shorter than recruiter tolerance.
- Lead with the metric when the question is metric-shaped.
- One technical specific per story (Wireshark + self-signed cert / OWASP LLM01 jailbreak corpus / explicit allowlist per token / asset-aware exclusions / anything-under-85%-routes-to-Telegram).
- Takeaway must sound like an engineer, not a slide. *"Tuning is not deleting rules, it's writing them with enough precision that a human can trust the feed."*

---

## 6. Live Coding Readiness

Eric may share his screen. He may not. If he asks "want to walk the code," you share *yours*. Have `agent.py`, `tools.py`, `main.py` open in tabs.

**Stack he'll expect you to handle without thinking:** Python 3.11, LangChain `create_agent`, boto3, Pydantic v2, pytest, Moto. Anthropic SDK directly if he wants to drop LangChain.

**Snippets to have memorized cold.** If Eric drops you into a blank file, type these from muscle memory.

### 6.1 Tool definition with Pydantic v2 schema

```python
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class GuardDutyFindingArgs(BaseModel):
    finding_id: str = Field(..., description="GuardDuty finding ID, e.g. 1c2b3a4d...")
    region: str = Field(default="us-east-1", description="AWS region")

@tool(args_schema=GuardDutyFindingArgs)
def get_guardduty_finding(finding_id: str, region: str = "us-east-1") -> str:
    """Fetch a single GuardDuty finding by ID. Read only."""
    client = boto3.client("guardduty", region_name=region)
    detector = client.list_detectors()["DetectorIds"][0]
    resp = client.get_findings(DetectorId=detector, FindingIds=[finding_id])
    return resp["Findings"][0] if resp["Findings"] else "Not found."
```

Why Pydantic, not raw dict: schema validation before the boto3 call, free JSON Schema for the LLM, clear error if the model passes a malformed arg.

### 6.2 Tool-calling agent loop skeleton (raw, no LangChain)

```python
from anthropic import Anthropic

def run_agent(question: str, tools: list, max_steps: int = 8) -> str:
    client = Anthropic()
    messages = [{"role": "user", "content": question}]
    for _ in range(max_steps):
        resp = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=2048,
            tools=tools,
            messages=messages,
        )
        if resp.stop_reason == "end_turn":
            return resp.content[-1].text
        if resp.stop_reason == "tool_use":
            tool_block = next(b for b in resp.content if b.type == "tool_use")
            result = dispatch(tool_block.name, tool_block.input)  # your dispatcher
            messages.append({"role": "assistant", "content": resp.content})
            messages.append({"role": "user", "content": [{
                "type": "tool_result", "tool_use_id": tool_block.id, "content": str(result)
            }]})
    return "Hit max_steps. Escalating to human."
```

The reason to know this: if Eric asks "what's `create_agent` doing under the hood," you draw it on demand.

### 6.3 Retry with exponential backoff for LLM calls

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from anthropic import APIStatusError, APIConnectionError

@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=2, max=20),
    retry=retry_if_exception_type((APIStatusError, APIConnectionError)),
    reraise=True,
)
def call_with_retry(client, **kwargs):
    return client.messages.create(**kwargs)
```

If he asks "why tenacity, not a hand loop": declarative, jitter built in, retry-on-exception type-safe. For surgical control roll your own.

### 6.4 Structured output parsing with Pydantic

```python
from pydantic import BaseModel, ValidationError

class Verdict(BaseModel):
    severity: str  # one of: info, low, medium, high, critical
    confidence: float  # 0.0 to 1.0
    iocs: list[str]
    citations: list[str]  # tool_response_ids that ground the verdict
    recommended_actions: list[str]

def parse_verdict(raw: str) -> Verdict:
    try:
        return Verdict.model_validate_json(raw)
    except ValidationError as e:
        # log + escalate, don't return malformed verdicts to humans
        raise InvestigationFormatError(str(e))
```

**Talking point:** "I never let the model freeform the final payload. Schema validation at the boundary or the verdict doesn't leave the agent."

### 6.5 Pytest fixture for Moto mock

```python
import pytest
import boto3
from moto import mock_aws

@pytest.fixture
def aws_sandbox():
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-public-bucket")
        s3.put_bucket_policy(Bucket="test-public-bucket", Policy='{"Statement":[{"Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"*"}]}')
        yield s3

def test_count_public_buckets(aws_sandbox):
    from tools import count_public_s3_buckets
    out = count_public_s3_buckets.invoke({})
    assert "1 are public" in out
    assert "test-public-bucket" in out
```

**Talking point:** "Clients are created inside each tool, not at module load. If you import-time-bind a boto3 client, it grabs real AWS before `@mock_aws` can intercept. Same reason the take-home creates clients inside the tool functions."

---

## 7. Whiteboard Scenarios

Eric may pose a design question. Below are five skeletons. Speak the boxes; don't draw if Meet whiteboard is unstable, just describe in order. Each scenario has a 60-second skeleton and the three follow-up tradeoffs you raise yourself before he has to ask.

### 7.1 "Design an investigation pipeline for IAM compromise alerts"

```
[CloudTrail+IdP+SIEM]──>[Normalizer]──>[Pivot Graph]──>[OSCAR Agent]──>[Verdict]
                          (canonical    required:        required pivots:   severity,
                           user_id,     IAM policy diff, MFA posture,       confidence,
                           role_arn,    last 30d auth,   role assumption    actions,
                           src_ip,      MFA events,      chain, conditional citations,
                           action,      device posture, access policies)   handoff
                           ts)
```

**60-sec walkthrough:** "IAM compromise has a fixed pivot graph the agent cannot skip — auth events plus MFA posture plus role-assumption chain plus conditional access policies. I'd encode the graph as code, version it, gate verdict on all pivots resolving. Cross-cloud is the same shape with different log sources — CloudTrail vs Azure Activity vs GCP audit. The hard part isn't the agent, it's the per-tenant field dictionary that maps the customer's column names to the canonical schema. Every new tenant is an integration test that probes the field map with a synthetic query."

**Three tradeoffs to raise:**
1. Latency vs evidence completeness — required pivots add seconds; tier them so high-confidence-benign closes fast and high-blast-radius always pulls full graph.
2. Single-tenant memory vs cold start — Dropzone's stance is per-tenant memory; that means every customer pays the cold-start cost on novel patterns. Mitigate with a shared *threat-pattern* index that holds public TI but not customer data.
3. Read-only vs response — IAM compromise begs for "disable the user." Don't give the agent that credential. Agent recommends, human approves, system executes.

### 7.2 "Design a tool that queries GuardDuty + CloudTrail + IAM correlated"

```python
class CompromiseLookupArgs(BaseModel):
    finding_id: str | None = None
    user_arn: str | None = None
    role_arn: str | None = None
    time_window_hours: int = 24

@tool(args_schema=CompromiseLookupArgs)
def correlate_compromise(...) -> CompromiseEvidence:
    """Pulls GuardDuty finding, CloudTrail events for the principal in
    window, and IAM policy snapshot. Returns a single evidence packet
    with grounded references."""
```

**60-sec walkthrough:** "One tool, three boto3 clients, returns a typed evidence packet, not three separate tool calls the agent has to fan out itself. The reason: investigation quality scales with tool semantics, not tool count. A coarse-grained `correlate_compromise` tool gives the model a clean pivot; three fine-grained tools force the model to do the join in its prompt context, which is where hallucination starts. Each finding gets a reference ID, every CloudTrail event gets one, the verdict has to cite them. I'd parallelize the three boto3 calls with `asyncio.gather` because they're independent and the latency adds up at scale."

**Three tradeoffs:**
1. Coarse-grained vs fine-grained tools — coarse is better for correlated tasks, fine-grained is better for discovery. I'd ship both.
2. Synchronous vs async — async for fan-out, but boto3 sync is fine inside one tool with `asyncio.to_thread`; the simple version ships first.
3. Cache vs fresh — IAM policy snapshots can cache for minutes; CloudTrail must be live; the tool needs a freshness contract per data source.

### 7.3 "Design an evaluation harness for the AI's output quality"

```
GOLDEN SET (2000 labeled, stratified by alert class)
   │
   ├──> Exact-match scorer  (verdict == label; IOCs match)
   ├──> Grounding scorer    (every claim cites a tool response)
   ├──> Pivot scorer        (required pivots executed)
   └──> LLM-as-judge        (narrative quality rubric, calibrated)

RED TEAM SET (300 adversarial)
   │
   └──> Pass/fail per OWASP LLM Top 10 class

SHADOW REPLAY (last 72h prod, candidate vs prod-pinned)
   │
   └──> Diff scorer + cost/latency delta

HUMAN REVIEW (2% weekly sample)
   │
   └──> Feed back into golden set
```

**60-sec walkthrough:** "Four layers. Golden set is the regression gate — every PR runs it, blocks merge on regression beyond tolerance per alert class. Red team is the safety gate — runs on every prompt or model change. Shadow replay is the production-realism gate — diffs candidate output against pinned prod for 72 hours of real traffic, with cost and latency deltas tracked alongside accuracy. Human review samples 2 percent of prod verdicts weekly and feeds the missed cases back into golden. Each layer has a dashboard, a clear owner, and a tolerance threshold. LLM-as-judge for the narrative quality piece, with a calibrated rubric and a periodic human spot check on the judge itself."

**Three tradeoffs:**
1. Cost of the harness vs cost of regression — running shadow replay on every PR is expensive; gate it on the prompt/model-change flag, not every commit.
2. Judge model vs human — judge is fast and cheap and biased; human is slow and expensive and the source of truth. Spot-check the judge against human monthly.
3. Stratification vs sample size — 2000 labeled cases sounds like a lot until you stratify across 30 alert classes and 5 tenant types. Some buckets will be thin; oversample real misses, don't synthesize.

### 7.4 "Design observability for the AI SOC analyst"

```
PER-STEP STRUCTURED EVENT  ──>  Datadog (logs)
  investigation_id              Datadog (metrics: cost, latency, tokens, conf)
  tenant_id                     OTel (traces: agent loop = root span,
  alert_class                                tool calls = child spans)
  step_name
  tool_name + args_hash         FAILURE TAXONOMY (10 codes, see Soundbite 3)
  response_ref_id                  ──>  SLO per code
  tokens_in/out                        ──>  Per-tenant heatmap
  cost_usd                             ──>  Weekly drift report
  latency_ms
  confidence_band               ALERTING:
  failure_code (nullable)         - cost_per_investigation > $X
                                  - p95 latency > Yms
                                  - confidence drift week-over-week
                                  - failure_code rate by class
```

**60-sec walkthrough:** "One structured event per step, shipped to Datadog over OpenTelemetry. The agent loop is the root span; each tool call is a child span. Metrics: cost per investigation, p95 latency per alert class, token consumption, confidence band distribution. The failure taxonomy is the SLO surface — ten failure codes, each gets a target rate, alerts when a code rate spikes. Per-tenant heatmaps catch drift that the aggregate hides — an integration regression in one tenant's Splunk schema looks fine in the global numbers and obvious per-tenant. The hard call is what *not* to log — full prompts and tool responses are PII-adjacent and tenant-isolated; I'd log args hashes and response IDs by default and store the full payloads in a tenant-scoped evidence store with separate retention."

**Three tradeoffs:**
1. Verbose logging vs PII risk — log references, store full payloads in tenant-scoped storage with retention policy.
2. Cardinality vs queryability — Datadog tag cardinality bites you fast; tenant_id and alert_class are mandatory tags, everything else is a structured field.
3. Real-time vs batch — alert on the cost and latency SLOs in real time; drift reports are batch weekly.

### 7.5 "Design a tool registry that scales to 100+ tools"

```
TOOL REGISTRY (per tenant)
  │
  ├── tool_id (semver)
  ├── name + description (LLM-readable)
  ├── args_schema (Pydantic / JSON Schema)
  ├── return_schema
  ├── permissions (read|write|destructive)
  ├── cost_class (cheap|moderate|expensive)
  ├── data_classification (public|internal|sensitive)
  ├── tenant_allowlist (which tenants see this tool)
  └── routing_hints (alert_class -> [preferred tools])

AGENT INIT:
  fetch_tools_for(tenant_id, alert_class) -> filtered subset
                  │
                  └── never give the agent all 100 tools at once;
                      LLM tool-pick degrades past ~30

WRITE TOOLS:
  always go through approval policy engine, never direct
```

**60-sec walkthrough:** "Three big problems at 100 tools. One, model tool-pick accuracy degrades past about 30 tools — solve with per-alert-class subsetting at agent init, not at runtime. Two, write tools need a separate path — every destructive action goes through a policy engine that can require human approval, not the agent's discretion. Three, schema versioning is a real product surface — I'd semver every tool, run a compatibility eval on every schema change, deprecate with a window. The registry itself is just a table — Postgres row per tool with the schema as JSONB. The agent never holds the write credential; it requests, the registry approves, the executor runs. That's the same pattern I built around OpenClaw skills."

**Three tradeoffs:**
1. Static subset vs dynamic retrieval — static is simpler and predictable; dynamic (RAG over tool descriptions) scales further but adds a tool-pick latency layer.
2. Per-tenant tools vs shared — most tools are shared, but tenant-specific integrations (custom Splunk indexes) need per-tenant registration.
3. Tool granularity policy — write a coarseness rubric. One tool per pivot, not per API endpoint. Resist sprawl.

---

## 8. Trust Phrases for Technical Depth

Sprinkle these. Don't deliver them as a string. They signal "I have shipped this," not "I have read about this."

1. "I caught this in a regression run before cutover." — model upgrade story
2. "The eval harness flagged drift on the IAM tool last week." — implies eval harness exists and runs
3. "I traced that hallucination back to the tool description being ambiguous, not the model." — context-engineering vocabulary
4. "We pinned the exact model version in config so a vendor swap couldn't move under us." — production discipline
5. "The grounding check rejected the verdict because the IOC had no source row." — schema-enforced quality
6. "The failure code on that one was excessive-agency-attempt; the policy engine refused the action." — taxonomy + governance
7. "I shadow-released that change for a week before flipping the canary to one percent." — rollout discipline
8. "Per-tenant field dictionary lives in the RAG index, pinned at query build time." — Dropzone's exact pattern
9. "Token budget hit the ceiling so the agent escalated to human tier with the evidence pointers intact." — context window management
10. "The first chunk of the result set carried the query context; the next three didn't. Classic context-engineering bug." — direct echo of Rahul Popat's blog post

**Use them in answer middles, not as openers.** "Yeah, I caught this in a regression run before cutover — the model upgrade had…" lands; "I caught this in a regression run before cutover" as a standalone sentence sounds rehearsed.

---

## 9. What to Ask Eric (Five Questions)

These are Director-level. Pick three to ask live; hold two as backup. All five are extension hooks — they invite him to talk about the engineering culture, not the recruiting pitch. Order is by priority.

### Q1 (always ask first)
> **"How do you measure investigation quality internally? Is there a number on the wall, or is it a portfolio of metrics that move per release?"**

Why it lands: directly mirrors the role mandate. Tells him you understand the job is to move a metric, not just write code. His answer reveals their actual eval discipline.

### Q2
> **"What's the failure mode that scares you the most right now? The one you wake up worrying about — is it a missed APT hidden in benign traffic, prompt injection through log content, model drift after a vendor upgrade, or something else?"**

Why it lands: forces specificity. A weak Director will list everything; a strong one will name one and explain why. Either way, you learn what the real engineering tension is. And you've given him three concrete options that show you've thought about this layer.

### Q3
> **"Where's the boundary between deterministic detection logic and LLM reasoning in the investigation? In other words, what does the agent decide and what's still in code?"**

Why it lands: Dropzone's whole differentiation is *"the scaffolding is the reliability engine, not the LLM."* Asking this signals you read the context-engineering post and understand the architectural axis they argue along.

### Q4 (backup)
> **"How does the team handle the tradeoff between investigation depth and latency? Customers want both; you can't fully optimize for both. What's the dial that gets turned?"**

Why it lands: shows you think about product tradeoffs, not just engineering elegance. Dropzone's customer voice talks about "30-60 min → 1 min" — that's the latency dial — but they also need to defend depth as the moat.

### Q5 (backup, if conversation has been deep on architecture)
> **"What does the first 90 days look like for someone owning investigation quality? Is the day-one work building eval infrastructure, fixing a specific accuracy gap on a specific alert class, or shipping integration coverage?"**

Why it lands: signals you're already mentally onboarding. His answer tells you whether the team is in eval-build mode (a rare clean slate to design the harness) or fix-the-fire mode (a known accuracy regression with a name on it). Both are good answers; the question shows you'd execute either way.

**Don't ask:**
- Comp, equity vesting, PTO. (Recruiter round, founder round.)
- "What's the engineering culture like?" (too vague, gets a recruiting answer)
- "Who reports to you?" (org chart energy, not engineering energy)
- Anything answerable from the website.

---

## 10. Closer (Last 90 Seconds)

Three variants. Read the room in the last 5 minutes — pick on the fly.

### Variant A — high-energy call (he was animated, you were animated, time flew)

> "Eric, this was a great conversation — I've got a clearer picture of the investigation-quality work than I had walking in, and it's the part of Dropzone I came in most excited about. Investigation quality at scale is the reason this role is at the top of my list. I'd love to know what the next step looks like and what the rough timeline is on your side. Anything I can put together between now and then to make the next round easier for the team?"

Word count: 80. Ends on a "what can I do for you" beat — senior energy.

### Variant B — measured call (it was professional, both of you held the line, no fireworks)

> "Eric, thanks again for the time. The technical layer at Dropzone is what I expected from the engineering blog and the take-home — investigation quality is real here, not a slogan, and that's the work I want to do at scale. What's the next step on your side, and what's a realistic timeline?"

Word count: 60. No flourish. Confident, not eager.

### Variant C — cold call (he was reserved, you read concern, the energy never quite locked)

> "Eric, I appreciate the directness on the technical questions — that's the bar I want to be measured against. Two things before we close. One, if there's a specific area where you'd want to see more depth before the next round, I'd rather hear it now than guess at it. Two, when should I expect to hear about next steps?"

Word count: 75. The "what didn't I show you" question is the senior move on a cold call. It tells him you've noticed the energy and you can take direct feedback. Almost always rescues a borderline call.

**Across all three:** end with the next-step question. Never end with "thank you" as the last sentence. Thank-you is in the middle.

---

## 11. 30-Min Pre-Call Ritual (12:15 – 12:45 PM EDT)

| Time | Action | Notes |
|---|---|---|
| 12:15 – 12:17 | Bathroom. Water. Refill glass to half. | No coffee in the last 30 min. |
| 12:17 – 12:19 | Headset on. Mic check. Camera on. Light on. | Test the headset against Meet's audio settings page, not just System Preferences. |
| 12:19 – 12:21 | Close everything — Slack, Telegram, Mail, calendar, Notion, anything that pings. Mute phone. | Silenced is not enough. *Do Not Disturb* on macOS, on the phone, on the watch. |
| 12:21 – 12:24 | Open the take-home repo in a tab. Open `agent.py`, `tools.py`, `main.py`. Have `sample_output.txt` ready in a fourth tab. | Don't share-screen yet. Just have it staged. |
| 12:24 – 12:26 | Index card on the desk: 200→12, 48hr→4hr, 8hr→90min. | Plus the red thread sentence, written out longhand. |
| 12:26 – 12:30 | Pitch dry-run. Variant A out loud. Variant B out loud. Time them. | Cap at 60 seconds each. If you're over, cut. |
| 12:30 – 12:33 | Three-question recall — say Q1, Q2, Q3 from section 9 out loud. | If you can't recall them clean, glance at the gameplan once and try again. |
| 12:33 – 12:36 | Soundbite 1 dry-run (investigation pipeline) — speak the boxes in order without looking. | Same for Soundbite 2 if there's time. |
| 12:36 – 12:39 | Two minutes of silence. Eyes closed. Slow breath, four-in seven-hold eight-out, three rounds. | This is the most important block. Drop the heart rate. |
| 12:39 – 12:41 | Posture check. Stand up. Roll shoulders. Sit back down. Eyes to the camera lens — not the preview window. | Note where the lens is so you don't drift into looking at his face on screen and breaking eye contact. |
| 12:41 – 12:43 | Open Meet. Join the room early. Audio test. Sit in the empty room with the camera on. | Comfortable in the room before he joins. |
| 12:43 – 12:45 | One last sip of water. Notebook open to a clean page. Pen down. Smile when his video lights up. | If he's late, don't fidget on camera. Sit still, breathe, wait. |

**Things on the desk, in this order from left to right:**
1. Notebook + pen
2. Index card with the three numbers + red thread
3. Half-glass of water
4. Phone face-down, on silent
5. Backup pen

**Things NOT on the desk:**
- Resume printout. (You know it cold; reading it on camera is a tell.)
- The full prep doc. (Index card is enough; if you're flipping pages on camera, you've lost.)
- A snack. (Don't.)

---

## File Path

`/Users/et/cyber-squire-ops/CoreDirective/career/dropzone-ai/10_TECHNICAL_ROUND_GAMEPLAN.md`
