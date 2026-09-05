# Dynamic Application Security Testing Methodology

**Organization:** Organization Security Operations Platform
**Assessment Date:** 2026-03-22
**Assessor:** System Owner
**Methodology:** OWASP Testing Guide v4.2, OWASP ZAP Scanning Methodology
**NIST 800-53 Controls:** RA-5, SA-11, SA-11(8), CA-8
**Classification:** Internal Use Only
**Version:** 1.1

---

## Document Control

| Field | Value |
|-------|-------|
| Document ID | DAST-001 |
| Version | 1.2 |
| Status | Active |
| Last Revised | 2026-06-24 |
| Next Review | 2026-09-22 |
| Author | Information Security Officer |
| Approver | System Owner |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-03-20 | Information Security Officer | Initial methodology and assessment plan |
| 1.1 | 2026-03-22 | Information Security Officer | Added baseline assessment results (OWASP ZAP 2.17.0 scan) |
| 1.2 | 2026-06-24 | Information Security Officer | Audit refresh: `ollama` removed from valid orchestrator actions list (action no longer wired, container still runs). Network segmentation prose reconciled with the 4-row table (three Compose networks plus default Docker bridge). Section 13.2 Q3 row collapsed to a single consistent statement. Companion authenticated ZAP scan called out in Appendix C header. |

---

## 1. Purpose

This document defines the Dynamic Application Security Testing (DAST) methodology for the Organization Security Operations Platform. DAST complements the existing static analysis (SAST), secrets detection, and IaC scanning documented in `SECURE_SDLC.md` by testing running applications from an external attacker's perspective.

Where SAST tools like Semgrep and Checkov analyze source code and configuration files at rest, DAST sends crafted HTTP requests to live endpoints and observes responses for evidence of vulnerabilities. This catches issues that static analysis cannot detect: runtime misconfigurations, server-side header omissions, authentication bypass flaws, and injection vulnerabilities that only manifest when the application processes real input.

This methodology satisfies NIST 800-53 controls for vulnerability monitoring (RA-5), developer security testing including dynamic analysis (SA-11, SA-11(8)), and penetration testing (CA-8).

---

## 2. Scope Definition

### 2.1 Architectural Context

The Organization's platform has zero directly exposed ports to the public internet. All external traffic routes through a Cloudflare Tunnel (svc-tunnel), which terminates TLS at Cloudflare's edge and proxies authenticated requests to internal services. This architecture dramatically reduces the external attack surface.

**Public endpoints (in scope for external DAST):**

| Endpoint | Service | Protocol | Authentication |
|----------|---------|----------|---------------|
| `https://[automation-subdomain].example-ops.com` | svc-automation (n8n web interface) | HTTPS (Cloudflare-terminated TLS) | Email/password login, session cookie |
| `https://[automation-subdomain].example-ops.com/webhook/master-cmd` | Master Orchestrator webhook | HTTPS POST | Cloudflare WAF and Access (service token); application-level header validation in progress |
| `https://[automation-subdomain].example-ops.com/webhook/gmail-read-*` | Gmail reader webhooks (4 endpoints) | HTTPS POST | Cloudflare WAF |
| `ssh://[ssh-subdomain].example-ops.com` | SSH access (Cloudflare-proxied) | SSH over Cloudflare | SSH key authentication |

**Internal-only services (out of scope for external DAST, candidates for internal DAST):**

| Service | Port | Network | Reason for Exclusion |
|---------|------|---------|---------------------|
| svc-db (PostgreSQL) | 5432 | net-core | No HTTP interface, not externally reachable |
| svc-llm (Ollama) | internal | net-ai | Internal API only, no external route |
| svc-transcription (Whisper) | internal | net-ai | Internal API only, no external route |
| svc-secrets (HashiCorp Vault) | internal | net-core | Internal only, not tunneled |
| svc-identity (Keycloak) | internal | net-core | Internal only, not tunneled |
| svc-ai-gateway (OpenClaw) | internal | bridge (default) | Internal only, Telegram-facing |
| svc-detection (Falco) | N/A | net-monitoring | Kernel-level, no HTTP interface |
| svc-monitor (Datadog Agent) | N/A | net-monitoring | Metrics collector, no HTTP interface |

### 2.2 In-Scope Targets

| Target | Type | Priority | Justification |
|--------|------|----------|--------------|
| n8n web interface | Web application | High | Primary external-facing application with authentication |
| Master Orchestrator webhook (`/webhook/master-cmd`) | REST API | High | Accepts JSON payloads with action routing to 16 backend services |
| Gmail reader webhooks (4 endpoints) | REST API | Medium | Accept inbound webhook calls |
| n8n API health check endpoint | REST API | Low | Read-only status endpoint |

### 2.3 Out of Scope

| Target | Reason |
|--------|--------|
| Cloudflare edge infrastructure | Shared responsibility model; Cloudflare manages their own security testing |
| Cloudflare WAF rules | Managed service; Organization configures rules but does not test Cloudflare's WAF implementation |
| Internal-only services (net-ai, net-monitoring) | Not reachable from external DAST scanner position; covered by container scanning and Falco runtime detection |
| Telegram bot interfaces (2 bots) | Third-party platform; Telegram's API security is their responsibility |
| SSH endpoint | Not an HTTP service; covered by SSH key management controls in `POLICY_ACCESS_CONTROL.md` |

---

## 3. Methodology

