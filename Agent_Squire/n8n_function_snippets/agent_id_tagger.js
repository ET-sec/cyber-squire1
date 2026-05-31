// agent_id tagger - paste into n8n Code node after any LLM-calling node.
//
// Purpose: stamp agent_id on every output item so the Datadog n8n integration
// carries the tag through to metrics, logs, and traces. Pairs with the
// Datadog tag taxonomy documented in docs/grc/AGENT_TELEMETRY.md.
//
// Usage:
//   1. Drop a Code node immediately AFTER the LLM-calling node
//      (OpenAI / Ollama / Anthropic / Tavily-summarize / etc).
//   2. Set the Code node Mode to "Run Once for All Items".
//   3. Paste this snippet.
//   4. Edit the AGENT_ID constant below to match the .agents/registry.yaml
//      entry for this workflow.
//
// Registry values for n8n agents (Phase 20):
//   - master_orchestrator        (workflow UIf3v1ZNN98OtUge)
//   - n8n_telegram_supervisor    (workflow iO6PfPdk0SSPBTWb)
//   - n8n_content_research       (workflow nhtwRpJATQoaZpxL)
//   - n8n_gmail_readers          (4 mailbox-specific workflows)
//
// Cardinality budget reminder: agent_id values are CLOSED (14 total). Do not
// inject per-session or per-request values; that explodes Datadog cardinality
// and breaks dashboards.

const AGENT_ID = 'master_orchestrator'; // EDIT ME per workflow

const out = [];
for (const item of $input.all()) {
  const payload = item.json || {};
  payload.agent_id = AGENT_ID;
  // Datadog n8n integration honors dd_tags array for tag injection.
  payload.dd_tags = Array.isArray(payload.dd_tags) ? payload.dd_tags : [];
  if (!payload.dd_tags.includes('agent_id:' + AGENT_ID)) {
    payload.dd_tags.push('agent_id:' + AGENT_ID);
  }
  out.push({ json: payload });
}
return out;
