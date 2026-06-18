# 03_TECHNICAL_PREP — Cloudflare Heat Map + Study Plan + Likely Q&A

## Heat map (verified against Emmanuel's actual repo)

| Product | Color | Reason |
|---|---|---|
| DNS records (proxied A/CNAME/TXT, tunnel CNAMEs to `cfargotunnel.com`) | GREEN | Five records in `dns.tf`, real production posture |
| DNSSEC | RED | Not configured. He has not signed a zone |
| WAF Managed Rulesets | YELLOW | Knows OWASP CRS exists, documented why it is not active on Free plan. Has not deployed |
| WAF Custom Rules (expression engine) | GREEN | Wrote 5 custom rules: scanner UA block, geo-fence, honeytoken paths, header anomaly challenge |
| Rate Limiting v2 | GREEN | Live ruleset on `/webhook/*`, 10 req/10s per IP+colo, mitigation timeout |
| DDoS Protection (HTTP) | YELLOW | On by default and benefits from it. Has not tuned sensitivity |
| DDoS Protection (network, Magic Transit) | RED | No L3 packet experience |
| Bot Management (paid SKU) | RED | Bot Fight Mode toggled, scanner UA blocklist. No JA3, no ML scoring |
| Zero Trust Access | GREEN | Four self-hosted apps with email policies, service token, SSH app |
| Zero Trust Gateway (DNS, HTTP filtering) | RED | No Gateway policies, no DNS filtering |
| Zero Trust Tunnel (cloudflared) | GREEN | Full ingress config in `tunnel.tf`, four hostnames, decision log on rollback |
| WARP client | RED | No device enrollment, no posture rules |
| Page Rules + Configuration Rules | YELLOW | Zone settings override (security level, browser check, HSTS), no Page Rules |
| Workers, Workers KV, R2 | RED | Zero Workers code in repo |
| Spectrum (TCP/UDP) | RED | Never used. SSH goes through Tunnel, not Spectrum |
| Magic Transit / Firewall / WAN | RED | Enterprise-only, no exposure |
| Argo Smart Routing | RED | Not enabled |
| Load Balancing + health checks | RED | One origin, no LB pools |
| API Shield | RED | No mTLS schemas, no OpenAPI uploads |
| Cloudflare One (SASE) | YELLOW | Owns Access + Tunnel. Has not used Gateway, WARP, CASB, DLP, RBI |
| mTLS Origin | RED | Origin connects over plain HTTP localhost from tunnel |
| Origin Certificates | YELLOW | Edge TLS via CF, tunnel handles transport |
| Cloudflare Access for SaaS | RED | Self-hosted apps only |
| Logs (Logpush, Logpull) | RED | No Logpush job. Pulls Datadog logs from host instead |
| API + Terraform provider | GREEN | `cloudflare/cloudflare ~> 4.52`, knows v4 vs v5 resource names, did import flow |

## Three products to whiteboard cold

These are where Emmanuel is strongest and a hiring manager will pull on:

1. **Zero Trust Tunnel + Access end to end.** Tunnel ingress rules, public hostname to origin mapping, `cfargotunnel.com` CNAME pattern, Access self-hosted apps, service tokens for machine-to-machine, why he reverted tunnel-level `access.required` until per-app `aud_tag` capture works.
2. **WAF Custom Rules expression engine.** Walk the 5 rules, what each catches, why honeytoken + geo-fence + scanner UA stack as defense in depth, Free plan limit of 5 rules and how to prioritize.
3. **Terraform provider for Cloudflare.** v4 vs v5 resource naming (`cloudflare_tunnel_config` vs `cloudflare_zero_trust_tunnel_cloudflared_config`), import flow without nuking tunnel secret, drift management when someone edits the dashboard, `cloudflare_ruleset` vs legacy firewall rules.

## Three products NOT to volunteer

- Workers, KV, R2, Durable Objects (zero production code)
- Magic Transit / Magic WAN / Magic Firewall (no L3 packet path experience)
- Bot Management paid SKU and API Shield (Bot Fight Mode is not Bot Management)

## Likely peer interview questions (easy → hard)

