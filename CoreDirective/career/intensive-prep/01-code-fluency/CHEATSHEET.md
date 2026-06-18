# Python Cheatsheet — Cold Recall for Coding Interviews

One page. Glance, type, move on. Use during practice, not during the live interview.

---

## Variables, Types, F-strings
```python
name = "alice"
count: int = 0
ratio: float = 0.5
active: bool = True
items: list[int] = [1, 2, 3]
config: dict[str, int] = {"timeout": 30}
seen: set[str] = {"alice", "bob"}
nothing: None = None

# Type cast
n = int("42")
s = str(3.14)
xs = list("abc")  # ['a','b','c']

# F-strings
print(f"user={name} count={count} pct={ratio:.2%}")
```

## If, For, While, Comprehensions
```python
if x > 0 and y > 0:
    pass
elif x == 0:
    pass
else:
    pass

for i in range(10):
    if i == 3: continue
    if i == 7: break

# Iterate with index
for i, item in enumerate(items):
    pass

# Iterate two lists together
for a, b in zip(list_a, list_b):
    pass

# List / dict / set comprehensions
squares = [x*x for x in range(10) if x % 2 == 0]
counts = {k: len(v) for k, v in groups.items()}
unique = {x.lower() for x in words}

# Generator expression (lazy)
total = sum(x*x for x in big_list)

# Ternary
status = "ok" if score > 0.5 else "fail"
```

## Functions
```python
def greet(name: str, loud: bool = False) -> str:
    """Docstring. Default args after non-default."""
    return name.upper() if loud else name

def take_many(*args, **kwargs):
    # args = tuple, kwargs = dict
    return args, kwargs

# Lambda (one-liners only)
key_fn = lambda x: x["score"]
items.sort(key=lambda x: x.priority, reverse=True)
```

## Classes and Dataclasses
```python
class Alert:
    def __init__(self, level: str, ip: str) -> None:
        self.level = level
        self.ip = ip

    def __repr__(self) -> str:
        return f"Alert(level={self.level!r}, ip={self.ip!r})"

    def is_critical(self) -> bool:
        return self.level == "CRITICAL"

# Dataclass shortcut
from dataclasses import dataclass, field

@dataclass
class Finding:
    title: str
    severity: int = 1
    tags: list[str] = field(default_factory=list)
```

## Decorators
```python
import functools

def timed(func):
    @functools.wraps(func)   # preserves __name__ and docstring
    def wrapper(*args, **kwargs):
        # before
        result = func(*args, **kwargs)
        # after
        return result
    return wrapper

@timed
def slow(): ...

# Decorator factory (parameters)
def retry(times: int):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*a, **kw):
            for _ in range(times):
                try: return func(*a, **kw)
                except Exception: pass
            raise
        return wrapper
    return deco

@retry(times=3)
def flaky(): ...
```

## Exceptions
```python
try:
    risky()
except (ValueError, KeyError) as e:
    print(f"caught: {e}")
except Exception:
    raise
else:
    print("no exception")
finally:
    print("always runs")

# Custom exception
class PromptInjectionDetected(Exception):
    pass

raise PromptInjectionDetected("blocked")
```

## Type Hints (modern syntax)
```python
from typing import Optional, Literal, Callable, Any

def f(a: int, b: str | None = None) -> list[dict]: ...
def g(items: list[int]) -> dict[str, int]: ...
def h(level: Literal["INFO", "ERROR"]) -> bool: ...
def cb(fn: Callable[[int, int], int]) -> int: ...

# Old way (still works): Optional[X] == X | None
```

## Async / Await
```python
import asyncio

async def fetch(url: str) -> dict:
    await asyncio.sleep(1)
    return {"url": url}

async def main():
    # Run concurrently
    results = await asyncio.gather(fetch("a"), fetch("b"), fetch("c"))
    # With timeout
    async with asyncio.timeout(5):
        await fetch("slow")
    # First to finish
    done, pending = await asyncio.wait(
        [asyncio.create_task(fetch("a")), asyncio.create_task(fetch("b"))],
        return_when=asyncio.FIRST_COMPLETED,
    )

asyncio.run(main())
```

## Standard Library One-Liners

### `os`, `pathlib`
```python
import os
from pathlib import Path

os.environ.get("API_KEY", "default")
os.environ["KEY"] = "value"

p = Path("/tmp/file.log")
p.exists(); p.is_file(); p.is_dir()
p.read_text(); p.write_text("hi")
p.parent; p.name; p.stem; p.suffix
list(Path(".").glob("*.py"))           # one level
list(Path(".").rglob("*.py"))          # recursive
new = Path("/tmp") / "child.json"
```

### `json`
```python
import json
data = json.loads('{"a": 1}')          # str -> dict
text = json.dumps({"a": 1}, indent=2)  # dict -> str

with open("f.json") as f: data = json.load(f)
with open("f.json", "w") as f: json.dump(data, f, indent=2)
```

### `subprocess`
```python
import subprocess
r = subprocess.run(
    ["echo", "hello"],          # ALWAYS a list, never shell=True with input
    capture_output=True,
    text=True,
    timeout=5,
    check=False,                # True = raise on non-zero
)
print(r.stdout, r.returncode)
```

