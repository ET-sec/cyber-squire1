#!/usr/bin/env bash
# Lab: VPC Flow Logs threat hunting with Athena
# Objective: Set up flow logs to S3, query them with Athena, find suspicious
#   patterns: outbound to TOR exit nodes, unusual ports, traffic to known C2.
#
# What an interviewer will ask:
#   1. "What is in a VPC Flow Log record? What is missing?"
#   2. "How would you detect data exfiltration with flow logs?"
#   3. "Why is GuardDuty cheaper than building this yourself?"

set -euo pipefail
REGION="${AWS_REGION:-us-east-1}"
PROFILE="${AWS_PROFILE:-default}"
PREFIX="lab-vpcfl-$(date +%s)"
aws_cli() { aws --profile "$PROFILE" --region "$REGION" "$@"; }

ACCOUNT_ID=$(aws_cli sts get-caller-identity --query Account --output text)

echo "=== STEP 1: enable Flow Logs to S3 (parquet) ==="

# Pick the default VPC, you can swap to your own
VPC_ID=$(aws_cli ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text)

LOG_BUCKET="${PREFIX}-logs-${ACCOUNT_ID}"
aws_cli s3api create-bucket --bucket "$LOG_BUCKET" \
  $([ "$REGION" != "us-east-1" ] && echo "--create-bucket-configuration LocationConstraint=$REGION") \
  >/dev/null

aws_cli s3api put-public-access-block --bucket "$LOG_BUCKET" \
  --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# enhanced format with most useful fields
FIELDS="\${version} \${vpc-id} \${subnet-id} \${instance-id} \${interface-id} \${account-id} \${type} \${srcaddr} \${dstaddr} \${srcport} \${dstport} \${pkt-srcaddr} \${pkt-dstaddr} \${protocol} \${bytes} \${packets} \${start} \${end} \${action} \${tcp-flags} \${log-status} \${flow-direction} \${traffic-path}"

FL_ID=$(aws_cli ec2 create-flow-logs \
  --resource-type VPC --resource-ids "$VPC_ID" \
  --traffic-type ALL \
  --log-destination-type s3 \
  --log-destination "arn:aws:s3:::${LOG_BUCKET}/AWSLogs/" \
  --log-format "$FIELDS" \
  --destination-options "FileFormat=parquet,HiveCompatiblePartitions=true,PerHourPartition=true" \
  --max-aggregation-interval 60 \
  --query 'FlowLogIds[0]' --output text)

echo "Flow log: $FL_ID  -> s3://$LOG_BUCKET"
echo "Wait at least 10 minutes for data to land in S3 before querying."

echo
echo "=== STEP 2: Athena queries to run after data lands ==="

cat <<'QUERIES'

-- Set up the table (run in Athena, swap account, region, bucket)

CREATE EXTERNAL TABLE IF NOT EXISTS vpc_flow_logs (
  version int,
  vpc_id string,
  subnet_id string,
  instance_id string,
  interface_id string,
  account_id string,
  type string,
  srcaddr string,
  dstaddr string,
  srcport int,
  dstport int,
  pkt_srcaddr string,
  pkt_dstaddr string,
  protocol int,
  bytes bigint,
  packets bigint,
  start_time bigint,
  end_time bigint,
  action string,
  tcp_flags int,
  log_status string,
  flow_direction string,
  traffic_path int
)
PARTITIONED BY (
  aws_account_id string,
  aws_service string,
  aws_region string,
  year string, month string, day string, hour string
)
STORED AS PARQUET
LOCATION 's3://<your-bucket>/AWSLogs/'
TBLPROPERTIES ('projection.enabled' = 'false');

MSCK REPAIR TABLE vpc_flow_logs;

-- ============================================================================
-- HUNT 1: Top egress destinations by bytes from one instance
-- (the canonical exfiltration query)
-- ============================================================================
SELECT dstaddr, dstport, sum(bytes)/1024/1024 AS mb, count(*) AS flows
FROM vpc_flow_logs
WHERE instance_id = 'i-0123456789abcdef0'
  AND flow_direction = 'egress'
  AND action = 'ACCEPT'
  AND year = '2026' AND month = '05' AND day = '08'
GROUP BY dstaddr, dstport
ORDER BY mb DESC
LIMIT 50;

