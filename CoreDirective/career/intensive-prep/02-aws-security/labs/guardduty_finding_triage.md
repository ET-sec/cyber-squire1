# Lab: GuardDuty finding triage

**Objective:** Be able to triage the top 10 GuardDuty findings from cold without a runbook. These are what you will see in a real SOC.

**What an interviewer will ask:**
1. "GuardDuty fires UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS. What are the first five things you do?"
2. "How is GuardDuty different from SecurityHub?"
3. "Walk me through tuning out a noisy GuardDuty finding."

---

## How GuardDuty works (one paragraph)

GuardDuty consumes CloudTrail (management + S3 + Lambda data), VPC Flow Logs, DNS query logs (Route 53 Resolver), and EKS audit logs. It applies AWS-managed ML models and threat intel feeds (AWS Threat Intelligence, third-party feeds) to detect anomalies and known-bad indicators. Findings are written to the GuardDuty service and forwarded to SecurityHub if SH is enabled. Free 30-day trial, then ~$1 per million CloudTrail events plus charges for VPC flow + DNS analysis. For a 50-person startup expect $300 to $1500/month.

---

## Top 10 findings to know cold

### 1. UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS

**Meaning:** EC2 instance role credentials are being used FROM OUTSIDE AWS. The instance role was issued for an instance running in your account, but the API call came from an external IP.

**Why it fires:** Almost certainly IMDS theft (Capital One pattern). Could also be a developer who set their `~/.aws/credentials` to instance role credentials they pulled off an instance.

**Triage steps:**
1. Quarantine the instance (replace SG with a deny-all SG, do NOT terminate).
2. Look at CloudTrail events using the affected access key in the last 24 hours. What did the attacker do?
3. Check if any new IAM users, access keys, or roles were created.
4. Check what S3 buckets, Secrets Manager secrets, KMS keys were accessed.
5. Snapshot the EBS volume(s) for forensics.
6. Rotate the role credentials by stopping/starting the instance OR by detaching/reattaching the role (this revokes the cached creds).
7. Patch the SSRF or app vuln that allowed IMDS access.
8. Confirm IMDSv2 is required on the instance (HttpTokens=required).

### 2. UnauthorizedAccess:IAMUser/ConsoleLoginSuccess.B

Successful console login from an IP associated with malicious activity in AWS threat intel feeds.

**Triage:**
1. Disable the user (remove console password, deactivate keys).
2. Force MFA reset.
3. Look at every action that user took in the session via CloudTrail.
4. Check for new access keys, role assumptions, IAM policy attachments.
5. If MFA was bypassed somehow (SIM swap), the human attacker has phone access. Notify the user via a side channel.

### 3. CryptoCurrency:EC2/BitcoinTool.B!DNS

**Meaning:** EC2 instance made a DNS query for a known cryptocurrency mining pool.

**Triage:**
1. Look at top processes on the instance via SSM Run Command.
2. Confirm the binary running. If it is xmrig, kinsing, or pnscan, you have a miner.
3. Check how the attacker got in. Common: exposed Redis, exposed Docker socket, vulnerable web app.
4. Check if the role has been used to spread laterally (DescribeInstances, RunInstances, GetCallerIdentity from inside).
5. Terminate the instance after preserving evidence. Re-launch from clean AMI. Patch the entry vector.

### 4. Recon:IAMUser/AnomalousASN

**Meaning:** API calls coming from an AS Number that the principal has not used before.

**Triage:**
1. Check if the principal is a developer who is traveling or using a new VPN.
2. If not, treat as ConsoleLoginSuccess.B style triage.
3. If the principal is a service role, this is more serious because service roles should have stable origin patterns.

### 5. Persistence:IAMUser/AnomalousBehavior

The principal's API call patterns differ from the historical baseline. Could be the user installing new tooling, could be an attacker with their creds.

**Triage:**
1. Open a quick chat with the user to confirm.
2. If unconfirmed, look at the specific anomalous API calls. Are they sensitive (IAM, KMS, CloudTrail, billing)?
3. Treat as compromise if any sensitive APIs were touched without ticket / change record.

### 6. Discovery:S3/MaliciousIPCaller

