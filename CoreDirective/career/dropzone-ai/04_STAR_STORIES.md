# Dropzone AI Interview — STAR Story Bank

**Candidate:** Emmanuel Tigoue
**Role:** Senior Security Engineer (Investigation Quality, AI SOC Analyst)
**Prepared:** 2026-04-16

Twelve behavioral stories ordered by interview value. Voice is direct, numbers first, senior. Each story is built to land in 60 to 90 seconds.

---

## 1. POS Skimmer Investigation at Texaco

**Tag:** This is a story about running an investigation end to end when the alert was a customer complaint, not a SIEM hit.

**Questions this answers:**
- Tell me about a time you investigated a security incident.
- How do you approach ambiguous alerts?
- Walk me through a time you had to preserve evidence under pressure.
- How do you prioritize investigation steps when you don't know what you're looking for?
- What does "investigation quality" mean to you?

**Situation (S).** A regular at my Texaco store in Atlanta reported that her card declined at our pump, then worked fine across the street. No SIEM, no EDR alert. Just one customer and a gut feeling. PCI environment, 45 plus devices, payment processor on the other end.

**Task (T).** Confirm or rule out a compromise at the terminal, without tipping off an attacker if real, and without killing forensic data.

**Action (A).** I pulled the transaction log for that pump first and compared timestamps against the store's network flow records. Nothing obvious in the transaction data, so I pivoted to the wire. Plugged a span into the pump's switch port and ran Wireshark for 20 minutes. I saw an outbound TLS session to a domain that was four days old per WHOIS, on port 443, with a self-signed cert that failed chain validation. That was the tell. I isolated the terminal at the switch rather than powering it down, because I wanted memory and disk state intact. I called the payment processor's fraud line, gave them the BIN range and timestamps, and we flagged transactions from that pump for the previous 72 hours. Then I walked the physical terminal looking for skimmer hardware. Nothing external, the compromise was software side. I wrote up the chain of evidence the same night and coordinated the rebuild with the POS vendor the next morning.

**Result (R).** Zero additional cards compromised after isolation. Payment processor confirmed fraud cluster on that terminal and reimbursed the one customer who surfaced it. I later turned the sequence into a six step IR runbook. Mean time from customer report to containment dropped from what would have been around eight hours of guessing to 90 minutes on the next incident.

**Takeaway.** Investigation quality is not about the alert that fires, it is about the one customer who tells you something is wrong. I start with the human signal, then make the wire confirm or deny it.

---

## 2. OpenClaw AI Gateway Red Team

**Tag:** This is a story about treating an AI system the same way I'd treat any production service, with threat models and regression tests.

**Questions this answers:**
- Tell me about a hard technical problem you solved recently.
- How do you think about quality of an AI system?
- What's a time you had to learn a new domain fast?
- How do you approach security of LLM applications?
- Tell me about a project where you set your own standard for "done."

**Situation (S).** I stood up OpenClaw, a Claude Opus 4.7 inference gateway behind my own infra, routing prompts from Telegram bots, n8n workflows, and a Mac CLI node. Handles sensitive operational data. No pre built playbook for securing it.

**Task (T).** Own the security posture of the gateway before it went into daily use across my stack.

**Action (A).** I built the threat model against OWASP LLM Top 10 and MITRE ATLAS. That gave me ten concrete attack classes to test against, not vibes. I wrote a red team harness in Python that fired prompt injection payloads from known public corpora plus variants I generated locally, scored responses for system prompt leakage, tool misuse, excessive agency, and data exfiltration via tool calls. I added detection at two layers: input filter on the gateway for known jailbreak patterns, and output classifier that inspected tool call arguments before execution. I gated skill permissions with an explicit allowlist per token, so a leaked token couldn't pivot into GitHub or Gmail tools by default. I logged every request and response to Postgres so I could diff behavior after model upgrades. When Opus 4.6 shipped, I reran the harness before cutting traffic over. I found two regressions in tool call handling and held the rollout until the classifier was updated.

