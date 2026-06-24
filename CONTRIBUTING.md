# Contributing

This is currently a solo project, but the contribution workflow is documented for two reasons: future collaborators, and to make the discipline visible.

## Workflow

All changes go through a branch and pull request. Direct pushes to `main` are not allowed.

### Quick path

```bash
# Start a new branch
./scripts/git/new-branch.sh feat/your-feature

# Make changes, commit
git add path/to/file
git commit -m "feat(scope): short subject"

# Push and open PR
./scripts/git/ship-pr.sh
```

### Branch naming

`<type>/<short-description>` where type is one of:

| Prefix | When to use |
|---|---|
| `feat/` | New feature, new doc, new infra |
| `fix/` | Bug fix or correction pass |
| `docs/` | Documentation only |
| `chore/` | Maintenance, formatting, dependency bumps |
| `security/` | Security fix or hardening |
| `refactor/` | Code restructure, no behavior change |
| `gta/` | GTA Ground Truth Audit run on a scope |
| `infra/` | Infrastructure change |
| `ci/` | CI/CD change |
| `test/` | Adding or fixing tests |
| `hotfix/` | Urgent production fix |
| `wip/` | Work in progress, never merged |

### Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

`<type>(<scope>): <subject>`

Examples:
- `feat(gta): add Milestone 2 audit and fix pipeline`
- `fix(grc): correct embedding provider drift across 5 docs`
- `docs(protocol): expand audit methodology`
- `security(sanitize): replace net-core with internal-net in playbooks`

## Writing style

The pre-commit hook automatically scans staged markdown files for AI writing patterns (em dashes, "leveraging", "robust", "seamlessly", and similar) and blocks commits that contain them.

To install the hook:
```bash
git config core.hooksPath .githooks
```

## Ground Truth Audit (GTA)

Before publishing any significant doc change, run the GTA skill:

```bash
# Quick scan of a directory or single file
python3 ~/.claude/skills/gta/scripts/sweep_ai_tells.py docs/grc/*.md

# Apply mechanical corrections in place
python3 ~/.claude/skills/gta/scripts/sweep_ai_tells.py --apply docs/grc/*.md
```

Full GTA pipeline documentation: [docs/GROUND_TRUTH_AUDIT_PROTOCOL.md](docs/GROUND_TRUTH_AUDIT_PROTOCOL.md)

## PR requirements

Every PR must:
- Pass all CI checks (Trivy, Semgrep, Gitleaks, Checkov, OPA as applicable)
- Use a branch name with a valid prefix
- Follow Conventional Commits
- Fill in the PR template (Summary, Test plan, Notes)
- Be self-reviewed before merge

## Merge strategy

Squash merge is the default. Each PR becomes one commit on `main`. Linear history is enforced.

## Sensitive content

Never commit:
- `CLAUDE.md`, `SANITIZATION_KEY.md`, `.env`, `.envrc`, credential files
- Internal IPs, port numbers, or internal hostnames in public-facing docs (use sanitized labels per `SANITIZATION_KEY.md`)
- Secrets of any kind (the Gitleaks scan will catch these, but do not push that responsibility)
