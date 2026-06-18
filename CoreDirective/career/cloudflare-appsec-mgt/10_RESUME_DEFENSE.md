# 10 — RESUME DEFENSE (Bullet by Bullet)

> **CoreDirective framing source of truth:** see `COREDIRECTIVE_FRAMING_LOCKED.md` in this folder. Any references in this file to "lab" or "personal engineering practice" are superseded by the locked version. CoreDirective is an AI security practice with a real anchor client (accounting firm) and a model-flexible AI stack (router that hits Claude or self-hosted Ollama).

This is the doc the interviewers will have open during the call. They will read a bullet, then ask a follow-up. You need a tight, defensible answer for every bullet on the resume. Read this once at 11 AM. Skim it again at 1:15 PM.

Resume on file: `Emmanuel Tigoue - Cloudflare Engineer (1).docx` (attached by Tiana 2026-04-29).

---

## TOP-LINE FACTS THEY WILL READ FIRST

### Resume header says "Cloudflare Engineer"

Risk: they ask "your resume says Cloudflare Engineer at the top but your current title is AI Security Engineer."

Answer: "Cloudflare Engineer is the role I am applying for. My current title at CoreDirective is AI Security Engineer. The resume header reflects the target so the file is easy to track on your side."

Move on. Do not over-explain.

### "WORK EXPERIENCE IN YEARS: 4 years"

Risk: they ask "the JD says 5 plus years, you have 4."

Answer: "Four years dedicated full-time IT security and operations at Texaco, plus the AI Security Engineer role at CoreDirective. The 5-plus framing in the JD is typical for this band. The work I have shipped at year four maps to what most candidates ship at year six because I owned end-to-end at Texaco rather than slotting into a function."

Do not apologize. Do not hedge.

### CoreDirective tenure (Sept 2025 to present)

Risk: they ask "you have only seven months at CoreDirective. Why so short?"

Answer: "CoreDirective is where I run my AI security program now. Before that I was full time at Texaco for four years. The seven months at CoreDirective is the AI security work, the four years at Texaco is the broader IT security and operations work. The two stack."

The honest version is that CoreDirective is your own work and Texaco is the long employer. Do not say "founder" or "I built the company." Employee posture. If they push, "CoreDirective is where the AI security program lives. The Cloudflare and Terraform work I described in bullets one through five is from there."

### Education shows 2026 graduation

Risk: they ask if you have graduated yet.

Answer: "Graduating this May. BBA in Computer Information Systems with the cybersecurity concentration, plus a second BBA in Business Economics. Already commencement-eligible." Then move on.

### "CISSP (In Progress, April 2026)"

Risk: they ask if you have passed.

Answer: "Sitting it this cycle." Do not claim a pass. Do not claim a date. If they push for specifics, "scheduled this cycle, prep is current." Then pivot back to capabilities you already have certified.

### "Eligible for Security Clearance"

Risk: they ask if you currently hold a clearance.

Answer: "No active clearance. Eligible based on background. I have not gone through a sponsor process yet." Do not volunteer this. Only answer if asked.

---

## COREDIRECTIVE BULLETS (BULLET BY BULLET)

### Bullet 1. Cloudflare edge security lifecycle (WAF, Rate Limiting, Bot Fight Mode, Zero Trust Access, Tunnel, DNS hardening). 200+ alerts to 12 daily.

Likely follow-ups:

- **"Walk me through one of your WAF custom rules."**
  > "I run five custom rules because Free tier caps at five. The most useful is a header anomaly challenge, fires when the user agent header pattern matches scanner signatures. Action is managed challenge, not block, so I get a JS interstitial that real browsers solve and scanners do not. Honeytoken paths are two of the five, fires on path patterns no real client should ever request, action block plus log."

- **"Walk me through your Rate Limiting setup."**
  > "Single rule on /webhook/* paths, 10 requests per 10 seconds keyed on IP plus colo. Mitigation timeout one minute. The colo key matters because a single attacker hitting from a botnet looks distributed unless you key on IP plus colo. The /webhook/* scope is because that is where automation traffic lands and where abuse would target."

- **"How did you get from 200 plus alerts to 12 daily?"**
  > "Three layers. One, edge tuning. Most of the noise was Cloudflare events that were not actionable, scanners that were already blocked. Tuned WAF and Rate Limiting first. Two, alert source filtering at the Datadog ingest layer. Three, Squire, the AI triage assistant, handled the residual. Most of the reduction came from layers one and two. Squire was the closer."

- **"Why Bot Fight Mode and not Bot Management?"**
  > "Free tier. Bot Management is paid SKU. Bot Fight Mode plus a scanner UA blocklist as custom rules covers the threat model for a one-zone deployment. For Candescent at multi-tenant scale Bot Management is the right control because credential stuffing across 1,300 FIs needs ML scoring."

