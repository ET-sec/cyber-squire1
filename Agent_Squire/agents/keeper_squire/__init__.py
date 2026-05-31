"""keeper_squire agent package.

Phase 17 scaffold. Phase 20 Plan 20-05 adds the telemetry side-effect import
so any module that runs `from keeper_squire import ...` or imports a submodule
gets the agent_id Datadog tag set before the first LLM call.
"""
from . import telemetry  # noqa: F401  # side-effect import sets agent_id tag

__version__ = "0.1.0"
