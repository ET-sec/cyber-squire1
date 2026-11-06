# --- VMS (CD-LAB-INFRASTRUCTURE) ---
# One map holds every machine. Disks are thin qcow2 on the internal NVMe pool,
# so the size is a ceiling, not what is used. Every VM is defined stopped;
# scripts/lab starts the ones a profile needs. Windows machines get UEFI with
# Secure Boot keys and an emulated TPM 2.0, which Windows 11 and Server 2025
# both require. Phase 1 installs by hand from the ISO and takes a golden
# snapshot; Packer and Ansible replace the hand install in phase 2.

locals {
  gib = 1024 * 1024 * 1024

  vms = {
    opnsense = { memory = 1024, vcpu = 1, disk_gb = 16, windows = false, iso = "OPNsense-amd64.iso", nets = ["wan", "tier0", "tier2", "attack", "dmz", "mgmt", "detonate", "k8s"], profiles = ["ad", "web", "blue", "re", "air"] }
    dc01     = { memory = 4096, vcpu = 2, disk_gb = 60, windows = true, iso = "windows-server-2025-eval.iso", nets = ["tier0"], profiles = ["ad"] }
    ca01     = { memory = 3072, vcpu = 2, disk_gb = 60, windows = true, iso = "windows-server-2025-eval.iso", nets = ["tier0"], profiles = ["ad"] }
    ws01     = { memory = 4096, vcpu = 2, disk_gb = 60, windows = true, iso = "windows-11-enterprise-eval.iso", nets = ["tier2"], profiles = ["ad"] }
    ws02     = { memory = 4096, vcpu = 2, disk_gb = 60, windows = true, iso = "windows-11-enterprise-eval.iso", nets = ["tier2"], profiles = [] }
    win11pro = { memory = 4096, vcpu = 2, disk_gb = 64, windows = true, iso = "windows-11-pro.iso", nets = ["tier2"], profiles = [] }
    kali     = { memory = 4096, vcpu = 2, disk_gb = 80, windows = false, iso = "kali-linux-installer-amd64.iso", nets = ["attack"], profiles = ["ad", "web"] }
    rocky    = { memory = 2048, vcpu = 2, disk_gb = 20, windows = false, iso = "Rocky-10-x86_64-minimal.iso", nets = ["dmz"], profiles = ["web"] }
    k8s01    = { memory = 3072, vcpu = 2, disk_gb = 30, windows = false, iso = "ubuntu-26.04.1-live-server-amd64.iso", nets = ["k8s"], profiles = ["web"] }
    flare    = { memory = 8192, vcpu = 4, disk_gb = 80, windows = true, iso = "windows-11-enterprise-eval.iso", nets = ["detonate"], profiles = ["re"] }
    remnux   = { memory = 4096, vcpu = 2, disk_gb = 25, windows = false, iso = "remnux-amd64.iso", nets = ["detonate"], profiles = ["re"] }
    capevm   = { memory = 4096, vcpu = 2, disk_gb = 50, windows = true, iso = "windows-11-enterprise-eval.iso", nets = ["detonate"], profiles = ["re"] }
  }

  selected = length(var.enabled_vms) == 0 ? local.vms : { for k, v in local.vms : k => v if contains(var.enabled_vms, k) }
}

resource "libvirt_volume" "disk" {
  for_each = local.selected

  name   = "${each.key}.qcow2"
  pool   = var.pool
  format = "qcow2"
  size   = each.value.disk_gb * local.gib

  # A golden domain controller is a day's work. No plan may delete a disk by
  # accident; removing a VM from the map is a deliberate two-step edit.
  lifecycle {
    prevent_destroy = true
  }
}

resource "libvirt_domain" "vm" {
  for_each = local.selected

  name      = each.key
  memory    = each.value.memory
  vcpu      = each.value.vcpu
  running   = false
  autostart = false
  machine   = "q35"

  # Windows 11 and Server 2025 need UEFI, Secure Boot keys and a TPM 2.0.
  firmware = each.value.windows ? var.ovmf_code : null

  dynamic "nvram" {
    for_each = each.value.windows ? [1] : []
    content {
      file     = "/var/lib/libvirt/qemu/nvram/${each.key}_VARS.fd"
      template = var.ovmf_vars_template
    }
  }

  dynamic "tpm" {
    for_each = each.value.windows ? [1] : []
    content {
      backend_type    = "emulator"
      backend_version = "2.0"
      model           = "tpm-crb"
    }
  }

  cpu {
    mode = "host-passthrough"
  }

  disk {
    volume_id = libvirt_volume.disk[each.key].id
  }

  disk {
    file = "${var.iso_dir}/${each.value.iso}"
  }

  boot_device {
    dev = ["hd", "cdrom"]
  }

  dynamic "network_interface" {
    for_each = each.value.nets
    content {
      network_name   = network_interface.value == "wan" ? libvirt_network.wan.name : libvirt_network.segment[network_interface.value].name
      wait_for_lease = false
    }
  }

  graphics {
    type        = "spice"
    listen_type = "address"
    autoport    = true
  }
}
