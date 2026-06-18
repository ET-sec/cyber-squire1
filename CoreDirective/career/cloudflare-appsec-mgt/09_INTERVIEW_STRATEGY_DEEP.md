# 09 — INTERVIEW STRATEGY DEEP DIVE

> **CoreDirective framing source of truth:** see `COREDIRECTIVE_FRAMING_LOCKED.md` in this folder. Any references in this file to "lab" or "personal engineering practice" are superseded by the locked version. CoreDirective is an AI security practice with a real anchor client (accounting firm) and a model-flexible AI stack. Read the locked file before re-reading anything below.

This is the teaching doc on interview meta-game (frames, presence, recovery moves). The Candescent interview was rescheduled, new date pending. The framework below applies to the rescheduled call and any future interviews.

---

## PART 1. YOUR STANDPOINT

### Who walks into the call

You are Emmanuel Tigoue. Atlanta. AI Security Engineer at CoreDirective. Four years at Texaco before that. SecurityX, SSCP, CCNA, Security plus, sitting CISSP this cycle. You ship Cloudflare in production today. You have lived PCI as the person on the hook, not the consultant who flew in for a week.

That is the identity. Carry it like a fact you already know is true. You are not auditioning to become a Cloudflare engineer. You are one. You are interviewing them as much as they are interviewing you.

### The three reasons you win this seat

1. **You run Cloudflare as code.** Most senior candidates at this rate manage Cloudflare in the dashboard. You codify zone, DNS, Tunnel, Access, and WAF in Terraform with eight OPA policy gates that block unsafe merges. That is operational discipline at a different tier.
2. **You have closed audit findings as the operator.** 14 critical AD findings down to 2 at Texaco. PCI DSS owner for 45 plus devices. Not theory. Not slides. The real cycle.
3. **You think in alert volume, not alert prevention.** Cutting 200 plus alerts to 12 daily is the senior move. Junior engineers add detection. Senior engineers tune until the signal is real.

Those are the three sentences that close the call if every other answer comes out shaky. Memorize them.

### The one gap and how to own it

Multi-zone enterprise scope. You run one zone, four hostnames. They run multi-tenant for 1,300 financial institutions. Say it once, calmly, then pivot to the flip side: everything is codified, so scaling out is configuration, not paradigm change.

Owning a gap kills the candidate fear that you are hiding things. It builds trust. Hiding it leaks through tone and gets exposed under follow-up.

### The frame for the whole call

You are a senior engineer evaluating whether Candescent is worth six months of your time. They are a banking SaaS six months out of a spinoff, with a Cloudflare footprint they inherited and an FFIEC examiner schedule they cannot miss. The fit is symmetrical. You both have something the other needs.

Walk in believing that. The body posture, voice, and pacing follow.

---

## PART 2. THE ART OF INTERVIEWING

### What is actually happening in an interview

An interview is not a test. It is a sales conversation with three buyers in the room.

- **The risk buyer.** Someone is asking "is this person going to break things." JT, the security architect, is the risk buyer.
- **The fit buyer.** Someone is asking "will this person work well with us under stress." Augustine, the GRC leaning seat, is probably the fit buyer.
- **The cost buyer.** Not in the room. They already approved the bill rate. Forget about them.

Every answer you give is being scored on two questions the buyers are asking silently:

1. Do I believe this person actually did the thing they said they did?
2. Do I want to spend 40 hours a week working with this person?

The first question is answered by specificity. Numbers, tool names, decision logs, configuration paths. The second question is answered by tone and pacing. Calm, low ego, curious.

If you nail those two, the technical depth almost does not matter. If you miss those two, no amount of technical depth saves you.

### The four questions hidden under every question

When they ask anything, ask yourself which of these they really want answered:

1. **Can you do the work?** (Technical capability)
2. **Will you do the work?** (Motivation, energy, ownership)
3. **Will you fit on the team?** (Style, communication, ego)
4. **Are you a flight risk?** (Stability, why this role, why now)

Most candidates only answer question 1. Senior candidates answer 1 and the most relevant of 2, 3, 4 in the same breath.

Worked example. They ask "tell me about a time you tuned a WAF rule."

A junior candidate answers question 1: technical steps to tune a rule.

