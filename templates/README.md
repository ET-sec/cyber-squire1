# templates

One Jinja2 template, rendered from the facts file into a published profile
section. Kept but not on the live path.

<!-- MANIFEST:templates -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `templates/**` | reference | One Jinja2 template rendered from the facts file into a published profile section. |
<!-- /MANIFEST -->

Status is `reference`: a live caller exists, `scripts/render-artifacts.py`,
whose allow list names this template explicitly, but no workflow runs that
script. The template seeds work rather than doing any.
