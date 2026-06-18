# Amex HM Screen — 20 Likely Questions + Model Answers

Expected timeline: HM invite arrives within 5-7 business days of submission (April 28 to April 30). Call length: typical 45-60 minutes. Mix of behavioral + technical.

HM name: TBD within TRIS Cybersecurity Engineering.

---

## Opening — The First Three Minutes

### Identity (never hedge)
"Emmanuel Tigoue. Application Security Engineer at CoreDirective in Atlanta."

### The 60-Second Opening Pitch

"I'm an Application Security Engineer at CoreDirective. My day-to-day is DevSecOps end-to-end — shift-left CI/CD with Trivy, Semgrep, Gitleaks, and OPA policy gates on every pull request, Cosign for image signing, Syft for SBOM generation, and OWASP ZAP for authenticated DAST against our production SOAR. I eliminated every exposed public port by routing traffic through Cloudflare Zero Trust with mTLS. I tuned Falco eBPF runtime detection from 200 alerts per day to 12 actionable findings. And I authored 37 GRC documents mapped to NIST 800-53 Rev 5, including a System Security Plan, ten security policies, five incident response playbooks, and a documented tabletop exercise.

Before CoreDirective I ran IT Security and Operations at Texaco in Atlanta for nearly four years. Managed across three retail locations, ran the PCI DSS program that dropped critical audit findings from 14 to 2, built the Splunk SIEM that cut mean time to detect from 48 hours to under 4, and wrote the IR runbook that reduced containment time from 8 hours to 90 minutes.

I'm finishing my BBA in Cybersecurity at Georgia State in May. CISSP sitting before end of April. Current certs: SecurityX, SSCP, CCNA, Security+. Eligible for security clearance.

I'm on this call because the AppSec contract at Amex maps directly to what I do today — shift-left pipeline, vendor SDLC review, architecture review, and the governance documentation that wraps it. The regulatory register — OCC supervision through AENB, CRI Profile alignment — is a context I'd bring working discipline to from day one."

**Pacing:** 70-80 seconds. Ends with two Amex-specific signals (OCC, CRI Profile) to demonstrate homework.

---

## Part 1 — 20 Likely Questions with Model Answers

### Behavioral (expect 4-6 of these)

#### 1. "Tell me about yourself."

Deliver the 60-second pitch above. Stop. Let HM drive.

#### 2. "Why Amex?"

(From `02_ROLE_FIT.md` — memorized)

"Three reasons. One, Amex is a premium brand operating a closed-loop network — which means the business model and the data custody relationship with customers are tighter than open-loop competitors. That tighter control makes AppSec work consequential. Two, the regulatory context — OCC supervision through AENB means the audit discipline is real, and the AppSec controls I build produce evidence that holds up under examiner review. I'd rather work in an environment where controls matter than one where they're theater. Three, TRIS under Gleb Reznik is fresh leadership — priorities are being re-set and there's investment going into the cybersecurity function. Joining at this moment means the work has upward trajectory, not maintenance trajectory."

#### 3. "Which Blue Box Value resonates most with you and why?"

(Pick one, weave a real story. HM scores against this.)

"Do What's Right. A couple years back at Texaco, the managed services vendor and the PCI auditor both endorsed quarterly Nessus scans and a 90-day patch cycle. That met the minimum, but we'd just worked a POS skimmer incident where the exploit-to-in-the-wild window on similar CVEs was 18 days. 90-day patching meant we'd knowingly be exposed for 72 days after exploits were published. I pushed back with data, proposed a staged monthly scanning + 30-day critical SLA with patch windows timed to off-peak retail, got buy-in from the GM, and dropped critical audit findings from 14 to 2 in eight months. The easy move was to accept the vendor recommendation. The right move was to push for what the data actually supported. That's what Do What's Right looks like operationally — not a slogan, but what you do when nobody is watching."

#### 4. "Tell me about a time you came up with a creative solution."

"At CoreDirective, our SOAR needed to triage sensitive security alerts — credential rotation checks, compliance drift monitoring, incident escalations. Standard practice would be routing everything through Claude API or a commercial LLM for summarization. The issue: some of those alerts contained PII or secret data that I wasn't comfortable sending to a third-party model.

