# .githooks

The two git hooks this repository installs through `core.hooksPath`, which move
the secret boundary from continuous integration onto the laptop. On a public
repository a pushed branch is already public, so a scan that only runs after the
push runs too late.

<!-- MANIFEST:.githooks -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `.githooks/**` | active | The two hooks core.hooksPath points at: pre-commit runs gitleaks fail closed, sweeps staged markdown for dash tells, and rebuilds metrics.yaml; pre-push rescans every local commit not yet on a remote. |
<!-- /MANIFEST -->

Install them with `git config core.hooksPath .githooks`. `pre-commit` runs
gitleaks fail closed, sweeps staged markdown for dash tells, and rebuilds
`metrics.yaml` when a counted source changes. `pre-push` rescans every local
commit that is not yet on a remote.
