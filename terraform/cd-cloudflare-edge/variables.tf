variable "cf_account_id" {
  description = "Cloudflare account ID. Real value in the gitignored terraform.tfvars."
  type        = string
}

variable "cf_zone_id" {
  description = "Cloudflare zone ID for the apex domain."
  type        = string
}

variable "domain" {
  description = "Apex zone name (example.com). Hostnames are derived from it so no real hostname sits in this code."
  type        = string
}

variable "admin_subdomains" {
  description = "Subdomains that carry admin UIs behind Access and the WAF geo-fence."
  type        = list(string)
  default     = ["n8n", "langfuse", "squire"]
}

variable "admin_emails" {
  description = "Human identities allowed through Access on admin surfaces."
  type        = list(string)
  sensitive   = true
}

variable "telegram_webhook_prefix" {
  description = "Path prefix of the n8n Telegram Trigger webhook (/webhook/<id>). Treated as a secret: it is the only thing between Telegram and the workflow besides the IP allowlist."
  type        = string
  sensitive   = true
}

variable "telegram_ip_ranges" {
  description = "Telegram Bot API webhook egress ranges, published at core.telegram.org/bots/webhooks. Only these sources may bypass Access on the Telegram webhook path."
  type        = list(string)
  default     = ["149.154.160.0/20", "91.108.4.0/22"]
}

variable "home_country" {
  description = "Country code the admin geo-fence allows."
  type        = string
  default     = "US"
}

locals {
  admin_hosts = [for s in var.admin_subdomains : "${s}.${var.domain}"]
  n8n_host    = "n8n.${var.domain}"

  # Cloudflare rules-language set literals: {"a" "b"} and {1.2.3.0/24 5.6.7.0/22}
  admin_host_set  = join(" ", [for h in local.admin_hosts : "\"${h}\""])
  telegram_ip_set = join(" ", var.telegram_ip_ranges)
}