### Bullet 2. 30+ resources, 16 Terraform modules, 8 OPA/Rego gates.

Likely follow-ups:

- **"Name a few of the 8 OPA gates."**
  > "Encryption at rest required on storage resources. Encryption in transit required on services. Resource tagging required for cost attribution. No secrets in plaintext (regex match on common secret patterns). Zero public ingress to anything not explicitly marked public. IAM least privilege check on role policies. Required logging on data-handling services. Required backup tags on stateful resources."

- **"Why OPA and not Sentinel or just Terraform validations?"**
  > "OPA is portable. Same Rego policies run in CI for Terraform plans, in admission control for Kubernetes if I add it, and in any future application authorization. Sentinel is HashiCorp-locked. Terraform variable validations are too narrow for cross-resource invariants. OPA is the senior choice when policy is going to outlive any single tool."

- **"How does the OPA gate run in CI?"**
  > "GitHub Actions on pull request. Terraform plan emits JSON. OPA evaluates the plan JSON against the eight policies. If any deny rule fires, the PR comment shows which policy failed and why. Merge is blocked until the policy passes or the policy is amended with a reviewed exception."

### Bullet 3. CI/CD security standard (Trivy, Semgrep, Gitleaks, OPA, Cosign, Syft SBOMs).

Likely follow-ups:

- **"What does Cosign give you that Trivy does not?"**
  > "Trivy is vulnerability scanning. Cosign is image signing. Different problems. Cosign signs the image at build time. Production runtime verifies the signature before pulling. Trivy tells you if the image has CVEs. Cosign tells you if the image is the one your CI built versus a tampered image from a compromised registry. Defense in depth."

- **"What do you do with the SBOM?"**
  > "Syft generates the SBOM at build time, stored as a release artifact. When a new CVE drops we grep the SBOM rather than rebuilding. The SBOM is also evidence for the GRC library, maps to NIST 800-53 SR-3 supply chain risk management."

### Bullet 4. Eliminated standing admin: Teleport JIT PAM, Keycloak SSO RBAC, Cloudflare Access on admin hostnames.

Likely follow-ups:

- **"Why Teleport and not just Cloudflare Access for the SSH path?"**
  > "Cloudflare Access handles HTTP and SSH gating at the edge. Teleport adds session recording and audit log on the SSH session itself. The pair is layered. Cloudflare Access decides whether the session can start. Teleport records what happens during the session. For audit evidence on a privileged path, both are required."

- **"How long is a JIT grant?"**
  > "Default 4 hours. Approval required from a second principal for anything longer. Auto-revoke at expiration. Session recording for the entire JIT window."

### Bullet 5. Runtime detection: CrowdStrike Falcon EDR, Falco eBPF, feeding Datadog.

Likely follow-ups:

- **"Why both Falcon and Falco?"**
  > "Falcon is endpoint behavior. Falco is container syscall behavior. Different layers. Falcon catches things on the host, Falco catches container escapes and runtime anomalies inside the container. Datadog is the aggregation layer so I have one query surface across both."

### Bullet 6. Squire, AI alert triage assistant on LangGraph. 80% review reduction.

Likely follow-ups:

- **"Walk me through Squire's architecture."**
  > "LangGraph workflow. Trigger node receives the alert. Retrieval node uses pgvector to find historically similar alerts and how they were resolved. LLM judge node classifies severity and proposes triage action. Guardrail node redacts PII via NeMo Guardrails. If confidence is high, Squire executes the triage action. If confidence is low, it routes to human-in-the-loop with the proposed action and the historical context. Langfuse traces every decision for audit."

- **"What model does Squire use?"**
  > "Claude Opus 4.7 for the judge node, lightweight embedding model for retrieval. The judge model is the cost driver, so the cheap retrieval step does most of the disambiguation work first. Most alerts get classified without ever calling the heavy model."

- **"How do you know the 80% number is real?"**
  > "Langfuse trace count and human review log. Before Squire, the team manually reviewed 200 plus alerts daily, average 3 minutes per review. After Squire, human review on the residual 12 to 15 alerts at 4 minutes per review because those are the harder ones. Total review time dropped from about 10 hours daily to about an hour. The 80 percent is the review-time reduction, conservative version."

- **"What about hallucination risk?"**
  > "Three guards. One, the LLM judge does not have authority to take destructive action. It can recommend, route, or auto-close known false positives that match historical patterns. Two, NeMo Guardrails check input and output for PII, prompt injection patterns, and out-of-policy responses. Three, every decision is traced in Langfuse, so we have a forensic trail if a decision was wrong."

### Bullet 7. Threat modeled OpenClaw AI gateway: 10 OWASP LLM categories, 14 MITRE ATLAS tactics.

Likely follow-ups:

