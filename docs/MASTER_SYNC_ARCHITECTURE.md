# Master Sync Architecture

**Why this exists.** Three public surfaces (this repo, the resume PDF, and the portfolio website) were drifting against each other on the same facts, GRC document count, NIST controls cited, POA&M findings, container count, deployed model. Each surface was edited by hand. Errors compounded. By 2026-06-25 the same fact appeared as three different numbers across surfaces.

This document describes the system that makes drift impossible going forward. It pairs **continuous local sync** (pre-commit hooks) with **periodic deep verification** (the GTA skill).

---

## The four artifacts

| Artifact | Lives at | Authoritative for |
|---|---|---|
| **Filesystem** | the repo on disk | every count derivable by walking files |
| **`metrics.yaml`** | repo root | canonical numeric facts, derived from filesystem |
| **`REPO_MAP.yaml`** | repo root | every file path, type, last-modified, regen rules |
| **CLAUDE.md / owner approval** | repo + global | values not derivable from disk (containers public count, n8n workflow count) |

Filesystem wins ties. `metrics.yaml` and `REPO_MAP.yaml` are derived, not hand-edited. CLAUDE.md and the `OWNER_APPROVED` block of `build_metrics.py` is where humans pin values that the filesystem cannot answer (e.g. droplet-side state).

---

## The flow

```
                                              EDITS A FILE
                                                    │
                                                    ▼
                                          ┌───────────────────┐
                                          │  git add <file>   │
                                          └───────────────────┘
                                                    │
                                                    ▼
                                       ┌─────────────────────────┐
                                       │  pre-commit hook fires  │
                                       │  .githooks/pre-commit   │
                                       └─────────────────────────┘
                                                    │
                       ┌────────────────────────────┼────────────────────────────┐
                       ▼                            ▼                            ▼
            ┌──────────────────┐     ┌──────────────────────┐     ┌────────────────────────┐
            │ AI-tells sweep   │     │ build_metrics.py     │     │ build_manifest.py      │
            │  (em dash, en)   │     │  writes metrics.yaml │     │  writes REPO_MAP.yaml  │
            └──────────────────┘     └──────────────────────┘     └────────────────────────┘
                       │                            │                            │
                       │                            └────────────┬───────────────┘
                       │                                         │
                       │                                         ▼
                       │                              git add metrics.yaml
                       │                              git add REPO_MAP.yaml
                       │
                       ▼
                   COMMIT
                       │
                       ▼
                  pushed to origin
                       │
   ┌───────────────────┴───────────────────┐
   │                                       │
   ▼                                       ▼
GitHub                                Portfolio sync (manual or PR-bot)
README, docs/grc/,                    cyber-squire1/metrics.yaml
terraform/, etc.                                 │
already in sync                                  ▼
                                       scripts/sync_portfolio.py
                                                 │
                                                 ▼
                                       ~/portfolio/index.html
                                       <!-- METRIC:key.path -->N<!-- /METRIC -->
                                                 │
                                                 ▼
                                       PR to ET-sec/portfolio
                                                 │
                                                 ▼
                                       et-sec.github.io/portfolio
```

---

## On every commit (continuous, free)

`.githooks/pre-commit` runs two jobs.

**Job 1, AI-tells sweep**
Runs against staged `.md` files. Hard-blocks em dashes, en dashes, double-hyphen prose. Warns on AI-tell phrases and "Not X. Y." juxtaposition.

**Job 2, Metric rebuild**
Triggered when staged changes touch any of:

- `docs/grc/**`
- `terraform/**`
- `detections/**`
- `.github/workflows/**`
- `COREDIRECTIVE_ENGINE/docker-compose.yaml`

When triggered the hook reruns `scripts/build_metrics.py` and `~/.claude/skills/gta/scripts/build_manifest.py`. Both write to repo root. If the regenerated file changed, it is staged into the same commit. If either script fails the commit is blocked.

Net effect: every commit that touches a tracked source path arrives at GitHub with `metrics.yaml` and `REPO_MAP.yaml` already in sync. No human intervention required, no possibility of forgetting.

---

## Periodically (deep verification)

The GTA skill at `~/.claude/skills/gta/` runs the full 11-phase audit on demand: `/gta`, `/gta --all`, or `/gta --website-sync`. Run it when something feels off, before any public push, or on a weekly cadence.

GTA goes further than the hook because it:

1. Re-derives every claim by re-reading the source docs, not the metric file.
2. Cross-references against external authority (NIST 800-53 Rev 5 catalog, OWASP tops 10).
3. Spawns 4 to 6 parallel persona agents to audit each doc cold.
4. Generates `_CONTRADICTIONS.md` when sidecars disagree.
5. Phase 11 runs the three-source diff: `metrics.yaml` versus portfolio HTML versus resume PDF text.

The hook is your daily seatbelt. GTA is the periodic mechanical inspection.

---

## How surfaces consume `metrics.yaml`

| Surface | Mechanism | Path |
|---|---|---|
| `README.md` (cyber-squire1) | manual reference, GTA Phase 11 flags drift | numbers should match `metrics.yaml` exactly |
| Portfolio HTML | `scripts/sync_portfolio.py` rewrites HTML markers | `~/portfolio/index.html` |
| Resume PDF | source resume reads `metrics.yaml` at build time (future) | flagship in `~/Library/Mobile Documents/com~apple~CloudDocs/` |
| IR playbooks (`docs/grc/PLAYBOOK_*.md`) | reference numbers should match `metrics.yaml` (manual today, GTA-enforced) | `docs/grc/PLAYBOOK_*.md` |
| Architecture diagrams (`docs/grc/diagrams/*.png`) | `gen_*.py` scripts read source docs (e.g. POA&M for `gen_poam_summary.py`) and regen the PNG | `docs/grc/diagrams/gen_*.py` |
| LinkedIn / external posts | manual reference | n/a |

### The portfolio marker pattern

In `~/portfolio/index.html`, wrap any number that comes from `metrics.yaml`:

```html
<!-- METRIC:grc.total_documents -->57<!-- /METRIC -->
<!-- METRIC:grc.nist_800_53_controls_cited -->133<!-- /METRIC -->
<!-- METRIC:grc.poam_findings_total -->42<!-- /METRIC -->
<!-- METRIC:stack.containers_public -->20<!-- /METRIC -->
<!-- METRIC:detection.sigma_rules -->17<!-- /METRIC -->
<!-- METRIC:infra.datadog_monitors -->10<!-- /METRIC -->
```

The dotted key matches the key path inside `metrics.yaml`. Markers persist; only the value between them is rewritten. Idempotent re-runs.

After wrapping the values once, sync becomes:

```bash
# from cyber-squire-ops repo root
python3 scripts/sync_portfolio.py            # dry-run, prints drift
python3 scripts/sync_portfolio.py --apply    # rewrite portfolio HTML
cd ~/portfolio && git add . && git commit -m "chore: sync portfolio metrics from cyber-squire1"
```

---

## What `metrics.yaml` covers today

Generated by `scripts/build_metrics.py`. Current canonical values (run 2026-06-25):

```yaml
stack:
  containers_public: 20            # owner-approved (CLAUDE.md)
  workflows_n8n_active: 14         # owner-confirmed (off-disk)
  workflows_github_actions: 13     # derived: ls .github/workflows/

grc:
  total_documents: 57              # ls docs/grc/*.md minus README.md
  total_files_including_index: 58
  nist_800_53_controls_cited: 133  # unique base controls in SSP_*.md
  policies: 10                     # POLICY_*.md
  ir_playbooks: 5                  # PLAYBOOK_*.md
  threat_model_docs: 6
  tabletop_exercises: 2
  executive_summaries: 3
  poam_findings_total: 42          # POAM-0## + POAM-P17-##
  poam_findings_base_cis_checkov_ra: 27
  poam_findings_squire_ai: 15
  poam_findings_open: 20
  poam_findings_closed: 7
  poam_findings_accepted_risk: 15

ai:
  openclaw_model: "Claude Fable 5"
  openclaw_model_id: "claude-fable-5"
  ollama_model: "Qwen 3 8B"
  whisper_engine: "faster-whisper"

detection:
  sigma_rules: 17

infra:
  terraform_files: 20
  opa_policies: 8
  datadog_monitors: 10
  datadog_dashboards: 2

contact:
  email: "etigoue@tigouetheory.com"
  github: "ET-sec"
  portfolio_url: "https://et-sec.github.io/portfolio/"
  linkedin: "https://www.linkedin.com/in/emmanuel-tigoue"
```

---

## What lives where

