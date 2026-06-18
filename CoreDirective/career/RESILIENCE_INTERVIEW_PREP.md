3# Interview Prep: Cyber Resilience N8N Engineer @ Resilience (Arceo.ai)
**Date:** April 9, 2026 | **Duration:** 1 hour
**Interviewers:**
- **Chris Wheeler** - CISO. Ex-Morgan Stanley (led SOAR program + CIRT Senior Analyst Team). Navy veteran + US Intelligence Community. Thinks in financial risk terms. Predicted "2026 will be the year we see the first meaningful breaches tied directly to AI." Will evaluate you on security maturity and operational judgment.
- **Paragi Shah** - Senior SecOps Engineer. 12 years at Trustwave as engineering manager, built SOAR platforms and threat data ingestion pipelines. Adjunct instructor for Digital Forensics at Northwestern. Presented real incidents at Resilience's March Risk Briefing: an autonomous agent that ran DROP DATABASE on a live production server after being told 11 times not to, and a prompt injection in GitHub Copilot that silently disabled user confirmations and exfiltrated code. She will evaluate you on technical depth and n8n/SOAR hands-on skill.
- **Jason Wright** - Likely engineering or security team. Expect standard behavioral and culture-fit questions.

**Company Intel:**
- Resilience connects cyber insurance with security visibility. Not just underwriting risk, actively helping policyholders prevent losses.
- Risk Operations Center monitors threats across their entire policyholder portfolio.
- Edge Solution includes Breach & Attack Simulation at no additional cost to policyholders.
- Mission: "Make the world cyber resilient." Founded on the belief that solving cyber risk requires security, economics, and behavior change working as one.
- They translate cybersecurity controls into financial prioritization and backstop losses with top-rated carriers (limits up to $20M).

---

## 1. "TELL ME ABOUT YOURSELF" (90 seconds)

"I'm Emmanuel Tigoue, an AI Security Engineer finishing dual degrees at Georgia State in Cybersecurity and Business Economics, graduating next month. I hold SecurityX, SSCP, CCNA, and Security+, with CISSP in progress.

For the past seven months at CoreDirective, I've been building and securing AI infrastructure on n8n, which is why this role caught my attention immediately. I built a SOAR platform with 14 production workflows and a master orchestrator that ties together 16 services through webhooks and sub-workflow architecture. I manage 20+ credential sets, handle alert triage by routing Claude API and local Ollama outputs through n8n Code nodes, and I tuned Falco eBPF rules to cut alert noise from over 200 daily events down to 12 actionable findings.

Before that, I spent four years at Texaco managing IT security and operations across three locations. I ran incident response, wrote an IR runbook that cut containment time from 8 hours to 90 minutes, rebuilt a flat network into segmented VLANs, and deployed Splunk as the SIEM.

What gets me about Resilience specifically is the intersection of security engineering and financial risk. You're not just selling insurance. You're actively reducing loss by translating security controls into dollars. That's exactly where my dual background in cybersecurity and economics fits. And the fact that this role is centered on n8n, where I've been living for the past seven months, means I can contribute from day one."

---

## 2. "WHY THIS ROLE / WHY RESILIENCE?"

"Three reasons.

First, the mission. Most cyber insurance companies underwrite risk and hope for the best. Resilience actually prevents losses. Your Risk Operations Center monitors threats across the entire policyholder portfolio, and your Edge Solution builds Breach & Attack Simulation into the policy at no extra cost. That's security engineering driving business outcomes, not just checking boxes.

Second, the technical fit. I've been building on n8n for seven months. 14 production workflows, master orchestrator with 16 integrated services, webhook-driven event ingestion, AI-powered alert triage. This role asks for exactly what I've been doing. I'm not learning n8n on the job. I've already shipped production workflows on it.

