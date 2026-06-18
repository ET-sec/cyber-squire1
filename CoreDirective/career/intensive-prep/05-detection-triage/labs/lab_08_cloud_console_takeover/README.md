# Lab 08: Cloud Console Takeover

## Attack Narrative

Admin-bob's credentials were phished or token-stolen via AiTM. At 17:30 attacker logs in from Bulgaria (94.156.71.122) with valid MFA bypass (likely token replay). Within 90 seconds:

1. 17:31:42 DeactivateMFADevice (cuts off bob from re-securing the account)
2. 17:32:05 CreateAccessKey (long-lived persistence outside the console)
3. 17:35:22 RunInstances of 4x p4d.24xlarge in us-east-1 (~$32/hour each, GPU compute for crypto mining)
4. 17:36:01 StopLogging on the org trail (anti-forensics)

GuardDuty fires three findings in parallel:
- `UnauthorizedAccess:IAMUser/ConsoleLoginSuccess.B` (anomalous login)
- `Stealth:IAMUser/CloudTrailLoggingDisabled` (anti-forensics)
- `CryptoCurrency:EC2/BitcoinTool.B!DNS` (the EC2s start mining)

The story matches the LAPSUS$, Scattered Spider, and Octo Tempest patterns of 2023 to 2024.

## Detection Logic

The composite alert is the high-confidence detection.

Login + MFA off + access key + stop logging within 10 minutes is the takeover signature. Each event alone has noise. The sequence has near-zero noise.

GuardDuty already gives you 80 percent of this for free. Sigma rule fills the gap and covers accounts where GuardDuty is not enabled.

## Run It

```bash
cd labs/lab_08_cloud_console_takeover

# All bob actions in time order
jq '.Records[] | select(.userIdentity.userName == "admin-bob") | {time: .eventTime, name: .eventName, ip: .sourceIPAddress, ua: .userAgent}' cloudtrail.json

# GuardDuty findings
jq '.GuardDutyFindings[] | {time: .createdAt, severity, type, title}' cloudtrail.json

# The kill chain in one query
jq '.Records[] | select(.eventName | IN("ConsoleLogin","DeactivateMFADevice","CreateAccessKey","StopLogging","RunInstances")) | {time: .eventTime, name: .eventName, ip: .sourceIPAddress}' cloudtrail.json
```

## Triage Outcome

Verdict: True Positive, Critical.

Page oncall immediately. Disable the IAM user (`aws iam delete-login-profile` and `aws iam update-access-key --status Inactive`). Delete the rogue access key `AKIAEXAMPLEEVIL2`. Re-enable MFA. Terminate the 4 EC2 mining instances. Re-enable CloudTrail. Pull the bob's session token from the original login at 17:30 and force credential and MFA reset across federation. Investigate phishing or AiTM vector for original token theft. Roll all access keys for any IAM user that touched the account in the last 30 days. Review GuardDuty findings history for sibling alerts.

Notification: cloud account compromise reaches legal and exec within 1 hour. Customer notification clock starts depending on data exposure. Cost recovery: AWS may waive the mining bill if reported quickly with incident documentation.

## Interviewer Questions

- "GuardDuty is already firing. Why write Sigma?" Three reasons. One, accounts without GuardDuty (cost or unsupported region). Two, lower latency on the composite signal — Sigma fires when the chain matches, GuardDuty alerts arrive minutes later. Three, GuardDuty is ML-based and tuned per AWS, not per your environment. Custom Sigma plus GuardDuty is defense in depth.
- "What is AiTM?" Adversary in the Middle. Reverse proxy phishing kits like Evilginx2 sit between the user and the real auth provider. They capture credentials AND session tokens after MFA. Token replay defeats MFA because MFA already happened upstream. Detection is at the session level: token used from a different fingerprint, anomalous geography, anomalous app context.
- "How would you prevent this?" Conditional Access with device compliance and named locations (Microsoft world). For AWS specifically: SCP that denies `iam:CreateAccessKey` and `iam:DeactivateMFADevice` from non-corporate networks. SCP that requires MFA for sensitive actions even after console login (`aws:MultiFactorAuthAge` condition).
- "What is the right response runbook?" Tested incident playbook in the SOAR. Auto-disable the user, rotate keys, halt running compute outside known regions, snapshot evidence, page on-call. Manual step: legal review for breach notification scope.
- "How does this map to ATT&CK?" T1078.004 (Valid Accounts: Cloud Accounts) for the login. T1098.001 (Account Manipulation: Additional Cloud Credentials) for the access key creation. T1562.008 (Impair Defenses: Disable or Modify Cloud Logs) for StopLogging. T1496 (Resource Hijacking) for the mining.
- "How does Dropzone or another AI SOC handle this?" Auto-investigates: pulls the user's login history, geo profile, recent activity, related GuardDuty findings, asset criticality. Writes a structured report ranking confidence high. Recommends the kill switch actions. Human approves the kill, the SOAR runs it.

## Variant: Detection Hardening

1. Custom rule on access key creation from a session that started from a non-corporate IP. Catches even if the attacker is patient (hours later).
2. Cost anomaly detection: RunInstances of GPU types in regions that have never run GPU workloads = page.
3. Trail tampering monitor at the org level: any `StopLogging`, `DeleteTrail`, `PutEventSelectors` against an org trail is critical regardless of source.
4. AWS Config rule for `mfa-enabled-for-iam-console-access` that flags within 60 seconds of MFA being removed.
