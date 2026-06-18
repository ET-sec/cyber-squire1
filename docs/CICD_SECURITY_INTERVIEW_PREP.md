# CI/CD Security Pipeline — Interview Prep Guide

**Role target:** Cybersecurity Engineer
**Your stack:** GitHub Actions, Trivy, Semgrep, Gitleaks, OPA/Rego, Cosign, Syft/SBOM, Terraform (16 files, 30+ resources)

---

## 1. The 60-Second Pitch

Practice this until it sounds like conversation, not a recitation.

> "I built a multi-stage security pipeline in GitHub Actions with two workflows. The first runs on every pull request and every push — it does secrets detection with Gitleaks, filesystem scanning with Trivy for CVEs and misconfigs, and SAST with Semgrep. The Terraform PR workflow is separate and runs format checks, validation, TFLint, Checkov, a plan, then OPA policy gates using eight custom Rego policies before anything gets near production. On merge to main, the pipeline does container image verification with Cosign and generates SBOMs with Syft — one for the repo filesystem and one per container image. The whole thing gates deploys on security scan results. If Trivy finds a CRITICAL or HIGH CVE that has a fix available, the PR doesn't merge."

Three things to remember for the pitch:
1. State the scope (what runs when)
2. Name the tools and what each one catches
3. Say what happens when something fails (blocks vs warns)

---

## 2. Each Tool — What It Does and How to Talk About It

### Trivy

**What it is:** Vulnerability and misconfiguration scanner from Aqua Security.

**What it scans:**
- `fs` mode: the repository filesystem — finds vulnerable packages in package-lock.json, requirements.txt, go.mod, etc.
- `image` mode: container images — scans layers, OS packages, and application dependencies
- `config` mode: Terraform, Kubernetes YAML, Dockerfiles for misconfigs
- `repo` mode: a git repository including commit history

**Your actual config:**
```yaml
scan-type: "fs"
scan-ref: "."
severity: "CRITICAL,HIGH"
format: "sarif"
exit-code: "1"
ignore-unfixed: true
skip-dirs: "DEPRECATED"
```

**How to explain each setting:**
- `severity: CRITICAL,HIGH` — you made a deliberate call not to block on MEDIUM or LOW. Medium/low would create too much noise and cause developers to ignore the tool entirely.
- `exit-code: 1` — this is what makes it a hard gate. Any CRITICAL or HIGH fails the pipeline.
- `ignore-unfixed: true` — this is important. If there's no patch available yet, blocking the PR doesn't help anyone. You can't fix what doesn't have a fix. This reduces noise without reducing security.
- `format: sarif` — SARIF output feeds directly into GitHub's Security tab, so findings appear in the PR as code annotations and in the security dashboard.

**Severity levels:**
- CRITICAL: CVSS 9.0–10.0. Remote code execution, authentication bypass, full system compromise. Non-negotiable blocking.
- HIGH: CVSS 7.0–8.9. Significant data exposure, privilege escalation. Blocking.
- MEDIUM: CVSS 4.0–6.9. Limited impact or requires local access. Advisory.
- LOW: CVSS 0.1–3.9. Minimal risk. Advisory or ignored.
- UNKNOWN: CVE exists but severity hasn't been rated yet.

**How to read Trivy output:**
```
Library          Vulnerability    Severity   Installed Version   Fixed Version
express          CVE-2022-24999   HIGH       4.17.1              4.17.3
```
Three questions: Is there a fix? Is the package actually used in production code? Is this a direct or transitive dependency? A transitive dep with no fix in a package that's only used in dev tooling is very different from a CRITICAL in your auth library.

---

### Semgrep

**What it is:** Static Application Security Testing (SAST) tool. It reads source code without executing it and matches patterns to find security issues.

**How SAST works conceptually:** The tool parses source code into an Abstract Syntax Tree (AST) — a structured representation of the code's logic. Rules are written as pattern matches against that AST. This is more accurate than regex-on-source because it understands code structure, not just text.

**Your rule sets:**
```yaml
config: >-
  p/security-audit
  p/secrets
  p/docker
  p/terraform
```

- `p/security-audit` — broad security patterns: SQL injection, hardcoded credentials, insecure deserialization, XSS, command injection
- `p/secrets` — API keys, tokens, private keys left in code (complements Gitleaks)
- `p/docker` — Dockerfile issues: running as root, using `latest` tag, `ADD` vs `COPY`
- `p/terraform` — Terraform misconfigs: open security groups, unencrypted storage, missing logging

**What a Semgrep rule looks like:**
```yaml
rules:
  - id: hardcoded-secret
    pattern: |
      $X = "..."
      ...
      requests.get(..., headers={"Authorization": $X}, ...)
    message: "Possible hardcoded secret in authorization header"
    languages: [python]
    severity: ERROR
```

