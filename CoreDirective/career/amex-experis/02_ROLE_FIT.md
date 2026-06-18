# Amex AppSec Contract — Role Fit + Gap Handling

---

## The One-Paragraph Mirror

"I'm an Application Security Engineer at CoreDirective. My day-to-day is shift-left AppSec — Trivy, Semgrep, Gitleaks, OPA policy gates on every PR, plus Cosign for image signing and Syft for SBOM. I run OWASP ZAP DAST against our production SOAR and verified zero injection vulnerabilities across 8 OWASP attack categories. I hardened a production Claude Opus AI gateway against OWASP LLM Top 10 and MITRE ATLAS. On the governance side, I authored 37 GRC documents mapped to NIST 800-53, including an IR playbook for third-party incidents. For the Amex AppSec contract, the tooling names differ but the disciplines match."

---

## JD Responsibility → Your Evidence

### "Design and implement secure application features using Go, Java, Python, or C#"

**Your evidence:**
- Python: primary production language at CoreDirective (AI gateway, SOAR orchestration, QC agents, build tools)
- Bash + PowerShell: Texaco automation (12 hrs/week recovered)
- HCL / Terraform: 16 files, 30+ resources, 8 OPA/Rego policies
- SQL: data work across PostgreSQL + analytics

**Honest gap:** Go, Java, C# not in production use. Can read Go (Amex stack is public); Java and C# are ramp-up time.

**Reframe:** "Primary production code is Python. I read Go well enough to navigate the GKE + Istio services stack. Java and C# are ramp-up time — not in my production rotation currently. If the role requires deep Go or Java fluency from day one, I'd want to know before offer. If it's 'can you write secure Python services while ramping on Go,' I'm day-one productive."

### "Perform deep-dive penetration testing on web applications and APIs using Burp Suite, Kali Linux, and Metasploit"

**Your evidence:**
- OWASP ZAP: authenticated DAST against production SOAR, zero injection vulns across 8 OWASP attack categories
- Burp Suite: proficiency at intercept, repeater, intruder — not at the level of a CTF player or OSCP holder
- Nmap: Texaco VLAN segmentation validation (network pen-test discipline)
- Kali Linux, Metasploit: familiar with the toolset, not primary in my current workflow

**Honest reframe:** "Full-spectrum offensive tooling isn't my daily work — I skew DevSecOps-side. Burp and ZAP fluent; Metasploit and Kali workshop-level. For a role where offensive pen-testing is primary, someone with OSWE or GXPN is a better hire. For shift-left AppSec with periodic offensive validation, I'm a fit."

### "Identify and prioritize vulnerabilities; work directly with engineering teams to define remediation paths and reproduce issues"

**Your evidence:**
- Falco tuning 200→12: precision/recall discipline applied to runtime findings
- POA&M tracking 37 findings across 4 assessment sources at CoreDirective
- Texaco Group Policy audit remediation: 14 → 2 critical findings in 8 months
- Trivy SBOM + Syft container analysis: dependency-level remediation coordination

**Strong fit.**

### "Integrate automated security scanning and security gates into modern CI/CD pipelines"

**Your evidence:**
- Trivy (container SAST + SCA) on every PR
- Semgrep (custom-rule SAST) on every PR
- Gitleaks (secrets detection) on every PR
- OPA policy gates block non-compliant deployments
- Cosign for image signing, Syft for SBOM generation
- GitHub Actions pipeline orchestration

**Strongest fit in the JD. Lead here.**

### "Partner with developers to review code and architectures for security weaknesses, recommending secure-by-design patterns"

**Your evidence:**
- 6 threat modeling documents using STRIDE in the GRC library
- Architecture review as part of new skill onboarding at CoreDirective
- Red team review pre-production on every AI skill deployed
- Public content (Threat Brief LIVE, The Build LIVE) trains clear technical communication

**Strong fit.**

---

## Required Skills Coverage Matrix

| JD Requirement | Your Match | Notes |
|---------------|------------|-------|
| BS CS / IT | BBA Computer Information Systems (Cybersecurity), Georgia State, May 2026 | Strong match |
| Production code in Go/Java/Python/C# | Python primary; can read Go | Language gap — see reframe above |
| Burp + Kali + Nmap + Sqlmap + Metasploit | Burp + ZAP + Nmap fluent; Metasploit/Kali workshop-level | Partial; lean DevSecOps over pure offense |
| Docker / container environments | Trivy + Cosign + Syft + Docker daily; GKE/K8s via research + CoreDirective | Strong |
| CI/CD security integration | Trivy/Semgrep/Gitleaks/OPA on every PR | Strongest match |

