# CoreDirective Automation Engine

[![Live Portfolio](https://img.shields.io/badge/Portfolio-Live-00FF41?style=flat-square)](https://et-sec.github.io/portfolio/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

**Production security platform on AWS — AI-augmented orchestration, Zero Trust architecture, Terraform IaC**

Built and operated by [Emmanuel Tigoue](https://et-sec.github.io/portfolio/) | Security Engineer | CASP+ (SecurityX), SSCP, CCNA

---

## What This Is

A 5-service containerized security platform running on a single EC2 instance. Integrates 17 services through a SOAR orchestration layer with zero external AI inference costs.

```
AWS EC2 t3.xlarge (16GB RAM) — RHEL 9 / Amazon Linux 2023
├── PostgreSQL 16          Workflow state + automation logs
├── n8n SOAR               17-service orchestration engine
├── Ollama (Qwen 2.5 7B)  Local AI inference ($0/month)
├── Faster-Whisper         Voice transcription (STT)
├── OpenClaw Gateway       Claude AI agent proxy
└── Cloudflare Tunnel      Zero-trust access (no exposed ports)
```

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Integrated Services | 17 |
| NIST/CIS Coverage | 89% (16/18 controls) |
| Attack Surface Reduction | 85% |
| AI Inference Cost | $0/month |
| Workflow Success Rate | 99.2% |
| Monthly Infrastructure | ~$135 |
| Annual Savings vs GPU | $3,732 (72%) |

---

## Repository Structure

```
├── COREDIRECTIVE_ENGINE/       Production Docker stack
│   ├── docker-compose.yaml       Service definitions
│   ├── .env.template             Configuration template (sanitized)
│   ├── cdae-init.sh              RHEL hardening + bootstrap
│   ├── cdae-healthcheck.sh       Post-deployment health checks
│   ├── deploy_workflows.sh       Workflow deployment automation
│   ├── sql/                      Database initialization scripts
│   └── workflow_*.json           n8n workflow definitions
│
├── terraform/                  Infrastructure as Code
│   ├── simple-ec2/               Quick-start (5 min, ~$135/mo)
│   └── cd-aws-automation/        Production-grade (VPC, NAT, S3 backend)
│
├── standalone_tools/           Security & automation utilities
│   ├── aws_security_tool.js      AWS security scanning
│   ├── security_scanner.js       General security analysis
│   ├── finance_manager.js        Financial management
│   └── webhook_handler.js        Webhook routing
│
├── docs/                       Architecture & operations
│   ├── Employment_Proof.md       Business case & capability overview
│   ├── Technical_Vault.md        Deep-dive system specifications
│   ├── ADHD_Runbook.md           Operational playbook
│   ├── ARCHITECTURE_DIAGRAMS.md  Full architecture with threat model
│   └── ...                       Deployment guides, setup docs
│
├── .planning/                  Phase-based project execution
│   ├── PROJECT.md                Project definition
│   ├── ROADMAP.md                10-phase development timeline
│   └── phases/01-10/             Planning, research, verification
│
└── DEPRECATED/                 Archived previous implementations
```

---

## Security Architecture

Three-layer defense model with zero exposed ports:

**Layer 1 — Perimeter:** AWS Security Groups (default-deny ingress) + Cloudflare Tunnel (TLS 1.3, no direct IP exposure)

**Layer 2 — Zero Trust:** Identity-aware proxy (OTP), Docker bridge isolation (172.28.0.0/16), quarterly credential rotation

**Layer 3 — Host:** SELinux enforcing (container_t domain), read-only filesystems, dropped capabilities, unprivileged execution

---

## Deployment

Two Terraform options:

| Option | Path | Time | Cost | Use Case |
|--------|------|------|------|----------|
| Quick Start | `terraform/simple-ec2/` | 5 min | ~$135/mo | Demos, interviews |
| Production | `terraform/cd-aws-automation/` | 15 min | ~$142/mo | Full security posture |

```bash
terraform init && terraform apply -var="my_ip=$(curl -s checkip.amazonaws.com)"
ssh -i your-key.pem ec2-user@<instance-ip>
cd COREDIRECTIVE_ENGINE && ./cdae-init.sh
cp .env.template .env && nano .env
docker compose up -d && ./cdae-healthcheck.sh
```

---

## Technical Decisions

| Decision | Rationale |
|----------|-----------|
| CPU inference over GPU | 72% cost savings, zero quality loss for security analysis tasks |
| PostgreSQL over SQLite | Concurrent workflow execution at scale (500+ daily) |
| Cloudflare Tunnel over VPN | Zero-trust, no exposed ports, built-in DDoS protection |
| Qwen 2.5 7B (4-bit) | Fits in 7.5GB RAM, <3s inference, $0/month |
| Three-tier docs | Business (Employment_Proof), Technical (Vault), Operational (Runbook) |

---

## Documentation

| Document | Audience | Description |
|----------|----------|-------------|
| [Employment_Proof.md](docs/Employment_Proof.md) | Recruiters | Business case and architecture overview |
| [Technical_Vault.md](docs/Technical_Vault.md) | Engineers | System specs, database tuning, network topology |
| [ADHD_Runbook.md](docs/ADHD_Runbook.md) | Operations | Copy-paste commands, zero jargon |
| [ARCHITECTURE_DIAGRAMS.md](docs/ARCHITECTURE_DIAGRAMS.md) | Security | Full threat model and control mapping |

---

## Security Notes

This repo is sanitized for public release:
- All `.env` files use placeholders (`REPLACE_WITH_*`)
- No credentials, API keys, or tokens committed
- Infrastructure state files (`.tfstate`) gitignored
- Private operational docs gitignored

---

## Contact

**Portfolio:** [et-sec.github.io/portfolio](https://et-sec.github.io/portfolio/)
**LinkedIn:** [linkedin.com/in/emmanuel-tigoue-672378307](https://www.linkedin.com/in/emmanuel-tigoue-672378307)
**GitHub:** [github.com/ET-sec](https://github.com/ET-sec)

---

MIT License