You answer 1 and 3: technical steps, plus how you decided which rule to tune first because the team was drowning, plus what you taught the team after so the next tuning cycle was theirs not yours. That signals "I do the work and I make the team better."

### The buying signals

These mean the interview is going well. Pay attention so you can lean in.

- They ask follow-up questions instead of jumping to the next pre-written question
- They reference something you said earlier ("you mentioned the OPA gates, can you go deeper on that")
- They use "we" when describing how they would approach a problem
- They start asking logistical questions (when can you start, are you flexible on the onsite day)
- They volunteer information you did not ask for ("we are also evaluating Akamai right now")

These mean you should worry. Recover with one of the moves in the recovery section.

- They cut you off mid-answer and pivot to something unrelated
- They go quiet and write notes after every answer without looking up
- They start asking about other candidates ("what makes you different from the others")
- They ask about your weaknesses early
- They run out of questions and end early

### The two traps

**Trap one: the depth trap.** They ask a question you can answer at three levels. You go to level three because you can. The interviewer wanted level one. You spent two minutes proving you know stuff and they tuned out at minute one.

The fix: answer at level one in two sentences, then ask "do you want me to go deeper on the policy phase ordering, or is this more about the team operating model." Let them pick the level. Saves time, signals senior judgment.

**Trap two: the agree trap.** They state a position. You agree because agreeing feels safe. Now you have flattened yourself into a yes person. The room loses interest.

The fix: when they state a position, you can agree, agree with a caveat, or politely disagree with reasoning. Senior candidates use all three within a single call. Disagreeing with reasoning is the strongest move when you actually have evidence. Save it for one moment in the call. Pick the moment.

Sample disagree-with-reasoning move: "I would actually push back gently on that. In my experience, blanket Bot Fight Mode catches more legitimate scrapers than people expect. If you have B2B partners or RSS consumers, I would default to Super Bot Fight Mode with the JS challenge tier scoped to specific paths instead. Curious what your traffic mix looks like."

### Power dynamics

Three rules.

1. **The person asking the question has the power.** Asking your own question moves the power. End answers with a question when you can.
2. **Pace controls the room.** If they are fast and clipped, match them. If they are reflective, slow down. Mirroring builds rapport without effort.
3. **Silence belongs to whoever can hold it.** After a clean answer, do not fill the air. Five seconds of silence feels like an hour to the interviewer. They will fill it. That is the goal.

### Recovery moves

Things will slip. Pre-load these.

- **You blank on the question.** "Let me think for ten seconds." Then think. Out loud is fine.
- **You realize the question had two parts and you only answered one.** "I want to come back to your second question about Z. The way I think about that is..."
- **You feel yourself rambling.** Stop mid sentence. "Let me land that. The outcome was X." Then stop talking.
- **You realize you said something wrong.** "Quick correction on what I just said. The number was 12 daily, not 20. The 20 was the original alert rate before tuning."
- **They ask something you have not done.** "I have not run that in production. The closest thing I have shipped is X. Is the team thinking about it for a specific use case?"
- **They ask why you left a job.** Always frame forward, never backward. "Texaco was a great four years, the work I want next is bigger surface and more regulated scale. Candescent fits that."

---

## PART 3. BEHAVIORAL DEEP DIVE

### What STAR is and why it works

STAR is Situation, Task, Action, Result. It works because human brains process stories in that order. You give them context, conflict, decision, outcome. That is the story spine for every novel and movie. The interviewer's brain locks in.

Without STAR, candidates ramble. They describe systems instead of moments. The interviewer cannot tell what *you* did versus what the team did. Credit gets diffused. The story does not stick.

With STAR, the interviewer can repeat your answer back to their hiring panel two hours later. That is the goal. You are writing the talking points they will use to advocate for you in the debrief.

### The five-second rule for picking a story

When they ask a behavioral question, you have five seconds to pick a story before the silence becomes uncomfortable. Pre-loading the five stories from your prep doc means the picking is instant.

Map of question to story:

| Question category | Story to use |
|---|---|
| Owned a project, drove change, led | Texaco AD hardening or VLAN cutover |
| Incident, pressure, ambiguity | Texaco IR runbook |
| Mistake, changed your mind, judgment | Cloudflare Tunnel access.required rollback |
| Cross-functional, leading without authority | Squire alert tuning or IR runbook |
| Saying no, pushing back on stakeholder | Texaco vendor access (JIT through jump host) |
| Cloudflare specifically | Tunnel rollback or 5 custom WAF rules story |
| AI in security | Squire alert tuning |

### The full story scripts

Read these aloud once today. Do not memorize the wording. Memorize the beats.

#### Story 1. Texaco AD hardening

> Situation. When I took over IT security at Texaco, Active Directory was a mess. Stale accounts going back years, domain admin sprawl, no GPO baseline. The annual audit came back with 14 critical findings, all on identity.
>
> Task. The audit gave me 90 days to close them. The bigger problem was that closing the findings without breaking store ops meant I had to do this without a second engineer.
>
> Action. I treated it as identity hygiene first, audit fix second. I started with stale accounts, scripted a PowerShell sweep that flagged anything inactive over 60 days, walked the list with the store managers, disabled then deleted. Then I rebuilt the GPO baseline from CIS controls, deployed in a test OU first, then phased to production over three weeks. Stripped admin rights that should not have been there. Automated credential rotation for service accounts.
>
> Result. The re-audit closed 12 of the 14 findings. We went from 14 critical to 2. The remaining two were architectural, not config, and got tracked into the next budget cycle. Lateral movement risk dropped, vendor access constrained, and the audit cycle the next year was four hours instead of two days.

Why this works on JT: it shows you have run a real audit cycle in a regulated environment. He has too.

#### Story 2. Texaco IR runbook

> Situation. Three retail locations, all PCI scope, no documented incident response process. When something hit, containment depended on whoever was awake. Average containment was 8 hours.
>
> Task. The board wanted that down. The processor relationship was at risk because we were calling them with panic instead of structured information.
>
> Action. I did not write a SANS template runbook. I wrote a six-step runbook tied to actual store ops: isolate the POS, snapshot the device, contact the processor, swap to the spare terminal, verify segmentation, document. Pre-staged spare terminals at every site. Trained store ops on the first three steps because they were going to be the first hands on the device, not me. Built a Splunk alert that fired the runbook playbook directly into Slack with the site ID embedded.
>
> Result. Next three incidents averaged 90 minutes from detection to contained. The processor relationship strengthened because we called them with the runbook output, not raw confusion. One of the incidents turned out to be a vendor with an expired credential, not an attack, and we caught that in step three.

Why this works on Augustine: it is a story about turning chaos into evidence and process. Auditor brain loves that.

#### Story 3. Cloudflare Tunnel access.required rollback

> Situation. I was hardening the Cloudflare Tunnel config for tigouetheory.com. Four self-hosted apps behind the tunnel, each with its own Access policy. I decided to also turn on tunnel-level access.required as a belt-and-suspenders move.
>
> Task. The goal was to make sure no one could reach any tunnel hostname without an Access challenge, even if a per-app policy had a bug.
>
> Action. I deployed the change. It worked, but it broke per-app aud_tag capture downstream. The aud_tag is what tells you which Access app authorized a given request, and we needed that for per-app policy evaluation in the next layer. I had two paths: keep the tunnel-level requirement and lose the per-app evidence, or roll it back and trust per-app policies. I rolled it back.
>
> Result. Per-app policies fired correctly with the right aud_tag. No outage because I rolled back inside the same change window. I wrote a decision log so the next person on this stack does not repeat the same trap. The lesson was that defense-in-depth at the wrong layer can erase evidence at the right layer.

Why this works on both: it is a story about changing your mind based on evidence. That is senior posture. Junior engineers double down. Senior engineers reverse course when the data tells them to.

#### Story 4. Squire alert tuning

> Situation. CoreDirective was running 200 plus Datadog alerts daily. The team was triage-numb. Real signal was getting lost in noise.
>
> Task. Cut alert volume without cutting detection coverage. The temptation was to add another tool. The right move was to tune at the source.
>
> Action. I started at the edge, not the SIEM. Most of the noise was Cloudflare events that were not actionable: scanner traffic that was already blocked, rate-limited requests from known good bots, geo blocks from countries we did not serve. I tuned WAF and Rate Limiting rules first, then built Squire on LangGraph: pgvector retrieval over historical alerts, NeMo Guardrails for PII redaction, Langfuse for tracing. Squire handled the residual triage.
>
> Result. Alert volume from 200 plus to 12 daily. Review time down 80 percent. The next week the team caught a real credential stuffing attempt that would have been buried in the old volume. Cross-functional partnership with infra and app owners, because they had to trust the tuning, and they did because we showed them the data.

