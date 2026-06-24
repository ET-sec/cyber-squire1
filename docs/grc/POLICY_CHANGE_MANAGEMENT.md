# Change Management Policy

**Document ID:** GRC-CM-001
**Version:** 1.0
**Classification:** Internal Use Only
**Effective Date:** 2026-03-11
**Review Cycle:** Annual (next review: 2027-03-11)
**Owner:** Information Security Officer
**NIST 800-53 Controls:** CM-1, CM-2, CM-3, CM-4, CM-5, CM-6, CM-7, CM-8

---

## 1. Purpose

This Change Management Policy establishes the processes, controls, and approval requirements for modifying the Organization's security operations platform. All changes to infrastructure, container configurations, CI/CD pipelines, access controls, and security policies SHALL follow the procedures defined herein.

The objective is to ensure that changes are authorized, tested, documented, reversible, and do not introduce unacceptable risk to the confidentiality, integrity, or availability of platform services.

---

## 2. Scope

This policy applies to all changes affecting:

- Infrastructure-as-code definitions (VPS provisioning, networking, firewall rules, DNS)
- Docker Compose service definitions (all 19 containers on `alpha-node`)
- CI/CD pipeline configurations and security scanning rules
- Infrastructure policy definitions (8 Rego policies)
- Access control configurations (`svc-identity` realms, `svc-gateway` roles, `svc-secrets` policies)
- Monitoring and detection rules (`svc-monitor`, `svc-detection`)
- Backup procedures and schedules
- Secret rotation and credential changes
- Cloudflare and zero-trust tunnel configurations

---

## 3. Roles and Responsibilities

| Role | Change Management Responsibility |
|------|----------------------------------|
| Information Security Officer | Policy owner; emergency change approval authority; post-change review |
| System Owner | Change requestor; technical implementation; rollback execution |
| Auditor | Change log review; compliance verification; exception review |

---

## 4. Change Categories

### 4.1 Standard Changes

**Definition:** Pre-approved, low-risk, routine changes that follow a documented procedure and do not require individual review.

**Examples:**
- Container image version updates (patch-level, e.g., `16.2` to `16.3`). For Renovate-tracked images, the bump flows in as a Renovate-authored PR. Locally built Tier 0 images (`svc-nemo`, `svc-squire`, `svc-fluentd`) require a manual PR per the docker-compose header note.
- Dependency version bumps with passing CI
- Documentation updates
- Log rotation adjustments
- Monitoring threshold tuning (non-critical alerts)

**Process:** Commit to branch, open PR, automated CI passes, merge. No additional approval required.

### 4.2 Normal Changes

**Definition:** Changes that modify platform behavior, access controls, infrastructure topology, or security posture. Require explicit review.

**Examples:**
- New service deployment or removal
- Infrastructure-as-code changes (VPS sizing, firewall rules, DNS records)
- Infrastructure policy additions or modifications
- Access control changes (`svc-identity` roles, `svc-gateway` JIT rules)
- CI/CD pipeline modifications
- Secret rotation affecting multiple services
- Backup schedule or retention changes
- Network configuration changes

**Process:** Full change request process (Section 5).

### 4.3 Emergency Changes

**Definition:** Changes required to restore service availability, mitigate an active security incident, or address a critical vulnerability. Time-sensitive; bypass normal review.

**Examples:**
- Patching a critical CVE (CVSS >= 9.0) under active exploitation
- Revoking compromised credentials
- Blocking an active attack via firewall rule
- Restoring a failed critical service (Tier 1)

**Process:** Emergency change process (Section 9).

---

## 5. Change Request Process

All Normal Changes SHALL follow this process:

### 5.1 Step 1 - Branch and Develop

1. Create a feature branch from `main` in the code repository
2. Implement the change in the appropriate configuration files
3. Commit with a descriptive message that references the change rationale

### 5.2 Step 2 - Open Pull Request

1. Push the branch to the code repository platform
2. Open a Pull Request (PR) with:
  - **Title:** Concise description of the change
  - **Description:** What is being changed, why, and what the expected impact is
  - **Risk assessment:** Low / Medium / High
  - **Rollback plan:** How to revert if the change causes issues
  - **Testing performed:** What local or pre-merge testing was done

