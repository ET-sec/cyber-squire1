# CoreDirective Information Flows

Two critical paths through the stack. Read each diagram top to bottom. Annotations call out model, latency, cost, guardrail layer.

---

## Flow A — Squire autonomous SOC analyst (alert path)

A Falco event arrives. Squire classifies it, retrieves the relevant playbook from a 1,564-chunk RAG, drafts an IR brief, runs a critique loop, and routes to a human analyst. Every step is traced in self-hosted Langfuse and gated by five guardrail layers.

```mermaid
%%{init: {'theme':'base', 'themeVariables': {
  'primaryColor':'#0d1117',
  'primaryTextColor':'#7CFFB2',
  'primaryBorderColor':'#39d98a',
  'lineColor':'#39d98a',
  'secondaryColor':'#161b22',
  'tertiaryColor':'#1f2933',
  'fontFamily':'JetBrains Mono, Menlo, monospace',
  'fontSize':'13px'
}}}%%
flowchart TB

  classDef src fill:#1f2933,stroke:#7CFFB2,color:#7CFFB2,stroke-width:2px
  classDef rail fill:#1c2c3a,stroke:#f97583,color:#f97583,stroke-width:2px
  classDef node fill:#161b22,stroke:#39d98a,color:#cdd9e5
  classDef model fill:#1c2c3a,stroke:#7CFFB2,color:#7CFFB2,stroke-width:2px
  classDef store fill:#1f2933,stroke:#f2cc60,color:#cdd9e5
  classDef obs fill:#1f2933,stroke:#a371f7,color:#cdd9e5
  classDef out fill:#1f2933,stroke:#58a6ff,color:#cdd9e5

  SRC["**Falco eBPF event**<br/>kernel-level container detection<br/>· root shell · cred file read · escape attempt"]:::src
  WEB["POST /alert<br/>squire.tigouetheory.com<br/>(Cloudflare Tunnel ingress)"]:::node

  subgraph BREAKERS["**Pre-graph breakers** (run BEFORE any LLM call)"]
    direction LR
    AUTH["Auth check<br/>SQUIRE_WEBHOOK_TOKEN<br/>+ interview-token list"]:::rail
    DEDUP["**Dedup**<br/>Redis 5-min sliding window<br/>verified: dedup→ $0 / 0 ms"]:::rail
    COST["**Cost ceiling**<br/>daily rolling spend on ir_investigations<br/>verified: 503 + Retry-After:3600"]:::rail
    PII1["**Pre-graph PII regex**<br/>SSN · CC · email · phone scrub"]:::rail
  end

  subgraph GRAPH["**LangGraph state machine** (7 nodes)"]
    direction TB
    N1["**classify**<br/>Sonnet 4.6 · 12 s p95"]:::node
    N2["**retrieve**<br/>pgvector cosine search<br/>top-k=8 from 1,564 chunks<br/>· 1.5 s p95"]:::node
    N3["**enrich**<br/>2.5 s p95"]:::node
    N4["**investigate**<br/>Opus 4.7 · 29 s p95"]:::node
    N5["**draft**<br/>Opus 4.7 · 70 s p95"]:::node
    N6{{"**critique**<br/>Opus 4.7 · 12 s p95<br/>APPROVED / LOOP verdict"}}:::node
    N7["**route_severity**<br/>0.1 s"]:::node
  end

  subgraph RAILS["**Per-node guardrails**"]
    direction LR
    NEMOIN["NeMo input rail<br/>presidio PII"]:::rail
    NEMOOUT["NeMo output rail<br/>presidio PII"]:::rail
    CITE["**Citation allow-list**<br/>regex `^T\\d{4}` · 800-53 IDs<br/>verified: 97.2% citation validity"]:::rail
    LOOP["Critique loop cap<br/>max 3 iters · max $0.50 · max 30 s wall<br/>verified: 28% loop rate (target <35%)"]:::rail
    ACT["**Recommend-only allow-list**<br/>actions.yml rewrites forbidden verbs<br/>(docker stop, kubectl delete, rm -rf, etc)<br/>→ RECOMMEND: advisories"]:::rail
  end

  subgraph MODELS["**Models · external**"]
    direction LR
    OPUS["Anthropic API<br/>**Opus 4.7**<br/>investigate · draft · critique"]:::model
    SONNET["Anthropic API<br/>**Sonnet 4.6**<br/>classify"]:::model
    OLLM["Ollama local<br/>fallback when degraded"]:::model
    VOYE["Voyage<br/>voyage-3-large 1024-dim"]:::model
  end

  subgraph STORES["**Stores · retrieval**"]
    PG[("pgvector<br/>1,564 chunks · 38 GRC docs<br/>HNSW m=16 ef_construction=64")]:::store
    REDIS[("Redis<br/>dedup keys · TTL 300 s")]:::store
  end

  subgraph TRACE["**Observability**"]
    LFTRACE["**Langfuse v3**<br/>1 trace per /alert<br/>· 9 spans (1 per node)<br/>· prompt + completion + tokens + latency + cost<br/>· degraded-mode header captured"]:::obs
  end

  subgraph DELIVER["**Delivery**"]
    direction LR
    N8NWH["n8n webhook<br/>master-cmd"]:::out
    TGAPI["Telegram Bot API<br/>fallback if n8n 404"]:::out
    HUMAN["Analyst<br/>(Telegram chat)"]:::out
  end

  SRC --> WEB
  WEB --> AUTH
  AUTH --> DEDUP
  DEDUP --> COST
  COST --> PII1
  PII1 --> N1

  N1 --> N2
  N2 --> N3
  N3 --> N4
  N4 --> N5
  N5 --> N6
  N6 -->|APPROVED| N7
  N6 -->|LOOP back to draft| N5

  N1 -->|embed query| VOYE
  N2 -->|cosine search| PG
  N1 -->|text in/out| NEMOIN
  N1 -->|text in/out| NEMOOUT
  N6 -->|validate| CITE
  N6 -->|enforce caps| LOOP

  N1 --> SONNET
  N4 --> OPUS
  N5 --> OPUS
  N6 --> OPUS
  N4 -->|fallback| OLLM

  DEDUP <--> REDIS

  N1 -->|span| LFTRACE
  N2 -->|span| LFTRACE
  N3 -->|span| LFTRACE
  N4 -->|span| LFTRACE
  N5 -->|span| LFTRACE
  N6 -->|span| LFTRACE
  N7 -->|span| LFTRACE

  N7 --> ACT
  ACT --> N8NWH
  N8NWH -->|if 404| TGAPI
  TGAPI --> HUMAN
  N8NWH --> HUMAN
```

