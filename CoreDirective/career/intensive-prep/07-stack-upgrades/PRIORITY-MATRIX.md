# Priority Matrix: 14-Day Execution Order

**Frame:** Ten upgrades on the long roadmap. You have 14 days. Five make the cut. The other five wait until after first interviews land.

**Scoring scale (1-5 each).**
- **Interview leverage.** How many minutes of strong technical answer this earns you across the pipeline.
- **Build effort.** Inverse score. 5 = ships in a day, 1 = three painful days. Higher is better.
- **Defensibility.** How well it survives a senior interviewer poking at it. 5 = you can pull up a real production artifact and a number.

---

## Ranked top 5

| Rank | Upgrade | Leverage | Effort | Defens. | Total | Notes |
|------|---------|----------|--------|---------|-------|-------|
| 1 | A. Promptfoo CI gate against OpenClaw | 5 | 4 | 5 | 14 | Every interviewer asks "how do you know it's safe after a change." This is the answer. |
| 2 | J. LangGraph triage agent on Falco | 5 | 2 | 5 | 12 | Most expensive build, highest single-interview ceiling. The mirror story for Dropzone, OneDigital, Resilience. |
| 3 | D. Falco rules tuned for agentic abuse | 4 | 4 | 4 | 12 | Public detection-engineering portfolio you don't yet have. Pairs with E for amplification. |
| 4 | G. Real-time prompt-injection classifier at gateway | 5 | 2 | 4 | 11 | Above the bar. Most candidates won't have this. Heaviest day-3 of the build. |
| 5 | F. AI Bill of Materials | 3 | 5 | 4 | 12 | One day, one new GRC doc, one JSON. Cheap leverage for any GRC-leaning interviewer. |

**Cuts and why.**
- **B. NeMo Guardrails.** Pushed to week 3. Strong story, but Promptfoo + classifier already covers the inbound-threat narrative. Don't double-pay.
- **C. Garak weekly.** Pushed to week 3. The Promptfoo harness (Upgrade A) already proves model red-teaming on every commit. Garak is a nice-to-have second opinion.
- **E. Sigma library.** Pushed to week 3. Falco rules in D give you the public detection portfolio. Sigma is the polish, not the pitch.
- **H. Chainguard.** Pushed to month 2. One-day work, low individual leverage. Bundle with a future supply-chain story.
- **I. Coverage matrix.** Pushed to month 2. Director-level artifact, not relevant for the IC engineering rounds in the next 14 days.

---

## 14-day execution order with daily milestones

### Day 1 (start of week 1) — Promptfoo skeleton
- Stand up `~/cyber-squire-ops/builds/promptfoo-eval/`
- Write `promptfoo-config.yaml` with provider pointed at OpenClaw chat-completions endpoint
- Add 10 OWASP LLM Top 10 test cases
- Run locally, capture first scorecard

**End-of-day checkpoint.** First green local run, even if only 10 tests. Commit `feat(eval): seed promptfoo harness against openclaw`.

### Day 2 — Promptfoo full corpus + CI gate
- Add 30 more tests covering MITRE ATLAS techniques and tool-call hijack
- Write `.github/workflows/promptfoo-eval.yml` triggered on push to main and weekly cron
- Add threshold gate: any failed assertion blocks merge
- Push public sanitized fork to `ET-sec/openclaw-eval-harness`

**End-of-day checkpoint.** First green CI run on GitHub Actions. Public repo live. Tweet/LinkedIn post-ready (do not post yet).

### Day 3 — Falco agentic rules draft
- Create `COREDIRECTIVE_ENGINE/falco/rules/falco_rules_agentic.yaml`
- Write 8 rules: model container shell spawn, OpenClaw outbound non-loopback, Ollama writing outside volume, n8n exec into shell, suspicious tool-call args, model upload to public bucket, secrets in env probe, agent process forking unexpectedly
- Hot-load into Falco, watch logs

**End-of-day checkpoint.** Eight rules live. Trigger each one synthetically on a non-prod replica. Commit.

### Day 4 — Falco rules to Datadog + Sigma siblings
- Wire severity through Falcosidekick to Datadog with custom tags
- Write Sigma equivalents for the four most portable rules
- Push `ET-sec/falco-agentic-rules` repo with README, ATT&CK + ATLAS coverage table

**End-of-day checkpoint.** Public repo live, two screenshots saved (Datadog event, Falco log) for interview decks.

### Day 5 — AI Bill of Materials
- Write `manifest.yaml` cataloguing every model, prompt template, dataset, and inference endpoint
- Build `generate.py` to emit both markdown and JSON
- Render `docs/grc/AI_BOM.md` (becomes GRC doc 38)
- Add `.github/workflows/ai-bom.yml` to regenerate on manifest change