### `re` (regex)
```python
import re
re.search(r"user=(\w+)", "user=alice").group(1)   # 'alice'
re.findall(r"\b\d+\b", "a 1 b 22 c 333")          # ['1','22','333']
re.sub(r"\s+", " ", "a   b\tc")                   # 'a b c'
re.match(r"^ERROR", "ERROR boom")                 # match (start of string only)
```

### `datetime`
```python
from datetime import datetime, timedelta, timezone
now = datetime.now(timezone.utc)
parsed = datetime.fromisoformat("2026-05-08T12:00:00")
formatted = now.strftime("%Y-%m-%d %H:%M:%S")
soon = now + timedelta(minutes=15)
```

### `collections`
```python
from collections import Counter, defaultdict, deque
Counter("abracadabra").most_common(2)      # [('a', 5), ('b', 2)]
d = defaultdict(list); d["k"].append(1)    # auto-creates []
q = deque([1,2,3]); q.append(4); q.popleft()  # O(1) both ends
```

## Pydantic v2
```python
from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Literal
from datetime import datetime

class LogEntry(BaseModel):
    timestamp: datetime
    level: Literal["INFO", "WARN", "ERROR", "CRITICAL"]
    message: str = Field(max_length=500)
    user: str | None = None

    @field_validator("message")
    @classmethod
    def no_html(cls, v: str) -> str:
        if "<script" in v.lower():
            raise ValueError("no html")
        return v

try:
    e = LogEntry(timestamp="2026-05-08T12:00:00", level="ERROR", message="x")
except ValidationError as exc:
    print(exc.errors())

e.model_dump()           # -> dict
e.model_dump_json()      # -> JSON string
LogEntry.model_validate(some_dict)
```

## requests
```python
import requests

r = requests.get(url, timeout=5, headers={"Auth": "..."}, params={"k":"v"})
r.raise_for_status()
data = r.json()

requests.post(url, json={"a": 1}, timeout=5)

# Session for connection pooling
with requests.Session() as s:
    s.headers.update({"User-Agent": "x"})
    s.get(url)
```

## pytest
```python
def test_basic():
    assert 1 + 1 == 2

import pytest

@pytest.mark.parametrize("a,b,expected", [(1,2,3), (2,2,4)])
def test_add(a, b, expected):
    assert a + b == expected

def test_raises():
    with pytest.raises(ValueError):
        int("not a number")

@pytest.fixture
def sample_log():
    return {"level": "ERROR", "ip": "10.0.0.5"}

def test_with_fixture(sample_log):
    assert sample_log["level"] == "ERROR"
```

## Mocking
```python
from unittest.mock import patch, MagicMock

# Patch a function in the module under test
with patch("mymodule.requests.get") as mock_get:
    mock_get.return_value.json.return_value = {"ok": True}
    result = mymodule.fetch()

# Patch as a decorator
@patch("mymodule.requests.get")
def test_fetch(mock_get):
    mock_get.return_value.status_code = 200
```

## LangGraph (essentials)
```python
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

class State(TypedDict):
    input: dict
    verdict: Literal["auto", "escalate", ""]

def parse(state: State) -> dict:
    return {"verdict": "auto"}      # partial update

def route(state: State) -> str:
    return "notify" if state["verdict"] == "escalate" else "close"

g = StateGraph(State)
g.add_node("parse", parse)
g.add_node("notify", lambda s: {})
g.add_node("close", lambda s: {})
g.add_edge(START, "parse")
g.add_conditional_edges("parse", route, {"notify": "notify", "close": "close"})
g.add_edge("notify", END)
g.add_edge("close", END)

app = g.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["notify"],     # human-in-the-loop
)

config = {"configurable": {"thread_id": "case-001"}}
app.invoke({"input": {}, "verdict": ""}, config=config)
app.invoke(None, config=config)      # resume after interrupt
state = app.get_state(config)        # inspect current state
```

## Idioms Worth Memorizing
```python
# Swap
a, b = b, a

# Default for missing key
value = d.get("k", "fallback")
d.setdefault("k", []).append(x)

# Build a dict from two lists
dict(zip(keys, values))

# Walrus (assignment in expression, Python 3.8+)
if (n := len(data)) > 10:
    print(f"big: {n}")

# Unpacking
first, *rest = [1, 2, 3, 4]    # first=1, rest=[2,3,4]
a, b, *_ = some_list           # ignore extras

# Reverse a string / list
s[::-1]
list(reversed(items))

# Sort with multiple keys
sorted(items, key=lambda x: (x["priority"], x["name"]))

# Check if all / any
all(x > 0 for x in nums)
any(x.startswith("ERROR") for x in lines)

# Read entire file as lines (small files only)
lines = Path("f.log").read_text().splitlines()
```

## Common Pitfalls
- `is` vs `==`: use `==` for value, `is` only for `None`, `True`, `False`.
- Mutable default args: `def f(x=[])` keeps the same list across calls. Use `None` and create inside.
- `dict.keys()` returns a view, not a list. Wrap in `list()` if you need to slice.
- `range(n)` goes 0 to n-1. Off-by-one is the #1 interview bug.
- Strings are immutable. `s[0] = "x"` is an error. Build a new string.
