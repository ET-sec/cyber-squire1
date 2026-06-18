# Drill 03: Customer Support Chatbot With RAG

## Prompt
"Threat model an LLM-based customer support chatbot. The bot reads a knowledge base of customer-uploaded documents (RAG) plus product docs. Customers chat through a web widget."

## Scope (Phase 1)

Assets:
- Customer chat history (PII)
- Customer-uploaded documents (may contain confidential business data)
- LLM API keys (Anthropic, OpenAI)
- System prompt and tool definitions
- Vector embeddings of all corpus

Actors:
- End customer (authenticated)
- Anonymous trial user
- Internal support agent (escalation path)
- Adversarial user attempting prompt injection
- Compromised document publisher (indirect prompt injection)
- LLM API provider

Data classes:
- Customer-submitted text (mixed sensitivity)
- Retrieved chunks from KB (may include other customers' data if KB is shared)
- LLM responses
- Audit logs

Assumptions:
- One LLM provider, one embedding provider
- Vector DB is pgvector on managed Postgres
- Tool use is enabled (the bot can search KB, file tickets, look up account)
- Per-tenant KB isolation is required

## DFD

```
[ Customer ] --HTTPS--> ( Widget JS ) --> ( Edge / WAF )
                                                |
- - - - - - - - - - - - - - - - - - - - - - - - | - INTERNET BOUNDARY
                                                v
                                        ( Chat API svc )
                                       /        |        \
                                      /         |         \
                                  retrieve     log      invoke tool
                                      |         |         |
                                      v         v         v
                                =========    ======    ( Tool router )
                                | pgvec |    |Audit|         |
                                | KB    |    | DB  |         v
                                =========    ======    ( Account API )
                                                       ( Ticket API )
                                                       ( Search API )
                                  ^
                                  | embed
                                  |
                              ( Embedding fn )
                                  ^
                                  |  upload
- - - - - - - - - - - - - - - - -|- - - - - - - - - - - - - - - -
                              ( Doc Upload svc )
                                  ^
                                  |
[ Customer / Publisher ] --upload-->
                                  
                            INTERNET BOUNDARY for outbound to LLM
                                  v
                          ( Anthropic / OpenAI )
```

Trust boundaries:
1. Customer to Widget (TB1)
2. Widget to Chat API (TB2, internet)
3. Chat API to LLM provider (TB3, third-party egress)
4. Chat API to retrieved chunk (TB4, prompt injection boundary)
5. LLM output to tool router (TB5, output handling boundary)
6. Tool router to internal API (TB6, authorization boundary)
7. Doc upload to embedding pipeline (TB7, supply chain boundary)
8. Tenant KB to tenant KB (TB8, multi-tenant)

## STRIDE plus ATLAS matrix

| # | Boundary | Framework | Threat | L | I | Risk |
|---|----------|-----------|--------|---|---|------|
| 1 | TB2 | S (STRIDE) | Session token theft, attacker chats as victim | M | H | H |
| 2 | TB4 | E (STRIDE) + AML.T0051 | Indirect prompt injection: malicious doc tells the LLM to ignore instructions | H | H | H |
| 3 | TB4 | I (STRIDE) | RAG returns chunks from another tenant's KB | M | H | H |
| 4 | TB5 | E (STRIDE) | LLM emits tool call with attacker-supplied arguments (SSRF, account lookup of victim) | H | H | H |
| 5 | TB5 | I (STRIDE) | LLM regurgitates chunk that contains another customer's PII | M | H | H |
| 6 | TB3 | I (STRIDE) | Sensitive customer text egresses to LLM provider, retained for training | M | M | M |
| 7 | TB3 | D + AML.T0024 | Model extraction via API queries (mass query rate) | L | M | L |
| 8 | TB7 | T + AML.T0020 | Poisoned doc uploaded to flip retrieval order | M | H | H |
| 9 | TB6 | E (STRIDE) | Tool router invokes ticket-creation tool without verifying user-of-record | M | H | H |
| 10 | TB1 | T (STRIDE) | XSS in widget executes attacker JS in customer browser | M | H | H |
| 11 | TB2 | D (STRIDE) | Adversary floods chat to exhaust LLM token budget | H | M | H |
| 12 | TB4 | E + AML.T0043 | Adversarial input crafts prompt that bypasses safety classifier | M | H | H |
| 13 | TB5 | I + AML.T0048 | LLM hallucinates a false fact about a customer that gets logged as truth | H | M | H |
| 14 | TB7 | R (STRIDE) | No record of which doc embedding produced which retrieval | M | M | M |
| 15 | TB3 | S (STRIDE) | LLM API key leaks via client-side error log | L | H | M |

## Top 10

1. (#2) Indirect prompt injection
2. (#4) LLM tool abuse (excessive agency)
3. (#3) Cross-tenant RAG retrieval
4. (#5) PII regurgitation
5. (#9) Tool router authz bypass
6. (#10) XSS in widget
7. (#8) Doc poisoning
8. (#11) Token budget DoS
9. (#13) Hallucinated facts in audit
10. (#12) Safety classifier bypass

## Mitigations

| # | Primary | Compensating | Cost |
|---|---------|--------------|------|
| 1 | Strict input sanitization on retrieved chunks: strip instructions-shaped patterns, render in `<retrieved>` XML tag, instruct model to treat content as data not instructions | Output critique-loop comparing answer to retrieved chunk for hijack signals | M |
| 2 | Tool router enforces authorization on every tool call against the original user's session, never the LLM-supplied user | Audit log every tool call, alert on cross-user invocations | M |
| 3 | Tenant_id filter in pgvector query, IAM-scoped read policy, integration test that proves cross-tenant query fails | Daily automated cross-tenant probe | L |
| 4 | Output filter for PII (Presidio), redact before display, redact before logging | Per-query reviewer sample 1 percent | M |
| 5 | Tool allow-list, tool argument schema validation, tools are idempotent and read-mostly | Human-in-the-loop for write tools | M |
| 6 | CSP headers, sanitize all LLM output, render in sandboxed iframe, no innerHTML | DAST scan in CI | L |
| 7 | Doc upload scanned for instruction-shaped content, embedding stored with provenance, signed manifest | Periodic re-embed and consistency check | M |
| 8 | Per-user and per-tenant token budget, daily ceiling, 429 with backoff | Cost dashboard, alert at 80 percent | L |
| 9 | LLM responses tagged as `unverified` in audit until human confirms, transcripts signed | Drift detection on hallucination metrics | M |
| 10 | Defense-in-depth input filter (NeMo Guardrails or similar) | Red-team the bot quarterly | M |

## Residual risk

After mitigations: 0 HIGH, 5 MEDIUM, 10 LOW.

MEDIUMs:
- Indirect prompt injection: accepted because no perfect defense exists today, mitigation is layered (sanitize, structure, critique).
- Doc poisoning: accepted because at scale we cannot manually vet uploads, compensation is provenance plus re-embed.
- Hallucination in audit: accepted because language models hallucinate, mitigation is labeling and human verification on writes.
- Egress to LLM provider: accepted with contractual zero-retention DPA.
- Token-budget DoS: accepted with ceilings plus alerting.

The HIGH I would not ship without: tool router authz on every call. Without that, prompt injection becomes RCE.

## Detections

- Indirect injection: critique-loop disagreement metric, alert if disagreement rate exceeds 5 percent in any 1-hour window.
- Cross-tenant query: integration test runs every 5 minutes, page on failure.
- PII leak: scan LLM output with Presidio in shadow mode, alert on hits.
- Tool abuse: alert on any tool call where the requested user_id does not match the authenticated session.
- Doc poisoning: anomaly detection on retrieval rank shifts after new doc uploads.
- Token budget abuse: per-user spend alarm above 95th percentile.

Closing line:
"For RAG systems the boundary that surprises people is the chunk-to-context boundary. Every retrieved document is untrusted input, the same as user input. The threat surface widens because the LLM is now a confused deputy with tool access. The compensating control is to never trust the LLM to enforce authorization. Authorization lives in the tool router, always."
