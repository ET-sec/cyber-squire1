#!/usr/bin/env bash
# Lab: Lambda execution role and resource-based policy
# Objective: Show the difference between execution role (what the function code
#   can do) and resource-based policy (who can invoke the function). Demonstrate
#   tenant isolation in a multi-tenant SaaS Lambda.
#
# What an interviewer will ask:
#   1. "Difference between execution role and resource policy on Lambda?"
#   2. "How do you stop one customer from invoking another customer's function?"
#   3. "Where do Lambda function URLs live in the auth model?"

set -euo pipefail
REGION="${AWS_REGION:-us-east-1}"
PROFILE="${AWS_PROFILE:-default}"
PREFIX="lab-lambda-$(date +%s)"
aws_cli() { aws --profile "$PROFILE" --region "$REGION" "$@"; }

ACCOUNT_ID=$(aws_cli sts get-caller-identity --query Account --output text)

echo "=== STEP 1: build a Lambda that processes per-tenant S3 data ==="

# Multi-tenant S3 bucket with prefixes per tenant
BUCKET="${PREFIX}-tenant-data-${ACCOUNT_ID}"
aws_cli s3 mb "s3://${BUCKET}"
aws_cli s3api put-public-access-block --bucket "$BUCKET" \
  --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

echo "tenant-acme-secret" | aws_cli s3 cp - "s3://${BUCKET}/tenants/acme/data.txt"
echo "tenant-globex-secret" | aws_cli s3 cp - "s3://${BUCKET}/tenants/globex/data.txt"

# Execution role - this is what the LAMBDA CODE can do
cat > /tmp/${PREFIX}-trust.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

ROLE_ARN=$(aws_cli iam create-role \
  --role-name "${PREFIX}-exec" \
  --assume-role-policy-document file:///tmp/${PREFIX}-trust.json \
  --query 'Role.Arn' --output text)

aws_cli iam attach-role-policy --role-name "${PREFIX}-exec" \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# THE KEY PATTERN: scope S3 access to the tenant prefix using session policy
# at invocation time. The execution role can read from any tenant prefix, but
# the *invocation* uses an STS session policy that narrows to one tenant.
cat > /tmp/${PREFIX}-s3pol.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:ListBucket"],
    "Resource": [
      "arn:aws:s3:::${BUCKET}",
      "arn:aws:s3:::${BUCKET}/tenants/*"
    ]
  }]
}
EOF

aws_cli iam put-role-policy --role-name "${PREFIX}-exec" \
  --policy-name "s3-access" --policy-document file:///tmp/${PREFIX}-s3pol.json

echo "Wait 10s for IAM consistency..."
sleep 10

# Lambda function code
mkdir -p /tmp/${PREFIX}-src
cat > /tmp/${PREFIX}-src/index.py <<'EOF'
import boto3, os, json
def handler(event, context):
    tenant = event.get('tenant')
    if not tenant or '/' in tenant or '..' in tenant:
        return {"error": "invalid tenant"}
    s3 = boto3.client('s3')
    bucket = os.environ['BUCKET']
    key = f"tenants/{tenant}/data.txt"
    obj = s3.get_object(Bucket=bucket, Key=key)
    return {"tenant": tenant, "data": obj['Body'].read().decode()}
EOF
(cd /tmp/${PREFIX}-src && zip -q /tmp/${PREFIX}.zip index.py)

aws_cli lambda create-function \
  --function-name "${PREFIX}-fn" \
  --runtime python3.12 --role "$ROLE_ARN" \
  --handler index.handler \
  --zip-file fileb:///tmp/${PREFIX}.zip \
  --environment "Variables={BUCKET=${BUCKET}}" \
  --timeout 10 >/dev/null

echo "Lambda created. Testing happy path."
aws_cli lambda invoke --function-name "${PREFIX}-fn" \
  --payload "$(echo -n '{"tenant": "acme"}' | base64)" \
  /tmp/${PREFIX}-out.json
cat /tmp/${PREFIX}-out.json

echo
echo "=== STEP 2: tenant isolation flaw and the fix ==="

cat <<'EXPLAIN'

The vuln: the function trusts event.tenant. If the API gateway in front does
not authenticate the user OR does not bind the tenant claim to the JWT, an
attacker passes tenant=victim and reads someone else's data.

Two fixes, both should be in production:

FIX 1: API Gateway Lambda authorizer that pulls tenant from the JWT and
overwrites event.tenant before the Lambda runs. The function never reads
tenant from the request body.

FIX 2: When invoking the Lambda from upstream, pass a session policy that
locks S3 to ONE tenant prefix, even though the execution role permits all
tenant prefixes. This is defense in depth, in case the input validation
fails.

  aws sts assume-role \
    --role-arn arn:aws:iam::123:role/upstream-invoker \
    --role-session-name tenant-acme \
    --policy '{
      "Version":"2012-10-17",
      "Statement":[{
        "Effect":"Allow",
        "Action":"lambda:InvokeFunction",
        "Resource":"arn:aws:lambda:*:*:function:tenant-fn",
        "Condition":{"StringEquals":{"lambda:SourceFunctionArn":"...","x-tenant-id":"acme"}}
      }]
    }'

The session policy is the *intersection* with the role's permissions. It can
only narrow, not widen.

EXPLAIN

echo
echo "=== STEP 3: resource-based policy on Lambda ==="

# Allow ONE other account or service to invoke
aws_cli lambda add-permission \
  --function-name "${PREFIX}-fn" \
  --statement-id allow-apigateway \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-account "$ACCOUNT_ID" \
  --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:abc123def4/*"

aws_cli lambda get-policy --function-name "${PREFIX}-fn" --query Policy --output text | jq .

cat <<'EXPLAIN2'

Resource-based policy on Lambda answers: WHO can call this function?

It is separate from the IAM identity policy of the caller. Both must allow.

Common mistake: putting "*" as Principal with no source-arn or source-account
condition. That makes the function callable by any service in the world that
spoofs the principal. Always include source-account + source-arn.

For Lambda function URLs (the recent feature), the auth type is either
AWS_IAM or NONE. NONE = public, no auth, no IAM. Use NONE only behind a CDN
that does its own auth, or for true public webhooks. For everything else,
AWS_IAM and validate the SigV4 signature.

EXPLAIN2

echo
echo "=== STEP 4: cleanup ==="
read -r -p "Press enter to clean up... "
aws_cli lambda delete-function --function-name "${PREFIX}-fn" || true
aws_cli iam delete-role-policy --role-name "${PREFIX}-exec" --policy-name "s3-access" || true
aws_cli iam detach-role-policy --role-name "${PREFIX}-exec" \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole || true
aws_cli iam delete-role --role-name "${PREFIX}-exec" || true
aws_cli s3 rm "s3://${BUCKET}" --recursive || true
aws_cli s3 rb "s3://${BUCKET}" || true
rm -rf /tmp/${PREFIX}*
echo "Done."
