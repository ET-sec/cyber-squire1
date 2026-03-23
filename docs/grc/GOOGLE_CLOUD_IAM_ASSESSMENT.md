# Google Cloud IAM Assessment

**Organization:** Organization Security Operations Platform
**Assessment Date:** 2026-03-22
**Assessor:** System Owner
**Methodology:** NIST SP 800-53 Rev. 5 (Security and Privacy Controls), Google Cloud IAM Best Practices
**NIST 800-53 Controls:** AC-2 (Account Management), AC-3 (Access Enforcement), AC-6 (Least Privilege), IA-2 (Identification and Authentication), IA-8 (Identification and Authentication of Non-Organizational Users)
**Classification:** Internal Use Only
**Version:** 1.0

---

## Document Control

| Field | Value |
|-------|-------|
| Document ID | IAM-GCP-001 |
| Version | 1.0 |
| Status | Approved |
| Last Revised | 2026-03-22 |
| Next Review | 2026-09-22 |
| Author | Information Security Officer |
| Approver | System Owner |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-03-22 | Information Security Officer | Initial release |

---

## 1. Purpose

### 1.1 Assessment Objective

This document assesses the Identity and Access Management configuration for the Organization's Google Cloud project and associated Google Workspace integration. The assessment was triggered by the configuration of Google Cloud IAM to support Workspace API access across multiple organizational contexts, including one Google Workspace domain account and three consumer Gmail accounts.

The assessment evaluates the security posture of:

- The Google Cloud IAM role assignment model
- OAuth 2.0 credential lifecycle and scope management
- Organization policy modifications required for multi-account access
- Compensating controls that mitigate risks introduced by policy relaxation

### 1.2 Framework Alignment

| NIST Control | Title | Relevance |
|--------------|-------|-----------|
| **AC-2** | Account Management | Google Cloud IAM principal management across organizational and consumer identities |
| **AC-3** | Access Enforcement | Role-based access control at organization and project levels |
| **AC-6** | Least Privilege | Service Usage Consumer role selection over broader alternatives |
| **AC-6(1)** | Authorize Access to Security Functions | Organization Policy Administrator assignment restricted to Workspace admin |
| **AC-6(2)** | Non-Privileged Access for Non-Security Functions | Consumer accounts limited to API quota consumption only |
| **IA-2** | Identification and Authentication | OAuth 2.0 authorization code flow with offline refresh |
| **IA-8** | Identification and Authentication (Non-Organizational Users) | Consumer Gmail accounts authenticated as non-organizational principals |

---

## 2. Scope

### 2.1 Systems Under Assessment

| Component | Description |
|-----------|-------------|
| **Google Cloud Organization** | Organization bound to example-ops.com Google Workspace domain |
| **Google Cloud Project** | org-automation-project, originally provisioned for svc-automation SOAR integrations |
| **Google Workspace Domain** | example-ops.com (single-user Workspace organization) |
| **Workspace APIs** | 7 APIs enabled: Gmail, Google Drive, Google Sheets, Google Docs, Google Calendar, Google Slides, Google Tasks |
| **OAuth 2.0 Client** | Web application type, configured for both svc-automation callback and desktop CLI authorization |
| **Authenticated Principals** | 4 accounts (1 Workspace + 3 consumer) |

### 2.2 Authenticated Account Inventory

| Account | Type | Domain | Purpose |
|---------|------|--------|---------|
| admin@example-ops.com | Google Workspace | example-ops.com | Primary administrative account, Workspace org owner |
| brand@consumer-mail.com | Consumer Gmail | gmail.com | Brand communications and public-facing workflows |
| personal@consumer-mail.com | Consumer Gmail | gmail.com | Personal correspondence |
| business@consumer-mail.com | Consumer Gmail | gmail.com | Business correspondence and vendor communications |

### 2.3 Out of Scope

- Google Cloud billing configuration and cost controls
- Google Workspace Admin Console settings beyond IAM policy constraints
- Third-party applications consuming Google APIs outside this project
- Physical security of Google data centers

---

## 3. IAM Architecture

### 3.1 Resource Hierarchy

