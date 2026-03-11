# --- PROJECT (CD-DO-INFRASTRUCTURE) ---
# Import: terraform import digitalocean_project.coredirective 9a2c687c-9b03-431d-88eb-582667caa3dd

resource "digitalocean_project" "coredirective" {
  name        = var.do_project_name
  description = "Update your project information under Settings"
  is_default  = true
  resources   = [digitalocean_droplet.cd_alpha.urn]

  # NOTE: environment, purpose intentionally omitted (live state has empty strings).
  # is_default matches live state. purpose has provider default "Web Application"
  # that conflicts with live empty — ignored to prevent drift.
  lifecycle {
    ignore_changes = [purpose]
  }
}
