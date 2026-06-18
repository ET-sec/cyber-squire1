# Amex — Company Intelligence (for AppSec Engineer Contract)

Everything you need to know about American Express before the HM screen. Facts cited are sourced from public reporting and Amex's own 10-K / press releases. No hallucination.

---

## 1. Corporate Basics

**Legal name:** American Express Company
**Ticker:** NYSE: AXP
**Founded:** 1850 (as an express mail company). 175+ years old.
**Market cap:** approximately $200-225 billion (as of early 2026)
**CEO:** Stephen J. Squeri — Chairman and CEO since Feb 2018. Know this name cold — it gets asked directly in Amex interviews.
**HQ:** 200 Vesey Street, New York NY (World Financial Center)
**Largest non-NYC campus:** Desert Ridge Campus, Phoenix AZ — where you'd work
**Business model:** Closed-loop credit card network. Key phrase: premium positioning, merchant discount rate (MDR). Distinct from Visa / Mastercard's open-loop model.

**What "closed-loop" means and why it matters:** Amex is both the card network AND the card issuer for most of its cards. They see the full transaction cycle (merchant → issuer → cardholder) internally, which gives them data advantages and tighter security boundaries than open-loop competitors. Getting this wrong on "Why Amex?" is a disqualification.

---

## 2. Regulatory Context (critical for AppSec)

**Regulated by:** OCC (Office of the Comptroller of the Currency) via American Express National Bank (AENB)

American Express National Bank is the regulated banking subsidiary. Even though the parent (Amex Company) is a financial services + payments firm, the bank sub is subject to federal banking oversight. This changes the AppSec register:

- AppSec controls must produce audit artifacts that meet OCC examiner standards
- Every change to a system handling cardholder data has evidence requirements
- Third-party / vendor security is subject to FFIEC guidance on outsourcing
- Breach notification is subject to both federal (GLBA, OCC) and state AG requirements

**Translation for your HM screen:** When you say "GRC library with 37 documents mapped to NIST 800-53," that lands differently with Amex than it would at a pure software company. You're speaking a language that maps directly to what their OCC examiners want to see.

---

## 3. TRIS — Amex's Cybersecurity Program

**Full name:** Technology Risk and Information Security
**Abbreviation:** TRIS (use this term, not "SecOps" or "InfoSec")

**Structure (from public 10-K disclosures + security press):**
TRIS is one of the cybersecurity functions within Technology at Amex. Three pillars:
1. **Architecture** — designs the secure-by-default patterns used across the enterprise
2. **Engineering** — builds and maintains security controls (this is where an AppSec Engineer contract sits)
3. **Operations & Assurance** — runs the SIEM, IR, assurance reviews

**CISO:** Gleb Reznik, who took over in October 2025 after Fred Gibbins retired from a 13-year run. Reznik previously led security architecture functions at Amex before promotion to CISO. This is a fresh-leadership context — means priorities are being re-set, investment lines are being re-drawn.

**Reporting line:** CISO → CIO (not CFO, not CRO). Briefs Board, Enterprise Risk Committee, and Operational Risk Committee at least annually.

---

## 4. CRI Profile — Amex's Framework Choice

**Full name:** Cyber Risk Institute Profile

Amex explicitly references the CRI Profile in its 10-K as the cybersecurity maturity framework. Not NIST CSF (though CRI is an extension of CSF specifically designed for the financial sector).

**Why CRI Profile specifically:**
- Published by the Cyber Risk Institute (CRI), a financial services trade group (BPI, SIFMA, and others)
- Extends NIST CSF with 60+ controls specifically relevant to financial institutions
- Maps to BSA/AML, PCI DSS, OCC cybersecurity examiner guidance, SOX, GLBA
- Designed to reduce duplicative compliance work across regulators

**Interview use:**
- Saying "I align controls to CRI Profile" lands harder than "I align to NIST CSF"
- When asked about a framework you'd use, say CRI Profile FIRST, then mention NIST CSF as the foundational layer
- Example: "For the app security control mapping, CRI Profile is the register. It extends CSF with financial-services-specific detail that makes the audit story cleaner."

---

## 5. Amex Public Tech Stack (what you can credibly reference)

**Cloud:** Hybrid — VMware on-prem bridged to Google Kubernetes Engine (GKE). Also runs a custom internal K8s platform for specific workloads.

**Languages:** Go heavy for payments and rewards microservices. One of the largest commercial WebAssembly (Wasm) deployments — used for internal FaaS.

**Service mesh:** Istio (confirmed through Amex engineering blog posts and conference talks)

**Frontend:** Micro-frontend architecture built on React / Next.js

**SAST / DAST / SCA:** Not publicly confirmed. Based on GKE + Go heavy stack + typical bank-sector patterns, educated guess is GitHub Advanced Security (GHAS) + Snyk or equivalent. Be ready to discuss Snyk, Veracode, Checkmarx, Semgrep, GHAS fluently without claiming specific Amex deployment.

**SIEM:** Not publicly confirmed. Peer banks run Splunk ES or Microsoft Sentinel. Assume Splunk is plausible.

**WAF:** Akamai and Cloudflare both historically served amex.com edge traffic.

**EDR:** Likely CrowdStrike Falcon — dominant in Fortune 50 financial services.

**What to do with this info:**
- Reference the Go + Istio + GKE stack to signal you've done homework
- Don't claim deep hands-on with any specific Amex-internal tool
- Use "from what's publicly documented" when citing the stack

