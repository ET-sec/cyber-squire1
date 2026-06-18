# Dropzone AI — Behavioral Question Bank, Stage 3

**Round:** Technical interview, Eric Hammerle, Director of Engineering
**Date:** Thursday May 7, 2026, 12:45 to 1:30 PM EDT (45 minutes)
**Format:** Google Meet, 1:1 with hiring manager
**Role:** Senior Security Engineer, $175k to $217k base plus equity, remote US
**Owner:** Investigation quality on the AI SOC Analyst, Python codebase

This file pairs with `04_STAR_STORIES.md` (twelve stories) and `07_MASTER_FRAMING.md` (red thread, value prop matrix). Read those first. This file is the question bank, the answer skeletons, and the openers.

---

## 1. Director of Engineering interview style primer

A Director of Engineering at a Series B AI startup is not running a coding screen, that already happened. He is running a calibration. He has 45 minutes to decide one question: would I want this person on my team, accountable for a slice of the product, in the next sprint.

Published frameworks for how directors run these rounds:

- **Gergely Orosz, "The Pragmatic Engineer"** — argues that director rounds test for engineering judgment, ownership, and ability to operate one level above their title. Orosz's framing: directors hire for "people who would make my life easier in two months." The signal is autonomy under ambiguity, not raw skill.
- **Will Larson, "An Elegant Puzzle"** — defines four modes of senior engineering work: solver, fixer, tech lead, architect. Directors probe for which modes a candidate occupies naturally. They want range, not a single mode.
- **Camille Fournier, "The Manager's Path"** — chapter on hiring at the senior IC level emphasizes that the strongest signal is "how this person handles being wrong, being challenged, or being interrupted." Behavioral questions are designed to surface that, not the wins.
- **Lara Hogan, "Resilient Management"** — frames the senior IC interview as a check on five behaviors: how you handle conflict, how you mentor, how you say no, how you escalate, and how you recover from a mistake. Hogan's "manager voice" exercise is a useful rehearsal frame for the disagreement question.

What this means in practice for Eric's 45 minutes:

- **Technical leadership.** Can this person own a slice of the product and ship it without weekly hand holding.
- **Conflict and pushback.** Does the candidate have an actual point of view, and can they hold it under disagreement without becoming a problem to manage.
- **Ambiguity tolerance.** Can the candidate translate a fuzzy mandate into a shipped artifact, especially when the right answer is not obvious.
- **Prioritization.** Does the candidate know what to drop, not just what to do.
- **Mentorship and influence.** Can this person raise the bar for engineers around them without organizational authority.
- **Code review judgment.** Does this person know what to push back on and what to let go.
- **On call grace.** Can they stay calm and useful at 3 AM with incomplete information.
- **Customer empathy.** Do they treat the customer's pain as real engineering input, not noise from GTM.
- **Hiring and firing instincts.** Would this person spot a bad hire in their first month, and would they have the spine to flag it.

Eric will probably not ask all nine. He will pick four or five and probe. The rest of this document is built so any of the forty most likely questions has a story ready to deploy in 60 to 90 seconds.

---

## 2. Forty behavioral questions, organized by theme

Each question lists the primary STAR story to deploy (named exactly as it appears in `04_STAR_STORIES.md`), a Problem-Specifics-Consequence skeleton sized for 60 to 90 seconds, and the trap to avoid.

### Theme A. Ownership and investigation quality (8 questions)

**A1. Walk me through an investigation you ran end to end.**
- Story: 1. POS Skimmer Investigation at Texaco
- Problem: Customer reported a card decline at one pump, no SIEM alert, PCI environment, 45 plus devices on a flat network.
- Specifics: Pulled transaction log, span port and Wireshark on the pump switch, found outbound TLS to a four day old self signed cert domain, isolated at the switch to keep memory and disk intact, called payment processor with BIN range and timestamps, walked the physical terminal.
- Consequence: Zero additional cards compromised, 8 hours to 90 minutes containment on the next case, six step IR runbook still in use.
- Trap: Do not over explain PCI scope. Eric is an engineer, not an auditor. Stay on the wire and the decisions.

**A2. What does investigation quality mean to you?**
- Story: lead with framing, then Story 2. OpenClaw AI Gateway Red Team as proof
- Problem: Investigation quality is two things. First, the investigator does not stop at the alert that fired. Second, the investigation reproduces.
- Specifics: For the OpenClaw gateway I built a regression harness against OWASP LLM Top 10 and MITRE ATLAS, ten attack classes, scored for system prompt leakage, tool misuse, excessive agency, and exfil via tool calls. Logged every request to Postgres so I could diff after model upgrades.
- Consequence: Zero confirmed prompt injection successes across 90 days, two model upgrade regressions caught before cutover.
- Trap: Do not turn this into a definition speech. Define in one sentence, prove with one story.

