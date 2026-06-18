# Amex — Master Framing

---

## The Red Thread

**"DevSecOps engineer with shift-left discipline. Secure development, not just testing. Governance that holds up to an OCC examiner."**

Deliver this line at least once in the HM screen. Anchors you in the DevSecOps category Amex is hiring for, and signals regulatory fluency without lecturing.

---

## Core Identity Paragraph

"I'm an Application Security Engineer at CoreDirective. I run the shift-left CI/CD pipeline, the infrastructure as code, the runtime detection, the vendor review process, and the governance documentation. For an Amex AppSec contract, the tools and scale differ — but the discipline is what I do day-to-day."

---

## Three Pitches

### 30-Second Pitch (elevator)

"Emmanuel Tigoue, Application Security Engineer at CoreDirective in Atlanta. DevSecOps — shift-left CI/CD with Trivy, Semgrep, Gitleaks, OPA gates. Zero exposed ports via Cloudflare Zero Trust + mTLS. Authored 37 GRC documents mapped to NIST 800-53. Previously ran IT Security at Texaco, including the PCI DSS program. Georgia State BBA in Cybersecurity, CISSP in progress."

### 60-Second Pitch (HM opener)

See `04_HM_SCREEN.md` — already written. Memorize. Voice-memo x3.

### 2-Minute Pitch (full panel walkthrough)

"I'm an Application Security Engineer at CoreDirective, about seven months in. My role is DevSecOps end-to-end. I built the shift-left pipeline — Trivy for container SAST and SCA, Semgrep for custom-rule SAST, Gitleaks for secrets detection, OPA policy gates for deployment compliance, Cosign for image signing, Syft for SBOM generation. Every pull request goes through the full gate set. OWASP ZAP runs authenticated DAST against production services and verified zero injection vulnerabilities across eight OWASP attack categories.

On the infrastructure side, I eliminated every exposed public port by routing traffic through Cloudflare Zero Trust tunnels with mTLS certificate authentication. Zero inbound ports confirmed by external scan. Infrastructure-as-code across 16 Terraform files managing 30-plus resources on DigitalOcean and Cloudflare, with 8 OPA/Rego policies blocking non-compliant deployments.

On the runtime side, I tuned Falco eBPF from 200 alerts per day to 12 actionable findings, routing criticals to Datadog via Falcosidekick. I built an n8n SOAR that cut routine triage overhead by 80 percent using NVIDIA NeMo-sandboxed workloads for sensitive data, with every automated action idempotent and audit-logged.

On the governance side, I authored 37 GRC documents anchored to NIST 800-53 Rev 5 — a full System Security Plan, a Plan of Action and Milestones tracking 37 findings, ten security policies, five IR playbooks including one for third-party breach response, a risk assessment, a tabletop exercise.

Before CoreDirective, nearly four years at Texaco in IT Security and Operations. Three retail locations under me. Built the Splunk SIEM that cut MTTD from 48 hours to under 4. Wrote the 6-step IR runbook that reduced containment time from 8 hours to 90 minutes. Ran the PCI DSS program that dropped critical audit findings from 14 to 2 over 8 months. Segmented a flat network into 4 VLANs, validated with Nmap, killed lateral movement risk. Hardened Active Directory with Group Policy baselines and least-privilege admin. Built Python and PowerShell automation that recovered 12 hours a week of operational overhead.

I'm finishing my BBA in Cybersecurity at Georgia State in May. CISSP sitting before end of April. Certs: SecurityX, SSCP, CCNA, Security+. Eligible for security clearance.

I'm here because the Amex AppSec contract maps directly to what I do today — shift-left pipeline, payment flow threat modeling, architecture review, vendor SDLC attestation, and the governance documentation that wraps all of it. The regulatory register — OCC supervision through AENB, CRI Profile alignment instead of generic NIST CSF — is context I'd bring working discipline to from day one."

---

## JD Mirror Language (weave into answers)

