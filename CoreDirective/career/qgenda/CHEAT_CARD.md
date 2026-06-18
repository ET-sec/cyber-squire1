# QGenda Pre-Call Cheat Card — Austin Nix

## Opening line

"Thanks for reaching out, Austin. I read the JD and the role lines up well with what I'm doing now: AWS security tooling, vuln management, HIPAA and SOC 2 control work, plus AI/ML governance. Happy to walk through the fit."

## 3 killer talking points

1. **CI/CD security at depth.** Not just "I used Snyk." Real pipeline ownership: SAST (Semgrep), SCA (Trivy), secrets (Gitleaks), IaC (OPA Conftest), signed artifacts (Cosign), SBOMs (Syft), admission control (OPA Gatekeeper for Kubernetes), DAST (OWASP ZAP). Blocks unsigned artifacts at merge. This maps 1:1 to the JD's SDLC integration ask.

2. **GRC translation muscle.** 49 documents, NIST 800-53 (169 controls), HIPAA, SOC 2, ISO 27001, FedRAMP moderate, NIST AI RMF, ISO 42001. Sanitized public versions live in the GitHub repo. Mid-level Security Engineers rarely write policy. For a healthcare SaaS shop carrying SOC 2 + HIPAA + FedRAMP this saves the team months.

3. **AI/ML governance with human in the loop.** Not hype. Built Squire (LangGraph SOC analyst) with HITL approval gates, NeMo Guardrails for PII redaction (DLP), Promptfoo eval harness for control testing. The JD calls out "human in the loop" by name. Almost no mid-level candidate can speak to this credibly.

## Honest answers for likely gaps

| Gap | Read |
|---|---|
| AWS title not "Cloud Security Engineer" | LinkedIn says AI Security Engineer because the day-to-day is LLM/agent security on top of cloud infra. The cloud security work is the foundation, not a side project. Show pipeline + GRC. |
| No production multi-account AWS Organizations | "Honest answer: the org I run today is single-account AWS plus DigitalOcean, but the patterns transfer (centralized findings, delegated admin, SCPs). Open to learning Organizations on the job, the tooling depth is there." |
| No Wiz / Sysdig / Orca / Lacework | "Used Falco for runtime, Trivy for image scan, OPA Gatekeeper for admission. Not licensed for CNAPP yet but the model is the same: agentless inventory, posture, runtime, identity. Pick it up fast." |
| No CySA+ / CEH / OSCP / AWS Security Specialty | "SecurityX, SSCP, Sec+, CCNA, CISSP sitting April 2026. AWS Security Specialty would be next on the cert ladder if hired." |
| Healthcare exposure | "Direct healthcare zero. Adjacent through HIPAA control authoring in the GRC library and the Texaco PCI DSS scope. Comfortable with PHI handling, BAA expectations, and audit posture." |

## 4 questions to ask Austin

1. Who does this role report to (CISO, Director Security, Manager) and what's the team size?
2. AJC Top Workplace was last cited 2022. Is there a more recent year, and what changed culture-wise post-Hearst acquisition?
3. FedRAMP status: ready, in process, or authorized? That changes the role scope significantly.
4. Interview process: how many rounds, what's the typical timeline from screen to offer?

## Comp anchor

- Stated band: $100-120K. The Ladders confirms $90-120K. Levels.fyi median total comp $135K (with bonus + benefits factored in).
- **Anchor: $118K base** if asked. Reasoning: AWS + HIPAA + GRC + DevSecOps mid-level in Atlanta market is $110-125K. GRC library + pipeline depth justifies top of band.
- If pushed for a number first: "$115-125K depending on bonus structure and HSA contribution."
- Going above $120K triggers a "wrong level" reroute to a Senior req that needs YOE Emmanuel does not yet have.

## Red flags to avoid

- Do NOT lead with AI/LLM hype. QGenda is not an AI shop. Hold AI as a closer, not opener.
- Do NOT frame CoreDirective as a company you run. Frame as security engineering scope.
- Do NOT cert-stack as identity. Lead with the work.