```
Google Cloud Organization (example-ops.com)
│
│   Org-Level IAM Bindings:
│   ├── admin@example-ops.com → Organization Administrator
│   ├── admin@example-ops.com → Owner
│   └── admin@example-ops.com → Organization Policy Administrator
│
│   Org-Level Policies:
│   └── iam.allowedPolicyMemberDomains → Allow All (modified)
│
└── Project: org-automation-project
    │
    │   Project-Level IAM Bindings:
    │   ├── admin@example-ops.com → Owner (inherited + direct)
    │   ├── brand@consumer-mail.com → Service Usage Consumer
    │   ├── personal@consumer-mail.com → Service Usage Consumer
    │   └── business@consumer-mail.com → Service Usage Consumer
    │
    │   Enabled APIs (7):
    │   ├── Gmail API
    │   ├── Google Drive API
    │   ├── Google Sheets API
    │   ├── Google Docs API
    │   ├── Google Calendar API
    │   ├── Google Slides API
    │   └── Google Tasks API
    │
    └── OAuth 2.0 Client (Web Application)
        ├── Redirect URI: svc-automation callback
        └── Redirect URI: http://localhost (desktop CLI)
```

### 3.2 Role Inheritance Model

Google Cloud IAM follows a top-down inheritance model. Roles granted at the organization level automatically apply to all projects and resources beneath it. This assessment confirms that:

1. **Organization-level roles** are assigned exclusively to the Workspace admin account (admin@example-ops.com). No consumer accounts hold org-level roles.
2. **Project-level roles** are where consumer accounts receive their limited Service Usage Consumer binding.
3. **Inheritance is additive.** The Workspace admin inherits Owner at the project level through the org-level binding, plus holds a direct project-level Owner binding.

### 3.3 Organization Policy Cascade

Organization policies set at the org level apply to all descendant projects unless overridden. The `iam.allowedPolicyMemberDomains` constraint operates at the organization level and restricts which principals can be added to IAM policies throughout the hierarchy. Because consumer Gmail accounts do not belong to any Google Workspace customer ID, the constraint was modified to permit all domains. This modification cascades to org-automation-project and any future projects created under this organization.

---

## 4. Identity and Authentication

### 4.1 OAuth 2.0 Authorization Code Flow

All 4 accounts authenticate via the OAuth 2.0 authorization code flow configured for a web application client. The flow proceeds as follows for desktop CLI usage:

```
[1] CLI initiates authorization request
    → Browser opens Google consent screen
    → User authenticates with Google account credentials + MFA (if enabled)
          |
[2] User grants consent to requested scopes
    → Google issues authorization code
    → Redirect to http://localhost with code parameter
          |
[3] CLI exchanges authorization code for tokens
    → Access token (short-lived, ~1 hour)
    → Refresh token (long-lived, offline access)
          |
[4] CLI stores tokens in encrypted keyring
    → Subsequent API calls use access token
    → Access token refreshed automatically via refresh token
    → No re-authentication required for routine operations
```

The `access_type=offline` parameter ensures the refresh token is issued on first authorization, enabling unattended API operations without repeated interactive consent.

### 4.2 OAuth Scope Inventory

The OAuth 2.0 client requests 12 scopes. Each scope maps to a specific Workspace API and is bounded by the minimum permission level required for the Organization's operational workflows.

| Scope | API | Access Level | Justification |
|-------|-----|-------------|---------------|
| `gmail.modify` | Gmail API | Read + write + send (no delete) | Workflow-triggered email operations via svc-automation |
| `drive` | Google Drive API | Full file access | Document creation, template management, shared drive operations |
| `spreadsheets` | Google Sheets API | Full spreadsheet access | Automated reporting, tracker maintenance |
| `documents` | Google Docs API | Full document access | Document generation from workflow templates |
| `calendar` | Google Calendar API | Full calendar access | Event scheduling and availability management |
| `presentations` | Google Slides API | Full presentation access | Slide deck generation from workflow data |
| `tasks` | Google Tasks API | Full task access | Task creation and completion tracking |
| `userinfo.email` | OAuth 2.0 | Email address (read-only) | Account identification during token exchange |
| `userinfo.profile` | OAuth 2.0 | Profile info (read-only) | Display name resolution |
| `openid` | OpenID Connect | ID token | Identity verification during authentication |
| `cloud-platform` | Google Cloud | Project resource access | API enablement and quota consumption |
| `gmail.send` | Gmail API | Send-only | Outbound email automation (subset of gmail.modify) |

