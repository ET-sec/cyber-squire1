# scripts

The toolchain: everything a workflow, a hook, or an operator runs. Each subtree
owns one job, and the scripts at this directory's root are the loose ones a
pipeline or an incident calls directly.

<!-- MANIFEST:scripts -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `scripts/**` | active | Operational and CI scripts at the scripts root: audit log shipping and verification, docker bench runs, image signature verification, the facts and artifacts pair, the POA and M sync, the portfolio and views sync, and the alert relay definition. |
| `scripts/build_metrics.py` | active | Generates metrics.yaml by counting the filesystem: detections, workflows, policies, controls, containers, and the governance library. |
| `scripts/conftest-check.sh` | active | Runs conftest over a saved terraform plan using the policies beside it. |
| `scripts/daily-health-digest.sh` | archived | A daily host summary that queried the monitoring API and posted the result to a chat channel. |
| `scripts/git/**` | active | Two shell helpers: start a branch off current main, and open a pull request with a templated body. |
| `scripts/grc/**` | active | The governance toolchain: the inventory scanner and its allow list, the reviewer and its evaluation harness, the OSCAL builder, sanitization, the spend ledger, budget guard, card validation, signature verification, and the corpus MCP server. |
| `scripts/grc/inventory_sources/**` | active | Six sources the inventory scanner reads: agent cards, compose services, MCP servers, n8n workflows, assistant skills, and a Python grep pass. |
| `scripts/keycloak/**` | active | An idempotent script that adds the agent roles, client scopes, and service account clients to the realm through the admin API. |
| `scripts/observers/**` | active | Drift observers: each reads one declared fact and observes the corresponding reality, for containers, workflows, agents, terraform, OPA, governance documents, and playbooks. |
| `scripts/repo/**` | active | The repository hygiene gates built in Phase 21: the manifest checker and its allow list, the review register evaluator, the directory README generator, and the sweep that runs every mechanical gate behind one command. |
| `scripts/repo/gen_folder_readmes.py` | active | Generates the contents table in every top-level directory README from this manifest, replacing only what sits between the MANIFEST markers. |
| `scripts/repo/manifest_check.py` | active | The gate behind this manifest: it diffs the rows against git ls-files and fails on a tracked path with no row, a row matching nothing, or a review date that has passed. |
| `scripts/repo/repo_sweep.py` | active | Runs every mechanical gate in one command and prints only failures; the repo-sweep skill in the operator's assistant directory is a wrapper over this file and is not tracked, because that directory is gitignored and logic there could never be reviewed, tested, or run by CI. |
| `scripts/site/**` | active | The portfolio toolchain: render, flow and node checks, an overflow probe, and the anchor remapper. |
| `scripts/site/check_public.py` | active | The public surface gate: operational security patterns, price tier language, writing tells, and design tells, over the site and, with --repo, over this repository's tracked text. |
<!-- /MANIFEST -->

`scripts/build_metrics.py` is the single producer of every published number, and
`docs/MASTER_SYNC_ARCHITECTURE.md` explains the marker contract the sync scripts
depend on. `scripts/requirements.txt` pins what the Python entries need.
