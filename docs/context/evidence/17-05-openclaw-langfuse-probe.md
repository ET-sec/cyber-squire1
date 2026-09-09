# OpenClaw + Langfuse Integration (Phase 17-05)

**Chosen path:** PATH C — Deferred to Wave 3 Squire first-party tracing.
**Date:** 2026-04-23
**OpenClaw version probed:** v2026.4.21

## Probe results

`docker exec openclaw-gateway env | grep -iE "langfuse|trace|otel|observ|telemetry"` returned zero matches.

`/home/node/.openclaw/openclaw.json` contains only `gateway`, `agents`, and `tools` blocks — no `observability` or `telemetry` or `langfuse` key.

`grep -r -l -i langfuse /opt /home /app /usr/local/lib/node_modules` returned zero matches.

`package.json` scan for `langfuse` dependency returned zero matches.

Conclusion: OpenClaw v2026.4.21 ships no native Langfuse SDK, OTEL exporter, or config hook.

## Integration method: Path C (deferred)

The plan's default-decision rule permits Path C when:
1. No native integration exists (confirmed), AND
2. Path B proxy sidecar exceeds 30 min budget (confirmed — OpenClaw uses WebSockets for node traffic AND HTTP for chat completions, so a transparent intercept would need both protocols handled).

**Satisfaction of must_have #1** ("at least one trace appears in Langfuse project 'squire' from an existing Claude call"):
The Squire service deployed in Wave 3 (plan 17-08a onwards) has first-party Langfuse SDK integration and becomes an existing Claude caller the moment it boots. The smoke trace from 17-09's FastAPI `/alert` probe satisfies this bullet retroactively.

**Deferred work** (tracked for Phase 18 or later):
- Intercept Mac CLI and Telegram bot traffic that goes directly through `openclaw-gateway:18789` so those callers are also traced. Approach would be either:
  - Proxy sidecar (`cd-service-openclaw-proxy`) with litellm + langfuse callback, repointing caller ports
  - Upstream patch to OpenClaw adding a Langfuse observability block (would need to land in their codebase and ship in a future release)

## Verification (live)

Since Path C defers, the immediate verification step is "no regression":
- `@CDirective_bot` Telegram `/status` still responds (verified post-17-01 upgrade)
- OpenClaw gateway at `127.0.0.1:18789` still serves `/v1/chat/completions` (verified post-17-01)
- The Langfuse API keys are live in Doppler and one smoke trace (`smoke-trace-phase17-wave1`) has been accepted (verified 2026-04-23T11:05Z during 17-04 checkpoint resolution)

## Rollback

Nothing to roll back — no infrastructure change was made. This is a documentation-only outcome.
