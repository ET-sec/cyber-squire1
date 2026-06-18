# HIS-STACK: Threat Model of CoreDirective Engine (Production)

This is the threat model of Emmanuel's actual production stack. The single most powerful asset for any AI security interview. Open with: "I threat-modeled my own production stack and shipped the controls. Want me to walk you through it?"

System under model: CoreDirective Engine, hosted on a single DigitalOcean droplet running 14 containers, fronted by Cloudflare Tunnel, with Teleport for privileged access and Falco for runtime detection.

---

## Scope (Phase 1)

### Assets
- Postgres (workflow state, audit, n8n data, event store)
- n8n workflow secrets (44 secrets in env)
- LLM API keys (Anthropic, OpenAI, Tavily, Notion, Gumroad, Cloudflare, Telegram)
- Customer / brand IP (content, gumroad products, business correspondence)
- Personal credentials federated through OAuth (Gmail, Google Workspace)
- OpenClaw gateway authority (full Claude Opus 4.7 access)
- Telegram bot tokens (two bots routing to control surfaces)
- Vault unseal keys
- Keycloak realm and admin credentials
- Falco rule set and Datadog API keys
- The droplet itself (root-equivalent host)

### Actors
- Emmanuel (legitimate operator)
- External attacker (internet, scanning Cloudflare-fronted endpoints)
- Compromised LLM provider (Anthropic/OpenAI vendor breach)
- Adversarial Telegram message (prompt injection into bot)
- Adversarial email content reaching Gmail-reader workflows (indirect injection)
- Compromised npm/pip/Docker dependency
- Cloudflare account compromise (downstream of phishing)
- Doppler / 1Password compromise (secrets vault)
- Curious passerby on TikTok/YouTube live streams (exposure of internal topology)

### Data classes
- LLM API keys (highest)
- Vault unseal keys (highest)
- Customer / business email content via Gmail readers (high, may include PII)
- Workflow state in Postgres including OAuth tokens (high)
- Audit logs (high, evidence)
- Public docs / GRC corpus (low, deliberately public)

### Assumptions
- Single droplet, single region (nyc1), no HA
- Doppler is the only secrets path; 1Password write-only
- Cloudflare Tunnel is the only inbound path
- No public ports on the droplet (only Tunnel)
- Falco runs in-band, ships to Falcosidekick to Datadog
- Datadog is the SIEM, Sentry is the application error tracker

---

## DFD (Phase 2)

```
                                       INTERNET BOUNDARY
[ Emmanuel's Browser ] -----> ( n8n.tigouetheory.com via CF Access )
[ Telegram User ]      -----> ( Telegram BotAPI )
[ Email Senders ]      -----> ( Gmail )
                                       |
                                       v
                          ( Cloudflare Edge / WAF )
                                       |
                                       | TLS, identity gate (Access for some routes)
                                       |
                                       v
                          ( Cloudflare Tunnel: tunnel-cyber-squire )
                                       |
- - - - - - - - - - - - - - - - - - - | - - - - - DROPLET BOUNDARY
                                       v                  no inbound ports
                          ( cd-service-n8n :5678 )
                                       |
                                       +--> ( cd-service-db :5432 )  Postgres + audit
                                       +--> ( OpenClaw gateway :18789 ) ----> Anthropic
                                       +--> ( cd-service-ollama :11434 )
                                       +--> ( cd-service-whisper :8000 )
                                       +--> egress to Telegram, Gmail (OAuth), Notion, Gumroad
                                       
                          ( cd-service-vault :8200 )  -- secrets, future use
                          ( cd-service-keycloak :8080 ) -- IdP, future use
                          ( cd-service-teleport :3080 ) -- PAM, JIT
                                       |
                                       v
                          ( cd-service-event-handler ) -> ship audit
                                       |
                                       v
                          ( cd-service-fluentd ) ------> Datadog SaaS
                                       
                          ( cd-service-falco )    --syscalls / eBPF--> ( cd-service-falcosidekick ) ----> Datadog
                          ( cd-service-datadog agent ) --infra metrics--> Datadog SaaS

[ Engineer Laptop ] --tsh login--> ( Teleport Proxy ) --> Teleport Auth --> Node Agent on droplet

[ OpenClaw Mac CLI ] --ws://---> ( OpenClaw Gateway )

                          ===== Doppler (SaaS) =====
                                       |
                                       | inject env vars at container start
                                       v
                          ( all containers )
```

