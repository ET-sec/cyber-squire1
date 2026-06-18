# STAR Story Bank: 12 Stories From the Real Stack

**Candidate:** Emmanuel Tigoue
**Stack reference (sanitized in stories):** cd-alpha droplet at 10.100.1.10, 4 vCPU 8GB Ubuntu 24.04, 13 Compose services + OpenClaw v2026.3.8, 14 active n8n workflows, 37 GRC docs, 8 OPA Rego policies, $48/mo infra, Datadog us5
**Voice:** Direct, numbers first, senior. Each story lands in 90 to 120 seconds spoken.

**Frame for every story:** You did this work. The story is not aspirational. State it that way.

---

## 1. Building the n8n SOAR Stack as a One-Person SOC

**Tag.** Solo execution under ambiguity. Picking your own stack and shipping it.

**Questions this answers.**
- Tell me about a project you owned end to end.
- How do you scope work when you're the only one on the team.
- What does "ship under ambiguity" look like for you.

**Situation.** I needed a SOAR fabric for CoreDirective. Email triage, alert correlation, incident drafting, automated runbooks. No vendor budget, no team, one droplet.

**Task.** Stand up a production SOAR stack on a 4 vCPU 8GB Ubuntu host, with state, observability, and identity from day one. Cost ceiling 50 dollars a month.

**Action.** I picked n8n as the orchestration layer because it gave me a 400-plus-node integration library and I could read the source. PostgreSQL 16 for state. HashiCorp Vault for secrets. Keycloak v26 for identity. Cloudflare Tunnel for zero-trust ingress so nothing exposed a port to the public internet. I authored the docker-compose stack, 13 services, with healthchecks and chmod-600 environment files. I wired in 14 workflows: a master orchestrator with 16 service actions, four Gmail readers across my account boundary, an ADHD operations bot, a finance reconciler, an API health check on cron, a Gumroad solvency engine, three tool sub-workflows. Datadog agent on the host shipped logs and metrics to us5.

**Result.** Forty-eight dollars a month. Zero downtime quarter to date. Webhook-driven master orchestrator that I trigger from a phone bot. The stack runs my business operations and gave me the foundation to plug an AI gateway and a triage agent on top of it. The architectural lesson I keep referencing is that I designed for a team from day one. Every service has a runbook, every secret has a vault entry, every policy has Rego in IaC. That's why the stack survives me adding a new service every two weeks.

**Takeaway.** Being a one-person SOC isn't a constraint, it's a forcing function for clean interfaces. If I can't read it tired at 2am, I can't ship it.

---

## 2. Designing OpenClaw With Prompt Injection Defenses

**Tag.** Treating an AI system the same way I'd treat any production service: threat model, eval harness, regression gate.

**Questions this answers.**
- Tell me about a hard technical problem you solved recently.
- How do you think about the security of LLM applications.
- Walk me through a project where you set your own bar for done.

**Situation.** I needed an inference gateway for a Claude Opus 4.7 model that several callers would hit: a Telegram bot, the n8n master orchestrator, and a Mac CLI node. Sensitive operational data flows through it. No vendor playbook for hardening it.

**Task.** Own the security posture before traffic ever touched it.

**Action.** I started with a threat model against OWASP LLM Top 10 and MITRE ATLAS. Ten attack classes, no vibes. I wrote a Python red-team harness that fired prompt-injection payloads from public corpora plus mutations I generated locally, scored responses for system-prompt leakage, tool misuse, excessive agency, and tool-call exfiltration. Defense in depth: input filter at the gateway layer for known jailbreak signatures, an output classifier that inspects tool-call arguments before the call executes, and an explicit allowlist on skill tokens so a stolen token couldn't pivot from a Tavily search to a GitHub write. Every request and response logged to Postgres so I could diff behavior across model upgrades. When Opus 4.7 shipped, I reran the harness before cutting traffic. Two regressions in tool-call handling; held rollout until the classifier was patched.

**Result.** Zero injection findings on the OWASP LLM Top 10 across eight DAST categories on the latest pass. Latency added by the input/output filters under 50ms p95. The eval harness now runs in CI on every commit; if a system-prompt change drops the score, the build fails before merge. I treat the model the way I treat the database: never let untrusted input land on it without a proxy.

**Takeaway.** Investigation quality on the defender side starts with input quality on the AI side. If your prompt path isn't a regression gate, your model isn't a production system.

---

## 3. Threat Modeling the Entire CoreDirective Engine

