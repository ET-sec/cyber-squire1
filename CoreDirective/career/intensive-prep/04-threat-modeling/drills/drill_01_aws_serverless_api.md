# Drill 01: AWS Serverless API

## Prompt
"Threat model a public REST API built on API Gateway, Lambda, and DynamoDB. The API serves authenticated mobile and web clients. There are about 50 endpoints, mixed read and write, with one write path that triggers a payment via Stripe."

## Scope (Phase 1)

Assets:
- Customer PII in DynamoDB (name, email, phone, address)
- Payment events flowing to Stripe
- API request logs in CloudWatch
- Lambda execution role credentials

Actors:
- End users (mobile, web), authenticated via Cognito
- Internal admins via separate console
- External attackers (internet)
- Malicious or compromised customers
- Supply chain (Lambda layer publishers)

Data classes:
- PII (medium-high sensitivity)
- Payment metadata (high, regulated under PCI-DSS even though Stripe holds PAN)
- Auth tokens (high)
- Application logs (medium)

Assumptions:
- Single AWS account, single region
- WAF in front of API Gateway is in scope
- Stripe webhook back to a separate Lambda is in scope
- Mobile clients are not jailbreak-hardened

## DFD (Phase 2)

```
                                            INTERNET BOUNDARY
[ End User ] --HTTPS--> ( CloudFront ) --> ( WAF ) --> ( API Gateway )
   (mobile/web)                                              |
                                                             |  invoke
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - | - - - - -
                                                             v   AWS ACCOUNT BOUNDARY
                                                       ( Lambda fn )
                                                        /     |    \
                                                       /      |     \
                                              read/write    log    invoke
                                                  |          |       |
                                                  v          v       v
                                              =========   ======  ( Stripe API )
                                              | Dynamo|   |Cloud|
                                              | DB    |   |Watch|
                                              =========   ======
                                                                       
                                                                INTERNET BOUNDARY
[ Stripe ] --webhook HTTPS--> ( API Gateway: /webhooks/stripe ) --> ( Lambda webhook fn ) --> DynamoDB
```

Trust boundaries identified:
1. Internet to CloudFront (TB1)
2. WAF to API Gateway (TB2, edge-to-AWS)
3. API Gateway to Lambda (TB3, control to compute)
4. Lambda to DynamoDB (TB4, IAM-mediated)
5. Lambda to Stripe (TB5, egress to third party)
6. Stripe to webhook endpoint (TB6, inbound from third party)
7. Cognito to API (TB7, identity boundary)

## STRIDE matrix (Phase 3)

| # | Boundary | STRIDE | Threat | L | I | Risk |
|---|----------|--------|--------|---|---|------|
| 1 | TB1 | S | Stolen JWT replayed from another device | M | H | H |
| 2 | TB1 | S | Cognito session fixation | L | H | M |
| 3 | TB2 | T | WAF bypass via encoding tricks | M | M | M |
| 4 | TB2 | D | Volumetric DDoS exhausts API Gateway quota | M | H | H |
| 5 | TB3 | E | Authorizer Lambda misconfigured, allows anonymous | L | H | M |
| 6 | TB3 | I | Verbose Lambda error returns stack trace and env vars | M | H | H |
| 7 | TB4 | E | Over-broad `dynamodb:*` IAM grants table-wide access | M | H | H |
| 8 | TB4 | T | Application layer IDOR overwrites another user's row | H | H | H |
| 9 | TB4 | I | DynamoDB scan returns full table because no filter | M | M | M |
| 10 | TB5 | I | Stripe API key leaks via Lambda env var snapshot | L | H | M |
| 11 | TB5 | T | Outbound MITM rewrites payment amount | L | H | M |
| 12 | TB6 | S | Forged Stripe webhook with no signature check | H | H | H |
| 13 | TB6 | R | Webhook replay credits same payment twice | M | H | H |
| 14 | TB7 | E | Cognito user pool group escalation via attribute write | L | H | M |
| 15 | TB1 | R | No request-id propagation, cannot trace abuse | M | M | M |

## Top 10 threats prioritized

1. (#8) IDOR on write paths
2. (#12) Forged Stripe webhook
3. (#13) Webhook replay double-charge
4. (#1) Stolen JWT replay
5. (#7) Over-broad DynamoDB IAM
6. (#4) Volumetric DDoS
7. (#6) Verbose error disclosure
8. (#3) WAF bypass
9. (#9) Unbounded scan
10. (#5) Authorizer misconfig

## Mitigations (Phase 5)

| # | Primary control | Compensating control | Cost |
|---|-----------------|----------------------|------|
| 1 | Server-side authorization check on every record by user_id | CloudWatch metric on cross-user access patterns | M |
| 2 | Verify Stripe signature on every webhook with `stripe-signature` header and raw body | Reject unsigned, alert | L |
| 3 | Idempotency key on payment writes, DynamoDB conditional put | Webhook event_id dedup table with TTL | L |
| 4 | Short-lived JWT (15m), refresh-token rotation, device binding via Cognito | Anomaly detection on geo-velocity | M |
| 5 | Per-table IAM with item-level conditions where possible (LeadingKeys) | IAM Access Analyzer, monthly review | M |
| 6 | API Gateway throttling per-key plus AWS Shield Advanced | WAF rate-based rule, CloudWatch alarms | H |
| 7 | Generic error responses, structured exceptions, log full detail server-side only | Datadog error budget alert | L |
| 8 | WAF managed rules plus custom rule for known bypass patterns | Tarpit on repeated 403s | M |
| 9 | Use Query with key condition, never Scan in production paths | DynamoDB CloudWatch metric on Scan count | L |
| 10 | Cognito JWT signature pinning, audience claim validation | Failed auth metric per IP, alert | L |

## Residual risk (Phase 6)

After mitigations: 0 HIGH, 4 MEDIUM, 6 LOW.

The 4 MEDIUMs:
- WAF bypass: accepted because every WAF can be bypassed eventually, mitigation is detection on application errors plus monthly rule tuning.
- Cognito session fixation: accepted because Cognito session model has known limits, compensating control is short JWT TTL.
- Outbound MITM to Stripe: accepted because TLS plus certificate pinning at the AWS SDK layer is the industry standard.
- Stripe API key leak via env var: accepted because key rotation is in place every 90 days plus Secrets Manager versioning.

The HIGH that I would not accept ship: forged webhook without signature check. That is non-negotiable.

## Detections (Phase 7)

- IDOR: log every request with user_id and accessed resource_id. Datadog alert if accessed_id != user_id and authz check returned allow. Threshold: any.
- Webhook forgery: alert on signature verification failure rate above 0 over any 5-minute window. Page on-call.
- Payment double-charge: nightly job reconciles Stripe events table to internal payment table, page on mismatch.
- DynamoDB Scan in prod: CloudWatch metric, alert if Scan count > 0 on production tables.
- Lambda env var leak: GuardDuty IAM finding plus secret-in-CloudWatch-logs scanner.

Closing senior phrase to use:
"The threat surface widens because we have two third-party trust boundaries, Cognito on the inbound and Stripe on both directions. The residual risk is bounded by the fact that we treat both as untrusted and re-validate every signature. The compensating control for any IAM drift is Access Analyzer plus a monthly review with engineering managers signing off."
