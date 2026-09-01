# ARCHIVED: DigitalOcean infrastructure (frozen 2026-08-19)

This directory is **no longer active**. The DigitalOcean droplet and its
Spaces state bucket were lost when the account lapsed. These files are kept as a **working reference** for the architecture,
not as live infrastructure. Do not `terraform apply` here.

**Active infrastructure lives in `../cd-oci-infrastructure/`** (Oracle Cloud,
Always Free ARM). The Cloudflare layer (Access/ZTNA, WAF, DNS, tunnel) and the
per-agent machine-identity work carry over from here to there.

Why keep it: it documents the exact DO-era stack (droplet, VPC, firewall,
tunnel routes, WAF rules) so nothing about what existed is lost, the way the
AWS setup was lost with no record.

**Sanitization note (2026-08-31):** host-specific literals in this archived
config (edge hostnames, engine filesystem path, bucket names, Datadog site)
were replaced with generic placeholders during the Phase 20.1 truth sweep.
The design is preserved; the identifiers are not real.