**Community rules vs custom rules:** The `p/` prefix means community rulesets maintained by Semgrep. Custom rules let you encode your organization's specific patterns — things like "we never call this internal legacy API directly" or "all SQL queries must go through our ORM layer." You can write custom rules in YAML and add them to your config alongside community rules.

**The limitation worth knowing:** SAST has false positives. It can't know if a string that looks like an API key is actually a test fixture. It can't always follow all code paths. SAST is one layer — not a substitute for code review or DAST.

---

### Gitleaks

**What it is:** Secrets detection tool that scans git history and the current working tree for patterns that look like credentials.

**How it finds secrets:** Gitleaks uses a set of regex patterns, each associated with a known credential type (AWS access keys, GitHub tokens, Stripe keys, generic private keys, etc.). It runs these patterns against every line of code, including commit history.

**Why scanning history matters:** A developer might commit a secret, notice it, delete it in a follow-up commit, and push. The secret is still in the git history, readable by anyone with access to the repo. Without `fetch-depth: 0` in your checkout step, you'd only see the latest commit. Your pipeline uses full history:
```yaml
- name: Checkout code
  uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

**The .gitleaks.toml config:** This is where you tune the tool. Common patterns:
```toml
[allowlist]
  description = "Global allowlist"
  regexes = [
    '''EXAMPLE_SECRET''',           # test fixtures
    '''TEST_API_KEY''',              # known test values
  ]
  paths = [
    '''tests/fixtures/''',           # test data directory
    '''.gitleaks.toml''',            # the config file itself
  ]
  commits = [
    "abc123def456"                   # a specific commit that has a known false positive
  ]
```

The key concept here: you never disable the tool for a broad category. You add a specific, narrow exception with a comment explaining why. That keeps the audit trail clean.

**What happens when it fires:** Gitleaks exits non-zero, the step fails, the PR is blocked. The developer needs to rotate the exposed credential first (it's already compromised), then use git history rewriting or `git filter-repo` to remove it, then force push.

---

### OPA / Rego

**What it is:** Open Policy Agent (OPA) is a general-purpose policy engine. Rego is the policy language. Together they implement policy-as-code.

**What policy-as-code means:** Security rules that used to live in a runbook ("never open port 22 to the public internet") become executable code that runs automatically. The policy is version-controlled, testable, and auditable — just like application code.

**How it fits in your pipeline:**
```
terraform plan → terraform show -json → conftest test plan.json --policy ./policy/
```
Conftest is a tool that runs OPA policies against structured data. You generate the plan as JSON, then evaluate your Rego policies against that JSON before any `terraform apply` runs.

**Your 8 policies:**

| Policy | Type | What it checks |
|--------|------|----------------|
| `deny_public_firewall.rego` | DENY | Firewall rules allowing 0.0.0.0/0 on non-HTTPS ports |
| `deny_no_encryption.rego` | DENY | Spaces buckets without versioning, volumes without filesystem type |
| `deny_root_ssh_key.rego` | DENY | SSH keys named "root" (shared credential anti-pattern) |
| `deny_missing_prevent_destroy.rego` | DENY | Deletion of production resources (droplet, bucket, volume, DB cluster) |
| `warn_tags.rego` | WARN | Droplets without tags (cost tracking) |
| `warn_backup.rego` | WARN | Droplets without backups enabled |
| `warn_naming.rego` | WARN | Resource naming convention violations |
| `warn_sizing.rego` | WARN | Resource size/spec recommendations |

**DENY vs WARN:** DENY policies exit non-zero and block the pipeline. WARN policies produce output in the PR comment but don't fail the job. This is a deliberate design choice — hard blocks for security violations, soft warnings for operational hygiene.

**How to read Rego syntax:**

```rego
package main
import rego.v1

