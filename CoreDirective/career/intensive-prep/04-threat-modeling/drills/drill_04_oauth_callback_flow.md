# Drill 04: Third-Party OAuth Integration

## Prompt
"Threat model an OAuth 2.0 authorization code flow where our app integrates with a third-party SaaS (think Slack or Google) to read user data. Cover the full callback path."

## Scope (Phase 1)

Assets:
- OAuth client_id and client_secret
- Issued access tokens and refresh tokens for each user
- User identity records linking our user to third-party account
- Scopes granted by users

Actors:
- End user (the person granting consent)
- Authorization server (third-party SaaS)
- Resource server (third-party SaaS API)
- Internal app server
- Adversarial user (CSRF, code interception)
- Compromised third party (token leakage)

Data classes:
- OAuth tokens (HIGH)
- Client secret (HIGH)
- User identity binding (HIGH)
- Scopes and consent records (MEDIUM)

Assumptions:
- Authorization Code with PKCE is required
- Tokens stored encrypted at rest
- Single tenant, multi-user
- We act as a confidential client (server-side)

## DFD

```
                                  INTERNET BOUNDARY
[ User Browser ]
      |
      | 1. Click "Connect Slack"
      v
( Our App ) -- 2. 302 to authz_url with state, code_challenge, scope --> [ User Browser ]
                                                                              |
                                                                              | 3. follow redirect
                                                                              v
                                                                  ( Third-Party Authz Server )
                                                                              |
                                                                              | 4. user logs in, consents
                                                                              v
                                                                  [ User Browser ]
                                                                              |
                                                                              | 5. 302 to our /callback?code&state
                                                                              v
                                                                  ( Our App /callback )
                                                                       /
                                                                      /
                                                          6. POST token endpoint
                                                          (code, code_verifier, client_secret)
                                                                     /
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -/
                                                                   v
                                                       ( Third-Party Token Endpoint )
                                                                   |
                                                                   | 7. access_token, refresh_token
                                                                   v
                                                          ( Our App ) -> ====== Token DB =====

                                                          8. user calls our app
                                                                   |
                                                                   | use access_token
                                                                   v
                                                       ( Third-Party Resource API )
```

Trust boundaries:
1. User browser to our app (TB1)
2. Our app to authz server (TB2, via redirect)
3. User browser to authz server (TB3)
4. Authz server back to our /callback (TB4)
5. Our app to token endpoint (TB5, server-to-server)
6. Token DB at rest (TB6)
7. Our app to resource server with bearer token (TB7)

## STRIDE matrix

| # | Boundary | STRIDE | Threat | L | I | Risk |
|---|----------|--------|--------|---|---|------|
| 1 | TB1 | T | CSRF on initiate-flow endpoint, attacker links victim's account to attacker's third party | H | H | H |
| 2 | TB1/TB4 | S | State parameter not validated on /callback, attacker injects code | H | H | H |
| 3 | TB3 | S | Authorization code interception via referer leak or open redirector | M | H | H |
| 4 | TB4 | S | Open redirect on /callback redirect_uri, code stolen | M | H | H |
| 5 | TB5 | I | client_secret leaks via env var dump, log file, or code commit | M | H | H |
| 6 | TB5 | T | Token endpoint MITM rewrites tokens (no cert pinning) | L | H | M |
| 7 | TB6 | I | Tokens at rest stolen via DB compromise | L | H | M |
| 8 | TB7 | E | Access token grants more scope than the feature needs | H | M | H |
| 9 | TB7 | R | Token usage not logged per-user, cannot trace abuse | M | M | M |
| 10 | TB1 | E | "Connect" link works without active session, attacker pre-binds | M | H | H |
| 11 | TB2 | T | code_challenge omitted (PKCE not enforced) | M | H | H |
| 12 | TB4 | T | Code reuse not detected, attacker replays an intercepted code | L | H | M |
| 13 | TB7 | I | Refresh tokens never expire, stolen one is forever | M | H | H |
| 14 | TB1 | I | Tokens leaked via client-side error logging (Sentry, LogRocket) | M | H | H |
| 15 | TB3 | S | User logs into wrong account at IdP, our app does not detect identity mismatch | L | M | L |

## Top 10

1. (#1) CSRF on initiate
2. (#2) State validation missing
3. (#11) PKCE not enforced
4. (#5) client_secret leak
5. (#4) Open redirect
6. (#13) Refresh-token longevity
7. (#8) Over-scoped token
8. (#3) Code interception via referer
9. (#14) Client-side token leak
10. (#10) Pre-bind via no-session initiate

## Mitigations

| # | Primary | Compensating | Cost |
|---|---------|--------------|------|
| 1 | Cryptographically random `state` value bound to session, validate on callback, reject mismatch | Log every state-validation failure, alert | L |
| 2 | Enforce PKCE for every flow (S256 challenge), generate verifier server-side | Reject any callback whose code does not have a paired verifier | L |
| 3 | client_secret in Doppler/Vault, never in env files in git, rotated quarterly | Secret scanning in CI, GitHub Advanced Security | L |
| 4 | Strict allowlist of redirect_uri values registered with the authz server | Server-side check that the inbound URI matches exactly | L |
| 5 | Refresh tokens encrypted at rest with KMS, rotated on each use, max lifetime 30 days | Detect refresh-token replay (same token used twice), revoke | M |
| 6 | Request minimum-necessary scope per feature, separate flows for separate scopes | Quarterly scope audit, downgrade unused | L |
| 7 | Set HTTP `Referrer-Policy: no-referrer`, never put codes in URLs that a third party could log | Test referrer behavior in CI | L |
| 8 | Tokens never sent to client side, server-side proxy for all third-party calls | If client must hold a token, scope it to read-only, short TTL | M |
| 9 | Initiate endpoint requires authenticated session, reject anonymous starts | CSRF token plus state | L |
| 10 | Cert pinning at HTTP client layer for token endpoint | TLS 1.3 enforced, no fallback | L |

## Residual risk

After mitigations: 0 HIGH, 4 MEDIUM, 11 LOW.

MEDIUMs:
- Token at-rest theft: accepted because if the DB is compromised we have bigger problems; mitigation is encryption with KMS plus token rotation.
- Identity mismatch at IdP: accepted because we cannot fully detect, compensation is showing the connected identity in user UI for self-service revocation.
- Refresh token MITM during rotation: accepted because TLS plus pinning is the standard control.
- Logging of token usage: accepted as low impact because tokens themselves are scoped and short-lived.

The HIGH I would not ship without: state validation and PKCE. They are free and they shut down the entire CSRF and code-interception class.

## Detections

- State mismatch on /callback: alert on any rate above zero, page if sustained.
- Refresh-token reuse: detect when the same refresh token is presented twice; revoke entire grant and alert.
- Client_secret usage from unexpected IP: alert on token-endpoint calls from any IP not in our egress range.
- Scope-escalation request: monitor scope changes per app, alert on any feature requesting a scope it did not need before.
- Anomalous resource usage: per-user API call rate, alert on top 1 percent.

Closing line:
"OAuth is mostly a series of redirects, and every redirect is a trust boundary. The most common breach pattern is not crypto, it is a state parameter someone forgot to validate. The compensating controls are PKCE, scope minimization, and refresh-token rotation, in that order. The residual risk is bounded by storage encryption and short token lifetimes."
