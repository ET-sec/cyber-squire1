# Incident Response Playbook: AI System Compromise

**Document ID:** IR-PLAY-005
**Version:** 1.0
**Last Updated:** 2026-03-12
**Owner:** Incident Commander
**Classification:** Internal Use Only
**NIST 800-53 Controls:** IR-4 (Incident Handling), IR-5 (Incident Monitoring), IR-6 (Incident Reporting), SI-4 (Information System Monitoring), SI-3 (Malicious Code Protection)
**OWASP LLM Top 10 (2025):** LLM01, LLM02, LLM06, LLM07, LLM08
**MITRE ATLAS:** AML.T0040, AML.T0043, AML.T0048, AML.T0051, AML.T0054

---

## 1. Purpose

This playbook provides step-by-step procedures for responding to AI-specific incidents within the Organization infrastructure. These are incidents that originate from, target, or exploit the AI inference pipeline and its integration with downstream automation. These threat classes are not adequately covered by the existing container, credential, DDoS, or unauthorized access playbooks.

Specifically, this playbook addresses:

- **Prompt injection and jailbreak**: adversarial input that overrides AI system instructions or extracts protected context
- **Excessive agency and unauthorized AI-triggered actions**: AI agent executing workflow actions beyond its authorized scope
- **Data exfiltration via AI inference**: sensitive data (PII, credentials, operational context) leaked through AI prompts or responses to external API providers
- **AI model supply chain compromise**: tampered model weights, backdoored container images, or compromised upstream model providers

This playbook cross-references the STRIDE Threat Model (`THREAT_MODEL_STRIDE.md`), Attack Tree (`ATTACK_TREE_AI_PIPELINE.md`), and AI Threat Catalog (`AI_THREAT_CATALOG.md`) for threat decomposition and control mapping.

### Incident Response Decision Tree

Use this flowchart to quickly route an AI incident from initial detection through triage to the correct scenario-specific response path (A, B, C, or D).

```
┌─────────────────────────────────────────────────────────────────────┐
│                     AI INCIDENT DETECTED                            │
│                                                                     │
│  Sources: monitoring alert, user report, log anomaly, CI/CD scan    │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                v
┌─────────────────────────────────────────────────────────────────────┐
│                      INITIAL TRIAGE (0-5 min)                       │
│                                                                     │
│  1. Which AI system? AI-001 (Gateway), AI-002 (LLM), AI-003 (STT)  │
│  2. Is the incident still active?                                   │
│  3. Have downstream actions been triggered?                         │
│  4. Preserve logs BEFORE taking any containment action              │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                v
                 ┌──────────────────────────────┐
                 │  What is the primary signal?  │
                 └──────┬───────┬───────┬───────┘
                        │       │       │
          ┌─────────────┤       │       ├─────────────────┐
          │             │       │       │                  │
          v             v       v       v                  v
┌──────────────┐ ┌────────────────┐ ┌──────────────┐ ┌──────────────────┐
│ Suspicious   │ │ AI executed    │ │ Sensitive     │ │ Model hash       │
│ input or     │ │ actions beyond │ │ data found    │ │ mismatch, image  │
│ abnormal     │ │ its authorized │ │ in outbound   │ │ digest changed,  │
│ AI output    │ │ scope          │ │ API calls or  │ │ or vendor        │
│              │ │                │ │ AI responses  │ │ advisory issued  │
└──────┬───────┘ └───────┬────────┘ └──────┬───────┘ └────────┬─────────┘
       │                 │                  │                   │
       v                 v                  v                   v
┌──────────────┐ ┌────────────────┐ ┌──────────────┐ ┌──────────────────┐
│  SCENARIO A  │ │  SCENARIO B    │ │  SCENARIO C  │ │  SCENARIO D      │
│  Prompt      │ │  Excessive     │ │  Data Exfil  │ │  Supply Chain    │
│  Injection   │ │  Agency        │ │  via AI      │ │  Compromise      │
└──────┬───────┘ └───────┬────────┘ └──────┬───────┘ └────────┬─────────┘
       │                 │                  │                   │
       v                 v                  v                   v
┌──────────────┐ ┌────────────────┐ ┌──────────────┐ ┌──────────────────┐
│ Detect:      │ │ Detect:        │ │ Detect:      │ │ Detect:          │
│ Input patt-  │ │ Unexpected     │ │ PII/creds in │ │ Hash mismatch,   │
│ ern match,   │ │ workflow exec, │ │ API traffic, │ │ behavior change, │
│ output anom- │ │ permission     │ │ system prompt│ │ Trivy/Cosign     │
│ aly, user    │ │ escalation,    │ │ extraction,  │ │ alert, vendor    │
│ report       │ │ action volume  │ │ network      │ │ advisory         │
│              │ │ spike          │ │ anomaly      │ │                  │
├──────────────┤ ├────────────────┤ ├──────────────┤ ├──────────────────┤
│ Contain:     │ │ Contain:       │ │ Contain:     │ │ Contain:         │
│ Block input  │ │ Disable AI to  │ │ iptables     │ │ Stop affected    │
│ channel,     │ │ svc-automation │ │ DROP outbound│ │ AI service,      │
│ deactivate   │ │ integration,   │ │ 443 from     │ │ block model      │
│ AI-triggered │ │ rotate webhook │ │ gateway,     │ │ registry access, │
│ workflows,   │ │ secrets, stop  │ │ switch to    │ │ export container │
│ network iso- │ │ gateway if     │ │ local LLM,   │ │ for forensics    │
│ late if SEV1 │ │ still active   │ │ rotate creds │ │                  │
├──────────────┤ ├────────────────┤ ├──────────────┤ ├──────────────────┤
│ Eradicate:   │ │ Eradicate:     │ │ Eradicate:   │ │ Eradicate:       │
│ Analyze pay- │ │ Audit all AI   │ │ Add output   │ │ Verify model     │
│ load, update │ │ actions taken, │ │ filtering +  │ │ provenance, pull │
│ input filter │ │ reverse unauth │ │ prompt sani- │ │ clean model from │
│ rules, hard- │ │ actions, tight-│ │ tization, im-│ │ trusted source,  │
│ en system    │ │ en allowlist + │ │ plement DLP  │ │ Trivy scan new   │
│ prompt       │ │ approval gates │ │ rules        │ │ image, baseline  │
│              │ │                │ │              │ │ behavior test    │
├──────────────┤ ├────────────────┤ ├──────────────┤ ├──────────────────┤
│ Recover:     │ │ Recover:       │ │ Recover:     │ │ Recover:         │
│ Restart gate-│ │ Re-enable      │ │ Assess breach│ │ Deploy verified  │
│ way, re-en-  │ │ workflows one  │ │ scope, remove│ │ clean model,     │
│ able work-   │ │ at a time, add │ │ iptables     │ │ remove network   │
│ flows, test  │ │ human-in-loop, │ │ block, vali- │ │ restrictions,    │
│ with known   │ │ monitor 48h    │ │ date filters,│ │ run full test    │
│ prompts,     │ │                │ │ monitor 72h  │ │ suite, record    │
│ monitor 24h  │ │                │ │              │ │ new hash base-   │
│              │ │                │ │              │ │ line, monitor    │
└──────┬───────┘ └───────┬────────┘ └──────┬───────┘ └────────┬─────────┘
       │                 │                  │                   │
       └─────────┬───────┘                  └─────────┬────────┘
                 │                                    │
                 └──────────────┬──────────────────────┘
                                │
                                v
┌─────────────────────────────────────────────────────────────────────┐
│                    POST-INCIDENT (all scenarios)                     │
│                                                                     │
│  1. Collect evidence + generate SHA-256 manifest (Section 6)        │
│  2. Complete incident timeline, assign root cause (Section 7.1)     │
│  3. Update threat model, attack tree, AI threat catalog (Sec 7.2)   │
│  4. Create POA&M entries for control gaps (Section 7.3)             │
│  5. Update this playbook + SSP + risk assessment (Section 7.4)      │
│  6. Post-incident review meeting within 5 business days             │
└─────────────────────────────────────────────────────────────────────┘

Severity Quick Reference:
  SEV-1 (Critical): Unauthorized infra actions executed, confirmed data exfiltration
  SEV-2 (High):     Successful injection, supply chain compromise, manipulated outputs
  SEV-3 (Medium):   Attempted injection blocked, anomalous output not yet consumed
  SEV-4 (Low):      Resource anomaly, minor output drift, performance degradation

Escalation to other playbooks:
  Container shell/crypto miner  --> IR-PLAY-001 (Compromised Container)
  Credentials in AI logs        --> IR-PLAY-002 (Leaked Credential) + this playbook
  AI resource exhaustion/DDoS   --> IR-PLAY-003 (DDoS/Service Degradation)
  Unauthorized accounts created --> IR-PLAY-004 (Unauthorized Access)
```

