# --- TERRAFORM CONFIGURATION (CD-DO-INFRASTRUCTURE) ---
# Remote state on DO Spaces (S3-compatible) — migrated in Phase 4

terraform {
  required_version = ">= 1.6.3"

  backend "s3" {
    endpoints = {
      s3 = "https://nyc3.digitaloceanspaces.com"
    }
    bucket = "cd-terraform-state"
    key    = "cd-do-infrastructure/terraform.tfstate"
    region = "us-east-1" # Required by S3 backend but ignored by DO Spaces

    # DO Spaces doesn't support these S3 features
    skip_credentials_validation = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true
    skip_s3_checksum            = true
  }

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.79"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.52"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
    http = {
      source  = "hashicorp/http"
      version = "~> 3.4"
    }
  }
}