**A3. Tell me about a time you owned the outcome of a system end to end.**
- Story: 4. n8n SOAR From Zero
- Problem: Needed orchestration across incident response, content ops, Gmail triage, and finance. No team, no budget for commercial SOAR.
- Specifics: Picked n8n, single webhook entry point as MASTER_ORCHESTRATOR_V1 routing to 16 services, every workflow as a typed function with an Error Handler workflow, credentials in n8n's store, exported to git.
- Consequence: 14 active workflows in under a month, MTTR on workflow failures under 10 minutes because the error path posts the failing node and payload to Telegram.
- Trap: Do not list workflows. List the one architectural choice that mattered: every workflow is a function with an error path.

**A4. What is something you built that you are most proud of, and why.**
- Story: 2. OpenClaw AI Gateway Red Team
- Problem: Stood up a Claude Opus 4.7 inference gateway behind my own infra, sensitive data flowing through it, no playbook for securing an LLM gateway.
- Specifics: Threat model against OWASP LLM Top 10 and MITRE ATLAS, Python red team harness, two layer defense (input filter on jailbreaks plus output classifier on tool call args), per token allowlist, every request logged for behavior diff.
- Consequence: Zero confirmed prompt injection successes in 90 days, harness is now my standard pre deploy gate.
- Trap: Do not say "I am proud of" five times. State the work, let the work do the proud part.

**A5. How do you know when an investigation is done.**
- Story: 1. POS Skimmer Investigation at Texaco, with Story 5. Splunk MTTD 48 Hours to Under 4 as backup
- Problem: An investigation is done when three questions are answered: what happened, how do I know, and what do I do next time. Anything before that is a status update.
- Specifics: For the skimmer case the first question got answered in Wireshark, the second in the transaction log timestamps and the cert chain, the third in the six step runbook I wrote that night.
- Consequence: The runbook is what made the next case 90 minutes instead of 8 hours. That is the test for "done."
- Trap: Do not start with the runbook. The runbook is the artifact, not the answer.

**A6. Describe a time you found something that nobody else was looking for.**
- Story: 3. Falco Alert Tuning 200 to 12
- Problem: Falco was firing 200 plus alerts a day across 13 containers. Engineers had stopped reading the feed, which meant the real ones were invisible.
- Specifics: Pulled 14 days of alerts, clustered by rule, container, process. Three rules drove 78 percent of the noise. Rewrote with explicit process lineage and namespace filters, mapped the rest to MITRE ATT and CK, added a weekly diff job for new clusters.
- Consequence: 200 to 12 actionable findings a day, two real findings caught in month one that would have been buried in the old noise.
- Trap: Do not frame this as "I cleaned up someone's mess." Frame as "I made the feed trustworthy again."

**A7. How do you handle an alert when you cannot tell if it is real.**
- Story: 1. POS Skimmer Investigation at Texaco
- Problem: A customer complaint was the only signal. No SIEM, no EDR, no IOC.
- Specifics: Started with the human signal, then made the wire confirm or deny. Transaction log first because it costs nothing, span port and packet capture second because it gives ground truth, physical inspection third.
- Consequence: 90 minutes from report to containment because I did the cheap checks first and the expensive checks second.
- Trap: Do not say "I trust my gut." Say "I order the checks by cost and by signal strength."

**A8. When you join a new system, how do you decide what to look at first.**
- Story: 3. Falco Alert Tuning 200 to 12 (the inventory step)
- Problem: Inherited a Falco deployment with no documentation on which rules mattered.
- Specifics: First step was an inventory: alerts by rule, container, process, time of day. I do not change anything before I have a fingerprint of how the system behaves on a normal day.
- Consequence: The cluster analysis is what told me three rules drove 78 percent of the volume. That was not visible from the rule names.
- Trap: Do not say "I read the docs first." The docs lie. Say "I read the data first."

### Theme B. Disagreement, conflict, pushback (5 questions)

**B1. Tell me about a time you disagreed with a decision and pushed back.**
- Story: 9. Segmentation vs Wi-Fi Disagreement
- Problem: Owner wanted faster customer Wi-Fi prioritized over PCI segmentation. He was right that customers do not see segmentation.
- Specifics: Did not argue protocols. Pulled fine schedule, average breach response cost, downtime cost in dollars per day. One page, three numbers. Offered a compromise: segmentation first, guest Wi-Fi VLAN as part of the same cutover.
- Consequence: He agreed in 10 minutes. Both shipped within a week. Relationship intact for three more projects.
- Trap: Do not let this become a "I won" story. Frame it as "I translated."

**B2. Tell me about a time you disagreed with another engineer.**
- See section 9 below for the pre built peer engineer disagreement answer.

**B3. How do you handle being wrong in front of the team.**
- Story: lead with framing, then 12. n8n Credential Remapping DB Debug as proof
- Problem: I was wrong about where the credential ID truth lived. I assumed the API and CLI were authoritative because the UI agreed with them.
- Specifics: When the runtime kept failing I stopped trusting my own assumption, dumped the schema, found the workflow_history table that I had not known about, wrote up the new behavior in my project notes so it would not cost anyone else an afternoon.
- Consequence: 14 workflows clean on first run after the fix. The note is the artifact that says "I was wrong, here is the corrected model."
- Trap: Do not perform humility. Just state the wrong assumption, the correction, and what you wrote down.