### Verified flow metrics (per `SQUIRE_MODEL_CARD.md` and Phase 17 SUMMARYs)

| Metric | Verified value | Target |
|--------|----------------|--------|
| End-to-end p50 latency | **47 s** | < 60 s |
| End-to-end p95 latency | **82 s** | < 90 s |
| Cost per invocation p95 | **$0.38** | < $0.50 |
| Citation validity rate | **97.2%** | > 95% |
| Critique loop rate | **28%** | < 35% |
| RAG retriever p95 | **< 500 ms** (317–345 ms on 5 real queries) | <500 ms |
| Top-1 playbook match | **5/5** paraphrased queries | n/a |
| Red-team cumulative cases | **20** (cycle 1: 6, cycle 2: 14) | n/a |
| Red-team true bypasses | **0** of 17 valid (3 INFRA_ERROR tracked in POAM-P17-15) | 0 |
| Red-team cumulative LLM spend | **$6.81** ($0.42 avg / valid case) | n/a |

### Where the five guardrail layers fire

1. **Pre-graph regex PII scanner** (`pre_graph_pii.py`) — scrubs SSN / CC / email / phone before the alert touches a model.
2. **NeMo input rail** — presidio PII pass on every prompt entering each LLM node.
3. **NeMo output rail** — presidio PII pass on every completion leaving each LLM node.
4. **Citation allow-list** at the critique node — every `T1234` ATT&CK technique and every `AC-2` style 800-53 ID must match the allow-list regex; otherwise the critique forces a LOOP back to draft (max 3 iters, max $0.50, max 30 s).
5. **Recommend-only `actions.yml` boundary** at the response layer — forbidden verbs (`docker stop`, `kubectl delete`, `rm -rf`, `rotate key`, `shutdown`, etc) are rewritten to `RECOMMEND:` advisories with `sanitization_events[]` attached.

---

## Flow B — Phase 19 AI-native GRC pipeline (PR path)

A pull request opens. Path filters split traffic to one of two reviewer agents. Both honor a daily cost ceiling and a kill switch. On merge to main, three OSCAL artifacts get cosign-signed via Sigstore keyless OIDC. Eval harness scores reviewer output against a 12-fixture golden set in self-hosted Langfuse.

