# --- PROVIDER CONFIGURATION (CD-DO-INFRASTRUCTURE) ---
# All credentials via environment variables -- never inline

# DigitalOcean -- reads DIGITALOCEAN_TOKEN env var
provider "digitalocean" {}

# Cloudflare v4 -- reads CLOUDFLARE_API_TOKEN env var
provider "cloudflare" {}

# 1Password -- desktop app auth via Touch ID
provider "onepassword" {
  account = "my.1password.com"
}
