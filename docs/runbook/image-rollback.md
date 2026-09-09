# Image Rollback Runbook

Procedures for safely deploying and rolling back container image changes in the COREDIRECTIVE_ENGINE compose stack.

Every host command below uses the `cd-oci` SSH alias. If direct SSH times out, the network you are working from sits outside the instance's ingress allowlist. Use the `cd-oci-tunnel` alias instead, which reaches the same host through cloudflared and needs a one time `cloudflared access login` per device.

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

On the host:

```bash
ssh cd-oci
cd /opt/coredirective
TS=$(date -u +%Y%m%d-%H%M%S)
cp docker-compose.yaml docker-compose.yaml.pre-pin-$TS
ls -la docker-compose.yaml.pre-pin-*
```

This creates an immutable rollback point that does not depend on git history.

## Deploy Updated Compose to the Host

From your Mac (after committing changes):

```bash
scp ~/cyber-squire-ops/COREDIRECTIVE_ENGINE/docker-compose.yaml \
    cd-oci:/opt/coredirective/docker-compose.yaml
```

Then on the host, pull all images and validate they exist before touching running containers:

```bash
ssh cd-oci
cd /opt/coredirective
docker compose pull
```

If `pull` fails for any image, abort. Fix the digest or tag in compose, scp again. Do not proceed.

## Per-Service Rollout (recommended)

Bring services up one at a time so a single bad image does not knock the stack over.

```bash
ssh cd-oci
cd /opt/coredirective
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
ssh cd-oci
cd /opt/coredirective
docker compose up -d
sleep 30
docker compose ps
```

Verify every service shows `(healthy)` in status.

## Rollback Paths

### Tier 1 and Tier 2 (image:semver@digest or image:semver)

Two options.

Option A, fast, file level rollback:

```bash
ssh cd-oci
cd /opt/coredirective
cp docker-compose.yaml.pre-pin-<timestamp> docker-compose.yaml
docker compose up -d
```

Option B, clean, git level rollback:

```bash
# On Mac
cd ~/cyber-squire-ops
git revert <bad-commit-sha>
git push origin main
scp COREDIRECTIVE_ENGINE/docker-compose.yaml cd-oci:/opt/coredirective/docker-compose.yaml

# On the host
ssh cd-oci
cd /opt/coredirective
docker compose up -d
```

Option B is preferred when the bad commit is already pushed. Leaves a clean audit trail.

### Tier 3 (image:latest)

The previous image's digest is what you need to rollback to. Capture it before any restart:

```bash
# Before restart, capture current digest
ssh cd-oci
docker inspect ollama/ollama:latest --format "{{json .RepoDigests}}"
# Save the output. That is your rollback target.
```

To rollback after a bad pull:

```bash
ssh cd-oci
# Pull the known-good digest
docker pull ollama/ollama@sha256:<saved-digest>
# Retag it as latest locally so compose picks it up
docker tag ollama/ollama@sha256:<saved-digest> ollama/ollama:latest
# Restart the service
cd /opt/coredirective
docker compose up -d --no-deps cd-service-ollama
```

### Tier 0 (locally built: cd-service-nemo, cd-service-squire, cd-service-fluentd)

Versioning convention going forward: tag rebuilds as `cd-service-<name>:YYYYMMDD-<short-sha>` and keep the last 3 versions on disk.

#### Build path

These three images are produced on the host rather than pulled, so the host needs a builder. It did not have one until 2026-09-09.

**What is installed.** BuildKit comes from Ubuntu's own `docker-buildx` package in `jammy-updates/universe`:

```bash
ssh cd-oci 'sudo apt-get update && sudo apt-get install -y docker-buildx'
ssh cd-oci 'docker buildx version && docker buildx ls'
```

Installed 2026-09-09 at `0.30.1-0ubuntu1~22.04.1`, native arm64. The plugin lands in `/usr/libexec/docker/cli-plugins/` beside the compose and trust plugins that were already there, and `docker buildx ls` reports a `default` builder running BuildKit v0.26.2 on `linux/arm64`.

**Why not Docker's own repository.** `docker-buildx-plugin` is Docker's name for the same component and it lives at `download.docker.com`. The host's `docker.io` and `containerd` packages both come from Ubuntu's archive, and putting a second packaging source beside them for one stack is a reliable way to break a working install. There is nothing in Docker's build of buildx that this repository needs and Ubuntu's build does not provide. After the install, `/etc/apt/sources.list.d/` still holds zero entries.

**What it consumes.** Measured with `df -k /` immediately before and after: about 79 MiB of host disk, of which the plugin binary is roughly 65 MiB. One package from a repository the host is already configured to trust, with nothing upgraded and nothing removed. Operator time is one command. Build minutes run on the instance's four cores, where the Fluentd image finishes in seconds and NeMo is the expensive one because it pulls torch and the 560 MB `en_core_web_lg` spaCy model. There is no account to create, no key to hold, no continuous integration surface, and no new dependency at runtime.

