# --- TERRAFORM CONFIGURATION (CD-DO-INFRASTRUCTURE) ---
# Foundation for managing CoreDirective's DigitalOcean + Cloudflare infrastructure.
# Local state until Phase 4 (Spaces backend migration after zero-diff confirmed).

terraform {
  required_version = ">= 1.6.3"

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.79"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.52"
    }
    onepassword = {
      source  = "1Password/onepassword"
      version = "~> 3.2"
    }
  }

  # No backend block -- local state for Phase 1-3.
  # Phase 4 will add DO Spaces S3 backend after imports confirmed zero-diff.
}
