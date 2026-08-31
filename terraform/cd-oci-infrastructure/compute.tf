# --- COMPUTE (CD-OCI-INFRASTRUCTURE) ---
# Ampere A1 Flex instance (aarch64), Always Free. Image and availability
# domain are resolved via data sources so no region-specific OCIDs are
# hardcoded. cloud-init installs Docker + Compose so the host is ready for
# the stack on first boot.

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.oci_tenancy_ocid
}

# Latest aarch64 platform image matching the requested OS + version,
# constrained to the A1.Flex shape.
data "oci_core_images" "ubuntu_arm" {
  compartment_id           = local.compartment
  operating_system         = var.instance_os
  operating_system_version = var.instance_os_version
  shape                    = "VM.Standard.A1.Flex"
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

resource "oci_core_instance" "cd_alpha" {
  # A1 capacity varies by AD in Ashburn. On "Out of host capacity", bump
  # -var availability_domain_index=1 (or 2) and re-apply.
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[var.availability_domain_index].name
  compartment_id      = local.compartment
  display_name        = var.instance_name
  shape               = "VM.Standard.A1.Flex"

  shape_config {
    ocpus         = var.instance_ocpus
    memory_in_gbs = var.instance_memory_gb
  }

  source_details {
    source_type             = "image"
    source_id               = data.oci_core_images.ubuntu_arm.images[0].id
    boot_volume_size_in_gbs = var.boot_volume_gb
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.public.id
    assign_public_ip = true
    hostname_label   = "cdalpha"
    nsg_ids          = []
  }

  metadata = {
    ssh_authorized_keys = file(pathexpand(var.ssh_public_key_path))
    user_data           = base64encode(file("${path.module}/cloud-init.yaml"))
  }

  freeform_tags = var.tags

  lifecycle {
    ignore_changes = [
      source_details[0].source_id, # don't rebuild when a newer image publishes
      metadata["user_data"],
    ]
  }
}
