#!/usr/bin/env bash
# Lab: KMS envelope encryption walkthrough
# Objective: Show envelope encryption end to end. The KMS key encrypts a data
#   key. The data key encrypts the data. KMS never sees the data.
#
# What an interviewer will ask:
#   1. "Explain envelope encryption to a non-technical person in 60 seconds."
#   2. "Why does AWS use envelope encryption? Why not just call KMS directly?"
#   3. "What is the difference between Encrypt and GenerateDataKey?"

set -euo pipefail
REGION="${AWS_REGION:-us-east-1}"
PROFILE="${AWS_PROFILE:-default}"
PREFIX="lab-envelope-$(date +%s)"
aws_cli() { aws --profile "$PROFILE" --region "$REGION" "$@"; }

echo "=== STEP 1: create CMK ==="
KEY_ID=$(aws_cli kms create-key --description "$PREFIX" --query 'KeyMetadata.KeyId' --output text)
aws_cli kms create-alias --alias-name "alias/${PREFIX}" --target-key-id "$KEY_ID"
echo "Created CMK alias/${PREFIX} -> $KEY_ID"

echo
echo "=== STEP 2: prepare data ==="
PLAIN_FILE="/tmp/${PREFIX}-secret.txt"
echo "this is a 5 MB file standing in for a video, model weights, or PII corpus" > "$PLAIN_FILE"
# inflate to ~5MB so the cost difference between direct KMS encrypt and envelope encrypt is obvious
yes "filler line for the demo" | head -c 5000000 >> "$PLAIN_FILE"
ls -la "$PLAIN_FILE"

echo
echo "=== STEP 3: WRONG WAY (calling KMS Encrypt directly) ==="
echo "KMS Encrypt has a 4 KB plaintext limit. Files larger than 4 KB will fail."
set +e
aws_cli kms encrypt --key-id "$KEY_ID" \
  --plaintext "fileb://$PLAIN_FILE" \
  --output text --query CiphertextBlob 2>&1 | head -c 200
set -e
echo
echo "(if you saw an error about plaintext too large, that is the lesson)"

echo
echo "=== STEP 4: RIGHT WAY (envelope encryption) ==="
echo
echo "  ask KMS for a data key (256-bit AES, plaintext + ciphertext copies)"

DATA_KEY_RESPONSE=$(aws_cli kms generate-data-key --key-id "$KEY_ID" --key-spec AES_256 --output json)

PLAINTEXT_KEY=$(echo "$DATA_KEY_RESPONSE" | jq -r .Plaintext | base64 -d | xxd -p -c 9999)
ENCRYPTED_KEY=$(echo "$DATA_KEY_RESPONSE" | jq -r .CiphertextBlob)

echo "Got plaintext data key (hex first 16 bytes): ${PLAINTEXT_KEY:0:32}..."
echo "Got ciphertext data key (encrypted by CMK, base64 first 64 chars): ${ENCRYPTED_KEY:0:64}..."

echo
echo "  encrypt the file locally with openssl using the plaintext data key"
echo "$DATA_KEY_RESPONSE" | jq -r .Plaintext | base64 -d > /tmp/${PREFIX}-key.bin
openssl enc -aes-256-cbc -pbkdf2 -in "$PLAIN_FILE" -out /tmp/${PREFIX}-cipher.bin -pass file:/tmp/${PREFIX}-key.bin

echo "Cipher file size:"
ls -la /tmp/${PREFIX}-cipher.bin

echo
echo "  IMMEDIATELY zero the plaintext data key from memory"
PLAINTEXT_KEY=""
shred -u /tmp/${PREFIX}-key.bin 2>/dev/null || rm -f /tmp/${PREFIX}-key.bin

echo
echo "  store the ENCRYPTED data key alongside the cipher file (or in metadata)"
echo "$ENCRYPTED_KEY" > /tmp/${PREFIX}-encrypted-key.b64

echo
echo "=== STEP 5: decrypt path ==="
echo "  call KMS Decrypt on the encrypted data key to recover the plaintext key"
RECOVERED_KEY_B64=$(aws_cli kms decrypt \
  --ciphertext-blob "fileb://<(echo $ENCRYPTED_KEY | base64 -d)" \
  --output text --query Plaintext 2>/dev/null || true)

# bash heredoc with base64 -d does not always work cleanly, do it via temp file
echo "$ENCRYPTED_KEY" | base64 -d > /tmp/${PREFIX}-enckey.bin
RECOVERED_KEY_B64=$(aws_cli kms decrypt \
  --ciphertext-blob "fileb:///tmp/${PREFIX}-enckey.bin" \
  --output text --query Plaintext)

echo "$RECOVERED_KEY_B64" | base64 -d > /tmp/${PREFIX}-key.bin

echo "  decrypt the file with the recovered data key"
openssl enc -d -aes-256-cbc -pbkdf2 -in /tmp/${PREFIX}-cipher.bin -out /tmp/${PREFIX}-decrypted.txt -pass file:/tmp/${PREFIX}-key.bin

echo "First 80 bytes of decrypted file:"
head -c 80 /tmp/${PREFIX}-decrypted.txt
echo

# zero the plaintext key again
shred -u /tmp/${PREFIX}-key.bin 2>/dev/null || rm -f /tmp/${PREFIX}-key.bin

echo
cat <<'EXPLAIN'

=== Why envelope encryption matters ===

1. KMS limit: Encrypt API only handles 4 KB. Real data is gigabytes.

2. Cost: KMS Encrypt costs $0.03 per 10,000 requests. Encrypting a billion files
   directly via KMS is bankruptcy. With envelope encryption you call KMS once
   per data key (which can encrypt many files). At $0.03 per 10K calls,
   GenerateDataKey for batch jobs is 100x to 10000x cheaper.

3. Performance: Local AES is microseconds. KMS roundtrip is milliseconds.
   Envelope = bulk encrypt locally, only call KMS for the small key.

4. Defense: KMS never sees plaintext. Even if KMS were breached, the attacker
   needs the encrypted data files separately.

=== When the AWS SDK does this for you ===

S3 SSE-KMS: AWS does envelope encryption under the hood. You upload the file,
the S3 service calls GenerateDataKey on the CMK, encrypts the object with the
data key, stores the encrypted data key alongside the object metadata. With
"bucket key enabled", S3 caches one data key per bucket per minute, cutting
KMS calls 99%.

EBS volume encryption: same pattern. CMK encrypts the volume key. The volume
key encrypts the disk blocks. Key never leaves KMS.

RDS encryption at rest: same pattern.

Snowflake / Databricks customer-managed keys on AWS: they call your CMK to
unwrap the data key, run their compute, never persist the plaintext key.

=== Failure modes to know ===

- If the CMK is deleted or scheduled for deletion, every encrypted data key is
  unrecoverable. Same as losing the master key for everything. Set the deletion
  window to 30 days for production.

- Multi-region keys: replicas share key material. Useful for multi-region S3
  replication. The KEY ID and ARN are different per region, the material is the
  same.

- Cross-account: the consuming account needs both kms:Decrypt in its IAM AND
  the key policy must allow that account's principal. Two-sided check.

EXPLAIN

echo
echo "=== STEP 6: cleanup ==="
aws_cli kms delete-alias --alias-name "alias/${PREFIX}" || true
aws_cli kms schedule-key-deletion --key-id "$KEY_ID" --pending-window-in-days 7
rm -f /tmp/${PREFIX}-*
echo "Key scheduled for deletion."
