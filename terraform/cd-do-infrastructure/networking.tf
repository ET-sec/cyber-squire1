# --- NETWORKING (CD-DO-INFRASTRUCTURE) ---
# Import: terraform import digitalocean_vpc.default VPC_UUID

resource "digitalocean_vpc" "default" {
  name     = "default-nyc1"
  region   = var.do_region
  ip_range = var.do_vpc_cidr

  lifecycle {
    postcondition {
      condition     = self.ip_range == var.do_vpc_cidr
      error_message = "VPC CIDR (${self.ip_range}) does not match expected (${var.do_vpc_cidr})."
    }
  }
}