S3 bucket accessed from a known-bad IP.

**Triage:**
1. Confirm the bucket is private (BPA on, bucket policy not public). If it is private and an attacker hit it, they have credentials.
2. Look at the access via S3 server access logs or CloudTrail data events.
3. Rotate any credentials that were used.

### 7. Stealth:IAMUser/CloudTrailLoggingDisabled

Someone called StopLogging or DeleteTrail. This is alarm-level.

**Triage:**
1. Re-enable the trail immediately.
2. The attacker is already in. Treat as full compromise.
3. Pivot to LookoutTrail or Lake history if your trail data was preserved.
4. Rotate all credentials. Force re-auth on Identity Center.
5. Trigger the IR playbook.

### 8. Backdoor:EC2/C&CActivity.B!DNS

Instance is talking DNS to a known command-and-control domain.

**Triage:**
1. Network isolate the instance.
2. Memory dump if possible (LIME, fmem, or AWS Forensics tools).
3. Snapshot the volume.
4. Tear down and rebuild.

### 9. PenTest:IAMUser/KaliLinux

API call from an AWS account using a Kali Linux user agent.

**Triage:**
1. Check if it is your own pen tester. If yes, suppress.
2. If not, treat like ConsoleLoginSuccess.B.

### 10. Policy:S3/BucketBlockPublicAccessDisabled

Someone disabled Block Public Access on a bucket.

**Triage:**
1. Re-enable BPA via Lambda auto-remediation.
2. Look at the request: who, when, why.
3. Open a CR with the team that did it. Either revert + lock down with SCP, or accept with documented reason.

---

## Tuning noisy findings

Two patterns:

### Suppression rules

In the GuardDuty console -> Suppression rules. You can suppress findings matching a filter (e.g., source IP = your office, or finding type = Recon:IAMUser/AnomalousASN with userArn = your-monitoring-tool-role).

Rule of thumb: only suppress if the finding genuinely has no security signal. Otherwise, route the finding to a "low priority" queue but keep it visible.

### EventBridge filtering before SOAR

Most teams have GuardDuty -> EventBridge -> Lambda or n8n. Filter at EventBridge before paging anyone. Example rule: only forward findings with severity >= 5.0 (medium and above) to PagerDuty. Severity < 5 goes to a Slack channel for daily review.

---

## GuardDuty vs SecurityHub

This shows up in every interview. Get it right.

**GuardDuty:** detection. Generates findings from telemetry. AWS-native, behavioral.

**SecurityHub:** aggregator. Pulls findings from GuardDuty + Inspector + Macie + Config + 50 partner tools (Snyk, CrowdStrike, Wiz, etc) into one console. Also runs compliance checks (CIS, AWS FSBP, PCI DSS, NIST 800-53). Findings are normalized into AWS Security Finding Format (ASFF).

**The relationship:** GuardDuty generates raw security events. SecurityHub deduplicates them, applies severity scoring, runs compliance benchmarks, and gives you one queue to triage from. Most enterprises wire SecurityHub findings into Jira / SOAR.

**The non-obvious thing interviewers like:** SecurityHub's "AWS Foundational Security Best Practices" standard has ~250 controls. Most are simple Config rules. Turning it on in production gives you a free baseline of misconfig findings without paying for a third-party CSPM tool.

---

## Real engineer answer template

> "When GuardDuty fires InstanceCredentialExfiltration.OutsideAWS, my first move is to quarantine the instance with a deny-all security group. Don't terminate, terminate kills the evidence. Then I pull the affected access key from the finding and run a CloudTrail query for every event in the past 24 hours signed by that key. I'm looking for new IAM users, role assumptions, S3 GetObjects on sensitive buckets, KMS Decrypt calls, anything indicating data movement or persistence. While that runs, I detach the IAM role from the instance, which revokes the cached creds. Then I snapshot the volume for forensics, rotate any downstream credentials the role had access to, and start a post-mortem on how the IMDS access happened. Almost always it is IMDSv1 still allowed plus an SSRF in the app layer. Fix is enforce IMDSv2 with hop limit 1 at the account default level and patch the SSRF."