### 5.3 Step 3 - Automated Security Scanning (CI Gate)

The PR pipeline SHALL automatically execute the following security gates. ALL gates must pass before merge is permitted.

#### PR Pipeline (runs on every push to a PR branch):

| Gate | Tool | Purpose | Failure Action |
|------|------|---------|----------------|
| Format Check | `terraform fmt` | Enforce consistent IaC formatting | PR blocked; author must fix formatting |
| Validation | `terraform validate` | Verify IaC syntax and configuration | PR blocked; author must fix errors |
| Linting | Terraform linter | Detect IaC anti-patterns and misconfigurations | PR blocked; author must address findings |
| IaC Security | Checkov | Scan IaC for security misconfigurations (CIS benchmarks) | PR blocked; author must remediate or document exception |
| Plan | `terraform plan` | Preview infrastructure changes; sticky PR comment with plan output | PR annotated with plan output for review |

#### Merge Pipeline (runs after merge to `main`):

| Gate | Tool | Purpose |
|------|------|---------|
| Container Security | CVE scanner | Scan container images and filesystem for CVEs |
| SAST | SAST scanner | Static analysis for code-level vulnerabilities |
| Secret Detection | Secrets scanner | Detect committed secrets, tokens, or credentials |
| IaC Apply | `terraform apply` | Apply infrastructure changes with manual approval gate |
| Image Signing | Container signing tool | Container image signature verification (soft-fail) |
| SBOM Generation | `syft` or equivalent | Produce software bill of materials |
| Policy Engine Evaluation | Policy engine | Enforce organizational policies against merged state |

### 5.4 Step 4 - Code Review

1. At minimum, the author SHALL self-review the diff for unintended changes
2. For High-risk changes, the Information Security Officer SHALL review before merge
3. Review SHALL verify:
  - Change matches the stated intent
  - No secrets or sensitive data in the diff
  - Rollback plan is viable
  - Security scanning results are acceptable
  - Infrastructure policies pass

### 5.5 Step 5 - Merge and Deploy

1. Merge the PR to `main`
2. Merge pipeline executes automatically
3. If the change requires deployment:
  - For IaC changes: Execute `iac apply` from local workstation or CI
  - For container changes: SSH to `alpha-node` and execute `docker compose pull && docker compose up -d`
  - For configuration changes: Restart affected service(s)
4. Verify deployment success (service health checks, monitoring dashboard)

### 5.6 Step 6 - Post-Change Verification

1. Confirm the change achieves its intended effect
2. Monitor for unexpected side effects (15-minute observation window minimum)
3. Verify no degradation in monitoring, detection, or access control systems
4. Document the change in the change log (Section 12)

---

## 6. Infrastructure Policy Enforcement

Eight policy engine (Rego) policies are enforced in the CI pipeline. These policies codify organizational security requirements and are evaluated against every infrastructure change.

### 6.1 Policy Inventory

| Policy ID | Policy Name | Enforcement Point | Description |
|-----------|-------------|-------------------|-------------|
| OPA-001 | `deny_public_firewall` | Merge pipeline | Blocks firewall rules that allow unrestricted inbound access (0.0.0.0/0) |
| OPA-002 | `deny_no_encryption` | Merge pipeline | Requires encryption on remote state and storage resources |
| OPA-003 | `deny_missing_prevent_destroy` | Merge pipeline | Requires lifecycle `prevent_destroy` on critical stateful resources |
| OPA-004 | `deny_root_ssh_key` | Merge pipeline | Blocks SSH key configurations that allow root login |
| OPA-005 | `warn_naming` | Merge pipeline | Warns on resources not following naming conventions |
| OPA-006 | `warn_tags` | Merge pipeline | Warns on resources missing required tags |
| OPA-007 | `warn_sizing` | Merge pipeline | Warns on oversized or undersized resource specifications |
| OPA-008 | `warn_backup` | Merge pipeline | Warns on resources without backup configuration |

