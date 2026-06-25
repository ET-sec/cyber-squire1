# CoreDirective Automation Engine

[![Live Portfolio](https://img.shields.io/badge/Portfolio-Live-00FF41?style=flat-square)](https://et-sec.github.io/portfolio/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![CodeQL](https://github.com/ET-sec/cyber-squire1/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/ET-sec/cyber-squire1/actions/workflows/codeql.yml)
[![Security Scan](https://github.com/ET-sec/cyber-squire1/actions/workflows/security.yml/badge.svg?branch=main)](https://github.com/ET-sec/cyber-squire1/actions/workflows/security.yml)
[![GRC Validate](https://github.com/ET-sec/cyber-squire1/actions/workflows/grc-validate.yml/badge.svg?branch=main)](https://github.com/ET-sec/cyber-squire1/actions/workflows/grc-validate.yml)
[![DAST ZAP](https://github.com/ET-sec/cyber-squire1/actions/workflows/dast-zap.yml/badge.svg?branch=main)](https://github.com/ET-sec/cyber-squire1/actions/workflows/dast-zap.yml)

**Production security platform on DigitalOcean, 20 containers, NIST 800-53 compliance, full IaC with Terraform, agentic AI with NeMo Guardrails and Langfuse observability**

Built and operated by [Emmanuel Tigoue](https://et-sec.github.io/portfolio/) | AI Security Engineer | CISSP, SecurityX (CASP+), CCNA, Security+

---

## What This Is

A 20-container security operations platform running on a single DigitalOcean droplet. SOAR orchestration, runtime threat detection, privileged access management, agentic AI with guardrails and LLM observability, plus full compliance documentation, all on one node at $48/month.

Everything is codified in Terraform, secured by a CI/CD pipeline with 6 security scans, and documented to NIST 800-53 Rev. 5 Moderate baseline with 86% control coverage.

---

## Architecture

```
DigitalOcean Droplet (4 vCPU / 8GB RAM) -- Ubuntu 24.04            $48/mo
│
├── Core Platform
│   ├── PostgreSQL 16                  Workflow state + agent state + audit
│   ├── n8n SOAR                       16-action orchestration engine
│   └── Cloudflare Tunnel              Zero-trust access (no exposed ports)
│
├── Identity & Access
│   ├── HashiCorp Vault                Secrets management
│   ├── Keycloak v26                   Identity + RBAC
│   ├── Teleport v18                   SSH + session recording + JIT access
│   └── Teleport Event Handler         Audit event shipping
│
├── Detection & Observability
│   ├── Datadog Agent                  Metrics, logs, container monitoring
│   ├── Falco (eBPF)                   Runtime threat detection
│   ├── Falcosidekick                  Alert routing to Datadog
│   ├── Fluentd                        Log routing to Datadog
│   └── Langfuse Stack                 LLM observability (web + worker + redis + clickhouse)
│
└── AI Layer
    ├── OpenClaw Gateway               Claude AI agent proxy
    ├── Ollama (Qwen 3 8B)             Local AI inference
    ├── Faster-Whisper                 Voice transcription
    ├── NeMo Guardrails                LLM input/output policy enforcement
    └── Squire                         Custom AI security agent
```

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Containers Running | 20 (19 Compose-managed + 1 standalone OpenClaw) |
| NIST 800-53 Controls Mapped | 133 |
| Control Coverage | 86% (114/133 implemented or partial) |
| Monthly Infrastructure | $48 |
| CI/CD Security Scans | 10 (Trivy, Semgrep, Gitleaks, Checkov, Snyk OSS, CodeQL, OWASP ZAP DAST, Cosign, SBOM, Container Image Verify) |
| GRC Documents | 58 policies, plans, playbooks, threat models, and AI security artifacts |
| GRC Diagrams | 16 PNGs (network topology, data flow, control coverage, risk heat map, AI pipeline) |
| OPA Policy Rules | 8 Rego policies enforced on every PR |
| Terraform Files | 20 .tf files managing DigitalOcean + Cloudflare |

---

## GRC Compliance Library

Full governance, risk, and compliance documentation aligned to NIST SP 800-53 Rev. 5 Moderate baseline, FIPS 199, and CIS Docker Benchmark.

**[Browse the full library](docs/grc/README.md)**

| Category | Count | Contents |
|----------|-------|----------|
| Core Plans | 4 | System Security Plan (SSP), Plan of Action & Milestones (POA&M), Risk Assessment, Squire SSP |
| Policies | 10 | Incident Response, Access Control, Acceptable Use, Business Continuity, Disaster Recovery, Change Management, Vulnerability Management, Security Awareness, Risk Management, AI Governance |
| IR Playbooks | 5 | Compromised Container, Leaked Credential, DDoS/Service Degradation, Unauthorized Access, AI Incident Response |
| Threat Modeling | 8 | DFD, STRIDE Threat Model, Attack Tree (AI Pipeline), AI Threat Catalog, AI Supply Chain Risk + Register, AI Red Team Plan, Squire Threat Model |
| IAM Documentation | 2 | RBAC Role Map (3-tier model), Access Review Process (JIT workflow) |
| Risk Register | 1 | CIS Docker Benchmark findings with compensating controls |
| Tabletop Exercises | 2 | Operation Phantom Container, Squire Tabletop Exercise |
| Executive Summaries | 3 | Architecture, Compliance, Security Posture |
| AppSec, SDLC, Pen Test | 7 | Secure SDLC, Code Review Findings, DAST Methodology, OWASP MCP Top 10 Audit, Pen Test Self-Assessment, Red Team Results, n8n Credential Exposure Write-Up |
| AI Security Artifacts | 5 | Squire AI Risk Assessment, Squire Data Flow Classification, Squire Model Card, Guardrails Configuration, ADR-001 Embedding Provider |
| Compliance Crosswalks | 4 | SOC 2 + ISO 27001, Squire Framework Crosswalk, HIPAA Security Rule, HIPAA ePHI Handling |
| Architecture and Ops Specs | 6 | Agent Signing, Agent Telemetry, AI Audit Trail Spec, Google Cloud IAM Assessment, HITL Policy, POA&M MCP 2025 |
| Diagrams | 16 | Network topology, data flow, control coverage, risk heat map, AI pipeline attack tree, NIST control mapping, and more |

All documents are sanitized for public hosting. Personal identifiers and internal infrastructure details are replaced with generic equivalents. Product names (Vault, Keycloak, Teleport, Falco, Datadog, Cloudflare, Trivy) are preserved to demonstrate the actual technology stack.

---

## Infrastructure as Code

20 Terraform files in [`terraform/cd-do-infrastructure/`](terraform/cd-do-infrastructure/) managing DigitalOcean and Cloudflare resources.

- **Providers:** DigitalOcean (compute, networking, storage) + Cloudflare (DNS, tunnel)
- **Remote state:** DigitalOcean Spaces with encryption at rest
- **Policy-as-code:** 8 OPA/Rego policies (4 deny, 4 warn) enforced via conftest on every PR
- **Pre-commit hooks:** terraform fmt, validate, tflint, checkov

---

## CI/CD Pipeline

13 workflow files in [`.github/workflows/`](.github/workflows/) cover the full lifecycle:

**Code security:** `security.yml` (Trivy, Semgrep, Gitleaks, Snyk), `codeql.yml` (CodeQL SAST), `dast-zap.yml` (OWASP ZAP DAST baseline)

**Infrastructure:** `terraform-pr.yml` (fmt, validate, tflint, Checkov, plan, OPA), `image-smoke.yml` (container build verification)

**GRC and compliance:** `grc-validate.yml` (sanitization, link, OSCAL, STIX, Cosign), `grc-reviewer.yml` (LLM-assisted GRC review)

**Agent signing:** `agent-signing.yml`, `agent-verify.yml`, `agent-inventory.yml` (Sigstore signing for agent cards)

**Workflow hygiene:** `auto-label.yml`, `stale.yml`, `pr-agent.yml`

Security-first: Gitleaks blocks any hardcoded secrets. Checkov fails on security violations. OPA deny policies are hard-fail. CodeQL flags vulnerable code patterns. OWASP ZAP blocks on HIGH or CRITICAL findings.

---

## Observability and Detection

- **Datadog:** Container monitoring, custom dashboard, 7 alert monitors (container down, CPU, memory, disk, n8n errors, health digest, certificate expiry)
- **Falco:** eBPF runtime threat detection with custom rules per container (shell access, sensitive file reads, privilege escalation, network anomalies)
- **Falcosidekick:** Routes Falco alerts to Datadog for centralized visibility
- **Teleport:** SSH session recording with JIT access (4-hour TTL), full audit trail
- **Audit logs:** Exported to DigitalOcean Spaces (versioned, hash-chained for integrity)

---

## Repository Structure

```
.
├── README.md
├── docs/
│   ├── grc/                          58 GRC documents + 16 diagrams + 7 generators
│   │   ├── README.md                 Library index
│   │   ├── SSP_SYSTEM_SECURITY_PLAN.md
│   │   ├── SQUIRE_SSP.md             Agentic AI system security plan
│   │   ├── POAM_PLAN_OF_ACTION.md
│   │   ├── RISK_ASSESSMENT.md
│   │   ├── POLICY_*.md              10 security policies (including AI governance)
│   │   ├── PLAYBOOK_*.md            5 incident response playbooks (including AI incident)
│   │   ├── SQUIRE_*.md              5 Squire AI security artifacts (model card, threat model, tabletop)
│   │   ├── FRAMEWORK_CROSSWALK_*.md 4 compliance crosswalks (SOC 2, ISO 27001, HIPAA)
│   │   ├── EXECUTIVE_SUMMARY_*.md   3 executive summaries
│   │   └── diagrams/                16 PNGs + 7 Python generators
│   ├── GROUND_TRUTH_AUDIT_PROTOCOL.md  Repo verification methodology
│   ├── GTA_SKILL_DESIGN_NOTES.md       GTA build backlog
│   └── WORKFLOW_GUIDE.md               Branch + PR + merge discipline
├── terraform/
│   ├── cd-do-infrastructure/         20 .tf files + 8 OPA policies
│   ├── cd-aws-automation/            Legacy AWS IaC (retained for reference)
│   └── simple-ec2/                   Legacy quick-start (retained for reference)
├── .github/workflows/                13 CI/CD pipelines
├── .githooks/                        Pre-commit AI-tells sweep
└── scripts/                          Operational scripts (health, audit, git workflow)
```

---

## Security

- Gitleaks runs on every push via CI/CD pipeline (hard-fail on detection)
- `.gitignore` blocks `.env`, `.tfstate`, `.pem`, and all secret-containing files
- Pre-commit hooks validate no secrets in staged files
- No API keys, credentials, or secrets in the current codebase

---

## Contact

**Portfolio:** [et-sec.github.io/portfolio](https://et-sec.github.io/portfolio/)
**LinkedIn:** [linkedin.com/in/emmanuel-tigoue](https://www.linkedin.com/in/emmanuel-tigoue)
**GitHub:** [github.com/ET-sec](https://github.com/ET-sec)

---

MIT License
