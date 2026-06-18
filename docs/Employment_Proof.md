# Technical Capability Summary: CoreDirective Automation Engine

**Document Type:** Infrastructure Architecture and Security Posture Assessment
**Framework Alignment:** NIST SP 800-53 Rev. 5 Moderate Baseline
**Version:** 3.0
**Status:** Production

---

## Executive Summary

The CoreDirective Automation Engine is a production security operations platform deployed on a DigitalOcean droplet (4 vCPU, 8GB RAM, Ubuntu 24.04). It runs 14 containers providing SOAR orchestration, runtime threat detection, privileged access management, identity and access control, secrets management, and full observability -- all on a single node at $48/month.

The platform is documented to NIST SP 800-53 Rev. 5 Moderate baseline with 86% control coverage (114 of 133 controls implemented or partially implemented), supported by a 37-document GRC compliance library.

### Key Differentiators

- **Cost:** $48/month total infrastructure (vs. $400+ for equivalent managed services)
- **Security depth:** Runtime threat detection (Falco eBPF), privileged access management (Teleport JIT), identity federation (Keycloak RBAC), secrets management (Vault)
- **Compliance:** 37 GRC documents covering SSP, POA&M, risk assessment, 10 policies (including AI governance), 5 IR playbooks (including AI incident response), 6 threat modeling documents (DFD, STRIDE, attack tree, AI threat catalog, AI supply chain risk, AI red team plan), CIS risk register, 2 IAM documents, tabletop exercise, and 3 executive summaries
- **IaC maturity:** 16 Terraform files, 8 OPA/Rego policies, CI/CD with 6 security scans, pre-commit hooks

---

## Platform Architecture

### Container Stack (14 Services)

| Container | Service | Purpose |
|-----------|---------|---------|
| PostgreSQL 16 | cd-service-db | Workflow state, audit logs, n8n persistence |
| n8n SOAR | cd-service-n8n | 16-service orchestration engine |
| Datadog Agent | cd-service-datadog | Metrics, logs, container monitoring |
| Falco (eBPF) | cd-service-falco | Runtime threat detection |
| Falcosidekick | cd-service-falcosidekick | Alert routing to Datadog |
| HashiCorp Vault | cd-service-vault | Secrets management |
| Keycloak v26 | cd-service-keycloak | Identity, RBAC, SSO |
| Teleport v18 | cd-service-teleport | SSH, session recording, JIT access |
| Teleport Event Handler | cd-service-event-handler | Audit event shipping |
| Fluentd | cd-service-fluentd | Log routing to Datadog |
| Ollama (Qwen 3 8B) | cd-service-ollama | Local AI inference |
| Faster-Whisper | cd-service-whisper | Voice transcription |
| Cloudflare Tunnel | tunnel-cyber-squire | Zero-trust access (no exposed ports) |
| OpenClaw Gateway | openclaw-gateway | Claude AI agent proxy |

**Host:** DigitalOcean Droplet (s-4vcpu-8gb) -- 4 vCPU, 8GB RAM, 160GB disk
**OS:** Ubuntu 24.04 LTS
**Network:** Docker bridge (internal), Cloudflare Tunnel (external) -- zero exposed ports
**Monthly cost:** $48

---

## Security Stack

### Defense in Depth

**Layer 1 -- Perimeter:**
- DigitalOcean Cloud Firewall (default-deny ingress, ICMP only exception)
- Cloudflare Tunnel (TLS 1.3, no direct IP exposure, DDoS protection)

**Layer 2 -- Identity and Access:**
- Keycloak v26 (RBAC, password policies, brute-force detection)
- Teleport v18 (JIT privileged access, 4-hour TTL, session recording)
- SSH key-only authentication (ed25519)

**Layer 3 -- Runtime:**
- Falco eBPF detection (custom rules per container: shell access, sensitive file reads, privilege escalation, network anomalies)
- Falcosidekick alert routing to Datadog
- Container hardening: `no-new-privileges` on 12/13 services, `cap_drop: ALL`, resource limits (CPU, memory, PIDs), log rotation

**Layer 4 -- Audit:**
- Teleport session recording (node-sync mode)
- Audit logs exported to DigitalOcean Spaces (versioned, hash-chained)
- Fluentd log pipeline with mTLS to Datadog

### Observability

- **Datadog:** 7 alert monitors (container down, CPU, memory, disk, n8n errors, health digest, certificate expiry)
- **Custom dashboard:** Container resource utilization, service health, alert summary
- **Daily health digest:** Automated script reporting system status

---

## Compliance Posture

### NIST SP 800-53 Rev. 5 -- Moderate Baseline