**B4. Describe a time you held an unpopular position and were eventually right.**
- Story: 9. Segmentation vs Wi-Fi Disagreement
- Problem: The unpopular position was that PCI segmentation came before customer experience improvements. The store owner did not want to hear that.
- Specifics: I held the position by translating it into the language he cared about. Three numbers on one page.
- Consequence: He agreed without me having to invoke authority, which mattered because I did not have any.
- Trap: Do not say "I knew I was right." Say "I knew the numbers were on my side and I had to surface them."

**B5. Tell me about a time you had to give critical feedback.**
- Story: framing plus partial pull from 7. 37 GRC Documents in Two Months (the QC pass)
- Problem: I ran a six agent QC audit on my own GRC library before publishing. The audit caught documents that were citation strong but argument weak. I had to rewrite my own work.
- Specifics: I treated my own drafts as if they had come from another engineer. The feedback was specific (this control points at a clause, not a behavior, rewrite around the behavior), not vague (this could be tighter).
- Consequence: Zero rework demanded by the human reviewers who read the published library. The QC pass is what got it there.
- Trap: Do not pretend you have managed people. State that you have set the bar on yourself first, then on artifacts you reviewed.

### Theme C. Ambiguity and startup mindset (5 questions)

**C1. Tell me about a time you shipped something without a clear spec.**
- Story: 4. n8n SOAR From Zero
- Problem: I needed automation across the stack with no spec, no team, no orchestration layer.
- Specifics: Picked n8n on three criteria (self hosted, credential store, JSON exportable). Defined the spec by writing the orchestrator as a typed function with one entry point. Every workflow had to fit that contract.
- Consequence: 14 workflows in under a month, contract held for every one, error path defined before the happy path.
- Trap: Do not say "I just figured it out." Say "I wrote the contract first and made the workflows fit."

**C2. How do you decide when something is good enough to ship.**
- Story: 4. n8n SOAR From Zero, with 2. OpenClaw AI Gateway Red Team as backup
- Problem: Good enough means the failure modes are observable and recoverable. Not all failure modes are prevented, all of them are observable.
- Specifics: For n8n the bar was every workflow has an error path that posts the failing node and payload to Telegram. For the OpenClaw gateway the bar was every model upgrade re runs the regression harness before cutover.
- Consequence: 14 workflows shipped, two model regressions caught pre deploy.
- Trap: Do not say "I ship when I am confident." Say "I ship when the failure path is wired."

**C3. Tell me about a time the requirements changed mid build.**
- Story: 10. NeMo Local Inference Architecture
- Problem: Started building an AI triage workflow assuming cloud API. Realized partway in that several event types contained data I was not willing to send to a third party model, and a real customer would feel the same.
- Specifics: Split the pipeline into two lanes at ingest. Classifier decides cloud safe versus local only. Same JSON schema both lanes so downstream automation does not care which model answered.
- Consequence: 100 percent of sensitive payloads on local infra, cloud handled the rest at frontier model quality, schema stable through model changes on either lane.
- Trap: Do not say "I pivoted." Say "I split the pipeline."

**C4. How do you operate when you do not have all the information.**
- Story: 1. POS Skimmer Investigation at Texaco
- Problem: One customer report, no SIEM, no IOC, PCI environment, no clear adversary signal.
- Specifics: Worked from cheapest signal to most expensive. Transaction log, packet capture, physical inspection. Each step either confirmed or denied a hypothesis.
- Consequence: 90 minutes to containment because I did not wait for perfect information.
- Trap: Do not say "I trust my instincts." Say "I order the next check by cost and signal."

**C5. What is the messiest project you have ever taken on.**
- Story: 11. DigitalOcean Migration From AWS, with 4. n8n SOAR From Zero as backup
- Problem: AWS instance suspended for nonpayment. 13 containers, daily workflows, Cloudflare tunnel terminating into the dead instance. No restore budget.
- Specifics: Triaged by business impact first (n8n workflows and Telegram bots are production, the rest can absorb a gap). New droplet sized to the working set, not peak. Postgres volume restored from snapshot, n8n brought up against it, Cloudflare tunnel rewired to the new origin without changing public hostnames. Moved secrets to Doppler during the migration as a forced cleanup.
- Consequence: Live in under 72 hours, zero downtime on the workflows that mattered, monthly cost down to 48 dollars.
- Trap: Do not narrate the panic. Narrate the triage decision.

### Theme D. Mentorship, leadership, influence without authority (5 questions)

