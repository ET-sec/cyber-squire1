# --- SSH KEY (DIGITALOCEAN) ---
# Import: terraform import digitalocean_ssh_key.coredirective 54804544

resource "digitalocean_ssh_key" "coredirective" {
  name       = var.do_ssh_key_name
  public_key = file(var.ssh_public_key_path)
}
