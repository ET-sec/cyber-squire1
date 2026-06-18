# OneDigital AI Security Engineer — Role Fit Analysis

Every JD line mapped to your real evidence. Gaps named honestly with a reframe strategy. When Pavel probes, you respond from this document.

---

## The One-Paragraph Mirror (deliver if asked "walk me through your fit")

"I've been running production AI security at CoreDirective for about seven months. My day-to-day is hardening a Claude Opus gateway against OWASP LLM Top 10 and MITRE ATLAS, plus shift-left CI/CD with Trivy, Semgrep, Gitleaks, and OPA on every pull request. I route everything through Cloudflare Zero Trust with mTLS, which means zero exposed ports. I've tuned Falco eBPF runtime detection from 200 alerts a day to 12 actionable, and built the n8n SOAR that cut our routine triage by 80% using NeMo-sandboxed models. On the governance side, I authored 37 GRC documents from scratch, including an SSP mapped to 800-53 and five IR playbooks. The OneDigital role maps directly to that work — the tooling is different vendor to vendor, but the problems are identical."

---

## JD Responsibility → Your Evidence

### 1. AI Architecture and Zero Trust Integration (Entra ID, PRMFA)

**JD says:** *"Design and enforce security guardrails for AI applications, ensuring all systems integrate seamlessly with our identity management frameworks, including Microsoft Entra ID and Phishing-Resistant Multi-Factor Authentication (PRMFA)."*

**Your evidence:**
- OpenClaw AI gateway (Claude Opus 4 + NeMo sandboxed local inference) running with identity-first access controls
- All traffic through Cloudflare Zero Trust tunnels with mTLS certificate authentication. This is the Zero Trust principle applied in practice.
- Keycloak SSO with RBAC centralizes identity; Teleport PAM provides JIT access with session recording. Standing admin privileges eliminated.

**Acknowledge-and-bridge line for Entra ID:** "I've implemented the same Zero Trust patterns with Keycloak and Teleport — federation, conditional access, JIT privileged access, PRMFA equivalents through FIDO2 and WebAuthn. Entra ID is Microsoft's implementation of patterns I already own at the architectural level. I'd expect a ramp-up of a week to get fluent on Conditional Access policies and Entra Workload ID specifics."

**Do not say:** "I don't know Entra." Say: "I've implemented the same patterns in Keycloak. Happy to walk through how I'd map that to Entra Conditional Access."

---

### 2. Application Testing and Code Security (Snyk SAST/SCA, DAST)

**JD says:** *"Lead comprehensive application security testing across the enterprise. Utilize Snyk for Static Application Security Testing (SAST) and Software Composition Analysis (SCA), and conduct Dynamic Application Security Testing (DAST) to identify and remediate vulnerabilities early."*

**Your evidence:**
- Shift-left CI/CD pipeline with Trivy (container SAST), Semgrep (SAST), Gitleaks (secrets detection), OPA policy gates on every PR
- Images signed with Cosign. SBOMs generated with Syft.
- Authenticated DAST assessments with OWASP ZAP against production SOAR. Verified zero injection vulnerabilities across 8 OWASP attack categories. Identified and remediated 4 header misconfigurations same-day via Cloudflare transform rules.

**Snyk reframe:** Semgrep + Trivy + Gitleaks covers the same surface area as Snyk Code + Snyk Container + Snyk Open Source. The UX and rule set differ, the problem is identical. "Trivy and Semgrep are what I run in production. Snyk has a cleaner developer UX and broader commercial rule library — that's a config tool switch, not a skills gap. First week on the job, I'd stand up Snyk against our highest-risk repos and compare findings against what we're catching today."

---

### 3. API Security (Salt Security)

**JD says:** *"Leverage Salt to secure enterprise APIs and data pipelines, ensuring robust discovery, posture management, and threat protection for the systems feeding our AI models and core applications."*

**Your evidence:**
- OpenClaw AI gateway exposes a `/v1/chat/completions` API that I designed, hardened, and monitored. Authentication at the Cloudflare edge with mTLS, rate limiting, request logging, redaction of PII before it hits the model.
- API discovery is effectively done through my infrastructure-as-code inventory (16 Terraform files, 30+ resources). I know every API endpoint in the environment because I wrote the resource definitions.
- API threat protection: OWASP ZAP DAST runs against APIs. Cloudflare WAF on edge. OPA policies block misconfigured deployments.

