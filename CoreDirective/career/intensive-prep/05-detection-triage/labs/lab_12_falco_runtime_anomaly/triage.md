# Lab 12: Falco Triage Drill

10 alerts. Triage each in under 5 minutes. Decide: TP / FP / Inconclusive. Score severity. Action.

Use the worksheet below. Then compare to the answer key at the bottom.

## Alerts to Triage

```bash
cd labs/lab_12_falco_runtime_anomaly
jq -c '{ts: .time, rule, priority, container: .output_fields["container.name"], image: .output_fields["container.image.repository"]}' falco.json
```

Print each alert one at a time and triage.

## Worksheet (one per alert)

```
ALERT N
Rule:
Container/Image:
Verdict (TP/FP/Inconclusive):
Asset criticality (1-4):
Threat severity (1-4):
Priority (1-16):
Action (auto-respond/escalate/page/suppress/tune):
Comms (one sentence):
Detection improvement note:
```

## Answer Key (review after triaging)

### Alert 1 — Terminal shell in cd-service-n8n (19:14:01)
- **Verdict**: True Positive likely. The n8n container should never spawn an interactive shell as root in production. If you started one yourself for debugging, mark TP-but-authorized and document.
- **Criticality**: 4 (n8n holds workflow secrets, OAuth tokens, drives outbound API calls).
- **Severity**: 3.
- **Priority**: 12.
- **Action**: Escalate. Do not auto-respond, you might kill your own session. Verify with the owner first.
- **Comms**: "Shell spawned as root in cd-service-n8n at 19:14:01. Verifying whether this is sanctioned debug work."
- **Detection improvement**: Maintain a debug-window allowlist: shells spawned in service containers during a maintenance window (announced in #infra) should not page.

### Alert 2 — Read /etc/shadow in cd-service-n8n (19:14:05)
- **Verdict**: TP. n8n has zero reason to read /etc/shadow.
- **Criticality**: 4. **Severity**: 4. **Priority**: 16.
- **Action**: Page on-call. Pair with alert 1 (same container, 4 seconds later).
- **Comms**: "cd-service-n8n executed cat /etc/shadow at 19:14:05, 4 seconds after a shell spawn. Investigating compromise."
- **Detection improvement**: rule level Critical. Pair with shell spawn in same container as auto-correlation.

### Alert 3 — Outbound to 45.135.232.8:4444 from cd-service-n8n (19:14:12)
- **Verdict**: TP, Critical.
- **Criticality**: 4. **Severity**: 4. **Priority**: 16.
- **Action**: Page on-call (same incident as 1+2). Network-isolate the container. Snapshot for forensics.
- **Comms**: "cd-service-n8n outbound to 45.135.232.8:4444 with curl. C2 confirmed. Containing."
- **Detection improvement**: Add 45.135.232.8 to threat intel watchlist. Hunt for any other contact across NetFlow.

### Alert 4 — Write below /etc in cd-service-n8n (19:14:30)
- **Verdict**: TP, persistence. /etc/cron.d/persistence is on-the-nose.
- **Criticality**: 4. **Severity**: 4. **Priority**: 16.
- **Action**: Same incident as 1-3. Now full incident response: rotate all n8n creds, snapshot the container, redeploy from clean image.
- **Comms**: "Persistence dropped at /etc/cron.d/persistence in cd-service-n8n. Full IR. All n8n creds rotating."
- **Detection improvement**: rule level should be Critical not Notice. Persistence in production containers is never benign.

### Alert 5 — Shell in cd-service-db doing pg_dumpall (19:30:11)
- **Verdict**: Inconclusive without context. Looks like a backup but should be running as the postgres user via the cron job, not via `bash -c`. The exact form here matches a manual or attacker-driven dump.
- **Criticality**: 4. **Severity**: 3 if attacker, 1 if legitimate backup.
- **Priority**: 12 if attacker.
- **Action**: Escalate. Check the scheduled backup job. If it ran, why is the cron user using bash. If it did not run, this is exfil.
- **Comms**: "pg_dumpall via bash -c in cd-service-db at 19:30. Verifying whether it is the scheduled backup or unauthorized."
- **Detection improvement**: tag the legitimate cron user/hash and exclude. Anything else is auto-page.

### Alert 6 — Shell in cd-service-vault (21:00:01)
- **Verdict**: TP. Vault should never have a shell. Hashicorp ships Vault as a static binary.
- **Criticality**: 4 (Vault holds secrets). **Severity**: 4. **Priority**: 16.
- **Action**: Page on-call immediately. Worst-case scenario for a secrets manager.
- **Comms**: "Shell spawned in cd-service-vault at 21:00:01. Vault is breached or being tampered with. Page on-call now."
- **Detection improvement**: Vault container should have a custom Falco rule with priority Critical for any process other than `vault`.

### Alert 7 — Privileged container util-pod started (21:00:08)
- **Verdict**: TP. Following alert 6 by 7 seconds. Same incident.
- **Criticality**: 4. **Severity**: 4. **Priority**: 16.
- **Action**: Same incident as 6. Privileged container is the attacker preparing for host escape.
- **Comms**: "util-pod with privileged=true spawned 7s after Vault shell. Containing host."
- **Detection improvement**: Pair this with alert 6 in the SIEM. Two Critical Falco alerts on the same host within 60 seconds is auto-page regardless of rule.

### Alert 8 — kubectl port-forward to pod/secrets-manager (22:14:15)
- **Verdict**: TP, Suspicious. kubectl port-forward bypasses ingress logging. Used for remote access to internal services.
- **Criticality**: 4 (the pod name is secrets-manager). **Severity**: 3. **Priority**: 12.
- **Action**: Escalate. Identify who initiated the port-forward (audit log lookup). If sanctioned, document. If not, page.
- **Comms**: "kubectl port-forward to secrets-manager pod from cd-alpha at 22:14:15. Verifying authorization."
- **Detection improvement**: K8s audit log correlation. Get the user.username from the matching API call.

### Alert 9 — Container started, prom/prometheus (23:01:42)
- **Verdict**: FP / Informational. Routine container start of monitoring tooling.
- **Criticality**: 2. **Severity**: 1. **Priority**: 2.
- **Action**: Suppress. This rule should not have priority Notice. Tune Falco config.
- **Comms**: none required.
- **Detection improvement**: Tune the Falco rule. Inbound/outbound traffic for known monitoring containers should be Informational only or excluded entirely.

### Alert 10 — mkdir /usr/local/bin/.hidden in cd-service-ollama (23:14:00)
- **Verdict**: TP, Persistence-like.
- **Criticality**: 3 (Ollama runs LLM inference, less critical than Vault but still production). **Severity**: 3. **Priority**: 9.
- **Action**: Escalate. Investigate. Ollama containers should not be modifying their own /usr/local/bin paths at runtime.
- **Comms**: "Ollama container created hidden directory in /usr/local/bin at 23:14. Investigating for tampering."
- **Detection improvement**: Tighten "Mkdir binary dirs" rule to Warning at minimum, page when combined with shell spawn.

## Pattern To Notice

Alerts 1, 2, 3, 4 are one incident: shell spawn -> sensitive file read -> C2 -> persistence. The Falco rules fire correctly but each as separate alerts. Senior engineering says: correlate at the SIEM. Any container with 3+ distinct Falco alerts within 60 seconds is an auto-page.

Alerts 6 + 7 are another incident. Shell in Vault followed by privileged container 7 seconds later. Same correlation rule catches both.

Alert 9 is the noise. Suppress and tune.

## Speed Drill

Goal: triage all 10 in under 30 minutes by alert 10. Then re-do, target 25 minutes. Then 20.

Decision speed is the senior signal. The exact severity is less important than the decisive output.
