# OneDigital HM Screen — Pavel Kotelnikov (Thu 4/23 1 PM EDT, 30 min Teams)

This is an HM screen, not a recruiter screen. Pavel is making the hire decision. 30 minutes is tight — expect: 3 min intros, 5 min "tell me about yourself", 15 min questions + scenarios, 5 min your questions, 2 min wrap.

**Pavel's profile (verified):**
- Sr. Manager, Information Security, OneDigital
- CISA (ISACA audit/GRC cert holder)
- Kennesaw State University alum — Atlanta local
- LinkedIn: [linkedin.com/in/pavel-kotelnikov-cisa-632604b4](https://www.linkedin.com/in/pavel-kotelnikov-cisa-632604b4/)

**What CISA tells you about his interview style:**
- Control frameworks, not exploit dev
- Process + documentation + evidence trail
- Third-party / vendor risk
- Policy alignment
- Segregation of duties, least privilege, access review
- Risk-based prioritization

**He will NOT grill you on:** Metasploit payloads, CTF-style exploit chains, Burp Suite macro writing, kernel-level detection internals.

---

## Opening — The First Two Minutes

### Identity (never hedge)
"Emmanuel Tigoue. AI Security Engineer at CoreDirective."

### The 60-Second Pitch (memorize, deliver cold)

"I'm an AI Security Engineer at CoreDirective in Atlanta. For about seven months I've been running our production AI security end-to-end — a Claude Opus gateway I've red teamed against OWASP LLM Top 10 and MITRE ATLAS, a shift-left CI/CD pipeline with Trivy, Semgrep, Gitleaks, and OPA on every pull request, and a Cloudflare Zero Trust architecture with mTLS that eliminated every exposed port.

On the detection side, I tuned Falco from 200 alerts a day to 12 actionable, and I built the n8n SOAR that cut our routine triage by 80 percent using NVIDIA NeMo sandboxed workloads. On the governance side, I authored 37 GRC documents including a NIST 800-53-mapped SSP, ten policies including AI Governance, and five IR playbooks including one for AI-specific incidents.

Before CoreDirective I ran IT Security and Operations at Texaco in Atlanta for nearly four years. Ran IR, maintained PCI DSS, built the Splunk deployment that cut MTTD from 48 hours to under 4, and wrote the runbook that reduced containment time from 8 hours to 90 minutes.

I'm finishing my BBA in Cybersecurity at Georgia State in May. Actively pursuing CISSP — sitting before end of April. Certs: SecurityX, SSCP, CCNA, Security+. I'm in this conversation because the OneDigital role lines up with exactly what I do today — AI-specific threat modeling, shift-left AppSec, Zero Trust architecture, SaaS vendor review, and the governance documentation that wraps all of it."

**Pacing:** 55-65 seconds at conversational pace. Practice on voice memo. If you're running over 75 seconds, cut. If under 45 seconds, add a specific tool detail.

---

## Part 1 — 20 Questions Pavel Is Likely to Ask (with model answers)

### Behavioral / Background

#### 1. "Walk me through your background."

Use the 60-second pitch above. Stop there. Let him drive follow-up.

#### 2. "Why OneDigital?"

"Three reasons. One, the company is at a specific moment — Stone Point and CPP Investments closed the majority investment in December at over seven billion, and new capital means the security function has budget and expectation to scale, not just to maintain. Two, you're navigating active third-party risk exposure publicly — the Salesloft Drift impact — at the same time you're building out AI adoption across client-data custodian work. That's the exact intersection I work at today. Three, it's Atlanta-based, and I want to stay in this market."

**Why this answer works for Pavel:** references real public events (shows you did homework), connects to strategic context (shows you think beyond the role), ends with an anchor to stability (shows commitment).

#### 3. "Tell me about a time you disagreed with a technical decision and what you did."

[Use Texaco patching story from `03_TECHNICAL_PREP.md` S7]

Compressed (60 sec): "At Texaco the managed services vendor and the PCI auditor both endorsed quarterly Nessus scans and a 90-day patch cycle. I pushed for monthly scans and 30-day critical SLA because we'd worked a POS incident where the exploit-to-in-the-wild window on similar CVEs was 18 days. I took it up with data — average CVE to public exploit 18 days, 90-day patch means we're knowingly exposed for 72 days after exploits are published. I proposed a staged rollout so patch windows wouldn't disrupt retail operations. Got buy-in from the GM, moved to monthly, dropped critical audit findings from 14 to 2 in eight months. The lesson I named: 'technically correct' loses to the team's operational reality, so you have to design the controls to match how the work actually happens."

#### 4. "What's your management style or work style?"

"Autonomy with clear outcomes. Give me the outcome, the constraints, the deadline, and I'll own the path. I'll over-communicate progress through written updates so you don't have to ask. I read for detail — if you point me at a NIST document or a vendor SOC 2, I'll come back with specific sections, not vague summaries. I default to writing things down — policies, incident records, tabletop notes — because documentation is what turns individual knowledge into organizational capability. On the team side, I'd rather coach peers through a review comment than rewrite their work."

**Why this lands with a CISA manager:** documentation-forward, evidence-forward, clear ownership, doesn't require micromanagement.

#### 5. "What drew you to cybersecurity?"

"Started with an IT ops role at Texaco where a lot of what I was asked to do was fix broken things quickly. The interesting versions of that were security incidents — a POS skimmer, a credential compromise, a vendor access that shouldn't have been open. What I noticed was that the organizations that handled those well had done the paper work beforehand — the runbooks, the segmentation maps, the vendor reviews. The ones that handled them poorly were improvising under pressure. I wanted to be on the side that prepared. That's still why I'm here — I'd rather write the policy that prevents the bad day than triage the bad day."

### Technical / Approach

#### 6. "How do you approach threat modeling for an AI system?"

[Use Q1 frame from `03_TECHNICAL_PREP.md` — STRIDE + MITRE ATLAS + OWASP LLM Top 10 + NIST AI RMF]

#### 7. "What's the biggest AI security risk you're concerned about today?"

[Use Q2 frame from `03_TECHNICAL_PREP.md` — indirect prompt injection]

#### 8. "Walk me through how you'd review a SOC 2 Type 2 report."

[Use Q3 frame from `03_TECHNICAL_PREP.md` — 5-point method]

#### 9. "How do you translate Zero Trust for a non-technical executive?"

[Use Q4 frame from `03_TECHNICAL_PREP.md`]

#### 10. "Describe a security incident you worked."

[Use Story 4 (POS skimmer) from `04_STAR_STORIES.md`]

#### 11. "A user pasted customer SSNs into ChatGPT. What do you do?"

[Use Q5 frame from `03_TECHNICAL_PREP.md` — contain, scope, notify, remediate]

#### 12. "How would you vet a new AI vendor?"

[Use S1 scenario from `03_TECHNICAL_PREP.md` — 7-point vendor AI review]

### Scenario / Judgment

#### 13. "How familiar are you with CIS Top 18?"

"Aligned to it conceptually — at CoreDirective our GRC library is mapped to NIST 800-53, but the 800-53 families cross-reference to CIS control categories cleanly. I can walk through how the OneDigital stack maps to CIS 18: Snyk covers 16, Qualys covers 7, CrowdStrike Falcon + AIDR covers 10 and 13 and 17, Salt covers 13 and 16, the human factors piece in the JD is control 14, the SOC 2 vendor review is control 15. The stack is internally consistent against CIS. My first week I'd spend time inside your existing control documentation to make sure my language matches what your auditors and internal stakeholders are already using."

**Why this works for Pavel:** acknowledges the framework difference between your background and theirs, signals you can translate, shows you've already done some of the mapping work.

#### 14. "The Salesloft Drift incident — what's your read on it?"

**Only if he brings it up specifically.** If he doesn't, do not mention it by name.

"It's a canonical example of the third-party SaaS integration category that's going to keep happening. The attackers compromised a vendor's GitHub environment, pivoted to the Drift AWS environment, stole OAuth tokens, and then just ran bulk exports against seven hundred Salesforce tenants over a ten-day window. Nobody's internal perimeter was breached. That's the point — OAuth scope governance and third-party anomaly monitoring are the controls that would have reduced the blast radius. The industry playbook is public: disconnect the integration, rotate exposed credentials, forensic review of export logs, reduce OAuth permission scopes, monitor data volume anomalies, embed OAuth scope review into Identity Governance. I'd be honest — I haven't managed a response at this scale, but I've built the equivalent scope hygiene in our Cloudflare Zero Trust architecture. I'd apply the published remediation playbook and contribute to the next control generation, not claim I'd have prevented what nobody prevented."

**Key phrase:** "not claim I'd have prevented what nobody prevented." That's the honesty Pavel will respect.

#### 15. "Where do you see yourself in three to five years?"

"Leading a security engineering function or running a mature AI security program. CISSP gets me credential-aligned for the leadership track. The substantive progression I care about is deeper — moving from building the controls to mentoring a team that builds them, owning a broader governance function end-to-end, being trusted with executive and board communication. OneDigital is interesting because it sits in a regulated client-data space and has an acquisition model — both of those create specific career-growth paths I wouldn't get at a pure-engineering company."

### Culture / Fit

#### 16. "What's your pace like — how do you handle multiple parallel things?"

"Parallel is my default. At any given week I'm tuning detection rules, reviewing a vendor SOC 2 report, writing or updating a GRC document, running a code review, handling a sprint ticket. The way I manage it is written prioritization — every Monday I draft a week ahead with outcomes ranked by risk impact and deadline. I keep a running doc where I log what I'm blocked on and what I'm waiting on from others, which cuts out status-meeting overhead. If something slips, I over-communicate early, not late."

**Why Pavel asks:** Glassdoor reviews mention "heavy workloads." He wants to know you can operate in that environment without burning out or dropping balls.

#### 17. "What's a weakness you're working on?"

"I default to writing rather than presenting. My strongest medium is a well-structured document, and I'll sometimes reach for that when a 15-minute walkthrough would be faster and land harder with a non-technical audience. I'm working on it two ways — I stream weekly content live to general audiences, which forces me to simplify and present in the moment, and I've been more deliberate about verbal whiteboard sessions with peers before I lock conclusions into writing. The goal is being equally fluent in both modes, not switching off the writing discipline."

**Why this works:** names a real weakness, connects to the role (you'll need to brief executives + deal with non-technical stakeholders), shows active mitigation, doesn't collapse into "my weakness is I work too hard."

#### 18. "Tell me something about you that isn't on your resume."

"Atlanta's where I've been since I moved to the US for college. I did my first IT work at Texaco while I was a student at Georgia State, and stayed through graduate level work. I stream cybersecurity content weekly — Threat Brief LIVE on Tuesdays, The Build LIVE on Thursdays. That's where a lot of the explainability practice comes from — you can't hide behind jargon when you're doing live Q&A with an audience that includes people at every level of experience. Outside of that, I'm a fairly disciplined person — everything I do has a system attached, because I've found that's how consistency happens when life doesn't cooperate."

#### 19. "Do you have a CISSP timeline?"

"Sitting the exam before the end of April. Pearson Vue date is being locked in this week. Zac flagged the 'in progress' note — I told him I'd have the sit date confirmed. That part of the commitment is on me to keep."

**If he asks about voucher / reimbursement:** "I'd love to discuss that post-offer. Right now I'm focused on the fit conversation."

#### 20. "What questions do you have for me?"

[Use `06_QUESTIONS_FOR_THEM.md` — pick 3 that map to how he'll answer]

---

## Part 2 — Bridge Moments (use these naturally)

### The Kennesaw State rapport opportunity

Pavel is a Kennesaw State alum. Don't force it, but if a moment opens:

"You're at Kennesaw, right? Atlanta's security scene has had good roots there — their cybersecurity program is one of the stronger ones in the region. I'm across town at Georgia State, but we run into each other through OWASP Atlanta and ISSA events."

**Use this only if:**
- He mentions education / background
- He asks about Atlanta security community
- Natural small talk opens at start or end

**Do not:** Force it. Ask about it first. Name-drop. Start with this.

### The ISACA opening (if he asks about professional community)

"I'm planning to join Atlanta ISACA this year — makes sense once CISSP posts to open up joint ISC2/ISACA event access. I've been more active in OWASP Atlanta and streaming my own content, but membership in the chapter is next on the list. Are you active in the Atlanta chapter?"

**Why this works:** honest ("planning to join"), curious about him, creates a rapport opportunity on his home turf, gives him something to say beyond "any questions?"

### The "heavy workloads" signal

If Pavel alludes to workload, volume, acquisition pace, or scale:

"That's actually a fit signal for me. At Texaco I managed IT and security across three locations while completing a degree and authoring the runbook that cut our IR containment time. At CoreDirective I've shipped thirty-seven GRC documents plus the infrastructure and the detection engineering simultaneously. Volume doesn't break me — but I run on written prioritization and over-communication so I don't drop balls."

---

## Part 3 — The Close

### At 25 minutes in — ask for the next step

"What does the process look like from here? Is there a panel round after this, and who would I talk to?"

### Final question — the uncertainty close

If he's pulling back and wrapping, hit this:

"Based on what we've talked through, is there anything that leaves you uncertain about me for this role? I'd rather surface it now than leave it unsaid."

**Why this matters:** asks for the objection, shows you want real feedback, surfaces the concern before it becomes "we went with another candidate." If he answers honestly, you get one last chance to address it. If he dodges, you've signaled confidence without arrogance.

### The post-call follow-up (within 2 hours)

Subject: `Thanks for the time today — Emmanuel Tigoue`

```
Pavel,

Thanks for the conversation. Three things that landed for me:

1. [Something specific Pavel said — his priority, a concern he raised, a project he mentioned]. That matches how I'd think about the role.

2. On [topic where you flagged a gap — Snyk / Entra / CIS 18 specifics], I'll put time in this week so the specifics are sharper if we get to a panel round.

3. [Something the team or role does that you're genuinely interested in].

Let me know what the next step looks like. Happy to share additional references or artifacts if that'd help.

Emmanuel
```

**Tone rules:** human, direct, specific. No em dashes. No "I'm passionate." No "synergy." Short paragraphs. 120 words max.

---

## Part 4 — Day-Of Logistics

**Meeting:** [Teams meeting link](https://teams.microsoft.com/meet/27829678530426?p=U9EAXRGc39kUvB205y)
**Meeting ID:** 278 296 785 304 26
**Passcode:** zp95vw6y
**Dial-in backup:** +1 872-240-8925 conference ID 391 817 090#
**Organizer:** Tommy Hauser (tommy.hauser@onedigital.com)
**Attendees:** Pavel Kotelnikov, Alex (role TBD — OneDigital internal coordinator likely)

**30 minutes before:**
- Test Teams video + audio with a burner meeting
- Glass of water at desk
- Clean shirt, neutral background
- Phone on DND
- Notepad + pen visible
- Index card (see `00_INDEX.md`) visible

**5 minutes before:**
- Enter the Teams meeting lobby. Pavel will admit you.
- Smile before you speak. Changes your voice, even audio-only.
- Energy at 7/10. Not performative — present.
