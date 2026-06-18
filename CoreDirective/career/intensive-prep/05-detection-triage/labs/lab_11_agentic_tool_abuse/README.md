# Lab 11: Agentic Tool Abuse (n8n)

## Attack Narrative

The Content Research Pipeline workflow on n8n is designed to: fetch an article, summarize it via Anthropic, append the summary to Notion. Reasonable. Productive.

An attacker plants a prompt injection on a blog post that the workflow will fetch. When the n8n agent processes the article, the embedded instructions hijack its goal. Within seconds:

1. 11:42:00 HTTP Request fetches `https://attacker-controlled-blog.example/article-x`
2. 11:42:02 Anthropic Chat node processes the article (and the embedded instructions)
3. 11:42:05 Gmail Send to `attacker@evil.tld` with base64 of env vars
4. 11:42:11 GitHub Create Issue with AKIA cred in the body

A second incident at 15:00:
1. 15:00:00 Gmail Read of message `abc123` (potentially attacker-sent message containing instructions)
2. 15:00:09 Google Drive Share to `attacker@evil.tld` with writer role

Both follow the same pattern: untrusted ingest -> sensitive write within 30 seconds. The agent's sanctioned tools become the exfil channel.

## Detection Logic

Sequence detection on the execution log. Group by `execution_id` and `workflow_id`. Flag any execution where an untrusted-fetch node is followed by a sensitive-write node within 30 seconds.

This is the canonical detection for ATLAS AML.T0051.001 (Indirect Prompt Injection).

## Run It

```bash
cd labs/lab_11_agentic_tool_abuse
python3 detect.py n8n_executions.log
```

Expected: 2 sequences flagged (exec_002 and exec_004). exec_001 (Tavily + Notion append) and exec_003 (Telegram trigger + reply) are clean.

## Triage Outcome

Verdict: True Positive, Critical.

Page oncall. Disable the affected workflows. Pull the email and the GitHub issue body, redact and rotate. Rotate any creds the agent had access to (NPM_TOKEN, AWS keys, GitHub PAT). Block the attacker domains and email at egress and gmail-side.

Engineering followup. Rebuild the workflow with structural mitigations:
- The HTTP Request node and Gmail Send must not co-occur in the same workflow without a human approval node between them
- The agent's tool surface should be minimum necessary: research workflows do not need send_email or createIssue
- Add an n8n approval node that gates sensitive writes when the workflow trace includes any external fetch

Audit other workflows for the same anti-pattern. The Master Orchestrator V1 workflow has 16 actions including gmail and github. Tighten the guardrails: only the explicitly intended chains should be allowed.

## Interviewer Questions

- "What is indirect prompt injection?" Adversarial instructions embedded in content the LLM ingests via tools (web pages, emails, documents). The LLM cannot distinguish trusted system instructions from instructions in fetched content because both arrive as text. Researcher Kai Greshake formalized this in 2023.
- "Why is the n8n execution log a good detection source?" It is structured, includes the workflow ID, execution ID, node sequence, operation, and inputs. That is exactly what you need for sequence correlation. Most agentic platforms log similarly: LangSmith, Helicone, OpenAI Logs.
- "What is the structural fix?" Constrained tool surfaces. An agent that summarizes web articles does not need send_email. An agent that drafts emails should require human approval before send. Lean into capability-based design: each tool grants is justified.
- "How do you scale this detection across 100 workflows?" Build a metadata layer: every workflow gets a tag set of allowed tool combinations. Detection compares each execution's actual tool sequence to the allowed set, flags mismatches. Detection-as-code repo holds the allowlist next to the rules.
- "How does Dropzone or Prophet use this?" These AI SOC platforms could not exist without sequence telemetry. They consume execution logs from agent platforms (n8n, LangChain, LlamaIndex), apply detections like this one, and run their own LLM agent to triage. Recursive: an AI agent triages alerts about another AI agent.
- "What is MITRE ATLAS?" Adversarial Threat Landscape for Artificial Intelligence Systems. ATT&CK for ML. AML.T0051 covers Prompt Injection. AML.T0051.001 is Indirect specifically. Worth referencing in AI security interviews to signal you read AI-specific frameworks.
- "How does this map to ATT&CK?" T1190 (Exploit Public-Facing Application) for the gateway entry. T1041 (Exfiltration Over C2 Channel) for the agent-as-channel. ATLAS is the better mapping.

## Variant: Detection Plus Hardening

1. Tool gating policy in n8n: define allowed (fetch_tool, write_tool) pairs per workflow tag. Any other pair triggers an approval gate.
2. n8n custom node that runs a guardrail model on every external content ingest. Strip suspected injection markers, escape HTML comments.
3. Periodic adversarial test: red team posts content with injection on a sandbox blog. Workflow should refuse to act on the embedded instructions. CI runs this monthly.
4. Sigma rule converts to whatever your organization's SIEM is via sigma-cli. The detection logic does not depend on n8n specifically. Same pattern applies to LangChain, OpenAI Assistants, AWS Bedrock Agents.
