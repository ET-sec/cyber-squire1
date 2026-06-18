---
name: freelance-finder
description: Search freelance platforms for matching DevOps/automation gigs and draft proposals
---

# Freelance Finder

## When to Use
User asks to find gigs, search freelance work, check job boards, or draft proposals.

## Search Procedure

1. **Search platforms** using `web_search`:
   - `site:upwork.com "aws" OR "devops" OR "n8n" OR "docker" OR "python automation"`
   - `site:fiverr.com buyer-requests aws devops automation`
   - `site:toptal.com/developers aws infrastructure`
   - `site:freelancer.com/projects aws docker n8n`

2. **Filter:** $50+/hr or $500+ fixed, remote only. Primary: AWS, Docker, n8n, Python, Terraform, CI/CD, PostgreSQL. Secondary: InDesign, DaVinci Resolve, data viz.

3. **Score (1-5):** 5=exact stack, 4=strong overlap, 3=partial, <3=skip.

## Proposal Templates

**n8n/Automation:** "I build production n8n pipelines on AWS with Docker, PostgreSQL, and AI (Ollama, Whisper, Claude). 6+ active workflows for Telegram bots, content pipelines, multi-service orchestration."

**AWS/DevOps:** "I manage AWS infra (EC2, Cloudflare tunnels, Docker Compose) with Terraform. Production: PostgreSQL, n8n, Ollama, Whisper on t3.xlarge, zero-trust access."

**AI Pipeline:** "End-to-end AI pipelines: local inference (Ollama/Qwen), voice (Faster-Whisper), Claude via gateway. Docker Compose + n8n orchestration."

## Track in Google Sheets
POST `https://n8n.tigouetheory.com/webhook/master-cmd`:
```json
{"action":"sheets","spreadsheet_id":"FREELANCE_TRACKER","sheet_name":"Applications","data":{"date":"YYYY-MM-DD","platform":"...","title":"...","budget":"...","score":"...","status":"Applied","url":"..."}}
```

## Alert on High-Match
Score 4-5: Telegram immediately:
```json
{"action":"telegram","chat_id":"6691629392","text":"HIGH-MATCH GIG (X/5)\nPlatform: ...\nBudget: ...\nTitle: ...\nURL: ..."}
```
