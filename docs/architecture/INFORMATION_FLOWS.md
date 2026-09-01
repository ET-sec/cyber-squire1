# CoreDirective Information Flows

Two critical paths through the stack, current as of 2026-08-31. Runtime context first, because it changes how to read both flows: the platform now runs on a single Oracle Cloud Infrastructure (OCI) Ampere A1 Always Free ARM instance with 3 live containers (PostgreSQL 16 with pgvector, n8n, the Cloudflare tunnel sidecar). The previous x86 host died in August 2026. Squire and its self-hosted dependencies (NeMo Guardrails, Langfuse, Redis, Ollama, the Falco sensor) are designed and codified in the master compose file but pending the ARM rebuild, and the diagrams mark them with dashed grey boxes.

Acronyms, once: SOC (security operations center), RAG (retrieval augmented generation), PII (personally identifiable information), IR (incident response), eBPF (extended Berkeley Packet Filter), LLM (large language model), GRC (governance, risk, and compliance), OIDC (OpenID Connect), MCP (Model Context Protocol), OSCAL (Open Security Controls Assessment Language), SSP (System Security Plan), POA&M (Plan of Action and Milestones), OPA (Open Policy Agent), CI (continuous integration).

---

## Flow A: Squire autonomous SOC analyst (alert path)

**Status: designed and previously verified, pending ARM rebuild.** This flow ran end to end on the previous x86 host and every metric below was measured there during Phase 17. The code, guardrail configs, and eval evidence survived in the repo; the runtime did not. Live today from this diagram: the PostgreSQL container (its RAG corpus needs re-ingest, the chunks died with the old host), the n8n webhook delivery path, and Telegram. Everything drawn dashed comes back with the ARM rebuild.

The flow: a Falco event arrives, Squire classifies it, retrieves the relevant playbook from the RAG store, drafts an IR brief, runs a critique loop, and routes a recommend-only advisory to a human analyst. Every step is traced in self-hosted Langfuse and gated by five guardrail layers.

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
  classDef pending fill:#0d1117,stroke:#8b949e,color:#8b949e,stroke-dasharray:6 4

  STATUS["STATUS: flow verified end to end in Phase 17 on the previous x86 host.<br/>Squire and its dashed dependencies are DESIGNED, pending the ARM rebuild.<br/>Live today: PostgreSQL, n8n webhook delivery, Telegram."]:::rail

  SRC["Falco eBPF event<br/>kernel-level container detection<br/>· root shell · cred file read · escape attempt<br/>(sensor pending ARM rebuild)"]:::pending
  WEB["POST /alert<br/>Squire edge hostname<br/>(Cloudflare Tunnel ingress)"]:::pending

  subgraph BREAKERS["Pre-graph breakers (run BEFORE any LLM call) · pending ARM rebuild"]
    direction LR
    AUTH["Auth check<br/>webhook token<br/>+ interview-token list"]:::rail
    DEDUP["Dedup<br/>Redis 5-min sliding window<br/>verified: dedup = $0 / 0 ms"]:::rail
    COST["Cost ceiling<br/>daily rolling spend on ir_investigations<br/>verified: 503 + Retry-After"]:::rail
    PII1["Pre-graph PII regex<br/>SSN · CC · email · phone scrub"]:::rail
  end

  subgraph GRAPH["LangGraph state machine (7 nodes) · pending ARM rebuild"]
    direction TB
    N1["classify<br/>Opus 5 · 12 s p95"]:::node
    N2["retrieve<br/>pgvector cosine search<br/>top-k=8 · 1.5 s p95"]:::node
    N3["enrich<br/>2.5 s p95"]:::node
    N4["investigate<br/>Fable 5 · 29 s p95"]:::node
    N5["draft<br/>Fable 5 · 70 s p95"]:::node
    N6{{"critique<br/>Fable 5 · 12 s p95<br/>APPROVED / LOOP verdict"}}:::node
    N7["route_severity<br/>0.1 s"]:::node
  end

  subgraph RAILS["Per-node guardrails · pending ARM rebuild"]
    direction LR
    NEMOIN["NeMo input rail<br/>presidio PII"]:::rail
    NEMOOUT["NeMo output rail<br/>presidio PII"]:::rail
    CITE["Citation allow-list<br/>ATT&CK + 800-53 ID regex<br/>verified: 97.2% citation validity"]:::rail
    LOOP["Critique loop cap<br/>max 3 iters · max $0.50 · max 30 s wall<br/>verified: 28% loop rate (target under 35%)"]:::rail
    ACT["Recommend-only allow-list<br/>actions.yml rewrites forbidden verbs<br/>(docker stop, kubectl delete, rm, etc)<br/>to RECOMMEND: advisories"]:::rail
  end

  subgraph MODELS["Models · external"]
    direction LR
    FABLE["Anthropic API<br/>Fable 5 tier<br/>investigate · draft · critique"]:::model
    OPUS5["Anthropic API<br/>Opus 5 tier<br/>classify"]:::model
    OLLM["Ollama local<br/>fallback when degraded<br/>(pending ARM rebuild)"]:::pending
    VOYE["Voyage<br/>voyage-3-large 1024-dim"]:::model
  end

  subgraph STORES["Stores · retrieval"]
    PG[("pgvector (LIVE container)<br/>RAG corpus re-ingest pending:<br/>chunks died with the old host")]:::store
    REDIS[("Redis<br/>dedup keys · TTL 300 s<br/>(pending ARM rebuild)")]:::pending
  end

  subgraph TRACE["Observability"]
    LFTRACE["Langfuse<br/>1 trace per /alert · 1 span per node<br/>prompt + tokens + latency + cost<br/>(pending ARM rebuild)"]:::pending
  end

  subgraph DELIVER["Delivery (LIVE)"]
    direction LR
    N8NWH["n8n<br/>command webhook"]:::out
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

  N1 --> OPUS5
  N4 --> FABLE
  N5 --> FABLE
  N6 --> FABLE
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

