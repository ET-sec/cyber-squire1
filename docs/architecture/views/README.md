# Architecture views

Seven sanitized views of the CoreDirective reference platform, drawn as the full reference design. Public: no addresses, ports, hostnames, account IDs, regions, bucket names, or image versions.

| slug | what it shows | source |
|---|---|---|
| topology | one hardened host, three trust segments, every request, AI, audit, and change path | `topology.html`, hand-authored |
| multi-cloud | edge on Cloudflare, runtime on Oracle, security plane on AWS, what crosses, what a lost account reaches | `gen_multi-cloud.py` |
| threat-model | six attacker positions, the wall that meets each, the residual | `gen_threat-model.py` |
| identity-access | four privilege tiers, every credential with its lifetime, the "if stolen" rail | `gen_identity-access.py` |
| ai-trust | five models, three trust levels, every crossing out of the host and what stands in front of it | `gen_ai-trust.py` |
| control-layers | seven barrier layers with NIST 800-53 Rev 5 chips per layer | `gen_control-layers.py` |
| authorization-boundary | the boundary, the inherited controls, every crossing with its control | `gen_authorization-boundary.py` |

## Pipeline

```
python3 docs/architecture/views/render_views.py      # generators write <slug>.html beside themselves
python3 scripts/sync_views.py --check               # exit 1 on drift against ~/portfolio (or --portfolio PATH)
python3 scripts/sync_views.py --apply               # writes ~/portfolio/views/<slug>.html and the <!-- VIEW:slug --> blocks in index.html
```

`views.yaml` is the manifest (slug, title, generator, section). `.github/workflows/portfolio-sync.yml` runs the renderer, `scripts/sync_portfolio.py` (numbers from `metrics.yaml`), and `sync_views.py --check` against ET-sec/portfolio main on every PR and push.

Rules for edits: change the data lists in the generator, never the rendered HTML; keep the design grammar in the topology (fonts, palette, node and arrow style); no ports, IPs, hostnames, or versions anywhere in a view; the drawings show the reference design and the site captions carry live state.

## Node tables (clickable boxes)

`nodes/<slug>.yaml` makes the boxes on a view clickable. One entry per box, keyed by the exact label text on the drawing: what the box is (one sentence), the NIST 800-53 controls it carries, its status today (`live`, `partial`, or `designed`) with one honest sentence of why, and evidence links as `{label, path, line}` into this repo. `sync_views.py` wraps each matching rect and label in a focusable group, attaches the SSP row (name, status, line number) to every control at sync time, and emits the JSON the panel reads; the panel itself is one CSS block and one script that the sync writes into both the standalone page and `index.html` between the `NODES:css` and `NODES:js` markers.

The sync refuses to write when a control id has no row in SSP section 5, an evidence path is not tracked on main, a label is not found exactly once in the SVG, or a status is outside the three values. The `solidify` field is a private cross-reference and never reaches the page. Today only `topology.yaml` exists; `scripts/site/nodecheck_portfolio.mjs` is the QC for it (31 boxes, open on click and Enter, close on Escape and outside click, focus returns, no navigation, no console errors, at 1440 and 390 on the page and the standalone).

`scripts/site/check_public.py` is the mechanical gate on the published files: OPSEC patterns, writing and design tells, every control id on the page against SSP section 5, every cited repo path against `git ls-files`, and (`--links`) every external href. It runs in `portfolio-sync.yml`; the link check is advisory there.
