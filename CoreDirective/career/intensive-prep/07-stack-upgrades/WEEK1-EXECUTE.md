# Week 1 Execute: Day-By-Day Playbook

**Window.** 7 calendar days starting tomorrow morning.
**Operator profile.** ADHD, 4-hour sleep nights, learns by building. No block longer than 90 minutes. Two blocks per day max on a heavy day. Commits as proof of motion.
**Goal at end of week.** Three upgrades shipped (A, D, F), one upgrade scaffolded (J), one demo-ready public repo, one new GRC doc.

**Rules.**
- Every block ends with a commit. If there's no commit, the block didn't happen.
- If a block runs past 90 minutes, stop, write down where you are, walk for 10. Resume next block.
- Two consecutive failed blocks = pivot to the rest day plan, not power through.
- Phone on do not disturb during blocks. Telegram bot off. No exceptions.

---

## Day 1 — Monday: Promptfoo skeleton

**Morning block (90 min). Stand up the harness directory and first 10 tests.**

```bash
mkdir -p ~/cyber-squire-ops/builds/promptfoo-eval/{tests,results}
cd ~/cyber-squire-ops/builds/promptfoo-eval
npm init -y
npm install -g promptfoo
```

Create `promptfoo-config.yaml`:

```yaml
description: OpenClaw AI Gateway eval against OWASP LLM Top 10 + MITRE ATLAS

providers:
  - id: openclaw
    config:
      apiBaseUrl: http://172.17.0.1:18789/v1
      model: anthropic/claude-opus-4-7
      apiKeyEnvar: OPENCLAW_ANTHROPIC_KEY

prompts:
  - file://prompts/system.txt
  - "{{user_prompt}}"

tests: file://tests/owasp-llm-top10.yaml

defaultTest:
  options:
    cache: true
    transform: file://transforms/strip_thinking.js

threshold: 0.85
```

Create `tests/owasp-llm-top10.yaml` with 10 cases:
- LLM01 prompt injection (3 cases)
- LLM02 insecure output handling (1 case)
- LLM03 training data poisoning (1 case, prompt-side proxy)
- LLM06 sensitive info disclosure (2 cases)
- LLM07 insecure plugin design (1 case)
- LLM08 excessive agency (1 case)
- LLM09 overreliance (1 case)

Each case has `assert: not-icontains: <leak signal>` or `llm-rubric` checks.

Run locally:
```bash
doppler run -- promptfoo eval -c promptfoo-config.yaml
```

Capture first scorecard. Commit:
```bash
git add builds/promptfoo-eval/
git commit -m "feat(eval): seed promptfoo harness against openclaw with first 10 OWASP LLM tests"
```

**End-of-day checkpoint.** Local green run with 10 tests. Scorecard saved to `results/2026-05-09.json`.

**Evening block (45 min, optional). Read STAR Story 2 aloud three times.** Time it. Do not look at notes after the first read.

---

## Day 2 — Tuesday: Promptfoo full corpus + CI gate

**Morning block (90 min). Add 30 more tests + tool-call hijack cases.**

Add `tests/mitre-atlas.yaml` covering:
- AML.T0051 LLM Prompt Injection (5 cases)
- AML.T0048 External Harms (3 cases)
- AML.T0054 LLM Jailbreak (5 cases)
- AML.T0057 LLM Data Leakage (3 cases)

Add `tests/tool-call-hijack.yaml` covering:
- Tool call to GitHub when user asked for Tavily (3 cases)
- Tool call argument injection (4 cases)
- Tool call without explicit user intent (3 cases)
- Stub-tool exfiltration probes (4 cases)

Run all 50 tests locally:
```bash
doppler run -- promptfoo eval -c promptfoo-config.yaml --output results/run-$(date +%F).json
```

**Afternoon block (60 min). Wire to GitHub Actions.**

Create `.github/workflows/promptfoo-eval.yml`:

