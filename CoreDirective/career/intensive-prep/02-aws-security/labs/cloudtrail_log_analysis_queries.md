# Lab: CloudTrail log analysis queries

**Objective:** Build the muscle memory for hunting in CloudTrail. Every query here should be runnable in Athena over CloudTrail Lake or over an S3-backed CloudTrail with the Athena partition projection patterns.

**What an interviewer will ask:**
1. "An attacker has admin in your account. What's in your CloudTrail playbook?"
2. "Show me how you'd detect credential exfiltration."
3. "What does CloudTrail NOT capture?"
4. "Difference between management events and data events?"

---

## Setup: CloudTrail Lake table

If using CloudTrail Lake (recommended for security teams):

```sql
-- Most queries below use the standard CloudTrail event schema.
-- Lake stores events in a managed format. Just SELECT FROM event_data_store.
SELECT eventTime, eventName, userIdentity.arn, sourceIPAddress, awsRegion
FROM <event-data-store-id>
WHERE eventTime > timestamp '2026-05-08 00:00:00'
LIMIT 10;
```

If using S3-backed CloudTrail with Athena partition projection:

```sql
CREATE EXTERNAL TABLE cloudtrail_logs (
  eventVersion string,
  userIdentity struct<
    type:string, principalId:string, arn:string, accountId:string,
    accessKeyId:string, userName:string,
    sessionContext:struct<attributes:struct<mfaAuthenticated:string, creationDate:string>,
                          sessionIssuer:struct<type:string, arn:string, userName:string>>>,
  eventTime string,
  eventSource string,
  eventName string,
  awsRegion string,
  sourceIPAddress string,
  userAgent string,
  errorCode string,
  errorMessage string,
  requestParameters string,
  responseElements string,
  additionalEventData string,
  requestID string,
  eventID string,
  resources array<struct<arn:string, accountId:string, type:string>>,
  eventType string,
  apiVersion string,
  readOnly string,
  recipientAccountId string,
  serviceEventDetails string,
  sharedEventID string,
  vpcEndpointId string
)
PARTITIONED BY (region string, year string, month string, day string)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://<your-cloudtrail-bucket>/AWSLogs/<account>/CloudTrail/'
TBLPROPERTIES (
  'projection.enabled' = 'true',
  'projection.region.type' = 'enum',
  'projection.region.values' = 'us-east-1,us-east-2,us-west-1,us-west-2,eu-west-1',
  'projection.year.type' = 'integer',
  'projection.year.range' = '2024,2030',
  'projection.month.type' = 'integer',
  'projection.month.range' = '1,12',
  'projection.day.type' = 'integer',
  'projection.day.range' = '1,31',
  'storage.location.template' = 's3://<bucket>/AWSLogs/<account>/CloudTrail/${region}/${year}/${month}/${day}/'
);
```

---

## Query 1: root user activity (huge red flag)

Root should never be used. Period. Any activity on root is an incident.

```sql
SELECT eventTime, eventName, sourceIPAddress, userAgent, errorCode
FROM cloudtrail_logs
WHERE userIdentity.type = 'Root'
  AND year = '2026' AND month = '5'
ORDER BY eventTime DESC;
```

Expected result on a healthy account: zero rows for the past 90 days.

If you see anything, the playbook is:
1. Force MFA reset on root
2. Rotate root account access keys (delete them, root should not have keys)
3. Check billing console activity (typical attacker target)
4. Check CreateUser, CreateAccessKey, AttachUserPolicy events tied to root

---

## Query 2: console logins without MFA

```sql
SELECT eventTime, userIdentity.arn, sourceIPAddress, userAgent,
       responseElements, additionalEventData
FROM cloudtrail_logs
WHERE eventName = 'ConsoleLogin'
  AND json_extract_scalar(additionalEventData, '$.MFAUsed') = 'No'
  AND json_extract_scalar(responseElements, '$.ConsoleLogin') = 'Success'
ORDER BY eventTime DESC;
```

