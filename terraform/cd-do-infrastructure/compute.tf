# --- COMPUTE (DIGITALOCEAN DROPLET) ---
# Import: terraform import digitalocean_droplet.cd_alpha 557327264

resource "digitalocean_droplet" "cd_alpha" {
  name     = var.do_droplet_name
  region   = var.do_region
  size     = var.do_droplet_size
  image    = var.do_image
  vpc_uuid = digitalocean_vpc.default.id
  ssh_keys = [digitalocean_ssh_key.coredirective.id]
  tags     = var.do_tags

  # Safety guard: prevent accidental destruction of production droplet
  lifecycle {
    prevent_destroy = true
  }
}