deny contains msg if {
    some rc in input.resource_changes
    rc.type == "digitalocean_firewall"
    not action_is_delete(rc)
    fw := rc.change.after
    some rule in fw.inbound_rule
    rule.protocol != "icmp"
    has_public_source(rule)
    not port_is_https(rule)
    msg := sprintf(
        "DENY: Firewall '%s' allows public inbound on port %s.",
        [fw.name, rule.port_range],
    )
}
```

Read the body as: "For every resource change in the plan, if the resource type is a firewall, and it's not being deleted, and it has an inbound rule that allows public source addresses, and the port is not HTTPS, then deny with this message."

Rego uses logical conjunction — every line in the body must be true for the rule to fire. If any condition is false, the rule doesn't fire. No `if/else` — just conditions.

**Common interview framing for OPA:**
> "Instead of hoping a developer remembers the rule, I encode the rule as code. It runs on every PR. A developer can't accidentally open a database to the public internet because the pipeline will catch it before Terraform applies. And if a new team member joins, they don't need to know the rule from memory — the policy enforces it automatically."

---

### Cosign

**What it is:** A tool from the Sigstore project for signing and verifying container images.

**What signing proves:** That a specific image (identified by its SHA256 digest) was produced by a specific pipeline, key, or identity. It prevents supply chain substitution — someone replacing `postgres:16-alpine` with a modified image that looks identical but has malware inside.

**How it works conceptually:**
1. After building and pushing an image, you sign it: `cosign sign <image>@<digest>`
2. The signature is stored in the same container registry as the image (as a separate tag)
3. Before deploying, you verify: `cosign verify --certificate-identity ... <image>`
4. If the signature doesn't match, deployment is blocked

**Keyless signing:** Traditional signing requires managing a private key, which creates a new secret that needs to be protected. Keyless signing (the Sigstore approach) uses OIDC identity instead. The pipeline authenticates to the Sigstore transparency log (Rekor) using the GitHub Actions OIDC token. The identity is "this GitHub Actions workflow at this commit on this repo" — not a key that could be stolen.

**Your actual use:** Your pipeline verifies signatures on upstream images (postgres, n8n, vault, etc.) rather than signing images you build yourself. This is checking the supply chain integrity of your dependencies — confirming the images you pull are the ones the vendors actually published.

```yaml
- name: Verify upstream image signatures
  continue-on-error: true
  run: |
    cosign verify \
      --certificate-oidc-issuer-regexp '.*' \
      --certificate-identity-regexp '.*' \
      "$IMAGE"
```

The `continue-on-error: true` is intentional — many vendors don't sign their images yet (Ollama, faster-whisper). You're doing discovery and auditing, not hard-blocking, while the ecosystem catches up. You can honestly say: "I know which of my upstream dependencies are signed and which aren't."

---

### Syft / SBOM

**What an SBOM is:** Software Bill of Materials. A machine-readable inventory of every package, library, and component in a piece of software — the equivalent of a nutrition label for code.

**Why it matters:**
- When a new CVE drops (like Log4Shell in 2021), an SBOM lets you instantly answer: "Do any of my systems contain this package?" without manually inspecting every container.
- Supply chain regulations (Executive Order 14028, NTIA guidelines) increasingly require SBOMs for software sold to the federal government.
- It's the foundation for ongoing vulnerability management — you can run new CVE databases against old SBOMs without re-scanning every deployed artifact.

**SPDX vs CycloneDX:**
- SPDX (Software Package Data Exchange): Linux Foundation standard, originally focused on license compliance, now covers security as well. Your pipeline uses `spdx-json`.
- CycloneDX: OWASP standard, designed specifically for security use cases, richer vulnerability data fields. Often preferred for pure security workflows.
- In practice: check what your downstream consumers (SBOM ingestion tools, compliance frameworks) expect and match that.

**What's inside an SBOM:**
```json
{
  "SPDXID": "SPDXRef-DOCUMENT",
  "packages": [
    {
      "name": "express",
      "version": "4.17.1",
      "supplier": "Organization: npmjs",
      "downloadLocation": "https://registry.npmjs.org/express/-/express-4.17.1.tgz",
      "checksums": [{"algorithm": "SHA256", "checksumValue": "abc123..."}]
    }
  ]
}
```

**Your pipeline generates:**
- One repo SBOM (the codebase itself, what packages are in the source)
- One SBOM per container image (postgres, n8n, vault, datadog, cloudflared)
- All stored as GitHub Actions artifacts, retained 90 days
- Named with the commit SHA: `sbom-postgres-<sha>` so you can trace any SBOM back to the exact commit

---

## 3. Pipeline Architecture

### Where each tool runs

```
PULL REQUEST
├── Gitleaks           → secrets in code / git history         [BLOCKS]
├── Trivy (fs mode)    → CVEs in dependencies, misconfigs      [BLOCKS: CRITICAL/HIGH with fix]
├── Semgrep            → SAST security patterns                [BLOCKS based on rule severity]
└── Terraform PR workflow (if terraform/ changed):
    ├── fmt check                                              [advisory]
    ├── init + validate                                        [BLOCKS]
    ├── TFLint                                                 [BLOCKS on error]
    ├── Checkov                                                [BLOCKS per .checkov.yaml]
    ├── terraform plan                                         [BLOCKS if plan fails]
    └── OPA conftest (8 policies)                              [BLOCKS on DENY violations]

