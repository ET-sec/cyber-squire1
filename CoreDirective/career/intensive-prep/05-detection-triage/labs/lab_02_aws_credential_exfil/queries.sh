#!/usr/bin/env bash
# AWS credential exfil triage queries.
# Run each block. Each surfaces a step in the kill chain.
# Requires: jq

TRAIL=cloudtrail.json

echo "=== 1. All distinct source IPs and counts ==="
jq -r '.Records[].sourceIPAddress' $TRAIL | sort | uniq -c | sort -rn

echo
echo "=== 2. Events from non-corporate IPs (anything not 10.x) ==="
jq '.Records[] | select(.sourceIPAddress | startswith("10.") | not) | {time: .eventTime, source: .eventSource, name: .eventName, ip: .sourceIPAddress, ua: .userAgent, err: .errorCode}' $TRAIL

echo
echo "=== 3. The Capital One pattern: GetCallerIdentity, ListBuckets, GetObject ==="
jq '.Records[] | select(.eventName == "GetCallerIdentity" or .eventName == "ListBuckets" or .eventName == "GetObject") | {time: .eventTime, name: .eventName, ip: .sourceIPAddress, principal: .userIdentity.arn}' $TRAIL

echo
echo "=== 4. Anti-forensics signals: CloudTrail tampering and IAM persistence attempts ==="
jq '.Records[] | select(.eventName == "StopLogging" or .eventName == "DeleteTrail" or .eventName == "CreateAccessKey" or .eventName == "DeactivateMFADevice" or .eventName == "UpdateAssumeRolePolicy") | {time: .eventTime, name: .eventName, ip: .sourceIPAddress, err: .errorCode, principal: .userIdentity.arn}' $TRAIL

echo
echo "=== 5. Role used from multiple source IPs (session hijack indicator) ==="
jq -r '.Records[] | select(.userIdentity.type == "AssumedRole") | "\(.userIdentity.arn) \(.sourceIPAddress)"' $TRAIL | sort -u | awk '{print $1}' | sort | uniq -c | sort -rn | awk '$1 > 1 {print "ROLE WITH MULTIPLE IPs: " $0}'

echo
echo "=== 6. The smoking gun: web-prod-01 role used from public IP ==="
jq '.Records[] | select(.userIdentity.arn != null and (.userIdentity.arn | contains("web-prod-01")) and (.sourceIPAddress | startswith("10.") | not))' $TRAIL
