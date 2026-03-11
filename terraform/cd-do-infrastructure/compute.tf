# --- COMPUTE (CD-DO-INFRASTRUCTURE) ---
# Import: terraform import digitalocean_droplet.cd_alpha 557327264

resource "digitalocean_droplet" "cd_alpha" {
  name          = var.do_droplet_name
  region        = var.do_region
  size          = var.do_droplet_size
  image         = var.do_image
  vpc_uuid      = digitalocean_vpc.default.id
  ssh_keys      = [digitalocean_ssh_key.coredirective.id]
  tags          = var.do_tags
  droplet_agent = true

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [image, ssh_keys]
  }
}
