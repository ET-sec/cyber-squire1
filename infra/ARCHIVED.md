# ARCHIVED: compose admission policies (frozen 2026-09-09)

This directory is **no longer active**. It holds seven Conftest policies written
to gate `COREDIRECTIVE_ENGINE/docker-compose.yaml` at pull request time:
privileged containers, missing resource limits, floating image tags,
unapproved registries, host networking, missing healthchecks, and writable root
filesystems. Do not treat a passing local run here as a merge gate.

Nothing calls them, and nothing in this repository ever has. The workflow the
README describes, `.github/workflows/compose-admission.yml`, does not exist. The
two Conftest runs that do exist point elsewhere:
`.github/workflows/grc-validate.yml:92` tests the governance library against
`policies/grc/`, and `.github/workflows/terraform-pr.yml:92` tests each
Terraform plan against that plane's own `policy/` directory. No shell script, no
hook, and no evidence anchor reads anything under `infra/`. The one file outside
this directory that names the policy path is an untracked workflow under
`Agent_Squire/`, which git ignores and which never runs here.

**Active policy enforcement lives in `../policies/grc/` and in
`../terraform/cd-oci-infrastructure/policy/`.**

Why keep it: the seven rules are a working reference for the OPA work, and they
are the compose shaped half of the argument the Terraform policies make about
plans. Removing them would mean keeping a private copy of the same files for no
gain, since the rules are the reusable part and the missing workflow is the part
that was never written.

What would bring it back: a job that runs
`conftest test <compose file> --policy infra/conftest/policy/` on pull requests
touching the compose file or this directory. On the day that job exists, delete
this marker and move the `infra/**` row in `docs/REPO_MANIFEST.yaml` back to
`active` with a reason that names the job.