**Scope restriction note:** The `gmail.modify` scope was selected over `gmail.readonly` because svc-automation workflows require the ability to compose and send emails. The `mail.google.com` (full access) scope was intentionally excluded as it includes permanent deletion capabilities that exceed operational requirements.

### 4.3 Multi-Account Credential Isolation

Each authenticated account stores credentials in a separate configuration directory to prevent cross-contamination and enable per-account revocation.

```
~/.config/gws/
├── client_secret.json       (chmod 600, shared OAuth client config)
├── accounts/
│   ├── admin@example-ops.com/
│   │   └── token.json       (encrypted keyring reference)
│   ├── brand@consumer-mail.com/
│   │   └── token.json       (encrypted keyring reference)
│   ├── personal@consumer-mail.com/
│   │   └── token.json       (encrypted keyring reference)
│   └── business@consumer-mail.com/
│       └── token.json       (encrypted keyring reference)
```

This isolation ensures that revoking one account's refresh token does not affect the other three. File permissions are enforced at `chmod 600` for all credential files and `chmod 700` for all directories in the chain.

### 4.4 Token Lifecycle

| Token Type | Lifetime | Storage | Renewal |
|------------|----------|---------|---------|
| Access token | ~3600 seconds (1 hour) | In-memory during CLI session | Automatic via refresh token |
| Refresh token | No fixed expiry (revocable) | OS-level encrypted keyring | Re-authorization required if revoked or expired due to inactivity |
| ID token | ~3600 seconds (1 hour) | In-memory during CLI session | Issued alongside access token refresh |

Refresh tokens can be revoked through the Google Account security page, the Google Cloud Console, or programmatically via the `https://oauth2.googleapis.com/revoke` endpoint. Revocation is immediate and invalidates all access tokens derived from the refresh token.

---

## 5. Authorization Model

### 5.1 Role Assignment Matrix

| Account | Level | Role | Permissions Summary | Justification |
|---------|-------|------|---------------------|---------------|
| admin@example-ops.com | Organization | Organization Administrator | Full org-level resource and policy management | Workspace domain owner, sole administrator |
| admin@example-ops.com | Organization | Owner | All Google Cloud resources and billing | Required for project creation and API enablement |
| admin@example-ops.com | Organization | Organization Policy Administrator | Modify org-level constraints | Required to adjust `iam.allowedPolicyMemberDomains` for consumer account access |
| admin@example-ops.com | Project | Owner | Full project access (inherited from org) | Inherited binding, not directly assigned at project level |
| brand@consumer-mail.com | Project | Service Usage Consumer | Consume API quota only | Minimum role for OAuth token exchange and API calls through project quota |
| personal@consumer-mail.com | Project | Service Usage Consumer | Consume API quota only | Minimum role for OAuth token exchange and API calls through project quota |
| business@consumer-mail.com | Project | Service Usage Consumer | Consume API quota only | Minimum role for OAuth token exchange and API calls through project quota |

### 5.2 Least Privilege Analysis

The Service Usage Consumer role (`roles/serviceusage.serviceUsageConsumer`) grants exactly one permission: `serviceusage.services.use`. This permission allows the principal to make API calls that are billed to and quota-limited by the project. It does not grant:

| Capability | Granted? | Explanation |
|------------|----------|-------------|
| View or modify IAM policies | No | Requires `resourcemanager.projects.getIamPolicy` / `setIamPolicy` |
| Access billing or cost data | No | Requires `billing.accounts.get` or Billing Account Viewer role |
| Create, modify, or delete resources | No | Requires Editor or specific resource roles |
| View other users or their permissions | No | Requires `resourcemanager.projects.getIamPolicy` |
| Enable or disable APIs | No | Requires `serviceusage.services.enable` (Service Usage Admin) |
| Access Cloud Console dashboards | Limited | Can view project in Console but cannot see resources, logs, or IAM |
| View audit logs | No | Requires `logging.logEntries.list` (Logs Viewer role) |