**Result (R).** Zero confirmed prompt injection successes against the gateway in production across 90 days. Caught two model upgrade regressions before cutover. Harness is now my standard pre deploy gate for any new model or skill. The methodology also became a GRC artifact that maps directly to NIST AI RMF.

**Takeaway.** Investigation quality for an AI system means you have a regression suite for behavior, not just code. Models change, your tests catch it, or your customers do.

---

## 3. Falco Alert Tuning 200 to 12

**Tag:** This is a story about killing alert noise without killing detection coverage.

**Questions this answers:**
- Tell me about a time you reduced false positives.
- How do you think about signal to noise in a detection pipeline?
- Describe a detection engineering win.
- How do you balance coverage against analyst fatigue?
- What is your approach to rule tuning?

**Situation (S).** I inherited a Falco eBPF deployment at CoreDirective generating 200 plus alerts a day across 13 containers. Most were benign. Engineers were ignoring the feed, which meant the few real ones got ignored too.

**Task (T).** Get the alert volume down to something a human would actually read, without dropping coverage on the attack patterns that mattered.

**Action (A).** First I pulled 14 days of alerts out of Falco and clustered them by rule ID, container, and process. Three rules accounted for 78 percent of the volume, all of them tied to normal container startup behavior. I did not disable them. I rewrote the conditions with explicit process lineage and namespace filters so they only fired on the unexpected case. Then I mapped every remaining rule to MITRE ATT and CK technique IDs so I had a clear picture of what coverage I had and where I was blind. I routed the tuned output through Falcosidekick into Datadog, added a second tier for high severity that paged Telegram, and left the rest as a low priority dashboard for weekly review. I also added a weekly job that diffs alert fingerprints against the previous week and flags new clusters, because the worst thing is a new alert silently joining the noise floor.

**Result (R).** Daily volume went from 200 plus to about 12 actionable findings a day. Coverage of the MITRE techniques I cared about stayed the same or expanded. Analyst eyes on the feed went from zero to daily. Two real findings in the first month would have been lost in the old noise.

**Takeaway.** Tuning is not deleting rules, it is writing them with enough precision that a human can trust the feed. If your analysts tune out, your detection layer is already dead.

---

## 4. n8n SOAR From Zero

**Tag:** This is a story about shipping a SOAR stack in weeks without a team and without a playbook.

**Questions this answers:**
- Tell me about a time you built something from scratch under ambiguity.
- How do you move fast in a startup environment?
- Describe a time you had to pick your own stack and own the outcome.
- How do you decide when something is good enough to ship?
- What is the biggest system you have built solo?

**Situation (S).** I needed automation across my stack for incident response, content operations, Gmail triage, and finance ops. No existing orchestration layer, no budget for commercial SOAR, one person owning the outcome.

**Task (T).** Ship a production grade orchestration layer that I could trust with real work, fast.

**Action (A).** I picked n8n because it was self hostable, had a credential store, and would let me version workflows as JSON. I stood it up on the DigitalOcean droplet behind Cloudflare Tunnel so there was no public ingress. I built MASTER\_ORCHESTRATOR\_V1 as a single webhook entry point with an action router that dispatches to 16 services. That forced me to think of every workflow as a function with a typed contract, which made the rest easier. I wired 20 plus credentials through n8n's credential store so no secret lived in a workflow body. For each workflow I wrote a failure path that dumped to an Error Handler workflow, which is the piece most n8n users skip. I built the Gmail readers for four accounts, a content research pipeline, a Gumroad solvency check, a daily API health sweep, and the Telegram supervisor agent that listens for my commands. Every workflow got a manual test case plus a cron or webhook trigger. I versioned all of it in git as exports and set up automated imports on the droplet.

**Result (R).** 14 active production workflows in under a month, one inactive by design. Zero credential leaks. The orchestrator has handled thousands of requests with a documented error path for every action. MTTR on workflow failures is under 10 minutes because the Error Handler posts directly to Telegram with the node that failed and the input payload.

**Takeaway.** In a startup you do not wait for the right tool, you pick one and put guardrails on it. The guardrail that matters most is the error path.

---

## 5. Splunk MTTD 48 Hours to Under 4

