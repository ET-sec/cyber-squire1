# 02_ROLE_FIT — JD Phrase to Evidence Mapping

## JD (recruiter copy)

> "These positions are responsible for the design, implementation, and ongoing management of Cloudflare services to protect and optimize the organization's digital assets. This role will work closely with security, infrastructure, and application teams to ensure robust protection against DDoS attacks, secure web application delivery, and effective traffic management. The ideal candidate will have hands-on experience with Cloudflare's suite of products, a strong understanding of cloud security principles, and the ability to troubleshoot and optimize web performance and security configurations."

## Phrase-by-phrase mapping

| JD phrase | Emmanuel evidence | Resume bullet ref |
|---|---|---|
| "design, implementation, and ongoing management of Cloudflare services" | Owns full Cloudflare edge security lifecycle on tigouetheory.com production zone: WAF, Rate Limiting, Bot Fight Mode, Zero Trust Access, Tunnel, DNS | Bullet 1 (CoreDirective P007) |
| "protect and optimize the organization's digital assets" | Cut Datadog alerts from 200+ to 12 daily by tuning edge controls. Public site, payment-handling history (PCI DSS at Texaco) | Bullets 1, P024 (Texaco) |
| "work closely with security, infrastructure, and application teams" | "Partnered cross functionally with infrastructure and application owners" language injected throughout | Bullets 1, 9, P020 |
| "robust protection against DDoS attacks" | HTTP DDoS protection on by default, Bot Fight Mode active, Rate Limiting v2 on webhook endpoints (10 req/10s/IP/colo) | Bullet 1 |
| "secure web application delivery" | Cloudflare Tunnel fronting n8n + SSH, edge TLS termination, WAF custom + managed rule evaluation | Bullets 1, 4 |
| "effective traffic management" | DNS hardening, Tunnel ingress routing, Splunk traffic management dashboards (Texaco) | Bullets 1, P022 |
| "hands-on experience with Cloudflare's suite of products" | WAF, Rate Limiting, Bot Fight Mode, Zero Trust Access, Tunnel, DNS, Terraform cloudflare provider | Bullets 1, 2 |
| "strong understanding of cloud security principles" | NIST 800-53 169 controls, NIST AI RMF, ISO 42001, OPA/Rego gates enforcing encryption, tagging, secrets, zero public ingress | Bullets 2, 10 |
| "troubleshoot and optimize web performance and security configurations" | Tuned alert pipeline 200+ to 12 daily, IR runbook 8h to 90min containment, Splunk detection 48h to 4h | Bullets 1, P020, P022 |

## Gap reframes (what to say if probed)

### Gap: "Have you run Cloudflare for a multi-zone enterprise?"
> "Honest answer: my hands-on production work is on one zone with four hostnames. The primitives, WAF expression engine, Rate Limiting, Access policy logic, Tunnel ingress, DNS, all run daily. What I haven't felt is multi-zone rule drift across business units or RBAC at scale. I'd want a week of pairing with someone on the team to learn how that operating model works here. The flip side is I codify everything in Terraform with policy gates, so scaling out is a configuration problem, not a paradigm shift."

### Gap: "Have you shipped Workers in production?"
> "Hobby-level, not production. I know where the seams are between edge and origin since I run Tunnel + Access on top of an origin I control. Picking up Workers is a code lift on a small runtime, not a concept lift. If the team writes Workers as part of the security control surface, I'd want to ramp on your patterns before deploying one."

### Gap: "Bot Management or Advanced Rate Limiting (paid SKUs)?"
> "I've operated Free and Pro tier features end to end. Bot Fight Mode, Rate Limiting v2, custom WAF rules, all in production. The paid tiers I've read but not run since my own infra doesn't justify the spend. I'd be learning the dashboard and tuning loop on the job."

### Gap: "Akamai / Imperva / F5 experience?"
> "Cloudflare is my edge. The WAF concepts, OWASP Core Ruleset thinking, rate limiting strategy, bot mitigation logic, those translate. Specific Akamai or Imperva product names I'd ramp on, but the underlying threat model is the same."

### Gap: "Why are you in contracting right now?"
> "Optionality. I want to see the real day-to-day before committing to FTE, and a contract-to-hire path lets the team and me both make a clean decision at conversion. Atlanta local, full benefits flexibility, ready to start fast."

## Bridge statements (turn weakness into evidence)

- "I haven't run Cloudflare at multi-zone scale, but I've run the only thing that scales worse: an unsegmented Texaco network with 45 PCI devices and zero monitoring. Rebuilt it as 4 VLANs in a defined cutover window. Multi-zone Cloudflare is the same problem with better tooling."
- "I haven't shipped a Worker, but I've codified 16 Terraform modules with policy gates that block unsafe merges. The discipline transfers."
- "I'm finishing CISSP this cycle. Not as a checkbox, as the lens I want for governance design. SecurityX, SSCP, CCNA, Security+ already cover the rest."
