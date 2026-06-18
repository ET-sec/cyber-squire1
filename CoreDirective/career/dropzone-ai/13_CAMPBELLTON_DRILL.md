# Story 13 Drill: Campbellton Plaza Gate Access Design

Use this to rehearse and defend the story under cross examination.

Key principle to internalize first, because every answer ladders back to it:

> **AI on the edges. Deterministic critical path. The unlock decision is load-bearing, so I refused to put a probabilistic system in front of it.**

That sentence is the spine. If you forget everything else, say that.

---

## 1. The 90-Second Script (rehearse out loud, 5 times)

This is the version you give if the interviewer asks "tell me about a recent customer project" or "what excites you about Dropzone." Time it. It should land at 75 to 90 seconds.

> Today, on Campbellton Road in Atlanta, I sat with the owner of a small plaza of salon studios. He had spent fifty thousand dollars on a security fence after dangerous foot traffic into the courtyard, and he was about to deploy key fobs. He was worried about clients losing them, sharing them, and the lack of an audit when something went wrong. The blocker was after-hours access. Clients arriving early or leaving past midnight had no safe entry path.
>
> I split the system into two layers. Critical path is the unlock decision. That stays deterministic. A valid time-bound code, inside the booked appointment window, equals unlock. I refused to put AI in that path because latency and false negatives are unrecoverable when a physical lock is the failure mode.
>
> The stylist is the authenticated party with an MFA app like Microsoft Authenticator or Duo. The client stays unauthenticated and only receives a one-time SMS code from a smart number that accepts it only during their appointment window. PIN keypad on the gate as fallback. Audit log ties every entry to a stylist, an appointment, and a timestamp.
>
> The AI work goes on the edges only. Anomaly detection on the audit log, natural language queries for the owner over entry history, incident report drafting if a flagged pattern fires. I recommended Claude API with Sonnet for reasoning and Haiku for routine automation, because at this volume a self-hosted model loses on math and operational burden.
>
> I produced a one-page deliverable in DOCX while we talked, priced as a fixed-scope vendor evaluation engagement between twenty five hundred and five thousand dollars. The architectural rule I led with, AI on the edges and a deterministic critical path, is the same rule I would apply to any AI SOC analyst design. You amplify the deterministic system. You do not replace it.

---

## 2. The 30-Second Compressed Version

Use this if asked "give me a one-line example of how you think about deploying AI."

> A salon plaza owner today wanted me to put a key fob system on his after-hours gate. I told him keep the unlock decision deterministic. Time-bound SMS code plus appointment window equals unlock. AI goes on the edges only, in anomaly detection on the audit log and natural language queries for the owner. The principle is the same one Dropzone applies to AI SOC analysts. You do not put a probabilistic system in the load-bearing path. You amplify the deterministic system from the side.

---

## 3. The Whiteboard Sketch (memorize, replicate if asked)

If they ask "draw it for me," draw this. Practice on paper twice before the interview.

```
                                    +-----------------------+
                                    |   Salon Owner Console |
                                    |   (audit log, NL Qs)  |
                                    +----------+------------+
                                               |
                                               | (read only)
                                               v
+--------------+        +-------------------+      +-------------------+
| Booking app  |------->| Code generator    |      |  AI on the edges  |
| (stylist's)  |        | (TOTP-style,      |      |  - anomaly detect |
+--------------+        |  appt-window-     |      |  - NL queries     |
       ^                |  scoped)          |      |  - IR drafting    |
       |                +---------+---------+      +---------+---------+
       |                          |                          ^
       | (MFA: Authenticator      | (SMS via Twilio /        | (read-only feed
       |  or Duo)                 |  Bandwidth, A2P 10DLC)   |  from log)
       v                          v                          |
+--------------+         +-------------------+               |
|   Stylist    |         |   Client phone    |               |
+--------------+         +-------------------+               |
                                   |                         |
                                   | (text code to           |
                                   |  smart number)          |
                                   v                         |
        +----------+----------+----------+                   |
        | Trust boundary: gate controller |                  |
        +---------------------------------+                  |
                                   |                         |
                                   v                         |
                       +----------------------+              |
                       |  Brivo or Kisi gate  |---write----->+
                       |  controller          | audit log    |
                       |  (deterministic)     |              |
                       +----------+-----------+              |
                                  |                          |
                                  v                          |
                          +---------------+                  |
                          |  Physical     |                  |
                          |  unlock       |                  |
                          +---------------+                  |
```

Trust boundary lives between the client's phone and the gate controller. Everything inside the controller is deterministic. AI lives outside the controller, fed by a read-only copy of the audit log.

---

## 4. The Numbers You Must Know Cold

