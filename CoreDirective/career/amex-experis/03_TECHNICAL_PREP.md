# Amex AppSec — Technical Prep

Focus areas specific to Amex: payment flow threat modeling, OWASP Top 10 + PCI DSS v4.0 crossover, OAuth/JWT pitfalls, DevSecOps pipeline patterns, third-party breach scenarios.

For broader AppSec acronym coverage, also see `/Users/et/cyber-squire-ops/CoreDirective/career/onedigital/03_TECHNICAL_PREP.md` Part 1 (acronym glossary covers all the SAST/DAST/SCA/Entra/NIST material).

---

## Part 1 — Payment Flow Threat Modeling (Amex will ask this)

**Expect a question like:** *"Walk me through threat modeling a card-not-present payment flow using STRIDE."*

### The Card-Not-Present Payment Flow (reference architecture)

1. Cardholder enters card details on merchant checkout page
2. Merchant's payment gateway tokenizes card number (or sends to card network directly)
3. Token + transaction details sent to Amex network over HTTPS with mTLS
4. Amex performs authorization: fraud screening, risk scoring, 3DS (3-D Secure) authentication if enabled, credit check, balance/limit check
5. Approved / declined response returned to merchant
6. Merchant completes transaction
7. Settlement occurs separately on a batch cycle (T+1 typically)

### STRIDE Applied

| STRIDE Category | Threat | Mitigation |
|----------------|--------|------------|
| **Spoofing** | Attacker impersonates merchant | mTLS certificate pinning, merchant identity verification via signed contracts, per-merchant API keys rotated quarterly |
| **Tampering** | Attacker modifies transaction amount in transit | HTTPS + certificate pinning, HMAC-signed request bodies, idempotency keys preventing replay-as-different-amount |
| **Repudiation** | Merchant claims transaction wasn't theirs | Immutable audit log (write-once to object storage with hash chain), signed merchant attestation at transaction origination, dispute resolution procedure |
| **Information Disclosure** | Cardholder PAN leaked in logs | PCI DSS 3.3 (do not display full PAN), tokenization before logging, structured logging with scrubbing, logs encrypted at rest, access to logs audited |
| **Denial of Service** | Payment endpoint overwhelmed | Rate limiting per merchant + per cardholder, WAF (Akamai/Cloudflare), DDoS protection, graceful degradation with circuit breakers |
| **Elevation of Privilege** | Attacker exploits vulnerability to access other cardholders' data | Least privilege in microservices (GKE Workload Identity, Istio mTLS for service-to-service), strict tenant isolation, regular pen-testing of the authorization service |

**Add PCI DSS v4.0 context if asked:**
- Requirement 3: Protect stored account data (tokenization mandatory for PAN storage)
- Requirement 4: Protect cardholder data with strong cryptography during transmission
- Requirement 6: Develop + maintain secure systems (shift-left AppSec, SAST, DAST, change control)
- Requirement 11: Test security of systems regularly (quarterly ASV scans, pen-testing)
- Requirement 12: Maintain an information security policy + awareness program

---

## Part 2 — OWASP Top 10 (2021 version, with PCI overlap)

| OWASP | Category | PCI DSS Crossover |
|-------|----------|---------------------|
| A01 | Broken Access Control | Req 7 (Restrict access to need-to-know) |
| A02 | Cryptographic Failures | Req 3, 4 (stored + in-transit crypto) |
| A03 | Injection | Req 6.5 (SQLi, command injection) |
| A04 | Insecure Design | Req 6.1-6.3 (secure SDLC) |
| A05 | Security Misconfiguration | Req 2 (secure configurations) |
| A06 | Vulnerable Components | Req 6.2 (patch management + SCA) |
| A07 | Identification + Auth Failures | Req 8 (MFA, strong auth) |
| A08 | Software + Data Integrity Failures | Req 6.7 (software integrity — SBOM, code signing) |
| A09 | Security Logging + Monitoring Failures | Req 10 (audit trails) |
| A10 | Server-Side Request Forgery (SSRF) | Req 6.5.12 (specific to 4.0) |

**For Amex specifically:** know that OWASP A08 (Software + Data Integrity) is the lens for the 2024 third-party merchant processor breach. SBOM, SCA, code signing, vendor SDLC attestation are the controls.

---

## Part 3 — OAuth 2.0 / OIDC / JWT Pitfalls

Expected interview area — banking APIs are OAuth-heavy.

### OAuth 2.0 common vulnerabilities
- **Insufficient scope validation:** tokens granted too broad access (over-privileged clients)
- **Token leak via logging:** OAuth bearer tokens in app logs, URLs, error pages
- **Token misbinding:** tokens usable by any client if not bound to client_id + audience
- **PKCE missing:** mobile/SPA apps not using PKCE are vulnerable to authorization code interception
- **Refresh token rotation absent:** long-lived refresh tokens stolen = indefinite access

### OIDC specifics
- **id_token validation failures:** signature not verified, issuer + audience not checked, expiry not enforced
- **Nonce replay:** authentication response replayed; nonce verification prevents

