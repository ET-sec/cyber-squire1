# --- PROJECT (CD-DO-INFRASTRUCTURE) ---
# Import: terraform import digitalocean_project.coredirective 9a2c687c-9b03-431d-88eb-582667caa3dd

resource "digitalocean_project" "coredirective" {
  name        = var.do_project_name
  description = "Update your project information under Settings"
  resources   = [digitalocean_droplet.cd_alpha.urn]

  # NOTE: environment and purpose intentionally omitted.
  # Live project has both as empty strings (never configured).
  # Setting any value would cause drift after import.
  # After import, update via DO console first, then add here.
}
