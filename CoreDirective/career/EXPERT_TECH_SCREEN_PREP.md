# Expert Technical Solutions Screen — Paul Adams

**Role:** Security Engineer, 100% remote, payment processing client
**Stack:** Splunk, Python, AWS, AI platforms
**Comp posted:** up to $110k (low for the stack — do NOT anchor here)
**Stage:** Recruiter screen. NOT technical. Paul is a salesperson, not a blue team lead.

---

## 1. What Paul Will Actually Ask

1. Current work status and availability
2. Location and remote setup
3. Work authorization (US citizen, no sponsorship needed)
4. Salary expectations
5. Quick stack confirmation (Splunk, Python, AWS, AI — yes to all)
6. Why you're looking
7. Anything you're wrapping up with a current employer

That is it. 15 to 25 minutes, conversational.

---

## 2. Your 30 Second Pitch (Memorize This)

> I'm a security engineer with a focus on AI and cloud security. My background is detection engineering, incident response, and GRC on a full DigitalOcean and AWS stack I run myself. CISSP in progress, SecurityX, SSCP, CCNA, and Security Plus already done. Currently finishing a BBA and looking to move into a full time AI security or cloud security role where I can build detections, automate response, and harden LLM and API workloads. Payment processing is a strong fit because I have hands on PCI DSS scoping, Splunk detections, and AWS security work.

Say it out loud three times before the call. That is your opener when he says "tell me about yourself."

---

## 3. Stack Confirmation Answers — The Heart of the Call

**This is the section that matters most.** Paul told you the role is Splunk, AWS, and scripting heavy. He will confirm each one. Give him short confident answers with a concrete hook. Do NOT ramble. Each answer is 15 to 25 seconds max.

---

### Splunk

**30 second answer:**
"Yes, Splunk is part of my daily toolkit. I use it for detection engineering and incident response. I write SPL for correlation searches, tune indexes, onboard new data sources, and build dashboards. My detection work focuses on auth anomalies, failed login bursts, suspicious S3 and IAM API activity, and lateral movement patterns. I also work with the Common Information Model and field extractions when normalizing log sources."

**Key vocabulary to drop (recruiters listen for these exact words):**
- SPL (Search Processing Language)
- Correlation searches
- Data models and CIM (Common Information Model)
- Index and sourcetype configuration
- Field extractions
- Dashboards and forms
- Alert tuning and false positive reduction
- ES (Enterprise Security) if asked — say "I've worked with ES notables and risk based alerting"

**If he asks for an example:**
"One I can share — I built a detection in Splunk for anomalous AWS API activity. The search pulled CloudTrail events, looked for high volume IAM or S3 calls from a principal that normally did not touch those services, and fired a notable. I tuned it over a couple weeks to cut false positives from IAM role assumptions and automated scanners."

---

### AWS

**30 second answer:**
"AWS is the cloud I know best. I work across Security Hub, GuardDuty, CloudTrail, IAM, KMS, VPC flow logs, and S3 access logs. On the infrastructure side I write Terraform, use OPA for policy as code, and run Checkov and Trivy for security scans in my pipelines. I treat IAM as the control plane — least privilege, role based access, no long lived keys where I can avoid it."

**Key vocabulary:**
- Security Hub, GuardDuty, Config, CloudTrail, Inspector
- IAM roles, policies, SCPs (Service Control Policies)
- KMS for encryption at rest, TLS for in transit
- VPC flow logs into SIEM
- S3 bucket policies, public access block, versioning, MFA delete
- Least privilege, just in time access
- Terraform, Checkov, OPA, Cosign, SBOM

**If he asks for an example:**
"I built a Terraform stack for my own infrastructure and ran it through a Checkov and OPA pipeline. Every PR gets scanned, Trivy catches container vulns, Gitleaks catches secrets, and Cosign signs the images before they ship. The same pattern applies to client environments — security gates at PR time instead of prod time."

---

### Scripting (Python Primary)

**30 second answer:**
"Python is my daily scripting language. I use it for detection logic, automation, log parsing, and API integration. I also write bash for ops work and SPL for Splunk. On the automation side I tie things together with n8n as a SOAR layer, so I can chain Python scripts, Splunk alerts, and response actions into one workflow."

**Key vocabulary:**
- Requests, boto3, json, csv, re (regex), logging
- Parsing CloudTrail, VPC flow logs, Splunk exports
- API integration with Splunk, AWS, Datadog, ServiceNow, Jira
- SOAR / workflow automation
- Infrastructure as code helpers

**If he asks for an example:**
"I built an AI incident response assistant in Python as a capstone project. It takes an incident description, pulls relevant log context from the SIEM, runs it through an LLM with guardrails, and returns a recommended containment plan mapped to the NIST 800 61 phases. It is not a replacement for a real responder, it is a first pass summary to save the analyst 20 minutes on a page."

---

### AI Platforms (Bonus Differentiator)