**Tag.** STRIDE and ATLAS applied to a real stack, output is a real artifact, not a whiteboard exercise.

**Questions this answers.**
- Walk me through a threat model you ran.
- How do you choose what to threat-model first.
- How does your threat model influence the rest of your security program.

**Situation.** Thirteen services, identity, secrets, agentic workflows, internet-facing tunnel, and an LLM. I needed one document senior reviewers could trust as the source of truth for the system.

**Task.** Produce a threat model the GRC corpus could reference, the IR playbooks could pivot off, and a future hire could read on day one.

**Action.** I drew the trust boundaries first: internet to Cloudflare Tunnel, tunnel to host, host to container, container to container, container to Vault, container to LLM. Six trust boundaries. For each, I ran STRIDE per pair of components and ATLAS for any pair that touched the model. I prioritized by blast radius, not by likelihood. The two highest were the n8n-to-LLM edge and the Vault-to-everything edge. I wrote up findings in `docs/grc/SQUIRE_THREAT_MODEL.md`, with sanitized diagrams, control mappings to NIST CSF 2.0, and a per-finding remediation track. I cross-referenced every finding into the POA&M so nothing died in the document.

**Result.** Threat model is now 1 of 37 docs in the GRC corpus. Eight findings closed within 30 days. Two findings became the basis for new Falco rules. The doc is the first thing I send any reviewer who asks how the stack is secured because it's the only document that actually shows the trust boundaries.

**Takeaway.** A threat model that doesn't change a control isn't a threat model, it's a checklist. Ground every finding in a fix or a detection or a rejection-with-rationale. Otherwise it dies.

---

## 4. Writing the GRC Corpus With AI Governance Policy

**Tag.** Policy-as-code thinking applied to GRC. Documents that aren't decoration.

**Questions this answers.**
- How do you approach policy writing.
- How do you make compliance work for engineers, not against them.
- Tell me about your AI governance program.

**Situation.** No GRC documentation existed for CoreDirective Engine. I needed a usable corpus that mapped to NIST CSF 2.0 and supported a SOC2 conversation later, and that an engineer could read without rolling their eyes.

**Task.** Build a sanitized public-facing GRC library covering the standard set: SSP, POA&M, risk assessment, IR playbooks, threat models, plus an AI Governance policy and an AI Incident Response playbook because the existing field guides skipped those.

**Action.** I scoped 31 documents on the first wave. Started with the AI Governance policy because it was the differentiator. Wrote it against NIST AI RMF and the OWASP LLM Top 10, with sections on model inventory, data classification at the inference boundary, prompt-handling controls, and human-in-the-loop checkpoints. Then the AI Incident Response playbook with detection sources mapped to ATLAS techniques. Standard SSP, ten policies including AI Governance, five IR playbooks including AI Incident, six threat-modeling docs, IAM docs, executive summaries. Every document has a sanitization key so cd-service-* maps to svc-* in public, and 161.35.0.184 maps to 10.100.1.10. The corpus shipped public on the cyber-squire1 repo with a sanitization map kept locally only.

**Result.** Thirty-seven documents, around 15,000 lines. AI Governance policy referenced in two recruiter conversations as a differentiator. Corpus passed a 7-agent QC sweep for sanitization, citation integrity, and framework coverage gaps. The corpus is what closed two recruiter conversations because it answered "show me your security program" with a link, not a slide.

**Takeaway.** Policy is a developer experience problem. If the engineer can't read it without losing patience, the policy doesn't exist.

---

## 5. Hardening Cloudflare Tunnel and Teleport for Zero Trust

**Tag.** Zero-trust ingress and PAM with JIT, on a one-person budget.

**Questions this answers.**
- How do you grant access to production without VPNs.
- Tell me about a zero-trust deployment.
- How do you handle privileged access for a small team.

**Situation.** I needed remote access to cd-alpha for SSH, n8n admin, and Teleport, with no public ports exposed and no static SSH keys floating in laptops. One operator, multiple devices, varying networks.

**Task.** Stand up zero-trust ingress for the host, plus PAM with just-in-time elevation for any privileged operation.

**Action.** Cloudflare Tunnel with two routes: n8n.tigouetheory.com to localhost:5678 and ssh.tigouetheory.com to localhost:22. Tunnel ID pinned in Terraform, token in Vault. No 22, no 5678, no 8080 ever exposed at the host. Then Teleport v18 as the privileged-access plane: every shell, every kubectl, every database session goes through a Teleport proxy with session recording on by default. JIT elevation requires an out-of-band approval through Telegram. Audit shipper sends every Teleport event to Datadog, retention 90 days. Falco watches for any sshd process that didn't come through the tunnel, which is the canary.

