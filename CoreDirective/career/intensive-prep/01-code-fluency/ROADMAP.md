# Code Fluency Roadmap — Zero to LangGraph Security Agent in 14 Days

You have 6 weeks before $200K AI Security code interviews. This roadmap gets you to writing LangGraph agents in 14 days. Each day is a 90 minute block. No filler. Every exercise produces working code.

## Operating Rules
- Run every lab file before reading the next one. `python3 labs/day01_variables_to_functions.py` and watch what happens.
- If you finish a day in 60 minutes, do the TRY THIS challenges at the bottom of each lab file.
- If you stall for more than 15 minutes on one concept, skip it and come back. Momentum beats completeness.
- You learn by typing, not reading. Retype the lab into a fresh file from memory at the end of each day.
- Use Python 3.14 at `/opt/homebrew/bin/python3`. Make a venv on day 6 when we install packages.

## Setup (Do This Before Day 1, 10 minutes)
```bash
cd /Users/et/cyber-squire-ops/CoreDirective/career/intensive-prep/01-code-fluency
/opt/homebrew/bin/python3 -m venv .venv
source .venv/bin/activate
python3 --version    # confirm 3.14
```

You will install packages on Day 6. Days 1 through 5 use only the standard library.

---

## Week 1 — Python Core (Days 1 to 5)

### Day 1 — Variables, Types, Control Flow, Functions (90 min)
**File:** `labs/day01_variables_to_functions.py`
**Goal:** Print, variables, ints, strings, lists, if, for, while, def, return.

**Exercises (do in the lab file):**
1. Make a function `severity_score(level: str) -> int` that returns 1 for INFO, 2 for WARN, 3 for ERROR, 4 for CRITICAL.
2. Loop a list of fake log lines and print only the ones containing the word "denied".
3. Write `fizzbuzz` from 1 to 30. This is interview muscle memory.
4. Write a function that takes a list of integers and returns the max without using `max()`.
5. Write a function `is_private_ip(ip: str) -> bool` that checks if an IP starts with `10.`, `192.168.`, or `172.`.

### Day 2 — Strings, Lists, Dicts, Sets (90 min)
**File:** `labs/day02_strings_lists_dicts.py`
**Goal:** Indexing, slicing, methods (`split`, `strip`, `lower`, `startswith`), dict operations, set operations.

**Exercises:**
1. Take a log line like `"2026-05-08 ERROR auth failed for user=root ip=10.0.0.5"` and parse it into a dict with keys `date`, `level`, `message`, `user`, `ip`.
2. Count how many times each user appears in a list of 50 log entries (use a dict).
3. Find unique IPs in a list using a set.
4. Sort a list of dicts by the value of a key (`severity`).
5. Reverse a string without using `[::-1]` first, then with it.

### Day 3 — Functions Deeper, Errors, List/Dict Comprehensions (90 min)
**File:** `labs/day03_functions_errors_comprehensions.py`
**Goal:** Default args, *args, **kwargs, try/except/finally, raising, list comp, dict comp.

**Exercises:**
1. Write `safe_divide(a, b)` that returns 0 and logs a warning instead of crashing on divide by zero.
2. Write a list comp that filters log entries above WARN level.
3. Write a dict comp that maps username to count of failed logins.
4. Make a custom exception `PromptInjectionDetected` and raise it when a string contains "ignore previous instructions".
5. Write a function `parse_logs(*lines, level="ERROR")` that uses *args and a default.

### Day 4 — Classes, Decorators, Type Hints (90 min)
**File:** `labs/day04_classes_decorators_typing.py`
**Goal:** `class`, `__init__`, methods, inheritance, `@staticmethod`, `@property`, simple decorators, `from typing import`.

**Exercises:**
1. Build a `LogEntry` class with `__init__(self, level, message, source)` and a `is_critical()` method.
2. Subclass it as `SecurityAlert` that adds a `severity_score()` method.
3. Write a decorator `@timed` that prints how long a function took.
4. Write a decorator `@requires_auth` that checks a fake token before running.
5. Use type hints on every function. Run `python3 -m mypy file.py` if you want extra credit.

### Day 5 — Async, Iterators, Generators (90 min)
**File:** `labs/day05_async_iterators_generators.py`
**Goal:** `async def`, `await`, `asyncio.run`, `asyncio.gather`, `yield`, generator expressions.

**Exercises:**
1. Write an async function that simulates fetching a threat feed (use `asyncio.sleep(1)`).
2. Run 5 async fetches concurrently with `asyncio.gather`.
3. Write a generator that yields one log line at a time from a list.
4. Write a generator expression that filters and transforms in one line.
5. Compare time for sequential vs concurrent async fetch (print both).

---

## Week 2 — Real Tools (Days 6 to 10)

### Day 6 — Pydantic Models and JSON (90 min)
**File:** `labs/day06_pydantic_json.py`
**Setup:** `pip install "pydantic>=2.0" requests`

**Goal:** Pydantic v2 models, validation, parsing, serialization, json module.

**Exercises:**
1. Define a `LogEntry` pydantic model with `timestamp: datetime`, `level: Literal["INFO","WARN","ERROR","CRITICAL"]`, `message: str`, `source_ip: str`.
2. Parse a raw dict into the model and catch ValidationError.
3. Serialize back to JSON.
4. Write a custom validator that rejects messages over 500 chars.
5. Define a nested model `Alert` that contains a list of `LogEntry`.

### Day 7 — Files, Pathlib, OS, Subprocess (90 min)
**File:** `labs/day07_files_subprocess.py`
**Goal:** Read/write files, walk directories, run shell commands safely.