Every IAM user with console access should have MFA. SCP at the org level can deny `iam:CreateAccessKey` and most actions when `aws:MultiFactorAuthPresent = false`.

---

## Query 3: failed authentications (brute force, leaked creds)

```sql
SELECT
  date_trunc('hour', from_iso8601_timestamp(eventTime)) AS hour,
  sourceIPAddress,
  count(*) AS fail_count,
  count(distinct userIdentity.arn) AS distinct_principals
FROM cloudtrail_logs
WHERE errorCode IN ('SignatureDoesNotMatch', 'InvalidSignatureException', 'AccessDenied')
  AND eventTime > date_format(current_date - interval '1' day, '%Y-%m-%dT%H:%i:%s')
GROUP BY 1, 2
HAVING count(*) > 50
ORDER BY fail_count DESC;
```

50+ AccessDenied from one IP in one hour against multiple principals is suspicious. Could also be a misconfigured app, but worth checking.

---

## Query 4: GetCallerIdentity from new IPs (credential testing)

The first thing an attacker does with stolen credentials is `aws sts get-caller-identity`. It is a free, low-noise check. Hunt for it.

```sql
WITH known_ips AS (
  SELECT DISTINCT sourceIPAddress
  FROM cloudtrail_logs
  WHERE eventName = 'GetCallerIdentity'
    AND eventTime BETWEEN date_format(current_date - interval '30' day, '%Y-%m-%dT00:00:00')
                      AND date_format(current_date - interval '7' day, '%Y-%m-%dT00:00:00')
)
SELECT eventTime, userIdentity.arn, sourceIPAddress, userAgent
FROM cloudtrail_logs
WHERE eventName = 'GetCallerIdentity'
  AND eventTime > date_format(current_date - interval '7' day, '%Y-%m-%dT00:00:00')
  AND sourceIPAddress NOT IN (SELECT sourceIPAddress FROM known_ips)
  AND sourceIPAddress NOT LIKE 'AWS Internal'
  AND sourceIPAddress NOT LIKE '%amazonaws.com';
```

---

## Query 5: privilege escalation candidate events

The 21 IAM privesc paths from Rhino Security all touch a small set of API calls. Hunt for them.

```sql
SELECT eventTime, eventName, userIdentity.arn, sourceIPAddress,
       requestParameters, errorCode
FROM cloudtrail_logs
WHERE eventName IN (
    -- direct privesc
    'AttachUserPolicy', 'AttachRolePolicy', 'AttachGroupPolicy',
    'PutUserPolicy', 'PutRolePolicy', 'PutGroupPolicy',
    'CreatePolicyVersion', 'SetDefaultPolicyVersion',
    -- pass-role abuse setup
    'CreateRole', 'UpdateAssumeRolePolicy',
    'CreateFunction', 'UpdateFunctionConfiguration',  -- lambda + PassRole
    'CreateInstanceProfile', 'AddRoleToInstanceProfile',
    -- access key cloning
    'CreateAccessKey', 'CreateLoginProfile', 'UpdateLoginProfile',
    -- federation abuse
    'AssumeRole', 'AssumeRoleWithSAML', 'AssumeRoleWithWebIdentity'
  )
  AND eventTime > date_format(current_date - interval '7' day, '%Y-%m-%dT00:00:00')
  AND errorCode IS NULL  -- successful only
ORDER BY eventTime DESC;
```

Triage rule of thumb: if a non-security principal calls AttachUserPolicy on themselves with AdministratorAccess, that is the privesc.

---

## Query 6: CloudTrail tampering

```sql
SELECT eventTime, eventName, userIdentity.arn, sourceIPAddress, errorCode,
       json_extract_scalar(requestParameters, '$.name') AS trail_name
FROM cloudtrail_logs
WHERE eventName IN ('StopLogging', 'DeleteTrail', 'UpdateTrail',
                    'PutEventSelectors', 'StartLogging')
ORDER BY eventTime DESC;
```

