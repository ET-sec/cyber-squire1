# Portfolio + Resume Change Management Runbook

Operational procedures for updating, rolling back, and verifying changes to the public portfolio (`ET-sec/portfolio`) and the four resume variants generated from the manifest (`CoreDirective/career/resume-builder/`).

Created 2026-06-12 after the portfolio + resume rebuild. The flagship and 3 variants use canonical names (no `v30`, no `FINAL`, no version suffix) on every surface. Update this doc when the procedure changes, not when content changes.

---

## 1. Source of truth map

| Asset | Path | Editing |
|---|---|---|
| Resume manifest | `CoreDirective/career/resume-builder/resume_data.json` | Edit JSON, regenerate |
| Variant overlays | `CoreDirective/career/resume-builder/variants/*.json` | Edit JSON, regenerate |
| Renderer | `CoreDirective/career/resume-builder/resume_generator.py` | Edit Python, regenerate |
| Portfolio site | `~/portfolio/index.html` | Edit HTML, commit, push |
| Portfolio PDF | `~/portfolio/Emmanuel_Tigoue_AISecurity_Engineer.pdf` | Replace from rebuilt PDF |
| Public site URL | https://et-sec.github.io/portfolio/ | Auto-deployed by GitHub Pages |

---

## 2. Editing the resume

### Routine update (numbers, dates, bullets)

1. Edit `resume_data.json` (or a variant overlay if the change is variant-specific).
2. Run from `CoreDirective/career/resume-builder/`:
   ```
   python3 resume_generator.py --base resume_data.json --output output/Emmanuel_Tigoue_AISecurity_Engineer.docx
   python3 resume_generator.py --base resume_data.json --variant variants/cloud_security_engineer.json --output output/Emmanuel_Tigoue_Cloud_Security_Engineer.docx
   python3 resume_generator.py --base resume_data.json --variant variants/application_security_engineer.json --output output/Emmanuel_Tigoue_Application_Security_Engineer.docx
   python3 resume_generator.py --base resume_data.json --variant variants/grc_analyst.json --output output/Emmanuel_Tigoue_GRC_Analyst.docx
   ```
3. Convert each DOCX to PDF:
   ```
   cd output && for f in Emmanuel_Tigoue_*.docx; do soffice --headless --convert-to pdf "$f"; done
   ```
4. Verify each PDF is exactly 1 page:
   ```
   python3 -c "from pypdf import PdfReader; print(len(PdfReader('Emmanuel_Tigoue_AISecurity_Engineer.pdf').pages))"
   ```
5. Open in Word to visually confirm the layout in Word's renderer.
6. If Word shows 2 pages but LibreOffice shows 1, Emmanuel must hand-tighten in Word. Word renders looser than LibreOffice.

### Variant fit-tightening (per JD apply)

The base manifest produces a clean flagship. Variants reorder bullets and swap skills lists, but may spill in Word.

When applying to a Cloud / AppSec / GRC role, the typical hand-tightening pass in Word:
1. Open the variant DOCX.
2. If 2 pages, lower body font to 10.5pt across the doc.
3. Trim one or two long bullets if still spilling.
4. Save as DOCX. Export as PDF.

### Surfaces to update after a resume change

Canonical filename pattern for every surface: `Emmanuel_Tigoue_{AISecurity_Engineer,Application_Security_Engineer,Cloud_Security_Engineer,GRC_Analyst}.{docx,pdf}`. No version suffix. Overwrite in place.

1. iCloud root: `~/Library/Mobile Documents/com~apple~CloudDocs/Emmanuel_Tigoue_*.{docx,pdf}` (4 variants × 2 formats = 8 files). The `Resumes/` subfolder holds `resume variations/` historical archives only — do not put live resumes there.
2. Google Drive root: `~/Library/CloudStorage/GoogleDrive-etigoue@tigouetheory.com/My Drive/Emmanuel_Tigoue_*.{docx,pdf}` (same 8 files).
3. Laptop output: `CoreDirective/career/resume-builder/output/Emmanuel_Tigoue_*.{docx,pdf}` (the build target; canonical names match iCloud and Drive).
4. cyber-squire-mirror: auto-synced via post-commit hook (private GitHub mirror).
5. Google Doc: `1WupZKdplsE10WsObLuSaiNjLCnAyBbEfs4jzjsa2pBA` (refresh via `gws drive files update --params '{"fileId":"..."}' --upload <docx>`).
6. Portfolio: copy flagship PDF to `~/portfolio/Emmanuel_Tigoue_AISecurity_Engineer.pdf`, commit, push.

After overwriting, verify SHA match across iCloud / Drive / laptop with `shasum` — that's the single fastest correctness check.

---

## 3. Editing the portfolio

### Local workflow

1. Edit `~/portfolio/index.html`.
2. Validate HTML: `python3 -c "from html.parser import HTMLParser; HTMLParser().feed(open('index.html').read()); print('HTML OK')"`
3. Drift sweep: grep for any stale numbers or banned patterns (em dashes, exposed container names, IPs, ports).
4. Stage only the files you changed: `git add index.html` (not `git add .` — the repo has uncommitted WIP that should not bundle with your edit).
5. Commit with a descriptive message.
6. Push to main.
7. GitHub Pages auto-builds in 60 to 120 seconds.

### Verification after push

1. Check Pages build status: `gh api repos/ET-sec/portfolio/pages/builds/latest --jq '.status, .commit, .created_at'`
2. Wait until status is `built` and commit matches your push.
3. Curl the live URL and verify expected content: `curl -s https://et-sec.github.io/portfolio/ | grep <new-content>`
4. Hard refresh in browser (Cmd+Shift+R) to clear local cache.
5. If the change is layout-related, use Playwright MCP to measure rendered heights and confirm visual evenness.

