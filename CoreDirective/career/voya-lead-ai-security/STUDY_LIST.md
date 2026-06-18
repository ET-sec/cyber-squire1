# Voya Lead AI Security Engineer — Study List

Tiered by must-know vs high-probability vs nice-to-have. Heat map: green = strong, yellow = needs sharpening, red = real gap.

## TIER 1: must-know (before the live build round)

### TypeScript (yellow → green) — 8 hours over 4 days
- Build a prompt injection test harness in TypeScript. Sample prompts in JSON, run through OpenAI / Anthropic SDK, evaluate against allow / deny rules.
- Drill: tagged template literals for prompt construction, zod schema validation on LLM output, async generators for streaming abuse detection.
- Resource: typescriptlang.org/docs/handbook/utility-types.html and the Anthropic TypeScript SDK reference.

### Go (red → yellow) — 12 hours over 5 days
- Goal: pass the live build round, not become fluent.
- Focus: net/http reverse proxy that intercepts LLM requests, context cancellation, JSON tag struct unmarshaling, table-driven tests.
- Resource: go.dev/tour, the Anthropic Go SDK README, one example of an HTTP middleware in Go.
- If they offer choice: pick TypeScript.

### Prompt injection and jailbreak taxonomy (green → green sharper) — 4 hours
- OWASP LLM Top 10 2025: walk every category and name your defense for each.
- MITRE ATLAS: AML.T0051 (LLM Prompt Injection), AML.T0054 (LLM Jailbreak), AML.T0057 (LLM Data Leakage). Memorize the IDs.
- Examples to internalize: direct injection, indirect injection via RAG, payload smuggling, role-play jailbreaks, output exfiltration.
- Resource: simonwillison.net prompt injection archive, owasp.org/www-project-top-10-for-large-language-model-applications.

### MCP and function calling security (yellow → green) — 4 hours
- Read the official MCP spec end to end: spec sections on tool discovery, capability negotiation, sandboxing.
- Threat model: tool spoofing, capability escalation, prompt injection via tool descriptions, side-channel data leakage.
- Defense patterns: tool allowlists, capability scopes, response schema validation, blast-radius limits per call.
- Resource: modelcontextprotocol.io/specification and the Anthropic MCP blog post on agent security.

## TIER 2: high-probability (before the red-team exercise)

### Tenant isolation patterns (yellow) — 3 hours
- Logical partitioning at the prompt layer (system prompt enforces tenant ID)
- RAG isolation: per-tenant vector namespaces, retrieval filters as a security control
- Tool-call isolation: per-tenant API keys, per-tenant rate limits, per-tenant audit logs
- Voya specific: OneAmerica migration through 2026 means 8M new participants joining the platform. Tenant isolation under migration is the live blast radius.

### Do-not-train and data residency (yellow) — 2 hours
- Workday Wellness AI partnership (Sep 2025): data flows out of Voya. Do-not-train and residency must hold at the contract layer AND the security layer.
- ERISA fiduciary obligations on participant data
- Voya WealthPath built with Orion (advisor surface). Different data class than participant surface.

### Autonomy red-teaming methodology (green) — 2 hours
- Capability gate framework: what can the agent do, what can it spend, what can it write to, what can it tell the user
- Promotion gate: red team before promotion, red team after promotion
- Findings feed back into the autonomy decision

## TIER 3: nice-to-have (before the domain + governance round)

### ERISA AI governance (red) — 3 hours
- Benefits Law Advisor July 2025: "Harnessing AI Under ERISA" guide. Read end to end.
- March 31 2026 EBSA proposed AI rule (if final by interview date)
- Fiduciary sensitivity of outputs: what a manipulated participant agent output could do to a participant's retirement decision
- Frame for the panel: AI security IS fiduciary risk management

### Azure AI Foundry mental model (red) — 2 hours
- Goal: speak to the platform, not claim production experience
- Foundry = unified AI development platform on Azure (model catalog, prompt flow, evaluation)
- Databricks = Unity Catalog for data governance, MLflow for model registry
- Honest framing: "The threat model transfers. The runtime details I would ramp in 30 days."

## Heat map summary

| Topic | Status |
|---|---|
| LLM prompt injection theory | GREEN |
| OWASP LLM Top 10 | GREEN |
| MITRE ATLAS | GREEN |
| MCP tool security | GREEN |
| Promptfoo / eval harness | GREEN |
| Adversarial testing as code | GREEN |
| Python | GREEN |
| TypeScript | YELLOW (drill before live build) |
| Go | RED (drill or pick TS) |
| Rust | RED (acknowledge gap) |
| Azure AI Foundry | RED (acknowledge gap, transfer pattern) |
| Databricks | RED (acknowledge gap) |
| ERISA | RED (one focused session, frame as adjacent governance) |
| Tenant isolation at scale | YELLOW |
| Do-not-train enforcement | YELLOW |
| NIST AI RMF | GREEN |
| ISO 42001 | GREEN |

## Time budget

- Days 1 to 3: Tier 1 TypeScript + Go drill (20 hours total)
- Day 4: Tier 1 prompt injection + MCP sharpening (8 hours)
- Days 5 to 6: Tier 2 tenant isolation + do-not-train + autonomy red-team (7 hours)
- Day 7: Tier 3 ERISA + Azure Foundry (5 hours)
- Day 8: Full mock interview run-through, all 7 stages

Total: 40 hours over 8 days. If recruiter screen lands sooner, prioritize Tier 1 only.
