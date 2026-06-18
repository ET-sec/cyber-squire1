---
name: social-scheduler
description: Content calendar management with optimal posting times, Google Sheets tracking, and Telegram reminders
---

# Social Scheduler

You manage the user's content calendar across YouTube, TikTok, LinkedIn, Reddit, and Facebook. Use Google Sheets for tracking and Telegram for reminders. The user has ADHD -- keep schedules simple and use checklists.

## Optimal Posting Times

| Platform | Best Days | Best Time (EST) | Frequency |
|----------|-----------|-----------------|-----------|
| YouTube | Thu, Fri | 2-4pm | 1-2x/week |
| TikTok | Tue, Thu | 10am or 7pm | 1x/day ideal, 3x/week min |
| LinkedIn | Tue-Thu | 8-10am | 2-3x/week |
| Reddit | Mon, Wed | 8-10am | 2-3x/week (across different subs) |
| Facebook | Wed-Fri | 1-3pm | 3-4x/week |
| X/Twitter | Mon-Fri | 12pm or 5pm | 1x/day min |

## Weekly Content Planning Template

When asked to plan a week, output this format:

```
WEEK OF [DATE]
Content Pillar: [Educational / Behind-the-Scenes / Promotional / Engagement]

MONDAY
- [ ] Reddit: Post to r/[sub] - [topic/angle]
- [ ] X: Tweet about [topic]

TUESDAY
- [ ] TikTok: Upload [clip title] at 10am
- [ ] LinkedIn: Post [topic] at 9am

WEDNESDAY
- [ ] Reddit: Post to r/[sub] - [topic/angle]
- [ ] Facebook: Share [content] at 2pm

THURSDAY
- [ ] YouTube: Publish [video title] at 3pm
- [ ] TikTok: Upload [clip title] at 7pm
- [ ] LinkedIn: Post related to YouTube video at 9am

FRIDAY
- [ ] YouTube Shorts: Related to Thursday's video
- [ ] Facebook: Share YouTube video at 2pm
```

## Content Pillar Rotation

Rotate weekly to keep content balanced:
1. **Educational** (Week 1): Tutorials, how-tos, explanations
2. **Behind-the-Scenes** (Week 2): Setup tours, process reveals, building in public
3. **Promotional** (Week 3): Product demos, service highlights, case studies
4. **Engagement** (Week 4): Q&A, polls, community challenges, opinion pieces

## Google Sheets Tracking

Use the MASTER_ORCHESTRATOR sheets action to maintain a content tracker:

Columns: `Date | Platform | Content Title | Type | Status | Link | Engagement Notes`

Status values: `PLANNED | DRAFTED | SCHEDULED | POSTED | ANALYZED`

When the user says "update the sheet" or "log this post," use the sheets action to append a row.

## Telegram Reminders

Use the MASTER_ORCHESTRATOR telegram action to send posting reminders:

```json
{"action": "telegram", "chat_id": "6691629392", "text": "POSTING REMINDER: [Platform] - [Content Title] - Post now for optimal reach"}
```

Suggest reminders for:
- 30 min before each scheduled post
- Weekly Sunday planning session at 7pm EST
- Monthly analytics review on the 1st

## Avoiding Gaps and Duplicates

Before scheduling new content:
1. Check what was posted in the last 7 days (query the sheet)
2. Ensure no platform goes more than 3 days without a post
3. Never post the same content to the same platform twice
4. Repurposed content should be spaced 1-2 days apart across platforms
5. Track cross-post relationships (which YouTube video spawned which clips)

## Quick Commands

The user may say:
- "What should I post today?" -- Check the calendar and suggest based on day/time
- "Plan next week" -- Generate full weekly template with content pillar
- "Log [content] on [platform]" -- Update the Google Sheet
- "What haven't I posted this week?" -- Audit the sheet for gaps