Why this works on JT: it is the senior alert-tuning story he has lived as a manager.

#### Story 5. VLAN segmentation cutover

> Situation. Texaco network was flat. 45 PCI devices on the same broadcast domain as guest WiFi and vendor laptops. Lateral movement was a single hop.
>
> Task. Segment for PCI scope reduction, with no business interruption.
>
> Action. Designed four VLANs: POS, back-office, guest, vendor. ACLs at the gateway. Vendor access through a jump host with MFA. Built a cutover plan with a defined window and a rollback path. Coordinated with the payment processor so they knew the timing in case any traffic flagged anomalous.
>
> Result. Lateral movement validated to zero with Nmap from each VLAN, pre and post. PCI scope tightened by 60 percent because the segmented devices fell out of audit scope. The next SAQ took half the time. Vendor access auditable for the first time.

Why this works on both: PCI scope reduction is the language a banking interviewer recognizes immediately.

### Making STAR not feel scripted

The reason STAR feels scripted in interviews is that candidates rehearse the words instead of the beats. They sound like they are reading.

The fix is to rehearse only the four anchors:

1. The opening one-liner that sets the situation
2. The decision that pivots the story
3. The number at the end
4. The one-sentence lesson

The middle is improvised every time. That keeps it fresh. You can tell a story 50 times and the middle changes each time, but the anchors hold.

For Story 1 the anchors are:

1. "When I took over Texaco IT security, Active Directory was a mess. Annual audit came back with 14 critical findings."
2. "I treated it as identity hygiene first, audit fix second."
3. "14 critical to 2. The remaining two were architectural and went into the next budget cycle."
4. "The audit cycle next year was four hours instead of two days. Hygiene work pays in audit time."

Memorize those four. Improvise everything else.

### How to handle follow-ups

Behavioral follow-ups usually go one of three directions:

1. **Drill on the action.** "How did you decide which stale accounts to delete first?" Answer: be specific. The criteria you used. The risk you weighed.
2. **Drill on the result.** "How do you know lateral movement actually went to zero?" Answer: the evidence. Nmap output, the SAQ documentation, the next audit cycle.
3. **Drill on the lesson.** "What would you do differently?" Answer: have one ready for every story. For Story 1: "I would have phased the GPO rollout in two weeks instead of three. I was being cautious, but the additional caution did not buy us anything."

Pre-load the lesson for each of the five stories. That is the move most candidates miss.

### A worked behavioral exchange

Here is a realistic 90-second exchange so you can hear the rhythm.

> **JT:** "Tell me about a time you owned an incident."
>
> **You:** "Sure. At Texaco I owned the IR program for three retail sites, all PCI scope. The biggest one I led was a POS skimmer attempt at the Bouldercrest location. (Situation, 8 seconds.)
>
> The task was containment without taking the store offline during dinner rush. (Task, 5 seconds.)
>
> I followed the runbook I had written six months earlier. Isolated the POS, snapshotted the device, called the processor, swapped to the spare terminal we pre-staged. Total time on the floor was 45 minutes, the store kept running on the spare. The forensic image went to the processor's investigator the next morning. (Action, 25 seconds.)
>
> Containment took 90 minutes from detection. We confirmed the skimmer attempt failed because of the segmentation work we had done six months prior. The processor cleared us at the next compliance check, no fines, no breach notice. (Result, 12 seconds.)
>
> The lesson I took was that the runbook was useful, but the segmentation work months earlier was what made the runbook fast. Containment is a function of the architecture you built before the incident. (Lesson, 10 seconds.)"
>
> **JT:** "How did you decide to pre-stage spare terminals?"
>
> **You:** "Cost-benefit on tabletop. A spare terminal was about 800 dollars. A four-hour outage during dinner rush was around 4,000 dollars in lost sales per location. We pre-staged at all three sites, so the math paid back in any single incident. The harder part was getting the processor to bless the swap process so the swap was not itself a compliance event."

