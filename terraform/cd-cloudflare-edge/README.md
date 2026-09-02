# cd-cloudflare-edge

The edge plane of the three-plane design (Cloudflare edge, Oracle Cloud
workloads, AWS security plane), as code. Access gates every admin surface,
the custom WAF and rate limit sit in front of it, and the tunnel is the only
path to the origin. Nothing here is created from scratch: every resource
was already live and is **adopted by import**, so the login wall in front
of the automation host is never recreated underneath the operator.

## Status

| Layer | State | Notes |
|---|---|---|
| Custom WAF ruleset (4 rules) | adopted 2026-09-02 | Telegram egress carve-out added to the geo-fence and header rules |
| Rate limit ruleset (/webhook/*) | adopted 2026-09-02 | unchanged |
| Access: n8n host app, admin policy, service-token policy, shared token | adopted 2026-09-02 | unchanged |
| Access: Telegram webhook bypass (path + IP scoped) | created 2026-09-02 | the one new resource |
| Access: langfuse, squire, ssh apps | pending import | dormant until the ARM rebuild brings those services back |
| Per-agent service tokens | pending | design in the archived `cloudflare-adopt` notes |
| DNS records, tunnel ingress config | pending import | tunnel ingress edits through the dashboard cause drift once imported; import when ready to commit to code-only changes |
| Zone security settings | pending | import shows a wide diff on defaults; reconcile separately |

## Why the Telegram carve-out exists

On 2026-09-01 the bot's registered webhook was returning **403** to
Telegram: the WAF geo-fence blocks non-US sources on admin hosts, and
Telegram's webhook egress is not in the US. Even past the WAF, every path
on the host is behind Access, which Telegram cannot authenticate to. The
bot could not receive a single update from its own edge.

The fix keeps the edge closed by default and opens exactly one thing: the
Telegram Trigger path, for Telegram's published ranges only
(`149.154.160.0/20`, `91.108.4.0/22`). The webhook path prefix is treated
as a secret and lives in the gitignored tfvars. The remaining trust for
that path is enforced in n8n (Restrict to Chat IDs on the trigger node)
and by the per-IP rate limit.

## Adoption procedure

Auth comes from `CLOUDFLARE_API_KEY` and `CLOUDFLARE_EMAIL` in the
environment. Load them from Doppler first (`source scripts/session-secrets.sh`),
then run the commands below in that shell. State goes to the same OCI bucket as the
compute plane under its own key; the partial config is in the gitignored
`backend.hcl`.

```bash
cd terraform/cd-cloudflare-edge
cp terraform.tfvars.example terraform.tfvars   # fill in
terraform init -backend-config=backend.hcl

# Read live IDs (rulesets, Access apps, policies, service tokens) from the
# API, then import each resource BEFORE any apply. v4 provider ID formats:
#   cloudflare_ruleset                 zone/<zone_id>/<ruleset_id>
#   cloudflare_access_application      <account_id>/<app_id>
#   cloudflare_access_policy           account/<account_id>/<app_id>/<policy_id>
#   cloudflare_access_service_token    <account_id>/<token_id>
terraform import cloudflare_ruleset.custom_waf zone/<zone_id>/<ruleset_id>
# ... repeat for each adopted resource ...

terraform plan
# The plan MUST show zero destroys. Expected changes on first adoption:
# in-place expression updates on two WAF rules, plus the new Telegram
# bypass application and policy. Anything wanting to replace an Access
# application means an import was wrong. Stop and fix before applying.
terraform apply
```

## Verification receipts

Recorded in the decision record
[DR-06](../../docs/architecture/decisions/DR-06-webhook-trust-at-the-edge.md).

## Free plan limits that shape this code

5 custom WAF rules, 1 rate limit rule (10 requests per 10 seconds, 10
second mitigation), no managed OWASP core ruleset as a resource, no request
body inspection. Every rule here fits inside that envelope on purpose.
