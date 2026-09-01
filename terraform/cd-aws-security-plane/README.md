# cd-aws-security-plane

The security and evidence plane of a three-plane, multi-cloud design:
Cloudflare holds the edge, OCI holds the workloads, and AWS holds what must
survive the other two. The rule behind every resource here: security telemetry
and recovery material never share a failure domain with the workloads they
protect. The 2026-08 provider loss that took a host and its Terraform state
in one event is the origin story; this plane makes that class of failure a
non-event.

## Status

DESIGNED, apply pending account activation. This module follows the same
discipline as `../cd-oci-infrastructure/`: no control is claimed as running
until its forced-failure receipt exists. The verification plan below is the
checklist for that apply.

## What this plane holds

| Control | Resource | Defeats |
|---------|----------|---------|
| Evidence vault | S3 + versioning + Object Lock (compliance mode) + CMK | Vendor death, ransomware reaching the off-cloud copy, silent tampering |
| Cross-cloud break-glass | Secrets Manager secret holding the sealed OCI emergency credential | Single-cloud lockout; silent use (any read alerts) |
| Alert-on-use | CloudTrail management events, EventBridge rule (read-only events enabled), Lambda to Telegram | Break-glass becoming a backdoor |
| Native CI federation | IAM OIDC provider + role pinned to repo and main | Long-lived cloud keys in CI |
| Account audit log | CloudTrail into the vault with log file validation | Unattributed account activity |
| Region guard | Explicit deny outside us-east-1 on every created principal | Stolen-credential activity in regions nobody watches |

The uploader identity (`cd-evidence-uploader`) is write-only into the vault.
It cannot read other objects and cannot delete anything; Object Lock refuses
deletion regardless. It is the one long-lived credential in the design,
because OCI instance principals cannot federate into AWS; the tradeoff and
its rotation schedule are recorded in DR-05.

## Deliberate minimalism

Nothing runs here that is not a security control. No compute beyond one
alert Lambda, no VPC, no NAT, no standing services. The region guard denies
created principals everything outside us-east-1 while the trail stays
multi-region, watching the regions where nothing should ever appear.
Checkov: 135 passed, 0 failed, 11 skips each carrying its reason inline.

Monitoring rationale: the alert path is EventBridge to Lambda to Telegram
because it is push-based, near-zero cost, and wakes the operator. Log analytics
is Athena over the vault on demand. A managed SIEM (Datadog or Splunk) is a
documented future lane, not enabled by default: at this scale a standing
SIEM adds cost and surface without adding detection the trail and rules do
not already provide.

## Bootstrap order (fresh account)

1. Billing alarm first. Always.
2. Create the state bucket for this module by hand (or reuse an existing
   one), then `cp backend.hcl.example backend.hcl` and fill it in.
3. `cp terraform.tfvars.example terraform.tfvars`, pick a globally unique
   evidence bucket name.
4. `terraform init -backend-config=backend.hcl && terraform plan`
5. `terraform apply`, then set the break-glass secret VALUE and the
   `/cd/alerts/telegram` SSM parameter out-of-band (never through state).
   Subscribe an email to the `cd-breakglass-alerts` topic so dead-lettered
   alerts have somewhere to land.
6. Wire the nightly evidence upload from the OCI instance using the
   uploader's scoped credentials (distributed via the secrets manager).
   Uploads land under the `evidence/` prefix; `cloudtrail/` is reserved
   for the trail's own delivery.

## Verification plan (receipts to capture at apply)

1. Object Lock: attempt a delete of a locked object as an admin; keep the
   `AccessDenied` with the retention message.
2. Break-glass alarm: read the secret once on purpose; keep the Telegram
   message and the CloudTrail event ID.
3. Federation pinning: run the assume-role step from a non-main ref; keep
   the `AccessDenied` on `sts:AssumeRoleWithWebIdentity`.
4. Uploader containment: attempt `s3:GetObject` and `s3:DeleteObject` as
   the uploader; keep both denials.
5. Drift leg: hand-add a tag in the console, confirm the nightly plan
   flags it, revert.