### 6.2 Policy Exception Process

If a change requires violating an infrastructure policy:

1. Document the specific policy being bypassed and the technical justification
2. Information Security Officer must approve the exception in writing (PR comment)
3. The exception SHALL be time-bound (default: 30 days)
4. A remediation ticket SHALL be created to bring the configuration back into compliance
5. Exception SHALL be logged in the risk register

---

## 7. Rollback Procedures

### 7.1 Infrastructure-as-Code Rollback

```
Procedure:
1. Identify the last known-good IaC state version
2. Run: iac plan     (review what will change on rollback)
3. Run: iac apply     (apply the rollback)
4. Verify infrastructure matches expected state
5. Document rollback in change log with reason
```

**Note:** IaC state is versioned on encrypted object storage. Previous versions are available for rollback.

### 7.2 Container Configuration Rollback

```
Procedure:
1. Revert the Docker Compose change in git:
  git revert <commit-hash>
2. Push revert to main (triggers merge pipeline)
3. On alpha-node:
  docker compose pull
  docker compose up -d
4. Verify service health
5. Document rollback in change log
```

### 7.3 Single Container Rollback

```
Procedure:
1. Identify the previous image tag or compose configuration
2. Update the specific service definition
3. docker compose up -d <service-name>
4. Verify service health
5. Document rollback in change log
```

### 7.4 Secret Rollback

Secrets cannot be "rolled back" in the traditional sense. If a secret rotation causes issues:

1. Generate a new secret value (do NOT revert to the old value, which may be compromised)
2. Update the secrets manager
3. Re-inject into the production environment
4. Restart affected services
5. Verify authentication and connectivity

---

## 8. Docker Compose Change Process

Changes to the Docker Compose stack follow the standard change process with additional controls:

### 8.1 Adding a New Service

1. Define the service in `docker-compose.yaml` on a feature branch
2. Include: image reference, resource limits, network configuration, volume mounts, environment variables, health check, logging driver, restart policy
3. Update infrastructure policies if the new service has unique requirements
4. Open PR; all CI gates must pass
5. After merge, deploy to `alpha-node`:
  ```
  docker compose pull <new-service>
  docker compose up -d <new-service>
  ```
6. Verify service health and integration with existing services
7. Update GRC-BCP-001 and GRC-DRP-001 to include the new service

### 8.2 Removing a Service

1. Remove or comment out the service definition on a feature branch
2. Document data migration or archival plan if the service has persistent data
3. Open PR with justification for removal
4. After merge, on `alpha-node`:
  ```
  docker compose stop <service>
  docker compose rm <service>
  ```
5. Archive persistent volumes if data retention is required
6. Update GRC-BCP-001 and GRC-DRP-001

### 8.3 Modifying a Service

1. Modify the service definition on a feature branch
2. For image version changes: verify the new version's CVE status via the container security scanner
3. For environment variable changes: verify no secrets are hardcoded
4. For volume changes: verify backup strategy still applies
5. Open PR; CI gates must pass
6. After merge, deploy:
  ```
  docker compose up -d <service>
  ```

### 8.4 Critical Safety Rules

- **NEVER** run `docker compose down` via the zero-trust tunnel: this kills `svc-tunnel` and severs remote access
- **NEVER** use the `-v` flag with `docker compose down`: this destroys persistent data volumes
- **ALWAYS** stop individual services with `docker compose stop <service>` when possible
- **ALWAYS** have direct SSH access available as a fallback before modifying tunnel-related services

---

## 9. Emergency Change Process

### 9.1 Authorization

Emergency changes may be executed WITHOUT prior PR review when:

1. A Critical vulnerability (CVSS >= 9.0) is under active exploitation
2. An active security incident requires immediate containment
3. A Tier 1 service failure requires immediate recovery action
4. Credential compromise requires immediate rotation

**Authorization:** System Owner may execute; Information Security Officer must be notified within 1 hour.

### 9.2 Execution

