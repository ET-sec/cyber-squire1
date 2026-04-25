# NemoClaw Migration Plan

> Status: READY TO EXECUTE
> Last Updated: 2026-03-18
> Estimated Cutover Time: ~15 minutes (images cached from first build)
> Rollback Time: ~30 seconds

## What This Does

Replaces the standalone `openclaw-gateway` Docker container with a NemoClaw-sandboxed OpenClaw instance. Same model (Claude Opus 4.7), same functionality, but wrapped in NVIDIA OpenShell with network policies, filesystem isolation, and process sandboxing.

---

## Pre-Cutover Checklist

- [ ] All 13 Compose services healthy (`docker ps`)
- [ ] OpenClaw gateway responding (`docker logs openclaw-gateway --tail 3`)
- [ ] Telegram bot @CDirective_bot operational (send test message)
- [ ] Verify no active OpenClaw sessions (`docker exec openclaw-gateway openclaw sessions list`)
- [ ] Confirm NemoClaw CLI installed (`/root/.nvm/versions/node/v22.22.1/bin/nemoclaw --help`)
- [ ] Confirm OpenShell CLI installed (`/usr/local/bin/openshell --version`)
- [ ] Confirm swap exists (`swapon --show` should show 4GB at /swapfile)
- [ ] Back up current config: `cp /root/moltbot/config-dir/openclaw.json /root/moltbot/config-dir/openclaw.json.pre-nemoclaw`

---

## Current OpenClaw Container Spec

```
Image:          openclaw:v2026.3.8
Command:        node openclaw.mjs gateway --allow-unconfigured
Restart:        unless-stopped
Network:        bridge (Docker)
Ports:          127.0.0.1:18789-18790 -> 18789-18790/tcp
Volumes:
  /root/moltbot/workspace    -> /home/node/clawd      (workspace)
  /root/moltbot/config-dir   -> /home/node/.openclaw   (config + identity + memory)
Env:            NODE_ENV=production
```

### Config (/root/moltbot/config-dir/openclaw.json)
```json
{
  "gateway": {
    "mode": "local",
    "auth": {
      "token": "SRky5hJjZk5g4GQJDtFSKQ__fn9bdKH-33EF4OSCrxU"
    },
    "controlUi": {
      "dangerouslyAllowHostHeaderOriginFallback": true
    }
  }
}
```

### Skills (4 ready)
- healthcheck (bundled)
- node-connect (bundled)
- skill-creator (bundled)
- weather (bundled)

### Workspace Files (at /root/moltbot/workspace/)
- SOUL.md (agent personality)
- IDENTITY.md (unfilled template)
- BOOTSTRAP.md (first-run guide)
- USER.md (unfilled template)
- HEARTBEAT.md (empty, no tasks)
- TOOLS.md (template)
- AGENTS.md (full agent behavior spec)

### Memory
- /root/moltbot/config-dir/memory/main.sqlite (agent memory DB)

### Identity
- /root/moltbot/config-dir/identity/device.json (device keypair)

### Cron
- /root/moltbot/config-dir/cron/jobs.json (empty, no jobs)

---

## Port Conflicts to Resolve

| Port  | Current Owner | NemoClaw Needs | Resolution |
|-------|--------------|----------------|------------|
| 8080  | Keycloak     | OpenShell gateway | Remap Keycloak to 8180 |
| 18789 | openclaw-gateway | NemoClaw dashboard | Stop openclaw-gateway first |

---

## n8n Workflow Impact

Only 2 workflows reference OpenClaw/Claude, neither calls the chat completions endpoint directly:
- **Gmail Label & Filter Creator** - references Claude model name, no HTTP calls
- **CoreDirective API Health Check** - tests Ollama, not OpenClaw

**No n8n endpoint changes needed.**

---

## Cutover Sequence

### Phase 1: Free RAM (~1 min)

```bash
# Source nvm
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

# Stop non-essential services to free ~700MB for image export
cd /root/COREDIRECTIVE_ENGINE
docker compose stop \
  cd-service-teleport \
  cd-service-teleport-event-handler \
  cd-service-vault \
  cd-service-keycloak \
  cd-service-falco \
  cd-service-falcosidekick \
  cd-service-fluentd \
  cd-service-datadog \
  cd-service-ollama \
  cd-service-whisper
```