**D1. Tell me about a time you raised the bar for engineers around you.**
- Story: 4. n8n SOAR From Zero (the error handler pattern)
- Problem: Most n8n stacks I had seen on public blogs skipped the error handler entirely. Workflows would fail silently and someone would notice three days later.
- Specifics: Set the standard that no workflow merges without a wired error path. Built the Error Handler workflow as the reference. Documented the pattern.
- Consequence: 14 workflows, every one with an error path, MTTR under 10 minutes because every failure surfaces with the failing node and payload.
- Trap: Do not say "I taught the team." Say "I set the standard and made the reference."

**D2. How do you mentor a junior engineer.**
- Story: framing plus 7. 37 GRC Documents in Two Months
- Problem: Mentorship for me has looked less like one on ones and more like setting an artifact bar that other people can reach.
- Specifics: For the GRC library I made the cross reference rule explicit (every control points to the behavior, every policy points to the control, every IR playbook points to a real incident I had run). Anyone who joined the work would have a template, not a verbal explanation.
- Consequence: Zero rework on the published library, and the template held for documents I did not write personally.
- Trap: Do not invent direct reports. State what you actually have done, which is set bars on artifacts.

**D3. Describe a time you influenced a decision without organizational authority.**
- Story: 9. Segmentation vs Wi-Fi Disagreement
- Problem: I was the security engineer at a franchise. The owner had the money. He wanted Wi-Fi first.
- Specifics: Translated risk into dollars on one page. Three numbers. Offered the compromise that gave him the customer experience win on the same cutover.
- Consequence: 10 minute conversation, both projects shipped, relationship preserved.
- Trap: Do not say "I convinced him." Say "I translated."

**D4. How do you build trust with a new team.**
- Story: framing plus 11. DigitalOcean Migration From AWS as proof of behavior under pressure
- Problem: Trust comes from how you handle the first crisis, not how you introduce yourself.
- Specifics: When the AWS instance went down I did not ask for permission, I triaged by business impact and shipped the migration. Documented the rationale so anyone could see the decisions.
- Consequence: 72 hours to live, written record of the call I made.
- Trap: Do not say "I introduce myself well." Say "I show the work and the reasoning."

**D5. Tell me about a time you pulled someone up.**
- Story: framing plus 8. PCI DSS Cross Functional at Texaco
- Problem: The store owner was not a technical person and was about to make decisions that would expose him to PCI fines he did not know existed.
- Specifics: Rather than letting him approve or block on vibes, I gave him the financial frame and the technical map on the same page. He made the right call himself with the information.
- Consequence: He learned to ask the right question on the next two projects, which was a better outcome than me being right alone.
- Trap: Do not patronize the stakeholder. State the translation as respect, not condescension.

### Theme E. Failure, mistake, what you would do differently (5 questions)

**E1. Tell me about a mistake you made.**
- See section 8 below for the pre built biggest mistake answer (recommends Falco).

**E2. What would you do differently on the OpenClaw red team work.**
- Story: 2. OpenClaw AI Gateway Red Team
- Problem: I built the regression harness alongside the gateway, not before it.
- Specifics: That meant my first month of production traffic was unobserved against the harness. I caught up later, but the right move was harness first, gateway behind it.
- Consequence: I now treat the regression suite as a pre deploy gate by default. For any new model or skill the harness runs first.
- Trap: Do not pick a mistake that is actually a humblebrag. Pick the real one.

**E3. Tell me about a project that did not go well.**
- Story: 6. CoreDirective Accounting AI (use the bracketed real version, see Master Framing Part 4)
- Problem: First version of the accounting workflow had no human review gate on transactions above a dollar threshold. I had assumed model categorization accuracy was the whole story.
- Specifics: My partner caught a misclassification during the shadow mode period that would have hit the books had I shipped earlier. I added the review gate, the kill switch, and the weekly reconciliation job before cutover.
- Consequence: Caught two prior quarter misclassifications during the catch up, zero compliance issues since deployment.
- Trap: Do not minimize the early miss. State it cleanly. The recovery is the signal.

**E4. Tell me about a time you over engineered something.**
- Story: framing plus partial pull from 7. 37 GRC Documents in Two Months
- Problem: My first GRC table of contents had 50 documents, not 37. I had inflated the scope to look thorough.
- Specifics: A six agent QC pass flagged thirteen documents that were duplicates or nice to haves, not load bearing. I cut them. The remaining 37 cross referenced cleanly.
- Consequence: Cleaner library, faster reviewer experience, no padding.
- Trap: Do not pick something trivial. State the real over engineering.

**E5. Tell me about a time you missed a deadline or a shipment.**
- Story: framing plus 11. DigitalOcean Migration From AWS as the recovery
- Problem: The AWS instance suspension was a financial miss on my side that became a delivery miss on the stack. I had let the bill go past due during a cash crunch.
- Specifics: I owned it as my decision, not as bad luck. Triaged by impact, shipped the migration, used the forced move as a cleanup opportunity for secret management.
- Consequence: 72 hours to live, monthly cost down to 48 dollars, secret management improved as a side effect.
- Trap: Do not blame the cash situation. Own the call that put you there.

### Theme F. Prioritization, tradeoffs, saying no (4 questions)

