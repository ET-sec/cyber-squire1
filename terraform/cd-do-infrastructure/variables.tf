# --- INPUT VARIABLES (CD-DO-INFRASTRUCTURE) ---
# Configuration parameters for CoreDirective DigitalOcean + Cloudflare infrastructure.
# Non-secret values live in terraform.tfvars. Secrets come from env vars or 1Password.

# --- DIGITALOCEAN COMPUTE ---

variable "do_region" {
  description = "DigitalOcean region for all resources"
  type        = string
  default     = "nyc1"

  validation {
    condition     = contains(["nyc1", "nyc3", "sfo3"], var.do_region)
    error_message = "Region must be one of: nyc1, nyc3, sfo3 (US regions with VPC support)."
  }
}

variable "do_droplet_size" {
  description = "Droplet size slug (must support Docker + PostgreSQL + n8n + OpenClaw)"
  type        = string
  default     = "s-4vcpu-8gb"

  validation {
    condition     = can(regex("^s-", var.do_droplet_size))
    error_message = "Droplet size must be a shared CPU slug (s-* series) for cost efficiency."
  }
}

variable "do_droplet_name" {
  description = "Droplet hostname"
  type        = string
  default     = "cd-alpha-engine"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]*[a-z0-9]$", var.do_droplet_name))
    error_message = "Droplet name must be lowercase alphanumeric with hyphens, no leading/trailing hyphens."
  }
}

variable "do_image" {
  description = "Droplet OS image slug"
  type        = string
  default     = "ubuntu-24-04-x64"
}

variable "do_vpc_cidr" {
  description = "CIDR block for the VPC (default-nyc1 uses 10.116.0.0/20)"
  type        = string
  default     = "10.116.0.0/20"

  validation {
    condition     = can(cidrhost(var.do_vpc_cidr, 0))
    error_message = "Must be a valid CIDR block (e.g., 10.116.0.0/20)."
  }
}

# --- DIGITALOCEAN PROJECT ---

variable "do_project_name" {
  description = "DigitalOcean project name for resource grouping"
  type        = string
  default     = "first-project"
}

variable "do_ssh_key_name" {
  description = "Name of the SSH key registered in DigitalOcean"
  type        = string
  default     = "coredirective-key"
}

variable "do_tags" {
  description = "Tags applied to all DigitalOcean resources"
  type        = list(string)
  default     = ["coredirective", "production"]
}

# --- CLOUDFLARE ---

variable "cf_zone_id" {
  description = "Cloudflare zone ID for tigouetheory.com"
  type        = string

  validation {
    condition     = can(regex("^[a-f0-9]{32}$", var.cf_zone_id))
    error_message = "Zone ID must be a 32-character hex string."
  }
}

variable "cf_account_id" {
  description = "Cloudflare account ID"
  type        = string

  validation {
    condition     = can(regex("^[a-f0-9]{32}$", var.cf_account_id))
    error_message = "Account ID must be a 32-character hex string."
  }
}

variable "cf_tunnel_id" {
  description = "Cloudflare Tunnel UUID (tunnel-cyber-squire)"
  type        = string

  validation {
    condition     = can(regex("^[a-f0-9-]{36}$", var.cf_tunnel_id))
    error_message = "Tunnel ID must be a valid UUID (36 chars with hyphens)."
  }
}

# --- GENERAL ---

variable "environment" {
  description = "Deployment environment (affects project settings and tagging)"
  type        = string
  default     = "prod"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "project_name" {
  description = "Project name for tagging and identification"
  type        = string
  default     = "CoreDirective"
}

# --- SSH KEY ---

variable "ssh_public_key_path" {
  description = "Path to the SSH public key file for DO SSH key resource"
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}

# --- NOTES ---
#
# Required Variables (no defaults -- set in terraform.tfvars):
#   - cf_zone_id: Cloudflare zone ID for tigouetheory.com
#   - cf_account_id: Cloudflare account ID
#   - cf_tunnel_id: Cloudflare Tunnel UUID
#
# Optional Variables (have sensible defaults):
#   - All DO variables default to current production values
#   - environment defaults to "prod"
#
# Usage:
#   source env.sh && terraform plan
#   source env.sh && terraform plan -var="environment=staging"
#
# Or set overrides in terraform.tfvars:
#   do_droplet_size = "s-8vcpu-16gb"
#   environment = "staging"
