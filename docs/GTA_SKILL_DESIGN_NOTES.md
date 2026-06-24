# GTA Skill Design Notes
**Owner:** Emmanuel Tigoue
**Created:** 2026-06-24
**Companion to:** `docs/GROUND_TRUTH_AUDIT_PROTOCOL.md`
**Purpose:** Improvements, accuracy patterns, and failure-mode antidotes for the Ground Truth Audit skill build. Written after the first manual GTA run on the GRC library, which found 280+ corrections across 60 docs.

This is the design backlog for the `/gta` Claude Code skill. The protocol file documents how to RUN it. This file documents how to BUILD it well.

---

## v1 priority improvements (build into the first cut of the skill)

### 1. Split the mechanical from the semantic

The first GRC run had fix agents doing both factual corrections (port numbers, model names) AND the em-dash sweep at the same time. The em-dash sweep is deterministic and belongs in a Python script, not in an LLM agent. LLMs introduce variation per run. A regex pass is consistent every time. Separate the two phases. Run the deterministic script first to handle em dashes, double-hyphens, "not X. Y." juxtapositions, and known AI-tell phrases. Then run the semantic LLM agent for the harder judgment calls.

Why this matters: catches more em dashes, and lets the LLM focus its tokens on judgment instead of mechanical pattern-matching.

### 2. Verify with a separate set of eyes

In the first run, agents wrote "fixed line 234" and we trusted them. The skill should add a verification phase: an agent that does NOT know what was supposed to be fixed and only sees the post-fix file. It re-audits cold. If its findings list does not match (original sidecar findings list minus applied fixes), something is off.

Why this matters: agents claim work they did not do sometimes. Second-pass verification catches the silent miss.

### 3. Diff-based verification, not summary-based

The verification phase reads the actual `git diff` and runs an agent over the diff itself. Not the agent's claim of what it changed. The diff is what actually happened. The agent's summary is one degree removed.

Why this matters: closes the trust gap between "agent said it did X" and "X actually happened in the file."

### 4. Confidence scores per finding

Every sidecar entry gets a confidence rating:

- **HIGH**: ground truth file says it explicitly. Auto-fix.
- **MEDIUM**: multiple sources agree but no single proof. Auto-fix with a TODO note explaining the inference.
- **LOW**: one source, no confirmation, judgment call. Always becomes UNCLEAR. Human review only.

Why this matters: prevents agents from confidently applying their best guesses. Forces explicit calibration.

### 7. Pre-built ground truth catalogs

Maintain JSON files inside the skill for things that change slowly:

- NIST 800-53 Rev 5 control IDs + names + descriptions
- OWASP Top 10 (Web 2021, API 2023, LLM 2025, Agentic 2026)
- MITRE ATT&CK Enterprise techniques
- MITRE ATLAS techniques for AI
- ISO 27001:2022 Annex A controls
- NIST CSF 2.0 Functions/Categories/Subcategories
- NIST AI RMF Functions/Categories
- HIPAA Security Rule (45 CFR §164.308/310/312/316) sections

Refreshed quarterly via WebFetch from authoritative sources. Agents look up against the catalog instead of relying on training data.

Why this matters: the biggest single accuracy win. Training data hallucinates control numbers and OWASP rankings. A maintained JSON catalog does not.

### 9. Checkpoint and resume

After each phase, write a state file: scope, files audited, sidecars produced, fixes applied, errors. Resume re-enters cleanly at the next pending phase without re-doing work.

Why this matters: a big-scope GTA could take 30 to 60 minutes. Laptop closure, context limits, or network drops should not waste the run.

### 12. Three personas, not two

Recruiter + Senior Interviewer + Stranger.

- **Recruiter pass**: scores credibility for a non-technical reader. Surfaces sentences a recruiter would trip on.
- **Senior interviewer pass**: scores technical defensibility. Surfaces sentences a Lead-level interviewer would push back on.
- **Stranger test**: reads one doc cold with no project context. If they cannot figure out what the project is and why it matters from the doc alone, the doc fails. Catches insider-jargon docs that only make sense to Emmanuel.

Why this matters: three personas cover the three failure modes (looks bad to recruiter, looks shallow to interviewer, looks like internal noise to anyone else).

### 15. Treat my outputs as drafts

The skill bakes in the assumption that I confidently hallucinate sometimes. Default mode:

- Single-agent finding = draft
- Two-agent agreement = candidate fix
- Three sources (two agents plus ground truth file) = applied fix

Why this matters: this is the antidote to my known failure mode. It is a structural defense, not a behavioral one.

### 16. Hold-position protocol in debates

Per the existing rule, an agent must not switch positions because another agent pushed back. Only new evidence shifts the position. The debate protocol enforces this: each "switch" must cite specific new evidence not present in the original claim.

Why this matters: without this rule, the louder agent wins. With this rule, the agent with better evidence wins.

### 17. Batch ground-truth reads at the start

In the first GRC run, each of the 6 audit agents independently re-read `compose.yaml`, `CLAUDE.md`, and `SANITIZATION_KEY.md`. Wasteful, and inconsistent if files change mid-run. The skill's Phase 0 should read every ground-truth file once, snapshot it, hash it, and pass the snapshot to every downstream agent.

