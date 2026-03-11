# --- DATADOG MONITORS & ALERTING (CD-DO-INFRASTRUCTURE) ---
# Monitors, webhook integration, and DND downtime schedule
# All alerts route through n8n webhook relay -> Telegram
# Created by Phase 07-02

# --- LOCALS ---

locals {
  dd_host = "cd-alpha-engine-do"

  # Standard tags applied to all monitors
  monitor_tags_base = [
    "env:production",
    "team:coredirective",
    "managed-by:terraform",
  ]

  # Standard remediation footer for all monitors
  telegram_notify = "@webhook-telegram-relay"
}

# --- WEBHOOK INTEGRATION ---
# Routes Datadog alerts to n8n, which relays to Telegram with severity filtering

resource "datadog_webhook" "telegram_relay" {
  name = "telegram-relay"
  url  = "https://n8n.tigouetheory.com/webhook/dd-alert"

  custom_headers = jsonencode({
    "Content-Type" = "application/json"
  })

  payload = jsonencode({
    alert_title  = "$ALERT_TITLE"
    alert_status = "$ALERT_STATUS"
    event_msg    = "$TEXT_ONLY_MSG"
    priority     = "$PRIORITY"
    tags         = "$TAGS"
    link         = "$LINK"
    snapshot     = "$SNAPSHOT"
  })

  encode_as = "json"
}

# =============================================================================
# REQUIRED MONITORS (OBS-03): disk, container, SSH
# =============================================================================

# --- Monitor: Disk Usage > 80% ---

