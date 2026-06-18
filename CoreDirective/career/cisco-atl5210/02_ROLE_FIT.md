# Cisco ATL5210 — Role Fit Analysis

**Verdict:** ~25% match. Role is CyberArk PAM specialist, not AI Security Engineer. Likely PERM filing (see `00_JOB_DESCRIPTION.md`).

## Hard Requirements vs Emmanuel

| Requirement | Emmanuel | Gap |
|-------------|----------|-----|
| CyberArk Vault / DR Vault | None | CRITICAL gap |
| CyberArk CPM / PSM / PSMP / PTA | None | CRITICAL gap |
| CyberArk Conjur | None | CRITICAL gap |
| CyberArk CP / CCP | None | CRITICAL gap |
| HashiCorp Vault | Deployed in cd-service-vault | MATCH |
| AWS Secrets Manager | Aware, not deployed | Partial |
| AD Schema / GPO | Texaco IT Sec Ops Mgr exposure | Partial |
| PKI | Cloudflare mTLS, Cosign signing | MATCH (different stack) |
| PowerShell automation | Limited | Gap |
| Python automation | Strong (n8n, SOAR scripts) | MATCH |
| Networking protocols (TCP/UDP/DNS/etc) | Strong (CCNA) | MATCH |
| Routing/switching/firewall | CCNA + Cloudflare WAF | MATCH |
| Windows + Linux admin | Linux strong, Windows Texaco-era | Partial |
| AD / IIS / LDAPS | Texaco era | Partial |
| SAML / OAuth / SCIM | Keycloak deployed (OIDC), SAML conceptual | Partial |
| IGA integration | Keycloak only | Partial |
| Cloud (AWS/GCP/Azure) | DigitalOcean primary, AWS some | Partial |
| Jenkins / Ansible / Terraform | Terraform strong, Ansible some, Jenkins none | Partial |
| Docker / K8s / OpenShift | Docker Compose strong, K8s minimal, OpenShift none | Partial |
| 5+ years post-bacc InfoSec | Texaco 2022-2026 (~4 yrs) + CoreDirective | Borderline |

## What Emmanuel CAN Credibly Offer
1. **HashiCorp Vault production deployment** — JD explicitly lists Vault alongside CyberArk Conjur as acceptable secrets platforms
2. **Secrets management discipline** — Doppler integration, env var rotation, chmod 600 on .env, never-on-disk patterns
3. **PKI and mTLS** — Cloudflare Zero Trust + mTLS, Cosign image signing, Syft SBOMs
4. **Identity stack** — Keycloak v26 for SSO/RBAC, Teleport v18 for PAM/JIT (conceptually adjacent to CyberArk PSM)
5. **PAM concepts via Teleport** — Teleport v18 IS a PAM solution: session recording, just-in-time access, audit shipping via cd-service-event-handler. Not CyberArk, but same problem space.
6. **GRC depth** — 37 docs, SSP w/ 800-53, AI governance NIST AI RMF — useful for "adapt to changing regulatory requirements"

## What Emmanuel CANNOT Fake
- CyberArk product names, install/upgrade flow, PSMP routing rules
- Conjur policy syntax
- AD Schema modifications (vs just AD admin)
- Jenkins pipelines (use GitHub Actions instead)
- OpenShift (use Docker Compose instead)

## Honest Positioning
"I'm not a CyberArk specialist — my PAM stack is Teleport and HashiCorp Vault. If the role is open to a candidate with equivalent PAM/secrets-management depth on adjacent tooling and a willingness to ramp on CyberArk, I'd be interested. If you need a 5-year CyberArk admin specifically, I'm not the right fit, and I'd appreciate knowing if Cisco has other InfoSec or AI Security openings I should look at."

Why this framing:
- Respects the recruiter's time
- Surfaces other Cisco openings (the real prize from this call)
- Does not fabricate CyberArk experience
- Does not waste a 2nd round if PERM filing is the actual purpose
