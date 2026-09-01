---
document_id: SSP-OPS-001
title: System Security Plan
doc_type: ssp
system_name: Organization Security Operations Platform
classification: CUI-INTERNAL
version: "1.2"
last_updated: 2026-05-25
next_review: 2026-09-11
owner: System Owner
approver: System Owner (Authorizing Official)
frameworks:
  - NIST SP 800-53 Rev 5
  - NIST CSF 2.0
related:
  - POAM-OPS-001
  - CW-SQUIRE-001
  - SSP-SQUIRE-001
---

> **Status note (2026-09-01):** this document describes the DigitalOcean-era baseline as assessed. That environment was retired 2026-08. The platform now runs on an Oracle Cloud (OCI) ARM instance with a partial stack (3 containers live); the remaining services are pending ARM rebuild. A re-baseline of this document is queued and tracked in the POA&M.

# System Security Plan (SSP)

## Organization Security Operations Platform

**Document Identifier:** SSP-OPS-001
**Classification:** CONTROLLED UNCLASSIFIED - INTERNAL USE ONLY
**Version:** 1.2
**Last Updated:** 2026-05-25
**Next Scheduled Review:** 2026-09-11
**Prepared By:** System Owner
**Approved By:** System Owner (Authorizing Official)

---

## Table of Contents

