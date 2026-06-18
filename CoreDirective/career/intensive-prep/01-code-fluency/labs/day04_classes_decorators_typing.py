"""
Day 4 — Classes, Decorators, Type Hints
Run with: python3 day04_classes_decorators_typing.py
"""

from __future__ import annotations
from typing import Optional, Callable
import time
import functools


# ============================================================
# 1. Basic class
# ============================================================
class LogEntry:
    """A single parsed log line."""

    # __init__ runs when you create a new instance: LogEntry(...)
    def __init__(self, level: str, message: str, source: str) -> None:
        self.level = level
        self.message = message
        self.source = source

    # Regular method (takes self)
    def is_critical(self) -> bool:
        return self.level == "CRITICAL"

    # __repr__ controls what print() shows
    def __repr__(self) -> str:
        return f"LogEntry(level={self.level!r}, source={self.source!r})"


entry = LogEntry("ERROR", "auth failed", "firewall")
print(entry)
print("critical?", entry.is_critical())


# ============================================================
# 2. Inheritance
# ============================================================
class SecurityAlert(LogEntry):
    """A LogEntry that represents an actionable alert."""

    def __init__(self, level: str, message: str, source: str, ip: str) -> None:
        # super() calls the parent class constructor
        super().__init__(level, message, source)
        self.ip = ip

    def severity_score(self) -> int:
        return {"INFO": 1, "WARN": 2, "ERROR": 3, "CRITICAL": 4}.get(self.level, 0)


alert = SecurityAlert("CRITICAL", "exfil suspected", "edr", "10.0.0.5")
print("\nalert:", alert)
print("score:", alert.severity_score())
print("is alert critical?", alert.is_critical())  # inherited method


# ============================================================
# 3. @property and @staticmethod
# ============================================================
class Threshold:
    def __init__(self, score: int) -> None:
        self._score = score  # underscore = "private by convention"

    @property
    def is_high(self) -> bool:
        """Access like an attribute: t.is_high (no parentheses)."""
        return self._score >= 3

    @staticmethod
    def from_level(level: str) -> "Threshold":
        """No self. Lives on the class. Useful as a factory."""
        mapping = {"INFO": 1, "WARN": 2, "ERROR": 3, "CRITICAL": 4}
        return Threshold(mapping.get(level, 0))


t = Threshold.from_level("CRITICAL")
print("\nthreshold high?", t.is_high)


# ============================================================
# 4. Decorators
# ============================================================
# A decorator is a function that takes a function and returns a function.
# functools.wraps preserves the original function's name and docstring.

def timed(func: Callable) -> Callable:
    """Print how long the wrapped function takes."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[{func.__name__}] took {elapsed:.4f}s")
        return result
    return wrapper


@timed
def slow_lookup(ip: str) -> dict:
    """Pretend to look up an IP."""
    time.sleep(0.05)
    return {"ip": ip, "rep": "clean"}


print("\n", slow_lookup("8.8.8.8"))


# ============================================================
# 5. Decorator with state
# ============================================================
def requires_auth(token: str):
    """Decorator factory: returns a decorator parametrized by token."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            provided = kwargs.pop("auth", None)
            if provided != token:
                raise PermissionError(f"bad auth token for {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


@requires_auth("secret123")
def delete_alert(alert_id: int) -> str:
    return f"deleted alert {alert_id}"


print("\n", delete_alert(42, auth="secret123"))
try:
    delete_alert(42, auth="wrong")
except PermissionError as e:
    print("blocked:", e)


# ============================================================
# 6. Type hints in practice
# ============================================================
def find_alert(alerts: list[SecurityAlert], ip: str) -> Optional[SecurityAlert]:
    """Optional[X] is the same as X | None.
    Returns the first matching alert or None."""
    for a in alerts:
        if a.ip == ip:
            return a
    return None


pool = [
    SecurityAlert("ERROR", "scan", "ids", "10.0.0.5"),
    SecurityAlert("WARN", "slow", "edr", "10.0.0.6"),
]

found = find_alert(pool, "10.0.0.5")
print("\nfound:", found)
print("missing:", find_alert(pool, "1.2.3.4"))


# ============================================================
# 7. dataclass shortcut (modern Python idiom)
# ============================================================
from dataclasses import dataclass


@dataclass
class Finding:
    """@dataclass auto-generates __init__, __repr__, __eq__."""
    title: str
    severity: int
    closed: bool = False


f = Finding(title="prompt injection in chat endpoint", severity=4)
print("\n", f)


# ============================================================
# TRY THIS
# ============================================================
# 1. Add a method `to_dict()` on LogEntry that returns its fields as a dict.
# 2. Build a class `Triage` with a method `decide(entry)` that returns
#    "escalate" if level is CRITICAL, else "auto".
# 3. Write a decorator `@retry(times=3)` that retries on Exception.
# 4. Add another @dataclass `Tool` with name, description, fn (Callable).
# 5. Override __eq__ on LogEntry so two entries match on level + message.
