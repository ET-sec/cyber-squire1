#!/usr/bin/env bash
# Lab: ABAC (attribute-based access control) using IAM tags
# Objective: A developer can manage their own EC2 instances but not anyone else's,
#   without any account IDs or hardcoded resource lists in the policy.
#
# What an interviewer will ask:
#   1. "How does ABAC work in IAM and why is it useful at scale?"
#   2. "What stops a developer from changing their own tag to access someone else's resources?"
#   3. "Compare ABAC vs RBAC for a 50-person engineering org."

set -euo pipefail
REGION="${AWS_REGION:-us-east-1}"
PROFILE="${AWS_PROFILE:-default}"
PREFIX="lab-abac-$(date +%s)"

aws_cli() { aws --profile "$PROFILE" --region "$REGION" "$@"; }

echo "=== STEP 1: create two developer users with team tags ==="
aws_cli iam create-user --user-name "${PREFIX}-alice" --tags Key=team,Value=alpha >/dev/null
aws_cli iam create-user --user-name "${PREFIX}-bob"   --tags Key=team,Value=beta >/dev/null

echo
echo "=== STEP 2: write the ABAC policy ==="
# The key trick: aws:PrincipalTag/team must equal aws:ResourceTag/team
cat > /tmp/${PREFIX}-abac.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ManageEC2OwnedByMyTeam",
      "Effect": "Allow",
      "Action": ["ec2:StartInstances", "ec2:StopInstances", "ec2:RebootInstances", "ec2:TerminateInstances"],
      "Resource": "arn:aws:ec2:*:*:instance/*",
      "Condition": {
        "StringEquals": {"aws:ResourceTag/team": "${aws:PrincipalTag/team}"}
      }
    },
    {
      "Sid": "DescribeAll",
      "Effect": "Allow",
      "Action": ["ec2:Describe*"],
      "Resource": "*"
    },
    {
      "Sid": "TagInstancesAtCreation",
      "Effect": "Allow",
      "Action": "ec2:RunInstances",
      "Resource": "*",
      "Condition": {
        "StringEquals": {"aws:RequestTag/team": "${aws:PrincipalTag/team}"}
      }
    },
    {
      "Sid": "PreventTagModification",
      "Effect": "Deny",
      "Action": ["ec2:CreateTags", "ec2:DeleteTags"],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {"aws:ResourceTag/team": "${aws:PrincipalTag/team}"}
      }
    }
  ]
}
EOF

POLICY_ARN=$(aws_cli iam create-policy --policy-name "${PREFIX}-abac" \
  --policy-document file:///tmp/${PREFIX}-abac.json --query 'Policy.Arn' --output text)

aws_cli iam attach-user-policy --user-name "${PREFIX}-alice" --policy-arn "$POLICY_ARN"
aws_cli iam attach-user-policy --user-name "${PREFIX}-bob"   --policy-arn "$POLICY_ARN"

echo "Policy attached. Alice (team=alpha) and Bob (team=beta) now share the same policy."
echo "Alice can only touch instances tagged team=alpha. Bob only team=beta."

echo
echo "=== STEP 3: why this is powerful ==="
cat <<'EXPLAIN'

The critical pattern is ${aws:PrincipalTag/team} on the LEFT of the comparison
and aws:ResourceTag/team on the RIGHT. The IAM evaluation engine substitutes
the principal's tag value at request time. One policy, scales to N teams.

What stops Alice from changing her own tag to "beta"?
  - Alice has no iam:TagUser permission. The tag comes from Identity Center
    (or the IAM admin who created her). Self-service tag updates would be a
    privesc path. AWS docs explicitly warn about this:
    https://docs.aws.amazon.com/IAM/latest/UserGuide/access_iam-tags.html

What stops Alice from creating an instance tagged team=beta?
  - The TagInstancesAtCreation statement requires aws:RequestTag/team =
    aws:PrincipalTag/team. RunInstances will be denied if the tag does not match.

What if she creates an untagged instance?
  - The condition only allows RunInstances if the request tag matches. No tag
    means the condition is false. Denied. Add a separate Deny statement that
    explicitly blocks RunInstances without the team tag for belt-and-suspenders.

ABAC at scale: in a 100-team org, this is one policy instead of 100 RBAC roles.
RBAC still wins for sensitive cross-team access (security, finance) where the
authorization is a human decision, not a tag match.

EXPLAIN

echo
echo "=== STEP 4: cleanup ==="
read -r -p "Press enter to clean up... "
aws_cli iam detach-user-policy --user-name "${PREFIX}-alice" --policy-arn "$POLICY_ARN" || true
aws_cli iam detach-user-policy --user-name "${PREFIX}-bob"   --policy-arn "$POLICY_ARN" || true
aws_cli iam delete-policy --policy-arn "$POLICY_ARN" || true
aws_cli iam delete-user --user-name "${PREFIX}-alice" || true
aws_cli iam delete-user --user-name "${PREFIX}-bob" || true
rm -f /tmp/${PREFIX}-abac.json
echo "Done."