### Phase 2: Remap Keycloak + Stop Old Gateway (~30 sec)

```bash
# Move Keycloak from 8080 to 8180
sed -i "s/127.0.0.1:8080:8080/127.0.0.1:8180:8080/" /root/COREDIRECTIVE_ENGINE/docker-compose.yaml

# Stop old OpenClaw gateway
docker stop openclaw-gateway
```

### Phase 3: Start NemoClaw (~10 min first time, ~3 min with cached images)

```bash
# Stop any leftover OpenShell gateway
openshell gateway stop 2>/dev/null || true

# Run onboard
nemoclaw onboard --non-interactive
```

This will:
1. Start OpenShell gateway on port 8080
2. Build sandbox image (cached from previous build)
3. Create sandbox "my-assistant" with OpenClaw inside
4. Forward port 18789

**If it asks for NVIDIA_API_KEY, that's expected. It will fail at step 4/7 (NIM config) but the sandbox is already created. Continue to Phase 4.**

### Phase 4: Configure Claude Inference (~1 min)

```bash
# Get Anthropic API key from Doppler (run from Mac, or use key directly)
# Replace YOUR_ANTHROPIC_KEY below

cat > /tmp/openclaw-claude.json << 'EOF'
{
  "gateway": {
    "mode": "local",
    "auth": {
      "token": "SRky5hJjZk5g4GQJDtFSKQ__fn9bdKH-33EF4OSCrxU"
    },
    "controlUi": {
      "dangerouslyAllowHostHeaderOriginFallback": true
    }
  },
  "agents": {"defaults": {"model": {"primary": "anthropic/claude-opus-4-7"}}},
  "models": {"mode": "merge", "providers": {
    "anthropic": {
      "baseUrl": "https://api.anthropic.com",
      "apiKey": "YOUR_ANTHROPIC_KEY",
      "api": "anthropic-messages",
      "models": [{
        "id": "claude-opus-4-7",
        "name": "Claude Opus 4.7",
        "reasoning": false,
        "input": ["text"],
        "contextWindow": 1000000,
        "maxTokens": 32768
      }]
    }
  }}
}
EOF

# Upload to sandbox
openshell sandbox upload my-assistant /tmp/openclaw-claude.json /sandbox/.openclaw/

# SSH in and replace config
ssh -o ProxyCommand="/usr/local/bin/openshell ssh-proxy --gateway-name nemoclaw --name my-assistant" \
    -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    sandbox@openshell-my-assistant \
    "cp /sandbox/.openclaw/openclaw-claude.json /sandbox/.openclaw/openclaw.json && openclaw doctor --fix"

# Clean up key from disk
rm /tmp/openclaw-claude.json
```

### Phase 5: Upload Workspace Files (~1 min)

```bash
# Upload all workspace files from old OpenClaw
for file in SOUL.md IDENTITY.md USER.md HEARTBEAT.md TOOLS.md AGENTS.md; do
  openshell sandbox upload my-assistant /root/moltbot/workspace/$file /sandbox/.openclaw/workspace/ 2>/dev/null
done

# Upload memory DB
openshell sandbox upload my-assistant /root/moltbot/config-dir/memory/main.sqlite /sandbox/.openclaw/memory/ 2>/dev/null

# Upload device identity (so sessions persist)
openshell sandbox upload my-assistant /root/moltbot/config-dir/identity/device.json /sandbox/.openclaw/identity/ 2>/dev/null

# Upload cron config
openshell sandbox upload my-assistant /root/moltbot/config-dir/cron/jobs.json /sandbox/.openclaw/cron/ 2>/dev/null
```

### Phase 6: Update Network Policy (~30 sec)

