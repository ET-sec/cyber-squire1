# --- NETWORKS (CD-LAB-INFRASTRUCTURE) ---
# Microsoft's tier model as libvirt networks. Every segment except lab-wan is
# isolated (mode none): no NAT, no DHCP, no DNS from libvirt. The OPNsense VM
# sits on all of them and is the only router, firewall and DHCP server, so
# every cross-segment hop is a firewall decision it logs to Wazuh.
# lab-wan is the one NAT network, and only OPNsense's WAN interface joins it.
# The home LAN is never a libvirt network: the sensor (Kismet, the airspace
# parser) runs on the host and sees the real house through the host's NIC.

locals {
  segments = {
    tier0    = { cidr = "10.90.0.0/24", purpose = "domain controller and certificate server" }
    tier2    = { cidr = "10.90.2.0/24", purpose = "workstations, where phishing lands" }
    attack   = { cidr = "10.90.6.0/24", purpose = "Kali and the C2 server" }
    dmz      = { cidr = "10.90.4.0/24", purpose = "web targets exposed to the attack net" }
    mgmt     = { cidr = "10.90.8.0/24", purpose = "Wazuh, Velociraptor, BloodHound; agents push in" }
    detonate = { cidr = "10.90.9.0/24", purpose = "CAPE guest; fake internet only, no route out" }
    k8s      = { cidr = "10.90.5.0/24", purpose = "the Kubernetes target" }
  }
}

resource "libvirt_network" "segment" {
  for_each = local.segments

  name      = "lab-${each.key}"
  mode      = "none"
  autostart = true
  addresses = [each.value.cidr]

  dhcp {
    enabled = false
  }

  dns {
    enabled = false
  }
}

resource "libvirt_network" "wan" {
  name      = "lab-wan"
  mode      = "nat"
  autostart = true
  addresses = ["10.90.99.0/24"]

  dhcp {
    enabled = true
  }
}