**F1. Tell me about a time you said no.**
- Story: 9. Segmentation vs Wi-Fi Disagreement
- Problem: Owner wanted Wi-Fi first.
- Specifics: I said no on the sequence and yes on the scope. Segmentation first, then Wi-Fi as part of the same cutover.
- Consequence: Both shipped on a defensible sequence.
- Trap: Do not frame "no" as confrontation. Frame as sequence and scope.

**F2. How do you decide what to drop when you cannot do everything.**
- Story: 11. DigitalOcean Migration From AWS
- Problem: 13 containers, finite migration window, real budget pressure.
- Specifics: Triaged by business impact. n8n workflows and Telegram bots are production. Whisper, Ollama, the secondary services could absorb a gap. I left the AWS only artifacts behind on purpose.
- Consequence: Production live in 72 hours. The secondary services came back later, which was acceptable.
- Trap: Do not say "I prioritized everything." Say "I left things behind on purpose."

**F3. Walk me through a tradeoff you made between speed and rigor.**
- Story: 4. n8n SOAR From Zero
- Problem: I needed orchestration in weeks, not quarters. Commercial SOAR would have taken months to procure.
- Specifics: Picked n8n for self hosting and credential store. Made one rigor non negotiable: every workflow has an error path. Dropped other rigor (no test framework yet, manual cutover for new workflows) on purpose.
- Consequence: 14 workflows shipped, the one rigor that mattered held, the rest is a backlog I can address.
- Trap: Do not pretend you did not drop anything. Name what you dropped and why.

**F4. How do you handle competing priorities from different stakeholders.**
- Story: 8. PCI DSS Cross Functional at Texaco
- Problem: Three stakeholders, three different definitions of done. Owner wanted no downtime. Payment processor wanted attestation. POS vendor wanted scheduled cutover windows.
- Specifics: One page plan with three views, one sentence each. Same plan, three languages.
- Consequence: 70 percent PCI scope reduction, zero downtime, attestation renewed on time.
- Trap: Do not list the stakeholders. State the translation move.

### Theme G. Customer empathy and GTM partnership (3 questions)

**G1. Tell me about a time a customer changed how you built something.**
- Story: 10. NeMo Local Inference Architecture
- Problem: A real customer in the AI triage scenario would not send sensitive payloads to a cloud model. I felt that constraint personally during my own build.
- Specifics: Split the pipeline at ingest. Classifier decides cloud safe versus local. Same JSON schema both lanes.
- Consequence: 100 percent of sensitive payloads stay on local infra, cloud handles the rest at frontier quality.
- Trap: Do not say "the customer asked for it." Say "the customer's data classification was the design constraint."

**G2. How do you partner with go to market or customer success.**
- Story: 8. PCI DSS Cross Functional at Texaco (translated to GTM language)
- Problem: My peer at the franchise was the operations side, which is the equivalent of GTM. He needed financial framing, not technical detail.
- Specifics: I translated every technical decision into business cost. PCI fine schedule, downtime cost, breach response cost.
- Consequence: He stopped pushing back on technical work because he had the frame to own the conversation with the owner.
- Trap: Do not condescend. The translation is respect for what the other side is solving for.

**G3. Tell me about a time you turned a customer complaint into a product change.**
- Story: 1. POS Skimmer Investigation at Texaco (the runbook)
- Problem: One customer surfaced a card decline. The product gap was that we had no playbook for "alert from a human, not from a system."
- Specifics: After the case I wrote the six step IR runbook with explicit steps for the human reported pattern. It treated the customer as a first class signal source.
- Consequence: 8 hours to 90 minutes containment on the next case. The runbook was the productized version of one customer's complaint.
- Trap: Do not say "the customer was right." Say "the customer was a signal that the system was missing."

### Theme H. On call and production incidents (3 questions)

**H1. Tell me about a production incident you handled.**
- Story: 1. POS Skimmer Investigation at Texaco, with 11. DigitalOcean Migration From AWS as backup
- Problem: PCI environment, no SIEM alert, customer complaint as the trigger.
- Specifics: Cheapest checks first, evidence preservation second, payment processor coordination third, physical inspection last.
- Consequence: 90 minutes to containment, zero additional cards.
- Trap: Do not narrate adrenaline. Narrate the order of operations.

**H2. Walk me through how you stay calm when the system is on fire.**
- Story: 11. DigitalOcean Migration From AWS
- Problem: AWS instance suspended, 13 containers down, no budget to restore.
- Specifics: First move was triage, not migration. n8n is production, the rest is not. I worked one decision at a time, not all of them at once.
- Consequence: 72 hours to live, zero production downtime on the workflows that mattered.
- Trap: Do not say "I stayed calm." Say "I narrowed the decision space."

