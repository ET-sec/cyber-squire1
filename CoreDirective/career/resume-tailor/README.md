# resume-tailor

CLI tool that takes a job posting URL and generates a tailored resume, cover letter, and company research brief.

## Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Set your Anthropic API key
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

```bash
# Basic usage with a job posting URL
resume-tailor --url "https://example.com/jobs/security-engineer"

# Custom resume and output directory
resume-tailor --url "https://example.com/jobs/123" --resume ./my_resume.json --output ./applications/

# Run as module
python -m resume_tailor.cli --url "https://example.com/jobs/123"
```

## What It Does

1. **Scrapes** the job posting (title, company, skills, certs, responsibilities)
2. **Analyzes** the posting against your master resume data
3. **Picks** the best resume variant based on keyword matching
4. **Generates** (via Claude API):
   - Tailored resume with rewritten bullets and reordered sections
   - Cover letter (250-350 words) mapping your qualifications to their requirements
   - Company research brief with interview talking points

## Output

Files are saved to the output directory as:
- `{company}_{role}_resume.md`
- `{company}_{role}_cover_letter.md`
- `{company}_{role}_research.md`

## Master Resume

Edit `data/master_resume.json` with your information. The JSON includes:
- Contact info and links
- Certifications with issuer and notes
- Education details
- Technical skills by category
- Multiple resume variants (different bullet sets for different role types)
- Prior work experience
- Projects and DoD compliance data

## Supported Job Sites

- Indeed
- Dice
- LinkedIn (public/guest view, limited)
- Generic company career pages
- Any page with JSON-LD JobPosting schema

Sites that require JavaScript rendering or authentication will show a warning and attempt to extract whatever is available from the static HTML.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key for Claude access |
