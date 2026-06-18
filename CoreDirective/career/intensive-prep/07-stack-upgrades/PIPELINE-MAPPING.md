# Pipeline Mapping: Stack Upgrades and STAR Stories Per Active Role

**Frame.** Every role in the active pipeline gets the same treatment: top three stack upgrades that map best to the JD, top three STAR stories to lead with. Order in each list reflects where you should spend prep time, not where you should drop it in casually.

**Stories referenced.** See `STAR-STORIES.md` for the canonical 12.
**Upgrades referenced.** See `ROADMAP.md` for the full A-J set.

---

## Dropzone AI — Senior Security Engineer (Investigation Quality)

**Role anchor.** Investigation quality on an AI SOC analyst. Python codebase. Director of Engineering interview.
**Comp.** $175K-$217K + equity. Take-home submitted 2026-04-21, recruiter screen passed.
**Lead thesis.** "Investigation quality is what I do. I've done it as a human, I've built systems for it, and I want to ship it at scale."

**Top 3 stack upgrades to lead with.**
1. **Upgrade J. LangGraph triage agent on Falco** — direct mirror of Dropzone's product. Demo video is the close. Their AI SOC analyst triages alerts; yours does the same on real Falco signal.
2. **Upgrade A. Promptfoo CI gate** — answers "how do you keep an AI investigation honest" in CI, not in vibes. Eval harness language is exactly what Eric Hammerle's team uses.
3. **Upgrade G. Real-time prompt-injection classifier** — AI-on-the-defense story. Latency budget under 200ms, precision number on a held-out set, public PR curve. Same investigation-quality discipline applied to AI inputs.

**Top 3 STAR stories to lead with.**
1. **Story 2. OpenClaw AI Gateway Red Team** — strongest single asset. OWASP LLM Top 10, eight DAST categories, zero injection findings, eval harness in CI. Lead here when Eric asks about hardest technical problem or AI quality.
2. **Story 1. POS Skimmer Investigation at Texaco** — the human investigator anchor. Customer report, Wireshark, 90-minute containment. Lead here if Eric asks about an incident you ran end to end.
3. **Story 9. Failing Forward (n8n Switch v3 / database divergence)** — code-level depth. Says "I am a real engineer who reads source and goes to the database when the docs lie." This is the engineer-test story.

---

## Resilience — N8N Engineer (Sr.)

**Role anchor.** n8n engineering with security overlay. Interview 2026-04-09 already done; this section is for any callbacks or pipeline restarts.
**Lead thesis.** "I run 14 active n8n workflows in production with a master orchestrator covering 16 service actions, all OPA-gated and Falco-monitored."

**Top 3 stack upgrades to lead with.**
1. **Upgrade B. NeMo Guardrails at the n8n LLM boundary** — direct relevance. n8n is their stack and yours. Wrap every LLM call with a rails proxy. Strongest in-context demo.
2. **Upgrade A. Promptfoo CI gate** — ties n8n workflow changes to AI safety regression tests. They will respect the CI gate framing.
3. **Upgrade D. Falco rules tuned for agentic abuse** — detection on n8n containers exec'ing into shells, n8n outbound calls outside the allowlist. n8n-specific rule examples carry weight here.

**Top 3 STAR stories to lead with.**
1. **Story 1. Building the n8n SOAR Stack as a One-Person SOC** — 14 workflows, 13 services, 48 dollars a month. Direct mirror of their job.
2. **Story 9. Failing Forward (n8n Switch v3 bug)** — n8n internals, workflow_entity vs workflow_history database divergence. Says you've debugged the platform at the source level.
3. **Story 8. CARL Rule System and Agentic Safety** — agent envelope as version-controlled rules. Pairs with their n8n + AI angle.

---

## Insight Global — AI Security Engineer (1yr Remote Contract)

**Role anchor.** MS Security Copilot + Defender for Cloud gap, end client redacted. Recruiter Savannah Daoust.
**Lead thesis.** "I run AI security in production at CoreDirective. Microsoft stack is a vocabulary translation, not a learning curve."

