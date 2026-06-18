# Lab 01: SSH Brute Force

## Attack Narrative

A Tor exit node (185.220.101.45) sprays the prod web host with ~12 username guesses in ~15 seconds, then succeeds on `ubuntu`. Within seconds, the attacker runs `whoami`, dumps `/etc/shadow`, and creates a backdoor user.

This is T1110.001 (Brute Force: Password Guessing) immediately followed by T1078 (Valid Accounts) and T1136.001 (Local Account creation for persistence).

## Detection Logic

Two signals matter, but only the pair is high confidence.

1. Burst of failed auths from one IP (5+ within 60s)
2. Successful auth from the same IP within 5 minutes of the burst

The burst alone is noise (every internet-facing host on port 22 sees this hourly). The success after burst is the breach.

## Run It

```bash
cd labs/lab_01_brute_force_ssh
python3 detect.py auth.log
```

Expected output:
```
=== Brute force burst sources ===
  185.220.101.45: burst start 2026-05-08T04:22:17 duration ~17s

=== Successful auths from brute-force IPs (LIKELY BREACH) ===
  CRITICAL: 185.220.101.45 as ubuntu at 2026-05-08T04:22:36
```

The Sigma equivalent is in `rule.yml`. Convert it with `sigma convert -t splunk rule.yml`.

## Triage Outcome

Verdict: True Positive, Critical.

Page oncall. Disable user `ubuntu` on this host. Force key rotation. Review subsequent commands (the post-auth shadow dump and useradd are the smoking gun). Rotate any creds touched. Hunt for the same source IP across all hosts in the last 30 days.

## Interviewer Questions

- "Why is the burst alone not enough?" Because every public SSH endpoint sees thousands of these per day. Alerting on every burst is alert fatigue. The success after burst is what matters.
- "How would you tune for false positives?" Filter known maintenance jumphosts, allowlist scanner subnets, suppress dev environments. Add a `falsepositives` block in the Sigma rule.
- "What if the attacker rate-limits below your 5-in-60s threshold?" Lower threshold drives noise. Better answer: catch downstream signals (the post-auth `whoami`, the shadow file read) which are TTPs higher on the Pyramid of Pain.
- "How does this map to ATT&CK?" T1110.001 (Password Guessing). Pair with T1078 (Valid Accounts) for the success step.
- "What log sources besides auth.log give you signal?" `journalctl -u ssh -o json`, fail2ban logs, network flow records (Suricata), conntrack for repeated connections from one IP.

## Variant: Adapt for Production

In production, burst detection lives at fail2ban or CrowdSec, not in the SIEM. The SIEM rule should fire on the `Accepted password` event when the source IP is on a recent block list. That correlation across systems is where senior engineering shows.
