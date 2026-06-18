# Lab: SecurityHub aggregation across accounts

**Objective:** Set up SecurityHub as the single pane of glass across a multi-account org. Understand finding flow from GuardDuty/Inspector/Macie/Config/partners into ASFF, dedup, and SOAR routing.

**What an interviewer will ask:**
1. "Walk me through the SecurityHub finding lifecycle."
2. "How do you tune SecurityHub findings for a 50-account org?"
3. "What is ASFF and why does it matter?"

---

## The data flow

```
+-------------------+
| GuardDuty         |---+
+-------------------+   |
+-------------------+   |
| Inspector v2      |---+
+-------------------+   |
+-------------------+   |          +----------------+        +--------------+
| Macie             |---+--------->|  SecurityHub   |------->| EventBridge  |
+-------------------+   |          | (per account,  |        +--------------+
+-------------------+   |          |  per region)   |              |
| Config            |---+          +----------------+              v
+-------------------+                      |                +-----------+
+-------------------+                      v                | n8n SOAR  |
| Partner: Snyk,    |---+          +----------------+       | or Lambda |
| CrowdStrike, Wiz, |   |          | Delegated      |       +-----------+
| Trend Micro...    |---+--------->| Admin (Sec     |
+-------------------+              | Tooling acct)  |
                                   +----------------+
                                           |
                                           v
                                    Cross-region
                                    aggregator
```

Each finding is normalized into AWS Security Finding Format (ASFF), a JSON schema with fields like:
- `Id`, `ProductArn`, `GeneratorId`
- `AwsAccountId`, `Region`, `CreatedAt`, `UpdatedAt`
- `Severity` (Label + Normalized 0-100)
- `Resources[]` (the affected resources)
- `Workflow.Status` (NEW, NOTIFIED, RESOLVED, SUPPRESSED)
- `Compliance.Status` (PASSED, FAILED, WARNING, NOT_AVAILABLE)
- `Types[]` (taxonomy: TTPs, Effects, Software-and-Configuration)

Why ASFF matters: every product that integrates emits findings in this shape. SecurityHub deduplicates by ProductArn + Id. SOAR tools query one schema across all sources.

---

## Cross-account pattern

In an AWS Organization with management/log-archive/security-tooling/workload OUs:

1. **Designate the security tooling account** as the SecurityHub delegated administrator at the org level:
   ```
   aws organizations register-delegated-administrator \
     --service-principal securityhub.amazonaws.com \
     --account-id <security-tooling-account-id>
   ```

2. **Enable SecurityHub in every account in every region** via the delegated admin. This auto-enables AWS Foundational Security Best Practices and CIS standards across the org.

3. **Cross-region aggregator** in the security tooling account so all findings land in one region (typically us-east-1):
   ```
   aws securityhub create-finding-aggregator \
     --region-linking-mode ALL_REGIONS
   ```

4. **EventBridge rule** in the aggregation region forwards critical findings to your SOAR:
   ```json
   {
     "source": ["aws.securityhub"],
     "detail-type": ["Security Hub Findings - Imported"],
     "detail": {
       "findings": {
         "Severity": {"Label": ["CRITICAL", "HIGH"]},
         "Workflow": {"Status": ["NEW"]}
       }
     }
   }
   ```

5. **SOAR (n8n, Tines, Lambda)** ingests the event, enriches with CloudTrail context, opens a ticket, and pages on-call if severity = CRITICAL.

---

## Tuning for noise (the part interviewers want to hear about)

A fresh SecurityHub install in a 50-account org will produce 5,000-50,000 findings on day one. Most are config compliance findings on resources that pre-date the controls. Triage strategy:

### Step 1: filter what gets created
- Disable controls that are not relevant (e.g., disable PCI controls in non-PCI accounts via `BatchUpdateStandardsControl`)
- Disable AWS-managed standards you don't need (CIS 1.4 vs 3.0 - pick one, not both, the overlap is 80%)
- For partner integrations, only enable the ones you ingest (don't turn on Snyk integration if you don't use Snyk)

### Step 2: bulk-suppress historical findings
After enabling, batch-update existing findings to `Workflow.Status = SUPPRESSED` if they predate your control implementation date. New findings after that date are what matters.

### Step 3: route by severity
- CRITICAL/HIGH -> page immediately
- MEDIUM -> create ticket, daily review
- LOW -> dashboard only, no notification

### Step 4: insights and custom actions
- Create SecurityHub insights for common dashboards: "all findings tagged production", "all findings on internet-facing resources", "all findings older than 30 days"
- Custom actions let SOC analysts trigger remediation Lambdas straight from the SecurityHub console

### Step 5: aging
Findings have an `UpdatedAt`. Anything not auto-archived in 90 days is an open backlog item. Pair with a weekly report to leadership: "X findings open, Y critical, Z opened in the last week".

---

## ASFF in real life

Example finding (truncated):

```json
{
  "SchemaVersion": "2018-10-08",
  "Id": "arn:aws:securityhub:us-east-1:123456789012:finding/abc-123",
  "ProductArn": "arn:aws:securityhub:us-east-1::product/aws/guardduty",
  "GeneratorId": "arn:aws:guardduty:us-east-1:123456789012:detector/.../finding/...",
  "AwsAccountId": "123456789012",
  "Types": [
    "TTPs/Initial Access/Unauthorized Use of IAM Credentials",
    "Effects/Data Exfiltration"
  ],
  "FirstObservedAt": "2026-05-08T14:00:00Z",
  "LastObservedAt": "2026-05-08T14:05:00Z",
  "CreatedAt": "2026-05-08T14:00:00Z",
  "UpdatedAt": "2026-05-08T14:05:00Z",
  "Severity": {"Label": "HIGH", "Normalized": 70},
  "Title": "API GetCallerIdentity was invoked from a Tor exit node IP address.",
  "Description": "...",
  "Resources": [{
    "Type": "AwsIamAccessKey",
    "Id": "arn:aws:iam::123456789012:access-key/AKIA...",
    "Region": "us-east-1"
  }],
  "Workflow": {"Status": "NEW"},
  "RecordState": "ACTIVE"
}
```

What to query in your SOAR:

- Pull `Resources[0].Id` to know which access key was abused
- Pull `Severity.Label` for routing
- Pull `Types[]` for category-based handling
- Pull `ProductArn` to know which tool flagged it (different remediation per source)
- Use `Id` + `ProductArn` for dedup (SecurityHub does this for you, your SOAR should too as a backstop)

---

## Real engineer answer

> "SecurityHub is the aggregator across GuardDuty, Inspector, Macie, Config, and partners like Snyk and CrowdStrike. I run it with a delegated admin in the security tooling account, cross-region aggregator pinning everything to us-east-1, and AWS Foundational Best Practices plus CIS standards on. EventBridge filters for severity HIGH/CRITICAL and Workflow NEW, and routes to our SOAR. The biggest win is dedup: ASFF normalizes findings so I'm not chasing the same misconfig across five tools. The biggest pain is initial noise on a fresh org. Strategy is bulk-suppress findings predating control implementation, disable controls that don't apply per account, and route LOW/MEDIUM to a dashboard rather than a paging channel. Aging is the thing teams forget: every finding still NEW at 90 days is a backlog item, not just noise."