**Top 3 stack upgrades to lead with.**
1. **Upgrade J. LangGraph triage agent** — directly equivalent to Security Copilot agent work. Demo video shows you've already shipped the pattern.
2. **Upgrade F. AI Bill of Materials** — answers "how do you maintain inventory of AI assets" which is a Defender for Cloud question reframed.
3. **Upgrade A. Promptfoo CI gate** — eval harness for any AI deployment, transferable across vendors including Microsoft.

**Top 3 STAR stories to lead with.**
1. **Story 2. OpenClaw AI Gateway Red Team** — the AI security story that proves you've done the work. Map onto whatever vendor stack they describe.
2. **Story 4. Writing the GRC Corpus With AI Governance Policy** — policy work transfers across stacks. NIST AI RMF is universal.
3. **Story 11. Cross-Functional Decision (AI Governance with the accounting client)** — this role is contract; recruiter wants to know you can land in someone else's stack and operate at the policy level. This story shows you do.

---

## WBD — Cybersec Engineer (AI Focused), Job 34698-1, Milestone Tech

**Role anchor.** $85/hr W2, 6mo, hybrid 3d ATL. Submittal package ready.
**Lead thesis.** "I do AI-focused cybersec with a real production stack. ATL onsite is a feature, not a bug."

**Top 3 stack upgrades to lead with.**
1. **Upgrade A. Promptfoo CI gate** — every team building with AI wants a regression gate. Universal currency.
2. **Upgrade D. Falco rules tuned for agentic abuse** — detection engineering on AI workloads, public artifact, mappable to whatever WBD's stack actually is.
3. **Upgrade I. Coverage matrix (deferred)** — if they push on SOC2 alignment in the screen, mention this is in your roadmap; do not promise it before week 3.

**Top 3 STAR stories to lead with.**
1. **Story 2. OpenClaw AI Gateway Red Team** — AI focus is in the JD title. Lead here.
2. **Story 7. OPA Policies for Terraform IaC** — policy-as-code is universal, especially in a media company with regulated data flows.
3. **Story 12. Build vs Buy on the SOAR Layer** — contract roles want to see judgment under cost constraint, fast.

---

## Brilliant Cloudflare (Candescent) — via Matthew Morgan

**Role anchor.** $85/hr W2, 6mo, Sandy Springs 1d onsite. Recruiter screen passed, awaiting HM round.
**Lead thesis.** "I run Cloudflare in production for tigouetheory.com and the cd-alpha tunnel. I've shipped a build plan to add Pro + Load Balancing."

**Top 3 stack upgrades to lead with.**
1. **Upgrade H. Chainguard / Wolfi base images** — supply chain story for any AppSec-leaning role. Pairs with your Trivy + Cosign + SBOM existing pipeline.
2. **Upgrade B. NeMo Guardrails (or any defensive ingress story)** — defensive ingress is the Cloudflare mindset. The rails proxy applies directly.
3. **Upgrade D. Falco agentic rules** — detection on the host side. Cloudflare engineers respect host-level eBPF visibility.

**Top 3 STAR stories to lead with.**
1. **Story 5. Hardening Cloudflare Tunnel and Teleport for Zero Trust** — direct relevance to Cloudflare engineering. Lead here.
2. **Story 6. OWASP ZAP DAST and Header Remediation** — Cloudflare edge headers, real fix, IaC migration. Tells the operations story they care about.
3. **Story 7. OPA Policies for Terraform IaC** — IaC discipline is what AppSec engineering managers screen for at this tier.

**Note.** See `candescent-cloudflare-build-plan-2026-04-29.md` in memory for the 9-step Cloudflare build plan. Cap demo tool spend at 2% of contract value per `feedback_paid_tools_for_interview_demos.md`.

---

## QGenda — Mid-Level Security Engineer

**Role anchor.** $115K base + 10% + benefits, remote, AWS + HIPAA, healthcare SaaS owned by Hearst. Recruiter Austin Nix.
**Lead thesis.** "Healthcare SaaS, HIPAA, AWS Security: I do this exact work plus I run my own GRC corpus with privacy controls."

