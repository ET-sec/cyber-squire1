# Drill 02: Multi-Tenant Kubernetes (EKS)

## Prompt
"You run an EKS cluster shared by 8 product teams. Each team has its own namespace, its own service accounts, its own Helm releases. Threat model the platform."

## Scope (Phase 1)

Assets:
- Workload data per tenant (varies, some PII, some payment, some non-sensitive)
- Cluster control plane and etcd
- Container images in ECR
- Secrets in External Secrets Operator backed by AWS Secrets Manager
- IAM roles for service accounts (IRSA)

Actors:
- Tenant developers (push code, deploy via GitOps)
- Cluster admin (platform team)
- External attackers (internet-facing services)
- Malicious tenant (insider threat)
- Compromised CI/CD pipeline

Data classes:
- Per-tenant application data (sensitivity varies)
- Cluster credentials and tokens (high)
- Secrets (high)

Assumptions:
- Single cluster, single AWS account
- Argo CD is the GitOps engine
- Pod Security Standards enforced at restricted level
- Network policies mostly default-deny
- Falco runs as DaemonSet

## DFD

```
                                       INTERNET BOUNDARY
[ User ] --HTTPS--> ( ALB / Ingress Controller )
                                |
- - - - - - - - - - - - - - - - | - - - - - - - - - - - - - VPC BOUNDARY
                                v
                         ( Service A in ns-team1 )       
                                | <- network policy
                                v
                         ( Service B in ns-team1 )
                                |
                       IRSA-bound IAM role
                                |
- - - - - - - - - - - - - - - - | - - - - - - - - - - AWS ACCOUNT BOUNDARY
                                v
                              ===========
                              | S3, RDS |
                              ===========

[ Developer ] --git push--> ( GitHub ) --> ( Argo CD ) --> ( apiserver )
                                                              |
                                                              v
                                                           = etcd =

[ Admin ] --kubectl--> ( apiserver )
                            |
                  (RBAC, audit log)
                            |
                            v
                       Datadog/Falco

- - - - - - - - - - - - NAMESPACE BOUNDARY (logical, not strong)
ns-team1 | ns-team2 | ns-team3 | ... | ns-team8
```

Trust boundaries:
1. Internet to ALB (TB1)
2. Ingress to pod (TB2, network)
3. Pod to AWS API via IRSA (TB3, AWS account boundary)
4. Tenant namespace to tenant namespace (TB4, soft boundary)
5. Tenant pod to control plane (TB5)
6. Argo CD to apiserver (TB6, GitOps deploy boundary)
7. Container runtime to host kernel (TB7, escape boundary)

## STRIDE matrix

| # | Boundary | STRIDE | Threat | L | I | Risk |
|---|----------|--------|--------|---|---|------|
| 1 | TB1 | S | Forged JWT in header bypasses ingress auth | M | H | H |
| 2 | TB2 | E | Pod in ns-team1 talks to pod in ns-team2 because no NetworkPolicy | H | H | H |
| 3 | TB3 | E | Service account token mounted in pod, attacker steals and assumes IAM role | M | H | H |
| 4 | TB3 | E | IRSA role over-permissioned (s3:* across tenant buckets) | M | H | H |
| 5 | TB4 | I | Tenant A reads tenant B secrets via ESO misconfig | L | H | M |
| 6 | TB5 | E | Tenant gains RBAC `cluster-admin` via mis-bound RoleBinding | L | H | M |
| 7 | TB6 | T | Attacker pushes malicious manifest to Git, Argo Sync deploys it | M | H | H |
| 8 | TB7 | E | Container escape via kernel CVE, attacker on host | L | H | M |
| 9 | TB7 | E | Privileged container deployed because admission missed it | L | H | M |
| 10 | TB1 | D | One tenant's noisy neighbor exhausts node CPU/mem | H | M | H |
| 11 | TB6 | R | Argo applies manifest with no audit of who triggered it | L | M | L |
| 12 | TB3 | I | Pod logs leak secrets that were passed via env vars | M | M | M |
| 13 | TB5 | T | Tenant uses `kubectl exec` into another tenant pod via shared kubeconfig | L | H | M |
| 14 | TB1 | I | Ingress error pages reveal upstream service names and versions | M | L | L |
| 15 | TB7 | T | Attacker mounts hostPath, modifies /etc on node | L | H | M |
| 16 | TB3 | S | Pod uses default service account with cluster-wide permissions | M | H | H |

