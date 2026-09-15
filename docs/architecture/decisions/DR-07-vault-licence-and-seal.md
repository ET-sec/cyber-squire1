# DR-07: Vault under BUSL, the KMS seal, and the identity tier's exposure

**Date:** 2026-09-15
**Status:** Applied 2026-09-15 on the Arm host (receipts below). Two engines enabled; the first consumer of the database role is the orchestration engine, wired in a later change.

## Problem

The secrets manager in the design had three things wrong with it that a reviewer would find in the first minute:

1. Its AppRole story was a comment in the compose file. No engine was enabled, no consumer existed, and the version pinned was past its end of life.
2. It loaded two configuration sources that disagreed: an environment variable the entrypoint wrote to a JSON file, and an HCL file on the volume. Which one won depended on load order.
3. `tls_disable` was inherited from a template with a one-word comment and no decision behind it.

A fourth question sat behind all three: HashiCorp moved Vault to the Business Source License at 1.15, and the platform pins a version on the far side of that line.

## Options weighed

| Option | Effect | Verdict |
|---|---|---|
| A. Stay on Vault, current line, under BUSL 1.1 | The licence forbids offering Vault as a competing hosted service; it does not restrict running it inside a platform you operate. Nothing about this platform's use is a competing offering | **Chosen** |
| B. Switch to OpenBao | The MPL fork of Vault 1.14. It mirrors the seal types this design needs, including the cloud KMS seal used here, so it is a real alternative rather than a talking point | Recorded, not taken: the fork tracks a 2023 base and the platform gains nothing today from moving |
| C. Shamir seal with the shares in the secrets manager of record | Works everywhere, but every restart needs an operator or an automation holding three shares, and that automation would be the very stored credential the design avoids | Fallback only, not taken |
| D. Cloud KMS seal through the instance identity | The instance is the identity; the seal key is wrapped by a key the host never holds. A restart unseals with no human and no stored share | **Chosen** |

## Decision

1. **Vault stays, on the current line, under BUSL 1.1.** OpenBao is named here as the alternative with the same seal so a later reviewer does not have to rediscover it.
2. **The seal is the cloud KMS through the instance principal, with its own key.** The storage key that encrypts state and backups is never reused for a second purpose. The seal key is a separate AES key in the same vault, and the instance's dynamic group is granted `use keys` scoped to that key's id and nothing wider. No unseal material exists on the host; the recovery shares and the initial root token went to the secrets manager of record on initialization and to no file.
3. **One configuration source.** The environment variable is gone from the compose block; the HCL file on the volume is the whole configuration. The seal key id and the two KMS endpoints are identifiers the repository does not carry, so the seal reads them from the environment the compose block loads.
4. **`tls_disable` is true, and this is the reason.** The listener is reachable only on the compose network and on a loopback publish; TLS terminates at the edge; nothing on that path leaves the host. A certificate inside the container would have to be issued, distributed to every client on that network and rotated, for a hop that never crosses a network boundary. If the listener is ever published beyond the host, this line is the one to revisit.
5. **Two roles, nothing else.** The database secrets engine issues short-lived Postgres credentials through one role, `cd-app-readwrite`, with a one hour lease and a two hour maximum. The transit engine holds one key for wrapping the orchestration engine's encryption key. No other engine and no auth method beyond the token backend is enabled.
6. **The healthcheck reads the health endpoint over HTTP** and is healthy only when the server is initialized, unsealed and active, so a sealed server reads unhealthy and says so instead of being masked by a command whose exit codes were written for a different question.

## The identity tier's exposure, decided here

The identity provider is the one service in this tier that gets a public hostname, because the edge login needs to redirect a browser to it. Three controls, each named:

- **The hostname routes the login flow's path families and nothing else:** the realm's discovery document, `/realms/<realm>/.well-known/*`, the OpenID Connect protocol endpoints, `/realms/<realm>/protocol/openid-connect/*`, the form actions the login page posts to, `/realms/<realm>/login-actions/*`, and the page's static assets under `/resources/*`. The first design named only the first two, and the login form's own POST answered not found; the third family fixed that, which is why the list is written out here. The administration console, the account consoles and every other realm match no route and answer not found at the edge. They are reachable only from inside the host, where an administrator already has a shell.
- **Production mode sits behind a terminating tunnel,** so `KC_PROXY_HEADERS=xforwarded` and `KC_HTTP_ENABLED=true` are set beside the strict hostname. The plain HTTP listener is bound to loopback on the host and is reachable only by the tunnel process on that same host.
- **The edge application keeps `auto_redirect_to_identity` off with two providers,** so the email one-time-code path stays on the login page beside the new provider. A fault in the identity provider cannot lock the operator out of the edge.

The access gateway keeps local authentication with a second factor. Its OIDC and SAML connectors are Enterprise features, and the community GitHub connector maps organization teams while the owner's account is personal, so federation at the gateway is a recorded upgrade rather than a configuration in this build. Its proxy is not routed through the edge here.

## Blast radius

If the KMS key is deleted or the policy is revoked, Vault cannot unseal on its next restart. The recovery shares do not unseal an auto-sealed Vault; they authorize operations such as generating a new root token. Recovery is a seal migration, which needs the old seal reachable, so the key's deletion is guarded by the vault's own deletion window and by the same 30-day thinking the backups carry. If the database role's Postgres user loses its rights, dynamic credentials stop issuing and every consumer falls back to its deploy-time credential, which still exists today.

## Verification receipts

| # | Test | Expected | Result |
|---|---|---|---|
| 1 | `vault status` after initialization | seal type is the cloud KMS, sealed false, recovery seal shamir | Seal Type ocikms, Recovery Seal Type shamir, Initialized true, Sealed false, five recovery shares with a threshold of three |
| 2 | Server log at first unseal | unsealed with a stored key, no operator action | "unsealed with stored key", "post-unseal setup complete" |
| 3 | Terraform plan after the seal key and its policy were applied | no changes | exit 0, no changes |
| 4 | One read of `database/creds/cd-app-readwrite` | a lease of one hour, a username and a password present | lease 3600, both present, the credential itself never printed |
| 5 | Transit encrypt then decrypt of a fixed string | the same string back | identical |
| 6 | `vault secrets list` and `vault auth list` | the two engines plus the built-in mounts; the token backend only | database and transit beside cubbyhole, identity, sys and the built-in agent registry; token only |
| 7 | The volume on the host | no unseal share, no token file | nothing matching key, token or unseal in the volume listing |

## The interview version

"The secrets manager in my reference design was a comment about AppRole and a version past end of life, so I made it real. It runs on the current line under the source-available licence, which is fine for a platform you operate yourself, and I wrote down that OpenBao is the fork with the same seal in case that ever changes. The seal is the cloud KMS through the instance's own identity with a dedicated key, so a restart unseals with nobody holding a share and nothing stored on the box. Two engines only: dynamic database credentials on a one hour lease, and transit for the orchestrator's encryption key. And I decided the plain listener on purpose, in writing, instead of inheriting it."

## Residuals

- The first consumer of the dynamic database role is the orchestration engine; its deploy-time credential stays until that change lands.
- Re-keying the orchestration engine's encryption key through transit is a separate change; this record proves the engine answers.
- The root token from initialization should be revoked once a named admin policy and token exist.
