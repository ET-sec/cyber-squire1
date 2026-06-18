#!/usr/bin/env bash
# Lab: KMS grant abuse and the right scoping pattern
# Objective: Show how a sloppy CreateGrant call hands over decrypt to a wider
#   principal than intended, then show the scoped fix.
#
# What an interviewer will ask:
#   1. "What is a KMS grant and how is it different from a key policy statement?"
#   2. "If a service has CreateGrant on a key, what can it do?"
#   3. "Walk me through SSE-KMS. Where do grants show up?"

set -euo pipefail
REGION="${AWS_REGION:-us-east-1}"
PROFILE="${AWS_PROFILE:-default}"
PREFIX="lab-kms-grant-$(date +%s)"
aws_cli() { aws --profile "$PROFILE" --region "$REGION" "$@"; }

ACCOUNT_ID=$(aws_cli sts get-caller-identity --query Account --output text)

echo "=== STEP 1: create a CMK with a basic key policy ==="
cat > /tmp/${PREFIX}-keypol.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EnableRoot",
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::${ACCOUNT_ID}:root"},
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Sid": "AllowCreateGrantForLambdaService",
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": ["kms:CreateGrant", "kms:Decrypt", "kms:GenerateDataKey"],
      "Resource": "*"
    }
  ]
}
EOF

KEY_ID=$(aws_cli kms create-key \
  --policy file:///tmp/${PREFIX}-keypol.json \
  --description "${PREFIX}" \
  --query 'KeyMetadata.KeyId' --output text)

aws_cli kms create-alias --alias-name "alias/${PREFIX}" --target-key-id "$KEY_ID"

echo "Created key: $KEY_ID"

echo
echo "=== STEP 2: the abusable grant pattern ==="
cat <<'EXPLAIN'

Imagine your app calls CreateGrant from inside a Lambda to give a downstream
worker the ability to decrypt one specific record. A common mistake:

  aws kms create-grant \
    --key-id alias/my-key \
    --grantee-principal arn:aws:iam::123:role/worker-role \
    --operations Decrypt

That grants kms:Decrypt to worker-role on EVERY ciphertext encrypted under this
key. There is no scoping. Anyone with that role can decrypt anything.

The fix is grant constraints, specifically EncryptionContextEquals or
EncryptionContextSubset:

  aws kms create-grant \
    --key-id alias/my-key \
    --grantee-principal arn:aws:iam::123:role/worker-role \
    --operations Decrypt \
    --constraints EncryptionContextEquals='{tenant=acme,record_id=12345}'

The grant only works for ciphertexts encrypted with that exact context. The
context is part of the AAD (additional authenticated data) on the AES-GCM
encryption. Tampering with the context fails the decrypt.

Three things every engineer should know about grants:
  1. Grants are programmatic. They do not show up in the key policy. List them
     with "aws kms list-grants --key-id ...".
  2. Grants can be retired (immediate, by retiring principal) or revoked
     (delayed, by anyone with kms:RevokeGrant).
  3. Grant tokens take up to 5 minutes to be eventually consistent. For HA
     workloads, capture the GrantToken from CreateGrant and pass it explicitly.

EXPLAIN

echo
echo "=== STEP 3: prove the fix ==="

# Create a target role to receive the grant
cat > /tmp/${PREFIX}-trust.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::${ACCOUNT_ID}:root"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

TARGET_ROLE_ARN=$(aws_cli iam create-role \
  --role-name "${PREFIX}-target" \
  --assume-role-policy-document file:///tmp/${PREFIX}-trust.json \
  --query 'Role.Arn' --output text)

sleep 5

# Encrypt one record with context A
PLAIN_A="record-A-data"
PLAIN_B="record-B-data"
CIPH_A=$(aws_cli kms encrypt --key-id "$KEY_ID" \
  --plaintext "$(echo -n $PLAIN_A | base64)" \
  --encryption-context "tenant=acme,record_id=12345" \
  --query CiphertextBlob --output text)

CIPH_B=$(aws_cli kms encrypt --key-id "$KEY_ID" \
  --plaintext "$(echo -n $PLAIN_B | base64)" \
  --encryption-context "tenant=acme,record_id=99999" \
  --query CiphertextBlob --output text)

# Issue a SCOPED grant, only for record_id=12345
GRANT_ID=$(aws_cli kms create-grant \
  --key-id "$KEY_ID" \
  --grantee-principal "$TARGET_ROLE_ARN" \
  --operations Decrypt \
  --constraints "EncryptionContextEquals={tenant=acme,record_id=12345}" \
  --query GrantId --output text)

echo "Created scoped grant: $GRANT_ID"
echo
echo "Decrypt of CIPH_A with the right context: SHOULD SUCCEED"
echo "Decrypt of CIPH_B with a different context: SHOULD FAIL"
echo
echo "(In a real test you would assume the target role then run kms decrypt with"
echo " --encryption-context. The point is the grant is bound to that context.)"

echo
echo "=== STEP 4: cleanup ==="
read -r -p "Press enter to clean up... "

aws_cli kms revoke-grant --key-id "$KEY_ID" --grant-id "$GRANT_ID" || true
aws_cli iam delete-role --role-name "${PREFIX}-target" || true
aws_cli kms delete-alias --alias-name "alias/${PREFIX}" || true
aws_cli kms schedule-key-deletion --key-id "$KEY_ID" --pending-window-in-days 7
rm -f /tmp/${PREFIX}-*.json
echo "Key scheduled for deletion in 7 days."

cat <<'CLOSING'

KEY POINTS FOR INTERVIEW:

- Key policy is the root authority on a CMK. Without an Allow in the key policy,
  no IAM grant or grant call can override it. (Exception: AWS-managed keys.)

- Grants are short-lived programmatic permissions. They cannot grant kms:* admin
  ops (PutKeyPolicy, ScheduleKeyDeletion, etc). They CAN grant Decrypt, Encrypt,
  GenerateDataKey, ReEncryptFrom, ReEncryptTo, CreateGrant, RetireGrant,
  DescribeKey.

- Encryption context is integrity-checked (AES-GCM AAD). Always use it when you
  need authorization tied to data attributes (tenant id, record id, env=prod).

- aws:ViaService condition limits a key to a single service. Example:
    "Condition": {"StringEquals": {"kms:ViaService": "s3.us-east-1.amazonaws.com"}}
  Stops the same role from using kms:Decrypt for non-S3 calls.

CLOSING