**Tag:** This is a story about turning a SIEM from a log warehouse into a detection engine.

**Questions this answers:**
- Describe a measurable security outcome you drove.
- How do you approach detection engineering?
- Tell me about a time you improved a metric the business cared about.
- What does MTTD mean in practice and how do you drive it down?
- How do you know a detection rule is good?

**Situation (S).** Splunk at the store environment was being used as a search box. Real incidents were surfacing through customer reports or payment processor calls, not through alerts. Mean time to detect was roughly two days.

**Task (T).** Build detection content and correlation logic that would surface the incidents that mattered inside a single shift.

**Action (A).** I inventoried the log sources first so I knew what I could detect against: POS transactions, switch syslog, DNS, DHCP, and the payment processor callback logs. Then I wrote detection use cases tied to the business, not the framework. The top three: unexpected outbound TLS to newly registered domains from a POS VLAN, card transaction failure rate spikes per terminal, and DHCP lease changes on the segmented POS network. Each use case got a correlation search, a threshold tuned on 30 days of baseline, a severity, and a named response runbook. I ran each rule in alert only mode for a week, measured false positive rate, adjusted, then promoted to notable. I also built a dashboard that sorted notables by business impact, not alphabetical rule name, because attention is the real scarce resource.

**Result (R).** MTTD dropped from around 48 hours to under 4 across the validation period. False positive rate on the three core rules stayed under 5 percent. The POS outbound rule caught the self signed cert behavior pattern on a second terminal before a customer ever noticed.

**Takeaway.** A detection rule is good when it lets an analyst stop investigating alphabetically and start investigating the business.

---

## 6. CoreDirective Accounting AI

> USER NOTE: Fill in bracketed details during prep. This is your AI as a solution for humans at work story. Maps directly to Dropzone's core value prop.

**Tag:** This is a story about putting AI into a governed workflow for real financial work, not a demo.

**Questions this answers:**
- Tell me about a time you used AI to solve a real business problem.
- How do you think about AI governance?
- Describe working with a non technical stakeholder on an AI deployment.
- What is an example of AI replacing human effort responsibly?
- How do you measure whether an AI solution is actually working?

**Situation (S).** CoreDirective's accounting and legal compliance work was being done by my partner. That was a single point of failure for the business, and it was eating hours that belonged in revenue work.

**Task (T).** Design an AI assisted workflow that handled the recurring compliance tasks, with guardrails strong enough that I would trust it on our actual books.

**Action (A).** I scoped the workflow to [SPECIFIC TASKS: e.g., invoice categorization, sales tax reconciliation, expense classification against COA]. I picked [SPECIFIC TOOL: e.g., Claude via OpenClaw with a custom accounting skill / Ollama local model / n8n workflow with LLM node] because [REASON: e.g., data sensitivity required local inference / tool calls needed strict allowlist / cost at our volume]. I wrote the system prompt around explicit rules [SPECIFIC RULES APPLIED: e.g., GAAP revenue recognition category, GA sales tax thresholds, LLC expense categorization rules]. I added a human review gate on any transaction above [DOLLAR THRESHOLD] and any new vendor not already in the chart of accounts. Every AI decision logged to [STORAGE: e.g., Postgres table with prompt, response, action taken, reviewer signoff]. I added a weekly reconciliation job that compared AI categorizations against bank feed and flagged variance. I also built a kill switch so my partner could disable the automation with one Telegram command if anything looked off.

**Result (R).** [SPECIFIC METRIC: e.g., X hours per week of partner time returned to revenue work]. [SPECIFIC METRIC: e.g., categorization accuracy measured at Y percent against manual review]. [SPECIFIC OUTCOME: e.g., books closed on time for Q without partner doing catch up work]. Zero compliance issues flagged by [CPA / filing / audit] since deployment.

**Takeaway.** AI earns production access when it has a review gate, a log, and a kill switch. Anything less is a demo pretending to be a workflow.

---

## 7. 37 GRC Documents in Two Months

**Tag:** This is a story about shipping a full compliance library solo, with enough rigor that an auditor would accept it.