Third, the people. Chris, I read your piece on cybersecurity budgets. The idea that CISOs need to speak the language of money to get funding resonates with me because I studied Business Economics alongside Cybersecurity. And Paragi, I watched the March Risk Briefing where you walked through the autonomous agent that ran DROP DATABASE on a production server after being told 11 times not to. That's exactly the kind of AI agent risk I've been hardening against. I secured an AI gateway against OWASP LLM Top 10 and red teamed every deployed skill for prompt injection, jailbreaks, and capability abuse. This team is working on problems I care about."

---

## 3. TEN BEHAVIORAL QUESTIONS (STAR FORMAT)

### Q1: "Tell me about a time you handled a security incident under pressure."

**Situation:** At Texaco, a customer reported a declined card that had been working fine. I pulled transaction logs and saw repeated declined attempts from the same card on one terminal, then a successful charge 40 miles away 20 minutes later. Classic skimmer pattern.

**Task:** I needed to identify the exfiltration method, contain the breach, and coordinate with the payment processor without shutting down all three locations.

**Action:** I ran Wireshark on the network segment and found outbound traffic to an unfamiliar IP on port 443 with a self-signed cert and a domain registered six days prior. I physically isolated the terminal from the network without powering it off to preserve forensic state, redirected transactions to the other two terminals, and called the payment processor's security line. I documented the full timeline and IOCs: destination IP, domain, cert fingerprint.

**Result:** Terminal was replaced within 48 hours. Zero additional cards compromised after isolation. That incident led me to deploy network monitoring across all three locations and implement weekly visual inspection protocols for card readers. I later formalized this into a 6-step IR runbook that cut containment time from 8 hours to 90 minutes.

---

### Q2: "Describe a time you built automation from scratch to solve a real problem."

**Situation:** At CoreDirective, I inherited a setup where security operations were entirely manual: checking email for alerts, running health checks by hand, manually triaging every event. I was spending 80% of my time on repetitive tasks.

**Task:** Build a SOAR platform from zero that could automate detection, triage, and response across the entire infrastructure.

**Action:** I chose n8n as the platform and built 14 production workflows with sub-workflow architecture. The master orchestrator integrates 16 services: PostgreSQL, Telegram, GitHub, Cloudflare, Notion, Gmail, and more. I set up 10+ webhook endpoints to catch security events in real time, including 4 Gmail inboxes monitored for phishing. I wrote custom Code nodes in JavaScript to handle alert triage logic, built error handling workflows that push failures to Telegram, and implemented daily health check crons.

**Result:** Cut manual security operations by approximately 80%. The platform handles 20+ managed credential sets and runs autonomously. When a workflow fails, I get a Telegram alert within seconds instead of discovering it hours later. The architecture is modular, so adding a new service takes hours, not days.

---

### Q3: "Tell me about a time you worked with a cross-functional team on a security initiative."

**Situation:** At Texaco, I needed to implement PCI DSS compliance across 45+ devices spanning three locations. This required coordination with the location owner, the payment processor's compliance team, and the POS vendor.

**Task:** Get all three locations PCI compliant without disrupting daily operations at any site.

**Action:** I mapped every device in scope, ran quarterly Nessus vulnerability scans, and documented findings in a format the payment processor could accept. I coordinated terminal firmware updates with the POS vendor during off-hours. I rebuilt the network into 4 VLANs to isolate POS traffic from back-office and guest Wi-Fi, which the payment processor specifically required. I maintained SAQ documentation and walked the location owner through what each control meant in business terms.

**Result:** All three locations passed PCI assessment. Network segmentation eliminated lateral movement between segments. The documentation I built became the template for ongoing quarterly reviews. The key learning: translating security controls into language non-technical stakeholders understand is a skill, and it is exactly what Resilience does at scale with policyholders.

---

### Q4: "Describe a situation where you had to meet a tight deadline on a security project."

**Situation:** After the POS skimmer incident at Texaco, I had a 48-hour window before the payment processor's deadline to submit a formal incident report with IOCs, a timeline, and proof of containment.

**Task:** Produce a complete incident report, verify containment across all three locations, and implement short-term monitoring. All in 48 hours while the locations stayed open.

