# Triage Playbook

The exact mental flowchart for triaging an alert in an interview scenario or on shift. Six steps, ordered. Memorize the sequence and the verbatim phrasing. Map directly to the Dropzone AI workflow at the end.

---

## Step 1: Classify

Within the first 30 seconds, name what you are looking at. Four possibilities.

**True Positive**: The alert reflects a real attack or unauthorized activity.

**False Positive**: The alert fired but the activity is benign. Detection error.

**True Negative**: This is not what you are looking at. True negatives never fire alerts. They are the baseline of normal.

**False Negative**: An attack that did NOT generate an alert. You only learn about these from external signal (a tip, an incident from elsewhere, hindsight). They drive coverage gap analysis.

Verbatim phrasing for the interview:

> "First I classify. Is this a true positive, a false positive, or noise. I look at the rule's historical precision, the asset criticality, and the user identity in the first 30 seconds before I commit time."

If precision on this rule is under 30 percent and there are no enrichment red flags, you are probably looking at a false positive. Move fast.

---

## Step 2: Determine Criticality

Severity is not a rule property, it is a context property. Compute it in two dimensions.

**Asset value (1 to 4)**:
- 1: Dev or test asset, no sensitive data
- 2: Production but non-customer-facing, internal tooling
- 3: Customer-facing production, holds PII or business data
- 4: Crown jewel. Domain controllers, root accounts, secrets stores, payment systems

**Threat severity (1 to 4)**:
- 1: Recon, scanning, low-confidence anomaly
- 2: Initial access attempt, single failed exploitation
- 3: Successful execution, lateral movement, persistence
- 4: Active data exfil, ransomware deployment, identity takeover

Multiply or add to a priority. Asset 4 plus Threat 3 is the page-oncall combination. Asset 1 plus Threat 1 is fire-and-forget triage.

Verbatim:

> "I score asset criticality on a 1 to 4 scale and threat severity on a 1 to 4 scale. Crown jewel asset and active execution is a wake-up. Dev asset and a port scan goes on the daily review."

---

## Step 3: Gather Context (5 minutes hard cap)

Five minutes. Hard cap. If you cannot tell what happened by minute 5, escalate. Do not become the analyst who spent two hours triaging one alert and let three others rot.

