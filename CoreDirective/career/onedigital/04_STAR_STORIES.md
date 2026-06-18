# OneDigital STAR Stories — Pavel Adapted

10 behavioral stories. Each in STAR (Situation, Task, Action, Result) with PSC delivery discipline (Problem, Specifics, Consequence) for 60-90 second verbal answers.

**Pavel is CISA.** Emphasize: control discipline, evidence, documentation, stakeholder communication, process rigor. De-emphasize: pure offense, raw exploit dev.

---

## Story 1 — Authoring 37 GRC Documents from Scratch

**This is your strongest Pavel story. Lead with it when you have a choice.**

### Situation
CoreDirective had no formal GRC program when I joined in September 2025. Infrastructure was running — AI gateway, SOAR, Kubernetes on DigitalOcean — but there was no SSP, no POA&M, no written policies, no IR playbook. For a company handling AI governance services and client data, that gap was material.

### Task
Build a full GRC library from zero in a timeframe that matched the company's posture — meaning done in months, not years.

### Action
I took the NIST 800-53 Rev 5 control catalog and walked it against our actual environment. For each applicable control family, I drafted: a policy, a procedure, and an evidence artifact. Documents I produced:

- **System Security Plan (SSP)** with 800-53 controls mapped to implementation details
- **POA&M** tracking 37 findings across 4 assessment sources (internal review, Trivy scans, Semgrep findings, audit observations)
- **10 security policies**: Access Control, Acceptable Use, AI Governance, Data Classification, Incident Response, Encryption, Vendor Risk, Remote Work, Logging and Monitoring, Change Management
- **5 IR playbooks**: Ransomware, Insider Threat, Data Exfiltration, AI Incident (prompt injection / agent abuse), Third-Party Breach
- **Risk Assessment** using NIST 800-30 methodology
- **Tabletop Exercise** for AI incident response with documented after-action report
- **6 threat modeling documents** — STRIDE applied to the major architecture components
- **3 executive summaries** translating the technical posture for non-technical readers

All documents cross-referenced. POA&M items tie to specific controls in the SSP. Policies reference procedures that reference evidence artifacts.

### Result
37 documents, fully indexed, sanitized for public sharing. CISSP-aligned. The library is my Rosetta Stone between the technical work I do daily and the governance language auditors + boards + clients speak. When someone asks "how do you handle third-party risk," I don't describe it — I hand them the policy + the vendor risk register + the SOC 2 review template.

**PSC compression for 60 seconds:**
- **P:** CoreDirective had the engineering, not the paper trail. Not defensible.
- **S:** I authored 37 GRC docs in about two months, NIST 800-53-mapped, with an SSP, POA&M tracking 37 findings, 10 policies including AI Governance, 5 IR playbooks including one for AI incidents, and a documented tabletop.
- **C:** The engineering work is now defensible to an auditor, a board, or a client. For a CISA-led team at OneDigital, that's the discipline I'd bring day one.

---

## Story 2 — OpenClaw AI Gateway Red Team

### Situation
CoreDirective deploys Claude Opus 4 and NeMo-sandboxed local models through a custom AI gateway called OpenClaw. Gateway exposes APIs to internal skills and automated workflows. Before production launch, I had to confirm the gateway wasn't exploitable.

### Task
Red team the gateway and every deployed skill against OWASP LLM Top 10 and MITRE ATLAS. Remediate findings before go-live.

### Action
Systematic test plan, one LLM vulnerability at a time:

- **Prompt injection (direct):** drafted adversarial prompts across all skills, checked for unintended tool activation, privilege escalation via role-play
- **Prompt injection (indirect):** planted instructions in documents the skills would retrieve, tested whether the model followed them
- **Jailbreak:** DAN-style, multi-turn priming, encoding-based bypasses
- **System prompt leakage:** probed every skill with prompts designed to exfiltrate instructions
- **Excessive agency:** reviewed tool permission scopes per skill; several were overbroad
- **Training data poisoning:** not applicable (using API-served models)
- **Model DoS / cost attack:** confirmed rate limits at the gateway
- **Sensitive information disclosure:** tested prompts for PII leakage from context windows
- **Insecure output handling:** confirmed downstream consumers sanitized model outputs
- **Supply chain:** pinned Claude API SDK versions, SBOM via Syft, verified image signatures

Findings documented, severity-scored, remediated in order. High-severity findings blocked go-live until fixed. The exercise got encoded as a recurring practice — every new skill gets red-teamed before production per the AI Governance policy.