This DAST assessment follows the OWASP Testing Guide v4.2, adapted for the Organization's tunnel-based architecture. The assessment proceeds in five phases.

### 3.1 Phase Overview

| Phase | Activity | Duration | Output |
|-------|----------|----------|--------|
| **1. Reconnaissance** | Passive enumeration of endpoints, response headers, technology fingerprinting | 1 hour | Target inventory, technology profile |
| **2. Configuration** | Configure ZAP scan policies, authentication, scope exclusions, rate limits | 1 hour | ZAP session file with scan policy |
| **3. Active Scanning** | Automated crawl and active scan of in-scope targets | 2-4 hours | Raw scan results |
| **4. Manual Verification** | Triage findings, confirm true positives, eliminate false positives | 2 hours | Verified finding list |
| **5. Reporting** | Document findings, assign severity, recommend remediation | 1 hour | DAST assessment report |

### 3.2 OWASP Testing Guide Mapping

| OWASP Phase | OWASP Reference | Organization Activity |
|-------------|-----------------|----------------------|
| Information Gathering | OTG-INFO-001 through OTG-INFO-010 | Technology fingerprinting via response headers, error pages |
| Configuration Management | OTG-CONFIG-001 through OTG-CONFIG-008 | TLS configuration, HTTP method testing, security header audit |
| Identity Management | OTG-IDENT-001 through OTG-IDENT-005 | User enumeration via n8n login, role testing |
| Authentication | OTG-AUTHN-001 through OTG-AUTHN-010 | Credential transport, session fixation, brute force |
| Authorization | OTG-AUTHZ-001 through OTG-AUTHZ-004 | Path traversal, privilege escalation, IDOR |
| Session Management | OTG-SESS-001 through OTG-SESS-008 | Cookie attributes, session timeout, CSRF |
| Input Validation | OTG-INPVAL-001 through OTG-INPVAL-017 | XSS, SQL injection, command injection, parameter tampering |
| Error Handling | OTG-ERR-001 through OTG-ERR-004 | Error code analysis, stack trace disclosure |
| Cryptography | OTG-CRYPST-001 through OTG-CRYPST-004 | TLS version, cipher suites, certificate validation |

---

## 4. Tool Selection

### 4.1 Primary Tool: OWASP ZAP

OWASP ZAP (Zed Attack Proxy) is selected as the primary DAST tool for the following reasons:

| Criteria | ZAP Capability |
|----------|---------------|
| **Cost** | Open source, zero license cost |
| **CI/CD integration** | GitHub Action available (`zaproxy/action-*`), command-line mode for automation |
| **API scanning** | Native OpenAPI/Swagger import, JSON payload fuzzing |
| **Authenticated crawl** | Session management with cookie/header-based authentication |
| **Customizable scan policies** | Per-category enable/disable, severity thresholds, scan strength tuning |
| **Reporting** | HTML, JSON, XML, Markdown output formats |
| **Community** | Active development, regular rule updates, OWASP flagship project |

### 4.2 Supplementary Tools

| Tool | Purpose | When Used |
|------|---------|-----------|
| `curl` | Manual header inspection, endpoint enumeration | Reconnaissance phase |
| `testssl.sh` | TLS configuration audit | Configuration phase |
| `nikto` | Web server misconfiguration scanner | Configuration phase (supplementary) |
| Browser developer tools | Manual request inspection, cookie analysis | Verification phase |

---

## 5. Pre-Scan Configuration

### 5.1 Authentication Setup

The n8n web interface requires email/password authentication. ZAP must be configured to authenticate and maintain a valid session.

**Authentication method:** Form-based login

| Parameter | Value |
|-----------|-------|
| Login URL | `https://[automation-subdomain].example-ops.com/signin` |
| Login request method | POST |
| Username field | `emailOrLdapLoginId` (not `email`) |
| Password field | `password` |
| Session indicator | Presence of session cookie after successful login |
| Logged-in indicator | Response containing user dashboard elements |
| Logged-out indicator | Redirect to `/signin` |

**Session management:** ZAP's cookie-based session management will capture and replay the session cookie on all subsequent requests.

### 5.2 Scan Policy Configuration

| Category | Enabled | Scan Strength | Threshold | Justification |
|----------|---------|--------------|-----------|--------------|
| Injection (SQL, NoSQL, LDAP) | Yes | Medium | Medium | n8n uses PostgreSQL backend; test for SQL injection in webhook parameters |
| Cross-Site Scripting (XSS) | Yes | Medium | Medium | n8n renders user-provided workflow names and descriptions |
| Broken Authentication | Yes | High | Low | Critical area given single-user architecture |
| Security Misconfiguration | Yes | Medium | Low | Header analysis, error handling, default credentials |
| Sensitive Data Exposure | Yes | Medium | Medium | Check for credential leakage in responses and error messages |
| XML External Entities (XXE) | No | N/A | N/A | No XML processing endpoints identified |
| Server-Side Request Forgery | Yes | Medium | Medium | Webhook endpoints accept URLs and external references |
| Directory Browsing | Yes | Medium | Low | Check for exposed internal paths |

### 5.3 Scope Exclusions

The following paths are excluded from active scanning to prevent disruption:

| Excluded Path | Reason |
|---------------|--------|
| `*/logout*` | Scanning logout endpoints invalidates the session, breaking subsequent tests |
| `*/api/v1/workflows/*/activate` | Toggling workflow activation could disrupt production automation |
| `*/api/v1/workflows/*/delete` | Destructive operation |
| `*/api/v1/credentials/*` | Credential management endpoints, avoid accidental modification |
| `*/api/v1/executions/*/delete` | Destructive operation |
| `*/healthz` | Health check endpoint, low risk, high noise |

