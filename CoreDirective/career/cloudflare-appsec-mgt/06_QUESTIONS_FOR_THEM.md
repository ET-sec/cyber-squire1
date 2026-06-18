# 06_QUESTIONS_FOR_THEM — 3 Tiers

## Tier 1 — Must ask Matthew before submittal

1. Who is the end client?
2. What is the budgeted bill rate range?
3. Is this a true contract-to-hire with a defined conversion window, or open-ended contract?
4. What does the AppSec team own day-to-day inside Cloudflare: WAF tuning, page shield, API security, all of it?

## Tier 2 — Ask Matthew during the screen call

1. Mid or senior on the end client's org chart? (Matters for rate floor)
2. How many candidates are you submitting? (Gauges your odds)
3. What's the timeline, when does the client want someone to start?
4. Has the role been open long? (Long open = something is wrong)
5. Are they replacing someone, or is this a new headcount?
6. What's the team size in security? Reporting structure?
7. Do they require background check, drug test, or specific clearance?
8. Is the 1-day onsite a hard rule or flexible?
9. What's the interview process: phone, technical, panel, exec?
10. How does Brilliant handle benefits on W2 contracts? (Healthcare, PTO, holidays)

## Tier 3 — Ask the end client (HM round, if it happens)

### About Cloudflare posture
1. How many zones, accounts, or business units do you run on Cloudflare?
2. Are you on Free, Pro, Business, or Enterprise tier?
3. Do you use Cloudflare One (Access, Gateway, WARP, Tunnel)? At what depth?
4. Do you ship Workers in production for security purposes?
5. What's your DDoS playbook? Have you been hit?
6. Are WAF rules managed in dashboard or as code (Terraform, Wrangler, Pulumi)?
7. Do you Logpush to a SIEM? Which one, what fields, what sampling?
8. What's your false-positive rate on the OWASP Core Ruleset right now?

### About the team
1. Who's on the AppSec team and where do they live in the org?
2. Who decides WAF rule deployments, the team or a change board?
3. What's the on-call structure? Page volume?
4. What does the first 30 / 60 / 90 days look like for this role?
5. What's the biggest unsolved Cloudflare problem you'd want this person to attack first?

### About the contract
1. What's the conversion criteria? (Performance, headcount, budget?)
2. Has anyone in this contract slot ever converted to FTE before?
3. Does the contract include benefits, or W2 with Brilliant handling those?
4. Is the rate fixed or does it adjust at conversion?

### About the work
1. How is success measured at 90 days? At 6 months?
2. What's the current state of WAF tuning, bot management, API security? Where are the gaps?
3. Do you have an internal threat model for the public-facing application?
4. Who do I partner with on the infrastructure and application sides?
5. Is there a documented runbook for L7 DDoS response, or am I writing it?
