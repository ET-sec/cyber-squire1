# --- TERRAFORM OUTPUTS (CD-DO-INFRASTRUCTURE) ---
# Display important information after infrastructure deployment

# --- COST CALCULATION LOCALS ---

locals {
  # DigitalOcean shared CPU droplet pricing (monthly USD)
  # Source: https://www.digitalocean.com/pricing/droplets
  droplet_costs = {
    "s-1vcpu-512mb" = 4
    "s-1vcpu-1gb"   = 6
    "s-1vcpu-2gb"   = 12
    "s-2vcpu-2gb"   = 18
    "s-2vcpu-4gb"   = 24
    "s-4vcpu-8gb"   = 48
    "s-8vcpu-16gb"  = 96
    "s-16vcpu-32gb" = 192
  }
  droplet_monthly = lookup(local.droplet_costs, var.do_droplet_size, -1)
  spaces_monthly  = 5 # DO Spaces minimum ($5/mo for 250GB)

  credit_months = local.droplet_monthly >= 0 ? floor(200 / (local.droplet_monthly + local.spaces_monthly)) : 0

  cost_breakdown = local.droplet_monthly >= 0 ? join("\n", [
    "Cost Breakdown (Monthly):",
    format("  - Droplet (%s):  $%.2f", var.do_droplet_size, local.droplet_monthly),
    "  - Cloudflare Tunnel:                  $0.00",
    "  - DNS Records:                        $0.00",
    format("  - DO Spaces (state backend):         ~$%.2f", local.spaces_monthly),
    "  ----------------------------------------",
    format("  Total:                               ~$%.2f/mo", local.droplet_monthly + local.spaces_monthly),
    "",
    format("Coverage: $200 GitHub Education credit (~%d months free)", local.credit_months),
  ]) : "WARNING: Unknown droplet slug '${var.do_droplet_size}' -- cannot calculate cost. Update the droplet_costs lookup table in outputs.tf."
}

# --- DROPLET INFORMATION ---

output "droplet_ip" {
  description = "Public IPv4 address of the cd-alpha droplet"
  value       = digitalocean_droplet.cd_alpha.ipv4_address
}

output "droplet_id" {
  description = "ID of the cd-alpha droplet"
  value       = digitalocean_droplet.cd_alpha.id
}

# --- NETWORK INFORMATION ---

output "vpc_id" {
  description = "ID of the DigitalOcean VPC"
  value       = digitalocean_vpc.default.id
}

# --- ACCESS ---

output "ssh_command" {
  description = "SSH command to connect to the cd-alpha droplet"
  value       = "ssh root@${digitalocean_droplet.cd_alpha.ipv4_address}"
}

output "n8n_url" {
  description = "n8n dashboard URL (via Cloudflare Tunnel)"
  value       = "https://n8n.tigouetheory.com"
}

# --- SERVICE URLS ---

output "service_urls" {
  description = "All service access URLs"
  value = {
    n8n_dashboard = "https://n8n.tigouetheory.com"
    ssh_tunnel    = "ssh.tigouetheory.com (via cloudflared)"
    openclaw_api  = "http://${digitalocean_droplet.cd_alpha.ipv4_address}:18789/v1/chat/completions"
    datadog       = "https://us5.datadoghq.com"
    website       = "https://tigouetheory.com"
  }
}

# --- RESOURCE INVENTORY ---

output "resource_inventory" {
  description = "All resource IDs created by this configuration"
  value = {
    droplet         = digitalocean_droplet.cd_alpha.id
    vpc             = digitalocean_vpc.default.id
    firewall        = digitalocean_firewall.cd_alpha.id
    ssh_key         = digitalocean_ssh_key.coredirective.id
    tunnel_config   = cloudflare_tunnel_config.cd_alpha.id
    dns_record_root = cloudflare_record.root.id
    dns_record_www  = cloudflare_record.www.id
    dns_record_n8n  = cloudflare_record.n8n.id
    dns_record_ssh  = cloudflare_record.ssh_tunnel.id
  }
}

# --- COST ESTIMATE ---

output "estimated_monthly_cost" {
  description = "Estimated monthly cost breakdown (dynamic based on droplet size)"
  value       = local.cost_breakdown
}

# --- VERIFICATION COMMANDS ---

output "verification_commands" {
  description = "Commands to verify deployment"
  value       = <<-EOT
    # Check droplet status
    doctl compute droplet get ${digitalocean_droplet.cd_alpha.id} --format ID,Name,Status,PublicIPv4

    # Verify SSH access
    ssh root@${digitalocean_droplet.cd_alpha.ipv4_address} 'hostname && uptime'

    # Verify n8n via tunnel
    curl -sI https://n8n.tigouetheory.com | head -1

    # Check Docker stack
    ssh root@${digitalocean_droplet.cd_alpha.ipv4_address} 'cd /root/COREDIRECTIVE_ENGINE && docker compose ps'
  EOT
}
