# Threat Modeling Intensive: 10 Day Roadmap

Owner: Emmanuel Tigoue
Target outcome: Run a 30 minute live threat modeling session with confidence. Whiteboard a system, identify trust boundaries, enumerate threats with STRIDE plus ATLAS, propose mitigations, articulate residual risk.

References used throughout this intensive:
- Microsoft STRIDE (Howard, Lipner)
- OWASP Threat Modeling Cheat Sheet
- Adam Shostack, Threat Modeling: Designing for Security
- MITRE ATT&CK Enterprise v15
- MITRE ATLAS (AML.T codes, latest release)
- NIST SP 800-154 Guide to Data-Centric Threat Modeling
- PASTA: Process for Attack Simulation and Threat Analysis (Tony UcedaVelez)
- OCTAVE Allegro (CMU SEI)

Daily structure: 90 minutes split as 30 min reading, 60 min applied exercise. Each day ends with a written output committed to disk.

---

## Day 1: Trust Boundaries Fundamentals

Reading (30 min):
- OWASP Threat Modeling Cheat Sheet, sections 1 to 3
- Shostack chapter 2: Strategies for Threat Modeling
- Microsoft Threat Modeling tool docs: trust boundary definition

Concepts to lock in:
- A trust boundary is a place where the level of trust changes. Data crossing a boundary must be re-validated.
- Three boundary categories: process boundaries (kernel vs userland), machine boundaries (host vs host), and trust level boundaries (authenticated vs anonymous, internal vs internet, tenant A vs tenant B).
- Every external interface is a trust boundary by default. Inside the boundary you trust the data; outside you do not.

Practical exercise:
Take a sticky note. Draw the path of a single HTTP request hitting `tigouetheory.com`, from browser to Cloudflare to origin to backend service to database. Mark every place trust changes with a dashed line. Aim for at least 5 boundaries.

Output: `day01_trust_boundaries.md` with a sketch and a written list of boundaries discovered.

---

## Day 2: STRIDE Deep Dive Part One (S, T, R)

Reading:
- Shostack chapter 3: STRIDE
- Microsoft STRIDE original paper

Each letter, with examples to memorize:

**Spoofing** (identity): Pretending to be someone you are not.
- Example: Attacker submits a JWT signed with a leaked key.
- Example: Forged Slack webhook payload posing as GitHub.
- Mitigations: Strong auth (mTLS, signed payloads, OIDC), audience checks, issuer pinning.

**Tampering** (integrity): Modifying data in flight or at rest.
- Example: MITM rewrites an unsigned API response.
- Example: Attacker writes to an S3 bucket without object lock.
- Mitigations: TLS, code signing, file integrity monitoring, append-only logs, database row hashing.

**Repudiation** (non-repudiation): Denying you took an action.
- Example: Admin deletes an audit row to hide their action.
- Example: User claims they did not click "approve" because no log captured the click.
- Mitigations: Tamper-evident logs (CloudTrail, Datadog audit, append-only Postgres), digital signatures, separation of duties.

Practical exercise:
List 3 spoofing, 3 tampering, 3 repudiation threats against `n8n.tigouetheory.com`.

Output: `day02_str.md`.

---

## Day 3: STRIDE Deep Dive Part Two (I, D, E)

Reading: Shostack chapter 3 continued, OWASP STRIDE examples page.

**Information disclosure** (confidentiality): Leaking data to someone who should not see it.
- Example: Verbose error message returns a stack trace with DB credentials.
- Example: S3 bucket misconfigured to allow `s3:GetObject` to `*`.
- Mitigations: Generic error messages, server-side filtering of fields, encryption at rest with KMS, IAM least privilege, DLP.

**Denial of service** (availability): Making a system unavailable.
- Example: Slow loris on an unprotected origin.
- Example: One tenant exhausts a shared LLM token budget.
- Mitigations: Rate limiting (per IP, per user, per tenant), circuit breakers, autoscaling with ceilings, quota systems, WAF.

**Elevation of privilege** (authorization): Doing something you should not be allowed to do.
- Example: IDOR on `/api/orders/{id}` returns another customer's order.
- Example: Container escape via misconfigured `--privileged` flag.
- Example: Prompt injection makes the LLM call a tool the user is not authorized to invoke.
- Mitigations: Authorization checks at every layer, RBAC plus ABAC, kernel hardening, action allow-lists, separation of duties.