The context bundle (the 5 W's plus blast radius):

- **Who**: user, service account, IP, device fingerprint
- **What**: action taken, command run, API called, file written
- **When**: first event timestamp, duration, frequency
- **Where**: source, destination, asset, geography
- **Why does it matter**: the attacker's likely objective at this point in the kill chain
- **Blast radius**: what else can this entity touch. Roles, groups, network reach, data scope.

Triage queries you run in parallel:

```bash
# All recent activity from this user
# All recent activity from this source IP
# All recent alerts on this asset
# Asset criticality lookup (CMDB)
# User role lookup (HR or IDP)
# Reputation check on IP and any domains
# Any concurrent alerts within 30 min that share entities
```

Verbatim:

> "I give myself 5 minutes for context. I pull who, what, when, where, blast radius. If I do not have a clear picture by 5 minutes, I escalate. The cost of sitting on it is missing the next alert."

---

## Step 4: Decide Action

One of five outcomes. Pick fast.

**Auto-respond**: high-confidence true positive on a known pattern. SOAR playbook handles it. Disable user, isolate host, revoke token, rotate key. Logged for review.

**Escalate to L2**: ambiguous signal that needs investigation depth beyond 5 minutes. Pass with full context bundle.

**Page oncall**: high-severity, high-confidence, active threat. Wake someone up. Use the comms template (Step 5).

**Suppress**: known benign pattern, documented in the rule's `falsepositives` section. Mark and move.

**Tune**: the rule is firing too broadly. Suppress this instance, file a tuning ticket on the rule itself. Detection-as-code repo PR.

Verbatim:

> "Decision is one of five: auto-respond, escalate, page, suppress, tune. I commit. Sitting on alerts is the worst outcome."

---

## Step 5: Document and Communicate

Every alert closes with a written record. Even the false positives. Especially the false positives.

**Alert ticket fields**:
- Verdict: TP / FP / Inconclusive
- Root cause (one sentence)
- Action taken
- Evidence links (log queries, screenshots, related alerts)
- Time spent

**Comms format for escalation or paging**:

```
SUMMARY: [one sentence, what happened]
WHO: [user/asset/IP]
WHAT: [action observed]
WHEN: [first event time, duration]
SEVERITY: [score and reasoning]
BLAST RADIUS: [scope of affected resources]
IMMEDIATE ACTION: [what I have done]
RECOMMENDED NEXT: [what L2 or oncall should do]
EVIDENCE: [links to relevant queries and logs]
MY CONFIDENCE: [low/medium/high and why]
```

Senior signal: include `MY CONFIDENCE` explicitly. Juniors hide uncertainty. Seniors name it.

Verbatim:

> "Every alert closes with a verdict, a root cause, and an action. The escalation template is who, what, when, where, severity, blast radius, immediate action, recommended next, my confidence. That last one is the difference between sounding senior and sounding junior."

---

## Step 6: Follow-Up

The triage is not done when the ticket closes. Three follow-ups.

**Root cause**: post-incident, what was the underlying mechanism. Phishing source, vulnerability, misconfig, insider, dependency compromise. Document.

**Detection improvement**: did this rule fire correctly. Was the precision worth keeping. Should the rule expand or tighten. Should a sibling rule be written for the related TTPs the attacker did not use this time but might next.

**Threat hunt for the same TTP elsewhere**: if I caught an attacker using technique X here, are they using technique X anywhere else in the environment. Run the same query at scale across all data sources for the last 30 days. This is how you find the long tail of dwell.

Verbatim:

> "After every TP, I do three things. Root cause, detection improvement, hunt for the same TTP elsewhere. The hunt is what catches the breach the rule missed last week."

---

## Mapping to the Dropzone AI Workflow

Dropzone AI's pitch is that their AI agent runs steps 1, 2, and 3 autonomously, then hands the analyst a curated package for steps 4 and 5. Step 6 stays with the analyst and the detection engineering team.

**What the Dropzone agent does** (per their public materials):

- Receives the alert from the SIEM (Splunk, Sentinel, Chronicle)
- Reads the alert context and runs an investigation playbook
- Pulls related logs, identity context, asset metadata, threat intel
- Writes a structured investigation report with verdict, evidence, and recommended action
- Either auto-resolves benign cases or hands escalations to a human with the report attached

**What the analyst still does**:

- Reviews the report, validates the AI's reasoning
- Makes the final call on action (auto-respond, escalate, page, suppress, tune)
- Communicates to stakeholders
- Drives root cause analysis and detection improvement

**Where the detection engineer fits**:

- Writes the rules that fire the alerts
- Tunes the AI agent's prompts and playbooks (this is new and important)
- Audits the AI's investigation reports for hallucinations or systematic blind spots
- Treats every AI report as a test case that feeds back into both the rule and the agent's reasoning

In the interview, frame your value as: "I can write the rules, tune the agent, and audit its reasoning. The combo is rare. Most detection engineers know rules. Most ML engineers do not know detection. I do both."

---

## Drill: Run This Daily Until Automatic

Pick one alert from `lab_12_falco_runtime_anomaly`. Triage it out loud in 5 minutes. Speak the steps. Write the comms template. Decide the action.

Then pick another. Do 10. By alert 10 you should be under 4 minutes per alert and the steps should feel like reflexes. That is the senior signal in interviews. You sound like you have done this 1000 times because you have done this 100 times in practice.

The phrasing in this playbook is the verbatim language to use in interviews. Memorize the section headers. The bullet structure under each header is the muscle memory.
