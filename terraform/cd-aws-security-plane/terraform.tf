# cd-aws-security-plane
#
# AWS holds the security and evidence plane for a platform whose workloads
# run on OCI behind a Cloudflare edge. Evidence, backup replicas, and the
# break-glass credential live here so that no single vendor failure can
# blind, lock out, or silently erase the operator. That requirement comes
# from the 2026-08 provider loss that took a host and its state bucket in
# one event.
#
# State backend: partial config, same pattern as cd-oci-infrastructure.
#   terraform init -backend-config=backend.hcl
# backend.hcl is gitignored; see backend.hcl.example.

terraform {
  required_version = ">= 1.9.0"

  backend "s3" {}

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.6"
    }
  }
}
