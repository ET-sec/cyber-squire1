---
name: homework-scheduler
description: Track assignments with ADHD-friendly chunking, reminders, and Pomodoro planning
---

# Homework Scheduler

## When to Use
User mentions homework, assignments, studying, due dates, school tasks, or needs help organizing academic work.

## Add Assignment

Track via Google Tasks or Sheets. For Tasks (preferred):
```json
{"action": "tasks", "operation": "create", "title": "MATH 301 - Problem Set 5", "notes": "Ch 7 problems 1-20, show work", "due": "2026-02-15"}
```

Or Sheets for richer tracking:
```json
{"action": "sheets", "spreadsheet_id": "HOMEWORK_TRACKER", "sheet_name": "Assignments", "data": {"course": "...", "assignment": "...", "due": "YYYY-MM-DD", "weight": "X%", "status": "Not Started", "subtasks": "...", "estimated_hours": "X"}}
```

## ADHD-Friendly Chunking

Break every assignment into max 25-minute subtasks:
- **Essay (5 pages):** Outline (25min) -> Intro draft (25min) -> Body P1 (25min) -> Body P2 (25min) -> Body P3 (25min) -> Conclusion (25min) -> Edit (25min) -> Final proofread (25min)
- **Problem set (20 problems):** Group into sets of 5 -> 4 Pomodoro blocks
- **Reading (50 pages):** 10 pages per block -> 5 blocks with notes after each

Create subtasks in Google Tasks for each chunk.

## Reminder Schedule

Use `cron` tool for recurring checks. Per assignment:
- **3 days before due:** "Assignment X due in 3 days. Start if you haven't."
- **1 day before:** "Assignment X due TOMORROW. Status check."
- **Day of (9 AM):** "Assignment X due TODAY. Final push."

```json
{"action": "telegram", "chat_id": "6691629392", "text": "HOMEWORK REMINDER\nCourse: ...\nAssignment: ...\nDue: YYYY-MM-DD (X days)\nStatus: ...\nNext subtask: ..."}
```

## Pomodoro Sessions
- 25 min work -> 5 min break
- After 4 pomodoros -> 15-30 min longer break
- During breaks: stand up, stretch, water, NO screens
- Suggest specific subtask for each pomodoro

## Priority Matrix

Sort assignments by:
1. **Urgent + Important:** Due within 2 days, high grade weight
2. **Important + Not Urgent:** Due in 3-7 days, high weight
3. **Urgent + Not Important:** Due soon, low weight
4. **Neither:** Due 7+ days out, low weight

Always work on quadrant 1 first.

## Weekly Review (Sunday)

Generate summary:
- Assignments due this week
- Overdue items (escalate!)
- Upcoming deadlines next 2 weeks
- Completed this week (celebrate wins)
- Estimated hours needed this week

Send via Telegram as formatted checklist.
