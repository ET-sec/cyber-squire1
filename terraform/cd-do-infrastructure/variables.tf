# --- INPUT VARIABLES (CD-DO-INFRASTRUCTURE) ---
# Configuration parameters for DigitalOcean + Cloudflare production infrastructure

# --- DIGITALOCEAN REGION ---

variable "do_region" {
  description = "DigitalOcean datacenter region for all resources"
  type        = string
  default     = "nyc1"

  validation {
    condition     = contains(["nyc1", "nyc3", "sfo3"], var.do_region)
    error_message = "Region must be one of: nyc1, nyc3, sfo3 (US-based low-latency regions)"
  }
}

# --- DROPLET CONFIGURATION ---

variable "do_droplet_size" {
  description = "Droplet size slug (must support 8GB+ RAM for PostgreSQL + n8n + OpenClaw + Datadog)"
  type        = string
  default     = "s-4vcpu-8gb"
}

variable "do_droplet_name" {
  description = "Hostname for the primary droplet"
  type        = string
  default     = "cd-alpha-engine"
}

variable "do_image" {
  description = "Droplet OS image slug"
  type        = string
  default     = "ubuntu-24-04-x64"
}

# --- NETWORK CONFIGURATION ---

variable "do_vpc_cidr" {
  description = "CIDR block for the VPC private network"
  type        = string
  default     = "10.116.0.0/20"

  validation {
    condition     = can(cidrhost(var.do_vpc_cidr, 0))
    error_message = "do_vpc_cidr must be a valid CIDR block (e.g., 10.116.0.0/20)"
  }
}

# --- PROJECT & ACCESS ---

variable "do_project_name" {
  description = "DigitalOcean project name to group resources under"
  type        = string
  default     = "first-project"
}

variable "do_ssh_key_name" {
  description = "Name of the SSH key registered in DigitalOcean"
  type        = string
  default     = "coredirective-key"
}

variable "do_tags" {
  description = "Tags applied to all DigitalOcean resources for filtering and billing"
  type        = list(string)
  default     = ["coredirective", "production"]
}

# --- CLOUDFLARE CONFIGURATION ---

variable "cf_zone_id" {
  description = "Cloudflare Zone ID for tigouetheory.com DNS management"
  type        = string
}

variable "cf_account_id" {
  description = "Cloudflare Account ID for tunnel and resource ownership"
  type        = string
}

variable "cf_tunnel_id" {
  description = "Cloudflare Tunnel ID for zero-trust ingress (n8n + SSH)"
  type        = string
}

# --- ENVIRONMENT & PROJECT METADATA ---

variable "environment" {
  description = "Deployment environment (controls tagging and naming conventions)"
  type        = string
  default     = "prod"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod"
  }
}

variable "project_name" {
  description = "Project name for resource tagging and identification"
  type        = string
  default     = "CoreDirective"
}

# --- SSH KEY PATH ---

variable "ssh_public_key_path" {
  description = "Local path to SSH public key for droplet provisioning"
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}

# --- NOTES ---
#
# Required Variables (no defaults -- must be supplied):
#   - cf_zone_id:    Cloudflare Zone ID for tigouetheory.com
#   - cf_account_id: Cloudflare Account ID
#   - cf_tunnel_id:  Cloudflare Tunnel ID (tunnel-cyber-squire)
#
# Optional Variables:
#   - All others have sensible defaults matching current DO droplet
#
# Usage:
#   terraform plan -var-file="terraform.tfvars"
#   terraform apply -var="do_droplet_size=s-8vcpu-16gb" -var="environment=staging"
#
# Or create terraform.tfvars:
#   cf_zone_id    = "44f6a683c92275d8fea6f6702589c608"
#   cf_account_id = "e4871d2a375f9719092b286866ce26f2"
#   cf_tunnel_id  = "4bcf8238-8a8d-423d-b333-e8fe033d4de9"
#   environment   = "prod"
