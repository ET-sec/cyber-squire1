---
name: resume-tailor
description: Tailor resumes to specific job postings with ATS optimization and cover letter talking points
---

# Resume Tailor

Takes a job posting and the user's base resume, produces a tailored version optimized for ATS and human reviewers.

## Inputs

- **Job posting:** URL (use `web_fetch`) or pasted text
- **Base resume:** File from disk or pasted text

## User's Skill Inventory

- AWS EC2, VPC, IAM, CloudFront, S3 -- production infrastructure management
- Docker multi-service orchestration (7+ containers, compose, networking)
- Terraform IaC for AWS provisioning
- PostgreSQL database administration
- Python scripting and automation
- n8n workflow automation (17-service master orchestrator)
- AI/ML pipeline deployment (Ollama, Whisper, LLM routing)
- Cloudflare zero-trust tunneling, DNS, networking
- CI/CD pipeline design
- Linux system administration
- Video production (DaVinci Resolve)
- Print/digital design (InDesign, IDML generation)

## Procedure

### 1. Analyze Job Posting

Extract:
- Hard requirements (must-have skills)
- Preferred skills (nice-to-haves)
- Years of experience needed
- Industry/domain context
- Keywords repeated 2+ times (ATS trigger words)

### 2. Gap Analysis

Create a three-column comparison: Required | User Has | Gap. Identify which skills to emphasize and which gaps to address or reframe.

### 3. Generate Tailored Resume

- Reorder experience bullets to lead with most relevant skills
- Mirror the job posting's exact language and keywords
- Quantify achievements: "orchestrated 7-container Docker stack," "automated 17-service pipeline," "managed production infrastructure serving N requests"
- Keep to 1-2 pages max
- Remove or minimize irrelevant experience

### 4. ATS Optimization Checklist

- Standard section headers: Experience, Skills, Education, Projects
- No tables, columns, graphics, or headers/footers with critical info
- Exact keyword matches from the posting included
- Acronyms spelled out once: "Amazon Web Services (AWS)"
- Output as .docx or clean PDF (no fancy templates)

### 5. Cover Letter Talking Points

Generate 3-4 bullet points connecting specific user projects to job requirements:
- The problem solved
- The tech used (matching their stack keywords)
- The measurable result

### 6. Output

- Write tailored resume to file or create via `docs` tool (Google Docs)
- Send change summary via Telegram `telegram` tool (chat_id: `6691629392`)
- List skills to study/upskill for any identified gaps