MERGE TO MAIN
├── (All PR checks run again)
├── Cosign verification    → upstream image signature audit    [advisory, continue-on-error]
├── Image digest manifest  → pinned digest record              [informational]
├── Syft SBOMs (6 total)  → repo + 5 container images         [informational, 90d retention]
└── terraform apply        → if plan shows changes             [runs only after all security passes]
```

### What blocks vs what's advisory

The distinction is intentional and worth articulating in interviews:

**Hard blocks (pipeline fails, PR can't merge):**
- Gitleaks: any confirmed secret detection
- Trivy: CRITICAL or HIGH CVE that has a fix available
- Semgrep: rules at ERROR severity
- OPA: any `deny` rule fires
- Checkov: any failed check not in the skip list

**Advisory (produces output, doesn't fail):**
- Trivy: vulnerabilities with no fix yet (`ignore-unfixed: true`)
- OPA: `warn` rules — shows in PR comment, doesn't exit non-zero
- Cosign: vendor images without signatures (`continue-on-error: true`)
- TFLint: format warnings

**The philosophy:** Hard blocks for things a developer can actually fix right now. Advisory for things that require external action or carry accepted risk. If everything is a hard block, developers route around the pipeline.

### Handling false positives without disabling the tool

This is a critical interview topic. The wrong answer is "I just set exit-code to 0." The right answers:

**Trivy false positives:**
- Use `.trivyignore` with a specific CVE ID and a comment explaining why
- Add `ignore-unfixed: true` for the class of "no fix available" (already doing this)
- Skip specific directories: `skip-dirs: "DEPRECATED"` (already doing this)
- Never raise the severity threshold broadly — that hides real issues

**Semgrep false positives:**
- Add `# nosemgrep: rule-id` inline comment on the specific line
- For test fixtures, add path exclusions in `.semgrepignore`
- Write a rule exception in the Semgrep config with a comment explaining the suppression

**Gitleaks false positives:**
- Add narrow regex to `.gitleaks.toml` allowlist targeting the specific test value
- Specify exact file paths that contain test fixtures
- Never add a broad pattern that would allow real secrets of that type

**OPA false positives:**
- Add a specific exception in the Rego rule itself with a conditional
- Document accepted risk in the policy comment (example: your `deny_public_firewall.rego` documents the SSH 22 exception)
- The policy itself becomes the documentation of why the exception exists

### GitHub Actions YAML structure — key concepts

```yaml
on:
  push:
    branches: ["main", "dev"]
  pull_request:
    branches: ["main"]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write    # needed for SARIF upload
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0        # full history for Gitleaks

  terraform-apply:
    needs: security-scan        # job ordering - won't run until security-scan passes
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'  # main only
    environment: production     # triggers GitHub environment protection rules
```

Key concepts to know:
- `needs:` creates job dependency — later jobs only run if earlier jobs pass
- `if:` conditions control when a job runs (only on main, only on PR, etc.)
- `permissions:` follows least privilege — only grant what the job needs
- `environment: production` ties to GitHub's environment protection rules (can require manual approval, restrict to protected branches)
- `continue-on-error: true` on a step vs `soft_fail: false` on Checkov — these are different. Step-level vs tool-level failure handling.

---

## 4. How This Connects to the Role

### CI/CD security as attack surface management

The software supply chain is an attack vector. SolarWinds (2020) was a supply chain attack through the build pipeline — malicious code injected into a legitimate build process. XZ Utils (2024) was a backdoor introduced through a malicious open source contributor.

Your pipeline addresses this directly:
- **Gitleaks**: catches insider threat or accidental secret leakage in the commit stream
- **Trivy + Semgrep**: catches vulnerable dependencies and insecure code patterns before they reach production
- **Cosign**: verifies the upstream images you pull are the ones the vendors actually signed
- **SBOM**: creates an auditable inventory so you can respond quickly when new CVEs are published against your dependencies
- **OPA**: prevents infrastructure misconfigurations that would expose the pipeline itself (public firewall rules, unencrypted storage)

In an interview, connect it: "Securing the CI/CD pipeline is a specific instance of attack surface reduction — the attack surface is everything that touches your code between a developer's laptop and production."

### BAS connection

Breach and Attack Simulation can test whether your pipeline actually catches what it claims to catch. You can simulate:
- A commit with a synthetic secret to verify Gitleaks fires
- A PR adding a known-vulnerable package version to verify Trivy fires
- A Terraform change that opens a port to verify OPA blocks it
- An unsigned image substitution to verify Cosign detects it

The pipeline is only as good as its last verified test. BAS closes that gap.

### EASM connection

