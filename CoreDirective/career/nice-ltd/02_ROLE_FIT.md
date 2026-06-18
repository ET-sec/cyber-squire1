# NICE Ltd AI Data Specialist — Role Fit + Scope Clarifier

The first 5 minutes of the Wednesday call determine if this is a real fit or a scope mismatch. This document prepares both scenarios.

---

## The Central Uncertainty

**Your primary work is AI Security.** The JD is titled "AI Data Specialist" and describes: data structure design, precision/recall validation, unstructured-to-structured data conversion, feedback to Research + Product.

These are adjacent disciplines, not the same one. Before Matt invests the full 30 minutes pitching NICE, you need to decide which scope lens applies.

**Ask this in the first 5 minutes (after intros, before Matt pitches):**

> "Matt, thanks again for the details in the email. Before we go too deep, can I ask one clarifier up front — is this role scoped more toward the security posture of the AI data pipelines, or is it primarily schema design and pipeline evaluation work? That'll help me tell you honestly how my background maps."

---

## Scenario A — Security Posture of AI Data Pipelines (STRONG FIT)

**If Matt says:** "Security posture is a big part of it — how do we keep data pipelines safe, handle PII in interactions, validate model outputs won't leak sensitive information, govern third-party AI tools."

**Your positioning then becomes:**
- You are a natural fit
- Lean into your flagship AI Security work: OpenClaw AI gateway, OWASP LLM Top 10 red team, NIST AI RMF + ISO 42001 alignment, 37 GRC documents including AI Governance policy
- Your Falco 200→12 tuning is a precision/recall story in production (runtime detection IS a precision/recall problem)
- NeMo sandboxing is model risk validation — direct precision/recall lens
- Your 37 GRC docs include an IR playbook for AI-specific incidents

**One-paragraph fit pitch for Scenario A:**

"That actually maps well. At CoreDirective I run a production Claude Opus gateway that we red teamed against OWASP LLM Top 10 and MITRE ATLAS. Precision and recall show up in that work as detection-engineering metrics — I tuned Falco eBPF from 200 runtime alerts per day to 12 actionable findings, which is precision/recall tuning in a security context. I authored 37 GRC documents including an AI Governance policy anchored to NIST AI RMF and ISO 42001, and an IR playbook specifically for AI incidents like prompt injection leading to data exfiltration. For a role focused on AI data pipeline security posture at NICE's scale, I'd expect to be productive quickly."

---

## Scenario B — Schema Design + Data Engineering (PARTIAL FIT)

**If Matt says:** "Primarily schema design. Defining the taxonomies that classify customer interactions. Validating precision/recall of data structures against ground truth. Working with Research to refine models."

**Your positioning then becomes:**
- Honest: this is not your primary work today
- Still credible because: AI evaluation discipline transfers; NeMo evaluation frameworks are relevant; precision/recall thinking is consistent across ML domains
- You ARE a data engineer in production — IaC, schemas, pipeline definitions — even if not CCaaS-specific
- Your gap is domain expertise in contact center AI, not technical fluency

**Honest reframe for Scenario B:**

"Candor — my primary day-to-day is AI Security, not CX domain data modeling. What does transfer: I evaluate AI systems against adversarial conditions using precision/recall as a primary metric; I've worked with NeMo evaluation frameworks for model behavior validation; my GRC library includes data classification and data handling policies that underpin structured data from unstructured sources. The gap I'd close quickly is CX industry domain — intent taxonomies, agent quality taxonomies, CCaaS-specific terminology. I'd want to know how much of the role is domain-agnostic data engineering versus deep CX subject matter expertise. What's the split?"

**Decision after Scenario B answer:**
- If role is 70%+ CX domain expertise: decline gracefully, thank Matt, preserve relationship for future security roles
- If role is 50/50 or CX-light: continue, emphasize data engineering + evaluation + quick ramp on domain

---

## Scenario C — It's Both, or "Not Sure Yet" (DEFAULT)

**If Matt is vague or says "a bit of both":**

"Got it. Happy to lean into either side — my strongest evidence is on the security posture angle because that's where I live today, but I'm a quick study on CX-specific data structures if NICE wants that weighting. I can tailor how I frame my background as we go — what's useful to know first?"

This preserves optionality and lets Matt pitch freely without you over-committing to one lens.

---

## JD Evidence Mapping (both scenarios)

Verbatim JD phrases → your matching evidence.

### "Pre-defined data structures for automated analysis of large sets of CX interactions"

**Your evidence:**
- At CoreDirective: 16 Terraform files defining 30+ infrastructure resources across DigitalOcean and Cloudflare, with 8 OPA/Rego policies enforcing schema-level compliance before any deployment
- Falco rule schemas for runtime detection — precision/recall tuned
- Data classification schemas in the GRC library tying data types to controls

**Gap:** Not specifically for CX interactions (audio, chat, email, social). Ramp on the specific taxonomies.