### JWT pitfalls
- **alg:none:** attacker strips signature and sets alg to "none"
- **kid confusion:** kid header controlled by attacker, points to attacker-chosen key
- **HMAC vs RSA confusion:** if the server allows both, an RSA public key can be used as an HMAC secret to forge tokens
- **Missing expiry / iat validation:** tokens reused indefinitely
- **Scope escalation through payload modification** (only possible if signature validation is broken)

### Mitigations (your reference answer)
- JWKS endpoint for public key rotation
- Strict alg whitelisting (RS256, ES256 — never HS256 + none)
- Audience (aud) + issuer (iss) validation mandatory
- Short token lifetimes (15 min access tokens, 24 hr refresh with rotation)
- Token binding to client and optionally to DPoP (demonstrating proof of possession)
- Request signing (HMAC on full request body)

---

## Part 4 — DevSecOps Pipeline (your strongest territory — use as anchor)

### The canonical shift-left pipeline you own at CoreDirective

```
Developer PR
   ↓
GitHub Actions triggered
   ↓
[Trivy] container + IaC scan (SAST/SCA)
   ↓
[Semgrep] custom-rule SAST
   ↓
[Gitleaks] secrets detection
   ↓
[OPA policy gates] infrastructure + deployment compliance
   ↓
If pass: merge allowed
If fail: block + surface findings inline to PR
   ↓
Post-merge:
[Cosign] sign container image
[Syft] generate SBOM
[OWASP ZAP] scheduled DAST against prod SOAR
[Falco] runtime detection in prod
```

### What this looks like at Amex scale (speak to this)

"At Amex scale, the shift-left pipeline would be structurally similar but tool-substituted. Snyk Code + Snyk Container replace Semgrep + Trivy. GitHub Advanced Security (GHAS) likely layered for enterprise SAST + dependency review. SBOM probably via Anchore or Snyk depending on vendor state. Signing via Sigstore / Cosign in the Sigstore public infrastructure. Runtime via CrowdStrike Falcon. DAST via Burp Enterprise or an internal scanning platform. The discipline is constant across the stack."

---

## Part 5 — Third-Party Breach Response (ready if Amex asks)

See `01_COMPANY_INTEL.md` Section 6 for the 2024 incident context.

**If asked: "Walk me through how you'd handle a third-party breach announcement affecting Amex cardholder data."**

**Answer frame (90 sec):**

"Hour zero: establish the facts. Who got breached, what data, what's our exposure. Pull our vendor agreement to confirm contractual breach notification timing — typically 72 hours after the vendor becomes aware. Engage the vendor's incident response team directly. For a merchant processor breach specifically, we'd request their forensic report and the list of affected cardholder data we had shared with them.

Day one to three: internal escalation. CISO (Reznik) + legal + privacy + external comms. Regulatory coordination — OCC supervisor notification since we're regulated bank. State AG notifications start mapping: Massachusetts, California, New York, Maryland have specific breach notification timelines; some as short as 30 days post-confirmation. Begin the customer notification plan.

Week one: remediation. Rotate any API keys shared with the vendor. Temporarily disable the integration if the vendor hasn't confirmed remediation. Reassess the vendor relationship — audit rights exercised, SOC 2 Type 2 report re-reviewed, additional compensating controls imposed or relationship terminated. For Amex specifically, the payment processor ecosystem means terminating a vendor is rarely feasible in short order — so compensating controls are the primary play.