### Result
Every deployed skill passed a documented security review. No finding rated above medium shipped to production. The red-team discipline is now standard practice, not an ad-hoc event. An auditor can see: what was tested, what failed, what was fixed, who signed off.

**PSC (60 sec):**
- **P:** OpenClaw's production launch needed defensible proof it wasn't exploitable.
- **S:** I red teamed against OWASP LLM Top 10 plus MITRE ATLAS, categorized findings by severity, blocked go-live on anything above medium, and embedded the practice into our AI Governance policy.
- **C:** The gateway shipped with documented, defensible AI-specific security controls — exactly the pattern the OneDigital role calls for.

---

## Story 3 — Falco Alert Tuning: 200 Events per Day to 12 Actionable

### Situation
We deployed Falco eBPF runtime detection on the CoreDirective Kubernetes cluster. First week after turn-up: 200 alerts per day flowing into Datadog. No one could triage that. Alert fatigue was immediate and obvious.

### Task
Get the signal-to-noise ratio to something humans could actually respond to.

### Action
Three-week tuning cycle with a data discipline. Each day:
1. Bucket the previous day's alerts by rule that fired
2. For each rule firing more than 5 times, inspect the trigger pattern — legitimate workload vs actual concern
3. Adjust the rule with an exception for legitimate workload, or disable the rule if the signal was false-positive by design
4. Document the decision — what I changed, why, and what would cause it to need revisit

Key patterns I identified: system maintenance cron jobs firing "read sensitive file" rules, container image pulls triggering "write below binary dir," network probe traffic triggering "unexpected network connection" in ways that mapped to legitimate Kubernetes controller activity.

Over 15 working days: the 200-per-day rate fell. Not because I suppressed noise, but because I separated signal from noise and documented the separation.

### Result
12 actionable alerts per day. Every alert is now investigated. Falcosidekick routes criticals to Datadog dashboards with runbook links. The tuning documentation serves as an audit artifact — an auditor can see which rules are active, which are exception-tuned, and why.

The meta-lesson: detection engineering is precision/recall on operational events. Too noisy and you lose trust. Too quiet and you miss real incidents. Tuning is the daily discipline, not a one-time project.

**PSC (60 sec):**
- **P:** 200 Falco alerts a day meant real alerts were getting lost in noise.
- **S:** Three-week daily tuning cycle. Each alert bucket reviewed, rule-by-rule exception logic added with documented reasoning, false positives by design disabled.
- **C:** 12 actionable alerts per day. Every alert investigated. Documented for audit. This is the detection engineering rigor I'd apply to CrowdStrike Falcon + AIDR at OneDigital.

---

## Story 4 — POS Skimmer Incident Response at Texaco

### Situation
At Texaco (Atlanta retail location), a routine Splunk alert flagged unusual network traffic from a payment terminal. Timestamp matched an overnight shift with no authorized service activity.

### Task
Determine if it was a skimmer, contain the blast radius if real, preserve evidence for law enforcement.

### Action
Followed the IR runbook I'd written the prior quarter. Six steps:
1. **Detect** — Splunk alert, cross-referenced to payment traffic volume baseline
2. **Triage** — Wireshark packet capture on the POS network segment, identified outbound connections to an IP not in our processor allowlist
3. **Contain** — isolated the affected terminal via VLAN switch-port disable, preserved the physical hardware chain of custody
4. **Eradicate** — confirmed a hardware skimmer physically attached to the terminal; coordinated with law enforcement for evidence collection
5. **Recover** — replaced the terminal with a sealed unit from secure storage, re-tested payment flow end-to-end
6. **Lessons learned** — tightened outbound firewall rules on the POS VLAN, added periodic physical tamper inspections to the shift checklist

Throughout: every decision captured in an incident record. Post-incident review with district management. Report submitted to the payment processor per PCI DSS vendor breach notification.

### Result
Containment from initial alert to isolated terminal: 90 minutes — versus the pre-runbook benchmark of 8 hours. No cardholder data loss confirmed by the payment processor's forensic review. No PCI DSS compliance action. Insurance claim resolved cleanly because the incident record met evidentiary standards.

**Why this story matters for Pavel:** IR with documented runbook + evidence discipline + regulatory compliance path. That is CISA auditor heaven. You're not just fast — you're structured.

---

## Story 5 — n8n SOAR Build: 80 Percent Triage Reduction

### Situation
CoreDirective handled security triage manually through my direct Slack and email inbox. Credential rotations, compliance monitoring checks, incident escalations — all manual, all taking hours per week of my time that should have been going to higher-leverage work.

