# job-digest

Cybersecurity job posting scraper, scorer, and daily digest generator.

Scrapes multiple job sources, scores postings 0-100 based on your qualifications, deduplicates with SQLite, and sends a filtered digest via webhook or prints to terminal.

## Installation

```bash
cd builds/job-digest
pip install -e .
```

Or without installing:

```bash
pip install -r requirements.txt
python -m job_digest
```

## Usage

```bash
# Run and print digest to terminal
job-digest

# Run and send to webhook
job-digest --send --webhook "https://n8n.tigouetheory.com/webhook/job-digest"

# View all past postings
job-digest history

# Mark a posting as applied (by database ID)
job-digest applied 42

# View application tracker
job-digest tracker

# View statistics
job-digest stats

# Force re-scrape (show all, not just new)
job-digest --fresh

# Verbose logging
job-digest -v
```

## Configuration

Edit `config.yaml` to customize:

- **search_terms**: Keywords to search across all job boards
- **locations**: Target locations (supports "Remote")
- **my_certs**: Your certifications for scoring matches
- **company_pages**: Direct company career pages to scrape
- **webhook_url**: Default webhook endpoint for digest delivery
- **scoring**: Weight configuration for the scoring algorithm
- **usajobs**: USAJobs API settings (email for User-Agent header)
- **rate_limit**: Delay and retry settings for HTTP requests

## Job Sources

| Source | Method | Notes |
|--------|--------|-------|
| Indeed | HTML scraping | Requires rotating User-Agents |
| Dice | HTML scraping | Handles shadow DOM fallbacks |
| USAJobs | REST API | Free, no key needed (just email in User-Agent) |
| LinkedIn | Public listings | May be blocked; handles gracefully |
| Company Pages | HTML scraping | Truist, Southern Company, EY, Insight Global |

## Scoring Algorithm (0-100)

| Component | Max Points | Logic |
|-----------|-----------|-------|
| Cert Match | 40 | +10 per matching cert found in posting |
| Salary | 20 | 20 if $90K+, 10 if $70-90K, 0 otherwise |
| Location | 15 | 15 if Atlanta/Remote, 10 if GA, 5 if Southeast |
| Experience | 15 | 15 if 0-3yr, 10 if 3-5yr, 5 if 5-7yr, 0 if 7+ |
| Clearance | 10 | 10 if none required, 5 if preferred, 0 if required |

Only postings scoring 50+ are included in the digest (configurable).

## Cron Setup

For daily runs at 8 AM Eastern:

```bash
# See cron_entry.txt for full examples
crontab -e
# Add:
TZ=America/New_York
0 8 * * * cd /path/to/job-digest && python -m job_digest --send >> /var/log/job-digest.log 2>&1
```

## Database

SQLite database (`job_digest.db`) stores all scraped postings for:
- Deduplication across runs (by source+ID or fuzzy title+company match)
- Application tracking (mark postings as applied)
- Historical analysis

Override database path with `JOB_DIGEST_DB` environment variable.

## Webhook Payload

When `--send` is used, the webhook receives:

```json
{
  "text": "DAILY JOB DIGEST -- February 13, 2026\n...",
  "postings": [
    {
      "id": 1,
      "source": "usajobs",
      "title": "Cybersecurity Analyst",
      "company": "DHS",
      "location": "Atlanta, GA",
      "salary": "$95,000-$120,000",
      "url": "https://...",
      "score": 85,
      "matched_certs": ["Security+", "CASP+"],
      "date_found": "2026-02-13"
    }
  ],
  "count": 7
}
```