Why this matters: same source for everyone. Cheaper. No mid-run drift.

---

## v1.1 backlog (build after v1 ships)

### 8. Test fixture for regression

Build 3 to 5 intentionally-broken sample docs where the right corrections are known. Run the skill against the fixture before running against real docs. Catches when the skill itself has drifted from prior versions.

### 10. Signed audit attestations

Every completed GTA produces a small signed file: "scope X, audited {date}, GTA v{N}, found {Y} corrections." Sigstore or cosign. Compliance evidence. Real senior interview talking point: my repo carries signed audit attestations.

### 11. Drift diff between runs

After each run, compute the diff against the previous run's state. "Since the last audit, X new claims drifted, Y were closed, Z new TODOs appeared." Surfaces drift velocity. Tells whether doc-code commits are traveling together or slipping.

### 13. Pull-request mode

When run on a branch, the skill produces PR-shaped output: each correction as a separate commit with a real message, organized for review. Makes the discipline mergeable, not one giant blob.

### 14. Slack or Telegram summary

Post a brief summary to a channel at the end: scope, fixes applied, time taken, TODOs left, debates pending. Pairs with the existing Telegram bots.

---

## v2 backlog

### 5. Multi-model audit on high-stakes scopes

For interview-critical docs (SSP, threat models, Executive Summaries), run a second pass with a different model. Opus audits, then Sonnet audits independently. Disagreements between models surface the hardest cases and reduce the chance both models share the same blind spot. Expensive, so target only the top 10 percent of docs by impact.

### 6. External fact-checking with WebFetch

When a doc cites NIST 800-53 AC-2 or OWASP LLM01, the agent WebFetches the actual standard and verifies the citation. Not just well-formatted. The actual text matches. Adds latency and cost. Worth it for compliance-grade output.

### CI gate

Wire the GTA to GitHub Actions on every PR that touches docs/. Block merge until a current GTA sidecar exists with zero outstanding WRONG entries. Steady state. Once the backlog is clean, the CI keeps it clean.

---

## How my failure modes shaped this design

This section is explicit because the skill must defend against me, not assume I am perfect.

**I confidently hallucinate.** Items 4, 5, 15 are the antidotes. Confidence scores force calibration. Multi-model audits catch shared blind spots. Treating my outputs as drafts means no single-agent claim becomes a fix without a second pair of eyes.

**I switch positions under social pressure.** Item 16 is the antidote. The debate protocol holds position unless new evidence appears.

**I conflate "I applied the fix" with "the fix is in the file".** Items 2, 3 are the antidotes. Verification phase reads the actual diff, not my claim.

**I miss things when context is long.** Items 9, 17 are antidotes. Checkpoint and resume keeps each phase short. Batched ground-truth snapshots avoid re-reading the same file 6 times.

**I introduce voice drift even with rules.** Item 1 antidote: deterministic Python sweep for em dashes and AI tells catches more than a single LLM pass would.

**I lose precision in big clusters.** Smaller clusters with more agents reduce per-agent context load. Already in the protocol, but worth restating: when in doubt, split the cluster.

---

## Open design questions

1. **Where does the REPO_MAP.yaml live?** Probably at repo root: `/Users/et/cyber-squire-ops/REPO_MAP.yaml`. Gitignored or committed? Argument for committed: provenance. Argument for gitignored: it leaks scope and structure to anyone with read access. Default to gitignored, with a `REPO_MAP.example.yaml` committed for reference.

2. **Auto-regenerate REPO_MAP.yaml or manual refresh?** Auto on every GTA run. Manual override available. Pin the schema version so older runs do not break on schema bumps.

3. **Where does the skill live?** `~/.claude/skills/gta/` as a Claude Code skill. Reads from the repo root via $CLAUDE_PROJECT_DIR.

4. **How do debates surface to Emmanuel?** Inline in the master synthesis doc, with the full reasoning narrated by the main thread. NOT as a separate file he has to remember to read. Visibility = he sees them or they did not happen.

5. **What does the website sync actually push?** Generated HTML or markdown? Probably markdown that the website build pipeline converts. Verify the website's source format before designing the sync.

6. **Cost ceiling per run?** Worth a hard cap. If a single GTA run exceeds $5 in tokens, pause and ask. Prevents runaway costs.

7. **What is the minimum scope worth a GTA?** Probably a single doc. Tighter scopes have less overhead. The skill should work on single files cleanly, not assume "full library."

---

## Build order checkpoint

When v1 is being built, the order is:

1. REPO_MAP.yaml schema + scanner script (Phase 0 spine)
2. Skill scaffold in `~/.claude/skills/gta/`
3. Ground truth catalog files (JSON for NIST, OWASP, MITRE)
4. Deterministic Python sweep script (em dashes, AI tells, double-hyphens)
5. Phase 1-2 prompts (scope, parallel audit)
6. Phase 6 prompts (master synthesis)
7. Phase 8 prompts (parallel fix)
8. Phase 10 prompts (verification)
9. Personas (recruiter, senior interviewer, stranger)
10. Phase 7 debate adjudication with narrated reasoning
11. Checkpoint and resume state files
12. End-to-end test on a small fixture

That order gets v1 working end-to-end before any of the v1.1 niceties are added.
