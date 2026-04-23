# --- CLOUDFLARE TUNNEL CONFIG (CD-DO-INFRASTRUCTURE) ---
# Imported in Phase 3 (2026-03-11)
# Tunnel resource itself stays UNMANAGED (API cannot return secret). Only config is managed.
# Uses cloudflare_tunnel_config (v4 name, NOT cloudflare_zero_trust_tunnel_cloudflared_config which is v5)
# WARNING: After import, ALL tunnel config changes must go through Terraform. Dashboard edits cause drift.

resource "cloudflare_tunnel_config" "cd_alpha" {
  account_id = var.cf_account_id
  tunnel_id  = var.cf_tunnel_id

  config {
    ingress_rule {
      hostname = "n8n.tigouetheory.com"
      service  = "http://localhost:5678"
      origin_request {
        connect_timeout        = "30s"
        tls_timeout            = "10s"
        tcp_keep_alive         = "30s"
        keep_alive_timeout     = "1m30s"
        keep_alive_connections = 100
        proxy_address          = "127.0.0.1"
        no_tls_verify          = false
        access {
          required  = false
          team_name = ""
        }
      }
    }

    ingress_rule {
      hostname = "ssh.tigouetheory.com"
      service  = "ssh://localhost:22"
    }

    # Langfuse v3 self-hosted UI (Phase 17-04)
    ingress_rule {
      hostname = "langfuse.tigouetheory.com"
      service  = "http://localhost:3100"
      origin_request {
        connect_timeout        = "30s"
        tls_timeout            = "10s"
        tcp_keep_alive         = "30s"
        keep_alive_timeout     = "1m30s"
        keep_alive_connections = 100
        proxy_address          = "127.0.0.1"
        no_tls_verify          = false
        access {
          required  = false
          team_name = ""
        }
      }
    }

    # Squire FastAPI surface (Phase 17-09)
    ingress_rule {
      hostname = "squire.tigouetheory.com"
      service  = "http://localhost:8020"
      origin_request {
        connect_timeout        = "30s"
        tls_timeout            = "10s"
        tcp_keep_alive         = "30s"
        keep_alive_timeout     = "1m30s"
        keep_alive_connections = 100
        proxy_address          = "127.0.0.1"
        no_tls_verify          = false
        access {
          required  = false
          team_name = ""
        }
      }
    }

    # REQUIRED: catch-all rule must be last
    ingress_rule {
      service = "http_status:404"
    }
  }
}
