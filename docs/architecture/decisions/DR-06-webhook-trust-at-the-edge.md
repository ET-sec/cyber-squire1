# DR-06: Webhook trust at the edge (Access, WAF, and the Telegram carve-out)

**Date:** 2026-09-02
**Status:** Edge change applied 2026-09-02 (receipts below). Workflow-side controls tracked in the residuals.

## Problem

Scoring the platform against the OWASP GenAI Security Crosswalk on 2026-09-01 surfaced one finding and one assumption:

1. The master orchestrator webhook has no application-layer authentication. Known since the May code review (CR-001-F4), accepted with compensating controls, and past its remediation date.
2. An assumption that webhook paths had to sit outside Cloudflare Access because Telegram's servers must be able to reach the bot's webhook without credentials.

Both were checked against the live edge on 2026-09-02 instead of against the documents:

- Every path on the automation host, webhooks included, answers an unauthenticated POST with a 302 to the Access login page. The orchestrator webhook is edge-authenticated. The accepted risk in CR-001-F4 was scoped correctly: application-layer only.
- Telegram's `getWebhookInfo` for the bot reported its last delivery attempt failed with **403 Forbidden**. The custom WAF geo-fences admin hostnames to the home country, and Telegram's webhook egress is not in it. Even past the WAF, Telegram would have met the Access wall, since it cannot present a service token. The bot could not receive a single update from its own edge.

So the real finding was not "the webhook is open." It was "the edge is closed so well that the one caller we need was locked out, and nobody noticed because the failure was silent."

## Options weighed

| Option | Effect | Verdict |
|---|---|---|
| A. Disable the geo-fence and add a host-wide Access bypass for `/webhook/*` | Fixes the bot, opens every webhook to the internet | Rejected |
| B. Move the bot to long polling from inside the host | Removes the inbound path entirely; needs a persistent poller (pending ARM rebuild) and gives up edge rate limiting and logging | Deferred, reasonable later |
| C. Path-scoped Access application on the Telegram Trigger path with a bypass policy limited to Telegram's published egress ranges, matching WAF carve-outs, chat-ID restriction on the trigger node, per-IP rate limit unchanged | Opens one path to two published ranges, nothing else changes | **Chosen** |
| D. Keep the orchestrator webhook edge-only | Status quo; a leaked service token or a compromised edge account reaches the raw-SQL action unopposed | Rejected in favour of app-layer header auth as a second layer |

## Decision

1. **The edge stays closed by default.** Access keeps gating every path on the automation host. Machine callers present a service token; humans get a one-time PIN.
2. **One carve-out, scoped twice.** A path-scoped Access application covers only the Telegram Trigger webhook prefix, and its bypass policy includes only Telegram's published ranges (`149.154.160.0/20`, `91.108.4.0/22`). The WAF geo-fence and header-anomaly rules exempt the same ranges. The webhook prefix is treated as a secret and lives in gitignored variables.
3. **The edge becomes code.** A new Terraform root, `terraform/cd-cloudflare-edge`, adopts the live rulesets and the n8n Access resources by import (never by create) and holds state under its own key in the same locked, versioned bucket as the compute plane. The remaining Cloudflare resources (other Access apps, DNS, tunnel ingress, per-agent tokens) are imported in follow-up passes.
4. **Second layer on the orchestrator.** The Squire caller now presents both the Access service-token headers and an application-layer token header. The matching Header Auth credential on the orchestrator's webhook node closes CR-001-F4 for real instead of by acceptance.

## Blast radius

What the carve-out exposes: one path, reachable from two published ranges, terminating in a workflow that only acts on an allowlisted chat ID, capped at 60 requests per minute per source by the rate limit. Spoofing a source inside Telegram's ranges is not practical over TCP. A compromise of Telegram itself is outside this system's threat model.

