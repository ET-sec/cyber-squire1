# builds

Application source. Squire, the SOC analyst agent, is the one thing this
platform builds and the only subtree here that is tracked.

<!-- MANIFEST:builds -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `builds/squire/**` | active | The Squire agent service: packaging, container definition, dependency manifest, and the readme that explains its graph. |
| `builds/squire/config/actions.yml` | active | The action allow list the agent is bound to, currently recommend only. |
| `builds/squire/docker/nemo_config/**` | active | The guardrail configuration: rails definitions, prompts, and the container that serves them. |
| `builds/squire/src/**` | active | The application: the FastAPI surface, the analysis graph and its nodes, the guardrail clients, retrieval, persistence, and the cost ceiling. |
| `builds/squire/tests/**` | active | The Squire suite: unit tests, graph integration, guardrail red team cases, and the evaluation harness. |
<!-- /MANIFEST -->

`.gitignore:163` ignores `builds/*` and re-includes exactly two paths,
`builds/squire/` and this file. Other directories under `builds/` hold client
work, take homes, and content tooling, and they stay private by default rather
than by omission. Two of them, `grc_librarian` and `ir-assistant`, are on disk,
untracked, and recorded as dated known gaps in
`scripts/repo/manifest_allow_list.yaml` by owner decision as of 2026-09-09.
