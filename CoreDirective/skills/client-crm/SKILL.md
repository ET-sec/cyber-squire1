---
name: client-crm
description: Simple CRM using Google Sheets to track leads, contacts, and follow-ups
---

# Client CRM

## When to Use
User asks about leads, clients, contacts, follow-ups, pipeline, or CRM management.

## Sheet Structure

**Sheet: Pipeline**
| Column | Content |
|--------|---------|
| A: Date Added | YYYY-MM-DD |
| B: Name | Contact full name |
| C: Company | Company/org name |
| D: Email | Contact email |
| E: Source | Where lead came from (Upwork, referral, cold, etc.) |
| F: Stage | Lead / Contact Made / Proposal Sent / Negotiating / Won / Lost |
| G: Deal Value | Estimated $ value |
| H: Next Action | What to do next |
| I: Follow-up Date | YYYY-MM-DD |
| J: Notes | Interaction log with timestamps |

## Operations via MASTER_ORCHESTRATOR

**Add lead:**
```json
{"action": "sheets", "spreadsheet_id": "CRM_SHEET_ID", "sheet_name": "Pipeline", "data": {"date": "2026-02-08", "name": "...", "company": "...", "stage": "Lead", "next_action": "...", "follow_up": "2026-02-11"}}
```

**Update stage:**
Find row by name, update Stage column and add timestamped note.

**Log interaction:**
Append to Notes column: `[YYYY-MM-DD HH:MM] Called, discussed scope. Moving to Proposal Sent.`

## Pipeline Stages
```
Lead --> Contact Made --> Proposal Sent --> Negotiating --> Won
                                                       \-> Lost
```

## Follow-up Reminders

Use `cron` tool: daily at 9 AM, check for follow-ups due today or overdue.

Send Telegram reminder:
```json
{"action": "telegram", "chat_id": "6691629392", "text": "CRM FOLLOW-UP DUE\nName: ...\nCompany: ...\nStage: ...\nAction: ...\nOverdue: X days"}
```

## Weekly Pipeline Report

Every Sunday, generate summary:
- Total leads in pipeline
- Leads by stage (count + total value)
- Follow-ups due this week
- Deals won/lost this month
- Conversion rate (Won / Total closed)

Send via Telegram as formatted summary.