---

## 2. Scope

Applies to all three AI systems within the authorization boundary and their downstream consumers:

| ID | System | Service | Model | Trust Zone |
|----|--------|---------|-------|------------|
| AI-001 | AI Agent Gateway | svc-ai-gateway (OpenClaw) to Claude Opus 4.7 | Anthropic API (external) | DMZ |
| AI-002 | Local LLM | svc-llm (Ollama) running `<MODEL_NAME>` | Ollama registry (pulled locally) | Internal |
| AI-003 | Transcription | svc-transcription (Whisper) | Open-weight (local) | Internal |

<!-- TODO(et): verify deployed Ollama model name via `ssh engine-host "docker exec svc-ollama ollama list"` and replace <MODEL_NAME> placeholder throughout this playbook -->

**Downstream consumers in scope:**
- svc-automation: orchestration workflows triggered by AI outputs (16 action types, 14 currently operational; `workspace_admin` and `excel` need OAuth re-auth)
- svc-db: database operations executed via AI-initiated workflow actions
- Telegram bot interfaces: user-facing message channel for AI-001

**Out of scope:** Non-AI container compromise (see IR-PLAY-001), credential leaks not involving AI systems (see IR-PLAY-002), DDoS not targeting AI endpoints (see IR-PLAY-003), unauthorized access not originating from AI behavior (see IR-PLAY-004).

---

## 3. Severity Classification

| Severity | Criteria | Example |
|----------|----------|---------|
| **SEV-1 (Critical)** | AI agent executed unauthorized infrastructure actions via svc-automation; confirmed data exfiltration through AI inference to external party | AI-001 triggers database DROP via svc-automation; PII confirmed sent to Anthropic API |
| **SEV-2 (High)** | Successful prompt injection altering AI behavior; model supply chain compromise detected; AI producing manipulated outputs consumed by workflows | Attacker crafts Telegram message that causes AI-001 to reveal system prompt; svc-llm model hash mismatch after update |
| **SEV-3 (Medium)** | Attempted prompt injection detected and blocked; anomalous AI output patterns not yet consumed by downstream systems | Input filter catches injection attempt; AI-001 generates unusual response format flagged by monitoring |
| **SEV-4 (Low)** | Unusual AI resource consumption; minor output anomalies; AI service performance degradation | svc-llm CPU spike during normal hours; AI-001 response latency increase; single unusual output in logs |

---

## 4. Incident Scenarios

### Scenario A: Prompt Injection / Jailbreak

**Threat References:** OWASP LLM01, MITRE ATLAS AML.T0051, AML.T0054, AML.T0043
**AI Threat Catalog:** ATC-01, ATC-02
**Attack Tree:** Path 1, Nodes 1.1.1-1.1.3, 1.2.1-1.2.2

#### A.1 Detection Triggers

- [ ] **Input pattern matching**: known injection patterns detected in Telegram messages or API inputs (e.g., "ignore previous instructions", "you are now", system prompt extraction attempts)
- [ ] **Output anomaly**: AI response contains content inconsistent with system prompt constraints (refusal override, persona change, raw system prompt text)
- [ ] **Behavior deviation**: AI-001 initiates svc-automation workflow actions not aligned with the user's stated request
- [ ] **Indirect injection indicator**: AI output references content from an external source (web page, document) that contains embedded instructions
- [ ] **User report**: authorized user reports unexpected AI behavior or response content
- [ ] **Monitoring platform alert**: log analysis rule triggers on suspicious prompt or response patterns

#### A.2 Triage Checklist (0-10 minutes)

- [ ] **Step A.2.1**: Identify the injection vector:
  - Direct injection via Telegram message?
  - Indirect injection via retrieved external content (Tavily search, browser skill, GitHub, Notion, python-interpreter, Gemini)?
  - Injection via API call to svc-ai-gateway?

- [ ] **Step A.2.2**: Determine which AI system is affected:
  ```bash
  # Check svc-ai-gateway logs for the incident window
  docker logs --since 1h svc-ai-gateway 2>&1 | tail -200

  # Check svc-llm logs if AI-002 is involved
  docker logs --since 1h svc-llm 2>&1 | tail -100
  ```

- [ ] **Step A.2.3**: Determine if the injection succeeded:
  - Did the AI execute an action it should not have?
  - Did the AI reveal system prompt content or operational context?
  - Did the AI change persona or override safety instructions?

- [ ] **Step A.2.4**: Check if any svc-automation workflows were triggered as a result:
  ```bash
  # Check svc-automation execution history via API
  # n8n REST API requires X-N8N-API-KEY header (value from CD_N8N_KEY in Doppler)
  curl -s -H "Content-Type: application/json" \
    -H "X-N8N-API-KEY: $CD_N8N_KEY" \
    http://localhost:<automation-port>/api/v1/executions?limit=20 | jq '.'

  # Check svc-db for recent workflow execution records
  docker exec svc-db psql -U <admin_user> -d <db_name> -c \
    "SELECT id, workflow_id, status, started_at FROM execution_entity ORDER BY started_at DESC LIMIT 20;"
  ```

- [ ] **Step A.2.5**: Assign severity per Section 3. If injection succeeded and triggered actions: SEV-1 or SEV-2. If detected and blocked: SEV-3.

- [ ] **Step A.2.6**: Open an incident ticket:
  - Incident ID: `INC-YYYY-MM-DD-NNN`
  - Injection vector (direct / indirect)
  - Affected AI system(s)
  - Whether actions were triggered
  - Severity

#### A.3 Containment (10-30 minutes)

> **CRITICAL:** Preserve conversation logs and API call records BEFORE taking containment actions. AI conversation state is ephemeral and may be lost on restart.

- [ ] **Step A.3.1**: Preserve the current conversation state and logs:
  ```bash
  # Export svc-ai-gateway logs (OpenClaw runs standalone, not under compose)
  # Logs go to stdout/stderr, captured by the Docker daemon
  docker logs svc-ai-gateway > /tmp/evidence_ai_gateway_$(date +%Y%m%d_%H%M%S).txt 2>&1

  # Export svc-automation execution logs
  docker logs --since 4h svc-automation > /tmp/evidence_automation_$(date +%Y%m%d_%H%M%S).txt 2>&1
  ```

