# OWASP GenAI Top 10 (2026) to CoreDirective Stack Mapping

**Status (2026-09-01): mapped against the full 19-service design as it ran before the 2026-08 host migration.** Today 3 containers run on the OCI instance (PostgreSQL 16 with pgvector, n8n, the Cloudflare tunnel sidecar); the remaining services are design-tier until the ARM rebuild lands. "Covered" below means covered by the design baseline. Live today: the CI controls (Gitleaks, Trivy, Semgrep, SBOM, Sigstore signing), Doppler-only secrets, and the recommend-only design boundary. Design-tier until the rebuild: NeMo Guardrails, Langfuse, Vault, Keycloak, Teleport, Falco, Datadog, Ollama, and Squire itself. See `STACK_OVERVIEW.md` for the live-versus-designed breakdown.

Two lists ship under the OWASP GenAI Security Project.

1. **Top 10 for LLM Applications.** The original list. The 2026 refresh kept the same ten
   categories in the same order as 2025 (verified against the release, Aug 2026). Guidance and
   mitigations were refined. Rankings did not move.
2. **Top 10 for Agentic Applications (ASI01 to ASI10).** The newer list, and the one that actually
   stresses this stack, because Squire is a 7-node LangGraph agent with tool access, memory, and
   inter-node message passing.

Each risk below maps to the real components in `docs/architecture/STACK_OVERVIEW.md`:
Squire FastAPI (LangGraph, recommend-only), NeMo Guardrails 0.21 (Presidio PII rails, Colang
`BLOCKED_BY_RAIL`), Langfuse v3 tracing, PostgreSQL 16 + pgvector (1,564 ir_chunks), Anthropic API,
Voyage embeddings, n8n SOAR (16 actions), OpenClaw gateway, Vault / Keycloak / Teleport, Falco /
Datadog / Fluentd.

Columns: **Covered** is a control already in the stack. **Gap** is what an interviewer would poke at.

---

## Part 1. LLM Top 10 (2026, unchanged order from 2025)

### LLM01 Prompt Injection
Untrusted input (direct or via retrieved IR chunks) rewrites the model's instructions.
- **Covered:** NeMo Guardrails input rails plus Colang `BLOCKED_BY_RAIL`. Squire runs recommend-only,
  so a hijacked prompt cannot auto-execute a remediation.
- **Gap:** Indirect injection through the 1,564 pgvector `ir_chunks`. Content retrieved into context
  is not itself rail-filtered. Threat-hunt this: poisoned doc, then retrieval, then instruction override.

### LLM02 Sensitive Information Disclosure
Secrets, PII, or internal topology leak into prompts, outputs, or traces.
- **Covered:** Presidio PII rails. Doppler-only secrets, never in prompts. Langfuse self-hosted, so
  traces stay on the host, not a third-party SaaS.
- **Gap:** Langfuse traces capture full prompt and response pairs, so that store is now a PII sink.
  Confirm retention and access policy on the Langfuse Postgres and ClickHouse.

### LLM03 Supply Chain
Compromised models, packages, or embeddings enter the pipeline.
- **Covered:** Sigstore plus Rekor keyless signing on build artifacts. Gitleaks, Trivy, Semgrep in CI.
  SBOM on merge.
- **Gap:** NeMo Guardrails 0.21, LangGraph, Voyage and Anthropic SDKs pulled from PyPI. Pin and
  hash-lock them, and scan transitive deps. Model weights (Ollama fallback) provenance is unverified.

### LLM04 Data and Model Poisoning
Malicious content in training, fine-tune, or RAG corpus.
- **Covered:** You do not fine-tune. Models are hosted API (Anthropic), so the poisoning surface is
  mostly the RAG corpus, which is curated GRC docs you control.
- **Gap:** ir_chunks ingestion has no integrity gate. Ask who can write to the corpus, and whether a
  signed or reviewed pipeline runs before chunks land in pgvector.

### LLM05 Improper Output Handling
Model output consumed downstream without validation (SSRF, injection, code exec).
- **Covered:** Recommend-only mode is the strongest control here. Output is advisory text, not an
  executed action.
- **Gap:** The n8n SOAR path (16 actions) is where output becomes action. Any workflow that takes an
  LLM string and feeds it to `postgres`, `github`, or `gmail` without schema validation is the live risk.

### LLM06 Excessive Agency
Agent has more permission or autonomy than the task needs.
- **Covered:** Recommend-only Squire. Keycloak RBAC. Teleport JIT for privileged access.
- **Gap:** The n8n master orchestrator holds 16 broad action credentials in one workflow. Scope
  per-action least privilege. This is the biggest excessive-agency finding in the stack.