1. Document the emergency and justification (even a single-line note)
2. Execute the minimum change necessary to address the emergency
3. Verify the change resolves the immediate issue
4. Do NOT make additional "while we're at it" changes under emergency authority

### 9.3 Post-Emergency Review (Mandatory)

Within 48 hours of an emergency change, the following SHALL be completed:

1. **Retroactive PR:** Create a PR that captures the change made, with full description
2. **CI validation:** Run the full CI pipeline against the current state to identify any policy violations
3. **Risk assessment:** Document any residual risk introduced by the emergency change
4. **Remediation plan:** If the emergency change introduced technical debt or policy violations, create a remediation plan with timeline
5. **Lessons learned:** Document what triggered the emergency and whether the standard process could be improved to prevent future emergencies
6. **Sign-off:** Information Security Officer reviews and approves the post-emergency documentation

---

## 10. Configuration Baseline

### 10.1 Infrastructure Baseline

The infrastructure-as-code platform state file is the authoritative configuration baseline for:

- VPS specification (CPU, memory, disk, region)
- Network configuration (VPC, firewall rules)
- DNS records
- Object storage buckets
- SSH key assignments

**Drift detection:** An IaC plan command SHALL be executed monthly to detect configuration drift. Any drift SHALL be investigated and either reconciled (apply the baseline) or documented (update IaC to match intended state).

### 10.2 Container Baseline

The Docker Compose file (`docker-compose.yaml`) is the authoritative configuration baseline for:

- Container images and versions
- Environment variables (template; actual secrets from secrets manager)
- Volume mounts
- Network configuration
- Resource limits
- Health checks
- Restart policies

**Drift detection:** `docker compose config` SHALL be compared against the repository version monthly.

### 10.3 Policy Baseline

The 8 infrastructure policies (Rego) in the code repository are the authoritative policy baseline. Any policy modification follows the Normal Change process.

---

## 11. Configuration Inventory

Per NIST 800-53 CM-8, the Organization maintains an inventory of all configurable components.

| Component | Type | Configuration Source | Owner |
|-----------|------|---------------------|-------|
| `alpha-node` VPS | Infrastructure | IaC state | System Owner |
| `svc-db` | Container | Docker Compose | System Owner |
| `svc-automation` | Container | Docker Compose | System Owner |
| `svc-secrets` | Container | Docker Compose + secrets engine config | System Owner |
| `svc-identity` | Container | Docker Compose + Realm export | System Owner |
| `svc-gateway` | Container | Docker Compose + gateway config | System Owner |
| `svc-monitor` | Container | Docker Compose + agent config | System Owner |
| `svc-detection` | Container | Docker Compose + rules config | System Owner |
| `svc-detection-router` | Container | Docker Compose | System Owner |
| `Fluentd` | Container | Docker Compose + routing config | System Owner |
| `svc-event-shipper` | Container | Docker Compose | System Owner |
| `svc-tunnel` | Container | Docker Compose + tunnel token | System Owner |
| `svc-llm` | Container | Docker Compose | System Owner |
| `svc-transcription` | Container | Docker Compose | System Owner |
| `svc-ai-gateway` | Container | Docker Compose + gateway config | System Owner |
| `svc-squire` | Container (locally built) | Docker Compose + `builds/squire/` Dockerfile | System Owner |
| `svc-nemo` | Container (locally built) | Docker Compose + `builds/squire/docker/nemo_config/` Dockerfile and rail config | System Owner |
| `svc-langfuse-web` | Container | Docker Compose | System Owner |
| `svc-langfuse-worker` | Container | Docker Compose | System Owner |
| `svc-langfuse-clickhouse` | Container | Docker Compose | System Owner |
| `svc-langfuse-redis` | Container | Docker Compose | System Owner |
| Firewall rules | Network | Infrastructure-as-code platform | System Owner |
| DNS records | Network | Infrastructure-as-code platform / Cloudflare | System Owner |
| CI/CD pipelines | Automation | Repository workflow files | System Owner |
| Infrastructure policies | Policy | Repository Rego files | Information Security Officer |

---

## 12. Change Log

