"""Model routing contract (SQUIRE_AI_RISK_ASSESSMENT.md AI-RISK model-downgrade).

The heavy-reasoning nodes must run on the primary model (Fable 5) and the
structured classifier on the secondary (Opus 5). Changing this map requires
an ADR; this test makes a silent change fail CI instead of shipping.
"""

import re
from pathlib import Path

from squire.settings import Settings

SRC = Path(__file__).resolve().parents[1] / "src" / "squire" / "nodes"


def _model_attr(node_file: str) -> str:
    text = (SRC / node_file).read_text()
    m = re.search(r"model\s*=\s*settings\.(claude_model_\w+)", text)
    assert m, f"{node_file}: no settings-driven model assignment found"
    return m.group(1)


def test_default_model_ids():
    s = Settings()
    assert "claude-fable-5" in s.claude_model_primary
    assert "claude-opus-5" in s.claude_model_secondary


def test_heavy_nodes_use_primary():
    for node in ("investigate.py", "draft.py", "critique.py"):
        assert _model_attr(node) == "claude_model_primary", node


def test_classify_uses_secondary():
    assert _model_attr("classify.py") == "claude_model_secondary"