Month one: fraud mitigation. Credit monitoring for affected cardholders (Amex's standard playbook). Enhanced fraud scoring on cards with potentially-exposed data. Regulatory reporting under FFIEC guidance. Public disclosure if required by SEC materiality threshold.

Throughout: documented decision trail. Every action logged in the IR record. Evidence preserved for OCC examiner review and potential regulatory action. Post-incident retrospective with lessons integrated into vendor risk policy updates."

---

## Part 6 — Likely Amex-Specific Technical Questions

### Q1: "What's the difference between Amex's closed-loop model and Visa/Mastercard's open-loop from a security perspective?"

**Answer (60 sec):** "Closed-loop means Amex is both the card network and the issuer for most Amex cards — we see the full transaction lifecycle internally. Security-wise: tighter data control, because fewer parties handle cardholder data end-to-end; richer fraud signals, because the same entity sees merchant, issuer, and cardholder telemetry; and a more consolidated regulatory stance, since Amex is prudentially supervised by OCC via AENB. The flipside is that a breach in Amex's own systems is not buffered by a separate issuing bank — we're the primary custodian."

### Q2: "What's your threat model for a Go microservice in a GKE + Istio environment?"

**Answer (75 sec):** "I'd start with the trust boundaries. Service-to-service traffic should be authenticated with mTLS through Istio's service mesh — that's mandatory for anything handling regulated data. External ingress through a gateway with rate limiting + WAF + auth enforcement.

Application-level: Go makes memory safety easier than C/C++, but doesn't solve logic bugs. OWASP Top 10 still applies — injection in SQL queries through database/sql or GORM, SSRF through HTTP client libraries, auth bypasses in custom middleware. I'd enforce structured logging with scrubbing on PII before anything hits a log aggregator.

Dependency risk: Go's module system is good but not foolproof. Supply chain attacks via typosquatting or compromised maintainers. SCA on go.mod + go.sum with Snyk or Trivy. SBOM on build output.

Runtime: Falco (or CrowdStrike Falcon AIDR at Amex scale) for runtime anomaly detection. Detect anomalous syscalls, unexpected process spawns, suspicious file access patterns.

Identity: Workload Identity in GKE instead of static service account keys. Secrets from a secret manager (Google Secret Manager, HashiCorp Vault), never baked into the image or env vars logged in manifests."

### Q3: "How do you handle secret rotation at scale?"

**Answer (60 sec):** "Three layers. One, never let a secret be static. Every API key, every cert, every token has a rotation schedule. At CoreDirective, I automated credential rotation in the n8n SOAR — rotation triggers, validation of rotation success, rollback if the new credential fails. Two, separation of secret management from code. Secrets live in a vault (HashiCorp Vault or cloud-native secret managers), code retrieves them at runtime via short-lived credentials. Three, audit trail on every access. Who read the secret, when, which service, what for. That audit trail is the evidence an OCC examiner wants to see."

### Q4: "Explain how you'd investigate a SAST finding that developers argue is a false positive."

**Answer (60 sec):** "Five-step method. One, reproduce the finding locally — is it a real pattern in the code or a scanner artifact? Two, if real, assess reachability — is the vulnerable code path actually reachable in production? Taint-tracking analysis helps. Three, if reachable, assess exploitability — is it authenticated-only, is input validated upstream, are there mitigating controls? Four, document the analysis — either confirm remediation is needed (with severity + owner + ETA) or mark it as a false positive with the reasoning trail preserved for audit. Five, if it's a false positive, tune the scanner rule to avoid the same flag next time. Never just dismiss findings — every dismissal is a documented decision."

### Q5: "What's your experience with CI/CD security gates — and what happens when a build fails a gate?"

**Answer (75 sec):** "At CoreDirective every PR goes through the full gate set: Trivy for containers + IaC, Semgrep for custom SAST rules, Gitleaks for secrets, OPA for deployment compliance. Failures block merge. A blocked build is surfaced inline to the developer in the PR — they see the specific finding, the file, the line, the rule, and a suggested fix when the tool supports it.

The gate doesn't punish developers for the finding — it gives them the information to fix it. If a developer believes a finding is wrong, the dispute path is: engage security review, document the reasoning, get a CISO-approved exception with an expiry date. Exceptions can't persist forever; they're defensible decisions with owners.

The failure mode I watch for: gates that produce so much noise that developers tune them out. Falco tuning is a direct parallel — 200 alerts a day meant developers ignored all 200. When I moved it to 12 actionable, engagement returned. The same principle applies to CI/CD gates. Signal-to-noise is the leadership decision."

---

## Part 7 — Your Resume Metrics (be ready to defend)

Every number in your submitted Amex resume may be probed. Brief backstory for each:

| Metric | Backstory (30 sec ready) |
|--------|-----------------------|
| 80%+ SOAR triage reduction | n8n orchestrator, NeMo-sandboxed workloads, Ollama local, Claude API; measured Jan-Mar 2026 at CoreDirective |
| 200 events/day → 12 actionable | Falco eBPF rule tuning + Falcosidekick routing to Datadog; 15 working days of daily tuning cycles |
| Zero exposed ports | Cloudflare Zero Trust tunnels + mTLS at CoreDirective; external port scan confirmed zero inbound |
| Zero injection vulns across 8 OWASP categories | Authenticated OWASP ZAP DAST against production SOAR; 4 header misconfigs found + remediated same-day via Cloudflare transform rules |
| 16 Terraform files + 30+ resources + 8 OPA policies | CoreDirective infra-as-code on DigitalOcean + Cloudflare |
| 37 GRC documents | NIST 800-53 Rev 5 SSP, POA&M tracking 37 findings, 10 policies, 5 IR playbooks, risk assessment, tabletop exercise |
| 48h → <4h MTTD | Texaco Splunk correlation rules across 3 retail locations |
| 8h → 90min IR containment | Texaco 6-step IR runbook + POS skimmer incident |
| 14 → 2 critical audit findings | Texaco AD Group Policy baselines + least-privilege admin + credential rotation |
| 45+ devices in PCI DSS scope | Texaco; quarterly Nessus scans + SAQ documentation |
| 12 hrs/week recovered | Texaco Python + PowerShell automation (patch deploy, user provisioning, reporting) |
| 3 retail locations | Texaco Atlanta operational scope |

If a metric doesn't have a clean backstory you can deliver in 30 seconds, re-read it from the resume file and commit the context.
