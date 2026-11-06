# --- OUTPUTS (CD-LAB-INFRASTRUCTURE) ---

output "segments" {
  description = "Lab network name to CIDR."
  value       = { for k, n in libvirt_network.segment : n.name => local.segments[k].cidr }
}

output "profiles" {
  description = "Profile name to the VMs scripts/lab starts for it, with the RAM they need together."
  value = {
    for p in distinct(flatten([for v in local.vms : v.profiles])) :
    p => {
      vms        = sort([for k, v in local.vms : k if contains(v.profiles, p)])
      memory_mib = sum([for k, v in local.vms : v.memory if contains(v.profiles, p)])
    }
  }
}

output "defined_vms" {
  description = "Every VM this apply defined, stopped."
  value       = sort(keys(libvirt_domain.vm))
}
