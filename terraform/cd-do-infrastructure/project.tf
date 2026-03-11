# --- PROJECT (DIGITALOCEAN) ---
# Import: terraform import digitalocean_project.coredirective 9a2c687c-9b03-431d-88eb-582667caa3dd

resource "digitalocean_project" "coredirective" {
  name        = var.do_project_name
  description = "CoreDirective production infrastructure"
  purpose     = "Service or API"
  environment = var.environment == "prod" ? "Production" : title(var.environment)
  resources   = [digitalocean_droplet.cd_alpha.urn]
}