That is what good looks like. 60 seconds for the main answer. Specific number on the follow-up. One detail that shows you thought about the second-order problem (processor blessing).

---

## PART 4. TECHNICAL DEEP DIVE

### The Cloudflare request flow with the why

Memorize the chain. More important, memorize the *why* at each step. The why is the senior signal.

```
Client request
  -> DDoS L3/L4 mitigation       (cheap drop, network layer, no compute cost)
  -> DDoS L7 mitigation          (HTTP layer, before any rule eval)
  -> WAF Managed Rulesets        (Cloudflare Managed, OWASP CRS, Exposed Creds Check)
  -> WAF Custom Rules            (your expressions, after managed)
  -> Rate Limiting Rules         (after WAF so you don't rate-limit blocked traffic)
  -> Bot Management              (scoring, JA3/JA4, ML)
  -> Workers (request handlers)
  -> Page/Configuration/Transform Rules (cache keys, headers)
  -> Cache lookup                (HIT or MISS decision)
  -> Origin (via Tunnel or proxied DNS)
  -> Origin response
  -> Workers (response handlers)
  -> Cache write
  -> Edge response
```

The senior insight to drop in conversation: **order matters because cost matters.** You stop noise as far left in this chain as possible. Bot Management before Workers means you do not pay compute on traffic you would have blocked. WAF before Rate Limiting means you do not consume rate budget on traffic that was bad anyway. This is the kind of statement that signals you have actually thought about edge economics.

### The technical scenarios with full answers

#### Scenario 1. Walk me through what happens when a request hits your zone.

Recite the chain above. Add the cost insight. Mention one trade-off: "I keep custom rules after managed because managed gets the bulk catch with maintained signatures. Custom is for the gaps that managed does not cover."

#### Scenario 2. WAF managed ruleset firing false positives on the login endpoint. How do you tune?

> Three options, ranked by surgical-ness. One, add a skip-rule exception scoped to the path and the parameter pattern that is firing. Surgical, keeps the rule strong everywhere else, takes 10 minutes. Two, lower the rule sensitivity if the rule supports it. Less surgical, weakens the rule across the zone, do this only if the false positive is widespread. Three, last resort, disable the rule and write a custom rule that mimics the intent without the false positive.
>
> The principle is: never weaken a managed rule when an exception will do. The managed ruleset is maintained by Cloudflare. Custom rules are maintained by you. Every disabled managed rule is a future maintenance burden you took on yourself.

#### Scenario 3. How does Cloudflare Tunnel actually establish the connection?

> The cloudflared daemon on the origin opens an outbound connection to Cloudflare's edge over QUIC by default, falling back to HTTP/2 if QUIC is blocked. Outbound port 7844. No inbound port open on the origin firewall. The edge holds the connection and routes inbound public traffic over it. The tunnel is identified by a UUID and authenticated with a tunnel token issued at creation. Public hostnames are mapped to tunnel routes via CNAME records that point to <tunnel-uuid>.cfargotunnel.com.
>
> The architectural insight is that this inverts the trust direction. The origin trusts Cloudflare, not the other way around. That removes the traditional firewall punch-out problem. The risk you trade for is that the tunnel token, if leaked, lets an attacker impersonate your origin from anywhere.

#### Scenario 4. Difference between Access and WARP. When does a user need both?

> Access is the application layer. It sits in front of a hostname and challenges the user with an identity provider before passing to origin. WARP is the device layer. It is a client on the user's machine that creates a tunnel into Cloudflare for outbound traffic.
>
> A user needs Access alone when they are reaching a single self-hosted app from any device on any network. A user needs WARP alone when you want to enforce posture on the device, route corporate traffic through Cloudflare Gateway, or apply DNS filtering. A user needs both when you want device posture as part of the Access decision: only let this user into the admin panel if their device is corporate-managed and has WARP up.

#### Scenario 5. Customer says Cloudflare is caching authenticated user data and serving it to other users. Where do you start?

