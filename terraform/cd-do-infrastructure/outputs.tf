# --- TERRAFORM OUTPUTS (CD-DO-INFRASTRUCTURE) ---
# Display important information after infrastructure deployment

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

# --- RESOURCE INVENTORY ---
# TODO: Uncomment after Phase 3 Cloudflare import

output "resource_inventory" {
  description = "All resource IDs created by this configuration"
  value = {
    droplet = digitalocean_droplet.cd_alpha.id
    vpc     = digitalocean_vpc.default.id
    # tunnel_config    = cloudflare_tunnel_config.cd_alpha.id
    # dns_record_root  = cloudflare_record.root.id
    # dns_record_n8n   = cloudflare_record.n8n.id
    # dns_record_ssh   = cloudflare_record.ssh_tunnel.id
  }
}

# --- COST ESTIMATE ---

output "estimated_monthly_cost" {
  description = "Estimated monthly cost breakdown"
  value       = <<-EOT
    Cost Breakdown (Monthly):
      - Droplet (s-4vcpu-8gb):  $48.00
      - Cloudflare Tunnel:       $0.00
      - DNS Records:             $0.00
      ------------------------------
      Total:                    ~$48.00/mo

    Coverage: $200 GitHub Education credit (~4 months free, expires ~Mar 2027)
  EOT
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