- [ ] **Step A.3.2**: If the injection is ongoing (attacker actively sending messages), block the input channel:
  ```bash
  # Block the Telegram chat ID if the attack is via Telegram
  # Update the chat ID allowlist in the svc-ai-gateway config file
  # (canonical path on the live host: /root/moltbot/config-dir/openclaw.json)
  # Restart svc-ai-gateway to apply the change. OpenClaw runs standalone,
  # so use `docker restart` directly, NOT `docker compose restart`.
  docker restart svc-ai-gateway
  ```

- [ ] **Step A.3.3**: If the injection triggered unauthorized svc-automation workflows, disable the AI-to-automation integration:
  ```bash
  # Deactivate AI-triggered workflows in svc-automation
  # Target workflows: MASTER_ORCHESTRATOR_V1 (id UIf3v1ZNN98OtUge),
  # Telegram Supervisor Agent (id iO6PfPdk0SSPBTWb)
  curl -X PATCH -H "Content-Type: application/json" \
    -H "X-N8N-API-KEY: $CD_N8N_KEY" \
    http://localhost:<automation-port>/api/v1/workflows/<workflow_id> \
    -d '{"active": false}'
  ```

- [ ] **Step A.3.4**: If SEV-1 (confirmed unauthorized actions executed), isolate svc-ai-gateway from the network:
  ```bash
  # svc-ai-gateway sits on the docker default bridge (host gateway at 172.17.0.1).
  # Disconnect from internal-net to halt service-to-service traffic.
  docker network disconnect internal-net svc-ai-gateway
  ```

- [ ] **Step A.3.5**: Verify containment by checking that no new AI-initiated actions are executing:
  ```bash
  docker logs --since 5m svc-automation 2>&1 | grep -i "execution\|started\|webhook"
  ```

#### A.4 Eradication (30-60 minutes)

- [ ] **Step A.4.1**: Analyze the injection payload to understand the attack technique:
  ```bash
  # Review the preserved conversation logs for the injection content
  grep -i "ignore\|override\|system prompt\|you are\|pretend\|jailbreak" \
    /tmp/evidence_ai_gateway_*.txt
  ```

- [ ] **Step A.4.2**: Update input validation rules to block the specific injection pattern:
  - Add the injection pattern to the input filter rules
  - If indirect injection: add the source domain or content pattern to the block list

- [ ] **Step A.4.3**: Harden the system prompt:
  - Review system prompt for instruction boundary weaknesses
  - Add explicit refusal directives for the observed attack pattern
  - Reinforce separation between system instructions and user input

- [ ] **Step A.4.4**: If the injection leveraged a skill (browser, tavily-search, GitHub, Notion, python-interpreter, Gemini), restrict or temporarily disable that skill:
  ```bash
  # Update svc-ai-gateway configuration at /root/moltbot/config-dir/openclaw.json
  # Restart the gateway to apply. OpenClaw is standalone.
  docker restart svc-ai-gateway
  ```

- [ ] **Step A.4.5**: If unauthorized svc-automation actions were executed, reverse those actions:
  - Identify all actions taken (database writes, messages sent, API calls made)
  - Reverse each action where possible (delete records, retract messages)
  - Document any actions that cannot be reversed

#### A.5 Recovery (30-60 minutes)

- [ ] **Step A.5.1**: Restore svc-ai-gateway with updated configuration:
  ```bash
  # If network was disconnected, reconnect
  docker network connect internal-net svc-ai-gateway

  # Restart with updated system prompt and input validation
  docker restart svc-ai-gateway
  ```

- [ ] **Step A.5.2**: Re-enable AI-to-automation integration with tighter controls:
  ```bash
  # Reactivate the workflow with updated validation
  curl -X PATCH -H "Content-Type: application/json" \
    -H "X-N8N-API-KEY: $CD_N8N_KEY" \
    http://localhost:<automation-port>/api/v1/workflows/<workflow_id> \
    -d '{"active": true}'
  ```

- [ ] **Step A.5.3**: Validate AI behavior with test prompts:
  - Send known-safe prompts and verify expected responses
  - Send the injection pattern that triggered the incident and verify it is now blocked
  - Verify the AI refuses inappropriate requests correctly

- [ ] **Step A.5.4**: Monitor for recurrence over the next 24 hours:
  ```bash
  # Set up a log watch for injection patterns
  docker logs -f svc-ai-gateway 2>&1 | grep -i "ignore\|override\|system prompt"
  ```

#### A.6 Evidence Collection

| Artifact | Location | Collected? |
|----------|----------|------------|
| AI gateway conversation logs | `/tmp/evidence_ai_gateway_*.txt` | [ ] |
| svc-automation execution logs | `/tmp/evidence_automation_*.txt` | [ ] |
| Telegram message history (if applicable) | Bot API / chat export | [ ] |
| Monitoring platform AI alert events | Datadog dashboard export | [ ] |
| svc-db workflow execution records | `execution_entity` table dump | [ ] |
| Input validation rule state (before/after) | svc-ai-gateway config | [ ] |
| System prompt (before/after) | svc-ai-gateway config | [ ] |

---

### Scenario B: Excessive Agency / Unauthorized Actions

**Threat References:** OWASP LLM08, MITRE ATLAS AML.T0040
**AI Threat Catalog:** ATC-07, ATC-10
**Attack Tree:** Path 1, Node 1.1.3; Path 4

#### B.1 Detection Triggers

- [ ] **Unexpected workflow execution**: svc-automation executes a workflow not initiated by an authorized user or expected trigger
- [ ] **Permission escalation pattern**: AI-initiated action targets a service or resource outside its authorized scope
- [ ] **Action volume anomaly**: unusual number of svc-automation executions in a short window originating from AI input
- [ ] **Destructive action attempt**: AI attempts to trigger a workflow classified as destructive (data deletion, credential rotation, infrastructure change)
- [ ] **Cross-service chain**: AI triggers a sequence of actions across multiple integrated services (database + messaging + API) without a corresponding user request
- [ ] **Monitoring platform alert**: resource utilization spike in svc-automation correlated with AI gateway activity

#### B.2 Triage Checklist (0-10 minutes)

- [ ] **Step B.2.1**: Identify which workflows were triggered:
  ```bash
  # List recent svc-automation executions
  curl -s -H "X-N8N-API-KEY: $CD_N8N_KEY" \
    http://localhost:<automation-port>/api/v1/executions?limit=50 | \
    jq '.data[] | {id, workflowId: .workflowData.name, status: .finished, startedAt}'
  ```

- [ ] **Step B.2.2**: Determine what actions were actually executed:
  ```bash
  # Check svc-db for action details
  docker exec svc-db psql -U <admin_user> -d <db_name> -c \
    "SELECT id, workflow_id, mode, status, started_at, finished_at FROM execution_entity WHERE started_at > NOW() - INTERVAL '2 hours' ORDER BY started_at DESC;"
  ```

- [ ] **Step B.2.3**: Identify the AI input that triggered the action chain:
  ```bash
  docker logs --since 2h svc-ai-gateway 2>&1 | grep -B 5 -A 5 "webhook\|action\|workflow"
  ```

- [ ] **Step B.2.4**: Assess the impact of executed actions:
  - Were any database records modified or deleted?
  - Were any messages sent to external parties?
  - Were any API calls made to third-party services?
  - Were any infrastructure configurations changed?

- [ ] **Step B.2.5**: Assign severity per Section 3. If infrastructure actions executed: SEV-1. If non-destructive but unauthorized: SEV-2.