---

## 6. The 2024 Third-Party Breach (the interview topic)

**What happened:** In March 2024, a merchant processor vendor (not Amex itself) was breached. Amex card numbers, expirations, and names for a subset of cardholders were exposed.

**Key facts:**
- Amex internal systems were NOT breached
- The vendor breach affected multiple card networks, not just Amex
- State AG notifications triggered (Massachusetts notified approximately 1,300 residents)
- No public OCC or CFPB enforcement action followed
- Amex provided credit monitoring and fraud alerts to affected cardholders

**Why it matters for your interview:**
- Supply chain / vendor AppSec is the HIGHEST-WEIGHTED topic right now at Amex
- The JD's emphasis on CI/CD security gates, SBOM, DevSecOps maps directly to the controls that reduce this class of risk
- SOC 2 Type 2 vendor review, SBOM generation with Syft, vendor SDLC attestation, third-party dependency scanning — these are the specific controls you should speak fluently about

**How to talk about it:**
- Do NOT lead with it — let the HM bring it up
- If they do reference "the 2024 incident" or "vendor risk": acknowledge awareness from public reporting, do not name specific numbers
- Pivot to the control framework: "The 2024 merchant processor incident showed why supply chain AppSec has to be as rigorous as perimeter AppSec. I'd focus on SBOM discipline, vendor SDLC attestation, SCA on every dependency, and SOC 2 Type 2 vendor review as a continuous control, not a quarterly check."
- Do not claim you could have prevented what happened at a third party

---

## 7. Amex Phoenix Office (Desert Ridge Campus)

**Address:** 18850 N 56th Street, Phoenix AZ 85054
**Campus size:** 94 acres
**Buildings:** Two 190,000 sq ft office buildings + a 182,000 sq ft Central Services building
**Status:** Largest Amex campus outside NYC HQ. Currently being expanded (Amex announced Phoenix expansion in 2023-2024).
**Functions housed:** Technology, Customer Service, Risk, Global Business Financing, Cybersecurity
**Employee count (estimated):** 7,000-9,000

This is a real tech hub, not a back-office. TRIS has significant Phoenix presence. The AppSec Engineer contract you'd work would be in one of these buildings, likely in a shared open-floor plan with the broader TRIS Engineering team.

**Phoenix security community:**
- OWASP Phoenix (active chapter with regular meetings)
- ISC2 Phoenix Chapter
- ISSA Phoenix
- AZ Infosec
- Sonoran Desert Security Users Group (SDSUG)

**2026 Phoenix security conferences (useful for rapport / forward-looking questions):**
- SecureWorld Phoenix (May 28, 2026)
- AZ Tech Council Cybersecurity Summit (May 20, 2026 at GCU)
- AZ Technology Summit (Aug 26, 2026)

---

## 8. Amex Culture — Blue Box Values (memorize verbatim)

**The Four Values:**
1. **Deliver for Customers**
2. **Make It Great**
3. **Do What's Right**
4. **Win as a Team**

**Amex HM interviews score candidates against these four values.** This isn't a soft culture reference — it's the actual rubric. Weave one into every behavioral answer.

**Example pairings:**
- Deliver for Customers → when you tell the Texaco POS skimmer story (customer was the cardholder whose data you protected)
- Make It Great → when you tell the Falco 200 → 12 tuning story (went from noise to signal, ownership of quality)
- Do What's Right → when you tell the Texaco patching story (pushed back on "technically compliant" toward actual security)
- Win as a Team → when you tell the GRC library story (cross-functional with legal, HR, engineering)

**Additional Amex cultural signals:**
- Glassdoor rating: 4.1 / 5 (strong for a Fortune 50)
- Work-life balance rating: 4.4 / 5 (notably high for a financial services firm)
- Glassdoor summary: "Premium brand, high standards, good benefits, strong culture, sometimes slow decision velocity"

---

## 9. The CISO Reznik Transition (fresh-leadership context)

**Fred Gibbins** was CISO for 13 years (roughly 2012-2025). He retired in October 2025. Under Gibbins, TRIS built out its current three-pillar structure and established the CRI Profile alignment.

**Gleb Reznik** took over in October 2025. His prior role was at Amex in a security architecture capacity — he knows the internal program intimately.

**What this means for your interview:**
- TRIS priorities are being re-set under new leadership (fresh org, likely rebuilding priorities)
- Specific investment lines may shift — AI security is likely one of the areas getting fresh scrutiny
- Contract roles bring flexibility into an org that's recalibrating — you're a good hire during a transition because you can adapt to emerging priorities without legacy baggage

**If the HM references Reznik:** acknowledge context from public reporting, express interest in the direction, don't over-speculate on what his agenda is.

---

## 10. Key Links and Sources

- **Amex corporate:** [americanexpress.com](https://www.americanexpress.com)
- **Amex 10-K annual report:** available via [SEC EDGAR](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000004962)
- **CRI Profile:** [cyberriskinstitute.org](https://cyberriskinstitute.org/)
- **Experis (ManpowerGroup):** [experis.com](https://www.experis.com/)
- **Phoenix Desert Ridge Campus details:** Amex internal press releases + Phoenix Business Journal coverage
- **OCC regulatory framework for banks:** [occ.gov](https://www.occ.gov/)
- **Your submitted resume archive:** `/Users/et/cyber-squire-ops/CoreDirective/career/amex-experis/Emmanuel_Tigoue_Amex_submitted_2026-04-21.docx`
