"""Observer ABC + Drift + Context.

An Observer reads one (or sometimes two) fields from stack-facts.yaml,
observes the corresponding reality, and emits zero or more Drift objects.

Drift means: yaml says X, reality says Y, X != Y.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Drift:
    key: str       # dotted path into stack-facts (e.g. "infrastructure.containers_running")
    yaml: Any      # value declared in stack-facts.yaml
    real: Any      # value observed in reality

    def as_dict(self) -> dict:
        return {"key": self.key, "yaml": self.yaml, "real": self.real}


@dataclass
class Context:
    """Shared state passed to every observer.

    base_dir       : repo root (absolute, resolved)
    facts          : parsed stack-facts.yaml as dict
    ssh_target     : regex-validated ssh target name (e.g. "cd-alpha")
    skip_remote    : when True, remote observers must early-return []
    """
    base_dir: Path
    facts: dict
    ssh_target: str
    skip_remote: bool = False


class Observer(ABC):
    """Base class. Subclasses set `name` and implement `observe`."""

    name: str = ""           # human-readable, e.g. "grc_docs"
    is_remote: bool = False  # True if observer needs ssh / postgres

    @abstractmethod
    def observe(self, ctx: Context) -> list[Drift]:
        """Run the observation, compare to yaml, return drift list (may be empty).

        Observers must:
          - exit cleanly on empty results (return [])
          - call sys.exit(N) on hard failures matching the exit-code contract:
              2 input/schema, 3 external (ssh/pg), 4 secret retrieval, 6 policy
          - never raise unhandled exceptions if avoidable
        """
        raise NotImplementedError
