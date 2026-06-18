# OneDigital — Master Framing

One paragraph, three pitches, and the mirror language for Pavel's JD. Everything you say should land back on one of these frames.

---

## The One-Paragraph Core (memorize this verbatim)

"I'm an AI Security Engineer. I run production AI security today — the gateway, the guardrails, the CI/CD, the runtime detection, the IR playbooks, and the GRC library that wraps it all. OneDigital's stack uses different vendor names for the same categories, and I'll be fluent on the specific tools inside a week. What I bring on day one is the pattern recognition and the control framework — prompt injection looks the same whether you're defending a Claude gateway or a ChatGPT Enterprise tenant, and SOC 2 Type 2 vendor review is the same discipline whether the vendor is a SaaS chatbot or a CRM integration."

---

## The Red Thread (say this in some form every round)

**"AI security is governance plus operations. If you do one without the other, you fail an audit or you fail an incident. I do both."**

This line lives behind every answer. It positions you as the rare hire who speaks engineering AND control framework.

---

## Three Pitches (practice all three aloud)

### 30-Second Pitch (for handshakes, small talk, elevator)

"I'm Emmanuel Tigoue, AI Security Engineer at CoreDirective in Atlanta. I run production AI security — hardening our Claude Opus gateway, shift-left CI/CD, Zero Trust architecture — and I authored our 37-document GRC library from scratch. Before CoreDirective I ran IT Security at Texaco for four years. Georgia State BBA in cybersecurity, CISSP in progress, and I stream technical content weekly under the CoreDirective brand."

### 60-Second Pitch (for the HM screen opener)

[Use the version in `05_HM_SCREEN.md` — already formatted]

### 2-Minute Pitch (for the panel round if you get there)

"I'm an AI Security Engineer at CoreDirective in Atlanta, about seven months in. My role is end-to-end — I built and run the production AI stack, which means the Claude Opus gateway (red teamed against OWASP LLM Top 10 and MITRE ATLAS), the NeMo-sandboxed local inference for sensitive workflows, the Cloudflare Zero Trust architecture with mTLS that eliminated every exposed port, and the shift-left CI/CD that runs Trivy, Semgrep, Gitleaks, and OPA policy gates on every pull request.

On the detection side, I tuned Falco eBPF from 200 alerts a day to 12 actionable findings with Falcosidekick routing to Datadog. I built the n8n SOAR that cut our routine triage by 80 percent using NeMo sandboxed workloads for sensitive data, Ollama for low-sensitivity classification, and Claude API for context. Every automated action is idempotent with rollback and audit logging.

On the governance side, I authored 37 GRC documents anchored to NIST 800-53 Rev 5: a full SSP, a POA&M tracking 37 findings, ten security policies including an AI Governance policy aligned to NIST AI RMF and ISO 42001, five IR playbooks including one for AI-specific incidents, a risk assessment, and a documented tabletop exercise.

Before CoreDirective I ran IT Security and Operations at Texaco in Atlanta for almost four years. I built the Splunk SIEM that cut MTTD from 48 hours to under 4, authored the six-step IR runbook that reduced containment time from 8 hours to 90 minutes, and ran the PCI DSS program that dropped critical audit findings from 14 to 2. Segmented a flat network into four VLANs, validated with Nmap, killed lateral movement risk.

I'm finishing my BBA in Cybersecurity at Georgia State in May. CISSP sitting before end of April. Certs: SecurityX, SSCP, CCNA, Security+. Eligible for security clearance.

I'm here because the OneDigital role lands at the intersection where I already work — AI-specific threat modeling, Zero Trust architecture, shift-left AppSec, SaaS vendor review, and the governance documentation that makes all of it defensible. The specific tools in the JD — Snyk, Salt, CrowdStrike AIDR, Qualys, Entra — are different vendor names for categories I own today. The learning curve on the products is days. The foundational capability you need on day one is what I do now."

---

## JD Mirror Language (weave these into your answers)

Pavel wrote or approved the JD. Reflecting its exact phrases back signals comprehension without over-reading.