| Metric | Value |
|--------|-------|
| Control families mapped | 16 of 20 |
| Total controls mapped | 133 |
| Implemented or partially implemented | 114 (86%) |
| Security categorization | FIPS 199 -- Moderate |

### GRC Documentation Library (37 Documents)

| Category | Count | Documents |
|----------|-------|-----------|
| Core Plans | 3 | System Security Plan (SSP), POA&M, Risk Assessment |
| Policies | 10 | Incident Response, Access Control, Acceptable Use, Business Continuity, Disaster Recovery, Change Management, Vulnerability Management, Security Awareness, Risk Management, AI Governance |
| IR Playbooks | 5 | Compromised Container, Leaked Credential, DDoS/Service Degradation, Unauthorized Access, AI Incident Response |
| Threat Modeling | 6 | Data Flow Diagram (DFD), STRIDE Threat Model, Attack Tree, AI Threat Catalog, AI Supply Chain Risk, AI Red Team Plan |
| IAM Documentation | 2 | RBAC Role Map (3-tier model), Access Review Process (JIT workflow) |
| Risk Register | 1 | CIS Docker Benchmark findings with compensating controls |
| Tabletop Exercise | 1 | Operation Phantom Container (5-phase exercise) |
| Executive Summaries | 3 | Architecture, Compliance, Security Posture |

Supporting artifacts: 9 architecture diagrams, 7 Python diagram generators.

All documents are sanitized for public repository hosting per ISO 27001 information labeling requirements.

---

## Infrastructure as Code

### Terraform (DigitalOcean + Cloudflare)

- **16 .tf files** managing compute, networking, DNS, firewall, monitoring, dashboard, secrets, SSH, tunnel
- **Remote state:** DigitalOcean Spaces with encryption at rest
- **Providers:** DigitalOcean (droplet, firewall, spaces, project) + Cloudflare (DNS, tunnel config)
- **Templates:** cloud-init bootstrap + Docker Compose generation

### Policy-as-Code

- **8 OPA/Rego policies:** 4 deny (prevent_destroy, encryption, public firewall, root SSH) + 4 warn (backup, naming, sizing, tags)
- **Enforcement:** conftest runs on every PR with hard-fail on deny policies

### CI/CD Pipeline

| Stage | Tools | Trigger |
|-------|-------|---------|
| PR validation | terraform fmt, validate, tflint, checkov, conftest, plan | Pull request |
| Merge security | Trivy, Semgrep, Gitleaks, terraform apply, Cosign, SBOM | Merge to main |

Gitleaks blocks hardcoded secrets. Checkov fails on security violations. OPA deny policies are hard-fail.

---

## SOAR Orchestration (n8n)

16 integrated services through a single webhook-driven entry point:

**Services:** Google Tasks, Slides, Sheets, Drive, Docs, Gmail, Workspace Admin, Microsoft Excel, Gumroad, GitHub, Ollama (local LLM), PostgreSQL, Telegram, Cloudflare, Notion, Tavily Search

**Capabilities:**
- Content research pipeline (Tavily + AI synthesis)
- Dual Telegram bot architecture (Claude AI agent + n8n routing bot)
- Voice pipeline (Faster-Whisper local transcription)
- Automated health checks and financial monitoring
- Gmail multi-account management (4 accounts)

---

## Technical Decisions

| Decision | Rationale |
|----------|-----------|
| DigitalOcean over AWS | 65% cost reduction ($48 vs $135), simpler operations, GitHub Education credit coverage |
| Falco eBPF over Wazuh | Lightweight, container-native detection without agent overhead |
| Teleport over manual SSH | Session recording, JIT access, audit trail, certificate-based auth |
| Keycloak over Auth0 | Self-hosted, full RBAC control, no per-user pricing |
| Cloudflare Tunnel over VPN | Zero-trust, no exposed ports, built-in DDoS protection |
| CPU inference over GPU | $0 AI cost, sufficient for security analysis tasks |
| OPA/Rego over manual review | Automated policy enforcement, zero human error on infrastructure rules |

---

## Author

**Emmanuel Tigoue** -- Security Engineer
- SecurityX (CASP+), SSCP, CCNA
- Portfolio: [et-sec.github.io/portfolio](https://et-sec.github.io/portfolio/)
- LinkedIn: [linkedin.com/in/emmanuel-tigoue](https://www.linkedin.com/in/emmanuel-tigoue)
- GitHub: [github.com/ET-sec](https://github.com/ET-sec)

---

*This document contains technical architecture specifications only. No credentials, PII, or operational secrets are included.*