```yaml
name: Promptfoo OpenClaw Eval

on:
  push:
    paths:
      - 'builds/promptfoo-eval/**'
      - 'COREDIRECTIVE_ENGINE/openclaw/**'
  schedule:
    - cron: '0 6 * * 1'  # weekly Mon 06:00 UTC
  workflow_dispatch:

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm install -g promptfoo
      - name: Run eval
        env:
          OPENCLAW_ANTHROPIC_KEY: ${{ secrets.OPENCLAW_ANTHROPIC_KEY }}
        run: |
          cd builds/promptfoo-eval
          promptfoo eval -c promptfoo-config.yaml --output results/ci-${{ github.sha }}.json
      - uses: actions/upload-artifact@v4
        with:
          name: promptfoo-results-${{ github.sha }}
          path: builds/promptfoo-eval/results/
```

Add `OPENCLAW_ANTHROPIC_KEY` to repo secrets (pull from Doppler):
```bash
doppler secrets get OPENCLAW_ANTHROPIC_KEY --plain | gh secret set OPENCLAW_ANTHROPIC_KEY -R ET-sec/cyber-squire1
```

Push and watch first CI run land. Iterate until green.

**Sanitize and push public fork:**
```bash
gh repo create ET-sec/openclaw-eval-harness --public --description "Promptfoo eval harness for AI gateways: OWASP LLM Top 10 + MITRE ATLAS"
# Sanitize: scrub the openclaw provider URL to a placeholder, scrub real prompts, scrub test results
```

**End-of-day checkpoint.** First green GitHub Actions run. Public repo `ET-sec/openclaw-eval-harness` live with sanitized config. Save the green checkmark screenshot.

**Commit:**
```bash
git commit -m "feat(eval): wire promptfoo CI gate against openclaw with OWASP + ATLAS coverage"
```

---

## Day 3 — Wednesday: Falco agentic rules draft

**Morning block (90 min). Write 8 rules.**

```bash
mkdir -p ~/cyber-squire-ops/COREDIRECTIVE_ENGINE/falco/rules
cd ~/cyber-squire-ops/COREDIRECTIVE_ENGINE/falco/rules
```

Create `falco_rules_agentic.yaml`:

```yaml
- rule: Model container spawning shell
  desc: An AI model container should never exec into a shell
  condition: >
    spawned_process and
    container.name in (cd-service-ollama, cd-service-whisper, openclaw-gateway) and
    proc.name in (bash, sh, zsh, dash)
  output: "AI model container spawned shell (container=%container.name proc=%proc.cmdline user=%user.name)"
  priority: WARNING
  tags: [agentic, atlas-AML.T0024]

- rule: OpenClaw outbound non-loopback
  desc: OpenClaw should only talk to localhost or the model API
  condition: >
    outbound and
    container.name = openclaw-gateway and
    not fd.sip in (127.0.0.1, 172.17.0.1) and
    not fd.sport in (443) and
    not fd.sip in (cd_known_outbound_ips)
  output: "OpenClaw made unexpected outbound connection (container=%container.name dest=%fd.rip:%fd.rport)"
  priority: HIGH
  tags: [agentic, atlas-AML.T0048]

- rule: Ollama writing outside its volume
  desc: Ollama should only write inside CD_VOL_OLLAMA
  condition: >
    open_write and
    container.name = cd-service-ollama and
    not fd.name startswith /root/.ollama and
    not fd.name startswith /tmp
  output: "Ollama wrote outside expected volume (file=%fd.name container=%container.name)"
  priority: HIGH
  tags: [agentic]

- rule: n8n container exec'ing into shell
  desc: n8n shouldn't spawn shells unless explicitly run via execute-command node
  condition: >
    spawned_process and
    container.name = cd-service-n8n and
    proc.name in (bash, sh) and
    not proc.pname = node
  output: "n8n container spawned shell (container=%container.name proc=%proc.cmdline pproc=%proc.pname)"
  priority: WARNING
  tags: [agentic]

- rule: Tool call argument contains injection sigil
  desc: Filesystem write of a tool call payload that contains a known injection signal
  condition: >
    open_write and
    container.name in (cd-service-n8n, openclaw-gateway) and
    fd.name endswith .json and
    evt.buffer contains "ignore previous instructions"
  output: "Tool call payload contains injection sigil (file=%fd.name container=%container.name)"
  priority: HIGH
  tags: [agentic, atlas-AML.T0051]

- rule: Model upload to external bucket
  desc: AI containers shouldn't push to external object storage
  condition: >
    outbound and
    container.name in (cd-service-ollama, openclaw-gateway, cd-service-whisper) and
    (fd.sip startswith "s3.amazonaws.com" or fd.sip endswith ".digitaloceanspaces.com")
  output: "AI container pushed to external bucket (container=%container.name dest=%fd.rip)"
  priority: HIGH
  tags: [agentic, atlas-AML.T0025]

- rule: Secrets path probe in AI container
  desc: AI container reading common secret paths
  condition: >
    open_read and
    container.name in (cd-service-ollama, openclaw-gateway, cd-service-n8n) and
    (fd.name in (/etc/shadow, /etc/passwd, /root/.ssh/id_ed25519, /root/.ssh/id_rsa) or
     fd.name endswith .env)
  output: "AI container probed secrets path (file=%fd.name container=%container.name)"
  priority: HIGH
  tags: [agentic]

- rule: Agent process unexpected fork
  desc: An agent process should not fork beyond its known children
  condition: >
    spawned_process and
    container.name = openclaw-gateway and
    not proc.name in (openclaw, node, python3, claude)
  output: "OpenClaw forked unexpected process (proc=%proc.cmdline pproc=%proc.pname)"
  priority: WARNING
  tags: [agentic]
```

