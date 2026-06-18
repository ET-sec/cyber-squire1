---
name: interview-prep
description: Mock interviews tailored to specific job postings. Behavioral + technical prep, ADHD-optimized.
---

# Interview Prep

## Quick Prep (30 min before)

1. Fetch job posting via `web_fetch` if URL provided
2. Extract: role, required skills, company values, team size
3. Research company with `web_search` — recent news, products, culture
4. Generate the 3 prep packets below

## Behavioral Questions (STAR Format)

Prep exactly 3 stories from real experience. Each covers multiple questions:

**Story 1 — Built Something Complex:**
- The EC2 multi-service stack (PostgreSQL, n8n, Ollama, Whisper, OpenClaw, Cloudflare tunnel)
- STAR: Situation (needed autonomous AI infrastructure), Task (design and deploy), Action (Docker orchestration, Terraform, security hardening), Result (17-service orchestrator running 24/7)

**Story 2 — Solved a Hard Problem:**
- OpenClaw session corruption + rate limit cascade (debugged corrupted tool_use history, cleared cooldown, upgraded gateway)
- Or: n8n Switch v3 bug discovery (found that v3 breaks on import, documented workaround with v2)

**Story 3 — Worked Under Pressure:**
- Security incident: Telegram bot token exposed in public repo across 5 files. Identified, documented, planned revocation.

Map each story to common questions:
- "Tell me about a challenging project" → Story 1
- "How do you debug production issues" → Story 2
- "Tell me about a mistake and what you learned" → Story 3

## Technical Questions

Generate based on job posting requirements. Default areas:

**AWS:** VPC design, IAM policies, EC2 vs ECS vs Lambda tradeoffs, cost optimization, security groups
**Docker:** Multi-container orchestration, networking, volumes, compose vs swarm vs k8s, debugging crashed containers
**CI/CD:** GitHub Actions, deployment strategies, rollback procedures
**Python:** Data structures, API design, error handling, async patterns
**Networking:** DNS, reverse proxies, tunneling (Cloudflare), TLS, ports

Format: Question → Think through it → Key points to hit → What NOT to say

## Mock Interview Mode

When user says "mock me" or "practice interview":
1. Ask which role/company
2. Ask 5 questions (mix behavioral + technical)
3. Wait for answer to each
4. Give feedback: what was strong, what to add, what to cut
5. Score 1-10 with specific improvement notes

## ADHD Interview Day Checklist

- [ ] Company name, interviewer name, role title written down
- [ ] 3 stories rehearsed (say them out loud, not just in your head)
- [ ] 2 questions to ask THEM ready
- [ ] Tech setup tested (camera, mic, internet) if remote
- [ ] Water bottle, notebook, pen nearby
- [ ] Phone on silent
- [ ] Join 5 min early, not 15
