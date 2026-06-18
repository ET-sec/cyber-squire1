# Drill 09: Supply Chain CI/CD (GitHub Actions + Docker + ECR)

## Prompt
"Threat model our build and release pipeline. Engineers push to GitHub. GitHub Actions builds Docker images, pushes to ECR. EKS pulls from ECR via IRSA. Threat-model the supply chain end to end."

## Scope (Phase 1)

Assets:
- Source code in GitHub
- GitHub Actions runners and secrets
- Docker images and tags in ECR
- Signing keys (Cosign)
- IAM roles used by Actions (OIDC federation)
- SBOM artifacts
- Production EKS deployment configs

Actors:
- Developers (push code)
- Maintainers (review and merge)
- External attacker (PR injection)
- Compromised dependency (npm, pypi, base image)
- Compromised Action (third-party `uses:`)
- Compromised maintainer account
- AWS itself (out of scope)

Data classes:
- Source code (medium-high)
- Build artifacts (high)
- Secrets in CI (highest)
- Signing keys (highest)

Assumptions:
- Branch protection enforced on `main`
- Required reviewers on PRs
- GitHub OIDC federation to AWS (no static AWS keys in CI)
- Cosign keyless signing
- Trivy scanner in pipeline
- SBOM published per release

## DFD

```
                                   GITHUB TRUST BOUNDARY
[ Developer ] --git push--> ( GitHub Repo )
                                |
                                | PR opened
                                v
                          ( PR checks )
                                |
                                | merge to main
                                v
                          ( GH Actions Runner )
                                |     \
                                |      \-- pull deps (npm, pypi, ghcr base image)
                                |
                                | uses GH OIDC -> assume AWS role
                                |
                                v
- - - - - - - - - - - - - - - -|- - - - - - - - - - AWS ACCOUNT BOUNDARY
                                v
                          ( Build container )
                                |
                                | Trivy scan, SBOM gen, Cosign sign
                                |
                                v
                          ( Push to ECR )
                                |
                                v
                          ===== ECR =====
                                ^
                                | pull (IRSA on EKS)
                                |
- - - - - - - - - - - - - - - -|- - - - - - - - - - DEPLOY BOUNDARY
                                |
                          ( EKS pod )

[ Maintainer ] --review--> ( GitHub PR )
[ Attacker ]  --PR--> ( GitHub PR )    <-- could trigger pull_request workflows
```

Trust boundaries:
1. Developer to GitHub (TB1)
2. PR (especially from forks) to Actions (TB2)
3. Actions runner to dependency registries (TB3, supply chain inbound)
4. Actions runner to AWS via OIDC (TB4)
5. Actions runner to ECR (TB5, image publish)
6. ECR to EKS (TB6, image pull)
7. Maintainer review boundary (TB7, social/process)
8. Cosign key custody (TB8)

## STRIDE matrix

| # | Boundary | STRIDE | Threat | L | I | Risk |
|---|----------|--------|--------|---|---|------|
| 1 | TB1 | S | Compromised maintainer GitHub account pushes to main | L | H | M |
| 2 | TB1 | S | Personal Access Token leaked, attacker pushes as dev | M | H | H |
| 3 | TB2 | E | `pull_request` workflow runs attacker's code with secrets (poisoned PR) | H | H | H |
| 4 | TB2 | E | Workflow `pull_request_target` runs with write tokens on attacker code | M | H | H |
| 5 | TB3 | T | Typosquatted npm/pypi pulled into build, malicious code runs in CI | M | H | H |
| 6 | TB3 | T | Compromised legitimate package (XZ-style) | L | H | M |
| 7 | TB3 | T | Base image pulled by `latest` tag, swapped to malicious | M | H | H |
| 8 | TB4 | E | OIDC trust policy too broad, any repo can assume the role | L | H | M |
| 9 | TB4 | E | Action with `id-token: write` exfiltrates token to external endpoint | M | H | H |
| 10 | TB5 | T | Push to ECR with mutable tag, image silently swapped post-scan | H | H | H |
| 11 | TB5 | T | Cosign signing skipped in fast-path build | M | H | H |
| 12 | TB6 | T | EKS pulls image without verifying signature | M | H | H |
| 13 | TB7 | E | Single-reviewer policy, attacker socially engineers approval | L | H | M |
| 14 | TB8 | I | Cosign key (if not keyless) leaked from CI secret | L | H | M |
| 15 | TB1 | T | Force push to main bypasses branch protection because rules misconfigured | L | H | M |
| 16 | TB3 | T | Docker build pulls a build-tool with `curl | sh` install (RCE in CI) | H | M | H |

