# Drill 05: Payment Processing Flow

## Prompt
"Threat model a Stripe-style payment flow on a marketplace. Cardholders enter card details on our site, we tokenize via the processor, charge happens server-side, webhooks update order status. Refunds and chargebacks supported. PCI scope must stay narrow."

This drill matches the Amex AppSec interview prep.

## Scope (Phase 1)

Assets:
- Card data (PAN, CVV, expiry) - never stored, but in scope during transit
- Payment tokens (Stripe-style)
- Order records and order totals
- Webhook signing secrets
- Stripe API keys
- Customer billing PII

Actors:
- Cardholder (legitimate customer)
- Adversary attempting card testing or BIN attacks
- Marketplace seller (could be malicious)
- Internal customer support (refund authority)
- Payment processor (Stripe)
- Acquiring bank, card networks (downstream)

Data classes:
- PAN/CVV (highest, PCI-DSS in scope)
- Tokens (high)
- Order metadata (medium)
- Refund records (high, fraud-relevant)

Assumptions:
- Stripe Elements or equivalent client-side tokenization
- Server never sees raw PAN
- We are SAQ-A or SAQ-A-EP merchant
- Webhook endpoint is on our domain
- Internal CS tool for refunds is SSO-protected

## DFD

```
                                    INTERNET BOUNDARY
[ Cardholder ] -- HTTPS --> ( Browser: Stripe Elements iframe )
        |                        |
        |                        | tokenize
        |                        v
        |                  ( Stripe JS / Stripe API ) --> ===== Stripe Vault =====
        |                        |                       |  PAN, CVV stored      |
        |                        | token returns         ========================
        |                        v
        |                  [ Browser ]
        |                        |
        | submit form (token, order)
        v
( Our Site Frontend )
        |
        v
  ( Order API ) ----- create order, attach token --> ===== Order DB =====
        |
        | charge(token, amount)
        v
- - - - - - - - - - - - - - - - - - - - - - - - - - - - INTERNET BOUNDARY
( Stripe API )
        |
        | charge result
        v
( Order API ) ----- update order, charge_id --> ===== Order DB =====

[ Stripe ] -- HTTPS webhook --> ( /webhook/stripe ) --> ( Order API ) -> Order DB

[ CS Agent ] --SSO--> ( Internal Refund Tool ) --> ( Refund API ) --> ( Stripe API )
                                                                              |
                                                                              v
                                                                       ( Order DB )
```

Trust boundaries:
1. Cardholder browser to Stripe Elements (TB1, isolated iframe)
2. Browser to our Order API (TB2, internet)
3. Our backend to Stripe API (TB3, server-to-server)
4. Stripe webhook to our endpoint (TB4)
5. CS agent SSO to internal tool (TB5, internal trust)
6. Refund API to Stripe (TB6)
7. Order DB at rest (TB7)
8. Internal egress to Stripe (TB8, network)

## STRIDE matrix

| # | Boundary | STRIDE | Threat | L | I | Risk |
|---|----------|--------|--------|---|---|------|
| 1 | TB1 | T | Compromised JS on parent page reads card data via DOM injection | M | H | H |
| 2 | TB1 | T | Magecart-style supply chain attack on third-party script broadens iframe escape | M | H | H |
| 3 | TB2 | T | Order tampering: client submits token plus modified amount | H | H | H |
| 4 | TB3 | I | Stripe API key in env var leaks via log or env dump | M | H | H |
| 5 | TB3 | E | API key has live mode and full account scope, no restricted key | M | H | H |
| 6 | TB4 | S | Forged webhook with no signature validation | H | H | H |
| 7 | TB4 | R | Webhook replayed, order marked paid twice | M | H | H |
| 8 | TB4 | T | Webhook out-of-order delivery, refund processed before charge | M | M | M |
| 9 | TB2 | E | Card testing: thousands of tokens against our charge endpoint | H | M | H |
| 10 | TB5 | E | CS agent over-privileged, can refund without limit | M | H | H |
| 11 | TB5 | R | Refund issued, no who-did-it audit trail | M | H | H |
| 12 | TB6 | S | Refund API called by compromised internal service, no per-actor authn | L | H | M |
| 13 | TB7 | I | Order DB stolen, includes billing addresses and PII | L | H | M |
| 14 | TB2 | I | Receipt page leaks token via referer | L | M | L |
| 15 | TB8 | D | Stripe outage, our charge path 500s, do we lose orders | M | M | M |
| 16 | TB2 | T | Currency manipulation: client submits amount in different currency | L | H | M |