### LLM07 System Prompt Leakage
System prompt or instructions extracted by an attacker.
- **Covered:** Output rails can catch verbatim system-prompt echo.
- **Gap:** Assume the system prompt is discoverable and put no secrets in it. Rely on RBAC, not prompt
  secrecy. Audit the Squire node prompts for any embedded credential, path, or IP.

### LLM08 Vector and Embedding Weaknesses
Attacks on the pgvector store: poisoning, inversion, cross-tenant leakage.
- **Covered:** Single-tenant store. Voyage 1024-dim embeddings.
- **Gap:** No embedding-level access control. Every retrieval sees all 1,564 chunks. If the corpus ever
  mixes sensitivity tiers, you need per-chunk authz. Embedding inversion (reconstructing source text)
  is untested.

### LLM09 Misinformation
Model produces confident, wrong output that a human acts on.
- **Covered:** Recommend-only keeps a human in the loop. Langfuse lets you trace and grade answers.
- **Gap:** No grounding or citation enforcement. A Squire recommendation citing a nonexistent control
  would pass silently. Add a rule that it must cite the ir_chunk, and eval against it.

### LLM10 Unbounded Consumption
Cost or DoS from uncontrolled token or query volume.
- **Covered:** Datadog monitoring. Ollama local fallback caps external spend.
- **Gap:** No explicit rate limit or token budget on the Squire FastAPI endpoint. A loop that keeps
  re-invoking Anthropic is an unbounded-cost event. Instrument a per-session token ceiling.

---

## Part 2. Agentic Applications Top 10 (ASI, 2026), the list that hits Squire hardest

### ASI01 Agent Goal Hijack
Injected instructions redirect the agent's objective.
- **Squire exposure:** A LangGraph node that reads retrieved chunks or user text can have its goal
  rewritten. Recommend-only limits blast radius. Input rails are the first line.

### ASI02 Tool Misuse and Exploitation
Agent misuses legitimately-permitted tools (recursion, over-invocation, unsafe composition).
- **Squire exposure:** The n8n 16-action surface. A hijacked or looping agent could chain
  `tavily`, `gmail`, `github` in ways each individually permitted but collectively harmful. Top gap.

### ASI03 Agent Identity and Privilege Abuse
Delegated authority or ambiguous identity leads to unauthorized actions.
- **Squire exposure:** Does Squire act as itself or as the operator? Map every credential the agent
  can assume to a Keycloak identity. Teleport JIT should gate the privileged ones.

### ASI04 Agentic Supply Chain Compromise
Compromised external tools, schemas, or sub-agents.
- **Squire exposure:** OpenClaw gateway skills, Tavily, MCP-style tool schemas. Pin and verify tool
  definitions. A swapped tool schema is an injection vector.

### ASI05 Unexpected Code Execution
Agent-generated or agent-triggered code runs without isolation.
- **Squire exposure:** Recommend-only means Squire itself does not exec. Watch OpenClaw's
  python-interpreter skill. That is the code-exec surface. Confirm sandboxing.

### ASI06 Memory and Context Poisoning
Persistent agent memory or state corrupted to bias future runs.
- **Squire exposure:** LangGraph state plus pgvector retrieval feed future reasoning. Same root as
  LLM04 but time-shifted. A poisoned chunk influences every later session. Add corpus write-integrity.

### ASI07 Insecure Inter-Agent Communication
Messages between agents or nodes spoofed or injected.
- **Squire exposure:** The 7-node graph passes state node-to-node, plus Squire, n8n, and OpenClaw
  crosstalk. No signing or authentication on internal messages today. Trace one full path and note
  the trust boundaries.

### ASI08 Cascading Agent Failures
Small failure propagates system-wide.
- **Squire exposure:** Squire, then n8n, then external APIs. A malformed recommendation that n8n fans
  out to multiple actions is the cascade path. Falco and Datadog catch symptoms, not the causal chain.

### ASI09 Human-Agent Trust Exploitation
Humans over-trust a confident agent.
- **Squire exposure:** Recommend-only depends on the operator reading output critically. A polished
  wrong recommendation is the risk. It pairs with LLM09. Force citations so trust is verifiable.

### ASI10 Rogue Agents
Agent drifts from intent via misalignment or emergent behavior.
- **Squire exposure:** Lowest today (bounded 7-node graph, recommend-only). Becomes real if Squire
  ever gets write or execute mode. Langfuse behavioral baselining is the detection story.

---

## Sources
- OWASP Top 10 for LLM Applications: https://genai.owasp.org/llm-top-10/
- OWASP Top 10 for Agentic Applications 2026: https://genai.owasp.org/
