# Pre-Call Cheat Card - Milestone Tech (Elena Novo first, then end client)

## Opening line (first 5 minutes)
"Most candidates can name AI-SPM vendors. I run a production agentic stack with Langfuse evals (4 evaluators, 12 golden fixtures), OPA Rego policy gates, dual-source budget guard, sanitize_output blocking 10 PII patterns, and a POAM tracking residuals from two red-team cycles. Public artifacts at github.com/ET-sec/cyber-squire1 if you want to see the code before we talk."

## 3 killer talking points
1. **Production-grade AI guardrails today.** NeMo Guardrails + GLiNER PII redaction + OPA Rego on every model call. Not theory.
2. **Eval cadence.** Langfuse harness with 4 evaluators (groundedness, refusal, PII leak, prompt injection) gating model promotion in CI. Most contractors have read about Promptfoo. I run an evaluator weekly.
3. **Governance translates to enforced controls.** EU AI Act and GDPR mapped to OPA Rego rules, POAM entries, and IR playbook. Not paper compliance.

## Honest gap pivots

### "How many years AWS production?"
"Bedrock and Terraform are my current AWS surface. My production cloud footprint is DigitalOcean and Cloudflare with full Terraform IaC, OPA Rego admission, Falco eBPF runtime detection, Vault, Keycloak SSO, Teleport JIT PAM. Same engineering pattern, different cloud. I would expect a two-week ramp on AWS service specifics (IAM Identity Center, KMS, GuardDuty, SSM Session Manager) and full velocity by week three."

### "Walk me through Bedrock Guardrails in production."
"Content filters tuned per harm category at HIGH for both input and output, denied topics for PII categories the business cannot process, contextual grounding checks at 0.7+ to catch hallucinations against retrieved context, and ApplyGuardrail API standalone so non-Bedrock models route through the same policy. Wire CloudTrail data events for InvokeModel, scope IAM with aws:SourceVpce conditions, customer-managed KMS for prompt and response encryption. I have shipped this in lab; my production runtime guardrail patterns are NeMo + OPA + Langfuse trace inspection on the same threat model."

### "Have you shipped Databricks production?"
"No production Databricks. I have studied Unity Catalog and MLflow Registry security patterns during AI-SPM evaluation. Three-level namespace, lineage tracking, service principal access, signed model artifacts on Registry transitions - those map directly to controls I already enforce on pgvector + custom registry today. Two-week ramp."

### "Have you used UiPath?"
"No UiPath exposure. My RPA-equivalent is n8n agentic workflows with Execute nodes, which carry the same threat model: credential vault, untrusted input to executors, lateral movement through service accounts. UiPath Orchestrator security model (Asset store, robot identity, queue ACLs) maps to controls I already write for n8n."

### "How do you cap runaway tool calls from prompt injection?"
"Hard token + tool-call budget per session at the gateway, circuit breaker on anomalous spend velocity, dual-source reconciliation (provider API + internal counter), per-agent spend caps with auto-disable. I have it in production today as budget_guard.py with a SQLite spend ledger. Public if you want to see the code."

## Questions to ask Elena (recruiter screen)

1. Who is the end client? Industry, size, size of the AI security team this contract joins?
2. What is the team currently using for AI-SPM, runtime protection, and AI Gateway? Any active POCs?
3. What does the technical interview look like? Live code, system design whiteboard, scenario walk-through?
4. Why is this a contract and not full-time? Is there a contract-to-perm path if both sides want it?
5. Is the rate posted ($70/hr) firm or is there flex on the right candidate?

## Questions to ask the end-client technical screener
1. What does day 30 look like for this role? What ships?
2. What is the current state of AI guardrails on Bedrock and ChatGPT Enterprise?
3. How is Databricks workspace security split - centralized vs federated?
4. Who owns the EU AI Act and GDPR translation work today, and what is the current gap?
5. What is the relationship between this AI Security team and the broader Security Architecture / GRC org?

## Rate play sequence
1. Email reply already anchors at $95-$110 W2 with floor at $85.
2. If Elena counters at $80-$85: accept conditionally on the team and end-client name, ask for early renewal review.
3. If Elena counters at $70 firm: ask if they can do a 90-day rate review tied to a deliverable.
4. Walk away if they hold $70 firm with no review - $145K annualized for this scope is a step back, not a step forward.

## Closing line
"If your client wants engineering proof before the technical screen, my repo at github.com/ET-sec/cyber-squire1 has the Langfuse harness, OPA policies, FastMCP server, and budget guard live. They can read the code. Saves everyone time."