1. Walk me through what happens when a request hits your Cloudflare zone. Order of operations from edge to origin.
2. Difference between a Page Rule, a Configuration Rule, and a Transform Rule. When do you reach for each?
3. WAF managed ruleset firing false positives on your login endpoint. How do you tune without disabling the whole rule?
4. How does Cloudflare Tunnel actually establish the connection back to edge? What protocol, what ports outbound from origin?
5. Difference between Access and WARP. When does a user need both?
6. Allow only requests with a valid client cert to hit `/api/admin`. How do you build that in Cloudflare?
7. Customer says Cloudflare is caching their authenticated user data and serving it to other users. Where do you start?
8. Difference between Rate Limiting Rules and Advanced Rate Limiting. What can you key off in advanced?
9. Layer 7 DDoS hits a single endpoint. Auto-mitigation isn't catching it. Playbook in next 5 minutes?
10. Design Cloudflare architecture for a SaaS app with three tiers (public marketing, authenticated app, admin) where admin requires hardware key + IP allowlist, app needs bot mgmt + rate limit, marketing needs aggressive caching.

Pass: 1-5. Stretch: 6-8. Study before whiteboard: 9-10.

## Request-flow memorization

```
Request → DDoS L3/L4 mitigation
       → DDoS L7 mitigation
       → WAF Managed Rules (Cloudflare Managed Ruleset, OWASP Core Ruleset, Exposed Credentials Check)
       → Custom WAF Rules
       → Rate Limiting Rules
       → Bot Management
       → Workers (request handlers)
       → Page/Configuration/Transform Rules (cache, headers)
       → Cache lookup
       → Origin (via Tunnel or proxied DNS)
       → Origin response
       → Workers (response handlers)
       → Cache write
       → Edge response to client
```

## 4-hour study plan before recruiter call

Ranked by ROI for a recruiter screen:

1. **45 min — Cloudflare One product map.** Names + one-line purpose: Access, Gateway, Tunnel, WARP, CASB, DLP, RBI, Magic
2. **45 min — Where Brilliant likely uses Cloudflare.** `dig` and `curl -I` against `brilliant.org` and likely Atlanta end clients (Equifax, Cox Auto, NCR Voyix, Mailchimp). Look for `server: cloudflare`, `cf-ray`, `cf-cache-status`. Gives you a one-sentence opener
3. **45 min — Terraform provider talking points.** v4 vs v5, drift, import flow, ruleset phases (`http_request_firewall_custom`, `http_ratelimit`)
4. **45 min — Zero Trust elevator pitches.** Two minutes each: Tunnel, Access, Gateway, WARP. Define cleanly even for the two not deployed
5. **30 min — Honest gap statement rehearsal.** Say the answers from `02_ROLE_FIT.md` out loud 5 times until natural

## 2-week hiring manager study plan (5 days/week, 2 hours/day)

**Week 1 — Build proof, close obvious reds:**
- D1: Ship one Worker. Hello world + fetch handler that proxies and adds a header. Bind to a route on `tigouetheory.com`. Workers moves yellow.
- D2: Add Workers KV. Counter that increments on each request. Reason about consistency model out loud.
- D3: Logpush job from Cloudflare to Datadog or R2. Wire it, verify events arriving.
- D4: Configure DNSSEC on `tigouetheory.com`, document DS record handoff.
- D5: Read Bot Management docs end to end. One-page note on JA3, JA4, ML bot score, super bot fight mode.

**Week 2 — Edge depth + interview drills:**
- D6: API Shield. Upload OpenAPI schema for the squire FastAPI surface, schema validation in report mode.
- D7: Origin Certificate on a non-tunnel subdomain. End-to-end TLS with Authenticated Origin Pulls. mTLS Origin moves yellow.
- D8: Load Balancer with two pools and a health monitor (second origin can be a stub).
- D9: Whiteboard drills. Three scenarios out loud: protect internal admin app, protect public API, block credential stuffing.
- D10: Mock interview. Have someone ask "Walk me through your Cloudflare environment." 10 minutes, no notes.

After two weeks the heat map flips: Workers, Logpush, DNSSEC, API Shield, mTLS Origin, Load Balancing all out of red.

## Real Cloudflare repo paths (for whiteboard reference)

- `/Users/et/cyber-squire-ops/terraform/cd-do-infrastructure/tunnel.tf`
- `/Users/et/cyber-squire-ops/terraform/cd-do-infrastructure/waf.tf`
- `/Users/et/cyber-squire-ops/terraform/cd-do-infrastructure/access.tf`
- `/Users/et/cyber-squire-ops/terraform/cd-do-infrastructure/dns.tf`
- Resource counts: 20 cloudflare, 14 datadog, 5 digitalocean, 2 local
- Account ID: e4871d2a375f9719092b286866ce26f2 (do not share publicly)
- Tunnel ID: 4bcf8238-8a8d-423d-b333-e8fe033d4de9 (do not share publicly)
- Zone ID: 44f6a683c92275d8fea6f6702589c608 (do not share publicly)
