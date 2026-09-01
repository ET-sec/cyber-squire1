# Human-in-the-Loop (HITL) Policy

**Document ID:** POL-HITL-001
**Version:** 1.0
**Classification:** Internal Use Only
**Effective Date:** 2026-04-23
**Owner:** Information Security Officer
**Approved By:** System Owner
**NIST 800-53 Controls:** AC-3 (Access Enforcement), AC-6 (Least Privilege), CA-7 (Continuous Monitoring), IR-4 (Incident Handling), SI-4 (System Monitoring)

> **Status note (2026-09-01):** this policy describes the DO-era baseline; that environment was retired in 2026-08. A re-baseline against the current OCI stack is queued.

---

## Document Control

| Field | Value |
|-------|-------|
| Document ID | POL-HITL-001 |
| Version | 1.0 |
| Status | Approved |
| Last Revised | 2026-04-23 |
| Next Review | 2026-10-23 |
| Author | Information Security Officer |
| Approver | System Owner |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-23 | Information Security Officer | Initial HITL policy covering severity gates, token rotation, demo ephemeral tokens |

---

## 1. Purpose

Squire is advisory by design. It classifies, drafts, and recommends; it does not act. This policy defines where human review is mandatory, who qualifies as a reviewer, how fast they must respond, and how operational secrets that gate the HITL surface are rotated.

Two concerns are addressed together because they share infrastructure: the human gate on AI output, and the token discipline that controls who can invoke Squire in the first place.

---

## 2. Scope

This policy applies to:

- svc-squire on alpha-node (autonomous SOC analyst)
- The public `/alert` endpoint at https://squire.example-ops.com/alert
- The internal webhook path from svc-n8n and related integrations
- All demo and interview access paths to Squire
- The Langfuse UI at https://langfuse.example-ops.com where traces are reviewed

It does not apply to the foundation models themselves (Anthropic, OpenAI) which are external services governed by provider terms.

---

## 3. Mandatory Human Gates

Squire's output must be reviewed before any operator action in the following cases.

### 3.1 Severity-Based Gates

| Severity | Human Review Required | Max Time to Review |
|----------|----------------------|--------------------|
| LOW | No | N/A (auto-archive after 30 days) |
| MEDIUM | Optional, spot check | 72 hours |
| HIGH | Yes | 4 hours |
| CRITICAL | Yes, plus secondary approver | 1 hour |

Severity mapping to the canonical priority taxonomy in POL-IR-001 Section 4.1: CRITICAL = P1, HIGH = P2, MEDIUM = P3, LOW = P4.

A HIGH or CRITICAL investigation is marked `hitl_gate_triggered=true` and cannot be closed until a `ir_hitl_events` row with `event_type=approved` is written by a qualified reviewer.

### 3.2 Cost Ceiling Gates

Any investigation that would exceed the daily cost ceiling defaulting to $5 USD, configurable via `ANTHROPIC_DAILY_CEILING_USD` in docker-compose.yaml, is halted at the node boundary. The partial state is persisted and a HITL request is written. Resuming the invocation requires explicit approval.

### 3.3 Rail-Refusal Gates

If a NeMo rail refuses the draft or critique node output, the investigation is halted. The raw refusal is preserved in `ir_rail_events`. Rework requires either:

- Human rewrite of the sanitized input then re-invocation, or
- Documented policy exception from the system owner captured in `ir_hitl_events`

### 3.4 Autonomous-Verb Gates

The `actions.yml` allow-list is configured in `rewrite` mode. Any attempted autonomous verb in the draft is rewritten to advisory form, and the sanitization event is logged. No further gate is required, but the rewrite itself is considered a signal; sustained rewrite rate above 15% is a monitoring trip (see AI_AUDIT_TRAIL_SPEC.md section 8).

---

## 4. Roles

| Role | Responsibility | Qualification |
|------|----------------|---------------|
| Primary reviewer | First-line approval on HIGH and CRITICAL | System owner or designated operator with Teleport access |
| Secondary approver | Required on CRITICAL only | Second principal with Teleport access, distinct from primary |
| Policy owner | Maintains this policy, rotates tokens | Information Security Officer |
| Auditor | Validates HITL records quarterly | External or delegated internal |

Today the pool is the system owner acting as primary reviewer and policy owner. Secondary approver requirement is active on CRITICAL; if no secondary is available, the investigation escalates to manual handling (Teleport session, direct psql, no Squire automation).

---

## 5. SLA and Escalation

### 5.1 Review SLA

- HIGH: 4 hours from `ir_hitl_events` `requested` event to `approved` or `rejected`
- CRITICAL: 1 hour
- MEDIUM (optional): 72 hours

SLA clock runs on wall time, not business hours. Missed SLAs are themselves logged as `timed_out` events and are reviewed in the quarterly audit.

### 5.2 Escalation Chain

1. `requested` event fires, Telegram notification to the primary agent Telegram bot channel
2. After 50% of SLA without response, secondary notification via n8n Gmail workflow
3. After 100% of SLA without response, `timed_out` event auto-written; investigation remains in `pending_review` state indefinitely until manually closed

### 5.3 Override Authority

The system owner may override any HITL gate by writing an `ir_hitl_events` row with `event_type=approved` and `reason` containing the override rationale. Overrides are themselves audited and reviewed quarterly.

---

## 6. Token Rotation Policy

Squire's HITL surface depends on token hygiene. Two distinct token populations are governed here. Both rotate on a defined cadence and both rotate on event triggers.

### 6.1 Token Populations