This role was selected after evaluating and rejecting the following alternatives:

| Rejected Role | Reason for Rejection |
|---------------|---------------------|
| Viewer (`roles/viewer`) | Grants read access to all project resources, violating least privilege |
| Editor (`roles/editor`) | Grants read/write access to most resources, far exceeding requirements |
| Owner (`roles/owner`) | Full administrative control including IAM and billing, inappropriate for consumer accounts |
| Browser (`roles/browser`) | Grants `resourcemanager.projects.get` which is unnecessary for API consumption |

### 5.3 Effective Permission Boundary

Consumer accounts operate within a tightly bounded permission envelope. Their effective capabilities are:

1. Authenticate via OAuth 2.0 against the project's OAuth client
2. Make API calls (Gmail, Drive, Sheets, Docs, Calendar, Slides, Tasks) that consume project quota
3. Access only their own data within each Google service (Gmail reads their own inbox, Drive accesses their own files)

OAuth scopes provide an additional permission boundary beyond IAM roles. Even though Service Usage Consumer permits API consumption broadly, the scopes granted during OAuth consent restrict which APIs each account can actually call. An account cannot exceed the intersection of its IAM role permissions and its OAuth scope grants.

---

## 6. Organization Policy Governance

### 6.1 Constraint: `iam.allowedPolicyMemberDomains`

This organization policy constraint controls which domains can be added as principals to IAM policies throughout the organization hierarchy. It is a security guardrail designed to prevent accidental exposure of resources to external identities.

| Attribute | Value |
|-----------|-------|
| Constraint ID | `constraints/iam.allowedPolicyMemberDomains` |
| Enforcement Level | Organization |
| Cascades To | All projects and resources |
| Original State | Restricted to Workspace org domain only ([ORG-CUSTOMER-ID]) |
| Current State | Allow All |
| Modified Date | 2026-03-22 |
| Modified By | admin@example-ops.com (Organization Policy Administrator) |

### 6.2 Modification Rationale

The original policy restricted IAM principal domains to the Google Workspace customer ID [ORG-CUSTOMER-ID], which maps to the example-ops.com domain. This prevented any consumer Gmail account (which has no Workspace customer ID) from being added as an IAM principal at any level.

The constraint was modified to Allow All because:

1. **Consumer Gmail accounts have no customer ID.** Google Workspace customer IDs are issued only to Workspace organizations. Individual Gmail accounts cannot be added to the `allowedPolicyMemberDomains` list as individual entries.
2. **No intermediate option exists.** The constraint accepts customer IDs, not email domains. There is no way to allow `gmail.com` as a domain without allowing all Gmail accounts globally, which is functionally equivalent to Allow All for consumer account use cases.
3. **The Organization is single-user.** All four accounts (1 Workspace + 3 consumer) are personally owned and operated by the same individual (System Owner).

### 6.3 Risk Decision

**Decision: Accepted (MEDIUM risk)**

The policy modification introduces a theoretical risk: any Google identity could be added as an IAM principal within the organization. However, the following compensating controls reduce the residual risk to an acceptable level.

### 6.4 Compensating Controls

| Control | Description | NIST Mapping |
|---------|-------------|--------------|
| **IAM role restriction** | Consumer accounts receive only Service Usage Consumer. No role grants resource creation, deletion, or IAM modification. | AC-3, AC-6 |
| **Single administrator** | Only admin@example-ops.com holds Organization Administrator and Owner roles. No other principal can add IAM bindings. | AC-5, AC-6(1) |
| **No billing access** | Consumer accounts cannot view or modify billing. Even if an unauthorized principal were added, billing exposure is impossible without explicit Billing Account Viewer/Admin role. | AC-6(2) |
| **Audit logging** | Google Cloud Audit Logs record all IAM policy modifications. Admin Activity logs are always-on and cannot be disabled. Any addition of a new principal generates an auditable event. | AU-2, AU-3, AU-6 |
| **No public APIs** | The project exposes no public-facing services, Cloud Functions, or Cloud Run endpoints. API access requires OAuth authorization with a valid client ID and secret. | AC-3, SC-7 |
| **Quarterly review** | The policy modification will be re-evaluated quarterly. If consumer account access is no longer needed, the constraint will be restored to domain-restricted mode. | AC-2, CA-7 |

