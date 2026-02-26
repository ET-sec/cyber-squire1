# Security Stack Build Plan — $200K Architecture

> **Goal:** Build and stream the CoreDirective security platform across 5 episodes.
> Each episode = 1 component. Off-stream groundwork done first. Zero credential exposure.

---

## PRE-STREAM GROUNDWORK (Do This Off-Stream, ~2-3 hrs total)

### Step 1 — Claim Education Credits (~30 min)
Do this first. Everything else depends on it.

- [ ] Go to https://education.github.com/pack → verify student pack active
- [ ] Claim **Datadog** → Pro tier free (search "Datadog" in pack list)
  - Save API key + App key → 1Password → Core Infra vault → tag `datadog`
- [ ] Claim **DigitalOcean** → $200 credit
  - Create DO account if needed → save login → 1Password → Core Infra vault
  - Generate DO Personal Access Token → save to 1Password → tag `digitalocean`
- [ ] Verify GitHub Education Pack also gives: Namecheap, Heroku (if needed later)

> If Education Pack expired: Datadog 14-day free trial still works. DO gives $200 on signup anyway.

---

### Step 2 — GitHub Repo Secrets (~15 min)
These get referenced in GitHub Actions YAML. Set them in the repo, never in code.

Go to: https://github.com/ET-sec/cyber-squire1 → Settings → Secrets and variables → Actions

Add these secrets:
- [ ] `DATADOG_API_KEY` — from 1Password after Step 1
- [ ] `DATADOG_APP_KEY` — from 1Password after Step 1
- [ ] `AWS_ACCESS_KEY_ID` — from 1Password → Core Infra → AWS
- [ ] `AWS_SECRET_ACCESS_KEY` — from 1Password → Core Infra → AWS
- [ ] `DO_TOKEN` — from 1Password after Step 1

> Never put these values in YAML files. YAML uses `${{ secrets.NAME }}` only.

---

### Step 3 — Pre-Pull Docker Images on EC2 (~20 min, runs in background)
Avoids waiting on stream. Run this now, let it download overnight.

```bash
ssh cyber-squire-tunnel '
  docker pull quay.io/keycloak/keycloak:23.0 &&
  docker pull hashicorp/vault:1.15 &&
  docker pull datadog/agent:latest &&
  echo "All images pulled"
'
```

---

### Step 4 — Vault Init (NEVER ON STREAM — root token exposed)
Vault init prints 5 unseal keys + root token to stdout. Do this alone, save immediately.

```bash
# 1. Add Vault to docker-compose first (Episode 4 prep)
# 2. Start it in dev mode initially
# 3. Run init and IMMEDIATELY save output to 1Password

ssh cyber-squire-tunnel 'docker exec cd-service-vault vault operator init'
# → Save ALL output to 1Password → Core Infra → "Vault Init Keys"
# → Tag: vault, unseal-keys

# Unseal vault (needs 3 of 5 keys)
ssh cyber-squire-tunnel 'docker exec -it cd-service-vault vault operator unseal'
```

> **Do this off-stream.** You cannot unseal Vault without these keys. Losing them = full rebuild.

---

### Step 5 — Create Stream-Safe Shell Config (~15 min)

```bash
# Create stream protection profile
cat > ~/.zshrc_stream << 'EOF'
# Load before going live - protects against accidental credential exposure

# Block dangerous commands on stream
alias op='echo "[1Password - run off stream]"'
alias cat='cat_safe'
cat_safe() {
  case "$1" in
    *.env*|*secret*|*credential*|*key*|*token*)
      echo "[PROTECTED FILE - off stream only]"
      ;;
    *)
      /bin/cat "$@"
      ;;
  esac
}

# Clean prompt - no full paths that reveal structure
export PS1="%F{green}[STREAM]%f %1~ $ "

# Remind yourself
echo "🔴 STREAM MODE ACTIVE - credentials blocked"
EOF
```

Run `source ~/.zshrc_stream` before every stream.

---

### Step 6 — Create .env.demo (commit this to repo)

```bash
cat > /Users/et/cyber-squire-ops/.env.demo << 'EOF'
# DEMO VALUES — used for stream walkthroughs
# Real values are in 1Password → Core Infra vault

DATADOG_API_KEY=dd-api-xxxx-demo-stream-safe
DATADOG_APP_KEY=dd-app-xxxx-demo-stream-safe
DO_TOKEN=dop_v1_demo_stream_safe
VAULT_TOKEN=hvs.demo-root-token-stream
KEYCLOAK_ADMIN_PASSWORD=demo-admin-password-stream
VAULT_ADDR=http://localhost:8200
EOF
```

