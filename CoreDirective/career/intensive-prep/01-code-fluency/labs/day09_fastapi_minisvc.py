"""
Day 9 — FastAPI Mini Triage Service
Setup: pip install fastapi uvicorn
Run with:
    uvicorn day09_fastapi_minisvc:app --reload --port 8088
Then test:
    curl http://localhost:8088/health
    curl -X POST http://localhost:8088/triage \
         -H "Content-Type: application/json" \
         -d '{"timestamp":"2026-05-08T12:00:00","level":"CRITICAL","message":"exfil","source_ip":"10.0.0.5"}'
    curl http://localhost:8088/lookup/8.8.8.8

You can also just run `python3 day09_fastapi_minisvc.py` to launch the
server directly (the bottom of this file does that).
"""

from datetime import datetime
from typing import Literal

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
except ImportError:
    print("pip install fastapi uvicorn pydantic")
    raise SystemExit(1)


# ============================================================
# Request / Response models
# ============================================================
class LogEntry(BaseModel):
    timestamp: datetime
    level: Literal["INFO", "WARN", "ERROR", "CRITICAL"]
    message: str = Field(..., max_length=500)
    source_ip: str


class TriageDecision(BaseModel):
    verdict: Literal["auto", "escalate"]
    reasoning: str
    severity_score: int


class IPLookupResult(BaseModel):
    ip: str
    reputation: Literal["clean", "suspicious", "malicious"]
    confidence: float


# ============================================================
# Mock threat intel (would call an external API in production)
# ============================================================
def lookup_ip_mock(ip: str) -> IPLookupResult:
    if ip.startswith("10."):
        return IPLookupResult(ip=ip, reputation="clean", confidence=0.95)
    if ip.startswith("8."):
        return IPLookupResult(ip=ip, reputation="suspicious", confidence=0.7)
    return IPLookupResult(ip=ip, reputation="malicious", confidence=0.85)


# ============================================================
# Triage logic
# ============================================================
SEVERITY = {"INFO": 1, "WARN": 2, "ERROR": 3, "CRITICAL": 4}


def triage(entry: LogEntry) -> TriageDecision:
    """Decide if a log entry should escalate to a human or auto-respond."""
    score = SEVERITY[entry.level]
    intel = lookup_ip_mock(entry.source_ip)

    # Escalate on high severity OR malicious IP
    if score >= 4 or intel.reputation == "malicious":
        return TriageDecision(
            verdict="escalate",
            reasoning=f"level={entry.level} ip_rep={intel.reputation}",
            severity_score=score,
        )
    return TriageDecision(
        verdict="auto",
        reasoning=f"level={entry.level} ip_rep={intel.reputation}",
        severity_score=score,
    )


# ============================================================
# FastAPI app
# ============================================================
app = FastAPI(
    title="Triage Service",
    description="Mini SOC triage API",
    version="0.1.0",
)


@app.get("/health")
def health():
    """Liveness probe."""
    return {"status": "ok"}


@app.post("/triage", response_model=TriageDecision)
def triage_endpoint(entry: LogEntry):
    """Take a log entry, return a triage decision.
    FastAPI auto-validates the body against LogEntry."""
    return triage(entry)


@app.get("/lookup/{ip}", response_model=IPLookupResult)
def lookup_endpoint(ip: str):
    """Return mock threat intel for an IP."""
    if ip.count(".") != 3:
        raise HTTPException(status_code=400, detail=f"bad ip: {ip}")
    return lookup_ip_mock(ip)


@app.get("/")
def root():
    return {
        "service": "triage",
        "endpoints": ["/health", "POST /triage", "/lookup/{ip}", "/docs"],
    }


# ============================================================
# Run directly: python3 day09_fastapi_minisvc.py
# ============================================================
if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=8088)
    except ImportError:
        print("pip install uvicorn")


# ============================================================
# TRY THIS
# ============================================================
# 1. Add a POST /bulk-triage endpoint that takes a list of LogEntry.
# 2. Add an X-API-Key header check using FastAPI's Depends.
# 3. Write a test using the TestClient (from fastapi.testclient).
# 4. Add a query param /lookup/{ip}?verbose=true that returns more fields.
# 5. Replace lookup_ip_mock with a call to your day08 safe_get function.
