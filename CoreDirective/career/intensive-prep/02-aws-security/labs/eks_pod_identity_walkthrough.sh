#!/usr/bin/env bash
# Lab: EKS Pod Identity (and IRSA) walkthrough
# Objective: Show both identity mechanisms for pods to assume AWS IAM roles.
#   IRSA (older, OIDC-based) and EKS Pod Identity (newer, agent-based, since 2023).
#
# What an interviewer will ask:
#   1. "Walk me through what happens cryptographically when an EKS pod calls AWS APIs via IRSA."
#   2. "What is the difference between IRSA and Pod Identity?"
#   3. "Why never give the EKS node IAM role pod-level permissions?"
#
# This lab is mostly explanatory plus the YAML you would apply. EKS cluster
# provisioning is too expensive to spin up for a lab.

set -euo pipefail
PREFIX="lab-eks-pi"
echo "=== EKS Pod Identity vs IRSA: deep walkthrough ==="

cat <<'BACKGROUND'

CONTEXT: Kubernetes pods need AWS API access. The naive solution is to give
the EKS worker node an IAM role with broad permissions. Every pod on the
node inherits those permissions via IMDS. That is a multi-tenant disaster:
one compromised pod has the keys to every API the node role can call.

Two AWS solutions exist. Both bind a pod to a specific IAM role.

================================================================================
OPTION 1: IRSA (IAM Roles for Service Accounts) - introduced 2019
================================================================================

How it works:

1. Each EKS cluster has an OIDC provider URL (IAM identifier for the cluster).
   You register that OIDC provider with IAM:

     aws iam create-open-id-connect-provider \
       --url https://oidc.eks.us-east-1.amazonaws.com/id/ABCD1234 \
       --client-id-list sts.amazonaws.com \
       --thumbprint-list <kid-thumbprint>

2. You create an IAM role with a trust policy that says: "trust the OIDC
   provider, and only when the federated token's sub claim matches a specific
   service account in a specific namespace":

   {
     "Effect": "Allow",
     "Principal": {"Federated": "arn:aws:iam::ACCOUNT:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/ABCD1234"},
     "Action": "sts:AssumeRoleWithWebIdentity",
     "Condition": {
       "StringEquals": {
         "oidc.eks.us-east-1.amazonaws.com/id/ABCD1234:sub": "system:serviceaccount:my-namespace:my-sa",
         "oidc.eks.us-east-1.amazonaws.com/id/ABCD1234:aud": "sts.amazonaws.com"
       }
     }
   }

3. You annotate the Kubernetes ServiceAccount with the role ARN:

     apiVersion: v1
     kind: ServiceAccount
     metadata:
       name: my-sa
       namespace: my-namespace
       annotations:
         eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT:role/my-irsa-role

4. Pod uses that ServiceAccount. EKS injects two things into the pod:
   - AWS_ROLE_ARN environment variable
   - AWS_WEB_IDENTITY_TOKEN_FILE pointing to a projected token file at
     /var/run/secrets/eks.amazonaws.com/serviceaccount/token

5. AWS SDK in the pod sees those env vars, calls sts:AssumeRoleWithWebIdentity
   with the projected token, gets back temporary credentials, uses them.

6. The token is auto-rotated by kubelet every hour. SDK refresh is automatic.

Cryptographic detail interviewers like:
- The projected token is a signed JWT. The signature is verified by AWS using
  the cluster's OIDC public keys (the JWKS).
- "sub" claim is constructed by EKS as system:serviceaccount:NAMESPACE:NAME.
- "aud" must match what the trust policy allows (default: sts.amazonaws.com).
- TTL is configurable via the projected volume but defaults to 1 hour.

Failure modes:
- Cluster recreated: OIDC provider URL changes. Trust policies must be updated.
- Cross-account: target account must trust the source cluster's OIDC URL.
- aud mismatch: silent 403 from STS. Hard to debug without CloudTrail.

================================================================================
OPTION 2: EKS Pod Identity - introduced November 2023
================================================================================

