---
name: expense-tracker
description: Track spending with Microsoft Excel. Budget alerts via Telegram while unemployed.
---

# Expense Tracker

Uses Microsoft Excel via MASTER_ORCHESTRATOR (`excel` action, credential ID: `S6lyH6ffpNn5NFHf`).

## Spreadsheet Setup

Create or use existing workbook with these sheets:

**Sheet: Transactions**
| Date | Category | Description | Amount | Payment Method | Notes |
|------|----------|-------------|--------|----------------|-------|

**Sheet: Budget**
| Category | Monthly Limit | Spent | Remaining | Status |
|----------|--------------|-------|-----------|--------|

**Sheet: Summary**
| Month | Total Income | Total Expenses | Net | Savings Rate |
|-------|-------------|----------------|-----|-------------|

## Categories

Essential: Rent, Utilities, Groceries, Insurance, Phone, Internet, Gas/Transport
Discretionary: Dining Out, Entertainment, Subscriptions, Shopping, Personal Care
Business: Software, Domains, AWS/Cloud, Marketing, Professional Development

## Adding Expenses

When user says "spent $X on Y":
1. Parse amount, category, description
2. Add row to Transactions sheet via `excel` action
3. Update Budget sheet totals
4. If category exceeds 80% of monthly limit → warn via Telegram
5. If category exceeds 100% → alert via Telegram with remaining overall budget

## Weekly Summary (Cron)

Use `cron` tool — every Sunday 7pm:
1. Pull week's transactions from Excel
2. Calculate: total spent, top 3 categories, biggest single expense
3. Compare to monthly budget pace (are you on track?)
4. Send summary via Telegram message

Format:
```
Weekly Spend: $XXX
Pace: $XXX / $XXX budget (XX%)
Top: Groceries $XX, Gas $XX, Subscriptions $XX
⚠️ Over budget: [category] by $XX
```

## Monthly Report

On the 1st of each month:
1. Lock previous month's data
2. Generate summary: income vs expenses, category breakdown, month-over-month trend
3. Update Summary sheet
4. Send full report via Telegram

## Quick Commands

- "How much have I spent this week?" → query Transactions, sum current week
- "Budget check" → show all categories with remaining amounts
- "Add expense: $45 groceries Kroger" → log to Transactions
- "What am I spending most on?" → top 5 categories this month
- "Cancel [subscription name]" → flag it, remind to actually cancel, remove from recurring