```bash
cat > /tmp/nemoclaw-policy.yaml << 'POLICYEOF'
version: 1

filesystem_policy:
  include_workdir: true
  read_only:
    - /usr
    - /lib
    - /proc
    - /dev/urandom
    - /app
    - /etc
    - /var/log
  read_write:
    - /sandbox
    - /tmp
    - /dev/null

landlock:
  compatibility: best_effort

process:
  run_as_user: sandbox
  run_as_group: sandbox

network_policies:
  anthropic:
    name: anthropic
    endpoints:
      - host: api.anthropic.com
        port: 443
        protocol: rest
        enforcement: enforce
        tls: terminate
        rules:
          - allow: { method: "*", path: "/**" }
      - host: statsig.anthropic.com
        port: 443
        rules:
          - allow: { method: "*", path: "/**" }
      - host: sentry.io
        port: 443
        rules:
          - allow: { method: "*", path: "/**" }
    binaries:
      - { path: /usr/local/bin/claude }
      - { path: /usr/local/bin/openclaw }
      - { path: /usr/local/bin/node }

  github:
    name: github
    endpoints:
      - host: github.com
        port: 443
        access: full
      - host: api.github.com
        port: 443
        access: full
    binaries:
      - { path: /usr/bin/gh }
      - { path: /usr/bin/git }

  clawhub:
    name: clawhub
    endpoints:
      - host: clawhub.com
        port: 443
        protocol: rest
        enforcement: enforce
        tls: terminate
        rules:
          - allow: { method: GET, path: "/**" }
          - allow: { method: POST, path: "/**" }
    binaries:
      - { path: /usr/local/bin/openclaw }

  openclaw_api:
    name: openclaw_api
    endpoints:
      - host: openclaw.ai
        port: 443
        protocol: rest
        enforcement: enforce
        tls: terminate
        rules:
          - allow: { method: GET, path: "/**" }
          - allow: { method: POST, path: "/**" }
    binaries:
      - { path: /usr/local/bin/openclaw }

  openclaw_docs:
    name: openclaw_docs
    endpoints:
      - host: docs.openclaw.ai
        port: 443
        protocol: rest
        enforcement: enforce
        tls: terminate
        rules:
          - allow: { method: GET, path: "/**" }
    binaries:
      - { path: /usr/local/bin/openclaw }

  npm_registry:
    name: npm_registry
    endpoints:
      - host: registry.npmjs.org
        port: 443
        access: full
    binaries:
      - { path: /usr/local/bin/openclaw }
      - { path: /usr/local/bin/npm }

  telegram:
    name: telegram
    endpoints:
      - host: api.telegram.org
        port: 443
        protocol: rest
        enforcement: enforce
        tls: terminate
        rules:
          - allow: { method: GET, path: "/bot*/**" }
          - allow: { method: POST, path: "/bot*/**" }
POLICYEOF

openshell policy set --policy /tmp/nemoclaw-policy.yaml my-assistant
rm /tmp/nemoclaw-policy.yaml
```

### Phase 7: Verify Inference (~30 sec)

```bash
ssh -o ProxyCommand="/usr/local/bin/openshell ssh-proxy --gateway-name nemoclaw --name my-assistant" \
    -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    sandbox@openshell-my-assistant \
    "openclaw agent --agent main --local -m 'respond with only: NemoClaw active' --session-id verify-cutover 2>&1 | tail -3"
```

Expected output: `NemoClaw active`

### Phase 8: Restart All Services (~1 min)

```bash
cd /root/COREDIRECTIVE_ENGINE
docker compose start \
  cd-service-teleport \
  cd-service-teleport-event-handler \
  cd-service-vault \
  cd-service-keycloak \
  cd-service-falco \
  cd-service-falcosidekick \
  cd-service-fluentd \
  cd-service-datadog \
  cd-service-ollama \
  cd-service-whisper
```

### Phase 9: Verify Everything (~2 min)

```bash
# All containers up
docker ps --format "table {{.Names}}\t{{.Status}}" | sort

# NemoClaw sandbox healthy
nemoclaw my-assistant status

# Tunnel alive
curl -s -o /dev/null -w "%{http_code}" https://n8n.tigouetheory.com

# n8n healthy
docker logs cd-service-n8n --tail 3

# Keycloak on new port
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8180
```

---

## Post-Cutover: Mac CLI Re-Pairing

On your Mac after cutover:
```bash
# Update local OpenClaw
sudo npm i -g openclaw@latest

# Reconnect to NemoClaw gateway
# (exact command TBD -- depends on how NemoClaw exposes gateway for remote nodes)
# May need to set up a Cloudflare tunnel route for the OpenShell gateway
```

**NOTE:** Mac CLI pairing through NemoClaw is untested. The sandbox's k3s networking may not expose the pairing endpoint the same way Docker bridge does. This needs investigation before cutover.

