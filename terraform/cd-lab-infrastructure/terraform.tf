# --- TERRAFORM CONFIGURATION (CD-LAB-INFRASTRUCTURE) ---
# The on-prem lab host: a Lenovo M75q Gen 2 (32 GB, 1 TB NVMe) running Ubuntu
# 26.04 with KVM. This root defines the lab's virtual networks and every VM the
# four industry archetypes need, the same way cd-oci-infrastructure defines the
# cloud host. Nothing here runs on the Mac: the provider talks to libvirt on
# the Lenovo over SSH, or locally on the box itself.
#
# STATE BACKEND: the same versioned OCI Object Storage bucket as the cloud
# root, under its own key. Bucket name, namespace and region live in
# backend.hcl (gitignored):
#   terraform init -backend-config=backend.hcl
#
# VMs are DEFINED here and left stopped (running = false). scripts/lab starts
# the set a profile needs, because 32 GB runs one lab day at a time.

terraform {
  required_version = ">= 1.12.0"

  backend "oci" {}

  required_providers {
    libvirt = {
      source  = "dmacvicar/libvirt"
      version = "~> 0.8.0"
    }
  }
}