> First, do not panic. This is almost always a configuration issue, not a Cloudflare bug. Second, reproduce. Get the URL, the user account, the cache header response, and a timestamp. Third, walk the cache decision: cache rules, page rules, configuration rules, origin Cache-Control headers, Vary headers.
>
> Most likely causes ranked by probability: one, origin sets Cache-Control: public on an authenticated response. Two, cache key is missing the session cookie or auth header in the Vary or cache key custom rule. Three, a Page Rule is overriding origin cache headers. Four, the application is serving identical URLs to different users without query string or path differentiation.
>
> The fix is usually a cache rule with a bypass-on-cookie condition: if the session cookie is present, bypass cache. That is the standard pattern for authenticated content behind Cloudflare.

#### Scenario 6. Allow only requests with a valid client cert to hit /api/admin. How do you build it in Cloudflare?

> mTLS at the edge. Cloudflare API Shield mTLS or the equivalent in Access for SaaS. You upload the client certificate authority to Cloudflare. You configure a Cloudflare Access policy or a WAF custom rule that requires cf.tls_client_auth.cert_verified to be true and the SAN to match the expected client cert. Requests without a valid client cert fail at the edge before hitting origin.
>
> If they want defense in depth, layer Authenticated Origin Pulls so origin only accepts traffic from Cloudflare's signing CA. That blocks the origin-bypass attack pattern where someone finds the origin IP and tries to talk to it directly.

#### Scenario 7. Layer 7 DDoS hits a single endpoint. Auto-mitigation is not catching it. Playbook in five minutes?

> Five minutes is tight. Order of operations.
>
> Minute one: confirm the attack signature. Cloudflare dashboard, Security Events, filter by the endpoint. Look at top ASNs, top user agents, top countries. Identify the pattern.
>
> Minute two: drop in a custom WAF rule blocking the most distinctive signature. Could be a user agent string, a header pattern, a country, or an ASN. Set action to block.
>
> Minute three: tighten Rate Limiting on the endpoint. Drop the threshold for the duration of the attack. Key on IP, or IP plus colo if the attack is well-distributed.
>
> Minute four: if the attack is high volume and well-distributed, enable Under Attack Mode for the zone. JS challenge by default. Trade-off: legitimate users see a 5-second interstitial. Acceptable during an active attack, not acceptable as a default.
>
> Minute five: communicate. Update incident channel with what was blocked, what is still bleeding through, and the rollback timeline. Document for the post-incident review.

#### Scenario 8. Design Cloudflare for a SaaS app with three tiers.

Public marketing, authenticated app, admin panel where admin requires hardware key plus IP allowlist.

> Three hostnames or path-based, depending on app. Three different control sets.
>
> Marketing: aggressive caching at the edge, Bot Fight Mode on, no Access, basic WAF. The goal is performance.
>
> Authenticated app: Bot Management paid SKU if budget supports it, Rate Limiting on auth endpoints, custom WAF rules for known abuse patterns, no caching of authenticated responses (bypass on session cookie), Logpush to SIEM with full request fields.
>
> Admin: Cloudflare Access with hardware key (FIDO2) policy, IP allowlist via the Access policy or a WAF custom rule, mTLS via API Shield if you want a fourth factor, Authenticated Origin Pulls so origin only takes Cloudflare-signed traffic, session recording or audit log via Logpush.
>
> The architectural point is that defense in depth lives in different controls at different tiers. The marketing tier is optimized for cost and performance. The admin tier is optimized for non-repudiation and breach blast radius.

### The "I have not done that" framework

You will get asked about something you have not run in production. Bot Management paid SKU. API Shield. Magic Transit. A Worker doing real auth.

The framework is three sentences.

1. **Honest.** "I have not run that in production."
2. **Adjacent.** "The closest thing I have shipped is X." (Tail Worker for log streaming, custom WAF rules, Bot Fight Mode, etc.)
3. **Curious.** "How are you using it here?"

The third sentence is the move. It pivots from defense to learning. It signals you are interested in their specific use case, not just defending your gap. It also gets them talking, which gives you a real-world data point for the rest of the call.

Sample answer for Bot Management: "I have not run Bot Management paid SKU in production. The closest thing I have shipped is Bot Fight Mode plus a scanner UA blocklist as custom WAF rules. How are you using Bot Management here, is it more on the credential stuffing side or the API abuse side?"

