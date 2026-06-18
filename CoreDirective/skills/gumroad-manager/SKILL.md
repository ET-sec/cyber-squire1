---
name: gumroad-manager
description: Manage Gumroad digital products, track sales, and generate promotional content
---

# Gumroad Manager

## When to Use
User asks about Gumroad products, sales, revenue, product ideas, or digital product marketing.

## Product Ideas

| Product | Type | Price Range |
|---------|------|-------------|
| n8n Workflow Templates (Telegram bot, content pipeline) | JSON + docs | $19-49 |
| DaVinci Resolve Presets (color grades, transitions) | .drp/.setting | $9-29 |
| InDesign Templates (portfolios, proposals) | .idml + fonts | $15-39 |
| AWS Deployment Guides (Docker+n8n on EC2) | PDF + Terraform | $29-79 |
| ADHD Productivity System (n8n + Google Tasks) | Template bundle | $19-39 |

## Check Sales & Products

Use `web_fetch` on Gumroad API or MASTER_ORCHESTRATOR:
```json
{"action": "gumroad"}
```

## Create Product Listing

Structure every listing with:
1. **Title:** Clear, keyword-rich (e.g., "Production n8n Telegram Bot Workflow Template")
2. **Description:** Problem it solves, what's included, tech requirements
3. **Price:** Based on complexity and market research
4. **Tags:** 5-8 relevant tags for discoverability
5. **Thumbnail:** Describe ideal thumbnail for user to create

## Promotional Content

Generate for each platform:
- **Twitter/X:** 280-char hook + link, focus on pain point solved
- **LinkedIn:** Professional angle, ROI focus, 3-paragraph format
- **Reddit:** Value-first post for r/n8n, r/selfhosted, r/aws, r/devops (no direct selling)

## Revenue Tracking

Weekly summary via Telegram:
```json
{"action": "telegram", "chat_id": "6691629392", "text": "GUMROAD WEEKLY\nProducts: X\nSales this week: X\nRevenue: $X\nTop seller: ..."}
```

## Launch Checklist
1. Product file tested and working
2. README/guide included
3. Thumbnail created
4. Description written with keywords
5. Price set
6. Promo posts drafted for 3 platforms
7. Posted to relevant subreddits/communities
