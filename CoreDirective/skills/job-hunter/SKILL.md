---
name: job-hunter
description: Search job boards for DevOps/Cloud/AI roles and deliver scored daily digests via Telegram
---

# Job Hunter

Job search agent for a DevOps/Cloud/AI engineer in Atlanta (remote-friendly).

## Target Profile

- **Stack:** AWS (EC2, IAM, VPC, CloudFront), Docker, Terraform, PostgreSQL, Python, n8n, Cloudflare, Ollama, Whisper, LLM orchestration
- **Location:** Atlanta GA or Remote US
- **Titles:** DevOps Engineer, Cloud Engineer, Platform Engineer, SRE, AI/ML Ops Engineer, Automation Engineer, Infrastructure Engineer

## Procedure

### 1. Search Jobs

Use `web_search` to query across multiple sources:

```
site:linkedin.com/jobs "DevOps" OR "Cloud Engineer" OR "Platform Engineer" remote OR Atlanta
site:indeed.com "DevOps" OR "Cloud Engineer" AWS Docker remote
site:glassdoor.com DevOps cloud engineer Atlanta OR remote
site:remoteok.com devops OR cloud OR infrastructure
site:weworkremotely.com devops OR cloud OR sre
"AI automation" engineer remote job posting 2026
"n8n" OR "workflow automation" engineer job
Terraform AWS Docker engineer Atlanta OR remote
```

Use `web_fetch` to pull full job descriptions from promising results.

### 2. Score Each Posting (1-10)

Extract per result:

| Field | Source |
|-------|--------|
| Company | Job posting |
| Title | Job posting |
| Location | Remote / Hybrid / Atlanta |
| Salary Range | Posted or estimate via Glassdoor |
| Link | Direct URL |
| Match Score | Count of matching skills / total required skills |
| Key Gaps | Skills they want that user lacks |

Scoring: 8-10 = strong (>70% skill overlap), 5-7 = moderate, <5 = stretch.

### 3. Format Output

```
## Job Hunt Digest - [DATE]

### Top Matches (8-10)
1. **[Title] @ [Company]** - [Salary] - [Remote/Atlanta]
   Match: [X]/10 | [link]
   Skills hit: [matching skills]
   Gap: [missing skills if any]

### Worth Applying (5-7)
[same format]

### Stretch Roles
[same format]

Action items: Apply to top 3 today.
```

### 4. Deliver

- Send digest via Telegram using `telegram` tool (chat_id: `6691629392`)
- Save full results to Google Sheets via `sheets` tool
- Sheet columns: Date Found | Company | Title | Salary | Location | Match Score | Link | Status | Applied Date | Notes

### 5. Daily Cadence

When running daily:
- Deduplicate against previous entries in Sheets
- Only surface NEW postings in the digest
- Flag postings older than 14 days as stale
- Highlight any postings with deadlines approaching
