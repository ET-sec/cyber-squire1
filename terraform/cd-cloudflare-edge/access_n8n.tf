# Cloudflare Access in front of the n8n hostname.
#
# Every path on the host is gated, webhooks included. That is deliberate:
# a webhook URL is not a credential. Machine callers present a service
# token (CF-Access-Client-Id / CF-Access-Client-Secret); humans get a
# one-time PIN to an allowed email.
#
# The one carve-out is the Telegram Trigger webhook. Telegram cannot send
# Access headers, so its path gets a bypass policy scoped to Telegram's
# published egress ranges only. Anything else hitting that path still
# meets the login wall. The rest of the trust for that path lives in n8n
# (chat ID restriction on the trigger node) and in the WAF rate limit.

resource "cloudflare_access_application" "n8n" {
  account_id                = var.cf_account_id
  name                      = "n8n SOAR"
  domain                    = local.n8n_host
  type                      = "self_hosted"
  session_duration          = "24h"
  auto_redirect_to_identity = false
  app_launcher_visible      = true

  cors_headers {
    allowed_methods   = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    allowed_origins   = ["https://${local.n8n_host}"]
    allow_credentials = true
    max_age           = 600
  }
}

resource "cloudflare_access_policy" "n8n_allow_admin" {
  application_id = cloudflare_access_application.n8n.id
  account_id     = var.cf_account_id
  name           = "Allow CoreDirective admins"
  precedence     = 1
  decision       = "allow"

  include {
    email = var.admin_emails
  }
}

# Shared machine token for automation callers (Squire, schedulers). Per-agent
# tokens are the next step; this one is adopted so its rotation is code-managed.
resource "cloudflare_access_service_token" "n8n_automation" {
  account_id = var.cf_account_id
  name       = "n8n-automation-callers"
}

resource "cloudflare_access_policy" "n8n_allow_service_token" {
  application_id = cloudflare_access_application.n8n.id
  account_id     = var.cf_account_id
  name           = "Allow service tokens for automation"
  precedence     = 2
  decision       = "non_identity"

  include {
    service_token = [cloudflare_access_service_token.n8n_automation.id]
  }
}

# --- Telegram webhook: path-scoped, IP-scoped bypass ---
# A path-scoped application is evaluated before the host-wide one. The
# bypass applies only to sources inside Telegram's published ranges; every
# other caller to this path falls through to the host application above.
resource "cloudflare_access_application" "n8n_telegram_webhook" {
  account_id                = var.cf_account_id
  name                      = "n8n Telegram webhook (Telegram egress only)"
  domain                    = "${local.n8n_host}${var.telegram_webhook_prefix}"
  type                      = "self_hosted"
  session_duration          = "24h"
  auto_redirect_to_identity = false
  app_launcher_visible      = false
}

resource "cloudflare_access_policy" "n8n_telegram_bypass" {
  application_id = cloudflare_access_application.n8n_telegram_webhook.id
  account_id     = var.cf_account_id
  name           = "Bypass for Telegram webhook egress ranges"
  precedence     = 1
  decision       = "bypass"

  include {
    ip = var.telegram_ip_ranges
  }
}
