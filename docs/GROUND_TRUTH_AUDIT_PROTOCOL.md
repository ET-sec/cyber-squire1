# Ground Truth Audit Protocol (GTA)
**Owner:** Emmanuel Tigoue
**Created:** 2026-06-24
**Purpose:** A repeatable verification process that prevents repo rot, doc drift, and credibility risk in public GitHub artifacts.
**When to run:** Before any external publication (recruiter, interview, client). At the close of every milestone. Every 60 days on the full repo as a hygiene pass.

---

## Why this exists

Every doc, README, and config file in a repo is a claim. Claims drift. The system changes, the doc does not. An interviewer who reads a stale claim does not know it is stale. They assume it is current and downgrade you when reality contradicts it. The GTA prevents that.

The GRC library audit on 2026-06-24 was the first formal run of this protocol. It found 280+ corrections across 60 docs. Most were architecture drift (system changed, doc did not). The methodology below is what was actually done, written down so it can be re-run on any subset of the repo.

---

## The protocol in 6 steps

### Step 1: Define scope and exclusions

Pick the scope. Examples:
- "All docs in docs/grc/"
- "All workflow files in .github/workflows/"
- "Agent_Squire/ source code plus its README"
- "The root README.md and CLAUDE.md"

Pick exclusions. These are claims the audit must NOT modify, usually because the owner already decided they are out of scope or known-imperfect. Example exclusion from the GRC audit: container count numbers.

### Step 2: Inventory

List every file in scope with size and line count.
```
find <scope> -type f -name "*.md" | xargs wc -l | sort -rn
```
This gives you the count, the heavy hitters, and the surface area.

### Step 3: Identify ground truth sources

For every category of claim, name the authoritative source. The audit only believes the ground truth, never the doc.

Examples:
- Service names, ports, image versions: `docker-compose.yaml`
- Current secrets in Doppler: `doppler secrets list`
- Current GitHub workflows: `ls .github/workflows/`
- Real code structure: actual filesystem, never the doc's claim
- NIST control numbers: official NIST SP 800-53 Rev 5 PDF
- OWASP Top 10 lists: official OWASP site for the version cited
- MITRE ATT&CK or ATLAS IDs: official MITRE matrix for the year cited
- Sanitization mappings: `SANITIZATION_KEY.md`
- Current container state: `ssh cd-alpha 'docker ps'`

If two sources disagree, the more primary one wins. The compose file beats CLAUDE.md. The actual matrix beats your memory. The code beats the README.

### Step 4: Parallel audit

Cluster the scope into 4 to 6 buckets. Deploy one auditor agent per bucket in parallel. Each auditor:

1. Reads its assigned source doc
2. For every claim that names a number, version, port, IP, control ID, framework, date, file path, or vendor: verifies it against the ground truth source
3. Classifies each claim:
   - **ACCURATE**: confirmed against source
   - **OUTDATED**: was true once, now stale
   - **WRONG**: never was true
   - **UNCLEAR**: cannot verify, needs owner input
   - **EXCLUDED**: matches exclusion rule, do not flag
4. Hunts cross-doc contradictions (Doc A says X, Doc B says Y)
5. Flags AI writing tells (em dashes, "not X. Y." juxtaposition, robotic phrases, "leveraging", "robust", "seamlessly")
6. Writes a sidecar audit file per source: `_corrections/{DOCNAME}_AUDIT.md`

Sidecar structure:
```
# Audit: {DOC}
**Audited:** {date}
**Total claims checked:** N
**Status:** ACCURATE: X | OUTDATED: Y | WRONG: Z | UNCLEAR: W | EXCLUDED: C

## OUTDATED
- Line N: claims "X", current is "Y", source: {file:line}
- Recommended fix: {exact replacement text}

## WRONG
- Line N: claims "X", actual is "Y", source: {file:line}
- Recommended fix: {exact replacement text}

## UNCLEAR
- Line N: claims "X", cannot verify because Y. Owner must confirm.

## EXCLUDED per instruction
- Line N: claims "X". Noted, not flagged.

## Cross-doc contradictions
- This doc says X; {OTHER_DOC} says Y at line M.

## AI writing tells
- Line N: em dash, suggest comma break
- Line N: "not X. Y.", suggest direct positive
```

### Step 5: Master synthesis

One summary doc at the top of `_corrections/`. Lists:
- Headline (what is broken, what is strong)
- Top 10 interview-killer fixes ranked by impact
- Category counts (how many OUTDATED, WRONG, contradictions)
- What is already strong (do not rewrite)
- Fix order recommendation (round 1, round 2, etc.)

This file is the only one the owner reads first. Everything else is referenced from here.

### Step 6: Parallel fix

Same clustering as step 4. Deploy one fixer agent per bucket. Each fixer:

1. Reads its sidecars
2. Applies OUTDATED and WRONG corrections to source docs
3. For UNCLEAR: adds inline HTML comment `<!-- TODO(et): {what is unclear} -->` above the line
4. For EXCLUDED: skips
5. Sweeps em dashes (replace with comma, period, "and", or ":")
6. Sweeps "not X. Y." juxtapositions (rewrite as direct statement)
7. Saves, does not commit
8. Reports back: files modified, edits per file, TODO comments left

The owner reviews the diff and commits in batches.

---

## Standing rules across every GTA run

