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

  validation {
    condition     = can(regex("^s-[0-9]+vcpu-[0-9]+gb$", var.do_droplet_size))
    error_message = "do_droplet_size must be a valid DO shared-CPU slug (e.g., 's-4vcpu-8gb')."
  }

  validation {
    condition     = tonumber(regex("([0-9]+)gb$", var.do_droplet_size)[0]) >= 8
    error_message = "do_droplet_size must have at least 8GB RAM. Stack requires PostgreSQL + n8n + OpenClaw + Datadog."
  }
}

variable "do_droplet_name" {
  description = "Hostname for the primary droplet"
  type        = string
  default     = "cd-alpha-engine"

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9-]{1,62}[a-zA-Z0-9]$", var.do_droplet_name))
    error_message = "do_droplet_name must be 3-64 chars, start with a letter, end with alphanumeric, only contain letters/digits/hyphens (e.g., 'cd-alpha-engine')."
  }
}

variable "do_image" {
  description = "Droplet OS image slug"
  type        = string
  default     = "ubuntu-24-04-x64"

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.do_image))
    error_message = "do_image must be a valid DO image slug: lowercase letters, digits, and hyphens only (e.g., 'ubuntu-24-04-x64')."
  }
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

  validation {
    condition     = length(var.do_project_name) >= 1 && length(var.do_project_name) <= 175
    error_message = "do_project_name must be between 1 and 175 characters."
  }
}

variable "do_ssh_key_name" {
  description = "Name of the SSH key registered in DigitalOcean"
  type        = string
  default     = "coredirective-key"

  validation {
    condition     = length(var.do_ssh_key_name) >= 1
    error_message = "do_ssh_key_name cannot be empty."
  }
}

variable "do_tags" {
  description = "Tags applied to all DigitalOcean resources for filtering and billing"
  type        = list(string)
  default     = ["coredirective", "production"]

  validation {
    condition     = alltrue([for t in var.do_tags : can(regex("^[a-z0-9:_-]+$", t))])
    error_message = "Each do_tags entry must contain only lowercase letters, digits, hyphens, underscores, or colons (e.g., 'coredirective', 'env:production')."
  }
}

# --- CLOUDFLARE CONFIGURATION ---

variable "cf_zone_id" {
  description = "Cloudflare Zone ID for tigouetheory.com DNS management"
  type        = string

  validation {
    condition     = can(regex("^[a-f0-9]{32}$", var.cf_zone_id))
    error_message = "cf_zone_id must be a 32-character lowercase hex string (e.g., '44f6a683c92275d8fea6f6702589c608')."
  }
}

variable "cf_account_id" {
  description = "Cloudflare Account ID for tunnel and resource ownership"
  type        = string

  validation {
    condition     = can(regex("^[a-f0-9]{32}$", var.cf_account_id))
    error_message = "cf_account_id must be a 32-character lowercase hex string (e.g., 'e4871d2a375f9719092b286866ce26f2')."
  }
}

variable "cf_tunnel_id" {
  description = "Cloudflare Tunnel ID for zero-trust ingress (n8n + SSH)"
  type        = string

  validation {
    condition     = can(regex("^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$", var.cf_tunnel_id))
    error_message = "cf_tunnel_id must be a valid UUID format (e.g., '4bcf8238-8a8d-423d-b333-e8fe033d4de9')."
  }
}

# --- PROJECT METADATA ---

variable "project_name" {
  description = "Project name for resource tagging and identification"
  type        = string
  default     = "CoreDirective"

  validation {
    condition     = length(var.project_name) >= 1 && length(var.project_name) <= 64
    error_message = "project_name must be between 1 and 64 characters."
  }
}

# --- SSH KEY PATH ---

variable "ssh_public_key_path" {
  description = "Local path to SSH public key for droplet provisioning"
  type        = string
  default     = "~/.ssh/id_ed25519.pub"

  validation {
    condition     = can(regex("\\.pub$", var.ssh_public_key_path))
    error_message = "ssh_public_key_path must end with '.pub' (e.g., '~/.ssh/id_ed25519.pub')."
  }
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
