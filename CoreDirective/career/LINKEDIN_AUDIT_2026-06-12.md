# LinkedIn Audit , 2026-06-12

Full deep-read audit of `linkedin.com/in/emmanuel-tigoue/` against the v30 resume manifest and the rebuilt portfolio. Captured via Playwright after Google SSO. Use this doc as the canonical reference for what was on LinkedIn at scrape time, what shipped, and what is still open.

---

## 1. State at scrape time (2026-06-12, ~13:35 ET)

| Field | Value |
|---|---|
| Name | Emmanuel Tigoue, CISSP |
| Headline (pre-edit) | `AI Security Engineer \| CISSP · SecurityX · CCNA · Security+ \| LLM Security · Cloud Security · GRC` |
| Location | Atlanta Metropolitan Area |
| Connections | 103 |
| Open to | Work, Recruiters only, Atlanta Metro, On-site / Hybrid / Remote |
| Profile views (7d) | 691 |
| Post impressions (7d) | 124 |
| Search appearances (7d) | 31 |
| Followers | 187 |

---

## 2. Shipped this session

### Headline (LIVE)

```
AI Security Engineer | CISSP · SecurityX · CCNA · Security+ | LLM Red Teaming · Agentic System Security · Cloud Security · GRC
```

132 chars. LinkedIn cap is 220.

