"""Drift observers for verify-facts.py.

Each observer module exports a single `OBSERVER` instance (concrete subclass of
`base.Observer`) and is auto-discovered by `verify-facts.py` via this package.

Adding a new observer:
  1. Create `observers/<name>.py` exporting `OBSERVER = MyObserver()`.
  2. Add the module name to `_REGISTRY` below in the order it should execute.
  3. No edits to `verify-facts.py` required.
"""
from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Observer

# Execution order: filesystem observers first (fast, local), remote last.
_REGISTRY: list[str] = [
    "grc_docs",
    "terraform",
    "opa",
    "ir_playbooks",
    "agents",
    "containers",   # remote (ssh)
    "workflows",    # remote (ssh + psql)
]

_REMOTE: set[str] = {"containers", "workflows"}


def load_all(include_remote: bool = True) -> list["Observer"]:
    """Return all registered observers, in declared order.

    When include_remote=False, remote observers are skipped (used by
    --skip-remote flag).
    """
    out: list[Observer] = []
    for name in _REGISTRY:
        if not include_remote and name in _REMOTE:
            continue
        mod = import_module(f".{name}", package=__name__)
        out.append(mod.OBSERVER)
    return out
