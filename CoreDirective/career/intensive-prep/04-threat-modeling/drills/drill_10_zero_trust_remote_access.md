# Drill 10: Zero Trust Remote Access (Cloudflare Tunnel + Teleport)

## Prompt
"Threat model your remote access stack. No VPN. Cloudflare Tunnel exposes services without opening ports. Teleport handles SSH and Kubernetes access with MFA, recording, and just-in-time roles."

This drill matches Emmanuel's actual stack and is the strongest "I built this" story for the interview.

## Scope (Phase 1)

Assets:
- Internal services exposed via Tunnel (n8n, SSH, future apps)
- Production hosts and Kubernetes clusters
- Teleport CA (issues short-lived certs)
- Session recordings (sensitive evidence)
- Cloudflare account credentials
- Tunnel daemon credentials on the origin

Actors:
- Engineers (legitimate access)
- Compromised engineer laptop
- External attacker (credential phishing)
- Malicious insider
- Cloudflare itself (out of scope, vendor risk)
- Auditor (read access to session recordings)

Data classes:
- Session recordings (high)
- SSH keys / Teleport certs (highest)
- Cloudflare credentials (highest)
- Internal app data (varies)

Assumptions:
- Cloudflare Access in front of Tunnel for identity gating
- Okta is the IdP federating to both CF Access and Teleport
- Hardware-backed FIDO2 keys for engineers
- Teleport audit log shipped to immutable storage
- Tunnel daemon runs on each origin, no inbound ports

## DFD

```
                                   INTERNET BOUNDARY
[ Engineer Laptop ]
       |
       | 1. https://n8n.tigouetheory.com
       v
( Cloudflare Edge / WAF / Access )
       |
       | 2. redirect to Okta
       v
[ Engineer ] --> ( Okta IdP ) <-- WebAuthn / FIDO2
       |
       | 3. id_token + cf-jwt
       v
( Cloudflare Access ) -- 4. allow if policy match -->
       |
       | 5. proxied via Tunnel
       v
- - - - - - - - - - - - - - - - - - ORIGIN TRUST BOUNDARY (no inbound ports)
       v
( cloudflared on origin host )
       |
       | localhost
       v
( app: n8n :5678 )

[ Engineer ] --tsh login--> ( Teleport Proxy )
                                       |
                                       | 6. OIDC to Okta
                                       v
                                  ( Okta IdP )
                                       |
                                       | 7. role assertion
                                       v
                                  ( Teleport Auth )
                                       |
                                       | 8. issues short-lived cert (TTL 1-8h)
                                       v
                                  [ Engineer ] uses cert
                                       |
                                       v
                                  ( Teleport Node Agent )
                                       |
                                       v
                                  ( target host / kube apiserver )
                                       |
                                       v
                              ===== Session Recording =====
                                       |
                                       v
                                  ( Audit / SIEM )
```

Trust boundaries:
1. Engineer laptop to Cloudflare edge (TB1)
2. CF Access to Okta (TB2)
3. CF Access to origin via Tunnel (TB3, no inbound ports)
4. Tunnel daemon to localhost service (TB4)
5. Engineer to Teleport Proxy (TB5)
6. Teleport Proxy to Auth (TB6)
7. Teleport Auth to Node Agent / kube (TB7)
8. Session recording at rest (TB8)
9. Cloudflare control plane (TB9, vendor)

## STRIDE matrix

| # | Boundary | STRIDE | Threat | L | I | Risk |
|---|----------|--------|--------|---|---|------|
| 1 | TB1 | S | Stolen Okta credentials reused, MFA fatigue grants access | M | H | H |
| 2 | TB1 | S | Cookie / session token theft via infostealer on engineer laptop | M | H | H |
| 3 | TB2 | T | Okta tenant compromise (downstream of vendor breach) | L | H | M |
| 4 | TB3 | I | Tunnel daemon credentials leak from origin filesystem | L | H | M |
| 5 | TB3 | E | Tunnel exposes a service that does not implement its own auth (assumes CF Access is enough) | M | H | H |
| 6 | TB4 | E | Localhost service has CSRF or open admin endpoint, anyone past CF Access pivots | M | H | H |
| 7 | TB5 | S | Phishing for Teleport TTL cert via fake `tsh login` page | L | H | M |
| 8 | TB6 | T | Teleport CA compromise, attacker mints arbitrary certs | L | H | M |
| 9 | TB7 | E | Teleport role too broad: a single role grants prod-cluster admin | M | H | H |
| 10 | TB7 | R | Session recording disabled or rotated, evidence lost | L | H | M |
| 11 | TB8 | I | Session recording leaks secrets typed into terminals | M | H | H |
| 12 | TB8 | T | Recording tampered before audit | L | H | M |
| 13 | TB9 | I | Cloudflare account credentials leaked, attacker reroutes Tunnel | L | H | M |
| 14 | TB1 | S | Account takeover via SSO recovery weakness (email-based reset) | L | H | M |
| 15 | TB5 | E | Engineer holds long-lived cert past TTL via clock skew | L | M | L |
| 16 | TB7 | E | Bastion host on the prod side allows lateral movement once on it | M | H | H |

