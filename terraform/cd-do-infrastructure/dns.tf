# --- DNS RECORDS (CD-DO-INFRASTRUCTURE) ---
# Imported in Phase 3 (2026-03-11)
# Uses cloudflare_record (v4 name, NOT cloudflare_dns_record which is v5)
# Only managing tunnel-related records. MX, NS, TXT, DKIM left unmanaged.

resource "cloudflare_record" "root" {
  zone_id = var.cf_zone_id
  name    = "tigouetheory.com"
  type    = "CNAME"
  content = "tigouetheory-site.pages.dev"
  proxied = true
  ttl     = 1
}

resource "cloudflare_record" "www" {
  zone_id = var.cf_zone_id
  name    = "www"
  type    = "CNAME"
  content = "tigouetheory-site.pages.dev"
  proxied = true
  ttl     = 1
}

resource "cloudflare_record" "n8n" {
  zone_id = var.cf_zone_id
  name    = "n8n"
  type    = "CNAME"
  content = "${var.cf_tunnel_id}.cfargotunnel.com"
  proxied = true
  ttl     = 1
}

resource "cloudflare_record" "ssh_tunnel" {
  zone_id = var.cf_zone_id
  name    = "ssh"
  type    = "CNAME"
  content = "${var.cf_tunnel_id}.cfargotunnel.com"
  proxied = true
  ttl     = 1
}

# Langfuse v3 self-hosted UI (Phase 17-04)
resource "cloudflare_record" "langfuse" {
  zone_id = var.cf_zone_id
  name    = "langfuse"
  type    = "CNAME"
  content = "${var.cf_tunnel_id}.cfargotunnel.com"
  proxied = true
  ttl     = 1
}

# Squire FastAPI surface (Phase 17-09)
resource "cloudflare_record" "squire" {
  zone_id = var.cf_zone_id
  name    = "squire"
  type    = "CNAME"
  content = "${var.cf_tunnel_id}.cfargotunnel.com"
  proxied = true
  ttl     = 1
}