### Verified flow metrics (Phase 17, measured on the previous x86 host)

| Metric | Verified value | Target |
|--------|----------------|--------|
| End-to-end p50 latency | 47 s | under 60 s |
| End-to-end p95 latency | 82 s | under 90 s |
| Cost per invocation p95 | $0.38 | under $0.50 |
| Citation validity rate | 97.2% | over 95% |
| Critique loop rate | 28% | under 35% |
| RAG retriever p95 | under 500 ms (317 to 345 ms on 5 real queries) | under 500 ms |
| Top-1 playbook match | 5/5 paraphrased queries | n/a |
| Red-team cumulative cases | 20 (cycle 1: 6, cycle 2: 14) | n/a |
| Red-team true bypasses | 0 of 17 valid (3 INFRA_ERROR tracked in the POA&M) | 0 |
| Red-team cumulative LLM spend | $6.81 ($0.42 avg per valid case) | n/a |

These numbers stand as evidence of what the design achieves; they get re-verified on ARM once the rebuild lands, and the RAG counts get recounted after re-ingest.

### Where the five guardrail layers fire

1. **Pre-graph regex PII scanner** scrubs SSN, credit card, email, and phone patterns before the alert touches a model.
2. **NeMo input rail** runs a presidio PII pass on every prompt entering each LLM node.
3. **NeMo output rail** runs the same pass on every completion leaving each LLM node.
4. **Citation allow-list** at the critique node: every ATT&CK technique ID and every NIST 800-53 control ID must match the allow-list regex, otherwise the critique forces a LOOP back to draft (max 3 iterations, max $0.50, max 30 s).
5. **Recommend-only actions.yml boundary** at the response layer: forbidden verbs (docker stop, kubectl delete, rm, rotate key, shutdown, and the rest of the list) are rewritten to RECOMMEND advisories with sanitization events attached.

---

## Flow B: AI-native GRC pipeline (PR path)