**How to reverse it.**

```bash
ssh cd-oci 'docker buildx rm --all-inactive --force'
ssh cd-oci 'sudo apt-get remove -y docker-buildx'
```

Removing the package removes the subcommand, and `docker build` returns to the legacy builder, which still works in Docker 29.1.3. buildx is a client plugin, so neither installing nor removing it changes anything about the running stack. This was checked before it was written down: `apt-get -s remove docker-buildx` reports one package removed and nothing else touched.

**The alternative, and why it waits.** Publishing these images to the GitHub Container Registry with `docker/build-push-action` on the arm64 hosted runners is the better long run answer, and the ground is already prepared: the repository is public, the workflows SHA pin their actions, and `security.yml` already installs Cosign. It waits for Phase 24 because `scripts/verify_image_signatures.py` fails closed on any `image:` reference that has no entry in `.github/image-signers.json`. The moment a compose line points at a registry, that gate breaks the pull request until the images are keyless signed, which is requirement RB-04. Reversal for that path, if it is taken anyway: revert the workflow, revert the `image:` lines back to local tags, revert the signers entry, and delete the package from the GitHub packages interface.

**Two Arm pins had to move before any of this could build.** Both were measured on the host on 2026-09-09.

- `COREDIRECTIVE_ENGINE/CD_VOL_FLUENTD/Dockerfile`: base moved from `fluent/fluentd:v1.16-1` to `v1.19-1`. Every tag from v1.16 through v1.18 publishes a single amd64 manifest, so none of them can build here. v1.19-1 publishes amd64, arm and arm64.
- `builds/squire/docker/nemo_config/Dockerfile`: torch pin moved from `torch==2.5.1+cpu` to `torch==2.5.1`, and the PyTorch cpu extra index was dropped from that pip invocation. On aarch64 the `+cpu` local version only begins at 2.6.0, and PyPI serves a plain 2.5.1 aarch64 wheel that is already CPU only there, because upstream publishes no CUDA build for the platform.

**There is no repository checkout on the host.** The build source lives on the workstation, so the short SHA is computed where git is and the context is copied up. The rebuild commands below reflect that. Do not reintroduce a `git -C ... rev-parse` that runs on the host; it has nothing to read.

| Image | Context to copy up |
|---|---|
| `cd-service-nemo` | `builds/squire/docker/nemo_config/` |
| `cd-service-squire` | `builds/squire/` |
| `cd-service-fluentd` | `COREDIRECTIVE_ENGINE/CD_VOL_FLUENTD/` |

To rebuild:

```bash
# On the workstation, where the source and git history live.
cd ~/cyber-squire-ops
TAG="$(date -u +%Y%m%d)-$(git rev-parse --short HEAD)"

ssh cd-oci 'mkdir -p /tmp/build-nemo'
scp -r builds/squire/docker/nemo_config/. cd-oci:/tmp/build-nemo/

ssh cd-oci "cd /tmp/build-nemo \
  && docker buildx build --load -t cd-service-nemo:$TAG . \
  && docker image inspect cd-service-nemo:$TAG --format '{{.Architecture}} {{.Os}}' \
  && docker tag cd-service-nemo:$TAG cd-service-nemo:dev"

ssh cd-oci 'cd /opt/coredirective && docker compose up -d --no-deps cd-service-nemo'
ssh cd-oci 'rm -rf /tmp/build-nemo'
```

The inspect line should print `arm64 linux`. If it prints `amd64`, the base image or a pinned wheel is wrong for this host and the two entries above are the first place to look.

To rollback:

```bash
ssh cd-oci
# List existing builds
docker images cd-service-nemo
# Retag a prior build as :dev
docker tag cd-service-nemo:<prior-tag> cd-service-nemo:dev
cd /opt/coredirective
docker compose up -d --no-deps cd-service-nemo
```

To prune old builds (keep last 3):

```bash
ssh cd-oci
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
ssh cd-oci
cd /opt/coredirective
docker compose ps
docker compose ps --filter status=exited
docker stats --no-stream
```

Healthy stack: every service `Up X minutes (healthy)`, no exited containers, memory and CPU within limits set in the compose `deploy.resources.limits`.

If any service is unhealthy after 5 minutes, rollback immediately and investigate from logs.

## Backup Retention

Keep the 5 most recent pre-pin backups on the host. Prune older ones:

```bash
ssh cd-oci
cd /opt/coredirective
ls -t docker-compose.yaml.pre-pin-* | tail -n +6 | xargs -I {} rm -- {}
```