**Salt reframe:** "Salt automates API discovery + posture + runtime protection. At CoreDirective I do that manually because I own the infrastructure top to bottom. At OneDigital scale — 5,000 employees, 250 offices — that manual approach doesn't work, which is why the tool exists. Salt is a control-plane upgrade, not a different category of work. Ramp is days to fluency on the product, because I understand what it's automating."

**Bonus intel (use if Pavel asks about Salt specifically):** Salt Security is natively integrated with CrowdStrike Falcon via the Foundry app. That matters because OneDigital already runs CrowdStrike — Salt and Falcon share telemetry, so a compromised API and a compromised endpoint surface in the same SIEM pane. This is exactly the kind of detail that shows fluency without over-claiming.

---

### 4. Vulnerability Management (Qualys)

**JD says:** *"Utilize Qualys for continuous vulnerability scanning of the infrastructure hosting our AI tools and broader application environments."*

**Your evidence:**
- At Texaco: quarterly Nessus scans across 45+ devices + payment processor coordination for PCI DSS compliance
- At CoreDirective: Trivy for container vulnerability scanning on every build; Falco for runtime detection of exploited vulnerabilities

**Qualys reframe:** Qualys VMDR is the enterprise category leader for asset discovery + vulnerability scanning + prioritization. Nessus operates in the same space with different UX. At AI workload scale, Qualys Cloud Agents on the hosts running inference workloads give continuous coverage. "I've scoped, run, and remediated from vulnerability scan output at scale. Qualys is learning a new pane of glass, not a new discipline."

---

### 5. Threat Modeling for AI/ML (prompt injection, data poisoning)

**JD says:** *"Conduct rigorous threat modeling for AI and machine learning pipelines. Identify and mitigate risks specific to AI, such as prompt injection and data poisoning, guided by industry frameworks."*