#### B.3 Containment (10-30 minutes)

- [ ] **Step B.3.1**: Immediately disable the AI-to-automation integration:
  ```bash
  # Deactivate all AI-triggered workflows
  # Identify webhook-triggered workflows and deactivate
  curl -s -H "X-N8N-API-KEY: $CD_N8N_KEY" \
    http://localhost:<automation-port>/api/v1/workflows | \
    jq '.data[] | select(.active == true) | {id, name}'

  # Deactivate each AI-connected workflow
  curl -X PATCH -H "Content-Type: application/json" \
    -H "X-N8N-API-KEY: $CD_N8N_KEY" \
    http://localhost:<automation-port>/api/v1/workflows/<workflow_id> \
    -d '{"active": false}'
  ```

- [ ] **Step B.3.2**: Lock workflow credentials to prevent further authenticated actions:
  ```bash
  # Rotate the master orchestrator webhook secret if applicable
  # Update svc-automation environment variables
  docker compose restart svc-automation
  ```

- [ ] **Step B.3.3**: If the AI is still generating action requests, stop svc-ai-gateway:
  ```bash
  # OpenClaw runs standalone, not under compose
  docker stop svc-ai-gateway
  ```

- [ ] **Step B.3.4**: Preserve execution state before any cleanup:
  ```bash
  # Export svc-automation full execution log
  docker logs svc-automation > /tmp/evidence_automation_full_$(date +%Y%m%d_%H%M%S).txt 2>&1

  # Export svc-db execution records
  docker exec svc-db pg_dump -U <admin_user> -d <db_name> -t execution_entity \
    > /tmp/evidence_execution_entity_$(date +%Y%m%d_%H%M%S).sql
  ```

#### B.4 Eradication (30-90 minutes)

- [ ] **Step B.4.1**: Audit all AI-triggered actions during the incident window:
  - Generate a complete list of every workflow execution, target service, and result
  - Cross-reference against authorized action allowlist

- [ ] **Step B.4.2**: Reverse unauthorized actions where possible:
  - Database modifications: restore from backup or reverse the specific changes
  - Sent messages: retract or send corrections
  - API calls: review for side effects and remediate
  - Document any irreversible actions and their impact

- [ ] **Step B.4.3**: Update the action allowlist to prevent recurrence:
  - Restrict which workflow endpoints the AI can trigger
  - Add rate limits per action type per time window
  - Implement human approval gates for any newly identified sensitive actions

- [ ] **Step B.4.4**: Review and tighten the AI system prompt regarding action boundaries:
  - Explicitly define prohibited actions
  - Add confirmation requirements for multi-step action chains
  - Limit the scope of single-request action authority

#### B.5 Recovery (30-60 minutes)

- [ ] **Step B.5.1**: Re-enable svc-ai-gateway with updated configuration:
  ```bash
  # OpenClaw runs standalone
  docker start svc-ai-gateway
  ```

- [ ] **Step B.5.2**: Re-enable AI-to-automation integration with new guardrails:
  - Reactivate workflows one at a time
  - Verify each workflow has appropriate input validation
  - Confirm human approval gates are functional for sensitive actions

- [ ] **Step B.5.3**: Implement or verify human-in-the-loop controls:
  - Destructive actions require explicit operator confirmation
  - Multi-service action chains require step-by-step approval
  - Action budget (maximum actions per session) is enforced

- [ ] **Step B.5.4**: Monitor AI-initiated actions for 48 hours:
  ```bash
  # Review daily execution summary
  docker exec svc-db psql -U <admin_user> -d <db_name> -c \
    "SELECT workflow_id, COUNT(*) as exec_count, MIN(started_at), MAX(started_at) FROM execution_entity WHERE started_at > NOW() - INTERVAL '24 hours' GROUP BY workflow_id ORDER BY exec_count DESC;"
  ```

#### B.6 Evidence Collection

| Artifact | Location | Collected? |
|----------|----------|------------|
| svc-automation execution logs | `/tmp/evidence_automation_full_*.txt` | [ ] |
| svc-db execution history dump | `/tmp/evidence_execution_entity_*.sql` | [ ] |
| AI gateway action request logs | `docker logs svc-ai-gateway` | [ ] |
| Monitoring platform workflow traces | Datadog dashboard export | [ ] |
| Action allowlist (before/after) | svc-ai-gateway / svc-automation config | [ ] |
| Workflow configurations | svc-automation workflow exports | [ ] |

---

### Scenario C: Data Exfiltration via AI Inference

**Threat References:** OWASP LLM06
**AI Threat Catalog:** ATC-05
**Attack Tree:** Path 1, Nodes 1.3.1-1.3.2; Path 3

#### C.1 Detection Triggers

- [ ] **Sensitive data in outbound API calls**: PII, credentials, or internal architecture details detected in prompts sent to the Anthropic API
- [ ] **PII in AI responses**: AI output contains personally identifiable information, database contents, or credential material
- [ ] **Unusual data patterns in prompts**: prompts contain structured data (database query results, configuration files, environment variables) that should not be sent externally
- [ ] **System prompt extraction**: AI response contains verbatim or paraphrased system prompt contents
- [ ] **Monitoring platform alert**: log analysis detects sensitive patterns in AI gateway traffic
- [ ] **Network anomaly**: unusual outbound data volume from svc-ai-gateway to Anthropic API endpoints

#### C.2 Triage Checklist (0-15 minutes)

- [ ] **Step C.2.1**: Identify what data was exposed:
  ```bash
  # Review AI gateway logs for sensitive content
  docker logs --since 2h svc-ai-gateway 2>&1 | \
    grep -i "password\|token\|key\|secret\|ssn\|credit.card\|@.*\.com"
  ```

- [ ] **Step C.2.2**: Determine the destination of the exfiltrated data:
  - Was it sent to the Anthropic API (external)?
  - Was it returned in a Telegram response (user-facing)?
  - Was it logged to monitoring platform (internal but persistent)?
  - Was it passed to an svc-automation workflow?

- [ ] **Step C.2.3**: Determine if the exfiltration was adversarial (injection-driven) or accidental (user-initiated or system design):
  - Did a prompt injection cause the AI to dump context?
  - Did a user inadvertently include sensitive data in their request?
  - Did an svc-automation workflow pass sensitive data to the AI as context?

- [ ] **Step C.2.4**: Scope the breach:
  - What specific data types were exposed? (PII, credentials, architecture details, source code)
  - How many records or data points were disclosed?
  - Over what time period did the exposure occur?

- [ ] **Step C.2.5**: Assign severity per Section 3. If confirmed credentials or PII sent externally: SEV-1. If internal data in responses or system prompt leaked: SEV-2.

#### C.3 Containment (5-20 minutes)

> **PRIORITY:** Stop external data flow immediately. Switch to local-only inference if AI capability is still needed.

- [ ] **Step C.3.1**: Block external AI API calls from svc-ai-gateway:
  ```bash
  # Block outbound traffic from svc-ai-gateway to external APIs.
  # Use the DOCKER-USER chain (the canonical chain for filtering container
  # traffic on Docker bridge networks; FORWARD-chain rules can be
  # overridden by the auto-managed DOCKER chain).
  CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' svc-ai-gateway)

  # Block outbound HTTPS to Anthropic API
  iptables -I DOCKER-USER -s $CONTAINER_IP -p tcp --dport 443 -j DROP
  ```