The creative solution was a layered architecture. NVIDIA NeMo sandboxed local inference for anything touching sensitive data — NeMo never leaves our infrastructure. Ollama running locally for low-sensitivity classification. Claude API via our OpenClaw gateway only for non-sensitive contextual analysis. Each layer has defined data classification criteria; the triage workflow routes alerts based on content sensitivity, not on what tool was most convenient.

Result: 80 percent reduction in routine triage overhead with zero sensitive data ever leaving our environment. For an organization like Amex where regulated data handling is non-negotiable, that architecture pattern translates directly."

#### 5. "How comfortable are you working with people from different lifestyles and cultures?"

"I'm from Gabon originally — moved to the US for college. I've worked in retail at Texaco where teams included first-generation Americans, long-tenured locals, and international transfers. At CoreDirective I collaborate with engineers across time zones. Weekly I stream content to audiences that span every experience level from curious high schoolers to senior practitioners. Working across lifestyles and cultures is baseline for me, not a stretch. Amex Phoenix with 7-9 thousand people in Technology, Risk, Cybersecurity — that's a fit, not a concern."

#### 6. "What is the name of the CEO at American Express?"

"Stephen J. Squeri. Chairman and CEO since February 2018."

**Just the answer. Do not elaborate unless asked to.** This question tests prep, not analysis.

---

### Technical (expect 6-8 of these)

#### 7. "Walk me through how you'd threat model a card-not-present payment flow using STRIDE."

See `03_TECHNICAL_PREP.md` Part 1 for full STRIDE-on-payment-flow walkthrough. Deliver in 90 seconds. Lead with trust boundaries, end with PCI DSS crossover.

#### 8. "You're running SAST on every pull request and developers are pushing back because they're getting too many false positives. What do you do?"

(From `03_TECHNICAL_PREP.md` Part 6 Q4)

"Five-step method. Reproduce locally to confirm the finding is real. If real, assess reachability — is the vulnerable code path actually reachable in production. If reachable, assess exploitability — authentication required, input validated upstream, mitigating controls in place. Document the analysis either confirming remediation or marking false positive with reasoning trail preserved. If it's a false positive, tune the scanner rule so the same flag doesn't repeat.

The meta-point: signal-to-noise determines whether developers engage with findings or tune them out. At CoreDirective, Falco went from 200 alerts a day — which meant developers ignored all 200 — to 12 actionable, which meant every finding got investigated. Same principle for SAST. Gates that produce noise lose trust; gates that produce signal keep trust."

#### 9. "What's your experience with Burp Suite and offensive testing?"

"Burp Suite I've used for intercept, repeater, and intruder — manual chaining of findings like XSS into CSRF into account takeover. OWASP ZAP is my primary DAST tool — authenticated scans against production services with verified zero injection vulnerabilities across 8 OWASP attack categories at CoreDirective. Nmap I use for network validation — I segmented Texaco's network into 4 VLANs and validated with Nmap.

Honest: I'm not an offensive security specialist. Not OSWE or GXPN. For a role where pen-testing is primary work, someone with those credentials is a better hire. For shift-left AppSec where offensive validation is a quarterly check rather than daily work, I'm a fit."

#### 10. "How do you decide which SAST findings to prioritize?"

"Three axes. One, exploitability — what's the likelihood this vulnerability is actually reachable and exploitable in the current architecture. Two, impact — what's the blast radius if exploited. Three, remediation cost — how hard is it to fix.

CVSS gives me a score baseline. I weight it with our specific context — a reachable SQL injection in an internet-facing auth service outranks a theoretical XSS in an internal admin tool, even if CVSS scores are similar. I publish the prioritization framework so developers understand why their finding ranked where it did, and so the decisions survive audit scrutiny."

#### 11. "What's the difference between SAST, DAST, SCA, and IAST?"

"Four different lenses. SAST — static application security testing — scans source code or binaries without running them. Good at finding patterns like hardcoded credentials, obvious injection sinks, insecure crypto. Fast, shifts left naturally. Tools: Snyk Code, Semgrep, Checkmarx.

DAST — dynamic application security testing — tests the running application by sending attacks. Good at finding runtime behavior, auth bypasses, business logic flaws SAST misses. Slower, requires deployed environment. Tools: Burp, OWASP ZAP, Invicti.