### "Validations of completed and evolving data structures to ensure high standards for precision and recall"

**Your evidence:**
- OpenClaw red team validation against OWASP LLM Top 10 — test cases ARE precision/recall checks
- Falco rule tuning is measured in false positive + true positive rate — same math, different domain
- NeMo evaluation frameworks (NVIDIA's NeMo Evaluator supports LLM behavior testing)

**Gap:** Not directly BLEU/ROUGE/F1 in NLP evaluation context. Familiar with the concepts; haven't applied to intent classification.

### "Testing evolving tools from Research that support the development of the data structures"

**Your evidence:**
- You are the early adopter of security tools at CoreDirective — pilot + evaluate + provide feedback is how Trivy, Semgrep, NeMo, Falco all got integrated
- Pattern transfers: evaluate new tooling, document findings, advocate for or against adoption based on evidence

**Strong fit.**

### "Providing feedback to the Research and Product teams on how to continue to evolve tooling and data integration"

**Your evidence:**
- You've written 37 GRC documents — feedback in written form is your baseline
- Content creation (Threat Brief LIVE, The Build LIVE) trains you to communicate technical nuance to mixed audiences

**Strong fit on the communication side. Unknown whether Research at NICE works fast-feedback or slow-feedback; will adapt.**

---

## The "Why the AI Security Resume?" Question

**If Matt asks about your flagship AI Security Engineer resume on a data specialist role:**

"Deliberate. I sent the strongest version of my technical fluency because the role JD emphasized AI data work end-to-end, not pure schema design. AI Security is where my evaluation and precision/recall discipline is most visible — adversarial testing is precision/recall applied to attack scenarios. If this role weights domain-specific CX data engineering over AI evaluation, I'd tailor the resume for that angle. Your call on Wednesday helps me know which weighting NICE is looking for."

**Why this answer works:**
- Honest about the decision
- Shows you evaluated the fit yourself, not just blindly applied
- Reframes the resume choice as intentional signaling of your strongest work
- Offers to tailor if scope calls for it — shows flexibility without hedging

---

## The "Why Did You Apply to AI Data Specialist?" Question

**If Matt asks what drew you to the role:**

"Three reasons. One, it's Atlanta — I want to stay in this market, and the hybrid 2-day cadence is a real plus. Two, NICE is in growth mode on AI — I saw the Q4 2025 numbers, AI ARR up 66 percent, and hiring into the Enlighten AI data team is strategic, not maintenance. Three, the role description sits at the intersection of data evaluation and AI governance, both of which are fluent for me. The security lens I bring is additive — I don't think a strong AI Data Specialist hurts by understanding adversarial failure modes."

**This answer signals:**
- You did homework on NICE (stock numbers, market position)
- You understand the role's strategic context
- You see your security background as additive, not distracting

---

## Technical Vocabulary You'll Need (brief refresher)

Covered in depth in other files, but worth having at the surface:

### Precision and Recall
- **Precision** = of the things the model flagged as positive, how many actually were? (minimize false positives)
- **Recall** = of the actual positives, how many did the model find? (minimize false negatives)
- **F1** = harmonic mean of precision and recall, single metric when both matter equally
- **F-beta** = weighted version; beta > 1 favors recall, beta < 1 favors precision

### NLP Evaluation Metrics (for unstructured text + transcript analysis)
- **BLEU** (Bilingual Evaluation Understudy) — n-gram overlap for translation / generation. Higher is better. Used for LLM output quality vs reference.
- **ROUGE** — recall-oriented overlap for summarization. ROUGE-1, ROUGE-2, ROUGE-L variants.
- **Perplexity** — how surprised the model is by a sequence. Lower is better. Used to compare language models on held-out data.
- **Intent classification accuracy** — top-1 / top-3 accuracy for multi-class problems
- **Confusion matrix** — the full precision/recall picture across all classes, not just averages

### Audio / Speech-Specific (CX context)
- **WER** (Word Error Rate) — ASR (Automatic Speech Recognition) accuracy metric
- **Speaker diarization** — separating speakers in multi-party audio
- **VAD** (Voice Activity Detection) — detecting speech vs silence/noise

### Agent quality metrics (contact center specific)
- **CSAT** — Customer Satisfaction
- **FCR** — First Call Resolution
- **AHT** — Average Handle Time
- **QA scoring** — automated or human evaluation of agent interactions against rubrics

You don't need to have hands-on with every metric. You need to be able to acknowledge them when Matt mentions them, not stumble.

---

## The Bridge Statement (memorize — use whenever asked to connect AI Security to AI Data Specialist)

"My AI Security work is fundamentally about validating AI systems under adversarial conditions — precision and recall applied to attack scenarios. Your Enlighten AI team validates AI under normal conditions — precision and recall applied to intent classification. Same evaluation discipline, different failure surface. The skill set ports. The domain ramp is CX-specific taxonomies and CCaaS vocabulary, which is a few weeks, not a year."