### 6.5 Recommendation

Re-restrict the `iam.allowedPolicyMemberDomains` policy after confirming 90 days of stable operation with the current configuration. If consumer account access remains a permanent requirement, document this as a permanent risk acceptance with annual re-evaluation. Monitor Google Cloud IAM for the introduction of per-email domain allowlisting, which would allow a more granular alternative.

---

## 7. API Security

### 7.1 Enabled API Inventory

| API | Service Name | Purpose | Quota Impact |
|-----|-------------|---------|-------------|
| Gmail API | gmail.googleapis.com | Read, compose, send, and label email across 4 accounts | 250 quota units/user/second |
| Google Drive API | drive.googleapis.com | File creation, upload, folder management, sharing | 20,000 queries/100 seconds |
| Google Sheets API | sheets.googleapis.com | Spreadsheet creation, cell reads/writes, formatting | 300 requests/minute/project |
| Google Docs API | docs.googleapis.com | Document creation and content manipulation | 300 requests/minute/project |
| Google Calendar API | calendar.googleapis.com | Event creation, scheduling, availability queries | 1,000,000 queries/day |
| Google Slides API | slides.googleapis.com | Presentation creation and slide manipulation | 300 requests/minute/project |
| Google Tasks API | tasks.googleapis.com | Task list and task CRUD operations | 50,000 queries/day |

### 7.2 Quota Management

All API calls from all 4 authenticated accounts consume quota from the single org-automation-project. Quota limits are enforced per-project by Google Cloud and cannot be exceeded without a quota increase request. This provides a natural rate-limiting boundary:

- No individual account can consume API quota beyond the project-level cap
- Automated workflows (svc-automation) and CLI usage share the same quota pool
- Quota exhaustion results in HTTP 429 responses, not data exposure

### 7.3 Scope Restriction Per Account

Although all 4 accounts are authorized with the same set of 12 OAuth scopes, each account's OAuth token is independently issued and independently revocable. Revoking consent for one account invalidates only that account's tokens. The shared scope set was chosen for operational simplicity given the single-operator context. If additional users are onboarded in the future, per-account scope restriction should be implemented.

---

## 8. Credential Storage and Protection

### 8.1 Credential Inventory

| Credential | Storage Location | Protection | Rotation Cadence |
|------------|-----------------|------------|------------------|
| OAuth client secret | `~/.config/gws/client_secret.json` | File permissions (chmod 600), not committed to source control | On compromise or annually |
| Refresh tokens (x4) | OS-level encrypted keyring | gws CLI default encryption, isolated per account | On compromise or when consent is revoked |
| Access tokens (x4) | In-memory only | Not persisted to disk, expire after ~1 hour | Automatic via refresh token |
| Client ID | `~/.config/gws/client_secret.json` | Not secret (public identifier), but file-protected alongside client secret | Same as client secret |

### 8.2 Source Control Exclusions

The following entries are present in `.gitignore` to prevent credential leakage:

- `client_secret*.json`
- `token*.json`
- `.config/gws/`
- `*.credentials`

### 8.3 File Permission Enforcement

```
~/.config/gws/                       drwx------  (700)
~/.config/gws/client_secret.json     -rw-------  (600)
~/.config/gws/accounts/              drwx------  (700)
~/.config/gws/accounts/*/            drwx------  (700)
~/.config/gws/accounts/*/token.json  -rw-------  (600)
```

These permissions restrict all credential files to the owning user. No group or world read access is permitted.

### 8.4 Credential Compromise Response

If a credential compromise is suspected:

