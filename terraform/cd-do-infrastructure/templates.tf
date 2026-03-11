# --- TEMPLATES (CD-DO-INFRASTRUCTURE) ---
# Rendered configuration files for disaster recovery and documentation
# WARNING: Do NOT attach cloud-init to existing droplet (user_data is ForceNew)

# Render Docker Compose from template
locals {
  rendered_docker_compose = templatefile("${path.module}/templates/docker-compose.yml.tftpl", {
    n8n_hostname = "n8n.tigouetheory.com"
    n8n_port     = "5678"
    dd_hostname  = var.do_droplet_name
    dd_site      = "us5.datadoghq.com"
  })
}

# Render cloud-init bootstrap script
resource "local_file" "cloud_init" {
  content = templatefile("${path.module}/templates/cloud-init.sh.tftpl", {
    docker_compose_content = local.rendered_docker_compose
  })
  filename        = "${path.module}/rendered/cloud-init.sh"
  file_permission = "0755"
}

# Render Docker Compose as standalone file
resource "local_file" "docker_compose" {
  content         = local.rendered_docker_compose
  filename        = "${path.module}/rendered/docker-compose.yml"
  file_permission = "0644"
}
