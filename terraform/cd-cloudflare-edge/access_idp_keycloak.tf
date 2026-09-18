# The identity provider's day-one client: an additional OIDC identity provider
# on the edge, beside the one-time PIN provider (plan 24-02).
#
# The application in front of the orchestration host lists both providers and
# keeps auto_redirect_to_identity off, so the login page offers a chooser and
# the email code path survives a fault in the identity provider. The provider's
# endpoints are derived from the realm's discovery document, which is one of
# the path families the tunnel routes to it.

resource "cloudflare_access_identity_provider" "keycloak" {
  account_id = var.cf_account_id
  name       = "Keycloak"
  type       = "oidc"

  config {
    client_id        = var.keycloak_client_id
    client_secret    = var.keycloak_client_secret
    auth_url         = "https://${local.keycloak_host}/realms/${var.keycloak_realm}/protocol/openid-connect/auth"
    token_url        = "https://${local.keycloak_host}/realms/${var.keycloak_realm}/protocol/openid-connect/token"
    certs_url        = "https://${local.keycloak_host}/realms/${var.keycloak_realm}/protocol/openid-connect/certs"
    scopes           = ["openid", "email", "profile"]
    email_claim_name = "email"
    pkce_enabled     = true
  }
}
