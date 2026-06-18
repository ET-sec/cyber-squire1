# Drill 06: Internal Admin Panel With OIDC SSO

## Prompt
"Threat model an internal admin tool used by 200 employees. Auth via Okta OIDC. The tool can read and write production user data and trigger refunds, account deletions, and feature flag changes."

## Scope (Phase 1)

Assets:
- Production user data accessible to admins
- Refund authority
- Feature-flag control plane
- Admin sessions and OIDC tokens
- Audit logs of admin actions

Actors:
- Internal admins (varied roles: support, eng, finance)
- Internal attacker (compromised employee laptop)
- External attacker (phishing, credential stuffing)
- Okta IdP
- IT operating MDM

Data classes:
- User PII (high)
- Account state changes (high, financial impact)
- Audit logs (high, compliance asset)

Assumptions:
- Okta with MFA mandatory
- Admin laptops MDM-managed
- Tool is on a private domain with Cloudflare Access in front
- Network is zero-trust (no VPN required)
- Audit logs ship to Datadog

## DFD

```
                                  INTERNET BOUNDARY
[ Admin Browser ]
       |
       | 1. https://admin.internal
       v
( Cloudflare Access ) -- Identity-Aware Proxy --
       |
       | 2. redirect to Okta
       v
[ Admin Browser ] --> ( Okta IdP ) <-- MFA, SSO --
       |
       | 3. ID + access token
       v
( Cloudflare Access ) -- validates token, sets cf-jwt --
       |
- - - - - - - - - - - - - - - - - - CORP TRUST BOUNDARY
       v
( Admin Backend )
       |
       +--> Authorization layer (RBAC engine)
       |
       v
( Production API svc ) --> ===== User DB =====
       |
       v
( Audit Logger ) --> ===== Audit DB ===== --> Datadog SIEM

( Admin Backend ) --> ( Refund Service ) --> Stripe
( Admin Backend ) --> ( Feature Flag svc ) --> LaunchDarkly
```

Trust boundaries:
1. Internet to Cloudflare Access (TB1)
2. CF Access to Okta (TB2)
3. CF Access to admin backend (TB3, IAP boundary)
4. Admin backend to RBAC engine (TB4, authorization)
5. Admin backend to prod API (TB5, blast-radius boundary)
6. Admin backend to refund service (TB6)
7. Admin backend to feature flag service (TB7)
8. Audit logger to SIEM (TB8, evidence boundary)

## STRIDE matrix

| # | Boundary | STRIDE | Threat | L | I | Risk |
|---|----------|--------|--------|---|---|------|
| 1 | TB1 | S | Phished admin credentials, attacker logs in | H | H | H |
| 2 | TB1 | S | OIDC token theft via session fixation | M | H | H |
| 3 | TB2 | E | MFA fatigue / push bombing bypasses MFA | H | H | H |
| 4 | TB3 | T | CF Access misconfigured, app-level auth not enforced as fallback | L | H | M |
| 5 | TB4 | E | Privilege escalation: junior admin assumes senior role via UI flaw | M | H | H |
| 6 | TB4 | E | RBAC checked client-side only, attacker bypasses by hitting API directly | M | H | H |
| 7 | TB5 | I | Mass user export feature, no rate limit, used to scrape PII | M | H | H |
| 8 | TB5 | E | IDOR on admin endpoints (`/users/{id}/delete` not authorized per-record) | L | H | M |
| 9 | TB6 | E | Refund-amount cap not enforced, admin issues 100k refund | M | H | H |
| 10 | TB6 | R | Refund issued without ticket reference, untraceable to a request | H | M | H |
| 11 | TB7 | E | Feature flag toggles a payment-disabling kill switch unintentionally | M | H | H |
| 12 | TB8 | T | Admin can read or modify audit log they wrote | L | H | M |
| 13 | TB1 | I | Admin laptop infostealer steals session cookie | M | H | H |
| 14 | TB3 | R | No request-id in admin logs, cannot trace cross-service action | M | M | M |
| 15 | TB5 | I | UI shows full PII when only last-4 needed for the task | H | M | H |
| 16 | TB4 | R | Break-glass admin role used routinely, no expiry | M | H | H |

## Top 10

1. (#1) Phished credentials
2. (#3) MFA fatigue
3. (#5) Privilege escalation in RBAC
4. (#6) Server-side authorization missing
5. (#7) Mass export scrape
6. (#9) Refund cap missing
7. (#13) Cookie theft via infostealer
8. (#11) Feature flag blast radius
9. (#15) PII over-exposure in UI
10. (#16) Break-glass abuse

## Mitigations

| # | Primary | Compensating | Cost |
|---|---------|--------------|------|
| 1 | Phishing-resistant MFA (FIDO2/WebAuthn), no SMS, no TOTP for admin | Conditional access: admin tool reachable only from MDM-attested devices | M |
| 2 | Number-matching MFA, push only with code typing, max 3 push prompts then lockout | Datadog alert on rapid-fire push events | L |
| 3 | RBAC enforced server-side on every endpoint, deny-by-default, decision logged with policy version | OPA / open-source RBAC engine, policy as code in git | M |
| 4 | Per-role action limits: refund cap by role, mass-export gated behind dual approval | Just-in-time elevation via PAM (Teleport) for risky actions | H |
| 5 | UI shows minimum data per task (last-4, masked email), full reveal requires reason field | Reveal logged with reason, sampled for QA | M |
| 6 | Feature flag changes require change management, two-person rule on production toggles | Canary rollout, automatic rollback on error budget burn | M |
| 7 | Append-only audit log, separate write principal, admin cannot read or modify | Logs shipped to immutable Datadog archive | M |
| 8 | Session bound to device fingerprint plus client cert, short token TTL (8 hours) | Idle timeout 30 min, re-auth on sensitive actions | L |
| 9 | Break-glass role has 4-hour TTL, requires ticket, alerts security team on grant | Quarterly review of break-glass usage | L |
| 10 | Mass-export gated behind security team approval, all exports tagged in DLP | Per-admin daily export quota | M |

## Residual risk

After mitigations: 0 HIGH, 5 MEDIUM, 11 LOW.

MEDIUMs:
- Cloudflare Access misconfiguration: accepted because layered with app-level RBAC.
- IDOR on admin endpoints: accepted because covered by server-side per-record authz; the residual is policy bugs.
- Audit log integrity: accepted with append-only plus separate writer principal.
- Cookie theft via infostealer: accepted because device-bound sessions plus short TTL plus EDR.
- Break-glass role abuse: accepted with TTL plus alert plus quarterly review.

I would not ship without: phishing-resistant MFA and server-side RBAC. Those are the foundation.

## Detections

- Anomalous admin login: geo-velocity, new ASN, off-hours, alert immediately.
- MFA push spam: rate of push events per user above 3 in 1 minute = alert.
- Mass export: any export above 1000 records triggers a Slack message to security and the user's manager.
- Refund anomaly: alert on refund > 10x rolling 30-day median per agent.
- Break-glass usage: page security on every grant, audit weekly.
- Audit log tampering: integrity monitor that compares Datadog archive to live log on a 5 min loop.

Closing line:
"Internal admin tools are where insider threat lives. The threat surface widens because admins have legitimate authority over production. The compensating controls are phishing-resistant MFA, server-side RBAC, mass-action gates, and an immutable audit trail. Residual risk is bounded by the principle that no single admin should be able to cause irreversible harm in under 60 seconds without a second pair of eyes."