- [ ] **Step C.3.2**: If AI capability is needed during the incident, redirect to local inference:
  ```bash
  # svc-llm (Ollama) operates locally with no external API calls.
  # Note: the `ollama` action in MASTER_ORCHESTRATOR_V1 has been removed.
  # The svc-llm container still runs and is callable directly via the
  # Ollama HTTP API on port 11434 (e.g., POST /api/generate, /api/chat).
  # Workflows that previously used the n8n `ollama` action need to call
  # the Ollama API directly via an HTTP Request node.
  ```

- [ ] **Step C.3.3**: Preserve evidence of the exfiltration:
  ```bash
  # Export AI gateway logs covering the exfiltration window
  docker logs svc-ai-gateway > /tmp/evidence_exfiltration_$(date +%Y%m%d_%H%M%S).txt 2>&1

  # Capture network traffic if still active
  ssh root@10.100.1.10 "tcpdump -i any -w /tmp/evidence_network_capture.pcap host api.anthropic.com -c 1000" &
  ```

- [ ] **Step C.3.4**: If credentials were exfiltrated, immediately rotate them:
  - Follow IR-PLAY-002 (Leaked Credential) for credential rotation procedures
  - Prioritize credentials that were confirmed in the exfiltrated data

#### C.4 Eradication (30-90 minutes)

- [ ] **Step C.4.1**: Implement output filtering on svc-ai-gateway:
  - Add regex-based PII detection rules (SSN, email, credit card, API key patterns)
  - Configure filtering to scrub sensitive patterns before external API transmission

- [ ] **Step C.4.2**: Implement prompt sanitization:
  - Add pre-processing step that strips known sensitive patterns from user inputs before they reach the AI model
  - Sanitize svc-automation workflow outputs before they are injected as AI context

- [ ] **Step C.4.3**: Review and restrict what context the AI system receives:
  - Audit all data sources that feed into AI prompts
  - Remove unnecessary sensitive context from system prompts
  - Ensure database query results are filtered before AI processing

- [ ] **Step C.4.4**: Implement DLP (Data Loss Prevention) rules for AI traffic:
  ```bash
  # Add monitoring rules to detect sensitive data patterns in AI traffic
  # Configure Fluentd to flag sensitive patterns in log output
  # Add monitoring platform alert for PII patterns in AI gateway logs
  ```

#### C.5 Recovery (30-60 minutes)

- [ ] **Step C.5.1**: Assess breach scope and notification requirements:
  - Was the data subject to any regulatory requirements (PII, PHI)?
  - Does the Anthropic data processing agreement cover this scenario?
  - Are there breach notification obligations?

- [ ] **Step C.5.2**: Restore external API access with controls:
  ```bash
  # Remove iptables block
  iptables -D DOCKER-USER -s $CONTAINER_IP -p tcp --dport 443 -j DROP

  # Restart svc-ai-gateway with updated filtering. OpenClaw is standalone.
  docker restart svc-ai-gateway
  ```

- [ ] **Step C.5.3**: Validate that filtering is working:
  - Send test prompts containing synthetic sensitive data
  - Verify the data is scrubbed before external API transmission
  - Verify AI responses do not contain sensitive patterns

- [ ] **Step C.5.4**: Monitor outbound AI traffic for 72 hours:
  ```bash
  # Review AI gateway logs daily for sensitive pattern leakage
  docker logs --since 24h svc-ai-gateway 2>&1 | \
    grep -c -i "password\|token\|key\|secret\|ssn\|credit.card"
  ```

#### C.6 Evidence Collection

| Artifact | Location | Collected? |
|----------|----------|------------|
| AI gateway logs (exfiltration window) | `/tmp/evidence_exfiltration_*.txt` | [ ] |
| Network capture (if taken) | `/tmp/evidence_network_capture.pcap` | [ ] |
| Monitoring platform request traces | Datadog dashboard export | [ ] |
| List of exposed data elements | Incident documentation | [ ] |
| Anthropic API usage logs | Anthropic dashboard / billing | [ ] |
| Prompt/response pairs containing sensitive data | Extracted from gateway logs | [ ] |

---

### Scenario D: AI Model Supply Chain Compromise

**Threat References:** OWASP LLM03, MITRE ATLAS AML.T0018, AML.T0043
**AI Threat Catalog:** ATC-04
**Attack Tree:** Path 2, all nodes

#### D.1 Detection Triggers

- [ ] **Model hash mismatch**: checksum of pulled model does not match published/expected hash
- [ ] **Unexpected model behavior change**: AI outputs deviate from established baseline after a model update or without any configuration change
- [ ] **Upstream vendor advisory**: Anthropic, Ollama, or Whisper project publishes a security advisory affecting deployed model versions
- [ ] **CI/CD pipeline alert**: Trivy scan detects new CVE in AI container image; Cosign signature verification fails
- [ ] **Container image tampering**: image digest does not match the expected digest from the registry
- [ ] **Anomalous inference patterns**: model produces outputs with unexpected biases, hallucination patterns, or refusal behavior changes

#### D.2 Triage Checklist (0-15 minutes)

- [ ] **Step D.2.1**: Identify which AI system is affected:

  | System | Verification Method |
  |--------|-------------------|
  | AI-001 (svc-ai-gateway) | Check OpenClaw container image digest; Anthropic API model version is managed upstream |
  | AI-002 (svc-llm) | Check Ollama model metadata + local blob digests against last known-good values |
  | AI-003 (svc-transcription) | Check Whisper container image digest and model weight hash |

- [ ] **Step D.2.2**: Verify model integrity:
  ```bash
  # Check container image digests
  docker images --digests --format "{{.Repository}}:{{.Tag}} {{.Digest}}" | grep -E "ollama|whisper|openclaw"

  # For svc-llm (Ollama): check model metadata
  docker exec svc-llm ollama show <MODEL_NAME> --modelfile 2>/dev/null

  # For container images: compare against known-good digest
  docker inspect svc-ai-gateway --format '{{.Image}}'
  docker inspect svc-llm --format '{{.Image}}'
  docker inspect svc-transcription --format '{{.Image}}'
  ```

- [ ] **Step D.2.3**: Check when the model or image was last updated:
  ```bash
  # Check container creation time
  docker inspect --format '{{.Created}}' svc-ai-gateway svc-llm svc-transcription

  # Check Docker pull history
  docker history $(docker inspect --format '{{.Image}}' svc-llm) --no-trunc
  ```

- [ ] **Step D.2.4**: Determine if the compromise affects model behavior:
  - Test with known-good prompt/response pairs (baseline comparison)
  - Check for unexpected refusal patterns, bias shifts, or output format changes

- [ ] **Step D.2.5**: Assign severity. If confirmed model tampering with behavioral change: SEV-2. If hash mismatch without confirmed behavioral change: SEV-3. If vendor advisory only: SEV-4 until verified.

#### D.3 Containment (10-30 minutes)

- [ ] **Step D.3.1**: Isolate the affected AI service:
  ```bash
  # Stop the affected service to prevent compromised inference.
  # For compose-managed services (svc-llm, svc-transcription):
  docker compose stop <affected_service>
  # e.g., docker compose stop svc-llm
  # For svc-ai-gateway (OpenClaw runs standalone):
  # docker stop svc-ai-gateway
  ```

- [ ] **Step D.3.2**: Block model updates to prevent further supply chain compromise:
  ```bash
  # Block outbound connections from svc-llm to Ollama registry
  CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' svc-llm)
  iptables -I DOCKER-USER -s $CONTAINER_IP -p tcp --dport 443 -j DROP
  ```