-- ============================================================================
-- HUNT 2: Spike detection - any instance whose egress in the last hour is
-- 10x its rolling 24-hour average. Crude but effective.
-- ============================================================================
WITH last_hour AS (
  SELECT instance_id, sum(bytes) AS bytes_lh
  FROM vpc_flow_logs
  WHERE flow_direction = 'egress'
    AND from_unixtime(start_time) > current_timestamp - interval '1' hour
  GROUP BY instance_id
),
baseline AS (
  SELECT instance_id, sum(bytes)/24.0 AS bytes_per_hour_avg
  FROM vpc_flow_logs
  WHERE flow_direction = 'egress'
    AND from_unixtime(start_time) BETWEEN current_timestamp - interval '25' hour
                                       AND current_timestamp - interval '1' hour
  GROUP BY instance_id
)
SELECT a.instance_id, a.bytes_lh, b.bytes_per_hour_avg, a.bytes_lh / b.bytes_per_hour_avg AS spike_ratio
FROM last_hour a JOIN baseline b USING (instance_id)
WHERE a.bytes_lh > b.bytes_per_hour_avg * 10
ORDER BY spike_ratio DESC;

-- ============================================================================
-- HUNT 3: Outbound connections to weird ports (anything not 80/443/22 etc)
-- ============================================================================
SELECT instance_id, dstaddr, dstport, sum(bytes) AS bytes
FROM vpc_flow_logs
WHERE flow_direction = 'egress'
  AND action = 'ACCEPT'
  AND dstport NOT IN (80, 443, 22, 53, 25, 587, 465, 8080, 8443, 5432, 3306)
  AND from_unixtime(start_time) > current_timestamp - interval '24' hour
GROUP BY instance_id, dstaddr, dstport
HAVING sum(bytes) > 1000000
ORDER BY bytes DESC;

-- ============================================================================
-- HUNT 4: Inbound REJECT spikes (reconnaissance)
-- ============================================================================
SELECT srcaddr, count(*) AS reject_count, count(distinct dstport) AS distinct_ports
FROM vpc_flow_logs
WHERE flow_direction = 'ingress'
  AND action = 'REJECT'
  AND from_unixtime(start_time) > current_timestamp - interval '1' hour
GROUP BY srcaddr
HAVING count(*) > 100 AND count(distinct dstport) > 20
ORDER BY reject_count DESC;

-- ============================================================================
-- HUNT 5: VPC endpoint bypass (instances reaching S3 over the internet
-- when a VPC endpoint exists and should have been used)
-- ============================================================================
-- traffic-path = 8 means "through internet gateway" (vs through endpoint = 7)
-- Look for traffic to AWS service IPs that took the wrong path.
SELECT instance_id, dstaddr, dstport, sum(bytes) AS bytes, count(*) AS flows
FROM vpc_flow_logs
WHERE traffic_path = 8
  AND flow_direction = 'egress'
  AND from_unixtime(start_time) > current_timestamp - interval '24' hour
GROUP BY instance_id, dstaddr, dstport
ORDER BY bytes DESC
LIMIT 50;

QUERIES

echo
echo "=== STEP 3: what flow logs DO NOT capture ==="

cat <<'GAPS'

Flow logs DO NOT include:

1. Packet payload. Just metadata. You will not see HTTP paths, DNS query names,
   TLS SNI. For that, you need traffic mirroring (VPC Traffic Mirroring) or
   GuardDuty DNS logs.

2. DNS queries directly. AWS Route 53 Resolver logs are a separate service
   (Route 53 Resolver Query Logging). GuardDuty consumes them automatically.

3. Traffic to/from EC2 metadata service (169.254.169.254). That request never
   leaves the instance. No flow log entry.

4. Encrypted tunnel internals. If the host is using a VPN to a TOR entry node,
   you see the TLS flow to the entry node, not what's inside.

5. Traffic between containers on the same host (in EKS, this is sometimes
   visible if using AWS VPC CNI with one IP per pod, but not always).

6. Skipped packets (action = NODATA in some configurations).

This is why GuardDuty is worth it. It correlates flow logs + DNS logs +
CloudTrail + EKS audit logs + S3 data events into single findings. Building
this yourself is expensive at scale.

GAPS

echo
echo "=== STEP 4: cleanup ==="
read -r -p "Press enter to clean up..."
aws_cli ec2 delete-flow-logs --flow-log-ids "$FL_ID" || true
aws_cli s3 rm "s3://${LOG_BUCKET}" --recursive || true
aws_cli s3api delete-bucket --bucket "$LOG_BUCKET" || true
echo "Done."