---

### Step 7 — OBS Setup (before Episode 1)
- [ ] Add a **scene** called "Stream - Code" with terminal + browser
- [ ] Add a **scene** called "Stream - Architecture" with screen share + overlay
- [ ] Source filter on terminal: Filters → Crop/Pad — crop bottom 30px (hides prompt path)
- [ ] Test: type `cat ~/.ssh/id_rsa` and confirm it shows `[PROTECTED FILE]` via the alias
- [ ] Disable Telegram notifications during stream (Telegram → Settings → Notifications → mute)
- [ ] Disable Mac notification banners: System Settings → Notifications → set all to None

---

## STREAM EPISODES — BUILD ORDER

### Episode 1 — Architecture Overview (No credentials, 100% safe)
**What:** Draw and explain the full stack. No setup.
**Content value:** Sets context for entire series. One episode = 5-10 TikTok clips.
**Prep:** None. Just have the architecture doc + diagrams ready.

---

### Episode 2 — GitHub Actions Security Pipeline
**Pre-stream:** GitHub secrets set (Step 2 above)
**On-stream:** Write the YAML live
**Deliverable:** `.github/workflows/security.yml`

```yaml
# Preview — write this live on stream
name: Security Pipeline
on: [push, pull_request]
jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Trivy Scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          severity: 'CRITICAL,HIGH'
      - name: Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: p/security-audit
```

**Stream moment:** Push a test file with a fake credential → show pipeline block it live.
That clip alone will go viral in the security community.

---

### Episode 3 — Datadog Multi-Cloud Dashboard
**Pre-stream:** Datadog account + API key set (Steps 1-2 above), agent pre-installed
**On-stream:** Show integration, explain each panel, add AWS + Docker sources
**Demo moment:** Show GuardDuty alert flowing into Datadog Security Signals

---

### Episode 4 — Keycloak SSO & RBAC
**Pre-stream:** Docker image pulled (Step 3), admin password in 1Password
**On-stream:** Add to docker-compose live, configure realm + clients + RBAC
**Demo moment:** Log into n8n via Keycloak SSO instead of local auth

---

### Episode 5 — HashiCorp Vault Secrets Management
**Pre-stream:** Docker image pulled (Step 3), Vault initialized + unsealed (Step 4)
**On-stream:** Show secret policies, AppRole setup, migrate one .env value to Vault
**Demo moment:** n8n workflow fetches Postgres creds from Vault at runtime — no hardcoded password

---

## INTERVIEW DEMO SCRIPTS (prep these before applying)

**After Episode 2 (GitHub Actions):**
> "Every commit to my infra repo runs Trivy, Gitleaks, and Semgrep.
> Here's a PR I blocked last week when it detected a test credential I'd staged.
> The pipeline generates an SBOM on every merge to main."

**After Episode 3 (Datadog):**
> "I run Datadog across AWS and DigitalOcean — unified visibility from one pane.
> GuardDuty findings feed into Datadog Security Signals and auto-trigger my n8n
> SOAR workflow. Here's the dashboard live."

**After Episode 5 (Vault):**
> "Nothing is hardcoded. n8n uses AppRole to fetch a short-lived Postgres token
> at runtime. 1-hour TTL, auto-renew. Vault audits every access. The .env file
> has zero real values — all references point to Vault paths."

---

## CONTENT REPURPOSE PIPELINE (after each stream)

Each stream automatically becomes:
- 1x YouTube long-form (full stream recording, trimmed)
- 5-10x TikTok clips (key moments: demo blocks, "aha" explanations, the Vault AppRole explanation)
- 1x GitHub commit (the actual code, clean of credentials)
- 1x Skool post (community update + link to stream)

Use `builds/content-repurpose/` pipeline to automate the clip extraction.

---

## COST SUMMARY

| Service | Monthly Cost | How |
|---------|-------------|-----|
| GitHub Actions | $0 | Free for public repos |
| Datadog Pro | $0 | GitHub Education Pack |
| DigitalOcean K8s | $0 | $200 education credit (~8 months) |
| Keycloak | $0 | Open source, runs in Docker |
| Vault | $0 | Open source, runs in Docker |
| Trivy/Gitleaks/Semgrep | $0 | Open source GitHub Actions |
| **Total** | **$0/month** | Until DO credit expires |

After DO credit: ~$24/month for smallest K8s cluster, $23/month Datadog if Education Pack expires.

---

*Created: 2026-02-25*
*Start date: 2026-02-26*
