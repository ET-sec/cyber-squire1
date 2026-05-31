"""grc_librarian agent package.

Phase 17 scaffold. Phase 20 Plan 20-05 adds the telemetry side-effect import
so any module that runs `from grc_librarian import ...` or imports a submodule
gets the agent_id Datadog tag set before the first LLM call. The MCP server
entrypoint at mcp_server/server.py also imports this package to inherit the
tag.
"""
from . import telemetry  # noqa: F401  # side-effect import sets agent_id tag

__version__ = "0.1.0"
