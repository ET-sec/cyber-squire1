# --- TERRAFORM CONFIGURATION (CD-DO-INFRASTRUCTURE) ---
# No backend block -- local state until Phase 4

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
}
