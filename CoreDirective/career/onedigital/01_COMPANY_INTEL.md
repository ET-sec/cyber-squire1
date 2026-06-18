# OneDigital — Company Intelligence (Verified)

Every fact below is sourced. No speculation unless explicitly labeled. Dates are from public reporting.

---

## 1. Company Overview

**Legal name:** OneDigital Health and Benefits, Inc. (consumer brand: OneDigital)
**Founded:** 2000, Atlanta GA
**Founder + current role:** Adam Bruckman — Chairman and CEO
**Headquarters address:** 300 Galleria Parkway, Suite 1100, Atlanta GA 30339
**Location context:** Cumberland / Galleria submarket of Atlanta (not downtown Battery; same general area, a few minutes from Truist Park / The Battery). Cobb County side of I-285.
**Scale:** Over 5,000 employees, 250+ offices across the United States and Canada, serving 100,000+ employers and millions of individuals

**What they actually do:** Insurance brokerage, financial services, and HR consulting. Primary practices:
- Employee Benefits (flagship)
- HR & Workplace Consulting
- Retirement and Financial Planning (this is the line where the 2025 breach hit — "OneDigital Investment Advisors LLC")
- Medicare Advantage
- Property & Casualty insurance
- Wealth Management

**Industry ranking:** Top 20 largest US insurance broker continuously since 2017 (Business Insurance magazine rankings)

---

## 2. Ownership and Capital Structure (UPDATED)

**This changed recently — your memory and tracker tab previously said "Onex-owned." It is no longer majority Onex.**

**December 4, 2025:** Stone Point Capital and CPP Investments (Canada Pension Plan) closed a strategic investment that gave them majority ownership. Transaction valued OneDigital in excess of **$7 billion**.

**Current cap table:**
- Stone Point Capital + CPP Investments — majority owners (as of Dec 4, 2025)
- Onex Partners — remains a significant minority owner (was majority from Oct 2020 to Dec 2025)
- Other existing shareholders retained stake

**What this means for the interview:**
- Fresh capital means hiring + tooling budget is healthy
- New majority owners want growth proof points — AI security is a growth-era investment line
- If Pavel brings up "where the company is headed," the right register is "strategic growth under Stone Point / CPP, building out the security program to match enterprise scale"
- Do NOT say "Onex-owned" or "PE-backed" as if nothing changed — the investor set shifted four months ago

---

## 3. Recent M&A (growth signal — OneDigital is a roll-up)

**2026:**
- Silicon Valley Retirement Services — LBO closed Feb 26, 2026
- Amplified Benefits Partners — OneDigital acquired their Employee Benefits + HR Services divisions (2026)

**Historical pattern:**
- 200+ acquisitions since founding
- Acquired firms are rolled into regional OneDigital offices
- CEO Bruckman's model: aggressive organic growth + high-velocity acquisitions

**Interview implication:** Security scale challenge is real. Every acquisition = new identities to onboard, new SaaS to inventory, new data to classify, new endpoints to enroll in CrowdStrike. This is a pattern Pavel likely owns. If asked about what would excite you, M&A security integration is a defensible answer — it's an ongoing challenge, not a hypothetical.

---

## 4. 2026 Leadership Changes

- **Adam Bruckman** — Chairman and CEO (founder, since 2000)
- **Bill Carew** — promoted to President in 2026. Reports to Bruckman. Oversees regional operations and platform-level businesses.
- **Camry Blaising** — promoted to Chief Operating Officer in 2026. Reports to Carew. Oversees day-to-day operations.

**Interview implication:** Leadership team is fresh in their new roles (<1 year). When you ask "what is success at one year," you are asking a question the leadership is also asking themselves. Lower risk of stepping on sensitive internal politics.

---

## 5. The 2025 Salesforce / Salesloft / Drift Breach (ACTIVE — Pavel will reference)

**This is the single most important item in this document. Pavel notified affected clients in writing on April 8, 2026. That is 13 days ago. This is a live, unresolved operational matter when you sit down with him on Thursday.**

### What happened — verified timeline

- **March–June 2025:** Threat cluster UNC6395 compromised Salesloft's GitHub environment. Added a guest user and created rogue workflows for persistence.
- **(Pre-August 2025):** UNC6395 pivoted from GitHub into Drift's AWS environment. Drift is a chatbot tool that integrates with Salesforce. Salesloft acquired Drift and managed the integration.
- **August 12–18, 2025:** Attackers used stolen OAuth tokens (tied to customer integrations) to bulk query and export records from Salesforce instances across 700+ organizations.
- **August 22, 2025:** Salesforce notified OneDigital that its Salesforce instance was potentially affected.
- **December 22, 2025:** OneDigital formally discovered the breach in its own environment (the gap between Aug 22 notification and Dec 22 discovery is the investigation window).
- **April 8, 2026:** OneDigital began sending written notifications to affected clients.

