"""Retriever tests.

Two flavors:
  - Unit tests (always run): exercise the chunker on the fixture playbook and
    the GRCRetriever SQL-builder / row-mapping without touching the DB.
  - Integration tests (gated on RUN_INTEGRATION=1): hit the real pgvector DB
    via the SSH tunnel described in plan 17-07 task 5. Requires:
        CD_DB_HOST=127.0.0.1 CD_DB_PORT=15432 CD_DB_USER=... CD_DB_PASS=... CD_DB_NAME=...
        VOYAGE_API_KEY=... SQUIRE_EMBEDDING_PROVIDER=voyage SQUIRE_EMBEDDING_MODEL=voyage-3-large
    If RUN_INTEGRATION is unset or 0, those tests skip.
"""
from __future__ import annotations

import os
import statistics
import time
from pathlib import Path

import pytest

# Populate required env so pydantic-settings can instantiate for the unit tests.
os.environ.setdefault("CD_DB_USER", "x")
os.environ.setdefault("CD_DB_PASS", "x")
os.environ.setdefault("CD_DB_NAME", "x")
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "x")
os.environ.setdefault("LANGFUSE_SECRET_KEY", "x")
os.environ.setdefault("ANTHROPIC_API_KEY", "x")
os.environ.setdefault("SQUIRE_WEBHOOK_TOKEN", "x")

FIXTURE = Path(__file__).parent / "fixtures" / "sample_playbook.md"

RUN_INTEGRATION = os.environ.get("RUN_INTEGRATION", "0") == "1"

# The 5 canonical IR playbooks with natural-language queries that should map
# top-1 to the matching file. Queries are paraphrases, not filenames, so the
# retriever has to actually earn the top-1 via semantic similarity.
PLAYBOOK_QUERIES: list[tuple[str, str]] = [
    (
        "How do I respond to a compromised Docker container showing unexpected exec calls from Falco?",
        "PLAYBOOK_COMPROMISED_CONTAINER.md",
    ),
    (
        "Someone leaked a credential to GitHub, what are the rotation and blast-radius steps?",
        "PLAYBOOK_LEAKED_CREDENTIAL.md",
    ),
    (
        "The public n8n endpoint is under a DDoS attack causing service degradation, what is the playbook?",
        "PLAYBOOK_DDOS_SERVICE_DEGRADATION.md",
    ),
    (
        "We detected unauthorized SSH access to the droplet from an unfamiliar IP. Response steps?",
        "PLAYBOOK_UNAUTHORIZED_ACCESS.md",
    ),
    (
        "Prompt injection of the LLM agent is causing it to run disallowed actions, how do we respond?",
        "PLAYBOOK_AI_INCIDENT.md",
    ),
]


# ---------------------------------------------------------------------------
# Unit tests (no DB / no network)
# ---------------------------------------------------------------------------


def test_chunker_fixture_playbook_produces_sensible_chunks():
    from squire.ingest.chunker import chunk_document

    chunks = chunk_document(FIXTURE)
    assert len(chunks) >= 5, f"expected >=5 chunks, got {len(chunks)}"
    assert all(c.content.strip() for c in chunks), "found empty content"
    assert all(c.h1 for c in chunks), "h1 should be populated on every chunk"
    assert any(c.h2 for c in chunks), "at least some chunks should have h2"

    # doc_type inference: filename starts with nothing recognized, so falls back.
    assert chunks[0].doc_type in {"general", "playbook"}

    # citation_string preserves file + breadcrumb.
    cs = chunks[0].citation_string()
    assert cs.startswith("sample_playbook.md")
    assert "§" in cs


def test_chunker_real_playbook_produces_enough_chunks():
    from squire.ingest.chunker import chunk_document

    real = Path("/Users/et/cyber-squire-ops/docs/grc/PLAYBOOK_COMPROMISED_CONTAINER.md")
    if not real.exists():
        pytest.skip("real GRC corpus not present at expected path")
    chunks = chunk_document(real)
    assert len(chunks) >= 20, f"playbook should produce >=20 chunks, got {len(chunks)}"
    with_breadcrumb = sum(1 for c in chunks if c.h1)
    assert with_breadcrumb == len(chunks), "every chunk should have h1 populated"