- [ ] **Step D.3.3**: If AI-001 (Anthropic API) is affected by an upstream compromise:
  - The model runs externally; containment means stopping API calls
  - Block outbound from svc-ai-gateway (same as Scenario C, Step C.3.1)
  - Switch critical AI tasks to svc-llm (local) if it is unaffected. Note: the n8n `ollama` action was removed; route via direct HTTP to the Ollama API on port 11434.

- [ ] **Step D.3.4**: Preserve the potentially compromised model artifacts:
  ```bash
  # Export the container with the compromised model
  docker export svc-llm > /tmp/evidence_model_container_$(date +%Y%m%d_%H%M%S).tar

  # Save model metadata
  docker exec svc-llm ollama show <MODEL_NAME> > /tmp/evidence_model_metadata.txt 2>&1
  ```

#### D.4 Eradication (30-90 minutes)

- [ ] **Step D.4.1**: Verify model provenance from a trusted source:
  ```bash
  # Note: Ollama does NOT publish per-model SHA-256 hashes the way Docker Hub
  # publishes image digests. Verify instead via two paths:
  #   1. Query the local manifest digest via the Ollama API:
  #        curl -s http://svc-llm:11434/api/show -d '{"name":"<MODEL_NAME>"}' | jq .
  #      Compare the returned digest to the digest captured on the prior pull.
  #   2. Hash the local blob files and compare across pulls:
  #        docker exec svc-llm sh -c 'sha256sum /root/.ollama/models/blobs/*'
  # Document the comparison result and store the prior baseline values.
  ```

- [ ] **Step D.4.2**: Pull a clean model from the trusted source:
  ```bash
  # Remove the potentially compromised model
  docker exec svc-llm ollama rm <MODEL_NAME>

  # Pull fresh from trusted registry
  docker exec svc-llm ollama pull <MODEL_NAME>

  # Capture the new model metadata and blob digests for baseline
  docker exec svc-llm ollama show <MODEL_NAME> --modelfile
  docker exec svc-llm sh -c 'sha256sum /root/.ollama/models/blobs/*'
  ```

- [ ] **Step D.4.3**: For container image compromise, rebuild from trusted images:
  ```bash
  # Remove compromised image
  docker compose down <service_name>
  docker rmi <image_name>:<tag>

  # Pull verified image
  docker compose pull <service_name>

  # Verify image signature only if Cosign signing is in place for this image.
  # Cosign verification is currently aspirational: docker-compose.yaml pins
  # digests but no Cosign verification policy is documented. Skip if not
  # configured.
  # cosign verify <image_name>:<tag>

  # Run Trivy scan on the new image
  trivy image <image_name>:<tag>
  ```

- [ ] **Step D.4.4**: Compare new model behavior against known-good baseline:
  - Run a set of standardized test prompts
  - Compare outputs against documented expected responses
  - Verify no unexpected behavioral patterns

#### D.5 Recovery (30-60 minutes)

- [ ] **Step D.5.1**: Deploy the verified clean model:
  ```bash
  docker compose up -d <service_name>
  ```

- [ ] **Step D.5.2**: Remove network restrictions added during containment:
  ```bash
  iptables -D DOCKER-USER -s $CONTAINER_IP -p tcp --dport 443 -j DROP
  ```

- [ ] **Step D.5.3**: Validate outputs against known-good baseline:
  - Run the full behavioral test suite
  - Confirm outputs match expected patterns
  - Verify integration with downstream svc-automation workflows

- [ ] **Step D.5.4**: Implement ongoing model integrity monitoring:
  - Record the current model hash as the new baseline
  - Set up periodic hash verification checks
  - Configure alerts for any model file changes

#### D.6 Evidence Collection

| Artifact | Location | Collected? |
|----------|----------|------------|
| Compromised model container export | `/tmp/evidence_model_container_*.tar` | [ ] |
| Model metadata (before remediation) | `/tmp/evidence_model_metadata.txt` | [ ] |
| Container image digests (before/after) | `docker images --digests` output | [ ] |
| Trivy scan results (before/after) | CI/CD pipeline output | [ ] |
| Cosign verification results | Terminal output | [ ] |
| Behavioral comparison results | Test prompt outputs (before/after) | [ ] |
| Vendor security advisory (if applicable) | Vendor website / email | [ ] |
| Model pull logs (timestamps, source) | `docker logs svc-llm` | [ ] |

---

## 5. Communication Matrix

This matrix aligns with POLICY_INCIDENT_RESPONSE.md §7. For P1 incidents, the policy requires internal notification within 15 minutes; the playbook's "Immediately" and "Within 10 min" rows are stricter and acceptable. External notifications follow POLICY_INCIDENT_RESPONSE.md §7.3: drafted by Communications Lead, reviewed by System Owner, transmitted only after explicit approval.