**Questions this answers:**
- Tell me about a time you shipped a lot under pressure.
- How do you structure a large body of work when you own it end to end?
- Describe your writing and documentation approach.
- How do you balance depth against deadline?
- What does production quality mean in a non code deliverable?

**Situation (S).** CoreDirective needed a defensible GRC posture for client conversations and for my own AI and data handling work. I had no template library, no legal team, no prior org artifacts.

**Task (T).** Produce a complete GRC library covering policy, risk, incident response, and threat modeling, good enough to hand to a security reviewer and survive questions.

**Action (A).** I scoped it as a product with a table of contents first, not a document pile. 37 documents across six categories: SSP with NIST 800-53 mapped controls, POA and M with 37 findings tracked across four sources, 10 policies including AI Governance, five IR playbooks including AI Incident, risk assessment, tabletop reports, threat modeling, CIS risk register, and executive summaries. I set a sanitization standard up front so the public versions could live in the repo without leaking personal or infra detail, and I kept a reverse mapping key offline. I wrote each doc against a real scenario I had run, not a template. The IR playbook for POS compromise was the Texaco investigation written in a playbook shape. The AI Incident playbook was the OpenClaw red team turned into a response plan. I ran a six agent QC audit across the set before publishing, cross linking the docs so controls, findings, and policies pointed at each other.

**Result (R).** 37 documents, roughly 15,000 lines, published in under two months. Library is indexed and cross referenced. The sanitized version is public on GitHub as the live artifact of my engineering practice. Zero rework demanded by the reviewers who read it.

**Takeaway.** Documentation is a product. If you do not treat the library as a system, you get a pile of Word files that nobody trusts.

---

## 8. PCI DSS Cross Functional at Texaco

**Tag:** This is a story about getting a PCI environment into shape with three outside vendors in the loop.

**Questions this answers:**
- Tell me about a time you worked across teams or vendors.
- Describe a compliance project you owned.
- How do you handle stakeholders who do not share your technical context?
- Give an example of coordination under a real deadline.
- How do you approach segmentation in a hostile environment?

**Situation (S).** Texaco store environment had 45 plus devices on a flat network, a PCI scope that was effectively the entire LAN, and an owner who wanted a fix that would not slow the store down.

**Task (T).** Get the cardholder data environment into a defensible shape and reduce PCI scope, while keeping the business running.

**Action (A).** I mapped the devices first: POS terminals, pumps, back office workstation, CCTV, Wi-Fi, printers, and the owner's personal devices. Then I drew the target state on one page: four VLANs, POS isolated with its own uplink, back office on a management VLAN, guest and personal traffic on a Wi-Fi VLAN, and CCTV on its own because the vendor's firmware was not something I was willing to trust on shared segments. I coordinated with the payment processor to confirm the segmentation would satisfy their attestation requirements. I coordinated with the POS vendor to schedule IP changes outside of business hours. I walked the owner through the plan in financial terms, not protocol terms: a breach on a flat network is a closed store and a card brand fine, segmentation is a weekend of work. I did the switch config changes, tested each VLAN, validated with Nmap from the wrong side of the segment, and signed off with the payment processor.

**Result (R).** PCI scope reduced to the POS VLAN and the point to point uplink, roughly a 70 percent reduction in in scope devices. Zero downtime during the cutover window. Payment processor attestation renewed on time. Owner understood why and signed off without pushback.

**Takeaway.** Cross functional work is a translation job. Every stakeholder gets the same plan in their language.

---

## 9. Segmentation vs Wi-Fi Disagreement

**Tag:** This is a story about winning a technical argument by reframing it in dollars.

**Questions this answers:**
- Tell me about a time you disagreed with a stakeholder and how you resolved it.
- How do you influence without authority?
- Describe a time you had to push back on a business priority.
- How do you communicate risk to non technical leadership?
- Give an example of persuasion that worked.

**Situation (S).** During the PCI segmentation project at Texaco, the owner wanted me to prioritize a faster Wi-Fi rollout for customers over the VLAN work. His logic was that customers noticed slow Wi-Fi, customers did not notice PCI scope.

