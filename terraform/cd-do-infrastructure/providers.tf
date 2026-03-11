# --- PROVIDER CONFIGURATION (CD-DO-INFRASTRUCTURE) ---
# All credentials via environment variables -- never inline

# DigitalOcean -- reads DIGITALOCEAN_TOKEN env var
provider "digitalocean" {}

# Cloudflare v4 -- reads CLOUDFLARE_API_KEY + CLOUDFLARE_EMAIL env vars (Global API Key auth)
provider "cloudflare" {}

# 1Password provider removed -- secrets now come from Doppler env vars
# Run: doppler run -- terraform plan