Real engineers know: an attacker with admin will turn off CloudTrail before doing anything else. Detection is too late at that point. Defense:
- Multi-region trail
- Log file validation (digest files signed by AWS)
- S3 bucket policy on the log bucket denying delete from anyone except a break-glass role
- Object Lock on the log bucket (compliance mode is irrevocable)
- SCP at the org level forbidding `cloudtrail:Stop*`, `cloudtrail:Delete*` for everyone except SecurityAdmins
- Real-time alerting via CloudWatch Logs metric filter or EventBridge

---

## Query 7: data exfiltration via S3

```sql
SELECT eventTime, userIdentity.arn, sourceIPAddress,
       json_extract_scalar(requestParameters, '$.bucketName') AS bucket,
       eventName
FROM cloudtrail_logs
WHERE eventName IN ('GetObject', 'GetObjectAcl', 'CopyObject')
  AND userIdentity.type IN ('AssumedRole', 'IAMUser')
  AND sourceIPAddress NOT LIKE '10.%'   -- our internal CIDR
  AND sourceIPAddress NOT LIKE '172.%'
  AND sourceIPAddress NOT LIKE '%amazonaws.com';
```

This requires CloudTrail data events to be enabled on the bucket. They are NOT on by default and they cost money. Enable on critical PII buckets, not everything.

---

## Query 8: secrets / KMS abuse

```sql
SELECT eventTime, userIdentity.arn, sourceIPAddress, eventName,
       json_extract_scalar(requestParameters, '$.secretId') AS secret_id
FROM cloudtrail_logs
WHERE eventName IN ('GetSecretValue', 'PutSecretValue', 'DeleteSecret',
                    'Decrypt', 'GenerateDataKey', 'ScheduleKeyDeletion',
                    'DisableKey')
  AND eventTime > date_format(current_date - interval '24' hour, '%Y-%m-%dT00:00:00')
ORDER BY eventTime DESC;
```

Watch for `Decrypt` calls from unusual roles (a webserver suddenly decrypting prod database keys), or `ScheduleKeyDeletion` (ransomware playbook).

---

## What CloudTrail does NOT capture

This list comes up in interviews. Memorize it.

1. **Data events by default.** S3 GetObject, Lambda Invoke, DynamoDB query, etc. You must explicitly enable data events. They cost extra ($0.10 per 100K events).

2. **Network traffic.** Use VPC Flow Logs.

3. **DNS queries.** Use Route 53 Resolver query logs (or GuardDuty consumes them).

4. **EC2 instance internals.** OS-level activity, file changes, process exec. Use Falco, OSSEC, or CrowdStrike.

5. **In-memory or runtime activity.** A Lambda function decrypting a value with KMS shows up. The Lambda function reading its own /tmp does not.

6. **Some service-internal events.** SSM Run Command shows up (well-instrumented). Glue ETL job step-by-step does not.

7. **Cross-region / cross-account replication latency.** Lake events are typically there in 5-15 minutes. S3-backed are 5-15 minutes. Not real-time.

8. **Sub-second resolution.** eventTime is to the second. For ordering events that happen in the same second, use eventID + sequence number.

---

## Real engineer answer for: "Tell me about a time you found something subtle in CloudTrail"

> "We had a Lambda that was supposed to only read from one S3 prefix. CloudTrail data events showed it reading from a different prefix in the same bucket once a week. Turned out a rotated developer left a hardcoded S3 prefix in a config file from a year prior, and the Lambda fell back to it on a schedule. No GuardDuty finding because the role was authorized for the bucket. The signal was the prefix mismatch with the function's intended scope. After that we tightened the role to only the prefix the function should read, and added a CloudWatch metric filter on prefix mismatches. The lesson was that 'authorized' and 'intended' are not the same, and the difference between them is where most low-and-slow attacks live."