Why AWS built this even though IRSA worked:
- IRSA requires per-cluster OIDC provider setup
- Cross-account IRSA is painful (every consuming account must register the
  source cluster's OIDC provider)
- Trust policy condition strings are long and easy to misconfigure

Pod Identity replaces all of that with an EKS Pod Identity Agent (a DaemonSet
that AWS deploys via the eks-pod-identity-agent add-on).

How it works:

1. Install the add-on on the cluster:
     aws eks create-addon --cluster-name my-cluster \
       --addon-name eks-pod-identity-agent

2. Create an IAM role with a SIMPLE trust policy:
     {
       "Effect": "Allow",
       "Principal": {"Service": "pods.eks.amazonaws.com"},
       "Action": ["sts:AssumeRole", "sts:TagSession"]
     }

3. Create a Pod Identity Association linking a Kubernetes service account
   to the IAM role:
     aws eks create-pod-identity-association \
       --cluster-name my-cluster \
       --namespace my-namespace \
       --service-account my-sa \
       --role-arn arn:aws:iam::ACCOUNT:role/my-pod-identity-role

4. Use the service account in your pod:
     apiVersion: apps/v1
     kind: Deployment
     spec:
       template:
         spec:
           serviceAccountName: my-sa
           containers: [...]

5. Pod calls AWS. SDK sees a special env var injected by the agent. It calls
   the local agent (a unix socket / loopback listener) which calls AssumeRole
   on the pod's behalf. The agent has its own IAM role (the agent role) that
   is allowed to AssumeRole into your target role.

Why it is better:
- One trust policy template across all roles. No per-cluster OIDC URL.
- Cross-account works without setting up OIDC providers.
- Source identity is preserved (you can see the cluster, namespace, SA in
  CloudTrail, not just the role assumption).
- Session tags include kubernetes.io/cluster, kubernetes.io/namespace,
  kubernetes.io/service-account-name. ABAC works on these.

When to still use IRSA:
- Older EKS clusters (< 1.23 may not support the agent)
- You need to keep the auth flow purely OIDC for compliance reasons
- You are using Kubernetes-native projected tokens for other purposes too

================================================================================
THE NODE-ROLE TRAP
================================================================================

If the node IAM role has S3 access and a pod doesn't use IRSA or Pod Identity,
the pod inherits S3 access via IMDS. Solutions:

1. Make node role have ONLY what kubelet needs:
   - AmazonEKSWorkerNodePolicy
   - AmazonEKS_CNI_Policy (if using AWS VPC CNI)
   - AmazonEC2ContainerRegistryReadOnly
   Nothing else.

2. Block IMDS access from pods:
   - Use IMDSv2 with hop limit 1 (default since EKS 1.23 with managed node groups)
   - Use a network policy that drops 169.254.169.254 traffic from non-system pods
   - Or use SecurityGroupsForPods feature to attach a SG to pods that denies IMDS

3. Pod Security Standards (restricted) prevents pods running as root or with
   hostNetwork=true, both of which make IMDS-based privesc easier.

================================================================================
DETECTION
================================================================================

GuardDuty for EKS:
  Discovery:Kubernetes/MaliciousIPCaller
  Execution:Kubernetes/ExecInPod
  PrivilegeEscalation:Kubernetes/PrivilegedContainer
  CredentialAccess:Kubernetes/MaliciousIPCaller (for kubectl from new IP)

CloudTrail to watch for:
  AssumeRoleWithWebIdentity from unusual aud / sub claims
  AssumeRole calls to roles with broad permissions from pods.eks.amazonaws.com

================================================================================
WHAT TO SAY IN INTERVIEWS
================================================================================

"IRSA uses the cluster's OIDC provider. Each pod gets a projected JWT, the
SDK exchanges it for temporary creds via AssumeRoleWithWebIdentity. Pod
Identity is newer, uses an agent on each node and a per-association trust
policy. Both bind the pod to a specific IAM role with no IMDS dependency.
The mistake to avoid is letting the node role hold pod-level permissions,
because then any pod with IMDS access inherits them. Block IMDS from pods,
keep node role minimal, use IRSA or Pod Identity."

BACKGROUND

cat <<'YAML'

================================================================================
APPENDIX: copy-paste YAML you would apply
================================================================================

# ServiceAccount for IRSA
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  namespace: production
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/my-app-role

---
# Deployment using the SA
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: production
spec:
  replicas: 3
  selector: {matchLabels: {app: my-app}}
  template:
    metadata: {labels: {app: my-app}}
    spec:
      serviceAccountName: my-app
      automountServiceAccountToken: true
      containers:
        - name: app
          image: my-app:1.0.0
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            runAsNonRoot: true
            runAsUser: 10001
            capabilities: {drop: [ALL]}
          resources:
            requests: {cpu: 100m, memory: 128Mi}
            limits: {cpu: 500m, memory: 512Mi}

---
# NetworkPolicy denying IMDS access from app pods
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-imds
  namespace: production
spec:
  podSelector: {matchLabels: {app: my-app}}
  policyTypes: [Egress]
  egress:
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
            except: ["169.254.169.254/32"]

YAML

echo "End of walkthrough."
