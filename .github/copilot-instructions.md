# CoreDirective Automation Engine, AI Coding Agent Instructions

**Project:** CoreDirective Automation Engine
**AI Agent Target:** GitHub Copilot, Claude, Cursor, Windsurf

---

## Platform

Oracle Cloud (OCI) Always Free Ampere A1 ARM instance (Ubuntu 24.04).
Zero-trust access via Cloudflare Tunnel. No public IP exposed.

## Stack

Currently running on the instance: PostgreSQL 16 with pgvector, n8n, and the Cloudflare tunnel client. The rest of the 19-service design below is pending ARM rebuild.

| Container | Service |
|-----------|---------|
| svc-db | PostgreSQL 16 + pgvector |
| svc-n8n | n8n SOAR orchestrator |
| svc-datadog | Datadog Agent (logs, metrics, monitors) |
| svc-falco | Falco eBPF runtime detection |
| svc-falcosidekick | Alert router (Falco to Datadog) |
| svc-vault | HashiCorp Vault (secrets management) |
| svc-keycloak | Keycloak v26 (RBAC, SSO) |
| svc-ollama | Ollama (local LLM inference) |
| svc-whisper | Faster-Whisper (speech-to-text) |
| svc-teleport | Teleport v18 (PAM, JIT access, session recording) |
| svc-event-handler | Teleport audit log shipper |
| svc-fluentd | Fluentd (audit logs to Datadog) |
| tunnel-cyber-squire | Cloudflare Tunnel (zero exposed ports) |
| openclaw-gateway | OpenClaw (Claude Fable 5 proxy) |

All containers communicate on internal Docker network only.

## Access

Zero-trust via Cloudflare Tunnel. No ports exposed to public internet.

All services accessed via Cloudflare Tunnel (no direct SSH or exposed endpoints).

**NEVER** run `docker compose down` via the tunnel. It kills the tunnel container.

## IaC: Terraform

- **Active:** `terraform/cd-oci-infrastructure/` (OCI + Cloudflare providers)
- **Policies:** OPA/Rego policies in `terraform/cd-oci-infrastructure/policy/`
- **Archived reference:** `terraform/cd-do-infrastructure/` (DigitalOcean era)
- **Remote state:** OCI Object Storage (versioned bucket, locked)
- **Legacy (archived):** `terraform/simple-ec2/`, `terraform/cd-aws-automation/`

## CI/CD: GitHub Actions

**PR pipeline** (`terraform-pr.yml`): fmt, validate, TFLint, Checkov, plan, OPA/conftest, PR comment
**Merge pipeline** (`security.yml`): Trivy, Semgrep, Gitleaks, apply, Cosign, SBOM generation

## GRC: Compliance Library

Documents in `docs/grc/` covering NIST 800-53 Moderate baseline:
SSP, POA&M, Risk Assessment, policies (including AI governance), IAM maps, CIS register, IR playbooks (including AI incident response), threat modeling documents, executive summaries, tabletop exercise.
Diagram generators in `docs/grc/diagrams/`.

## Monitoring and Security

- **Datadog:** Logs, metrics, monitors (datadoghq.com)
- **Falco:** eBPF runtime threat detection with custom rules
- **Falcosidekick:** Routes Falco alerts to Datadog
- **Teleport:** SSH certificate auth, session recording, JIT access roles
- **Keycloak:** RBAC with password policies and brute-force protection

## Naming Conventions

```
Container prefixes:  svc-*
Network:             cd-automation-net
Volumes:             CD_VOL_* (on the instance)
Environment vars:    CD_* (e.g., CD_DB_PASS, CD_N8N_KEY)
```

## Secrets

All secrets managed via Doppler. Never commit `.env` or secrets to git.

## File Structure

```
docs/
  grc/                     NIST compliance library + diagram generators
  GROUND_TRUTH_AUDIT_PROTOCOL.md   repo verification methodology

COREDIRECTIVE_ENGINE/      Local Docker Compose copy
terraform/                 IaC (OCI active, DO and AWS archived)
.github/workflows/         CI/CD pipelines
.githooks/                 Pre-commit checks (AI-tells sweep)
scripts/                   Helper scripts (git workflow, etc.)
```

## Guidelines for AI Agents

1. Use `svc-*` prefixes for new service components (matches the public sanitized naming convention used throughout `docs/grc/`)
2. Read SECURITY.md for disclosure policy and CONTRIBUTING.md for workflow rules. Compliance context lives in `docs/grc/`.
3. Never commit `.env`, `*.pem`, `*.key`, `terraform.tfstate`, or any file matching `.gitignore` patterns
4. Terraform changes go through PR pipeline (fmt, validate, Checkov, OPA)
5. All containers communicate via internal Docker network, not exposed ports

---

**Last Updated:** June 2026
