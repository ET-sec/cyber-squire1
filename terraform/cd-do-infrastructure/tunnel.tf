# --- CLOUDFLARE TUNNEL CONFIGURATION ---
# Tunnel resource itself stays UNMANAGED (API cannot return secret). Only config is managed.
# Uses cloudflare_tunnel_config (v4 name, NOT v5 cloudflare_zero_trust_tunnel_cloudflared_config).
# Import: terraform import cloudflare_tunnel_config.cd_alpha e4871d2a375f9719092b286866ce26f2/4bcf8238-8a8d-423d-b333-e8fe033d4de9

resource "cloudflare_tunnel_config" "cd_alpha" {
  account_id = var.cf_account_id
  tunnel_id  = var.cf_tunnel_id

  config {
    # n8n dashboard
    ingress_rule {
      hostname = "n8n.tigouetheory.com"
      service  = "http://localhost:5678"
    }

    # SSH access
    ingress_rule {
      hostname = "ssh.tigouetheory.com"
      service  = "ssh://localhost:22"
    }

    # Catch-all (required by Cloudflare)
    ingress_rule {
      service = "http_status:404"
    }
  }
}
