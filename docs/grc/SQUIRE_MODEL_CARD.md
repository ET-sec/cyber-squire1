# Squire Model Card

**Document ID:** MC-SQUIRE-001
**Version:** 1.0
**Classification:** Internal Use Only
**Effective Date:** 2026-04-23
**Owner:** Information Security Officer
**Approved By:** System Owner
**Template:** Mitchell et al., "Model Cards for Model Reporting" (FAT\* 2019)

---

## Document Control

| Field | Value |
|-------|-------|
| Document ID | MC-SQUIRE-001 |
| Version | 1.0 |
| Status | Approved |
| Last Revised | 2026-04-23 |
| Next Review | 2026-10-23 |
| Author | Information Security Officer |
| Approver | System Owner |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-23 | Information Security Officer | Initial model card covering Opus 4.7 primary, Sonnet 4.6 classifier, text-embedding-3-large retriever |

---

## 1. Model Details

Squire is a composite AI system, not a single model. Three foundation models are wired together behind a LangGraph state machine. This card covers all three, because the risk surface of the combined system depends on choices made at every node.

### 1.1 Component Summary

| Role | Model | Provider | Version | License | Nodes |
|------|-------|----------|---------|---------|-------|
| Primary reasoning | Claude Opus 4.7 | Anthropic PBC | claude-opus-4-7 (2026 release) | Proprietary (API ToS) | investigate, draft, critique |
| Classifier | Claude Sonnet 4.6 | Anthropic PBC | claude-sonnet-4-6 | Proprietary (API ToS) | classify |
| Embeddings | text-embedding-3-large | OpenAI | v3-large, 1536 dim | Proprietary (API ToS) | retrieve (ingest side) |

Non-model components are covered in AI_SUPPLY_CHAIN_REGISTER.md.

### 1.2 Backend Abstraction

Squire talks to these models through a `LLMBackend` interface with three implementations. The composite system can run under any of them without code changes.

| Mode | Implementation | Use Case |
|------|----------------|----------|
| `api` | Direct Anthropic REST, OpenAI REST | Production |
| `max` | `claude` CLI over Max subscription | Development on Mac |
| `ollama` | Local Qwen or Llama via svc-ollama | Outage fallback, air-gap demo |

Backend selection is driven by `SQUIRE_BACKEND` environment variable with runtime override via `x-squire-backend` header on `/alert`. Ollama fallback is not a silent failover; degraded mode sets `state.backend_degraded=true` and the response envelope surfaces the flag to downstream consumers.

### 1.3 Architecture at a Glance

```
classify (Sonnet 4.6)
  -> retrieve (pgvector HNSW, vector(1536))
  -> enrich (Tavily search, no LLM)
  -> investigate (Opus 4.7)
  -> draft (Opus 4.7)
  -> critique (Opus 4.7, loops up to 3x)
  -> route_severity (deterministic)
```

Full data flow with trust boundaries is in SQUIRE_DATA_FLOW_CLASSIFICATION.md.

### 1.4 Model Routing Rationale

Splitting the classifier onto Sonnet 4.6 while keeping the investigate, draft, and critique nodes on Opus 4.7 is deliberate. The classify step is a short, highly structured call that outputs a small JSON envelope. Running Opus 4.7 on that step wastes budget; Sonnet 4.6 returns the same classification at a fraction of the token cost. The downstream three nodes each take multi-paragraph reasoning inputs and must maintain citation fidelity across the critique loop, which is where Opus 4.7 earns its cost.

The enrich node runs no LLM. Tavily's search API returns a structured result set that the investigate node consumes directly. Wrapping Tavily in an LLM summarizer was evaluated and rejected because the summarization step itself was a citation-fabrication risk. Investigate can reason over raw Tavily results more reliably than over an LLM-summarized version.

The route_severity node is pure Python. Given classify severity and critique approval state, it routes to HITL or to auto-close. No LLM involvement at this boundary is a deliberate trust decision, since the routing determines whether a human is paged.

---

## 2. Intended Use

### 2.1 Primary Use Case

Autonomous triage of security alerts arriving from Falco, n8n security workflows, and the public webhook at https://squire.example-ops.com/alert. Output is a structured investigation report with:

