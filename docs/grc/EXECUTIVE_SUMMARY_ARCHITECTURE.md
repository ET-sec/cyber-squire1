# Executive Summary: Architecture

**System Name:** Organization Security Operations Platform (OSOP)
**Document Identifier:** EXEC-ARCH-001
**Classification:** Internal Use Only
**Version:** 1.2
**Date:** 2026-05-25
**Prepared By:** System Owner

---

## Platform Overview

The Organization Security Operations Platform is a containerized security operations environment deployed on a single cloud VPS. It provides centralized SOAR, identity management, runtime threat detection, secrets management, and AI-assisted analysis through 20 containerized services.

| Specification | Value |
|---------------|-------|
| **Compute** | 4 vCPU, 8 GB RAM, 160 GB SSD |
| **Operating System** | Ubuntu 24.04 LTS |
| **Container Runtime** | Docker with Compose (13 managed services + 1 standalone) |
| **Public Ingress** | Zero-trust tunnel only (Cloudflare) |
| **Firewall** | Cloud firewall with deny-all default |
| **Exposed Ports** | 0 (all traffic routed through tunnel) |

---

## Network Architecture and Trust Zones

The platform implements four trust zones with network-layer isolation:

| Zone | Services | Access |
|------|----------|--------|
| **Public** | Cloudflare Tunnel (sole entry point) | Internet-facing, TLS-terminated |
| **DMZ** | n8n SOAR (svc-automation), OpenClaw Gateway | Accessible via tunnel routes only |
| **Internal** | svc-db, svc-llm, svc-transcription, svc-log-router, svc-detection-router, svc-monitor, svc-event-shipper | No external access, Docker bridge only |
| **Sensitive** | svc-secrets, svc-identity, svc-gateway | Restricted internal access, audit-logged |

All inter-service communication occurs over Docker bridge networks. No container ports are bound to the host's public interface.

![Network Topology](diagrams/network_topology.png)
![Security Boundaries](diagrams/security_boundaries.png)

---

## Service Inventory

### Core Services

| Container | Function | Port (Internal) |
|-----------|----------|-----------------|
| svc-db | PostgreSQL 16 - workflow state and operational data | 5432 |
| svc-automation | n8n SOAR - orchestration, webhooks, Telegram bot | internal |

### Access & Identity

| Container | Function | Port (Internal) |
|-----------|----------|-----------------|
| svc-gateway | Teleport v18 - PAM, session recording, JIT access | 3080 |
| svc-identity | Keycloak v26 - RBAC, SSO, 3-tier role model | internal |
| svc-event-shipper | Teleport audit event shipper | - |

### Security & Monitoring

| Container | Function | Port (Internal) |
|-----------|----------|-----------------|
| svc-detection | Falco - eBPF kernel-level runtime detection | - |
| svc-detection-router | Falcosidekick - alert routing to Datadog | - |
| svc-monitor | Datadog Agent - metrics, logs, APM | - |
| svc-log-router | Fluentd - structured log pipeline to Datadog | - |

### AI & Analysis

| Container | Function | Port (Internal) |
|-----------|----------|-----------------|
| svc-llm | Ollama - local LLM inference | internal |
| svc-transcription | Whisper - voice transcription | internal |
| svc-ai-gateway | OpenClaw - Claude Fable 5 AI gateway | internal |

### Infrastructure

| Container | Function | Port (Internal) |
|-----------|----------|-----------------|
| tunnel | Cloudflare Tunnel, zero-trust ingress | Host network |
| svc-secrets | HashiCorp Vault, secrets management | internal |

### Squire Subsystem (Phase 17)

| Container | Function | Port (Internal) |
|-----------|----------|-----------------|
| svc-squire | LangGraph 7-node autonomous SOC analyst (classify, retrieve, enrich, investigate, draft, critique, route_severity) | internal |
| svc-nemo | NeMo Guardrails, Colang rails plus presidio PII detection | internal |
| svc-langfuse-web | Langfuse observability UI and trace ingest | internal |
| svc-langfuse-worker | Langfuse async trace processing | internal |
| svc-langfuse-clickhouse | Langfuse columnar trace storage | internal |
| svc-langfuse-redis | Langfuse dedup and cache | internal |