- **"Name a few of the OWASP LLM categories."**
  > "LLM01 prompt injection. LLM02 insecure output handling. LLM03 training data poisoning. LLM06 sensitive information disclosure. LLM08 excessive agency. LLM10 model theft. The ones that hit hardest in production are 01, 02, 06, and 08."

- **"What is your top defense against prompt injection?"**
  > "Layered. One, input sanitization and length caps at the gateway. Two, system prompts that explicitly instruct the model to ignore user-supplied directives that override role constraints. Three, output guardrails that detect when the model is following an injected directive rather than the role. Four, capability scoping, the agent does not have authority to take action outside its defined scope, so even a successful injection cannot exfiltrate or destroy."

- **"What is MITRE ATLAS?"**
  > "MITRE's adversarial tactics framework specifically for AI/ML systems. Companion to ATT&CK but for the AI threat surface. Reconnaissance, Initial Access, ML Model Access, Execution, Persistence, Defense Evasion, Discovery, Collection, ML Attack Staging, Exfiltration, Impact. We mapped 14 of those tactics against the OpenClaw gateway architecture."

### Bullet 8. AI red team campaigns. Closed 6 high and medium issues.

Likely follow-ups:

- **"Name two of the issues you closed."**
  > "One, prompt injection escalation through tool-use parameters. The agent had a file-read tool that did not validate the path. Injected prompt could read files outside the working directory. Closed by adding path validation and a chroot-style scope. Two, secret leakage through agent-generated logs. Agent was logging the full system prompt and any tool input on error, which included credentials passed as parameters. Closed by structured log redaction at the boundary."

- **"What tooling for AI red team?"**
  > "Promptfoo for repeatable test campaigns. Manual probing for the harder cases that automated tools miss. PyRIT for some of the prompt injection categories."

### Bullet 9. n8n AI agent platform: 14 LLM workflows across 16 services. 12+ hours per week reclaimed.

Likely follow-ups:

- **"What does an n8n workflow look like in your environment?"**
  > "Trigger, classify, route, act. A typical one is the Telegram Supervisor Agent. Trigger on inbound message. Classify intent against a set of known commands. Route to the appropriate downstream service via the master orchestrator webhook. Action could be a postgres query, a github API call, a Notion lookup, a Telegram reply. Result returns to the user."

- **"What was the 12 hours per week?"**
  > "Manual triage and routing tasks. Email classification, alert correlation, status reporting. The 12 hours is across security and ops combined. Counted by tracking before-and-after time logs for two months on the recurring tasks."

### Bullet 10. CoreDirective AI security program: 49 GRC documents, NIST 800-53 169 controls, NIST AI RMF, ISO 42001, 5 IR playbooks, Promptfoo eval harness.

Likely follow-ups:

- **"Why 169 controls and not the full 800-53 catalog?"**
  > "Tailored to the architecture. 800-53 has more than a thousand controls across the catalog. 169 is the subset that applies to the CoreDirective architecture given the data classifications and system categorization. The tailoring exercise is the value, not the count."

- **"Walk me through one of the IR playbooks."**
  > "AI Incident playbook. Five steps. Detection: signal that the model behavior has drifted, either through Promptfoo eval regressions, Langfuse anomaly traces, or user reports. Containment: revoke the model from the routing layer, fall back to a known-good model. Investigation: pull traces, eval the suspect model against the regression suite, identify the cause. Recovery: roll forward to a fixed model or roll back to the prior version. Post-incident: update the eval harness to catch the new failure mode."

- **"What is Promptfoo?"**
  > "Eval framework for LLM applications. You define test cases with expected behaviors, run them against any prompt or model, and get a pass/fail report. Used for both development testing and regression testing on production prompts."

---

## TEXACO BULLETS (BULLET BY BULLET)

### Bullet 11. IR across 3 retail locations: Wireshark POS skimmer, credential compromises, vendor access.

Likely follow-ups:

- **"How did you use Wireshark on a POS skimmer?"**
  > "Span port on the switch in front of the POS. Captured traffic to a laptop running Wireshark. Looked for unexpected outbound connections from the POS to any host that was not the payment processor or the patch server. Filtered on the POS MAC and protocol. The skimmer attempt showed up as outbound HTTPS to a non-processor IP. Correlated against the processor's allow list."

- **"What about the credential compromise case?"**
  > "Account showing logins from a geo we did not operate in. Session logged into store back-office. Disabled the account, reset, MFA enrollment forced. Pulled session timeline from Splunk. Source was a phishing email opened by an assistant manager. Walked the team through the email, ran a phishing awareness session the next week."

### Bullet 12. 6-step IR runbook. 8 hours to 90 minutes.

This is Story 2 from the strategy doc. Already drilled.

### Bullet 13. Flat network to 4 VLANs. Lateral movement to zero, validated with Nmap.

This is Story 5. Already drilled.

