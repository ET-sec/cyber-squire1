# --- INPUT VARIABLES (CD-OCI-INFRASTRUCTURE) ---

# --- OCI AUTH (from Doppler via TF_VAR_oci_*) ---

variable "oci_tenancy_ocid" {
  description = "OCI tenancy OCID"
  type        = string

  validation {
    condition     = can(regex("^ocid1\\.tenancy\\.", var.oci_tenancy_ocid))
    error_message = "oci_tenancy_ocid must start with 'ocid1.tenancy.'."
  }
}

variable "oci_user_ocid" {
  description = "OCI user OCID. Empty when auth is SecurityToken (CI drift plan)."
  type        = string
  default     = ""

  validation {
    condition     = var.oci_user_ocid == "" || can(regex("^ocid1\\.user\\.", var.oci_user_ocid))
    error_message = "oci_user_ocid must start with 'ocid1.user.' or be empty."
  }
}

variable "oci_fingerprint" {
  description = "API signing key fingerprint. Empty when auth is SecurityToken."
  type        = string
  default     = ""
}

variable "oci_private_key" {
  description = "API signing private key, PEM content (from Doppler OCI_PRIVATE_KEY). Empty when auth is SecurityToken."
  type        = string
  sensitive   = true
  default     = ""
}

variable "tfstate_bucket_name" {
  description = "Terraform state bucket name. Set in gitignored tfvars locally and a CI secret: the backend address (name + namespace) stays out of the public repo."
  type        = string
}

# CI (the drift-detection workflow) authenticates with a short-lived UPST from
# the GitHub OIDC token exchange instead of a stored API key. Local runs keep
# the default ApiKey path via env.sh.
variable "oci_auth" {
  description = "Provider auth method: ApiKey (local, default) or SecurityToken (CI via token exchange)"
  type        = string
  default     = "ApiKey"

  validation {
    condition     = contains(["ApiKey", "SecurityToken"], var.oci_auth)
    error_message = "oci_auth must be ApiKey or SecurityToken."
  }
}

variable "oci_region" {
  description = "OCI home region"
  type        = string
  default     = "us-ashburn-1"
}

variable "compartment_ocid" {
  description = "Compartment to build in. Free tier uses the root compartment (== tenancy OCID)."
  type        = string
  default     = ""
}

# --- COMPUTE (Always Free Ampere A1) ---

variable "instance_name" {
  description = "Hostname for the primary instance"
  type        = string
  default     = "cd-alpha-engine"
}

variable "instance_ocpus" {
  description = "OCPUs for the A1.Flex shape. Always Free ceiling is 4 total across all A1 instances."
  type        = number
  default     = 4

  validation {
    condition     = var.instance_ocpus >= 1 && var.instance_ocpus <= 4
    error_message = "instance_ocpus must be 1-4 (Always Free A1 ceiling)."
  }
}

variable "instance_memory_gb" {
  description = "Memory in GB for A1.Flex. Always Free ceiling is 24GB total."
  type        = number
  default     = 24

  validation {
    condition     = var.instance_memory_gb >= 6 && var.instance_memory_gb <= 24
    error_message = "instance_memory_gb must be 6-24 (Always Free A1 ceiling)."
  }
}

variable "boot_volume_gb" {
  description = "Boot volume size in GB. Always Free block storage ceiling is 200GB total."
  type        = number
  default     = 150

  validation {
    condition     = var.boot_volume_gb >= 50 && var.boot_volume_gb <= 200
    error_message = "boot_volume_gb must be 50-200 (Always Free block storage ceiling)."
  }
}

variable "instance_os" {
  description = "Operating system for the image lookup (must have an aarch64 build)"
  type        = string
  default     = "Canonical Ubuntu"
}

variable "instance_os_version" {
  description = "OS version for the image lookup"
  type        = string
  default     = "22.04"
}

variable "availability_domain_index" {
  description = "Which AD to place the instance in (0-based). Bump on A1 out-of-capacity errors."
  type        = number
  default     = 0
}

# --- SSH ---

variable "ssh_public_key_path" {
  description = "Local path to SSH public key injected into the instance"
  type        = string
  default     = "~/.ssh/id_ed25519.pub"

  validation {
    condition     = can(regex("\\.pub$", var.ssh_public_key_path))
    error_message = "ssh_public_key_path must end with '.pub'."
  }
}

# --- NETWORK ---

variable "vcn_cidr" {
  description = "CIDR block for the VCN"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vcn_cidr, 0))
    error_message = "vcn_cidr must be a valid CIDR block."
  }
}

variable "subnet_cidr" {
  description = "CIDR block for the public subnet"
  type        = string
  default     = "10.0.1.0/24"

  validation {
    condition     = can(cidrhost(var.subnet_cidr, 0))
    error_message = "subnet_cidr must be a valid CIDR block."
  }
}

variable "ssh_allowed_cidrs" {
  description = "CIDR blocks allowed to reach port 22. Keep tight; real access goes through Cloudflare Tunnel."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Freeform tags applied to resources"
  type        = map(string)
  default = {
    project = "coredirective"
    env     = "production"
  }
}
