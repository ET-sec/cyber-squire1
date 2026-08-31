# --- TERRAFORM CONFIGURATION (CD-OCI-INFRASTRUCTURE) ---
# Oracle Cloud Infrastructure, Always Free tier. Migrated from DigitalOcean
# 2026-08-19 after the DO droplet and its Spaces state bucket were lost.
#
# STATE BACKEND: OCI Object Storage (native oci backend, Terraform >= 1.12)
# with versioning enabled on the bucket and native state locking. Bucket name,
# namespace, and region live in backend.hcl (gitignored) so account topology
# stays out of the public repo:
#   terraform init -backend-config=backend.hcl
#
# PENDING: migrate to Cloudflare R2 for compute-vendor decoupling (the lesson
# from losing the DO Spaces state bucket along with the droplet). Blocked on
# an operator action: R2 must be enabled in the Cloudflare dashboard (API
# returns code 10042). Until then, bucket versioning is the recovery layer.

terraform {
  required_version = ">= 1.12.0"

  backend "oci" {}

  required_providers {
    oci = {
      source  = "oracle/oci"
      version = ">= 5.30.0"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.52"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}