Practical exercise:
Take a real bug bounty writeup from `hackerone.com/hacktivity`. Classify which STRIDE letters apply. Aim for one of each.

Output: `day03_ide.md`.

---

## Day 4: Data Flow Diagrams

Reading:
- Shostack chapter 2 on diagrams
- Microsoft Threat Modeling Tool, DFD level 0 vs level 1

DFD elements (Microsoft notation):
- External entity: rectangle. People or systems outside your control.
- Process: circle or rounded rectangle. Code that does work.
- Data store: parallel lines or cylinder. Where data sits.
- Data flow: arrow. Direction matters.
- Trust boundary: dashed line. Where trust changes.

Rules of good DFDs:
- Level 0 fits on one whiteboard. Level 1 zooms into one process.
- Every flow crosses at least one boundary or it is uninteresting.
- Label flows with what data they carry, not just "request".
- Data stores should never connect to data stores directly. A process always sits between.

Practical exercise:
Whiteboard a level 0 DFD of a customer-facing chatbot. Then redraw the same system as a level 1 DFD focused on the LLM call. Time yourself. Target 8 minutes for level 0.

Output: `day04_dfd.md` with both diagrams in ASCII.

---

## Day 5: Attack Trees

Reading:
- Bruce Schneier original attack tree paper (1999)
- Shostack chapter 4

Attack tree structure:
- Root: attacker goal (steal customer PII).
- Children: steps required to reach the goal.
- AND nodes: all children must succeed.
- OR nodes: any child succeeds.
- Leaf annotations: cost, skill, detectability, probability.

Why attack trees beat checklists for novel systems:
- They model attacker intent, not just defender categories.
- They naturally surface AND chains (what must compound for a breach).
- They produce a kill chain you can map to detection.

Practical exercise:
Build an attack tree for "exfiltrate customer chat history from a RAG chatbot". Three levels deep. Mark which leaves your existing controls block.

Output: `day05_attack_tree.md`.

---

## Day 6: MITRE ATT&CK and ATLAS Mapping

Reading:
- MITRE ATT&CK Enterprise tactics overview
- MITRE ATLAS framework page and matrix
- ATLAS case studies (especially the PoisonGPT and Microsoft Tay write-ups)

ATT&CK 14 tactics, memorize the order:
Reconnaissance, Resource Development, Initial Access, Execution, Persistence, Privilege Escalation, Defense Evasion, Credential Access, Discovery, Lateral Movement, Collection, Command and Control, Exfiltration, Impact.

ATLAS 12 tactics (subset to know cold):
- AML.TA0002 Reconnaissance
- AML.TA0003 Resource Development
- AML.TA0004 Initial Access
- AML.TA0005 ML Model Access
- AML.TA0006 Execution (in ML pipeline)
- AML.TA0007 Persistence
- AML.TA0011 Defense Evasion
- AML.TA0012 Discovery
- AML.TA0013 Collection
- AML.TA0024 Exfiltration

ATLAS techniques to know by name:
- AML.T0051 LLM Prompt Injection (direct, indirect)
- AML.T0048 External Harms
- AML.T0043 Craft Adversarial Data
- AML.T0044 Full ML Model Access
- AML.T0019 Publish Poisoned Datasets
- AML.T0020 Poison Training Data
- AML.T0024 Exfiltration via ML Inference API

Practical exercise:
Take the Day 5 attack tree. Map every leaf to an ATT&CK technique ID. For LLM-specific leaves, map to ATLAS.

Output: `day06_attack_atlas.md`.

---

## Day 7: PASTA and OCTAVE Basics

Reading:
- PASTA: Process for Attack Simulation and Threat Analysis, chapters 1 and 7
- OCTAVE Allegro overview document (CMU SEI)

PASTA 7 stages, memorize:
1. Define business objectives.
2. Define technical scope.
3. Application decomposition.
4. Threat analysis.
5. Vulnerability and weakness analysis.
6. Attack modeling.
7. Risk and impact analysis.

When to use PASTA over STRIDE: When the audience is business stakeholders. PASTA leads with business impact, ends with risk in dollars. STRIDE leads with components, ends with controls.

OCTAVE Allegro 8 steps: focused on information assets, runs 2 to 5 day workshop, output is a risk register prioritized by impact area.