**Exercises:**
1. Read `/var/log/system.log` (or any file you have) and count ERROR lines.
2. Use `pathlib.Path` to find all `.py` files in this folder.
3. Run `subprocess.run(["echo", "hello"])` and capture output.
4. Run `who` or `whoami` and parse the output.
5. Write a JSON file then read it back.

### Day 8 — HTTP with requests, JSON parsing (90 min)
**File:** `labs/day08_http_requests.py`
**Goal:** GET, POST, headers, status codes, retries, JSON request/response.

**Exercises:**
1. GET `https://httpbin.org/get` and print the response JSON.
2. POST a dict to `https://httpbin.org/post` and read it back.
3. Add a custom User-Agent header.
4. Write a function `safe_get(url, retries=3)` with backoff.
5. Mock the `requests.get` call (using `unittest.mock`) so the test runs offline.

### Day 9 — FastAPI Mini Service (90 min)
**File:** `labs/day09_fastapi_minisvc.py`
**Setup:** `pip install fastapi uvicorn`

**Goal:** Define endpoints, request/response models, run a server.

**Exercises:**
1. POST `/triage` accepts a `LogEntry` and returns `{"verdict": "escalate" or "auto"}`.
2. GET `/health` returns `{"status": "ok"}`.
3. Use a pydantic model for request body.
4. Add a path parameter `/lookup/{ip}` that returns a stub threat intel result.
5. Run with `uvicorn day09_fastapi_minisvc:app --reload` and test with curl.

### Day 10 — pytest, Mocking, Test Discipline (90 min)
**File:** `labs/day10_pytest_mocks.py`
**Setup:** `pip install pytest`

**Goal:** Write tests, parametrize, mock external calls, run with `pytest`.

**Exercises:**
1. Write 5 unit tests for the parser you wrote on day 2.
2. Use `@pytest.mark.parametrize` for 4 input cases.
3. Mock a call to `requests.get` with `unittest.mock.patch`.
4. Test that your `PromptInjectionDetected` exception fires.
5. Get to green on `pytest -v`.

---

## Week 3 — LangGraph and Security Agents (Days 11 to 14)

### Day 11 — LangChain Primitives (90 min)
**File:** `labs/day11_langchain_primitives.py`
**Setup:** `pip install "langchain>=0.3" "langchain-anthropic>=0.3" "langchain-core>=0.3"`

**Goal:** Models, prompts, output parsers, basic chains. We mock the LLM by default. Set `ANTHROPIC_API_KEY` if you want it real.

**Exercises:**
1. Build a `ChatPromptTemplate` for a security triage prompt.
2. Pipe it into a fake model that returns `{"verdict": "escalate"}`.
3. Use `PydanticOutputParser` to coerce the LLM output into a pydantic model.
4. Chain prompt | model | parser using `|` syntax.
5. Add a system message that hardcodes prompt injection rules.

### Day 12 — LangGraph State Machines (90 min)
**File:** `labs/day12_langgraph_state.py`
**Setup:** `pip install "langgraph>=0.2"`

**Goal:** StateGraph, nodes, edges, conditional routing.

**Exercises:**
1. Define a `TypedDict` state with `log_entry`, `verdict`, `enriched`.
2. Add 3 nodes: `parse`, `enrich`, `decide`.
3. Wire START to parse to enrich to decide to END.
4. Add a conditional edge: if `verdict == "escalate"` go to a `notify` node, else END.
5. Compile and run with a sample log dict.

### Day 13 — Tool Use, Persistence, Human-in-the-Loop (90 min)
**File:** `labs/day13_langgraph_tools_persistence.py`
**Goal:** Tool nodes, checkpointers, interrupt before human decision.

**Exercises:**
1. Define 2 tools: `lookup_ip_reputation(ip)` (mocked) and `get_user_history(user)` (mocked).
2. Add a `tools` node using `ToolNode`.
3. Add a `MemorySaver` checkpointer so state persists between runs.
4. Add `interrupt_before=["notify"]` so the graph pauses for human approval.
5. Resume from the checkpoint and confirm the notify step ran.

### Day 14 — Full Security Agent with Prompt Injection Defense (90 min)
**File:** `labs/day14_langgraph_security_agent.py`
**Goal:** A real, runnable agent that triages a prompt-injection-suspected log entry, calls a mocked threat intel tool, decides escalate vs auto-respond, and emits structured JSON.

**Exercises:**
1. Run the agent end to end on a clean log (auto-respond path).
2. Run on a malicious log containing "ignore all previous instructions" (escalate path).
3. Verify the prompt injection guard catches the second one.
4. Add a 3rd test case where the IP is on a blocklist (escalate even if log seems clean).
5. Print the final state as JSON. This is your interview demo.

---

## What "Done" Looks Like on Day 14
You can sit in a screen share, get a prompt like "build a triage agent for suspicious logs", and within 30 minutes have a working LangGraph agent running locally. You can explain state, conditional edges, tool nodes, checkpointers, and how you would add prompt injection defenses. That is the bar at $200K.

## After Day 14 (If You Have More Time)
- Replay any day where you blanked. Retype the lab from memory.
- Read INTERVIEW-Qs.md. Solve every question without looking at the answer first.
- Drill ARTICULATION.md out loud. Record yourself. Listen back.
- Pair the agent with your existing SOAR stack (n8n webhook calls into the FastAPI service).

## Common Failure Modes
- **Reading too much, typing too little.** If your hands are not moving, stop and start typing.
- **Not running the file.** The compile error is the lesson. Embrace it.
- **Skipping pydantic.** Every senior AI security role uses pydantic. Do not skip Day 6.
- **Trying to memorize syntax.** Use the CHEATSHEET.md. Cold-recall comes from repetition, not memorization.
