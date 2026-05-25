# Secure Software Development Lifecycle

**Organization:** Organization Security Operations Platform
**Assessment Date:** 2026-03-22
**Assessor:** System Owner
**Methodology:** NIST SP 800-218 (SSDF), OWASP SAMM, NIST SP 800-53 Rev. 5
**NIST 800-53 Controls:** SA-11, SA-15, CM-3, CM-4, RA-5, SI-2, SI-7
**Classification:** Internal Use Only
**Version:** 1.0

---

## Document Control

| Field | Value |
|-------|-------|
| Document ID | SDLC-001 |
| Version | 1.0 |
| Status | Approved |
| Last Revised | 2026-03-22 |
| Next Review | 2026-09-22 |
| Author | Information Security Officer |
| Approver | System Owner |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-03-18 | Information Security Officer | Initial release |

---

## 1. Purpose

This document formalizes the Secure Software Development Lifecycle (SSDLC) for the Organization Security Operations Platform. It maps the existing CI/CD security pipeline to a structured development lifecycle, documenting security gates, tooling, enforcement policies, and evidence generation at each phase.

The Organization operates a security-first CI/CD pipeline with two complementary GitHub Actions workflows. The first workflow enforces security scanning on every push and pull request, gating all downstream jobs behind a mandatory security scan. The second workflow validates infrastructure-as-code changes through seven sequential checks before any Terraform modification reaches production. Together, these workflows implement shift-left security testing, supply chain verification, and policy-as-code enforcement.

This document satisfies NIST 800-53 controls for developer security testing (SA-11), development process standards (SA-15), configuration change control (CM-3), impact analysis (CM-4), vulnerability monitoring (RA-5), flaw remediation (SI-2), and software integrity verification (SI-7).

---

## 2. Scope

This Secure SDLC applies to all code, configuration, and infrastructure managed within the Organization's GitHub repository:

- **Infrastructure-as-Code:** 19 Terraform files defining Cloud Provider resources (droplet, firewall, DNS, Spaces, volumes, Cloudflare tunnel configuration)
- **Docker Compose:** 19-service container orchestration stack
- **OPA Policies:** 8 Rego policy files (249 lines) enforcing security, naming, and operational standards
- **CI/CD Workflows:** 2 GitHub Actions workflow files (`security.yml`, `terraform-pr.yml`)
- **Container Images:** 8 upstream images consumed from public registries
- **Automation Workflows:** n8n workflow definitions exported as JSON

### Out of Scope