When to use OCTAVE: regulated environments where the artifact must satisfy auditors and the conversation must happen between business and security at the same table.

How to talk about this in interview: "STRIDE is what I reach for first because it produces engineering-actionable output in under an hour. PASTA is what I run when the threat model itself has to defend a business case. OCTAVE is what I run during a SOC 2 readiness or HITRUST cycle."

Practical exercise:
Write a one-paragraph rationale for each of these scenarios:
1. Pre-launch threat model for a new microservice. Which framework? Why?
2. Quarterly risk review for a healthcare SaaS. Which framework? Why?
3. Post-breach lessons-learned threat model. Which framework? Why?

Output: `day07_frameworks.md`.

---

## Day 8: Threat Modeling LLM Systems

Reading:
- OWASP Top 10 for LLM Applications (current version)
- MITRE ATLAS case studies
- Anthropic responsible scaling policy (sections on misuse and oversight)
- Lakera prompt injection examples

LLM-specific threats not in classical STRIDE:
- Prompt injection (direct user input, indirect via retrieved docs).
- Training data poisoning.
- Model extraction via inference API queries.
- Embedding inversion (recover source text from vectors).
- Tool/agent abuse: LLM convinced to call a tool with dangerous arguments.
- Output handling: LLM emits malicious HTML, SQL, or shell commands consumed downstream.
- Excessive agency: agent has more authority than the task requires.
- Supply chain: poisoned model weights, poisoned dataset, malicious fine-tune.

Trust boundaries unique to LLM systems:
- User input to system prompt (prompt injection boundary).
- Retrieved documents to context window (indirect injection boundary).
- LLM output to downstream interpreter (output validation boundary).
- LLM output to tool invocation (tool use authorization boundary).

Practical exercise:
Draw a level 1 DFD of his Squire SOC analyst (or a generic RAG chatbot). Mark every prompt injection boundary with a special symbol. Enumerate threats at each boundary using STRIDE plus ATLAS.

Output: `day08_llm.md`.

---

## Day 9: Threat Modeling Cloud Architectures

Reading:
- AWS Well-Architected Security Pillar
- CIS AWS Foundations Benchmark threat scenarios
- Cloud Security Alliance Top Threats to Cloud Computing

Cloud-specific threat patterns:
- IAM as the new perimeter. Every threat model must cover IAM.
- Data plane vs control plane. Compromising the cloud control plane (root account, IAM role) is usually game over.
- Shared responsibility boundaries (AWS owns through hypervisor, customer owns OS up).
- Multi-tenant isolation: VPC, account boundary, KMS key boundary.
- Egress control: data exfiltration via misconfigured NAT or VPC endpoints.

Trust boundaries unique to cloud:
- AWS account boundary (the strongest isolation AWS offers).
- IAM role boundary (which role can assume which).
- VPC and subnet boundary.
- KMS key boundary (who can decrypt what).
- Region boundary (data residency).

Practical exercise:
Take drill_07 (data warehouse ETL) and drill_01 (serverless API). Annotate every IAM role and every KMS key as a trust boundary. Enumerate spoofing and elevation threats specific to each.

Output: `day09_cloud.md`.

---

## Day 10: Articulating Findings to Executives

Reading:
- FAIR (Factor Analysis of Information Risk) one-pager
- Adam Shostack on "Communicating Threat Modeling Results"
- Sample executive summary from his own SQUIRE_THREAT_MODEL.md

Executive translation rules:
- Lead with business impact in dollars or service hours, not CVE counts.
- One sentence per threat: who could do what, how bad, how likely.
- Risk rating must be HIGH, MEDIUM, or LOW. Never "9.4".
- Every HIGH must have an owner and a target date.
- Every accepted MEDIUM must have a written rationale.

The four-bullet exec summary template:
1. Scope of the threat model (system, version, date).
2. Threats found, by count and severity.
3. Mitigations in place vs planned.
4. Residual risk position and what we are accepting.

Practical exercise:
Take his SQUIRE threat model. Write a 200 word executive summary that a CFO would understand. Then write a 5 minute board talk version.

Output: `day10_executive.md`.

Final state at end of day 10: He has 10 days of artifacts, can run a live session in any of the 10 drill scenarios, and has an executive-ready voice for residual risk conversations.
