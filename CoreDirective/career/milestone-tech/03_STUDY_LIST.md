# Tech Ramp Study List - Milestone Tech AI Security Engineer/Architect

Honest heat map vs Emmanuel's real experience.

## Heat map

### GREEN (clear signal, defend on probe)
- AI guardrails, prompt injection defense, NeMo Guardrails, GLiNER PII redaction
- OWASP LLM Top 10, MITRE ATLAS
- Langfuse eval harness, golden fixtures, evaluators
- OPA Rego policies, budget guards, sanitize patterns
- n8n agentic workflows, threat surface
- Cosign sign-blob, SBOM, Trivy, Semgrep, Gitleaks
- AI Incident Response playbook, red-team cycle methodology
- NIST AI RMF, ISO 42001, AI governance translation
- Cloudflare Zero Trust, mTLS, Falco eBPF
- Terraform IaC patterns, OPA admission

### YELLOW (touched, need polish before screen)
- AWS Bedrock Guardrails (lab, not prod)
- AWS IAM scoping for Bedrock (need ApplyGuardrail API depth)
- EU AI Act Annex III, Article 9 risk management
- GDPR Article 22 automated decisioning
- AI-SPM vendor landscape (Wiz, Lakera, Prompt Security, Protect AI, Aim Security)
- ChatGPT Enterprise admin controls (DLP, retention, SCIM)

### RED (zero exposure, own the gap)
- Databricks production (Unity Catalog, MLflow Registry on Databricks)
- UiPath Orchestrator security
- AWS Org SCPs, Identity Center, GuardDuty production tuning
- KMS key policies for AI workloads at enterprise scale
- VPC endpoints for Bedrock private connectivity

## Tier 1 - MUST KNOW before the recruiter screen (4 hours)

| Topic | Resource | Time |
|---|---|---|
| Bedrock Guardrails policy schema | https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html | 60 min |
| Bedrock IAM scoping (model resource ARNs, aws:SourceVpce) | https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html | 45 min |
| Databricks Unity Catalog model lineage | https://docs.databricks.com/en/data-governance/unity-catalog/index.html | 45 min |
| MLflow Model Registry signing + transitions | https://mlflow.org/docs/latest/model-registry.html | 30 min |
| EU AI Act Annex III high-risk categories | https://artificialintelligenceact.eu/annex/3/ | 30 min |
| AI-SPM vendor cheat sheet (Wiz, Prompt Security, Lakera, Protect AI, Aim Security) | Vendor sites + Gartner Hype Cycle for AI Security | 60 min |

## Tier 2 - HIGH PROBABILITY in tech screen (6 hours)

| Topic | Resource | Time |
|---|---|---|
| Bedrock private VPC endpoint architecture | AWS reference architecture | 60 min |
| Databricks workspace network isolation, secret scopes | Databricks security best practices guide | 60 min |
| ChatGPT Enterprise admin controls (data retention, SCIM, audit) | OpenAI Enterprise admin docs | 45 min |
| GDPR Article 22 + DPIA for AI systems | EDPB AI guidelines | 45 min |
| EU AI Act conformity assessment process | EU AI Office implementation guide | 45 min |
| OWASP LLM Top 10 v1.1 | https://owasp.org/www-project-top-10-for-large-language-model-applications/ | 60 min |
| MITRE ATLAS tactics + case studies | https://atlas.mitre.org/matrices/ATLAS | 60 min |
| Agentic AI threat patterns (excessive agency, tool abuse, lateral movement) | OWASP Agentic AI Threats and Mitigations | 60 min |

## Tier 3 - NICE TO HAVE (2 hours)

| Topic | Resource | Time |
|---|---|---|
| UiPath security architecture overview | UiPath docs | 30 min |
| AWS GuardDuty for ML workloads | AWS security blog | 30 min |
| n8n agentic security patterns | n8n docs + blog | 30 min |
| Practical pickup on Lakera Guard or Prompt Security free tier (POC) | Vendor signup, run one prompt | 30 min |

## Recommended order
1. Tier 1 in 4 hours flat. Do it tonight if Elena calls tomorrow.
2. Tier 2 across 2-3 evenings before the end-client tech screen.
3. Tier 3 only if you have time after the screen is scheduled.

## Live-fire artifact to mention
Pull up your own repo `cyber-squire-ops` during the tech screen if they want to see code:
- `scripts/grc/eval_reviewer.py` (Langfuse harness with 4 evaluators)
- `scripts/grc/budget_guard.py` (dual-source spend tracking)
- `scripts/grc/sanitize_output.py` + `sanitize_patterns.py` (10 PII patterns)
- `scripts/grc/grc_mcp_server.py` (FastMCP server, read-only annotations, path-traversal guard)
- `infra/conftest/policy/*.rego` (OPA Rego policies, corpus baseline)
- `docs/grc/PLAYBOOK_AI_INCIDENT.md` (AI Incident Response playbook with Squire incident classes)
