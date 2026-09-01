# DR-01: Terraform Remote State Backend (Phase 20.1-01)

**Date:** 2026-08-31
**Status:** Implemented (OCI Object Storage), R2 migration pending operator action

## Problem
Terraform state for `cd-oci-infrastructure` lived as a local file next to the code, inside a directory that only luck and a global gitignore pattern kept out of a public repo. State contains resource OCIDs (Oracle Cloud Identifiers), IPs, and any secret a provider ever writes to an attribute. It is a credentials file wearing a JSON costume. Also: the previous state backend (DigitalOcean Spaces) was lost together with the droplet when the DO account died, which proved that state and compute sharing a vendor is a single point of failure.

## Options considered
1. **Cloudflare R2 (S3-compatible)** with Terraform native S3 locking (`use_lockfile`, TF >= 1.10). Wins on vendor decoupling: state survives the death of the compute account. Blocked today: R2 is not enabled on the account (API error 10042) and enabling it is a dashboard action with terms acceptance that an agent should not perform.
2. **OCI Object Storage via native `oci` backend** (TF >= 1.12). Available immediately, free tier, native state locking, bucket versioning as the recovery layer. Weakness: state lives with the compute vendor again, the exact anti-pattern that burned us in the DO era.
3. **HCP Terraform (Terraform Cloud) free tier.** Fully decoupled, managed locking and encryption. Rejected for now: introduces a third-party SaaS dependency and an account signup for a problem two clouds already solve.

## Decision
Option 2 now, option 1 as a queued migration once R2 is enabled by the operator. Backend migration is a two-command operation (`terraform init -migrate-state`), so sequencing convenience first and decoupling second costs almost nothing, and performing the migration twice is itself demonstrable operational skill. Mitigation for the vendor-coupling weakness in the interim: bucket versioning is enabled, so state history survives an accidental overwrite or delete of the current object.

## Implementation notes
- `backend "oci" {}` skeleton committed; bucket, namespace, region, and key live in `backend.hcl`, which is gitignored. Backend blocks cannot interpolate variables, so partial configuration is the only way to keep account topology out of a public repo.
- Bucket: the state bucket (name kept private), versioning Enabled, NoPublicAccess.
- Auth: local runs use `~/.oci/config` API key. CI auth is Phase 20.1-02 scope.
- Local tfstate deleted after a verified no-op plan from the remote.

## Blast radius if this fails
- Lock mechanism fails open -> two concurrent applies corrupt state -> recovery from bucket version history.
- Bucket deleted or OCI account lost -> state gone with the infra it describes (the DO scenario again) -> this is exactly why the R2 migration stays queued rather than cancelled.
- backend.hcl leaks -> exposes bucket name and namespace only; auth still requires the API key. Low severity, still gitignored.

## Verification (all performed 2026-08-31; verification transcript in the private evidence store)
1. `git check-ignore` confirms tfstate, tfvars, env.sh, backend.hcl all ignored.
2. State object present in bucket (28,559 bytes at migration; the later no-op apply in step 4 rewrote it, so the current version differs by a few bytes), `terraform state list` returns all 8 state entries (6 managed resources + 2 data sources) from remote.
3. First remote plan caught real drift: a console-added SSH ingress rule not in code. Codified via the existing `ssh_allowed_cidrs` variable in gitignored tfvars (keeps the home IP out of the public repo). Second plan: exit code 0, no changes. Nothing was applied against live infra.
4. Lock proven by contention: while a no-op apply held the lock, a concurrent `terraform plan -lock-timeout=0s` failed with "Error acquiring the state lock" (HTTP 412 IfNoneMatchFailed on the lock object PutObject).

## The interview version
"Terraform state is a secrets store, so I moved it off the laptop into versioned object storage with native locking, kept the bucket topology out of the public repo with partial backend config, and proved the lock works by making two runs fight over it: the loser fails with a 412 because the lock is just an atomic create-if-absent, a PutObject with If-None-Match star. First plan off the remote backend immediately caught real drift, a firewall rule someone added by hand in the console. I codified it as a variable instead of letting Terraform rip out my own SSH access. At enterprise scale the same design is S3 plus native locking or Terraform Cloud, with the state bucket in a separate account from the workloads so losing one blast radius doesn't take both."

## Re-evaluation triggers
- Operator enables R2 -> execute the queued migration (bucket + scoped token + `init -migrate-state`).
- OCI ships GitHub OIDC (OpenID Connect) federation improvements relevant to 20.1-02 -> revisit CI auth for state access.
