# --- PROJECT (CD-DO-INFRASTRUCTURE) ---
# Import: terraform import digitalocean_project.coredirective 9a2c687c-9b03-431d-88eb-582667caa3dd

resource "digitalocean_project" "coredirective" {
  name        = var.do_project_name
  environment = var.environment
  resources   = [digitalocean_droplet.cd_alpha.urn]
}