### 5.4 Rate Limiting

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Maximum concurrent requests | 2 | n8n is a single-instance application; higher concurrency risks self-DoS |
| Request delay | 500ms between requests | Prevent overwhelming the application and Cloudflare rate limits |
| Maximum scan duration | 4 hours | Prevent runaway scans; sufficient for the limited external surface |
| Alert threshold | 20 findings per category | Cap to prevent report flooding from repetitive findings |

---

## 6. Test Coverage Matrix

The following matrix maps OWASP Top 10 (2025) categories to specific ZAP test modules and expected finding types.

| OWASP Top 10 | ZAP Scanner Module | Expected Finding Type | Priority | Notes |
|-------------|-------------------|----------------------|----------|-------|
| **A01:2025 Broken Access Control** | Access Control Scanner, Path Traversal | IDOR on workflow IDs, unauthorized API access, directory traversal | High | Test with authenticated and unauthenticated sessions |
| **A02:2025 Security Misconfiguration** | SSL/TLS Scanner (passive) | Weak TLS versions, missing HSTS, insecure cookies | Medium | TLS terminated at Cloudflare; test from client perspective |
| **A05:2025 Injection** | SQL Injection, Command Injection, CRLF Injection | SQL injection in webhook JSON parameters, header injection | High | Focus on `/webhook/master-cmd` action and query parameters |
| **A04:2025 Cryptographic Failures** | Manual review | Business logic flaws in webhook routing | Medium | Verify action parameter validation in Master Orchestrator |
| **A02:2025 Security Misconfiguration** | Server Header Scanner, Cookie Scanner, CSP Scanner | Missing security headers, verbose error messages, default credentials | High | Check X-Frame-Options, CSP, X-Content-Type-Options, Referrer-Policy |
| **A06:2025 Insecure Design** | Technology Detection (passive) | Outdated server headers, exposed version strings | Low | Component versions tracked via SBOM in SECURE_SDLC.md |
| **A07:2025 Authentication Failures** | Authentication Scanner, Brute Force | Weak session management, session fixation, credential stuffing | High | n8n login is the primary authentication target |
| **A08:2025 Data Integrity Failures** | Deserialization Scanner | Insecure deserialization in webhook JSON processing | Medium | JSON payloads to webhook endpoints |
| **A09:2025 Security Logging and Alerting Failures** | Manual review | Insufficient logging of failed auth attempts | Low | Verify via Datadog/Falco correlation after scan |
| **A03:2025 Software Supply Chain Failures** | Dependency scanning (Trivy, SBOM) | Compromised dependencies, outdated base images, unsigned containers | High | Covered by CI/CD pipeline (Trivy, Cosign, Syft); DAST validates runtime behavior |
| **A10:2025 Mishandling of Exceptional Conditions** | Error handling scanner, stack trace detection | Verbose error pages, unhandled exceptions, failing open | Medium | Test with malformed payloads, oversized requests, unexpected content types |

---

## 7. Architectural Controls

The Organization's architecture provides several built-in controls that reduce DAST scope and mitigate entire vulnerability classes.

### 7.1 Cloudflare Tunnel

All external traffic passes through Cloudflare Tunnel (svc-tunnel). No ports are directly exposed on the host. This provides:

| Control | Effect on DAST |
|---------|---------------|
| **TLS termination** | All traffic is encrypted at Cloudflare's edge. DAST cannot test for plaintext communication from the internet. |
| **DDoS protection** | Cloudflare absorbs volumetric attacks. DAST rate limiting is advisory, not critical. |
| **WAF rules** | Cloudflare's managed WAF may block certain ZAP payloads. DAST findings must be validated with and without WAF to distinguish application-level vs. WAF-level protection. |
| **Bot management** | ZAP's user-agent may trigger Cloudflare bot challenges. Configure ZAP to use a standard browser user-agent. |
| **IP reputation** | The scanner's source IP must not be on Cloudflare's threat list. Use a known-clean IP. |

**Testing approach:** Run DAST scans twice. First, with Cloudflare WAF active (production-representative). Second, from a position inside the tunnel (if feasible) to test the application layer directly without WAF filtering.

### 7.2 Network Segmentation

The Docker Compose stack uses three segmented application networks (net-core, net-ai, net-monitoring) plus the default Docker bridge for the one standalone container that lives outside Compose:

| Network | Services | DAST Relevance |
|---------|----------|---------------|
| net-core | svc-automation, svc-db, svc-secrets, svc-identity, svc-tunnel | Only svc-automation is reachable via tunnel. DAST scope limited to n8n web UI and webhooks. |
| net-ai | svc-llm, svc-transcription | Completely isolated from external traffic. No DAST targets. |
| bridge (default) | svc-ai-gateway | Standalone container on default Docker bridge. Telegram-facing only, no tunnel route. |
| net-monitoring | svc-detection, svc-monitor, svc-log-router | Monitoring plane. No external exposure. |

This segmentation means that even if a DAST scan discovers a vulnerability in svc-automation, lateral movement to AI inference or monitoring services requires escaping the container network boundary.

### 7.3 Reduced Attack Surface

