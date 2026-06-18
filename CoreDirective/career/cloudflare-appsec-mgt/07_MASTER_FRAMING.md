# 07_MASTER_FRAMING — Red Thread, Pitches, Mirror Language

## Red thread (one sentence that ties Texaco → CoreDirective → this role)

> "Every job I've held has been about turning a chaotic security posture into one a small team can defend, measure, and prove. Texaco was 14 critical findings down to 2. CoreDirective is 200+ daily alerts down to 12. Cloudflare at scale is the same problem with a bigger surface."

## Three pitch lengths

### 30 seconds (elevator)

> "AI Security Engineer at CoreDirective in Atlanta. I run a production Cloudflare-fronted stack today: WAF, Rate Limiting, Zero Trust Access, Tunnel, all in Terraform with OPA gates. Four years before that I owned IT security ops for Texaco, PCI DSS scope, three retail sites. SecurityX, SSCP, CCNA, Security+, sitting CISSP. Atlanta local, 1-day onsite is fine."

### 90 seconds (recruiter screen)

> "AI Security Engineer at CoreDirective. My day-to-day overlaps this role exactly. I run the Cloudflare edge for a production zone, WAF custom rules, Rate Limiting on webhook endpoints, Bot Fight Mode, Zero Trust Access for self-hosted apps, Cloudflare Tunnel for ingress, DNS hardening. Everything codified in Terraform across 16 modules with 8 OPA policy gates that block merges if encryption, tagging, secrets handling, or zero public ingress is broken. Cut Datadog alerts from 200+ to 12 daily by tuning the edge.
>
> Before CoreDirective I was IT Security & Operations Manager at Texaco for four years across three retail sites. PCI DSS scope on 45+ devices. Wrote the IR runbook that dropped containment from 8 hours to 90 minutes. Splunk SIEM detection 48 hours to 4. AD hardening 14 critical findings to 2.
>
> SecurityX, SSCP, CCNA, Security+ on the wall, sitting CISSP this cycle. Atlanta local, ready hybrid or remote, 1 day onsite is fine. Open to contract-to-hire."

### 3 minutes (HM screen)

Add to the 90-second pitch:
- Specific story about WAF custom rule writing on `tigouetheory.com` (5 rules, free-tier limit, prioritization)
- Tunnel + Access architecture story (why service tokens for machine-to-machine)
- Texaco IR story with concrete attacker behavior (POS skimmer, vendor access)
- Why this role: chance to operate Cloudflare at multi-zone scale and learn the things you can only learn under load

## Mirror language (use their words back)

JD says → Use these phrases:
- "design, implementation, and ongoing management of Cloudflare services"
- "protect and optimize the organization's digital assets"
- "work closely with security, infrastructure, and application teams"
- "robust protection against DDoS attacks" → "DDoS posture" (drop "robust")
- "secure web application delivery"
- "effective traffic management"
- "hands-on experience with Cloudflare's suite of products"
- "cloud security principles"
- "troubleshoot and optimize web performance and security configurations"

Wherever possible, mirror these phrases when describing your own work.

## Never-say list

- "Pivoting", "transitioning", "aspiring", "looking to break into"
- "Founder of CoreDirective", "I built the company"
- "Whatever rate you can do"
- "I'm not really a Cloudflare expert but..."
- "Just a contract gig for me"
- "I haven't really shipped much in production"
- "I'm finishing my degree" (only if asked, frame as graduating May 2026)
- "AI is the future" (don't pitch AI to a Cloudflare role)
- "Leveraging", "robust", "comprehensive", "seamless", "synergy"
- Em dashes when you talk

## The differentiator (use once per call, not more)

> "The thing most candidates at this rate have not done is run Cloudflare as code with policy gates. I codify zone, DNS, Tunnel, Access, and WAF rulesets in Terraform, and 8 OPA/Rego gates block merges that break encryption, tagging, secrets handling, or zero public ingress. That means edge config drift is a configuration problem, not a paradigm shift, when you scale to multiple zones."

## Honest gap framing (have one ready)

> "My biggest Cloudflare gap is multi-zone enterprise operations. I run one zone with four hostnames at production-grade. The primitives are second nature, but I haven't felt multi-zone rule drift across business units or RBAC at scale. The flip side is everything I do is codified, so scaling out is a known unknown, not an unknown unknown."

## If they ask about AI

This is a Cloudflare role, not an AI role. Keep AI on the bench unless they ask.

If they ask:
> "Yes, I run AI security at CoreDirective: threat modeling against OWASP LLM and MITRE ATLAS, AI red teaming, an internal alert triage assistant. That's why my day job touches edge security closely, because the AI gateway sits behind Cloudflare. Happy to go deeper if it's relevant."

Do not lead with AI. Do not name-drop NeMo Guardrails, Langfuse, pgvector. Those land flat with a Cloudflare hiring manager.
