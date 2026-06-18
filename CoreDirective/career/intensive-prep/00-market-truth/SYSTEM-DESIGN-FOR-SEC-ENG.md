# System Design Rounds for Senior Security Engineers, USD 200K Bar

Reference document. How senior security engineers handle system design rounds.
Five common prompts plus rubrics and what distinguishes the USD 200K answer from
the USD 150K answer. Sources cited inline.

---

## 1. The Rubric Interviewers Use

### 1.1 Exponent's SALT framework
Source: Exponent senior security engineer interview prep.
https://www.tryexponent.com/blog/security-engineer-interview-prep

| Stage | Time | Focus |
|-------|------|-------|
| Scope | 5 to 10 min | Restate, clarify, define what is and is not in scope |
| Assets | 5 to 10 min | Identify assets, trust boundaries, threats |
| Layers | 20 to 30 min | Identity, network, data, monitoring, response |
| Tradeoffs | 5 to 10 min | Cost, latency, usability, residual risk |

### 1.2 The "interviewing.io" senior systems guide
Source: A Senior Engineer's Guide to the System Design Interview, interviewing.io.
https://interviewing.io/guides/system-design-interview/part-two

Key signal: senior candidates lead the conversation, narrate their reasoning,
and proactively name trade-offs without being asked. Mid candidates wait for the
interviewer to dig.

### 1.3 General senior dimensions

| Dimension | Mid (USD 150K) | Senior (USD 200K) |
|-----------|----------------|-------------------|
| Structure | Names components | Names components plus the reason each exists |
| Threat model | Generic threats | Specific, named, recent incidents |
| Trade-offs | Acknowledges when prompted | Surfaces unprompted |
| Failure modes | Happy path only | Walks through what breaks first |
| Cost reasoning | Hand-waves | Names dollars, latency budgets, ops load |
| Validation | None | Red team scope, regression tests, metrics |

---

## 2. Prompt: Design a Secure Secrets Management Service

### 2.1 Scope clarifications to ask
- Single account or multi-tenant?
- Workloads on which platforms (EKS, ECS, Lambda, EC2, on-prem)?
- Compliance constraints (SOC 2, FedRAMP, PCI)?
- Existing IdP and CI/CD?
- Dynamic vs static secrets?

### 2.2 USD 200K answer hits
1. **Vault choice with reasoning.** AWS Secrets Manager for managed simplicity.
   HashiCorp Vault for dynamic secrets (database creds, PKI), policy-as-code, and
   multi-cloud. Justify your pick.
2. **Identity-driven access.** No static credentials inside the workload. OIDC
   federation from CI to cloud roles. EKS Pod Identity or IRSA for workloads.
   Vault auth methods: JWT/OIDC for CI, Kubernetes for pods.
3. **Short TTLs and rotation.** Database creds with 15-minute TTL. Static API
   keys rotated on a cadence with break-glass procedure.
4. **Defense in depth.** Vault audit log piped to SIEM. Sentinel or OPA policies
   on top of Vault policy. SCP that prevents disabling rotation.
5. **Disaster recovery.** Vault auto-unseal via cloud KMS. Cross-region replica.
   Recovery key custodianship documented and tested.
6. **Threat model.** Adversary inside a pod with kubelet access; adversary in
   CI/CD; adversary with stolen recovery key; adversary with valid OIDC token.
   Walk each.
7. **Validation.** Quarterly red team that targets the Vault path. Synthetic
   monitoring on rotation success. Cost ceiling per workload.
8. **What you would not build.** "I would not roll my own KMS. I would not store
   secrets in Kubernetes Secrets without sealed-secrets or Vault Agent."

### 2.3 USD 150K answer signs
- Says "use Vault" without auth method, audit, or DR.
- Skips the rotation question.
- Treats secrets as encryption rather than identity-driven access.
- No mention of CI federation; assumes a static API key in the deploy pipeline.

Reference: HashiCorp Vault docs, AWS Secrets Manager, OWASP Cheat Sheet on Secrets.
https://www.hashicorp.com/products/vault
https://docs.aws.amazon.com/secretsmanager/

