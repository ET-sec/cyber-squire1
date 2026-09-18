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
  description = "Subdomains behind the WAF geo-fence and header rule: the admin UIs behind Access. The identity provider's hostname stays out, because the edge exchanges the login code with it from its own network."
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
  description = "Telegram Bot API webhook egress ranges, the full list published at core.telegram.org/resources/cidr.txt (read 2026-09-11). Only these sources may bypass Access on the Telegram webhook path. The two-range list from the webhooks guide missed the range Telegram delivered from on 2026-09-11 and the geo-fence answered 403."
  type        = list(string)
  default     = ["91.105.192.0/23", "91.108.4.0/22", "91.108.8.0/22", "91.108.12.0/22", "91.108.16.0/22", "91.108.20.0/22", "91.108.56.0/22", "149.154.160.0/20", "185.76.151.0/24", "2001:67c:4e8::/48", "2001:b28:f23c::/48", "2001:b28:f23d::/48", "2001:b28:f23f::/48", "2a0a:f280::/32"]
}

variable "home_country" {
  description = "Country code the admin geo-fence allows."
  type        = string
  default     = "US"
}

locals {
  admin_hosts   = [for s in var.admin_subdomains : "${s}.${var.domain}"]
  n8n_host      = "n8n.${var.domain}"
  keycloak_host = "${var.keycloak_subdomain}.${var.domain}"

  # Cloudflare rules-language set literals: {"a" "b"} and {1.2.3.0/24 5.6.7.0/22}
  admin_host_set  = join(" ", [for h in local.admin_hosts : "\"${h}\""])
  telegram_ip_set = join(" ", var.telegram_ip_ranges)
}

variable "cf_tunnel_id" {
  description = "Id of the tunnel that carries every route to the origin. Real value in the gitignored terraform.tfvars; an identifier, not a credential, and not marked sensitive so the imported resource plans clean."
  type        = string
}

variable "keycloak_subdomain" {
  description = "Subdomain label of the identity provider's public hostname; the zone comes from the domain variable, the same way the admin hostnames are built."
  type        = string
  default     = "auth"
}

variable "keycloak_realm" {
  description = "Realm whose login flow (the discovery document, the protocol endpoints, the form actions) is routed to the identity provider beside its static assets, and nothing else. Real value in the gitignored terraform.tfvars."
  type        = string
  sensitive   = true
}

variable "otp_identity_provider_id" {
  description = "Id of the account's one-time PIN identity provider, the login path that stays beside the identity provider so a fault there cannot lock the operator out. Real value in the gitignored terraform.tfvars."
  type        = string
}

variable "keycloak_client_id" {
  description = "Client id registered in the identity provider for the edge login."
  type        = string
  default     = "cloudflare-access"
}

variable "keycloak_client_secret" {
  description = "That client's secret. Never in a file: passed as TF_VAR_keycloak_client_secret from the secrets manager at run time."
  type        = string
  sensitive   = true
}
