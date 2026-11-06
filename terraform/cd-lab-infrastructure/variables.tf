# --- VARIABLES (CD-LAB-INFRASTRUCTURE) ---

variable "libvirt_uri" {
  description = "libvirt connection. qemu:///system on the Lenovo, qemu+ssh://<user>@lab/system from the Mac."
  type        = string
  default     = "qemu:///system"
}

variable "pool" {
  description = "libvirt storage pool that holds every VM disk. Internal NVMe only, never the T7."
  type        = string
  default     = "default"
}

variable "iso_dir" {
  description = "Folder on the Lenovo holding install media (copied from the T7's CYBER/iso)."
  type        = string
  default     = "/srv/lab/iso"
}

variable "ovmf_code" {
  description = "UEFI firmware with Secure Boot keys, for the Windows VMs."
  type        = string
  default     = "/usr/share/OVMF/OVMF_CODE_4M.ms.fd"
}

variable "ovmf_vars_template" {
  description = "UEFI variable store template for the Windows VMs."
  type        = string
  default     = "/usr/share/OVMF/OVMF_VARS_4M.ms.fd"
}

variable "enabled_vms" {
  description = "Names from local.vms to define. Empty means all of them. scripts/lab starts and stops them per profile."
  type        = set(string)
  default     = []
}