| Asset | Path | Purpose |
|---|---|---|
| Derive script | `scripts/build_metrics.py` | walks filesystem, emits `metrics.yaml` |
| Canonical numbers | `metrics.yaml` | single source for every public count |
| Portfolio sync | `scripts/sync_portfolio.py` | rewrites HTML markers from metrics |
| Pre-commit hook | `.githooks/pre-commit` | runs both jobs on every commit |
| File inventory | `REPO_MAP.yaml` | path/type/audit-status for every file |
| Manifest scanner | `~/.claude/skills/gta/scripts/build_manifest.py` | regenerates REPO_MAP.yaml |
| Asset regen | `~/.claude/skills/gta/scripts/regenerate_assets.py` | re-runs `gen_*.py` diagram scripts |
| Diagram generators | `docs/grc/diagrams/gen_*.py` | regen PNGs when source data changes |
| GTA skill manifest | `~/.claude/skills/gta/SKILL.md` | the 11-phase periodic audit |
| Owner overrides | `OWNER_APPROVED` block in `build_metrics.py` | values not on disk |

---

## Adding a new tracked metric

1. Edit `scripts/build_metrics.py`. Add a function or extend an existing `compute_*` to count the new thing from the filesystem. If the value is not derivable from disk, add it to `OWNER_APPROVED` and explain why in a comment.
2. Run `python3 scripts/build_metrics.py`. Check the new key appears in `metrics.yaml`.
3. If the value should appear on the portfolio, wrap that number in HTML:

   ```html
   <!-- METRIC:section.key -->VALUE<!-- /METRIC -->
   ```

   Run `python3 scripts/sync_portfolio.py --apply` from `cyber-squire-ops` root.
4. Commit. The hook runs automatically and verifies sync.

---

## Adding a new tracked diagram

PNG diagrams under `docs/grc/diagrams/` should have a sibling `gen_*.py` so they regenerate when source data changes. Today four diagrams have generators:

- `gen_poam_summary.py`, reads `POAM_PLAN_OF_ACTION.md`
- `gen_risk_summary_dashboard.py`, reads risk register
- `gen_risk_heat_map.py`, reads risk register
- `gen_control_coverage.py`, reads SSP

To add a new one:

1. Write `gen_<name>.py` that reads its source markdown directly and writes the PNG.
2. Add the regen rule to `REPO_MAP.yaml` via the GTA manifest scanner: edit the source doc's entry to include `regenerate_when_changed: [docs/grc/diagrams/<name>.png]`.
3. The hook will not run the regen automatically (it would slow every commit). Instead `regenerate_assets.py` is invoked by GTA Phase 9 or run manually with `python3 ~/.claude/skills/gta/scripts/regenerate_assets.py`.

---

## What this system does NOT do

Listed honestly so you know the boundary:

- **It does not edit the resume PDF.** Resume rebuild stays manual today. The intent is that the resume source (LaTeX / docx / Pages) should read `metrics.yaml` at build time, but that integration is not yet wired. Until then, GTA Phase 11 flags resume drift but does not fix it.
- **It does not push to the portfolio repo automatically.** `sync_portfolio.py` only writes locally. Portfolio commit and push are still manual or PR-bot driven.
- **It does not verify diagram content.** It verifies PNG existence and regen on source change. The diagrams themselves are not audited (that is a GTA Phase 9 manual review).
- **It does not check Notion, LinkedIn, Skool, or Gumroad.** External SaaS surfaces are out of scope. GTA may grow checks against these in a future v1.1.

---

## Recovery: if `metrics.yaml` is wrong

Either the derive script has a bug or an `OWNER_APPROVED` value drifted.

1. Run `python3 scripts/build_metrics.py --json` and check each computed number against the actual files. The script prints which path it counted from.
2. If a count is wrong: fix the bug in `build_metrics.py`. Add a test if necessary.
3. If an owner-approved value drifted: update the `OWNER_APPROVED` block and note the date in the comment.
4. Rerun `python3 scripts/build_metrics.py`. Verify. Commit.

The `--check` flag exits non-zero if the on-disk `metrics.yaml` is stale relative to a fresh derive. CI uses this:

```bash
python3 scripts/build_metrics.py --check
```

---

## Status as of 2026-06-25

| Component | Status |
|---|---|
| `scripts/build_metrics.py` | done |
| `metrics.yaml` (seeded) | done |
| `scripts/sync_portfolio.py` | done (dry-run-tested) |
| `.githooks/pre-commit` extension | done |
| `docs/MASTER_SYNC_ARCHITECTURE.md` | this file |
| GTA SKILL.md wiring of `metrics.yaml` | done (Phase 0 and Phase 11) |
| Portfolio HTML marker injection | pending, first sync PR |
| Resume source build reads metrics | pending, future work |
| Diagram gen_*.py for remaining diagrams | pending, only 4 of 18 PNGs have generators today |
| IR playbook reference auto-check | pending, GTA Phase 2 audit job |
