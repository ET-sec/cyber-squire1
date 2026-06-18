# Cisco InfoSec Engineer (ATL5210) — 5-Day Study Plan

Tech interview Tue 6/23 3:30 PM EST. 5 days of prep (Wed 6/18 through Mon 6/22).

## TIER 1: must-know cold (8 hours over 3 days)

### CyberArk component map — 4 hours
Memorize the architecture diagram. Know what each component does and where it sits in the access path.

| Component | What it is | Where it sits |
|---|---|---|
| Vault | Encrypted credential storage at rest | Core, on-prem or cloud |
| DR Vault | Disaster recovery replica of Vault | Standby site |
| CPM (Central Policy Manager) | Rotates passwords on managed targets | Middle layer, talks to targets |
| PSM (Privileged Session Manager) | Records and proxies privileged sessions | User-facing access layer |
| PSMP (PSM for SSH Proxy) | SSH-specific privileged session proxy | SSH access path |
| PTA (Privileged Threat Analytics) | Detects anomalous privileged behavior | Analytics layer above Vault |
| Conjur | Secrets management for apps and DevOps pipelines | Secrets-as-API layer, similar to HashiCorp Vault |

Resource: search "CyberArk PAM architecture diagram" and study the official component diagram. Do not waste time on YouTube tutorials.

### HashiCorp Vault to CyberArk Conjur translation — 1 hour
You already run HashiCorp Vault. Map the equivalents:
- Vault secrets engines → Conjur policies
- Vault auth methods → Conjur authenticators
- Vault tokens → Conjur API keys
- Vault dynamic secrets → Conjur ephemeral secrets

Talk track: "I run HashiCorp Vault for secrets at the AI agent layer. The Conjur equivalents are X, Y, Z. The threat model is the same. The product migration is real but the discipline transfers."

### Active Directory + Group Policy + PKI refresh — 2 hours
Texaco bullet is your source of truth. Be ready to walk through:
- GPO baselines you enforced
- Stale account cleanup process
- Standing admin removal approach
- Credential rotation automation (Python + PowerShell)
- LDAPS configuration
- AD Schema basics (do not pretend to be a Schema expert)

### OAuth + SAML + SCIM mental model — 1 hour
- OAuth 2.0: access delegation, not authentication. Bearer tokens, scopes, refresh tokens.
- SAML: enterprise SSO, XML-based, browser redirects, IdP and SP roles.
- SCIM: cross-domain identity management, user provisioning API, GET/POST/PATCH on /Users and /Groups.

Keycloak is your prop. You ran Keycloak SSO RBAC. That is enough.

## TIER 2: high-probability (3 hours over 2 days)

### Networking protocols quick refresh — 1.5 hours
JD lists: TCP, UDP, DNS, NetBIOS, HTTP/HTTPS, SMTP, SNMP, SSH, TLS.

You have CCNA. This is muscle memory. Spend 1.5 hours touching:
- TLS handshake stages (ClientHello, ServerHello, Certificate, Finished)
- DNS resolution chain (recursive vs iterative)
- SNMP versions (v1, v2c, v3) and security implications
- NetBIOS / SMB lateral movement risk in PAM context

### Python automation patterns for PAM — 1 hour
Have 1 concrete Python automation story ready. Texaco patch deployment is best. Frame:
- What ran on what schedule
- Error handling and retry
- Logging and audit trail
- Integration with AD or service account credentials

### Cisco internal context — 30 min
- Cisco's market cap (~$215B), recent earnings sentiment
- Atlanta office context (Cisco Atlanta is a real engineering presence)
- Public CISO statements if any (search "Cisco CISO 2026")
- AnyConnect, Duo, Umbrella relevance to InfoSec org

## TIER 3: nice-to-have (1 hour, only if time)

### IGA concepts (not vendor tooling) — 30 min
- Access certification campaigns
- Separation of duties enforcement
- Joiner-mover-leaver process
- Privileged access reviews

Frame: "I have not used SailPoint or Saviynt, but the IGA mental model maps to what I have done in Keycloak with role-based access control and access reviews."

### OpenShift basics — 30 min
- Red Hat Kubernetes distribution
- Routes (vs Kubernetes Ingress)
- BuildConfigs and ImageStreams
- SCC (Security Context Constraints)

Acknowledge gap, do not overclaim.

## Heat map

| Topic | Status | Why |
|---|---|---|
| CyberArk component map | YELLOW (study) | Memorize before Tue |
| HashiCorp Vault | GREEN | Production at CoreDirective |
| Teleport JIT PAM | GREEN | Production at CoreDirective |
| Keycloak SSO + RBAC | GREEN | Production at CoreDirective |
| AD + GPO + standing admin | GREEN | Texaco bullets |
| Python + PowerShell automation | GREEN | Texaco bullets |
| OAuth + SAML federation | GREEN | Keycloak prop |
| SCIM | YELLOW | Concept solid, no specific tool |
| Networking protocols | GREEN | CCNA |
| TLS handshake | GREEN | Sec+ + CISSP |
| Conjur | YELLOW (translate from Vault) | Same concept, different tool |
| Jenkins | RED (acknowledge) | Use GH Actions instead |
| OpenShift | RED (acknowledge) | Docker only, no OpenShift |
| SailPoint or Saviynt IGA | RED (acknowledge) | Concept only |
| CyberArk PTA | YELLOW (read the wiki) | Analytics layer, learn the boundaries |

## Time budget

- Wed 6/18 (today): 2 hours CyberArk component map + 1 hour Vault-to-Conjur translation
- Thu 6/19: 2 hours AD/GPO/PKI refresh + 1 hour OAuth/SAML/SCIM
- Fri 6/20: 1.5 hours networking + 1 hour Python automation story rehearsal
- Sat 6/21: 1 hour Cisco context + run full mock interview answering top 10 predicted questions
- Sun 6/22: REST. Re-read this doc once. Lay out clothes, test camera, test mic.
- Mon 6/22 morning: Light review only. Do NOT cram.
- Tue 6/23 3:00 PM: 30 min before. Walk, water, breathe. NO last-minute studying.

Total: ~11 hours over 5 days.
