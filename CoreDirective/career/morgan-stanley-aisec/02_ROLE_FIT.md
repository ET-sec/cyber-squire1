# 02 - Role Fit: JD bullet to evidence map

For every JD requirement, what you point to from CoreDirective + Texaco. Cite real artifacts.

---

## Responsibilities

### "Use AI tools to identify software vulnerabilities and security risks"
- CoreDirective: Claude Opus 4.7 gateway (OpenClaw) running in production. Integrated with custom n8n SOAR workflows that triage Trivy, Semgrep, and Gitleaks output. AI rewrites raw scan results into prioritized findings with remediation.
- Texaco: ran Snyk and SonarQube against legacy POS code; AI assist for code review wasn't standard yet so this is mostly CoreDirective.
- Hard number: routine triage workload reduced 80%+ via AI orchestration.

### "Test applications and systems for cyber threats"
- CoreDirective: weekly red team of own Claude Opus AI gateway against OWASP LLM Top 10 (prompt injection, training data poisoning, model DoS, supply chain). MITRE ATLAS sequences run monthly.
- Texaco: pentested POS, in-store networks, customer Wi-Fi. Quarterly external pentests reviewed; remediation tracked through ticketing.

### "Research zero-day and known vulnerabilities"
- CoreDirective: Falco eBPF runtime detection tuned from 200 alerts daily to 12 actionable findings. CVE intake feeds prioritized by EPSS + asset criticality.
- Texaco: PCI-DSS quarterly scans, vendor advisory triage, internal POC reproduction before pushing fixes.

### "Build AI-driven security solutions and defenses"
- CoreDirective: built the SOAR triage AI, the IR co-pilot (cut IR from 8 hours to 90 minutes), and the GRC documentation pipeline (37 sanitized docs in public repo).
- Promptfoo evals run against the AI gateway weekly. Falco + Datadog + Fluentd send detection signals to a single pane.

### "Work with engineering teams to improve software security"
- CoreDirective: stood up Trivy + Semgrep + Gitleaks in CI/CD, working with my own engineering work to cut from 14 to 2 critical findings. Established secure SDLC norms.
- Texaco: ran security review with developers on every release. Drove POS PIN encryption upgrade across stores. Trained shift supervisors on phish reporting (reduced click rate noticeably across the chain).

### "Analyze attack patterns and recommend fixes"
- CoreDirective: MITRE ATT&CK mapping in GRC docs. Falco + Wazuh detections mapped to TTPs. Incident playbooks (5 published) keyed to attack patterns: ransomware, AI incident, data exfil, account takeover, insider threat.
- Texaco: card-skimmer pattern analysis at register level after industry advisory; rolled out mitigations chain-wide.

---

## Skills

### "Cybersecurity fundamentals"
SecurityX (CASP+), SSCP, CCNA, Security+. CISSP exam sitting April 2026 (per memory). 6+ years across Texaco and CoreDirective.

### "Penetration testing / ethical hacking"
Weekly red team of own AI gateway against OWASP LLM Top 10 + MITRE ATLAS. Burp Suite, OWASP ZAP for DAST. Internal pentest exercises against my Cloudflare-tunneled services.

### "Programming knowledge (Python, C++, Java, etc.)"
- Python: production. n8n SOAR workflows, AI gateway tooling, GRC pipeline scripts.
- Java: reading level + small refactors. Not where I would claim production depth. Bridge: Snyk SCA + Checkmarx SAST are language-agnostic in workflow; deep Java vulnerability classes (deserialization, Spring patterns) I have studied and can speak to.
- C++: reading level only. Honest bridge: secure coding principles transfer (memory safety, input validation, buffer handling). I can review C++ findings with help, would not lead C++ remediation cold.

### "Understanding of AI/ML concepts"
- Operational: prompt injection defense via Promptfoo evals, LLM red team patterns, RAG security (context leak, indirect prompt injection), agentic AI security (tool poisoning, scope explosion).
- Reading and lab: training data poisoning, model extraction, adversarial perturbation, MITRE ATLAS technique families.
- Production frame: my Claude Opus gateway has guardrails, eval gates, output filters. I tune them weekly.

### "Knowledge of vulnerability assessment tools"
- In production at CoreDirective: Trivy, Semgrep, Gitleaks, Falco, Wazuh, OWASP ZAP, Burp Suite, Promptfoo.
- Vendor tools I have hands-on lab exposure with: Snyk, SonarQube (Texaco), Veracode.
- MS-stack tools (Wiz, Checkmarx) I have not run in production. Bridge: Snyk + Trivy operational depth transfers directly; tool-specific configuration is days not weeks.

### "Secure coding practices"
- OWASP Top 10 (web + API + LLM), OWASP ASVS, SANS Top 25 CWE.
- CI/CD shift-left at CoreDirective (Trivy + Semgrep + Gitleaks gated PRs).
- Secure SDLC training and code review experience at Texaco (POS rollouts).

---

## Honest gap reframes

### Java production depth
"My production work is mostly Python. Java I can read fluently and have worked through OWASP Cheat Sheet Series for Spring and Java EE. For AppSec at MS scale, my plan is to pair with senior Java engineers on the first remediation tickets so I learn the dialects and conventions of your codebase. Snyk and Checkmarx findings are language-agnostic at the workflow level, and I can drive the triage process while ramping the language depth."

### Wiz + Checkmarx specifics
"I have not run Wiz or Checkmarx in production. I have run Trivy and Snyk in CI/CD against my own production stack, which gives me the same workflow muscle: ingest findings, prioritize by CVSS plus EPSS plus asset context, drive remediation with engineering. Vendor-specific config is days not weeks."

### FINRA broker-dealer regulatory experience
"I have not held FINRA registration. I have however written 37 sanitized GRC docs across SOX-adjacent controls (asset management, access controls, change management) and 10 organizational policies. I am SOC-2 framework fluent. FINRA fingerprinting and Rule 17f-2 obligations I am ready to complete on day one."

### Enterprise-scale incident response volume
"My IR experience is at a smaller scale than MS Fusion Resilience Center. The patterns transfer: containment, triage, evidence preservation, root cause, postmortem. At CoreDirective I cut IR from 8 hours to 90 minutes using AI-assisted enrichment. I expect the curve at MS scale will be on volume management and team coordination, not on the engineering work itself."

---

## Bridge statements (memorize)

> "I run a small production AI security practice today. The patterns are the same as enterprise. The scale is different. The way I close that gap is by pairing with senior engineers on the first month of work and showing up with the metrics and playbooks I already use."

> "Morgan Stanley's AI@MS rollout is exactly the surface area I think about every week. Prompt injection, RAG context leakage, agentic tool scope, eval coverage. The fact that you are opening to autonomous agents in WM tells me the AppSec team needs people who can stand between models and engineering and translate."