```mermaid
%%{init: {'theme':'base', 'themeVariables': {
  'primaryColor':'#0d1117',
  'primaryTextColor':'#7CFFB2',
  'primaryBorderColor':'#39d98a',
  'lineColor':'#39d98a',
  'secondaryColor':'#161b22',
  'tertiaryColor':'#1f2933',
  'fontFamily':'JetBrains Mono, Menlo, monospace',
  'fontSize':'13px'
}}}%%
flowchart TB

  classDef src fill:#1f2933,stroke:#7CFFB2,color:#7CFFB2,stroke-width:2px
  classDef gate fill:#1c2c3a,stroke:#f97583,color:#f97583,stroke-width:2px
  classDef agent fill:#161b22,stroke:#39d98a,color:#cdd9e5
  classDef model fill:#1c2c3a,stroke:#7CFFB2,color:#7CFFB2,stroke-width:2px
  classDef store fill:#1f2933,stroke:#f2cc60,color:#cdd9e5
  classDef obs fill:#1f2933,stroke:#a371f7,color:#cdd9e5
  classDef out fill:#1f2933,stroke:#58a6ff,color:#cdd9e5

  PR["**Pull request opens**<br/>cyber-squire1 repo"]:::src

  PATH{"path filter<br/>**docs/grc/** OR code"}:::gate

  subgraph BUDGET["**Pre-call kill switches**"]
    direction LR
    BG["**budget_guard.py**<br/>$1/day enforced cap<br/>· dual-source ledger<br/>· admin API + local SQLite"]:::gate
    KILL["repo vars<br/>GRC_REVIEWER_DISABLED<br/>PR_AGENT_DISABLED<br/>(executable in <10 s)"]:::gate
    SIZE["diff size guard<br/>100 KB hard skip<br/>· concurrency cancel-in-progress<br/>· timeout 5/8 min"]:::gate
  end

  subgraph DOCAGENT["**GRC reviewer agent** (docs/grc/** only)"]
    direction TB
    GRCREV["scripts/grc/grc_reviewer.py<br/>Sonnet 4.6 default<br/>Opus 4.7 escalation<br/>(>50 KB or >5 files)"]:::agent
    PCACHE["**Prompt caching**<br/>7,835-char system block<br/>cache_control: ephemeral"]:::agent
    GRCREF["scripts/grc/grc_reference.md<br/>105 lines · 475 NIST tokens · 16 POAM tokens"]:::store
    SAN["sanitize_output.py<br/>10 patterns · POAM/NIST passthrough"]:::gate
  end

  subgraph CODEAGENT["**PR-Agent** (code paths only)"]
    direction TB
    PRA["qodo-ai/pr-agent@<br/>0e37fc84... (40-char SHA)<br/>Sonnet 4.6 default<br/>Opus 4.7 fallback"]:::agent
    PRACONF[".pr_agent.toml<br/>describe + review + improve<br/>100k token cap"]:::store
  end

  subgraph MCP["**MCP server** (Claude Desktop access)"]
    MCPSRV["grc_mcp_server.py · 308 lines<br/>**5 tools** over stdio<br/>list_docs · read_doc · search_corpus<br/>get_poam · get_threat_model_entry"]:::agent
  end

  subgraph MERGE["**On merge to main only**"]
    direction TB
    MGUARD["bot-actor exclusion<br/>github.actor != github-actions[bot]"]:::gate
    BUILDOSCAL["build_oscal.py<br/>3 artifacts:<br/>· SSP · POAM · Component-Definition"]:::agent
    COSIGN["**cosign sign-blob --bundle**<br/>keyless OIDC<br/>(GitHub Actions identity)"]:::agent
    REKOR["**Rekor public log**<br/>transparency entry<br/>verifiable by any 3rd party"]:::out
    UPLOAD["actions/upload-artifact@v4<br/>oscal-bundles-${SHA}<br/>**90-day retention**"]:::out
  end

  subgraph PRGATE["**On every PR**"]
    direction TB
    OPA["**OPA conftest**<br/>3 Rego policies<br/>required_frontmatter · classification · poam_id_integrity<br/>data.config.soft_fail = true (rollout)"]:::gate
    DDLOAD["dawidd6/action-download-artifact<br/>verify cosign bundle<br/>tolerance: if_no_artifact warn"]:::gate
  end

  subgraph EVAL["**Eval harness** (self-hosted)"]
    direction LR
    GOLDEN["**12-fixture golden set**<br/>10 LLM-generated + 2 hand-crafted<br/>(binary diff · 60.9 KB diff)"]:::store
    LFEXP["Langfuse experiment<br/>Squire-GRC-Reviewer baseline"]:::obs
    EVALS["**4 evaluators × 12 fixtures = 48 scores**<br/>control_coverage · poam_id_accuracy<br/>sanitization_catch_rate · hallucination_rate"]:::obs
  end

  subgraph BUDGETLEDGER["**Spend ledger**"]
    LEDGER[("~/.cache/grc/spend_ledger.sqlite<br/>+ Anthropic admin API")]:::store
  end

  ANTH["Anthropic API<br/>Sonnet 4.6 / Opus 4.7"]:::model
  COMMENT["**PR comment**<br/>NIST mapping + POAM deltas<br/>+ residual_risk required"]:::out

  PR --> PATH
  PATH -->|docs/grc/**| BG
  PATH -->|code paths| BG
  BG --> KILL
  KILL --> SIZE
  SIZE -->|docs path| GRCREV
  SIZE -->|code path| PRA

  GRCREV --> PCACHE
  PCACHE -->|cached system| GRCREF
  GRCREV --> ANTH
  GRCREV --> SAN
  SAN --> COMMENT
  PRA --> ANTH
  PRA --> COMMENT
  COMMENT --> PR

  BG <--> LEDGER

  PR --> OPA
  OPA -->|merge gate| PR
  PR --> DDLOAD
  DDLOAD --> COMMENT

  PR -->|if merged to main| MGUARD
  MGUARD --> BUILDOSCAL
  BUILDOSCAL --> COSIGN
  COSIGN --> REKOR
  COSIGN --> UPLOAD
  UPLOAD --> DDLOAD

  GRCREV -->|daily nightly| EVALS
  EVALS --> LFEXP
  GOLDEN --> EVALS

  MCPSRV -->|stdio| GRCREV
```

