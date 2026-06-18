# OneDigital Technical Prep — Tools, Acronyms, Q&A

For the Thu 4/23 Pavel screen. 30 minutes, technical + behavioral mixed. Pavel is CISA, not a pentester — he'll probe process, control frameworks, and judgment, not exploit dev.

---

## Part 1 — Acronym Glossary (know each one cold, do not stumble)

### AI / ML / LLM Security

| Acronym | Full Name | What It Is |
|---------|-----------|------------|
| **LLM** | Large Language Model | GPT-4, Claude, Gemini, Llama — the underlying generative models |
| **OWASP LLM Top 10** | Open Web Application Security Project — LLM Applications | The 10 most critical LLM vulnerabilities. 2025 version. Covers prompt injection, sensitive info disclosure, supply chain, data + model poisoning, improper output handling, excessive agency, system prompt leakage, vector + embedding weaknesses, misinformation, unbounded consumption |
| **MITRE ATLAS** | Adversarial Threat Landscape for AI Systems | MITRE's ATT&CK-style knowledge base for ML attacks. Tactics: reconnaissance, resource dev, ML model access, ML attack staging, persistence, defense evasion, discovery, collection, ML attack, exfiltration, impact |
| **NIST AI RMF** | National Institute of Standards AI Risk Management Framework | NIST's AI governance framework. Four functions: Govern, Map, Measure, Manage. Pair with AI RMF Playbook and Generative AI Profile (NIST-AI-600-1) |
| **ISO/IEC 42001** | International Standard for AI Management Systems | 2023 standard. The ISO 27001 equivalent for AI. Management system requirements for AI — governance, policies, risk, lifecycle |
| **NeMo** | NVIDIA NeMo | NVIDIA's framework for LLMs. "NeMo Guardrails" is the specific piece for LLM safety — blocks prompt injection + output filtering + conversation policy |
| **Prompt Injection** | — | Manipulating LLM behavior by inserting instructions in user input. Direct (user typed) vs indirect (attacker plants in content LLM ingests) |
| **RAG** | Retrieval-Augmented Generation | LLM pattern where context is retrieved from a vector DB before prompting. Attack surface: poisoned vectors, data exfiltration via retrieval |
| **Excessive Agency** | — | OWASP LLM05. Giving an LLM more tool/permissions than needed. Mitigation: least-privilege tool design, human-in-the-loop on high-impact actions |
| **Jailbreak** | — | Bypassing LLM safety guardrails. Classic example: DAN-style prompts, role-play bypasses, multi-turn priming |
| **AIDR** | AI Detection and Response | New category (CrowdStrike's Falcon AIDR). Real-time detection + behavioral analysis + response across the AI stack — models, prompts, agents, data pipelines |

### AppSec / Code Security

| Acronym | Full Name | What It Is |
|---------|-----------|------------|
| **SAST** | Static Application Security Testing | Scans source code / binaries for vulns without running them. Examples: Snyk Code, Semgrep, Checkmarx, SonarQube |
| **DAST** | Dynamic Application Security Testing | Tests running applications by sending attacks. Examples: OWASP ZAP, Burp Suite, Invicti |
| **SCA** | Software Composition Analysis | Scans dependencies for known CVEs. Examples: Snyk Open Source, Dependabot, Trivy (containers), OSS Review Toolkit |
| **IAST** | Interactive Application Security Testing | Hybrid — instruments the running app to see what SAST would see in the flow. Contrast, Seeker |
| **RASP** | Runtime Application Self-Protection | Blocks attacks in production at runtime. Less common now, replaced by WAF + eBPF runtime detection |
| **SBOM** | Software Bill of Materials | Inventory of components in software. Formats: CycloneDX, SPDX. Tools: Syft, Trivy |
| **OWASP Top 10** | — | The classic Top 10 (not LLM). 2021 edition: Broken Access Control, Crypto Failures, Injection, Insecure Design, Security Misconfiguration, Vulnerable Components, ID/Auth Failures, Software/Data Integrity Failures, Logging/Monitoring, SSRF |

### API / Cloud / Identity

| Acronym | Full Name | What It Is |
|---------|-----------|------------|
| **WAF** | Web Application Firewall | Blocks attacks at the HTTP layer. Examples: Cloudflare, Akamai Kona, AWS WAF |
| **mTLS** | Mutual TLS | Both client and server present certs. Ensures both sides are authenticated. Strong Zero Trust pattern |
| **OAuth 2.0** | Open Authorization | Delegated access — third-party apps get tokens to access resources without seeing passwords. **CENTRAL to the Salesloft/Drift breach** |
| **OIDC** | OpenID Connect | Identity layer on top of OAuth 2.0. Adds `id_token` for authentication. SSO pattern |
| **SSO** | Single Sign-On | One login, many applications. Usually via OIDC / SAML |
| **SAML** | Security Assertion Markup Language | Older SSO standard, XML-based. Still in enterprise. OneDigital / Microsoft: likely uses SAML + OIDC hybrid |
| **Entra ID** | Microsoft Entra ID (formerly Azure AD) | Microsoft's IAM. Conditional Access policies, PIM, Identity Protection. OneDigital runs this. |
| **Conditional Access** | — | Entra feature: policies like "require MFA + compliant device for this app." Zero Trust enforcement point |
| **PRMFA** | Phishing-Resistant Multi-Factor Authentication | MFA that resists AiTM phishing. Examples: FIDO2/WebAuthn, Windows Hello for Business, certificate-based auth. SMS/TOTP/push approval are NOT phishing-resistant. |
| **PIM** | Privileged Identity Management | Entra feature for time-boxed admin elevation. Equivalent to Teleport PAM |
| **JIT** | Just-In-Time (access) | Ephemeral access with approval. The opposite of standing admin rights |
| **PAM** | Privileged Access Management | Broader discipline: vaulting, rotation, session recording, JIT. Teleport is the PAM tool you deployed |
| **FIDO2** | Fast IDentity Online 2 | Passwordless + PRMFA standard. WebAuthn is the browser API |
| **Zero Trust** | — | Architecture principle: never trust, always verify. Explicit verification, least privilege, assume breach. NIST SP 800-207 |
| **CNAPP** | Cloud-Native Application Protection Platform | Combines CSPM + CWPP + CIEM. Examples: Wiz, Prisma Cloud, Defender for Cloud |
| **CSPM** | Cloud Security Posture Management | Misconfiguration detection across cloud accounts |
| **CWPP** | Cloud Workload Protection Platform | Runtime protection for VMs, containers, serverless |
| **CIEM** | Cloud Infrastructure Entitlement Management | Manages cloud identity permissions — least privilege at scale |

### Compliance / Governance

| Acronym | Full Name | What It Is |
|---------|-----------|------------|
| **CISA** | Certified Information Systems Auditor | ISACA cert. Audit, assurance, control evaluation. **Pavel holds this.** |
| **CISM** | Certified Information Security Manager | ISACA. Management-focused peer to CISA |
| **CISSP** | Certified Information Systems Security Professional | ISC2. Broad security leadership cert. **You are pursuing this — sitting before end of April 2026** |
| **SOC 2 Type 2** | — | AICPA audit report. Examines design + operating effectiveness of controls over a period (usually 6-12 months). Type 1 = design only. Type 2 = operating effectiveness over time |
| **Trust Services Criteria (TSC)** | — | What SOC 2 audits against: Security, Availability, Processing Integrity, Confidentiality, Privacy |
| **NIST SP 800-53** | — | Security + Privacy Controls for Federal Systems and Organizations. Rev 5. **You mapped 37 GRC docs to 800-53.** |
| **NIST CSF** | Cybersecurity Framework | 2.0 released Feb 2024. Six functions: Govern, Identify, Protect, Detect, Respond, Recover |
| **CIS Controls / CIS Top 18** | Center for Internet Security Critical Security Controls | Prescriptive, prioritized. 18 controls in v8.1. **OneDigital aligns to this — Pavel will reference** |
| **ISO/IEC 27001** | — | International information security management standard. Control set is Annex A (114 controls) |
| **ISO/IEC 27002** | — | Implementation guidance for Annex A controls |
| **HIPAA** | Health Insurance Portability and Accountability Act | OneDigital touches health benefits — HIPAA-adjacent compliance relevant |
| **GLBA** | Gramm-Leach-Bliley Act | Applies to financial services. OneDigital Investment Advisors LLC is a registered investment advisor — GLBA + SEC Safeguards Rule apply |
| **POA&M** | Plan of Action and Milestones | Tracked remediation list. You maintain one at CoreDirective with 37 findings across 4 assessment sources |
| **SSP** | System Security Plan | Foundational doc in 800-53 compliance. Describes the system, controls, and control implementation |

### Infrastructure / Detection

| Acronym | Full Name | What It Is |
|---------|-----------|------------|
| **eBPF** | Extended Berkeley Packet Filter | Linux kernel tech for running sandboxed programs for observability + security. Falco uses it. |
| **SIEM** | Security Information and Event Management | Log aggregation + correlation + alerting. Splunk, Sentinel, Datadog |
| **SOAR** | Security Orchestration, Automation, and Response | Playbook automation. n8n, Tines, Demisto/XSOAR |
| **EDR / XDR** | Endpoint/Extended Detection and Response | Host + network detection. CrowdStrike Falcon, SentinelOne, Defender for Endpoint |
| **IOC** | Indicator of Compromise | Hashes, IPs, domains, patterns that signal known attacks |
| **TTP** | Tactics, Techniques, Procedures | MITRE ATT&CK abstraction — what attackers actually do |
| **MTTD** | Mean Time To Detect | Detection speed metric. **Your Texaco Splunk work: 48h → <4h** |
| **MTTR** | Mean Time To Respond | Response speed. **Your Texaco IR runbook: 8h → 90min containment** |

---

## Part 2 — Tool Deep Dives (speak fluently)

### Snyk (SAST + SCA + Container + IaC)

**What it does:** Developer-first security platform. Scans: source code (Snyk Code — SAST), open-source deps (Snyk Open Source — SCA), container images (Snyk Container), infrastructure-as-code (Snyk IaC).

**Typical integration:** Git repository connection → scan on every PR → block merge on critical findings → fix PRs suggested by Snyk's remediation advice.

**Use case narrative for Pavel:** "We'd plug Snyk into GitHub Actions or equivalent. On every pull request, Snyk Code catches SAST issues — XSS, SQL injection, hardcoded secrets. Snyk Open Source catches vulnerable dependencies with known CVEs. Snyk Container scans base images. The developer gets feedback inline in the PR. Blocked PRs have to be remediated or explicitly waived with a CISO-approved exception. That's how SAST/SCA shifts left without slowing down velocity."

**Your equivalent:** Semgrep (Snyk Code peer) + Trivy (Snyk Container peer) + Gitleaks (secrets) + OPA policies (Snyk IaC peer). Different vendors, same discipline.

### Salt Security (API Security)

**What it does:** API posture + runtime threat detection. Uses ML to baseline normal API behavior and flag anomalies. Discovers shadow APIs — endpoints that exist but aren't documented. Integrates with CrowdStrike Falcon natively (Salt sensor deploys through Falcon Foundry — this is the path of least resistance at OneDigital).

**Three-phase model Salt uses:**
1. **Discovery** — find every API endpoint (documented and shadow)
2. **Posture** — identify vulnerabilities (auth issues, excessive data exposure, broken object-level authorization — OWASP API Top 10)
3. **Threat protection** — runtime detection of attacks against APIs (account takeover, data exfiltration via API, credential stuffing)

**Use case narrative:** "Salt solves the problem that traditional WAFs and DAST miss — the shadow APIs nobody documented and the business logic attacks that look like normal traffic. At OneDigital scale, with AI pipelines pulling data from dozens of backend APIs, Salt gives you the API visibility that the developer portal doesn't."

**Why it matters post-Salesloft:** OAuth tokens get abused via API calls. Salt's behavioral detection would flag a legitimate OAuth token being used to bulk-query Salesforce in a way the normal user never would. That's exactly the control gap the 2025 breach exposed.

### CrowdStrike AIDR (AI Detection and Response)

**What it is:** CrowdStrike announced Falcon AIDR as a dedicated product category in 2024-2025. Extends Falcon's EDR approach to AI workloads.

**What it monitors:**
- Endpoints running AI workloads (training nodes, inference hosts)
- Cloud environments hosting models (GPU fleets, model registries)
- The AI assets themselves — models, prompts, agents, data pipelines

**Detection categories:**
- Prompt injection attempts
- Model abuse patterns (excessive inference queries, cost-DoS)
- Agent misuse (an agent doing things outside its defined scope)
- Data exfiltration through AI context windows
- Supply chain tampering (malicious model weights, poisoned training data)

**Use case narrative:** "AIDR gives you EDR-class telemetry for AI workloads. If someone prompt-injects our chatbot to exfiltrate customer data, AIDR catches the anomalous data access pattern in the same Falcon console where we'd see a compromised endpoint. That integration story is why it fits OneDigital — CrowdStrike is already your endpoint stack."

**Your equivalent:** Falco eBPF + Datadog. Different scope (Falco is host runtime, not AI-aware). AIDR is a natural extension.

### Qualys (VMDR — Vulnerability Management)

**What it is:** Qualys Cloud Platform. Flagship product is VMDR (Vulnerability Management, Detection, and Response). Asset discovery + vulnerability scanning + prioritization + patch deployment in one platform.

**How it runs:** Cloud agents installed on endpoints report posture continuously. Scanners run authenticated + unauthenticated scans against servers, network devices, web apps. Findings get prioritized by exploitability (CVSS + threat intel).

**Use case narrative:** "Qualys VMDR gives you continuous scanning across the infrastructure hosting the AI workloads plus the broader app environment. You scope a scan against a class of assets, review findings by risk score, push tickets to patch owners via ServiceNow/Jira integration, and verify remediation on the next scan cycle. I did this with Nessus at Texaco on 45+ devices across PCI scope. Qualys is a UX ramp, not a methodology change."

**Your equivalent:** Nessus (Texaco) + Trivy (CoreDirective). Same vulnerability management discipline.

### Microsoft Entra ID + PRMFA

**What Entra ID is:** Microsoft's cloud identity provider. Formerly Azure AD. Handles authentication + authorization + identity governance for all Microsoft 365 users and federated third-party apps.

**Key features to know:**
- **Conditional Access policies** — rules like "require MFA + compliant device + trusted location for this app"
- **Identity Protection** — risk-based user/sign-in risk detection (leaked creds, unfamiliar sign-in locations, anonymous IPs)
- **PIM (Privileged Identity Management)** — time-boxed admin elevation with approval workflow
- **Workload Identity** — service principals and managed identities for non-human accounts
- **Entra Agent ID** (new, 2025) — extends identity to AI agents specifically
- **B2B / B2C** — external identity scenarios

**PRMFA in Entra:**
- FIDO2 security keys (YubiKey, physical keys)
- Windows Hello for Business (biometric + TPM-bound)
- Passkeys (emerging)
- Certificate-based authentication

**NOT phishing-resistant (known gaps):** SMS codes, voice calls, TOTP apps, push-without-number-matching. If Pavel asks about PRMFA specifically, know the difference.

**Use case narrative:** "In Entra, you'd enforce PRMFA on admin roles and high-sensitivity apps via a Conditional Access policy that requires FIDO2 or Windows Hello. You'd pair that with Identity Protection to catch compromised sessions and PIM to eliminate standing admin privileges. That's Zero Trust identity in Microsoft's stack — same pattern as what I did with Keycloak + Teleport at CoreDirective."

---

## Part 3 — Likely Technical Questions (with answer frames)

### Q1: "Walk me through how you'd threat model an AI application."

**Frame (90 sec):**
"Four passes. First, **data flow** — where does data come from, where does it go, where does it cross trust boundaries. Second, **threat identification** — I use STRIDE for general threats plus MITRE ATLAS for AI-specific tactics. Third, **risk scoring** — likelihood + impact, prioritized against business criticality. Fourth, **mitigation mapping** — controls from OWASP LLM Top 10, NIST AI RMF, or ISO 42001.

For a concrete example, OpenClaw at CoreDirective. The data flow: user prompts come through Cloudflare edge, hit the gateway, get routed to either Claude Opus API or a NeMo-sandboxed local Ollama. Context comes from an internal knowledge base. Trust boundaries: edge, gateway, model inference, knowledge retrieval.

Threats: prompt injection at the user input, indirect injection via retrieved context, excessive agency if an LLM gets tool access, data exfiltration through the response window, supply chain risk on the Claude API or NeMo container images.

Mitigations mapped from OWASP LLM Top 10: input validation and prompt filtering at the gateway, system prompt instruction and output constraint, NeMo Guardrails for content policy, least-privilege tool access, rate limiting at Cloudflare edge, mTLS for service-to-service calls. Documented as an AI-specific IR playbook."

### Q2: "What's the biggest AI security risk right now, and how do you mitigate it?"

**Frame (60-75 sec):**
"Indirect prompt injection, because the defenses are weaker than the attack surface is wide. Direct injection — a user typing a jailbreak — is well-understood. Indirect is when an attacker plants instructions in content the LLM will later ingest: a poisoned PDF, a malicious web page in a RAG retrieval, a calendar event summarized by an assistant.

Mitigation is layered. First, treat all retrieved content as untrusted and constrain the LLM to extracting facts rather than following instructions. Second, use output constraints — structured outputs with schema validation, so the model can't just execute arbitrary instructions. Third, least-privilege agency — the model should not have the tools needed to cause damage unless a human approves. Fourth, monitor for anomalies — if an LLM starts requesting tools it doesn't usually use, alert.

The mindset shift is treating the LLM like a confused deputy. It doesn't know the difference between your instruction and an attacker's instruction embedded in data. So you architect around that assumption."

### Q3: "How would you review a SOC 2 Type 2 report from a vendor?"

**Frame (60 sec — Pavel will love this one, it's CISA home turf):**
"Five-point review. First, **scope** — what trust services criteria does the report cover (Security always, plus possibly Availability, Confidentiality, Privacy, Processing Integrity). Confirm the scope matches our data relationship with them.

Second, **reporting period** — Type 2 covers a period (usually 6-12 months). Check the dates align with when we're relying on them. Gaps matter.

Third, **subservice organizations** — Type 2 reports often carve out subservice orgs. A vendor using AWS carves out AWS controls. I confirm their carve-outs make sense and review their AWS SOC 2 or equivalent separately.

Fourth, **exceptions and deviations** — the auditor's opinion lists control failures. I read every exception, assess materiality, check if management's response includes a dated remediation plan.

Fifth, **complementary user entity controls (CUECs)** — what controls OUR organization has to implement on our side for the vendor's controls to work. Miss these and you think you're covered when you're not.

Output: a vendor risk memo with findings mapped to our internal control framework, recommended compensating controls if gaps exist, and a revalidation cycle."

### Q4: "Explain Zero Trust to a non-technical executive."

**Frame (45 sec):**
"Zero Trust means we don't give anything automatic trust based on where it is on the network. Old model: if you're inside the corporate firewall, we trust you. That model broke when everyone went remote and when attackers got inside the firewall.

New model: every request — user, device, service — has to prove who it is and that it should have access, every time, based on current context. Your user account is valid, your laptop is compliant with security posture, you're requesting access to something your role allows, and the request pattern looks normal.

Three principles: verify explicitly, least privilege, assume breach. In practice: MFA everywhere, device compliance checks, conditional access policies, segmentation so a breach doesn't spread, and continuous monitoring."

### Q5: "A user pasted customer Social Security numbers into ChatGPT Enterprise. What's your response?"

**Frame (75 sec):**
"First 15 minutes: contain. Confirm the incident — platform log, user confirmation. Determine if ChatGPT Enterprise tenant has data retention enabled (default yes, 30-day minimum for compliance). Engage the account team at OpenAI to initiate data deletion on our tenant per our enterprise contract. Freeze the user's session.

First hour: scope. How many records? What fields? When did the paste happen? Did the model output get shared with anyone downstream? Are there conversation exports, shared links, or chat history sharing enabled? Disable conversation sharing org-wide if not already.

First day: notify. Internal escalation to legal and privacy. State breach notification laws — in Georgia specifically, if SSNs were involved and the exposure is material, we have to notify impacted individuals within a reasonable time. Begin the vendor breach process with OpenAI if retention hasn't been able to purge.

First week: remediate. Root cause — why did a user think pasting SSNs was OK. Update AI use policy. Deploy DLP controls on outbound traffic to unsanctioned LLM endpoints. Add a structured AI awareness module addressing this pattern specifically. If the JD's "human factors" emphasis is real, this is the exact scenario the role exists to prevent."

### Q6: "What's your approach to getting developers to care about security?"

**Frame (45-60 sec):**
"Three things. One, make secure the easy path. If Snyk findings show up in the PR with a one-click fix suggestion, developers accept them. If they have to leave their IDE and go to a separate dashboard to triage, they won't.

Two, own your noise. A SAST tool dropping 400 findings with 90 percent false positives makes developers ignore all 400. I tune rules until findings are actionable. Falco at CoreDirective went from 200 alerts a day to 12 actionable — that's when developers started paying attention.

Three, translate security into their metrics. Don't tell engineers their code is insecure. Tell them which finding would cause a production incident, which would fail a SOC 2 audit, which would block a customer deal. Security outcomes mapped to outcomes developers already own."

### Q7: "Describe a time you disagreed with a technical decision. What did you do?"

**Frame (60-75 sec — behavioral, have ready):**
"At Texaco, the recommendation from the managed services vendor was to run quarterly Nessus scans and patch on a 90-day cycle. The PCI auditor agreed — that's the minimum. I pushed for monthly authenticated scans plus a 30-day patch SLA on critical findings because the attack surface was a flat network with POS devices, and the 2021 POS skimmer incident we handled showed how fast attackers move once they're in.

I built the case with data: average time from CVE disclosure to exploit-in-the-wild for recent POS-relevant vulns was 18 days. Ninety-day patch cycle means we are knowingly exposed to in-the-wild exploits for 72 days after they're published. Not acceptable for payment processing.

I took it to the GM. The resistance wasn't security — it was operational disruption on patch windows. I proposed a staged rollout: patch critical findings during off-peak retail hours in a 2-hour window, validate with quick regression, roll to the rest of the fleet overnight. That worked. We moved to monthly scanning + 30-day critical SLA. In 8 months I dropped critical audit findings from 14 to 2.

The lesson I named: 'technically correct' is not enough. You have to design for the operational reality of the team doing the work. Otherwise, security becomes the team that is right on paper and ignored in practice."

### Q8: "What's a security trend you're tracking that most people aren't?"

**Frame (45-60 sec):**
"Agent identity. Non-human identity has been growing — service principals, managed identities, OAuth apps — and now autonomous AI agents are a third category. Microsoft announced Entra Agent ID as its answer. CrowdStrike AIDR is addressing the detection side. The point is that an AI agent with OAuth access to Salesforce looks a lot like what attackers used in Salesloft/Drift — and existing IAM programs were designed for humans and service accounts, not for autonomous software that makes its own decisions about what to query.

The gap I see: most enterprises don't yet have an identity governance program that treats agents as a distinct class. They either over-permission them because they don't fit the human model, or under-permission them and the agent doesn't work. Both are bad outcomes.

I'm tracking this because OneDigital deploying AI agents across 5,000 employees means this governance problem is coming fast. If I'm in this seat, that's one of the first 90-day deliverables I'd push for — a named agent identity framework with scoped OAuth, mandatory rotation, anomaly monitoring. Builds on the post-Salesloft industry playbook."

---

## Part 4 — Scenario Questions (CISA-style, likely from Pavel)

Pavel as a CISA holder thinks in control frameworks. Expect at least one scenario that tests your audit + documentation + evidence discipline.

### S1: "A business unit wants to deploy a new AI chatbot vendor. Walk me through your review process."

**Frame (90 sec):**
"Seven-point vendor AI review, maps to the JD's SaaS/vendor security responsibility.

1. **Request SOC 2 Type 2 report.** Read it using the 5-point method — scope, period, subservice carve-outs, exceptions, CUECs. If they can't produce one, that's a material finding.

2. **Data flow classification.** What data does the chatbot touch? Public, internal, confidential, regulated (HIPAA, GLBA, PCI)? Everything above 'internal' requires additional controls.

3. **AI-specific risk assessment.** What model underneath? Is our data used for training? Can we contractually opt out? (For enterprise OpenAI, Anthropic, Google contracts — usually yes, but you verify.) How is our data retained and when is it deleted?

4. **Identity integration.** Does it support Entra SSO? Conditional Access? JIT provisioning? If we can't control access through our IAM, it's a no.

5. **Threat modeling the integration.** OAuth scopes requested — are they minimum necessary? Webhook endpoints — how are they authenticated? Data retrieval patterns — what can it pull from our systems?

6. **Compliance + legal review.** BAA if health data, DPA if EU data subjects, contract language on breach notification timing, audit rights, subprocessor transparency.

7. **Approval + monitoring plan.** Documented approval with risk owner sign-off. Defined monitoring controls post-deployment. Annual revalidation cycle.

Output: a vendor risk memo with findings mapped to CIS 18 + 800-53 controls, gaps documented in a POA&M, and a defensible audit trail."

### S2: "You find a critical vulnerability in a production AI system. What's your next 24 hours?"

**Frame (75 sec):**
"First hour: validate. Confirm it's real, not a scanner false positive. Reproduce in a controlled way. Document the finding — CVE, CVSS, exposure, business impact, preconditions.

Next 2-4 hours: contain. Can we compensating-control in the short term — WAF rule, egress block, feature flag? If yes, deploy that to reduce the window. If no, escalate to a service-level decision on whether to take the feature down.

Same-day: disclose up. Notify hiring manager + app owner with the finding, the containment state, and the remediation plan. If material, loop in legal + comms on breach notification readiness — don't wait for confirmed exploitation.

24 hours: fix plan + timeline. Remediation owner identified, patch or code fix in progress, test plan defined, rollback plan in case the fix breaks something, evidence capture for the audit trail.

Documentation throughout. Every decision is captured in the incident record. Pavel as a CISA knows this — the audit matters as much as the fix. A correct fix with no paper trail fails the post-incident review."

### S3: "One of your AI vendors just had a breach. What do you do?"

**Frame (60-75 sec):**
"Hour zero: inventory. What data do we have with this vendor, what's the blast radius if everything they had leaked? Map to our internal classification.

Hour one: engage the vendor. Request their breach notification letter with the specifics — affected records, data types, timeline, remediation steps. Make sure it's in writing.

Day one: scope our exposure. Pull audit logs of what we sent the vendor during the breach window. Cross-reference their affected-records scope with our data sent.

Day one to three: notify. Internal escalation + legal + privacy. If the exposed data includes regulated data — SSNs, PHI, financial — our own breach notification obligations trigger even though we weren't the primary target. State laws vary; some have 30-day notification windows, some shorter.

Week one: remediate + reassess. Rotate any shared secrets — OAuth tokens, API keys, service account credentials. Temporarily disable the integration if the vendor hasn't confirmed remediation. Reassess the vendor relationship — do we keep using them, migrate, or enforce additional controls going forward.

The Salesloft/Drift playbook in Aug 2025 is the canonical recent example. FINRA issued the alert, 700 orgs disconnected the integration, OAuth tokens rotated across the industry. That's the template."

---

## Part 5 — CIS Top 18 Quick Reference (Pavel may reference)

OneDigital JD explicitly calls out "aligning security practices to the CIS Top 18 Controls." Know the 18 by category. You don't need to memorize every sub-control — just be fluent on what each control covers.

| # | Control | What it covers |
|---|---------|----------------|
| 1 | Inventory and Control of Enterprise Assets | Know every device connected to the network |
| 2 | Inventory and Control of Software Assets | Know every application running |
| 3 | Data Protection | Classification, retention, encryption |
| 4 | Secure Configuration of Assets and Software | Hardening baselines (CIS Benchmarks) |
| 5 | Account Management | User + service account lifecycle |
| 6 | Access Control Management | Least privilege, MFA, privileged access |
| 7 | Continuous Vulnerability Management | **Qualys territory** |
| 8 | Audit Log Management | Centralized logging, retention |
| 9 | Email and Web Browser Protections | Phishing defense, browser security |
| 10 | Malware Defenses | **CrowdStrike territory** |
| 11 | Data Recovery | Backups, restore testing |
| 12 | Network Infrastructure Management | Segmentation, firewall config |
| 13 | Network Monitoring and Defense | **Salt + CrowdStrike + SIEM territory** |
| 14 | Security Awareness and Skills Training | **JD's "human-centric" focus** |
| 15 | Service Provider Management | **SOC 2 Type 2 vendor review territory** |
| 16 | Application Software Security | **Snyk + DAST territory** |
| 17 | Incident Response Management | **CrowdStrike AIDR + tabletop territory** |
| 18 | Penetration Testing | Scheduled pen tests, red team |

**For Pavel: when the JD tools map to CIS, call it out.** "Snyk covers control 16, Qualys covers control 7, CrowdStrike covers 10 and 13 and 17, Salt layers onto 13 and 16, the human factors responsibility in the JD is control 14, the SOC 2 vendor review is control 15. The stack is internally consistent against CIS 18."

---

## Part 6 — The Three Frameworks Pavel Cares About

Lead with these when asked about governance frameworks. Know them deeper than surface level.

### NIST CSF 2.0 (released February 2024)

Six functions — prior version had five, 2.0 added **Govern**:
1. **Govern** — the context and risk appetite (new in 2.0, central)
2. **Identify** — know your assets, risks
3. **Protect** — safeguards
4. **Detect** — find events
5. **Respond** — act on events
6. **Recover** — restore operations

**Why this matters:** The addition of Govern in 2.0 is exactly the bend a CISA interviewer cares about. When Pavel asks what you think of CSF 2.0, lead with "the Govern function pulling board-level risk integration into the framework is the biggest shift — it acknowledges that the CISO is increasingly an executive role, not just IT."

### NIST SP 800-53 Rev 5

The control catalog. Rev 5 added privacy controls as a first-class family. Structure:
- **Families** (20 of them): AC (Access Control), AT (Awareness and Training), AU (Audit and Accountability), CA (Assessment), CM (Configuration Management), CP (Contingency Planning), IA (Identification and Authentication), IR (Incident Response), MA (Maintenance), MP (Media Protection), PE (Physical and Environmental), PL (Planning), PM (Program Management), PS (Personnel Security), PT (Privacy), RA (Risk Assessment), SA (System and Services Acquisition), SC (System and Communications Protection), SI (System and Information Integrity), SR (Supply Chain Risk Management)

**Your CoreDirective work:** 37 GRC documents include an SSP with 800-53 controls mapped. You can speak to the mapping exercise.

### ISO/IEC 42001:2023 (AI Management Systems)

The AI-specific management system standard. Published December 2023. Think of it as ISO 27001 for AI.

**Core concepts:**
- AI management system (AIMS) — governance structure for AI
- AI system lifecycle — scoping, data, dev, deployment, operation, decommissioning
- Risk assessment specific to AI — bias, explainability, misuse, safety
- Impact assessment — what does this AI do to the humans affected
- Control set — Annex A has organizational, technical, and human-oriented controls

**Why 42001 is underrated:** Most AI risk programs anchor on NIST AI RMF, which is voluntary. 42001 is certifiable. Enterprises that need third-party audit evidence of AI governance will push for 42001 certification over the next 2 years.

**Your angle:** "At CoreDirective the AI Governance policy in our GRC library aligns to both NIST AI RMF and ISO 42001. RMF is the day-to-day risk-thinking framework. 42001 is the structure you'd target if you needed a third-party attestation for clients."