---

## 3. Prompt: Design a CI/CD Pipeline with Supply Chain Security

### 3.1 Scope clarifications to ask
- Source repo platform (GitHub, GitLab, self-hosted)?
- Artifact types (containers, Lambda zips, language packages)?
- Target SLSA level?
- Existing scanners and where in the flow?
- Deployment platform?

### 3.2 USD 200K answer hits
1. **Stages.** Source -> Build -> Test -> Security scan -> Sign -> Publish ->
   Deploy. Each stage produces an attested artifact.
2. **Source integrity.** Branch protection, signed commits via Sigstore Gitsign,
   required code review with at least one security reviewer for security-relevant
   paths.
3. **Hermetic builds.** Build runs in an ephemeral runner with no inbound
   network. Dependencies pulled from a private mirror (CodeArtifact, Artifactory)
   that is the only allowed source. Pinned by hash.
4. **Scanning fan-out.** SAST (Semgrep or CodeQL), SCA (Snyk or OSS Review
   Toolkit), IaC scan (Checkov), container scan (Trivy), secret scan (Gitleaks).
   Block on critical, file ticket on high.
5. **Provenance.** SLSA Build L3 minimum. Provenance signed by the builder, not
   the developer. Sigstore Cosign for image signatures.
6. **Deploy verification.** Admission controller (Kyverno, Gatekeeper) verifies
   the image signature before allowing the workload. Policy says "no unsigned
   images, no images without provenance, no images from outside the registry
   allowlist."
7. **Threat model.** Walk Codecov 2021 (build env compromise), SolarWinds 2020
   (build pipeline implant), npm package takeover (event-stream 2018), GitHub
   Actions runner compromise (Heroku 2022). Map mitigations to each.
8. **Secrets in CI.** No long-lived tokens. OIDC federation. Per-job least
   privilege. Audit log to SIEM.
9. **Validation.** SLSA assessor or third-party audit. Continuous evidence via
   `cosign verify` in CI. Regression tests for the policy controls.

### 3.3 USD 150K answer signs
- Adds scanners but does not gate on them.
- No provenance, no signing.
- Long-lived deploy tokens stored in repo secrets.
- Skips the admission controller and assumes the image is fine because it built.

Reference: SLSA framework, NIST SP 800-204D, Wiz SLSA primer.
https://slsa.dev/
https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-204D.pdf
https://www.wiz.io/academy/application-security/slsa-framework

---

## 4. Prompt: Design an LLM Proxy with Safety Controls

### 4.1 Scope clarifications to ask
- Self-hosted models, API-based (Anthropic, OpenAI), or both?
- Use cases (chatbot, agent with tools, embedding service)?
- Tenancy (single internal team, multi-tenant)?
- Compliance constraints?

### 4.2 USD 200K answer hits
1. **Architecture.** Reverse proxy in the request path. Centralizes auth,
   policy, logging, cost control. The proxy is owned by the platform or AppSec
   team, not the application team.
2. **Identity in.** Per-app and per-user keys. Quotas per identity. Audit log.
3. **Input controls.**
   - PII detector (Presidio or equivalent).
   - Prompt injection classifier (Lakera Guard, Rebuff, or in-house model).
   - Content policy classifier.
   - Token budget enforcement.
4. **Routing.** Choose model per use case. Route low-risk to cheap fast model,
   high-risk to a higher-quality model. Fall back on provider failure.
5. **Tool gateway.** Tools are not invoked directly by the model; the proxy
   maintains an allowlist of tools per session. Every tool call is logged.
6. **Output controls.** Output validation against a schema. Output classifier
   for sensitive data leakage. Strip URLs that match an exfiltration pattern.
7. **Sandbox for external fetches.** If an agent retrieves URLs, route through
   a fetch service that enforces a network allowlist, blocks internal IP
   ranges, and sanitizes returned content before it reaches the prompt.
   Reference: Reversec design patterns to secure LLM agents.
   https://labs.reversec.com/posts/2025/08/design-patterns-to-secure-llm-agents-in-action
