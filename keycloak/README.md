# keycloak

Notes for the identity provider's realm. The template the provider imports on
its first start is tracked beside the compose file, at
`COREDIRECTIVE_ENGINE/CD_VOL_KEYCLOAK_IMPORT/coredirective-realm.json`: realm
settings, the human and agent roles, and the agent service account clients, with
no user record and no secret in it.

<!-- MANIFEST:keycloak -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `keycloak/**` | active | Notes for the identity provider's realm: where the imported template lives and how the agent clients are applied. |
<!-- /MANIFEST -->

The operator user and the edge login client are created through the admin
interface after the import, and their values go to the secrets manager of
record. `scripts/keycloak/apply_agents.py` is the idempotent script that adds the
agent roles and service account clients through the admin interface; it leaves
existing human roles alone.
