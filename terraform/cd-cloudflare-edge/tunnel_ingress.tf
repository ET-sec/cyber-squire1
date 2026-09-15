# The tunnel's ingress, as code (plan 24-02).
#
# The tunnel is token-run; its ingress lived in the dashboard and in no state.
# This resource was IMPORTED from the live configuration and proved a zero-diff
# plan before the identity provider's rules were added, so the routes that
# carry the operator's own SSH session and the orchestration dashboard were
# never rewritten underneath them. Rules are an ordered list: the first match
# wins and the catch-all answers not found.

resource "cloudflare_tunnel_config" "cyber_squire" {
  account_id = var.cf_account_id
  tunnel_id  = var.cf_tunnel_id

  config {
    ingress_rule {
      hostname = local.n8n_host
      service  = "http://localhost:5678"
      origin_request {
        connect_timeout          = "30s"
        tls_timeout              = "10s"
        tcp_keep_alive           = "30s"
        no_happy_eyeballs        = false
        keep_alive_connections   = 100
        keep_alive_timeout       = "1m30s"
        http_host_header         = ""
        origin_server_name       = ""
        ca_pool                  = ""
        no_tls_verify            = false
        disable_chunked_encoding = false
        bastion_mode             = false
        proxy_address            = "127.0.0.1"
        proxy_port               = 0
        proxy_type               = ""
        http2_origin             = false
        access {
          aud_tag   = []
          required  = false
          team_name = ""
        }
      }
    }
    ingress_rule {
      hostname = "ssh.${var.domain}"
      service  = "ssh://localhost:22"
    }
    ingress_rule {
      hostname = "langfuse.${var.domain}"
      service  = "http://localhost:3100"
      origin_request {
        connect_timeout          = "30s"
        tls_timeout              = "10s"
        tcp_keep_alive           = "30s"
        no_happy_eyeballs        = false
        keep_alive_connections   = 100
        keep_alive_timeout       = "1m30s"
        http_host_header         = ""
        origin_server_name       = ""
        ca_pool                  = ""
        no_tls_verify            = false
        disable_chunked_encoding = false
        bastion_mode             = false
        proxy_address            = "127.0.0.1"
        proxy_port               = 0
        proxy_type               = ""
        http2_origin             = false
        access {
          aud_tag   = []
          required  = false
          team_name = ""
        }
      }
    }
    ingress_rule {
      hostname = "squire.${var.domain}"
      service  = "http://localhost:8020"
      origin_request {
        connect_timeout          = "30s"
        tls_timeout              = "10s"
        tcp_keep_alive           = "30s"
        no_happy_eyeballs        = false
        keep_alive_connections   = 100
        keep_alive_timeout       = "1m30s"
        http_host_header         = ""
        origin_server_name       = ""
        ca_pool                  = ""
        no_tls_verify            = false
        disable_chunked_encoding = false
        bastion_mode             = false
        proxy_address            = "127.0.0.1"
        proxy_port               = 0
        proxy_type               = ""
        http2_origin             = false
        access {
          aud_tag   = []
          required  = false
          team_name = ""
        }
      }
    }
    # The identity provider: the login flow's path families and nothing else. A
    # bare hostname route would publish the administration console and every
    # account console behind one password. The edge login needs the realm's
    # discovery document, the protocol endpoints, the form actions the login page
    # posts to, and the page's static assets; those are the only families routed.
    # Everything else on this hostname falls through to the catch-all. The service
    # is the loopback binding the identity provider's compose block publishes,
    # reached by the tunnel process on the host's own network namespace.
    ingress_rule {
      hostname = local.keycloak_host
      path     = "^/realms/${var.keycloak_realm}/\\.well-known/"
      service  = "http://localhost:8080"
    }
    ingress_rule {
      hostname = local.keycloak_host
      path     = "^/realms/${var.keycloak_realm}/protocol/openid-connect/"
      service  = "http://localhost:8080"
    }
    ingress_rule {
      hostname = local.keycloak_host
      path     = "^/realms/${var.keycloak_realm}/login-actions/"
      service  = "http://localhost:8080"
    }
    ingress_rule {
      hostname = local.keycloak_host
      path     = "^/resources/"
      service  = "http://localhost:8080"
    }
    ingress_rule {
      service = "http_status:404"
    }
  }
}

# The identity provider's name in the zone, pointing at the tunnel. New work:
# nothing to import.
resource "cloudflare_record" "keycloak" {
  zone_id = var.cf_zone_id
  name    = var.keycloak_subdomain
  type    = "CNAME"
  content = "${var.cf_tunnel_id}.cfargotunnel.com"
  proxied = true
  ttl     = 1
  comment = "identity provider, path-filtered through the tunnel"
}
