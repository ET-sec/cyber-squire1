# --- TERRAFORM CONFIGURATION (CD-OCI-INFRASTRUCTURE) ---
# Oracle Cloud Infrastructure, Ampere A1 Flex shapes. Migrated from DigitalOcean
# 2026-08-19 after the DO droplet and its Spaces state bucket were lost.
#
# STATE BACKEND: OCI Object Storage (native oci backend, Terraform >= 1.12)
# with versioning enabled on the bucket and native state locking. Bucket name,
# namespace, and region live in backend.hcl (gitignored) so account topology
# stays out of the public repo:
#   terraform init -backend-config=backend.hcl
#
# State and compute share a vendor here, which is the lesson from losing the
# DO Spaces state bucket along with the droplet. Moving state to Cloudflare R2
# needs an operator action first: R2 must be enabled in the dashboard (the API
# returns code 10042). Bucket versioning is the recovery layer either way.

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
