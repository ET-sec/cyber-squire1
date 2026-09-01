# DR-02: Workload Identity for CI (Phase 20.1-02)

**Date:** 2026-08-31
**Status:** Spike proven end to end; promotion to production auth pending

## Problem
The deployment pipeline needs to talk to OCI. The default pattern, long-lived cloud keys in GitHub repo secrets, means anyone who can read repo secrets (compromised action, leaked runner, over-scoped collaborator) holds standing production credentials. User-facing federation already exists (Cloudflare Access at the edge), but the pipeline's trust boundary had nothing.

## Options considered
1. **OIDC (OpenID Connect) token exchange via OCI Identity Domain.** GitHub mints a signed JWT (JSON Web Token) per workflow run; OCI validates it against GitHub's published keys and a trust rule pinned to repo and branch, then issues a user principal session token (UPST) that dies in minutes. No stored cloud keys. Risk going in: OCI has no first-class GitHub federation like AWS/Azure/GCP, so this rides the generic RFC 8693 token exchange, which is underdocumented.
2. **Static CI credential, tightly scoped, auto-rotated via Doppler.** The fallback if the exchange dead-ended. Still a standing secret; rotation shrinks but does not close the window.

## Decision
Option 1. The spike proved it live on 2026-08-31: positive run authenticated to OCI with zero stored keys, and a run from an unpinned branch was refused with "No rules matched from given token to find impersonation user." Evidence with run URLs lives in the verification transcript in the private evidence store.

## How it actually works (the interview version)
"GitHub signs an identity token for each workflow run with the repo and branch baked into the sub claim. My OCI identity domain holds a trust that only accepts that issuer, verifies the signature against GitHub's public keys, and maps exactly one sub value to a service user with minimal permissions. The workflow trades that JWT for a session token bound to a keypair generated inside the run, lives minutes, and dies with the job. I tested both directions on purpose: the pinned branch authenticates, a different branch gets a 401, and I keep both run logs as evidence. The secrets left in GitHub are exchange-client credentials that are useless without a valid GitHub-signed token matching the trust rule."

## Blast radius if this fails
- Trust misconfigured too wide (rule wildcard): any branch or fork matching the rule impersonates cd-ci. Mitigated: exact-match rule, one branch, no wildcards.
- GitHub OIDC issuer compromise: an attacker minting valid GitHub JWTs impersonates any workload identity on any cloud; industry-wide event, not specific to this design.
- Federation path down or trust broken: pipeline cannot deploy. Mitigation is the break-glass credential with alert-on-use (promotion checklist; not yet built).
- cd-ci over-permissioned later: the identity is only as safe as its IAM policy. Policy stays minimal and reviewed per addition.

## Verification
1. Positive: exchange HTTP 200, authenticated `oci os ns get` succeeded, zero cloud keys in repo secrets used.
2. Negative: wrong-branch run refused at the exchange with 401.
3. Client sanity: client_credentials grant verified separately, isolating exchange-specific failures during debugging.

## What the debugging taught
Four failures, each isolating one layer: wrong requested_token_type URN (parameter layer), quoted rule value (trust-rule layer), a schema with no token-exchange grant, proving authorization lives in the trust's oauthClients (authorization-model layer), and a trailing newline breaking the CLI's token decode (client layer). Debugging a federation chain means walking the layers in order: parameters, signature, trust rule, client consumption.

## Re-evaluation triggers
- OCI ships first-class GitHub federation: simplify to it.
- Workflow merges to main: re-pin the trust rule to refs/heads/main in the same PR.
- Audience validation: add aud claim check to the trust before production promotion.
