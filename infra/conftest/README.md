# Compose Admission Control with Conftest

OPA-based admission gate for the CoreDirective Docker Compose stack.
Mirrors the role of OPA Gatekeeper for Kubernetes admission, applied to
`COREDIRECTIVE_ENGINE/docker-compose.yaml` at PR time.

Same Rego language as the Terraform OPA policies under
`terraform/cd-do-infrastructure/policy/`. Same enforcement concept,
applied to a different artifact.

## Policies

| File | Type | What it gates |
|------|------|----------------|
| `policy/no_privileged.rego` | DENY | Reject services with `privileged: true` |
| `policy/require_resource_limits.rego` | DENY | Reject services without a memory limit (v2 `mem_limit` or v3 `deploy.resources.limits.memory`) |
| `policy/no_latest_tags.rego` | DENY | Reject `image: foo:latest` and untagged images |
| `policy/approved_registries.rego` | DENY | Reject images outside the allow list |
| `policy/no_host_network.rego` | DENY | Reject `network_mode: host` except for the documented Cloudflare Tunnel exception |
| `policy/require_healthcheck.rego` | WARN | Require a healthcheck or document the base-image fallback |
| `policy/require_readonly_rootfs.rego` | WARN | Require `read_only: true` or document the stateful-service exception |

## Local check

```
brew install conftest
conftest test COREDIRECTIVE_ENGINE/docker-compose.yaml --policy infra/conftest/policy/
```

Exit code 0 means clean. Non-zero means at least one policy denied or warned.

## CI gate

The `.github/workflows/compose-admission.yml` workflow runs Conftest on
every PR that touches `COREDIRECTIVE_ENGINE/docker-compose.yaml` or any
file under `infra/conftest/`. Failed denials block merge.

## Adding a policy

1. Drop a new `.rego` file in `policy/`. Use `package main` and `import rego.v1`.
2. Use `deny contains msg if { ... }` for blocking violations.
3. Use `warn contains msg if { ... }` for advisory violations.
4. Add a row to the table above.
5. Update the GRC doc at `docs/grc/compose-admission-policy.md`.

## Rationale

Docker has no native admission controller equivalent to Kubernetes
admission webhooks. Conftest fills that gap by running the same
OPA Rego logic against the compose YAML before deploy.

This approach has three advantages over standing up a Kubernetes cluster
just to use Gatekeeper:

1. **Same Rego, same OPA**, different target. No new policy language to learn.
2. **Shifts left**. Violations caught at PR review, not at admission time.
3. **No additional runtime cost**. No control plane to operate.
