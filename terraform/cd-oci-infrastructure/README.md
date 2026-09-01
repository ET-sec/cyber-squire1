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
- **CI holds no cloud keys.** The nightly drift check authenticates by
  exchanging GitHub's OIDC token for a short-lived OCI session token, mapped to
  a read-only principal. See `.github/workflows/drift-check.yml`.
- **Runtime is reached by API/SSH with Doppler creds**, not interactive console
  logins. Any machine with this repo + Doppler access can manage the stack.

## What is live (verified 2026-08-31)

- OCI Ampere A1 instance (aarch64, 4 OCPU / 24GB / 150GB), Always Free, $0.
- Core stack: PostgreSQL + n8n + Cloudflare tunnel (`COREDIRECTIVE_ENGINE/
  docker-compose.oci-core.yaml`), fronted by a Cloudflare Access gate in
  front of a live origin. The remaining services of the full stack are pending
  the ARM rebuild (see `COREDIRECTIVE_ENGINE/docker-compose.yaml` header).
- Cloudflare edge (Access/ZTNA, WAF, DNS, tunnel) carried over unchanged and is
  serving traffic.
- Data protection layer (`data_protection.tf`): customer-managed encryption
  key in OCI Vault wrapping both buckets, nightly PostgreSQL + n8n backups to a
  retention-locked bucket (deletes are refused until the window expires, even
  for the account owner), uploaded by instance principal so the host stores no
  cloud credentials, plus a monthly timed restore test.
- Nightly drift detection: `terraform plan` runs in CI against live OCI on a
  schedule; any hand-made change alerts within 24 hours.

## Layout

| Path | What |
|------|------|
| `providers.tf` `terraform.tf` | OCI + Cloudflare providers, remote `oci` backend, ApiKey/SecurityToken auth switch |
| `variables.tf` | Inputs; `oci_*` come from Doppler via `env.sh` locally, or the session token in CI |
| `terraform.tfvars.example` | Template for the gitignored `terraform.tfvars`, copy and fill |
| `backend.hcl.example` | Template for the gitignored backend address, copy and fill |
| `networking.tf` | VCN, subnet, internet gateway, route table, security list |
| `compute.tf` | Ampere A1 instance + Docker cloud-init (data-source image/AD) |
| `data_protection.tf` | KMS vault + customer-managed key, state/backup buckets, retention rule, backup-agent dynamic group + least-privilege policies |
| `cloud-init.yaml` | Installs Docker from Ubuntu repo (NOT download.docker.com, its DNS flaps on OCI first boot) |
| `outputs.tf` | Public IP, instance/vcn IDs, $0 cost note |
| `env.sh` | Doppler -> `TF_VAR_oci_*` loader (gitignored) |
| `policy/` | 8 OPA policies (deny public firewall, deny unencrypted storage, deny root SSH key, and more) |

The Cloudflare edge config (Access apps, WAF, DNS, tunnel) is managed in a
local-only module staged for `terraform import`; it publishes here once its
identity values are parameterized.

## Run this yourself (replication)

Everything below runs on OCI Always Free tier: expected cost is $0.

Prerequisites: an OCI account, Terraform >= 1.12, an API signing key for your
user (Identity > My profile > API keys).

```bash
cd terraform/cd-oci-infrastructure

# 1. Your inputs (both files are gitignored, nothing you write here is committed)
cp terraform.tfvars.example terraform.tfvars     # fill in region + bucket name
cp backend.hcl.example backend.hcl               # fill in bucket + namespace

# 2. Credentials as environment variables (Doppler optional, any env source works)
export TF_VAR_oci_tenancy_ocid=... TF_VAR_oci_user_ocid=... \
       TF_VAR_oci_fingerprint=... TF_VAR_oci_private_key="$(cat ~/.oci/key.pem)"

# 3. First run bootstraps against local state, then migrates to the bucket
terraform init                                    # local backend first
terraform apply -target=oci_objectstorage_bucket.tfstate
terraform init -migrate-state -backend-config=backend.hcl
terraform plan
# A1 out-of-capacity in Ashburn? bump: -var availability_domain_index=1  (or 2)
```

To reproduce the keyless CI auth (GitHub OIDC to OCI token exchange), the
recipe is in `.github/workflows/drift-check.yml`: create an OCI Identity Domain
confidential app with the token-exchange grant, an identity propagation trust
whose rule pins `sub eq repo:<you>/<repo>:ref:refs/heads/main`, and a service
user in a read-only group. The workflow file documents the two non-obvious
parts (Oracle's `urn:oci:token-type:oci-upst` token type and the SDK's
fingerprint requirement for session auth).

## Remaining work (post-migration, in priority order)

1. **Terraform state -> Cloudflare R2**: state is already remote (versioned OCI
   bucket with locking); moving it off the compute vendor waits on a one-time
   R2 enable in the CF dashboard, then `terraform init -migrate-state`.
2. **Re-import n8n workflows**: 14 JSON files in `COREDIRECTIVE_ENGINE/`; the
   DB is fresh (old data died with the droplet). Credentials need reconnecting.
3. **Full stack parity**: bring up the remaining services on ARM: strip/re-pin
   digests for arm64, rebuild local images (nemo/squire/fluentd), regenerate
   Teleport certs + Keycloak realm + Vault data (lost with the droplet), wire
   falcosidekick -> Splunk.
4. **Adopt the Cloudflare layer into Terraform**: `import`, not apply, then
   parameterize and publish the module.

Full point-in-time record: `.private/INFRA_SNAPSHOT_2026-08-19.md` (gitignored)
and the mirrored Google Drive doc.