External Attack Surface Management scans for exposed CI/CD infrastructure. Jenkins dashboards running on port 8080 with default credentials, GitLab instances with public project visibility, exposed Artifact registries — these are EASM targets. Your Cloudflare Tunnel removes the droplet from public exposure entirely. No port-forward, no VPN, no exposed management interface.

---

## 5. Jenkins and GitLab (Transferable Knowledge)

You don't have direct Jenkins or GitLab experience. Here's how to talk about that honestly without underselling yourself.

**The transfer statement:**
> "I built this in GitHub Actions but the concepts translate directly. Each of these tools — Trivy, Semgrep, Gitleaks, OPA — is a standalone binary or API. In Jenkins I'd install them as plugins or shell steps in a Jenkinsfile. In GitLab I'd define stages in .gitlab-ci.yml with runner tags. The security logic doesn't change — where the YAML lives changes."

### Jenkins specifics

**Architecture:**
- Controller (formerly "master"): manages pipelines, schedules builds, serves the UI
- Agents (formerly "slaves"): execute the actual build steps, can be ephemeral containers or persistent VMs
- The controller should never run build code — security separation

**Jenkinsfile:**
```groovy
pipeline {
    agent any
    stages {
        stage('Security Scan') {
            steps {
                sh 'trivy fs . --exit-code 1 --severity CRITICAL,HIGH'
                sh 'semgrep --config p/security-audit .'
            }
        }
        stage('Build') {
            steps {
                sh 'docker build -t myapp:${BUILD_NUMBER} .'
            }
        }
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'kubectl apply -f k8s/'
            }
        }
    }
    post {
        failure {
            emailext(to: 'security@example.com', subject: 'Build Failed', body: '${BUILD_LOG}')
        }
    }
}
```

**Key differences from GitHub Actions:**
- Jenkinsfile is Groovy DSL, not YAML
- Plugins do a lot of what GitHub's ecosystem provides natively (credentials, SCM integration, notifications)
- Jenkins manages its own secret store (Jenkins Credentials) rather than using a platform-native solution
- Self-hosted always — Jenkins doesn't have a managed cloud option the way GitHub Actions has hosted runners
- Shared Libraries let teams package common pipeline logic as reusable Groovy code (similar to composite actions in GitHub)

**Security concerns in Jenkins you should know:**
- Groovy Script Console: if an attacker reaches the Jenkins UI, they can execute arbitrary code on the controller
- Credentials stored in Jenkins can be extracted by any pipeline if not scoped properly
- Plugin vulnerabilities are frequent — Jenkins plugin ecosystem has had many CVEs
- Script Security plugin sandboxes Groovy execution, but sandbox escapes have been found

### GitLab CI specifics

**.gitlab-ci.yml:**
```yaml
stages:
  - security
  - build
  - deploy

trivy-scan:
  stage: security
  image: aquasec/trivy:latest
  script:
    - trivy fs . --exit-code 1 --severity CRITICAL,HIGH
  only:
    - merge_requests
    - main

semgrep:
  stage: security
  image: semgrep/semgrep:latest
  script:
    - semgrep --config p/security-audit .
  allow_failure: false

deploy:
  stage: deploy
  script:
    - ./deploy.sh
  only:
    - main
  needs: ["trivy-scan", "semgrep"]
```

**Key differences from GitHub Actions:**
- Single YAML file (`.gitlab-ci.yml`) defines everything; no separate workflow files per concern
- `stages:` defines execution order; jobs within a stage run in parallel
- `needs:` creates direct job dependencies (same as GitHub Actions `needs:`)
- Runners can be shared (GitLab.com hosted) or self-managed (registered to your instance)
- `allow_failure: false` (default) is the equivalent of GitHub's blocking behavior
- GitLab has native SAST, secret detection, dependency scanning — can replace some external tools but they run on their platform only
- GitLab's security dashboards (Vulnerability Report, Dependency List) are more integrated than GitHub's Security tab

---

## 6. Terraform Security

### What your 16 files manage

**Active production infrastructure (cd-do-infrastructure, 14 files):**

| File | What it manages |
|------|----------------|
| `compute.tf` | The DigitalOcean Droplet (Ubuntu 24.04, 4vCPU/8GB) with `prevent_destroy` lifecycle |
| `firewall.tf` | Inbound/outbound rules — SSH restricted to allowed CIDRs, all outbound allowed |
| `networking.tf` | VPC configuration |
| `dns.tf` | Cloudflare DNS records |
| `tunnel.tf` | Cloudflare Tunnel configuration (n8n subdomain, SSH subdomain) |
| `ssh.tf` | SSH key resource |
| `secrets.tf` | DigitalOcean Spaces bucket for Terraform state backend (sensitive) |
| `dashboard.tf` | DigitalOcean monitoring dashboard |
| `monitoring.tf` | Uptime alerts, threshold alerts |
| `project.tf` | DO Project grouping all resources |
| `providers.tf` | Provider versions (digitalocean, cloudflare) |
| `terraform.tf` | Backend config (Spaces S3-compatible) |
| `variables.tf` | Input variables |
| `outputs.tf` | Outputs (droplet IP, etc.) |
| `templates.tf` | Cloud-init / user data templates |
| `checks.tf` | Terraform checks (postconditions on resources) |