1. **Revoke refresh tokens** for all affected accounts via `https://oauth2.googleapis.com/revoke` or the Google Account security page
2. **Rotate the OAuth client secret** in the Google Cloud Console, then update `client_secret.json` on all authorized machines
3. **Review Cloud Audit Logs** for unauthorized API calls during the exposure window
4. **Re-authenticate** all accounts to generate new refresh tokens
5. **File an incident** per PLAYBOOK_LEAKED_CREDENTIAL.md procedures

---

## 9. Monitoring and Audit

### 9.1 Google Cloud Audit Logs

Google Cloud generates three categories of audit logs relevant to this configuration:

| Log Type | Retention | Content | Can Be Disabled? |
|----------|-----------|---------|-----------------|
| Admin Activity | 400 days | IAM policy changes, API enablement, org policy modifications | No (always-on) |
| Data Access | 30 days (configurable) | API read/write operations against Google services | Yes (not currently enabled for all APIs) |
| System Event | 400 days | Google-initiated system events (maintenance, config changes) | No (always-on) |

**Recommendation:** Enable Data Access audit logs for Gmail API and Drive API to capture detailed API operation records. These are the two APIs with the highest sensitivity in this configuration.

### 9.2 Monitoring Checkpoints

| Checkpoint | Method | Frequency | Owner |
|------------|--------|-----------|-------|
| New IAM principal additions | Cloud Audit Logs (Admin Activity) | Continuous (log-based alert recommended) | System Owner |
| OAuth consent grants/revocations | Google Account activity log | Monthly manual review | System Owner |
| API quota consumption | Google Cloud Console, APIs & Services dashboard | Weekly | System Owner |
| Refresh token usage patterns | OAuth token refresh timestamps in API logs | Monthly | System Owner |
| Organization policy modifications | Cloud Audit Logs (Admin Activity) | Continuous (log-based alert recommended) | System Owner |

### 9.3 Recommended Alert Configuration

The following Cloud Monitoring alerting policies should be created to provide automated detection of security-relevant events:

1. **IAM Policy Change Alert:** Trigger on any `SetIamPolicy` audit log entry at the organization or project level
2. **New Principal Alert:** Trigger on `SetIamPolicy` where the delta includes a new `member` binding
3. **Organization Policy Change Alert:** Trigger on `SetOrgPolicy` or `DeleteOrgPolicy` audit log entries
4. **Unusual API Volume Alert:** Trigger when any single API exceeds 80% of its quota allocation within a 1-hour window

These alerts are not yet implemented. They are tracked as recommendations in Section 11.

---

## 10. Risk Assessment

### 10.1 Risk Summary

| Risk ID | Risk Description | Likelihood | Impact | Inherent Risk | Compensating Controls | Residual Risk |
|---------|-----------------|------------|--------|---------------|----------------------|---------------|
| GCP-R1 | Domain Restricted Sharing relaxation allows unauthorized principals | Low (2) | Moderate (3) | MEDIUM (6) | Single administrator, IAM role restriction, audit logging | LOW (3) |
| GCP-R2 | OAuth refresh token compromise enables persistent unauthorized API access | Moderate (3) | Moderate (3) | MEDIUM (9) | Keyring encryption, file permissions, per-account isolation, revocation capability | LOW-MEDIUM (4) |
| GCP-R3 | Consumer accounts in organizational project create identity management complexity | Low (2) | Low (2) | LOW (4) | Service Usage Consumer role limitation, no billing access, audit trail | LOW (2) |
| GCP-R4 | OAuth client secret exposure enables token minting by unauthorized parties | Low (2) | High (4) | MEDIUM (8) | chmod 600, .gitignore exclusion, rotation procedure documented | LOW-MEDIUM (4) |
| GCP-R5 | Overly broad OAuth scopes enable data access beyond operational need | Low (2) | Moderate (3) | MEDIUM (6) | Scopes bounded to modify (not full access), each account accesses only own data | LOW (3) |

### 10.2 Risk Detail: GCP-R1 (Domain Restriction Relaxation)

**Threat:** An attacker who gains Organization Administrator access could add any Google identity as an IAM principal, bypassing the domain restriction guardrail that would normally prevent this.

**Likelihood:** Low. Exploitation requires compromise of the admin@example-ops.com account, which is the sole Organization Administrator. The attacker would need both the account credentials and MFA bypass.