| Traditional DAST Target | Organization Status | Implication |
|------------------------|-------------------|-------------|
| Multiple public-facing web applications | 1 web application (n8n) | Focused, thorough scan rather than broad surface coverage |
| Database ports exposed | Zero database ports exposed | No direct database testing from DAST position |
| Admin panels on public IPs | Admin panel behind Cloudflare Tunnel | DAST must authenticate through Cloudflare |
| Multiple API gateways | Webhook endpoints routed through n8n | Single entry point for API testing |

---

## 8. Authentication and Session Testing

### 8.1 n8n Session Management Tests

| Test | OWASP Reference | Method | Expected Result |
|------|----------------|--------|-----------------|
| Session cookie attributes | OTG-SESS-002 | Inspect Set-Cookie headers | HttpOnly, Secure, SameSite=Strict/Lax flags present |
| Session timeout | OTG-SESS-007 | Idle session for 30+ minutes, attempt reuse | Session should expire within configurable timeout |
| Session fixation | OTG-SESS-003 | Capture session ID pre-login, verify change post-login | Session ID must change after authentication |
| Concurrent sessions | OTG-SESS-008 | Login from two browsers simultaneously | Verify session isolation |
| Logout invalidation | OTG-SESS-006 | Capture session cookie, logout, replay cookie | Server must reject the replayed session |
| CSRF protection | OTG-SESS-005 | Submit state-changing request without CSRF token | Request must be rejected |

### 8.2 Credential Testing

| Test | Method | Expected Result |
|------|--------|-----------------|
| Credentials over HTTPS | Verify login form submits to HTTPS endpoint | No plaintext credential transmission |
| Login error messages | Submit invalid username, then invalid password | Generic error message (no user enumeration) |
| Account lockout | Submit 10+ failed login attempts | Account lockout or rate limiting after threshold |
| Password in URL | Check for credentials in URL parameters or Referer header | No credentials in URLs |
| Autocomplete on login form | Inspect form attributes | `autocomplete="off"` on password field recommended |

### 8.3 JWT and API Token Testing

If n8n uses JWT tokens for API authentication:

| Test | Method | Expected Result |
|------|--------|-----------------|
| JWT algorithm confusion | Modify JWT header to `alg: none` | Server must reject unsigned tokens |
| JWT expiration | Use expired token | Server must reject expired tokens |
| JWT signature verification | Modify JWT payload without re-signing | Server must reject tampered tokens |
| API key in response | Inspect all responses for exposed API keys | No API keys returned in responses |

---

## 9. API Security Testing

### 9.1 Master Orchestrator Webhook

The Master Orchestrator webhook (`/webhook/master-cmd`) is the highest-priority API target. It accepts JSON payloads with an `action` parameter that routes to 15 backend services.

**Valid actions:** `postgres`, `telegram`, `github`, `drive`, `tasks`, `sheets`, `docs`, `slides`, `gumroad`, `cloudflare`, `notion`, `tavily`, `gmail`, `workspace_admin`, `excel`

> Note: the `ollama` action was removed from the orchestrator. The ollama container still runs on the host; the action route is no longer wired into n8n.

**Test cases:**

| Test | Payload | Expected Result |
|------|---------|-----------------|
| Invalid action parameter | `{"action": "invalid_action"}` | Graceful error response, no stack trace |
| Missing action parameter | `{}` | Validation error, no backend processing |
| SQL injection in query parameter | `{"action": "postgres", "query": "'; DROP TABLE users; --"}` | Query must be sanitized or rejected |
| Command injection in text parameter | `{"action": "telegram", "text": "test; cat /etc/passwd"}` | Text treated as literal string, no command execution |
| SSRF via URL parameter | `{"action": "tavily", "query": "http://169.254.169.254/latest/meta-data/"}` | Internal metadata endpoint must not be reachable |
| Oversized payload | 10MB JSON body | Request must be rejected with appropriate size limit |
| Unexpected content type | `Content-Type: text/xml` with XML body | Must reject non-JSON content types |
| Null bytes in parameters | `{"action": "telegram\u0000admin", "text": "test"}` | Null bytes must be stripped or rejected |
| Path traversal in parameters | `{"action": "docs", "path": "../../etc/passwd"}` | Path traversal must be blocked |

### 9.2 Gmail Reader Webhooks

The four Gmail reader webhooks accept inbound calls:

| Endpoint | Test Focus |
|----------|-----------|
| `/webhook/gmail-read-main` | Input validation, authentication requirements |
| `/webhook/gmail-read` | Same payload format, test for inconsistent validation |
| `/webhook/gmail-read-personal` | Same payload format |
| `/webhook/gmail-read-business` | Same payload format |

**Test cases for each endpoint:**

- Verify that the endpoint requires proper caller authentication or validation
- Test with malformed JSON payloads
- Test with oversized payloads
- Test response headers for information disclosure

### 9.3 Response Header Analysis

All webhook responses will be analyzed for security headers:

| Header | Expected Value | Risk if Missing |
|--------|---------------|-----------------|
| `X-Content-Type-Options` | `nosniff` | MIME type confusion attacks |
| `X-Frame-Options` | `DENY` or `SAMEORIGIN` | Clickjacking |
| `Content-Security-Policy` | Restrictive policy | XSS, data injection |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | TLS downgrade (may be set by Cloudflare) |
| `Referrer-Policy` | `strict-origin-when-cross-origin` or `no-referrer` | Information leakage via Referer header |
| `X-Powered-By` | Absent | Technology fingerprinting |
| `Server` | Absent or generic | Server software fingerprinting |
| `Cache-Control` | `no-store` on authenticated pages | Cached sensitive data |