**H3. Tell me about a time you escalated.**
- Story: 1. POS Skimmer Investigation at Texaco (the payment processor call)
- Problem: I needed BIN range correlation across the broader payment network, which was outside my access.
- Specifics: Called the processor's fraud line with timestamps and BIN range. Shared the cert chain finding so they had ground for their own investigation.
- Consequence: They confirmed a fraud cluster on that terminal and reimbursed the customer.
- Trap: Do not say "I asked for help." Say "I escalated with evidence so the next layer could act."

### Theme I. Hiring, culture, team building (2 questions)

**I1. What kind of engineer do you want to work with.**
- Framing answer, no story:
- Problem: I want to work with engineers who argue about alert quality at 11 PM and care which JSON field a tool call returns.
- Specifics: The two markers I look for are how someone handles being wrong (do they update the model in their head, or do they re argue) and what they write down (do they leave a trail for the next person, or do they keep it in their head).
- Consequence: Those two markers predict every other behavior I care about on a small team.
- Trap: Do not list traits. Name two markers and explain why they matter.

**I2. Tell me about a time you flagged a bad cultural signal.**
- Framing plus partial pull from 3. Falco Alert Tuning 200 to 12
- Problem: When I joined the Falco feed, engineers had stopped reading it. That was a culture signal, not a tooling one.
- Specifics: I treated "the team has tuned out the alerts" as a leading indicator of detection failure. Fixed the noise first so the cultural signal could come back.
- Consequence: Engineers reading the feed daily within a month. The signal recovery was the culture recovery.
- Trap: Do not turn this into a hiring story. State that engineering culture and detection quality fail together.

---

## 3. The "tell me about yourself" answer

Three variants. Pick one based on Eric's opener.

### 60 second variant (default, if Eric asks "tell me a bit about yourself")

> "I'm Emmanuel Tigoue, AI Security Engineer at CoreDirective. I run a 13 container production stack on DigitalOcean with an n8n SOAR layer and a Claude Opus 4.7 gateway I red teamed against the OWASP LLM Top 10. Before CoreDirective I was the security engineer at a Texaco franchise in Atlanta where I ran real investigations end to end, packet capture, endpoint forensics, payment processor coordination, dropped mean time to contain from eight hours to ninety minutes. The two sides of that work, building AI systems that investigate and doing investigation work as a human, are the exact intersection Dropzone hires for. That's why I'm in this room."

### 90 second variant (if Eric asks for more depth)

> "I'm Emmanuel Tigoue, AI Security Engineer at CoreDirective. I run a 13 container production stack on DigitalOcean. Postgres, n8n SOAR, Vault, Keycloak, Teleport, Falco, Datadog, a Claude Opus 4.7 gateway. Python and Terraform throughout, eight OPA policies gating every deploy.
>
> The work that maps closest to Dropzone is the AI gateway. I red teamed it against OWASP LLM Top 10 and MITRE ATLAS, ten attack classes, two layer defense with input filter and output classifier on tool call args, every request logged for behavior diff after model upgrades. Caught two regressions during the last model cutover.
>
> Before CoreDirective I was the security engineer at a Texaco franchise in Atlanta. One case I keep coming back to: a customer reported a card decline with no SIEM alert. I pulled the wire, found outbound TLS to a four day old self signed cert domain, isolated at the switch, called the processor with BIN range. Eight hour containment dropped to ninety minutes on the next case.
>
> Dropzone owns investigation quality on an AI SOC analyst. I've built AI systems that investigate, and I've done the investigation work myself. That's why this role."

### 2 minute variant (if Eric explicitly says "take your time")

> "I'm Emmanuel Tigoue, AI Security Engineer at CoreDirective in Atlanta. The work sits at the intersection of two things Dropzone cares about. AI systems that investigate, and the human craft of investigation itself.
>
> On the AI side, I run a 13 container production stack on DigitalOcean. Postgres, n8n SOAR with 14 active workflows, Vault, Keycloak v26 for identity, Teleport v18 for privileged access, Falco for eBPF detection, Datadog for observability, and a Claude Opus 4.7 gateway I call OpenClaw. Python and Terraform throughout. Eight OPA policies gate every deploy, zero policy violations in production.
>
> The interesting piece for this role is the gateway security work. I red teamed OpenClaw against OWASP LLM Top 10 and MITRE ATLAS. Ten concrete attack classes, not vibes. Wrote a Python harness that fired prompt injection payloads from public corpora plus locally generated variants, scored responses for system prompt leakage, tool misuse, excessive agency, exfil via tool calls. Two layer defense, input filter on jailbreak patterns, output classifier on tool call arguments before execution. Per token allowlist for skill access. Logged every request to Postgres so I could diff behavior after model upgrades. When Opus 4.6 shipped I reran the harness before cutting traffic over and caught two regressions in tool call handling.
>
> On the investigation side, before CoreDirective I was the security engineer at a Texaco franchise in Atlanta. The case I keep coming back to: a regular at the store reported her card declined at one pump and worked across the street. No SIEM, no EDR, just a customer and a gut feeling. PCI environment, 45 plus devices on a flat network. I pulled the transaction log first because it cost nothing, then a span port and Wireshark on the pump, found outbound TLS to a four day old self signed cert domain, isolated at the switch to keep memory and disk intact, called the payment processor with BIN range and timestamps. Eight hour containment on a guess dropped to ninety minutes once I had the runbook written.
>
> Dropzone hires this role to own investigation quality on an AI SOC analyst. I've built the AI side, I've done the human side, and I want to ship that quality at scale. That's the job."

