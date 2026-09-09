# Agent_Squire

Four per agent telemetry stubs and one n8n function snippet that tags an
outbound call with the identifier of the agent that made it. The agent itself
lives in `builds/squire/`; this directory exists because the inventory scanners
read it as one of their sources.

<!-- MANIFEST:Agent_Squire -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `Agent_Squire/**` | reference | Four per agent telemetry stubs and one n8n function snippet that tags outbound calls with an agent identifier. |
<!-- /MANIFEST -->

Status is `reference`. `scripts/observers/agents.py`, two inventory sources, the
agent inventory workflow, `CODEOWNERS`, and the labeler all name this path, so
it is live as a scanner input and stale as content. Nothing published depends on
what is inside it: the tree carries zero evidence anchors.