Hot-load:
```bash
ssh cd-alpha 'cd /root/COREDIRECTIVE_ENGINE && docker compose restart cd-service-falco'
```

Tail logs:
```bash
ssh cd-alpha 'docker logs -f cd-service-falco' &
```

**Afternoon block (60 min). Trigger each rule synthetically.**

For each rule, write a one-line trigger you can run on the host. Capture the Falco log entry for each. Save to `~/cyber-squire-ops/COREDIRECTIVE_ENGINE/falco/tests/test_agentic_rules.sh`.

**End-of-day checkpoint.** Eight rules live, eight Falco events captured in test logs.

**Commit:**
```bash
git commit -m "feat(detection): add 8 falco rules for agentic abuse patterns mapped to MITRE ATLAS"
```

---

## Day 4 — Thursday: Falco rules to Datadog + public repo

**Morning block (60 min). Verify Falcosidekick to Datadog routing.**

Confirm `cd-service-falcosidekick` config has Datadog endpoint and API key:
```bash
ssh cd-alpha 'cat /root/COREDIRECTIVE_ENGINE/.env | grep DATADOG_API_KEY'
ssh cd-alpha 'docker logs cd-service-falcosidekick 2>&1 | tail -20'
```

Trigger one HIGH-priority synthetic event. Confirm it lands in Datadog us5 within 60 seconds. Screenshot for the interview deck (save to `~/cyber-squire-ops/CoreDirective/career/intensive-prep/07-stack-upgrades/screenshots/`).

**Afternoon block (90 min). Public repo + README.**

```bash
mkdir -p ~/repos/falco-agentic-rules
cd ~/repos/falco-agentic-rules
cp ~/cyber-squire-ops/COREDIRECTIVE_ENGINE/falco/rules/falco_rules_agentic.yaml .
```

Sanitize: replace `cd-service-*` with placeholder names, strip any internal IPs, change `openclaw-gateway` to `<your-ai-gateway>`.

Write `README.md`:
- Title: "Falco Rules for Agentic AI Abuse"
- 8 rules summary table with ATT&CK + ATLAS mappings
- How to install (path, Falco config snippet)
- How each rule is tested
- Known false positives and tuning advice

Push:
```bash
gh repo create ET-sec/falco-agentic-rules --public --description "Falco rules for detecting agentic AI abuse mapped to MITRE ATLAS"
git init && git add . && git commit -m "init: 8 falco rules for agentic abuse detection"
git push -u origin main
```

**End-of-day checkpoint.** Public repo live. Datadog screenshot saved. `docs/grc/DETECTION_RULES_AGENTIC.md` written and committed.

**Commit on cyber-squire1:**
```bash
git add docs/grc/DETECTION_RULES_AGENTIC.md
git commit -m "docs(grc): add agentic detection rules document referencing falco-agentic-rules"
```