---

## 4. The "why Dropzone" answer (45 seconds, no buzzwords)

> "Three reasons. First, Edward Wu's ExtraHop lineage tells me the founders understand what good detection looks like at scale, which is rare in this category. Second, OSCAR is real investigation methodology, not playbook automation. Observe, scope, contain, analyze, remediate, lessons learned, that's the same shape as the runbook I wrote at Texaco after the skimmer case. Third, the role mandate is the part of your product where I have evidence on both sides of the agent. I've built AI systems that investigate, and I've run investigations as a human. The match is rare and it is real."

Forty four seconds at conversational pace. Anchored to investigation quality and OSCAR. No "passionate," no "excited," no buzzwords.

---

## 5. The "why are you leaving CoreDirective" answer

> "CoreDirective is my LLC. I'm AI Security Engineer there because I built it that way. The reason I'm in this room is scale. I've shipped investigation quality on one stack, my own, and I want to ship it on every SOC. That's a product company with real customers, not a one person back office. CoreDirective continues, the work continues, but the next slot for the work I want to do at the scale I want to do it is here."

No founder talk. No "my company." States CoreDirective is the LLC, names the role he holds there, frames the move as scale.

---

## 6. The "weakness" answer

Real, specific, with a remediation in flight.

> "I default to building the system before I build the regression suite for it. On the OpenClaw gateway I shipped the inference path first and the red team harness second, which meant my first month of production was unobserved against the harness. I caught up, but the right sequence was harness first, gateway behind it. The fix that I'm running now: any new model or skill on the gateway runs the harness as a pre deploy gate before traffic cuts over. That sequence is now the default. The next test is whether I keep that discipline when the new build is exciting and the harness is the boring part."

Real weakness (sequencing), specific story (OpenClaw), remediation in flight (harness as pre deploy gate), self aware about the recurrence risk.

---

## 7. Recommendation for the "biggest mistake" answer

**Recommended:** the Falco tuning regression frame, because it is the cleanest engineering mistake in the bank and lands well with a Director of Engineering. The n8n SOAR rollback is too thin for this prompt. A real production incident is too dramatic for 60 to 90 seconds.

> "When I first tuned the Falco rules I dropped three rules that were driving 78 percent of the noise. I rewrote them with explicit process lineage and namespace filters. What I missed on the first pass: I did not map the rewritten rules back to MITRE ATT and CK before promoting them. Two weeks in I noticed a coverage gap on a technique I had assumed was still covered, because the new rule was tighter than I had realized. The fix was to add ATT and CK mapping as a non negotiable step before any rule promotion. The fix held. Two real findings the following month would have been buried in the old noise, and one of them was on a technique that was still covered because I had caught the gap before promotion. The lesson: in detection engineering, tighter rules without coverage mapping is a regression you do not see until something fires that should not have been visible."

Real mistake (coverage gap from over tightening), real fix (ATT and CK mapping as a gate), real signal (caught the gap before it cost a real finding). 70 seconds at conversational pace.

---

## 8. The "disagreement with manager" answer (Emmanuel reports to himself)

Emmanuel is AI Security Engineer at CoreDirective, his own LLC. There is no manager to disagree with. Reframe to a customer disagreement (the Texaco store owner) or a peer engineer disagreement (n8n credential remapping community advice). Pre built version below uses the store owner because it has the strongest specifics and the best result.

> "I should give context first. CoreDirective is my LLC, so the closest analog to a manager disagreement in my work is when I disagreed with the store owner at the Texaco franchise where I was the security engineer. He wanted to prioritize a faster customer Wi-Fi rollout over PCI segmentation. His logic was that customers see slow Wi-Fi and customers do not see segmentation, which was technically correct.
>
> I did not argue protocols. I pulled the PCI fine schedule for a mid tier merchant, the average breach response cost for a store his size, and the daily card volume converted to dollars per day of lost revenue if the processor suspended us. One page, three numbers. Then I offered a compromise that respected his customer signal: segmentation first, guest Wi-Fi VLAN built into the same cutover so customers got faster Wi-Fi the following week.
>
> Ten minute conversation. He agreed. Both projects shipped within a week. Relationship intact, which mattered because I needed him for three more projects. The lesson I take into engineering work: when a stakeholder speaks in dollars, technical rightness without a financial frame is losing."

Acknowledges the structural fact (no manager), reframes cleanly to a real disagreement, lands with a senior engineering takeaway.

---

## 9. The peer engineer disagreement answer (B2 from the bank)

Use this if Eric explicitly asks "have you disagreed with another engineer."