**Status: live in CI, with one paused branch.** This flow runs in GitHub Actions, so it survived the host loss almost untouched. The reviewer agents, kill switches, OPA gates, and the cosign signing path on merge all operate today. The one casualty: the eval harness lands its scores in self-hosted Langfuse, which is pending the ARM rebuild, so eval reruns are paused. The Phase 19 baseline scores were landed before the loss and remain the recorded baseline.

The flow: a pull request opens, path filters split traffic to one of two reviewer agents, both honor a daily cost ceiling and a kill switch. On merge to main, three OSCAL artifacts get cosign-signed via Sigstore keyless OIDC. The eval harness scores reviewer output against a 12-fixture golden set.

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
  classDef pending fill:#0d1117,stroke:#8b949e,color:#8b949e,stroke-dasharray:6 4

  PR["**Pull request opens**<br/>cyber-squire1 repo"]:::src

  PATH{"path filter<br/>**docs/grc/** OR code"}:::gate

  subgraph BUDGET["**Pre-call kill switches**"]
    direction LR
    BG["**budget_guard.py**<br/>$1/day enforced cap<br/>· dual-source ledger<br/>· admin API + local SQLite"]:::gate
    KILL["repo vars<br/>GRC_REVIEWER_DISABLED<br/>PR_AGENT_DISABLED<br/>(executable in under 10 s)"]:::gate
    SIZE["diff size guard<br/>100 KB hard skip<br/>· concurrency cancel-in-progress<br/>· timeout 5/8 min"]:::gate
  end

  subgraph DOCAGENT["**GRC reviewer agent** (docs/grc/** only)"]
    direction TB
    GRCREV["scripts/grc/grc_reviewer.py<br/>Opus 5 default<br/>Fable 5 escalation<br/>(over 50 KB or over 5 files)"]:::agent
    PCACHE["**Prompt caching**<br/>cached system block<br/>cache_control: ephemeral"]:::agent
    GRCREF["scripts/grc/grc_reference.md<br/>NIST + POA&M reference tokens"]:::store
    SAN["sanitize_output.py<br/>10 patterns · POA&M/NIST passthrough"]:::gate
  end

  subgraph CODEAGENT["**PR-Agent** (code paths only)"]
    direction TB
    PRA["qodo-ai/pr-agent<br/>pinned by 40-char SHA<br/>Opus 5 default<br/>Fable 5 fallback"]:::agent
    PRACONF[".pr_agent.toml<br/>describe + review + improve<br/>100k token cap"]:::store
  end

  subgraph MCP["**MCP server** (Claude Desktop access)"]
    MCPSRV["grc_mcp_server.py<br/>**5 tools** over stdio<br/>list_docs · read_doc · search_corpus<br/>get_poam · get_threat_model_entry"]:::agent
  end

  subgraph MERGE["**On merge to main only**"]
    direction TB
    MGUARD["bot-actor exclusion<br/>github.actor != github-actions[bot]"]:::gate
    BUILDOSCAL["build_oscal.py<br/>3 artifacts:<br/>· SSP · POA&M · Component-Definition"]:::agent
    COSIGN["**cosign sign-blob**<br/>keyless OIDC<br/>(GitHub Actions identity)"]:::agent
    REKOR["**Rekor public log**<br/>transparency entry<br/>verifiable by any 3rd party"]:::out
    UPLOAD["upload-artifact<br/>oscal bundle per merge SHA<br/>**90-day retention**"]:::out
  end

  subgraph PRGATE["**On every PR**"]
    direction TB
    OPA["**OPA conftest**<br/>3 Rego policies<br/>required_frontmatter · classification · poam_id_integrity<br/>soft_fail = true (rollout)"]:::gate
    DDLOAD["download-artifact<br/>verify cosign bundle<br/>tolerance: warn if no artifact"]:::gate
  end

  subgraph EVAL["**Eval harness** (self-hosted; reruns paused pending ARM rebuild)"]
    direction LR
    GOLDEN["**12-fixture golden set**<br/>10 LLM-generated + 2 hand-crafted"]:::store
    LFEXP["Langfuse experiment<br/>Squire-GRC-Reviewer baseline<br/>(Phase 19 scores landed; host pending ARM rebuild)"]:::pending
    EVALS["**4 evaluators × 12 fixtures = 48 scores**<br/>control_coverage · poam_id_accuracy<br/>sanitization_catch_rate · hallucination_rate"]:::obs
  end

  subgraph BUDGETLEDGER["**Spend ledger**"]
    LEDGER[("local SQLite spend ledger<br/>+ Anthropic admin API")]:::store
  end

  ANTH["Anthropic API<br/>Opus 5 / Fable 5"]:::model
  COMMENT["**PR comment**<br/>NIST mapping + POA&M deltas<br/>+ residual_risk required"]:::out

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

  GRCREV -->|"nightly (paused pending rebuild)"| EVALS
  EVALS --> LFEXP
  GOLDEN --> EVALS

  MCPSRV -->|stdio| GRCREV
