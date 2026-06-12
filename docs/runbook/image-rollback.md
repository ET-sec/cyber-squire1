# Image Rollback Runbook

Procedures for safely deploying and rolling back container image changes in the COREDIRECTIVE_ENGINE compose stack.

## Image Tier Reference

Service tier determines update behavior and rollback path. See header of `COREDIRECTIVE_ENGINE/docker-compose.yaml` for the full policy.

| Tier | Behavior | Update path | Rollback path |
|------|----------|-------------|---------------|
| 1 (security boundary) | Digest pinned `image:semver@sha256:...` | Renovate PR, manual review | git revert + redeploy |
| 2 (state bearing) | Semver `image:major.minor.patch` | Renovate PR, patch may auto-merge | git revert + redeploy |
| 3 (stateless inference) | `image:latest` acceptable | Restart pulls newest | Retag previous digest |
| 0 (locally built) | `name:dev` or `name:YYYYMMDD-sha` | Rebuild + tag bump | Retag prior build |

Tier 1 services: Vault, Keycloak, Teleport, Teleport event handler, cloudflared, OpenClaw gateway.

Tier 2 services: pgvector, n8n, Datadog, Langfuse (web + worker), Redis, ClickHouse, Falco, Falcosidekick.

Tier 3 services: Ollama, Whisper.

Tier 0 services: cd-service-nemo, cd-service-squire, cd-service-fluentd.

## Pre-Deploy Backup (always run before pushing compose changes)

On the droplet:

```bash
ssh cd-alpha
cd /root/COREDIRECTIVE_ENGINE
TS=$(date -u +%Y%m%d-%H%M%S)
cp docker-compose.yaml docker-compose.yaml.pre-pin-$TS
ls -la docker-compose.yaml.pre-pin-*
```

This creates an immutable rollback point that does not depend on git history.

## Deploy Updated Compose to Droplet

From your Mac (after committing changes):

```bash
scp /Users/et/cyber-squire-ops/COREDIRECTIVE_ENGINE/docker-compose.yaml \
    cd-alpha:/root/COREDIRECTIVE_ENGINE/docker-compose.yaml
```

Then on the droplet, pull all images and validate they exist before touching running containers:

```bash
ssh cd-alpha
cd /root/COREDIRECTIVE_ENGINE
docker compose pull
```

If `pull` fails for any image, abort. Fix the digest or tag in compose, scp again. Do not proceed.

## Per-Service Rollout (recommended)

Bring services up one at a time so a single bad image does not knock the stack over.

```bash
ssh cd-alpha
cd /root/COREDIRECTIVE_ENGINE
docker compose up -d --no-deps <service>
sleep 20
docker compose ps <service>
docker compose logs --tail=50 <service>
```

If the service goes healthy, move to the next. If it does not, see rollback below.

Order matters for services with dependencies:
1. cd-service-db (everyone depends on it)
2. cd-service-vault, cd-service-keycloak
3. cd-service-langfuse-clickhouse, cd-service-langfuse-redis
4. cd-service-langfuse-worker, cd-service-langfuse-web
5. cd-service-n8n
6. cd-service-teleport, cd-service-teleport-event-handler
7. cd-service-fluentd
8. cd-service-ollama, cd-service-whisper, cd-service-nemo, cd-service-squire
9. cd-service-falco, cd-service-falcosidekick
10. cd-service-datadog
11. tunnel-cyber-squire

## Bulk Rollout (faster, more risk)

If the change is small and you trust the smoke test:

```bash
ssh cd-alpha
cd /root/COREDIRECTIVE_ENGINE
docker compose up -d
sleep 30
docker compose ps
```

Verify every service shows `(healthy)` in status.

## Rollback Paths

### Tier 1 and Tier 2 (image:semver@digest or image:semver)

Two options.

Option A — fast, file-level rollback:

```bash
ssh cd-alpha
cd /root/COREDIRECTIVE_ENGINE
cp docker-compose.yaml.pre-pin-<timestamp> docker-compose.yaml
docker compose up -d
```

Option B — clean, git-level rollback:

```bash
# On Mac
cd /Users/et/cyber-squire-ops
git revert <bad-commit-sha>
git push origin main
scp COREDIRECTIVE_ENGINE/docker-compose.yaml cd-alpha:/root/COREDIRECTIVE_ENGINE/docker-compose.yaml

# On droplet
ssh cd-alpha
cd /root/COREDIRECTIVE_ENGINE
docker compose up -d
```

Option B is preferred when the bad commit is already pushed. Leaves a clean audit trail.

### Tier 3 (image:latest)

The previous image's digest is what you need to rollback to. Capture it before any restart:

```bash
# Before restart — capture current digest
ssh cd-alpha
docker inspect ollama/ollama:latest --format "{{json .RepoDigests}}"
# Save the output. That is your rollback target.
```

To rollback after a bad pull:

```bash
ssh cd-alpha
# Pull the known-good digest
docker pull ollama/ollama@sha256:<saved-digest>
# Retag it as latest locally so compose picks it up
docker tag ollama/ollama@sha256:<saved-digest> ollama/ollama:latest
# Restart the service
cd /root/COREDIRECTIVE_ENGINE
docker compose up -d --no-deps cd-service-ollama
```

### Tier 0 (locally built — cd-service-nemo, cd-service-squire, cd-service-fluentd)

Versioning convention going forward: tag rebuilds as `cd-service-<name>:YYYYMMDD-<short-sha>` and keep the last 3 versions on disk.

To rebuild:

```bash
ssh cd-alpha
cd /root/COREDIRECTIVE_ENGINE
# Adjust path to source as needed
SHORT_SHA=$(git -C /root/cyber-squire-ops rev-parse --short HEAD)
TS=$(date -u +%Y%m%d)
docker build -t cd-service-nemo:$TS-$SHORT_SHA ../builds/squire/docker/nemo_config/
docker tag cd-service-nemo:$TS-$SHORT_SHA cd-service-nemo:dev
docker compose up -d --no-deps cd-service-nemo
```

To rollback:

```bash
ssh cd-alpha
# List existing builds
docker images cd-service-nemo
# Retag a prior build as :dev
docker tag cd-service-nemo:<prior-tag> cd-service-nemo:dev
cd /root/COREDIRECTIVE_ENGINE
docker compose up -d --no-deps cd-service-nemo
```

To prune old builds (keep last 3):

```bash
ssh cd-alpha
docker images cd-service-nemo --format '{{.Tag}}\t{{.CreatedAt}}' | sort -k2 -r | tail -n +4 | awk '{print $1}' | xargs -I {} docker rmi cd-service-nemo:{}
```

## Renovate PR Workflow

Renovate opens PRs every Monday before 9am ET. Each PR will:

1. Update one or more `image:` lines with a new digest or tag.
2. Trigger the `image-smoke.yml` CI workflow, which pulls and starts each changed image.
3. Apply labels: `tier-1`, `tier-2`, `security-boundary`, `needs-review`, etc.

Review checklist:

- [ ] Read the upstream changelog linked in the PR description.
- [ ] Confirm the smoke test passed.
- [ ] For Tier 1, verify no breaking config changes (Vault auth method changes, Teleport role schema, etc.).
- [ ] For Tier 2 majors, run the upgrade in a staging environment first if available.
- [ ] Merge during a low-traffic window.

## Post-Deploy Verification

Always run after any rollout:

```bash
ssh cd-alpha
cd /root/COREDIRECTIVE_ENGINE
docker compose ps
docker compose ps --filter status=exited
docker stats --no-stream
```

Healthy stack: every service `Up X minutes (healthy)`, no exited containers, memory and CPU within limits set in the compose `deploy.resources.limits`.

If any service is unhealthy after 5 minutes, rollback immediately and investigate from logs.

## Backup Retention

Keep the 5 most recent pre-pin backups on the droplet. Prune older ones:

```bash
ssh cd-alpha
cd /root/COREDIRECTIVE_ENGINE
ls -t docker-compose.yaml.pre-pin-* | tail -n +6 | xargs -I {} rm -- {}
```