**Task (T).** Change his mind without lecturing him, because I worked for him and he was right that customers do not see segmentation.

**Action (A).** I did not argue the technical side. I pulled the PCI fine schedule for a mid tier merchant, the average cost of a card brand breach response for a store his size, and the downtime he would absorb if the payment processor suspended our ability to take cards. Then I added his daily card volume and showed him how many days of store closure that would be. I gave him a one page with three numbers: cost of a weekend of segmentation work, cost of a breach, cost of a day of store closure. I also offered a compromise that respected his signal: I would finish segmentation first, then stand up a guest Wi-Fi VLAN as part of the same cutover so customers got the faster Wi-Fi the following week. That gave him a win on both.

**Result (R).** He agreed to the segmentation first path inside a 10 minute conversation. Guest Wi-Fi shipped the week after segmentation. Customers got their faster network, and the store got PCI scope reduction. Relationship stayed intact, which mattered because I needed him for three more projects.

**Takeaway.** If your stakeholder speaks in dollars, translate. Technical rightness without a financial frame is losing.

---

## 10. NeMo Local Inference Architecture

**Tag:** This is a story about making an architecture decision driven by what the customer was actually willing to send over the wire.

**Questions this answers:**
- Tell me about a design decision you made under constraint.
- Describe a time customer requirements changed your architecture.
- How do you handle sensitive data in AI workflows?
- What is an example of customer obsession in your design work?
- Walk me through a privacy or data residency tradeoff.

**Situation (S).** I was building an AI triage workflow that would classify and enrich security events. The obvious architecture was to send events to Claude over the cloud API. The blocker: several event types contained data I was not willing to send to a third party model, and a real customer in this situation would feel the same way.

**Task (T).** Design a triage path that kept sensitive data on infrastructure I controlled, without giving up the quality of a frontier model on the events where it was safe.

**Action (A).** I split the pipeline into two lanes at ingest. A classifier decided whether an event was cloud safe or local only, based on tags like data classification, source, and keyword detection on payload. Cloud safe events went to Claude via OpenClaw with the normal tool call surface. Local only events routed to Ollama running on the droplet, with a NeMo guardrails layer in front for input validation, toxicity, and PII detection. I designed the prompts so the local model and the cloud model returned the same JSON schema, which meant downstream automation did not care which lane answered. I built a fallback where a local model failure could escalate to cloud only after an explicit sanitization pass stripped the fields that triggered the classifier in the first place. Every routing decision was logged with the rule that fired, so the customer equivalent could audit it.

**Result (R).** 100 percent of sensitive payloads handled on local infrastructure. Cloud lane handled the majority of volume at frontier model quality. Downstream automation stayed schema stable through model changes on either lane. Design became the template I would bring to a customer with data residency concerns.

**Takeaway.** Customer obsession in AI work is an ingest decision, not a model decision. Decide what leaves your network first, then pick the model.

---

## 11. DigitalOcean Migration From AWS

**Tag:** This is a story about moving a live stack in days when the bill stopped being payable.

**Questions this answers:**
- Tell me about a time you handled a crisis or unplanned work.
- Describe a resilience or cost moment you owned.
- How do you plan a migration under time pressure?
- What is an example of working under real resource constraint?
- How do you prioritize when you cannot do everything?

**Situation (S).** AWS EC2 instance for my stack got suspended for nonpayment. 13 containers, n8n workflows running daily operations, Cloudflare tunnels terminating into that instance, no budget to restore the AWS account.

**Task (T).** Move the stack to cheaper infrastructure fast, with zero downtime for the workflows that mattered to the business.

**Action (A).** I did not lift and shift. I triaged by business impact first. n8n workflows with scheduled triggers and the Telegram bots were production, everything else could absorb a gap. I spun up a DigitalOcean droplet with a spec that matched the working set, not the peak: 4 vCPU, 8 GB RAM. I restored the Postgres volume from the last snapshot on day one, brought n8n up against it, and validated that workflow history and credentials survived the move. I rewired Cloudflare tunnel to the new origin without changing the public hostnames, so no downstream integration saw a new URL. I moved credentials from the old env to Doppler during the migration rather than copying the .env forward, which tightened the secret story at the same time. I left the AWS only artifacts behind on purpose and documented the suspension state so future me would not try to revive it.

