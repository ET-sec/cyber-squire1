---
name: cold-outreach-drafter
description: Research companies and draft personalized outreach emails to hiring managers with send and tracking
---

# Cold Outreach Drafter

Research target companies, draft personalized emails to hiring managers and CTOs, send via Gmail, and track all outreach.

## Procedure

### 1. Research Target Company

Use `tavily` tool (depth: advanced) and/or `perplexity` tool to gather:
- Company size, funding stage, recent news
- Tech stack (from job postings, engineering blog, GitHub org)
- Current hiring needs and engineering team structure
- Key contacts: VP Engineering, CTO, hiring manager names
- Recent challenges or initiatives where the user's skills apply

### 2. Choose Template and Draft

**Template A: Direct Application (no posted role)**

Subject: [Specific skill] engineer -- saw your [specific company detail]

Body (under 150 words):
- 1 sentence: what caught your attention about their company (specific!)
- 1 sentence: your relevant project ("built a multi-service AI orchestration platform on AWS with Docker, handling 17 integrated services")
- 1 sentence: connecting your work to their needs
- 1 sentence: specific technical challenge you solved relevant to them
- CTA: "Would you be open to a 15-minute call this week?"

**Template B: Warm Networking**

Subject: Fellow [DevOps/Cloud] engineer -- quick question about [company]

Body: How you found them, what interests you about their work, your relevant credential, offer to share knowledge in return, ask for 15-min virtual coffee.

**Template C: Informational Interview**

Subject: Admire [company]'s approach to [specific tech]

Body: Genuine compliment about specific technical work, your overlapping expertise, one specific question about their domain, low-pressure ask.

### 3. Customization Rules

- NEVER use: "passionate about," "team player," "synergy," "leverage," "rockstar"
- ALWAYS reference something specific (blog post, product feature, funding round, GitHub repo)
- Under 150 words total
- One clear call to action
- Professional but human tone

### 4. Send via Gmail

Use `gmail` tool:
- to: [recipient email]
- subject: [customized subject line]
- text: [drafted email body]

Always confirm with user before sending.

### 5. Track in Google Sheets

Use `sheets` tool to log every outreach:
- Columns: Date Sent | Company | Contact Name | Contact Title | Email | Status | Follow-Up Date | Response | Notes
- Set follow-up date to 5 business days after send date

### 6. Follow-Up System

After 5 business days with no response:
- Send Telegram reminder via `telegram` tool (chat_id: `6691629392`):
  "Follow up with [Name] at [Company] -- sent [date], no response yet"
- Draft short follow-up email: 2-3 sentences, reference original, add new value or relevant update

### 7. Batch Mode

When given a list of target companies:
1. Research all companies in sequence
2. Draft all emails
3. Present ALL drafts for review before sending any
4. Send only after user approval
5. Log all to Sheets at once
