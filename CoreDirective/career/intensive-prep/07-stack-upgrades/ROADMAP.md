# CoreDirective Stack Upgrades: 14-21 Day Roadmap

**Owner:** Emmanuel Tigoue
**Window:** 21 calendar days, 6-week interview runway
**Goal:** Add 5 to 7 components that turn an already-shipping stack into demonstrable $200K AI Security Engineer evidence
**Constraint:** Each upgrade must be shippable in 1 to 3 days, runnable on cd-alpha (4 vCPU, 8GB) or free-tier, demonstrable in a 90-second interview walkthrough
**Frame:** You already do this work. These upgrades give it a public surface, a CI gate, or an artifact you can hand a Director of Engineering.

---

## Stack baseline (already shipping)

- 13 Compose services + OpenClaw gateway on cd-alpha (10.x.x.x)
- 14 active n8n workflows including MASTER_ORCHESTRATOR_V1
- 37 GRC documents in `docs/grc/`, 8 OPA Rego policies in `terraform/cd-do-infrastructure/`
- CI pipeline: Trivy, Semgrep, Gitleaks, SBOM, Cosign signing
- OWASP ZAP DAST clean run, IR playbooks including AI Incident Response
- Cloudflare Tunnel zero-trust ingress, Teleport v18 PAM with JIT
- Falco eBPF detection routing through Falcosidekick to Datadog us5

---

## Upgrade A. Promptfoo CI Gate Against OpenClaw

**Why:** Every senior AI security role asks "how do you know your model is safe after a change." A Promptfoo workflow on every commit is the cleanest answer. You already red-teamed OpenClaw manually. Make the harness a CI step.

**Scope.**
- `promptfoo-config.yaml` with 40 to 60 test cases: OWASP LLM Top 10, MITRE ATLAS, system prompt extraction, tool-call hijack, jailbreak corpus
- GitHub Action `.github/workflows/promptfoo-eval.yml` that runs against the OpenClaw chat-completions endpoint via tunnel-pinned token
- Threshold gate: any regression fails the build
- Public repo `ET-sec/openclaw-eval-harness` with sanitized config and result history

**Time.** 2 days. Day 1: write tests. Day 2: wire to GitHub Actions, ship first green run.

**Files he creates.**
```
~/cyber-squire-ops/builds/promptfoo-eval/
  promptfoo-config.yaml
  tests/owasp-llm-top10.yaml
  tests/mitre-atlas.yaml
  tests/tool-call-hijack.yaml
  README.md
.github/workflows/promptfoo-eval.yml
```

**Public artifact.** `github.com/ET-sec/openclaw-eval-harness` (new repo, sanitized fork)

**Interview talking-point.** "Every commit to my AI gateway runs a Promptfoo eval against the OWASP LLM Top 10 and MITRE ATLAS. If a model upgrade or a system-prompt change drops the score below threshold, the build fails. That's how I know an AI change is safe before traffic hits it."

**Best for.** Dropzone AI, Resilience, Insight Global, OneDigital. The eval-harness story sells hardest to anyone hiring for investigation quality or AI assurance.

---

## Upgrade B. NeMo Guardrails at the n8n LLM Boundary

**Why:** n8n nodes that hit Ollama or Claude are currently untrusted in both directions. Guardrails between the workflow and the model is a textbook AI security control and most candidates will have only read about it.

**Scope.**
- NeMo Guardrails container running on cd-alpha as `cd-service-guardrails` on port 8001
- Five rails: jailbreak detector, PII scrubber, secrets blocker, off-topic classifier, output content filter
- Sub-workflow `LLM_GUARDRAIL_PROXY` in n8n that wraps any LLM HTTP call
- Update Master Orchestrator to route every LLM action through the proxy

**Time.** 2 days. Day 1: container + rails config. Day 2: n8n wrapper workflow + cutover.

**Files he creates.**
```
~/cyber-squire-ops/COREDIRECTIVE_ENGINE/guardrails/
  config.yml
  rails/jailbreak.co
  rails/pii.co
  rails/secrets.co
  Dockerfile
~/cyber-squire-ops/COREDIRECTIVE_ENGINE/docker-compose.yaml  # add cd-service-guardrails
```

**Public artifact.** `docs/grc/AI_GUARDRAILS_DESIGN.md` (sanitized architecture doc, added to GRC corpus, brings count to 38)

**Interview talking-point.** "Every LLM call in my SOAR fabric goes through a NeMo Guardrails proxy. PII gets scrubbed, jailbreak patterns get rejected at the rail layer, off-topic prompts get refused before they hit the model. I treated the model the same way I treat the database: never let untrusted input land on it without a proxy."

