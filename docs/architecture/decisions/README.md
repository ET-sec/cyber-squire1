# Decision Records

One record per security control shipped in Phase 20.1 (the SCS-grade cloud
hardening pass, 2026-08-31). Each follows the same shape: the problem, the
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