| Item | Number | Why it matters |
|------|--------|----------------|
| Fence cost (anchor) | $50,000 | Sets the owner's investment frame |
| Engagement price | $2,500 to $5,000 fixed scope | Shows pricing discipline, not hourly billing |
| Recurring software | $30 to $50 per door per month for Brivo or Kisi | The owner asks "what's the ongoing cost" |
| API cost per workflow run | Pennies for Haiku, dimes for Sonnet | The "Claude over self-hosted" math |
| Self-hosted breakeven | Roughly 10,000+ LLM calls per day | When self-hosted wins on cost |
| SMS cost | About $0.0079 per SMS via Twilio (A2P 10DLC) | Cost per gate unlock |
| MFA app | Microsoft Authenticator (free) or Duo Free (10 users) or Duo Essentials | Stylist-side auth |
| Tenants in plaza | 4 (salon studios) | Sets the scale of the engagement |
| Code time window | Bounded by appointment + 15 min lead and 15 min trail buffer | The "smart number" rule |

If you do not remember a number, say "I would size that against the volume before quoting." Never guess.

---

## 5. Tech Stack Defense (know one paragraph on each)

### a. Time-bound SMS code mechanism
HOTP-style or TOTP variant where the server side maintains a single-use code per appointment, scoped to the booked window plus buffer. Server validates: code matches, not yet used, current time inside window. On match, the controller fires unlock. On miss, log and rate limit.

### b. Smart number
Twilio or Bandwidth provides a long code or short code with programmable webhook. Inbound SMS hits a webhook that validates the code against the appointment store. A2P 10DLC registration required for legitimate high-throughput SMS in the US. Without it, deliverability drops.

### c. MFA app for stylists
Microsoft Authenticator or Duo. Stylist enrolls once, gets a TOTP that protects their account, used to log into the booking app and approve appointments. The stylist is the authenticated party. The client is not.

### d. Brivo vs Kisi
Both are cloud-managed access control vendors. Brivo is the older incumbent with more property management and multi-site features. Kisi is newer, mobile-first, often nicer UI and integrates well with HR systems. For a four-tenant plaza, either works. I priced for vendor evaluation, not lock-in.

### e. Audit log schema
At minimum: timestamp (UTC), event type (unlock, fail, locked out, manual override), method (SMS code, PIN, fob, manual), stylist ID, appointment ID if applicable, client phone hash (not raw), gate ID, success or failure, error code if any. Stored in Postgres or the vendor's cloud. Read-only feed exposed to the AI edges layer.

### f. AI on the edges
Three concrete uses:
1. Anomaly detection: entries outside any booked window, repeat failed codes, unusual entry frequency for a stylist's clients.
2. Natural language queries for the owner: "show me all entries between 11 PM and 2 AM last week."
3. Incident report drafting: when a flagged pattern fires, the agent drafts a structured report with supporting evidence and a recommended action, then routes for human review.

### g. Why API beats self-hosted at this volume
Self-hosted Llama or Qwen looks cheaper until you price the GPU, ops burden, and your hours maintaining it. Below roughly 10,000 LLM calls per day, API wins on TCO. Above that, you start to see self-hosted compete. This plaza is well below that threshold. If the customer had clearance, federal, or HIPAA constraints, the math changes and self-hosted is the right call regardless of cost.

---

## 6. The 12 Follow-Up Questions an Interviewer Will Fire

For each, the answer is in 30 to 45 seconds.

### Q1. What stops a client from sharing the code?

The code is bound to a specific appointment window plus a 15 minute buffer on each side. After that window closes, the code is dead. So even if the client shares it, the receiver only has that window. The stronger control is that the audit log shows entry under that appointment regardless of who used the code, so the stylist is on the hook. That is the social control. The technical control is the window.

### Q2. What if the SMS provider goes down?

Two layers. First, the gate has a PIN keypad fallback that the salon owner can give a client over the phone in an emergency. Second, the booking system can fall back to a stylist-initiated unlock from their app if the stylist is on premises. The deterministic critical path tolerates SMS outage by design.

### Q3. What if a client's phone is intercepted, SIM swapped, or hit by SS7 abuse?

For a four-tenant plaza, SMS is appropriate to the threat model. The asset is access during off hours, not a cryptocurrency exchange. If the threat model rises, I would recommend a passkey-style flow on a client web link, where the link still hits the smart number flow under the hood but adds a one-tap confirmation. For this engagement, SMS plus appointment window plus audit log is proportionate.

### Q4. How do you authenticate the stylist if their phone is stolen?

Stylist account is MFA-protected. Loss of the phone means the stylist contacts the salon owner who locks the account. Backup codes for the MFA app are stored in a password manager during onboarding. Recovery is a tier two flow, not the critical path.

### Q5. Why not biometric on the gate?

Three reasons. Cost: biometric readers add hardware and recurring cost the plaza does not need. Trust model: the stylists own their clients, not the plaza, so binding biometrics to the plaza creates a weird privacy posture. UX: clients will not enroll biometrics with a salon they may visit twice. SMS plus PIN is the right ergonomics.

### Q6. How does this scale to 10 plazas?

