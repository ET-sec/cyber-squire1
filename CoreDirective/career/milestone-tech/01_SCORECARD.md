# Scorecard - Milestone Tech AI Security Engineer/Architect

## Before vs After (foundation v. tailored)

| Dimension | Foundation | Tailored | Notes |
|---|---|---|---|
| ATS keyword match | 58% | ~85% | Injected: AI-SPM, AI Runtime Protection, agentic, secure-by-design, EU AI Act, GDPR, Terraform (named), Bedrock (in scan zone), AI Incident Response |
| First 4 lines AWS visibility | Bedrock at line 28 only | Bedrock in scan zone (lead bullet) | Recruiter sees AWS Bedrock without scrolling |
| Skills line items | 21 (bloated) | 8 (intentional) | Bedrock Guardrails, Databricks Unity Catalog, MLflow Registry, ChatGPT Enterprise, Promptfoo, Lakera Guard, Wiz AI-SPM, Vertex AI |
| AWS implementation tenure (4-6 yr bar) | Implicit, weak | Bedrock + Terraform (16 modules) + 30+ resources surfaced | Still vulnerable in screen, see cheat card pivot |
| Public artifact proof | Not framed | Three real harnesses cited (Langfuse eval, OPA Rego, FastMCP, budget_guard, sanitize_output) | Public repo at github.com/ET-sec/cyber-squire1 if asked |

## Verdicts (from 6 research agents)

- **Hiring manager:** SUBMIT WITH CAVEAT. AI security depth is rare, AWS implementation gap is the only risk.
- **Senior peer (BS detector):** AI security half is real and peer-respectable. AWS/Databricks/MLflow half is legitimately bolted on for this JD. Honest depth check on Langfuse harness, OPA Rego, FastMCP server, budget_guard, sanitize_output: **production-grade for a small team**, peer would respect.
- **Competition analysis:** $70/hr filters out top tier. Pool is mostly mid-career cloud security people stretching. Emmanuel's public artifact trail puts him in the top 5%.
- **ATS audit:** All top-15 missing keywords now injected through real Phase 19 work, no fabrication.
- **Tech screen prep:** Q4 (agentic prompt-injection defense) is Emmanuel's strongest. Q1 (Bedrock IAM/KMS/VPC depth) and Q2 (Databricks Unity Catalog production) are weakest.
- **Company intel:** Milestone IT services firm, owned by H.I.G. Capital. Most probable end client: Meta. Recruiter Elena Novo runs generalist tech contract desk.

## Blended offer probability
- Recruiter screen (Elena): **85%** - she will pass through if rate aligns
- End-client tech screen: **55%** - depends entirely on whether they prioritize AI security depth (high) over AWS years (medium gap)
- Offer at counter rate ($95-$110): **35%** at $95, **20%** at $110
- Offer at original $70: **65%** if they like the screen

## Rate strategy
1. Anchor at $95-$110 in first reply (sent in email draft)
2. Floor walk-away $85 W2
3. If they push back, pivot to $90 + start-date-flex + early renewal review
4. Do NOT accept $70 unless they are Meta and the team is exceptional - rate is below market by ~$25/hr for the named scope

## Key risk
AWS production tenure. Resume now SHOWS Bedrock + 30+ AWS resources + Terraform, but a strict screener will probe IAM/KMS/VPC depth. Cheat card has the pivot scripts.