---

## Preferred Certifications — Honest Position

**JD lists:** OSWE, GPEN, GWAT, GXPN, CEH, CSSLP

**You hold:** SecurityX (CASP+), SSCP, CCNA, Security+. CISSP in progress (sitting before end of April 2026).

**Gap:** No offensive certs. No CSSLP (Certified Secure Software Lifecycle Professional — ISC2).

**Reframe:** "Certifications I hold are breadth-first — SecurityX, SSCP, CCNA, Security+. CISSP is sitting this month. The offensive certs in your preferred list (OSWE, GXPN, GPEN) I don't hold — haven't invested there because my work is shift-left DevSecOps, not offensive pen-testing as primary. CSSLP is closer to my lane; it's on my radar post-CISSP."

---

## The Phoenix Relocation Answer

**If asked about Phoenix onsite cadence:**

"Open to relocating for this role. I've done cost-of-living math — Phoenix is roughly 2-3% cheaper than Atlanta overall. The Arizona 2.5% flat state tax versus Georgia's 5.39% means about $3,300 more in my take-home per year, which offsets some of the relocation cost. I've been tracking the Phoenix security community — OWASP Phoenix, ISC2 Phoenix Chapter, the Sonoran Desert Security Users Group. Reasonable notice for relocation is 4-6 weeks from offer accept. If the role requires someone in Phoenix earlier, I'd want to know that up front."

**If they press on why Phoenix specifically:**

"Honestly — the role is what drew me, not the geography. But Phoenix itself has strong assets: the Desert Ridge campus is a real tech hub, not a back-office, and the security community there is active. It's a legitimate career move, not a compromise."

---

## The "Why Amex" Answer

**Memorize this. Every Amex interview asks it.**

"Three reasons. One, Amex is a premium brand operating a closed-loop network — which means the business model and the data custody relationship with customers are tighter than open-loop competitors like Visa and Mastercard. That tighter control makes AppSec work consequential. Two, the regulatory context — OCC supervision through AENB means the audit discipline is real, and the AppSec controls I build produce evidence that holds up under examiner review. I'd rather work in an environment where controls matter than one where they're theater. Three, TRIS under Gleb Reznik is fresh leadership — priorities are being re-set and there's investment going into the cybersecurity function. Joining at this moment means the work has upward trajectory, not maintenance trajectory."

**Why this answer works:**
- References the closed-loop business model (tests that you understand Amex)
- Cites the regulatory register (OCC / AENB) — signals banking-sector fluency
- Names CISO Reznik by name + transition context — signals recent homework
- Doesn't rely on generic "great company" / "prestigious brand"

---

## The "Why Contract Instead of FTE" Answer

**If asked:**

"Contracts are specific. A contract role is defined by a clear scope and timeline — for this one, through December 2026 plus long-term extension potential. That clarity is attractive when I'm looking for depth on a mission-critical function rather than breadth across a full platform. The Right-to-Hire clause means if Amex and I align after ramp, the conversion path exists. If we don't, the role still delivers defined value."

**Do not:**
- Say "I'm flexible" (sounds mercenary)
- Say "Contract is the only option available" (sounds desperate)
- Dismiss the FTE vs contract distinction

---

## The "Tenure at CoreDirective" Question

**If HM raises that you've been at CoreDirective for only 7 months:**

"True. Prior to that, nearly four years at Texaco in IT Security and Operations — managed across three retail locations, ran the PCI program, built the Splunk SIEM, wrote the IR runbook. CoreDirective has been concentrated AI Security work — seven months to ship a production AI gateway, build the shift-left CI/CD pipeline, author 37 GRC documents, and build a SOAR orchestrator. Density over duration. On a contract with a defined end date, the tenure question is also less material."

---

## The Bridge Paragraph (use when a single summary is requested)

"AppSec Engineer at CoreDirective with a DevSecOps focus. Shift-left pipeline (Trivy, Semgrep, Gitleaks, OPA) on every PR. Zero exposed ports via Cloudflare Zero Trust + mTLS. Falco runtime detection tuned from 200 to 12 actionable alerts. Authored 37 GRC docs mapped to NIST 800-53 including AI Governance and an IR playbook for third-party incidents. For an Amex AppSec contract in Phoenix — DevSecOps, vendor SDLC review, payment flow threat modeling, and shift-left integration with the Go + Istio + GKE stack — the discipline ports directly. The vendor-specific tools (their SAST, their SIEM, their ticketing) are days of ramp, not weeks."
