# DR-03: Data Protection, Keys and Immutable Backups (Phase 20.1-03)

**Date:** 2026-08-31
**Status:** Implemented and verified (verification transcript in the private evidence store)

## Problem
Two exposures. One: both buckets were encrypted with Oracle-managed keys, meaning no revocation power, no rotation policy of our own, and no audit trail of key use. Two: there were no offsite backups of the production PostgreSQL and n8n data at all since the OCI migration, and the DigitalOcean death already proved what happens when data and its only copies share a fate.

## Options considered
1. **Customer-managed key (CMK), software-protected, in OCI Vault.** Free (unlimited software key versions, verified against Oracle's Always Free docs), Terraform-managed, revocable, auditable. Added risk: self-inflicted key deletion, mitigated by OCI's mandatory deletion waiting period and by the key existing only as Terraform config (no hand-deletes).
2. **HSM-protected key.** Bills past 20 key versions. No threat in this model requires hardware key isolation. Rejected on cost with no security payoff at this scale.
3. **Stay on Oracle-managed keys.** Zero effort, but concedes the control and audit story, which is half the point of the phase. Rejected.

For backups: retention rule on the bucket (chosen) vs restic append-only (rejected: append-only is a transport restriction, not a storage guarantee; it does not survive an attacker who reaches the storage API).

## Decision
Software CMK wrapping both buckets, 30-day retention rule on cd-backups, nightly backup + monthly timed restore via cron, and the host authenticating by instance principal so the backup job holds zero stored credentials.

## The two deliberate tradeoffs
1. **The retention rule is UNLOCKED.** A locked rule is irreversible for its whole duration; on a personal free-tier account, a sizing mistake with a locked rule cannot be undone. Unlocked means a tenancy admin could remove the rule and then delete objects, so the guarantee today is "ransomware with stolen writer credentials fails" and "admin fat-fingers fail," not "malicious admin fails." Re-evaluate locking at phase close.
2. **The writer cannot delete.** The instance's policy grants create/read/inspect only. Even before the retention rule, a compromised backup script cannot destroy history. Defense in depth: policy layer plus retention layer, different failure modes.

## Blast radius if this fails
- Key deleted: data unreadable after the waiting period expires. Mitigations: deletion delay (cancelable), key config in Terraform, no console operations.
- Key service outage: reads/writes to CMK buckets fail until recovery; state and backups are unavailable, not lost.
- Retention mis-sized too long: storage grows past free tier; at ~28KB/day this is arithmetic, not risk.
- Instance compromised: attacker can write junk backups and read old ones (data exposure), but cannot delete or overwrite history. Restore tests would surface junk within a month; tightening that window is the Stage 3 alerting item.

## Verification (all live, 2026-08-31)
1. CMK attached to both buckets, confirmed by bucket get.
2. Instance principal authenticated with no credential file on the host.
3. First backup uploaded; nightly + monthly restore crons installed.
4. Delete refused twice: instance principal (404, permission absent) and tenancy admin (403 RetentionRuleViolation).
5. Restore test: 76 tables into a scratch container, RTO 5 seconds, logged.
6. Key rotated; pre-rotation object still decrypts. Envelope model: rotation re-wraps data keys, never re-encrypts data.

## The interview version
"Both storage buckets encrypt under a customer-managed key I provision in Terraform, and I proved the envelope model by rotating the key and reading back a pre-rotation backup: rotation is a re-wrap, not a re-encryption project. Backups upload nightly under an instance principal, so the host holds no cloud credential and its policy can't delete anything even if the job is compromised. The bucket's retention rule then blocks deletion for 30 days for everyone, including me as the account admin, and I keep the 403 from my own delete attempt as evidence. Restores run monthly into a scratch database with the recovery time logged, because a backup that has never restored is a hypothesis."

## Re-evaluation triggers
- Phase close: decide on locking the retention rule (irreversibility vs malicious-admin coverage).
- Data growth changes the retention arithmetic (currently ~1MB per 30-day window against 20GB).
- Stage 3 lands: wire backup-failure and restore-failure alerts into the drift alert path.