## Top 10

1. (#3) Order tampering on amount
2. (#6) Forged webhook
3. (#7) Webhook replay double-credit
4. (#9) Card testing / BIN attacks
5. (#10) CS over-privileged refunds
6. (#11) Missing refund audit
7. (#1) DOM injection on parent page
8. (#5) Over-scoped Stripe API key
9. (#4) API key leak
10. (#2) Magecart on third-party script

## Mitigations

| # | Primary | Compensating | Cost |
|---|---------|--------------|------|
| 1 | Server-side computed amount, never trust client-submitted total. Token + server-side cart -> server-side amount | Reconcile order total to cart hash on every charge | L |
| 2 | Verify `Stripe-Signature` header on every webhook with raw body and shared secret, reject unsigned | Quarantine unsigned, alert | L |
| 3 | Idempotency on charge and refund using `event_id` from webhook, conditional update in DB | Webhook event log table with TTL, dedup | L |
| 4 | Restricted API keys: scope to charges and webhooks only, separate keys for refunds and reads | Stripe radar for fraud, key rotation 90 days | M |
| 5 | Per-IP and per-card-fingerprint rate limit on charge attempts, plus Stripe Radar | Captcha on retry, anomaly alert | M |
| 6 | RBAC on internal CS tool: refund limits per role (1 dollar / 100 dollars / unlimited). All refunds require reason | Refunds above threshold require second approver | L |
| 7 | Audit log for every refund: who, when, why, customer, amount, before/after | SIEM correlation with chargeback rate | L |
| 8 | CSP with strict source allowlist, SRI on every script tag, Stripe Elements iframe isolation | Out-of-band integrity monitor (Tinfoil-style) on script hashes | M |
| 9 | DB-at-rest encryption with KMS, column-level encryption on PII fields | Backup encryption verified | L |
| 10 | Webhook ordering: state machine in DB rejects refund-before-charge, queues until charge present | DLQ for out-of-order events | L |

## Residual risk

After mitigations: 0 HIGH, 5 MEDIUM, 11 LOW.

MEDIUMs:
- Magecart class supply chain: accepted because zero perfect defense, mitigation is SRI, CSP, and integrity monitoring.
- CS over-privileged refunds: accepted with role-based limits and dual control above threshold.
- Stripe outage: accepted with retry queue and graceful degradation, customer sees clear error.
- Refund API service-to-service: accepted because internal-only with mTLS plus SSO chain of custody.
- Currency manipulation: accepted because server computes amount, never trusts client.

I would not ship without: webhook signature verification and idempotency. Those are the table stakes for payments.

## Detections

- Order amount mismatch: alert on any case where client-submitted total != server-computed total.
- Unsigned webhooks: any signature failure pages on-call.
- Card testing: spike detection on charge failures by BIN, alert on more than 100 declines per minute from same source.
- Refund anomalies: alert if any agent refunds more than 10x their daily average.
- API key leak: GitHub secret scanning, plus monitor for charges from unknown IPs.
- Magecart drift: nightly hash check on every loaded script versus baseline, alert on diff.

Closing line:
"Payments boil down to two questions: do you trust the amount, and do you trust the event. Order tampering and webhook forgery are the bread and butter. Server-side computation of amount and signature verification on webhooks are the controls you must never skip. The residual risk is bounded by your refund authorization model. That is where insider threats live and that is where I would put the most monitoring."