| Population | Purpose | Consumers | Storage |
|------------|---------|-----------|---------|
| Production webhook token (`SQUIRE_WEBHOOK_TOKEN`) | Authenticates svc-n8n, Falco alert router, Datadog forwarder | Internal integrations on alpha-node and in the ops fabric | Doppler `<SECRETS_PROJECT>/<CONFIG>` |
| Per-interview ephemeral tokens (`SQUIRE_INTERVIEW_TOKENS` additive allow-list) | Short-lived demo access for interviewers | Human visitors with a signed interview link | Doppler, regenerated per session |

The populations are deliberately separate. A demo token leak during an interview must not compromise the production webhook population.

### 6.2 Production Token Rotation

Cadence: every 60 days, plus event-driven triggers.

Event triggers:

- Suspected leak (any sign of token material in a commit, log, or screenshot)
- Personnel change (any change to the team with production access)
- Post-incident (any investigation that touches the webhook trust boundary)
- Semester boundary (academic cycle alignment for demo scheduling clarity)

Rotation command sequence (run from a Teleport-gated session):

```bash
# Generate and set new production token in Doppler
doppler secrets set SQUIRE_WEBHOOK_TOKEN="$(openssl rand -hex 48)" \
  --project <SECRETS_PROJECT> --config prd

# Reload svc-squire on alpha-node to pick up the new token
ssh alpha-node 'cd /opt/platform/ && docker compose up -d --no-deps svc-squire'

# Verify the old token is rejected and the new token is accepted
# (OLD_TOKEN holds the pre-rotation value captured before the rotation step)
curl -s -o /dev/null -w "%{http_code}\n" \
  -H "x-squire-token: ${OLD_TOKEN}" \
  https://squire.example-ops.com/alert -X POST -d '{}'
# Expected: 401

curl -s -o /dev/null -w "%{http_code}\n" \
  -H "x-squire-token: $(doppler secrets get SQUIRE_WEBHOOK_TOKEN --plain)" \
  https://squire.example-ops.com/health
# Expected: 200
```

After rotation, update every integration that consumes the token (n8n credential, Falco alert router config, Datadog webhook destination). Rotation that leaves a stale consumer behind is logged as an incomplete rotation in the `ir_rotation_events` audit trail.

### 6.3 Per-Interview Ephemeral Tokens

Cadence: one token per interview session, invalidated at session end.

Mechanism: the application checks `SQUIRE_INTERVIEW_TOKENS`, a comma-separated additive allow-list distinct from `SQUIRE_WEBHOOK_TOKEN`. A request presenting a token from either population passes auth. The production token is never exposed to interview participants.

Generation and revocation pattern:

```bash
# Generate an ephemeral token for an interview
TOKEN_INTERVIEW=$(openssl rand -hex 24)

# Append to the additive allow-list in Doppler
CURRENT=$(doppler secrets get SQUIRE_INTERVIEW_TOKENS --plain 2>/dev/null)
doppler secrets set SQUIRE_INTERVIEW_TOKENS="${CURRENT:+${CURRENT},}${TOKEN_INTERVIEW}" \
  --project <SECRETS_PROJECT> --config prd

# Reload svc-squire on alpha-node
ssh alpha-node 'cd /opt/platform/ && docker compose up -d --no-deps svc-squire'

# Share TOKEN_INTERVIEW with the interviewer via a pre-signed link
# (delivery channel out of scope of this policy)

# After the interview completes: revoke by removing from the list
REMAINING=$(doppler secrets get SQUIRE_INTERVIEW_TOKENS --plain | \
  tr ',' '\n' | grep -v "^${TOKEN_INTERVIEW}$" | paste -sd, -)
doppler secrets set SQUIRE_INTERVIEW_TOKENS="$REMAINING" \
  --project <SECRETS_PROJECT> --config prd
ssh alpha-node 'cd /opt/platform/ && docker compose up -d --no-deps svc-squire'
```

Note: the additive allow-list consumer side (`SQUIRE_INTERVIEW_TOKENS` parsing in `app.py`) is planned under plan 17-15, which wires the portfolio-facing interview demo surface. This policy defines the procedure ahead of the mechanism; once 17-15 lands, the above flow activates without policy changes.

### 6.4 Leak Response

If a token (either population) is suspected leaked, the leaked token is rotated within 1 hour regardless of cadence. The leak response writes a `ir_rotation_events` row with `reason=suspected_leak` and attaches a Langfuse trace review covering the 24 hours preceding the suspected leak.

### 6.5 Audit

Every rotation writes to `ir_rotation_events` with:

- Population rotated
- Old token SHA-256 (never the raw value)
- New token SHA-256
- Actor principal
- Trigger (cadence, event, leak, other)
- Timestamp

Quarterly audit walks these rows to verify cadence compliance.

---

## 7. Language Discipline

Squire may not emit autonomous action language in any investigation output. The `actions.yml` rewrite enforces this by prepending `RECOMMEND: human operator should ...` to forbidden verbs. Reviewers are required to read the recommended action set in its rewritten form and translate to action themselves. The LLM is never the authority on action.

---

## 8. Review Record

A completed review produces:

- `ir_hitl_events` row (`approved` or `rejected`) tied to `investigation_id`
- Langfuse score annotation on the trace (1-5 scale, free text)
- If rejected: a rationale captured in the Langfuse comment field
- If approved: a timestamp on the `ir_investigations.completed_at` column

---

## 9. Cross-References

- SQUIRE_MODEL_CARD.md (intended use, limitations)
- AI_AUDIT_TRAIL_SPEC.md (where HITL events land)
- SQUIRE_DATA_FLOW_CLASSIFICATION.md (data classes the reviewer sees)
- POLICY_AI_GOVERNANCE.md (parent governance)
- POLICY_INCIDENT_RESPONSE.md (IR overlay when HITL rejects a finding)
- AI_SUPPLY_CHAIN_REGISTER.md (Doppler, svc-squire as components in scope)
- PLAYBOOK_AI_INCIDENT.md (runbook for rail refusals and token leaks)
