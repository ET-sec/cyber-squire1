# --- PROVIDER CONFIGURATION (CD-LAB-INFRASTRUCTURE) ---
# From the Mac: qemu+ssh://<user>@lab/system rides the same key-only SSH the
# lab sync uses (LAN at home, the Cloudflare tunnel away). On the Lenovo
# itself: qemu:///system. No credential lives in this file or in state.
provider "libvirt" {
  uri = var.libvirt_uri
}
