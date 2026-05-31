# Sample Incident Response Playbook: Fixture Stub

**Document ID:** IR-PLAY-TEST-001
**Version:** 0.1
**Classification:** Test Fixture Only
**Owner:** Squire Test Suite
**NIST 800-53 Controls:** IR-4 (Incident Handling), SI-4 (Information System Monitoring)

---

## 1. Purpose

Minimal fixture used by chunker unit tests. Kept intentionally short so tests run fast and deterministically without any network access.

## 2. Detection

Detection is triggered when a Falco eBPF rule fires on an unexpected exec in a production container. The alert payload lands on the Squire webhook and enters the investigation graph.

## 3. Triage

### 3.1 Confirm the alert

Verify the container is still running, capture `ps auxww` inside the namespace, and confirm the exec did not originate from a legitimate cron or deployment actor.

### 3.2 Collect evidence

Pull Falco JSON, Datadog metrics for the surrounding 10 minutes, and any Cloudflare access logs for the associated tunnel route.

## 4. Containment

Disconnect the container from `net-core`, apply `iptables` DROP on egress, and `docker pause` to freeze the runtime state. Preserve the filesystem for later forensic review.

## 5. Eradication

Replace the compromised image with the last-known-good tag from the internal registry, redeploy with a fresh secret, and rotate any credentials that lived inside the container's environment.

## 6. Recovery

Bring the service back in a blast-radius-limited manner (one replica, observed for one hour), then scale back up once Langfuse traces and Datadog dashboards confirm steady-state behavior.

## 7. Lessons Learned

Schedule a retro within 48 hours. Capture three improvements, file them as POA&M items, and attach the resulting Langfuse trace id to the ir_investigations row.