### Showing depth without flexing

The senior move is to teach a small thing during your answer without making it sound like a lecture.

Bad: "Well, you see, the way Cloudflare's edge works at the network layer is..."

Good: "I keep custom rules after managed because managed gets maintained signatures. The trade-off is custom rules cost you maintenance time, so I save them for the gaps managed does not cover."

The good version embeds a small teaching moment inside a personal practice. You are saying "here is what I do and why." Not "here is how Cloudflare works."

JT will catch the senior framing. Augustine will catch the trade-off thinking. Both will score you up.

---

## PART 5. STRATEGY FRONT TO BACK

### The 30-minute arc, predicted

This is the most likely shape of the call. Banking interviews are predictable.

| Minute | What happens | Your move |
|---|---|---|
| 0:00 to 1:00 | Hellos, intros, "thanks for joining" | Smile, camera contact, "good to meet you both" |
| 1:00 to 3:00 | Their intros: who they are, what they do at Candescent | Listen for which is JT and which is Augustine, which one runs Cloudflare day to day, which one runs audit. Take a mental note |
| 3:00 to 4:00 | "Tell us about yourself" | Your 75-second pitch. End with "what questions do you want answered first" |
| 4:00 to 14:00 | First interviewer drives. Probably JT on technical Cloudflare scenarios | T-D-C-E-O on every answer. Land and pause |
| 14:00 to 24:00 | Second interviewer drives. Probably Augustine on behavioral and GRC framing | STAR on every behavioral. Map controls to frameworks when possible |
| 24:00 to 28:00 | Their summary, your questions | Pick three of your prepared questions. Tier 1 first (recon question), Tier 2 in the middle, save the operating-model question for last |
| 28:00 to 30:00 | Logistics, next steps, goodbye | "What is the next step, and what is the timeline?" Then thank both by name |

### The first 90 seconds

This is the part most candidates blow.

When they ask "tell me about yourself," do not start with where you went to school. Do not start with "well." Do not apologize for anything.

Start with what you do today, in present tense. "I am an AI Security Engineer at CoreDirective in Atlanta." That sentence anchors you. Then go into the 75-second pitch. End with a question that hands them the wheel.

The reason the first 90 seconds matters so much: interviewers form an impression in the first 30 seconds and spend the next 29 minutes confirming it. Your job is to make the first 30 seconds *match the resume they already saw*. Tone: confident, specific, calm. Posture: eyes on camera, hands visible, voice low and even.

### The middle 20 minutes

This is where you actually win or lose. Two principles.

**Principle one: every answer ends with a question or a clean stop.** Never let an answer trail off. Either you ask them something or you stop talking and let them respond.

**Principle two: vary the length.** Some answers should be 20 seconds. Some should be 60. Some should be 90 with a follow-up invitation. If every answer is the same length, you sound rehearsed. Real senior engineers calibrate length to the question.

Twenty-second answer: "Difference between Page Rules and Configuration Rules?"
> "Page Rules are deprecated for new accounts. Configuration Rules are the modern replacement, with better expression matching. I use Configuration Rules for zone settings overrides like security level or HSTS, and Cache Rules for cache behavior. Page Rules in legacy zones I leave alone unless I am migrating."

That is a clean 20 seconds. No fluff.

90-second answer: "Walk me through your Cloudflare environment."
> Long-form, with the chain, the OPA gates, the trade-offs.

The variance signals senior judgment.

### Your questions phase

You will get four to six minutes for your questions. Three to four questions is the right count. Less and you look uninterested. More and you eat into their next meeting.

Order them strategically.

1. **First question: shows you did the recon.** Use the UltraDNS plus Cloudflare proxy question. It puts a real architectural decision they made into the conversation and asks them to talk about how they think.
2. **Second question: shows you think about the operating model.** "Are WAF rules managed in dashboard or as code today?" This is asking how they work, not what they do.
3. **Third question: shows you think about success.** "What does a great hire look like in this seat six months in?" This is the closer that gets them to imagine you in the seat.
4. **Last question, only if there is time: logistics.** "What is the next step in the process?"

Skip questions about benefits, comp, PTO, equity. Those go to Matt Morgan after the offer.

### The exit