Likely follow-up: **"Name the four VLANs."**
> "POS, back-office, guest WiFi, vendor. ACLs at the gateway, only POS-to-payment-processor and back-office-to-internal-services were permitted. Vendor traffic was forced through a jump host with MFA."

### Bullet 14. Splunk SIEM. 48h to 4h detection.

Likely follow-up: **"What correlation rules did you build?"**
> "Three categories. One, authentication anomalies, multi-account failed-then-success patterns. Two, lateral movement, east-west traffic that did not match the segmentation policy. Three, POS-specific, anything outbound from a POS that was not on the processor allow list. The detection time drop came mostly from category three because before Splunk we had no automated way to spot POS anomalies."

### Bullet 15. AD hardening: 14 critical to 2 findings.

This is Story 1. Already drilled.

Likely follow-up: **"What were the remaining two findings?"**
> "Both architectural. One was domain trust topology, would have required a forest restructure. Two was service account credential lifecycle for legacy applications that did not support modern credential rotation. Both went into the next budget cycle and got closed in year two."

### Bullet 16. PCI DSS for 45+ devices. Quarterly Nessus.

Likely follow-ups:

- **"What was your SAQ level?"**
  > "SAQ-D. We had POS, back-office, and the web ordering application in scope. After segmentation the web ordering app dropped scope because the back-end was hosted by a PCI-validated processor and we only handled the order metadata, not card data."

- **"How did you handle Nessus findings?"**
  > "Quarterly scan, triage by CVSS plus exploit availability. Anything CVSS 7 plus with public exploit was 30-day fix. Lower severity went into the patch cycle. Findings that could not be remediated within the window got compensating controls and a documented exception in the SAQ."

### Bullet 17. Scripted patch deployment, user provisioning, compliance reporting in Python and PowerShell. 12 hours per week saved.

Likely follow-up: **"Show me a high-level of one of those scripts."**
> "User offboarding. Trigger from HR ticket, pull the username, disable AD account, remove from groups, revoke MFA tokens, archive mailbox to compliance hold, generate the offboarding report. PowerShell calling AD modules and Microsoft Graph for the M365 side, Python for the report generation. Idempotent so a re-run does not break."

### Bullet 18. NIST AI RMF policies, LLM phishing detection, incident triage across 3 locations.

Risk: this bullet sits at Texaco, but Texaco is mostly retail IT, not AI. Interviewers may ask "you did AI work at Texaco?"

Answer: "End of my Texaco tenure I was already doing the early AI security work that became the CoreDirective program. LLM phishing detection was a small project, used embeddings to catch lookalike phishing variants that traditional keyword filters missed. NIST AI RMF policy work was preparing for the AI use cases CoreDirective would adopt."

If you do not feel solid on this answer, deflect: "That bullet sits at the seam between Texaco and CoreDirective. The bulk of the AI work is in the CoreDirective bullets above."

---

## SKILLS LINE DEFENSE

The skills line at the top reads "LangChain, LiteLLM, LlamaIndex, Hugging Face, OWASP ML Top 10, CSA AI Controls Matrix, Adversarial ML, Burp Suite, Snyk, FedRAMP."

Risk: JT may notice no Cloudflare-specific tooling in the skills line.

Answer: "The skills line is the AI security tooling stack. The Cloudflare and Terraform stack is in the bullets. Skills lines on senior resumes pull the differentiator tooling, not the tools that already show up in the bullets. If you want, I can walk through my Cloudflare provider experience in Terraform, that is where the day-to-day lives."

---

## THE THREE BULLETS THEY ARE MOST LIKELY TO ASK ABOUT

If you only prep three deep follow-ups, prep these.

1. **Bullet 1, the 200 plus to 12 alert reduction.** This is the most quotable number on the resume. They will ask how you got there.
2. **Bullet 2, the OPA gates.** This is the senior differentiator. JT will pull on this because policy-as-code is rare at this rate.
3. **Bullet 6, Squire architecture.** Augustine will pull on this because AI in security operations is the area he posts about.

Drill those three follow-ups out loud once before the call.

---

## TWO BULLETS WITH HIDDEN RISK

1. **Bullet 18, NIST AI RMF at Texaco.** Already addressed above. Be ready to redirect to CoreDirective work.
2. **Bullet 6, the 80 percent number for Squire.** If they ask "how do you know," have the conservative-method answer ready: Langfuse trace count plus before-and-after time logs over two months.

---

## FINAL CHECK

Open the PDF on a second screen at 1:15 PM. Skim every bullet once. Make sure your mouth knows the version of the story that is on paper. The interviewers will be reading from the same paper.

Resume PDF path: `~/cyber-squire-ops/CoreDirective/career/cloudflare-appsec-mgt/Emmanuel_Tigoue_AISecurity_Engineer_Cloudflare_AppSec_Manager.pdf`
