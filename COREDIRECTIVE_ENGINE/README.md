# COREDIRECTIVE_ENGINE

The Docker Compose definitions for the platform: the full nineteen service
design, and the smaller file that describes what actually runs on the instance
today. Two files rather than one, so neither has to lie about the difference.

<!-- MANIFEST:COREDIRECTIVE_ENGINE -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `COREDIRECTIVE_ENGINE/CD_VOL_FLUENTD/Dockerfile` | active | The build context for the Fluentd log shipper, one of the three Tier 0 images the stack builds locally rather than pulling. |
| `COREDIRECTIVE_ENGINE/README.md` | active | The directory README for COREDIRECTIVE_ENGINE/, whose contents block is generated from this manifest. |
| `COREDIRECTIVE_ENGINE/docker-compose.oci-core.yaml` | active | The definition of what runs on the instance: the database, the orchestration engine, the tunnel, the model and speech servers, the kernel sensor and its router, and the monitoring agent. |
| `COREDIRECTIVE_ENGINE/docker-compose.yaml` | active | The full nineteen service stack definition: databases, orchestration, identity, secrets, inference, observability, and the runtime detection agents. |
<!-- /MANIFEST -->

`docs/architecture/STACK_OVERVIEW.md` explains what each service does, how the
memory ceiling shapes the caps, and which file is the definition of record.
Image digests here are pinned, verified by `scripts/verify_image_signatures.py`
against `.github/image-signers.json`, and updated under the tiered rules in
`renovate.json`.