8. **Observability.** Every prompt, retrieval, tool call, and response is
   logged with the model, version, latency, cost, and identity. Metrics on
   refusal rate, classifier hit rate, anomaly score.
9. **Threat model.** Direct injection, indirect injection in retrievals, system
   prompt extraction, tool abuse for data exfil, cost-exhaustion DoS, model
   theft via API. Map mitigations.
10. **Validation.** Promptfoo regression suite. Garak scans on model upgrades.
    Quarterly red team scope.

### 4.3 USD 150K answer signs
- Names a guard library and stops.
- No identity layer, no per-tenant quotas.
- Treats output handling as optional.
- No tool allowlist; assumes the model picks the right tool.
- No fall-back model when the provider is degraded.
- Skips cost ceilings; the candidate has not run a real LLM in production.

Reference: System Design Handbook LLM system design guide; Microsoft AI security
planning; Pydantic LLM intro.
https://www.systemdesignhandbook.com/guides/llm-system-design/
https://learn.microsoft.com/en-us/ai/playbook/technology-guidance/generative-ai/mlops-in-openai/security/security-plan-llm-application
https://pydantic.dev/articles/llm-intro

---

## 5. Prompt: Design a SOC Alerting Pipeline

### 5.1 Scope clarifications to ask
- Cloud, on-prem, or hybrid?
- Existing SIEM and EDR?
- Alert volume per day?
- 24/7 SOC or business hours?
- MTTR targets?

### 5.2 USD 200K answer hits
1. **Ingestion.** Logs from CloudTrail, GuardDuty, VPC flow, EDR, identity
   provider, application, and SaaS. Normalize to a common schema (OCSF or
   ECS).
2. **Detection layer.** Sigma-style rules in the SIEM, plus correlation rules,
   plus ML-based anomaly detection for the highest-volume sources. Senior
   candidates explicitly say correlation rules drift fast and require monthly
   review.
3. **Enrichment.** Each alert is enriched with asset criticality, identity
   context, threat intel, and recent-change data. Reference data lives in a
   feature store, not hardcoded.
4. **Triage.** Tiered. Tier 0 (auto-close known false positive), Tier 1
   (analyst), Tier 2 (engineer). Auto-close requires explicit approval with
   audit, not silent suppression.
5. **AI augmentation (where appropriate).** A constrained agent that proposes
   triage notes, drafts the timeline, and suggests next steps. Human approves
   before action. Frame as augment, not replace; the agent reduces analyst
   load on Tier 1, freeing seniors for hunts.
6. **Response.** Auto-remediation for low-risk responses (block IP, isolate
   host) gated by human-in-the-loop for first uses. Playbooks in code.
7. **Feedback loop.** Every closed alert tagged with outcome. Detection
   engineer reviews top false positives weekly and tunes.
8. **Threat model the pipeline.** Adversary disables logging, adversary tampers
   with detection rules, adversary floods the pipeline to cause alert blindness,
   insider modifies suppression list. Map mitigations: immutable log archive,
   change control on rules, rate-aware ingestion.
9. **Metrics.** MTTD, MTTR, false-positive rate, detection coverage mapped to
   MITRE ATT&CK.
10. **Validation.** Atomic Red Team, purple team exercises, detection-as-code
    in CI.

### 5.3 USD 150K answer signs
- "Use Splunk" as the answer.
- No enrichment.
- No tiering.
- AI agent replaces analysts (rejected framing).
- No metrics; cannot say MTTD.

Reference: OCSF schema, MITRE ATT&CK, Atomic Red Team.
https://schema.ocsf.io/
https://attack.mitre.org/
https://atomicredteam.io/

---

## 6. Prompt: Design Zero Trust Remote Access

### 6.1 Scope clarifications to ask
- Replacing VPN entirely or coexistence?
- Workforce size and device posture?
- BYOD or managed?
- Apps web-only or also TCP/SSH/RDP?
- Existing IdP?

### 6.2 USD 200K answer hits
1. **Reference.** NIST SP 800-207 Zero Trust Architecture as the framework.
   https://nvlpubs.nist.gov/nistpubs/specialpublications/NIST.SP.800-207.pdf