## Top 10

1. (#1) Phished credentials + MFA fatigue
2. (#2) Cookie theft via infostealer
3. (#5) Service-behind-tunnel without own auth
4. (#9) Over-broad Teleport role
5. (#16) Bastion lateral movement
6. (#11) Session recording leaks secrets
7. (#6) Localhost service CSRF / open admin
8. (#13) Cloudflare account compromise
9. (#3) Okta tenant compromise
10. (#10) Session recording disabled

## Mitigations

| # | Primary | Compensating | Cost |
|---|---------|--------------|------|
| 1 | Phishing-resistant MFA only (FIDO2/WebAuthn), no SMS, no TOTP for engineers | Conditional access: device must be MDM-attested, on-network for very-sensitive resources | M |
| 2 | Device-bound sessions, short TTL (8h), idle timeout 30 min | EDR on laptops alerts on cookie-jar reads | L |
| 3 | Defense-in-depth: every backend service still does its own authn (mTLS or session check), even behind CF Access | Periodic test harness probes endpoints with no auth headers | M |
| 4 | Tunnel daemon credentials in Vault, scoped per host, rotated 30 days | Alert on daemon re-registration from new host id | L |
| 5 | Teleport roles minimized: `prod-read`, `prod-troubleshoot`, `prod-deploy`, with JIT elevation for breakglass | Quarterly access review, automated role drift check | M |
| 6 | Sessions recorded by default, disable requires emergency-bypass with security alert | Tamper-evident log shipped to immutable storage (S3 Object Lock) | M |
| 7 | Restricted commands and command filters in Teleport for sensitive roles (block `cat /var/log/secret`) | Session-recording redactor masks tokens in real time | M |
| 8 | Cloudflare account: mandatory 2FA via FIDO2, scope API tokens minimally, rotate quarterly | Read-only audit account for change monitoring | L |
| 9 | Okta admin actions require step-up auth, recovery via phone callback to security team only | Datadog alert on admin-config change | L |
| 10 | Bastion replaced by Teleport-mediated access; if bastion exists, no shell, only port-forward | Detect lateral SSH from bastion, alert on any | M |
| 11 | Service auth fail-safe: HTTP middleware that requires Cloudflare-Access-JWT plus app-session, deny by default | Test suite confirms middleware on every route | L |

## Residual risk

After mitigations: 0 HIGH, 6 MEDIUM, 10 LOW.

MEDIUMs:
- Okta tenant compromise: accepted because vendor-side, mitigation is breakglass procedure documented.
- Cloudflare account compromise: accepted with FIDO2 plus monitoring; if it falls, recovery runbook activates.
- Teleport CA compromise: accepted because Teleport supports CA rotation, runbook practiced.
- Session recording leaks of typed secrets: accepted with redactor plus engineer training to use vault-injected secrets.
- Bastion lateral: accepted while bastion exists; long-term plan removes it.
- Cookie theft: accepted with EDR plus device binding plus short TTL.

I would not ship without: phishing-resistant MFA, app-level auth behind Tunnel, Teleport session recording.

## Detections

- Phishing-resistant MFA bypass attempts: alert on fallback to TOTP / SMS.
- New device login: any new device fingerprint pages, even if MFA passed.
- Unusual Teleport role escalation: alert on JIT elevation outside business hours, alert on use of breakglass role.
- Session recording disabled: alert immediately, page security.
- Tunnel re-registration: alert on Tunnel ID associated to new origin.
- Cloudflare config change: webhook to security-events channel, daily diff vs IaC.
- Bastion shell: any successful interactive session pages.

Closing line:
"Zero trust remote access replaces 'are you on the VPN' with 'who are you, on what device, doing what action'. Every layer assumes breach of the previous layer. Cloudflare Tunnel removes the listening port; Cloudflare Access verifies identity; Teleport verifies authorization; the app still does its own authn; and the session is recorded. The threat surface widens because there are more vendors in the chain, but the blast radius narrows because no single compromise gets you all the way through. Residual risk is bounded by IdP integrity. If Okta falls, we have to rotate everything fast, and the runbook for that is rehearsed quarterly."