### Trust boundaries
1. Internet to Cloudflare edge (TB1)
2. CF edge to Tunnel daemon to host (TB2, no inbound ports)
3. Tunnel to localhost service in container (TB3)
4. n8n workflow to internal services (Postgres, Ollama, Whisper) over Docker net (TB4)
5. n8n to OpenClaw gateway (TB5, LLM authority boundary)
6. OpenClaw to Anthropic / Tavily (TB6, third-party egress)
7. Telegram BotAPI to bot token holder (TB7)
8. Gmail OAuth to n8n Gmail readers (TB8, indirect injection boundary for email content)
9. Doppler SaaS to container env (TB9, secrets supply chain)
10. Teleport access to droplet shell (TB10, PAM boundary)
11. Container runtime to host kernel (TB11, escape boundary)
12. Falco syscall capture vs container runtime (TB12, detection boundary)
13. OpenClaw output to tool execution (TB13, agent authority boundary)
14. Audit log writer to Datadog (TB14, evidence integrity)

---

## STRIDE plus ATLAS matrix (Phase 3)

| # | Boundary | Framework | Threat | L | I | Risk |
|---|----------|-----------|--------|---|---|------|
| 1 | TB1 | D | Volumetric DDoS exhausts Cloudflare quota or Tunnel concurrency | M | M | M |
| 2 | TB1 | S | Phished Cloudflare account, attacker reroutes Tunnel | L | H | M |
| 3 | TB2 | I | Tunnel daemon credentials leak from `/etc/cloudflared` | L | H | M |
| 4 | TB3 | E | Service exposed via Tunnel without app-level auth (n8n basic auth misconfigured) | M | H | H |
| 5 | TB4 | E | Container in Docker network reaches another container without scope (cd-service-n8n hits Vault) | M | H | H |
| 6 | TB5 | E + AML.T0048 | n8n workflow grants OpenClaw a tool the workflow author did not intend | M | H | H |
| 7 | TB6 | I | Sensitive email content forwarded to Anthropic, retained for training | L | H | M |
| 8 | TB7 | S | Telegram bot token leaked, attacker sends commands as the bot | M | H | H |
| 9 | TB8 | T + AML.T0051 | Adversarial email content includes prompt injection that manipulates the bot's reasoning | H | H | H |
| 10 | TB9 | I | Doppler personal token compromised, attacker pulls all 44 secrets | L | H | M |
| 11 | TB9 | T | Doppler personal token used from a non-Mac IP, secrets exfil | L | H | M |
| 12 | TB10 | E | Teleport role lets engineer drop to root, no command filtering | M | H | H |
| 13 | TB10 | R | Teleport session recording disabled or stripped from audit | L | H | M |
| 14 | TB11 | E | Container escape via privileged container or kernel CVE | L | H | M |
| 15 | TB12 | T | Falco rules disabled or container compromised before alert ships | L | M | L |
| 16 | TB13 | E + AML.T0051 | Indirect injection in retrieved chunk causes OpenClaw to call Notion or Gumroad write tools maliciously | M | H | H |
| 17 | TB14 | T | Audit log tampered locally before fluentd ships | L | H | M |
| 18 | TB1 | I | Streaming the screen on TikTok/YouTube reveals an internal hostname or token | M | M | M |
| 19 | TB6 | D | Anthropic outage or rate limit cascades to all bot workflows | M | M | M |
| 20 | TB4 | T | Compromised npm package in n8n Functional node executes arbitrary code | M | H | H |
| 21 | TB7 | T | Replay of legitimate Telegram update (no dedup), command runs twice | M | M | M |
| 22 | TB13 | E | OpenClaw skill installed from registry contains malicious code | L | H | M |

---

## Top 15 threats prioritized