---

## Day 5 — Friday: AI Bill of Materials

**Morning block (90 min). Manifest + generator.**

```bash
mkdir -p ~/cyber-squire-ops/builds/ai-bom
cd ~/cyber-squire-ops/builds/ai-bom
```

Create `manifest.yaml`:

```yaml
ai_bom_version: 0.1
generated_at: 2026-05-13
operator: CoreDirective Engine

models:
  - id: claude-opus-4-7
    provider: Anthropic
    deployment: openclaw-gateway
    purpose: orchestration, reasoning, code generation
    data_classification: operational + sanitized
    residency: cloud (US, Anthropic)
    fallback: ollama-local (llama3.1:8b)
    license: vendor terms

  - id: llama3.1:8b
    provider: Meta (via Ollama)
    deployment: cd-service-ollama
    purpose: local fallback, sensitive triage
    data_classification: sensitive
    residency: on-host (cd-alpha)
    fallback: refuse and log
    license: Llama 3.1 Community License

  - id: whisper-large-v3
    provider: OpenAI (via local container)
    deployment: cd-service-whisper
    purpose: voice transcription
    data_classification: operational
    residency: on-host
    fallback: refuse
    license: MIT

prompt_templates:
  - id: master-orchestrator-system
    location: builds/n8n/prompts/master_system.md
    last_review: 2026-05-01
  - id: triage-agent-summarize
    location: builds/triage-agent/nodes/summarize_prompt.md
    last_review: pending

inference_endpoints:
  - id: openclaw-chat-completions
    url: http://172.17.0.1:18789/v1/chat/completions
    auth: bearer token, scope-limited
    rate_limit: 60 rpm per token
  - id: ollama-generate
    url: http://172.17.0.1:11434/api/generate
    auth: localhost-only
  - id: whisper-asr
    url: http://172.17.0.1:8000/asr
    auth: localhost-only

datasets:
  - id: grc-corpus
    location: docs/grc/
    classification: sanitized
    purpose: retrieval grounding for triage agent
    record_count: 37
```

Create `generate.py`:

```python
import yaml, json, sys
from pathlib import Path
from datetime import datetime

src = yaml.safe_load(Path("manifest.yaml").read_text())

# Render markdown
md = ["# AI Bill of Materials", f"\n**Generated:** {src['generated_at']}\n"]
md.append(f"**Operator:** {src['operator']}\n")

for section, items in src.items():
    if section in ("ai_bom_version", "generated_at", "operator"): continue
    md.append(f"\n## {section.replace('_', ' ').title()}\n")
    for it in items:
        md.append(f"\n### {it.get('id', 'unknown')}\n")
        for k, v in it.items():
            if k == "id": continue
            md.append(f"- **{k.replace('_', ' ')}:** {v}")

Path("../../docs/grc/AI_BOM.md").write_text("\n".join(md))
Path("../../ai-bom.json").write_text(json.dumps(src, indent=2))
print("AI-BOM rendered: docs/grc/AI_BOM.md + ai-bom.json")
```

Run:
```bash
python3 generate.py
```

**Afternoon block (45 min). CI workflow + commit.**

Create `.github/workflows/ai-bom.yml`:

```yaml
name: AI BOM Regenerate
on:
  push:
    paths: [builds/ai-bom/manifest.yaml]
  workflow_dispatch:
jobs:
  regen:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install pyyaml
      - run: cd builds/ai-bom && python3 generate.py
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore(ai-bom): regenerate AI-BOM from manifest"
          file_pattern: "docs/grc/AI_BOM.md ai-bom.json"
```

**End-of-day checkpoint.** GRC corpus is now 38 docs. AI-BOM.md and ai-bom.json committed. CI regenerates on manifest change.

**Commit:**
```bash
git add builds/ai-bom/ docs/grc/AI_BOM.md ai-bom.json .github/workflows/ai-bom.yml
git commit -m "feat(grc): add AI Bill of Materials with generator and CI regen workflow"
```

**Update resume.** Change `37 GRC documents` to `38 GRC documents including AI-BOM` everywhere it appears.

