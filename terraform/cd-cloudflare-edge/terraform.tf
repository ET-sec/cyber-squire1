# cd-cloudflare-edge: the edge plane as code.
#
# Cloudflare holds the zero-trust edge for the platform: Access in front of
# every admin surface, the custom WAF, the per-path rate limit, DNS, and the
# tunnel ingress. These resources have been live since the DigitalOcean era
# and were orphaned when that Terraform state died with its bucket. This
# root adopts them by IMPORT, never by create, so nothing that currently
# gates admin traffic is ever recreated underneath the operator.
#
# State: same OCI Object Storage bucket as the compute plane, separate key,
# so a mistake in one plane cannot corrupt the other's state. Partial
# backend config lives in the gitignored backend.hcl.
#
# Provider auth: CLOUDFLARE_API_KEY + CLOUDFLARE_EMAIL from the environment
# (Doppler locally). No credential is stored in this repo or in CI.

terraform {
  required_version = ">= 1.6.0"

  backend "oci" {}

  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.52"
    }
  }
}

provider "cloudflare" {}