**30 second answer:**
"I work on LLM security directly. Prompt injection testing, OWASP LLM Top 10 coverage, guardrails around Claude and Ollama deployments, and API abuse prevention. I run a self hosted LLM gateway so I understand the infrastructure side as well as the policy side. I also wrote an AI governance policy and an AI incident response playbook as part of my GRC library."

**This is your unfair advantage over other Splunk / AWS candidates.** Most of them do not do LLM security. Lean into it briefly if the conversation gives you space.

---

## 4. Salary Question — Play This Soft, Get The Offer

Paul will ask "what are you looking for." Your answer:

> "I'm flexible and focused on finding the right fit. The posting mentioned up to 110, which works for me. If there's flexibility based on the stack fit I'm open to that conversation, but I don't want comp to be the blocker. I'd rather get in front of the client and let the fit speak for itself."

Why this wording:
- "Flexible" signals you are easy to work with, which is what recruiters want to hear.
- "Works for me" removes the objection immediately so Paul feels safe submitting you.
- You leave the door cracked open for more without demanding it.
- "Don't want comp to be the blocker" is a phrase senior candidates use. It sounds confident.

**Do not volunteer a higher number. Do not negotiate on this call.** Negotiation happens at the offer stage with the client, not with the recruiter. Your job on this call is simple: be the candidate Paul cannot wait to send over.

If Paul himself says "the client might flex for the right person," then and only then say: "Appreciate that. I'd be thrilled with 110 and if there's room to discuss we can revisit once we've had the technical rounds." That is it. Do not push further.

**Real talk:** A confirmed $110k offer in hand beats any $150k role you are still chasing. Take the offer, cash a paycheck, then look for the next jump in 12 months. You are not in a position to be picky and Paul can smell desperation if you try to act like you are. Stay warm, stay easy, stay employable.

---

## 5. Why You Are Looking

**Safe version, use this verbatim:**
"I'm finishing my BBA in May 2026 and actively transitioning into a full time AI security engineering role. My recent work has been project and contract based, which gave me hands on range across Splunk, AWS, and LLM security, and now I'm ready to bring that into a full time seat on a security team."

Rules:
- NEVER say "unemployed" or "between jobs" or "laid off"
- NEVER say how long you have been out
- NEVER sound desperate, even if you feel it
- "Project and contract based" is TRUE and it reframes the gap as intentional
- "Ready to bring that into a full time seat" closes the loop for Paul

If he asks "how soon can you start" the answer is: "I can start within two weeks of an offer." Not "immediately." Immediately sounds desperate. Two weeks sounds professional.

---

## 6. Questions to Ask Paul (Always Have Two Ready)

1. "What does the client's interview loop look like? Technical screen, panel, take home?"
2. "What would make a candidate stand out for this specific req? What is their dream hire?"

Bonus if the call is going well:
3. "Beyond this role, what other security engineering reqs are you working on right now? Specifically AI security or cloud security?"

---

## 7. What Paul Will NOT Ask (Leave the Resilience PTSD at the Door)

He will NOT ask:
- Walk me through an IR in Splunk
- How would you investigate a compromised EC2 instance
- What is the difference between a SIEM and a SOAR
- Explain the MITRE ATT&CK chain for a ransomware event
- Write me a SPL query on the spot

Those are CLIENT technical round questions. Separate call, separate day, separate prep. Not today.

---

## 8. If He Surprises You With Something Technical

Only if he does, which is unlikely. Rule: answer in ONE sentence, then pivot to experience.

Example:
> "For IR in Splunk I follow the NIST 800 61 lifecycle: identify, contain, eradicate, recover. In practice that means pulling the indicator into a search, pivoting across authentication, network, and endpoint indexes, then building a timeline. I did this most recently when I set up detection for suspicious API calls on my own AWS environment."

That is the pattern: framework, process, concrete example. Framework first so you do not blank, then the example anchors it.

---

## 9. Logistics Checklist (Before the Call)

- [ ] Quiet room, headphones, good mic
- [ ] Resume open in a second tab (Emmanuel_Tigoue_AISecurity_Engineer.pdf)
- [ ] Portfolio open: et-sec.github.io/portfolio
- [ ] LinkedIn open to your profile in case he references it
- [ ] Glass of water
- [ ] Notepad for his contact info, client name, and next step
- [ ] Calendar open so you can book the client round on the spot

---

## 10. After the Call

Within 1 hour, send Paul a LinkedIn DM:

> Hey Paul, thanks for the quick call. Appreciate the context on the role and the client. Looking forward to next steps. Let me know if you need anything else from me on my end.

Then log the conversation. Client name, comp band he confirmed, timeline, next step.

---

## Bottom Line

You are not walking into another Resilience. This is a 20 minute sales call where the recruiter wants you to succeed because it pays him. Speak in short confident sentences. State your comp target. Ask two questions. Hang up.

You got this.