**Best for.** Resilience (n8n engineer, this is the headline), OneDigital (AIDR/agentic), Brilliant Cloudflare (defensive ingress story).

---

## Upgrade C. Garak Scheduled Scans of Ollama

**Why:** Ollama is the local model. It is a soft target if anyone ever reaches it laterally. A scheduled Garak run is real model red-teaming on a real model and the output is a public report you can hand an interviewer.

**Scope.**
- Garak installed in a builder container, run nightly via systemd timer or GitHub Actions cron
- Scan profiles: `dan`, `promptinject`, `glitch`, `encoding`, `goodside`
- Results dumped to `docs/grc/AI_RED_TEAM_REPORT.md` and re-rendered each Sunday
- A `latest-scan.json` artifact uploaded to a GitHub Release on the eval repo

**Time.** 1 day.

**Files he creates.**
```
~/cyber-squire-ops/builds/garak-runner/
  Dockerfile
  run-garak.sh
  config/profiles.yaml
.github/workflows/garak-weekly.yml
docs/grc/AI_RED_TEAM_REPORT.md
```

**Public artifact.** Weekly scan report on the GRC index. Number-anchored: "X probes, Y findings, Z fixed."

**Interview talking-point.** "I run Garak weekly against my local Ollama instance. Five probe families, results land in a GRC document with a fix-by date. The point isn't catching every probe, it's keeping a number you can show a board: this is how the model's posture changed week over week."

**Best for.** Dropzone AI, OneDigital, Insight Global, Resilience.

---

## Upgrade D. Falco Rules Tuned for Agentic Abuse Patterns

**Why:** Most candidates know Falco for container syscalls. You already run Falco. The differentiator is custom rules tuned for AI agents misbehaving: tool calls outside allowlist, a model process spawning shell, a workflow process opening unexpected outbound. This is detection engineering applied to AI.

**Scope.**
- New rule file `falco_rules_agentic.yaml` with 8 to 12 rules covering: model container spawning shell, OpenClaw process opening non-egress connection, Ollama writing outside its volume, n8n container exec'ing into a shell, tool-call argument containing a known injection sigil
- Sigma equivalents in a sibling repo for portability
- Detections route through Falcosidekick to Datadog with severity mapping
- Test harness that triggers each rule on a non-prod replica

**Time.** 2 days. Day 1: write rules. Day 2: test, tune false positives, document.

**Files he creates.**
```
~/cyber-squire-ops/COREDIRECTIVE_ENGINE/falco/
  rules/falco_rules_agentic.yaml
  tests/test_agentic_rules.sh
docs/grc/DETECTION_RULES_AGENTIC.md
```

**Public artifact.** `github.com/ET-sec/falco-agentic-rules` with the rule file plus walkthrough README. This is the public detection-engineering portfolio he is missing.

**Interview talking-point.** "I wrote a Falco ruleset for agentic abuse. Twelve rules, each one tied to a specific MITRE ATLAS technique. If my OpenClaw container ever spawns bash, that's an alert. If Ollama opens an outbound socket that isn't loopback, that's an alert. I treat the AI processes the same as any other workload, with detection custom-tuned to what they shouldn't do."

**Best for.** Dropzone AI, OneDigital, WBD, Resilience. Detection-engineering proof for everyone.

---

## Upgrade E. Sigma Rule Library on GitHub

**Why:** Same instinct as Upgrade D, broader reach. Sigma is the lingua franca of detection engineering. A public Sigma library tied to your real Falco rules, MITRE ATT&CK + ATLAS mapped, is a senior portfolio piece.

**Scope.**
- `sigma-coredirective` repo with 15 to 25 rules, divided into `agentic/`, `cloud/`, `linux/`, `web/`
- Each rule has `references:` to a real CoreDirective use case (sanitized)
- README with ATT&CK + ATLAS coverage matrix
- A simple `sigma-cli` validation step in GitHub Actions

**Time.** 2 days. Pair with Upgrade D so Falco rules and Sigma rules ship together.

**Files he creates.**
```
~/cyber-squire-ops/builds/sigma-rules/
  agentic/llm_tool_call_hijack.yml
  agentic/excessive_agency_attempt.yml
  cloud/terraform_opa_violation.yml
  cloud/cloudflare_tunnel_off_zero_trust.yml
  linux/falco_agentic_mirror.yml
  README.md
  coverage-matrix.md
.github/workflows/sigma-validate.yml
```

**Public artifact.** `github.com/ET-sec/sigma-coredirective`

**Interview talking-point.** "I publish the Sigma rules I run in production. Twenty-something rules, mapped to ATT&CK and ATLAS, validated in CI. If you wanted to drop them in your own Splunk or Elastic, the schema is portable."

