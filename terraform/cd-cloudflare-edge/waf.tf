# Custom WAF and rate limit on the Cloudflare Free plan.
# Free plan capacity: 5 custom rules, 1 rate limit rule. Both rulesets are
# LIVE and are adopted by import (see README). Rule expressions are built
# from variables so no hostname appears in code.
#
# Layering from the edge inward:
#   1. Cloudflare Free Managed Ruleset (zone-level, not a resource here)
#   2. This custom ruleset (scanner UAs, admin geo-fence, honeytokens, header anomaly)
#   3. Rate limit on /webhook/* (below)
#   4. Cloudflare Access (access_n8n.tf) evaluated after the WAF

resource "cloudflare_ruleset" "custom_waf" {
  zone_id     = var.cf_zone_id
  name        = "cd_custom_waf"
  description = "CoreDirective custom WAF: bot UA, geo-fence admin, honeytokens, body cap, header anomaly"
  kind        = "zone"
  phase       = "http_request_firewall_custom"

  # 1. Scanner user agents and empty UA, all hosts.
  rules {
    action      = "block"
    expression  = "(http.user_agent contains \"sqlmap\") or (http.user_agent contains \"nikto\") or (http.user_agent contains \"masscan\") or (http.user_agent contains \"nuclei\") or (http.user_agent contains \"acunetix\") or (http.user_agent contains \"nessus\") or (http.user_agent contains \"openvas\") or (http.user_agent contains \"wpscan\") or (http.user_agent contains \"zgrab\") or (http.user_agent eq \"\")"
    description = "Block known scanner user agents and empty UA"
    enabled     = true
  }

  # 2. Geo-fence admin surfaces to the home country.
  # Telegram's webhook egress is not in the home country, so its published
  # ranges are carved out here. Without this carve-out the bot webhook got
  # a 403 from our own edge (observed 2026-09-01 in getWebhookInfo).
  rules {
    action      = "block"
    expression  = "(http.host in {${local.admin_host_set}}) and (ip.geoip.country ne \"${var.home_country}\") and not (ip.src in {${local.telegram_ip_set}})"
    description = "Geo-fence admin subdomains to ${var.home_country} (Telegram egress exempt)"
    enabled     = true
  }

  # 3. Honeytoken paths: nothing legitimate ever asks for these.
  rules {
    action      = "block"
    expression  = "(http.request.uri.path contains \".env\") or (http.request.uri.path contains \".git/config\") or (http.request.uri.path contains \"wp-admin\") or (http.request.uri.path contains \"wp-login\") or (http.request.uri.path contains \"phpmyadmin\") or (http.request.uri.path contains \"/admin.php\") or (http.request.uri.path contains \"/xmlrpc.php\")"
    description = "Honeytoken paths -- block scanners probing for legacy stack"
    enabled     = true
  }

  # 4. Header anomaly: real browsers and API clients send Accept.
  # Telegram exempt for the same reason as rule 2.
  rules {
    action      = "challenge"
    expression  = "(http.host in {${local.admin_host_set}}) and (not http.request.headers[\"accept\"][0] contains \"/\") and not (ip.src in {${local.telegram_ip_set}})"
    description = "Challenge admin traffic with missing Accept header (Telegram egress exempt)"
    enabled     = true
  }
}

# Per-IP rate limit on webhook endpoints. Free plan: period 10s, timeout 10s.
resource "cloudflare_ruleset" "rate_limit" {
  zone_id     = var.cf_zone_id
  name        = "cd_rate_limit"
  description = "Per-IP rate limit on webhook endpoints"
  kind        = "zone"
  phase       = "http_ratelimit"

  rules {
    action      = "block"
    expression  = "(http.request.uri.path contains \"/webhook/\")"
    description = "Rate limit webhook endpoints: 60 req/min per IP"
    enabled     = true

    ratelimit {
      characteristics     = ["ip.src", "cf.colo.id"]
      period              = 10
      requests_per_period = 10
      mitigation_timeout  = 10
    }
  }
}