**Result.** Zero direct-to-host SSH attempts succeed. Audit log of every privileged command for 90 days. JIT elevation latency under 30 seconds. The architecture is publicly described in `docs/grc/IAM_ARCHITECTURE.md` so any reviewer can see the trust boundary I'm enforcing.

**Takeaway.** Zero trust isn't a tool, it's the answer to "what happens if my laptop is compromised tonight." If the answer involves "they'd still need," you've done it. If the answer is "they'd be in," you haven't.

---

## 6. Running OWASP ZAP DAST and Remediating Findings

**Tag.** Real DAST run on real internet-facing surfaces, real fixes the same day.

**Questions this answers.**
- Tell me about a vulnerability you found and fixed.
- How do you assess the security of an external surface.
- Walk me through your remediation discipline.

**Situation.** I have two internet-facing endpoints behind Cloudflare Tunnel: the n8n admin and the brand site at tigouetheory.com. I'd never run DAST against them.

**Task.** Run a baseline OWASP ZAP scan and remediate every finding before I added another exposed surface.

**Action.** ZAP container against both surfaces, baseline scan first to set a floor, then full active scan within rate limits. Findings clustered into security headers, cookie hardening, and one missing CSP directive. The fix path was Cloudflare Pages headers config plus Tunnel edge rules: HSTS preload, Permissions-Policy locked down, X-Content-Type-Options nosniff, Referrer-Policy strict-origin-when-cross-origin, CSP with explicit allowlist for the script bundles I actually serve. Re-ran ZAP, all four header findings closed. Pen test write-up went into `docs/grc/PEN_TEST_REPORT.md` with the remediation evidence inline. IR playbook diagrams updated to reflect the new header-violation detection class.

**Result.** Four findings, four closed same day. Public DAST artifact lives in the GRC corpus. I now run baseline ZAP weekly via GitHub Actions; any regression on headers fails the build.

**Takeaway.** External surface hygiene is one of the cheapest interview signals to lose and one of the cheapest to win. If you can't run a clean DAST against your own brand site, no senior reviewer is going to take your AI security claims seriously.

---

## 7. Building OPA Policies for Terraform IaC

**Tag.** Policy-as-code as a deploy gate. The board asks "how do you stop misconfiguration." This is the answer.

**Questions this answers.**
- How do you prevent misconfigurations in IaC.
- Walk me through your policy-as-code program.
- Tell me about a CI/CD gate you've owned.

**Situation.** Terraform was running my DigitalOcean infrastructure: droplet, firewall, Spaces buckets, Cloudflare Tunnel, DNS. Without policy-as-code, a wrong `firewall.allow_ssh = "0.0.0.0/0"` is one PR away from production.

**Task.** Build OPA policies as a hard gate in the Terraform PR pipeline. Zero exceptions for misconfig.

**Action.** Eight Rego policies covering: no SSH from internet, no Spaces bucket public-read, no resource without tags, no droplet without backups enabled, no DNS record outside allowed zones, no Cloudflare rule that bypasses the tunnel, no Terraform module without a version pin, no resource without an OPA-approved module path. The PR pipeline runs fmt, validate, tflint, checkov, plan, then OPA evaluation against the plan output. Plan must pass all eight policies before merge is allowed. PR comment renders the OPA decision.

**Result.** Zero policy violations have shipped to production. Two PRs blocked by the OPA gate when I almost shipped a public-read bucket and a DNS record outside the zone. Public source on the cyber-squire1 repo. The pipeline is CI evidence I show in any senior conversation.

**Takeaway.** Policy that lives in a doc is a wish. Policy that lives in CI is a control. Pick the second every time.

---

## 8. The CARL Rule System and Agentic Safety

**Tag.** Rules that govern an agent's behavior, owned in version control, applied at runtime.

**Questions this answers.**
- How do you control AI agents at scale.
- Tell me about a guardrail system you've designed.
- How do you keep an agent from going off-script.

**Situation.** I run several Claude-powered agents through OpenClaw: a Telegram conversational bot, sub-agents that run inside the IDE, and a triage agent reading Falco alerts. Each one needs a different behavioral envelope. Without explicit rules, they drift, repeat AI tells, or skip steps.

**Task.** Build a rule system that lets me declare per-domain behavior, version it, audit it, and apply it at agent runtime.

