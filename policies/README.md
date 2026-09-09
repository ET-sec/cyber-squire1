# policies

Rego policies that Conftest runs over the governance library itself: required
frontmatter, plan of action identifier integrity, and classification. Policy
about the documents, not about the infrastructure.

<!-- MANIFEST:policies -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `policies/grc/**` | active | Three Rego policies over the governance library: required frontmatter, POA and M identifier integrity, and classification. |
<!-- /MANIFEST -->

`.github/workflows/grc-validate.yml` runs Conftest against this directory on
every pull request that touches `docs/grc/`, which is what makes the frontmatter
contract real rather than a convention. Infrastructure policy lives beside the
plan it judges, in each Terraform plane's own `policy/` directory.