def test_retriever_sql_builder_shape():
    """Verify SQL builder composes filters without DB access."""
    from squire.retrievers.grc_retriever import GRCRetriever

    r = GRCRetriever.__new__(GRCRetriever)  # skip __init__ to avoid engine build
    fake_vec = [0.1] * 1024
    sql, params = r._build_sql(
        query_vec=fake_vec,
        top_k=5,
        doc_type="playbook",
        nist_controls=["IR-4"],
        mitre_tactics=None,
    )
    rendered = str(sql)
    assert "source_kind = :doc_type" in rendered
    assert "metadata->'nist_controls' ?| :nist_controls" in rendered
    assert "mitre_tactics" not in rendered
    assert params["doc_type"] == "playbook"
    assert params["nist_controls"] == ["IR-4"]
    assert params["top_k"] == 5
    assert params["query_vec"].startswith("[")


# ---------------------------------------------------------------------------
# Integration tests (gated on RUN_INTEGRATION=1)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not RUN_INTEGRATION, reason="RUN_INTEGRATION=1 not set")
def test_retriever_returns_top1_for_each_playbook():
    from squire.retrievers.grc_retriever import GRCRetriever

    retriever = GRCRetriever()
    # Warm up: first call pays cold-start cost (voyageai import, DB pool, HTTP
    # session). Steady-state latency is what the budget tracks.
    retriever.search(query_text="warmup", top_k=1)

    failures: list[str] = []
    per_query_ms: list[int] = []

    for query, expected_file in PLAYBOOK_QUERIES:
        t0 = time.perf_counter()
        hits = retriever.search(query_text=query, top_k=5)
        dt_ms = int((time.perf_counter() - t0) * 1000)
        per_query_ms.append(dt_ms)

        assert hits, f"no hits for query: {query!r}"
        top = hits[0]
        if top.source_file != expected_file:
            top_files = [h.source_file for h in hits]
            failures.append(
                f"\n  query: {query!r}"
                f"\n  expected top-1: {expected_file}"
                f"\n  got top-5:      {top_files}"
            )

    if failures:
        pytest.fail("Playbook top-1 misses:" + "".join(failures))

    # After warmup, all 5 queries should land under the 500 ms ceiling.
    p95_like = max(per_query_ms)
    assert p95_like < 500, (
        f"max query latency {p95_like}ms exceeds 500ms budget; per-query ms = {per_query_ms}"
    )


@pytest.mark.skipif(not RUN_INTEGRATION, reason="RUN_INTEGRATION=1 not set")
def test_retriever_respects_doc_type_filter():
    from squire.retrievers.grc_retriever import GRCRetriever

    retriever = GRCRetriever()
    hits = retriever.search(
        query_text="how should we rotate leaked credentials",
        top_k=5,
        doc_type="playbook",
    )
    assert hits, "doc_type=playbook filter should still return hits"
    assert all(h.doc_type == "playbook" for h in hits), (
        "filter leaked non-playbook rows: " + str([h.doc_type for h in hits])
    )


@pytest.mark.skipif(not RUN_INTEGRATION, reason="RUN_INTEGRATION=1 not set")
def test_retriever_latency_budget():
    """Run 20 queries and assert p95 < 500ms."""
    from squire.retrievers.grc_retriever import GRCRetriever

    retriever = GRCRetriever()
    queries = [q for q, _ in PLAYBOOK_QUERIES] * 4  # 20 total
    per_query_ms: list[int] = []
    for q in queries:
        t0 = time.perf_counter()
        _ = retriever.search(query_text=q, top_k=5)
        per_query_ms.append(int((time.perf_counter() - t0) * 1000))

    per_query_ms.sort()
    # p95 index for N=20 is ~19
    p95 = per_query_ms[int(len(per_query_ms) * 0.95) - 1]
    median = statistics.median(per_query_ms)
    assert p95 < 500, (
        f"p95={p95}ms exceeds 500ms budget; median={median}ms; all={per_query_ms}"
    )