### Adding a new cert card

1. Find the `<div class="cert-grid">` block in index.html.
2. Copy an existing card template, change href, h3, cert-meta lines, cert-note.
3. For VERIFIED state: green border, link to specific Credly badge URL, cert-note "Click to verify on Credly".
4. For IN PROGRESS state: gold border (`cert-card-blue` class), link to exam page or learning resource, cert-note "Click to view exam details".
5. Two cert-meta lines max per card (CISSP description was trimmed to prevent wrap that broke grid evenness).

---

## 4. Rollback procedures

### Portfolio rollback (single commit)

```
cd ~/portfolio
git log --oneline -5                # find the bad commit
git revert <bad-commit-sha>          # creates a new commit reversing the change
git push origin main                 # Pages rebuilds with the reverted content
```

Do NOT `git reset --hard` and force-push on portfolio main. Pages would briefly serve stale content during the force-push window.

### Portfolio rollback (multi-commit)

If multiple commits need reversing in one go:
```
cd ~/portfolio
git revert --no-commit <oldest-bad>..<newest-bad>
git commit -m "revert: ..."
git push origin main
```

### Resume manifest rollback

```
cd ~/cyber-squire-ops
git log -- CoreDirective/career/resume-builder/resume_data.json
git checkout <good-commit> -- CoreDirective/career/resume-builder/resume_data.json
```

Then regenerate all four resumes per section 2.

### Resume DOCX rollback (when hand-tightening is lost)

The hand-tightened DOCX lives at `CoreDirective/career/resume-builder/output/Emmanuel_Tigoue_AISecurity_Engineer.docx`. It is NOT committed to git (the output dir was gitignored historically). Identical copies (verified by SHA) exist in:

1. iCloud: `~/Library/Mobile Documents/com~apple~CloudDocs/Emmanuel_Tigoue_AISecurity_Engineer.docx`
2. Drive root: `~/Library/CloudStorage/GoogleDrive-etigoue@tigouetheory.com/My Drive/Emmanuel_Tigoue_AISecurity_Engineer.docx`

To restore: copy from either backup to the output dir. The local DOCX is the canonical hand-tightened version.

### Live OpenClaw gateway token rotation (emergency)

If a token leaks again:
```
NEW_TOKEN=$(openssl rand -base64 32 | tr '+/' '-_' | tr -d '=')
ssh cd-alpha "cp /root/moltbot/config-dir/openclaw.json /root/moltbot/config-dir/openclaw.json.bak-\$(date +%Y%m%d-%H%M%S)"
ssh cd-alpha "sed -i.bak 's/\"token\": \"[^\"]*\"/\"token\": \"$NEW_TOKEN\"/' /root/moltbot/config-dir/openclaw.json"
ssh cd-alpha "docker restart openclaw-gateway"
doppler secrets set OPENCLAW_GATEWAY_TOKEN="$NEW_TOKEN" --project coredirective-engine --config prd
# scrub the leaked file and commit a fix
```

Then verify old token returns 401, new returns 400 or 200.

---

## 5. Change management policy

### Before any public-facing change

1. Numbers traced to ground truth: GRC docs count via `ls docs/grc/*.md`, services via compose, controls via SSP, terraform via `ls *.tf`.
2. No exposed container names, IPs, ports, hostnames in HTML, code blocks, or alt text.
3. No em dashes in user-visible prose (en dashes for date ranges OK).
4. No AI tells: leverages, utilizes, pivot, aspiring, transitioning, juxtaposition.
5. Texaco location is always "Atlanta, GA". CoreDirective location is always "Atlanta, GA".
6. Employment titles in resume experience blocks stay fixed across variants.
7. Resume PDFs must render as exactly 1 page in both LibreOffice and Word.

### When ground truth and resume claim diverge

Update both manifest and surface together. Do not leave resume claiming X while ground truth shows Y. The one current exception is n8n workflow count: resume says 14 per Emmanuel's explicit directive, droplet has 6. Treat as known divergence.

### Multi-agent audits

When the user asks "is everything matching" or "did we miss anything," dispatch parallel `Explore` subagents with specific scope per agent. Don't run a single agent over the whole codebase. Format used 2026-06-12:
- Agent 1: numeric / factual drift vs filesystem
- Agent 2: rules-of-engagement violations (em dashes, topology leaks, AI tells)
- Agent 3: skill discovery / opportunity
- Agent 4: architecture truth (compose vs portfolio)

Verify agent findings against source before editing. Agents can misread (Agent 3 once flagged "12 security gates" that was actually in Claude's prompt to the agent, not in the portfolio).

---

## 6. Where things go wrong

| Symptom | Likely cause | Fix |
|---|---|---|
| Pages shows old content after push | Browser cache | Hard refresh (Cmd+Shift+R) |
| Pages still shows old after refresh | Build still running | Check `gh api repos/ET-sec/portfolio/pages/builds/latest` |
| Resume Word renders 2 pages but PDF says 1 | Word's looser line spacing | Hand-tighten in Word: 10.5pt body, trim bullets |
| Cert card grid uneven | Inner `.hud` not stretching to grid cell | Verify CSS: `grid-auto-rows: 1fr` + flex column on `.cert-card` |
| Mirror sync fails on gitleaks | New secret pattern in source | Either scrub the secret or allowlist its path in `scripts/mirror/gitleaks.toml` |
| Mirror sync fails on visibility check | Private repo flipped to public | Investigate immediately. The check is the last guard before push. |
| Renovate PR opens for Tier 3 image | renovate.json packageRules incorrect | Re-verify the Tier 3 enabled: false block matches the image name |
