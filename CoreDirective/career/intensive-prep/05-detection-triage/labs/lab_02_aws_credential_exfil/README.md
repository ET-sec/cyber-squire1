# Lab 02: AWS Credential Exfil (Capital One Pattern)

## Attack Narrative

Web-prod-01's EC2 role keys were stolen via SSRF to the IMDS endpoint (T1552.005). The attacker exfiltrated the temporary credentials to their own host (45.135.232.8) and used them from there.

The kill chain in CloudTrail:

1. 14:42:17 GetCallerIdentity from 45.135.232.8 (the "who am I" first call)
2. 14:42:42 ListAttachedRolePolicies (figuring out what the role can do)
3. 14:43:05 ListBuckets (S3 enumeration)
4. 14:43:48 GetObject on `prod-customer-pii/exports/customers-2026-04.csv` (the actual exfil)
5. 14:44:15 CreateAccessKey on dev-alice (persistence attempt, denied)
6. 14:45:01 StopLogging on prod-org-trail (anti-forensics, denied)

The role `EC2-WebRole/web-prod-01` is bound to EC2 instance `web-prod-01` on internal IP `10.0.5.50`. Its appearance from the public IP `45.135.232.8` is the smoking gun.

## Detection Logic

Any IAM role session originating from outside the corporate VPC or AWS service IP space is a high-confidence credential theft signal. EC2-bound roles should never appear from outside.

## Run It

```bash
cd labs/lab_02_aws_credential_exfil
chmod +x queries.sh
./queries.sh
```

Or run individual jq queries from `queries.sh`. The 6th query is the kill chain in one line.

## Triage Outcome

Verdict: True Positive, Critical.

Page oncall. Revoke the role's active sessions (`aws sts revoke-iam-credentials` is not a thing, so attach a deny policy with `aws:TokenIssueTime` after the breach window). Rotate the EC2 instance role. Patch the SSRF vulnerability that gave up the IMDS creds. Force IMDSv2 only across the org. Investigate the GetObject call: was customer PII exfiltrated, scope the breach, trigger incident response and legal notification.

## Interviewer Questions

- "Walk me through the Capital One incident." 2019. Paige Thompson. SSRF in the WAF (Modsec misconfig), reached IMDSv1 on 169.254.169.254, pulled temp creds for the WAF role, used them to ListBuckets and GetObject across S3, exfil'd 100M+ Capital One records.
- "How would you prevent this?" IMDSv2 enforcement (token-required), VPC endpoint policies, least privilege roles, S3 bucket policies that condition on `aws:SourceVpc` or `aws:SourceIp`.
- "How would you detect IMDSv1 use?" CloudTrail does not log IMDS calls (those are EC2 internal). VPC flow logs see traffic to 169.254.169.254. Some EDRs hook on the metadata fetch. And IMDSv2 enforcement in account-level settings shows in config compliance.
- "What about GuardDuty?" It would have flagged this with `UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS`. Worth knowing the finding type by name.
- "What if the attacker used a residential proxy that overlaps with corporate ranges?" Then this rule misses. Pair with role-to-IP baseline detection: this role has only ever been seen from 10.0.5.50, alert on any new IP. Behavioral baselining beats CIDR allowlists for sophisticated attackers.

## Variant: Detection Tuning

Three filter additions for production:
1. Allowlist roles owned by sanctioned third-party SaaS by their `userName` field.
2. Allowlist NAT gateway and VPN concentrator IPs by their public-facing addresses.
3. Maintenance window awareness: incident response role coming from the SOC tools subnet.

Each filter goes in the Sigma rule `falsepositives` block AND as an explicit `filter_*` selection so the rule code matches the documentation.
