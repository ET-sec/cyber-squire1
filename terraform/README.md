# terraform

Every generation of this platform's infrastructure as code, live and retired.
Three planes are active and three are archived, and each archived directory
carries an `ARCHIVED.md` saying when it froze and what would revive it.

<!-- MANIFEST:terraform -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `terraform/README.md` | active | The directory README for terraform/, whose contents block is generated from this manifest. |
| `terraform/cd-aws-automation/**` | archived | The production automation network that was built on the first cloud: VPC, subnets, NAT, security groups, and the instance. |
| `terraform/cd-aws-security-plane/**` | active | The designed second cloud plane: OIDC federation, an immutable evidence vault, region guard, and a break glass path. |
| `terraform/cd-cloudflare-edge/**` | active | The edge plane: zero trust access on the automation hostname, the firewall rules, and the carve out that lets the bot webhook through. |
| `terraform/cd-do-infrastructure/**` | archived | The previous provider's full stack: droplet, network, firewall, tunnel routes, monitoring, dashboards, and the templates it rendered. |
| `terraform/cd-do-infrastructure/policy/**` | archived | Ten OPA policies written against the previous provider's plan, with their fixtures. |
| `terraform/cd-oci-infrastructure/**` | active | The live infrastructure: compute, networking, data protection, outputs, the remote state backend example, and the cloud init that builds the host. |
| `terraform/cd-oci-infrastructure/policy/**` | active | Ten OPA policies over the infrastructure plan, with the fixtures that prove each one both passes and fails. |
| `terraform/simple-ec2/**` | archived | The first single instance configuration, before the automation network replaced it. |
<!-- /MANIFEST -->

`terraform/cd-oci-infrastructure/` is what runs, with remote state in a
versioned and locked bucket under a customer managed key.
`terraform/cd-cloudflare-edge/` is the only tier enforced before a request
reaches the host. `terraform/cd-aws-security-plane/` is written, reviewed, and
held at plan. The retired directories are kept because an earlier cloud setup
was lost with no record, and that is not happening twice. Each plane keeps its
OPA policies beside the plan they judge, in its own `policy/` directory.
