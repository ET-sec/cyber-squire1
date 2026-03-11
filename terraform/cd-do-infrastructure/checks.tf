# --- HEALTH CHECKS (CD-DO-INFRASTRUCTURE) ---
# Non-blocking assertions that validate service reachability
# These produce warnings during plan/apply but never block operations
# Requires: Terraform >= 1.5.0 (installed: 1.14.3)
# Requires: hashicorp/http provider (declared in terraform.tf by plan 05-04)

check "n8n_reachable" {
  data "http" "n8n_health" {
    url = "https://n8n.tigouetheory.com/healthz"

    request_timeout_ms = 5000
  }

  assert {
    condition     = data.http.n8n_health.status_code == 200
    error_message = "n8n dashboard is not responding at https://n8n.tigouetheory.com/healthz (HTTP ${data.http.n8n_health.status_code})."
  }
}

check "ssh_tunnel_reachable" {
  data "http" "ssh_tunnel_check" {
    url = "https://ssh.tigouetheory.com"

    request_timeout_ms = 5000
  }

  assert {
    condition     = data.http.ssh_tunnel_check.status_code > 0
    error_message = "SSH tunnel endpoint ssh.tigouetheory.com is not reachable."
  }
}