---

## 10. False Positive Management

### 10.1 Triage Process

Every DAST finding goes through a three-step triage:

| Step | Action | Outcome |
|------|--------|---------|
| **1. Automated dedup** | ZAP groups findings by CWE and URL pattern | Consolidated finding list |
| **2. Manual verification** | Replay the request manually using `curl` or browser | Confirmed true positive, or reclassified as false positive |
| **3. Context assessment** | Evaluate whether Cloudflare WAF, network segmentation, or other controls mitigate the finding | Risk-adjusted severity |

### 10.2 Common False Positives for This Architecture

| ZAP Finding | Why It May Be False Positive | Verification Method |
|-------------|------------------------------|-------------------|
| Missing HSTS header | Cloudflare may add HSTS at the edge, not visible in the application response | Check response from Cloudflare edge vs. direct application |
| CSP header missing | n8n may not set CSP natively; Cloudflare can add it via transform rules | Verify whether CSP is present in the final client-received response |
| Cookie without Secure flag | If ZAP tests through HTTP (which it cannot, since tunnel enforces HTTPS), this is a false positive | Confirm all traffic flows through HTTPS tunnel |
| Information disclosure via error page | Generic n8n error pages may trigger ZAP's information disclosure scanner without containing sensitive data | Review actual error page content |
| SQL injection in webhook | n8n's workflow engine may not pass user input directly to SQL; the `postgres` action is processed by a workflow node | Trace the data flow from webhook input to database query in the n8n workflow |

### 10.3 Suppression Rules

Verified false positives are suppressed to prevent recurrence in future scans:

| Suppression Method | When to Use |
|-------------------|-------------|
| ZAP alert filter (context-level) | False positive specific to this application |
| ZAP scan policy exclusion | Entire test category not applicable (e.g., XXE for JSON-only API) |
| Finding-level `WONTFIX` tag | Accepted risk with documented justification |

Suppressed findings must be documented in the DAST report with the suppression rationale. Suppressions are reviewed at each quarterly DAST cycle.

---

## 11. Reporting Template

Each confirmed finding is documented using the following format:

### Finding Template

```
### [DAST-YYYY-NNN] [Finding Title]

**URL:** https://[automation-subdomain].example-ops.com/[path]
**Parameter:** [affected parameter name]
**Method:** [GET/POST/PUT/DELETE]
**CWE:** [CWE-XXX: CWE Name]
**CVSS 3.1:** [score] ([vector string])
**OWASP Top 10:** [A01-A10 category]
**ZAP Alert ID:** [ZAP internal alert ID]
**Confidence:** [High/Medium/Low]

**Evidence:**
[HTTP request and response excerpts demonstrating the vulnerability]

**Impact:**
[Description of what an attacker could achieve by exploiting this finding]

**Remediation:**
[Specific steps to fix the vulnerability]

**Compensating Controls:**
[Existing controls that reduce the exploitability or impact]

**Priority:** [Critical/High/Medium/Low/Informational]
**Status:** [Open/In Remediation/Resolved/Accepted Risk]
**POA&M Reference:** [POAM entry ID if applicable]
```

### Report Structure

The full DAST assessment report follows this structure:

1. Executive Summary (findings count by severity, overall risk posture)
2. Scope and Methodology (targets, tools, scan configuration)
3. Findings (ordered by severity, using the template above)
4. False Positive Log (suppressed findings with rationale)
5. Recommendations (prioritized remediation roadmap)
6. Appendix: Raw ZAP report (attached as HTML artifact)

---

## 12. Integration with Secure SDLC

DAST findings feed back into the CI/CD pipeline and GRC documentation through the following integration points:

### 12.1 Finding-to-Pipeline Flow

```
DAST Scan
    │
    ├── Critical/High findings
    │   ├── Create GitHub Issue (tagged: security, dast)
    │   ├── Add to POAM_PLAN_OF_ACTION.md
    │   └── SLA: Critical 48h, High 7 days (per POLICY_VULNERABILITY_MANAGEMENT.md)
    │
    ├── Medium findings
    │   ├── Create GitHub Issue (tagged: security, dast)
    │   ├── Add to POAM if not resolved in 30 days
    │   └── SLA: 30 days
    │
    ├── Low/Informational findings
    │   ├── Document in DAST report
    │   └── Address in next maintenance cycle
    │
    └── False positives
        ├── Add to ZAP suppression rules
        └── Document in DAST report false positive log
```

### 12.2 SDLC Phase Placement

DAST occupies the Testing and Monitoring phases of the Secure SDLC defined in `SECURE_SDLC.md`:

| SDLC Phase | Static Testing (Existing) | Dynamic Testing (This Document) |
|-----------|--------------------------|-------------------------------|
| Testing (PR) | Checkov, TFLint, `terraform validate` | N/A (DAST runs against deployed application) |
| Testing (Merge) | Gitleaks, Trivy, Semgrep | N/A (DAST runs post-deployment) |
| Deployment | Cosign, SBOM | N/A |
| Post-Deployment | Falco (runtime) | DAST quarterly scan against production |

### 12.3 CI/CD Integration (Shipped 2026-05-25)

DAST is integrated into the CI/CD pipeline via .github/workflows/dast-zap.yml (shipped 2026-05-25). The approach is:

1. Deploy a staging environment with the latest merge
2. Run ZAP baseline scan (passive + light active) against staging
3. Fail the pipeline if any HIGH or CRITICAL findings are detected
4. Upload ZAP report as a GitHub Actions artifact
5. Post summary to the merge PR as a comment

This follows the same pattern as the existing Trivy SARIF upload and Conftest PR comment.

---

## 13. Schedule

### 13.1 DAST Assessment Cadence

| Assessment Type | Frequency | Scope | Duration |
|----------------|-----------|-------|----------|
| Full DAST assessment | Quarterly | All in-scope targets, authenticated and unauthenticated | 8 hours |
| Targeted rescan | After major application changes | Changed endpoints only | 2 hours |
| Regression scan | After critical finding remediation | Specific finding verification | 30 minutes |

### 13.2 Quarterly Schedule Alignment

DAST assessments align with the existing quarterly review cadence. CI/CD DAST integration shipped on 2026-05-25 (see Section 12.3); the Q3 row below reflects the completed go-live plus the scheduled Q3 full retest.

| Q2 2026 | Q3 2026 | Q4 2026 | Q1 2027 |
|---------|---------|---------|---------|
| Initial DAST assessment (baseline) | Full retest plus AI adversarial testing (per `AI_RED_TEAM_PLAN.md`); CI/CD DAST integration shipped 2026-05-25, retest validates the gate. | DAST plus annual remediation review | DAST plus annual SDLC review |

### 13.3 Assessment Prerequisites

Before each quarterly DAST assessment:

1. Verify svc-automation is running and accessible through the tunnel
2. Confirm scan credentials are valid (n8n login)
3. Review scope for new endpoints added since last assessment
4. Update ZAP to the latest stable version
5. Review and update suppression rules for previously accepted false positives
6. Notify System Owner of the scan window to avoid confusion with monitoring alerts
7. Verify Cloudflare WAF is not configured to block the scanner's source IP

---

## 14. Cross-References

| Document | Relationship |
|----------|-------------|
| [SECURE_SDLC.md](SECURE_SDLC.md) | Defines the CI/CD pipeline this DAST methodology complements; Section 12.2 describes planned CI/CD DAST integration |
| [POLICY_VULNERABILITY_MANAGEMENT.md](POLICY_VULNERABILITY_MANAGEMENT.md) | Defines severity classifications, remediation SLAs, and exception processes for DAST findings |
| [THREAT_MODEL_STRIDE.md](THREAT_MODEL_STRIDE.md) | Identifies threats at trust boundaries TB-1 and TB-2 that DAST validates |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | Receives Critical/High DAST findings as new POA&M entries |
| [CIS_RISK_REGISTER.md](CIS_RISK_REGISTER.md) | Documents accepted risks that may appear as DAST findings (e.g., break-glass SSH) |
| [AI_RED_TEAM_PLAN.md](AI_RED_TEAM_PLAN.md) | Quarterly AI adversarial testing schedule aligns with DAST cadence |
| [DATA_FLOW_DIAGRAM.md](DATA_FLOW_DIAGRAM.md) | DFD trust boundaries inform DAST scope decisions |
| [POLICY_INCIDENT_RESPONSE.md](POLICY_INCIDENT_RESPONSE.md) | Incident response procedures if DAST discovers an actively exploited vulnerability |

---

## Appendix A: ZAP Configuration Checklist

Use this checklist before each DAST assessment to ensure consistent configuration.

- [ ] ZAP updated to latest stable release
- [ ] Scan policy loaded with Organization-specific settings (Section 5.2)
- [ ] Authentication configured with correct login URL and field names (Section 5.1)
- [ ] Session management validated (logged-in/logged-out indicators working)
- [ ] Scope exclusions applied (Section 5.3)
- [ ] Rate limiting configured (Section 5.4)
- [ ] Suppression rules from previous assessment imported
- [ ] Scanner source IP whitelisted in Cloudflare WAF (if applicable)
- [ ] User-agent set to standard browser string (avoid bot detection)
- [ ] Notification sent to System Owner with scan window

## Appendix B: Webhook Payload Samples for API Testing

### Master Orchestrator, Valid Request

```json
{
  "action": "postgres",
  "query": "SELECT NOW()"
}
```

### Master Orchestrator, Injection Test

```json
{
  "action": "postgres",
  "query": "SELECT * FROM users WHERE id = '1' OR '1'='1'"
}
```

### Master Orchestrator, SSRF Test

```json
{
  "action": "tavily",
  "query": "http://10.100.1.10:5432/",
  "depth": "basic"
}
```

### Master Orchestrator, Action Fuzzing

```json
{
  "action": "../../../etc/passwd",
  "query": "test"
}
```

### Gmail Webhook, Malformed Payload

```json
{
  "invalid_key": "no expected fields",
  "nested": {"deep": {"object": "test"}}
}
```

---

## Appendix C: Baseline Assessment Results (2026-03-22)

### Assessment Summary

| Field | Value |
|-------|-------|
| Assessment Date | 2026-03-22 |
| Tool | OWASP ZAP 2.17.0 (daemon mode) |
| Java Runtime | OpenJDK 17.0.18 (Homebrew) |
| Scanner Position | External (Mac workstation through public internet) |
| Target | `https://[automation-subdomain].example-ops.com` |
| Authentication | Unauthenticated (pre-login surface only). A companion authenticated ZAP scan was also captured on 2026-03-22 as `zap-report-n8n-auth-20260322.html`. <!-- TODO(et): add an Appendix D covering the authenticated-scan results, or reference where those results live. --> |
| Scan Type | Spider + Passive + Active (full scan policy) |
| Spider Results | 161 URLs discovered |
| Scan Duration | Approximately 8 minutes (spider: 12s, passive: 60s, active: ~7 min) |

