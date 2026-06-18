"""
Day 13 — LangGraph: Tool Use, Persistence, Human-in-the-Loop
Setup: pip install "langgraph>=0.2"
Run with: python3 day13_langgraph_tools_persistence.py

Concepts:
- Define mock tools the agent can call
- Use a checkpointer (MemorySaver) so state persists between runs
- interrupt_before to pause for human approval
- Resume from a saved state
"""

from typing import TypedDict, Literal

try:
    from langgraph.graph import StateGraph, START, END
    from langgraph.checkpoint.memory import MemorySaver
except ImportError:
    print("pip install 'langgraph>=0.2'")
    raise SystemExit(1)


# ============================================================
# 1. Mock tools (real ones would call APIs)
# ============================================================
def lookup_ip_reputation(ip: str) -> dict:
    """Tool: return mock reputation for an IP."""
    if ip.startswith("203.") or ip.startswith("198."):
        return {"ip": ip, "reputation": "malicious", "confidence": 0.9}
    if ip.startswith("8."):
        return {"ip": ip, "reputation": "suspicious", "confidence": 0.6}
    return {"ip": ip, "reputation": "clean", "confidence": 0.95}


def get_user_history(user: str) -> dict:
    """Tool: return mock user activity history."""
    bad_users = {"root", "admin"}
    return {
        "user": user,
        "failed_logins_24h": 12 if user in bad_users else 0,
        "is_privileged": user in bad_users,
    }


TOOLS = {
    "lookup_ip_reputation": lookup_ip_reputation,
    "get_user_history": get_user_history,
}


# ============================================================
# 2. State
# ============================================================
class State(TypedDict):
    log_entry: dict
    tool_calls: list
    tool_results: list
    verdict: Literal["auto", "escalate", ""]
    reasoning: str
    human_approved: bool


# ============================================================
# 3. Nodes
# ============================================================
def plan_tools(state: State) -> dict:
    """Decide which tools to call based on the log entry."""
    entry = state["log_entry"]
    calls = []
    if entry.get("source_ip"):
        calls.append({"tool": "lookup_ip_reputation", "args": {"ip": entry["source_ip"]}})
    if entry.get("user"):
        calls.append({"tool": "get_user_history", "args": {"user": entry["user"]}})
    print(f"[plan]    {len(calls)} tool calls planned")
    return {"tool_calls": calls}


def execute_tools(state: State) -> dict:
    """Run each planned tool. In real LangGraph use ToolNode for this."""
    results = []
    for call in state["tool_calls"]:
        fn = TOOLS[call["tool"]]
        result = fn(**call["args"])
        results.append({"tool": call["tool"], "result": result})
        print(f"[tool]    {call['tool']} -> {result}")
    return {"tool_results": results}


def decide(state: State) -> dict:
    """Combine tool results to a verdict."""
    rep = "clean"
    privileged = False
    for r in state["tool_results"]:
        if r["tool"] == "lookup_ip_reputation":
            rep = r["result"]["reputation"]
        elif r["tool"] == "get_user_history":
            privileged = r["result"]["is_privileged"]

    level = state["log_entry"].get("level", "INFO")
    if rep == "malicious" or (privileged and level in ("ERROR", "CRITICAL")):
        verdict = "escalate"
    else:
        verdict = "auto"
    reasoning = f"level={level} rep={rep} privileged={privileged}"
    print(f"[decide]  verdict={verdict}")
    return {"verdict": verdict, "reasoning": reasoning}


def notify(state: State) -> dict:
    """Side-effect node. Should require human approval first."""
    print(f"[notify]  paging on-call: {state['reasoning']}")
    return {}


def auto_close(state: State) -> dict:
    print(f"[close]   auto-closed: {state['reasoning']}")
    return {}


def route(state: State) -> str:
    return "notify" if state["verdict"] == "escalate" else "auto_close"


# ============================================================
# 4. Build with checkpointer + interrupt_before
# ============================================================
graph = StateGraph(State)
graph.add_node("plan_tools", plan_tools)
graph.add_node("execute_tools", execute_tools)
graph.add_node("decide", decide)
graph.add_node("notify", notify)
graph.add_node("auto_close", auto_close)

graph.add_edge(START, "plan_tools")
graph.add_edge("plan_tools", "execute_tools")
graph.add_edge("execute_tools", "decide")
graph.add_conditional_edges("decide", route, {"notify": "notify", "auto_close": "auto_close"})
graph.add_edge("notify", END)
graph.add_edge("auto_close", END)

# MemorySaver keeps state in process memory across invocations.
# Production would use SqliteSaver or Postgres.
checkpointer = MemorySaver()

# interrupt_before pauses the graph so a human can approve before notify.
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["notify"],
)


# ============================================================
# 5. Run with thread_id for persistence
# ============================================================
def run_with_approval(thread_id: str, log_entry: dict, approve: bool):
    config = {"configurable": {"thread_id": thread_id}}
    initial: State = {
        "log_entry": log_entry,
        "tool_calls": [],
        "tool_results": [],
        "verdict": "",
        "reasoning": "",
        "human_approved": False,
    }

    print(f"\n=== thread {thread_id} (approve={approve}) ===")
    # First invoke runs until the interrupt
    state = app.invoke(initial, config=config)

    # If we hit the interrupt, the graph paused before `notify`
    snapshot = app.get_state(config)
    if "notify" in snapshot.next:
        print(f"[pause]   waiting for human approval. next={snapshot.next}")
        if approve:
            # Resume by invoking with None (continues from checkpoint)
            print("[human]   APPROVED -> resuming")
            app.invoke(None, config=config)
        else:
            print("[human]   DENIED -> not resuming")
    else:
        print(f"[done]    no interrupt, ended at: {snapshot.next}")


if __name__ == "__main__":
    # Case 1: malicious IP, human approves
    run_with_approval("t-001", {
        "level": "CRITICAL",
        "source_ip": "203.0.113.5",
        "user": "root",
        "message": "auth fail",
    }, approve=True)

    # Case 2: clean IP, no escalation needed (no interrupt)
    run_with_approval("t-002", {
        "level": "INFO",
        "source_ip": "10.0.0.5",
        "user": "alice",
        "message": "login ok",
    }, approve=False)

    # Case 3: malicious but human denies the page
    run_with_approval("t-003", {
        "level": "CRITICAL",
        "source_ip": "198.51.100.7",
        "user": "admin",
        "message": "exfil",
    }, approve=False)


# ============================================================
# TRY THIS
# ============================================================
# 1. Replace MemorySaver with SqliteSaver:
#    from langgraph.checkpoint.sqlite import SqliteSaver
#    cp = SqliteSaver.from_conn_string("/tmp/triage.db")
# 2. Add a 3rd tool `query_siem(query: str)` and call it for ERROR level.
# 3. After resume, inspect state with app.get_state(config).values
# 4. Add interrupt_after=["execute_tools"] so human can review tool outputs.
# 5. Walk the state history with app.get_state_history(config).
