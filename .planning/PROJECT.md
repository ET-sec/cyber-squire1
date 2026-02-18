# Cyber-Squire Engine

## What This Is

A Telegram-first automation system that routes commands (text and voice) to specialized n8n workflows for task management, content generation, and security operations. Built for a cybersecurity specialist (CASP+, CCNA, SSCP).

## Core Value

**Every interaction through Telegram must route to the right workflow with zero manual overhead.** If the router fails, nothing downstream works.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Telegram Router (Agent 01) receives and classifies all incoming messages
- [ ] Voice notes transcribed via Whisper before routing
- [ ] AI inference cascades: Ollama → Gemini (free) → manual Claude escalation
- [ ] All outputs formatted for ADHD: bold keywords, max 3 bullets, single next-step
- [ ] Low-uptime mode switches system to passive/maintenance tasks

### Out of Scope

- Claude API integration — subscription only, no API billing
- Mobile app — Telegram is the interface
- Real-time dashboards — Notion serves as the data layer
- Multi-user support — single principal (ET)

## Context

**Principal Profile:**
- Cybersecurity: CASP+, CCNA, SSCP, SecurityX, Zero Trust, NIST RMF

**Business Entity:**
- CoreDirective: Security operations and automation

**Infrastructure (Running):**
- EC2 t3.xlarge (16GB RAM)
- n8n in Host Mode, Port 5678
- PostgreSQL 16 @ localhost
- Ollama + Qwen 3 8B (7.5GB)
- Telegram Bot: @Coredirective_bot
- Cloudflare Tunnel for access

**Existing Workflows (Partial):**
- Various n8n workflow JSONs in `COREDIRECTIVE_ENGINE/`
- Need debugging and completion

## Constraints

- **Budget**: No Claude API — Ollama/Gemini free tier only for automation
- **Energy**: All outputs scannable (ADHD-optimized format)
- **Security**: No hardcoded credentials (env vars only)
- **Latency**: Voice commands must feel responsive (<5s to acknowledgment)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Telegram as sole interface | Single entry point, mobile-friendly, voice support | — Pending |
| Ollama → Gemini → Manual Claude cascade | Stay within budget, Claude Max subscription only | — Pending |
| 4-agent architecture | Token efficiency, prevent context rot | — Pending |
| Host Mode n8n (not Docker) | Direct PostgreSQL access, simpler debugging | — Pending |

---
*Last updated: 2026-02-04 after initialization*