**Best for.** Dropzone AI, Resilience, OneDigital, WBD. Detection portfolio is universal currency.

---

## Upgrade F. AI Bill of Materials (AI-BOM)

**Why:** SBOMs you have. AI-BOMs almost no candidate has. CISA published the field guide. Producing one for CoreDirective Engine is a one-day artifact that distinguishes you in any GRC-leaning interview.

**Scope.**
- Markdown + JSON manifest listing every model, dataset, prompt template, and inference endpoint in the stack
- For each entry: provider, version, hash, training data category, license, data residency, fallback
- Render to `docs/grc/AI_BOM.md` plus machine-readable `ai-bom.json`
- Add to the SBOM CI workflow so it regenerates on commit when the manifest changes

**Time.** 1 day.

**Files he creates.**
```
~/cyber-squire-ops/builds/ai-bom/
  manifest.yaml
  generate.py
  schema.json
docs/grc/AI_BOM.md
ai-bom.json  # generated
.github/workflows/ai-bom.yml
```

**Public artifact.** Adds doc 38 to the GRC corpus, with a JSON sibling for tooling.

**Interview talking-point.** "I maintain an AI Bill of Materials alongside my SBOM. Every model, every prompt template, every inference endpoint is enumerated with version, hash, training-data category, and license. If a regulator asked me to demonstrate AI inventory tomorrow, I'd hand them the JSON."

**Best for.** OneDigital (AI Governance is a JD line), Insight Global, QGenda (HIPAA), Brilliant Cloudflare.

---

## Upgrade G. Real-Time Prompt-Injection Classifier at the Gateway

**Why:** Highest-ceiling upgrade. A small classifier inline at OpenClaw, scoring every prompt before it hits the model, with a published precision-recall curve. This is the build that puts you above other AI Sec Eng candidates because almost none of them have an inline detection model in production.

**Scope.**
- Pin a small classifier (DeBERTa-base or a Llama Guard variant) into a sidecar container
- Wire OpenClaw to call the classifier first, route high-risk prompts to a deny path that returns a refusal + Datadog alert
- Eval on a held-out test set, publish PR curve to a `docs/grc/PROMPT_INJECTION_CLASSIFIER.md`
- Latency budget: under 200ms p95 added to inference

**Time.** 3 days. Day 1: container + model. Day 2: gateway integration + Datadog. Day 3: eval, doc, curve.

**Files he creates.**
```
~/cyber-squire-ops/COREDIRECTIVE_ENGINE/pi-classifier/
  Dockerfile
  app.py
  model/
~/cyber-squire-ops/builds/pi-classifier-eval/
  eval.py
  test_set.jsonl
  pr_curve.png
docs/grc/PROMPT_INJECTION_CLASSIFIER.md
```

**Public artifact.** Doc 39 in GRC corpus + a public eval repo with the precision-recall curve.

**Interview talking-point.** "Every prompt at my gateway gets scored by a fine-tuned classifier before it reaches the model. p95 latency cost is under 200ms. Precision is point-eight-something on the test set. If a prompt scores past threshold, the model never sees it and Datadog gets a high-severity event. That's the part that puts a real number on AI defense in depth."

**Best for.** Dropzone AI (this is the investigation-quality story for AI inputs), OneDigital, Insight Global. Highest single-asset value.

---

## Upgrade H. Chainguard / Wolfi Base Images

**Why:** You have Trivy, Cosign, SBOM. The supply-chain story isn't complete without distroless or Wolfi base images. This is the closing move on the supply-chain narrative and it earns "you take supply chain seriously" credit instantly.

**Scope.**
- Migrate 4 of the 13 services to Chainguard/Wolfi base images, starting with anything custom-built (skill-runner sidecars, the AI-BOM generator, the PI classifier from Upgrade G)
- Re-run Trivy, document CVE delta in `docs/grc/SUPPLY_CHAIN_HARDENING.md`
- Cosign sign every rebuilt image, verify in CI

**Time.** 1 day.

**Files he creates.**
```
COREDIRECTIVE_ENGINE/<service>/Dockerfile  # FROM cgr.dev/chainguard/python:latest
docs/grc/SUPPLY_CHAIN_HARDENING.md
```

**Interview talking-point.** "I migrated my custom containers to Chainguard. CVE count dropped from N to M, every image is Cosign-signed, the SBOM is regenerated on every commit. Supply chain is a continuous control, not a one-time scan."

**Best for.** Brilliant Cloudflare, Amex Experis, WBD. Supply chain is universal.

---

## Upgrade I. SOC2-Mapped MITRE ATT&CK + ATLAS Coverage Report

