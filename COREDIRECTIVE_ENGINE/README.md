# COREDIRECTIVE_ENGINE

The Docker Compose definitions for the platform: the full nineteen service
design, and the smaller file that describes what actually runs on the instance
today. Two files rather than one, so neither has to lie about the difference.

<!-- MANIFEST:COREDIRECTIVE_ENGINE -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `COREDIRECTIVE_ENGINE/CD_VOL_DATADOG/conf.d/**` | active | The monitoring agent's check configurations, mounted over the image's drop-in path: today the host authentication log tail. |
| `COREDIRECTIVE_ENGINE/CD_VOL_FALCO/**` | active | The kernel sensor's configuration overlay and the platform's own detection rules. |
| `COREDIRECTIVE_ENGINE/CD_VOL_KEYCLOAK_IMPORT/coredirective-realm.json` | active | The realm template the identity provider imports on its first start: realm settings, the human and agent roles, and the service account clients. |
| `COREDIRECTIVE_ENGINE/CD_VOL_TELEPORT/config/roles.yaml` | active | The two gateway roles: the requestable administrative role and the operator role that may request it. |
| `COREDIRECTIVE_ENGINE/CD_VOL_TELEPORT/config/teleport.yaml` | active | The access gateway's configuration: auth, proxy and node in one process, local authentication with a second factor, session recording at the node. |
| `COREDIRECTIVE_ENGINE/CD_VOL_TELEPORT_EVENTS/teleport-event-handler.toml` | active | The event handler's forwarder table: where the audit stream goes, over which certificates, and which gateway it reads from. |
| `COREDIRECTIVE_ENGINE/CD_VOL_VAULT/config/vault.hcl` | active | The secrets manager's single server configuration: file storage, the plain listener with its written TLS decision, the cloud KMS seal through the instance principal, and the lease bounds. |
| `COREDIRECTIVE_ENGINE/CD_VOL_VECTOR/vector.yaml` | active | The audit log shipper's pipeline: a mutual TLS listener for the access gateway's event handler, a path route for audit and session streams, the SIEM sink with a bounded memory buffer, and the metrics exporter the health scrape reads. |
| `COREDIRECTIVE_ENGINE/README.md` | active | The directory README for COREDIRECTIVE_ENGINE/, whose contents block is generated from this manifest. |
| `COREDIRECTIVE_ENGINE/docker-compose.oci-core.yaml` | active | The definition of what runs on the instance: the database, the orchestration engine, the tunnel, the model and speech servers, the kernel sensor and its router, the monitoring agent, the secrets manager, the identity provider, the access gateway, its event handler, and the audit log shipper. |
| `COREDIRECTIVE_ENGINE/docker-compose.yaml` | active | The full nineteen service stack definition: databases, orchestration, identity, secrets, inference, observability, and the runtime detection agents. |
<!-- /MANIFEST -->

`docs/architecture/STACK_OVERVIEW.md` explains what each service does, how the
memory ceiling shapes the caps, and which file is the definition of record.
Image digests here are pinned, verified by `scripts/verify_image_signatures.py`
against `.github/image-signers.json`, and updated under the tiered rules in
`renovate.json`.