### Results Overview

| Severity | Count | Category |
|----------|-------|----------|
| Critical | 0 | - |
| High | 0 | - |
| Medium | 4 | Security header misconfigurations |
| Low | 536 | Missing hardening headers on static assets <!-- TODO(et): the 536 Low count exceeds the Section 5.4 "alert threshold 20 findings per category" cap by 26x. Either the per-category threshold was disabled for the baseline, or the count is correctly consolidated across many categories. Verify against the raw zap-report-n8n-20260322.html and add a one-line note explaining which is the case. --> |
| Informational | 193 | Cache directives, technology detection |

**No injection vulnerabilities detected.** ZAP tested SQL injection, Cross-Site Scripting (XSS), command injection, path traversal, LDAP injection, CRLF injection, and Server-Side Request Forgery (SSRF) against all discovered endpoints. All attack payloads were either rejected or had no observable effect.

### Findings

#### DAST-2026-001: Missing Anti-Clickjacking Header

| Field | Value |
|-------|-------|
| URL | `https://[automation-subdomain].example-ops.com/` |
| CWE | CWE-1021: Improper Restriction of Rendered UI Layers |
| OWASP Top 10 | A02:2025 Security Misconfiguration |
| Confidence | Medium |
| Severity | Medium |

**Evidence:** The response from the application root does not include an `X-Frame-Options` header or a `Content-Security-Policy` header with a `frame-ancestors` directive. This allows the login page to be embedded in an iframe on a malicious site, enabling clickjacking attacks.

**Impact:** An attacker could overlay the n8n login form within a transparent iframe on a phishing page, tricking users into entering credentials on what appears to be a different site.

**Remediation:** Configure the web server or reverse proxy to add `X-Frame-Options: DENY` or set CSP `frame-ancestors 'none'` on all HTML responses. This can be implemented through Cloudflare Transform Rules or n8n's environment configuration.

**Compensating Controls:** Cloudflare Tunnel limits access. The application is not indexed by search engines. Single-user architecture reduces the attack surface for credential-harvesting clickjacking.

**Status:** Remediated
**Priority:** Medium

---

#### DAST-2026-002: Content Security Policy Not Set

| Field | Value |
|-------|-------|
| URL | `https://[automation-subdomain].example-ops.com/` |
| CWE | CWE-693: Protection Mechanism Failure |
| OWASP Top 10 | A02:2025 Security Misconfiguration |
| Confidence | High |
| Severity | Medium |

**Evidence:** The main application page does not return a `Content-Security-Policy` header. Without CSP, the browser has no instructions to restrict which scripts, styles, and resources can be loaded.

**Impact:** If an attacker discovers a stored XSS vulnerability in n8n (none found in this scan), the absence of CSP would allow arbitrary script execution without browser-level restrictions.

**Remediation:** Deploy a Content-Security-Policy header. Start with a report-only policy (`Content-Security-Policy-Report-Only`) to identify legitimate resource sources, then enforce. Recommended minimum: `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none';`

**Compensating Controls:** No XSS vulnerabilities were detected in the active scan. n8n's Vue.js framework provides built-in XSS escaping for rendered content.

**Status:** Remediated
**Priority:** Medium

---

#### DAST-2026-003: CSP Directive Missing Fallback

| Field | Value |
|-------|-------|
| URL | `https://[automation-subdomain].example-ops.com/sitemap.xml` |
| Parameter | `content-security-policy` |
| CWE | CWE-693: Protection Mechanism Failure |
| OWASP Top 10 | A02:2025 Security Misconfiguration |
| Confidence | High |
| Severity | Medium |

**Evidence:** The `sitemap.xml` response includes a CSP header with `default-src 'none'` but omits several directives that do not fall back to `default-src` (e.g., `base-uri`, `form-action`, `frame-ancestors`). These directives default to allowing everything when not explicitly set, regardless of the `default-src` value.

**Impact:** An attacker who discovers an injection point could potentially manipulate the `<base>` tag, submit forms to external domains, or embed the page in iframes, since these specific directives are not restricted.

**Remediation:** Add explicit values for directives without fallback: `base-uri 'self'; form-action 'self'; frame-ancestors 'none';`

**Status:** Remediated
**Priority:** Medium

---

#### DAST-2026-004: Private IP Address Disclosure

| Field | Value |
|-------|-------|
| URL | `https://[automation-subdomain].example-ops.com/` (JavaScript bundle) |
| CWE | CWE-497: Exposure of Sensitive System Information |
| OWASP Top 10 | A01:2025 Broken Access Control |
| Confidence | Medium |
| Severity | Low |

**Evidence:** The string `192.168.1.1` was found in a JavaScript response body. This appears to be a default/example IP address within an n8n workflow node or configuration template, not the actual infrastructure IP.

**Impact:** Minimal. The IP `192.168.1.1` is a common default gateway address and does not reveal the Organization's internal network topology. This is likely a false positive from a bundled n8n node that references common network addresses as examples.

**Triage Decision:** False positive. The IP is a generic example address embedded in n8n's application code, not a reflection of the Organization's infrastructure.