- Severity classification (LOW, MEDIUM, HIGH, CRITICAL)
- MITRE ATT&CK technique mappings
- CSA Agentic MANAGE allow-list codes
- Citations into the 31-doc pgvector RAG corpus
- Recommended next actions (passed through a `rewrite` allow-list that strips autonomous verbs)

### 2.2 In Scope

- Single-tenant demo on alpha-node running from /opt/platform/
- Alert volumes up to ~50 per day (cost ceiling enforced at $0.50 per invocation)
- GRC corpus of 31 sanitized documents as the only knowledge base

### 2.3 Out of Scope

- Multi-tenant SaaS operation
- Automated remediation (all recommended actions are advisory, mediated through HITL per HITL_POLICY.md)
- Alert volumes above the cost ceiling (HTTP 429 with `cost_ceiling_exceeded`)
- Use as a substitute for an analyst on CRITICAL severity investigations (HITL is required per HITL_POLICY.md section 3)

### 2.4 Users

| Role | Access | Surface |
|------|--------|---------|
| Owner | full | Teleport to alpha-node, Langfuse UI, all APIs |
| Interviewer | demo token | `/alert` with `SQUIRE_INTERVIEW_TOKENS` entry |
| Integration (n8n, Falco) | production webhook token | `/alert` with `SQUIRE_WEBHOOK_TOKEN` |

---

## 3. Factors

Factors that meaningfully shift Squire's behavior, drawn from evaluation data and operational observation.

### 3.1 Alert Modality

- **Shell exec signals** (Falco `shell_in_container`, `sudo_potential_privilege_escalation`): best-performing modality, p95 latency 55s on API backend
- **Credential leak signals** (gitleaks webhook, Datadog security signals): second best, p95 latency 62s
- **Ambiguous DDOS-shaped signals**: worst, p95 latency 78s, citation validity rate drops to 82%

### 3.2 Backend Choice

- `api` backend: p95 latency 55-80s, cost $0.12-$0.38 per invocation
- `max` backend: p95 latency 3-5 min (CLI overhead, subscription-speed), cost $0 marginal
- `ollama` backend: p95 latency 25-40s, citation validity drops to ~45% (local models do not follow the citation contract consistently)

### 3.3 Corpus State

Squire is only as good as the pgvector corpus. The initial 31 GRC docs give it strong grounding on this system. Corpus drift (doc updates not re-embedded) is the silent failure mode. Re-embedding job schedule is covered in AI_AUDIT_TRAIL_SPEC.md section 5.

---

## 4. Metrics

Observed on the current 62-test suite plus 10 canonical integration fixtures, captured in Langfuse project `Squire` (id cmobbrs8f0006rt07bz3q73jj).

| Metric | Target | Observed (api backend) | Observed (max backend) |
|--------|--------|-----------------------|-----------------------|
| Latency p50 | < 60s | 47s | 3.2 min |
| Latency p95 | < 90s | 82s | 5.1 min |
| Cost per invocation p95 | < $0.50 | $0.38 | $0 marginal |
| Citation validity rate | > 95% | 97.2% | 96.8% |
| Critique loop rate | < 35% | 28% | 32% |
| Red-team pass rate (17-11, pending) | > 85% | deferred until credit restored | deferred |

Per-node timing (Opus 4.7 primary, API backend):

| Node | p50 | p95 |
|------|-----|-----|
| classify | 8s | 12s |
| retrieve | 1.2s | 1.5s |
| enrich | 1.5s | 2.5s |
| investigate | 25s | 29s |
| draft | 43s | 70s |
| critique | 7s | 12s |
| route_severity | 0.05s | 0.1s |

Per-node evidence rows are written to `ir_investigations` for every invocation. See AI_AUDIT_TRAIL_SPEC.md.

---

## 5. Training Data

**Not applicable.** Squire is a RAG system over proprietary foundation models. No fine-tuning. No weight updates. The three foundation models were trained by Anthropic and OpenAI on proprietary corpora; provider training data disclosures apply.