**Result (R).** Stack live on DigitalOcean in under 72 hours. Monthly cost dropped from AWS levels to 48 dollars a month, covered by GitHub Education credit for four months. Zero downtime on the workflows that mattered. Secret management improved as a side effect of the move.

**Takeaway.** A crisis migration is a forcing function for the cleanup you were going to do anyway. Take the cleanup.

---

## 12. n8n Credential Remapping DB Debug

**Tag:** This is a story about not believing the documentation and reading the code.

**Questions this answers:**
- Tell me about a deep technical debugging session.
- Describe a time you had to understand an internal system you did not build.
- How do you debug something the docs do not cover?
- What is a time persistence paid off on a technical problem?
- How do you validate that a fix actually worked?

**Situation (S).** After the DigitalOcean migration, I recreated n8n credentials with new IDs. Workflows imported via the CLI imported cleanly and the admin UI showed the new credential IDs wired up. At runtime, workflows kept failing with authentication errors that pointed at old credential IDs that no longer existed.

**Task (T).** Find out why the runtime was loading stale credential references and fix it without losing workflow history.

**Action (A).** I started at the UI, confirmed the draft showed the new IDs. Then I hit the REST API and PATCHed a workflow with the new credential map, confirmed the response echoed the new IDs. Re ran the workflow, same failure. At that point I stopped trusting the API layer and went to the database. I dumped the workflow\_entity table and the nodes JSONB, and the credentials were correct there. But I found that n8n 2.x also stores a snapshot in workflow\_history for the version the runtime executes against, and the history row still had the old credential ID. The CLI import had updated workflow\_entity but not the history snapshot. REST API PATCH updated the draft but not the runtime version either on the path I was hitting. I wrote a small SQL migration that did a targeted text replace on the nodes JSONB in both tables, scoped to the old ID strings, and ran it inside a transaction with a rollback path. Re ran the workflow. Clean.

**Result (R).** All 14 workflows ran cleanly on the first execution after the migration. Documented the workflow\_history table behavior in my project notes so future migrations would not cost another afternoon. No history was lost because I scoped the replace to credential ID strings only.

**Takeaway.** When the UI, the API, and the CLI all agree and the runtime still disagrees, the truth is in the database. Read the schema.

---

# Appendix A. Mapping Matrix

Fifteen common behavioral questions mapped to which story to deploy. Primary story first, backup second.

| # | Question | Primary Story | Backup |
|---|---|---|---|
| 1 | Tell me about a time you investigated a security incident. | 1. POS Skimmer | 5. Splunk MTTD |
| 2 | Tell me about a hard technical problem. | 2. OpenClaw Red Team | 12. n8n DB Debug |
| 3 | How do you think about quality of an AI system? | 2. OpenClaw Red Team | 10. NeMo Architecture |
| 4 | How do you reduce false positives? | 3. Falco Tuning | 5. Splunk MTTD |
| 5 | Tell me about shipping under ambiguity. | 4. n8n SOAR | 7. 37 GRC Docs |
| 6 | Tell me about a measurable security outcome. | 5. Splunk MTTD | 3. Falco Tuning |
| 7 | Tell me about using AI for a real business problem. | 6. Accounting AI | 10. NeMo Architecture |
| 8 | Describe shipping a large body of work. | 7. 37 GRC Docs | 4. n8n SOAR |
| 9 | Tell me about a cross functional project. | 8. PCI Cross Functional | 11. DO Migration |
| 10 | Tell me about a disagreement and how you resolved it. | 9. Segmentation vs Wi-Fi | 8. PCI Cross Functional |
| 11 | Describe a design decision under constraint. | 10. NeMo Architecture | 11. DO Migration |
| 12 | How do you handle crisis or unplanned work? | 11. DO Migration | 1. POS Skimmer |
| 13 | Describe a deep debugging session. | 12. n8n DB Debug | 2. OpenClaw Red Team |
| 14 | Tell me about mentorship or leadership. | 7. 37 GRC Docs (set standard for library) | 4. n8n SOAR (set standard for workflows) |
| 15 | Security first mindset when others optimize for speed. | 9. Segmentation vs Wi-Fi | 8. PCI Cross Functional |

