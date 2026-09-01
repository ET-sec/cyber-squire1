# DR-05: The AWS Security Plane (multi-cloud by blast radius)

**Date:** 2026-09-01
**Status:** Designed and gated; apply scheduled, receipts pending. Terraform is public in `terraform/cd-aws-security-plane/` and passes the full PR gate (fmt, validate, Checkov 135/0 with 11 reasoned skips). This record flips to "Implemented and verified" when the five receipts in the module README exist.

## Problem
In August 2026 one cloud provider failure took the production host AND the
infrastructure records meant to survive it. The Phase 20.1 controls fixed
the intra-cloud story (immutable backups, remote locked state, drift
detection), but every one of those controls still lives with the workloads
it protects. The evidence that proves the platform's behavior, the backups
that resurrect it, and the emergency credential that unlocks it shared one
vendor failure domain. The lesson wasn't "pick a better vendor," it was:
**the watcher must not live in the house it watches.**

## Trust boundary
This plane splits custody across three vendors, each holding what the
others cannot be trusted to survive: Cloudflare holds the edge, OCI holds
the workloads, AWS holds evidence, backup replicas, and break-glass. GitHub
is the identity issuer for both cloud pipelines: the same signed OIDC token
that exchanges into an OCI session natively assumes an AWS role, both
trusts pinned to this repo and main. Compromise of the workload cloud
cannot blind the operator (evidence is off-cloud, Object Lock compliance
mode), cannot silently use the emergency path (any read of the break-glass
secret is a CloudTrail management event that alerts within minutes), and cannot spread laterally (the AWS
principals carry an explicit deny outside the home region and the uploader
can only write).

## Options considered
1. **AWS as the security and evidence plane (chosen).** S3 Object Lock is
   the strongest immutability primitive available at free-tier cost;
   CloudTrail gives tamper-evident audit down to per-object S3 data events; GitHub
   federation is first-class. Everything here is a control, nothing is a
   workload: one Lambda, no VPC, no standing compute.
2. **Second OCI tenancy or region.** Rejected: same vendor, same billing
   relationship, same failure domain as the event that motivated this.
3. **Cloudflare R2 for everything.** Partial: R2 takes the state-file split
   (queued), but R2 has no Object Lock equivalent with compliance-mode
   semantics and no CloudTrail-grade data events, so it cannot carry the
   evidence custody role.
4. **A managed SIEM (Datadog or Splunk) as the watcher.** Deferred and
   documented: push alerts via EventBridge to Telegram cover detection at
   this scale, Athena queries the vault on demand, and a standing SIEM adds
   monthly cost and a third-party data-custody surface without new signal.
   The integration point (S3 to SIEM ingest) exists when scale demands it.

## Blast radius
- Workload cloud dies: evidence, replicas, and break-glass survive on AWS;
  recovery starts from the vault. This is the exact 2026-08 scenario,
  closed.
- AWS account compromised: the uploader can only add objects (Object Lock
  refuses deletes even for root inside the window), the drift role can
  only read the plane's own config, the region guard denies everything
  outside us-east-1, and every access is on the trail with log file
  validation. Workloads are untouched; OCI credentials do not live in AWS
  except the sealed break-glass, whose access screams.
- Both clouds die together: the git repository remains the third copy of
  the design, which is how the platform survived the first time.

## The one long-lived credential
OCI instance principals cannot federate into AWS, so the nightly evidence
upload authenticates as a scoped IAM user (`cd-evidence-uploader`):
PutObject and GenerateDataKey only, region-locked, rotated on the standard
schedule through the secrets manager. Accepted risk, recorded here: the
alternative (running the upload from GitHub-hosted CI to get federation)
would move private backup data through a third party's runners.

## Verification plan (receipts on apply)
1. Object Lock delete attempt as admin: kept denial.
2. Deliberate break-glass read: kept Telegram alert and CloudTrail event.
3. Wrong-ref federation attempt: kept AssumeRoleWithWebIdentity denial.
4. Uploader attempting GetObject and DeleteObject: kept both denials.
5. Console tag drift: caught by the nightly plan leg, reverted.

## At enterprise scale
Same shape, different parts: the evidence plane becomes an AWS Security
Lake or dedicated log-archive account inside an organization, the region
guard becomes an SCP, break-glass becomes two-person-controlled with a
hardware token, and the SIEM question flips because scale pays for it. The
principle that survives every size: security telemetry and recovery
material live in a different failure domain than the workloads, with
custody you can prove.

## The interview version
"My workloads run on Oracle behind a Cloudflare zero trust edge, but the
evidence, the backup replicas, and the break-glass credential live in AWS
behind Object Lock, because the day I lost a cloud provider I learned the
security plane can't share a failure domain with what it protects. Same
GitHub identity federates into both clouds, pinned to one repo and one
branch, and the break-glass secret is wired so any read of it pages me
with the caller's identity inside two minutes."
