# .github

Everything GitHub reads: the Actions workflows that gate a pull request and scan
a merge, the composite action that trades the job's token for a cloud session,
the review and issue policy, and the image signing configuration. This is the
enforcement layer behind every control the governance library claims as
automated.

<!-- MANIFEST:.github -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `.github/**` | active | Repository configuration that is not a workflow: the labeler, the pull request template, and the assistant instructions. |
| `.github/CODEOWNERS` | active | Who must review each part of the tree. |
| `.github/ISSUE_TEMPLATE/**` | active | Issue forms for bug reports, feature requests, and ground truth audit findings, plus the chooser config. |
| `.github/actions/**` | active | The composite action that exchanges the job's GitHub OIDC token for a cloud session, so no cloud key is stored in the repository. |
| `.github/image-signers.json` | active | Per publisher signing policy for every image the compose files pin: keyless, key, or explicitly unsigned with a note. |
| `.github/keys/**` | active | The one publisher signing key pinned by digest policy, for a publisher that signs with a key rather than keylessly. |
| `.github/workflows/*.yml` | active | The GitHub Actions workflows: pull request gates, merge scans, nightly drift, agent signing and verification, and the portfolio publish. |
| `.github/workflows/drift-check.yml` | active | The nightly job that plans against the live infrastructure and alerts on any difference from the committed state. |
| `.github/workflows/grc-validate.yml` | active | Frontmatter, POA and M identifier integrity, and classification policy checks over the governance library, run with conftest against policies/grc/. |
| `.github/workflows/image-smoke.yml` | active | A pull time smoke test that the pinned container images still resolve and start. |
| `.github/workflows/security.yml` | active | The merge pipeline: Trivy, Semgrep, Gitleaks, cosign image verification, SBOM, and the POA and M sync. |
| `.github/workflows/terraform-main.yml` | active | The real plan and conftest run on main after every merge, with apply held behind the production environment. |
| `.github/workflows/terraform-pr.yml` | active | The credential free pull request pipeline for infrastructure changes: fmt, validate, Checkov, the OPA fixture self test, and a plan comment. |
<!-- /MANIFEST -->

`docs/WORKFLOW_GUIDE.md` maps a red check back to the thing that has to be
fixed.
