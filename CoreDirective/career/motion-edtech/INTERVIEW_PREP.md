\# Motion EdTech — Senior Cloud Security Engineer

**Recruiter:** Shikha Sable (Motion Recruitment IT Recruiter, new)
**Contact:** shikhasable09@gmail.com | linkedin.com/in/shikhasable
**Outreach:** 2026-05-18 5:29 PM ET LinkedIn DM
**End client:** Likely Cambium Assessment (highest-probability hypothesis per JD wording match: 131M tests, 15M students, AWS-native)
**Role:** Senior Cloud Security Engineer | C2H W2 | 100% Remote (EST/CST) | 1-3x/yr travel
**Foundation used:** Cloud_Security_Engineer
**Resume:** Emmanuel_Tigoue_Cloud_Security_Engineer_Motion_EdTech.docx (built 2026-05-19, all 11 QC gates passed)

## Scorecard (post-tailor)

| Dimension | Before | After |
|---|---|---|
| ATS keyword match | 52% (13/25) | 88% (22/25) |
| Hiring manager verdict | "Maybe, AWS depth on faith" | "Yes call, $70-$85/hr W2" |
| Peer credibility | "Mid dressed as Senior" | "Mid+ realistic if screen weights detection eng + IaC" |
| One-page fit | PASS | PASS (PDF 1 page exactly) |
| Title vs LinkedIn | Mismatch (Cloud vs AI) | Aligned (AI Security Engineer at CoreDirective) |
| Blended offer probability | 25% | 50% |

## Pre-call cheat card

**Opening line:**
"Thanks for the outreach Shikha. The role maps to what I am doing now at CoreDirective. Before we get into rate, who is the end client and what does the technical screen look like?"

**3 killer talking points:**
1. Detection engineering: cut Datadog alerts from 200+ to 12 daily through tuning. Falco eBPF rules mapped to MITRE ATT&CK. That is the EdTech assessment platform job in one bullet.
2. CI/CD security: Semgrep, Trivy, Gitleaks, Checkov, OPA Conftest against Terraform AND CloudFormation, Cosign signing, Syft SBOMs, OWASP ZAP DAST. Mature pipeline, not a checklist.
3. SIEM history: built Splunk at Texaco from zero, cut MTTD from 48 hours to 4 on a PCI environment. Sumo Logic syntax is the same shape; ramp is fast.

**Honest answers for gaps:**
- AWS CDK: "I am Terraform-first in production. I have read the CDK constructs library and shipped CloudFormation, so the model is familiar. Ramp on TypeScript stacks is one weekend."
- JavaScript: "Primary scripting is Python and Bash. JavaScript shows up in my n8n workflows. Not the language I would pick for a fresh automation, but I can read and ship it."
- Sumo Logic: "Datadog is my daily SIEM. I have the Splunk SPL background. Sumo Logic search syntax is a 4-hour ramp."

**4 questions to ask Shikha:**
1. Who is the end client? Is this Cambium Assessment?
2. Who at Motion owns the account relationship? (Get the senior AM name. Shikha is new; the AM is who actually closes.)
3. What is the contract length and conversion path?
4. What does the technical screen look like — live coding, whiteboard, log analysis, or all three?

**Rate play:**
- Anchor: $85/hr W2
- Floor: $75/hr W2
- Walk: below $75. At $75, GA net annualized is roughly equivalent to OneDigital FTE at $125k.
- Shikha is new and likely passes verbatim. Anchor confidently.

## Tech screen study list (8-12 hours pre-screen)

### Tier 1 — must know (4 hours)
- **CloudTrail forensics:** Walk a sample CloudTrail log, find IAM privilege escalation. Read 3 AWS security blog incident write-ups. Familiar with `eventName`, `userIdentity.type`, `requestParameters`, `responseElements`.
- **IAM Condition keys cold:** `aws:SourceIp`, `aws:MultiFactorAuthPresent`, `aws:PrincipalTag`, `aws:RequestTag`. Write a deny policy from memory.
- **VPC Flow Logs:** know the format, know how to spot exfil patterns (high bytes-out on unusual ports, off-hours flows to non-corp IPs).

### Tier 2 — high probability (4 hours)
- **AWS CDK basics:** TypeScript `Stack`, `Construct`, common L2 constructs for VPC, IAM, S3, KMS. `cdk synth`, `cdk diff`, `cdk deploy`. Spend two hours in the CDK Workshop labs.
- **CloudFormation:** review intrinsic functions (`!Ref`, `!Sub`, `!GetAtt`), drift detection, StackSet basics.
- **Sumo Logic search syntax:** parse, where, count, timeslice. Two hours through their free training.
- **Detection-as-code:** Sumo Logic Cloud SIEM rules in YAML, Sigma rule format basics.

### Tier 3 — nice to have (2 hours)
- Purple team mindset: read one Atomic Red Team test, walk through detection coverage.
- GuardDuty findings taxonomy, Security Hub finding aggregation, EventBridge rules to ship findings.

### Honest heat map vs Emmanuel's experience
| Topic | Color | Notes |
|---|---|---|
| CloudTrail / IAM / VPC Flow Logs | Green | Real production-equivalent in CoreDirective lab |
| Detection engineering (Falco, Datadog) | Green | 200+ to 12 alert cut is real |
| CI/CD security gates | Green | Cleanest section of the resume |
| Splunk SIEM | Green | Texaco 48h to 4h MTTD cut |
| Sumo Logic | Yellow | Same shape as Splunk, 4-hour ramp |
| AWS CDK | Yellow | Terraform-first; CDK is read-only |
| CloudFormation | Yellow | OPA Conftest gates it, never authored at scale |
| JavaScript / Node.js | Red | n8n only; do not lean on this |
| Purple team formal | Yellow | Validation tests against AI runtime are the closest |

## Red flags to avoid
- Do NOT claim CDK production depth. Do NOT claim heavy Sumo Logic.
- Do NOT inflate JavaScript.
- Do NOT position as founder of CoreDirective. Employee.
- Never frame as "pivoting" or "transitioning" or "breaking into" cloud security. Claim Senior Cloud Security Engineer directly.

## Files
- Resume DOCX: `/Users/et/Documents/Resumes/resume variations/Emmanuel_Tigoue_Cloud_Security_Engineer_Motion_EdTech.docx`
- Resume PDF: `/Users/et/Documents/Resumes/resume variations/Emmanuel_Tigoue_Cloud_Security_Engineer_Motion_EdTech.pdf`
- iCloud mirror: `/Users/et/Library/Mobile Documents/com~apple~CloudDocs/resume variations/`
- Recruiter-clean: `/Users/et/Downloads/Emmanuel_Tigoue_Cloud_Security_Engineer.{docx,pdf}`
- Email draft: `/tmp/motion_edtech_email.txt` (also open in TextEdit)
- JD: `/tmp/motion_edtech_jd.txt`
- Tracker tab: `Motion_EdTech` (sheetId 1063946562) — Dashboard priority 11, Comp_Analysis rank 4
