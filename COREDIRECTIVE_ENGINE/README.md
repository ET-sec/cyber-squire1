# COREDIRECTIVE_ENGINE

The Docker Compose definitions for the platform: the full nineteen service
design, and the smaller file that describes what actually runs on the instance
today. Two files rather than one, so neither has to lie about the difference.

<!-- MANIFEST:COREDIRECTIVE_ENGINE -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `COREDIRECTIVE_ENGINE/README.md` | active | The directory README for COREDIRECTIVE_ENGINE/, whose contents block is generated from this manifest. |
| `COREDIRECTIVE_ENGINE/docker-compose.oci-core.yaml` | active | The definition of what actually runs on the instance today: the database, the automation service, and the tunnel. |
| `COREDIRECTIVE_ENGINE/docker-compose.yaml` | active | The full nineteen service stack definition: databases, orchestration, identity, secrets, inference, observability, and the runtime detection agents. |
<!-- /MANIFEST -->

`docs/architecture/STACK_OVERVIEW.md` explains which services are live, which
are waiting on the ARM rebuild, and what the memory ceiling has to do with it.
Image digests here are pinned, verified by `scripts/verify_image_signatures.py`
against `.github/image-signers.json`, and updated under the tiered rules in
`renovate.json`.
