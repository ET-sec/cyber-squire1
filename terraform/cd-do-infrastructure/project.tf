# --- PROJECT (CD-DO-INFRASTRUCTURE) ---
# Import: terraform import digitalocean_project.coredirective PROJECT_UUID

resource "digitalocean_project" "coredirective" {
  name        = var.do_project_name
  description = "Update your project information under Settings"
  is_default  = true
  resources = [
    digitalocean_droplet.cd_alpha.urn,
    "do:space:cd-terraform-state"
  ]

  # NOTE: environment, purpose intentionally omitted (live state has empty strings).
  # is_default matches live state. purpose has provider default "Web Application"
  # that conflicts with live empty — ignored to prevent drift.
  lifecycle {
    ignore_changes = [purpose]
  }
}
