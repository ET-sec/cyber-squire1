---
name: portfolio-generator
description: Generate portfolio case studies from GitHub repos, architecture configs, and real project data
---

# Portfolio Generator

Auto-generate polished portfolio content from the user's existing projects and infrastructure.

## Source Projects

### Project 1: Cyber Squire -- Multi-Service AI Infrastructure

- **Repo:** github.com/ETcodin/cyber-squire1
- **Stack:** AWS EC2 t3.xlarge (16GB), Docker Compose 7 containers, PostgreSQL 16, n8n, Ollama + Qwen 2.5:7b, Faster-Whisper, Cloudflare Tunnel
- **Config:** `COREDIRECTIVE_ENGINE/docker-compose.yaml`
- **Highlight:** Full production stack on a single EC2 with zero-trust networking

### Project 2: Master Orchestrator -- 17-Service Automation Hub

- **What:** n8n webhook-driven orchestrator connecting PostgreSQL, Telegram, GitHub, Google Workspace (Drive, Sheets, Docs, Slides, Tasks, Gmail), Perplexity, Ollama, Cloudflare, Notion, Tavily, Gumroad, Excel
- **Config:** `COREDIRECTIVE_ENGINE/workflow_supervisor_agent.json`
- **Highlight:** Single webhook endpoint routes to 17 different service integrations

### Project 3: AI Voice Pipeline

- **What:** Faster-Whisper STT feeding Ollama/Qwen for AI processing, Telegram bot interface
- **Highlight:** Local inference (zero API costs), real-time voice transcription

### Project 4: OpenClaw Gateway -- Multi-Model AI Routing

- **What:** Gateway routing between Claude Sonnet/Opus with Telegram bot frontend
- **Highlight:** Autonomous AI agent with integrated tool use

## Case Study Template

For each project, generate:

```markdown
## [Project Name]

### Problem
What challenge drove this? (1-2 sentences)

### Solution
What was built and how? Architecture overview. (3-5 sentences)

### Architecture
Component diagram description: services, ports, connections, data flow.
Reference actual docker-compose or workflow config for accuracy.

### Key Decisions
2-3 technical choices and rationale.
Example: "Chose Ollama over API-based LLMs to eliminate per-token costs while maintaining 7B parameter quality"

### Results
Quantifiable outcomes: uptime, cost savings, services integrated, automation metrics.

### Tech Stack
Bullet list of all technologies.
```

## Output Options

- **Markdown:** Write to file for GitHub Pages or README
- **HTML:** Clean, responsive single-page portfolio
- **Google Doc:** Create via `docs` tool for easy sharing/editing
- Send preview via Telegram `telegram` tool (chat_id: `6691629392`)

## Architecture Descriptions

When describing architecture, produce detailed text suitable for diagram tools (Mermaid, draw.io). Include: service names, ports, network topology, data flow direction, external integrations, container relationships.

## GitHub Integration

Use `github` tool to pull repo metadata: languages, commit activity, stars, README content. Use this to enrich case studies with live data.