SCA — software composition analysis — scans dependencies for known CVEs. Good at catching vulnerable libraries. Tools: Snyk Open Source, Trivy, Dependabot.

IAST — interactive application security testing — hybrid, instruments the running app to see SAST-style findings in the flow. Good for catching issues SAST and DAST individually miss. Tools: Contrast, Seeker.

Mature AppSec programs run all four plus runtime protection. Each catches what the others miss."

#### 12. "What's the CRI Profile and how does it relate to NIST CSF?"

"CRI Profile is the Cyber Risk Institute's financial-sector extension of NIST CSF. It maps the CSF functions — Govern, Identify, Protect, Detect, Respond, Recover — to specific control statements that address bank-sector regulatory requirements from OCC, FFIEC, BSA/AML, PCI DSS, SOX, GLBA. It reduces duplicative compliance work across regulators because the same evidence supports multiple examination regimes.

Amex references CRI Profile in the 10-K as the cybersecurity maturity framework. For a TRIS AppSec role, aligning application security controls to CRI-specific statements is the audit register, not generic CSF."

#### 13. "Describe your experience with OAuth 2.0 and JWT security."

"Pitfalls to watch for: alg:none attacks where attacker strips signature and sets algorithm to none, kid header confusion where attacker controls key identifier, HMAC-vs-RSA confusion that lets RSA public keys be used as HMAC secrets, missing audience and issuer validation, missing expiry enforcement.

Mitigations in a production deployment: strict algorithm whitelisting — RS256 or ES256, never HS256 or none. JWKS endpoint for public key rotation. Audience and issuer validation mandatory on every token validation. Short access token lifetimes — 15 minutes typical — with refresh tokens rotated on every use. Token binding to client_id. DPoP (demonstrating proof of possession) for sensitive flows.

For bank-sector OAuth specifically, scope hygiene is non-negotiable — tokens grant only the minimum permissions needed, scope boundaries reviewed quarterly, anomaly detection on bulk API activity. That last point is where the Salesloft Drift OAuth supply-chain incident landed industry-wide."

#### 14. "Have you worked with containers, Kubernetes, or GKE?"

"Containers yes, daily. Docker for local dev, CoreDirective production workloads run on DigitalOcean Kubernetes-equivalent with Docker images. Trivy scans every container build. Cosign signs every production image. Syft generates SBOMs.

GKE specifically I haven't operated in production. From the published Amex stack — GKE plus Istio plus Go microservices — I'd expect ramp on GKE Workload Identity, Binary Authorization, Config Connector, and Istio service mesh patterns. That's a week to solid fluency, given the fundamentals transfer from generic Kubernetes."

---

### Situational / Judgment (expect 3-5)

#### 15. "You find a critical vulnerability in a production payment microservice. What's your next 24 hours?"

"Hour one: validate and scope. Confirm it's real, reproduce in a controlled way, document the CVE or CWE classification, CVSS score, exploitability assessment, affected data types, business impact estimate.

Hours two to four: contain. Can I deploy a compensating control quickly — WAF rule, egress block, feature flag disabling the vulnerable code path? If yes, deploy that to reduce the exposure window. If no, escalate to service owner for a take-down decision.

Same-day: escalate. Notify TRIS leadership plus application owner plus legal plus privacy. If the vulnerability could have been exploited to expose cardholder data, trigger the incident response process formally. For Amex specifically, regulatory notification readiness starts now — OCC supervisor, state AGs — do not wait for confirmed exploitation.

24 hours: fix plan. Remediation owner assigned, patch or code fix in progress, test plan defined, rollback plan documented in case the fix breaks production, evidence capture for the audit trail.

Documentation throughout. Every decision logged. A clean fix with no paper trail fails post-incident review under OCC examination."

#### 16. "A vendor we integrate with just disclosed a breach. Walk me through your response."

See `03_TECHNICAL_PREP.md` Part 5 for the full 90-second answer. Key beats: hour-zero inventory, day-one scope, day-one to three notification, week-one remediation including token rotation, month-one fraud mitigation.

#### 17. "You disagree with a hiring manager on a security control decision. What do you do?"