The architecture scales horizontally. Booking system is per-tenant. Smart number can be per-plaza or shared with an additional plaza ID parameter. Gate controllers are independent. The AI layer aggregates by tenant for owner-level queries and by tenant-of-tenant if you ever wanted plaza-of-plaza analytics. The bottleneck at scale is the booking integration, not the access control.

### Q7. What is the threat model?

Top three threats. One: code interception or sharing leading to unauthorized entry. Mitigated by time-bounded codes plus audit log. Two: stylist account takeover leading to fraudulent appointment creation and entry. Mitigated by MFA on the stylist app. Three: gate controller compromise leading to unlock bypass. Mitigated by vendor selection (Brivo and Kisi do their own audits) and by network segmentation between the controller and the rest of the plaza network.

### Q8. What is your liability story for the owner?

The audit log is the liability shield. If something happens, the owner can show who entered, under whose appointment, and when. Insurance carriers and lawyers care about that record. The system is not perfect security, it is provable accountability. That is what the owner is buying.

### Q9. How do you sell this to a non-technical owner?

I sold the principle, not the product. He understood "key fob means anyone with the fob gets in" versus "tied to an appointment means only the right person at the right time." Once he saw that, the rest was technical detail. The DOCX one-pager I produced has a no-jargon section at the top and the technical detail at the bottom for whoever he forwards it to.

### Q10. What if the AI on the edges flags a false anomaly?

Two layers. First, the anomaly is a recommendation, not an action. It surfaces in the owner's dashboard and waits for a human read. Second, every flag has its supporting evidence shown inline (the log entries that triggered it), so the owner can decide. False positives are a bias problem in detection, not a blast-radius problem in unlock.

### Q11. Why a fixed-scope engagement instead of hourly?

Two reasons. One: it lets the owner approve the work in a single decision, so I am not racing the clock against his patience. Two: for the size of this work, the unknown unknowns are bounded. I have done enough vendor evaluations to scope it tightly. Hourly billing on small engagements signals "I am not sure what I am selling." Fixed scope signals expertise.

### Q12. What did you deliberately leave out and why?

I did not include any reference to specific past incidents at the property, even though I suspected he had some. The doc reads cleaner without that loaded language and I wanted him to read it on the architectural merits first. If he has had break-ins, that is a verbal conversation that strengthens the audit-log argument and lets me push the engagement scope up.

---

## 7. Bridging Phrases to Dropzone

When you finish the story, the bridge to Dropzone is short and specific. Have one of these ready:

> "The reason I am telling you this is that the same rule applies to an AI SOC analyst. You do not put a probabilistic system between the alert and the action. You put it next to the analyst, where it amplifies them. That is what excites me about Dropzone."

> "When I read your Stage 3 prep, I noticed the investigation quality thesis. That is the same thing I was selling to this plaza owner. The deterministic system carries the audit. The AI makes the human better at it."

> "I am applying for this role because the architecture I argue for in the field is the architecture you are productizing. I want to be where that architecture is the product."

---

## 8. What NOT to Say

- Do not say "we built." Say "I designed and the owner is procuring." This was a consulting deliverable today, not a deployment.
- Do not say "fully autonomous." The system is deliberately not autonomous. Say "deterministic with AI assistance on the edges."
- Do not name a price you did not actually quote. The 2500 to 5000 range is what your prior conversation drafted. Hold that range.
- Do not claim the owner has signed. Say "the owner showed strong interest, the next step is scope confirmation."
- Do not over-engineer in the answer. If they push for biometrics or hardware tokens, explain why you proposed proportionate controls.
- Do not promise zero risk. Say "the residual risk is bounded by the audit log and the appointment window."

---

## 9. Drilling Schedule

| When | Drill |
|------|-------|
| Tonight | Read the 90-second script out loud 5 times. Time yourself with the phone. |
| Tomorrow morning | Re-read with a coffee. Cover one of the follow-ups blind, pull from this doc, repeat. |
| Tomorrow afternoon | Practice drawing the whiteboard sketch on paper twice without looking. |
| Day before any Dropzone round | Run the 12 follow-ups in random order with a timer. 30 seconds each. If you can not answer, re-read the relevant section here. |
| Morning of the round | One pass on the 90-second script. One pass on the bridge phrase. Stop. Do not over-rehearse. |

---

## 10. Artifact Backing This Story

The DOCX one-pager titled "Campbellton gate access proposal" produced today. Keep it on your laptop, ready to surface if the interviewer asks for evidence or a writeup. If they ask, send it via the recruiter, not directly. The owner has not signed, so do not name him.

---

## 11. The Single Line To Memorize

> "AI on the edges. Deterministic critical path. The unlock decision is load-bearing, so I refused to put a probabilistic system in front of it."

If you only remember one sentence from this entire doc, remember that one. It is the spine of the story, the spine of your AI security philosophy, and the bridge to Dropzone.