| Audience | SEV-1 | SEV-2 | SEV-3 | SEV-4 | Method |
|----------|-------|-------|-------|-------|--------|
| Incident Commander | Immediately | Within 15 min | Within 1 hour | Next business day | Direct message / phone |
| System Owner | Within 10 min | Within 30 min | Within 4 hours | Next business day | Direct message / phone |
| AI Model Provider (Anthropic) | If upstream compromise | If upstream advisory | - | - | Support ticket / email |
| Affected users (data breach) | Within 24 hours (HIPAA breach notification rule allows up to 60 days for individuals; 24h is the playbook's stricter target) | Within 48 hours | - | - | Email from `admin@example-ops.com` (after System Owner approval per POL-IR §7.3) |
| Legal / compliance | If PII breach confirmed | If data exposure suspected | - | - | Email to `admin@example-ops.com` |
| Cloud provider | If infrastructure action needed | - | - | - | Support ticket |

---

## 6. Evidence Preservation Checklist

This consolidated checklist covers all four scenarios. Collect all applicable artifacts.

| Artifact | Applicable Scenarios | Location | Collected? |
|----------|---------------------|----------|------------|
| AI gateway conversation/prompt logs | A, B, C | `docker logs svc-ai-gateway` | [ ] |
| svc-automation execution logs | A, B | `docker logs svc-automation` | [ ] |
| svc-automation execution database dump | A, B | `execution_entity` table in svc-db | [ ] |
| svc-db query logs (incident window) | B, C | `docker logs svc-db` | [ ] |
| Network capture (if taken) | C, D | `/tmp/evidence_network_capture.pcap` | [ ] |
| Container image digests | D | `docker images --digests` | [ ] |
| Model metadata and checksums | D | Ollama show output / image inspect | [ ] |
| Compromised model container export | D | `/tmp/evidence_model_container_*.tar` | [ ] |
| Monitoring platform dashboards | A, B, C, D | Datadog UI screenshots / export | [ ] |
| svc-detection alerts (incident window) | A, B, C, D | `docker logs svc-detection` | [ ] |
| svc-detection-router events | A, B, C, D | `docker logs svc-detection-router` | [ ] |
| Telegram message logs (if applicable) | A | Bot API / chat export | [ ] |
| Trivy / Cosign scan results | D | CI/CD pipeline output | [ ] |
| Vendor security advisories | D | Vendor email / website | [ ] |
| SHA-256 hash manifest of all evidence | A, B, C, D | `/tmp/evidence_manifest_sha256.txt` | [ ] |

After collecting all applicable artifacts:

```bash
# Generate hash manifest for evidence integrity
sha256sum /tmp/evidence_* > /tmp/evidence_manifest_sha256.txt

# Transfer evidence to secure off-node location
# Do NOT store evidence solely on the potentially compromised host
```

---

## 7. Post-Incident Activities

All AI incidents require the following post-incident activities within 72 hours:

### 7.1 Lessons Learned

- [ ] Complete the incident timeline with exact timestamps:
  - When did the AI incident begin?
  - When was it detected?
  - Mean Time to Detect (MTTD) target: < 5 minutes (aligned to POLICY_INCIDENT_RESPONSE.md §9)
  - Detection-to-containment time (target: <15 minutes)
  - Total incident duration and service impact window

- [ ] Identify root cause:
  - Was this a novel attack or a known technique?
  - Did existing controls fail, or was there a control gap?
  - Was the AI system configured within policy (AI Governance Policy, POL-AI-001)?

- [ ] Write a post-incident report containing:
  - Executive summary
  - Timeline of events
  - AI system(s) affected and scope of impact
  - Attack technique classification (OWASP LLM / MITRE ATLAS reference)
  - Data or systems affected
  - Remediation actions taken
  - Lessons learned
  - Action items with owners and due dates

### 7.2 Threat Model Updates

- [ ] Update the STRIDE Threat Model (`THREAT_MODEL_STRIDE.md`) if a new threat category or vector was identified
- [ ] Update the Attack Tree (`ATTACK_TREE_AI_PIPELINE.md`) if a new attack path was exploited
- [ ] Update the AI Threat Catalog (`AI_THREAT_CATALOG.md`) with:
  - Revised control status for affected threats
  - New detection gaps identified
  - Updated residual risk ratings

### 7.3 Control Gap Remediation

- [ ] Create POA&M entries (`POAM_PLAN_OF_ACTION.md`) for any new control gaps identified
- [ ] Update AI Governance Policy (`POLICY_AI_GOVERNANCE.md`) if policy gaps contributed to the incident
- [ ] Review and update input validation / output filtering rules
- [ ] Review and update action allowlists and human approval gates
- [ ] Verify detection rules would catch this incident pattern going forward

### 7.4 Documentation Updates

- [ ] Update this playbook with any lessons learned or procedure improvements
- [ ] Update the SSP (`SSP_SYSTEM_SECURITY_PLAN.md`) if control implementations changed
- [ ] Update the Risk Assessment (`RISK_ASSESSMENT.md`) if risk ratings need adjustment
- [ ] Schedule a post-incident review meeting within 5 business days

---

## 8. Cross-References

### 8.1 Threat Modeling Documents

| Document | Relationship |
|----------|-------------|
| [THREAT_MODEL_STRIDE.md](THREAT_MODEL_STRIDE.md) | STRIDE threat categories T-01 (Tampering/Injection), I-01/I-03 (Information Disclosure), E-02/E-04 (Elevation of Privilege) map to Scenarios A-D |
| [ATTACK_TREE_AI_PIPELINE.md](ATTACK_TREE_AI_PIPELINE.md) | Path 1 (Prompt Injection → Unauthorized Actions), Path 2 (Supply Chain), Path 3 (Data Exfiltration), Path 4 (Lateral Movement) |
| [AI_THREAT_CATALOG.md](AI_THREAT_CATALOG.md) | ATC-01/02 (Injection) → Scenario A; ATC-07/10 (Agency/Lateral) → Scenario B; ATC-05 (Disclosure) → Scenario C; ATC-04 (Supply Chain) → Scenario D |

### 8.2 Existing Playbooks

| Playbook | When to Escalate |
|----------|-----------------|
| [PLAYBOOK_COMPROMISED_CONTAINER.md](PLAYBOOK_COMPROMISED_CONTAINER.md) (IR-PLAY-001) | AI container itself is compromised (shell access, crypto miner, reverse shell) - not just adversarial AI behavior |
| [PLAYBOOK_LEAKED_CREDENTIAL.md](PLAYBOOK_LEAKED_CREDENTIAL.md) (IR-PLAY-002) | Credentials discovered in AI logs, prompts, or responses; follow IR-PLAY-002 for rotation procedures alongside this playbook |
| [PLAYBOOK_DDOS_SERVICE_DEGRADATION.md](PLAYBOOK_DDOS_SERVICE_DEGRADATION.md) (IR-PLAY-003) | AI resource exhaustion causes platform-wide degradation (Scenario D of IR-PLAY-003 Section 3 applies) |
| [PLAYBOOK_UNAUTHORIZED_ACCESS.md](PLAYBOOK_UNAUTHORIZED_ACCESS.md) (IR-PLAY-004) | AI-triggered action results in creation of unauthorized accounts or access paths |

### 8.3 Governance Documents

| Document | Relationship |
|----------|-------------|
| [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) | NIST 800-53 controls SI-4, SI-3, IR-4, IR-5, IR-6 implementations |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | Remediation tracking for AI-related control gaps |
| [POLICY_AI_GOVERNANCE.md](POLICY_AI_GOVERNANCE.md) | AI risk register (AI-R01 through AI-R10) |
| [POLICY_AI_GOVERNANCE.md](POLICY_AI_GOVERNANCE.md) | AI risk tolerance, lifecycle management, human oversight requirements |
| [POLICY_INCIDENT_RESPONSE.md](POLICY_INCIDENT_RESPONSE.md) | Overarching IR policy governing all playbook activation |

---

## 9. NIST 800-53 Control Mapping

| Control | Description | Playbook Coverage |
|---------|-------------|-------------------|
| IR-4 | Incident Handling | All scenarios, all phases |
| IR-4(1) | Automated Incident Handling Processes | Detection triggers (monitoring platform alerts, log analysis) |
| IR-5 | Incident Monitoring | Detection triggers across all scenarios |
| IR-6 | Incident Reporting | Post-incident report (Section 7) |
| SI-3 | Malicious Code Protection | Scenario D (supply chain - model integrity verification) |
| SI-4 | Information System Monitoring | All detection triggers, monitoring platform integration |
| SI-4(2) | Automated Tools for Real-Time Analysis | svc-detection eBPF monitoring, monitoring platform log analysis |
| SI-4(5) | System-Generated Alerts | Detection triggers across all scenarios |
| SI-10 | Information Input Validation | Scenario A (input filtering), Scenario C (prompt sanitization) |
| AC-6 | Least Privilege | Scenario B (action allowlists, permission boundaries) |
| AU-6 | Audit Review, Analysis, and Reporting | Evidence preservation, post-incident log review |
| AU-9 | Protection of Audit Information | Evidence hash manifest, off-node transfer |
| SC-7 | Boundary Protection | Scenario C (outbound traffic blocking), Scenario D (model update blocking) |
| CP-10 | Information System Recovery | Recovery phases across all scenarios |

---

## 10. Quick Reference Card

**For use during an active AI incident, tear-off summary:**

```
SCENARIO A: PROMPT INJECTION
1. PRESERVE: docker logs svc-ai-gateway > /tmp/evidence_ai_*.txt
2. BLOCK:    Block attacker input (Telegram chat ID / API source)
3. DISABLE:  Deactivate AI to svc-automation workflows
4. ANALYZE:  Review injection payload and triggered actions
5. HARDEN:   Update input filters and system prompt
6. RESTORE:  docker restart svc-ai-gateway, re-enable workflows, validate

SCENARIO B: EXCESSIVE AGENCY
1. DISABLE:  Deactivate all AI-triggered workflows immediately
2. PRESERVE: Export execution logs and svc-db records
3. AUDIT:    List all AI-triggered actions during incident window
4. REVERSE:  Undo unauthorized actions where possible
5. TIGHTEN:  Update action allowlist and add human approval gates
6. RESTORE:  Re-enable workflows one at a time, monitor 48h

SCENARIO C: DATA EXFILTRATION
1. BLOCK:    iptables DROP on DOCKER-USER, outbound 443 from svc-ai-gateway
2. SWITCH:   Call Ollama API directly on port 11434 if local AI needed
3. ROTATE:   Rotate any exposed credentials (see IR-PLAY-002)
4. FILTER:   Implement PII scrubbing on prompts and responses
5. ASSESS:   Scope breach, check notification requirements
6. RESTORE:  Re-enable external API with filtering, monitor 72h

SCENARIO D: SUPPLY CHAIN
1. STOP:     docker compose stop <affected_service> (or docker stop svc-ai-gateway)
2. EXPORT:   docker export <container> > /tmp/evidence_model_*.tar
3. VERIFY:   Compare Ollama /api/show digest and blob sha256 to baseline
4. PULL:     Pull clean model from trusted registry
5. SCAN:     trivy image (Cosign only if signing policy active)
6. RESTORE:  Deploy verified model, validate against baseline
```

---

## When the incident involves Squire (Phase 17)

> **Key Point:** Squire incidents require evidence capture from Langfuse traces plus the ir_investigations table in addition to the standard AI incident response steps above. HITL token revocation is the immediate isolation action.

### Squire-specific isolation sequence

1. Revoke the X-Squire-Token at the Cloudflare edge to stop ingress.
2. Block the alert source at Cloudflare WAF.
3. Query `ir_investigations` for the affected verdicts and record the trace IDs.
4. Export the Langfuse trace tree for each trace ID to the incident evidence folder.
5. Snapshot `ir_alerts`, `ir_chunks`, `ir_investigations`, `ir_rotation_events` tables for forensics.
6. If guardrail bypass is suspected, freeze `svc-nemo-config` and schedule a rail coverage regression in staging.

### Squire-specific containment

<!-- TODO(et): confirm that disable_alert_ingress.sh and run_rail_coverage.sh exist in builds/squire/ or document where they live. They are referenced here but not located in the public corrections cluster. -->

```
# Disable /alert ingress at Squire container level (does not require compose down)
ssh host-alpha 'docker exec svc-squire /opt/platform/scripts/disable_alert_ingress.sh'

# Verify rail coverage is intact
ssh host-alpha 'docker exec svc-nemo /opt/platform/nemo-config/run_rail_coverage.sh'

# Replay the incident payload against the current rail config
python -m squire.replay --trace-id <trace_id> --env staging
```

### Squire-specific evidence

| Artifact | Location | Retention |
|----------|----------|-----------|
| Langfuse trace tree | ClickHouse via Langfuse UI export | 90 days |
| ir_investigations row | `svc-db` postgres table `ir_investigations` | 365 days |
| ir_rotation_events audit trail | `svc-db` postgres table `ir_rotation_events` | 3 years |
| Pre-graph scanner result | Langfuse span attribute `pre_graph_pii.result` | 90 days |
| NeMo rail decision log | NeMo container stdout, Datadog log retention | 15 days |

Cross-reference: `AI_AUDIT_TRAIL_SPEC.md` for full replay procedure; `HITL_POLICY.md` for token revocation; `REDTEAM_RESULTS.md` for known attack patterns; `POAM_PLAN_OF_ACTION.md` POAM-P17 cluster for tracked Phase 17 issues.

## Squire Agent Incidents (plan 17-14)

This subsection enumerates the three primary Squire incident classes and maps each to NIST CSF 2.0 subcategories, MITRE ATLAS tactics, and Phase 17 response artifacts.

### Case A: Jailbreak via prompt injection

Squire produces a recommendation that contradicts the source alert (for example, recommends halting svc-n8n for a phishing alert delivered through n8n). Classic symptom of role-hijack injection.

| Mapping | Reference |
|---------|-----------|
| CSF 2.0 | RS.AN-03 (analyze impact), MG-4.3 (manage AI incidents) |
| ATLAS | AML.T0051 Prompt Injection |
| Threat model | `SQUIRE_THREAT_MODEL.md` section 2.2 |
| Tabletop | `SQUIRE_TABLETOP_EXERCISE.md` full scenario |
| POAM | P17-11 (novel injection coverage gap) |
| Response lead | Incident Commander |

Quick response:

1. Operator confirms suspicion on Telegram recommendation.
2. Rotate `SQUIRE_WEBHOOK_TOKEN` via Doppler (revokes ingress).
3. Stop svc-squire, keep all other services.
4. Langfuse trace diagnosis: check rail_outcomes for `INCONSISTENT_FLAG` from critique node.
5. Follow Phase 3 through 6 of `SQUIRE_TABLETOP_EXERCISE.md`.

### Case B: Hallucinated containment (runaway recommendation)

Squire drafts a destructive containment recommendation that slips past actions.yml rewrite because the phrasing used a synonym or paraphrase the allow-list did not anticipate.

| Mapping | Reference |
|---------|-----------|
| CSF 2.0 | RS.MA-01 (execute response plan), MG-4.3 |
| ATLAS | AML.T0051 Prompt Injection + excessive agency (OWASP LLM06) |
| Threat model | `SQUIRE_THREAT_MODEL.md` section 1.1 (svc-squire Elevation of Privilege row) |
| Tabletop | `SQUIRE_TABLETOP_EXERCISE.md` Phase 1 and 4 |
| POAM | P17-11 + new entry at time of incident |
| Response lead | Incident Commander |

Quick response:

1. Operator does not execute the recommendation under any circumstances; all destructive verbs require separate human approval per `HITL_POLICY.md`.
2. Update actions.yml allow-list with the observed synonym within the same release cycle.
3. Add regression test in `builds/squire/tests/test_redteam.py`.
4. Record in `REDTEAM_RESULTS.md` as a new case.

### Case C: Runaway loop (critique fails to converge)

Squire exhausts its 3 critique iterations without reaching APPROVED state; returns with `INCONSISTENT_FLAG`. Cost ceiling caps spend but operator receives ambiguous output.

| Mapping | Reference |
|---------|-----------|
| CSF 2.0 | RS.AN-03 (analyze impact), DE.CM-07 (monitoring) |
| ATLAS | AML.T0029 Model DoS (self-induced) |
| Threat model | `SQUIRE_THREAT_MODEL.md` section 2.4 |
| Tabletop | `SQUIRE_TABLETOP_EXERCISE.md` Phase 3 |
| POAM | Open new entry if pattern repeats more than 2 times in 30 days |
| Response lead | SOC Analyst |

Quick response:

1. SOC Analyst treats INCONSISTENT output as unverified; does not forward to on-call.
2. Pull Langfuse trace, examine critique node costs per iteration.
3. If recurring pattern, adjust iteration cap or classifier prompt per change control.

### Cross-reference to 17-14 artifacts

| Artifact | Use |
|----------|-----|
| `SQUIRE_THREAT_MODEL.md` | Tactic ID lookup, residual rating, control mapping |
| `SQUIRE_TABLETOP_EXERCISE.md` | Runbook for the full jailbreak recovery flow |
| `diagrams/squire-atlas-threat-model.png` | Incident command briefing visual |
| `diagrams/squire-state-machine.png` | Node-level diagnosis reference |
| `diagrams/squire-data-flow.png` | Evidence capture scope |

---

*This playbook SHALL be updated after any AI-related security incident, when new AI systems are deployed, when AI integration scope changes, or when new OWASP LLM or MITRE ATLAS techniques relevant to this environment are published. The next scheduled review is 2026-09-12.*