Retrieval corpus is the 31 sanitized GRC documents under `docs/grc/`. Embedding pipeline is documented in ADR_001_EMBEDDING_PROVIDER.md.

---

## 6. Evaluation Data

### 6.1 Canonical Fixtures

10 canonical alerts in `builds/squire/tests/fixtures/`:

| Fixture | Modality | Expected Severity |
|---------|----------|-------------------|
| falco_shell | shell exec | HIGH |
| cred_leak_git | credential leak | HIGH |
| sudo_esc | privilege escalation | CRITICAL |
| dd_ddos_baseline | DDOS | MEDIUM |
| (6 more) | mixed | mixed |

### 6.2 Red-Team Suite

20+ cases defined in AI_RED_TEAM_PLAN.md; execution scheduled under plan 17-11 once Anthropic credit is restored. Cases cover prompt injection (IGNORE PREVIOUS INSTRUCTIONS variants), tool misuse, citation fabrication, and cost-ceiling evasion.

### 6.3 Ground Truth

Severity labels and MITRE technique mappings for canonical fixtures were authored by the system owner against the published Falco rules and verified against MITRE ATT&CK Enterprise v15.1.

---

## 7. Ethical Considerations

### 7.1 Autonomy

Squire never acts. `actions.yml` uses `enforcement_mode: rewrite` to prepend `RECOMMEND: human operator should ...` to every forbidden verb. The output rail ensures the model cannot fabricate autonomous verbs even under adversarial input. HITL gates are required for HIGH and CRITICAL severities per HITL_POLICY.md.

### 7.2 Bias and Fairness

Squire triages machine-generated alerts, not human behavior. Bias risk is primarily in severity classification: the classifier node could systematically under-call or over-call certain signal types. Evaluated on the 10 fixtures; drift monitored via Langfuse score distributions.

### 7.3 Privacy

Alert payloads may contain process paths, container IDs, and (in worst case) credentials that leaked into logs. Defense-in-depth:

1. `pre_graph_pii.py` regex scanner strips SSN, Luhn CC, email, phone before `graph.invoke`
2. NeMo input rail runs presidio PII detection on draft and critique nodes
3. Langfuse traces mask known secret patterns before persist

### 7.4 Dual-Use

Squire's outputs describe attack techniques, which could in theory assist an attacker. Mitigation: outputs are only returned to authenticated webhook consumers; the public demo endpoint is token-gated with ephemeral tokens (HITL_POLICY.md section 6).

---

## 8. Caveats and Limitations

- **Credit-gated operation.** API backend requires live Anthropic credit. Ollama fallback is functional but citation quality degrades.
- **Single-tenant.** No tenant isolation in the codebase. Multi-tenant use would require namespacing `ir_*` tables and per-tenant cost ceilings.
- **No continuous re-embedding.** Corpus drift is a manual catch today.
- **NeMo rails partial.** Presidio PII rail is live. PolicyAI self-check is commented out pending credit rebalance. GLiNER and PINT v2 deferred.
- **Cost ceiling is best-effort.** Two concurrent sub-ceiling reads can both pass; Redis atomic counter upgrade is Phase 18+.
- **Temperature quirk.** Opus 4.7 rejects the `temperature` parameter. APIBackend omits it for that model. Downstream code that relies on deterministic sampling should account for this.
- **Citation contract is model-dependent.** Opus 4.7 and Sonnet 4.6 respect the structured citation format in prompts. Local models under the `ollama` backend follow the contract inconsistently. Citation validity rate of 45% on Ollama is the dominant limitation of the degraded path.
- **Critique loop is self-scoring.** The critique node evaluates its own prior draft. Adversarial pressure that survives the critique loop is possible. The red-team suite in plan 17-11 is the primary evidence that the loop catches common failure modes; the suite has not yet run at the time of this card because Anthropic credit was $0.
- **Cost telemetry is post-hoc.** Token costs are read back from provider response metadata. A sustained provider pricing change between the token count and the cost calculation could under-report cost. The cost ceiling is still enforced on the model-reported token count, which is the reliable figure.

### 8.1 Known Failure Modes

