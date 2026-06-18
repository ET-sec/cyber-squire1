# Cisco Information Security Engineer (ATL5210) — Pre-Interview Cheat Card

**Interview:** Tuesday June 23, 3:30 PM EST (pending confirmation)
**Format:** HM technical screen (Cisco norm: 30 to 45 minutes)
**Recruiter contact:** amsrecruiting@cisco.com

## Opening line (if you speak first)

"I've been running privileged access and secrets in production for the AI platform at CoreDirective: Teleport JIT, HashiCorp Vault, Keycloak SSO with role based access control. I came to the ATL5210 role because the operational discipline and the identity work are exactly what I've been shipping."

DO NOT volunteer the CyberArk gap. Lead with what you've built.

## 3 killer talking points (rank order)

**1. AD hardening at Texaco is the lead.** Closed **12 of 14** critical audit findings on Active Directory: GPO baselines, stale account cleanup, removed standing admin rights, automated credential rotation. This is real operational identity work at scale. Have the story tight, walk it through end to end if asked.

**2. HashiCorp Vault and Teleport JIT in production now.** At CoreDirective I run Vault as the secrets layer, Teleport for JIT privileged access with session recording, Keycloak for SSO and RBAC. MFA enforced on admin paths. Standing admin eliminated. This is the same problem space CyberArk solves, different vendor.

**3. Python and PowerShell automation reclaiming 12 hours weekly.** Texaco: automated patch deployment, user provisioning, and compliance reporting. Cisco wants PIM process automation in the same stack. Same skill, larger blast radius.

## How to answer the CyberArk question

If they ask about specific CyberArk components, the answer is NOT "I do not have CyberArk production." That hands them the rejection.

The answer IS:

"I've worked the same problem space at the AI agent layer with HashiCorp Vault, Teleport for JIT privileged access, and Keycloak for identity federation. I've studied the CyberArk component architecture and I know how Vault, CPM, PSM, PSMP, PTA, and Conjur fit together. The hands-on with the specific product is what I'd own in the first 30 days."

Then SHIFT to a concrete example: "Here's how I think about the problem. At CoreDirective the equivalent of CPM rotating credentials on managed targets is..."

This is not lying. CyberArk's component map is public. Study it (4 hours, see STUDY_LIST.md). By Tuesday you can speak to the architecture confidently. What you cannot speak to is hands-on troubleshooting of a specific PSM error or a Vault clustering issue. If they push there, you redirect to your Vault and Teleport experience and frame the specific product knowledge as a 30 day ramp.

## How to answer other gaps

| Gap | Answer |
|---|---|
| Jenkins | "I run GitHub Actions in production. Pipeline as code is pipeline as code. Jenkins syntax is a translation, not a new concept." |
| OpenShift | "I run Docker and orchestrate containers on DigitalOcean. OpenShift is Red Hat's Kubernetes distribution. Two weeks of focused work to get fluent." |
| SailPoint or Saviynt | "I implement role based access control through Keycloak with OAuth and SAML federation. IGA concepts (access reviews, attestation, separation of duties) I can speak to. Vendor tooling I'd ramp." |

Across all of these: never lead with "I do not have." Always lead with what you DO have, then frame the specific product as a bounded ramp.

## Tactical Cisco-specific moves

- **Lead with CCNA when networking protocols come up.** Cisco hires hold CCNA in high regard, especially for an InfoSec Engineer role at their Atlanta office.
- **Do not claim CyberArk component knowledge you do not have.** Cisco runs CyberArk internally. The HM team knows the product deeply. Bluffing component names (DR Vault, PSMP, PTA) will lose the room.
- **Do not bring up AI Security unless asked.** They want a PAM specialist. The AI Sec resume is what got you in. They have it. You do not need to re-pitch that angle.
- **Bring 3 concrete examples ready to walk through:**
  1. Teleport JIT PAM deployment story (CoreDirective)
  2. AD hardening story with 12 of 14 audit findings (Texaco)
  3. Python automation story (compliance reporting, user provisioning)

## 4 questions to ask the HM

1. What does the team's PAM environment look like today? Are you net-new building, or operating an existing CyberArk install?
2. How is on-call structured for the PAM team?
3. What is the 30-day, 60-day, 90-day ramp plan you would expect from a new hire on this role?
4. What does success look like at the 6-month mark?

## Rate play

- Do not anchor first. Cisco has internal bands.
- If they ask for your number: "I would want to see the full package before naming a base. Equity vest schedule, bonus target, and benefits all matter. The right base depends on the total."
- If they insist: $170K base target, $150K floor.
- Walk-away floor: $150K base.
- All rate talk on the call, never in writing.

## Avoid

- Do NOT say "I do not have CyberArk." Lead with what you DO have. Frame the specific product as a 30 day ramp.
- Do NOT bluff a specific CyberArk feature or error you have not actually touched. Architecture-level fluency is fair game. Hands-on troubleshooting claims are not.
- Do NOT pitch CoreDirective as a side project. It is the employer.
- Do NOT bring up Voya or any other opportunity.
- Do NOT mention you are interviewing elsewhere unless they ask.
- Do NOT say "immediately available" or "ready to start".
- Do NOT lead with the CISSP. Lead with the operational PAM work.

## After the call

Write a tight follow-up email within 4 hours. Reference one concrete thing the HM said. Send to amsrecruiting@cisco.com with HM cc'd if they share the address.
