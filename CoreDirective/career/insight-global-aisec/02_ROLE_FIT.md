# 02 — Role Fit (JD phrase by phrase)

## Top-line read

This JD reads as a **legitimate AI Sec Eng role** built on top of an existing Microsoft Security stack. The 1-year contract framing plus the EU AI Act August 2026 deadline strongly suggests a compliance-driven build. Emmanuel is a strong conceptual fit. The vendor-surface gap on Microsoft Security Copilot + Defender for Cloud is the only material risk.

Fit estimate: **70-75%** (lower if end client demands deep MS hands-on, higher if they value AI sec breadth + governance authoring)

---

## JD phrase → Emmanuel evidence map

### "Bachelor's degree or equivalent experience in computer science"
- Georgia State, Cybersecurity major + Economics minor, BBA expected May 2026
- Eight semesters of practitioner work alongside school
- Verdict: **Pass**

### "Relevant certifications: OSCP, CEH, CISSP, or emerging AI security credentials a plus"
- Hold: SecurityX (CASP+), SSCP, CCNA, Security+
- In progress: CISSP (sitting Aug 2026)
- AI-specific: 37 GRC documents authored covering AI governance, AI threat modeling, AI IR
- Verdict: **Pass.** CISSP-IP > OSCP/CEH for this role's governance lean. Lead with CISSP and the GRC body of work.

### "3+ years of hands-on experience in security operations and AI tools usage"
- Texaco AppSec/SecEng: Mar 2022 → Feb 2026 (~4 years)
- CoreDirective AI Security Engineer: 2024 → present (overlapping)
- AI tools usage: Anthropic API in production, OpenClaw gateway, Ollama + Whisper, Datadog AI ops, n8n SOAR with LLM-driven triage
- Verdict: **Pass with margin**

### "Experience with Microsoft Security Copilot and Defender for Cloud"
- Hands-on: **none.** Honest answer.
- Adjacent: Datadog (SIEM analog), Falco + Sidekick (Defender XDR analog), Sentinel concepts via reading-level study
- Reframe: "I run the same control plane on a different vendor stack. Ramp time on the Microsoft UI is days. Ramp time on the concepts is zero."
- Verdict: **Material gap.** Acknowledge directly. Do not bluff.

### "Knowledge of AI governance frameworks such as NIST AI RMF, ISO 42001, or the EU AI Act"
- Authored 37 GRC docs sanitized for public release, including AI Governance Policy and AI Incident Response Playbook
- NIST AI RMF mapping done in SQUIRE_THREAT_MODEL.md
- ISO 42001 reading-level fluency, framework comparison published
- EU AI Act high-risk timeline tracked (Aug 2026 obligations)
- Verdict: **Strength. Lead with this.**

### "Familiarity with MLOps pipelines, model registries, and the security considerations of deploying AI in production"
- Production deployment: Ollama + Whisper containers under Falco runtime detection, Vault secrets, Cloudflare zero-trust ingress
- Model registry: have not run a formal one (MLflow, AzureML, SageMaker). Read-level only.
- CI/CD guardrails for AI: Trivy + Semgrep + Gitleaks + Cosign on COREDIRECTIVE_ENGINE pipelines
- Verdict: **Mixed.** Strong on production deployment + supply chain. Weak on formal model registry tooling.

### "Background in threat intelligence or adversarial machine learning research"
- Threat intel: STRIDE + MITRE ATLAS authored, threat models for OpenClaw + n8n SOAR
- Adversarial ML: prompt injection testing against the Anthropic API, Ollama jailbreak experiments
- Research-level: read-level on poisoning, inversion, extraction, backdoor patterns
- Verdict: **Pass for "or" gate.** Threat intel is the stronger half of the OR.

---

## Day-to-day phrase mapping

### "Use AI offensively to find our weaknesses before adversaries do"
- AI red teaming. Maps to Emmanuel's prompt-injection work on Anthropic + Ollama, plus the broader CoreDirective AppSec posture.
- Reframe if asked for a specific tool: "I have not run PyRIT or Garak in production. I have run the same patterns against my own LLM endpoints using custom payloads via the Anthropic API."
- Honest tool gap: PyRIT, Garak, Counterfit. Read-level only.

### "Secure the AI systems we depend on"
- Direct hit. The COREDIRECTIVE_ENGINE production stack is exactly this scope.
- Lead with: Falco runtime detection on Ollama, Vault for API keys, Cloudflare zero-trust, OPA policies, 37 GRC docs.

### "Embed intelligent automation into every layer of our security practice"
- n8n SOAR with LLM triage, MASTER_ORCHESTRATOR_V1 routing 16 actions
- 80%+ triage reduction
- This is the strongest single positioning anchor in the JD

### "Copilot, internal chatbots, and third-party AI services configured securely"
- Internal chatbot: @CDirective_bot (OpenClaw + Claude Opus 4.7), @Coredirective_bot (n8n)
- Third-party AI services: Anthropic, OpenAI (read-level), Tavily, Perplexity, Notion AI — all routed through OpenClaw with Vault-managed keys
- Copilot: gap. Acknowledge.

### "Continuously monitored"
- Datadog Agent + Falco + Sidekick + Fluentd shipping to Datadog
- 200 → 12 alerts (precision/recall on production AI workloads)
- This is a precision-and-recall conversation Emmanuel can lead from front

---

## Bridge statement (use verbatim if asked the gap question)

"My production AI security work runs on the open-source and Anthropic stack: Falco for runtime, Vault for keys, OPA for policy, n8n for SOAR, Anthropic API direct for inference. The Microsoft equivalents — Defender for Cloud, Sentinel, Security Copilot, Purview — are different vendor surfaces of the same control plane. I have not run them in production. I read their docs and I understand the data model. The ramp on the tooling is days. The ramp on the concepts is zero. Where I add value Day One is the AI governance authoring, the offensive testing, and the SOAR integration. The Microsoft tooling I learn while delivering."

---

## Honest gap reframes (drill out loud)

### Gap 1: MS Security Copilot
"I have not run Security Copilot. I have run an equivalent SOC LLM workflow through n8n calling the Anthropic API directly. Same pattern: natural language → query → triage → action. Different vendor wrapper. I would expect a one-week ramp to fluency on the Copilot UI and embedded skill packs."

### Gap 2: Defender for Cloud
"I have not run Defender for Cloud. I run posture management with Falco at runtime and OPA at admission, and threat protection with Falco + Sidekick → Datadog. The 2026 AI-SPM features in Defender are concepts I have already implemented; the vendor mapping is what I would learn."

### Gap 3: Model registry
"I have not stood up MLflow or Azure ML model registry in production. I have implemented the supply-chain controls those registries enforce — model signing analog via Cosign for containers, training data lineage via Datadog, RBAC via Keycloak. The model-registry-specific UI is the part I would learn."

### Gap 4: PyRIT / Garak
"I have not run PyRIT or Garak. I have run prompt injection and jailbreak testing against Anthropic + Ollama using custom payload sets. The methodology transfers; the tooling I would adopt in week one."

---

## What to bring to the front in 60 seconds

1. AI Security Engineer at CoreDirective + 4 years AppSec at Texaco
2. 80%+ SOAR triage reduction with LLM-in-the-loop
3. 37 GRC documents authored, sanitized, public — including AI Governance Policy and AI IR
4. Threat models executed against the live AI stack (OpenClaw, n8n, Ollama)
5. CISSP April 2026, SecurityX, SSCP, CCNA, Security+
6. Honest line: "Microsoft Security Copilot and Defender for Cloud are net-new tooling for me. The control plane underneath them is what I do every day."
