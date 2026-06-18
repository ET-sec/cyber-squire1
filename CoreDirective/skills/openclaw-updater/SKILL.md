---
name: openclaw-updater
description: Check for OpenClaw updates, summarize changelogs, and rate importance
---

# OpenClaw Updater

## When to Use
User asks about OpenClaw updates, new versions, or when doing weekly maintenance.

## Current Version
- OpenClaw Gateway: **v2026.2.6**
- Container: `openclaw-gateway` (standalone, outside docker-compose)
- Config: `/home/ec2-user/openclaw/config/openclaw.json`

## Check for Updates

1. Search for latest release:
```
web_search: "openclaw release latest 2026 site:github.com/openclaw/openclaw"
```

2. Or fetch releases page:
```
web_fetch: https://github.com/openclaw/openclaw/releases
```

3. Compare version numbers. If newer exists, proceed to analysis.

## Changelog Analysis

For each new version, summarize:
- **Security fixes:** Urgent -- flag for immediate update
- **Bug fixes:** Important -- schedule update within a week
- **New features:** Nice-to-have -- update at convenience
- **Breaking changes:** Caution -- read migration guide first

## Importance Rating

| Rating | Criteria | Action |
|--------|----------|--------|
| URGENT | Security vulnerability fix | Update ASAP, alert user |
| HIGH | Bug fix affecting current usage | Update this week |
| MEDIUM | New useful feature | Update when convenient |
| LOW | Minor changes, no impact | Note for next maintenance window |

## Alert Format

Weekly check (use `cron` tool, Sundays):
```json
{"action": "telegram", "chat_id": "6691629392", "text": "OPENCLAW UPDATE CHECK\nCurrent: v2026.2.6\nLatest: vX.X.X\nImportance: HIGH/MEDIUM/LOW\nKey changes:\n- ...\n- ...\nAction: [Update recommended / No action needed]"}
```

## DO NOT Auto-Update
Never update automatically. Only notify the user and let them decide when to update. Updates may require:
- Config migration
- Skill compatibility checks
- Downtime for the gateway
- Mac node re-pairing