### Squire pipeline

```mermaid
flowchart LR
    A[alert ingress] --> CF[Cloudflare WAF]
    CF --> PRE[pre_graph_pii scanner]
    PRE --> CLF[classify node]
    CLF --> NIR[NeMo input rail]
    NIR --> RET[retrieve: pgvector ir_chunks]
    RET --> ENR[enrich: Tavily]
    ENR --> INV[investigate: Anthropic]
    INV --> DRAFT[draft node]
    DRAFT --> CRT[critique node]
    CRT --> NOR[NeMo output rail]
    NOR --> RTE[route_severity]
    RTE -->|HIGH/CRITICAL| TG[Telegram + HITL review]
    RTE -->|INFO/LOW| WH[webhook delivery]
    CLF -.trace.-> LF[Langfuse traces]
    INV -.trace.-> LF
    CRT -.trace.-> LF
```

---

## Data Flow

![Data Flow Diagram](diagrams/data_flow.png)

**Inbound:** Internet traffic terminates at Cloudflare's edge, passes through the zero-trust tunnel, and routes to internal services (n8n on `n8n.example-ops.com`, SSH via `ssh.example-ops.com`).

**Internal:** svc-automation orchestrates workflows by connecting to svc-db, Telegram Bot API, GitHub API, svc-llm, and external SaaS integrations. svc-gateway records all SSH and console sessions. svc-detection monitors syscalls via eBPF and ships alerts through svc-detection-router to Datadog.

**Outbound:** Audit logs flow from svc-event-shipper through svc-log-router to Datadog. svc-monitor ships metrics, logs, and traces to the Datadog SaaS platform.

---

## Infrastructure as Code

| Component | Detail |
|-----------|--------|
| **IaC Tool** | Terraform |
| **Files** | 20 `.tf` files |
| **State** | Remote, encrypted |
<!-- TODO(et): Verified 8 .rego policies as of 2026-06-24. Confirm count stays current when policy directory changes. -->
| **Policy Enforcement** | 8 OPA (Rego) policies evaluated on every PR |
| **Managed Resources** | VPS, firewall rules, DNS records, tunnel configuration, monitoring |

### Secrets Management

| Principle | Implementation |
|-----------|---------------|
| No hardcoded secrets | External secrets manager injects env vars at runtime |
| Encrypted at rest | `.env` file `chmod 600`, Vault for future secret rotation |
| Least privilege | Per-service env var scoping, no shared secret namespace |
| Rotation tracking | Credential vault as source of truth for rotation schedules |

---

## Key Design Decisions

1. **Single-VPS consolidation** - reduces attack surface to one hardened host with centralized monitoring
2. **Zero-trust over VPN** - Cloudflare Tunnel eliminates the need for open inbound ports or VPN infrastructure
3. **eBPF over agent-based detection** - Falco operates at the kernel level without modifying containers
4. **Compose over Kubernetes** - right-sized orchestration for a single-node deployment, lower operational complexity
5. **Immutable audit chain** - Teleport session recordings and Falco alerts ship to external SaaS (Datadog), preventing local tampering

---

## Related Documents

| Document | Description |
|----------|-------------|
| [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) | Full system description and control mapping |
| [RISK_ASSESSMENT.md](RISK_ASSESSMENT.md) | Threat scenarios and trust zone analysis |
| [IAM_RBAC_ROLE_MAP.md](IAM_RBAC_ROLE_MAP.md) | 3-tier RBAC role definitions |
| [IAM_ACCESS_REVIEW.md](IAM_ACCESS_REVIEW.md) | Access review process with JIT workflow |
| [EXECUTIVE_SUMMARY_SECURITY_POSTURE.md](EXECUTIVE_SUMMARY_SECURITY_POSTURE.md) | Security posture one-pager |
| [EXECUTIVE_SUMMARY_COMPLIANCE.md](EXECUTIVE_SUMMARY_COMPLIANCE.md) | Compliance readiness one-pager |
| [SQUIRE_SSP.md](SQUIRE_SSP.md) | Squire subsystem SSP |
| [DATA_FLOW_DIAGRAM.md](DATA_FLOW_DIAGRAM.md) | DFD including Phase 17 extension |