### Task
Automate the repetitive triage layer without introducing new security risk.

### Action
Built an n8n SOAR with three layers:

1. **Detection integration:** webhooks from Datadog, Falco, Trivy, Gitleaks, Semgrep. Each triggers on specific finding thresholds.
2. **AI triage layer:** NVIDIA NeMo sandboxed local inference for sensitive data (because sending alerts to Claude API with plaintext PII or secrets is not OK). Ollama running locally for low-sensitivity classification. Claude API via the OpenClaw gateway for non-sensitive contextual analysis and summary.
3. **Action layer:** each finding gets routed — auto-remediate (Cloudflare transform rule push for misconfigs, Terraform apply for drift), auto-ticket (GitHub issues or GRC library POA&M entries), or escalate to human (Telegram alert with pre-summarized context).

Safety: all automated actions are idempotent + have defined rollback + are logged for audit trail. No automation can take production-impacting action without a documented playbook approval.

### Result
Routine triage overhead cut by 80 percent — credential rotation checks, compliance drift monitoring, minor incident escalation no longer require my direct attention unless they pattern-deviate. Documented as a capability in the AI Governance policy: "automated security operations with NeMo-sandboxed AI workloads and audit-preserved action logs."

**PSC (60 sec):**
- **P:** Manual triage was eating hours per week that should've gone to governance and architecture.
- **S:** n8n SOAR layering NeMo-sandboxed local inference for sensitive triage, Ollama for low-sensitivity classification, Claude API for context, all with idempotent actions and audit logging.
- **C:** 80 percent reduction in routine triage. The automation is documented, auditable, and has defined rollback — not a black box.

---

## Story 6 — Zero Trust Tunnel Migration (eliminating exposed ports)

### Situation
CoreDirective infrastructure previously had SSH exposed on the public internet for administrative access. Despite firewall rules and key-based auth, that's an unnecessary attack surface.

### Task
Eliminate every publicly reachable port while maintaining operator access.

### Action
Rearchitected to Cloudflare Zero Trust tunnels. Every service that needed remote access got a tunnel route (n8n dashboard, SSH to the droplet, future services). Operator access routes through a Cloudflare Zero Trust identity check (Entra-style Conditional Access) plus mTLS certificate validation at the tunnel terminator.

Two tunnels in production: `n8n.tigouetheory.com` → localhost 5678, `ssh.tigouetheory.com` → localhost 22. No other inbound ports exposed. All egress through Cloudflare. DNS + certificate management automated.

### Result
Zero exposed ports on the production droplet. External port scan confirms 0 open inbound. Administrative access is identity-gated + cert-gated + tunnel-gated. Audit artifact: Terraform-defined tunnel configuration, logged authentication events, signed certificates.

**Pavel hook:** This maps directly to the Zero Trust architecture responsibility in the JD. "You're not just protecting applications — you're eliminating the ways attackers reach them."

---

## Story 7 — AI Governance Policy Authoring

### Situation
Generative AI tools were landing inside CoreDirective workflows daily — new LLMs, new chatbots, new Claude-powered assistants. Without a governance frame, every adoption decision was ad-hoc and the risk posture was invisible.

### Task
Write the AI Governance policy that defines how CoreDirective adopts, monitors, and retires AI tools — anchored to recognized frameworks.

### Action
Policy structure:

1. **Scope** — all AI systems handling CoreDirective or client data, directly or indirectly
2. **Anchoring frameworks** — NIST AI RMF (Govern/Map/Measure/Manage), ISO/IEC 42001, OWASP LLM Top 10, MITRE ATLAS
3. **Adoption criteria** — risk tier (low/medium/high based on data classification), required controls at each tier, required approvals
4. **Runtime controls** — logging requirements, sensitive-data redaction at prompt construction, output verification requirements, rate limiting
5. **Third-party AI controls** — SOC 2 Type 2 review, DPA + BAA requirements by data type, data retention opt-outs, training-data opt-outs
6. **Incident response** — named AI incident playbook, red team requirements pre-launch, tabletop cadence
7. **Retirement** — sunset process for AI tools, data deletion evidence, audit record retention

Reviewed by me as security owner, signed off by me as AI Governance lead.

### Result
Every new AI tool adoption goes through this policy. Refusals and approvals have documented reasoning. The policy is a living document — updated quarterly against NIST AI RMF and 42001 evolution. For a CISA-led interview, this is the artifact that proves "AI security" means governance + operations, not just red team.

---

## Story 8 — Texaco VLAN Segmentation (flat to tiered network)