- Classifier under-calling CRITICAL on ambiguous signals. Mitigated by the HITL gate on HIGH, which catches the common case where a CRITICAL was classified HIGH.
- Citation drift when the underlying GRC doc is edited without re-embedding. Detection is operational, not automated; the 60-day review in AI_SUPPLY_CHAIN_REGISTER.md surfaces this.
- Rail rewrites masking legitimate autonomous language. A draft that legitimately says "the system automatically rotated the token" gets rewritten to advisory form, which reads awkwardly but does not lose information. Acceptable tradeoff.
- Backend degraded silently on Ollama path if the ollama container is restarting. The `backend_degraded` flag is set when fallback fires, but an outage during the fallback itself is possible. Datadog monitor trips on sustained `backend_degraded=true` rate.

---

## 9. Provenance

| Aspect | Detail |
|--------|--------|
| Foundation models | Anthropic (Opus 4.7, Sonnet 4.6), OpenAI (text-embedding-3-large) |
| Orchestration | LangGraph 0.2+, LangChain 1.0+, langchain-anthropic 0.3+ |
| Observability | Langfuse v3 self-hosted at langfuse.example-ops.com |
| Guardrails | NeMo Guardrails v0.21.0, presidio PII via `[sdd]` extra |
| Hosting | alpha-node (Ubuntu 24.04, Docker Compose) |
| Repository | github.com/ET-sec/cyber-squire1, `builds/squire/` |
| Model card author | Information Security Officer |

For full component inventory including licenses, hashes, and risk scores, see AI_SUPPLY_CHAIN_REGISTER.md.

---

## 10. Degraded Mode Semantics

Squire treats the `ollama` backend as a degraded fallback, not an equal peer to the API backend. The backend abstraction is intentional so the fallback path is code-complete, but the semantics of a degraded invocation differ in three ways that operators must understand.

### 10.1 Output Envelope Flag

Every `/alert` response carries `backend` and `backend_degraded` fields. When Ollama served the invocation, `backend_degraded=true`. Downstream consumers (n8n, the Telegram notifier, the Langfuse trace annotation) read this flag and tag the investigation accordingly. A degraded investigation is not trusted equivalently to a non-degraded one; HITL reviewers see the flag in the notification.

### 10.2 Citation Suppression

When `backend_degraded=true`, the citation validity rate is materially lower. Rather than emit citations that may not resolve into the GRC corpus, the draft node running under Ollama emits citations but marks them as unverified. The downstream critique pass tests each citation against the pgvector corpus; citations that do not match a real chunk are stripped before the response is returned. The stripped-citation count is logged as a sanitization event.

### 10.3 Cost Accounting

Ollama invocations have no provider-reported token cost. Cost accounting under `ollama` records the wall-clock latency and the number of input and output tokens, but populates `cost_usd=0` with a metadata flag. The cost ceiling cannot be meaningfully enforced on Ollama; the ceiling code path short-circuits when `backend=ollama` and relies on the invocation timeout instead.

### 10.4 When Degraded Mode Activates

Three triggers promote degraded mode:

1. Explicit operator choice via `SQUIRE_BACKEND=ollama` or the `x-squire-backend: ollama` header
2. API backend failure (HTTP 5xx from Anthropic, timeouts, or `credit_balance_too_low`) and `SQUIRE_FALLBACK_OLLAMA=true`
3. Air-gap or interview-demo operating mode where external API calls are policy-prohibited

The second trigger is opt-in. A Squire with fallback disabled surfaces the API failure as a 500 response rather than silently downgrading, which is the safer default for production use.

---

## 11. Cross-References

- HITL_POLICY.md (mandatory human gates for HIGH and CRITICAL)
- AI_AUDIT_TRAIL_SPEC.md (what is logged, where, how long)
- SQUIRE_DATA_FLOW_CLASSIFICATION.md (data classes, retention, sanitization)
- AI_SUPPLY_CHAIN_REGISTER.md (component inventory, hashes, risk scores)
- POLICY_AI_GOVERNANCE.md (parent governance framework)
- AI_THREAT_CATALOG.md (threat model this card mitigates)
- ADR_001_EMBEDDING_PROVIDER.md (embedding provider selection rationale)
