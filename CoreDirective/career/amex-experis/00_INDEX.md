# Amex via Experis — AppSec Engineer Contract — Prep Index

**Status as of 2026-04-21:** Resume submitted to Amex by Darren Ingram at $55/hr W2. Awaiting HM screen invitation (expected within 5-7 business days = April 28–30).
**Role:** Application Security Engineer (Contract through 12/31/2026 + long-term extension)
**Location:** Phoenix AZ 85054 (Desert Ridge Campus, 18850 N 56th St). Amex Flex: 3 days onsite typical for AppSec.
**Compensation submitted:** $55/hr W2 (JD listed $60-65; difference is Experis margin 20-25%)
**Recruiter:** Darren Ingram, Principal Recruiter at Experis / ManpowerGroup

**Submitted resume archived:** `/Users/et/cyber-squire-ops/CoreDirective/career/amex-experis/Emmanuel_Tigoue_Amex_submitted_2026-04-21.docx`

---

## The Non-Negotiables (memorize cold)

### Red Thread
**"DevSecOps engineer with a shift-left discipline. Secure development, not just testing — and governance that holds up to an OCC auditor."**

Amex is regulated by the OCC via American Express National Bank (AENB). This line tells them you understand that.

### Identity
"Emmanuel Tigoue. Application Security Engineer at CoreDirective."

**For Amex specifically, lead with "Application Security Engineer" over "AI Security Engineer"** — the JD title is AppSec, the client brief was AppSec, and Darren submitted you as AppSec. Keep the AI Security work as your differentiator, not your identity.

### Top 3 Metrics
- **80%+ SOAR triage reduction** (AI-driven automation at CoreDirective)
- **200 Falco events → 12 actionable** (detection engineering precision/recall)
- **Zero exposed ports** via Cloudflare Zero Trust tunnels + mTLS
- Plus: **37 GRC documents** authored, NIST 800-53-mapped

### Amex Blue Box Values (memorize verbatim — HM scores against these)
1. **Deliver for Customers**
2. **Make It Great**
3. **Do What's Right**
4. **Win as a Team**

Weave one into every STAR answer.

### Key Amex Facts
- **CEO:** Stephen J. Squeri
- **CISO:** Gleb Reznik (took over Oct 2025 after Fred Gibbins retired — 13-year run)
- **Security program name:** TRIS (Technology Risk and Information Security) — not SecOps or InfoSec
- **Maturity framework:** CRI Profile (Cyber Risk Institute Profile) — not generic NIST CSF
- **Tech stack (public):** GKE + Istio + Go for payments/rewards microservices. WebAssembly for internal FaaS. React/Next.js micro-frontends. Akamai + Cloudflare WAF.
- **Live risk:** 2024 third-party merchant processor breach. State AG notifications but no OCC enforcement. Supply chain / vendor AppSec is the highest-weighted topic right now.

---

## Document Map