**Status:** Accepted (false positive)
**Priority:** Informational

---

#### DAST-2026-005: HSTS Header Not Set

| Field | Value |
|-------|-------|
| URLs Affected | 65 |
| CWE | CWE-319: Cleartext Transmission of Sensitive Information |
| OWASP Top 10 | A02:2025 Security Misconfiguration |
| Confidence | High |
| Severity | Low |

**Evidence:** Responses from the application do not include the `Strict-Transport-Security` header. HSTS instructs browsers to only connect via HTTPS, preventing TLS downgrade attacks.

**Impact:** Without HSTS, a user's first request could theoretically be intercepted before the HTTPS redirect occurs (SSL stripping). However, the Cloudflare Tunnel architecture eliminates direct HTTP access entirely.

**Remediation:** Add `Strict-Transport-Security: max-age=31536000; includeSubDomains` to all responses. This can be implemented via Cloudflare response header transform rules at the edge.

**Compensating Controls:** Cloudflare Tunnel enforces HTTPS at the edge. No HTTP listener exists on the origin server. Direct IP access is blocked.

**Status:** Remediated
**Priority:** Low

---

#### DAST-2026-006: X-Content-Type-Options Header Missing

| Field | Value |
|-------|-------|
| URLs Affected | 64 |
| CWE | CWE-693: Protection Mechanism Failure |
| OWASP Top 10 | A02:2025 Security Misconfiguration |
| Confidence | Medium |
| Severity | Low |

**Evidence:** Responses for static assets (JavaScript, CSS) do not include the `X-Content-Type-Options: nosniff` header. This header prevents browsers from MIME-sniffing the response content type.

**Impact:** In older browsers, an attacker could potentially serve malicious content that the browser interprets differently than the declared Content-Type. Modern browsers have significantly reduced this risk.

**Remediation:** Add `X-Content-Type-Options: nosniff` to all responses. This is a single Cloudflare transform rule.

**Status:** Remediated
**Priority:** Low

---

### Negative Findings (Tests Passed)

The following vulnerability classes were actively tested and no findings were detected:

| Test Category | ZAP Module | Payloads Tested | Result |
|--------------|------------|-----------------|--------|
| SQL Injection | SQL Injection Scanner | Union-based, blind, time-based | No injection points found |
| Cross-Site Scripting | XSS (Reflected, Persistent) | Script injection, event handlers | No reflection or storage of payloads |
| Command Injection | OS Command Injection | Shell metacharacters, pipe injection | No command execution |
| Path Traversal | Path Traversal Scanner | `../`, encoded traversal sequences | No directory access |
| Remote File Inclusion | Remote File Inclusion Scanner | External URL references | No file inclusion |
| CRLF Injection | CRLF Injection Scanner | Header injection via `%0d%0a` | No header injection |
| Server-Side Request Forgery | SSRF Scanner | Internal IP references, cloud metadata URLs | No SSRF detected |
| XML External Entity (XXE) | XXE Scanner | External entity declarations | No XXE processing |

### Remediation Priority

| Priority | Finding ID | Action | Owner | Status |
|----------|-----------|--------|-------|-------------|
| 1 | DAST-2026-001, 002, 003 | Add CSP and X-Frame-Options via Cloudflare Transform Rules | System Owner | Remediated 2026-03-22 |
| 2 | DAST-2026-005 | Add HSTS header via Cloudflare | System Owner | Remediated 2026-03-22 |
| 3 | DAST-2026-006 | Add X-Content-Type-Options via Cloudflare | System Owner | Remediated 2026-03-22 |

All three remediation items can be resolved in a single Cloudflare configuration change by adding response header transform rules. Estimated effort: 15 minutes.

### Next Steps

1. Implement Cloudflare response header transform rules for findings DAST-2026-001 through 006
2. Run regression scan after header changes to verify remediation
3. Configure authenticated DAST scan (n8n login) to test post-authentication attack surface
4. Schedule Q2 2026 full DAST assessment per Section 13.2

## Appendix D: OWASP Top 10 Coverage Summary

| OWASP Category | Covered by DAST | Covered by SAST | Covered by Other |
|----------------|----------------|-----------------|-----------------|
| A01:2025 Broken Access Control | Yes (ZAP, includes SSRF) | Partial (Semgrep) | Falco runtime detection, network segmentation |
| A02:2025 Security Misconfiguration | Yes (ZAP passive + TLS scan) | Yes (Checkov) | CIS Docker Bench, Cloudflare headers |
| A03:2025 Software Supply Chain Failures | No | Yes (Trivy, Cosign, Syft) | SBOM generation, image signing |
| A04:2025 Cryptographic Failures | Partial (manual) | No | Threat model (STRIDE) |
| A05:2025 Injection | Yes (ZAP active scan) | Yes (Semgrep) | OPA policy validation |
| A06:2025 Insecure Design | Partial (fingerprinting) | Yes (Trivy) | SBOM, Cosign |
| A07:2025 Authentication Failures | Yes (ZAP auth scan) | No | n8n session management |
| A08:2025 Data Integrity Failures | Partial (deserialization) | Yes (Semgrep) | Cosign image verification |
| A09:2025 Security Logging and Alerting Failures | No | No | Falco, Datadog, Fluentd |
| A10:2025 Mishandling of Exceptional Conditions | Partial (error handling) | Partial (Semgrep) | n8n workflow error handler |