**Legacy/suspended (cd-aws-automation + simple-ec2):** EC2, VPC, NAT, security groups — not active.

### The OPA/Terraform workflow

```
Developer opens PR with terraform/ changes
          ↓
terraform fmt -check     (formatting)
          ↓
terraform init           (provider download)
          ↓
terraform validate       (HCL syntax)
          ↓
tflint                   (best practice linting)
          ↓
checkov                  (static misconfiguration scan against the .tf files themselves)
          ↓
terraform plan           (calculate changes, output plan)
          ↓
terraform show -json     (convert binary plan to JSON)
          ↓
conftest test plan.json --policy ./policy/   (run 8 OPA Rego policies against the plan)
          ↓
Post results as PR comment (pass/fail table for all 7 checks)
          ↓
Merge to main → terraform apply (only if plan showed changes, only after all security passes)
```

**Why OPA runs against the plan JSON, not the .tf files:**
Checkov runs against the static `.tf` files and catches known patterns. OPA runs against the evaluated plan — after Terraform has resolved variables, computed dependencies, and determined the actual changes. This means OPA sees what will actually be created, not what the template says. A variable could resolve to a value that creates a public firewall — OPA catches that, Checkov might not.

### Common Terraform misconfigs to know

These come up in interviews regardless of what cloud provider you're using:

**AWS (even though your prod is DO):**
- Security groups with `0.0.0.0/0` on port 22 or port 3389
- S3 buckets with `acl = "public-read"` or `block_public_acls = false`
- RDS instances with `publicly_accessible = true`
- CloudTrail logging disabled
- No MFA on root account (can't enforce via Terraform but comes up in GRC)
- EBS volumes without encryption (`encrypted = false`)
- Lambda functions with overly broad IAM roles

**DigitalOcean (your stack):**
- Firewalls with `source_addresses = ["0.0.0.0/0"]` on non-HTTPS ports (your OPA policy catches this)
- Droplets without `prevent_destroy` (your deny_missing_prevent_destroy policy catches this)
- Spaces buckets without versioning (your deny_no_encryption policy catches this)
- SSH keys named "root" shared across resources (your deny_root_ssh_key policy catches this)

**General:**
- Hardcoded credentials in `.tf` files — should be environment variables or Vault
- State files stored locally (no remote backend with locking) — concurrency issues
- No state encryption for sensitive outputs
- `terraform destroy` possible in production pipelines — your `prevent_destroy` lifecycle blocks this

---

## 7. Interview Questions — How to Answer Them

### "Walk me through your CI/CD security pipeline"

Start with scope, then tools in order, end with the outcome:

> "I have two GitHub Actions workflows. The main security pipeline runs on every PR and push — it does secrets detection first with Gitleaks scanning full git history, then filesystem vulnerability scanning with Trivy filtering on CRITICAL and HIGH with fixes available, then SAST with Semgrep using the security-audit, secrets, docker, and terraform rule packs. Any of those failures blocks the PR. The Terraform pipeline is separate — it runs format, validate, lint, Checkov static analysis, generates a plan, converts it to JSON, then runs eight custom OPA Rego policies I wrote. On merge to main, the pipeline verifies container image signatures with Cosign and generates SBOMs with Syft for the repo and each container image. The whole thing means nothing reaches production that hasn't cleared secrets detection, vulnerability scanning, static analysis, and policy validation."

### "A developer says your Trivy scan is blocking their deployment. What do you do?"

Don't say "I'll suppress the finding." This is a judgment and communication question.

> "First, I look at the actual finding — what CVE, what package, what severity. If it's a CRITICAL with a patch available, it needs to be fixed before deployment. I'll help the developer understand the risk and what the upgrade path looks like. If the package is a transitive dependency, sometimes it's as simple as bumping a parent package version.
>
> If there's no fix available, I look at whether the vulnerable code path is actually exercised in this application. If the CVE is in an HTTP server component but this package is only used as a CLI tool with no network exposure, that changes the risk. In that case I'd add the specific CVE to `.trivyignore` with a comment explaining the accepted risk and a ticket to revisit it when a fix is available.
>
> If there's no fix and the code path is exposed, that's a genuine security risk and the deployment should wait. The scan doing its job isn't the scan being wrong.
>
> The thing I won't do is raise the severity threshold or disable the tool. That creates a gap I can't see."

### "How would you add security scanning to an existing Jenkins pipeline?"

> "I'd start by understanding what the pipeline currently does and where it runs — whether it's declarative or scripted pipeline, what agents it uses. Then I'd add scanning as new stages, starting with the highest-value, lowest-disruption tools.
>
> Gitleaks first — it's fast, doesn't require building anything, and secret exposure is usually the most urgent risk. I'd add it as a stage before any build steps using a shell step: `sh 'gitleaks detect --source=. --exit-code=1'`.
>
> Then Trivy on the filesystem before the build, and on the built image after. Then Semgrep as a parallel stage alongside Trivy if the pipeline allows parallel execution.
>
> I'd start these as `allowFailure: true` for the first sprint so I can see the baseline noise level without blocking deployments. Once I've tuned the suppressions and the team understands the findings, I'd flip them to blocking.
>
> The tools themselves are the same binaries I use in GitHub Actions — only the YAML syntax and how I handle credentials (Jenkins Credentials binding plugin instead of GitHub Secrets) is different."

### "What's the difference between SAST and DAST?"

> "SAST — Static Application Security Testing — analyzes source code without running it. It catches issues at write time: insecure function calls, SQL injection patterns, hardcoded secrets, logic flaws visible in the code structure. It runs early in the pipeline, before a build. The limitation is it doesn't know what happens at runtime — a variable might look dangerous in the source but always gets sanitized before use.
>
> DAST — Dynamic Application Security Testing — tests a running application from the outside, the way an attacker would. Tools like OWASP ZAP send actual HTTP requests, attempt injections, probe authentication. It catches things SAST misses: runtime configuration issues, authentication state management problems, actual injection vulnerabilities that slip through imperfect static analysis. The limitation is it needs a running environment and only tests code paths the tool can reach.
>
> Best practice is both — SAST as a fast gate in the PR pipeline, DAST in staging before production release. I've implemented SAST with Semgrep and Trivy. I've run ZAP scans against staging environments. They're complementary, not substitutes."

### "How do you handle secrets in CI/CD?"

> "Three principles: never commit them, never log them, inject them from external sources at runtime.
>
> For GitHub Actions, secrets live in the repository's Secrets settings and get injected as environment variables: `${{ secrets.MY_KEY }}`. GitHub automatically redacts them from build logs. For my Terraform pipeline, API keys for DigitalOcean and Cloudflare are stored as GitHub Secrets and injected via the `env:` block on specific steps — not exported globally.
>
> For the running infrastructure, secrets come from Doppler, a secrets manager. The application gets secrets injected at startup via `doppler run -- <command>` — they're in memory only, never written to disk, never in the codebase.
>
> Gitleaks runs in the pipeline as the safety net — if a developer accidentally commits a secret, it gets caught before the PR merges. But the real solution is making it easy to do the right thing. If developers have a simple way to access secrets from the secrets manager, they're less likely to hardcode them.
>
> The failure mode I've seen is secrets in build logs. That happens when a step echoes environment variables for debugging. The fix is to audit every `echo`, `env`, and `printenv` call in pipeline scripts, and to use masked variables where the platform supports it."

---

## 8. What Can Go Wrong

### Pipeline too slow — developers bypass it

**The problem:** If a PR takes 20 minutes to merge because of security scans, developers start pushing directly to main, getting exceptions, or disabling protections.

**How to mitigate:**
- Parallelize jobs that don't depend on each other (Gitleaks, Trivy, and Semgrep can all run simultaneously)
- Cache tool downloads between runs — Trivy downloads a CVE database on every run if not cached
- Use path filters so Terraform checks only run when `.tf` files change
- Separate blocking gates (fast, high-signal) from advisory scans (can run async)
- Measure and report pipeline duration. Set a target. Treat it like a product.

**The cultural piece:** Work with developers, not against them. If the pipeline is catching real issues, that's good. If it's generating noise, that's a problem you need to fix.

### False positives causing alert fatigue

**The problem:** Too many findings, most of them not real risks. Developers start ignoring the output entirely.

**How it happens:** Using community rulesets at maximum sensitivity without tuning. Not adding `.trivyignore` or `nosemgrep` suppressions for known false positives. Not differentiating blocking from advisory.

**The fix:** Triage every finding category. Ask: "If this fires, is there always something a developer should do?" If the answer is no for a class of findings, demote it to advisory or suppress it with documented justification. Track suppression rate over time — if you're suppressing 80% of findings, the rule set isn't calibrated for your codebase.

### Secrets leaked in build logs

**How it happens:**
- `echo $SECRET` in a debug step
- A tool that prints its config including credentials on startup
- `env` or `printenv` called for debugging
- Error messages from API calls that include the request headers (with Bearer tokens)

**How to prevent:**
- Platform-level: use masked variables. GitHub Actions masks secrets automatically in log output.
- Code review for pipeline scripts: treat `.yml` files as sensitive code
- Audit scripts for any command that could expand environment variables into logs
- Add Gitleaks or similar to scan build artifacts and logs (some pipelines generate log archives)

**If it happens:** Rotate the credential first, immediately. Then investigate how it ended up in the log. Then add a check that would have caught it.

### Supply chain attack through compromised dependencies

**The threat:** An attacker compromises an npm package, a Python library, or a container image. Your build pulls it in. Without scanning, it reaches production.

**Your mitigations:**
- Trivy catches known CVEs in dependencies at build time
- Cosign verifies image signatures so a substituted image (same name, different content) fails verification
- SBOM gives you an inventory to query when new CVEs are disclosed
- Pin dependency versions in package files rather than using `latest` or open ranges
- Use hash pinning for GitHub Actions: `actions/checkout@v4` should become `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683` — the SHA is immutable, the tag can be moved

**What none of this fully solves:** A malicious package published to a public registry before any CVE exists for it. This is the XZ Utils problem — sophisticated, long-game supply chain compromise with no CVE to scan for. Defense in depth, behavioral monitoring, and minimal blast radius (least privilege) are the answers there.

### Cosign key management

**The problem with key-based signing:** The private key becomes a high-value target. If stolen, an attacker can sign malicious images as legitimate. Key rotation is operationally painful.

**Keyless signing solves this:** No long-lived private key. The pipeline authenticates using a short-lived OIDC token from the CI platform. The identity is "GitHub Actions workflow on repo X at commit Y" — specific enough to be meaningful, short-lived enough that theft isn't useful.

**For your current setup:** You're doing verification of upstream images, not signing images you build. The risk for you is upstream vendors who don't sign their images — you have no cryptographic guarantee those images are what the vendor published. Your pipeline documents which images are verified vs unverified. The next step would be image pinning by digest for unverified images so at minimum you get a consistent, auditable version.

---

## Quick Reference

### One-line definitions (for rapid-fire questions)

| Tool | What it is |
|------|-----------|
| Trivy | CVE and misconfiguration scanner for containers, filesystems, and git repos |
| Semgrep | SAST tool that matches security patterns against source code AST |
| Gitleaks | Secrets detector that scans code and git history for credentials |
| OPA/Rego | Policy-as-code engine — Rego policies run against structured data to enforce rules |
| Cosign | Container image signing and verification (Sigstore project) |
| Syft | SBOM generator — produces machine-readable component inventories |
| Checkov | Static analysis for Terraform, CloudFormation, Kubernetes YAML misconfigs |
| Conftest | Runs OPA Rego policies against structured data (JSON, YAML, plan files) |
| TFLint | Terraform-specific linter for best practices and provider-specific rules |

### The 3 questions for any finding

1. Is it exploitable in this specific context?
2. Is there a fix available right now?
3. Does the risk of waiting outweigh the cost of fixing immediately?

### Common follow-up questions and quick answers

**"What's CVSS?"** — Common Vulnerability Scoring System. A 0-10 score that rates severity of a vulnerability based on exploitability, impact, and environmental factors. CRITICAL = 9-10, HIGH = 7-8.9.

**"What's a SARIF file?"** — Static Analysis Results Interchange Format. A JSON format for security tool output that GitHub's Security tab natively ingests for code annotations and dashboards.

**"What's a Terraform backend?"** — Where Terraform stores its state file. Your pipeline uses DigitalOcean Spaces (S3-compatible) with locking so multiple runs don't corrupt state.

**"What's `prevent_destroy`?"** — A Terraform lifecycle setting that causes any plan attempting to delete that resource to fail. Your `deny_missing_prevent_destroy.rego` policy enforces this on all production resource types through OPA, so even if the lifecycle block is missing, the plan is rejected.

**"What's the difference between Semgrep and Checkov?"** — Semgrep is general-purpose SAST for source code in any language. Checkov is specifically for IaC (Terraform, CloudFormation, Kubernetes) — it knows the resource types and their security-relevant attributes deeply.

**"What is SBOM used for practically?"** — Rapid impact assessment when a CVE is disclosed. Query the SBOM for the package name, see which services contain it, prioritize remediation. Also: vendor risk assessment, software license compliance, compliance reporting (FedRAMP, DoD).