### OneDigital specifics

- **Affected individuals:** 28,414 people in the US
- **Data exposed:** Full names and Social Security Numbers
- **Business line affected:** OneDigital Investment Advisors LLC (retirement / financial planning — not the employee benefits side)
- **Internal network compromised:** NO. This was purely a third-party SaaS integration compromise.
- **Remediation offered:** 12 months of complimentary Experian IdentityWorks credit and identity monitoring
- **Regulators notified:** Maine AG, California AG, Massachusetts AG (industry-standard per HIPAA-adjacent and state breach laws)
- **Active litigation:** Class action being investigated by Migliaccio & Rathod LLP and others

### What the industry (FINRA, CSA, Cloudflare, Anomali) identified as remediation priorities

Memorize these — Pavel will almost certainly ask some variant of "if you were here during that response, what would you have done." Answer from this list, do not invent.

1. **Disconnect all Salesloft / Drift integrations** from Salesforce and any other platforms immediately upon awareness
2. **Rotate OAuth tokens and credentials** that were exposed to the compromised integration
3. **Conduct forensic audit log reviews** of all Salesforce queries and exports during the breach window
4. **Reduce third-party application permission scopes** — principle of least privilege applied to OAuth apps
5. **Deploy monitoring for anomalies in data volume** — detect bulk queries or exports that look unlike normal user behavior
6. **Embed OAuth scope reviews into Identity Governance procedures** — this is the control that prevents the next one
7. **Vendor SDLC attestation** — require SaaS vendors to prove how they handle OAuth token storage, rotation, and compromise response

### How to talk about this with Pavel

- **Do not lead with it** — let him bring it up. He may not, depending on legal guidance.
- **If he brings it up generally** ("we had a third-party incident last year"): acknowledge awareness from public reporting. Do not name specific numbers. Pivot to the control framework: "The Salesloft / Drift OAuth compromise was a good demonstration of why OAuth scope hygiene and third-party integration monitoring have to be treated as first-class controls, not afterthoughts."
- **If he asks what you would do if it happened here tomorrow:** use the 7-point list above, in order. Frame it as "first 48 hours, first two weeks, first quarter" timeboxes.
- **Connect it to the JD:** The role JD calls out SOC 2 Type 2 vendor review AND Salt Security for API/data pipeline protection. That is directly responsive to this incident class. You can say so.
- **Do not over-claim:** You have not lived through this breach at OneDigital. Do not say you would have "saved" them. Say you would apply the published industry remediation playbook and contribute to preventing the next one.

---

## 6. Culture and Employee Sentiment (Glassdoor 2025-2026 verified)

**Overall rating:** 3.1 out of 5 (from 937+ reviews)
**Trajectory:** Declined 6% over the last 12 months
**Recommend to friend:** 51%
**Positive business outlook:** 50%
**Compensation & benefits rating:** 2.9/5 (declined 8% over 12 months)
**Work-life balance:** 3.2/5
**Culture & values:** 3.1/5
**Career opportunities:** 3.1/5