## Top 10

1. (#3) Poisoned PR workflow
2. (#10) Mutable tag swap
3. (#12) EKS pulls unsigned image
4. (#7) Base image latest-tag swap
5. (#5) Typosquatted dep
6. (#9) Token exfiltration via Action
7. (#11) Skipped signing on hot path
8. (#16) curl-pipe-sh in build
9. (#4) `pull_request_target` misuse
10. (#2) Leaked PAT

## Mitigations

| # | Primary | Compensating | Cost |
|---|---------|--------------|------|
| 1 | Required workflow approval for first-time contributors, no secrets on `pull_request` from forks | Use `pull_request_target` only with explicit allow-list and read-only token | M |
| 2 | Image tags by digest in deploy, never by tag-name; ECR tag immutability enforced | EKS deploy manifests use `image@sha256:...`; renovate bumps digests via PR | M |
| 3 | Cosign verify in admission controller (Kyverno or Gatekeeper); block unsigned images | Cosign keyless via Fulcio + Rekor; verifying root + Rekor presence | M |
| 4 | Pin base images by digest, not tag; Renovate auto-PRs digest bumps | SBOM diff alerts on base layer changes | L |
| 5 | Lockfiles (package-lock.json, poetry.lock) checked in; CI verifies hashes | OSV scanner, Snyk, Dependabot alerts | M |
| 6 | Pin `uses:` in Actions to commit SHA, not version tag; mirror critical Actions internally | Required PR review on workflow file changes | M |
| 7 | OIDC trust policy scoped to `repo:org/repo:ref:refs/heads/main`; minimum-permission AWS role | Dual-account separation: build account vs deploy account | H |
| 8 | Branch protection: required PR review, status checks, signed commits, no force push | CODEOWNERS for sensitive paths; two-person rule on `.github/` directory | L |
| 9 | Eliminate `curl | sh` in builds; use language-native package managers with hash verification | Network egress allow-list on runners (only registries) | M |
| 10 | PAT replacement: GitHub Apps with fine-grained permissions, short-lived tokens | Secret scanning (push and partner program) | L |
| 11 | SBOM at build time (Syft or equivalent), shipped to artifact store, reviewable in PR | License and CVE gating on SBOM, fail build above threshold | L |

## Residual risk

After mitigations: 0 HIGH, 5 MEDIUM, 11 LOW.

MEDIUMs:
- Maintainer account compromise: accepted with required reviews and CODEOWNERS, plus alerting on first-time admin actions.
- Compromised legitimate dependency (zero-day in trusted lib): accepted because no perfect defense, mitigation is fast SBOM diff and rollback runbook.
- Cosign key leak: accepted by going keyless (Fulcio); residual is Fulcio root compromise which is upstream risk.
- OIDC role drift: accepted with quarterly review of trust policies.
- Force push slipping through: accepted because branch protection plus alerting catches misconfig.

I would not ship without: image-by-digest, signed images, and `pull_request` workflows with no secrets.

## Detections

- Workflow run with secrets on a fork PR: GitHub audit log alert.
- ECR tag mutation: CloudTrail event `PutImage` with `imageTag` overwrite, alert.
- Unsigned image deploy: Kyverno/Gatekeeper deny event paged.
- New `uses:` introduced in workflow: PR check that flags any non-pinned `uses`.
- OIDC token exfil: monitor outbound network from runners; allow-list registries; alert on unknown egress.
- PAT in source: GitHub secret scanning plus internal periodic scan.
- Maintainer first-time push to sensitive paths: alert.

Closing line:
"Software supply chain is where most modern breaches start: SolarWinds, 3CX, Codecov. The threat surface widens every time you add a dependency. The compensating controls are pin everything by digest, sign everything, and verify at admission. The residual risk is bounded by how aggressively you treat your own CI as production. If your CI is less protected than your prod cluster, the prod cluster does not really matter."
