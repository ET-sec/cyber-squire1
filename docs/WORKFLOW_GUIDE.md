# Workflow Guide
**Created:** 2026-06-24
**Purpose:** Document the branch + PR + merge discipline so the process is clear, repeatable, and visible.

---

## What changed

The repository moved from a "commit straight to main" pattern to a "branch + PR + merge" pattern. Three forces make this stick:

1. **Automation that makes the disciplined path the easiest path** (helper scripts, PR template, pre-commit hook).
2. **CI gates that enforce the rule** (branch protection, status checks).
3. **The GTA skill that produces PR-ready output** for every audit run.

## The daily flow

For any change you want to ship:

```bash
cd /Users/et/cyber-squire-ops

# 1. Start a branch with a typed prefix
./scripts/git/new-branch.sh feat/some-change

# 2. Make changes, commit in logical chunks
git add path/to/changed/file
git commit -m "feat(scope): short subject"
# Pre-commit hook runs the AI-tells sweep. Blocks if em dashes are found.

# 3. Push and open PR
./scripts/git/ship-pr.sh
# Prompts for title, opens PR with the template, returns the URL.

# 4. Fill in the PR template body (Summary, Test plan, Notes)
# 5. Wait for CI green
# 6. Squash merge
gh pr merge --squash --delete-branch

# 7. Update local main
git checkout main
git pull --rebase
```

That is the whole loop. Three scripts to run, one git CLI command to merge.

## Branch naming reference

| Prefix | When | Example |
|---|---|---|
| `feat/` | New feature or doc | `feat/gta-milestone-2-pipeline` |
| `fix/` | Bug or correction | `fix/grc-embedding-drift` |
| `docs/` | Doc only | `docs/expand-protocol` |
| `chore/` | Maintenance, deps | `chore/em-dash-sweep` |
| `security/` | Security work | `security/sanitize-net-core` |
| `refactor/` | No behavior change | `refactor/squire-nodes` |
| `gta/` | GTA audit run | `gta/grc-2026-06-24` |
| `infra/` | Infra change | `infra/datadog-dashboard` |
| `ci/` | CI/CD change | `ci/pin-action-shas` |
| `test/` | Tests | `test/squire-regression` |
| `hotfix/` | Urgent fix | `hotfix/credential-rotate` |
| `wip/` | Work in progress, never merge | `wip/langgraph-experiment` |

## What got built in this PR

**Workflow automation:**
- `.github/pull_request_template.md`: pre-fills the PR body
- `.github/CODEOWNERS`: auto-assigns review
- `.github/labeler.yml` plus `auto-label.yml`: tags PRs by branch prefix and changed paths
- `.github/workflows/stale.yml`: closes inactive PRs and branches automatically
- `.githooks/pre-commit`: blocks commits with em dashes or AI writing patterns
- `scripts/git/new-branch.sh`: one command to start a branch
- `scripts/git/ship-pr.sh`: one command to push and open a PR

**Repo signal docs:**
- `SECURITY.md`: vulnerability disclosure policy, response SLAs, AI security scope
- `CONTRIBUTING.md`: workflow rules, contribution patterns

**Updates:**
- `.gitignore`: excludes `REPO_MAP.yaml`, `.gta/`, `*.bak`

## What to do in the GitHub UI (one-time setup)

Visit the branch protection settings page and add a rule for `main`:

- Branch name pattern: `main`
- Require a pull request before merging: ON
  - Required approvals: 0 (self-approve allowed)
- Require status checks to pass: ON
  - Add the checks to gate: trivy, semgrep, gitleaks, checkov, opa
- Require linear history: ON (forces squash or rebase merges)
- Do not allow bypassing the above settings: ON
- Allow force pushes: OFF
- Allow deletions: OFF

That makes the discipline structural. Direct pushes to main become impossible.

## The pre-commit hook

The hook is installed via `git config core.hooksPath .githooks` (per-clone setup).

**What it does:**
- Runs the GTA AI-tells sweep on staged markdown files
- Hard-blocks commits with em dashes, en dashes, or double-hyphen prose between words
- Warns (but allows commit) on AI-tell phrases like "leveraging", "robust", "seamlessly"

**If it blocks you:**
```bash
python3 ~/.claude/skills/gta/scripts/sweep_ai_tells.py --apply <files>
git add <files>
git commit
```

**Emergency bypass** (rare, generally a bad idea):
```bash
git commit --no-verify
```

## How the GTA skill ties in

Every GTA run produces a PR-ready set of corrections. From Milestone 2 onward, running `/gta <scope>` will:

1. Audit the scope
2. Apply mechanical fixes
3. Create a `gta/<scope>-<date>` branch
4. Commit the corrections in logical chunks
5. Open a PR with the full audit summary as the body

The PR is then reviewed and merged through the standard flow.

## Follow-up work (separate PRs later)

Already shipped 2026-06-25:
- CodeQL workflow (PR #18)
- README badges + issue templates + repo About metadata (PR #19)
- Hide private folder names via single `CoreDirective/` gitignore rule (PR #20)
- Pin all GitHub Actions to commit SHAs (PR #21)

Still queued, each its own scoped PR when ready:

- **GPG commit signing**: generate a GPG key on the laptop, upload to GitHub, then require signed commits in branch protection
- **Compose admission + grc_librarian eval workflows**: bundled re-ship (sanitize `infra/conftest/` first, re-include `builds/grc_librarian/` in `.gitignore`, add `ANTHROPIC_API_KEY` secret in GitHub Actions, then track deps and re-open both workflows together)
- **Branch protection ruleset migration**: move from legacy branch protection to GitHub Rulesets so path-filtered checks can be "required if started" instead of unconditionally required
- **GitHub Discussions or Wiki**: architecture decision log

## When this discipline pays off

- **External audit**: the GitHub history shows branch + PR + merge pattern, not direct-to-main commits. Visible discipline.
- **Bug rollback**: every PR is one commit on main after squash. One `git revert <sha>` undoes it cleanly.
- **CI catches issues before main is dirty**: Trivy, Semgrep, Gitleaks, Checkov gate at PR time, not after.
- **GTA runs land as PRs**: audit corrections are reviewable and revertable.
- **Future collaborators**: the workflow is already documented and enforced.

## Three rules that make this not feel like overhead

1. **Land small, land often.** A 5-file PR ships in 10 minutes. A 50-file PR sits open for a week.
2. **One concern per PR.** Mixing a feature add with an unrelated bug fix is the anti-pattern. Two branches, two PRs.
3. **Trust the CI.** If trivy or gitleaks blocks a PR, do not bypass. Fix it. CI exists to catch the thing missed under time pressure.

That is the workflow. Use the scripts, trust the gates, ship clean PRs.