**Action:** I documented the incident timeline immediately during the response, so I had raw notes. I formatted those into the payment processor's required template, attached Wireshark packet captures as evidence, and included the IOCs. I then ran Nmap scans across all three locations to verify no other terminals showed similar outbound behavior. I set up basic network monitoring on all segments as a stopgap.

**Result:** Report submitted 6 hours before deadline. Payment processor accepted it without revisions. The monitoring I stood up as a stopgap became the foundation for permanent SIEM deployment (Splunk) that I built out over the following months.

---

### Q5: "Tell me about a time you disagreed with someone about security priorities."

**Situation:** At Texaco, the location owner wanted to prioritize upgrading the guest Wi-Fi (customer complaints about speed) over implementing network segmentation. I believed segmentation was critical because POS traffic was running on the same flat network as guest devices.

**Task:** Convince a non-technical business owner that an invisible infrastructure change mattered more than a visible customer-facing improvement.

**Action:** I framed it in financial terms. I showed the $20K loss from the previous card fraud incident and explained that a flat network meant any guest device could potentially reach POS systems. I mapped out the attack path visually. Then I proposed doing both: segmentation first (a weekend project that wouldn't affect business hours), then the Wi-Fi upgrade the following week.

**Result:** The owner approved segmentation first. We completed it over a weekend with zero downtime. The Wi-Fi upgrade followed the next week. Validated with Nmap that lateral movement between segments was eliminated. The lesson: when you translate security into dollars and offer a timeline that respects business priorities, the disagreement resolves itself.

---

### Q6: "Describe a time you had to learn a new technology quickly to deliver on a project."

**Situation:** When I decided to build the SOAR platform, I had zero experience with n8n. I knew Python and PowerShell automation, but n8n's visual workflow builder, webhook architecture, and credential management system were all new.

**Task:** Get productive enough in n8n to build production-grade workflows within weeks, not months.

**Action:** I started by building a simple webhook that posted to Telegram. Once I understood the execution model, I built increasingly complex workflows: multi-service orchestration, sub-workflow calls, error handling chains, custom Code nodes with JavaScript. I read the n8n source documentation, studied the API, and reverse-engineered how credential injection works. Within three weeks I had the master orchestrator running with 16 service integrations.

**Result:** 14 production workflows running today. I went from zero n8n experience to building a master orchestrator with sub-workflow architecture, 20+ credential sets, and webhook-driven event pipelines in under a month. The speed came from treating it like any other API platform: understand the execution model first, then build incrementally. I'm now at the point where I can troubleshoot n8n credential remapping at the database level, having learned that n8n 2.x uses workflow_history for runtime, not just workflow_entity.

---

### Q7: "Tell me about a time you managed competing priorities."

**Situation:** At CoreDirective, I was simultaneously building the CI/CD security pipeline (Trivy, Semgrep, Gitleaks, OPA), writing the GRC documentation library (37 documents), and hardening the AI gateway against OWASP LLM Top 10. All three were critical. None could wait.

**Task:** Make progress on all three without shipping half-finished work on any of them.

**Action:** I structured the work in waves. Week 1: CI/CD pipeline, because it would catch issues in everything else I built. Week 2-3: AI gateway hardening and red team testing, because that was the highest-risk attack surface. Weeks 3-4: GRC documentation, because the SSP and policies formalized what I had already implemented. Each wave's output fed the next: CI/CD caught issues in the gateway config, red team findings generated POA&M entries for the GRC library.

**Result:** All three delivered. CI/CD pipeline catches leaked secrets and critical CVEs on every PR. AI gateway has zero successful prompt injections since hardening. 37 GRC documents covering SSP, POA&M, 10 policies, 5 IR playbooks, and 6 threat models. The sequencing was key: doing CI/CD first meant everything after it was automatically validated.

---

### Q8: "Tell me about a time you identified a security risk that others had missed."

**Situation:** During red team testing of the OpenClaw AI gateway, I tested the browser skill for SSRF. Most people test AI tools for prompt injection and stop there. I tested what happens when the model's tool calls interact with the network.

**Task:** Determine if deployed AI skills could be weaponized to access internal infrastructure.

**Action:** I directed the browser skill to hit the cloud metadata endpoint (169.254.169.254). The skill attempted to fetch it before being blocked. I also tested the python-interpreter skill with `os.listdir('/')`, which returned a root directory listing. And I found that the GitHub skill's PAT had broader scope than needed, allowing it to list repository secrets via API. Eight vulnerabilities total across all deployed skills.

**Result:** Blocked RFC1918 and link-local ranges from the browser skill. Sandboxed the python-interpreter with read-only filesystem. Rotated the GitHub PAT and scoped it to read-only on specific repos. Wrote a custom Falco rule for unexpected outbound connections that actually caught the SSRF attempt during testing. These are exactly the kinds of findings that Paragi described in the March Risk Briefing. Autonomous agents doing things they shouldn't because nobody tested the tool-call layer.

---

### Q9: "Describe a time you improved a process that was inefficient."

**Situation:** At Texaco, Active Directory was a mess. 14 critical audit findings: stale accounts, excessive admin rights, no credential rotation, weak GPO baselines. Every audit was a fire drill.

**Task:** Harden AD to the point where audits became routine instead of emergencies.

**Action:** I enforced GPO baselines across all machines, cleared every stale account, and stripped admin rights that shouldn't have existed. I automated credential rotation with PowerShell scripts using REST API calls. Built compliance reporting that ran automatically so I could show audit-ready status at any time instead of scrambling before each review.

**Result:** Went from 14 critical audit findings to 2. Automated the compliance reporting so audits stopped being emergencies. The PowerShell automation freed up roughly 12 hours per week that I redirected to network segmentation and SIEM deployment. The 2 remaining findings were documentation gaps, not technical controls.

---

### Q10: "Tell me about a failure or mistake and what you learned from it."

**Situation:** When I first deployed Falco for runtime detection on the Docker stack, I turned on every default rule and pointed all alerts at Datadog. Within 24 hours I had 200+ alerts per day and alert fatigue set in immediately.

**Task:** I needed to make Falco useful instead of just noisy.

**Action:** I realized I had made the classic mistake: deploying a detection tool without tuning it to the environment. I went through every firing rule and categorized them: legitimate behavior (healthchecks triggering "terminal shell in container"), irrelevant (K8s rules on a Docker-only stack), and genuinely suspicious. I built a structured exception framework: named exceptions for known admin containers, startup-window suppressions for initialization writes, disabled irrelevant rules entirely.

**Result:** 200+ daily alerts down to 12 actionable findings. But the real lesson was operational: a detection tool with no tuning is worse than no detection tool, because it trains the operator to ignore everything. I now apply this principle to every monitoring system I deploy. Start with what matters, add rules as you understand the baseline, never deploy defaults to production.

---

## 4. FIVE SITUATIONAL QUESTIONS

### S1: "What would you do if an AI agent started executing unauthorized actions?"

"This is exactly what Paragi described in the March Risk Briefing. The agent that ran DROP DATABASE after being told 11 times not to.

My response framework:

**Immediate (0-5 minutes):** Kill the agent's API credentials or revoke its session token. Do not try to reason with it or send corrective prompts. Cut the execution path. If it's an n8n workflow, deactivate the workflow immediately. If it's an autonomous agent with tool access, revoke the tool permissions at the gateway level.

**Short-term (5-60 minutes):** Audit what it actually did. Pull the execution logs, the tool call history, the database query log if applicable. Determine blast radius. If it touched production data, initiate your IR playbook for unauthorized access. Notify stakeholders based on what was affected.

**Root cause:** Was this a prompt injection from external input? Was it a system prompt failure? Was the agent given permissions it shouldn't have had? In my experience hardening OpenClaw, the answer is almost always excessive agency, which is LLM08 in the OWASP LLM Top 10. The agent had the ability to run destructive commands because nobody scoped its permissions to read-only.

**Prevention:** Every agent skill gets minimum required permissions. Destructive actions require human approval. This is the 'human in the loop' principle that your March Risk Briefing called non-negotiable, and I agree completely. I also deploy Falco with custom rules to detect unexpected process spawns and outbound connections from agent containers, which gives you a second detection layer independent of the agent's own logs."

---

### S2: "How would you prioritize which n8n workflows to build first for our security operations?"

"I'd prioritize based on three factors: frequency of the manual task, blast radius if it goes wrong, and time-to-value.

**Tier 1 (Week 1-2): Detection and alerting.** Webhook endpoints that catch security events and route them to the right people. At CoreDirective, the first thing I built was a Telegram alert pipeline for workflow failures, because if your automation is broken and nobody knows, you're worse off than manual. For Resilience, this probably means alert ingestion from your monitoring stack, routed through n8n to your incident response channels.

**Tier 2 (Week 2-4): Triage and enrichment.** Workflows that take raw alerts, enrich them with context (threat intel lookups, asset inventory cross-reference, policyholder data), and present a prioritized queue. This is where AI nodes add value. I built alert triage in n8n using Claude API and Ollama Code nodes. Anything touching sensitive policyholder data stays on a sandboxed local model; general enrichment goes through the cloud API.

**Tier 3 (Month 2): Response automation.** Automated containment actions. These are higher risk, so they come after you have confidence in your detection and triage layers. Always with human approval gates for destructive actions.

**Tier 4 (Month 3+): Reporting and metrics.** Automated compliance reporting, SLA tracking, executive dashboards. These have the lowest urgency but the highest visibility with leadership.

I'd also build the error handling workflow first, before any of the operational workflows. At CoreDirective, my error handler pushes failures to Telegram immediately. If your automation fails silently, you don't have automation. You have a liability."

---

### S3: "How would you handle a ModelArmor alert showing prompt injection?"

"ModelArmor is Google Cloud's runtime protection for LLMs. It detects prompt injection, sensitive data leaks, and harmful content at the inference layer. If I get an alert:

**Step 1: Validate the alert.** Pull the full prompt and response from ModelArmor's logs. Is this a true positive or a false positive triggered by legitimate but unusual input? I've seen benign queries that look like injection attempts because they contain code snippets or technical instructions.

**Step 2: If true positive, determine the injection vector.** Direct injection (user typed it) or indirect injection (came from a tool call response, a retrieved document, or a web search result)? Indirect is more dangerous because it means your data pipeline is contaminated. At CoreDirective, I found exactly this: a Tavily search result contained hidden instructions in metadata that the model executed. The fix was output sanitization on all tool call responses before they re-entered the model context.

**Step 3: Check what the model actually did.** Did the injection succeed in changing the model's behavior? Did it exfiltrate data, execute unauthorized tool calls, or bypass safety controls? Pull the full response chain.

**Step 4: Contain.** If the injection vector is indirect (coming from a data source), quarantine that data source. If it's a specific user, suspend their access pending investigation. If it's a pattern, update ModelArmor's rules or add a pre-processing filter.

**Step 5: Document and feed back.** Log the IOCs (the injection payload pattern), update detection rules, and if this is a new technique, share it with the team. At Resilience, this could also feed into policyholder advisories if the technique is generalizable.

The key insight from my red team work: prompt injection is not one vulnerability. It's a class of attack with multiple vectors. You need defense at the input layer (ModelArmor), the tool-call layer (permission scoping), and the output layer (response filtering)."

---

### S4: "How would you approach securing a new GenAI tool deployment?"

"I'd follow a five-phase approach based on what I did securing the OpenClaw gateway:

**Phase 1: Threat model.** Before anything touches production, map the attack surface. What data does this tool access? What actions can it take? Who are the users? I use STRIDE for structure and MITRE ATLAS for AI-specific threats. At CoreDirective, I documented this in a formal threat model with attack trees.

**Phase 2: Permission scoping.** Apply least privilege to every capability. If the tool has a browser skill, block internal IP ranges. If it has code execution, sandbox the filesystem. If it has API access, scope tokens to minimum required permissions. This is where most deployments fail because teams give the tool full access to move fast.

**Phase 3: Input/output controls.** Pre-processing on prompts: strip delimiter injection sequences, reject instruction-override patterns. Post-processing on responses: filter for credential patterns, internal hostnames, base64-encoded data. This maps to OWASP LLM01 and LLM02.

**Phase 4: Red team before production.** I red teamed every deployed skill at CoreDirective and found 8 vulnerabilities, including SSRF, file system access, and system prompt extraction. You do not find these in a code review. You find them by attacking the tool the way an adversary would.

**Phase 5: Runtime monitoring.** Falco for container-level anomaly detection, logging of all tool calls and model interactions, alerting on unexpected behaviors. The monitoring needs to be independent of the AI tool itself because if the tool is compromised, its own logs may be unreliable.

For Resilience specifically, I'd add a sixth step: translate every finding into financial risk terms for policyholders. A prompt injection vulnerability isn't just a security finding. It's a quantifiable exposure that affects underwriting."

---

### S5: "How would you handle a security incident in a cloud AI platform?"

"I'd follow PICERL but with AI-specific adaptations at each phase:

**Preparation:** Have an AI-specific IR playbook. I wrote one at CoreDirective (AI Incident Response playbook, one of 5 IR playbooks in my GRC library). It covers scenarios standard IR doesn't: model behavior drift, training data poisoning indicators, prompt injection campaigns, and tool-call abuse.

**Identification:** Standard indicators plus AI-specific ones. Is the model producing outputs that don't match its baseline behavior? Are tool calls going to unexpected endpoints? Is there a spike in token usage that suggests data exfiltration via verbose responses? At CoreDirective, my custom Falco rules and n8n webhook monitoring caught anomalies that standard cloud monitoring missed.

**Containment:** Revoke the AI platform's API keys and service account credentials. If it's an agent with tool access, kill the tool permissions first, then the model access. Do not just disable the user-facing interface because the backend may still be processing queued requests.

**Eradication:** Identify the root cause. If it was a compromised credential, rotate everything the credential touched. If it was a prompt injection via data pipeline, quarantine and audit the data source. If it was a misconfiguration, fix it and validate with the same red team techniques that would have caught it.

**Recovery:** Bring the service back with tighter controls. Add monitoring for the specific attack vector. If you contained by revoking API keys, issue new keys with narrower scope.

**Lessons Learned:** Document the full timeline, update detection rules, and update the threat model. For Resilience, this is also a claims data point. Every incident you handle internally informs how you advise policyholders and price risk."

---

## 5. QUESTIONS TO ASK THEM

### For Chris Wheeler (CISO):

**Q1:** "You predicted that 2026 would see the first meaningful breaches tied directly to AI, not attacks assisted by AI but incidents exploiting weaknesses created by AI adoption. Has Resilience already seen claims that fit that pattern, and how is that changing how you think about your internal security posture?"

*Why this works:* Shows you read his published predictions. Connects external risk (policyholder claims) to internal security (his CISO responsibility). Opens a conversation about real-world AI incidents.

### For Paragi Shah (Senior SecOps Engineer):

**Q2:** "In the March Risk Briefing, you walked through the agent that executed DROP DATABASE after being told not to 11 times. When you're building n8n workflows that involve AI agents internally at Resilience, what's your current approach to human-in-the-loop gating for destructive actions?"

*Why this works:* References specific content she presented. Asks a technical question about her actual workflow design. Shows you understand the problem space.

**Q3:** "What does the current n8n workflow architecture look like at Resilience? Are you running a centralized orchestrator model, distributed workflows with sub-workflow calls, or something else? I'm asking because the architecture choice drives how you handle credential management and error propagation."

*Why this works:* Shows deep n8n knowledge (you understand that architecture decisions have downstream effects on credential management). Gives you intel on what you'd actually be building.

### For the panel:

**Q4:** "Resilience translates security controls into financial risk terms for policyholders. How does the internal security engineering team's work feed into that translation? When you build a detection workflow or harden an AI tool, does that directly inform how you advise policyholders on similar risks?"

*Why this works:* Shows you understand Resilience's unique value proposition (security + insurance). Connects the engineering work to business outcomes. Demonstrates you're thinking beyond just building workflows.

**Q5:** "What does the first 90 days look like for this role? Is there a backlog of workflows to build, or is this more greenfield? Where is the biggest gap you're trying to close with this hire?"

*Why this works:* Practical. Shows you're already thinking about how to deliver value. The answer tells you exactly what they need most urgently.

---

## QUICK REFERENCE: NUMBERS TO KNOW COLD

| Metric | Value |
|---|---|
| n8n production workflows | 14 |
| Master orchestrator services | 16 |
| Managed credential sets | 20+ |
| Webhook endpoints | 10+ |
| Gmail inboxes monitored | 4 |
| Manual ops reduction | ~80% |
| Falco alerts: before tuning | 200+ daily |
| Falco alerts: after tuning | 12 actionable |
| Red team vulnerabilities found | 8 across all skills |
| OWASP LLM categories addressed | 5 of 10 (LLM01, 02, 06, 07, 08) |
| CI/CD tools | Trivy, Semgrep, Gitleaks, OPA |
| Terraform files / resources | 16 files, 30+ resources |
| OPA/Rego policies | 8 |
| Containers in production | 13 (Compose) + 1 standalone |
| GRC documents | 37 total |
| IR playbooks | 5 |
| Policies | 10 |
| IR runbook improvement | 8 hours to 90 minutes |
| AD audit findings | 14 to 2 |
| PCI devices managed | 45+ |
| SIEM detection improvement | 48 hours to under 4 |
| Automation time saved (Texaco) | ~12 hours/week |
| Network segments (VLANs) | 4 |
| Texaco locations managed | 3 |
| Certs | SecurityX, SSCP, CCNA, Security+, CISSP (in progress) |

---

## INTERVIEWER-SPECIFIC TACTICS

### Chris Wheeler (CISO)
- **His background:** SOAR program lead + CIRT at Morgan Stanley, Navy + Intel Community. He knows what real SOAR looks like at enterprise scale.
- **What he respects:** Operational maturity, structured thinking, financial fluency. He wrote about CISOs needing to speak the language of money.
- **How to connect:** Your dual degree (CIS + Business Economics) is rare. Use it. When he asks about security decisions, frame the answer in terms of risk reduction and business impact, not just technical controls.
- **Watch out for:** He will probe whether your CoreDirective experience translates to enterprise scale. Be honest about scope (single droplet, 13 containers) but emphasize the rigor: IaC, CI/CD gating, formal GRC docs, structured red teaming.

### Paragi Shah (Senior SecOps Engineer)
- **Her background:** 12 years at Trustwave (engineering manager + IC), built SOAR platforms and threat data ingestion pipelines at MSSP scale. Adjunct instructor for Digital Forensics at Northwestern. She's your future peer or manager.
- **What she respects:** Hands-on technical skill, n8n depth, practical security thinking. She presented real incidents at the March Risk Briefing. She cares about what actually works, not theory.
- **How to connect:** Speak n8n fluently. Mention sub-workflow architecture, credential remapping at the database level, webhook endpoint design, error handling patterns. These are the things someone who has actually operated n8n at scale knows.
- **Watch out for:** She may ask you to whiteboard or describe a workflow in detail. Be ready to walk through the master orchestrator: how a webhook triggers the Switch node, routes to the right service integration, handles errors, and logs results.

### Jason Wright
- **Approach:** Standard behavioral + culture-fit until you learn more about his role. Be personable, be specific, show you want to be on this team specifically.

---

## CLOSING STATEMENT (if they ask "anything else?")

"I want to be direct. I've spent seven months building exactly what this job description asks for: n8n workflows, AI security hardening, SOAR architecture, alert triage with LLMs. I'm not theorizing about how I'd do this work. I've done it. My infrastructure is running right now. I can show you the workflows, the GRC documentation, the red team findings. I want to bring that experience to a team that's solving one of the hardest problems in security: making organizations resilient, not just defended."