All changes SHALL be recorded. The code repository's git log serves as the primary change log. Each commit message SHALL include:

- What was changed
- Why it was changed (reference to requirement, incident, or improvement)

For Normal and Emergency changes, the PR description serves as the formal change record and SHALL include the fields defined in Section 5.2.

A quarterly change log summary SHALL be produced for audit purposes, containing:

- Total changes by category (Standard, Normal, Emergency)
- Emergency changes with post-review status
- Infrastructure policy exceptions granted
- Rollbacks executed
- Failed CI gates and resolution

---

## 13. Document Control

| Field | Value |
|-------|-------|
| Document ID | GRC-CM-001 |
| Version | 1.0 |
| Status | Approved |
| Author | Information Security Officer |
| Approved By | System Owner |
| Effective Date | 2026-03-11 |
| Next Review | 2027-03-11 |
| Classification | Internal Use Only |
| Distribution | Information Security Officer, System Owner, Auditor |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-03-11 | Information Security Officer | Initial release |

---

*This document is the property of the Organization. Unauthorized distribution is prohibited.*

---

## Squire Integration (Phase 17)

> **Key Point:** Squire subsystem changes follow this policy. Guardrail configs, model routing, and actions allow-list changes are high-risk and require pre-approval plus post-change red-team validation. The 2026-04-23 pre-graph PII scanner deployment serves as the reference example for in-session emergency remediation under this policy.

Phase 17 change categories under this policy:

1. **Guardrail config change** (`svc-nemo-config`, `GUARDRAILS_CONFIGURATION.md`): Pre-change, the change is tested in staging with the full rail coverage suite. Post-change, the 6-case red-team battery runs against prod. High risk.
2. **Model routing change** (`SQUIRE_MODEL_CARD.md` version field): Requires regression eval against the evaluation data set documented in the model card. Medium risk.
3. **Actions allow-list change** (`actions.yml`): Requires security review of new action schemas plus audit trail validation. High risk (new agent capabilities).
4. **pgvector schema change** (`ir_chunks`, `ir_alerts`, `ir_investigations`, `ir_rotation_events`): Migration plus rollback procedure plus backup verified before apply. Medium risk.
5. **Token rotation policy change** (`HITL_POLICY.md` section 6): Requires IAM reviewer sign-off. Medium risk.

### Reference example: in-session emergency remediation

<!-- TODO(et): Verify commit hash 3e47524 exists in the cyber-squire1 git history before quoting it in interviews. The 127-test passing claim should also be confirmed against `builds/squire/tests/`. -->
On 2026-04-23, red-team Case 03 revealed that the NeMo input rail did not catch raw SSN in `/alert` payloads. Under the emergency remediation provision of this policy, the pre_graph_pii.py scanner was drafted, unit-tested (12 tests), wired into `builds/squire/src/squire/app.py` before `graph.invoke`, and validated against the same red-team payload. Commit 3e47524. The full suite of 127 tests passed. Post-deployment: a CLOSED entry was added to POAM (POAM-P17-01) with full evidence linkage. This path is documented as the standard for in-session emergency remediation when a live red-team finding surfaces a HIGH severity gap.

Cross-reference: `REDTEAM_RESULTS.md` Finding 1 (evidence); `POAM_PLAN_OF_ACTION.md` POAM-P17-01 (tracking); `SSP_SYSTEM_SECURITY_PLAN.md` SI-10 (control); `builds/squire/src/squire/pre_graph_pii.py` (artifact).

---

## Cross-References

| Document | Relationship |
|----------|-------------|
| [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) | System Security Plan with NIST 800-53 control mapping |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | Tracks findings and remediation milestones |
| [REDTEAM_RESULTS.md](REDTEAM_RESULTS.md) | 6 executed red-team cases including Finding 1 emergency remediation |
| [GUARDRAILS_CONFIGURATION.md](GUARDRAILS_CONFIGURATION.md) | Guardrail change control |
| [SQUIRE_MODEL_CARD.md](SQUIRE_MODEL_CARD.md) | Model routing change reference |
| [README.md](README.md) | GRC library index and reading guide |
