# --- OUTPUTS (CD-OCI-INFRASTRUCTURE) ---

output "instance_public_ip" {
  description = "Public IP of the primary instance"
  value       = oci_core_instance.cd_alpha.public_ip
}

output "instance_id" {
  description = "OCID of the primary instance"
  value       = oci_core_instance.cd_alpha.id
}

output "availability_domain" {
  description = "AD the instance landed in"
  value       = oci_core_instance.cd_alpha.availability_domain
}

output "image_id" {
  description = "OCID of the resolved aarch64 image"
  value       = data.oci_core_images.ubuntu_arm.images[0].id
}

output "ssh_command" {
  description = "Direct SSH (only works from an allowed CIDR; prefer the tunnel)"
  value       = "ssh ubuntu@${oci_core_instance.cd_alpha.public_ip}"
}

output "vcn_id" {
  description = "OCID of the VCN"
  value       = oci_core_vcn.main.id
}

output "estimated_monthly_cost" {
  description = "Always Free tier: A1 up to 4 OCPU / 24GB / 200GB block are $0."
  value       = "USD 0.00 (Always Free: A1.Flex ${var.instance_ocpus} OCPU / ${var.instance_memory_gb}GB / ${var.boot_volume_gb}GB boot)"
}
