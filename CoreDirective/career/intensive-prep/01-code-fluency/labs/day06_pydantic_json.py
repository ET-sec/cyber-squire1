"""
Day 6 — Pydantic Models and JSON
Setup: pip install "pydantic>=2.0"
Run with: python3 day06_pydantic_json.py

Pydantic gives you validated dataclasses with great error messages.
Every modern AI security stack uses pydantic for tool inputs/outputs.
"""

import json
from datetime import datetime
from typing import Literal

try:
    from pydantic import BaseModel, Field, ValidationError, field_validator
except ImportError:
    print("pip install 'pydantic>=2.0'")
    raise SystemExit(1)


# ============================================================
# 1. Basic model
# ============================================================
class LogEntry(BaseModel):
    timestamp: datetime
    level: Literal["INFO", "WARN", "ERROR", "CRITICAL"]
    message: str = Field(..., max_length=500)
    source_ip: str

    # Custom validator (runs after type coercion)
    @field_validator("source_ip")
    @classmethod
    def must_be_ipv4(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) != 4 or not all(p.isdigit() for p in parts):
            raise ValueError(f"not a valid IPv4: {v}")
        return v


# ============================================================
# 2. Parsing a raw dict
# ============================================================
raw_good = {
    "timestamp": "2026-05-08T12:00:00",
    "level": "ERROR",
    "message": "auth failed",
    "source_ip": "10.0.0.5",
}

entry = LogEntry(**raw_good)
print("parsed:", entry)
print("type of timestamp:", type(entry.timestamp))  # datetime, not str


# ============================================================
# 3. Validation errors
# ============================================================
raw_bad = {
    "timestamp": "not-a-date",
    "level": "DEBUG",        # not in Literal
    "message": "x" * 600,    # too long
    "source_ip": "10.0.0",   # incomplete IP
}

try:
    LogEntry(**raw_bad)
except ValidationError as e:
    print("\nvalidation errors:")
    for err in e.errors():
        print(f"  {err['loc']}: {err['msg']}")


# ============================================================
# 4. Serialization
# ============================================================
print("\nas dict:", entry.model_dump())
print("as JSON:", entry.model_dump_json())


# ============================================================
# 5. Nested model
# ============================================================
class Alert(BaseModel):
    alert_id: str
    verdict: Literal["auto", "escalate", "ignore"]
    entries: list[LogEntry]
    notes: str | None = None  # optional


payload = {
    "alert_id": "ALR-001",
    "verdict": "escalate",
    "entries": [
        {
            "timestamp": "2026-05-08T12:00:00",
            "level": "CRITICAL",
            "message": "exfil suspected",
            "source_ip": "10.0.0.5",
        },
        {
            "timestamp": "2026-05-08T12:01:00",
            "level": "ERROR",
            "message": "auth fail",
            "source_ip": "10.0.0.5",
        },
    ],
}

alert = Alert(**payload)
print("\nalert:", alert.alert_id, "verdict:", alert.verdict)
print("entry count:", len(alert.entries))


# ============================================================
# 6. Loading from JSON file
# ============================================================
# Write to disk first
with open("/tmp/alert.json", "w") as f:
    f.write(alert.model_dump_json(indent=2))

# Read back and validate
with open("/tmp/alert.json") as f:
    data = json.load(f)

reloaded = Alert(**data)
print("\nreloaded id:", reloaded.alert_id)


# ============================================================
# 7. Models for tool inputs/outputs (preview of LangGraph tools)
# ============================================================
class IPLookupInput(BaseModel):
    ip: str = Field(..., description="IPv4 address to look up")


class IPLookupOutput(BaseModel):
    ip: str
    reputation: Literal["clean", "suspicious", "malicious"]
    confidence: float = Field(ge=0.0, le=1.0)  # ge = greater or equal


def lookup_ip(req: IPLookupInput) -> IPLookupOutput:
    """A tool function with validated input and output.
    LLMs will call this and pydantic will reject malformed args."""
    # Mock logic: 10.x is clean, 8.x is suspicious, anything else malicious
    if req.ip.startswith("10."):
        return IPLookupOutput(ip=req.ip, reputation="clean", confidence=0.95)
    if req.ip.startswith("8."):
        return IPLookupOutput(ip=req.ip, reputation="suspicious", confidence=0.7)
    return IPLookupOutput(ip=req.ip, reputation="malicious", confidence=0.85)


print("\ntool result:", lookup_ip(IPLookupInput(ip="8.8.8.8")))


# ============================================================
# TRY THIS
# ============================================================
# 1. Add a `user: str | None` field to LogEntry, optional.
# 2. Add a validator that converts level to uppercase before validating.
# 3. Add a TriageDecision model with fields: verdict, reasoning, confidence.
# 4. Make IPLookupOutput include a list of `tags: list[str]`.
# 5. Write a function that takes raw JSON text, parses to Alert,
#    and returns a count of CRITICAL entries.