**Top 3 stack upgrades to lead with.**
1. **Upgrade F. AI Bill of Materials** — HIPAA-adjacent inventory discipline. AI-BOM as evidence of inventory thinking generalizes to PHI inventory.
2. **Upgrade A. Promptfoo CI gate** — even at mid-level, the regression-gate framing earns trust.
3. **Upgrade I. Coverage matrix** (deferred to month 2) — if asked about SOC2 / HIPAA mapping, name it as roadmap, do not promise before delivery.

**Top 3 STAR stories to lead with.**
1. **Story 4. Writing the GRC Corpus With AI Governance Policy** — they will read this as the privacy and policy story. NIST and AI RMF map cleanly to HIPAA Privacy Rule.
2. **Story 5. Hardening Cloudflare Tunnel and Teleport for Zero Trust** — IAM and JIT discipline is what HIPAA-regulated environments grade on.
3. **Story 7. OPA Policies for Terraform IaC** — preventing misconfigurations is the most common HIPAA breach class. Direct relevance.

**Note.** Mid-level title, so do not lead with the senior-tier "I run a 13-service stack" framing. Lead with "I do AWS + HIPAA-adjacent work in production at CoreDirective" and let the depth show in the STAR stories.

---

## Amex Experis — AppSec contract via Darren Ingram

**Role anchor.** $55/hr Phoenix, CISO Reznik, TRIS program. Payment flow threat model prep.
**Lead thesis.** "Payment flow threat modeling is exactly what I did at Texaco at three retail sites. I do it now in version control."

**Top 3 stack upgrades to lead with.**
1. **Upgrade H. Chainguard base images** — supply chain hygiene matters for AppSec contractors. One-day ship.
2. **Upgrade A. Promptfoo CI gate** — AppSec is shifting toward AI-touched code. CI gate framing applies.
3. **Upgrade D. Falco rules tuned for agentic abuse** — host-level detection complements AppSec.

**Top 3 STAR stories to lead with.**
1. **Story 1. POS Skimmer Investigation at Texaco** — real payment-flow threat-modeling proof. Same domain as TRIS.
2. **Story 3. Threat Modeling the Entire CoreDirective Engine** — STRIDE + ATLAS, real artifact in the GRC corpus.
3. **Story 6. OWASP ZAP DAST and Header Remediation** — DAST is AppSec daily bread.

**Note.** $55/hr is the rate; lead with depth, not seniority claims. Per `feedback_no_employment_type_in_replies.md`, never volunteer W2 framing.

---

## OneDigital — AI Security Engineer via FTS Zac Bennett

**Role anchor.** Snyk, Salt, CrowdStrike AIDR, Qualys, Zero Trust, AI threat modeling. AI security is the JD.
**Lead thesis.** "AI threat modeling is what I do. The vendor stack is a translation; the discipline is the same."

**Top 3 stack upgrades to lead with.**
1. **Upgrade J. LangGraph triage agent** — AIDR-equivalent. Demo video is the close. Highest leverage in the pipeline for this role.
2. **Upgrade G. Real-time prompt-injection classifier** — AI threat modeling made tangible with a real classifier and a real PR curve.
3. **Upgrade F. AI Bill of Materials** — inventory and Qualys-adjacent thinking. One-day ship.

**Top 3 STAR stories to lead with.**
1. **Story 2. OpenClaw AI Gateway Red Team** — AI threat modeling, red-teaming, eval harness. Lead here.
2. **Story 3. Threat Modeling the Entire CoreDirective Engine** — STRIDE + ATLAS at the system level, not a checkbox.
3. **Story 5. Hardening Cloudflare Tunnel and Teleport for Zero Trust** — direct relevance to the Zero Trust line in the JD.

---

## Pipeline-wide priority

**If you can only finish three upgrades in the next 14 days, ship Upgrade A, Upgrade J, and Upgrade D in that order.**

- **A. Promptfoo CI gate.** Earns trust with every interviewer in the pipeline. Two days. Public repo.
- **J. LangGraph triage agent.** Highest single-asset value for Dropzone AI, OneDigital, Resilience, Insight Global. Demo video is a closer. Three days.
- **D. Falco agentic rules.** Public detection-engineering portfolio you don't have yet. Two days.

**Total: 7 days of build, 7 days of buffer for the heavier upgrades (G, F) and rest. See `WEEK1-EXECUTE.md`.**
