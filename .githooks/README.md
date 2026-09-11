# .githooks

The three git hooks this repository installs through `core.hooksPath`, which move
the secret boundary from continuous integration onto the laptop. On a public
repository a pushed branch is already public, so a scan that only runs after the
push runs too late.

<!-- MANIFEST:.githooks -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `.githooks/**` | active | The three hooks core.hooksPath points at: pre-commit runs gitleaks fail closed, sweeps staged markdown for dash tells, and rebuilds metrics.yaml; commit-msg verifies the commit's author and co-authors are approved identities; pre-push rescans every commit being pushed for both secrets and identity. The identity rule is shared with scripts/repo/check_authorship.sh and the authorship-guard workflow, with the approved list held in config, not in source. |
<!-- /MANIFEST -->

Install them with `git config core.hooksPath .githooks`. `pre-commit` runs
gitleaks fail closed, sweeps staged markdown for dash tells, and rebuilds
`metrics.yaml` when a counted source changes. `commit-msg` verifies the commit's author and co-authors are approved
identities. `pre-push` rescans every commit being pushed for secrets and
identity. The identity rule is shared with `scripts/repo/check_authorship.sh`
and the `authorship-guard` workflow, so the laptop and the pipeline enforce it
identically. The approved list lives in config (a gitignored file locally, the
AUTHORSHIP_ALLOW repository variable in CI), never in source.
