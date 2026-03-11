# --- DNS RECORDS (CD-DO-INFRASTRUCTURE) ---
# Record IDs to be collected via CF API in Phase 3
# Uses cloudflare_record (v4 name, NOT cloudflare_dns_record which is v5)

resource "cloudflare_record" "root" {
  zone_id = var.cf_zone_id
  name    = "tigouetheory.com"
  type    = "CNAME"
  content = "placeholder.example.com"  # TODO: collect actual value in Phase 3
  proxied = true
}

resource "cloudflare_record" "n8n" {
  zone_id = var.cf_zone_id
  name    = "n8n"
  type    = "CNAME"
  content = "placeholder.example.com"  # TODO: collect actual value in Phase 3
  proxied = true
}

resource "cloudflare_record" "ssh_tunnel" {
  zone_id = var.cf_zone_id
  name    = "ssh"
  type    = "CNAME"
  content = "placeholder.example.com"  # TODO: collect actual value in Phase 3
  proxied = true
}