resource "datadog_monitor" "disk_usage_high" {
  name    = "[CoreDirective] Disk Usage High on ${local.dd_host}"
  type    = "metric alert"
  message = <<-EOT
    {{#is_warning}}
    WARNING: Disk usage above 80% on {{device.name}}
    {{/is_warning}}
    {{#is_alert}}
    CRITICAL: Disk usage above 90% on {{device.name}}
    {{/is_alert}}

    **Host:** {{host.name}}
    **Device:** {{device.name}}

    **Remediation:**
    - Check large files: `ssh cd-alpha 'du -sh /root/COREDIRECTIVE_ENGINE/CD_VOL_*'`
    - Prune Docker images: `ssh cd-alpha 'docker system prune -f'`
    - Check logs: `ssh cd-alpha 'du -sh /var/log/*'`

    ${local.telegram_notify}
  EOT

  query = "avg(last_5m):avg:system.disk.in_use{host:${local.dd_host}} by {device} > 0.9"

  monitor_thresholds {
    warning  = 0.8
    critical = 0.9
  }

  renotify_interval = 120
  notify_no_data    = false
  include_tags      = true

  tags = concat(local.monitor_tags_base, ["severity:warning"])
}

# --- Monitor: Container Down ---
# Uses query alert on running container count (more reliable than service check)

resource "datadog_monitor" "container_down" {
  name    = "[CoreDirective] Container Down on ${local.dd_host}"
  type    = "query alert"
  message = <<-EOT
    {{#is_alert}}
    CRITICAL: Running container count dropped below expected threshold.
    Expected: 5 containers (db, n8n, datadog, openclaw, tunnel)
    {{/is_alert}}
    {{#is_warning}}
    WARNING: Running container count is at minimum threshold.
    {{/is_warning}}

    **Host:** {{host.name}}

    **Remediation:**
    1. Check containers: `ssh cd-alpha 'docker ps --format "table {{.Names}}\t{{.Status}}"'`
    2. Restart failed service: `ssh cd-alpha 'cd /root/COREDIRECTIVE_ENGINE && docker compose restart <name>'`
    3. Check logs: `ssh cd-alpha 'docker logs --tail 50 <container>'`

    NOTE: NEVER run 'docker compose down' via Cloudflare tunnel.

    ${local.telegram_notify}
  EOT

  query = "avg(last_1m):avg:docker.containers.running{host:${local.dd_host}} < 4"

  monitor_thresholds {
    warning  = "5"
    critical = "4"
  }

  renotify_interval = 30
  notify_no_data    = true
  no_data_timeframe = 10
  include_tags      = true

  tags = concat(local.monitor_tags_base, ["severity:critical"])
}

# --- Monitor: Failed SSH Login Attempts ---

resource "datadog_monitor" "ssh_failed_login" {
  name    = "[CoreDirective] Failed SSH Logins on ${local.dd_host}"
  type    = "log alert"
  message = <<-EOT
    {{#is_warning}}
    WARNING: 5+ failed SSH login attempts detected in 5 minutes.
    {{/is_warning}}
    {{#is_alert}}
    CRITICAL: 10+ failed SSH login attempts detected in 5 minutes.
    Possible brute force attack in progress.
    {{/is_alert}}

    **Source IP:** {{@network.client.ip.name}}

    **Remediation:**
    - Check auth log: `ssh cd-alpha 'tail -50 /var/log/auth.log | grep Failed'`
    - Block IP: `ssh cd-alpha 'ufw deny from <ip>'`
    - Review recent connections: `ssh cd-alpha 'last -20'`

    ${local.telegram_notify}
  EOT

  query = "logs(\"source:auth status:error service:sshd host:${local.dd_host}\").index(\"*\").rollup(\"count\").by(\"@network.client.ip\").last(\"5m\") > 10"

  monitor_thresholds {
    warning  = "5"
    critical = "10"
  }

  renotify_interval  = 60
  notify_no_data     = false
  enable_logs_sample = true
  include_tags       = true

  tags = concat(local.monitor_tags_base, ["severity:error", "security:ssh"])
}

# =============================================================================
# SUPPORTING MONITORS
# =============================================================================

# --- Monitor: CPU Usage High ---

resource "datadog_monitor" "cpu_usage_high" {
  name    = "[CoreDirective] CPU Usage High on ${local.dd_host}"
  type    = "metric alert"
  message = <<-EOT
    {{#is_warning}}
    WARNING: CPU usage above 85% sustained for 10 minutes.
    {{/is_warning}}
    {{#is_alert}}
    CRITICAL: CPU usage above 95% sustained for 10 minutes.
    {{/is_alert}}

    **Host:** {{host.name}}

    **Remediation:**
    - Check top processes: `ssh cd-alpha 'top -b -n1 | head -20'`
    - Check container CPU: `ssh cd-alpha 'docker stats --no-stream'`

    ${local.telegram_notify}
  EOT

  query = "avg(last_10m):100 - avg:system.cpu.idle{host:${local.dd_host}} > 95"

  monitor_thresholds {
    warning  = "85"
    critical = "95"
  }

  renotify_interval = 120
  notify_no_data    = false
  include_tags      = true

  tags = concat(local.monitor_tags_base, ["severity:warning"])
}

# --- Monitor: Memory Usage High ---

resource "datadog_monitor" "memory_usage_high" {
  name    = "[CoreDirective] Memory Usage High on ${local.dd_host}"
  type    = "metric alert"
  message = <<-EOT
    {{#is_warning}}
    WARNING: Memory usage above 85% sustained for 10 minutes.
    {{/is_warning}}
    {{#is_alert}}
    CRITICAL: Memory usage above 95% sustained for 10 minutes.
    {{/is_alert}}

    **Host:** {{host.name}}

    **Remediation:**
    - Check memory: `ssh cd-alpha 'free -h'`
    - Check container memory: `ssh cd-alpha 'docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"'`
    - Restart heavy containers if needed

    ${local.telegram_notify}
  EOT

  query = "avg(last_10m):(avg:system.mem.used{host:${local.dd_host}} / avg:system.mem.total{host:${local.dd_host}}) * 100 > 95"

  monitor_thresholds {
    warning  = "85"
    critical = "95"
  }

  renotify_interval = 120
  notify_no_data    = false
  include_tags      = true

  tags = concat(local.monitor_tags_base, ["severity:warning"])
}

# --- Monitor: PostgreSQL Connections High ---

resource "datadog_monitor" "postgres_connections_high" {
  name    = "[CoreDirective] PostgreSQL Connections High on ${local.dd_host}"
  type    = "metric alert"
  message = <<-EOT
    {{#is_warning}}
    WARNING: PostgreSQL connections above 80% of max (default max_connections=100).
    {{/is_warning}}
    {{#is_alert}}
    CRITICAL: PostgreSQL connections above 90% of max. Connection exhaustion imminent.
    {{/is_alert}}

    **Host:** {{host.name}}

    **Remediation:**
    - Check connections: `ssh cd-alpha 'docker exec cd-service-db psql -U $CD_DB_USER -d $CD_DB_NAME -c "SELECT count(*) FROM pg_stat_activity;"'`
    - Kill idle connections if needed
    - Consider increasing max_connections in PostgreSQL config

    ${local.telegram_notify}
  EOT

  query = "avg(last_5m):avg:postgresql.connections{host:${local.dd_host}} > 90"

  monitor_thresholds {
    warning  = "80"
    critical = "90"
  }

  renotify_interval = 60
  notify_no_data    = false
  include_tags      = true

  tags = concat(local.monitor_tags_base, ["severity:error"])
}

# --- Monitor: n8n Container Restarts ---

resource "datadog_monitor" "n8n_container_restarts" {
  name    = "[CoreDirective] n8n Container Restarting on ${local.dd_host}"
  type    = "query alert"
  message = <<-EOT
    {{#is_warning}}
    WARNING: n8n container has restarted 2+ times in the last hour.
    {{/is_warning}}
    {{#is_alert}}
    CRITICAL: n8n container has restarted 3+ times in the last hour. Possible crash loop.
    {{/is_alert}}

    **Host:** {{host.name}}

    **Remediation:**
    - Check n8n logs: `ssh cd-alpha 'docker logs --tail 100 cd-service-n8n'`
    - Check container status: `ssh cd-alpha 'docker inspect cd-service-n8n --format "{{.State.Status}} restarts={{.RestartCount}}"'`
    - Manual restart: `ssh cd-alpha 'cd /root/COREDIRECTIVE_ENGINE && docker compose restart cd-service-n8n'`

    ${local.telegram_notify}
  EOT

  query = "change(sum(last_1h),last_5m):avg:docker.container.restart_count{container_name:cd-service-n8n,host:${local.dd_host}} > 3"

  monitor_thresholds {
    warning  = "2"
    critical = "3"
  }

  renotify_interval = 60
  notify_no_data    = false
  include_tags      = true

  tags = concat(local.monitor_tags_base, ["severity:error"])
}

# =============================================================================
# DND DOWNTIME SCHEDULE
# =============================================================================
# Mutes Sev 3-4 (warning + error) monitors from 10 PM - 8:30 AM ET daily
# Sev 0-2 (critical) monitors always notify

resource "datadog_downtime_schedule" "dnd_warning" {
  scope   = "managed-by:terraform AND severity:warning"
  message = "DND window: Sev 4 (warning) monitors muted 10 PM - 8:30 AM ET"

  display_timezone = "America/New_York"

  monitor_identifier {
    monitor_tags = ["severity:warning", "managed-by:terraform"]
  }

  recurring_schedule {
    timezone = "America/New_York"

    recurrence {
      rrule    = "FREQ=DAILY"
      start    = "2026-03-11T22:00:00"
      duration = "630m"
    }
  }
}

resource "datadog_downtime_schedule" "dnd_error" {
  scope   = "managed-by:terraform AND severity:error"
  message = "DND window: Sev 3 (error) monitors muted 10 PM - 8:30 AM ET"

  display_timezone = "America/New_York"

  monitor_identifier {
    monitor_tags = ["severity:error", "managed-by:terraform"]
  }

  recurring_schedule {
    timezone = "America/New_York"

    recurrence {
      rrule    = "FREQ=DAILY"
      start    = "2026-03-11T22:00:00"
      duration = "630m"
    }
  }
}