- **No em dashes ever.** Sweep on every pass.
- **No "not X. Y." juxtaposition.** Sweep on every pass.
- **No AI writing tells** (leveraging, robust, seamless, juxtapose, comprehensive, etc.).
- **TODO comments stay inline** in HTML format so they show in markdown raw view but not rendered output.
- **Exclusions are explicit.** Never auto-modify the excluded category even if it is wrong.
- **Sidecars are not committed.** They are working files in `_corrections/`. Delete them after the diff is approved and committed.
- **Container counts: leave alone** unless the owner explicitly opens that category to corrections.
- **Sanitization stays consistent** with the SANITIZATION_KEY.md. If the key is wrong, fix the key, not the docs.

---

## Where to apply this next

The GRC library is done. The other repo areas that need a GTA pass, ordered by interview-impact:

### 1. Public README at repo root (HIGH priority, 1 doc)
**Scope:** `/Users/et/cyber-squire-ops/README.md`
**Why:** This is the first thing a recruiter, interviewer, or stranger sees. Stale numbers here are interview-killers before you even talk.
**Ground truth:** `docker-compose.yaml`, `CLAUDE.md`, actual current state
**Time:** 30 minutes, one agent

### 2. Agent_Squire/ repo (HIGH priority, ~15 docs)
**Scope:** `/Users/et/cyber-squire-ops/Agent_Squire/` README, THREAT_MODEL.md, per-agent READMEs, evals
**Why:** This is your AI security flagship artifact. Drift here directly contradicts the GRC docs (which are now corrected).
**Ground truth:** the actual code in Agent_Squire/, the corrected GRC docs, the deployed Squire at squire.tigouetheory.com
**Time:** 1 to 2 days

### 3. terraform/cd-do-infrastructure/ (MEDIUM priority, ~25 .tf files plus OPA policies)
**Scope:** terraform code, OPA policies, READMEs in the IaC folder
**Why:** Cloud security and IaC are interview keywords. Drift between Terraform claims and actual DO droplet is a senior-level credibility hit.
**Ground truth:** actual DO state via `doctl`, current `terraform state list`
**Time:** 1 day

### 4. .github/workflows/ (MEDIUM priority, 12 workflow files)
**Scope:** all workflow YAML, plus any docs that describe the CI/CD pipeline
**Why:** Supply chain security and DevSecOps signal. Now that SECURE_SDLC.md claims 12 workflows, those 12 must actually do what is claimed.
**Ground truth:** workflow YAML itself, actual recent action runs
**Time:** half a day

### 5. detections/ Sigma rules (MEDIUM priority, 18 YAML rules)
**Scope:** all Sigma rules, plus the playbooks that reference them
**Why:** Several playbook TODOs flagged that rules referenced in playbooks do not exist (n8n shell-spawn allowlist, Keycloak account creation, root SSH break-glass, etc.). Closing those gaps either adds the rules or removes the playbook claim.
**Ground truth:** the actual Sigma rule files, what they cover, what they miss
**Time:** half a day

### 6. CLAUDE.md (LOW priority but high blast radius, 1 doc)
**Scope:** `/Users/et/cyber-squire-ops/CLAUDE.md`
**Why:** This file is the internal source of truth that other audits anchor against. If it is wrong, every downstream audit inherits the wrong anchor. Worth a self-audit pass to confirm it still matches reality.
**Ground truth:** actual stack state, current job pipeline, current cert state, current deployments
**Time:** 1 hour

### 7. docs/architecture/ and docs/runbooks/ (LOW priority, varies)
**Scope:** any leftover architecture docs, runbooks, deployment guides
**Why:** Some are stale per earlier mapping (COREDIRECTIVE_ENGINE/SUPERVISOR_DEPLOY.md, FIX_GOOGLE_OAUTH.md, ADHD_COMMANDER_SETUP.md). Decide: keep, archive, or delete.
**Ground truth:** current deployment, current OAuth state
**Time:** half a day

### 8. builds/ tools (LOWEST priority, multiple subfolders)
**Scope:** resume-tailor, proposal-gen, etc. plus their READMEs
**Why:** Internal tooling, not public-facing. Skip unless one of them is being demoed.
**Time:** skip until needed

---

## Running the GTA for any future scope

Three ways to invoke this, ranked by friction.

**1. Ad hoc (what we just did):** point me at a scope, say "GTA this," and the parallel agents run. Output: sidecars plus master summary plus optional fix pass.

**2. As a saved skill:** save the protocol as a Claude Code skill in `~/.claude/skills/gta/` so `/gta <scope>` runs it. The skill packages the prompts, the cluster split, and the output format so it is a single command.

**3. As a CI gate:** wire it to GitHub Actions on every PR that touches docs/. Block merge until a current GTA sidecar exists with no outstanding WRONG entries. This is the steady-state. Once the backlog is clean, the CI gate keeps it clean.

Recommendation: do #2 next session. The GTA is now a repeatable thing, not a one-off favor.

---

## The discipline going forward

Three habits prevent the kind of drift that caused this audit to find 280 corrections:

1. **Doc-code commits travel together.** When you change a service, change the doc in the same commit. If the change is too big, open a doc PR in the same hour. Never let a week go by with the code ahead of the doc.
2. **TODO comments are real work.** The 170+ inline TODOs from this audit are not decoration. They are the next batch of work. Close them in batches by owner-reviewing the inline comment, deciding accept or reject, and committing the resolution.
3. **The 60-day pass.** Every 60 days, run GTA on the full repo. Treat it like a backup verification. Drift that has not been caught in 60 days is drift you cannot defend in an interview.

That is the protocol. Run it. Re-run it. Trust the artifacts. Defend them in interviews because you wrote them and verified them against ground truth.
