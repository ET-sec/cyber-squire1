<!--
PR title format: <type>(<scope>): <subject>
Examples:
  feat(gta): Milestone 2 audit and fix pipeline
  fix(grc): GTA-applied corrections, embedding provider drift
  docs(roe): expand rules of engagement with multi-agent discipline
  security(sanitize): replace net-core with internal-net in playbooks
  chore(deps): bump langchain to 1.3.9 in the takehome exercise
-->

## Summary
<!-- 1 to 3 bullets on WHAT changed and WHY. Not a diff narration. -->
-
-
-

## Type of change
<!-- Check one -->
- [ ] `feat` new feature
- [ ] `fix` bug fix
- [ ] `docs` documentation only
- [ ] `chore` maintenance
- [ ] `security` security fix
- [ ] `refactor` no behavior change
- [ ] `gta` GTA audit run on a scope
- [ ] `infra` infrastructure
- [ ] `ci` CI/CD change
- [ ] `test` adding or fixing tests

## Scope of change
<!-- Which area of the repo? Examples: docs/grc, Agent_Squire, terraform, .github/workflows -->


## Test plan
<!-- Bulleted checklist of what was tested or verified. CI handles most of this. -->
- [ ] CI green (Trivy, Semgrep, Gitleaks, Checkov, OPA as applicable)
- [ ] AI-tells sweep clean on all touched markdown
- [ ] Self-reviewed the full diff before requesting merge
- [ ] No container counts modified (or modification was explicit and approved)
- [ ] No sensitive content leaked (Doppler keys, internal hostnames, IPs)

## Linked artifacts
<!-- Any related GTA sidecars, audit summaries, design docs, prior PRs -->


## Rollback plan
<!-- If this breaks, how do we revert? "git revert <merge-sha>" is the default. Note any data migrations or external state. -->


## Notes for reviewer (self or future-you)
<!-- Anything not obvious from the diff. Tradeoffs considered. Things deliberately left out. -->

