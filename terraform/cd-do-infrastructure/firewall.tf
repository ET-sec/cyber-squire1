# --- FIREWALL (DIGITALOCEAN) ---
# No existing firewall -- this will be CREATED in Phase 2, not imported.
# Rules follow zero-trust: only Cloudflare tunnel + ICMP inbound, all outbound.

resource "digitalocean_firewall" "cd_alpha" {
  name        = "cd-alpha-firewall"
  droplet_ids = [digitalocean_droplet.cd_alpha.id]

  # ICMP (ping) from anywhere -- needed for health checks
  inbound_rule {
    protocol         = "icmp"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # SSH via Cloudflare Tunnel only
  # TODO: Replace with Cloudflare IP ranges once firewall is created
  # See: https://www.cloudflare.com/ips/
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0"]
  }

  # HTTPS from anywhere (Cloudflare proxied traffic)
  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # All outbound traffic allowed
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}
