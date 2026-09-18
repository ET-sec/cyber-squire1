# Decision Records

One record per security control shipped since the SCS-grade cloud hardening
pass of 2026-08-31. Each follows the same shape: the problem, the
options weighed, the blast radius if the control fails, how it was verified
by attacking it, and what the same design looks like at enterprise scale.

These are published deliberately: finished code shows what was built, and
these show why. Raw command transcripts live in a private evidence store;
everything quoted here (HTTP status codes, error strings, timings) is from
live execution, not reconstruction.

| Record | Control | Proven by |
|--------|---------|-----------|
| [DR-01](DR-01-terraform-remote-state.md) | Remote locked Terraform state | Concurrent runs fight, loser gets HTTP 412 |
| [DR-02](DR-02-workload-identity.md) | Keyless CI via OIDC token exchange | Wrong-branch run refused with 401 |
| [DR-03](DR-03-data-protection.md) | Customer-managed keys + immutable backups | Owner delete refused with 403; restore timed |
| [DR-04](DR-04-drift-detection-and-findings-pipeline.md) | Nightly drift detection + self-updating POA&M | Hand-made change detected and alerted |
| [DR-05](DR-05-aws-security-plane.md) | AWS security and evidence plane (multi-cloud custody split) | Custody split held behind an apply gate; receipts land at apply |
| [DR-06](DR-06-webhook-trust-at-the-edge.md) | Webhook trust at the edge (Access, WAF, Telegram carve-out), edge plane adopted as code | Applied 2026-09-02; workflow-side controls in residuals |
| [DR-07](DR-07-vault-licence-and-seal.md) | Vault under BUSL, cloud KMS seal through the instance identity, two engines; the identity tier's exposure | Applied 2026-09-15; unsealed with a stored key, one dynamic credential read, transit round trip |
