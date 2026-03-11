# --- PROVIDER CONFIGURATIONS ---
# All credentials via environment variables. Never inline tokens.
# Source env.sh before running terraform commands.

# DigitalOcean -- reads DIGITALOCEAN_TOKEN env var
provider "digitalocean" {
  # token set via DIGITALOCEAN_TOKEN env var
  # spaces_access_id set via SPACES_ACCESS_KEY_ID env var (Phase 4)
  # spaces_secret_key set via SPACES_SECRET_ACCESS_KEY env var (Phase 4)
}

# Cloudflare v4 -- reads CLOUDFLARE_API_TOKEN env var
provider "cloudflare" {
  # api_token set via CLOUDFLARE_API_TOKEN env var
}

# 1Password -- desktop app auth via Touch ID (local dev)
# CI/CD will need service account (Phase 4/6)
provider "onepassword" {
  account = "my.1password.com"
}