**Why:** You have GRC docs, you have Falco rules, you have detection signal. Stitching them into a coverage matrix that maps SOC2 CC to ATT&CK + ATLAS to your specific rules is a director-level artifact. Almost nobody at the IC level produces this.

**Scope.**
- Spreadsheet (xlsx) and markdown rendering: rows are ATT&CK + ATLAS techniques, columns are SOC2 CC categories, cells reference your rule IDs and detection sources
- Generated from a YAML source-of-truth so it stays accurate as rules change
- Published as `docs/grc/DETECTION_COVERAGE_SOC2_ATTACK_ATLAS.md`

**Time.** 2 days.

**Files he creates.**
```
~/cyber-squire-ops/builds/coverage-matrix/
  techniques.yaml
  controls.yaml
  generate.py
docs/grc/DETECTION_COVERAGE_SOC2_ATTACK_ATLAS.md
docs/grc/coverage_matrix.xlsx
```

**Interview talking-point.** "I keep a coverage matrix that maps every detection rule I own to ATT&CK, ATLAS, and SOC2 CC. If the auditor asks where my evidence for CC7.2 lives, I point them at three rule IDs and the Falco event log. Same matrix tells me what coverage I'm missing this quarter."

**Best for.** OneDigital, QGenda, WBD, Insight Global. The "I think like a security director" artifact.

---

## Upgrade J. LangGraph Triage Agent on Falco Alerts

**Why:** This is the closing piece. A real LangGraph agent, running on cd-alpha, that consumes a Falco alert, queries Datadog and the GRC corpus, writes a draft incident write-up to `docs/grc/incidents/`, and posts to Telegram. Demonstrable AI-on-the-defenders'-side. This is the single highest-leverage demo for any AI SOC role.

**Scope.**
- LangGraph agent with three nodes: enrich (Datadog query), correlate (search GRC corpus and recent alerts), summarize (Claude Opus via OpenClaw)
- Triggered by Falcosidekick HTTP webhook on severity >= medium
- Output is a markdown draft to `docs/grc/incidents/YYYY-MM-DD-<rule>.md` plus a Telegram message
- Eval harness on synthetic alerts to score grounding, completeness, false-trigger rate

**Time.** 3 days.

**Files he creates.**
```
~/cyber-squire-ops/builds/triage-agent/
  graph.py
  nodes/enrich.py
  nodes/correlate.py
  nodes/summarize.py
  eval/synthetic_alerts.jsonl
  eval/score.py
  Dockerfile
COREDIRECTIVE_ENGINE/docker-compose.yaml  # add cd-service-triage-agent
docs/grc/AI_TRIAGE_AGENT_DESIGN.md
```

**Public artifact.** `github.com/ET-sec/falco-triage-agent` (sanitized) plus a 90-second screen recording for the demo.

**Interview talking-point.** "When Falco fires a medium-or-higher alert, a LangGraph agent on my droplet pulls the surrounding Datadog context, searches my GRC corpus for prior similar incidents, and writes a draft IR write-up to a markdown file. I review and ship. That's where I want AI on the defender side: handling the boring 80% so the analyst spends time on the interesting 20%."

**Best for.** Dropzone AI (this is the mirror story), OneDigital, Resilience, Insight Global. Single highest-impact demo.

---

## Roadmap summary table

| Upgrade | Days | Primary roles | Public artifact | Defensibility |
|---------|------|---------------|------------------|---------------|
| A. Promptfoo CI | 2 | Dropzone, OneDigital, Resilience, Insight | `openclaw-eval-harness` repo | High |
| B. NeMo Guardrails | 2 | Resilience, OneDigital, Brilliant | GRC doc 38 | High |
| C. Garak weekly | 1 | Dropzone, OneDigital, Insight | GRC scan report | Medium |
| D. Falco agentic | 2 | Dropzone, OneDigital, WBD | `falco-agentic-rules` repo | High |
| E. Sigma library | 2 | All detection roles | `sigma-coredirective` repo | Medium |
| F. AI-BOM | 1 | OneDigital, Insight, QGenda, Brilliant | GRC doc 38 + JSON | Medium |
| G. PI classifier | 3 | Dropzone, OneDigital, Insight | GRC doc 39 + curve | Very high |
| H. Chainguard | 1 | Brilliant, Amex, WBD | Supply chain doc | Medium |
| I. Coverage matrix | 2 | OneDigital, QGenda, WBD | GRC matrix doc | High |
| J. LangGraph triage | 3 | Dropzone, OneDigital, Resilience | `falco-triage-agent` repo + demo video | Very high |

**Total time at full build:** 19 days. Cut to 14 by skipping H, I, and one of D/E (see PRIORITY-MATRIX.md).