Last 60 seconds matters as much as the first 60.

Thank both interviewers by name. "JT, Augustine, thank you both for your time." Repeat one specific thing each said that you appreciated. "JT, the point about the FFIEC examiner cycle is exactly the kind of constraint I want to design for. Augustine, the framing around evidence as a design output rather than an audit afterthought is how I think too."

Confirm the next step. "I understand the next step is for Matt to follow up with timing. Anything you need from me before then?"

Smile, camera contact, "have a great rest of your Friday." End the call cleanly. Do not linger.

---

## PART 6. THE NO-STRESS PART

### Body and breath

Stress lives in the body before it lives in the voice. Pre-empt it.

- **30 seconds before the call.** Stand up. Shake out hands and shoulders. One slow breath in for 4 seconds, hold for 4, out for 6. Repeat three times. This drops your heart rate.
- **During the call, when you feel a spike.** Bring one hand to the desk. The physical anchor pulls you out of mental spiral. Take a breath before answering. Five seconds of pause is fine.
- **Voice low and slow when you are nervous, not high and fast.** Nervous people speed up. Force yourself to slow down. The interviewer reads slow as confident.

### The pre-call ritual (last 15 minutes)

Do this exact sequence.

1. 1:15 PM: tech check. Teams open. Mic and camera test. Lighting on face. Background clean. Second monitor with this doc visible to you, not visible on camera.
2. 1:20 PM: stand up. Walk for two minutes. Drink water. Use the bathroom. Sit back down.
3. 1:25 PM: re-read the never-say list. Re-read the internal anchor: *I run Cloudflare in production today. I lived PCI as the operator, not the consultant. I am here to do this work, not to learn it on someone else's dollar. Two interviewers, 30 minutes, then I go back to my day.*
4. 1:28 PM: three slow breaths. Sip of water. Hands visible.
5. 1:30 PM: join the meeting. Camera on. Wait for them to speak first if they joined first. If you joined first, smile when they appear.

### What to do if you blank

You will blank at least once. Everyone does.

The move: "Let me think for ten seconds." Then look up and to the side, not at the camera. Looking up signals thinking, not panic. Take the ten seconds. Come back with whatever you have, even partial. "I am going to start with the architectural piece and circle back to the implementation."

Blanking is not the problem. Visible panic is the problem. Buying yourself ten seconds of thinking time fixes the panic.

### What to do if you ramble

You will catch yourself rambling. Recovery move: stop mid sentence, say "let me land that," then give the outcome in one sentence.

Sample: "...so the rate limiting was running at 10 requests per 10 seconds keyed on IP plus colo, and the trade-off there was that legitimate retries from the same client were getting clipped, which meant we had to look at the retry-after header behavior, and... let me land that. The outcome was we shipped the rule, monitored for a week, and found two false positives that we tuned out. The final config is still running."

That kind of recovery actually scores higher than a clean answer because it shows self-awareness.

### What to do if they go silent

Do not fill it. They are thinking, taking notes, or testing whether you will fill it. Wait. Look at the camera. Half-smile. Wait.

If the silence lasts more than 15 seconds, you can ask "did I answer the question you were asking, or did you want me to go a different direction?" That is a power move because it returns the conversation to them on your terms.

### What to do if you hate one of your answers

Move on. Do not apologize. Do not try to redo it. Saying "actually, let me redo that one" puts the interviewer in the awkward position of pretending they did not hear the first version. Just give the next answer better.

The exception is a factual error. If you said the wrong number, correct it. "Quick correction on what I just said. The number was 12, not 20." That is fine.

### After the call

Walk away from the screen for ten minutes. Do not analyze. Your brain is in fight-or-flight and it will replay the worst three seconds of the call on loop. Wait until you are calm.

Then do three things.

1. Send the thank-you notes. JT and Augustine separately. Three sentences each. Reference one specific thing each said. Not generic gratitude.
2. Update the pipeline tracker. Brilliant_Cloudflare tab. Status, date, key takeaways, your read on next step.
3. Memory harvest only if something durable came up that you want in long-term memory: their Cloudflare tier, their SIEM, their pain points, hiring timeline.

That is the full strategy front to back. Read Part 3 and Part 4 once more at 1 PM. Everything else is one read today.
