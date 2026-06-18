# LLM / AI Security Cheatsheet

One pager. Memorize.

## OWASP LLM Top 10 v2 (2025)

| ID | Name | One-line defense |
|---|---|---|
| LLM01 | Prompt Injection | XML untrusted-input wrapper, system prompt names the wrapper, output validation on every tool call |
| LLM02 | Sensitive Information Disclosure | Server-side output filter, allowlist hosts in markdown images, hash prompts at rest, redact PII before persistence |
| LLM03 | Supply Chain | Pin model digests, sign and verify checkpoints, SBOM in CI, scanned model registry, dependency allowlist |
| LLM04 | Data and Model Poisoning | Provenance tags per chunk, trust tiers in retrieval, anomaly detection at ingest, audited training data |
| LLM05 | Improper Output Handling | Treat output as untrusted, schema validation, no `eval` on model output, sandboxed code execution |
| LLM06 | Excessive Agency | Per-role tool allowlist, JIT credentials with short TTL, human approval on destructive verbs |
| LLM07 | System Prompt Leakage | Do not put secrets in the system prompt, assume it leaks, design as if public |
| LLM08 | Vector and Embedding Weaknesses | Encrypt regulated embeddings, retrieval audit log, embedding drift alerts, similarity floor on retrieval |
| LLM09 | Misinformation | Citation requirement, refuse-out-of-scope rule, fact-check rail on output, periodic golden-set eval |
| LLM10 | Unbounded Consumption | Per-user token quota, max-tokens cap, conversation length cap, daily budget circuit breaker |

## MITRE ATLAS top techniques

| ID | Name | Tactic |
|---|---|---|
| AML.T0051 | LLM Prompt Injection | Initial Access |
| AML.T0054 | LLM Jailbreak | Defense Evasion |
| AML.T0057 | LLM Data Leakage | Collection |
| AML.T0024 | Exfiltration via ML Inference API | Exfiltration |
| AML.T0048 | External Harms | Impact |
| AML.T0049 | Exploit Public-Facing Application | Initial Access |
| AML.T0010 | ML Supply Chain Compromise | Initial Access |
| AML.T0020 | Poison Training Data | Resource Development |
| AML.T0043 | Craft Adversarial Data | ML Attack Staging |
| AML.T0029 | Denial of ML Service | Impact |

## Anthropic / OpenAI defense patterns

- Role separation, wrap all untrusted content in XML tags, system prompt names the tag and forbids following instructions inside it.
- Prompt sandwich, user instruction before the untrusted block, reasserting closing instruction after.
- Output validation, every tool call goes through a JSON schema validator and a per-role allowlist before any side effect fires.
- Two-rail Constitutional AI, input rail classifier blocks obvious attacks, output rail critic checks reply against a written constitution before delivery.
- Citation requirement, customer-facing answers must cite the source from the authorized corpus or refuse out of scope.
- Provenance per chunk in RAG, trust tiers, retriever filters by tier per query type.
- JIT credentials, short TTL tokens scoped per workflow run, never long-lived broad-scope tokens.
- Human in the loop on destructive verbs, never let the agent fire delete, drop, wipe, ban, send-money without a signed approval.

## Top tools

- **Garak** (NVIDIA, OSS), `pip install garak`. nmap-for-LLMs vulnerability scanner. Probes for prompt injection, jailbreaks, encoding bypasses, leak risks, toxicity.
- **Promptfoo** (OSS), YAML-driven LLM eval and red team in CI. Assertions like `not-icontains`, `contains-json`, `llm-rubric`. Pairs with any provider.
- **NeMo Guardrails** (NVIDIA, OSS), Colang-defined dialog flows and rails. Input, dialog, retrieval, output rails.
- **Lakera Guard** (commercial), low-latency prompt-injection classifier API. Fast first line in production.
- **Robust Intelligence** (commercial), enterprise model risk platform. Continuous validation, governance.
- **Microsoft PyRIT** (OSS), red team automation framework, generates adversarial prompts at scale.
- **Llama Guard** (Meta, OSS), small classifier model for safety screening, runs locally.
- **Presidio** (Microsoft, OSS), PII detection and redaction for LLM logs and prompts.

## Real incidents to cite

| Incident | Year | Lesson |
|---|---|---|
| Microsoft Tay | 2016 | Adversarial fine-tuning via crowd input; alignment is fragile under user pressure |
| Bing Sydney leak | Feb 2023 | System prompts are not secrets; treat as design notes |
| Greshake indirect injection | 2023 | "Not what you've signed up for" paper; agents reading hostile content |
| ChatGPT plugin SSRF | 2023 | Tools without validation become RCE |
| LangChain CVE-2023-29374 | 2023 | `LLMMathChain` `eval` sink; classic LLM05 |
| PoisonGPT | Jul 2023 | Mithril Security; model registry supply chain |
| Air Canada chatbot lawsuit | Feb 2024 | LLM09 Misinformation; legal liability for hallucinations |
| Many-shot jailbreaking | Apr 2024 | Anthropic; long-context shot stacking |
| PoisonedRAG | 2024 | Zou et al; 5 docs in 1M for 90 percent attack success |
| Sleeper Agents | 2024 | Anthropic; backdoors that survive safety training |

## Frameworks for governance

- **NIST AI RMF AI 100-1** (Jan 2023), four functions: Govern, Map, Measure, Manage.
- **NIST AI 600-1 GenAI Profile** (Jul 2024), GenAI-specific risks and controls layered on the core RMF.
- **ISO/IEC 42001:2023**, AI Management System (AIMS) standard, certifiable, Annex A controls for the lifecycle.
- **EU AI Act** (2024), risk tiers: prohibited, high-risk, limited-risk, minimal. Most LLM apps land in limited-risk; high-risk if they affect employment, law enforcement, education access.
- **Anthropic Responsible Scaling Policy**, capability-tied safety levels.
- **OpenAI Preparedness Framework**, similar shape.

## Logging signals to watch

- Sudden token burn per user or per workflow (LLM10).
- Refusal rate spike on a route (active jailbreak campaign).
- New tool-call pattern (excessive agency in motion).
- New outbound URL host in model output (exfil attempt).
- New retrieval source dominating top-k (RAG poisoning).
- Long-context shot-stacking shape (many-shot jailbreak).
- High base64 ratio in user prompts (encoding bypass).
- Persona keywords in user prompts (DAN, AIM, developer mode).

## Quick-reference defense ladder

1. Input rail (block obvious attacks before the model sees them).
2. Untrusted-input wrapper (treat all external content as data).
3. Hardened system prompt (names the wrapper, refuses to leak self).
4. Output rail (constitutional critic on every reply).
5. Tool gate (per-role allowlist, schema validation).
6. Egress filter (markdown image allowlist, URL allowlist).
7. Human approval (destructive verbs).
8. JIT credentials (short TTL, scoped).
9. Logging (prompt hash, tool calls, retrieval IDs, outputs).
10. Detection (Falco rules, Datadog alerts, anomaly thresholds).
11. CI evals (Promptfoo, Garak on every prompt change).
12. Quarterly red team (human attacker plus PyRIT plus Lakera Red).
