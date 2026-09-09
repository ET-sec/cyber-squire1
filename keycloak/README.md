# keycloak

The sanitized realm export for the identity tier: clients, roles, and scopes.
One file, kept in the repository so the identity design is reviewable before the
service is running.

<!-- MANIFEST:keycloak -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `keycloak/**` | active | The realm export: clients, roles, and scopes for the identity tier. |
<!-- /MANIFEST -->

Three evidence anchors on the published architecture views cite this file, so
removing it breaks the publish. What is inside it depends on the Phase 24
identity tier work. `scripts/keycloak/apply_agents.py` is the idempotent script
that adds the agent roles and service account clients through the admin
interface, and it leaves existing human roles alone.