```

### Verified flow metrics (Phase 19 records)

| Metric | Verified value |
|--------|----------------|
| Phase 19 actual spend | $1.77 ($0.48 golden gen + $0.72 eval run + $0.57 re-run) |
| Per-PR cost (warm cache) | $0.025 |
| Per-PR cost (cold cache) | $0.05 |
| Daily enforced kill switch | $1.00 / day |
| Eval-mode raised cap | $5.00 / day |
| Recurring projection | under $5 / month at 200 PRs |
| MCP tools exposed | 5 |
| OPA Rego policies in the GRC gate | 3 |
| Golden-set fixtures | 12 (10 LLM + 2 hand-crafted) |
| Langfuse evaluator scores landed | 48 (4 x 12) |
| Sanitization catch rate (baseline) | 0.917 |
| Hallucination rate (baseline) | 0.292 |
| Control coverage (baseline) | 0.750 |
| POA&M ID accuracy (baseline) | 0.667 |
| Cosign artifact retention | 90 days |
| OSCAL artifacts signed per merge | 3 (SSP, POA&M, Component-Definition) |

Since Phase 20.1 this flow gained a sibling: scanner findings (Trivy, Checkov, Gitleaks) now feed `scripts/poam_sync.py`, which maintains a script-owned, fingerprint-deduplicated POA&M intake ledger alongside the human-curated register. See STACK_OVERVIEW.md, detection plane.

### What this pipeline mirrors in the commercial world

| Self-hosted piece | Enterprise analog |
|-------------------|-------------------|
| Custom GRC reviewer (Opus 5 with Fable 5 escalation) | ServiceNow GRC + Drata workflow checklists |
| Qodo PR-Agent | CodeRabbit |
| Cosign + Rekor on OSCAL | Chainguard supply-chain attestation |
| OPA + conftest on frontmatter | ServiceNow workflow gates / policy-as-code |
| FastMCP server (5 tools) | RegScale REST API · Drata GraphQL |
| Langfuse eval harness | Internal QA · vendor SLA dashboards |
| budget_guard.py + spend ledger | Enterprise FinOps cost-cap controls |

---

## How to render to PNG

The `.mmd` files in this directory are the render sources; the markdown embeds mirror them.

```bash
cd ~/cyber-squire-ops
npx -y @mermaid-js/mermaid-cli -i docs/architecture/STACK_OVERVIEW_1.mmd \
  -o docs/architecture/STACK_OVERVIEW.png -p docs/architecture/puppeteer-config.json --scale 3
npx -y @mermaid-js/mermaid-cli -i docs/architecture/INFORMATION_FLOWS_1.mmd \
  -o docs/architecture/FLOW_A_squire_alert_path.png -p docs/architecture/puppeteer-config.json --scale 3
npx -y @mermaid-js/mermaid-cli -i docs/architecture/INFORMATION_FLOWS_2.mmd \
  -o docs/architecture/FLOW_B_phase19_grc_pipeline.png -p docs/architecture/puppeteer-config.json --scale 3
```
