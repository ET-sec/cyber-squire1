# Lab 03: Kubernetes Lateral Movement

## Attack Narrative

The `payments-api` pod was compromised via a vulnerable dependency (RCE in a JSON parser). The attacker now has shell-equivalent access inside the pod, which means access to the `payments-api` ServiceAccount token at `/var/run/secrets/kubernetes.io/serviceaccount/token`.

From there:

1. 14:00:05 Alice (real user, baseline): exec into payments-api pod. Normal dev activity.
2. 15:30:00 SA `payments-api` lists secrets in `kube-system` (denied, 403). Recon attempt.
3. 15:30:05 SA lists secrets in own namespace (allowed). Got DB creds.
4. 15:30:08 SA tries to exec into `coredns` in kube-system (denied).
5. 15:30:12 SA tries to bind cluster-admin to itself (denied).
6. 15:30:30 SA creates a privileged pod with `hostNetwork: true`, `hostPID: true`, `privileged: true`. Allowed (RBAC misconfig).
7. 15:30:45 SA execs into the privileged pod. Now attacker has node-level access.

The escalation pattern: when direct privilege escalation fails, attackers fall back to creating a privileged workload. RBAC that says "cannot bind cluster-admin" but allows "create pods with hostPID and privileged" is the gap.

## Detection Logic

ServiceAccounts performing any of: read kube-system secrets, exec into kube-system, create clusterrolebindings, create privileged pods, create pods with hostNetwork or hostPID.

The 403s are also signal. A SA that gets denied on those operations is probing.

## Run It

```bash
cd labs/lab_03_lateral_movement_k8s

# All SA actions
jq 'select(.user.username | startswith("system:serviceaccount:"))' audit.log

# All forbidden actions (signal of probing)
jq 'select(.responseStatus.reason == "Forbidden" or .responseStatus.code == 403)' audit.log

# Privileged pods created
jq 'select(.verb == "create" and .objectRef.resource == "pods" and .requestObject.spec.containers[]?.securityContext.privileged == true)' audit.log

# host namespace abuse
jq 'select(.requestObject.spec.hostNetwork == true or .requestObject.spec.hostPID == true)' audit.log
```

## Triage Outcome

Verdict: True Positive, Critical.

Page oncall. Cordon and drain the node hosting payments-api. Delete the privileged util-pod-debug pod. Rotate all secrets in the `payments` namespace. Review RBAC for the `payments-api` SA: it should not have create-pods permission with privileged or host namespace allowed. Patch the original RCE in payments-api. Hunt for similar pod creation patterns across the cluster for the last 30 days.

Pair with Falco runtime alerts. Falco's default rule "Launch Privileged Container" should have fired in parallel. The combination (audit log + Falco) is high-confidence detection.

## Interviewer Questions

- "How does this map to ATT&CK?" T1610 (Deploy Container) for the privileged pod creation. T1078.004 (Cloud Accounts) for the SA token abuse. T1611 (Escape to Host) is the next step after exec into the privileged pod.
- "Why didn't the cluster admin RBAC stop this?" The SA had `pods/create` permission, which is enough. RBAC granularity in K8s does not natively distinguish "create privileged pod" from "create pod" without admission control. You need a Pod Security Admission or OPA Gatekeeper policy on top.
- "What admission controllers help?" Pod Security Admission with `restricted` profile. OPA Gatekeeper with constraint templates. Kyverno with policies. They reject privileged or host-namespace pods at admission.
- "Tesla 2018?" Exposed K8s dashboard, no auth, attacker created pods. Crypto miner. The detection that should have fired: anonymous user creating any resource. The detection that did fire: a year later, when AV caught the egress.
- "Falco vs audit log?" Audit is API-level. Falco is syscall-level. You need both. API tells you the intent (`create pod`), syscall tells you the behavior (`shell spawned in container`).

## Variant: Coverage Hardening

Three additions:
1. PSA enforcement on `restricted` for all namespaces except infra ones.
2. Falco custom rule for SA tokens read from disk by anything other than kubelet.
3. Network policy denying pod-to-pod traffic across namespaces by default.

Defense in depth: even if the SA has the RBAC, admission rejects, runtime catches escape, network limits blast radius.