| # | File | When to Read | Core Use |
|---|------|--------------|----------|
| 01 | `01_COMPANY_INTEL.md` | Pre-HM screen | Amex corporate intel: regulatory context (OCC, AENB), TRIS structure, CRI Profile, 2024 breach, Phoenix office, CISO Reznik background |
| 02 | `02_ROLE_FIT.md` | Pre-HM screen | JD line-by-line mapped to your evidence. Language gap (Go/Java/C#) honest handling. Phoenix relocation answer |
| 03 | `03_TECHNICAL_PREP.md` | Pre-HM screen | AppSec-specific Q&A: STRIDE on payment flows, OWASP Top 10 + PCI DSS, OAuth/JWT pitfalls, Burp methodology, DevSecOps pipeline |
| 04 | `04_HM_SCREEN.md` | Pre-HM screen + day-of | 20 likely Amex HM questions with model answers. Blue Box Values woven in. Close sequence. Post-call email template. |
| 05 | `05_QUESTIONS_FOR_THEM.md` | Pre-HM screen | Questions for Amex HM and panel. Amex-specific (TRIS, CRI Profile, 2024 breach lessons). |
| 06 | `06_MASTER_FRAMING.md` | Pre-HM screen first | 30s / 60s / 2min pitches. Language gap reframe (Go/Java/C#). Phoenix answer. Why-Amex answer. |

---

## Why This Prep Is Leaner Than OneDigital and NICE

HM screen is not scheduled yet. You'll get 5-7 business days of lead time after the invite comes. This folder gives you the skeleton; when the HM invite lands, you'll do targeted deepening based on:
- Who the HM is (name, LinkedIn, background)
- Whether the HM is TRIS engineering or TRIS operations side
- What specific AppSec focus area the HM prioritizes

The Client Summary Darren sent to Amex is your baseline positioning. Read it again in `/Users/et/cyber-squire-ops/CoreDirective/career/amex-experis/Emmanuel_Tigoue_Amex_submitted_2026-04-21.md` — everything you've been submitted as, Amex is reading.

---

## Three Critical Flags (from the submitted resume)

### Flag 1 — Phoenix location vs Atlanta resume header

The submitted resume lists Atlanta as your location. The role is Phoenix onsite 3 days/week. HM will ask about relocation intent.

**Your answer:** "Open to relocating to Phoenix for this role. I've been tracking the Phoenix security community — OWASP Phoenix, ISC2 Phoenix Chapter, the Desert Ridge campus context. I can relocate with reasonable notice, and my cost-of-living analysis shows Phoenix is roughly 2% cheaper overall, with the state tax differential putting $3,300/year more in my pocket than staying in Georgia."

### Flag 2 — Professional Summary section (violates your resume rule)

Your normal resumes omit the summary/objective. This submitted version has BOTH a Professional Summary AND Darren's Client Summary. Darren likely added or restored the Professional Summary when he received your resume.

**Not a problem for Amex** — they expect summaries. Flag: do not let this version propagate to other submissions where your rule applies.

### Flag 3 — Language stack gap

JD asks Go, Java, Python, or C#. Your submitted resume lists Python, Bash, HCL, SQL. Match is Python only.

**Your answer if probed:** "Primary production language is Python. I can read and modify Go — Amex's public tech stack (GKE, Istio, Go microservices) is well-documented, and I'd pair with a senior Go engineer the first 2-3 weeks. Java and C# are ramp-up; not in production use today. If the role requires deep Go or Java fluency from day one, that's a gap I'd want to know about before offer."

---

## Key Metrics HM Will Probe (all from your submitted resume)

Memorize the backstory on each. Do not soften or hedge under questioning.

| Metric | Backstory |
|--------|-----------|
| 80%+ SOAR triage reduction | n8n orchestrator with NeMo-sandboxed workloads + Ollama + Claude API; measured Jan–Mar 2026 at CoreDirective |
| 200 Falco events/day → 12 actionable | eBPF rule tuning + Falcosidekick → Datadog routing; 15 working days of daily tuning cycles |
| 8h → 90min IR containment | Texaco 6-step IR runbook applied to POS skimmer incident |
| 48h → <4h MTTD | Splunk correlation rules across 3 Texaco retail locations |
| 14 → 2 critical audit findings | AD Group Policy baselines + least-privilege admin + credential rotation (Texaco PCI) |
| 12 hrs/week recovered | Python + PowerShell automation at Texaco (patch deployment, user provisioning, reporting) |
| Zero exposed ports | Cloudflare Zero Trust tunnels + mTLS at CoreDirective |
| 8 OPA/Rego policies + 16 Terraform files + 30+ resources | IaC at CoreDirective |
| 37 GRC documents | NIST 800-53 SSP, POA&M (37 findings), 10 policies, 5 IR playbooks, risk assessment, tabletop |

---

## Index Card (write down, keep visible during call)

```
RED THREAD: DevSecOps engineer. Shift-left. Governance that holds
           up to an OCC auditor.

IDENTITY: Application Security Engineer at CoreDirective.

BLUE BOX VALUES (weave one in every STAR):
  Deliver for Customers
  Make It Great
  Do What's Right
  Win as a Team

AMEX CONTEXT:
  CEO: Stephen J. Squeri
  CISO: Gleb Reznik (Oct 2025)
  Program: TRIS (not "SecOps")
  Framework: CRI Profile (not generic NIST CSF)
  Stack: GKE + Istio + Go + Wasm

TOP METRICS:
  80%+ SOAR triage reduction
  Falco 200/day -> 12 actionable
  Zero exposed ports (Cloudflare Zero Trust + mTLS)
  37 GRC documents (800-53 SSP + AI Governance)

3 QUESTIONS FOR HM:
  1. Highest-weighted risk on TRIS roadmap this year?
  2. How does AppSec interface with the Go + Istio engineering teams?
  3. What's the success metric at 90 days for someone in this seat?

COMP: $55/hr submitted. Push for $60 after panel pass.
     Do not renegotiate inside HM screen.

FLAGS:
  Phoenix: ready to relocate with reasonable notice
  Summary: keep Darren's version for Amex submission only
  Language: Python primary, can read Go, ramp on Java/C#

CLOSE: "Is there anything in what I've shared that
      leaves you uncertain?"
```

---

## Never Say

- "Pivoting" / "transitioning" / "aspiring" / "bridging"
- "My startup" — say "my employer CoreDirective"
- "Passionate" / "rockstar" / "ninja" / "fast learner"
- "I can do Go" — you can read Go; say exactly that
- "SecOps" when referring to Amex's security team — they call it TRIS
- "NIST CSF" when CRI Profile is the register — Amex specifies CRI Profile in 10-Ks
- Claim to have deep offensive/pentest credentials you don't have (OSWE, GPEN, GXPN)
- Lead with May 2026 graduation
- Em dashes in any written follow-up

---

## The Standard

Every answer: 45-90 seconds. PSC format. Specific numbers. Named tools.
Every STAR: weave one Blue Box Value.
Every gap: honest + reframe + ramp + foundational skill.
Every question for HM: couldn't have been Googled.

**Amex values candor + professionalism + regulatory discipline. Be the candidate who acts like they already work there — measured, precise, prepared.**
