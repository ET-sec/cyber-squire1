# scripts/grc/

GRC corpus tooling for the AI-Native GRC Pipeline (Phase 19).

## Modules

| File | Purpose | Plan |
|------|---------|------|
| `frontmatter_to_yaml.py` | Preprocess `docs/grc/*.md` frontmatter to a single YAML index for the reviewer agent | 19-01 |
| `grc_reference.md` | System-prompt reference card pinned into the reviewer agent's cache | 19-01 |
| `budget_guard.py` | Daily Anthropic spend gate (admin API or local ledger fallback) | 19-02 |
| `spend_ledger.py` | SQLite ledger with pinned per-model pricing | 19-02 |
| `sanitize_patterns.py` | 10 ordered regex patterns (IP, RFC1918, container names, tokens, etc.) | 19-02 |
| `sanitize_output.py` | Idempotent `sanitize(text)` function | 19-02 |
| `grc_reviewer.py` | PR reviewer agent (Opus 5 default, Fable 5 escalation) | 19-02 |
| `grc_mcp_server.py` | FastMCP stdio server exposing 5 read-only tools to Claude Desktop | 19-03 |
| `build_oscal.py` | OSCAL artifact emitter with optional cosign keyless signing | 19-05 |

---

## MCP Server Setup

`grc_mcp_server.py` exposes the GRC corpus to Claude Desktop over stdio. 5 read-only tools, no DB required.

### 1. Install dependencies (one-time, host-side)

```bash
python3 -m pip install --user --break-system-packages "mcp[cli]" python-frontmatter pydantic
```

### 2. Wire Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` and merge in the `grc_corpus` block. **Do not commit your edited config; it lives in your home directory only.**

```json
{
  "mcpServers": {
    "grc_corpus": {
      "command": "python3",
      "args": ["/Users/et/cyber-squire-ops/scripts/grc/grc_mcp_server.py"]
    }
  }
}
```

### 3. Restart Claude Desktop

Cmd+Q, reopen. The `grc_corpus` server should appear in the tool list with 5 tools:

- `list_docs` -- enumerate all GRC corpus documents
- `read_doc` -- read one document by filename (path-traversal + symlink guarded)
- `search_corpus` -- substring search across the corpus
- `get_poam` -- look up a POA&M row by short ID (e.g. `P17-15`)
- `get_threat_model_entry` -- pull a threat-model section by id (e.g. `T0051`, `ATC-01`)

Every tool return is sanitized: IPs, RFC1918, container names, internal domains, tokens, and root paths are redacted before they reach Claude Desktop.

---

## Demo prompts

Run these in a Claude Desktop chat after wiring the server. Same prompts live in `.planning/phases/19-ai-native-grc-pipeline/runbooks/mcp-demo.md`.

1. **List all GRC documents.**
   > Use the grc_corpus tool to list all GRC documents and summarize.

   Expected: a JSON array of 49+ documents from `docs/grc/`, each with filename, title, classification. Real titles, not hallucinations.

2. **Look up a real POA&M row.**
   > Use grc_corpus.get_poam to look up P17-15 and show me the row.

   Expected: a structured row with `poam_id`, `description`, `severity`, `owner`, `target_date`, `status`, `refs`. The description must reference the cycle 2 red-team rate-limit finding, not a fabricated entry.

3. **Search the corpus.**
   > Use grc_corpus.search_corpus for "residual risk" and show top 3 hits.

   Expected: 3 snippets with filename + offset + sanitized snippet text. Snippets must come from real documents (e.g. `RISK_ASSESSMENT.md`, `SQUIRE_SSP.md`, `SQUIRE_AI_RISK_ASSESSMENT.md`).

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Claude Desktop says "server broken" or the `grc_corpus` server is grey | Python interpreter cannot import `mcp` or `scripts.grc.sanitize_output` | Re-run the dependency install in step 1; ensure `claude_desktop_config.json` uses an absolute path to the script |
| Tool list is empty after restart | Config syntax error in `claude_desktop_config.json` | Validate with `python3 -m json.tool < ~/Library/Application\ Support/Claude/claude_desktop_config.json`; restart Claude Desktop |
| `read_doc` returns `Error: ... not allowed (path traversal)` | Filename contained `..` or started with `/` | Use only base filenames from `docs/grc/` (e.g. `SQUIRE_SSP.md`) |
| `read_doc` returns `Error: ... is a symlink (rejected)` | Filesystem entry inside `docs/grc/` is a symbolic link | Replace with a regular file or fetch the symlink target by its real filename |
| `get_poam` returns `error: poam_id must match ...` | ID was passed without the `P` prefix or wrong shape | Use canonical short form `P17-15` (no `POAM-` prefix, no spaces) |
| Tool response is cut off with `[TRUNCATED]` | Hit the 100KB hard cap | Use `read_doc` for the full document; refine `search_corpus` query; ask `get_threat_model_entry` for the specific section |

To debug end-to-end without Claude Desktop:

```bash
PYTHONPATH=. python3 -m pytest tests/grc/test_mcp_server_stdio.py -v
```

To run the MCP Inspector (interactive UI shows registered tools):

```bash
PYTHONPATH=. mcp dev scripts/grc/grc_mcp_server.py
```

---

## Disable

To stop Claude Desktop from launching the server:

1. Edit `~/Library/Application Support/Claude/claude_desktop_config.json`.
2. Remove the `grc_corpus` block from `mcpServers` (keep other servers intact). If `grc_corpus` is the only entry, you can delete the whole `mcpServers` key.
3. Restart Claude Desktop. The tool list should no longer show `grc_corpus`.

The server file at `scripts/grc/grc_mcp_server.py` stays in the repo; nothing else needs to change to disable it.

---

## Security posture

- Read-only by construction. Every tool carries `readOnlyHint: True` and there is no write path in the module.
- Path-traversal blocked: `is_relative_to(GRC_DIR.resolve())` plus symlink rejection on both pre-resolve and post-resolve paths.
- Output sanitized on every return through `scripts/grc/sanitize_output.sanitize()` (Plan 19-02): host-specific public IPs (env-supplied via `GRC_REDACT_IPS`), RFC1918, `cd-service-*`, `tigouetheory.com`, `/root/...`, Doppler tokens, Anthropic keys, GitHub PATs, AWS keys, Bearer tokens.
- Stdio pure: all logs go to stderr via `logging.basicConfig(stream=sys.stderr)`. Zero `print()` calls (CI-greppable).
- Size capped: 100KB hard ceiling on any single tool response; truncation marked with `[TRUNCATED]`.
- Tool exceptions trapped: every tool body wrapped in try/except, structured error returned, server stays alive.