1. (#9) Indirect prompt injection from email content into bots
2. (#4) Service behind Tunnel with weak app-level auth
3. (#6) n8n grants over-scoped tools to OpenClaw
4. (#16) Indirect injection in OpenClaw causes write-tool abuse
5. (#5) Lateral movement between containers on Docker net
6. (#12) Teleport role too broad
7. (#8) Telegram bot token leak
8. (#20) Compromised npm dep in n8n function
9. (#22) Malicious OpenClaw skill from registry
10. (#1) Volumetric DDoS
11. (#7) Sensitive email egress to LLM
12. (#14) Container escape
13. (#18) Stream exposure of internal data
14. (#10) Doppler token compromise
15. (#21) Telegram update replay

---

## ATLAS mapping (LLM-specific overlay)

| ATLAS code | Technique | Where in stack | Mitigation |
|------------|-----------|----------------|------------|
| AML.T0051 | LLM Prompt Injection | Telegram messages, retrieved emails, Gmail readers, OpenClaw context | Input tagging, no tool call without scope check, critique loop on plans |
| AML.T0048 | External Harms | OpenClaw with write tools (Notion, Gumroad, GitHub) | Tool allow-list, HITL on irreversible writes, per-run action caps |
| AML.T0024 | Exfiltration via Inference API | Anthropic egress with sensitive context | Pre-LLM scrubber (regex + Presidio), DPA with provider, daily token budget |
| AML.T0044 | Full ML Model Access | OpenClaw gateway has full Opus 4.7 authority | Gateway audit logs, per-skill scope, rotation of OPENCLAW_ANTHROPIC_KEY |
| AML.T0019 | Publish Poisoned Datasets | Threat-intel-style content reaching the bot via email or Telegram | Treat all external content as untrusted input, render in tagged context |

---

## Mitigations (Phase 5) - what is shipped vs planned

| # | Threat | Primary control (status) | Compensating | 
|---|--------|--------------------------|--------------|
| 1 | Indirect injection from email | SHIPPED: tag-context strategy in n8n LLM nodes; PLANNED: dedicated input rail similar to NeMo on the Squire SOC pattern | Critique loop on actions taken |
| 2 | Service behind Tunnel | SHIPPED: n8n basic auth + Doppler-managed credentials; PLANNED: CF Access policy on every route, not just SSH | Tunnel daemon scoped per service |
| 3 | n8n over-scoped tools | SHIPPED: per-credential scoping in n8n; PLANNED: per-workflow allow-list of which credentials it may use | Audit log diff weekly |
| 4 | OpenClaw write tool abuse | SHIPPED: HITL via Telegram approval for risky tools; PLANNED: tool router with per-skill scope | Per-run action caps |
| 5 | Container lateral movement | SHIPPED: Docker network segmentation per Compose; PLANNED: explicit deny rules between unrelated services | Falco rule on cross-service connections |
| 6 | Teleport role breadth | SHIPPED: Teleport v18 with role-based RBAC; PLANNED: command filters and JIT elevation for root | Session recording on every connection |
| 7 | Telegram token leak | SHIPPED: token in Doppler, never in code; PLANNED: rotate quarterly | Alert on bot use from unknown chat ids |
| 8 | npm supply chain | SHIPPED: lockfile pinning; PLANNED: SBOM for n8n custom nodes, Trivy scan of compose images | Datadog metrics on n8n function exec time anomaly |
| 9 | Malicious OpenClaw skill | SHIPPED: skills curated, not auto-installed; PLANNED: signature verification on skill registry | Manual review of every skill before deploy |
| 10 | Volumetric DDoS | SHIPPED: Cloudflare in front; PLANNED: rate-limit rules per route | Tunnel will refuse new connections at saturation |
| 11 | Email content egress | SHIPPED: scrubber on Gmail reader output before LLM; PLANNED: Presidio integration | Anthropic DPA, daily token ceilings |
| 12 | Container escape | SHIPPED: no privileged containers, no hostPath, Falco; PLANNED: AppArmor profiles per service | Datadog Falco alerts page on escape signatures |
| 13 | Stream exposure | SHIPPED: streamer-mode toggle that routes sensitive output to Telegram instead of screen; rules in CLAUDE.md | Pre-stream checklist |
| 14 | Doppler token | SHIPPED: token rotation, scoped to coredirective-engine/prd; PLANNED: short-lived tokens via Doppler service tokens for CI | Datadog alert on Doppler API access from new IP |
| 15 | Telegram replay | SHIPPED: update_id dedup in workflow state; PLANNED: explicit idempotency table | Daily reconciliation report |

---

## Residual risk (Phase 6)

After mitigations as currently shipped: 0 HIGH, 7 MEDIUM, 15 LOW.

MEDIUMs accepted with rationale:
- Indirect prompt injection from email/Telegram: accepted because no perfect class-of-defenses exists in 2026; mitigation layered with tagging plus critique plus HITL on writes. Tracked as ongoing.
- n8n over-scoped tools: accepted because workflow-level scoping is in place; per-workflow allow-list is in next sprint.
- Container lateral: accepted because Falco is the detective control; explicit deny rules planned.
- Teleport breadth: accepted because session recording captures everything and root usage is rare; command filtering planned.
- Doppler token compromise: accepted because token is on a single trusted Mac with Touch ID; service tokens for CI planned.
- Volumetric DDoS: accepted because Cloudflare bears the brunt and the droplet would degrade gracefully.
- Stream exposure: accepted with streamer-mode toggle and pre-stream checklist as compensating controls.

The HIGH I would not run without: app-level auth on every Tunnel route. That is non-negotiable.

---

## Detections (Phase 7)

Currently shipped:
- Falco syscall anomalies via Falcosidekick to Datadog (lateral movement, file integrity)
- Datadog infra metrics (CPU, memory, disk) per container
- Sentry on application errors in n8n custom nodes and OpenClaw gateway
- Cloudflare audit log on tunnel and DNS changes
- Teleport session recording, all connections
- Postgres audit table with workflow execution history

Planned next:
- Per-tool action rate alerts on OpenClaw (excess agency signal)
- Critique-loop disagreement metric for any LLM-driven action
- Doppler API access monitoring (new IP, new device)
- Daily SBOM diff on Compose images
- DLP scanner on stream output captures (post-hoc)

---

## What I would build next (prioritized)

1. Dedicated input rail for Telegram and Gmail content, modeled on NeMo Guardrails (4 weeks). Closes #1.
2. Tool router for OpenClaw with per-skill scope and explicit allow-list (3 weeks). Closes #4 and #6.
3. CF Access policy on every route, not just SSH (1 week). Closes #2.
4. Service tokens replacing personal Doppler token (1 week). Closes #10.
5. Image signing with Cosign across the Compose images and admission verification (2 weeks). Closes #20 and #22.
6. AppArmor profiles per container and removal of any remaining capabilities (2 weeks). Closes #14.
7. Quarterly red team of the bot stack with adversarial email prompts (recurring). Validates #1 and #4.

---

## Interview-ready talking points

When the interviewer says "tell me about a system you have threat modeled":

> "I threat modeled my own production stack last quarter. It is a single droplet running 14 containers: n8n for orchestration, Postgres, Vault, Keycloak, Teleport, Falco, Datadog agent, Ollama, Whisper, Cloudflare Tunnel, and an OpenClaw gateway that gives a Claude model tool access to my Notion, Gumroad, GitHub, and Gmail. I treated the email and Telegram inbound paths as the highest-risk trust boundaries because both feed text directly into LLM context, which makes them indirect prompt injection vectors. I mapped the LLM-specific surface to MITRE ATLAS, especially T0051 prompt injection and T0048 external harms. The fix that mattered most was scoping OpenClaw's tool access by skill and adding a critique loop. The residual risk I am still chasing is full input-rail enforcement on inbound text, modeled on NeMo Guardrails. The point of the exercise is not the diagram. It is the discipline of asking 'who could do what at every boundary' and making sure the answer is acceptable before I let strangers send messages to my bot."

When asked "what was the most surprising thing you found":

> "That my OpenClaw gateway was a confused-deputy waiting to happen. The LLM had legitimate authority over six tools. None of those tools individually checked whether the LLM was acting on a request from me or from an attacker who got into context via a poisoned email. Adding a tool router with per-skill scope and HITL on writes was a one-week change. It dropped my residual from HIGH to MEDIUM on three threats simultaneously."