1. [System Identification](#1-system-identification)
2. [System Description](#2-system-description)
3. [Security Categorization](#3-security-categorization)
4. [System Environment](#4-system-environment)
5. [NIST 800-53 Control Mapping](#5-nist-800-53-control-mapping)
6. [Continuous Monitoring Strategy](#6-continuous-monitoring-strategy)
7. [POA&M Reference](#7-poam-reference)
8. [Related GRC Documents](#related-grc-documents)
9. [Document Control](#8-document-control)

---

## 1. System Identification

| Field | Value |
|-------|-------|
| **System Name** | Organization Security Operations Platform (OSOP) |
| **System Abbreviation** | OSOP |
| **System Owner** | System Owner |
| **Authorizing Official** | System Owner |
| **System Type** | General Support System (GSS) |
| **Operational Status** | Operational |
| **Authorization Date** | 2026-03-11 |
| **Authorization Termination** | 2027-03-11 |
| **System Location** | DigitalOcean VPS - single-region deployment |

### 1.1 Purpose

The Organization Security Operations Platform provides centralized security orchestration, automation, and response (SOAR) capabilities for the Organization's infrastructure. The system integrates workflow automation, identity and access management, secrets management, runtime threat detection, session recording, and observability into a unified container-based platform. It serves as the operational backbone for security monitoring, incident response automation, and compliance evidence collection.

### 1.2 Authorization Boundary

The authorization boundary encompasses:

- One (1) cloud-hosted virtual private server (VPS) running Ubuntu 24.04 LTS
- Thirteen (13) containerized services operating within a Docker Compose stack
- One (1) standalone AI gateway container (not Compose-managed)
- All Terraform-managed cloud resources (VPS, firewall, DNS, tunnel, monitoring)
- CI/CD pipelines executing within the infrastructure-as-code repository
- The secrets management pipeline (external secrets manager injecting runtime environment variables)

The following are **outside** the authorization boundary:
- DigitalOcean's physical infrastructure, hypervisor, and network backbone
- The external Datadog (SaaS - shared responsibility)
- The external secrets manager (SaaS - shared responsibility)
- Third-party container registries from which base images are pulled
- End-user workstations used to administer the system

### 1.3 Information Types

| Information Type | NIST 800-60 Category | Description |
|-----------------|---------------------|-------------|
| System Audit Records | C.3.5.1 | Session recordings, access logs, syscall events |
| Authentication Data | C.2.8.1 | Passwords, TOTP seeds, session tokens |
| Infrastructure Configuration | C.3.4.1 | Terraform state, Docker Compose definitions, firewall rules |
| Workflow Automation Data | C.3.5.2 | SOAR playbooks, orchestration state, webhook payloads |
| Secrets and Credentials | C.2.8.1 | API keys, database credentials, tunnel tokens |

---

## 2. System Description

### 2.1 Architecture Overview

The platform operates as a 19-service containerized stack deployed on a single 4-vCPU / 8 GB VPS running Ubuntu 24.04 LTS. Services are segmented across three isolated Docker bridge networks: `net-core` (application and identity services), `net-ai` (LLM inference and transcription), and `net-monitoring` (observability and runtime detection). Only `svc-automation` bridges `net-core` and `net-ai` to orchestrate AI workflows. The only public ingress path is a zero-trust tunnel (`svc-tunnel`) operating in host networking mode. No service ports are directly exposed to the public internet.

```
             Internet
              |
          [ Cloud Firewall ]
              |
          [ svc-tunnel ] (host network, read-only rootfs)
           |      |
       automation.     ssh.
       example-ops.com   example-ops.com
           |      |
        +--net-core / net-ai / net-monitoring------+
        |                     |
   +----------+----------+     +--------+---------+
   | svc-automation |     | svc-gateway:3080 |
   | (SOAR engine)    |     | (SSH + recording) |
   +----------+----------+     +--------+---------+
        |               |
   +----------+----------+   +-------------+-----------+
   | svc-db:5432     |   | svc-event-shipper    |
   | (PostgreSQL 16)   |   | (gRPC -> mTLS -> logs) |
   +---------------------+   +-------------+-----------+
                        |
   +---------------------+   +-------------+-----------+
   | svc-secrets       |   | Fluentd     |
   | (secrets engine)  |   | (log pipeline -> monitoring) |
   +---------------------+   +-------------------------+

   +---------------------+   +-------------------------+
   | svc-identity       |   | svc-detection      |
   | (identity provider v26) | | (Falco) |
   +---------------------+   +-------------+-----------+
                        |
   +---------------------+   +-------------+-----------+
   | svc-llm    |   | svc-detection-router  |
   | (LLM engine)    |   | (-> Datadog) |
   +---------------------+   +-------------------------+

   +---------------------+   +-------------------------+
   | svc-transcription  |   | svc-monitor       |
   | (transcription engine) | | (agent, pid:host) |
   +---------------------+   +-------------------------+

   +-------------------------+
   | svc-ai-gateway     |
   |                    |
   | (standalone, not Compose)|
   +-------------------------+
```

### 2.2 Service Inventory

| Service | Role | Port | Network |
|---------|------|------|---------|
| `svc-db` | PostgreSQL 16 - persistent workflow state and application data | default | net-core |
| `svc-automation` | Workflow orchestration engine (SOAR) - 16+ automation actions | 5678 | net-core, net-ai |
| `svc-llm` | Local LLM inference - private AI processing | internal | net-ai |
| `svc-transcription` | Voice-to-text - local transcription, no external API calls | internal | net-ai |
| `svc-secrets` | Secrets engine - centralized secrets, AppRole auth, short-lived leases | internal | net-core |
| `svc-identity` | Identity provider (v26) - SSO, RBAC (3 roles), OIDC provider | internal | net-core |
| `svc-gateway` | Access gateway (v18) - zero-trust SSH, session recording, TOTP MFA, JIT access | internal | net-core |
| `svc-monitor` | Observability agent - container logs, metrics, process monitoring | N/A | net-monitoring |
| `svc-detection` | Runtime detection engine - eBPF-based syscall monitoring across all containers | N/A | net-monitoring |
| `svc-detection-router` | Routes runtime detection events to Datadog (Events + Logs API) | internal | net-monitoring |
| `Fluentd` | Log pipeline agent - receives access gateway audit events via mTLS, forwards to monitoring | internal | net-monitoring |
| `svc-event-shipper` | Streams access gateway audit events via gRPC to `Fluentd` using mTLS | N/A | net-core, net-monitoring |
| `svc-tunnel` | Zero-trust tunnel - sole public ingress path, read-only rootfs | host | host |
| `svc-ai-gateway` | AI agent gateway - standalone container, not Compose-managed | internal | bridge (default) |

### 2.3 Data Flows

**Inbound (User to Platform):**
1. User requests traverse the public internet to the cloud firewall.
2. The firewall permits only ICMP and emergency SSH (port 22 - accepted risk, documented).
3. All application traffic enters through `svc-tunnel` (zero-trust tunnel with TLS encryption).
4. `svc-tunnel` routes `automation.example-ops.com` to `svc-automation` and `ssh.example-ops.com` to `svc-gateway` or local SSH.

**Internal (Service to Service):**
1. `svc-automation` connects to `svc-db` on port 5432 (depends_on health check gating).
2. `svc-identity` shares the PostgreSQL backend with `svc-automation` via `svc-db`.
3. `svc-gateway` records SSH sessions locally and syncs to its auth component (node-sync mode).
4. `svc-event-shipper` streams access gateway audit events via gRPC to `Fluentd` using mutual TLS (mTLS).
5. `Fluentd` forwards audit events to the external Datadog's Logs API.
6. `svc-detection` monitors syscalls via eBPF across all containers and pushes events to `svc-detection-router`.
7. `svc-detection-router` forwards runtime detection events to Datadog's Events and Logs APIs.
8. `svc-monitor` collects Docker metrics, container logs, host system metrics, and process data.

**Outbound (Platform to External):**
1. `svc-tunnel` maintains a persistent outbound connection to the tunnel provider's edge network.
2. `svc-monitor`, `svc-detection-router`, and `Fluentd` transmit telemetry to `datadoghq.com`.
3. `svc-automation` makes outbound API calls for workflow execution (webhooks, API integrations).
4. `svc-ai-gateway` communicates with external AI model providers via HTTPS.

### 2.4 Network Segmentation

The 19 Compose-managed services are segmented across three isolated Docker bridge networks. `net-core` hosts application, identity, and secrets services (svc-automation, svc-db, svc-secrets, svc-identity, svc-gateway). `net-ai` isolates LLM inference and transcription (svc-llm, svc-transcription). `net-monitoring` isolates observability and runtime detection (svc-monitor, svc-detection, svc-detection-router, Fluentd). `svc-automation` bridges net-core and net-ai to orchestrate AI workflows. `svc-event-shipper` bridges net-core and net-monitoring for audit event forwarding. Only `svc-tunnel` uses host networking mode, as required for tunnel operation. No container ports are bound to the host's public interface except through the tunnel ingress path.

DigitalOcean's firewall restricts inbound traffic to ICMP (health checks) and TCP/22 (emergency SSH). All application access is brokered through the zero-trust tunnel, which terminates TLS at the tunnel provider's edge and re-originates connections to local services.

---

## 3. Security Categorization

### 3.1 FIPS 199 Categorization

Security categorization is performed in accordance with FIPS 199, *Standards for Security Categorization of Federal Information and Information Systems*, and NIST SP 800-60, *Guide for Mapping Types of Information and Information Systems to Security Categories*.

| Security Objective | Impact Level | Justification |
|-------------------|-------------|---------------|
| **Confidentiality** | Moderate | The system processes authentication credentials, API keys, session recordings, and infrastructure configuration. Unauthorized disclosure could compromise the integrity of managed infrastructure and expose operational patterns. |
| **Integrity** | Moderate | The system executes automated workflows that modify infrastructure state, manage credentials, and orchestrate incident response. Unauthorized modification of workflows, audit logs, or configuration could undermine trust in operational decisions. |
| **Availability** | Moderate | The system provides SOAR capabilities, monitoring, and alerting for the Organization's infrastructure. Extended unavailability would degrade incident detection and response capabilities, though manual fallback procedures exist. |

**Overall System Categorization: MODERATE**

SC OSOP = {(Confidentiality, Moderate), (Integrity, Moderate), (Availability, Moderate)}

### 3.2 Baseline Selection

The system applies NIST SP 800-53 Rev. 5 controls at the **Moderate** baseline. Control tailoring has been performed to account for the single-tenant, containerized deployment model and the cloud shared-responsibility boundary.

---

## 4. System Environment

### 4.1 Cloud Infrastructure

| Component | Specification |
|-----------|--------------|
| **Provider** | DigitalOcean (IaaS) |
| **Compute** | Single VPS - 4 vCPU, 8 GB RAM, 160 GB SSD |
| **Operating System** | Ubuntu 24.04 LTS (x64) |
| **Region** | Single-region deployment |
| **Network** | Private VPC with dedicated CIDR block |
| **Firewall** | Cloud-native firewall (Terraform-managed) |
| **Object Storage** | Provider-managed bucket with versioning (Terraform state, audit log export) |

### 4.2 Container Runtime

| Component | Specification |
|-----------|--------------|
| **Engine** | Docker (Compose v2) |
| **Orchestration** | Docker Compose (single-node) |
| **Network** | Bridge driver (3 networks: `net-core`, `net-ai`, `net-monitoring`), host mode for `svc-tunnel` only |
| **Image Sources** | Docker Hub (Langfuse, Redis, ClickHouse, pgvector, n8n, Datadog, Falco, cloudflared), Quay.io (svc-identity), AWS ECR Public (svc-gateway), GHCR (locally-built svc-squire and svc-nemo) |
| **Image Verification** | Container signature verification in CI/CD pipeline |
| **SBOM Generation** | SPDX-JSON format, per-image SBOMs generated on merge to main |

### 4.3 Infrastructure as Code

| Component | Specification |
|-----------|--------------|
| **IaC Tool** | Terraform (HCL) |
| **State Backend** | Remote - cloud object storage with versioning enabled |
| **Modules** | Compute, networking, firewall, DNS, tunnel config, monitoring (Terraform-managed dashboards and monitors), SSH keys |
| **Policy Engine** | Infrastructure policy engine - 8 Rego policies enforced in CI |
| **Linting** | Terraform linter with provider-specific ruleset |
| **Static Analysis** | Checkov with custom configuration |

### 4.4 CI/CD Pipeline

Two GitHub Actions workflows protect the main branch:

**Security & Deploy Pipeline** (`security.yml`) - triggers on push to `main`/`dev` and PRs to `main`:
- Secrets scanner: secrets detection across full commit history
- CVE scanner: filesystem and dependency CVE scanning (CRITICAL/HIGH, fail on findings)
- SAST scanner: SAST with security-audit, secrets, docker, and terraform rulesets
<!-- TODO(et): Confirm Cosign step enforcement level. Earlier QC noted continue-on-error (advisory only); verify against current .github/workflows/security.yml. -->
- Container verification: container signature verification for all upstream images
<!-- TODO(et): "6 container images" needs refresh. Compose has more services now; recount images covered by SBOM job. -->
- SBOM generation: SPDX-JSON for repository filesystem and 6 container images (90-day retention)
- Terraform apply: automated infrastructure deployment after security scan passes

**Terraform PR Validation** (`terraform-pr.yml`) - triggers on PRs modifying IaC:
- `terraform fmt -check` (format enforcement)
- `terraform validate` (syntax validation)
- Terraform linter (provider-aware linting)
- Checkov (CIS benchmark scanning)
- `terraform plan` (drift detection)
- Policy engine (8 custom Rego policies against plan JSON)
- Automated PR comment with validation results

### 4.5 Secrets Management Pipeline

All secrets are managed through an external secrets manager and injected as environment variables at runtime. No secrets are hardcoded in source code, Terraform configurations, or Docker Compose files. The secrets pipeline follows this flow:

```
Credential Vault (source of truth, biometric-locked)
  |
  v
Secrets Manager (runtime, project: prd)
  |
  v
Runtime injection: env vars via `secrets-manager run -- <command>`
  |
  v
Containers consume secrets from environment variables only
```

The `.env` file on the VPS is `chmod 600` (root-only readable). Terraform state is encrypted at rest in the remote backend. CI/CD secrets are stored in the repository's encrypted secrets store.

---

## 5. NIST 800-53 Control Mapping

The following tables document the implementation status of NIST SP 800-53 Rev. 5 controls at the Moderate baseline, organized by control family.

### Legend

| Status | Definition |
|--------|-----------|
| **Implemented** | Control is fully deployed and operational |
| **Partially Implemented** | Control is deployed but not all aspects are complete |
| **Planned** | Control is documented in the roadmap but not yet deployed |
| **Not Applicable** | Control does not apply to this system environment |
| **Inherited** | Control is satisfied by DigitalOcean or external service |

---

### 5.1 AC - Access Control

| Control ID | Control Name | Status | Implementation Description | Evidence Location |
|-----------|-------------|--------|---------------------------|-------------------|
| AC-1 | Policy and Procedures | Implemented | Access control policies are documented in this SSP and enforced through identity provider RBAC configuration and access gateway role definitions. Three-tier RBAC model (admin, operator, auditor) is codified in `svc-identity` realm configuration. | `docs/grc/SSP_SYSTEM_SECURITY_PLAN.md`; identity provider realm export |
| AC-2 | Account Management | Implemented | User accounts are provisioned and managed through `svc-identity` (identity provider v26). Three roles defined: `cd-admin` (full access), `cd-operator` (workflow and service management), `cd-auditor` (read-only monitoring and log access). Account lifecycle is managed through identity provider admin console with admin event logging enabled. | `svc-identity` admin console; identity provider admin event logs |
| AC-3 | Access Enforcement | Implemented | Access enforcement is implemented at multiple layers: (1) `svc-identity` enforces RBAC via OIDC tokens for application access; (2) `svc-gateway` enforces role-based SSH access with per-node permissions; (3) Cloud firewall restricts network-level access to ICMP and emergency SSH only; (4) `svc-tunnel` provides zero-trust application-layer access control. | `terraform/*/firewall.tf`; identity provider client scopes; access gateway role YAML |
| AC-4 | Information Flow Enforcement | Implemented | Information flow is enforced through Docker network segmentation. All services communicate over three segmented Docker bridge networks (`net-core`, `net-ai`, `net-monitoring`). `svc-tunnel` is the sole ingress path (host networking). No container ports are bound to the host's public interface. Egress is unrestricted for operational requirements (API integrations, telemetry). | `docker-compose.yaml` (network definitions); `terraform/*/firewall.tf` |
| AC-5 | Separation of Duties | Partially Implemented | Three-tier RBAC separates administrative, operational, and audit functions. The `cd-auditor` role provides read-only access to logs and monitoring without ability to modify configurations. Full separation requires a second admin account for break-glass scenarios. | identity provider realm role definitions |
| AC-6 | Least Privilege | Implemented | Containers run with `no-new-privileges` security option (18 of 19 services). `svc-detection` requires `SYS_ADMIN` capability for eBPF - this is an accepted risk with compensating controls (apparmor:unconfined is documented, all other capabilities are dropped via `cap_drop: ALL`). Resource limits (CPU, memory, PIDs) are enforced on all containers. JIT access via `svc-gateway` grants elevated privileges with 4-hour TTL auto-expiration. | `docker-compose.yaml` (security_opt, deploy.resources); access gateway JIT role definitions |
| AC-7 | Unsuccessful Logon Attempts | Implemented | `svc-identity` enforces lockout policy after failed authentication attempts. Failed SSH login attempts are monitored by `svc-monitor` with alerting configured at 5 (warning) and 10 (critical) failures within a 5-minute window. `svc-gateway` records all authentication events. | `terraform/*/monitoring.tf` (ssh_failed_login monitor); identity provider brute force detection settings |
| AC-8 | System Use Notification | Planned | Login banners are not yet configured for SSH and web application access. Planned for implementation via access gateway MOTD and identity provider login theme customization. | N/A - POA&M item |
| AC-9 | Previous Logon Notification | Partially Implemented | `svc-gateway` records all session start/end events. Session history is available in the access gateway audit log. Proactive notification to users of their last login time is not yet implemented in the web UI. | access gateway audit log (`session.start`, `user.login` events) |
| AC-10 | Concurrent Session Control | Partially Implemented | `svc-identity` supports session limits per client. `svc-gateway` enforces max session TTL. Global concurrent session caps across all access methods are not yet enforced. | identity provider session settings; access gateway role `max_session_ttl` |
| AC-11 | Session Lock | Implemented | Session lock functionality is provided through: (1) `svc-identity` (identity provider) enforces SSO idle timeout of 30 minutes, requiring re-authentication after inactivity; (2) `svc-gateway` (Teleport) enforces certificate-based session TTLs that auto-expire (4h admin, 8h operator, 10h SSO). Idle sessions are terminated and require re-authentication to resume. | `svc-identity` realm configuration (SSO session idle timeout); `svc-gateway` role definitions (`max_session_ttl`) |
| AC-12 | Session Termination | Implemented | `svc-gateway` enforces session TTL with automatic termination. JIT-elevated sessions expire after 4 hours. `svc-identity` enforces OIDC token expiration and refresh token limits. Idle session timeout is configured in `svc-automation`. | access gateway role definitions (`max_session_ttl`); identity provider token settings |

---

### 5.2 AU - Audit and Accountability

| Control ID | Control Name | Status | Implementation Description | Evidence Location |
|-----------|-------------|--------|---------------------------|-------------------|
| AU-1 | Policy and Procedures | Implemented | Audit policy is documented in this SSP. The platform implements defense-in-depth audit logging across four independent collection mechanisms: session recording (`svc-gateway`), syscall monitoring (`svc-detection`), container/host metrics (`svc-monitor`), and application-level logging (each service's JSON log output). | This document; `docker-compose.yaml` (logging configuration) |
| AU-2 | Event Logging | Implemented | The following events are logged: (1) Authentication success/failure (identity provider admin events, svc-gateway `user.login`); (2) SSH session start/end with full session recording (`svc-gateway`); (3) Privilege escalation and access request events (`svc-gateway` `access_request.*`); (4) Container lifecycle events (`svc-monitor`); (5) Syscall-level security events (`svc-detection`); (6) Failed SSH login attempts (host auth.log ingested by `svc-monitor`); (7) Database connection metrics (PostgreSQL integration). | Datadog dashboards; `terraform/*/monitoring.tf`; `terraform/*/dashboard.tf` |
| AU-3 | Content of Audit Records | Implemented | Audit records contain: timestamp, event type, source identity, outcome (success/failure), and affected resource. Access gateway events include user, session ID, server, and command. Runtime detection events include process name, container ID, syscall, and rule that triggered. All container logs include structured JSON with container name, timestamp, and log level. | access gateway audit event schema; detection rule output format; Docker JSON log driver |
| AU-4 | Audit Log Storage Capacity | Implemented | Container logs are configured with rotation: `max-size: 10m`, `max-file: 3` across all 19 services. This prevents disk exhaustion from log growth. Datadog provides 15-day log retention (standard tier). Audit logs are exported to versioned object storage for long-term retention. Disk usage is monitored with alerts at 80% (warning) and 90% (critical). | `docker-compose.yaml` (logging.options); `terraform/*/monitoring.tf` (disk_usage_high) |
| AU-5 | Response to Audit Logging Process Failures | Implemented | Container health checks detect logging subsystem failures. If `svc-detection` or `svc-monitor` containers fail, the container down monitor triggers a critical alert (threshold: fewer than 4 running containers). `svc-detection-router` health check validates event routing is operational. `Fluentd` health check confirms log pipeline agent is accepting events. All alerts route to the SOAR platform via webhook relay. | `terraform/*/monitoring.tf` (container_down); `docker-compose.yaml` (healthcheck definitions) |
| AU-6 | Audit Record Review, Analysis, and Reporting | Implemented | Audit records are reviewed through the Terraform-managed SOC dashboard, which provides five operational views: Infrastructure Health, Container Fleet, Security Operations, Application Performance, and Compliance Posture. The Security Operations panel displays runtime detection alerts, failed SSH attempts (24h), runtime detection events by priority (7d), and SSH auth failure log stream. | `terraform/*/dashboard.tf` (SOC dashboard definition) |
<!-- TODO(et): Verify Datadog retention claim still applies given current Datadog tier. -->
| AU-7 | Audit Record Reduction and Report Generation | Partially Implemented | Datadog provides log search, filtering by source/service/status, and faceted aggregation. Custom monitors generate threshold-based reports. Full automated compliance report generation from audit data is not yet implemented. | Datadog log explorer; `terraform/*/monitoring.tf` |
| AU-8 | Time Stamps | Implemented | All containers inherit the host system clock (UTC). The host runs NTP synchronization via systemd-timesyncd. Docker log timestamps are generated by the host kernel. Access gateway, Falco, and log pipeline agent events include ISO 8601 timestamps with timezone information. | Host NTP configuration; Docker daemon time handling |
| AU-9 | Protection of Audit Information | Implemented | Audit logs shipped to the external Datadog are protected by the platform's access controls. Access gateway audit events are transmitted to `Fluentd` via mTLS (mutual TLS with client certificate authentication), preventing tampering in transit. `svc-detection-router` operates with a read-only rootfs. Local container logs are accessible only to root. Audit logs exported to object storage use versioning to prevent overwrites. | `docker-compose.yaml` (svc-detection-router: read_only: true); mTLS certificates in `Fluentd` and `svc-event-shipper` volume mounts |
| AU-10 | Non-repudiation | Implemented | `svc-gateway` session recordings capture full terminal I/O with user identity binding. Access gateway audit events include authenticated user identity, session ID, and server address. SOAR workflow execution logs capture the triggering event and authenticated context. | access gateway session recordings; access gateway audit events |
| AU-11 | Audit Record Retention | Partially Implemented | Datadog retains logs for 15 days (standard tier). Audit logs are exported to versioned object storage for extended retention. Full retention policy with defined retention periods per log category is documented but automated lifecycle management (e.g., S3 lifecycle rules) is not yet configured. | Datadog retention settings; Object storage bucket configuration |
| AU-12 | Audit Record Generation | Implemented | Audit records are generated by four independent subsystems: (1) `svc-gateway` generates SSH session events via gRPC to `svc-event-shipper`; (2) `svc-detection` generates syscall-level events via detection rules to `svc-detection-router`; (3) `svc-monitor` collects container and host logs via Docker socket (read-only mount); (4) Each service generates application-level logs captured by the Docker JSON log driver. All four subsystems operate independently - failure of one does not affect the others. | `docker-compose.yaml` (volume mounts, depends_on chains); detection rules in `detection-config-volume/rules/` |

---

### 5.3 CA - Assessment, Authorization, and Monitoring

| Control ID | Control Name | Status | Implementation Description | Evidence Location |
|-----------|-------------|--------|---------------------------|-------------------|
| CA-1 | Policy and Procedures | Implemented | Security assessment and authorization policies are documented in this SSP. Annual review cycle is established. | This document (Section 8 - Document Control) |
| CA-2 | Control Assessments | Partially Implemented | Controls are assessed through automated mechanisms: CI/CD pipeline (Trivy, Semgrep, Gitleaks, Checkov), infrastructure policy enforcement, and CIS Docker Bench scans tracked on the SOC dashboard. Formal independent assessment has not been conducted. | `.github/workflows/security.yml`; `.github/workflows/terraform-pr.yml`; `terraform/*/dashboard.tf` (Compliance Posture group) |
| CA-3 | Information Exchange | Implemented | System interconnections are documented in this SSP (Section 2.3 - Data Flows). External connections include: Datadog (telemetry), tunnel provider (ingress), AI model provider (inference), and secrets manager (credential retrieval). All external connections use TLS encryption. | This document (Section 2.3) |
| CA-5 | Plan of Action and Milestones | Implemented | A POA&M is maintained for tracking open findings and remediation timelines. See Section 7. | `docs/grc/POAM_PLAN_OF_ACTION.md` |
| CA-6 | Authorization | Implemented | System Owner serves as the Authorizing Official for this system. Authorization is documented in this SSP with a 12-month authorization period. | This document (Section 1) |
| CA-7 | Continuous Monitoring | Implemented | Continuous monitoring is implemented through: (1) Real-time container and host metrics via `svc-monitor`; (2) Real-time syscall detection via `svc-detection`; (3) Automated CI/CD security scanning on every commit; (4) Terraform health checks validating service reachability; (5) Seven Terraform-managed monitors with threshold-based alerting and automated notification; (6) SOC dashboard with five operational views. See Section 6 for the full continuous monitoring strategy. | `terraform/*/monitoring.tf`; `terraform/*/dashboard.tf`; `terraform/*/checks.tf` |

---

### 5.4 CM - Configuration Management

| Control ID | Control Name | Status | Implementation Description | Evidence Location |
|-----------|-------------|--------|---------------------------|-------------------|
| CM-1 | Policy and Procedures | Implemented | Configuration management policy mandates all infrastructure changes flow through version-controlled IaC (Terraform) with mandatory PR review and automated validation. Docker Compose definitions are version-controlled in the same repository. | Repository CI/CD configuration; this document |
| CM-2 | Baseline Configuration | Implemented | The system baseline is defined by: (1) Terraform HCL files defining all cloud resources (19 .tf files across compute, networking, firewall, DNS, tunnel, monitoring, dashboard, secrets pipeline, SSH keys, project, outputs, checks, variables, providers, templates); (2) `docker-compose.yaml` defining all 19 services with pinned image versions where applicable; (3) Policy engine (Rego) rules defining 8 configuration constraints. | `terraform/*/` (19 .tf files); `docker-compose.yaml`; `terraform/*/policy/` (8 .rego files) |
| CM-3 | Configuration Change Control | Implemented | All configuration changes follow a controlled process: (1) Changes are submitted as pull requests; (2) `terraform-pr.yml` runs 7 automated checks (fmt, init, validate, lint, IaC compliance scan, plan, OPA); (3) PR comment auto-generated with pass/fail status for each check; (4) Merge to main triggers security scanning then automated `terraform apply`; (5) `prevent_destroy` lifecycle rules protect critical resources from accidental deletion. | `.github/workflows/terraform-pr.yml`; `.github/workflows/security.yml` |
| CM-4 | Impact Analyses | Implemented | Terraform plan output is generated and displayed in PR comments for every infrastructure change. The plan shows resources to be created, modified, or destroyed. Infrastructure policies evaluate the plan JSON to deny high-risk changes (public firewall rules, missing encryption, production resource deletion, root SSH keys). Checkov performs CIS benchmark analysis against proposed changes. | `.github/workflows/terraform-pr.yml` (plan step, OPA/Conftest step); `terraform/*/policy/*.rego` |
| CM-5 | Access Restrictions for Change | Implemented | Repository branch protection requires PR review before merge to main. CI/CD secrets are stored in encrypted repository secrets (not accessible to forks or PRs from external contributors). Terraform apply only executes on merge to main after security scan passes. SSH access to the production VPS requires key-based authentication. | Repository branch protection settings; `.github/workflows/security.yml` (terraform-apply job conditions) |
| CM-6 | Configuration Settings | Implemented | Container security settings are standardized: (1) `no-new-privileges: true` on 18/19 containers; (2) Resource limits (CPU, memory, PIDs) on all containers; (3) Log rotation (10MB max, 3 files) on all containers; (4) Health checks on all containers; (5) Read-only rootfs on `svc-tunnel` and `svc-detection-router`; (6) `cap_drop: ALL` + minimum required capabilities on `svc-detection`. Deviations are documented as accepted risks with compensating controls. | `docker-compose.yaml` (security_opt, deploy.resources, logging, healthcheck, read_only, cap_drop/cap_add) |
| CM-7 | Least Functionality | Implemented | Each container runs a single service with a defined purpose. No container includes development tools, compilers, or package managers beyond what the upstream image provides. `svc-detection-router` and `svc-tunnel` use read-only root filesystems with tmpfs for required writable paths. PID limits prevent fork bombs. APM is explicitly disabled on `svc-monitor` (`DD_APM_ENABLED=false`) as it is not needed. | `docker-compose.yaml` (single process per container, read_only, tmpfs, pids limit) |
| CM-8 | System Component Inventory | Implemented | The system component inventory is maintained through: (1) `docker-compose.yaml` as the authoritative service manifest (19 services with pinned images); (2) Terraform state as the authoritative cloud resource inventory; (3) SBOM generation (SPDX-JSON) for the repository and 6 container images on every merge to main, with 90-day artifact retention. | `docker-compose.yaml`; Terraform state (remote backend); `.github/workflows/security.yml` (sbom job) |

---

### 5.5 CP - Contingency Planning

| Control ID | Control Name | Status | Implementation Description | Evidence Location |
|-----------|-------------|--------|---------------------------|-------------------|
| CP-1 | Policy and Procedures | Implemented | Business Continuity Policy (POL-BC-001) and Disaster Recovery Policy (POL-DR-001) establish contingency planning procedures with defined roles, recovery objectives, and communication protocols. | `docs/grc/POLICY_BUSINESS_CONTINUITY.md`; `docs/grc/POLICY_DISASTER_RECOVERY.md` |
| CP-2 | Contingency Plan | Implemented | BCP defines continuity procedures with RTO/RPO targets, communication tree, and roles. DRP defines recovery procedures with step-by-step restoration instructions. Recovery procedures also embedded in monitor remediation runbooks. | `docs/grc/POLICY_BUSINESS_CONTINUITY.md`; `docs/grc/POLICY_DISASTER_RECOVERY.md`; `terraform/*/monitoring.tf` |
| CP-3 | Contingency Training | Partially Implemented | Tabletop exercise (Operation Phantom Container) documented with 5-phase scenario covering container compromise, lateral movement, and recovery. Semi-annual cadence established. | `docs/grc/TABLETOP_EXERCISE.md` |
| CP-4 | Contingency Plan Testing | Partially Implemented | Tabletop exercise validates contingency plan procedures including detection, containment, eradication, and recovery phases. Individual service recovery validated through operational restart procedures. | `docs/grc/TABLETOP_EXERCISE.md` |
| CP-6 | Alternate Storage Site | Implemented | Terraform state is stored in versioned object storage (remote backend with versioning enforced by infrastructure policy). Database backups are mounted to a dedicated backup volume (`CD_BACKUPS`). Off-site backup replication is planned but not yet implemented. | `terraform/*/terraform.tf` (backend config); `docker-compose.yaml` (CD_BACKUPS volume); `terraform/*/policy/deny_no_encryption.rego` (versioning enforcement) |
| CP-7 | Alternate Processing Site | Partially Implemented | The Terraform IaC codebase enables rapid reconstruction of the entire platform on a new VPS instance. All infrastructure is declaratively defined. Data restoration depends on database backup availability and Terraform state recovery from the versioned remote backend. Full hot/warm standby is not implemented. | `terraform/*/` (full IaC definition); Docker Compose (reproducible service stack) |
| CP-9 | System Backup | Partially Implemented | PostgreSQL backups are stored in the `CD_BACKUPS` volume. Terraform state is versioned in remote object storage. Docker volumes for persistent data (`svc-db`, `svc-automation`, `svc-secrets`, `svc-gateway`) are on local disk. Automated scheduled backup with off-site replication is planned. Infrastructure policy warns when VPS backups are not enabled. | `docker-compose.yaml` (backup volume mount); `terraform/*/policy/warn_backup.rego` |
| CP-10 | System Recovery and Reconstitution | Partially Implemented | The IaC codebase, Docker Compose definitions, and identity provider realm export enable full platform reconstitution from source control. `prevent_destroy` lifecycle rules on critical Terraform resources protect against accidental deletion. Recovery to a known-good state requires: (1) `terraform apply` for cloud resources; (2) `docker compose up -d` for services; (3) Database restore from backup; (4) Re-import `svc-identity` realm. | `terraform/*/compute.tf` (prevent_destroy); `docker-compose.yaml`; identity-import volume |

---

### 5.6 IA - Identification and Authentication

| Control ID | Control Name | Status | Implementation Description | Evidence Location |
|-----------|-------------|--------|---------------------------|-------------------|
| IA-1 | Policy and Procedures | Implemented | Authentication policy requires: (1) key-based SSH authentication (password auth disabled); (2) TOTP MFA for all `svc-gateway` users; (3) identity-provider-managed authentication for web application access; (4) API key authentication for programmatic access. | This document; access gateway auth config; identity provider realm settings |
| IA-2 | Identification and Authentication (Organizational Users) | Implemented | Users authenticate through `svc-identity` (identity provider) for web access and `svc-gateway` (Teleport) for SSH access. Both systems require unique user accounts. SSH access requires Ed25519 key-based authentication. `svc-gateway` enforces TOTP as a mandatory second factor for all users. | identity provider user database; access gateway user and role configuration |
| IA-2(1) | Multi-Factor Authentication to Privileged Accounts | Implemented | `svc-gateway` enforces TOTP MFA for all SSH access (second_factor: otp). JIT privilege escalation requires explicit access request approval in addition to existing MFA. Admin access to `svc-identity` requires authenticated session. | access gateway cluster auth_preference (`second_factor: otp`); JIT role configuration |
| IA-2(2) | Multi-Factor Authentication to Non-Privileged Accounts | Partially Implemented | MFA is enforced for SSH access via `svc-gateway`. Web application access through `svc-identity` supports MFA but does not mandate it for all users. Enforcement of MFA for all identity-provider-authenticated access is planned. | access gateway auth config; identity provider authentication flow settings |
| IA-3 | Device Identification and Authentication | Partially Implemented | SSH access requires Ed25519 key authentication, which implicitly identifies the connecting device. `svc-event-shipper` authenticates to `Fluentd` via mTLS client certificates. Service-to-service authentication within the Docker network relies on network isolation. | SSH key configuration; mTLS certificate chain for event shipping |
| IA-4 | Identifier Management | Implemented | User identifiers are managed through `svc-identity` (identity provider). Unique usernames are enforced. Service accounts (e.g., access gateway event-handler) have dedicated identities with scoped permissions. SSH keys are named per individual user - infrastructure policy denies keys named "root" to prevent shared credential patterns. | identity provider user management; `terraform/*/policy/deny_root_ssh_key.rego` |
| IA-5 | Authenticator Management | Implemented | Authenticator management is implemented through: (1) `svc-identity` password policies (minimum length, complexity, expiration); (2) SSH key management via Terraform (Ed25519 keys only); (3) TOTP seed generation and binding in `svc-gateway`; (4) API keys managed through external secrets manager with injection at runtime; (5) No secrets hardcoded in source - enforced by Gitleaks in CI/CD. | svc-identity password policy settings; `terraform/*/ssh.tf`; `.github/workflows/security.yml` (secrets scanner step) |
| IA-5(1) | Password-Based Authentication | Implemented | `svc-identity` enforces password complexity requirements through realm-level password policies. Brute force detection is enabled. Container service accounts use environment-injected credentials from the external secrets manager - passwords are never stored in source code. | identity provider realm password policy; `terraform/*/secrets.tf` (secrets pipeline documentation) |
| IA-6 | Authentication Feedback | Implemented | `svc-identity` provides generic error messages on authentication failure (does not distinguish between invalid username and invalid password). `svc-gateway` masks TOTP details in error responses. | identity provider login theme; access gateway authentication error handling |
| IA-8 | Identification and Authentication (Non-Organizational Users) | Not Applicable | The system does not support non-organizational user access. All authenticated access is restricted to Organization personnel. | N/A |

---

### 5.7 IR - Incident Response

| Control ID | Control Name | Status | Implementation Description | Evidence Location |
|-----------|-------------|--------|---------------------------|-------------------|
| IR-1 | Policy and Procedures | Implemented | Incident response policy is documented in the formal Incident Response Policy (POL-IR-001). The policy defines purpose, scope, roles and responsibilities, incident classification, and procedures for all IR lifecycle phases. Operational response procedures are additionally embedded in Terraform-managed monitor remediation runbooks. | `docs/grc/POLICY_INCIDENT_RESPONSE.md`; `terraform/*/monitoring.tf` (remediation steps in monitor messages) |
| IR-2 | Incident Response Training | Partially Implemented | Tabletop exercise (Operation Phantom Container) provides IR training through a 5-phase scenario. Four IR playbooks document response procedures for training reference. Semi-annual exercise cadence established. | `docs/grc/TABLETOP_EXERCISE.md`; `docs/grc/PLAYBOOK_*.md` |
| IR-3 | Incident Response Testing | Implemented | Tabletop exercise (Operation Phantom Container) defines a 5-phase TTX with inject cards, expected actions, and evaluation criteria. Exercise covers compromised container detection, lateral movement analysis, credential rotation, and post-incident review. | `docs/grc/TABLETOP_EXERCISE.md` |
| IR-4 | Incident Handling | Implemented | Automated incident handling is implemented through the SOAR pipeline: (1) `svc-detection` generates syscall-level alerts; (2) `svc-monitor` generates infrastructure and security alerts; (3) Seven Terraform-managed monitors with severity-tiered thresholds; (4) Webhook relay routes alerts to SOAR engine; (5) SOAR engine relays to messaging platform with severity filtering; (6) DND downtime schedule mutes warning/error alerts 10 PM - 8:30 AM ET while critical alerts always notify. | `terraform/*/monitoring.tf` (monitors, webhook, DND schedules); `svc-automation` webhook workflows |
| IR-5 | Incident Monitoring | Implemented | Incident monitoring is continuous through: (1) SOC dashboard with Security Operations panel (runtime detection alerts, failed SSH attempts, auth failure log stream); (2) Seven automated monitors (disk, containers, SSH, CPU, memory, PostgreSQL, svc-automation restarts); (3) Falco eBPF syscall monitoring with custom per-container rules; (4) access gateway audit event streaming to Datadog. | `terraform/*/dashboard.tf`; `terraform/*/monitoring.tf`; Falco rule files |
| IR-6 | Incident Reporting | Partially Implemented | Automated alert notifications are sent to the messaging platform. Formal incident reporting templates and escalation procedures are planned. | SOAR webhook relay configuration |
| IR-7 | Incident Response Assistance | Partially Implemented | Remediation runbooks are embedded in alert definitions, providing step-by-step commands for common incidents. The SOAR platform provides 16 automation actions for response activities. Formal incident response assistance contacts and escalation paths are planned. | `terraform/*/monitoring.tf` (remediation blocks); SOAR master orchestrator |
| IR-8 | Incident Response Plan | Implemented | The Incident Response Policy (POL-IR-001) includes the incident response plan covering: incident classification taxonomy, detection and analysis procedures, containment and eradication steps, recovery and post-incident activities, communication protocols, and escalation paths. Four operational playbooks provide scenario-specific response procedures for compromised containers, leaked credentials, DDoS/service degradation, and unauthorized access. | `docs/grc/POLICY_INCIDENT_RESPONSE.md`; `docs/grc/PLAYBOOK_COMPROMISED_CONTAINER.md`; `docs/grc/PLAYBOOK_LEAKED_CREDENTIAL.md`; `docs/grc/PLAYBOOK_DDOS_SERVICE_DEGRADATION.md`; `docs/grc/PLAYBOOK_UNAUTHORIZED_ACCESS.md` |

---

### 5.8 MA - Maintenance

| Control ID | Control Name | Status | Implementation Description | Evidence Location |
|-----------|-------------|--------|---------------------------|-------------------|
| MA-1 | Policy and Procedures | Partially Implemented | Maintenance procedures are documented operationally (safe restart commands, volume permission fixes). The Change Management Policy defines the change control process, approval workflows, emergency change procedures, and rollback requirements for all system maintenance activities. A formal standalone maintenance policy is planned. | `docs/grc/POLICY_CHANGE_MANAGEMENT.md`; `docker-compose.yaml` (operational procedures) |
| MA-2 | Controlled Maintenance | Implemented | System maintenance is controlled through: (1) Terraform-managed infrastructure changes with PR review and automated validation; (2) Docker Compose service restarts follow documented safe procedures; (3) DND maintenance windows (10 PM - 8:30 AM ET) suppress non-critical alerts during maintenance periods; (4) Container image updates are tracked through SBOM generation and container signature verification. | `.github/workflows/terraform-pr.yml`; `terraform/*/monitoring.tf` (DND schedules) |
| MA-3 | Maintenance Tools | Implemented | Maintenance tools are restricted to: Terraform CLI, Docker Compose CLI, SSH (key-based), and the SOAR engine's API. All tools authenticate via managed credentials. No interactive maintenance tools are installed on the production system beyond standard OS utilities. | SSH access controls; Terraform CLI configuration |
| MA-4 | Nonlocal Maintenance | Implemented | All maintenance is performed remotely via: (1) `svc-tunnel` (zero-trust tunnel for SOAR engine access); (2) SSH via `svc-gateway` with session recording and MFA; (3) Emergency direct SSH (port 22, key-based, monitored by failed login alert). All remote maintenance sessions are logged. | `terraform/*/tunnel.tf`; `docker-compose.yaml` (svc-gateway); `terraform/*/monitoring.tf` (ssh_failed_login) |
| MA-5 | Maintenance Personnel | Implemented | All maintenance is performed by the System Owner. Third-party maintenance is not permitted. SSH key management is enforced via Terraform with individual key naming (infrastructure policy denies root-named keys). | `terraform/*/ssh.tf`; `terraform/*/policy/deny_root_ssh_key.rego` |
| MA-6 | Timely Maintenance | Partially Implemented | Container image updates are tracked through CI/CD SBOM generation. CVE scanner detects known vulnerabilities on every commit. Automated patching schedules for the host OS are not yet implemented. | `.github/workflows/security.yml` (Trivy, SBOM jobs) |

---

### 5.9 MP - Media Protection

| Control ID | Control Name | Status | Implementation Description | Evidence Location |
|-----------|-------------|--------|---------------------------|-------------------|
| MP-1 | Policy and Procedures | Partially Implemented | Media protection is partially addressed through DigitalOcean controls and container security configuration. A formal media protection policy is planned. | This document |
| MP-2 | Media Access | Implemented | Access to persistent storage volumes is restricted through: (1) Docker volume ownership (`chown 1000:1000` for svc-automation, `999:999` for PostgreSQL); (2) `.env` file permissions (`chmod 600`); (3) Container-level volume mounts with `:ro` (read-only) where applicable (`svc-detection` host mounts, detection rule configs, log pipeline mTLS certs, identity-import, monitoring agent configs). | `docker-compose.yaml` (volume mount permissions) |
| MP-4 | Media Storage | Inherited | Physical media storage is managed by DigitalOcean under their shared responsibility model. The platform uses the provider's block storage (SSD) and object storage (with versioning enabled). | Cloud provider security documentation |
| MP-5 | Media Transport | Implemented | All data in transit is encrypted: (1) Zero-trust tunnel provides TLS encryption for ingress; (2) mTLS between `svc-event-shipper` and `Fluentd`; (3) HTTPS for all outbound API communications to Datadog, secrets manager, and AI providers; (4) SSH uses Ed25519 keys for session encryption. | `docker-compose.yaml` (mTLS cert mounts); `terraform/*/tunnel.tf` |
| MP-6 | Media Sanitization | Inherited | Physical media sanitization is the responsibility of DigitalOcean upon resource decommissioning. Terraform `prevent_destroy` lifecycle rules prevent accidental deletion of production resources containing sensitive data. | Cloud provider data destruction policy; `terraform/*/compute.tf` (prevent_destroy) |
| MP-7 | Media Use | Implemented | Removable media is not used in the system. All persistent data is stored on DigitalOcean block storage and object storage. Container images are pulled from trusted registries with signature verification. | `.github/workflows/security.yml` (container signature verification) |

---

### 5.10 PE - Physical and Environmental Protection

| Control ID | Control Name | Status | Implementation Description | Evidence Location |
|-----------|-------------|--------|---------------------------|-------------------|
| PE-1 | Policy and Procedures | Inherited | Physical and environmental protection is entirely the responsibility of DigitalOcean. The Organization does not operate physical data center facilities. | Cloud provider SOC 2 Type II report; DigitalOcean security documentation |

*Note: All PE family controls (PE-2 through PE-20) are inherited from DigitalOcean under the shared responsibility model. The provider maintains physical access controls, environmental controls, and facility security for the data center infrastructure.*

---

### 5.11 PL - Planning

| Control ID | Control Name | Status | Implementation Description | Evidence Location |
|-----------|-------------|--------|---------------------------|-------------------|
| PL-1 | Policy and Procedures | Implemented | Security planning is documented through this SSP, the security stack build plan, and the GSD roadmap. | This document; `docs/SECURITY_STACK_BUILD_PLAN.md`; `.planning/` |
| PL-2 | System Security and Privacy Plans | Implemented | This document serves as the System Security Plan. It describes the authorization boundary, security categorization, control implementation, and continuous monitoring strategy. | This document |
| PL-4 | Rules of Behavior | Planned | Formal rules of behavior for system users have not been documented. Operational procedures and restrictions are embedded in system configuration (e.g., identity provider RBAC, svc-gateway role restrictions). | N/A - POA&M item |

---

### 5.12 PS - Personnel Security

| Control ID | Control Name | Status | Implementation Description | Evidence Location |
|-----------|-------------|--------|---------------------------|-------------------|
| PS-1 | Policy and Procedures | Partially Implemented | The system is currently operated by a single System Owner. Personnel security procedures will be required if additional operators are onboarded. | This document |
| PS-2 | Position Risk Designation | Not Applicable | Single-operator system. No position categorization required. | N/A |
| PS-3 | Personnel Screening | Not Applicable | Single-operator system. | N/A |
| PS-4 | Personnel Termination | Partially Implemented | Account deprovisioning procedures exist in `svc-identity` and `svc-gateway`. `svc-gateway` supports immediate session revocation and certificate invalidation. Access request audit trail provides evidence of revocation. | identity provider user management; svc-gateway `tctl users rm` |
| PS-5 | Personnel Transfer | Not Applicable | Single-operator system. | N/A |
| PS-6 | Access Agreements | Planned | Formal access agreements are not yet documented. | N/A - POA&M item |
| PS-7 | External Personnel Security | Not Applicable | No external personnel have access to the system. | N/A |
| PS-8 | Personnel Sanctions | Not Applicable | Single-operator system. | N/A |

---

### 5.13 RA - Risk Assessment

| Control ID | Control Name | Status | Implementation Description | Evidence Location |
|-----------|-------------|--------|---------------------------|-------------------|
| RA-1 | Policy and Procedures | Implemented | Risk assessment is performed through automated scanning (Trivy, Semgrep, Checkov, Gitleaks), infrastructure policy enforcement, and CIS Docker Bench compliance tracking. | `.github/workflows/security.yml`; `terraform/*/policy/` |
| RA-2 | Security Categorization | Implemented | FIPS 199 security categorization is documented in Section 3 of this SSP. The system is categorized at the Moderate level across all three security objectives. | This document (Section 3) |
| RA-3 | Risk Assessment | Implemented | Formal risk assessment completed per NIST SP 800-30 Rev. 1 with 17 threat scenarios, 5x5 risk matrix (Likelihood x Impact), MITRE ATT&CK mapping, and residual risk scoring. 5 risks designated for mitigation with target dates. Automated risk assessment is continuous through CI/CD scanning (Trivy, Checkov, Semgrep, Gitleaks). Accepted risks documented with compensating controls. | `docs/grc/RISK_ASSESSMENT.md`; `docs/grc/POAM_PLAN_OF_ACTION.md`; `docs/grc/CIS_RISK_REGISTER.md` |
| RA-5 | Vulnerability Monitoring and Scanning | Implemented | Vulnerability scanning is automated through: (1) CVE scanner filesystem and dependency scanning (CRITICAL/HIGH severity, fail-on-findings) on every push and PR; (2) SAST scanner with security-audit, secrets, docker, and terraform rulesets; (3) Secrets scanner full-history secret scanning; (4) Checkov CIS benchmark scanning for Terraform configurations; (5) Container image digest manifest generation for provenance tracking; (6) CIS Docker Bench results tracked on SOC dashboard. Findings are uploaded to GitHub Security tab (SARIF format). | `.github/workflows/security.yml` (Trivy, Semgrep, secrets scanner steps); `.github/workflows/terraform-pr.yml` (Checkov step); GitHub Security tab |

---

### 5.14 SA - System and Services Acquisition

| Control ID | Control Name | Status | Implementation Description | Evidence Location |
|-----------|-------------|--------|---------------------------|-------------------|
| SA-1 | Policy and Procedures | Partially Implemented | Third-party service acquisition follows a least-privilege, open-source-first approach. Vendor selection criteria prioritize: open-source with enterprise support path, container-native deployment, and API-first architecture. | This document |
| SA-2 | Allocation of Resources | Implemented | Resource allocation is managed through Terraform variables and Docker Compose deploy.resources blocks. CPU, memory, and PID limits are defined per service. Cloud VPS sizing is parameterized in Terraform variables. Infrastructure policies warn on oversized instances. | `docker-compose.yaml` (deploy.resources); `terraform/*/variables.tf`; `terraform/*/policy/warn_sizing.rego` |
| SA-3 | System Development Life Cycle | Implemented | The system follows an IaC-driven development lifecycle: (1) Feature branches for changes; (2) Automated PR validation (7 checks); (3) Security scanning before merge; (4) Automated deployment after merge; (5) Continuous monitoring post-deployment. | `.github/workflows/terraform-pr.yml`; `.github/workflows/security.yml` |
| SA-4 | Acquisition Process | Implemented | All third-party components are acquired from trusted sources: Docker Hub official images, Quay.io, AWS ECR Public. Image provenance is verified through container signing tool signatures in CI/CD. SBOMs are generated for all container images providing supply chain transparency. | `.github/workflows/security.yml` (container signature verification, SBOM generation) |
| SA-5 | System Documentation | Implemented | System documentation includes: this SSP, Docker Compose file (service architecture), Terraform configurations (infrastructure), infrastructure policies (security constraints), CI/CD workflows (operational procedures), and Terraform-managed monitor definitions (operational runbooks). | `docs/grc/`; `docker-compose.yaml`; `terraform/*/`; `.github/workflows/`; `terraform/*/policy/` |
| SA-8 | Security and Privacy Engineering Principles | Implemented | The platform is designed around: (1) Defense in depth (4 independent audit subsystems); (2) Least privilege (no-new-privileges, resource limits, JIT access); (3) Fail-safe defaults (health checks gate service dependencies, prevent_destroy on critical resources); (4) Complete mediation (zero-trust tunnel as sole ingress); (5) Economy of mechanism (single-purpose containers); (6) Separation of privilege (3-tier RBAC). | `docker-compose.yaml`; `terraform/*/`; Keycloak realm; svc-gateway roles |
| SA-9 | External System Services | Implemented | External services within the shared responsibility model: (1) DigitalOcean - IaaS compute, storage, networking; (2) Tunnel Provider - zero-trust ingress; (3) Monitoring Platform - telemetry storage and analysis; (4) Secrets Manager - runtime secret injection; (5) AI Model Provider - inference API. All external connections use TLS. Service-level expectations are governed by each provider's published SLAs. | Service provider documentation; `terraform/*/tunnel.tf`; `terraform/*/monitoring.tf` |
| SA-10 | Developer Configuration Management | Implemented | All system configuration is version-controlled in Git. Branch protection requires PR review. CI/CD enforces format checking, linting, policy evaluation, and security scanning before changes reach production. Terraform state is stored remotely with versioning. | Repository settings; `.github/workflows/` |
| SA-11 | Developer Testing and Evaluation | Implemented | Security testing is integrated into the development pipeline: (1) CVE scanner for vulnerability scanning; (2) SAST scanner for static analysis; (3) Secrets scanner for secrets detection; (4) Checkov for CIS compliance; (5) policy engine for custom security policies; (6) Terraform validate and Terraform linter for configuration correctness; (7) container signing tool for supply chain integrity. | `.github/workflows/security.yml`; `.github/workflows/terraform-pr.yml` |

---

### 5.15 SC - System and Communications Protection

| Control ID | Control Name | Status | Implementation Description | Evidence Location |
|-----------|-------------|--------|---------------------------|-------------------|
| SC-1 | Policy and Procedures | Implemented | Communications protection policy mandates encryption for all data in transit and network segmentation between services. Documented in this SSP. | This document |
| SC-2 | Separation of User Functionality | Implemented | Each service operates in an isolated container with a single defined function. User-facing services (`svc-automation`, `svc-identity`) are separated from backend services (`svc-db`, `svc-secrets`). Administrative interfaces are not exposed through the public tunnel. | `docker-compose.yaml` (service definitions) |
| SC-3 | Security Function Isolation | Implemented | Security functions are isolated in dedicated containers: (1) `svc-identity` - authentication and authorization; (2) `svc-secrets` - secrets management; (3) `svc-gateway` - access control and session recording; (4) `svc-detection` - runtime threat detection; (5) `svc-monitor` - observability. Each operates independently with separate failure domains. | `docker-compose.yaml` |
| SC-4 | Information in Shared Resources | Implemented | Container resource isolation is enforced through: (1) Docker namespace isolation (PID, network, mount, user); (2) PID limits preventing cross-container resource exhaustion; (3) Memory limits preventing OOM impact on neighboring containers; (4) Separate data volumes per service (no shared volumes between unrelated services). | `docker-compose.yaml` (deploy.resources.limits.pids, memory; separate volumes) |
| SC-5 | Denial-of-Service Protection | Implemented | DoS protection is implemented at multiple layers: (1) Cloud firewall restricts inbound to ICMP and SSH only; (2) Zero-trust tunnel provider applies DDoS mitigation at its edge; (3) Container resource limits (CPU, memory, PIDs) prevent individual service exhaustion from cascading; (4) Health checks and automatic restarts (`restart: unless-stopped`) recover from transient failures; (5) Container down monitor alerts when running count drops. | `terraform/*/firewall.tf`; `docker-compose.yaml` (resource limits, healthchecks); `terraform/*/monitoring.tf` |
| SC-7 | Boundary Protection | Implemented | Network boundary protection is implemented through: (1) Cloud firewall as the outermost perimeter; (2) Zero-trust tunnel as the sole public ingress path - no application ports exposed directly; (3) Three segmented Docker bridge networks (`net-core`, `net-ai`, `net-monitoring`) isolating services by function and limiting lateral movement; (4) `svc-tunnel` is the only container with host networking; (5) Infrastructure policy denies firewall rules allowing public inbound on non-HTTPS ports (SSH exception documented as accepted risk). | `terraform/*/firewall.tf`; `terraform/*/tunnel.tf`; `docker-compose.yaml` (networks); `terraform/*/policy/deny_public_firewall.rego` |
| SC-8 | Transmission Confidentiality and Integrity | Implemented | All data in transit is encrypted: (1) Zero-trust tunnel provides TLS for web traffic ingress; (2) SSH sessions use Ed25519 key exchange; (3) mTLS (mutual TLS with client certificate authentication) secures the svc-gateway event pipeline (`svc-event-shipper` to `Fluentd`); (4) HTTPS for all outbound API calls to Datadog, secrets manager, and AI providers; (5) svc-gateway proxy encrypts all proxied SSH connections. | `docker-compose.yaml` (mTLS cert volume mounts); `terraform/*/tunnel.tf`; `terraform/*/ssh.tf` |
| SC-10 | Network Disconnect | Implemented | `svc-gateway` enforces session TTL with automatic disconnection. JIT sessions have 4-hour maximum lifetime. `svc-identity` enforces OIDC token expiration. Idle container connections are managed through health check intervals. | access gateway role definitions; identity provider token settings |
| SC-12 | Cryptographic Key Establishment and Management | Implemented | Cryptographic keys are managed through: (1) SSH keys managed via Terraform (`cloud_ssh_key` resource); (2) `svc-automation` encryption key stored in secrets manager; (3) `svc-gateway` identity certificates with defined TTL (1-year for event-handler); (4) mTLS certificates for event pipeline; (5) Secrets engine unseal keys stored in credential vault (biometric-locked). No keys are stored in source code - secrets scanner enforcement in CI. | `terraform/*/ssh.tf`; Secrets manager configuration; mTLS certificate chain |
| SC-13 | Cryptographic Protection | Implemented | The system uses industry-standard cryptographic mechanisms: (1) TLS 1.2+ for all HTTPS connections; (2) Ed25519 for SSH key authentication; (3) mTLS with X.509 certificates for event pipeline; (4) AES-256 encryption at rest by DigitalOcean (block storage and object storage). | SSH configuration; mTLS configuration; Cloud provider encryption documentation |
| SC-17 | Public Key Infrastructure Certificates | Partially Implemented | The zero-trust tunnel provider manages TLS certificates for public-facing hostnames. Internal mTLS certificates are self-managed (generated during audit event handler setup). Integration with a formal PKI or ACME certificate management is planned. | Tunnel provider certificate management; mTLS cert generation scripts |
| SC-18 | Mobile Code | Not Applicable | The system does not execute mobile code. All processing occurs server-side within containers. | N/A |
| SC-20 | Secure Name/Address Resolution Service | Inherited | DNS resolution is provided by DigitalOcean and tunnel provider. DNSSEC is managed at the DNS provider level. | Cloud provider DNS; Tunnel provider DNS |
| SC-23 | Session Authenticity | Implemented | Session authenticity is maintained through: (1) `svc-identity` OIDC tokens with cryptographic signatures; (2) `svc-gateway` session certificates; (3) `svc-automation` JWT-based session management with a dedicated JWT secret stored in the secrets manager. | identity provider OIDC configuration; access gateway session certs; svc-automation JWT configuration |
| SC-28 | Protection of Information at Rest | Implemented | Data at rest is protected through: (1) Cloud provider encrypts all block storage (SSD) and object storage at rest by default; (2) `svc-secrets` (secrets engine) encrypts its data directory; (3) `.env` file on the host is `chmod 600` (root-only); (4) Infrastructure policy enforces versioning on object storage buckets (data integrity safeguard); (5) Terraform state backend uses provider-encrypted storage with versioning. | Cloud provider encryption documentation; `terraform/*/policy/deny_no_encryption.rego` |
| SC-6 | Resource Availability | Implemented | Resource availability is enforced through container-level resource limits on all Compose-managed services. CPU shares, memory limits, and PID limits are defined in `deploy.resources` blocks, preventing any single service from exhausting host resources and impacting availability of other services. | `docker-compose.yaml` (deploy.resources.limits - cpu, memory, pids per service) |
| SC-15 | Collaborative Computing Devices | Not Applicable | No video conferencing, audio conferencing, or collaborative computing devices are deployed within the authorization boundary. The system is server-side infrastructure only. | N/A |
| SC-19 | Voice over Internet Protocol | Not Applicable | No VoIP services are deployed within the authorization boundary. *Note: SC-19 was withdrawn in NIST 800-53 Rev. 5 and incorporated into SC-7.* | N/A |
| SC-21 | Secure Name/Address Resolution Service (Recursive or Caching) | Inherited | DNS recursive resolution is provided by DigitalOcean's default DNS resolver on the VPS. The platform does not operate its own recursive DNS infrastructure. | Cloud provider network configuration |
| SC-22 | Architecture and Provisioning for Name/Address Resolution Service | Inherited | DNS architecture and provisioning are managed by Cloudflare (authoritative DNS) and DigitalOcean (recursive resolution). The platform delegates all DNS operations to these providers. | Cloudflare DNS configuration; DigitalOcean network settings |
| SC-24 | Fail in Known State | Partially Implemented | Containers are configured with `restart: unless-stopped` policy, ensuring they restart to a known-good state defined by their Docker image and Compose configuration. Infrastructure-as-Code (Terraform) defines the known-good infrastructure state, enabling full reconstitution. `prevent_destroy` lifecycle rules protect critical resources from accidental deletion. Full application-level fail-safe state management is not yet implemented. | `docker-compose.yaml` (restart policy); `terraform/*/compute.tf` (prevent_destroy); `terraform/*/` (IaC baseline) |

---

### 5.16 SI - System and Information Integrity

| Control ID | Control Name | Status | Implementation Description | Evidence Location |
|-----------|-------------|--------|---------------------------|-------------------|
| SI-1 | Policy and Procedures | Implemented | System integrity policy mandates automated vulnerability scanning, runtime threat detection, and secret leak prevention. Enforcement is automated through CI/CD and runtime monitoring. | This document; `.github/workflows/` |
| SI-2 | Flaw Remediation | Implemented | Flaw remediation is supported through: (1) CVE scanner detects known CVEs in dependencies and container images (CRITICAL/HIGH severity, CI pipeline fails on findings); (2) SAST scanner identifies code-level vulnerabilities via SAST rulesets; (3) Container images reference latest tags with digest manifest tracking for provenance; (4) Checkov identifies IaC misconfigurations against CIS benchmarks. Results are uploaded to the GitHub Security tab in SARIF format for tracking. | `.github/workflows/security.yml` (CVE scanner with exit-code: 1, SARIF upload); GitHub Security tab |
| SI-3 | Malicious Code Protection | Implemented | Malicious code protection is implemented through: (1) `svc-detection` (Falco) provides real-time eBPF-based syscall monitoring, detecting privilege escalation, sensitive file reads, and container exec events; (2) Secrets scanner scans full commit history for leaked secrets; (3) SAST scanner detects malicious patterns in code; (4) Container images are verified via container signing tool signatures; (5) `svc-detection-router` and `svc-tunnel` use read-only rootfs preventing runtime filesystem modification. | `docker-compose.yaml` (svc-detection, read_only: true); `.github/workflows/security.yml` (Gitleaks, Semgrep, Cosign) |
| SI-4 | System Monitoring | Implemented | System monitoring operates at four levels: (1) **Infrastructure**: `svc-monitor` collects host CPU, memory, disk, network metrics and container stats; (2) **Application**: Container health checks, PostgreSQL connection monitoring, svc-automation restart tracking; (3) **Security**: `svc-detection` eBPF syscall monitoring, failed SSH login detection, access gateway audit event streaming; (4) **Compliance**: CIS Docker Bench results tracked on SOC dashboard. Seven Terraform-managed monitors provide threshold-based alerting with automated notification. SOC dashboard provides real-time operational visibility across five panels. | `terraform/*/monitoring.tf` (7 monitors); `terraform/*/dashboard.tf` (5 dashboard groups); `docker-compose.yaml` (healthchecks, svc-detection, svc-monitor) |
| SI-5 | Security Alerts, Advisories, and Directives | Partially Implemented | CVE scanner references the National Vulnerability Database (NVD) for CVE identification. SAST scanner rulesets are maintained by the security community. Automated subscription to vendor security advisories for all deployed container images is not yet implemented. | `.github/workflows/security.yml` (CVE scanner NVD reference); SAST scanner community rulesets |
| SI-6 | Security and Privacy Function Verification | Implemented | Security function verification is automated through: (1) Terraform health checks validate `svc-automation` and SSH tunnel reachability on every plan/apply; (2) Container health checks verify each service is operational; (3) CI/CD pipeline validates security scanning tools execute successfully; (4) Infrastructure policy checks verify security constraints are enforced on infrastructure changes. | `terraform/*/checks.tf` (automation_reachable, ssh_tunnel_reachable); `docker-compose.yaml` (healthcheck definitions); `.github/workflows/terraform-pr.yml` |
| SI-7 | Software, Firmware, and Information Integrity | Implemented | Software integrity is verified through: (1) Container signature verification for upstream container images in CI/CD; (2) Image digest manifest generation for all deployed images; (3) SBOM generation (SPDX-JSON) for repository and 6 container images with 90-day retention; (4) Infrastructure policy prevents deletion of production resources (`prevent_destroy`); (5) Object storage versioning prevents audit log overwrites (enforced by infrastructure policy). | `.github/workflows/security.yml` (Cosign, SBOM jobs); `terraform/*/policy/deny_missing_prevent_destroy.rego`; `terraform/*/policy/deny_no_encryption.rego` |
| SI-8 | Spam Protection | Not Applicable | The system does not process inbound email. | N/A |
| SI-10 | Information Input Validation | Implemented | Input validation is enforced through: (1) Terraform variable validation with postconditions (VPC CIDR, VPS status, IPv4 assignment); (2) infrastructure policies validate plan inputs against security constraints; (3) Application-level input validation is delegated to individual services (svc-identity, svc-automation); (4) **Pre-graph PII scanner** (added 2026-04-23) runs before Squire LLM graph invocation, scanning raw `/alert` payloads for SSN (regex + context), Luhn-valid credit card, email, and US phone. On detection, the scanner returns a structured block with `reason_code=PII_DETECTED_PRE_GRAPH`, `rail_name=pre_graph`, at 0ms and zero token cost. This closes the rail-architecture gap where the NeMo input rail only fronts draft and critique LLM calls. Cross-maps to OWASP LLM06 (Sensitive Information Disclosure) and CSA Agentic MG-4.1. Framework: NIST AI RMF MAP-4.1 and MANAGE-4.1. | `terraform/*/compute.tf` (postconditions); `terraform/*/networking.tf` (postconditions); `terraform/*/policy/`; `builds/squire/src/squire/pre_graph_pii.py` (scanner); `builds/squire/src/squire/app.py` (integration point); `builds/squire/tests/test_pre_graph_pii.py` (12 unit tests) |
| SI-11 | Error Handling | Implemented | Error handling includes: (1) Container health checks with configurable retries and start periods; (2) `restart: unless-stopped` policy on all services for automatic recovery; (3) Dedicated error handler workflow in SOAR engine; (4) Container down monitor alerts on service failures; (5) `svc-detection-router` health check validates event routing pipeline integrity. | `docker-compose.yaml` (healthcheck, restart); `terraform/*/monitoring.tf` (container_down) |
| SI-12 | Information Management and Retention | Partially Implemented | Log retention: Docker JSON logs rotate at 10MB/3 files per container; Datadog retains logs for 15 days; audit logs exported to versioned object storage. SBOM artifacts retained for 90 days in CI/CD. Formal data retention schedule with automated lifecycle management is planned. | `docker-compose.yaml` (logging.options); `.github/workflows/security.yml` (retention-days: 90) |

---

## 6. Continuous Monitoring Strategy

### 6.1 Overview

The continuous monitoring strategy implements NIST SP 800-137 guidance through layered automated monitoring that provides real-time visibility into the security posture of the platform. Monitoring operates across four tiers:

| Tier | Scope | Mechanism | Frequency |
|------|-------|-----------|-----------|
| **Tier 1 - Infrastructure** | Host metrics, disk, CPU, memory, network | `svc-monitor` agent | Real-time (10-30s intervals) |
| **Tier 2 - Application** | Container health, service availability, database performance | Docker health checks, Terraform checks, PostgreSQL integration | 10-30s intervals; on every `terraform plan` |
| **Tier 3 - Security** | Syscalls, authentication, session recording, SSH brute force | `svc-detection` (Falco), `svc-gateway` (Teleport), `svc-monitor` (auth logs) | Real-time |
| **Tier 4 - Compliance** | CIS Docker Bench, IaC policy, vulnerability scanning, SBOM | CI/CD pipeline (Trivy, Semgrep, Checkov, Gitleaks, Cosign, OPA) | On every commit (push/PR) |

### 6.2 Alerting Framework

Alerts are severity-tiered with escalation paths:

| Severity | Examples | Notification | DND Behavior |
|----------|----------|-------------|-------------|
| **Critical** | Container down, disk >90%, SSH brute force (>10 attempts) | Immediate - SOAR webhook to messaging platform | Always notifies (no muting) |
| **Error** | PostgreSQL connections high, svc-automation crash loop | Immediate | Muted 10 PM - 8:30 AM ET |
| **Warning** | Disk >80%, CPU >85%, memory >85% | Immediate (during active hours) | Muted 10 PM - 8:30 AM ET |
| **Notice** | runtime detection syscall events (non-critical), CIS findings | Dashboard only | Dashboard only |

### 6.3 SOC Dashboard

The Terraform-managed SOC dashboard provides five operational views:

1. **Infrastructure Health** - Host CPU/memory/disk/network timeseries, host map
2. **Container Fleet** - Container health status, per-container CPU/memory, running container count
3. **Security Operations** - runtime detection alerts, failed SSH attempts, runtime detection events by priority, SSH auth failure log stream
4. **Application Performance** - PostgreSQL connections, svc-automation container CPU, error log count and stream
5. **Compliance Posture** - CIS Docker Bench pass/warn/info counts, 90-day compliance trend, compliance note

### 6.4 Automated Security Scanning Schedule

| Scan Type | Tool | Trigger | Failure Behavior |
|-----------|------|---------|-----------------|
| Secrets detection | Secrets scanner | Every push and PR | Blocks merge |
| CVE scanning | CVE scanner | Every push and PR | Blocks merge (CRITICAL/HIGH) |
| SAST | SAST scanner | Every push and PR | Blocks merge |
| CIS IaC compliance | Checkov | Every Terraform PR | Blocks merge |
| Custom security policies | Policy engine | Every Terraform PR | Blocks merge |
| Format/lint/validate | Terraform + Terraform linter | Every Terraform PR | Blocks merge |
| Container signatures | Container signing tool | Every merge to main | Advisory (continue-on-error) |
| Supply chain inventory | SBOM generator | Every merge to main | Artifacts stored 90 days |

### 6.5 Ongoing Assessment Activities

| Activity | Frequency | Owner | Evidence |
|----------|-----------|-------|---------|
| Review SOC dashboard for anomalies | Daily | System Owner | Dashboard screenshots |
| Review runtime detection alerts for false positives | Weekly | System Owner | runtime detection event log |
| Update container images and re-scan | Monthly | System Owner | SBOM diff, CVE scanner results |
| Review and update infrastructure policies | Quarterly | System Owner | Policy commit history |
| Review SSP control implementation | Semi-annually | System Owner | This document (revision history) |
| Full security control assessment | Annually | System Owner | Assessment report |

---

## 7. POA&M Reference

Open findings and planned remediations are tracked in the Plan of Action and Milestones document.

**Document Location:** `docs/grc/POAM_PLAN_OF_ACTION.md`

### Summary of Open Items

<!-- TODO(et): Reconcile SSP-local POA-XXX numbering with POAM_PLAN_OF_ACTION.md POAM-XXX scheme. Either renumber to POAM-* or state explicitly these are SSP-local control-traceable IDs separate from the register. POA-004, POA-005, POA-006 target dates (Q2 2026) have passed; re-evaluate status. -->

| ID | Finding | Control | Severity | Target Date | Status |
|----|---------|---------|----------|-------------|--------|
| POA-001 | System use notification banners not configured | AC-8 | Low | Q3 2026 | Planned |
| POA-002 | Formal contingency plan document not created | CP-2, CP-3, CP-4 | Medium | 2026-03-11 | Closed - BCP and DRP policies created (`POLICY_BUSINESS_CONTINUITY.md`, `POLICY_DISASTER_RECOVERY.md`) |
| POA-003 | Formal incident response plan not created | IR-8, IR-2, IR-3 | Medium | 2026-03-11 | Closed - IR policy and 4 playbooks created (`POLICY_INCIDENT_RESPONSE.md`, `TABLETOP_EXERCISE.md`) |
| POA-004 | MFA not mandatory for all identity provider web access | IA-2(2) | Medium | Q2 2026 | Planned |
| POA-005 | Automated host OS patching not configured | MA-6 | Medium | Q2 2026 | Planned |
| POA-006 | Off-site backup replication not implemented | CP-6, CP-9 | Medium | Q2 2026 | Planned |
| POA-007 | Formal rules of behavior not documented | PL-4 | Low | 2026-03-11 | Closed - Acceptable Use Policy created (`POLICY_ACCEPTABLE_USE.md`) |
| POA-008 | Automated data retention lifecycle not configured | AU-11, SI-12 | Low | Q3 2026 | Planned |
| POA-009 | Emergency SSH (port 22) open to 0.0.0.0/0 | SC-7 | Medium | Accepted Risk | Documented |
| POA-010 | `svc-detection` requires SYS_ADMIN + apparmor:unconfined | AC-6 | Low | Accepted Risk | Documented |
| POA-011 | `svc-monitor` requires pid:host for process monitoring | AC-6 | Low | Accepted Risk | Documented |
| POA-012 | Vendor security advisory subscription not automated | SI-5 | Low | Q3 2026 | Planned |

---

## 7.5 Squire Subsystem (Phase 17) Annex

> **Key Point:** The Squire autonomous SOC analyst subsystem is authorized under this parent SSP and ships with its own scoped SSP (`SQUIRE_SSP.md`) that details 36 Squire-specific control implementations across 9 control families. Squire inherits infrastructure controls from this parent SSP (container hardening, secrets management, network segmentation, monitoring, logging) and adds AI-specific control implementations for input validation, output validation, rate limiting, human-in-the-loop, audit trail, and cost ceiling.

### 7.5.1 Control count reconciliation

| Source | Control rows | Scope |
|--------|--------------|-------|
| This SSP (parent) | 133 | Platform-wide NIST 800-53 Moderate baseline |
| SQUIRE_SSP.md (child) | 36 | Squire-scoped controls with inheritance annotations |
| Combined coverage | 169 | Platform + Squire subsystem |

### 7.5.2 Squire subsystem summary

| Component | Function | Service name |
|-----------|----------|--------------|
| Squire | LangGraph 7-node state machine (classify, retrieve, enrich, investigate, draft, critique, route_severity) | svc-squire |
| NeMo Guardrails | Colang input and output rails, PII detection sidecar | svc-nemo |
| Langfuse web | Observability UI and trace ingest API | svc-langfuse-web |
| Langfuse worker | Async trace processing | svc-langfuse-worker |
| Langfuse ClickHouse | Columnar trace storage | svc-langfuse-clickhouse |
| Langfuse Redis | Dedup and cache | svc-langfuse-redis |
| Pre-graph scanner | Regex PII block before LLM invocation (Python) | `builds/squire/src/squire/pre_graph_pii.py` |

### 7.5.3 Defense-in-depth layers (Phase 17)

```
 Layer 1  WAF                          Cloudflare
 Layer 2  Rate limit                   Cloudflare (per-IP, per-token)
 Layer 3  X-Squire-Token auth          HMAC token, ephemeral, 60-day rotation
 Layer 4  Cost ceiling                 Hard stop at per-alert budget
 Layer 5  Actions allow-list           Typed action schema, deny-by-default
 Layer 6  Pre-graph PII scanner        Regex block before graph.invoke
 Layer 7  NeMo input rails             Colang + presidio PII detection
 Layer 8  HITL review                  HIGH and CRITICAL severity gate
 Layer 9  Audit trail                  Langfuse + pgvector ir_investigations
```

### 7.5.4 Cross-references

| Squire doc | Purpose |
|------------|---------|
| `SQUIRE_SSP.md` | 36-control scoped SSP with inheritance annotations |
| `GUARDRAILS_CONFIGURATION.md` | Rail-by-rail test coverage, failure modes, change control |
| `SQUIRE_MODEL_CARD.md` | Mitchell et al. model card for Fable 5, Sonnet 4.6, Voyage AI voyage-3-large |
| `AI_AUDIT_TRAIL_SPEC.md` | Per-invocation logging, retention tiers, immutability, replay procedure |
| `HITL_POLICY.md` | Human-in-the-loop triggers, SLA, 60-day ephemeral token rotation |
| `SQUIRE_DATA_FLOW_CLASSIFICATION.md` | Data classification, storage, retention, sanitization rules |
| `REDTEAM_RESULTS.md` | 6 executed red-team cases with Langfuse trace IDs |
| `FRAMEWORK_CROSSWALK_SQUIRE.md` | 31-control cross-framework mapping |
| `SQUIRE_AI_RISK_ASSESSMENT.md` | NIST AI RMF + CSA Agentic Profile, 10 AI risks |
| `AI_SUPPLY_CHAIN_REGISTER.md` | Living asset register, 14 components with version, license, hash |
| `SQUIRE_THREAT_MODEL.md` | STRIDE + MITRE ATLAS first-class threat model (plan 17-14) |
| `SQUIRE_TABLETOP_EXERCISE.md` | Jailbreak + hallucinated containment TTX with recovery procedure (plan 17-14) |

### 7.5.5 Squire subsystem diagrams (plan 17-14)

Four sanitized diagrams support the Squire SSP annex. Sources `.mmd` and rendered `.png` live in `docs/grc/diagrams/`.

| Diagram | File | Purpose |
|---------|------|---------|
| Architecture | `squire-architecture.png` | Deployed topology of the Squire stack on host-alpha, Cloudflare tunnel routes, external integrations |
| State machine | `squire-state-machine.png` | LangGraph node and edge diagram with per-node model assignment and invocation caps |
| Data flow | `squire-data-flow.png` | 3-lane swimlane: alert ingress, graph execution, observability writes |
| ATLAS threat model | `squire-atlas-threat-model.png` | Portfolio-grade adversary to attack-surface to control to residual-risk visual |

### 7.5.6 Interconnections and boundaries (Phase 17)

The Squire subsystem introduces the following external interconnections, each subject to SSP control SA-9 (External System Services):

| Connection | Direction | Purpose | Control reference |
|------------|-----------|---------|-------------------|
| Anthropic API | Outbound HTTPS from svc-squire | Sonnet 4.6 classify, Fable 5 draft + critique | SA-9, SC-7, SC-8 |
| Tavily API | Outbound HTTPS from svc-squire | Optional enrichment query | SA-9, SC-7, SC-8 |
<!-- TODO(et): Verify Telegram notifier is live for HIGH/CRITICAL severity. n8n Telegram credential is verified, but the Squire-side webhook path needs evidence. -->
| Telegram Bot API | Outbound via n8n route | Operator notification of severity HIGH + CRITICAL alerts | SA-9, IR-6 |
| n8n webhook | Inbound to svc-squire /alert | Alert dispatch from upstream SOAR workflows | AC-4, IA-3 |
| Cloudflare tunnel | Ingress for squire.example-ops.com, langfuse.example-ops.com | Zero-trust edge termination | SC-7, SC-8, AC-3 |

---

## Related GRC Documents

The following documents comprise the GRC library for this system and support the control implementations documented in this SSP:

| Document | Location | Description |
|----------|----------|-------------|
| Plan of Action and Milestones | `docs/grc/POAM_PLAN_OF_ACTION.md` | Plan of Action and Milestones |
| CIS Docker Benchmark Risk Register | `docs/grc/CIS_RISK_REGISTER.md` | CIS Docker Benchmark Risk Register |
| Risk Assessment | `docs/grc/RISK_ASSESSMENT.md` | Risk Assessment (NIST SP 800-30) |
| Incident Response Policy | `docs/grc/POLICY_INCIDENT_RESPONSE.md` | Incident Response Policy |
| Access Control Policy | `docs/grc/POLICY_ACCESS_CONTROL.md` | Access Control Policy |
| Acceptable Use Policy | `docs/grc/POLICY_ACCEPTABLE_USE.md` | Acceptable Use Policy |
| Business Continuity Plan | `docs/grc/POLICY_BUSINESS_CONTINUITY.md` | Business Continuity Plan |
| Disaster Recovery Plan | `docs/grc/POLICY_DISASTER_RECOVERY.md` | Disaster Recovery Plan |
| Change Management Policy | `docs/grc/POLICY_CHANGE_MANAGEMENT.md` | Change Management Policy |
| Vulnerability Management Policy | `docs/grc/POLICY_VULNERABILITY_MANAGEMENT.md` | Vulnerability Management Policy |
| Security Awareness and Training Policy | `docs/grc/POLICY_SECURITY_AWARENESS.md` | Security Awareness and Training Policy |
| Risk Management Policy | `docs/grc/POLICY_RISK_MANAGEMENT.md` | Risk Management Policy |
| IAM & RBAC Role Map | `docs/grc/IAM_RBAC_ROLE_MAP.md` | IAM & RBAC Role Map |
| IAM Access Review Process | `docs/grc/IAM_ACCESS_REVIEW.md` | IAM Access Review Process |
| IR Playbook: Compromised Container | `docs/grc/PLAYBOOK_COMPROMISED_CONTAINER.md` | IR Playbook: Compromised Container |
| IR Playbook: Leaked Credential | `docs/grc/PLAYBOOK_LEAKED_CREDENTIAL.md` | IR Playbook: Leaked Credential |
| IR Playbook: DDoS/Service Degradation | `docs/grc/PLAYBOOK_DDOS_SERVICE_DEGRADATION.md` | IR Playbook: DDoS/Service Degradation |
| IR Playbook: Unauthorized Access | `docs/grc/PLAYBOOK_UNAUTHORIZED_ACCESS.md` | IR Playbook: Unauthorized Access |
| Tabletop Exercise | `docs/grc/TABLETOP_EXERCISE.md` | Tabletop Exercise: Operation Phantom Container |
| Squire SSP (scoped) | `docs/grc/SQUIRE_SSP.md` | Squire subsystem SSP, 36 controls, 9 families |
| Squire AI Risk Assessment | `docs/grc/SQUIRE_AI_RISK_ASSESSMENT.md` | NIST AI RMF + CSA Agentic, 10 AI risks |
| Guardrails Configuration | `docs/grc/GUARDRAILS_CONFIGURATION.md` | Rail-by-rail test coverage and change control |
| Red-Team Results | `docs/grc/REDTEAM_RESULTS.md` | 6 executed red-team cases with Langfuse traces |
| Framework Crosswalk (Squire) | `docs/grc/FRAMEWORK_CROSSWALK_SQUIRE.md` | 31 Squire controls across 7 frameworks |
| Squire Model Card | `docs/grc/SQUIRE_MODEL_CARD.md` | Mitchell et al. model card |
| Squire Data Flow Classification | `docs/grc/SQUIRE_DATA_FLOW_CLASSIFICATION.md` | Per-class data rules |
| AI Audit Trail Spec | `docs/grc/AI_AUDIT_TRAIL_SPEC.md` | Per-invocation logging spec |
| HITL Policy | `docs/grc/HITL_POLICY.md` | Human-in-the-loop policy + token rotation |
| AI Supply Chain Register | `docs/grc/AI_SUPPLY_CHAIN_REGISTER.md` | Living asset register, 14 components |

---

## 8. Document Control

### 8.1 Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-03-11 | System Owner | Initial SSP creation - 13-service architecture, NIST 800-53 Moderate baseline, 16 control families mapped |
| 1.1 | 2026-04-24 | System Owner | Phase 17 annex added. SI-10 upgraded to Implemented with pre-graph PII scanner. Squire subsystem documented (36 additional controls in SQUIRE_SSP.md). Cross-refs to 10 Squire-specific GRC docs added. |
| 1.2 | 2026-05-25 | System Owner | Compose changes through May 25 reflected (Langfuse stack, NeMo, Squire image pinning, Renovate tier policy). Image source list refreshed. Keycloak references sanitized to `svc-identity` in CP-10 and IA-5. |

### 8.2 Review Schedule

| Review Type | Frequency | Next Review Date | Reviewer |
|-------------|-----------|-----------------|----------|
| Full SSP review | Semi-annual | 2026-09-11 | System Owner |
| Control implementation assessment | Annual | 2027-03-11 | System Owner |
| Security categorization review | Annual | 2027-03-11 | System Owner |
| POA&M status review | Quarterly | 2026-06-11 | System Owner |

### 8.3 Distribution

This document is classified as CONTROLLED UNCLASSIFIED - INTERNAL USE ONLY. Distribution is limited to:

- System Owner (Authorizing Official)
- Future security assessors (upon engagement)
- Compliance auditors (upon formal request)

### 8.4 Related Documents

| Document | Location | Purpose |
|----------|----------|---------|
| System Security Plan (this document) | `docs/grc/SSP_SYSTEM_SECURITY_PLAN.md` | Security control documentation |
| Plan of Action and Milestones | `docs/grc/POAM_PLAN_OF_ACTION.md` | Open finding tracking |
| Security Stack Build Plan | `docs/SECURITY_STACK_BUILD_PLAN.md` | Implementation roadmap |
| Docker Compose Definition | `docker-compose.yaml` | Service architecture baseline |
| Terraform IaC | `terraform/*/` | Infrastructure baseline |
| CI/CD Security Pipeline | `.github/workflows/security.yml` | Automated security scanning |
| CI/CD Terraform PR Validation | `.github/workflows/terraform-pr.yml` | Change control automation |
| Infrastructure Security Policies | `terraform/*/policy/*.rego` | Infrastructure policy constraints |

---

*End of System Security Plan*