**Action.** CARL is a domain-rule format I author in version control. Each domain (career, infrastructure, content, GRC) has a `.carl` file with rules: forbidden phrasing, required sources of truth, output formats, escalation triggers. A Claude-side hook injects the active rules into the system prompt at session start. Manifest parser validates rule syntax in CI. The rule set is the spec for the agent's behavior, and the spec is reviewable by humans before it ever shapes a response. When a rule is violated, the violation gets logged so I can tune.

**Result.** Forty-plus rules across six domains, all in version control. AI tells like em dashes and "great question" openers were eliminated as a class because the rule fires before generation. Operator-side feedback loop where I can update a rule and see the next session reflect it without code changes.

**Takeaway.** Agent safety isn't model-level only. It's the operator's runtime envelope, declared as data, version-controlled, applied as an injection. Treat agents like middleware, not like black boxes.

---

## 9. Failing Forward: The Switch v3 Bug That Cost Me a Day

**Tag.** A real mistake, what it taught me, what shipped because of it.

**Questions this answers.**
- Tell me about a time you failed.
- Walk me through a debugging session that humbled you.
- What did you change after a mistake.

**Situation.** I was rebuilding the master orchestrator workflow on a fresh n8n install, post-migration to DigitalOcean. The Switch v3 node was supposed to route 16 actions cleanly. It looked right in the canvas and broke at runtime.

**Task.** Get the orchestrator green before the rest of the migration depended on it.

**Action.** First instinct was that my routing config was wrong. Two hours of staring at the canvas. Then I ran the workflow with debug logs and saw the routing values weren't propagating. Switched to the database. n8n 2.x stores workflow definitions in `workflow_entity` but loads runtime from `workflow_history`. The CLI import I'd used updated `workflow_entity` only. The runtime was reading a stale version. I went direct to Postgres, ran a text replace on the nodes JSONB column for both tables, restarted the n8n container. Workflow ran on the next trigger. The lesson was bigger than the fix: the n8n REST API PATCH updates the draft, not always the runtime; the CLI can update one table and not the other; the database is the only source of truth I trust now.

**Result.** Day lost. But I documented the workflow_entity vs workflow_history dual-write behavior in my project memory and in the runbooks, so the next n8n credential remap took 20 minutes instead of 8 hours. The bug now appears in my CARL rules under the n8n-debugging domain.

**Takeaway.** I don't believe a system anymore until I've seen its database. If the docs and the canvas tell me one thing and the runtime tells me another, the database wins. That's an operator instinct, not a junior one.

---

## 10. A Vulnerability I Found and Fixed: The Header Misconfig and What It Implied

**Tag.** A small finding that opened a bigger architectural question. Investigation quality on a real surface.

**Questions this answers.**
- Tell me about a vulnerability you found.
- Walk me through a fix that mattered.
- How do you know when a finding is bigger than it looks.

**Situation.** OWASP ZAP baseline scan against tigouetheory.com surfaced four header findings: missing HSTS preload, weak Permissions-Policy, missing X-Content-Type-Options, no CSP. None of them are catastrophic alone. Together they imply an external surface that nobody had hardened.

**Task.** Fix the headers, but also figure out why this surface had drifted in the first place, and prevent it from drifting again.

**Action.** Headers fix at the Cloudflare edge: HSTS preload, Permissions-Policy locked, nosniff, Referrer-Policy strict-origin-when-cross-origin, CSP with an explicit allowlist for the script bundles I serve. Re-ran ZAP, all four closed. Then I asked the bigger question: what change pipeline owns these headers. The answer was that nothing did. They lived in a Cloudflare config that wasn't in IaC. I migrated the headers config into Terraform, added an OPA policy that requires HSTS preload on any new origin, added a weekly ZAP run as a scheduled GitHub Action. Updated `docs/grc/PEN_TEST_REPORT.md` and IR playbook diagrams to reflect the new header-violation detection class.

**Result.** Four findings closed in under an hour. Permanent guardrail in CI. The bigger fix was making the surface part of IaC instead of part of a vendor dashboard. That's the architectural change the four findings unlocked.

**Takeaway.** Small findings are sometimes a tell that a surface isn't owned. The fix is rarely the headers. The fix is taking ownership and putting the ownership into version control.

---

## 11. The Cross-Functional Decision: AI Governance Policy as a Legal + Engineering + Customer Conversation

**Tag.** Working across legal, customer, and engineering on a single policy. Influence without authority.