## Top 10

1. (#2) Lateral movement via missing NetworkPolicy
2. (#3) IRSA token theft
3. (#4) Over-permissioned IRSA role
4. (#7) GitOps supply chain attack
5. (#1) Ingress JWT forgery
6. (#16) Default service account abuse
7. (#10) Noisy-neighbor DoS
8. (#9) Privileged container deployed
9. (#5) ESO secret cross-tenant read
10. (#8) Container escape

## Mitigations

| # | Primary | Compensating | Cost |
|---|---------|--------------|------|
| 1 | Default-deny NetworkPolicy in every tenant namespace, Cilium for L7 enforcement | Falco rule on cross-namespace connections | M |
| 2 | Disable automount of SA token unless explicitly needed, use projected tokens with short TTL | Falco rule on `/var/run/secrets/...` reads from non-app processes | L |
| 3 | IRSA role narrowly scoped per workload, condition on `aws:SourceArn` and `aws:PrincipalTag` | Access Analyzer, monthly IAM review | M |
| 4 | Argo CD signed commits, image admission via Cosign verification, branch protection | OPA Gatekeeper denies unsigned images | M |
| 5 | Strong ingress auth (OIDC plus mTLS where possible), JWT signature pinning | Anomaly detection on auth failures | M |
| 6 | Disable default SA automounting, every workload uses a named SA with explicit RBAC | Audit Argo manifests for SA bindings | L |
| 7 | Resource quotas and LimitRanges per namespace, Karpenter overflow with priorities | Datadog alert on namespace pressure | L |
| 8 | OPA Gatekeeper blocks `privileged: true`, `hostNetwork`, `hostPID`, `hostPath`, root user | Falco runtime detection if it gets through | M |
| 9 | ESO Push uses tenant-scoped SecretStore with IAM condition keyed to namespace | Tenant cannot create SecretStore CRDs (RBAC) | L |
| 10 | Bottlerocket OS, frequent node rotation, gVisor or Kata for high-risk tenants | Falco syscalls anomaly, kernel CVE patching SLA | H |

## Residual risk

After mitigations: 0 HIGH, 5 MEDIUM, 11 LOW.

MEDIUMs accepted:
- Container escape: accepted because kernel CVEs are unpredictable. Compensation is fast node rotation, Bottlerocket, Falco.
- Argo CD signing bypass: accepted because Cosign requires cooperative signers, mitigation is admission policy plus monitoring.
- ESO secret cross-tenant: accepted because IAM scoping is the core control, compensation is namespace-scoped store CRDs.
- Privileged container: accepted because Gatekeeper plus runtime gives us defense in depth.
- Noisy neighbor: accepted because quotas can be misconfigured per release, compensation is alerting.

The HIGH I would not accept: missing default-deny NetworkPolicy. Day one task.

## Detections

- Cross-namespace traffic: Cilium Hubble flow logs, alert on any flow where source namespace != destination namespace and not in allowlist.
- IRSA abuse: CloudTrail `AssumeRoleWithWebIdentity` filtered by `userIdentity.sessionContext.attributes.creationDate`, alert if a token is used outside the expected pod lifetime.
- Container escape: Falco rules: `Mount Launched in Privileged Container`, `Read sensitive file untrusted`, `Outbound Connection to C2 Servers`.
- Argo drift: Argo CD audit log shipped to Datadog, alert on any manual sync that bypasses Git.
- Privileged container deployed: OPA Gatekeeper deny event in audit log, plus Falco fallback.

Closing line:
"In a multi-tenant cluster the namespace is a logical boundary, not a security boundary. The real boundary is the kernel and the IAM role. So I treat namespace separation as a convention and lean on NetworkPolicy, Pod Security Standards, IRSA scoping, and Falco for the actual isolation. The residual risk is bounded by how fast we patch nodes and how strict admission stays."
