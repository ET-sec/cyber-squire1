# Threat Modeling Interview Expectations, USD 200K Bar

Reference document. What a real USD 200K threat modeling round looks like, drawn
from Adam Shostack's published methodology, the OWASP Threat Modeling Cheat Sheet,
Microsoft's STRIDE process, Trail of Bits' approach, and Ross Anderson's *Security
Engineering*. Sources cited inline. `[UNVERIFIED]` marks paraphrased material.

---

## 1. The Frameworks the Interviewer is Mapping You Against

### 1.1 Shostack's Four Question Framework
1. What are we working on?
2. What can go wrong?
3. What are we going to do about it?
4. Did we do a good enough job?

Source: Adam Shostack, *Threat Modeling: Designing for Security* (Wiley, 2014);
the Four Question Framework GitHub.
https://github.com/adamshostack/4QuestionFrame
https://shostack.org/resources/threat-modeling

Shostack's explicit guidance is to time-box a session ("up to an hour, then we
stop") so candidates who try to cover everything in a 40-minute interview round
are signaling they have not run a real session. Source:
https://courses.shostack.org/pages/intensive-222

### 1.2 STRIDE
A mnemonic that pairs to classic security properties:

| STRIDE | Violates |
|--------|----------|
| Spoofing | Authentication |
| Tampering | Integrity |
| Repudiation | Non-repudiation / Accounting |
| Information Disclosure | Confidentiality |
| Denial of Service | Availability |
| Elevation of Privilege | Authorization |

Source: Microsoft Secure Development Lifecycle; OWASP Threat Modeling Cheat Sheet.
https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html

### 1.3 OWASP Threat Modeling Cheat Sheet, four phases
1. System Modeling (DFD, trust boundaries, data flows, processes, stores,
   external entities).
2. Threat Identification (apply STRIDE per element).
3. Response and Mitigations (Mitigate, Eliminate, Transfer, Accept).
4. Review and Validation.

Source:
https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html

### 1.4 Trail of Bits' approach
Trail of Bits publishes pragmatic threat modeling write-ups on the audit
engagements they run. Their bar: name specific real-world failures in the same
class of system, do not stay at the framework level. Reference: Trail of Bits
publications (audit reports on Cosmos, Solana, Compound, Optimism, etc.).
https://github.com/trailofbits/publications

### 1.5 Ross Anderson, *Security Engineering* (3rd ed., 2020)
Anderson's framing is mechanism plus economics: the right control depends on the
adversary's incentives and the cost of bypass. Senior interviewers reach for this
when a candidate proposes a control that is cryptographically sound but
operationally absurd or commercially irrelevant.
Reference book and free PDF: https://www.cl.cam.ac.uk/~rja14/book.html

---

## 2. The 40-Minute Round, Minute-by-Minute

A typical USD 200K threat modeling round runs 40 to 45 minutes. Here is what an
interviewer expects you to do in each segment, synthesized from Shostack's
intensive course material, the OWASP cheat sheet, and Exponent's senior security
engineer prep guide.
https://www.tryexponent.com/blog/security-engineer-interview-prep

### 2.1 First 5 minutes: scope the system

What the interviewer wants:
- Restate the prompt in your own words.
- Ask three to five clarifying questions: who are the users, what is the data
  classification, what is the deployment topology, what are the regulatory
  constraints, what is the threat model the org has already adopted.
