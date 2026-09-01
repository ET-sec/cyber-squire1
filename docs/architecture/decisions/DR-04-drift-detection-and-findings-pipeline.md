# DR-04: Drift Detection & Findings Pipeline (Phase 20.1-04)

**Date:** 2026-08-31
**Status:** Implemented and verified (verification transcript in the private evidence store)

## Problem
Two blind spots. One: infrastructure could be changed by hand (console, CLI)
and nothing would notice; Stage 0 proved this is real, not theoretical, when
the first remote-state plan caught a hand-added firewall rule that code review
never saw. Two: scanner findings (Trivy, Checkov, Gitleaks) died in CI logs
and the GitHub Security tab while the POA&M stayed a hand-curated document,
which means it was always somewhat wrong.

## Trust boundary
The drift job crosses the pipeline-to-cloud boundary with the Stage 1 token
exchange: GitHub's signed JWT for a minutes-lived session token, no stored
cloud keys. The principal (`cd-ci`) is deliberately one-directional: a single
`read all-resources` policy statement. It can see everything Terraform
manages and change nothing. The plan also runs `-lock=false`: a read-only
job that could wedge the state lock would be a denial-of-service on deploys.

## Options considered
1. **Scheduled plan in GitHub Actions (chosen).** Free on a public repo,
   authenticates with the already-proven federation, and the alert artifact
   is a public run URL. Constraint: a public repo means plan output is
   radioactive (resource identifiers, network detail), so the log gets
   addresses only and the full plan travels to Telegram as a private
   document. No artifact uploads: artifacts on public repos are downloadable.
2. **Drift detection from the instance (cron on the instance).** Rejected: the
   instance would need read access to all of tenancy (scope creep on the
   instance principal) and the evidence trail would be a private log instead
   of a public run.
3. **OCI-native config monitoring (Cloud Guard).** Rejected for now: detects
   posture violations, not code-versus-reality divergence; it answers a
   different question than "did someone bypass code review".

For the findings ledger:
1. **Script-owned intake queue, separate file (chosen).** poam_sync.py owns
   `POAM_AUTO_FINDINGS.md` entirely; the curated register keeps human
   judgment (compensating controls, milestones). Machines write the queue,
   humans make the decisions. Dedup by content fingerprint, auto-close when
   a scanned source stops reporting, reopen on regression.
2. **Scripts editing the curated POA&M in place.** Rejected: merging
   generated rows into a hand-written document destroys the authorship
   boundary and eventually the document.

## Blast radius
- Drift job compromised: attacker gets a read-only view of the tenancy for
  minutes. Cannot mutate, cannot delete backups (Stage 2 policy), cannot
  take the state lock. Worst case is reconnaissance, alerted by any use of
  the credentialed path outside the pinned sub claim.
- Trust rule now accepts exactly one subject: `refs/heads/main`, and main is
  branch-protected. The spike-branch rule was removed at promotion because
  an unprotected branch with authentication rights lets any push mint cloud
  access; with main-only, every credential the cloud issues traces to a
  commit that passed review and both required checks.
- Telegram token on the instance (backup alerting): root-only file, blast
  radius is "send messages as the bot", rotatable in one place.

## Tradeoffs accepted
- `-lock=false` means a drift plan could read state mid-write from a
  concurrent apply and report a phantom diff for one cycle. Accepted: false
  positive for one night versus a job that can block deploys.
- Auto-close trusts the scanner: a finding that stops being reported closes
  without human sign-off. Accepted for the intake queue only; anything
  graduated to the curated register closes by human decision.
- The gitleaks tripwires (custom sanitization rules) generate findings that
  are hygiene debt, not vulnerabilities. Accepted: 70 of the 75 initial rows
  are exactly the Stage 4 cleanup list, generated mechanically instead of by
  rereading every doc.

## Verification (all live, 2026-08-31)
1. Clean plan on the new auth path: run 33403730830, exit 0.
2. Deliberate console-style change (freeform tag on the instance): run
   33403878182, exit 2, resource identified, Telegram message + private plan
   document delivered, run red.
3. Revert, clean: run 33403970499, exit 0. First main run: 33404231940.
4. poam_sync.py: byte-identical ledger on rerun; synthetic finding adds
   exactly one row; absent finding auto-closes (full transcript in evidence).
5. SHA-pin audit: 0 unpinned `uses:` across all 14 workflows (codeql.yml was
   the last gap); every workflow has a `permissions:` block.
6. Backup-failure alert: forced failure fired Telegram; real backup still
   succeeds.

## What I'd do at enterprise scale
Drift: this pattern per state root, fanned out by workspace, with exit-2
results opening tickets automatically instead of messaging a human, and
Cloud Guard / AWS Config layered on for posture (they complement, not
replace, code-versus-reality). Findings: the intake queue becomes a real
system (DefectDojo or a data warehouse table), fingerprints become the join
key across scanners, and SLA clocks (per severity) hang off first_seen. The
authorship boundary survives at any scale: scanners write findings, humans
write acceptances.

## Re-evaluation triggers
- Terraform adds first-class read-only plan tokens or OCI ships native
  GitHub federation: revisit the exchange plumbing.
- Repo goes private or a private mirror appears: plan output handling can
  relax.
- poam_sync gains a second consumer (dashboards): promote the ledger from
  markdown to structured data (YAML/JSON) with the markdown rendered from it.
