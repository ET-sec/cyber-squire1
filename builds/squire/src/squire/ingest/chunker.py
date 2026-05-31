"""Header-aware markdown chunker for the GRC corpus.

Produces list[GRCChunk] from a .md file.

Design:
  - Parse markdown headers (h1 / h2 / h3) while streaming the file once.
  - Accumulate body text under the current h1/h2/h3 breadcrumb.
  - When a chunk reaches ~600 tokens, emit it and keep the header breadcrumb
    intact for the next chunk (so every chunk retains provenance).
  - If a single section is larger than the target, split inside the section on
    paragraph boundaries, then on sentences, then on hard character windows
    (RecursiveCharacterTextSplitter fallback semantics).
  - Extract document-level metadata from the first header block: Document ID,
    Version, NIST 800-53 Controls, OWASP LLM Top 10, MITRE ATLAS, Classification.
  - Infer doc_type from filename prefix (PLAYBOOK_, POLICY_, THREAT_MODEL_, etc.).

No external LLM / tiktoken dependency. Token count is approximated as
len(text.split()) * 1.3 which is close enough for chunk-size budgeting.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

# Target chunk budget in approximate tokens.
CHUNK_TARGET_TOKENS = 220
CHUNK_MAX_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 60

# Doc-type inference: filename prefix -> canonical type.
DOC_TYPE_PREFIX = [
    ("PLAYBOOK_", "playbook"),
    ("POLICY_", "policy"),
    ("THREAT_MODEL_", "threat_model"),
    ("ATTACK_TREE_", "threat_model"),
    ("AI_THREAT_CATALOG", "threat_model"),
    ("AI_SUPPLY_CHAIN_RISK", "threat_model"),
    ("AI_RED_TEAM_PLAN", "threat_model"),
    ("RISK_ASSESSMENT", "risk"),
    ("CIS_RISK_REGISTER", "risk"),
    ("POAM_", "risk"),
    ("SSP_", "compliance"),
    ("IAM_", "iam"),
    ("GOOGLE_CLOUD_IAM", "iam"),
    ("EXECUTIVE_SUMMARY_", "executive"),
    ("SECURE_SDLC", "appsec"),
    ("CODE_REVIEW_", "appsec"),
    ("DAST_", "appsec"),
    ("PENTEST_", "appsec"),
    ("VULN_WRITEUP_", "appsec"),
    ("DATA_FLOW_DIAGRAM", "architecture"),
    ("TABLETOP_", "exercise"),
    ("ADR_", "adr"),
]


@dataclass
class GRCChunk:
    """A single chunk ready to be embedded and inserted into ir_chunks."""

    source_file: str                # e.g. "PLAYBOOK_COMPROMISED_CONTAINER.md"
    source_path: str                # absolute or relative path as provided
    doc_type: str                   # playbook | policy | threat_model | risk | ...
    chunk_index: int                # 0-based ordinal within the document
    content: str                    # chunk text (header breadcrumb + body)
    content_hash: str               # sha256 of content (for dedup)
    token_count: int                # approximate token count (whitespace * 1.3)
    h1: str | None = None
    h2: str | None = None
    h3: str | None = None
    metadata: dict = field(default_factory=dict)

    def citation_string(self) -> str:
        """Return 'FILENAME §h1 > h2 > h3' with whichever headers are populated."""
        parts = [p for p in (self.h1, self.h2, self.h3) if p]
        if not parts:
            return self.source_file
        return f"{self.source_file} §{' > '.join(parts)}"


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------


def chunk_document(path: str | Path) -> list[GRCChunk]:
    """Chunk a single markdown file. Returns [] if the file is empty or unreadable."""
    p = Path(path)
    if not p.exists() or not p.is_file():
        return []
    raw = p.read_text(encoding="utf-8", errors="replace")
    if not raw.strip():
        return []

    source_file = p.name
    source_path = str(p)
    doc_type = _infer_doc_type(source_file)
    doc_metadata = _parse_metadata(raw)

    return list(
        _iter_chunks(
            raw=raw,
            source_file=source_file,
            source_path=source_path,
            doc_type=doc_type,
            doc_metadata=doc_metadata,
        )
    )


# ---------------------------------------------------------------------------
# Metadata / type inference
# ---------------------------------------------------------------------------


def _infer_doc_type(filename: str) -> str:
    upper = filename.upper()
    for prefix, dtype in DOC_TYPE_PREFIX:
        if upper.startswith(prefix):
            return dtype
    return "general"


_NIST_RX = re.compile(r"\b([A-Z]{2}-\d{1,2}(?:\(\d+\))?)\b")
_ATLAS_RX = re.compile(r"\bAML\.T\d{4}\b")
_LLM_RX = re.compile(r"\bLLM\d{2}\b")
_DOC_ID_RX = re.compile(r"\*\*Document ID:\*\*\s*([^\n]+)", re.IGNORECASE)
_VERSION_RX = re.compile(r"\*\*Version:\*\*\s*([^\n]+)", re.IGNORECASE)
_CLASSIFICATION_RX = re.compile(r"\*\*Classification:\*\*\s*([^\n]+)", re.IGNORECASE)
_OWNER_RX = re.compile(r"\*\*Owner:\*\*\s*([^\n]+)", re.IGNORECASE)


def _parse_metadata(raw: str) -> dict:
    """Extract document-level metadata from the first ~3000 chars.

    GRC docs follow a consistent header pattern with **Document ID:**, **Version:**,
    NIST 800-53 Controls, OWASP LLM, and MITRE ATLAS lines.
    """
    head = raw[:3000]
    md: dict = {}

    m = _DOC_ID_RX.search(head)
    if m:
        md["document_id"] = m.group(1).strip()
    m = _VERSION_RX.search(head)
    if m:
        md["version"] = m.group(1).strip()
    m = _CLASSIFICATION_RX.search(head)
    if m:
        md["classification"] = m.group(1).strip()
    m = _OWNER_RX.search(head)
    if m:
        md["owner"] = m.group(1).strip()

    nist_hits = sorted(set(_NIST_RX.findall(head)))
    if nist_hits:
        md["nist_controls"] = nist_hits

    atlas_hits = sorted(set(_ATLAS_RX.findall(head)))
    if atlas_hits:
        md["mitre_atlas"] = atlas_hits

    llm_hits = sorted(set(_LLM_RX.findall(head)))
    if llm_hits:
        md["owasp_llm"] = llm_hits

    return md


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------


_HEADER_RX = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def _approx_tokens(text: str) -> int:
    """Rough token estimate: word count * 1.3. Good enough for chunk budgeting."""
    wc = len(text.split())
    return int(wc * 1.3) + 1


def _iter_chunks(
    *,
    raw: str,
    source_file: str,
    source_path: str,
    doc_type: str,
    doc_metadata: dict,
) -> Iterator[GRCChunk]:
    lines = raw.splitlines()
    h1: str | None = None
    h2: str | None = None
    h3: str | None = None

    buffer: list[str] = []
    buffer_tokens = 0
    chunk_idx = 0

    def _flush(force: bool = False) -> Iterator[GRCChunk]:
        nonlocal buffer, buffer_tokens, chunk_idx
        if not buffer:
            return
        body = "\n".join(buffer).strip()
        if not body:
            buffer = []
            buffer_tokens = 0
            return

        breadcrumb = " > ".join([h for h in (h1, h2, h3) if h])
        content = f"[{breadcrumb}]\n\n{body}" if breadcrumb else body

        # If a single section blew past CHUNK_MAX_TOKENS even after header emission,
        # fall back to paragraph / sentence splitting to keep chunks under the cap.
        tokens = _approx_tokens(content)
        if tokens > CHUNK_MAX_TOKENS and not force:
            for sub in _recursive_split(body, CHUNK_TARGET_TOKENS):
                sub_content = (
                    f"[{breadcrumb}]\n\n{sub}" if breadcrumb else sub
                )
                yield _make_chunk(
                    sub_content,
                    source_file=source_file,
                    source_path=source_path,
                    doc_type=doc_type,
                    chunk_index=chunk_idx,
                    h1=h1,
                    h2=h2,
                    h3=h3,
                    doc_metadata=doc_metadata,
                )
                chunk_idx += 1
        else:
            yield _make_chunk(
                content,
                source_file=source_file,
                source_path=source_path,
                doc_type=doc_type,
                chunk_index=chunk_idx,
                h1=h1,
                h2=h2,
                h3=h3,
                doc_metadata=doc_metadata,
            )
            chunk_idx += 1

        buffer = []
        buffer_tokens = 0

    for line in lines:
        m = _HEADER_RX.match(line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            # Header encountered. Flush current buffer first so this header's
            # content becomes a fresh chunk. Every h1/h2 boundary flushes
            # unconditionally so short sections keep their own citation.
            # h3 boundaries flush only if the buffer has real body content.
            if level <= 3 and buffer_tokens > 0:
                yield from _flush()
            if level == 1:
                h1 = title
                h2 = None
                h3 = None
            elif level == 2:
                h2 = title
                h3 = None
            elif level == 3:
                h3 = title
            # h4+ headers are treated as body text to keep the breadcrumb shallow.
            else:
                buffer.append(line)
                buffer_tokens += _approx_tokens(line)
            continue

        buffer.append(line)
        buffer_tokens += _approx_tokens(line)

        if buffer_tokens >= CHUNK_TARGET_TOKENS:
            yield from _flush()

    # Final flush.
    yield from _flush(force=True)


def _recursive_split(text: str, target_tokens: int) -> list[str]:
    """Fall back when a section body exceeds CHUNK_MAX_TOKENS.

    Order of attempts:
      1. Split on blank-line paragraph boundaries.
      2. If a single paragraph is still too big, split on sentence boundaries.
      3. If a single sentence is still too big, hard-window by characters.
    """
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    out: list[str] = []
    current: list[str] = []
    current_tokens = 0

    for para in paras:
        para_tokens = _approx_tokens(para)
        if para_tokens > target_tokens:
            # Oversized paragraph: flush accumulated, then sentence-split this one.
            if current:
                out.append("\n\n".join(current))
                current = []
                current_tokens = 0
            out.extend(_sentence_split(para, target_tokens))
            continue

        if current_tokens + para_tokens > target_tokens and current:
            out.append("\n\n".join(current))
            current = []
            current_tokens = 0

        current.append(para)
        current_tokens += para_tokens

    if current:
        out.append("\n\n".join(current))

    return out


_SENT_RX = re.compile(r"(?<=[.!?])\s+")


def _sentence_split(text: str, target_tokens: int) -> list[str]:
    sents = _SENT_RX.split(text)
    out: list[str] = []
    current: list[str] = []
    current_tokens = 0
    for s in sents:
        s_tokens = _approx_tokens(s)
        if s_tokens > target_tokens:
            # Still too big. Hard-window this sentence by characters.
            if current:
                out.append(" ".join(current))
                current = []
                current_tokens = 0
            out.extend(_hard_window(s, target_tokens))
            continue
        if current_tokens + s_tokens > target_tokens and current:
            out.append(" ".join(current))
            current = []
            current_tokens = 0
        current.append(s)
        current_tokens += s_tokens
    if current:
        out.append(" ".join(current))
    return out


def _hard_window(text: str, target_tokens: int) -> list[str]:
    """Last-resort fixed character window."""
    # Rough: 1 token ~= 4 chars for English. Target_tokens chunks.
    chars = target_tokens * 4
    return [text[i : i + chars] for i in range(0, len(text), chars)]


def _make_chunk(
    content: str,
    *,
    source_file: str,
    source_path: str,
    doc_type: str,
    chunk_index: int,
    h1: str | None,
    h2: str | None,
    h3: str | None,
    doc_metadata: dict,
) -> GRCChunk:
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return GRCChunk(
        source_file=source_file,
        source_path=source_path,
        doc_type=doc_type,
        chunk_index=chunk_index,
        content=content,
        content_hash=content_hash,
        token_count=_approx_tokens(content),
        h1=h1,
        h2=h2,
        h3=h3,
        metadata=dict(doc_metadata),  # shallow copy; same doc-level md on every chunk
    )