**Your evidence (this is your strongest area):**
- Red teamed all deployed skills against **OWASP Top 10 for LLM Applications** for: prompt injection, system prompt leakage, excessive agency, training data poisoning, model DoS, sensitive information disclosure
- **MITRE ATLAS** threat model applied to the AI gateway
- NeMo sandboxing for untrusted AI workload isolation (NVIDIA's NeMo Guardrails framework)
- 37 GRC documents include an AI Governance policy aligned to **NIST AI RMF** and **ISO/IEC 42001**
- IR playbook for AI-specific incidents (prompt injection exfiltration, jailbreak exploitation, agent misuse)

**This is your strongest section. Lead Pavel here if he asks you to pick what to talk about.**

---

### 6. Detection and Incident Response (CrowdStrike AIDR, tabletop)

**JD says:** *"Monitor and respond to AI-specific threats using CrowdStrike AIDR. Develop playbooks and participate in tabletop exercises designed around AI-driven incidents to improve organizational resilience."*

**Your evidence:**
- Falco eBPF runtime detection tuned from 200 alerts/day to 12 actionable findings. Alerts route to Datadog via Falcosidekick.
- Splunk SIEM deployment at Texaco: MTTD cut from 48 hours to under 4 hours via correlation rules
- 6-step IR runbook at Texaco: containment time reduced from 8 hours to 90 minutes
- 5 IR playbooks authored at CoreDirective including AI Incident playbook
- Tabletop exercise documented in the GRC library

**CrowdStrike AIDR reframe:** AIDR is a new product (CrowdStrike announced it as a dedicated category in 2024-2025). It extends Falcon with AI-specific detection — prompt injection via telemetry, model abuse patterns, AI agent activity monitoring. "I've built the detection discipline with Falco + Datadog, which is the same pattern different engine. AIDR on top of Falcon gives you the integrated story Falco doesn't natively get. Ramping on the product is UX learning. The detection-engineering discipline is already there."

**Tabletop evidence:** "I ran a tabletop at CoreDirective scoped around AI gateway abuse — prompt injection leading to data exfiltration. Three roles: responder, attacker, exec comms. Documented the full playbook in our IR library. That pattern ports directly to OneDigital's AI adoption scenarios."

---

### 7. Human-Centric Security Focus (AI awareness, AI-generated phishing)

**JD says:** *"Collaborate with security awareness teams to evaluate how employees interact with AI. Develop strategies to mitigate risks related to over-reliance on AI outputs and AI-generated phishing attacks."*

**Your evidence:**
- At Texaco: deployed LLM-powered analysis for automated phishing detection and incident prioritization across 3 retail locations
- At CoreDirective: IR playbook specifically handles AI-generated social engineering (deepfake voice calls, LLM-crafted spear phishing)
- GRC library includes AI Governance policy addressing employee use of generative AI tools (prompt hygiene, PII handling, output verification)

**Reframe this as the most underrated part of AI security:** "The technical controls are the easier half. The harder half is getting 5,000 people to not paste client PII into ChatGPT, or to verify a Claude answer before acting on it. The JD calling this out tells me Pavel and the team already see that. At CoreDirective I wrote the policy that tells employees how to use AI safely, and the IR playbook that assumes they will mess it up anyway."

---

### 8. SaaS and Vendor Security (SOC 2 Type 2)

**JD says:** *"Evaluate the security posture of third-party AI applications and SaaS platforms. Ensure external tools meet our stringent compliance requirements, including SOC 2 Type 2 standards."*

**Your evidence:**
- 37 GRC documents include vendor risk management policy
- SSP maps 800-53 controls to third-party service providers
- Cloudflare Zero Trust + mTLS means third-party services integrate through a Zero Trust boundary, not a perimeter VPN
- Experience reviewing vendor SOC 2 Type 2 reports (mapping to controls, reviewing exceptions, checking subservice organizations, confirming reporting period)

**This is where you can reference the 2025 breach without naming it as a OneDigital event.** The Salesloft / Drift OAuth compromise is a canonical example of why SOC 2 Type 2 review + ongoing OAuth scope governance + anomaly monitoring on API exports matters. See `01_COMPANY_INTEL.md` section 5 for the full breach timeline and industry-recommended remediations. Memorize those seven controls before Thursday.

---

## Required Qualifications — Evidence Check

| JD Requirement | Your Match | Gap Handling |
|----------------|------------|--------------|
| BS or advanced degree in CS / InfoSec | BBA in Computer Information Systems (Cybersecurity), Georgia State University, May 2026, GPA 3.7, Dean's List | Strong |
| App security with AI/ML/LLM focus | OpenClaw AI gateway hardened against OWASP LLM Top 10 + MITRE ATLAS + ISO 42001 | Strongest point |
| Qualys, Salt, CrowdStrike AIDR, Snyk hands-on | Semgrep, Trivy, Gitleaks, Falco, Nessus; not hands-on on the specific four products | See reframes above — peer-tool fluency + product UX ramp |
| SAST / DAST / SCA | Trivy + Semgrep (SAST/SCA), OWASP ZAP (DAST), Gitleaks (secrets) | Strong, different vendors |
| Zero Trust + enterprise SSO | Cloudflare Zero Trust + mTLS; Keycloak SSO | Strong — Keycloak not Entra, same patterns |
| CIS Top 18 alignment | 37 GRC docs mapped to 800-53; familiarity with CIS Controls as a peer framework | Acknowledge CIS 18 is the operational framework OneDigital uses; your foundation is 800-53, same ground |
| Translate security to executive + technical audiences | 3 executive summary documents in GRC library; weekly content streaming (Threat Brief LIVE, The Build LIVE) | Strong |

---

## Preferred Attributes

**Background in human factors in cybersecurity:**
- You wrote the IR playbook that assumes humans will click the wrong link
- AI-generated phishing IR playbook explicitly addresses cognitive bias exploitation
- Content engine (Threat Brief LIVE) translates technical topics for non-technical audience — direct human factors application

**ISACA, ISC2, or mentorship community participation:**
- **ISC2 eligibility:** SSCP holder, CISSP in progress
- **ISACA:** Pavel holds CISA (ISACA cert). Atlanta ISACA Chapter has 2,800+ members. You are not a member yet — but if Pavel asks if you're active in ISACA, you can honestly say "I'm planning to join the Atlanta chapter this year, especially since CISSP in progress will open up joint ISACA/ISC2 event attendance. What events do you attend?" That's an honest answer that also opens a rapport opportunity.
- **Mentorship:** CoreDirective content engine (Gumroad study systems, Skool community, YouTube long-form briefings) is public mentorship for the cybersecurity community. Real work, verifiable.

---

## The Core Narrative to Drive

**"I'm an AI Security Engineer. I run production AI security today, including the gateway, the guardrails, the CI/CD, the runtime detection, the IR playbooks, and the GRC that wraps it. OneDigital's stack uses different vendor names for the same categories, and I'll be fluent on the specific tools inside a week. What I bring day one is the pattern recognition and the control framework — prompt injection looks the same whether you're defending a Claude gateway or a ChatGPT Enterprise tenant, and SOC 2 Type 2 vendor review is the same discipline whether it's a SaaS chatbot or a Salesforce integration."**

Every answer should land back on some piece of that paragraph.