**Secondary mapping for Dropzone specific signals:**

| Dropzone Signal | Story |
|---|---|
| Investigation quality | 1, 2, 5 |
| Python production code | 2, 4, 12 |
| Feature flags / rollouts / regression testing | 2 (harness as pre deploy gate), 4 (error handler pattern) |
| Customer obsessed | 1 (started from customer report), 10 (customer data residency) |
| Cross functional with GTM / CS | 8, 9, 6 |
| Mentorship | 7 (set documentation standard), 4 (set workflow standard) |
| Ambiguity tolerance | 4, 7, 11 |

---

# Appendix B. Delivery Tips

**Land each story in 60 to 90 seconds.** Interviewers lose focus after two minutes. A crisp story with a real metric beats a thorough one every time.

**Default structure for 60 to 90 seconds:**
- 10 seconds: Situation. One sentence.
- 10 seconds: Task. One sentence.
- 45 to 60 seconds: Action. Three to five specific moves. Name the tools and the decisions.
- 10 to 15 seconds: Result with a number.
- 5 seconds: Takeaway.

**When to skip the Situation.** If the interviewer already described the context in their question, acknowledge it in four words and jump to the Task. Example: "Right, that's what happened here. My job was to..."

**When to lead with Result.** For pattern questions like "describe a measurable outcome," open with the number. Example: "I dropped MTTD from 48 hours to under four at a PCI retail environment. Here's how." This earns attention for the rest of the story.

**Numbers to memorize cold so you never hesitate:**
- POS skimmer: zero additional cards, 8 hours to 90 minutes, 6 step runbook.
- OpenClaw: zero confirmed injections, 90 day window, two regressions caught pre deploy, 10 attack classes.
- Falco: 200 to 12 daily, 78 percent of noise from three rules, 14 day baseline.
- n8n SOAR: 14 workflows, under a month, 16 services, 20 plus credentials.
- Splunk: 48 hours to under 4, under 5 percent false positive on core rules, 30 day baseline.
- GRC: 37 documents, 15,000 lines, 2 months, 6 agent QC.
- PCI: 45 plus devices, 4 VLANs, 70 percent scope reduction, zero downtime.
- DO migration: 72 hours, 13 containers, 48 dollars a month, zero production downtime.
- n8n DB debug: 14 workflows, clean on first run after fix, transaction scoped SQL.

**Voice discipline.**
- No "I kind of," "sort of," "tried to." Past tense, active verb, subject first.
- No "we" when it was you. No "I" when it was the team. Be precise.
- If you do not know a detail, say "I would need to check the exact number, the order of magnitude was X." Do not guess.

**Handling follow ups.**
- If asked to go deeper, go deeper on the Action, not the Situation. Interviewers rarely want more context, they want more technical specificity.
- If asked what you would do differently, pick one real thing. The OpenClaw red team answer: I would have built the regression harness before I shipped, not alongside. The Falco answer: I would have mapped to ATT and CK on day one, not after tuning.
- If asked "why that tool," have a one sentence reason ready. Not a speech.

**Story sequencing if you get to pick.**
- Lead with Story 1 (POS skimmer) if the interviewer is on the investigation side.
- Lead with Story 2 (OpenClaw) if the interviewer is on the AI quality side.
- Lead with Story 4 (n8n SOAR) if the interviewer is probing for ship velocity.
- Save Story 9 (disagreement) for when they explicitly ask about conflict. Do not volunteer it.
- Story 6 (Accounting AI) is your closer for "what excites you about Dropzone" because it maps directly to their value prop. Have specifics ready before the interview.

**One rule above all.** Every story ends with a takeaway that sounds like something a senior engineer would say out loud, not a training slide. That's what tells them you have done the work, not just the resume.