- Runtime application logic within third-party containers (covered by `POLICY_VULNERABILITY_MANAGEMENT.md`)
- Cloud Provider managed infrastructure (shared responsibility model)
- Cloudflare edge configuration (managed via Terraform, but Cloudflare's own SDLC is their responsibility)

---

## 3. SDLC Phase Mapping

The following table maps traditional SDLC phases to the Organization's tooling and security controls. Each phase has at least one automated enforcement mechanism.

| Phase | Activity | Tools | Security Control | Evidence |
|-------|----------|-------|-----------------|----------|
| **Requirements** | Define infrastructure needs, document security requirements in Terraform variables and OPA policies | Terraform variables, OPA/Conftest policy definitions | SA-15, PL-8 | Policy files in `policy/` directory |
| **Design** | Author Terraform resources with security constraints, define Docker network segmentation | Terraform HCL, Docker Compose YAML | SA-8, SC-7 | `.tf` files, `docker-compose.yaml` |
| **Implementation** | Write IaC, update container configurations, modify automation workflows | Git, VS Code, Terraform CLI | CM-3, SA-11 | Git commit history, branch diffs |
| **Testing (PR)** | Automated validation: format, syntax, linting, IaC security scan, policy check, plan review | `terraform fmt`, `terraform validate`, TFLint, Checkov, `terraform plan`, Conftest/OPA | SA-11, CM-4, RA-5 | PR comment with status table |
| **Testing (Merge)** | Security gate: secrets detection, CVE scanning, SAST analysis | Gitleaks, Trivy, Semgrep | SA-11, RA-5, SI-7 | SARIF uploads to GitHub Security tab |
| **Deployment** | Conditional Terraform apply, container signature verification, SBOM generation | Terraform apply, Cosign, Anchore SBOM | CM-3, SI-7, SA-12 | Apply logs, digest manifest, SBOM artifacts |
| **Monitoring** | Runtime detection, log aggregation, metrics collection | Falco, Datadog, Fluentd | SI-4, AU-6, IR-5 | Falco alerts, Datadog dashboards |

---

## 4. Pipeline Architecture

The Organization operates two GitHub Actions workflows that form the complete CI/CD security pipeline. All security scans must pass before any production change is applied.

### 4.1 Workflow Overview

```
PR WORKFLOW (terraform-pr.yml):
  Triggers: Pull request to main (terraform/ path changes)

  commit ─→ [fmt] ─→ [init] ─→ [validate] ─→ [TFLint] ─→ [Checkov] ─→ [plan] ─→ [OPA/Conftest] ─→ PR Comment
                                                                                                       │
                                                                                                       │ 7-step status table
                                                                                                       │ posted to PR
                                                                                                       ▼
MERGE WORKFLOW (security.yml):
  Triggers: Push to main/dev, Pull request to main

  push ─→ [Gitleaks] ─→ [Trivy] ─→ [Semgrep] ──┬──→ [Terraform Init] ─→ [Plan] ─→ [Apply*]
          │              │            │           │
          │  secrets     │  CVE/FS    │  SAST     ├──→ [Cosign Verify] ─→ Digest Manifest
          │  detection   │  scan      │  4 rules  │     8 images
          │              │            │           │
          │              ▼            │           └──→ [Anchore SBOM] ─→ 90-day Retention
          │         GitHub Security   │                 6 SBOMs (1 repo + 5 images)
          │         Tab (SARIF)       │
          ▼                           ▼
     Block pipeline            Block pipeline
     on finding                on finding

  * Terraform Apply runs only on main branch, only when plan detects changes
```

### 4.2 Job Dependencies

The `security-scan` job in `security.yml` is the gate job. Three downstream jobs depend on it:

```
security-scan (GATE)
    ├── terraform-apply   (main branch only, depends: security-scan)
    ├── container-verification  (main branch only, depends: security-scan)
    └── sbom              (main branch only, depends: security-scan)
```

If `security-scan` fails, none of the downstream jobs execute. This ensures that no infrastructure change, container verification, or SBOM generation occurs against code that has known secrets, CVEs, or SAST findings.

### 4.3 Trigger Conditions

| Workflow | Trigger | Branch | Condition |
|----------|---------|--------|-----------|
| `security.yml` | `push` | main, dev | Every push |
| `security.yml` | `pull_request` | main | Every PR |
| `terraform-pr.yml` | `pull_request` | main | Only when `terraform/infrastructure/**`, `policy/**`, or the workflow file itself changes |

---

## 5. Security Gate Definitions

Each security gate has a defined purpose, scan target, severity threshold, and pipeline action.

### 5.1 Gitleaks (Secrets Detection)

| Attribute | Value |
|-----------|-------|
| **Tool** | Gitleaks v2 (GitHub Action) |
| **Phase** | Merge pipeline, first scan |
| **Scan Target** | Full git history (fetch-depth: 0) |
| **What It Detects** | Hardcoded API keys, tokens, passwords, private keys, connection strings in source code and git history |
| **Severity Threshold** | Any finding blocks the pipeline |
| **Action on Failure** | Pipeline halted, all downstream jobs skipped |
| **Evidence** | GitHub Actions log output |
| **NIST Controls** | RA-5, IA-5(7) |

Gitleaks runs with a license key for enhanced rule coverage. The full git history scan (fetch-depth: 0) ensures that secrets committed and subsequently removed are still detected.

### 5.2 Trivy (CVE and Filesystem Scan)

| Attribute | Value |
|-----------|-------|
| **Tool** | Trivy (aquasecurity/trivy-action) |
| **Phase** | Merge pipeline, second scan |
| **Scan Target** | Repository filesystem |
| **What It Detects** | Known CVEs in dependencies, OS packages, language-specific libraries, misconfigurations in IaC files |
| **Severity Threshold** | CRITICAL and HIGH (exit-code: 1) |
| **Output Format** | SARIF, uploaded to GitHub Security tab |
| **Action on Failure** | Pipeline halted, all downstream jobs skipped |
| **Evidence** | SARIF file in GitHub Security tab, filterable by severity |
| **Configuration** | `ignore-unfixed: true`, `skip-dirs: DEPRECATED` |
| **NIST Controls** | RA-5, SI-2, SI-5 |

The `ignore-unfixed: true` flag suppresses findings where no patched version exists, reducing noise from vulnerabilities outside the Organization's remediation ability. The SARIF upload enables GitHub's native security dashboard for tracking and trending.

### 5.3 Semgrep (Static Application Security Testing)

| Attribute | Value |
|-----------|-------|
| **Tool** | Semgrep v1 (semgrep/semgrep-action) |
| **Phase** | Merge pipeline, third scan |
| **Scan Target** | Repository source code |
| **What It Detects** | Code-level vulnerabilities, injection patterns, insecure configurations, Docker and Terraform misconfigurations |
| **Rule Sets** | 4 configurations: `p/security-audit`, `p/secrets`, `p/docker`, `p/terraform` |
| **Action on Failure** | Pipeline halted, all downstream jobs skipped |
| **Evidence** | Semgrep Cloud dashboard (authenticated via SEMGREP_APP_TOKEN) |
| **NIST Controls** | SA-11, RA-5 |

The four rule sets provide layered coverage:

| Rule Set | Focus Area | Example Findings |
|----------|-----------|-----------------|
| `p/security-audit` | General security patterns | SQL injection, XSS, path traversal, insecure deserialization |
| `p/secrets` | Hardcoded credentials | API keys in source, password literals, token patterns |
| `p/docker` | Container security | Running as root, missing health checks, insecure base images |
| `p/terraform` | IaC misconfigurations | Open security groups, unencrypted storage, missing logging |

### 5.4 Terraform Format Check

| Attribute | Value |
|-----------|-------|
| **Tool** | `terraform fmt -check -diff` |
| **Phase** | PR pipeline, first check |
| **Scan Target** | All `.tf` files in the IaC directory |
| **What It Detects** | Non-canonical HCL formatting |
| **Action on Failure** | Marked in PR status table, `continue-on-error: true` |
| **NIST Controls** | CM-3, SA-15 |

### 5.5 Terraform Validate

| Attribute | Value |
|-----------|-------|
| **Tool** | `terraform validate` |
| **Phase** | PR pipeline, third check (after init) |
| **Scan Target** | HCL syntax and internal consistency |
| **What It Detects** | Invalid resource references, missing required arguments, type mismatches |
| **Action on Failure** | Pipeline halted |
| **NIST Controls** | CM-3, SA-11 |

### 5.6 TFLint (Terraform Linter)

| Attribute | Value |
|-----------|-------|
| **Tool** | TFLint with `.tflint.hcl` configuration |
| **Phase** | PR pipeline, fourth check |
| **Scan Target** | Terraform HCL files |
| **What It Detects** | Deprecated syntax, invalid resource sizes, provider-specific best practice violations |
| **Action on Failure** | Pipeline halted |
| **NIST Controls** | SA-11, SA-15 |

### 5.7 Checkov (IaC Security Scanner)

| Attribute | Value |
|-----------|-------|
| **Tool** | Checkov (bridgecrewio/checkov-action) |
| **Phase** | PR pipeline, fifth check |
| **Scan Target** | Terraform directory with `.checkov.yaml` configuration |
| **What It Detects** | CIS benchmark violations, security misconfigurations, missing encryption, overly permissive access |
| **Action on Failure** | Pipeline halted (`soft_fail: false`) |
| **NIST Controls** | RA-5, CM-6, SC-28 |

Checkov enforces hard failures. Any CIS benchmark violation blocks the PR from proceeding to the plan stage. Intentional exceptions (such as break-glass SSH access) are documented in the `.checkov.yaml` skip list and cross-referenced in the `CIS_RISK_REGISTER.md`.

### 5.8 Conftest/OPA (Policy-as-Code)

| Attribute | Value |
|-----------|-------|
| **Tool** | Conftest v0.57.0 with 8 custom Rego policies |
| **Phase** | PR pipeline, seventh check (after plan JSON generation) |
| **Scan Target** | Terraform plan JSON output |
| **What It Detects** | Custom organizational policy violations (see Section 7) |
| **Action on Failure** | `deny` policies halt the pipeline, `warn` policies are informational |
| **Evidence** | Conftest output appended to GitHub Step Summary |
| **NIST Controls** | CM-3, CM-6, SA-15 |

---

## 6. Tool Configuration Matrix

| Tool | SDLC Phase | Scan Type | Severity Threshold | Action on Failure | Output |
|------|-----------|-----------|-------------------|-------------------|--------|
| Gitleaks v2 | Merge | Secrets detection | Any finding | Block pipeline | Actions log |
| Trivy | Merge | CVE + filesystem | CRITICAL, HIGH | Block pipeline | SARIF → GitHub Security |
| Semgrep v1 | Merge | SAST (4 rule sets) | Per-rule default | Block pipeline | Semgrep Cloud |
| `terraform fmt` | PR | Format validation | Any diff | Warn (continue-on-error) | PR comment |
| `terraform validate` | PR | HCL syntax | Any error | Block pipeline | PR comment |
| TFLint | PR | Linting + best practices | Any warning | Block pipeline | PR comment |
| Checkov | PR | IaC security (CIS) | Any failing check | Block pipeline | PR comment |
| `terraform plan` | PR + Merge | Change preview | Plan failure (exit 1) | Block pipeline | PR comment / apply decision |
| Conftest/OPA | PR | Custom policy (8 Rego) | deny = block, warn = info | Block on deny | GitHub Step Summary |
| Cosign | Merge | Image signature verification | Unsigned image | Log (continue-on-error) | Digest manifest |
| Anchore SBOM | Merge | Software composition | N/A (generation only) | N/A | SPDX-JSON artifacts (90-day retention) |

---

## 7. OPA Policy Enforcement

The Organization maintains 8 custom OPA/Rego policies (249 lines total) in the `policy/` directory. These policies evaluate the Terraform plan JSON output and enforce organizational security and operational standards.

### 7.1 Deny Policies (Hard Fail)

Deny policies halt the pipeline. Any violation must be resolved before the PR can merge.

#### deny_public_firewall

**Purpose:** Blocks any Cloud Provider firewall rule that allows public internet access (0.0.0.0/0 or ::/0) on non-HTTPS ports.

**Logic:** Iterates over all `cloud_provider_firewall` inbound rules. If a rule has a public source address and the port is not 443, the policy emits a deny.

**Example violation:**
```
DENY: Firewall 'primary-node-firewall' allows public inbound on port 22.
Only HTTPS (443) permitted from 0.0.0.0/0.
```

**Accepted risk:** The production firewall intentionally allows SSH (port 22) from 0.0.0.0/0 as a break-glass emergency access path. This is documented as an accepted risk in the `CIS_RISK_REGISTER.md` and Checkov skip list (CKV_DIO_4).

#### deny_no_encryption

**Purpose:** Enforces data integrity safeguards on storage resources.

**Logic:** Two rules. First, requires versioning enabled on all Spaces buckets (the Cloud Provider encrypts all block storage at rest by default, so versioning is the proxy for data integrity assurance on object storage). Second, requires `filesystem_type` set on all volumes.

**Example violation:**
```
DENY: Spaces bucket 'tfstate-bucket' must have versioning enabled for data integrity.
DENY: Volume 'data-vol' must have filesystem_type set (ext4 or xfs).
```

#### deny_missing_prevent_destroy

**Purpose:** Prevents accidental deletion of production resources.

**Logic:** Flags any Terraform plan that includes a `delete` action on critical resource types: droplets, Spaces buckets, volumes, and database clusters.

**Example violation:**
```
DENY: Attempted deletion of production resource 'cloud_provider_instance.primary_node'
(type: cloud_provider_instance). Must have lifecycle.prevent_destroy.
```

#### deny_root_ssh_key

**Purpose:** Blocks SSH keys with "root" in the name to prevent shared credential anti-patterns.

**Logic:** Checks all `cloud_provider_ssh_key` resources. If the key name contains "root" (case-insensitive), the policy emits a deny.

**Example violation:**
```
DENY: SSH key 'root-admin' contains 'root' in name. Use named user keys only.
```

### 7.2 Warn Policies (Informational)

Warn policies log advisory messages but do not block the pipeline.

#### warn_naming

**Purpose:** Enforces the `cd-` prefix naming convention on droplets and firewalls for consistent identification and cost tracking.

**Example warning:**
```
WARN: Resource 'cloud_provider_instance.web' name 'web-node' does not follow 'cd-' prefix convention.
```

#### warn_backup

**Purpose:** Flags droplets that do not have Cloud Provider weekly backups enabled.

**Example warning:**
```
WARN: Instance 'primary-node' does not have backups enabled. Consider enabling for disaster recovery.
```

#### warn_sizing

**Purpose:** Flags expensive droplet sizes (8+ vCPUs or specialized types like GPU, memory-optimized, storage-optimized) for cost review.

**Example warning:**
```
WARN: Instance 'primary-node' uses size 's-8vcpu-16gb'. Verify this is cost-appropriate.
```

#### warn_tags

**Purpose:** Flags droplets with no tags, which impedes cost tracking and resource filtering.

**Example warning:**
```
WARN: Instance 'primary-node' has no tags. Add tags for cost tracking and filtering.
```

### 7.3 Policy Summary

| Policy | Type | Resource Types | Lines | Purpose |
|--------|------|---------------|-------|---------|
| `deny_public_firewall` | Deny | `cloud_provider_firewall` | 48 | Block non-HTTPS public inbound |
| `deny_no_encryption` | Deny | `cloud_provider_spaces_bucket`, `cloud_provider_volume` | 45 | Require versioning and filesystem type |
| `deny_missing_prevent_destroy` | Deny | Instances, Buckets, Volumes, DBs | 32 | Block production resource deletion |
| `deny_root_ssh_key` | Deny | `cloud_provider_ssh_key` | 21 | Block root-named SSH keys |
| `warn_naming` | Warn | Instances, Firewalls | 26 | Enforce cd- naming convention |
| `warn_backup` | Warn | Instances | 20 | Flag missing backups |
| `warn_sizing` | Warn | Instances | 39 | Flag expensive instance sizes |
| `warn_tags` | Warn | Instances | 23 | Flag untagged resources |
| **Total** | | | **249** | |

---

## 8. Container Supply Chain Security

The merge pipeline includes container supply chain verification through two mechanisms: cryptographic signature verification with Cosign and software bill of materials generation with Anchore.

### 8.1 Cosign Image Verification

After the security-scan gate passes, the `container-verification` job verifies cryptographic signatures on all 8 upstream container images consumed by the platform.

**Verified images:**

| Image | Service | Registry |
|-------|---------|----------|
| `postgres:16-alpine` | svc-db (PostgreSQL) | Docker Hub |
| `n8nio/n8n:latest` | svc-automation (n8n SOAR) | Docker Hub |
| `ollama/ollama:latest` | svc-llm (Ollama) | Docker Hub |
| `fedirz/faster-whisper-server:latest-cpu` | svc-transcription (Whisper) | Docker Hub |
| `hashicorp/vault:1.15` | svc-secrets (HashiCorp Vault) | Docker Hub |
| `quay.io/keycloak/keycloak:23.0` | svc-identity (Keycloak) | Quay.io |
| `datadog/agent:latest` | svc-monitor (Datadog Agent) | Docker Hub |
| `cloudflare/cloudflared:latest` | svc-tunnel (Cloudflare Tunnel) | Docker Hub |

**Verification flow:**

```
For each image:
  1. cosign verify with flexible OIDC issuer matching
  2. Record result: VERIFIED or UNVERIFIED
  3. Generate summary: X / 8 verified

After verification:
  4. docker manifest inspect each image
  5. Extract digest (SHA-256)
  6. Generate digest manifest artifact
```

The verification step uses `continue-on-error: true` because not all upstream publishers sign their images with Cosign. The digest manifest provides a pinned reference for each image consumed during the build, enabling reproducible deployments and forensic analysis if a supply chain compromise is discovered.

### 8.2 SBOM Generation

The `sbom` job generates Software Bills of Materials in SPDX-JSON format using Anchore's SBOM action.

**Generated SBOMs:**

| SBOM Target | Type | Artifact Name Pattern |
|-------------|------|----------------------|
| Repository filesystem | Directory scan | `sbom-repo-{commit_sha}` |
| `postgres:16-alpine` | Container image | `sbom-postgres-{commit_sha}` |
| `n8nio/n8n:latest` | Container image | `sbom-n8n-{commit_sha}` |
| `hashicorp/vault:1.15` | Container image | `sbom-vault-{commit_sha}` |
| `datadog/agent:latest` | Container image | `sbom-datadog-{commit_sha}` |
| `cloudflare/cloudflared:latest` | Container image | `sbom-cloudflared-{commit_sha}` |

All SBOMs are uploaded as GitHub Actions artifacts with 90-day retention. The SPDX-JSON format enables downstream consumption by vulnerability scanners, license compliance tools, and audit systems.

**SBOM coverage rationale:** The 5 container images selected for SBOM generation are those with the largest dependency trees and highest exposure to CVEs. Lighter images (Ollama, Whisper, Keycloak) are covered by Cosign verification and Trivy scanning.

---

## 9. PR Validation Workflow Detail

The `terraform-pr.yml` workflow runs 7 sequential validation steps on every pull request that modifies Terraform files. The results are posted as a structured comment on the PR.

### 9.1 Step Sequence

| Step | Tool | ID | Failure Behavior |
|------|------|----|-----------------|
| 1 | `terraform fmt -check -diff` | `fmt` | Continue on error (advisory) |
| 2 | `terraform init` | `init` | Hard fail |
| 3 | `terraform validate` | `validate` | Hard fail |
| 4 | TFLint (with `.tflint.hcl`) | `tflint` | Hard fail |
| 5 | Checkov (with `.checkov.yaml`) | `checkov` | Hard fail (`soft_fail: false`) |
| 6 | `terraform plan` | `plan` | Continue on error (captured for comment) |
| 7 | Conftest/OPA (8 policies) | `conftest` | Hard fail on deny, warn is advisory |

### 9.2 PR Comment

After all steps complete (or fail), a GitHub Actions script posts a structured comment to the PR:

```
## Terraform PR Validation

| Check | Status |
|-------|--------|
| Format | `pass` |
| Init | `pass` |
| Validate | `pass` |
| TFLint | `pass` |
| Checkov | `FAIL` |
| Plan | `pass` |
| OPA Policies | `pass` |

<details><summary>Show Plan Output</summary>
[terraform plan output, truncated at 60,000 characters]
</details>

Triggered by @developer on pull_request
Commit: abc1234
```

The comment uses a marker (`<!-- terraform-plan-comment -->`) to update the same comment on subsequent pushes rather than creating duplicates.

### 9.3 Plan JSON for OPA

After the plan step, the workflow generates a JSON representation of the plan:

```
terraform plan -out=tfplan.binary
terraform show -json tfplan.binary > plan.json
conftest test plan.json --policy policy/
```

This allows OPA/Conftest to evaluate the planned changes (resource additions, modifications, deletions) against all 8 Rego policies before the plan is approved.

---

## 10. Failure Handling

### 10.1 Gate Failure Response

| Gate | Failure Type | Notification | SLA |
|------|-------------|-------------|-----|
| Gitleaks | Hardcoded secret detected | GitHub Actions email, PR blocked | Immediate: rotate exposed credential within 1 hour, remediate code within 24 hours |
| Trivy | CRITICAL/HIGH CVE | SARIF in GitHub Security tab, pipeline blocked | CRITICAL: 48 hours, HIGH: 7 days (per `POLICY_VULNERABILITY_MANAGEMENT.md`) |
| Semgrep | SAST finding | Semgrep Cloud alert, pipeline blocked | CRITICAL: 48 hours, HIGH: 7 days |
| Checkov | CIS violation | PR comment status table | Remediate before merge, or document exception in `.checkov.yaml` and `CIS_RISK_REGISTER.md` |
| OPA deny | Policy violation | Conftest output in Step Summary | Remediate before merge, or update policy with documented justification |
| Cosign | Unsigned image | Log warning (non-blocking) | Document in next supply chain review |

### 10.2 Exception Process

When a security gate finding is determined to be a false positive or an accepted risk:

1. **Document** the exception in the relevant register (`CIS_RISK_REGISTER.md`, `POAM_PLAN_OF_ACTION.md`, or Checkov skip list)
2. **Justify** the acceptance with a risk rationale and compensating control
3. **Approve** by System Owner (documented in the exception entry)
4. **Review** during the next quarterly risk register review
5. **Suppress** in the tool configuration (`.checkov.yaml` skip, `.gitleaks.toml` allowlist, or Semgrep nosem comment)

### 10.3 Rollback Procedure

If a security issue is discovered after merge and deployment:

1. Identify the commit that introduced the issue
2. Create a revert PR (triggers full PR validation pipeline)
3. Merge revert (triggers full merge pipeline including Terraform apply)
4. Verify rollback via Terraform state and container status
5. Document the incident per `POLICY_INCIDENT_RESPONSE.md`

---

## 11. Metrics and Evidence

### 11.1 Pipeline Metrics

The following metrics are collected automatically through GitHub Actions and tool dashboards:

| Metric | Source | Frequency | Purpose |
|--------|--------|-----------|---------|
| PRs with security scan pass/fail | GitHub Actions | Per PR | Measure developer security compliance |
| Gitleaks findings per scan | GitHub Actions logs | Per push | Track secret hygiene over time |
| Trivy CRITICAL/HIGH counts | GitHub Security tab (SARIF) | Per push | Trend CVE exposure |
| Semgrep finding density | Semgrep Cloud | Per push | Track code quality trajectory |
| Checkov pass rate | PR comments | Per IaC PR | Measure IaC compliance posture |
| OPA deny/warn counts | GitHub Step Summary | Per IaC PR | Track policy violation frequency |
| Cosign verification rate | Container-verification job | Per merge | Monitor supply chain integrity coverage |
| SBOM generation success | SBOM job | Per merge | Verify software inventory completeness |
| Time from finding to remediation | GitHub Issues / POA&M | Per finding | Measure SLA compliance |

### 11.2 Evidence Artifacts

| Artifact | Location | Retention | Format |
|----------|----------|-----------|--------|
| Trivy SARIF results | GitHub Security tab | Indefinite | SARIF |
| SBOM (repository) | GitHub Actions artifacts | 90 days | SPDX-JSON |
| SBOM (5 container images) | GitHub Actions artifacts | 90 days | SPDX-JSON |
| Image digest manifest | GitHub Actions logs | 90 days | Plain text |
| PR validation comments | Pull request history | Indefinite | Markdown table |
| Conftest/OPA output | GitHub Step Summary | Indefinite | Plain text |
| Semgrep findings | Semgrep Cloud | Per retention policy | Semgrep format |

### 11.3 Audit Trail

Every pipeline run is traceable through:

- **Git commit SHA:** Links the exact code state to the scan results
- **GitHub Actions run ID:** Provides full execution logs for each job and step
- **SBOM artifact naming:** Includes the commit SHA (`sbom-repo-{sha}`) for correlation
- **PR comment history:** Shows the validation state at each push to a PR branch

---

## 12. Continuous Improvement

### 12.1 Pipeline Review Cadence

| Review Activity | Frequency | Owner |
|----------------|-----------|-------|
| OPA policy review and update | Quarterly | System Owner |
| Checkov skip list audit | Quarterly | Information Security Officer |
| Tool version updates (Gitleaks, Trivy, Semgrep, Conftest) | Monthly | System Owner |
| SBOM coverage review (add/remove images) | Semi-annual | Information Security Officer |
| Full SDLC process review | Annual | System Owner |

### 12.2 Planned Enhancements

| Enhancement | Priority | Target | NIST Control |
|-------------|----------|--------|-------------|
| DAST integration (OWASP ZAP) | Medium | Shipped 2026-05-25 | SA-11(8), RA-5 |
| Container runtime scanning in pipeline | Medium | Q3 2026 | RA-5, SI-7 |
| Signed commits enforcement | Low | Q4 2026 | CM-3, SI-7 |
| Dependency update automation (Dependabot) | Low | Q4 2026 | SI-2, RA-5 |

---

## 13. Cross-References

| Document | Relationship |
|----------|-------------|
| [POLICY_CHANGE_MANAGEMENT.md](POLICY_CHANGE_MANAGEMENT.md) | Defines the change control process that this SDLC implements technically |
| [POLICY_VULNERABILITY_MANAGEMENT.md](POLICY_VULNERABILITY_MANAGEMENT.md) | Defines severity classifications and remediation SLAs referenced by pipeline gates |
| [CIS_RISK_REGISTER.md](CIS_RISK_REGISTER.md) | Documents accepted risks and Checkov skip justifications |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | Tracks open remediation items from pipeline findings |
| [AI_SUPPLY_CHAIN_RISK.md](AI_SUPPLY_CHAIN_RISK.md) | Covers supply chain risks for AI-specific container images (Ollama, OpenClaw) |
| [DAST_METHODOLOGY.md](DAST_METHODOLOGY.md) | Documents the DAST assessment approach now running in CI referenced in Section 12.2 |
| [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) | Maps NIST 800-53 controls to this SDLC's technical implementation |
| [THREAT_MODEL_STRIDE.md](THREAT_MODEL_STRIDE.md) | Identifies threats that this SDLC's security gates are designed to detect |

---

## Appendix A: Workflow File Reference

| File | Path | Lines | Triggers |
|------|------|-------|----------|
| `security.yml` | `.github/workflows/security.yml` | 299 | Push to main/dev, PR to main |
| `terraform-pr.yml` | `.github/workflows/terraform-pr.yml` | 207 | PR to main (terraform path changes) |

## Appendix B: OPA Policy File Reference

| File | Path | Type | Lines |
|------|------|------|-------|
| `deny_public_firewall.rego` | `terraform/infrastructure/policy/` | Deny | 48 |
| `deny_no_encryption.rego` | `terraform/infrastructure/policy/` | Deny | 45 |
| `deny_missing_prevent_destroy.rego` | `terraform/infrastructure/policy/` | Deny | 32 |
| `deny_root_ssh_key.rego` | `terraform/infrastructure/policy/` | Deny | 21 |
| `warn_naming.rego` | `terraform/infrastructure/policy/` | Warn | 26 |
| `warn_backup.rego` | `terraform/infrastructure/policy/` | Warn | 20 |
| `warn_sizing.rego` | `terraform/infrastructure/policy/` | Warn | 39 |
| `warn_tags.rego` | `terraform/infrastructure/policy/` | Warn | 23 |

## Appendix C: GitHub Actions Permissions

| Workflow | Permission | Scope | Reason |
|----------|-----------|-------|--------|
| `security.yml` / `security-scan` | `contents: read` | Repository code | Checkout and scan |
| `security.yml` / `security-scan` | `security-events: write` | GitHub Security | Upload Trivy SARIF |
| `security.yml` / `security-scan` | `actions: read` | GitHub Actions | Required by Gitleaks |
| `security.yml` / `terraform-apply` | `contents: read` | Repository code | Terraform init and apply |
| `security.yml` / `container-verification` | `contents: read` | Repository code | Cosign verification |
| `terraform-pr.yml` | `contents: read` | Repository code | All validation steps |
| `terraform-pr.yml` | `pull-requests: write` | PR comments | Post validation status table |