### Positive themes (verbatim from reviews)
- "Great culture and family feel for a large company"
- "I worked with some truly great people"
- "Benefits are great" (makes sense — they're a benefits broker)
- "Great work life balance"

### Negative themes (verbatim)
- "Management is incompetent" (one review)
- "Minimal or no training"
- Micromanagement mentions
- Bonus payment delays

### Role-level signal
Best-rated roles on Glassdoor: **Principal, Client Executive, and Manager** positions. That means senior ICs and people-managers tend to be happier than entry-level or individual contributor roles.

**Interview implication:**
- OneDigital is mature and family-brand-oriented, not a ship-fast startup
- "Heavy workloads" is a consistent theme — Pavel may probe how you handle ownership over multiple parallel streams. Have an answer ready.
- Leadership sentiment is mixed — if Pavel asks about management style you prefer, lean toward "autonomy with clear outcomes" rather than "daily check-ins"
- Bonus payment delays may be a cost-management artifact of the ownership transition

---

## 7. Interview Process (OneDigital overall — Glassdoor verified)

- **Average time to hire:** 21.9 days across 113 submitted interview reports
- **Positive experience rate:** 58.4%
- **Difficulty rating:** 2.48 / 5 (medium-low)
- **Format:** Commonly Zoom or Teams, sometimes in-person with office tour after HM round
- **Typical structure:** 1–3 rounds total. OneDigital is not a 6-round tech company.

### What this role's loop looks like (from your memory + public signal)
1. **Recruiter screen (DONE 4/16):** Zac Bennett at FTS. Passed.
2. **HM screen (THU 4/23 1 PM EDT, 30 min):** Pavel Kotelnikov on Teams. Technical + behavioral mixed.
3. **Likely final round (not confirmed):** Panel with peer IT Security team members and/or a tabletop-style scenario. Zac mentioned a "2-round process" in his initial outreach but may have been rounding.

Expect that passing Thursday leads to a same-week or following-week panel. If it's only 2 rounds, Thursday IS the technical round — treat it that way.

---

## 8. Why OneDigital Is Hiring an AI Security Engineer Right Now

**Three drivers, in order of likely weight:**

1. **Salesloft / Drift breach aftermath.** SaaS third-party risk is a live operational wound. Building AI workflows on the heels of a SaaS integration breach demands someone who thinks in "what is the next OAuth token someone steals."

2. **AI adoption pressure from internal stakeholders.** OneDigital's practice areas (benefits consulting, retirement planning, wealth management) are all areas where generative AI gets pitched by vendors daily. The role exists to keep the business from adopting AI tools faster than security can vet them.

3. **New ownership signaling.** Stone Point Capital and CPP Investments closed in Dec 2025 at a $7B valuation. They expect growth, and growth via acquisition plus AI adoption plus a client-data custodian posture means the security function has to scale. This is a cover role for that expansion.

**Interview implication:** When asked "why did you apply" or "why OneDigital," the right register connects to these three drivers, not to "I want to do AI security." Example frame: "The combination of an active third-party risk posture, AI adoption pressure on a client-data custodian, and fresh capital under Stone Point told me this role is about real budget and real stakes, not a box-checking exercise."

---

## 9. Key Links and Sources

- **Company:** [onedigital.com](https://www.onedigital.com/)
- **Atlanta HQ page:** [onedigital.com/en-US/locations/atlanta-ga-headquarters](https://www.onedigital.com/en-US/locations/atlanta-ga-headquarters/)
- **Adam Bruckman profile:** [onedigital.com/en-US/people/adam-bruckman](https://www.onedigital.com/en-US/people/adam-bruckman/)
- **Stone Point + CPP investment closing:** [onex.com/article/2025NewsRelease-OneDigitalClose-December4](https://www.onex.com/article/2025NewsRelease-OneDigitalClose-December4)
- **Globenewswire press release Dec 2025:** [globenewswire.com/news-release/2025/12/04/3200251](https://www.globenewswire.com/news-release/2025/12/04/3200251/0/en/Onex-Partners-Announces-Completion-of-Strategic-Investment-in-OneDigital-by-Stone-Point-Capital-and-CPP-Investments.html)
- **OneDigital breach disclosure (PlanSponsor):** [plansponsor.com/onedigital-latest-to-warn-clients-of-salesforce-data-breach](https://www.plansponsor.com/onedigital-latest-to-warn-clients-of-salesforce-data-breach/)
- **Breach technical details (BeyondMachines):** [beyondmachines.net/event_details/onedigital-reports-data-breach](https://beyondmachines.net/event_details/onedigital-reports-data-breach-following-salesforce-and-drift-integration-compromise-g-d-7-8-9)
- **FINRA alert on Salesloft Drift:** [finra.org/rules-guidance/guidance/salesloft-drift-AI-supply-chain-attack](https://www.finra.org/rules-guidance/guidance/salesloft-drift-AI-supply-chain-attack)
- **Anomali breach recap:** [anomali.com/blog/salesloft-drift-breach-recap](https://www.anomali.com/blog/salesloft-drift-breach-recap)
- **Cloud Security Alliance analysis:** [cloudsecurityalliance.org/blog/2025/09/25/the-salesloft-drift-oauth-supply-chain-attack](https://cloudsecurityalliance.org/blog/2025/09/25/the-salesloft-drift-oauth-supply-chain-attack-cross-industry-lessons-in-third-party-access-visibility)
- **OneDigital Glassdoor reviews:** [glassdoor.com/Reviews/OneDigital-Reviews-E1355072.htm](https://www.glassdoor.com/Reviews/OneDigital-Reviews-E1355072.htm)
- **OneDigital Glassdoor interviews:** [glassdoor.com/Interview/OneDigital-Interview-Questions-E1355072.htm](https://www.glassdoor.com/Interview/OneDigital-Interview-Questions-E1355072.htm)
- **Pavel's LinkedIn:** [linkedin.com/in/pavel-kotelnikov-cisa-632604b4](https://www.linkedin.com/in/pavel-kotelnikov-cisa-632604b4/)
- **ISACA Atlanta Chapter:** [engage.isaca.org/atlantachapter/home](https://engage.isaca.org/atlantachapter/home) (2,800+ members, Pavel's probable professional community)