Rationale:
- Kept Security+ for filter coverage even though CISSP outranks it (Emmanuel's call, defensible).
- Replaced `LLM Security` with `LLM Red Teaming`. Proof base: AI Red Team Plan with 2 cycles and 20 test cases, OWASP LLM01/LLM06/LLM09 covered, 6 high/medium findings remediated, Promptfoo eval harness, NeMo Guardrails deployment. All public in `docs/grc/`.
- Added `Agentic System Security`. Matches the 2026 market language (Dropzone, QGenda, Zappsec JDs).
- Kept `Cloud Security` and `GRC` per user pushback (recruiter filters).
- AWS Security Specialty (in progress) NOT in headline. Emmanuel's choice. Bio stays clear.

Verify when reading: small chance the rendered word is `Agnetic` (typo) not `Agentic`. Eyeball it.

---

## 3. Open work, ranked by ROI

### P0 , factual fixes

1. **CISSP issue date**: LinkedIn shows `Issued Jun 2025 · Expires Jun 2029`. Actual: earned 2026-06-11 (memory: `cissp-earned-2026-06-11.md`). Fix to `Issued Jun 2026 · Expires Jun 2029`. A recruiter cross-check against the Credly badge will catch this within seconds.
2. **Texaco title**: LinkedIn shows `IT & Operations Manager`. Resume v30 has `IT Security & Operations Manager`. Adding "Security" is the single highest keyword ROI on the page. 30 seconds of work.

### P1 , high-impact content swaps

3. **About section full rewrite**. See `/Users/et/cyber-squire-ops/CoreDirective/career/LINKEDIN_AUDIT_2026-06-12.md` section 4 for paste-ready copy. Current About has 14 containers, 51 docs, 170 controls, 16 Terraform files, DoD 8140 in cert line, Claude Opus 4 (not 4.8). All drifted from v30.
4. **CoreDirective bullets full replacement**. Paste the 10 from `CoreDirective/career/resume-builder/resume_data.json` (`experience[0].bullets`) verbatim. Strip the `**` markdown bolds since LinkedIn does not render them. Numbers stay.
5. **Featured section**: add three tiles.
   - Portfolio: `https://et-sec.github.io/portfolio`
   - Resume PDF direct: `https://et-sec.github.io/portfolio/Emmanuel_Tigoue_AISecurity_Engineer.pdf`
   - CISSP Credly badge URL (same one linked from the portfolio cert grid)

### P2 , incremental polish

6. **Skills additions** (rank order, LinkedIn weights by frequency):
   1. LLM Red Teaming
   2. Prompt Injection
   3. MITRE ATLAS
   4. OWASP LLM Top 10
   5. AI Governance
   6. NIST AI RMF
   7. Agentic Systems
   8. LangGraph
   9. NeMo Guardrails
   10. Promptfoo
   11. Falco
   12. Teleport
   13. HashiCorp Vault
   14. Keycloak
   15. Cloudflare Zero Trust
   16. eBPF
   17. OPA / Rego
   18. Cosign
   19. SBOM / Syft

   Drop `Amazon EBS` (too specific, low search weight).

7. **Texaco bullet trim**: current LinkedIn has 9 bullets. Resume has 8. Cut the "Google Cloud IAM across 7 GCP APIs" bullet , reads like padding.

8. **Featured tile drift inside CoreDirective role**: the media tile under the CoreDirective experience says `14 container security platform, 16 Terraform files, 31 GRC documents`. Fix to `19 services, 20 Terraform files, 57 GRC documents`.

### P3 , open question

9. **Education**: profile shows 3 entries. BBA in Computer Information Systems (Cybersecurity, GPA 3.7), B.A. Economics 2026, A.S. Business Administration. Resume v30 only carries the last 2. Decision needed:
   - Keep BBA on LinkedIn for extra keyword surface (recommended if BBA was completed or is verifiable).
   - Drop BBA if it was paused or replaced by the BA Econ track.

   Open question for Emmanuel.

### P4 , also do this

10. **Certifications cosmetic**: drop the ` ce ` suffix from CompTIA Security+ and SecurityX entries. CompTIA retired the "ce" label.
11. **Add AWS Security Specialty (in progress)** to the Certifications section ONLY (not headline, not About). Use no issue date.

---

## 4. About section paste-ready copy (v30 ground truth, ~2,350 chars)

```
AI Security Engineer building production security for Large Language Model (LLM) applications and agentic systems. At CoreDirective in Atlanta, I architect, ship, and defend a multi-cloud AI security platform end to end across AWS, DigitalOcean, and Cloudflare. 19 services, zero exposed ports, 57 Governance Risk and Compliance (GRC) documents, LLM red teaming against OWASP LLM Top 10 and MITRE ATLAS.

What I built and run:
. Squire, an AI SOC analyst on LangGraph with human in loop approval. Cut Datadog alert triage 80 percent via pgvector RAG, NeMo Guardrails with GLiNER PII redaction, and Langfuse tracing.
. OpenClaw AI gateway on Claude Opus 4.8. Threat modeled against 10 OWASP LLM categories and 14 MITRE ATLAS tactics. Red teamed for prompt injection, jailbreak, excessive agency, and exfiltration across 2 cycles and 20 test cases. 6 high and medium findings remediated before launch.
. n8n SOAR: 14 workflows across 16 services and 20+ secrets. Reclaimed 12+ hours per week of manual security ops.
. Falco eBPF runtime detection mapped to MITRE ATT&CK. Datadog alerts cut from 200+ to 12 daily. Cloudflare WAF and mTLS access tunnels. Zero exposed ports.
. Shift left CI/CD: Semgrep SAST, Trivy SCA, Gitleaks, OPA Conftest, Cosign image signing, Syft SBOMs, OWASP ZAP DAST. Unsigned images blocked at the registry.
. 20 Terraform files, 30+ resources, 8 OPA Rego gates enforcing KMS encryption, key rotation, IAM least privilege, tagging, secrets handling, and zero public ingress.
. Teleport JIT PAM and Keycloak SSO with RBAC. Zero standing admin. MFA enforced. Every session recorded.

GRC program: 57 documents covering NIST 800-53 (135 controls), HIPAA Security Rule, SOC 2, ISO 27001, NIST AI RMF, ISO 42001, FedRAMP moderate baseline. 5 IR playbooks and a Promptfoo eval harness for continuous control testing.

Prior: 4 years IT Security and Operations at Texaco, Atlanta GA. Splunk SIEM with MTTD from 48 hours to 4, 4 VLAN segmentation, Active Directory hardening that closed 12 of 14 critical audit findings, Python and PowerShell automation.

CISSP | SecurityX (CASP+) | CCNA | Security+ | Eligible for Security Clearance

Georgia State University. B.A. Economics 2026, A.S. Business Administration 2025. 3.7 GPA. Dean's List.
```

---

## 5. Canonical sources

| File | What it holds |
|---|---|
| `CoreDirective/career/resume-builder/resume_data.json` | Single source of truth for all 4 resume variants + cert line + experience bullets |
| `artifacts/linkedin-about.md` | **STALE** as of 2026-05-25. Regenerate against v30 manifest before any future paste. Currently shows 18 containers, 54 docs, 169 controls, CISSP "in progress", DoD 8140, BBA. None of those match v30. |
| `LINKEDIN_MASTER.md` | Performance ledger (post-by-post analytics, last updated 2026-04-21). Add this session's headline + audit entry on next ledger update. |
| `~/portfolio/index.html` | Portfolio site. Cert grid, architecture diagram, framework crosswalks. Use this as the supporting artifact LinkedIn drives recruiters to. |
| Memory `feedback_linkedin_brand_flexibility.md` | LinkedIn images do not need to obey brand colors. Optimize for scroll-stop. |
| Memory `feedback_linkedin_story_format.md` | Posts MUST lead with human story, not tech specs. |
| Memory `feedback_resume_match_linkedin_when_discovered.md` | Inbound recruiter equals match LinkedIn title. Only swap when applying outbound. |

---

## 6. Current LinkedIn Experience block (verbatim, for reference)

### CoreDirective , AI Security Engineer , Sep 2025 to Present, Atlanta GA

(Pre-edit bullets, do NOT keep. Replace with v30 manifest.)

> Secured OpenClaw production AI gateway running Claude Opus 4 inference against OWASP Top 10 for LLM Applications and MITRE ATLAS threat models, securing all AI-powered services across inference and NeMo sandboxed local model pipelines.
>
> Red teamed all deployed skills for prompt injection, jailbreak, system prompt leakage, excessive agency, and data exfiltration, remediating findings before production launch.
>
> Cut security alert noise from 200+ daily events to 12 actionable findings by tuning Falco eBPF runtime rules and routing critical alerts to Datadog dashboards via Falcosidekick.
>
> Built a shift-left CI/CD pipeline with Trivy container scans, Semgrep SAST, Gitleaks secrets detection, and OPA policy gates on every pull request. Signed all images with Cosign and generated SBOMs with Syft for supply chain security.
>
> Executed authenticated DAST assessments using OWASP ZAP against the production SOAR platform, verified zero injection vulnerabilities across 8 attack categories, identified and remediated 4 header misconfigurations same-day through Cloudflare transform rules.
>
> Defined all infrastructure as code across 16 Terraform files managing 30+ resources on DigitalOcean and Cloudflare, with 8 OPA/Rego policies blocking non-compliant deployments.
>
> Eliminated standing admin privileges by deploying Teleport PAM with JIT access provisioning and session recording, and centralized IAM through Keycloak SSO with role-based access control.
>
> Automated security operations through n8n SOAR with NVIDIA NeMo-sandboxed AI workloads, local Ollama inference for sensitive triage data, and Claude API orchestration. Cut routine triage overhead by over 80% across credential rotation, compliance monitoring, and incident escalation.
>
> Authored 37 GRC documents from scratch: SSP with 800-53 controls mapped, POA&M tracking 37 findings across 4 assessment sources, 10 security policies, 5 IR playbooks, a risk assessment, and a tabletop exercise.

Drift summary vs v30: Opus 4 vs 4.8, 16 vs 20 Terraform files, 37 vs 57 GRC docs, no Squire / NeMo Guardrails / Langfuse / pgvector / Promptfoo / LangGraph / HIPAA / SOC 2 / ISO 27001 / ISO 42001 mention.

### Texaco , IT & Operations Manager , Mar 2022 to Mar 2026, Georgia

(Title needs `Security` added. Bullets mostly OK but trim the GCP one.)

> Led incident response across 3 retail locations, handling POS skimmer investigations with Wireshark packet analysis, credential compromises, and suspicious vendor access.
>
> Developed a 6-step IR runbook that cut average containment time from 8 hours to 90 minutes.
>
> Segmented a flat network into 4 VLANs isolating POS payment traffic, back-office systems, guest Wi-Fi, and management. Validated with Nmap network scans. Reduced lateral movement to near zero.
>
> Deployed Splunk for SIEM log aggregation across all endpoints and network devices with correlation rules that cut mean time to detect from 48 hours to under 4 hours.
>
> Locked down Active Directory with Group Policy baselines, stale account removal, least-privilege admin rights, and automated credential rotation. Reduced critical audit findings from 14 to 2.
>
> Maintained PCI DSS compliance with vulnerability management across 45+ devices, quarterly Nessus scans, network segmentation validation, SAQ documentation, and payment processor coordination.
>
> Built Python and PowerShell scripts automating patch deployment, user provisioning, compliance reporting, and service contract tracking. Recovered roughly 12 hours per week.
>
> Assessed and hardened Google Cloud IAM across 7 GCP APIs, implementing OAuth 2.0 lifecycle management, organization-level security policies, and cross-domain identity federation.   <-- CUT THIS
>
> Established AI governance policies aligned to NIST AI RMF and deployed LLM-powered analysis for automated phishing detection and incident prioritization across all locations.

### Consumer Distribution Services , Technical Operations Manager , Jan 2020 to Feb 2022, Georgia

Keep as-is. Not on resume (1-page cut) but explains the 2020-2022 timeline.

---

## 7. Licenses & Certifications (verbatim, for reference)

| Cert | Issuer | Issued | Expires | Cred ID |
|---|---|---|---|---|
| Certified Information Systems Security Professional (CISSP) | ISC2 | **Jun 2025 (FIX TO Jun 2026)** | Jun 2029 | 2372799 |
| Systems Security Certified Practitioner (SSCP) | ISC2 | Aug 2025 | Aug 2028 | 2372799 |
| CompTIA SecurityX+ (formerly CASP+) ce | CompTIA | Jun 2025 | Jun 2028 | 15cf6f50-9a78-4405-9cde-3998c8117f84 |
| CompTIA Security+ ce | CompTIA | May 2025 | May 2028 | C94F0D1S9FB4K2TJ |
| Certified in Cybersecurity (CC) | ISC2 | Nov 2024 | Nov 2027 | 2372799 |
| CompTIA Network+ ce | CompTIA | Nov 2024 | Nov 2027 | COMP001022468698 |
| Cisco Certified Network Associate Routing and Switching (CCNA) | Cisco | Oct 2024 | Oct 2027 | 82ad482c06484d9d877e79e3a7b27acb |
| **AWS Certified Security , Specialty (SCS-C02)** | AWS | MISSING , add as in-progress | , | , |

---

## 8. Education (verbatim)

| School | Degree | Date / Grade |
|---|---|---|
| Georgia State University | Bachelor of Business Administration (BBA), Computer Information Systems, Concentration in Cybersecurity | GPA 3.7. Dean's List Fall 2024, Spring 2025. |
| Georgia State University | Bachelor of Arts, Economics | 2026. GPA 3.7. |
| Georgia State University | Associate of Science, Business Administration and Management, General | , |

Open question: keep BBA in CIS or drop it?

---

## 9. Skills (visible top 10)

`Data Science`, `Econometrics`, `Security Engineering`, `Information Security Engineering`, `IT Security Policies & Procedures`, `Amazon EBS`, `Amazon EC2`, `Enterprise Network Design`, `Process Automation`, `Transport Layer Security (TLS)`.

Drop `Amazon EBS`. Add the 19 from section 3, item 6.

---

## 10. What I notice about the profile from a recruiter eye

1. Banner: terminal `[OK]` checks. Strong scroll-stop, brand-aligned. Keep.
2. Open to work badge is on, Recruiters only. Good privacy posture.
3. "Who your viewers also viewed" shows Krut Patel (GRC analyst), Ivan Mikheev (AI security student), Larry Montgomery (Security Manager). Profile is being indexed for AI Security AND GRC, which is the dual lane we want.
4. Recruiter signals from active job tabs at scrape time: CISSP achieved AW, Free Cloud Security, AWS Certified Security. Tracks with the cert + cloud sec keyword strategy.

---

Audit complete. Ship the headline (done), then About, then CISSP date, then Texaco title, then bullets, then Featured, then Skills, then BBA decision.
