"""
Day 12 — LangGraph State Machines
Setup: pip install "langgraph>=0.2"
Run with: python3 day12_langgraph_state.py

LangGraph wraps your nodes (functions) into a state machine. Each node
takes the state, returns updates to the state. Edges define what runs next.
Conditional edges let you route based on state.
"""

from typing import TypedDict, Literal

try:
    from langgraph.graph import StateGraph, START, END
except ImportError:
    print("pip install 'langgraph>=0.2'")
    raise SystemExit(1)


# ============================================================
# 1. State schema
# ============================================================
# TypedDict tells LangGraph what keys live in state.
class TriageState(TypedDict):
    log_entry: dict
    parsed: dict
    enriched: dict
    verdict: Literal["auto", "escalate", ""]
    reasoning: str


# ============================================================
# 2. Nodes (each is a plain function)
# ============================================================
# Each node receives the full state and returns a partial update.
def parse_node(state: TriageState) -> dict:
    """Parse the raw log_entry dict into normalized fields."""
    raw = state["log_entry"]
    parsed = {
        "level": raw.get("level", "UNKNOWN").upper(),
        "ip": raw.get("source_ip", ""),
        "message": raw.get("message", ""),
    }
    print(f"[parse]   {parsed}")
    return {"parsed": parsed}


def enrich_node(state: TriageState) -> dict:
    """Mock enrichment: look up IP reputation."""
    ip = state["parsed"]["ip"]
    rep = "clean"
    if ip.startswith("203.") or ip.startswith("198."):
        rep = "malicious"
    elif ip.startswith("8."):
        rep = "suspicious"
    enriched = {"ip_reputation": rep}
    print(f"[enrich]  ip={ip} -> {rep}")
    return {"enriched": enriched}


def decide_node(state: TriageState) -> dict:
    """Pick auto vs escalate based on level and reputation."""
    level = state["parsed"]["level"]
    rep = state["enriched"]["ip_reputation"]

    if level == "CRITICAL" or rep == "malicious":
        verdict = "escalate"
        reason = f"level={level} ip_rep={rep}"
    else:
        verdict = "auto"
        reason = f"level={level} ip_rep={rep}"

    print(f"[decide]  verdict={verdict} ({reason})")
    return {"verdict": verdict, "reasoning": reason}


def notify_node(state: TriageState) -> dict:
    """Pretend to page a human."""
    print(f"[notify]  paging on-call: {state['reasoning']}")
    return {}


def auto_close_node(state: TriageState) -> dict:
    """Auto-close low risk alerts."""
    print(f"[close]   auto-closed: {state['reasoning']}")
    return {}


# ============================================================
# 3. Conditional routing
# ============================================================
def route_after_decide(state: TriageState) -> str:
    """Return the name of the next node based on verdict."""
    return "notify" if state["verdict"] == "escalate" else "auto_close"


# ============================================================
# 4. Build the graph
# ============================================================
graph = StateGraph(TriageState)

# Register nodes
graph.add_node("parse", parse_node)
graph.add_node("enrich", enrich_node)
graph.add_node("decide", decide_node)
graph.add_node("notify", notify_node)
graph.add_node("auto_close", auto_close_node)

# Wire edges
graph.add_edge(START, "parse")
graph.add_edge("parse", "enrich")
graph.add_edge("enrich", "decide")

# Conditional edge: decide where to go after `decide`
graph.add_conditional_edges(
    "decide",
    route_after_decide,
    {
        "notify": "notify",
        "auto_close": "auto_close",
    },
)

graph.add_edge("notify", END)
graph.add_edge("auto_close", END)

# Compile into a runnable
app = graph.compile()


# ============================================================
# 5. Run it
# ============================================================
def run_one(label: str, log_entry: dict):
    print(f"\n=== {label} ===")
    initial: TriageState = {
        "log_entry": log_entry,
        "parsed": {},
        "enriched": {},
        "verdict": "",
        "reasoning": "",
    }
    final = app.invoke(initial)
    print(f"[final]   verdict={final['verdict']} reason={final['reasoning']}")
    return final


if __name__ == "__main__":
    run_one("benign internal info", {
        "level": "INFO",
        "source_ip": "10.0.0.5",
        "message": "user login success",
    })

    run_one("critical with malicious IP", {
        "level": "CRITICAL",
        "source_ip": "203.0.113.5",
        "message": "exfil attempt detected",
    })

    run_one("warn with suspicious IP", {
        "level": "WARN",
        "source_ip": "8.8.4.4",
        "message": "outbound DNS to public resolver",
    })


# ============================================================
# TRY THIS
# ============================================================
# 1. Add a `correlate` node between enrich and decide that flags
#    repeat offenders (count of recent entries from same IP).
# 2. Add a 3rd terminal node `quarantine` and route to it when
#    rep == "malicious" AND level == "CRITICAL".
# 3. Print the graph as ASCII: print(app.get_graph().draw_ascii())
# 4. Convert TriageState to a pydantic BaseModel (LangGraph supports both).
# 5. Add a `retries` field to state and increment it in enrich on errors.
