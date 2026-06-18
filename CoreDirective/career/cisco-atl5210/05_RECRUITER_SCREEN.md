# Cisco ATL5210 — Recruiter Screen Talking Points

**Time:** 2026-06-05, 10:30 AM ET (Friday — confirm via calendar invite)
**Recruiter:** AMS Shared Mailbox (no named recruiter)
**Role:** Information Security Engineer (CyberArk PAM specialist), Atlanta, GA, Req ATL5210

## Goal of This Call
**Primary:** Determine if this is a real opening or PERM filing. ~85% likely PERM (see `00_JOB_DESCRIPTION.md`).
**Secondary:** Surface other Cisco InfoSec / AI Security openings.
**Tertiary:** Build Cisco recruiter network for future inbound.

**Do NOT** fabricate CyberArk experience. Do NOT pretend to be excited about a 5-year CyberArk admin role.

## Opening (60 seconds — fire this first)
"Thanks for sending the JD over. I want to be efficient with your time — I read it before the call. The role is centered on CyberArk-specific tooling (PSM, PSMP, PTA, Conjur, CP/CCP). My PAM and secrets-management work is in HashiCorp Vault and Teleport, not CyberArk. Before we go deep, can you share whether the team is open to a candidate with adjacent-tool depth and willingness to ramp on CyberArk, or is direct CyberArk product experience a hard requirement?"

This single question resolves 80% of the call. Their answer tells you whether to proceed or pivot.

## If "Direct CyberArk Required"
"Understood, then I'm not the right fit for ATL5210. I appreciate the honest read. Two quick questions before we wrap:
1. Does Cisco have other Information Security or AI Security Engineer openings in Atlanta or remote that match a candidate with HashiCorp Vault, Teleport, Keycloak, Cloudflare Zero Trust, and AI/LLM security depth?
2. Is there a way to stay on your radar for future roles — preferred email or LinkedIn?"

Close warm. Get other reqs. End call in 10 minutes.

## If "Adjacent Tools Acceptable"
Now actually run the screen.

### What I Bring
- 4 years at Texaco IT Security & Operations Manager (Atlanta, GA) — managed identity, AD, GPO, 45+ PCI DSS devices
- Currently AI Security Engineer at CoreDirective, building production AI gateway (OpenClaw running Claude Opus 4.7)
- HashiCorp Vault deployed in production (cd-service-vault) for secrets storage
- Teleport v18 for PAM — session recording, JIT access, audit shipping to Datadog
- Keycloak v26 for SSO/IGA — SAML/OIDC, RBAC
- Cloudflare Zero Trust + mTLS, zero exposed ports
- Terraform for 30+ DO/CF resources, 8 OPA/Rego policies, Cosign signing, Syft SBOMs
- Python automation throughout the SOAR stack
- CCNA 200-301 (Cisco's own cert — networking depth)
- SecurityX (CASP+), SSCP

### Honest Gaps
- No CyberArk product experience — would need to ramp on Vault/CPM/PSM
- Jenkins limited (use GitHub Actions); OpenShift limited (use Docker Compose)
- PowerShell limited (Python primary)

### Why Cisco Specifically
- Cisco-Splunk acquisition — Splunk SIEM is in current Texaco stack
- Cisco Duo — adjacent to Keycloak SSO work
- Atlanta presence — Emmanuel is local
- Hometown brand recognition for an InfoSec engineer building production AI security

## Confirm Role Basics (always ask)
- "Is this Cisco's internal Information Security org or product-side security?"
- "What's the level — Grade 9, 10, 11? Comp range?"
- "Is this 3-day hybrid in the Atlanta office or flex?"
- "How many interview rounds, who do I meet?"
- "What's the priority hire timeline — when are you looking to close?"
- "When was the req opened? Has it been on hold at any point?" (smoke-out PERM)

## Compensation
**Do NOT anchor first.** If asked: "I'm targeting $200K+ base for senior AI Security roles. For an InfoSec Engineer role in Atlanta with the listed stack, I'd want to see the band before I commit. What's the range Cisco has approved for ATL5210?"

If pushed: floor at $135K base.

## Red Flags to Watch (signal PERM confirmation)
- Recruiter dodges "is the role still actively interviewing other candidates?"
- Recruiter cannot share comp range
- Recruiter cannot describe team composition or hiring manager name
- Interview loop is "TBD" or "we'll get back to you"
- Recruiter says "we're still finalizing the JD" (despite having sent it)

## Close
"What are next steps and timeline? When should I expect to hear back?"

## Logistics
- Resume submitted: AI Security Engineer variant (Mar 2026)
- Personal Gmail used to apply: emmanueltigoue@gmail.com
- Primary contact: etigoue@tigouetheory.com
- Available immediately for next-round screen if invited

## After the Call (within 1 hour)
1. Update `application-trace.md` with screen outcome
2. Update `00_INDEX.md` status (PERM-CONFIRMED / OPEN-PROCEED / CLOSED)
3. Add row to Job Pipeline Tracker if not already present
4. Update memory file with Cisco AMS recruiter pattern intel
5. Send thank-you email within 4 hours

## Thank-You Email Template
```
Subject: Thank you - ATL5210 Screen

Hi,

Thanks for the time today. To summarize:
- [Outcome: e.g., role requires direct CyberArk depth I don't have; or, next round scheduled for X]
- [Any other openings discussed: list them]

I'll keep an eye on Cisco InfoSec and AI Security postings in Atlanta or remote. If anything matching my stack opens up (HashiCorp Vault, Teleport, Keycloak, Cloudflare Zero Trust, AI/LLM security, GRC), please send it my way.

Thanks again,
Emmanuel Tigoue
etigoue@tigouetheory.com
linkedin.com/in/emmanuel-tigoue
```
