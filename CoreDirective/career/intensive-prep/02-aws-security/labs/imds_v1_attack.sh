#!/usr/bin/env bash
# Lab: IMDSv1 SSRF attack and IMDSv2 fix
# Objective: Demonstrate the Capital One breach pattern. An app server with a
#   server-side request forgery (SSRF) vuln on an EC2 instance running IMDSv1
#   leaks its instance role credentials to an attacker.
#
# What an interviewer will ask:
#   1. "Walk me through the Capital One breach. What was the misconfig?"
#   2. "Why does IMDSv2 use a session token? What attack does that block?"
#   3. "What is the IMDS hop limit and why does it matter for containers?"
#
# Real breach reference: Capital One 2019, $190M FTC settlement, 100M records,
#   Paige Thompson exploited an SSRF in a misconfigured WAF to hit 169.254.169.254
#   on EC2 with IMDSv1 enabled, stole role credentials, used them to read S3.

set -euo pipefail
REGION="${AWS_REGION:-us-east-1}"
PROFILE="${AWS_PROFILE:-default}"
PREFIX="lab-imds-$(date +%s)"

aws_cli() { aws --profile "$PROFILE" --region "$REGION" "$@"; }

echo "=== PART A: simulated SSRF against IMDSv1 (no AWS needed) ==="

# This part runs locally and explains the attack.
cat <<'PARTA'

Capital One breach in plain English:

  Attacker -> WAF SSRF vuln -> EC2 instance -> http://169.254.169.254/latest/meta-data/iam/security-credentials/role-name

  The link-local address 169.254.169.254 is the EC2 metadata service. With IMDSv1,
  ANY HTTP GET from inside the instance returns the role's temporary credentials.
  No auth, no session token. If an app server has any SSRF or request proxy bug,
  the attacker pivots to AWS API calls signed with that role.

The credential response looks like:
  {
    "Code": "Success",
    "AccessKeyId": "ASIA...",
    "SecretAccessKey": "...",
    "Token": "FwoGZX...",
    "Expiration": "2026-05-08T20:00:00Z"
  }

The attacker then runs:
  aws sts get-caller-identity         # confirms creds work
  aws s3 ls                           # finds buckets
  aws s3 cp s3://victim-bucket/. . --recursive

PARTA

echo
echo "=== PART B: IMDSv2 fix and demonstration ==="

cat <<'PARTB'

IMDSv2 fix in three layers:

LAYER 1: session token requirement
  Step 1: PUT /latest/api/token with X-aws-ec2-metadata-token-ttl-seconds: 21600
  Step 2: GET /latest/meta-data/... with X-aws-ec2-metadata-token: <token>

  Why this kills SSRF: SSRF attacks usually only support GET. They cannot send PUT
  with custom headers easily. The token requirement breaks the attack chain.

LAYER 2: hop limit
  IMDSv2 default hop limit is 1. The IP TTL on the response is 1, so the packet
  cannot escape the instance. If a Docker container tries to reach IMDS through
  the host network, it fails (because that adds a hop).

  Set hop limit to 2 only if you have a reason. Most container workloads should
  use IMDSv2 with hop limit 1 plus a sidecar that proxies AWS API calls, or use
  IRSA on EKS instead.

LAYER 3: account-level enforcement
  Run once per region:
    aws ec2 modify-instance-metadata-defaults \
      --http-tokens required \
      --http-put-response-hop-limit 2 \
      --instance-metadata-tags enabled

  This sets the default for all NEW instances launched in this account/region.
  Existing instances need to be modified individually:
    aws ec2 modify-instance-metadata-options \
      --instance-id i-... \
      --http-tokens required \
      --http-endpoint enabled \
      --http-put-response-hop-limit 1

PARTB

echo
echo "=== PART C: hands-on test (requires AWS account) ==="
read -r -p "Run actual EC2 launch? (y/n): " run_aws
if [[ "$run_aws" != "y" ]]; then
  echo "Skipping the AWS portion. Re-run with 'y' when you have a sandbox."
  exit 0
fi

# Find a default VPC + subnet
VPC_ID=$(aws_cli ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text)
SUBNET_ID=$(aws_cli ec2 describe-subnets --filters Name=vpc-id,Values=$VPC_ID --query 'Subnets[0].SubnetId' --output text)
AMI=$(aws_cli ec2 describe-images --owners amazon --filters "Name=name,Values=al2023-ami-2023.*-x86_64" --query 'sort_by(Images, &CreationDate)[-1].ImageId' --output text)

echo "Launching IMDSv1-enabled instance (VULNERABLE)..."
VULN_ID=$(aws_cli ec2 run-instances \
  --image-id "$AMI" \
  --instance-type t3.micro \
  --subnet-id "$SUBNET_ID" \
  --metadata-options "HttpTokens=optional,HttpEndpoint=enabled,HttpPutResponseHopLimit=2" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${PREFIX}-vuln}]" \
  --query 'Instances[0].InstanceId' --output text)

echo "Launching IMDSv2-required instance (SECURE)..."
SAFE_ID=$(aws_cli ec2 run-instances \
  --image-id "$AMI" \
  --instance-type t3.micro \
  --subnet-id "$SUBNET_ID" \
  --metadata-options "HttpTokens=required,HttpEndpoint=enabled,HttpPutResponseHopLimit=1" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${PREFIX}-safe}]" \
  --query 'Instances[0].InstanceId' --output text)

echo "Vulnerable: $VULN_ID  | Secure: $SAFE_ID"

echo
echo "From a shell on the VULNERABLE instance, this works:"
echo "  curl http://169.254.169.254/latest/meta-data/iam/security-credentials/"
echo
echo "From a shell on the SECURE instance, the same curl returns 401:"
echo "  curl http://169.254.169.254/latest/meta-data/iam/security-credentials/"
echo "  HTTP/1.1 401 Unauthorized"
echo
echo "On the SECURE instance, the proper flow is:"
echo "  TOKEN=\$(curl -s -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 60')"
echo "  curl -s -H \"X-aws-ec2-metadata-token: \$TOKEN\" http://169.254.169.254/latest/meta-data/iam/security-credentials/"

read -r -p "Press enter to terminate both instances..."
aws_cli ec2 terminate-instances --instance-ids "$VULN_ID" "$SAFE_ID" >/dev/null
echo "Terminated."

echo
echo "=== Detection ==="
cat <<'DETECT'
GuardDuty finding to look for:
  UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS
  UnauthorizedAccess:EC2/MaliciousIPCaller.Custom

If you see this, an instance role's credentials are being used from outside AWS.
Almost always a sign of IMDS theft. Rotate the role, snapshot the instance for
forensics, do not just terminate.
DETECT