### Verified flow metrics (per `19-06-SUMMARY.md` and Phase 19 plan files)

| Metric | Verified value |
|--------|----------------|
| Phase 19 actual spend to date | **$1.77** ($0.48 golden gen + $0.72 eval run + $0.57 re-run) |
| Per-PR cost (warm cache) | **$0.025** |
| Per-PR cost (cold cache) | **$0.05** |
| Daily enforced kill switch | **$1.00 / day** (`DAILY_LIMIT_USD`) |
| Eval-mode raised cap | $5.00 / day |
| Recurring projection | **< $5 / month** at 200 PRs |
| GRC reviewer tests | 36 passing in 0.36 s |
| MCP tools exposed | **5** |
| MCP stdio purity tests | 17 passing in 1.03 s; zero `print()` calls |
| OPA Rego policies | **3** |
| OPA soft-fail mode warnings | 22 on current corpus |
| Golden-set fixtures | **12** (10 LLM + 2 hand-crafted) |
| Langfuse evaluator scores landed | **48** (4 × 12) |
| Sanitization catch rate (baseline) | **0.917** |
| Hallucination rate (baseline) | 0.292 |
| Control coverage (baseline) | 0.750 |
| POAM ID accuracy (baseline) | 0.667 |
| Cosign artifact retention | **90 days** |
| OSCAL artifacts signed per merge | **3** (SSP, POAM, Component-Definition) |

### What this pipeline mirrors in the commercial world

| OSS piece on the droplet | Enterprise analog |
|--------------------------|-------------------|
| Custom GRC reviewer (Sonnet 4.6 + Opus 4.7 escalation) | ServiceNow GRC + Drata workflow checklists |
| Qodo PR-Agent | CodeRabbit |
| Cosign + Rekor on OSCAL | Chainguard supply-chain attestation |
| OPA + conftest on frontmatter | ServiceNow workflow gates / policy-as-code |
| FastMCP server (5 tools) | RegScale REST API · Drata GraphQL |
| Langfuse eval harness | Internal QA · vendor SLA dashboards |
| budget_guard.py + spend_ledger.py | Enterprise FinOps cost-cap controls |

---

## How to render to PNG

```bash
# Option 1: one-shot via Mermaid CLI (mmdc) on the droplet or local Mac
brew install mermaid-cli   # if not yet installed
mmdc -i docs/architecture/STACK_OVERVIEW.md -o /tmp/stack_overview.png -t dark -b transparent
mmdc -i docs/architecture/INFORMATION_FLOWS.md -o /tmp/information_flows.png -t dark -b transparent

# Option 2: render in VS Code with the Mermaid Preview extension and screenshot
# Option 3: paste into mermaid.live for an interactive view
```

Render at 2160px wide minimum if you want the labels readable per `feedback_diagram_text_size`.
