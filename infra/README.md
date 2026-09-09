# infra

Seven Conftest policies written to gate the Compose file at pull request time.
Nothing calls them, so the directory is archived rather than live.

<!-- MANIFEST:infra -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `infra/**` | archived | Seven conftest policies for the compose file, covering privileged containers, resource limits, image tags, registries, host networking, healthchecks, and read only root filesystems, plus their readme and the archived marker. |
<!-- /MANIFEST -->

`infra/ARCHIVED.md` records when it stopped being called, why, and what would
bring it back. Active policy enforcement lives in `policies/grc/` and in
`terraform/cd-oci-infrastructure/policy/`. The policies are kept because they
are a working reference for the OPA work, and removing them would need a private
copy for no gain.
