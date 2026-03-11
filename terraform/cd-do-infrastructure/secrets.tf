# --- SECRET LOOKUPS (AUDIT BOUNDARY) ---
# All secret lookups in one file -- audit boundary.
# Currently for FUTURE use (Phase 4 secrets hardening).
# Providers auth via env vars (source env.sh) for Phase 1-3.

data "onepassword_item" "do_token" {
  vault = "kf775hyunb4glc5xdzbpdaqkoe" # Core Infra vault UUID
  title = "DigitalOcean API"
}

data "onepassword_item" "cf_api_token" {
  vault = "kf775hyunb4glc5xdzbpdaqkoe" # Core Infra vault UUID
  title = "Cloudflare API"
}

# Future additions (Phase 4+):
# - Datadog API key
# - Telegram bot token
# - OpenClaw API key
