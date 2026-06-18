# 08 — INTERVIEW DAY PREP (Fri 2026-05-01, 1:30 PM EST — RESCHEDULED, new date pending)

> **CoreDirective framing source of truth:** see `COREDIRECTIVE_FRAMING_LOCKED.md` in this folder. Any references in this file to "lab" or "personal engineering practice" are superseded by the locked version. CoreDirective is an AI security practice with a real anchor client (accounting firm) and a model-flexible AI stack (router that hits Claude or self-hosted Ollama).

## Logistics

- **When:** Friday May 1, 2026, 1:30 PM – 2:00 PM EST (30 minutes)
- **Where:** Microsoft Teams. Meeting ID `245 477 666 611 950`. Passcode `dy7Fj2kF`. Link: https://teams.microsoft.com/meet/245477666611950?p=ZN4l3MDFlp9FMKybQX
- **Resume on file:** `Emmanuel Tigoue - Cloudflare Engineer (1).docx` (the version Tiana attached)
- **Two interviewers in the room** (Matt Morgan is only CC'd on the invite, not joining)
- **Format read:** 30 min + two people = ~12 min each + 5 min for your questions. This is a screening conversation, not a whiteboard. Expect 3 short technical scenarios, 1–2 behavioral, and "why us / why now."

## Who you are talking to

### JT McFarlin — Sr Manager, Information Security & Security Architect

Player-coach. Atlanta payments lineage: Global Payments → Floor & Decor → Core & Main → Candescent. Every shop on his resume is PCI/SOX-heavy with vendor stack complexity. He's spent 15 years watching controls fail in regulated environments. No public posts, no GitHub, no conference talks — he's a quiet operator who ships.

**What he wants to hear:**
- Architect vocabulary: trust boundaries, blast radius, defense in depth, blast radius reduction, shared responsibility
- Trade-off thinking, not tool-naming. Don't say "I'd put a WAF on it." Say "I'd start by mapping where customer data crosses a trust boundary, then decide what enforcement sits on the edge vs origin."
- Concrete production stories where you owned the call, not "I helped"
- PCI DSS literacy. He's lived it across Global Payments, Floor & Decor, and now a bank-tech vendor

**What he does NOT want:**
- Researcher swagger ("I love breaking things")
- AI-replaces-analysts framing
- Theory without a deploy

### Augustine Jolliffe — likely the GRC / audit-leaning interviewer

Best public match is a 30-year cyber/audit storyteller, ISC2 speaker on "Accelerating Auditing with AI." Identity confidence is medium, but the framing fits the second seat on a Cloudflare interview at a banking SaaS: someone who evaluates whether you understand controls, evidence, and the FFIEC/SOC 2/PCI control narrative — not whether you can hand-write a Worker.

**What he wants to hear:**
- Story arcs, not feature dumps. He literally calls himself a storyteller
- Controls mapped to frameworks. PCI DSS Req 6.4, SOC 2 CC6.1, NIST 800-53 SC-7
- AI used in audit / evidence pipelines. He's published on this. If it lands naturally, mention you'd use LLMs to summarize Cloudflare logs into evidence packages
- Compliance treated as a design input, not paperwork

**What he does NOT want:**
- Packet-level edge minutiae as flex
- "Auditors slow us down" energy
- Dismissal of evidence and audit trail

## Where you stand (your standpoint, anchored)

You are not the candidate with 8 years of multi-zone Cloudflare ops. You are the candidate who:

1. **Runs Cloudflare as code with policy gates.** That's <10% of the candidate pool at this rate. Most candidates click in the dashboard.
2. **Lived PCI DSS as the owner**, not a consultant. Texaco, 4 years, 45+ devices, ran the cutover, wrote the runbook, sat the audits.
3. **Closed audit findings 14 → 2** at Texaco. That's an evidence story Augustine will recognize on the spot.
4. **Cut alert noise 200+ → 12 daily** at CoreDirective. That's a tuning story JT will recognize because he's been the manager whose team drowns in alerts.
5. **Has the GRC vocabulary native** (49 docs, NIST 800-53 169 controls, NIST AI RMF, ISO 42001) without the consultant tax.

Your gap is multi-zone enterprise scope. Own it once, in the gap section. Do not apologize twice. The flip side is everything is codified, so scaling out is configuration work, not a paradigm shift.

**Internal anchor before the call (read once at 1:25 PM):**
> "I run Cloudflare in production today. I lived PCI as the operator, not the consultant. I am here to do this work, not to learn it on someone else's dollar. Two interviewers, 30 minutes, then I go back to my day."

## The first 90 seconds will decide the call

Their first question will almost always be "tell me about yourself" or "walk me through your background." That answer sets the temperature. Memorize this:

> "I'm an AI Security Engineer at CoreDirective in Atlanta. My day-to-day overlaps this role: I run a production Cloudflare-fronted security stack — WAF custom rules, Rate Limiting, Bot Fight Mode, Zero Trust Access for four self-hosted apps, Cloudflare Tunnel for ingress, DNS — and everything is codified in Terraform across 16 modules with eight OPA policy gates that block merges if encryption, tagging, secrets, or zero public ingress is broken. We cut Datadog alerts 200-plus to 12 daily through edge tuning.
>
> Before CoreDirective I owned IT Security and Operations for Texaco for four years across three retail sites. PCI DSS scope on 45-plus devices. Wrote the IR runbook that dropped containment from 8 hours to 90 minutes, hardened Active Directory from 14 critical findings to 2, and stood up Splunk that cut detection from 48 hours to 4.
>
> SecurityX, SSCP, CCNA, Security+ on the wall, sitting CISSP this cycle. Atlanta local. The 1-day onsite cadence works. What questions do you want answered first?"

That's 75 seconds. End with the question. **Always end with a question.** It hands them back the wheel and signals confidence.

## Storytelling framework — your weak spot, fixed in one structure

You said storytelling is what you struggle with. Here is the only structure you need today:

**T-D-C-E-O — Threat, Decision, Control, Evidence, Outcome.**

Every technical answer you give in this interview should run that arc:

1. **Threat** — what was the actual risk in plain English? ("POS systems on a flat network with vendor remote access")
2. **Decision** — what did you decide and why? ("Segment first, monitor second. Segmentation removes the threat. Monitoring just watches it happen.")
3. **Control** — what specifically did you build or configure? ("4 VLANs, ACLs at the gateway, vendor access through a jump host with MFA")
4. **Evidence** — how did you prove it worked? ("Nmap from each VLAN, pre and post. Documented in the SAQ.")
5. **Outcome** — what changed in business terms? ("Lateral movement dropped to zero. PCI scope tightened. Audit cycle shrank.")

Five beats. ~45 seconds per answer. If you go longer they will cut you off, and the cut-off feeling is what makes you spiral. Land the 5 beats and stop. Silence after a clean answer is power.

For behavioral questions (conflict, mistake, leading without authority) use **STAR**: Situation, Task, Action, Result. Same shape, different vocabulary.

## Five stories — drill these, ignore the rest

You do not need 20 stories. You need 5 you can tell cold, in your sleep, in 60 seconds each. Pick these and drill them aloud once before the call.

### Story 1 — Texaco AD hardening (the trust story)

- **Threat:** AD had stale accounts, over-provisioned admin rights, no GPO baseline. 14 critical findings on the audit. Domain admin sprawl.
- **Decision:** Treat it as identity hygiene, not "audit fix." Identity is the perimeter at retail.
- **Control:** Enforced GPO baselines, cleared stale accounts, stripped admin rights that should not have been there, automated credential rotation.
- **Evidence:** Re-audit. 14 critical findings to 2.
- **Outcome:** Pass at the next cycle, lateral movement risk down, vendor access constrained to specific accounts.

**Use this story for:** "tell me about a time you owned a project end to end," "tell me about audit experience," "describe a time you turned around a failing posture."

### Story 2 — Texaco IR runbook (the pressure story)

- **Threat:** No documented IR process across 3 retail sites. POS skimmer attempts, vendor credential compromises happened, containment took 8 hours and depended on whoever was awake.
- **Decision:** Write a 6-step runbook tied to actual store ops, not a SANS template.
- **Control:** Runbook with concrete steps: isolate POS, snapshot, contact processor, swap terminal, verify segmentation, document. Trained store ops. Pre-staged spare terminals.
- **Evidence:** Next 3 incidents — 90-minute average containment.
- **Outcome:** 8 hours to 90 minutes. Processor relationship strengthened because we called them with structured info, not panic.

**Use this story for:** "tell me about an incident," "tell me about leading without authority" (you trained store ops who did not report to you), "tell me about working under pressure."

### Story 3 — Cloudflare Tunnel rollback (the judgment story)

- **Threat:** Enabled tunnel-level `access.required` to force Zero Trust Access on every tunnel hostname. Sounded right on paper. In production it broke per-app `aud_tag` capture, which meant we could not write per-app policies cleanly downstream.
- **Decision:** Roll back the tunnel-level requirement, switch to per-app Access policies. Slower to ship. Better operating model.
- **Control:** Reverted the Terraform change, kept per-app Access policies on the four hostnames, documented the why in a decision log so the next person does not repeat it.
- **Evidence:** Per-app policies fired correctly with the right `aud_tag`. Logs stayed clean. No outage.
- **Outcome:** No false sense of security from a coarse-grained control. Decision log captured the reasoning so the next engineer skips the same trap.

**Use this story for:** "tell me about a mistake," "tell me about a time you changed your mind," "tell me about a Cloudflare-specific decision."

### Story 4 — Squire alert tuning (the cross-functional story)

- **Threat:** 200+ Datadog alerts daily. Team was triage-numb. Real signal got lost. Classic alert fatigue at small-team scale.
- **Decision:** Tune at the source (edge) before tuning at the SIEM. Most of the noise was Cloudflare events that were not actionable.
- **Control:** Built Squire, an AI alert triage assistant on LangGraph. pgvector retrieval over historical alerts. NeMo Guardrails for PII redaction. Langfuse tracing. Tuned WAF and Rate Limiting at the edge first; Squire handled the residual.
- **Evidence:** Alert volume 200+ to 12 daily, 80% review-time reduction. Team caught a real credential stuffing attempt the next week instead of missing it.
- **Outcome:** Team went from drowning to actionable. Cross-functional partnership with infra and apps owners — they trusted the tuning because we showed them the data.

**Use this story for:** "tell me about cross-functional work," "tell me about AI in security," "tell me about reducing noise."

### Story 5 — VLAN segmentation cutover (the scale story)

- **Threat:** Flat network, 45+ PCI devices on the same broadcast domain as guest Wi-Fi and vendor laptops. Lateral movement was a single hop.
- **Decision:** Segment before you monitor. Monitoring a flat network is photographing a fire.
- **Control:** Designed 4 VLANs (POS, back-office, guest, vendor), ACLs at the gateway, vendor access through a jump host with MFA. Cutover in a defined window with rollback plan.
- **Evidence:** Nmap from each VLAN pre and post. Lateral movement dropped to zero. Documented in the SAQ.
- **Outcome:** PCI scope tightened, audit cycle shorter, vendor access auditable.

**Use this story for:** "tell me about an architecture decision," "tell me about a hard cutover," "tell me about working with PCI."

## Top 10 likely questions with exact answers

### 1. "Tell me about yourself."
Use the 75-second pitch above. End with a question.

### 2. "Why Candescent? Why this role?"
> "Three reasons. One, scale — 1,300 financial institutions on one platform is a different kind of edge problem than my one zone, and the kind of multi-zone discipline I want next. Two, the regulatory frame — FFIEC, GLBA Safeguards, SOC 2, PCI on the FI side. That maps cleanly to my Texaco PCI background and the GRC library I built at CoreDirective. Three, the post-spinoff timing — six months out from leaving NCR Voyix, you're still building the security operating model. I would rather help shape one than inherit one. What does the first 90 days actually look like?"

### 3. "Walk me through what happens when a request hits your Cloudflare zone."
Use the request-flow chain from the technical prep doc. Order: DDoS L3/L4 → DDoS L7 → WAF Managed → WAF Custom → Rate Limiting → Bot Management → Workers (request) → Page/Config/Transform Rules → Cache → Origin (via Tunnel) → Workers (response) → Cache write → Edge response.
Key insight to add: **"Order matters because cost matters. You stop noise as far left as possible. Bot Management before Workers means you don't pay compute on traffic you would have blocked anyway."**

### 4. "Tell me about a time you tuned a WAF rule that was firing on legit traffic."
> "Free tier on tigouetheory.com — I run 5 custom WAF rules because that's the cap. One was a header anomaly challenge that was firing on legitimate traffic from a webhook source I forgot about. I had two paths: weaken the rule, or carve a surgical exception. I went with the exception — match on the source IP range plus the specific header pattern, skip the rule. The rule kept its strength for everything else, and the webhook flow worked. The lesson is custom rules are last resort. Managed rulesets with tuned exceptions are the enterprise pattern. For Candescent at multi-tenant scale every FI customer can have its own exception set against the same managed ruleset, which is how you scale tuning without rule sprawl."

### 5. "Have you done multi-zone Cloudflare?"
The honest gap framing. Use the framing from `02_ROLE_FIT.md` exactly. Don't dress it up.
> "Honest answer: my hands-on production work is on one zone with four hostnames. The primitives — WAF expression engine, Rate Limiting, Access policy logic, Tunnel ingress, DNS — run daily. What I haven't felt is multi-zone rule drift across business units or RBAC at scale. The flip side is everything I do is codified in Terraform with policy gates, so scaling out is a configuration problem, not a paradigm shift. I'd want a week of pairing with someone on the team to learn the operating model here."

### 6. "Bot Management or API Shield?"
> "Bot Fight Mode and Super Bot Fight Mode I've operated. Bot Management — the paid SKU with JA3, JA4, ML scoring — I've read the docs but not run in production. Same with API Shield. My infra doesn't justify the spend. I'd be learning the dashboard and tuning loop on the job. What I bring is the reasoning model — what to score on, when to challenge vs block, how to feed the decision back into rule tuning."

### 7. "Tell me about an incident you led."
Use Story 2 (Texaco IR runbook). Hit T-D-C-E-O.

### 8. "How would you protect Candescent's admin endpoints?"
> "Three controls in layers. One, Cloudflare Access on the admin hostname with hardware key (FIDO2) plus IP allowlist. Hardware key beats TOTP for phishing resistance. Two, Origin Certificate with Authenticated Origin Pulls so the origin only accepts requests where the client cert is the Cloudflare signing CA — blocks the origin-bypass attack pattern. Three, WAF custom rule that blocks any admin request that does not carry the Access JWT. That's defense in depth across identity, transport, and request validation. For a banking platform, you also want session recording or audit log on the admin path so you have evidence for the FFIEC examiner — that's where Logpush feeds the SIEM."

### 9. "Tell me about a time you disagreed with a decision."
This is the hardest one for you. Use the Tunnel rollback story (Story 3). Not because you fought a person, but because you fought your own initial decision. That is a senior posture: I changed my mind based on evidence.

### 10. "Why are you in contracting if you have an FTE today?"
> "Optionality. I want to see the day-to-day before committing FTE, and a contract path lets the team and me both make a clean decision later. I'm Atlanta local, ready to start fast. If conversion isn't on the table, that's still a clean six months of the work I want to do."

## Behavioral questions they will probably ask

Banking SaaS interviews almost always include 1-2 of these. Pick a story for each before the call. **Do not switch stories mid-answer.**

| Question | Your story |
|---|---|
| Tell me about a time you led without authority | Texaco IR runbook — trained store ops who did not report to you |
| Tell me about a mistake | Tunnel `access.required` rollback |
| Tell me about working with a difficult stakeholder | Texaco vendor access — vendor wanted always-on remote, you scoped it to JIT through a jump host with MFA |
| Tell me about delivering under ambiguity | Squire alert tuning — no spec, owned the design |
| Tell me about saying no | Vendor wanted persistent admin access, you said no, scoped to JIT |
| Tell me about cross-functional work | Squire — partnered with infra and app owners on tuning |
| Tell me about a time you changed your mind | Tunnel rollback again |

## Their pain points (what you are actually selling against)

A banking SaaS spun out of NCR Voyix six months ago is rebuilding its security operating model under FFIEC/GLBA scrutiny. The Cloudflare seat exists because:

1. **They have a sprawling Cloudflare footprint** they inherited from NCR Voyix days. Multi-zone, multi-tenant for 1,300 FIs. Likely under-tuned, under-coded, dashboard-managed.
2. **An FFIEC examiner is coming** — or already has come — and the Cloudflare evidence trail is thin. They need someone who can produce audit evidence, not just configure controls.
3. **The CISO seat is open.** They are filling the working level while leadership shakes out. Whoever they hire here will have unusual latitude in the next 90 days.
4. **Acquisitions and integrations are coming.** Veritas Capital portfolios consolidate. New FI customers onboard fast.

**What you sell into that pain:**
- Cloudflare as code with policy gates (audit evidence is built-in)
- Tuning experience that shrinks alert volume (operations sanity)
- PCI/GRC vocabulary on day one (no consultant ramp)
- Atlanta local, hybrid-friendly, ready to start

## Honest gaps — say once, move on

- Multi-zone enterprise scope (one zone, four hostnames)
- Workers in production (one Tail Worker for log streaming, not the developer platform)
- Bot Management paid SKU (Bot Fight Mode only)
- API Shield (read docs, never shipped)

Frame: *"Smaller surface than yours. The reasoning models transfer; I'd ramp on your operating patterns in week one."*

## Your questions for them (pick 4, save the rest)

Open with one technical, close with one cultural. Pick from these:

**Technical / scope:**
1. How many Cloudflare zones do you run, and how is access scoped across teams?
2. Are WAF rules managed in dashboard or as code today? If code, what tool — Terraform, Wrangler, Pulumi?
3. Do you Logpush to a SIEM? Which one, and what's the false-positive rate on the OWASP Core Ruleset right now?
4. What's the biggest unsolved Cloudflare problem you'd want this person to attack first?
5. Do you ship Workers in production for security purposes, or is Workers more on the application side?

**Operating model:**
6. Who decides WAF rule deployments — the team or a change board?
7. What does the first 30 / 60 / 90 days look like for this role?
8. How is success measured at 90 days?

**Cultural close:**
9. What does a great hire look like in this seat six months in?

**Save these for the very end:**
10. What's the next step in the process and what's the timeline?

## The "convince them" framework

You said you need to convince them. Here is the only thing that actually convinces senior interviewers:

**Specificity beats credentials.** They have seen 50 candidates with CISSP this month. They have not seen a candidate who can quote OPA policy names, ruleset phase names (`http_request_firewall_custom`), and the exact rollback decision they made on a tunnel config last quarter.

When in doubt, **be more specific, not more impressive.** Replace any phrase like "I have experience with WAF tuning" with "I run 5 custom WAF rules on tigouetheory.com — scanner UA blocklist, geo-fence, two honeytoken paths, and a header anomaly challenge — and I prioritize because Free tier caps at 5."

Specificity does three things:
1. Proves the work is real (recruiters lie, candidates inflate, specifics are rare)
2. Gives the interviewer something to ask follow-up on (good follow-ups mean they are engaged)
3. Shows you think in operations, not concepts

## Tone and presence

- **Short sentences.** When you spiral, your sentences get long. Cut them.
- **Land and pause.** After every answer, stop talking. Five seconds of silence is fine. They will follow up or pivot. Filling silence is what kills candidates.
- **Lower your voice slightly when you say a number.** It signals the number is real. ("We dropped containment from 8 hours [pause] to 90 minutes.") Conversely, raise pitch slightly on rhetorical hooks. Don't sing-song the whole answer.
- **One hand visible on camera.** Lets you gesture, makes you look engaged. Both hands hidden reads as anxious.
- **Look at the camera, not their face on screen, for the open and close.** Camera contact at the start and end is what they remember.

## Never-say list (re-read at 1:25 PM)

- "Pivoting", "transitioning", "aspiring", "looking to break into"
- "Founder of CoreDirective" — employee posture
- "I'm not really a Cloudflare expert but..."
- "Whatever you can do" / any rate concession
- "AI is the future" — pitching AI to a Cloudflare hiring manager misreads the room
- "Leveraging", "robust", "comprehensive", "synergy"
- Em dashes when you talk
- Any phrase that ends in "...if that makes sense"

## Final 9-hour timeline

| Time | Action |
|---|---|
| 9:00 AM | Read Story 1-5 aloud once each. 60 seconds each. Don't memorize, internalize the beats |
| 10:00 AM | Re-read this doc, sections "Who you are talking to" and "The first 90 seconds" |
| 11:00 AM | Recon already done — see "Live recon on candescent.com" section below. Re-read it. |
| 12:00 PM | Light lunch, water, no caffeine spike. Walk 10 min. |
| 1:00 PM | Quiet space. Re-read Story 1, 2, 3 aloud once. Read the "Internal anchor" line. |
| 1:15 PM | Tech check: Teams app open, mic + camera test, second monitor with this doc on it (not visible to camera) |
| 1:25 PM | Re-read the never-say list. Re-read the internal anchor. Stand up, shake out hands. |
| 1:30 PM | Join. Camera on. First sentence is "Hi JT, hi Augustine, good to meet you both." Then wait for them to drive. |

## If something goes sideways

- **You blank on a question:** "Let me think for ten seconds." Then think. Out loud is fine: "I want to make sure I give you the right example. Are you asking about X or Y?"
- **You realize you're rambling:** Stop. Say "Let me land that." Then give the outcome in one sentence.
- **They ask something you don't know:** "I haven't run that. Here's the closest thing I have shipped — [analogue]. How do you use it here?" Never bluff. Banking interviewers will smell it.
- **They go silent:** Don't fill it. They're thinking, or they're testing whether you'll fill it. Wait.

## Live recon on candescent.com (run 2026-05-01 morning)

You're going in armed. Real edge fingerprints from the candescent.com main hostname:

- **Cloudflare confirmed:** `server: cloudflare`, `cf-ray: 9f4d27503c04e5e1-ATL` — Atlanta colo serving HQ region
- **HSTS preload on the apex:** `strict-transport-security: max-age=31536000; includeSubDomains; preload` — they care about transport posture
- **HTTP/2 + HTTP/3 (QUIC):** `alt-svc: h3=":443"` — modern edge, not legacy
- **`_cfuvid` cookie set** — Cloudflare unique visitor ID. Signal for Bot Management or analytics features that imply at least Business/Enterprise tier on this zone
- **DNS authoritative is UltraDNS** (`edns123.ultradns.org/biz/com/net`) — they proxy through Cloudflare but keep authoritative DNS off-Cloudflare. Multi-vendor DNS strategy. Likely a deliberate decoupling — the kind of decision a regulated bank-tech vendor makes for resilience and vendor risk
- **Origin behind:** `x-wf-region: us-east-1` — the marketing apex sits on Webflow. App-side likely lives elsewhere (the FI-tenant subdomains)
- **Cache status:** `cf-cache-status: BYPASS` on the apex — authenticated/dynamic-leaning page treatment

**Use this as your opener question (Tier 1, ask early in the Q&A window):**

> "I ran a quick `curl` on candescent.com this morning — you're on Cloudflare with HSTS preload, HTTP/3 enabled, but DNS authoritative on UltraDNS. That multi-vendor DNS pattern is a deliberate call. How do you think about that decoupling — vendor risk, resilience, or something else? And does the FI-tenant traffic land on the same zone, or do you fan out per institution?"

That question does four things at once:
1. Proves you actually looked at their edge (most candidates won't)
2. Names a real architectural decision they made (UltraDNS + Cloudflare proxy)
3. Asks about multi-zone scope without claiming you have it
4. Signals you think about vendor risk — exactly what a bank-tech security architect cares about

**If they ask "how did you know that?":** "Public DNS and HTTP headers. First thing I do before any edge conversation."

## After the call

- Thank-you note within 90 minutes to JT and Augustine separately. Reference one specific thing each said. Three sentences each, no more.
- Update the pipeline tracker. Tab `Brilliant_Cloudflare`, status = "HM round complete," date, key takeaways, next step ETA.
- Memory harvest only if something durable came up (their tier, their SIEM, their pain points, their hiring timeline).
