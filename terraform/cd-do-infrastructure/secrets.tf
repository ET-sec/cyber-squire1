# --- SECRETS PIPELINE (CD-DO-INFRASTRUCTURE) ---
# All secrets flow through Doppler (coredirective-engine / prd)
# Usage: doppler run -- terraform plan
#
# Required env vars for Terraform:
#   DIGITALOCEAN_TOKEN     — DO provider auth (auto-read by provider)
#   CLOUDFLARE_API_KEY     — CF provider auth (Global API Key)
#   CLOUDFLARE_EMAIL       — CF provider auth (account email)
#   SPACES_ACCESS_KEY      — DO Spaces backend auth (passed via -backend-config on init)
#   SPACES_SECRET_KEY      — DO Spaces backend auth (passed via -backend-config on init)
#
# Doppler is the runtime secrets manager. 1Password is the source of truth for rotation.
# No .tfvars files contain secrets. No secrets are hardcoded in .tf files.
# State is remote on DO Spaces (tf-state-bucket bucket, nyc3, versioning enabled).
#
# Backend init command:
#   terraform init \
#     -backend-config="access_key=$(doppler secrets get SPACES_ACCESS_KEY --plain)" \
#     -backend-config="secret_key=$(doppler secrets get SPACES_SECRET_KEY --plain)"