What the code adoption risks: an incorrect import that makes Terraform want to recreate an Access application would drop the login wall for the seconds between destroy and create. Mitigation: the adoption rule is import first, plan must show zero destroys, and the first apply is watched.

## Verification receipts

| # | Test | Expected | Result |
|---|---|---|---|
| 1 | `terraform plan` after import, before any change | zero destroys, only the intended in-place updates and the new bypass app | 2 to add, 3 to change, 0 to destroy. Post-apply plan: no changes |
| 2 | Unauthenticated POST to the orchestrator webhook path | 302 to Access login (unchanged) | 302 to Access login, after apply |
| 3 | Telegram `getWebhookInfo` after the operator sends the bot a message | the 403 clears; the next error, if any, comes from n8n itself | pending operator action (see the workflow store finding below: expect a 404 from n8n until the workflows are restored, which still proves the edge now lets Telegram through) |
| 4 | Read-back of the WAF geo-fence rule from the API | expression carries the `not (ip.src in {...})` carve-out | both the geo-fence and the header-anomaly rule carry it, read back after apply |
| 5 | Unauthenticated POST to the Telegram webhook path from a non-Telegram source | 302 to Access login (bypass is IP-scoped) | **403 from Access.** The path-scoped application carries only the IP-scoped bypass policy, so a source outside Telegram's ranges is denied outright instead of being offered a login. Stricter than designed. Kept |

## What the workflow store showed

With SSH restored, the workflow table on the OCI Postgres was read directly: **zero workflows, zero credentials, one user.** The n8n instance that has been running for 13 days is a fresh install. The orchestrator, the Telegram supervisor, and the twelve other workflows the project context still lists were never restored after the DigitalOcean loss. Telegram's registered webhook points at a trigger that does not exist on this host.

Consequences, recorded plainly:

- The 2026-09-01 "live finding" about the orchestrator's raw-SQL action described a workflow that is not deployed. It is a design finding against the exported definition, not a live exposure.
- The edge fix in this record is still correct and still needed. It is a precondition for the bot, not the whole repair.
- Eleven DO-era workflow exports exist in the repo's engine directory (health checks, error handler, finance and status tools, Gumroad, YouTube, Gmail labels, security pulse). Exports of the master orchestrator and the Telegram supervisor were not found on local disk; the agent cards under `.agents/` are the only surviving description of them.

## The interview version

"I scored my own stack against OWASP's GenAI crosswalk and found what looked like an unauthenticated orchestration webhook. Before writing it up I tested the live edge instead of trusting the docs. The edge was actually gating everything, including the webhook, which meant the accepted risk had been scoped right. The surprise was the opposite failure: my own WAF and Access policies had locked out Telegram, the one caller the bot needs, and the failure was silent. The fix was a path-scoped, IP-scoped carve-out for Telegram's published ranges, all of it adopted into Terraform by import so the edge is code from here on. The lesson I keep: verify the control from outside, because paper security and edge security drift in both directions."

## Correction on the record

The 2026-09-01 assessment stated the orchestrator endpoint had no authentication. That was accurate at the application layer and wrong at the edge. This record supersedes that statement.

## Residuals

- **Restore the SOAR layer on OCI.** Re-import the eleven surviving exports, rebuild the orchestrator and Telegram supervisor from their agent cards with the header-auth and chat-ID controls designed in, recreate credentials from Doppler. This is a rebuild, scheduled after the exam window.
- Header Auth credential on the orchestrator webhook node and Restrict to Chat IDs on the Telegram Trigger node (workflow-side; needs an n8n change window).
- Import the remaining Cloudflare resources into `cd-cloudflare-edge`.
- Per-agent service tokens replacing the shared automation token.
- A drift-check leg for the edge plane. Tradeoff to document when done: it needs a scoped read-only Cloudflare token stored in CI, which is the first stored cloud credential in the pipeline since the OIDC migration.
- Option B (long polling) as the eventual replacement for the inbound carve-out once the poller has a home.
