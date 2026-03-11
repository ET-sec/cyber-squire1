# All secret lookups in one file -- audit boundary
# For FUTURE use (Phase 4 secrets hardening). Providers auth via env vars now.

data "onepassword_item" "do_token" {
  vault = "kf775hyunb4glc5xdzbpdaqkoe"
  title = "DigitalOcean API Token"
}

data "onepassword_item" "cf_api_token" {
  vault = "kf775hyunb4glc5xdzbpdaqkoe"
  title = "Cloudflare"
}