### Situation
Texaco Atlanta retail: flat L2 network. POS, back-office systems, guest Wi-Fi, and management all shared the same broadcast domain. Lateral movement risk was the textbook attack path.

### Task
Segment the network to contain lateral movement, validate the segmentation, maintain operations during migration.

### Action
Designed 4 VLANs: POS payment (isolated, egress only to payment processor), back-office (ERP, store ops), guest Wi-Fi (internet only, client isolation), management (admin + logging). Rolled out one VLAN per weekend window. Validated with Nmap scans from each VLAN to confirm only permitted paths worked.

### Result
Lateral movement risk reduced to near zero — validated by Nmap. PCI DSS scope shrunk to only the POS VLAN, simplifying audit. No operational disruption during the migration window. Network diagram in the compliance evidence package.

---

## Story 9 — PCI DSS Compliance Program Ownership at Texaco

### Situation
Inherited a fragmented PCI DSS posture: vulnerability management was quarterly Nessus scans run by a managed vendor, network segmentation was mostly conceptual, SAQ documentation was two years stale.

### Task
Take the PCI program to a defensible, audit-ready state.

### Action
- Updated network segmentation (see Story 8)
- Moved Nessus scans in-house for tighter control; monthly authenticated scans; 30-day critical patch SLA
- Rewrote SAQ documentation to match current environment
- Coordinated directly with payment processor on compliance attestation
- Hardened AD with Group Policy baselines, stale account removal, least-privilege admin, automated credential rotation

### Result
Critical audit findings dropped from 14 to 2 over 8 months. SAQ documentation approved on first submission. PCI compliance sustained across three retail locations. Payment processor gave a written clean attestation.

**Framing for Pavel:** regulated industry experience. OneDigital Investment Advisors LLC is under SEC Safeguards Rule + GLBA — financial services compliance discipline is the cousin of PCI discipline. "Regulated environment, auditor-facing, controls-driven" is a vocabulary I speak.

---

## Story 10 — Accounting AI Incident Tabletop

### Situation
CoreDirective deployed an AI-assisted accounting workflow — generative AI drafting invoice categorizations, expense reconciliations, vendor communications. Without a tabletop, the team didn't know how it would respond to abuse or malfunction.

### Task
Run a tabletop exercise scoped to plausible AI incidents in the accounting flow. Document the playbook.

### Action
Designed a scenario: attacker uses indirect prompt injection via a maliciously crafted vendor invoice. The LLM, tasked with categorizing and summarizing invoice data, follows embedded instructions and emails a summary containing confidential client data to an external address.

Roles: Incident Commander, Responder, Attacker, Communications. Played through detection (what signals would we see), containment (shut down the workflow, preserve logs), eradication (remove the injected invoice from the queue), recovery (validate no other invoices contaminated), and post-incident (update the AI Governance policy, add DLP controls to outbound email from the workflow, require human approval on outbound client communication).

### Result
AI Incident IR playbook updated with the scenario-derived controls. Documented tabletop report added to the GRC evidence package. Team went from "we haven't thought about this" to "we have a tested playbook." Exercise scheduled on a quarterly cadence.

**Pavel hook:** Tabletop is explicitly called out in the JD. You've done it. With a documented after-action.

---

## Story-to-Question Mapping

When Pavel asks — lead with the story in the right column.

| Question Pattern | Best Story |
|------------------|-----------|
| "Tell me about yourself" | Not a story — use the 90-sec pitch from `07_MASTER_FRAMING.md` |
| "Walk me through a time you owned GRC" | Story 1 (37 GRC docs) |
| "How do you approach threat modeling AI" | Story 2 (OpenClaw red team) |
| "Describe your detection engineering approach" | Story 3 (Falco 200→12) |
| "Tell me about an incident you handled" | Story 4 (POS skimmer IR) |
| "How do you think about automation + AI" | Story 5 (n8n SOAR) |
| "Describe a Zero Trust project" | Story 6 (tunnels) |
| "How do you write security policy" | Story 7 (AI Governance) |
| "Give me a network security example" | Story 8 (VLANs) |
| "Describe compliance program ownership" | Story 9 (PCI DSS) |
| "Have you run tabletop exercises" | Story 10 (AI accounting tabletop) |
| "Tell me about a disagreement" | Texaco patching (Q&A S7 in `03_TECHNICAL_PREP.md`) |
| "What's a trend you're tracking" | Agent identity (Q&A S8 in `03_TECHNICAL_PREP.md`) |

Every story has a number. Every metric. Every outcome. That's the standard.
