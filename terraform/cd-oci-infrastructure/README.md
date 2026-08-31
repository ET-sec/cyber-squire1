# CoreDirective Infrastructure, Oracle Cloud (OCI)

Active infrastructure for the CoreDirective stack. Migrated from DigitalOcean
on 2026-08-19 after the DO droplet and its Terraform state bucket were lost.
The DigitalOcean config is frozen at `../cd-do-infrastructure/` (see its
`ARCHIVED.md`) as a reference only.

## Operating model (how this is meant to be run)

- **Design lives in this repo.** The `.tf` files here and the compose files in
  `COREDIRECTIVE_ENGINE/` are the source of truth for the architecture. Reading
  them tells you the whole stack. You do not read Terraform state to understand
  it.
- **Secrets live in Doppler.** Nothing secret is committed. `env.sh` maps the
  `OCI_*` secrets to `TF_VAR_oci_*` at runtime.
- **State is remote.** Versioned OCI Object Storage with native locking; the
  backend address lives in gitignored `backend.hcl`. Cloudflare R2 remains the
  eventual home (decoupled from the compute vendor), deferred until a one-time
  R2 enable in the Cloudflare dashboard.
- **Runtime is reached by API/SSH with Doppler creds**, not interactive console
  logins. Any machine with this repo + Doppler access can manage the stack.

## What is live (verified 2026-08-19)

- OCI Ampere A1 instance (aarch64, 4 OCPU / 24GB / 150GB), Always Free, $0.
- Core stack: PostgreSQL + n8n + Cloudflare tunnel (`COREDIRECTIVE_ENGINE/
  docker-compose.oci-core.yaml`), fronted by a Cloudflare Access gate in
  front of a live origin.
- Cloudflare edge (Access/ZTNA, WAF, DNS, tunnel) carried over unchanged and is
  serving traffic.

## Layout

| Path | What |
|------|------|
| `providers.tf` `terraform.tf` | OCI + Cloudflare providers, backend (R2 stubbed) |
| `variables.tf` `terraform.tfvars` | Inputs; `oci_*` come from Doppler via `env.sh` |
| `networking.tf` | VCN, subnet, internet gateway, route table, security list |
| `compute.tf` | Ampere A1 instance + Docker cloud-init (data-source image/AD) |
| `cloud-init.yaml` | Installs Docker from Ubuntu repo (NOT download.docker.com, its DNS flaps on OCI first boot) |
| `outputs.tf` | Public IP, instance/vcn IDs, $0 cost note |
| `env.sh` | Doppler -> `TF_VAR_oci_*` loader |
| `policy/` | 8 OPA policies (ported from DO) |
| `cloudflare-adopt/` | Cloudflare tf staged for IMPORT (see its README), do not apply blind, resources are live |

## Deploy / manage

```bash
cd terraform/cd-oci-infrastructure
source ./env.sh                      # Doppler creds, zero Touch ID
terraform plan
terraform apply -var 'ssh_allowed_cidrs=["<your-ip>/32"]'
# A1 out-of-capacity in Ashburn? bump: -var availability_domain_index=1  (or 2)
```

## Remaining work (post-migration, in priority order)

1. **Backups**, the live stack has none. Top risk. Postgres dump to R2 on a
   schedule. Losing data with no backup is exactly what the DO death cost.
2. **Terraform state -> Cloudflare R2**, enable R2 in the CF dashboard, then
   `terraform init -migrate-state` with the backend block in `terraform.tf`.
3. **Re-import n8n workflows**, 14 JSON files in `COREDIRECTIVE_ENGINE/`; the
   DB is fresh (old data died with the droplet). Credentials need reconnecting.
4. **Full stack parity**, bring up the other 15 services on ARM: strip/re-pin
   digests for arm64, rebuild local images (nemo/squire/fluentd), regenerate
   Teleport certs + Keycloak realm + Vault data (lost with the droplet), wire
   falcosidekick -> Splunk.
5. **Adopt the Cloudflare layer into Terraform**, `import`, not apply. See
   `cloudflare-adopt/README.md`.

Full point-in-time record: `.private/INFRA_SNAPSHOT_2026-08-19.md` (gitignored)
and the mirrored Google Drive doc.