---

## Day 6 — Saturday: Buffer + LangGraph triage scaffold

**Morning block (90 min). Buffer day if any of Days 1-5 slipped.** Otherwise:

Scaffold the triage agent so Day 8 can hit the ground running:

```bash
mkdir -p ~/cyber-squire-ops/builds/triage-agent/{nodes,eval}
cd ~/cyber-squire-ops/builds/triage-agent
python3 -m venv venv && source venv/bin/activate
pip install langgraph langchain-anthropic httpx
```

Create `graph.py` with three placeholder nodes that just print "stub" and return, and the LangGraph wiring. Create `nodes/enrich.py`, `nodes/correlate.py`, `nodes/summarize.py` as 5-line stubs.

Wire a Flask receiver at port 8003 to accept Falcosidekick webhook payloads:

```python
# receiver.py
from flask import Flask, request
import json
app = Flask(__name__)

@app.post("/falco")
def receive():
    payload = request.json
    print(json.dumps(payload, indent=2))
    return {"ok": True}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8003)
```

Test by triggering one Falco rule on the droplet, confirm payload lands.

**Afternoon block (rest).** Walk. Eat. Sleep more than 4 hours.

**Commit:**
```bash
git add builds/triage-agent/
git commit -m "scaffold(triage): seed langgraph triage agent with three node stubs and falco receiver"
```

---

## Day 7 — Sunday: Rest, review, dry run

**No new code.** This is the discipline day.

**Morning (60 min total, broken into chunks).**
- Read `STAR-STORIES.md` aloud at speaking pace. Do stories 1, 2, 3, 9. Time each one.
- Read `BUSINESS-FRAME.md` questions 1, 2, 5, 7, 10. Time each answer.
- For any story or answer that ran past 120 seconds, mark it. Tomorrow you trim.

**Midday (30 min).**
- Update LinkedIn featured: add `ET-sec/openclaw-eval-harness` and `ET-sec/falco-agentic-rules`.
- Update resume: 37 → 38 GRC docs, add line "Promptfoo CI gate against AI gateway: OWASP LLM Top 10 + MITRE ATLAS coverage."
- Apply through `/tailor-resume` for any role you didn't tailor for this week.

**Afternoon.** Walk. Read something not security. Sleep.

---

## End-of-week checklist

- [ ] Promptfoo harness with 50+ tests, CI gate live, public repo `ET-sec/openclaw-eval-harness`
- [ ] 8 Falco agentic rules deployed, Datadog routing verified, public repo `ET-sec/falco-agentic-rules`
- [ ] AI-BOM rendered to `docs/grc/AI_BOM.md` + `ai-bom.json`, CI regen wired
- [ ] LangGraph triage scaffold ready for Day 8 build
- [ ] Two Datadog screenshots saved for interview decks
- [ ] Resume updated: 38 GRC docs, Promptfoo CI line added
- [ ] LinkedIn featured updated with two new public repos
- [ ] Three STAR stories rehearsed aloud, timed under 120s

**If you hit 6 of 8 by end of Day 7, that's a green week.** Adjust Day 14 plans to absorb anything that slipped.

---

## ADHD operator notes

**On the 90-minute block.**
- Set a Pomodoro timer. When it rings, stop mid-keystroke if needed and walk for 10.
- The next block resumes from a written sticky note: "Next: write the Datadog test trigger for rule 5."
- The note is the bridge across the gap. Without it, you lose the next block to context-rebuilding.

**On commits.**
- Commit even if the work is half-done. The commit is proof of motion.
- A messy `wip:` commit you clean up later is better than a clean commit that didn't happen.
- End the week with `git log --oneline --since="7 days ago" | wc -l`. The number should be 12 to 20.

**On sleep.**
- 4 hours is the floor, not the plan. The plan is 6.
- The Promptfoo CI gate ships better at 6 hours than the LangGraph agent does at 4.
- If you have to choose between an evening block and an extra hour of sleep, pick sleep.

**On bailout.**
- If two consecutive blocks fail (no commit, no progress), stop the build day. Do the rest day plan. Resume tomorrow.
- Burning a day to rest beats burning a week to recover.