- Decide what is in scope. Explicitly mark what is out of scope. ("I am going to
  treat the IdP as trusted today. I will note it as a dependency.")
- Sketch a Data Flow Diagram with users, processes, data stores, external systems,
  and trust boundaries. Use the standard DFD shapes (rectangle for external,
  circle for process, two parallel lines for data store, arrows for data flow,
  dotted lines for trust boundaries).

What gets candidates downgraded here:
- Diving into controls before the system is sketched.
- Assuming the architecture instead of asking.
- Drawing pretty boxes without trust boundaries. The trust boundary is the
  signal of a senior threat modeler.

### 2.2 Minutes 5 to 30: enumerate threats per element

What the interviewer wants:
- Walk the DFD element by element. For each, apply STRIDE and call out what
  applies.
- Name specific attacks, not generic threat categories. "Information disclosure"
  is undergrad. "An unauthenticated GET against the metadata endpoint exfiltrates
  the IAM role credentials, which the attacker uses to enumerate S3" is senior.
- Reference real incidents. Capital One 2019 SSRF. Codecov 2021 build-time
  exfiltration. Solarwinds 2020 build pipeline. Snowflake 2024 customer credential
  reuse. Anthropic Claude Skills risks (2026 emerging). MCP server compromise
  cases in MITRE ATLAS January 2026.
- Group threats by likelihood and impact. The OWASP cheat sheet recommends DREAD
  or CVSS-style scoring; senior candidates are pragmatic about scoring rather
  than dogmatic.

What gets candidates downgraded here:
- Reciting STRIDE without applying it ("we should consider spoofing"). Apply it.
- Skipping repudiation and elevation of privilege. Most candidates skip these.
- Treating every threat as equally likely.
- Not noting which threats they will not chase, and why.

### 2.3 Minutes 30 to 40: mitigations and trade-offs

What the interviewer wants:
- For each top threat, propose a mitigation and name the alternative response
  (Mitigate, Eliminate, Transfer, Accept) per OWASP.
- Explicit trade-offs. "Mutual TLS between services raises the bar for spoofing
  and tampering. It costs us 3 to 8 ms per call and a cert rotation pipeline. I
  would do it for the data plane, not for the control plane in this design."
- A rough sequencing: what gets done in week one (block the obvious paths),
  what gets done in quarter one (build the controls that need engineering work),
  what is on the roadmap (defenses that depend on platform investments).
- Acknowledge what you would test or red team to validate the model.

What gets candidates downgraded here:
- Listing controls without sequencing.
- Ignoring cost. Real Anderson-style failure: the cryptographically perfect
  control that nobody runs because it broke their product.
- Forgetting the "Did we do a good enough job?" question. Strong candidates close
  with how they would re-test the model in 6 months.

---

## 3. What Distinguishes USD 200K from USD 150K

Synthesized from Exponent's senior security engineer rubric, Shostack's intensive
course, and the gracenolan study guide.
https://www.tryexponent.com/blog/security-engineer-interview-prep
https://github.com/gracenolan/Notes/blob/master/interview-study-notes-for-security-engineering.md

### USD 150K candidate
- Names STRIDE, names OWASP, names a few controls.
- Treats threat modeling as a checklist activity.
- Focuses on the technical answer, ignores the operating environment.
- Cannot prioritize. Lists 12 threats with no ranking.
- Stops at the first plausible mitigation.

### USD 200K candidate
- Frames the model around assets and adversary incentive, not controls.
- Distinguishes data plane from control plane.
- Names trust boundaries and challenges them ("the IdP is trusted by definition,
  but if the IdP is compromised, what's our blast radius?").
- Brings a real incident as a parallel. "This is the same failure mode as
  Capital One's 2019 SSRF." That signals first-hand engagement.
- Sequences mitigations by cost vs blast radius.
- Closes with a validation plan: red team scope, automated test coverage,
  metrics to monitor for regression.
- Acknowledges what they do not know. "I have not built MCP servers in
  production. My model is borrowing from the recent ATLAS case studies; I would
  validate with the team that runs the platform."

---

## 4. Common Threat Model Prompts You Should Drill

These appear in real interview rounds, sourced from Exponent, Shostack's intensive
material, and the OWASP cheat sheet sample exercises.

1. **Authentication service.** Threat model the login plus password reset plus
   MFA enrollment flow for a B2B SaaS.
2. **CI/CD pipeline.** Threat model a GitHub Actions plus EKS deployment pipeline
   that publishes container images.
3. **Secrets management service.** Threat model HashiCorp Vault or AWS Secrets
   Manager fronting a microservices app.
4. **Multi-tenant data plane.** Threat model a SaaS that stores customer data per
   tenant in Postgres plus S3.
5. **LLM-powered customer support agent.** Threat model an agent with tool access
   to ticketing, account lookup, and email.
6. **Zero trust remote access.** Threat model a Teleport or Cloudflare Zero Trust
   replacement for VPN.
7. **Federated identity bridge.** Threat model an IdP federation that maps SAML
   from a customer IdP to internal IAM.

For each, drill the same structure: scope, DFD, STRIDE-per-element, top five
threats, mitigations with trade-offs, validation plan.

---

## 5. Concrete Phrases and Moves That Land

Drawn from interviewer write-ups in the Exponent guide and from Shostack's
intensive course rubric.

- "Let me restate the prompt to make sure I am solving the right problem."
- "Before I start, I want to write down assumptions I am making explicit. Push
  back on any of these."
- "I am going to treat X as trusted for this exercise and come back to it."
- "Walking the DFD element by element, starting at the user."
- "For this data flow, the most likely threats are tampering and information
  disclosure. Spoofing matters less here because of the IdP. Repudiation is a
  problem because we do not log the user ID on this path."
- "The mitigation I would pick is X. The cost is Y. The thing I am giving up is
  Z. If we cannot pay that cost, the fallback is W."
- "I would validate this model with red team scope of A and a regression test
  for B. I would re-run the threat model after the C feature ships."

---

## 6. The Anti-Patterns That Get You Cut

Compiled from rejection write-ups (Yuva Surya Konatham Amazon SE write-up), the
gracenolan notes, and the Exponent rubric.

1. **Listing controls without a model.** "We should encrypt at rest." Encrypt
   what, against whom, with which keys.
2. **STRIDE recitation.** Naming categories without applying them to the DFD.
3. **Ignoring economics.** Proposing a control that costs more than the asset
   protects.
4. **Pretending to know.** Bluffing about a service or a recent incident gets
   caught fast at the senior bar.
5. **Skipping the validation question.** A model with no validation plan is just
   an opinion.
6. **Not asking clarifying questions.** Senior interviewers report this as the
   single most common rejection signal in design rounds.

---

## 7. What to Read

- Adam Shostack, *Threat Modeling: Designing for Security* (Wiley, 2014). Still
  the canonical book. Chapter 3 (STRIDE), Chapter 7 (Processing and Managing
  Risks), Chapter 17 (Bringing Threat Modeling to Your Organization) are the
  highest-yield for interviews.
- OWASP Threat Modeling Cheat Sheet.
  https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html
- Microsoft STRIDE documentation as part of the SDL.
- Ross Anderson, *Security Engineering*, 3rd ed. (free PDF). Read the chapters
  that match the role (cloud, IAM, crypto, hardware).
  https://www.cl.cam.ac.uk/~rja14/book.html
- Trail of Bits publications and audit reports.
  https://github.com/trailofbits/publications
- Shostack's Threat Modeling Intensive course (paid).
  https://courses.shostack.org/pages/intensive-222

---

## Sources

- Adam Shostack resources.
  https://shostack.org/resources/threat-modeling
  https://github.com/adamshostack/4QuestionFrame
  https://courses.shostack.org/pages/intensive-222
- Threat Modeling Connect: Shostack's Four Question Framework.
  https://www.threatmodelingconnect.com/blog/shostacks-four-question-framework-for-threat-modeling
- OWASP Threat Modeling Cheat Sheet.
  https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html
- OWASP Threat Modeling Process.
  https://owasp.org/www-community/Threat_Modeling_Process
- Exponent senior security engineer interview prep.
  https://www.tryexponent.com/blog/security-engineer-interview-prep
- gracenolan/Notes interview study notes.
  https://github.com/gracenolan/Notes/blob/master/interview-study-notes-for-security-engineering.md
- Trail of Bits publications repo.
  https://github.com/trailofbits/publications
- Ross Anderson, *Security Engineering* 3rd ed.
  https://www.cl.cam.ac.uk/~rja14/book.html
- Yuva Surya Konatham Amazon SE rejection write-up.
  https://medium.com/@yuvasurya1998/what-i-learned-from-getting-rejected-by-amazon-a-security-engineers-interview-experience-293e65a2f942
