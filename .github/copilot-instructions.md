# CoreDirective Automation Engine -- AI Coding Agent Instructions

**Project:** CoreDirective Automation Engine
**Engineer:** Emmanuel Tigoue
**AI Agent Target:** GitHub Copilot, Claude, Cursor, Windsurf

---

## Platform

DigitalOcean droplet (s-4vcpu-8gb, 4 vCPU, 8GB RAM, 160GB disk, Ubuntu 24.04).
Cost: $48/mo. SSH: `ssh cd-alpha`. IP: 161.35.0.184.

## Stack: 14 Containers (13 Compose + 1 Standalone)

| Container | Service | Port |
|-----------|---------|------|
| cd-service-db | PostgreSQL 16 | 5432 |
| cd-service-n8n | n8n SOAR orchestrator | 5678 |
| cd-service-datadog | Datadog Agent (logs, metrics, monitors) | -- |
| cd-service-falco | Falco eBPF runtime detection | -- |
| cd-service-falcosidekick | Alert router (Falco to Datadog) | -- |
| cd-service-vault | HashiCorp Vault (secrets management) | 8200 |
| cd-service-keycloak | Keycloak v26 (RBAC, SSO) | 8080 |
| cd-service-ollama | Ollama (local LLM inference) | 11434 |
| cd-service-whisper | Faster-Whisper (speech-to-text) | 8000 |
| cd-service-teleport | Teleport v18 (PAM, JIT access, session recording) | 3080 |
| cd-service-event-handler | Teleport audit log shipper | -- |
| cd-service-fluentd | Fluentd (audit logs to Datadog) | -- |
| tunnel-cyber-squire | Cloudflare Tunnel (zero exposed ports) | host net |
| openclaw-gateway | OpenClaw (Claude Opus 4.6 proxy) | 18789-18790 |

Compose file: `/root/COREDIRECTIVE_ENGINE/docker-compose.yaml`

## Access

Zero-trust via Cloudflare Tunnel. No ports exposed to public internet.

- `n8n.tigouetheory.com` -- n8n SOAR dashboard
- `ssh.tigouetheory.com` -- SSH via Cloudflare tunnel

**NEVER** run `docker compose down` via the tunnel -- it kills the tunnel container.

## IaC: Terraform

- **Active:** `terraform/cd-do-infrastructure/` (16 .tf files, DigitalOcean + Cloudflare providers)
- **Policies:** 8 OPA/Rego policies in `terraform/cd-do-infrastructure/policy/`
- **Remote state:** DigitalOcean Spaces (S3-compatible, nyc3 region)
- **Legacy (suspended):** `terraform/simple-ec2/`, `terraform/cd-aws-automation/`

## CI/CD: GitHub Actions

**PR pipeline** (`terraform-pr.yml`): fmt, validate, TFLint, Checkov, plan, OPA/conftest, PR comment
**Merge pipeline** (`security.yml`): Trivy, Semgrep, Gitleaks, apply, Cosign, SBOM generation

## GRC: Compliance Library

20 documents in `docs/grc/` covering NIST 800-53 Moderate baseline:
SSP, POA&M, Risk Assessment, 9 policies, IAM maps, CIS register, 4 IR playbooks, tabletop exercise.
Diagram generators in `docs/grc/diagrams/`.

## Monitoring & Security

- **Datadog:** Logs, metrics, 11 monitors (us5.datadoghq.com)
- **Falco:** eBPF runtime threat detection with custom rules
- **Falcosidekick:** Routes Falco alerts to Datadog
- **Teleport:** SSH certificate auth, session recording, JIT access roles
- **Keycloak:** RBAC with password policies and brute-force protection

## Naming Conventions

```
Container prefixes:  cd-service-*
Network:             cd-automation-net
Volumes:             CD_VOL_* (on droplet)
Environment vars:    CD_* (e.g., CD_DB_PASS, CD_N8N_KEY)
```

## Secrets

All secrets managed via Doppler (`coredirective-engine/prd` config).
On the droplet: `/root/COREDIRECTIVE_ENGINE/.env` (chmod 600).
Never commit `.env` or secrets to git.

## File Structure

```
docs/
  ADHD_Runbook.md          -- Operational playbook
  Employment_Proof.md      -- Business case overview
  Technical_Vault.md       -- Architecture deep-dive
  grc/                     -- 20-doc NIST compliance library + diagram generators

COREDIRECTIVE_ENGINE/      -- Local Docker Compose copy (13 services)
terraform/                 -- IaC (DigitalOcean active, legacy suspended)
.github/workflows/         -- CI/CD pipelines
DEPRECATED/                -- Archived legacy docs and tools
```

## Guidelines for AI Agents

1. Use `cd-*` prefixes for any new components
2. Read docs: Employment_Proof (why), Technical_Vault (how), ADHD_Runbook (ops)
3. Never commit `.env`, `*.pem`, `*.key`, or `terraform.tfstate`
4. Terraform changes go through PR pipeline (fmt, validate, Checkov, OPA)
5. All containers communicate via internal Docker network, not exposed ports
6. Monitor resource usage -- 8GB RAM shared across 14 containers

---

**Last Updated:** March 2026
**Maintained By:** Emmanuel Tigoue
