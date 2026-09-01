# --- PROVIDER CONFIGURATION (CD-OCI-INFRASTRUCTURE) ---
# All OCI credentials come from Doppler via TF_VAR_oci_* env vars.
# The private key is passed as PEM content (not a file path), so nothing
# secret needs to live on disk. Run with: ./env.sh && terraform plan
# or: doppler run -- terraform plan  (after env.sh maps OCI_* -> TF_VAR_oci_*)

# Two auth paths, same provider block:
#  - Local (ApiKey): credentials from Doppler via TF_VAR_oci_*, nothing on disk.
#  - CI (SecurityToken): the drift workflow exchanges GitHub's OIDC JWT for a
#    short-lived UPST and writes an ~/.oci/config DEFAULT profile pointing at
#    it. No long-lived cloud key exists anywhere in CI.
provider "oci" {
  auth                = var.oci_auth
  config_file_profile = var.oci_auth == "SecurityToken" ? "DEFAULT" : null
  tenancy_ocid        = var.oci_tenancy_ocid
  user_ocid           = var.oci_user_ocid != "" ? var.oci_user_ocid : null
  fingerprint         = var.oci_fingerprint != "" ? var.oci_fingerprint : null
  private_key         = var.oci_private_key != "" ? var.oci_private_key : null
  region              = var.oci_region
}

# Cloudflare v4 reads CLOUDFLARE_API_KEY + CLOUDFLARE_EMAIL env vars.
# Carries over unchanged from the DO stack; the ZTNA/WAF/DNS layer is
# provider-independent and does not care that compute moved to OCI.
provider "cloudflare" {}