---

## Rollback Procedure (~30 seconds)

If anything fails at any phase:

```bash
# Stop NemoClaw
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
openshell forward stop 18789 my-assistant 2>/dev/null
openshell gateway stop 2>/dev/null

# Restore Keycloak port
cd /root/COREDIRECTIVE_ENGINE
sed -i "s/127.0.0.1:8180:8080/127.0.0.1:8080:8080/" docker-compose.yaml
docker compose up -d cd-service-keycloak

# Start old gateway
docker start openclaw-gateway

# Restart any stopped services
docker compose start \
  cd-service-teleport cd-service-teleport-event-handler \
  cd-service-vault cd-service-falco cd-service-falcosidekick \
  cd-service-fluentd cd-service-datadog cd-service-ollama cd-service-whisper
```

---

## Known Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| OOM during sandbox creation | Build fails (exit 137) | Stop 10 services first, 4GB swap already in place |
| Port 8080 conflict | OpenShell can't start | Keycloak remapped to 8180 in Phase 2 |
| Wrong API type | Claude inference fails | Config uses `anthropic-messages` (not `anthropic`) |
| Binary whitelist blocks inference | 403 from OpenShell proxy | Policy adds openclaw + node to anthropic endpoint |
| Upload goes to wrong path | Config not found | Upload to directory, then `cp` inside sandbox |
| Mac CLI can't pair | No remote access from Mac | Investigate before cutover, keep old container as fallback |
| Sandbox OOM at runtime | Agent crashes under load | 4GB swap + services running = ~5GB available, should be fine |
| NemoClaw alpha breaking change | Sandbox stops working | Pin NemoClaw version, don't update without testing |
| Telegram bot not starting | @CDirective_bot offline | Bot runs inside OpenClaw; verify it starts in sandbox |

---

## Open Questions (resolve before cutover)

1. **Mac CLI pairing** -- How does the Mac `openclaw` CLI pair with NemoClaw's sandboxed gateway? The k3s networking may not expose the WS endpoint the same way.
2. **Telegram bot in sandbox** -- Does the OpenClaw Telegram integration start automatically inside the sandbox, or does it need explicit config?
3. **Chat completions endpoint** -- If n8n or other services need `http://172.17.0.1:18789/v1/chat/completions` in the future, will the NemoClaw port forward respond on that Docker bridge IP?
4. **Gateway token persistence** -- Does the sandbox's OpenClaw respect the gateway auth token for API access?
5. **Memory DB migration** -- Will the sqlite memory DB from the old container work inside the sandbox's OpenClaw version?

---

## File Inventory (what gets migrated)

| Source (old container) | Destination (sandbox) | Type |
|----------------------|----------------------|------|
| /root/moltbot/config-dir/openclaw.json | /sandbox/.openclaw/openclaw.json | Config (rewritten with Claude provider) |
| /root/moltbot/workspace/SOUL.md | /sandbox/.openclaw/workspace/SOUL.md | Agent personality |
| /root/moltbot/workspace/IDENTITY.md | /sandbox/.openclaw/workspace/IDENTITY.md | Agent identity |
| /root/moltbot/workspace/USER.md | /sandbox/.openclaw/workspace/USER.md | User profile |
| /root/moltbot/workspace/HEARTBEAT.md | /sandbox/.openclaw/workspace/HEARTBEAT.md | Heartbeat tasks |
| /root/moltbot/workspace/TOOLS.md | /sandbox/.openclaw/workspace/TOOLS.md | Tool notes |
| /root/moltbot/workspace/AGENTS.md | /sandbox/.openclaw/workspace/AGENTS.md | Agent behavior |
| /root/moltbot/workspace/BOOTSTRAP.md | /sandbox/.openclaw/workspace/BOOTSTRAP.md | First-run guide |
| /root/moltbot/config-dir/memory/main.sqlite | /sandbox/.openclaw/memory/main.sqlite | Agent memory |
| /root/moltbot/config-dir/identity/device.json | /sandbox/.openclaw/identity/device.json | Device keypair |
| /root/moltbot/config-dir/cron/jobs.json | /sandbox/.openclaw/cron/jobs.json | Cron jobs (empty) |
| (generated) | /tmp/nemoclaw-policy.yaml | Network policy |
