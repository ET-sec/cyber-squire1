# --- COMPUTE (CD-DO-INFRASTRUCTURE) ---
# Import: terraform import digitalocean_droplet.cd_alpha DROPLET_ID

resource "digitalocean_droplet" "cd_alpha" {
  name     = var.do_droplet_name
  region   = var.do_region
  size     = var.do_droplet_size
  image    = var.do_image
  vpc_uuid = digitalocean_vpc.default.id
  ssh_keys = [digitalocean_ssh_key.coredirective.id]
  tags     = var.do_tags

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [image, ssh_keys, droplet_agent]

    postcondition {
      condition     = self.status == "active"
      error_message = "Droplet ${self.name} is not in 'active' status (current: ${self.status})."
    }

    postcondition {
      condition     = self.ipv4_address != ""
      error_message = "Droplet ${self.name} has no public IPv4 address assigned."
    }
  }
}