**Questions this answers.**
- Tell me about a cross-functional decision you led.
- How do you align legal and engineering on AI risk.
- Walk me through a stakeholder conversation that mattered.

**Situation.** I was scoping AI services for a small accounting-firm client through CoreDirective. They wanted automation but were nervous about client data hitting third-party AI APIs. Their compliance posture was their entire reputation. I had to make a build-or-buy decision that the engineer in me wanted to make on speed and the policy author in me knew had to be made on data residency.

**Task.** Land an architecture and an AI Governance policy that legal could sign, engineering could ship, and the client could explain to their own clients without flinching.

**Action.** I ran a 30-minute conversation with the firm's lead partner where I framed three architectures: full cloud LLM with logging guarantees, hybrid (cloud LLM with PII scrubbing inline), local LLM on a dedicated host. Walked them through the cost, latency, and data-residency tradeoffs in dollars and minutes, not slides. They picked the hybrid path on cost grounds, then I overrode that recommendation in writing because the data-classification work I'd done said hybrid still leaked. Sent them a one-page memo: "I'd recommend local LLM, here is the cost delta, here is the residency guarantee, here is the policy you can show your insurance." They agreed. I shipped the local Ollama path. Wrote `docs/grc/AI_GOVERNANCE.md` against NIST AI RMF as the policy that governs that decision and any future client decision in this category.

**Result.** Client signed the architecture. The AI Governance policy is now a public differentiator (and 1 of 10 policies in the GRC corpus). Two recruiter conversations referenced the policy as a reason to take the screen.

**Takeaway.** A senior engineer doesn't push an architecture they don't believe in just because the client picked it on cost. You write the override in a memo, you back it with policy, and you respect them enough to give them the data to change their mind. Cross-functional isn't compromise, it's clarity.

---

## 12. The 200K-Tier Architecture Decision: Build vs Buy on the SOAR Layer

**Tag.** A real build-vs-buy decision with a real number, made under real cost constraints.

**Questions this answers.**
- Tell me about a build-vs-buy decision.
- How do you justify infrastructure spend.
- Walk me through a tradeoff between cost and capability.

**Situation.** I needed orchestration. The vendor SOAR options I priced were $5,000 a month at the low end and $50,000 at the senior end. My infrastructure ceiling was 50 dollars a month. The decision wasn't "what does the market like." The decision was "what survives the constraints, gives me ownership, and doesn't lock me in."

**Task.** Pick a SOAR substrate that I could ship in a week, run for under 50 a month, and own the source for.

**Action.** Three options on the table. Vendor SOAR: capability ceiling high, cost ceiling fatal, lock-in irreversible. Roll my own with Python plus a queue: cost low, time-to-first-workflow high, every integration custom. n8n self-hosted: 400-plus integrations out of the box, source available, runs in a container, scales with the host. I picked n8n. Reasoning: I valued integration breadth and source-readability over differentiated SOAR features I wouldn't use for two years. I sized the host: 4 vCPU, 8GB, 160GB. I committed to writing 14 workflows in the first 90 days as the bar for "did I make the right call."

**Result.** Forty-eight dollars a month. Fourteen active workflows in 90 days. Master orchestrator with 16 service actions covers the surface a vendor SOAR would have. Total cost of ownership over 12 months: 576 dollars. Nearest vendor option over the same window: 60,000. The capability gap I worried about didn't materialize because I never needed the differentiated SOAR features the vendors charged for. The lock-in I avoided is what matters longer-term: I can move this stack to any host, any cloud, any day.

**Takeaway.** Build-vs-buy isn't about features in a matrix, it's about who owns the substrate in two years. Pick the substrate where you can read the source, run the integrations, and move the data. Everything else is negotiable.

---

## Story-to-question quick map

| If they ask | Lead with |
|-------------|-----------|
| Hard technical problem recently | Story 2 (OpenClaw) |
| Investigation quality | Story 2 → Story 10 |
| Project end to end | Story 1 (n8n SOAR) |
| Threat modeling | Story 3 |
| AI governance / policy | Story 4 → Story 11 |
| Zero trust | Story 5 |
| Vulnerability you fixed | Story 10 → Story 6 |
| IaC / CI gates | Story 7 |
| Agent safety | Story 8 |
| A failure | Story 9 |
| Cross-functional | Story 11 |
| Build vs buy | Story 12 |
| 200K-tier judgment | Story 12 → Story 11 |
| Detection engineering | Story 3 (Falco tuning subset) → Story 7 (OPA) |
| Communication to executives | Story 11 (memo path) |