"Three-step default. One, seek to understand their position fully — what are the business constraints, operational realities, customer impacts they're weighing. Two, make my case with data — not opinion, specific risk quantification or precedent from similar incidents. Three, if we're still at impasse after that, escalate on the record — document the disagreement, surface to the next level with both positions stated clearly, and accept the final decision without re-litigating.

The key discipline is: I don't confuse disagreement with insubordination, and I don't confuse agreement with correctness. At Texaco I pushed back on the 90-day patch cycle over multiple conversations, with data, and eventually got buy-in. If the GM had said 'no, we're keeping 90 days,' I would have documented my concern in the audit trail and executed the 90-day policy faithfully. That's Win as a Team — you can disagree internally and still deliver externally."

#### 18. "Tell me about a time you had to say 'no' to a business request."

"Accounting team at CoreDirective wanted to deploy a new AI-assisted invoice processing workflow. The proposed vendor stored data in a jurisdiction we hadn't reviewed, had a SOC 2 Type 1 report not Type 2, and hadn't disclosed training data retention practices.

I said no to the deployment as-proposed. I didn't stop there — I offered a path forward. Requirements before I'd approve: SOC 2 Type 2 report within 90 days, contractual opt-out from training on our data, data residency constrained to approved jurisdictions, Data Processing Agreement with breach notification within 48 hours. I documented the requirements in a vendor risk memo, shared with the accounting owner, and gave them a timeline.

The vendor met three of four requirements. We went with them on a pilot, not production. Business need satisfied, security posture preserved. That's a 'no' that doesn't kill velocity — it redirects it."

---

### Culture / Fit (expect 3-5)

#### 19. "How do you handle multiple parallel priorities?"

"Written prioritization. Every Monday I draft a week-ahead with outcomes ranked by risk impact and deadline. Running doc where I log blockers and dependencies so status-meeting overhead drops. Over-communicate when something slips — early, not late. I've managed parallel streams at Texaco across three retail locations simultaneously while completing school, and at CoreDirective shipping 37 GRC documents plus infrastructure plus detection engineering inside seven months. Volume isn't the issue. Disorganization is the issue that volume exposes."

#### 20. "What questions do you have for me?"

Use `05_QUESTIONS_FOR_THEM.md` — pick 3-4 based on conversation flow.

---

## Part 2 — Close Sequence

### At 40-45 minutes — ask for next step

"What does the process look like from here? Is there a panel round, who would I meet, and what's the realistic timeline to offer?"

### The honest-uncertainty close

"Based on what we've talked through, is there anything that leaves you uncertain about me for this role? I'd rather surface it now than leave it unsaid."

### Post-call follow-up (within 2 hours)

Subject: `Thanks for the time today — Emmanuel Tigoue`

```
[HM name],

Thanks for the conversation today. Three things that landed for me:

1. [Specific thing HM said — concern raised, project mentioned, priority]

2. On [any topic where I acknowledged a gap — Burp depth, Go fluency,
   Snyk specifics], I'm putting time in this week to sharpen.

3. [Something the team or role does that's genuinely interesting]

Let me know what next step looks like. Happy to share artifacts if
that's useful — SSP or IR playbook samples that touch what we
discussed.

Emmanuel
```

**Tone rules:** human, direct, specific. No em dashes. No "I'm passionate." Short paragraphs. 130 words max.

---

## Part 3 — Day-Of Logistics

**Before the call:**
- Re-read this file + `02_ROLE_FIT.md` + `01_COMPANY_INTEL.md` section 6 (2024 breach)
- Voice memo the 60-second pitch x2 morning-of
- Index card visible from `00_INDEX.md`
- Water, clean shirt, quiet room, Teams or Zoom tested
- Phone DND, notepad + pen visible

**At the call:**
- Enter 2 minutes early
- Smile before speaking — changes voice even audio-only
- Energy at 7/10, measured
- Answer in PSC (Problem, Specifics, Consequence) — 45-90 seconds per answer
- Pause before answering instead of filling — confidence signal

**After the call:**
- Send follow-up within 2 hours
- Update memory file + Amex_AppSec tab with outcomes
- If moving forward: begin panel-round prep