| JD Phrase | Use In Your Answer |
|-----------|-------------------|
| "Security-Minded Developer" | "I think like a developer first — I write production code and I red-team my own work." |
| "shift-left" | "...shift-left discipline — security controls on the pull request, not after the deploy..." |
| "pen-testing tools" | Acknowledge without overclaiming: "Burp for intercept and repeater, OWASP ZAP for authenticated DAST, Nmap for network validation." |
| "remediation paths" | "Prioritize by reachability plus exploitability plus impact, not just CVSS." |
| "secure-by-design patterns" | "Threat modeling before code, STRIDE on every new architecture, secure defaults in the infrastructure-as-code layer." |
| "third-party" / "supply chain" | "Vendor SDLC review, SOC 2 Type 2, SBOM generation, OAuth scope governance" |

---

## The Gap Reframes (memorize cold)

### Gap: "You don't have Go, Java, or C# in production."

"Python is my primary. Go I can read — Amex's public stack of GKE plus Istio plus Go is well-documented enough that navigating code is a week of ramp. Java and C# are longer ramps. For a role where deep Go fluency from day one is required, I'd be a stretch. For a role where secure Python services plus Go readability from day one plus Go fluency by month two is acceptable, I'm a fit."

### Gap: "You don't hold OSWE, GPEN, GXPN, CEH, or CSSLP."

"Cert focus has been breadth-first — SecurityX, SSCP, CCNA, Security+. CISSP is sitting this month. The offensive certs in the preferred list I haven't pursued because my work has been shift-left DevSecOps, not offensive pen-testing as primary. CSSLP is on the path post-CISSP. If the role requires OSWE-level offensive depth, someone else is a better hire. If it's shift-left AppSec with periodic offensive validation, the cert stack I have is sufficient."

### Gap: "You've only been at CoreDirective seven months."

"Density over duration. Seven months at CoreDirective shipped a production AI gateway, shift-left CI/CD pipeline, Zero Trust architecture, a SOAR orchestrator cutting triage by 80 percent, and 37 GRC documents. Prior to that, nearly four years at Texaco with ownership across three retail locations. On a contract with a defined end date, the tenure question is less material than on an FTE."

### Gap: "You haven't worked in financial services before."

"Regulated industry, yes — PCI DSS at Texaco. Financial services specifically, no. What transfers: audit discipline, regulator-facing evidence, control framework mapping. What I'd ramp on: GLBA-specific nuance, OCC examiner expectations beyond what PCI covers, financial-specific threat models like ACH fraud or wire-transfer manipulation. That's a few weeks of ramp given my PCI foundation, not a complete restart."

---

## The Three Anchors (when you drift, come back to these)

1. **"I run the shift-left pipeline end-to-end today."** — production credibility
2. **"37 GRC documents mapped to 800-53."** — governance credibility
3. **"OCC register through AENB. CRI Profile, not generic CSF. Blue Box Values."** — Amex-specific homework credibility

---

## Never Say (absolute rules)

- "SecOps" when referring to Amex's cybersecurity function — they call it TRIS
- "NIST CSF" without also mentioning CRI Profile — Amex specifies CRI in 10-Ks
- "I can do Go" — say "I read Go"
- "Offensive" as primary skill — you're shift-left, not pentester
- "Startup" when referring to CoreDirective — say "my employer"
- "Pivoting" / "transitioning" / "aspiring" / "bridging"
- "Passionate" / "rockstar" / "ninja" / "fast learner"
- "Just" as in "it's just shift-left" — minimizes your work
- Em dashes in any written follow-up
- Specific dollar amounts from other pipeline conversations
- Any claim to have prevented the 2024 breach
- Lead with May 2026 graduation — engineer first, student second

---

## The Atmosphere Read

**Amex HM likely register:**
- Professional, measured, audit-style questioning
- Expects candidates to reference frameworks by name (CRI Profile, 800-53, OWASP Top 10, PCI DSS v4)
- Values documentation + evidence discipline
- Will likely score you against Blue Box Values without telling you they're doing it
- May be in a rush — TRIS is hiring aggressively post-Reznik transition
- Phoenix-based HMs tend to be direct, less politics than NYC Amex roles
- Expect panel-round follow-up within 1-2 weeks if HM screen goes well

**Mirror their register:** measured, framework-literate, concrete. Don't over-perform. Don't monologue. Pause before answering. Take the time seriously but not reverently.

---

## One-Line Gut Check Before the Call

"I run this today. The tools are different names. The discipline is constant. I'm honest about my gaps and confident about my evidence. That's what gets me through."
