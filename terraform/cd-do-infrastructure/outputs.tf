# --- OUTPUT VALUES ---
# Key infrastructure values for reference and downstream use.

output "droplet_ip" {
  description = "Public IPv4 address of the cd-alpha droplet"
  value       = digitalocean_droplet.cd_alpha.ipv4_address
}

output "droplet_id" {
  description = "DigitalOcean droplet ID"
  value       = digitalocean_droplet.cd_alpha.id
}

output "vpc_id" {
  description = "DigitalOcean VPC ID"
  value       = digitalocean_vpc.default.id
}

output "ssh_command" {
  description = "SSH command to connect to the droplet"
  value       = "ssh root@${digitalocean_droplet.cd_alpha.ipv4_address}"
}

output "n8n_url" {
  description = "n8n dashboard URL (via Cloudflare Tunnel)"
  value       = "https://n8n.tigouetheory.com"
}