2. **Identity-first.** Federate to the existing IdP. MFA required, with phish-
   resistant factor (FIDO2) for privileged access. Conditional access tied to
   device posture.
3. **Device trust.** MDM enrollment as a precondition. Device certificate or
   posture token presented per session.
4. **Per-app access.** Identity-aware proxy (Cloudflare Access, Teleport,
   Zscaler ZPA, Google BeyondCorp) terminates and authorizes per request.
   No flat network access.
5. **Continuous verification.** Re-evaluate session on policy change, posture
   change, anomaly score. Short token TTL.
6. **Audit.** Per-session, per-action audit. Recording for privileged sessions
   (SSH, DB, kubectl) via Teleport or equivalent.
7. **Migration plan.** Coexist with VPN for legacy apps for 6 to 12 months,
   then sunset. Communicate the timeline early.
8. **Threat model.** Compromised device, stolen session token, IdP compromise
   (the dependency you should explicitly call out), insider abusing a
   privileged access pattern, social engineering MFA fatigue. Map mitigations.
9. **Validation.** Quarterly test of conditional access policies. Red team
   scoped to the IAP. Synthetic monitoring on the access path.

### 6.3 USD 150K answer signs
- Says "ZTNA" and stops.
- Does not separate identity, device, application authorization.
- No mention of phishing-resistant MFA.
- Assumes the IdP is bulletproof.
- No migration plan.

Reference: NIST SP 800-207; Microsoft Zero Trust adoption guidance.
https://learn.microsoft.com/en-us/security/zero-trust/adopt/secure-remote-hybrid-work

---

## 7. Cross-Cutting Senior Moves

These show up across every prompt and are the highest-yield phrases to drill.

1. **State assumptions explicitly.** "I am assuming the IdP is healthy. If that
   assumption fails, we have a different problem."
2. **Separate data plane and control plane.** Senior signal.
3. **Name a real incident.** Capital One 2019, Codecov 2021, SolarWinds 2020,
   Snowflake 2024, Bing Sydney 2023, MITRE ATLAS MCP cases 2026.
4. **Cost.** Latency in milliseconds, dollars per request, ops load in pages.
5. **Validation plan.** Red team scope, regression tests, metrics. A model
   without validation is just an opinion.
6. **What you would not build.** Naming what you skipped and why is a strong
   signal.
7. **Acknowledge unknowns.** "I have not run this in production. My answer is
   based on the public Reversec write-up; I would validate with the team."

---

## 8. Practice Drill

Pick one prompt per week. Write the answer in 40 minutes. Time-box. Then read it
out loud to yourself or a peer and rewrite. Iterate weekly. After five prompts,
the structure becomes muscle memory and you spend the round reasoning rather
than remembering.

---

## Sources

- Exponent senior security engineer prep.
  https://www.tryexponent.com/blog/security-engineer-interview-prep
- interviewing.io senior system design guide.
  https://interviewing.io/guides/system-design-interview/part-two
- SLSA framework.
  https://slsa.dev/
- NIST SP 800-204D, software supply chain security.
  https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-204D.pdf
- NIST SP 800-207, Zero Trust Architecture.
  https://nvlpubs.nist.gov/nistpubs/specialpublications/NIST.SP.800-207.pdf
- System Design Handbook, LLM system design.
  https://www.systemdesignhandbook.com/guides/llm-system-design/
- Microsoft AI security planning.
  https://learn.microsoft.com/en-us/ai/playbook/technology-guidance/generative-ai/mlops-in-openai/security/security-plan-llm-application
- Reversec, design patterns to secure LLM agents.
  https://labs.reversec.com/posts/2025/08/design-patterns-to-secure-llm-agents-in-action
- OCSF schema. https://schema.ocsf.io/
- MITRE ATT&CK. https://attack.mitre.org/
- Atomic Red Team. https://atomicredteam.io/
- HashiCorp Vault, AWS Secrets Manager docs.
- Wiz SLSA primer.
  https://www.wiz.io/academy/application-security/slsa-framework
- Pydantic for LLMs. https://pydantic.dev/articles/llm-intro
