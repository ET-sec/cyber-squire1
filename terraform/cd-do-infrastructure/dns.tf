# --- DNS RECORDS (CLOUDFLARE) ---
# Record IDs to be collected via CF API in Phase 3.
# Uses cloudflare_record (v4 name, NOT v5 cloudflare_dns_record).

# Root domain -- tigouetheory.com
# TODO: Collect record ID for import in Phase 3
# Import: terraform import cloudflare_record.root <zone_id>/<record_id>
resource "cloudflare_record" "root" {
  zone_id = var.cf_zone_id
  name    = "tigouetheory.com"
  type    = "A"
  content = digitalocean_droplet.cd_alpha.ipv4_address
  proxied = true
  ttl     = 1 # Auto TTL when proxied
}

# n8n subdomain -- n8n.tigouetheory.com (via Cloudflare Tunnel)
# TODO: Collect record ID for import in Phase 3
# Import: terraform import cloudflare_record.n8n <zone_id>/<record_id>
resource "cloudflare_record" "n8n" {
  zone_id = var.cf_zone_id
  name    = "n8n"
  type    = "CNAME"
  content = "${var.cf_tunnel_id}.cfargotunnel.com"
  proxied = true
  ttl     = 1
}

# SSH subdomain -- ssh.tigouetheory.com (via Cloudflare Tunnel)
# TODO: Collect record ID for import in Phase 3
# Import: terraform import cloudflare_record.ssh <zone_id>/<record_id>
resource "cloudflare_record" "ssh" {
  zone_id = var.cf_zone_id
  name    = "ssh"
  type    = "CNAME"
  content = "${var.cf_tunnel_id}.cfargotunnel.com"
  proxied = true
  ttl     = 1
}
