# COREDIRECTIVE FRAMING — LOCKED VERSION

This is the only CoreDirective framing for the Candescent interview (and any future interview using this resume). All other versions in earlier prep docs are superseded by this file.

---

## Identity

- **Title used in conversation.** AI Security Engineer at CoreDirective.
- **Location.** Atlanta, GA.
- **Posture.** Employee posture by default. If asked directly "do you own it," answer yes honestly.
- **Legal entity.** Tigoue Theory LLC.

## What CoreDirective is

An AI security practice for mid-market and underserved smaller firms. The kind of business that does not have the budget for enterprise AI tooling or has a privacy posture that blocks sending data to OpenAI or Anthropic.

## What CoreDirective sells

A model-flexible AI stack. A router that can hit a frontier model like Claude when capability matters, or hit a self-hosted Ollama (open-source local LLM runtime) when data sovereignty or cost is the binding constraint. n8n for orchestration. Cloudflare on the edge. Same stack pattern he runs on his own infrastructure.

## Anchor client

An accounting firm (the one that did Emmanuel's taxes). They needed AI assistance for client document review and tax research, but their data privacy posture would not allow sending tax data to a third-party API. Replicated his stack pattern for them with the routing defaulted to the self-hosted Ollama side. Tax data never leaves infrastructure they own.

## Engagement model

**Monthly retainer for ops oversight.** Patching, monitoring, model updates, runbook maintenance. The reason to structure it that way: a self-hosted LLM stack needs ongoing care, you cannot ship and forget. This also explains how he stays current.

## Education arm

Free cybersecurity education content under CoreDirective. Notion-based study systems for entry-level certs (Network Plus, Security Plus, CCNA, CISSP). Plus a public GRC (Governance, Risk, and Compliance) documentation library covering NIST 800-53 and NIST AI RMF (AI Risk Management Framework). The line to use: "open source and free cybersecurity education."

---

## The opener (use whenever CoreDirective gets named)

> CoreDirective is my AI security practice. Set up as an LLC. The pattern I sell is a model-flexible AI stack. A router that can hit a frontier model like Claude when capability matters, or hit a self-hosted Ollama when data sovereignty or cost is the binding constraint. n8n for orchestration, Cloudflare on the edge. Same stack I run for my own infrastructure. Anchor client is an accounting firm where data sovereignty was non-negotiable, so the routing defaulted to the self-hosted side. I keep the client list small on purpose because I want to do the engineering, not the sales cycle.

35 seconds. Four memorized anchors:

1. "AI security practice. Set up as an LLC."
2. "Model-flexible AI stack. Router hits Claude or self-hosted Ollama."
3. "Anchor client is an accounting firm."
4. "Small client list on purpose."

## The "tell me about yourself" full pitch

> I am an AI Security Engineer at CoreDirective in Atlanta. Security pulled me in because I grew up watching systems break and the people fixing them always seemed two steps behind. I wanted to be on the side that builds things that hold. The way I work, I am the engineer who writes things down. Codified Terraform, decision logs, runbooks the next person can follow without me. Outside of work I am finishing a double BBA (Bachelor of Business Administration) at Georgia State and I contribute to open source and publish free cybersecurity education content under CoreDirective. The reason I am here today is that this seat has the kind of regulated, multi-tenant complexity I want to keep growing into, and Atlanta is home.

Open with role plus company plus city. Then the human story. Then outside-of-work plus the education arm of CoreDirective. Close with why-this-role and the Atlanta anchor.

---

## Direct question Q and A

### "What is CoreDirective?"

Use the opener above.

### "Is it a team or just you?"

> "Small. The legal entity is mine. I keep the client list intentionally narrow because I want to keep the engineering tight. The accounting firm is the main one I would point to. There is one other engagement I am not at liberty to discuss in detail."

### "Do you own it?"

> "Yes. I set up the LLC. The framing on the resume is engineering work because the engineering is what is relevant to this seat. If I were applying for a CTO or founder role I would frame it differently."

### "Do you have customers?"

> "Yes. Small client list, anchored by the accounting firm. I keep it small on purpose because I want to do deep engineering, not run a sales cycle. The reason I am sitting here today is that I want to bring this kind of work into a regulated environment with a security team."

### "Are you trying to grow it?"

> "Not actively. The practice is where I keep my hands on the engineering, not a business I am scaling. I am better when the engineering work is the main thing, not the sales work. That is also why I am here."

### "Who is your target market?"

> "Mid-market and underserved smaller firms. Businesses that do not have the budget for enterprise AI tooling or that have a privacy posture that blocks sending data to OpenAI or Anthropic. Self-hosted LLM is the differentiator for that customer profile."

### "How do you manage it on a monthly basis?"

> "Monthly retainer for ops oversight. Patching, monitoring, model updates, runbook maintenance. A self-hosted LLM stack needs ongoing care. You cannot ship and forget."

### "How do you keep up with updates?"

> "Daily I read the Cloudflare blog, the SANS (SysAdmin, Audit, Network, Security) Internet Storm Center, and Krebs on Security. Weekly I listen to Risky Business. For AI security I track MITRE ATLAS (Adversarial Threat Landscape for AI Systems) and OWASP (Open Web Application Security Project) LLM Top 10. The hands-on piece is more important than the reading. Every Cloudflare or AI security feature I read about, I try to ship it on my own stack within a week."

### "What model do you actually use?"

> "Depends on the task. Opus 4.7 for the heavy reasoning paths. Sonnet 4.6 for bulk classification. Haiku 4.5 for lookups. Self-hosted Ollama for anything where data sovereignty is binding. The point of the routing layer is that the model choice is a configuration decision per use case, not a vendor lock."

### "Do you have other clients?" (if pressed for a second name)

> "There is one other engagement I am not at liberty to discuss in detail. The accounting firm is the one I can speak to openly."

Do not invent a second client name. Hold the line.

### "Is this a side project?"

> "The engineering is the work. The legal entity is set up for tax purposes, no employees. The thirteen containers I run are real production load every day. The accounting firm engagement is real client engineering. The reason it does not look bigger is that I do not want it bigger. I want this seat."

### "Why a contract role if you have your own practice?"

> "Optionality. I want to see how a senior security team operates inside a regulated bank-tech vendor before I commit to FTE (Full-Time Employment). My practice is not where I want to spend the next decade. The engineering work this seat does is."

---

## The three fallback sentences

If you blank or get pulled off track, these three carry the framing.

1. "CoreDirective is my AI security practice. Anchor client is an accounting firm I built a model-flexible AI stack for."
2. "I keep the client list small on purpose because I want to do the engineering, not the sales cycle."
3. "The patterns I sell to small clients are the patterns Candescent needs on a bigger surface, which is why I am here."

---

## Vocabulary commitments (locked)

| Use | Do not use |
|---|---|
| AI security practice | Lab, side project, hobby, startup |
| Self-hosted on a DigitalOcean droplet I run | On-prem |
| Model-flexible AI stack | Self-hosted only, Claude-only |
| Frontier model like Claude | Just Claude |
| Mid-market and underserved smaller firms | Small businesses (avoid the word "small") |
| LLC for tax purposes | Founder, I built the company, my startup |
| Engineering work, not the sales cycle | Hustling, side hustle |
| Real production load | Demo environment, hobby setup |
| Anchor client | Just one client |

---

## Never-say list (CoreDirective edition)

- "I saw a gap in the market." (Startup pitch.)
- "I founded CoreDirective." (Triggers founder-flag.)
- "It is just a side thing I do." (Discounts the work.)
- "On-prem." (Wrong word for a cloud droplet.)
- "Self-hosted only." (Misses the model-flexible architecture.)
- Any invented client name. (Catastrophic if they verify.)
- Revenue numbers. (Senior answer is "I do not share specifics.")

---

## The three sentences that close any CoreDirective question

If the conversation drifts, return to one of these and pivot back to Candescent.

1. "The engineering is the point. The legal entity is just the wrapper."
2. "Small client list on purpose. Engineering depth over sales motion."
3. "The patterns I run for small clients are the patterns you need on a bigger surface."

---

## What this framing wins you

- **JT (security architect).** Hears: "this person designs trade-offs, runs production, has ground truth on the patterns they claim."
- **Augustine (GRC and audit lean).** Hears: "this person treats privacy and audit trails as design inputs, runs a teaching arm, communicates clearly."
- **Both.** Hears: "this person is the engineer the practice produced, not the salesperson the practice needs to grow."

That is the senior framing. It is true. It is consistent. It does not need to be defended because it does not stretch.

---

# THE ACCOUNTING FIRM STORY (FULL LAYOUT)

This is your primary client story. One story across all interviews. Angles change depending on the role.

## The setup

The accounting firm that did Emmanuel's taxes wanted AI assistance for client document review and tax research. Two blockers stopped them from using ChatGPT, Claude, or Gemini directly.

1. **Privacy posture.** Tax data is regulated PII (Personally Identifiable Information). Sending it to a third-party API created data residency and consent issues their compliance reviewer would not approve.
2. **Cost.** API spend at any meaningful query volume would have wiped their margin on the AI-assisted service offering.

## The decision

Self-hosted LLM (Large Language Model) on infrastructure they control. Trade frontier-model capability for data sovereignty and predictable cost. Same model-flexible stack pattern Emmanuel runs on his own infrastructure, with the routing default flipped so all client-data queries go to the local Ollama model.

## The build

Single droplet under their account. Docker Compose for the runtime. Six containers.

- **Ollama** running an open-weight model (Llama 3 family) for inference
- **n8n** for workflow orchestration (document upload, chunking, retrieval, response)
- **PostgreSQL** with pgvector for retrieval over their internal tax research notes
- **Cloudflare Tunnel (cloudflared)** for ingress, no inbound port on the origin
- **Lightweight monitoring** (Datadog Agent on the droplet, free tier)
- **Backup container** running a nightly database snapshot to encrypted object storage

The only public surface is the Cloudflare hostname. Cloudflare Access (Zero Trust application gating) policy restricts access to staff email addresses on their domain. WAF (Web Application Firewall) rules block scanner traffic and rate limit on the chat endpoint.

## Incident response (IR) for this client

Six beats. Same structure Emmanuel uses on his own stack, scoped down for a small client.

### 1. Detection

- **Cloudflare Security Events** surface any WAF action, Rate Limiting trigger, or Access challenge in real time
- **Cloudflare Access logs** record every staff session (who, when, from what IP)
- **Ollama process health checks** ping every 60 seconds
- **n8n workflow execution logs** capture failed runs and unusual latency

A Telegram bot in Emmanuel's CoreDirective control plane fires a notification on any of these signals.

### 2. Triage

First-pass classification. Two questions.

- Is this a security event (unauthorized access attempt, scanner, abuse) or a performance event (Ollama OOM, n8n stuck workflow)?
- Severity. Does it affect data integrity, access control, or just usability?

The RayID (Cloudflare's unique per-request identifier) is the join key when correlating Cloudflare edge logs against Ollama or n8n logs on the origin.

### 3. Containment

For a security event:

- Drop a custom WAF rule blocking the offending signature within minutes via the Cloudflare API
- Tighten Rate Limiting on the affected endpoint
- If credential abuse is suspected, revoke Access tokens and force re-authentication
- Worst case: take the n8n webhook offline. The LLM stays running for staff queries.

For a performance event:

- Restart the affected container
- Scale the droplet vertically if memory pressure is the cause
- Open a ticket with the client IT contact for anything requiring access to their account

### 4. Communication

- Telegram message to Emmanuel for any signal that requires action
- Email summary to the client IT contact within the same hour for anything user-visible
- Datadog log entry as the audit trail

### 5. Recovery

- Validate clean traffic patterns before lifting any containment rule
- Confirm with client that the user-facing service is back to normal
- Roll back rules that turned out to be too aggressive

### 6. Post-incident

- Decision log entry per change made during the incident
- Runbook update if the incident exposed a gap in the existing runbook
- Monthly status report flags the incident with severity and resolution time

## Triage workflow specifically

When something fires, Emmanuel runs through this in order.

1. **Classify.** Security or performance? (30 seconds)
2. **Score severity.** Is data at risk, access at risk, or just service degradation? (30 seconds)
3. **Contain or escalate.** If containable from the Cloudflare or n8n control plane, contain immediately. If it requires server-side access, escalate to the client IT contact. (1 to 5 minutes)
4. **Document the decision.** Decision log entry while the context is fresh. (2 minutes)
5. **Communicate.** Telegram, email, or both depending on user impact. (2 minutes)
6. **Recover.** Validate, confirm with client, lift containment. (10 to 60 minutes)
7. **Post-incident.** Update runbook, update monthly report. (15 minutes after resolution)

Total time-to-contain target: under 30 minutes for active incidents. Most signals are non-incidents and resolve in the triage phase.

## Documentation discipline

Three artifacts maintained per client.

### 1. Decision log

One markdown file per client engagement. Append-only. Every architectural decision and incident gets a dated entry. Format: date, decision, alternatives considered, rationale, expected trade-off, follow-up actions.

The reason this matters: when Emmanuel revisits the stack three months later, or hands off to another engineer, the decision log is the operating manual. It is also the audit evidence trail if the client ever gets reviewed.

### 2. Runbook

One markdown file covering the operational paths. Sections:

- Standard operations (deploy, restart, backup verify)
- Common issues (Ollama OOM, n8n stuck workflow, Cloudflare Access misconfig)
- Incident response (the six beats above)
- Escalation contacts (client IT contact, Cloudflare support, Emmanuel)

The runbook is given to the client IT contact so they can take first-pass action if Emmanuel is unreachable.

### 3. Monthly status report

Automated where possible (Cloudflare Analytics API, Ollama query metrics, Datadog uptime). Sent to the client managing partner on the first business day of each month. Sections:

- Uptime and availability
- Query volume and patterns
- Any incidents (severity, resolution time, lessons)
- Recommended changes for the coming month
- Compliance posture summary (Access logs reviewed, WAF rule additions, model updates applied)

## How to tell this story (T-D-C-E-O)

> **Threat.** The accounting firm that does my taxes wanted AI assistance for client document review and tax research. The blocker was that all the obvious tools (ChatGPT, Claude, Gemini) meant sending tax data to a third-party API. Their data privacy posture would not allow it, and the API bill at any volume would have wiped their margin on the service.
>
> **Decision.** Self-hosted Large Language Model on infrastructure they control. Trade some model capability for data sovereignty and cost predictability.
>
> **Control.** Replicated the stack pattern I run on my own infrastructure. Single droplet, Ollama running an open-weight model, n8n for orchestration, PostgreSQL with pgvector for retrieval, Cloudflare Tunnel for ingress with Zero Trust Access in front. No inbound port on the origin. Staff hit the service through a Cloudflare Access policy on their email domain.
>
> **Evidence.** Cloudflare Access logs are the audit trail showing only their staff hit the endpoint. Tunnel inverts the trust direction so the origin never has a listening port to scan. Monthly status report goes to the managing partner on the first business day of each month.
>
> **Outcome.** They got the productivity lift from AI on tax research and document review. Their data privacy posture stayed clean. Cost is a fixed monthly droplet bill plus my retainer instead of a variable API bill.
>
> **Lesson.** For regulated or cost-sensitive businesses, self-hosted LLM is not a downgrade. It is a different set of trade-offs. Frontier API for capability. Self-hosted for sovereignty and cost. Senior engineers know which trade is right for the customer in front of them.

## Role-specific angles (one story, different focus)

### For a Cloudflare role (like Candescent)

Emphasize: Cloudflare Tunnel inverting trust direction, Zero Trust Access policy, WAF rules, Rate Limiting, RayID as the join key for incident correlation. The accounting firm becomes a case study in shipping production Cloudflare for a regulated-data customer.

### For an AppSec or AI security role

Emphasize: threat modeling against OWASP LLM Top 10, the routing decision logic (when to hit Claude versus Ollama), prompt injection mitigations, output guardrails, the model selection trade-off as a security control.

### For a GRC or compliance role

Emphasize: data sovereignty as the binding constraint, the audit trail design (Access logs, decision log, monthly status report), how the architecture maps to NIST AI RMF and SOC 2 (Service Organization Control 2) common criteria, evidence-by-design.

### For a SRE or infrastructure role

Emphasize: the runbook, the monthly status report, time-to-contain target under 30 minutes, the IR triage workflow, monitoring setup, backup discipline, capacity planning under fixed-cost constraints.

### For a federal or cleared role

Emphasize: data residency and sovereignty, the principle of "data does not leave infrastructure the customer owns," supply chain considerations (open-weight model under a commercial-friendly license, no telemetry to third parties), evidence pipeline.

## What this story buys you across the pipeline

Same facts. Different emphasis. One story to drill, not five. The accounting firm engagement is now your most flexible interview asset.

For Candescent specifically: the story shows you have shipped Cloudflare Tunnel plus Zero Trust Access plus WAF for a regulated-data client. That is the same pattern they need for FI-tenant traffic. The accountant's tax data privacy posture is structurally identical to Candescent's FI customer data privacy posture. You have done the small version of what they do at multi-tenant size.
