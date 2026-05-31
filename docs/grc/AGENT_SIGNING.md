# Agent Card Signing and Verification

Public-safe trust model for cryptographically signed Agent Cards under
`.agents/`. This document explains how every card is signed, how a verifier
should check a card off CI, and why there is no key to rotate or steal.

## Why we sign Agent Cards

Every agent registered in the platform publishes a YAML or JSON Agent Card
that declares its identity, capabilities, allowed scopes, and OWASP MCP Top
10 control posture. Downstream consumers (the registry index, telemetry
pipelines, third-party auditors) trust those declarations to make access
decisions. Without signatures any contributor could draft a card claiming
elevated scopes, push it to a branch, and try to slip it through review. A
keyless OIDC signature ties each card to the CI workflow run that authored
it, so consumers can refuse any card that is unsigned, signed by a different
workflow, or modified after signing.

## Trust model

Signing is keyless OIDC via Sigstore. The CI runner requests a short-lived
Fulcio X.509 certificate bound to the GitHub Actions workflow identity
(workflow path, branch, repository) at the moment of signing. The signature
plus a Rekor transparency log entry land in a `.sigstore.json` bundle next
to the card. There is no long-lived signing key on disk, in a vault, or in
a HSM. Verification compares the certificate identity to a hardcoded regex,
so a forged signature from any other workflow or any other branch is
rejected.

## Architecture

Signing path:

- `.github/workflows/agent-signing.yml` triggers on push to `main` when any
  file matching `.agents/**.card.json` changes, and on manual
  `workflow_dispatch`.
- The job pins `sigstore/cosign-installer` by 40 character commit SHA and
  installs Cosign `v2.6.0`, which is the first release that emits the
  protobuf bundle format used here. Each card is signed by
  `cosign sign-blob --bundle <card>.sigstore.json --new-bundle-format
  --yes <card>`. Bundles are committed back to `main` as
  `github-actions[bot]`.

Verifying path:

- `.github/workflows/agent-verify.yml` triggers on pull requests that touch
  `.agents/**`. The job installs the same pinned Cosign release and runs the
  shared shell verifier at `scripts/grc/verify_agent_signatures.sh`.
- The verifier reads `--new-bundle-format` bundles and supplies
  `--certificate-identity-regexp` matching the signing workflow path on
  `refs/heads/main`. PRs that introduce unsigned cards, cards signed by a
  different workflow, or cards modified after signing fail this gate.

## Naming convention

Bundle filenames use the double extension form
`<agent_id>.card.json.sigstore.json`, for example
`squire.card.json.sigstore.json` for `squire.card.json`. Phase 20 research
draft D3 floated a single extension alternative
(`<agent_id>.card.sigstore.json`). The double extension form was kept
because `cosign sign-blob --bundle "${card}.sigstore.json"` naturally
appends `.sigstore.json` to the card path. Keeping the natural form means
the signer, verifier, inventory scan, and `.agents/README.md` all share one
glob (`.agents/*.card.json.sigstore.json`) with no string manipulation.

## How to verify off CI

Any consumer can verify a card without GitHub Actions by installing Cosign
`v2.6.0` or newer and running:

```
cosign verify-blob \
  --bundle .agents/squire.card.json.sigstore.json \
  --new-bundle-format \
  --certificate-identity-regexp "https://github\.com/Organization/example-ops-repo/\.github/workflows/agent-signing\.yml@refs/heads/main" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  .agents/squire.card.json
```

The repository path shown above is sanitized to `Organization/example-ops-repo`
per the project sanitization map. The actual repository path is hardcoded
inside the workflow files, which are themselves public; the doc abstracts
the identity to keep the brand string out of public grep harvests. The
`--new-bundle-format` flag is required when verifying bundles produced by
Cosign `v2.6.0` or newer signers because the bundles are encoded as protobuf
rather than legacy JSON.

## Failure modes

- Missing bundle file next to a card: the signing workflow has not yet run
  for that card. Push the card to `main` or trigger
  `workflow_dispatch` on `agent-signing.yml`.
- Invalid certificate identity: the signature came from a different
  workflow path or branch, which is the expected behavior for a forgery
  attempt. The card must be re-signed by the official signing workflow.
- Bundle format mismatch: the caller omitted `--new-bundle-format`. Cosign
  cannot parse a protobuf bundle as legacy JSON; add the flag and re-run.
- Expired Fulcio certificate: short-lived certs expire quickly. Re-sign by
  triggering `workflow_dispatch` on `agent-signing.yml`, which mints a fresh
  certificate for the run.

## Key non-rotation policy

There is no private key. Sigstore Fulcio issues a short-lived certificate
for each signing event and Rekor records the event in a public transparency
log. There is nothing to rotate, nothing to escrow, and nothing for an
attacker to exfiltrate from disk. The only sensitive trust anchor is the
GitHub Actions OIDC token, which the platform already protects as part of
the workflow run identity.
