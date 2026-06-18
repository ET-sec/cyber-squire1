# Voya Lead AI Security Engineer (EADS-2026-AISE) — Scorecard

## Recruiter and process snapshot
- Staffing firm: Pride Veterans Staffing Inc (Hoboken NJ)
- Primary recruiter (email): Lakshay Kumar, lakshay@prideveterans.com, 551-295-0467
- LinkedIn recruiter: Yogesh Kumar, yogesh@prideveterans.com, 217-765-0392
- Stages on JD: 7 (recruiter, HM, live build, red team, domain + governance, panel with Model Risk, refs + offer)
- Glassdoor reality: typically 3 to 5 stages, 22 day end to end average. JD's "offer in 5 business days" is optimistic.

## Comp band (defensible anchor)
- Voya is mid-market for IC engineers, not frontier-lab
- Base target: **$200,000** (range 175K to 210K)
- Bonus: 15 to 20 percent
- LTI: 25K to 50K/year
- All-in target: **$235,000** (range 215K to 275K)
- Floor walk-away: $185K base / $215K all-in
- Voya FY25 H1B median for Voya Services is $143K, 90th pct $178,602 (Software Engineer band)
- Anchor against Senior Staff Information Security Engineer market ($210K median, $257K at 75th pct), not internal Voya bands
- DO NOT WRITE a rate before they bring it up

## Resume vs JD scorecard

| Requirement | Resume strength | Score |
|---|---|---|
| Prompt injection and jailbreak defense | OpenClaw model gateway threat model, adversarial test suite on MCP skill catalog | 9 / 10 |
| Data exfiltration and leakage controls | Adversarial test suite covers exfiltration, GLiNER PII redaction, NeMo guardrails | 8 / 10 |
| Agent / MCP / tool security | n8n agent platform with Vault, function call validation, least privilege scopes | 8 / 10 |
| Autonomy red-teaming | Squire LangGraph human in loop, vuln mgmt on agent capabilities | 7 / 10 |
| Model supply chain | OpenClaw gateway, model gateway language, Cosign signing, Syft SBOMs | 7 / 10 |
| TypeScript / Python | Python real, TypeScript intermediate. Drill before live build round. | 5 / 10 |
| **Go and Rust** | **GAP. No production claim. Defend with TypeScript pick in stage 3.** | 2 / 10 |
| **Azure AI Foundry, Databricks** | **GAP. Resume is AWS / DigitalOcean / Cloudflare focus. Honest answer required.** | 3 / 10 |
| **ERISA / retirement domain** | **GAP. HIPAA / PCI / SOC 2 / ISO 27001 adjacency, no fiduciary work.** | 2 / 10 |
| GRC + AI governance | 57 docs, NIST AI RMF, ISO 42001, AI Incident Response playbook | 9 / 10 |

## Before / after read

| Lens | Before (foundation) | After (Voya tailored) |
|---|---|---|
| ATS keyword match | 64 percent | 87 percent (model gateway, MCP, tool calling, adversarial test suite, function call validation, tenant isolation, autonomy red-team all hit) |
| Recruiter confidence | 7 / 10 | 9 / 10 |
| Hiring manager verdict | "Maybe, leaning yes" | "Yes for tech screen" (predicted) |
| Peer credibility (Lead bar) | Conditional yes | Conditional yes (Go gap unchanged) |
| Blended interview probability | 55 percent | 72 percent if the live build goes clean |

## What the tailored version actually changed
- Bullet 10: dropped Claude Opus model version (peer audit caught Opus 4.8 typo on flagship). Added "model supply chain risk" language.
- Bullet 11: reframed from "vulnerability management lifecycle" to "adversarial test suite" on OpenClaw MCP-style skill catalog.
- Bullet 12: secured the n8n agent platform with HashiCorp Vault, function call validation, least privilege tenant scopes. Hits 3 JD must-haves.
- Bullet 17: surfaced AI Incident Response playbook and Promptfoo continuous adversarial testing.
- Skills line: rebuilt around tenant isolation, autonomy red-teaming, output and tool-call validation, data exfiltration controls. No duplication with bullets.
- Cut: VLAN bullet, AD IAM bullet, LLM phishing at gas station bullet. All low signal for Voya.

## Top 3 risks at the loop
1. **Live build in Go.** Pick TypeScript when offered the choice. Drill prompt injection harness in TypeScript before the technical round.
2. **Azure AI Foundry depth questions.** Acknowledge gap, pivot to the platform-agnostic threat model work (OpenClaw is the lab, the patterns transfer to Foundry / Databricks).
3. **ERISA fiduciary probes in domain round.** Read the Benefits Law Advisor AI under ERISA guide (linked in /tmp/voya_interview_process.md). Frame: fiduciary sensitivity of outputs, do-not-train enforcement, residency obligations.

## One high-impact differentiator move (per competition audit)
Publish a public MCP and agent red-team write-up using the existing OpenClaw stack as the lab. Map findings to OWASP MCP Top 10 and OWASP LLM Top 10. Ship repo plus blog post plus 60 to 90 second demo. Send the link in the recruiter screen as Exhibit A.

One weekend of work. Pre-clears stages 2, 3, and 4.