| JD Phrase | Use In Your Answer |
|-----------|-------------------|
| "secure adoption of artificial intelligence" | "...supporting the secure adoption of AI across the enterprise..." |
| "Zero Trust architecture" | "...integrated with Zero Trust architecture principles..." |
| "identity-first security principles" | "...identity-first, meaning authentication and authorization gate every request..." |
| "shift-left" | "...I run shift-left AppSec with SAST, SCA, and DAST on every PR..." |
| "prompt injection and data poisoning" | "...prompt injection, data poisoning, and the adjacent risks from OWASP LLM Top 10..." |
| "human factors" | "...the human factors piece — how employees actually interact with AI in their daily workflow..." |
| "stringent compliance requirements, including SOC 2 Type 2" | "...vendor review against SOC 2 Type 2 trust services criteria..." |
| "tabletop exercises" | "...I've documented and run tabletop exercises, including one scoped specifically to AI incidents..." |
| "CIS Top 18 Controls" | "...aligned to CIS 18, mapped through 800-53 in our current GRC library..." |

---

## The Gap Reframes (know these cold)

When Pavel probes a specific tool or capability you don't have direct experience with, the reframe structure is always:

1. Acknowledge the gap honestly (one sentence, no hedging)
2. Name the peer tool or capability you have used
3. State the ramp time
4. Close with the foundational skill that doesn't require the specific tool

**Template:**

"I haven't run [Tool X] hands-on. At CoreDirective I've used [Peer Tool] for the same purpose — [specific thing]. The UX and rule set differ, the underlying discipline is identical. I'd expect about [a week / a few days] of ramp on the product, because I already understand [category]. The capability you need from day one — [foundational skill] — is what I've been doing."

**Specific reframes:**

### Snyk
Gap: Don't use Snyk. Peer: Semgrep + Trivy + Gitleaks. Ramp: days. Foundational: shift-left AppSec discipline.

### Salt Security
Gap: Don't use Salt. Peer: Cloudflare API gateway + manual API inventory from Terraform. Ramp: days. Foundational: API security + OAuth scope governance + anomaly detection thinking.

### CrowdStrike AIDR
Gap: New product, no hands-on. Peer: Falco eBPF + Datadog routing. Ramp: days. Foundational: detection engineering + alert tuning.

### Qualys
Gap: Don't use Qualys. Peer: Nessus at Texaco + Trivy at CoreDirective. Ramp: days. Foundational: vulnerability management + prioritization + remediation coordination.

### Microsoft Entra ID
Gap: Don't use Entra directly. Peer: Keycloak SSO + Teleport PAM + Cloudflare Zero Trust. Ramp: a week for Conditional Access policies specifically. Foundational: Zero Trust identity, PRMFA, JIT access, least privilege.

### CIS Top 18 (as framework)
Gap: GRC library maps to 800-53 not CIS 18 directly. Peer: 800-53 Rev 5 family-level coverage. Ramp: the 18 controls map cleanly to 800-53 families. Foundational: control framework thinking.

---

## The Three Anchors (when you lose your footing, come back to these)

1. **"I've built this end-to-end at CoreDirective."** — production credibility
2. **"I authored 37 GRC documents."** — governance credibility
3. **"I've been in the Atlanta security community through Texaco and CoreDirective."** — local credibility

If a question goes sideways, one of these three anchors gets you back to solid ground.

---

## Things to Never Say (absolute rules)

- "Pivoting" / "transitioning" / "aspiring" / "bridging"
- "My startup" — say "my employer CoreDirective" or "where I work"
- "I'm passionate about" / "rockstar" / "ninja" / "fast learner"
- Lead with May 2026 graduation — you are an engineer first
- Em dashes in writing (you already know)
- "I haven't done that" as a full sentence — always follow with the reframe template above
- The exact phrase "Onex owns OneDigital" — outdated as of Dec 2025
- "Salesloft" or "Drift" by name unless Pavel raises them first
- Any specific number on the 28,414 breach figure unless Pavel brings it up
- Claim to have prevented a breach you weren't involved in

---

## The Atmosphere Read

Pavel's likely operating temperature:
- Calm, measured, audit-style questioning
- Prefers you pause and think before answering, over quick+shallow responses
- May write notes during your answers — that's normal, not a bad sign
- Will likely give you a full 30 minutes of attention (HM screens at OneDigital average this per Glassdoor)
- Tommy Hauser organized the meeting, so Pavel didn't have to do scheduling — means he's focused on content

**Mirror his energy:** measured, specific, structured. Don't over-perform. Don't monologue. Pause. Ask clarifying questions when his are vague. Take the 30 minutes seriously but don't treat it like a tribunal.