**End-of-day checkpoint.** GRC corpus is now 38 docs. Number is updated in resume + LinkedIn at end of week 1.

### Day 6 — Catch-up + LangGraph triage agent skeleton
- Buffer day. If anything from days 1-5 slipped, finish here.
- Otherwise: scaffold `builds/triage-agent/graph.py` with three placeholder nodes
- Wire Falcosidekick webhook target to a local Flask receiver

**End-of-day checkpoint.** End of week 1. You should be able to write the four-line LinkedIn update right now.

### Day 7 — Rest, review, dry run
- Read every file you wrote this week aloud as if explaining to an interviewer
- 60-second walkthrough script for each: Promptfoo CI, Falco agentic, AI-BOM
- No new code. ADHD recovery day. Sleep more than 4 hours.

### Day 8 — LangGraph enrich + correlate nodes
- Build `nodes/enrich.py`: Datadog API query for surrounding events
- Build `nodes/correlate.py`: search `docs/grc/` for similar incidents using a simple grep + embeddings combo
- Wire to OpenClaw chat-completions for `nodes/summarize.py` skeleton

**End-of-day checkpoint.** Synthetic alert in, three nodes execute end to end, ugly draft markdown out.

### Day 9 — LangGraph summarize + write-out + Telegram
- Implement `nodes/summarize.py` with structured prompt: Situation, Indicators, Recommended Action
- Output writes to `docs/grc/incidents/YYYY-MM-DD-<rule>.md`
- Telegram alert via `@Coredirective_bot` with 3-bullet summary

**End-of-day checkpoint.** First end-to-end run on a synthetic Falco alert produces a real incident draft you'd be proud to ship.

### Day 10 — LangGraph eval harness + 90-second demo recording
- Write `eval/synthetic_alerts.jsonl` with 20 synthetic Falco events
- Score grounding, completeness, false-trigger
- Record screen capture: alert fires → Telegram pings → markdown lands. Keep under 90 seconds.
- Push public repo `ET-sec/falco-triage-agent`

**End-of-day checkpoint.** Demo video saved at `~/cyber-squire-ops/CoreDirective/career/intensive-prep/07-stack-upgrades/demos/triage-agent-90s.mp4`.

### Day 11 — Prompt-injection classifier container
- Pull DeBERTa-base prompt-injection classifier (Hugging Face) into a sidecar container
- Wrap in a 50-line FastAPI app, expose `/classify` on port 8002
- Add `cd-service-pi-classifier` to compose

**End-of-day checkpoint.** `curl localhost:8002/classify` returns a score in under 200ms.

### Day 12 — Wire classifier into OpenClaw path + Datadog
- Add a pre-inference hook in OpenClaw config that calls the classifier
- Score >= threshold returns refusal + emits a Datadog event with severity high
- Write a one-page `docs/grc/PROMPT_INJECTION_CLASSIFIER.md` covering: design, threshold, latency, FP rate
- p95 latency target: under 200ms added

**End-of-day checkpoint.** Send a known jailbreak prompt through OpenClaw, observe refusal + Datadog event.

### Day 13 — Classifier eval + PR curve + cleanup
- Run on a held-out test set of 200 prompts
- Render PR curve to `pr_curve.png`
- Update `docs/grc/PROMPT_INJECTION_CLASSIFIER.md` with the curve and the precision/recall numbers

**End-of-day checkpoint.** GRC corpus is now 39 docs. You have a defensible classifier story with a real number.

### Day 14 — Polish, mock-interview, ship
- Read every public README aloud, fix anything that reads like an AI wrote it
- Update resume: 38 GRC docs becomes 39, add "Promptfoo CI gate" and "LangGraph triage agent" lines
- Update LinkedIn featured: add the two public repos and the demo video
- Deliver one mock-interview pass on each top-5 STAR story (see STAR-STORIES.md)

**End-of-day checkpoint.** All five upgrades shipped. Five new artifacts. Two new public repos. One new demo video. Resume + LinkedIn synced.

---

## Ruthless cuts confirmed

**Do not start any of these in the next 14 days.**
- NeMo Guardrails. Promptfoo + classifier covers the same interview question.
- Garak weekly. Promptfoo on every commit is the better story.
- Sigma library. Falco agentic rules are public enough.
- Chainguard. One-day work, but it's a closing chapter, not a lead.
- Coverage matrix. Director-level artifact, not the question that lands $200K IC roles.

These are good builds. They are not the builds that win the next 14 days. Defer.

---

## Daily review ritual

Every night before sleep, two questions:
1. **Did I commit something today?** If no, tomorrow starts at 90 minutes of catch-up.
2. **Could I demo what I shipped today in 90 seconds tomorrow morning?** If no, polish before sleep, not feature work.

ADHD discipline. Time-boxes. Commits as proof of motion. No mid-task pivots.
