# Voya Lead AI Security Engineer — Pre-Call Cheat Card

## Opening line (if you speak first)
"I'm in the middle of this work right now at CoreDirective. The OpenClaw model gateway and the MCP skill catalog are the lab, prompt injection defenses and autonomy red-teaming are the day-to-day."

## 3 killer talking points

**1. The model gateway is the unit of work.** Not the SDK. Not the framework. Where prompts, tool calls, and credentials cross a trust boundary. That is what I threat modeled at OpenClaw, that is what Voya needs hardened at the AI Foundry layer.

**2. Adversarial testing as code, not as a quarterly audit.** Promptfoo eval harness in CI. Each push runs the prompt injection, jailbreak, exfiltration, excessive agency, and output leakage suite. Findings gate the release. That is the lead-level expectation in the JD, that is what I run today.

**3. GRC plus AI sec is the hybrid that financial services actually needs.** 57 sanitized GRC docs, AI Incident Response playbook in the bundle, NIST AI RMF tied to ISO 42001. The model risk partner on the panel needs a security IC who can speak governance evidence. I can.

## Honest answers for gaps

| Gap | Honest answer |
|---|---|
| Go production experience | "Intermediate at best. I would pick TypeScript on the live build. I will be up to ship-quality Go inside 60 days if that is the team's primary language." |
| Rust | "No production claim. Open to picking it up if the team uses it for the gateway." |
| Azure AI Foundry, Databricks production | "AWS plus DigitalOcean plus Cloudflare is my production stack. Bedrock and Vertex AI for inference. The threat model and the controls transfer directly to Foundry. The runtime details I would ramp in the first 30 days." |
| ERISA, retirement domain | "HIPAA, PCI, SOC 2, ISO 27001 are the regulatory adjacencies I have worked. ERISA fiduciary obligations on AI outputs would be new study, not new thinking." |

## 4 questions to ask the recruiter

1. Is this direct hire FTE, or contract-to-hire? (JD says FTE Regular Exempt, confirm)
2. What is the comp band for Lead / Staff IC on this req? (Wait for them to anchor)
3. Has this role been open before, and what made prior candidates fall short?
4. Hiring manager name and tenure? Who is the EADS leadership chain into Santhosh Keshavan?

## Rate play

- Do not anchor first. Let them give the band.
- If they push for your number: "I would want to see the full package, the equity / LTI structure, and the bonus target before naming a base. The right base depends on what the rest looks like."
- If they insist on a number: $200K base target, willing to discuss based on equity and bonus.
- Walk-away floor: $185K base.
- Never write a rate number in email. All rate talk on the call.

## Avoid

- Do NOT say "immediately available" or "ready to start"
- Do NOT pitch CoreDirective as a side project; it is the employer
- Do NOT volunteer that you are interviewing elsewhere unless they ask
- Do NOT mention the recent Voya layoff cadence on the recruiter call; save for HM round if relevant
- Do NOT claim Azure Foundry or ERISA experience you do not have
- Do NOT lead with the CISSP; lead with the AI security work
