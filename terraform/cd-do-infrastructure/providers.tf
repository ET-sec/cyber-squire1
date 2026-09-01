# --- PROVIDER CONFIGURATION (CD-DO-INFRASTRUCTURE) ---
# All credentials via environment variables -- never inline

# DigitalOcean -- reads DIGITALOCEAN_TOKEN env var
provider "digitalocean" {}

# Cloudflare v4 -- reads CLOUDFLARE_API_KEY + CLOUDFLARE_EMAIL env vars (Global API Key auth)
provider "cloudflare" {}

# Datadog -- reads DD_API_KEY and DD_APP_KEY env vars
# Site: datadoghq.com (DigitalOcean region)
provider "datadog" {
  api_url = "https://api.datadoghq.com"
}

# 1Password provider removed -- secrets now come from Doppler env vars
# Run: doppler run -- terraform plan