> "After the DigitalOcean migration my n8n credentials kept failing at runtime even though the UI, the CLI, and the REST API all said the new credential IDs were wired correctly. I posted on the n8n community and the consensus answer was that I needed to re export and re import the workflows, and that the runtime would catch up. I disagreed because I had already done that twice and the failure was deterministic.
>
> I went to the database. Dumped the workflow_entity table and found that n8n 2.x also stores a snapshot in workflow_history that the runtime executes against. The history row still had the old credential ID. The community advice would not have fixed it because the import path does not touch workflow_history.
>
> I wrote a scoped SQL migration with a transaction and a rollback path, ran the text replace on the nodes JSONB in both tables, and the next workflow run was clean. I posted the finding back to the community with the table name and the SQL snippet. The lesson: when the UI, the API, and the CLI all agree and the runtime still disagrees, the truth is in the database. Read the schema before you trust the consensus."

Real peer disagreement (community consensus was wrong), real engineering judgment (read the schema), real artifact left behind (the post). Maps to Story 12 in the bank.

---

## 10. Curveballs

Ten left field questions a Director of Engineering might throw to see how a candidate thinks off script. 30 second answers each.

**X1. What is the last book you read on engineering.**
> "Camille Fournier's 'The Manager's Path.' Read it because I run a one person stack and I wanted to understand how a real engineering org would scale the work I'm doing solo. The chapter on tech lead behavior, especially the part about setting the bar through artifacts not meetings, is what I keep coming back to."

**X2. What is an opinion about AI in the SOC that most people disagree with.**
> "Most people frame the AI SOC analyst question as 'can AI do tier one.' My read is the harder question is 'can AI's reasoning hold up under review by a human investigator.' The accuracy of the verdict is easier than the auditability of the path to the verdict. Investigation quality is a writing problem, not just a detection problem."

**X3. Describe a system you admire and why.**
> "Stripe's idempotency key model on the API. It's a single design decision that propagates safety through every retry path in every customer integration. The reason I admire it: one engineering decision, made early, removes a category of customer pain forever. That is the kind of decision I want to be making at Dropzone."

**X4. What is something you have changed your mind on in the last year.**
> "I used to think alert tuning was about deletion. Drop rules, cut volume, ship. I'm now firm that tuning is rewriting rules with enough precision that a human can trust the feed. The Falco work made the case. Same coverage, less noise, only because the rules carried more context per alert."

**X5. What is your favorite debugging tool.**
> "psql against the production database with read only credentials. Most of my hardest debugging stories end at the schema. The n8n credential remapping issue, the Falco rule diff job, the OpenClaw request log queries. The UI lies, the API lies, the docs lie, the schema does not."

**X6. Tell me about a project you killed.**
> "A custom OpenClaw skill I wrote to do invoice categorization with chained tool calls. I killed it because the chain was three tools deep and the failure mode on a tool call regression was silent. Replaced it with a single tool call plus a structured prompt. The lesson: tool call depth is a debt, not a feature."

**X7. What is the worst code review feedback you have given or received.**
> "Worst received was 'this looks fine, ship it' on an n8n workflow that had no error path. The reviewer was being fast, not careful. I now treat 'looks fine' as a non review and ask for the failure path explicitly. Worst given was 'this needs more thought' with no specifics. Vague feedback is worse than no feedback."

**X8. What is your favorite metric.**
> "MTTR on a workflow failure. Not because it is the most important metric, but because it tells me whether the error path is wired correctly. A long MTTR means the failure is silent. A short MTTR means the system is honest about what broke."

**X9. If you had a free week to work on anything, what would you ship.**
> "I would build a behavior diff tool for OpenClaw that takes the same prompt set and runs it against two model versions, reporting tool call shape changes, output schema drift, and confidence variance. It is the tool I needed for the Opus 4.6 cutover and I rebuilt it from scratch each time. It belongs as infra."

**X10. What question would you ask if you were sitting in my chair.**
> "I would ask the candidate to describe the worst alert they ever investigated, and what they wrote down after. The first half tells me whether they have done the work. The second half tells me whether they leave the next investigator better off."

---

## Final delivery checklist

- Land every answer in 60 to 90 seconds. Crisp beats thorough.
- Lead with identity, not certifications, not school.
- Numbers in the first ten seconds of any technical story.
- End every story with a one sentence takeaway that sounds like a senior engineer talking, not a slide.
- Return to the red thread once every fifteen minutes, verbatim if possible:
  > "I care about investigation quality. I've done it as a human, I've built systems for it, and I want to ship it at scale to every SOC in the world."
- Banned phrases stay banned: pivoting, transitioning, aspiring, bridging, passionate, rockstar, fast learner. No em dashes. No juxtaposition phrasing.
- If you do not know a number, say "the order of magnitude was X, I'd need to check the exact figure." Do not guess.
- Last 5 minutes, ask Eric: "What does success look like for the person in this role at the 90 day mark, and where does it most often go wrong." That question signals seniority and gives you the next round's framing.