**Impact:** Moderate. An unauthorized principal could be assigned roles that grant access to project resources, API quota, or audit logs.

**Compensating controls:**
- Admin Activity audit logs capture all `SetIamPolicy` calls and cannot be disabled
- Only the Workspace admin account can modify IAM bindings
- Consumer accounts hold no role that permits IAM policy modification
- Quarterly review of the policy modification ensures ongoing risk acceptance validity

### 10.3 Risk Detail: GCP-R2 (Refresh Token Compromise)

**Threat:** An attacker who obtains a refresh token from the local keyring or through a machine compromise could make API calls as the token's associated account until the token is revoked.

**Likelihood:** Moderate. Refresh tokens are stored locally on the operator workstation. Malware, unauthorized physical access, or a backup exposure could lead to token extraction.

**Impact:** Moderate. The attacker would gain the same API access as the compromised account: email read/write/send, Drive file access, Sheets/Docs/Calendar/Slides/Tasks operations. For consumer accounts, this is limited to each account's own data. For the admin account, project-level resource access is also possible.

**Compensating controls:**
- Tokens stored in OS-level encrypted keyring (not plaintext on disk)
- File permissions enforce user-only access (chmod 600)
- Per-account credential isolation limits blast radius to one account
- Immediate revocation capability via API or Google Account page
- Access tokens expire in 1 hour, requiring the refresh token for continuation

### 10.4 Risk Detail: GCP-R4 (Client Secret Exposure)

**Threat:** The OAuth client secret, if exposed through source control, backup, or file sharing, enables an attacker to mint valid authorization URLs and exchange authorization codes for tokens. This does not bypass user consent, but enables phishing scenarios where the attacker presents a legitimate-looking OAuth consent screen.

**Likelihood:** Low. The client secret is stored with chmod 600 and excluded from version control. Exposure would require a targeted file exfiltration or a misconfigured backup.

**Impact:** High. A compromised client secret enables sophisticated phishing against any Google account that has previously consented to the OAuth client. The attacker could intercept authorization codes if they control the redirect URI.

**Compensating controls:**
- Redirect URIs locked to `http://localhost` and the svc-automation callback URL in Google Cloud Console
- Google rejects authorization code exchanges where the redirect URI does not match the registered URIs
- Client secret rotation invalidates all existing tokens, forcing re-authentication
- Source control exclusion via `.gitignore` prevents accidental commit

---

## 11. Recommendations

### 11.1 Priority Actions

| Priority | Recommendation | NIST Control | Target Date |
|----------|---------------|-------------|-------------|
| HIGH | Enable Data Access audit logs for Gmail API and Google Drive API | AU-2, AU-3 | 2026-04-05 |
| HIGH | Create Cloud Monitoring alert policies for IAM and org policy changes | AU-6, SI-4 | 2026-04-05 |
| MEDIUM | Re-evaluate `iam.allowedPolicyMemberDomains` policy after 90 days of stable operation | AC-3, CA-7 | 2026-06-22 |
| MEDIUM | Implement OAuth token rotation schedule (revoke and re-authenticate quarterly) | IA-5(1) | 2026-06-22 |
| MEDIUM | Monitor API usage for anomalous volume or unusual access patterns | SI-4, AU-6 | Ongoing |
| LOW | Evaluate service account migration for svc-automation workflows (eliminates consumer account dependency for automated operations) | AC-2, IA-4 | 2026-09-22 |
| LOW | Investigate per-account OAuth scope restriction if multi-user onboarding occurs | AC-6, AC-3 | As needed |

### 11.2 Long-Term Considerations

**Service Account Migration:** Automated workflows running through svc-automation currently authenticate via user OAuth tokens. Migrating to a Google Cloud service account with domain-wide delegation would eliminate the need for consumer account IAM bindings and allow the `iam.allowedPolicyMemberDomains` constraint to be re-restricted. This migration requires Google Workspace admin configuration for domain-wide delegation and is tracked as a low-priority item given the single-operator context.

