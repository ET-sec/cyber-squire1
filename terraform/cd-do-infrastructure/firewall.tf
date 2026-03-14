# --- FIREWALL (CD-DO-INFRASTRUCTURE) ---
# No existing firewall -- this will be CREATED in Phase 2, not imported

resource "digitalocean_firewall" "cd_alpha" {
  name        = "cd-alpha-firewall"
  droplet_ids = [digitalocean_droplet.cd_alpha.id]

  # ICMP (ping) -- allow from anywhere for health checks
  inbound_rule {
    protocol         = "icmp"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # SSH -- restricted to explicitly allowed CIDRs (default: deny all)
  # Access should go through Cloudflare Tunnel; direct SSH only for emergencies
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = var.ssh_allowed_cidrs
  }

  # All outbound
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
