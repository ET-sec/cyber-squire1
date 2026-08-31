# --- NETWORKING (CD-OCI-INFRASTRUCTURE) ---
# VCN with a single public subnet, internet gateway, route table, and a
# security list. Real access to services goes through the Cloudflare Tunnel
# (outbound-only from the host), so the security list stays deny-by-default
# on ingress except SSH from explicitly allowed CIDRs.

locals {
  compartment = var.compartment_ocid != "" ? var.compartment_ocid : var.oci_tenancy_ocid
}

resource "oci_core_vcn" "main" {
  compartment_id = local.compartment
  cidr_blocks    = [var.vcn_cidr]
  display_name   = "cd-vcn"
  dns_label      = "cdvcn"
  freeform_tags  = var.tags
}

resource "oci_core_internet_gateway" "main" {
  compartment_id = local.compartment
  vcn_id         = oci_core_vcn.main.id
  display_name   = "cd-igw"
  enabled        = true
  freeform_tags  = var.tags
}

resource "oci_core_route_table" "main" {
  compartment_id = local.compartment
  vcn_id         = oci_core_vcn.main.id
  display_name   = "cd-rt"
  freeform_tags  = var.tags

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.main.id
  }
}

resource "oci_core_security_list" "main" {
  compartment_id = local.compartment
  vcn_id         = oci_core_vcn.main.id
  display_name   = "cd-sl"
  freeform_tags  = var.tags

  # Egress: all (host reaches Cloudflare, package repos, LLM APIs, etc.)
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }

  # Ingress: SSH only from allowed CIDRs (bootstrap/emergency).
  dynamic "ingress_security_rules" {
    for_each = var.ssh_allowed_cidrs
    content {
      protocol = "6" # TCP
      source   = ingress_security_rules.value
      tcp_options {
        min = 22
        max = 22
      }
    }
  }

  # Ingress: ICMP path MTU + unreachable from within the VCN.
  ingress_security_rules {
    protocol = "1" # ICMP
    source   = var.vcn_cidr
    icmp_options {
      type = 3
    }
  }
}

resource "oci_core_subnet" "public" {
  compartment_id             = local.compartment
  vcn_id                     = oci_core_vcn.main.id
  cidr_block                 = var.subnet_cidr
  display_name               = "cd-public-subnet"
  dns_label                  = "cdpub"
  route_table_id             = oci_core_route_table.main.id
  security_list_ids          = [oci_core_security_list.main.id]
  prohibit_public_ip_on_vnic = false
  freeform_tags              = var.tags
}