**Workspace Licensing:** If additional operators are onboarded, each should receive a Workspace account under the example-ops.com domain rather than using consumer Gmail accounts. This eliminates the need for the domain restriction policy relaxation and provides centralized identity lifecycle management through the Workspace Admin Console.

---

## 12. Cross-References

| Document | Relevance |
|----------|-----------|
| [IAM_RBAC_ROLE_MAP.md](IAM_RBAC_ROLE_MAP.md) | Infrastructure-level RBAC model (3-tier: admin/operator/auditor) that this Google Cloud IAM configuration extends to cloud services |
| [IAM_ACCESS_REVIEW.md](IAM_ACCESS_REVIEW.md) | Access review process and JIT workflow. Google Cloud IAM principals should be included in the monthly access review cycle. |
| [POLICY_ACCESS_CONTROL.md](POLICY_ACCESS_CONTROL.md) | Organizational access control policy (AC-1 through AC-12) governing all identity and authorization decisions, including cloud IAM |
| [PLAYBOOK_LEAKED_CREDENTIAL.md](PLAYBOOK_LEAKED_CREDENTIAL.md) | Credential compromise response procedures applicable to OAuth client secret or refresh token exposure |
| [RISK_ASSESSMENT.md](RISK_ASSESSMENT.md) | Master risk assessment. Risks GCP-R1 through GCP-R5 from this document should be incorporated at the next quarterly review. |

---

## Appendix A: OAuth Scope to API Permission Mapping

| OAuth Scope URI | Shorthand | API | Permissions Granted | Permissions NOT Granted |
|-----------------|-----------|-----|--------------------|-----------------------|
| `https://www.googleapis.com/auth/gmail.modify` | gmail.modify | Gmail API | Read, compose, send, label, archive | Permanent delete, admin settings |
| `https://www.googleapis.com/auth/gmail.send` | gmail.send | Gmail API | Send only | Read, delete, label, admin settings |
| `https://www.googleapis.com/auth/drive` | drive | Google Drive API | Full CRUD on user's files | Admin console, org-wide access |
| `https://www.googleapis.com/auth/spreadsheets` | spreadsheets | Google Sheets API | Full CRUD on spreadsheets | Drive file management |
| `https://www.googleapis.com/auth/documents` | documents | Google Docs API | Full CRUD on documents | Drive file management |
| `https://www.googleapis.com/auth/calendar` | calendar | Google Calendar API | Full CRUD on calendars/events | Admin console |
| `https://www.googleapis.com/auth/presentations` | presentations | Google Slides API | Full CRUD on presentations | Drive file management |
| `https://www.googleapis.com/auth/tasks` | tasks | Google Tasks API | Full CRUD on task lists/tasks | Calendar events |
| `https://www.googleapis.com/auth/userinfo.email` | userinfo.email | OAuth 2.0 | Read email address | Write, account settings |
| `https://www.googleapis.com/auth/userinfo.profile` | userinfo.profile | OAuth 2.0 | Read display name, profile photo | Write, account settings |
| `openid` | openid | OpenID Connect | ID token with subject identifier | Any resource access |
| `https://www.googleapis.com/auth/cloud-platform` | cloud-platform | Google Cloud | Project resource access per IAM role | Exceeds IAM role grants |

---

## Appendix B: Google Cloud CLI Verification Commands

The following commands can be used to verify the IAM configuration described in this assessment:

```bash
# List organization-level IAM bindings
gcloud organizations get-iam-policy [ORG-ID] --format=yaml

# List project-level IAM bindings
gcloud projects get-iam-policy org-automation-project --format=yaml

# Check organization policy for domain restriction
gcloud org-policies describe iam.allowedPolicyMemberDomains \
  --organization=[ORG-ID] --effective

# List enabled APIs in the project
gcloud services list --project=org-automation-project --enabled

# Verify OAuth client configuration
gcloud auth application-default print-access-token  # confirm token exchange works

# Review recent Admin Activity audit logs
gcloud logging read \
  'logName="organizations/[ORG-ID]/logs/cloudaudit.googleapis.com%2Factivity"' \
  --limit=25 --format=json

# Check IAM role details for Service Usage Consumer
gcloud iam roles describe roles/serviceusage.serviceUsageConsumer
```
