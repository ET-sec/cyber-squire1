# 30 Python Coding Interview Questions for AI Security Roles

Solutions are heavily commented. Read each one like a tutorial. Try the question yourself first, then check.

Difficulty key: **E** = easy (warmup), **M** = medium (core bar), **H** = hard (senior signal).

---

## Section 1: String Manipulation (5)

### 1. (E) Reverse a String
**Q:** Write a function `reverse(s: str) -> str` without using `[::-1]`.

```python
def reverse(s: str) -> str:
    # Build a list of chars in reverse order, then join
    chars = []
    for i in range(len(s) - 1, -1, -1):
        chars.append(s[i])
    return "".join(chars)

assert reverse("python") == "nohtyp"
```

### 2. (E) Count Vowels
**Q:** Count vowels in a string, case insensitive.

```python
def count_vowels(s: str) -> int:
    # Convert to lowercase once, then count using a comprehension + sum
    vowels = set("aeiou")
    return sum(1 for ch in s.lower() if ch in vowels)

assert count_vowels("Emmanuel") == 4
```

### 3. (M) Anagram Check
**Q:** Are two strings anagrams (same letters, different order)?

```python
def is_anagram(a: str, b: str) -> bool:
    # Normalize: lowercase, remove spaces. Then compare sorted chars.
    a_clean = a.replace(" ", "").lower()
    b_clean = b.replace(" ", "").lower()
    return sorted(a_clean) == sorted(b_clean)

# O(n log n) due to sort. For O(n), use Counter(a_clean) == Counter(b_clean).
assert is_anagram("listen", "silent")
assert not is_anagram("hello", "world")
```

### 4. (M) Longest Substring Without Repeating Chars
**Q:** Given a string, return the length of the longest substring with no repeats.

```python
def longest_unique(s: str) -> int:
    # Sliding window: shrink from the left when we hit a duplicate
    seen = {}             # char -> last index seen
    left = 0
    best = 0
    for right, ch in enumerate(s):
        # If we've seen ch at or after `left`, jump left past it
        if ch in seen and seen[ch] >= left:
            left = seen[ch] + 1
        seen[ch] = right
        best = max(best, right - left + 1)
    return best

assert longest_unique("abcabcbb") == 3   # "abc"
assert longest_unique("bbbb") == 1
```

### 5. (M) Strip Comments and Trim Log Lines
**Q:** Given a list of strings, strip everything after `#` and remove blank lines.

```python
def clean_lines(lines: list[str]) -> list[str]:
    out = []
    for raw in lines:
        # Split on first # only, take left side, strip whitespace
        no_comment = raw.split("#", 1)[0].strip()
        if no_comment:
            out.append(no_comment)
    return out

assert clean_lines(["a=1 # set", "", "b=2", "# full comment"]) == ["a=1", "b=2"]
```

---

## Section 2: Dict Counting and Aggregation (4)

### 6. (E) Count Word Frequency
**Q:** Return a dict of word -> count for a sentence.

```python
def word_counts(sentence: str) -> dict:
    # split() with no args splits on any whitespace
    counts = {}
    for word in sentence.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts

assert word_counts("the cat the dog the cat") == {"the": 3, "cat": 2, "dog": 1}
```

### 7. (E) Top K Frequent Items
**Q:** Return the K most common items in a list.

```python
from collections import Counter

def top_k(items: list, k: int) -> list:
    # Counter.most_common returns list of (item, count) tuples
    return [item for item, _ in Counter(items).most_common(k)]

assert top_k(["a", "b", "a", "c", "a", "b"], 2) == ["a", "b"]
```

### 8. (M) Group Logs by Source IP
**Q:** Given a list of log dicts, return a dict mapping source_ip to list of messages.

```python
from collections import defaultdict

def group_by_ip(logs: list[dict]) -> dict:
    # defaultdict(list) auto-creates an empty list on first access
    groups = defaultdict(list)
    for log in logs:
        groups[log["source_ip"]].append(log["message"])
    return dict(groups)

logs = [
    {"source_ip": "10.0.0.1", "message": "ok"},
    {"source_ip": "10.0.0.1", "message": "fail"},
    {"source_ip": "10.0.0.2", "message": "ok"},
]
assert group_by_ip(logs) == {"10.0.0.1": ["ok", "fail"], "10.0.0.2": ["ok"]}
```

### 9. (M) Two Sum (Hash Map Classic)
**Q:** Return indices of two numbers in `nums` that sum to `target`. Each input has exactly one solution.

```python
def two_sum(nums: list[int], target: int) -> list[int]:
    # Map each number to its index. As we scan, check if the complement
    # is already in the map. O(n) time, O(n) space.
    seen = {}
    for i, n in enumerate(nums):
        complement = target - n
        if complement in seen:
            return [seen[complement], i]
        seen[n] = i
    return []

assert two_sum([2, 7, 11, 15], 9) == [0, 1]
```

---

## Section 3: List Filtering and Two Pointer (4)

### 10. (E) Filter and Square Even Numbers
**Q:** Return squares of even numbers from a list.

```python
def even_squares(nums: list[int]) -> list[int]:
    # List comprehension with filter and transform
    return [n * n for n in nums if n % 2 == 0]

assert even_squares([1, 2, 3, 4, 5]) == [4, 16]
```

### 11. (M) Remove Duplicates Preserving Order
**Q:** Given a list, return a new list with duplicates removed but order preserved.

```python
def dedupe(items: list) -> list:
    # set() loses order. Use a seen set + list to keep order.
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

assert dedupe([1, 2, 1, 3, 2, 4]) == [1, 2, 3, 4]
```

### 12. (M) Two Pointer: Sorted Pair Sum
**Q:** Given a SORTED list and a target, find any pair that sums to target.

```python
def pair_sum_sorted(nums: list[int], target: int) -> tuple | None:
    # Two pointers: left starts at 0, right at the end.
    # If sum too small, move left up. If too big, move right down.
    left, right = 0, len(nums) - 1
    while left < right:
        s = nums[left] + nums[right]
        if s == target:
            return (nums[left], nums[right])
        if s < target:
            left += 1
        else:
            right -= 1
    return None

assert pair_sum_sorted([1, 2, 4, 7, 11], 9) == (2, 7)
```

### 13. (M) Merge Two Sorted Lists
**Q:** Merge two sorted lists into one sorted list.

```python
def merge_sorted(a: list, b: list) -> list:
    out = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    # One list is exhausted. Extend with whatever is left.
    out.extend(a[i:])
    out.extend(b[j:])
    return out

assert merge_sorted([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6]
```

---

## Section 4: Log and File Parsing (5)

### 14. (E) Count ERROR Lines in a Log
**Q:** Count lines containing "ERROR" in a file.

```python
def count_errors(path: str) -> int:
    count = 0
    with open(path) as f:
        for line in f:           # streaming, doesn't load whole file
            if "ERROR" in line:
                count += 1
    return count
```

### 15. (M) Parse a Log Line into a Dict
**Q:** Given `"2026-05-08 ERROR auth failed user=root ip=10.0.0.5"`, return a dict.

```python
def parse_log(raw: str) -> dict:
    parts = raw.strip().split(maxsplit=2)
    if len(parts) < 3:
        return {}
    date, level, rest = parts
    fields = {"date": date, "level": level, "message": rest}
    # Pull key=value pairs from the rest
    for tok in rest.split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            fields[k] = v
    return fields

result = parse_log("2026-05-08 ERROR auth failed user=root ip=10.0.0.5")
assert result["user"] == "root" and result["ip"] == "10.0.0.5"
```

### 16. (M) Find Top Failing User
**Q:** Given a list of log lines containing "user=X", return the user with the most occurrences.

```python
import re
from collections import Counter

def top_failing_user(lines: list[str]) -> str:
    # re.findall returns all matches. ([\w.-]+) captures user value.
    users = []
    for line in lines:
        match = re.search(r"user=([\w.-]+)", line)
        if match:
            users.append(match.group(1))
    return Counter(users).most_common(1)[0][0]

lines = ["user=alice fail", "user=root fail", "user=alice fail"]
assert top_failing_user(lines) == "alice"
```

### 17. (M) Detect Brute Force Pattern
**Q:** Given timestamped failed logins per user, return users with 5+ failures in a 60 second window.

```python
from collections import defaultdict

def brute_force_users(events: list[tuple[str, int]], window: int = 60, threshold: int = 5) -> list[str]:
    # events = [(user, timestamp_seconds), ...]
    by_user = defaultdict(list)
    for user, ts in events:
        by_user[user].append(ts)

    flagged = []
    for user, times in by_user.items():
        times.sort()
        # Sliding window over sorted timestamps
        left = 0
        for right in range(len(times)):
            while times[right] - times[left] > window:
                left += 1
            if right - left + 1 >= threshold:
                flagged.append(user)
                break
    return flagged

events = [("alice", 1), ("alice", 5), ("alice", 10), ("alice", 15), ("alice", 20), ("bob", 1), ("bob", 200)]
assert brute_force_users(events) == ["alice"]
```

### 18. (H) Tail a Log File (last N lines without loading all)
**Q:** Return the last N lines of a file efficiently.

```python
from collections import deque

def tail(path: str, n: int) -> list[str]:
    # deque(maxlen=n) auto-drops old items. Memory cost = N lines, not whole file.
    with open(path) as f:
        return list(deque(f, maxlen=n))

# For huge files, seek from end and read backwards. The deque approach
# is simpler and good enough for most interviews.
```

---

## Section 5: Regex (3)

### 19. (E) Extract All IPv4 Addresses
**Q:** Find all IPv4 addresses in a string.

```python
import re

def find_ips(text: str) -> list[str]:
    # \b = word boundary. \d{1,3} = 1-3 digits.
    pattern = r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
    return re.findall(pattern, text)

assert find_ips("from 10.0.0.5 to 8.8.8.8") == ["10.0.0.5", "8.8.8.8"]
```

### 20. (M) Mask Email Addresses
**Q:** Replace all emails in a string with `<email>`.

```python
import re

def mask_emails(text: str) -> str:
    # Simple email pattern. Don't ship to production; use a library.
    pattern = r"[\w.+-]+@[\w.-]+\.\w+"
    return re.sub(pattern, "<email>", text)

assert mask_emails("contact alice@a.com or bob@b.co") == "contact <email> or <email>"
```

### 21. (M) Parse Key=Value Pairs
**Q:** Pull all `key=value` pairs from a log line into a dict.

```python
import re

def kv_pairs(line: str) -> dict:
    # ([\w]+)=(\S+) captures key and value (non-whitespace)
    return dict(re.findall(r"(\w+)=(\S+)", line))

assert kv_pairs("user=root ip=10.0.0.5 ok") == {"user": "root", "ip": "10.0.0.5"}
```

---

## Section 6: Recursion and Algorithms (3)

### 22. (E) Factorial
**Q:** Recursive factorial.

```python
def factorial(n: int) -> int:
    # Base case stops the recursion.
    if n <= 1:
        return 1
    return n * factorial(n - 1)

assert factorial(5) == 120
```

### 23. (M) Flatten a Nested List
**Q:** `[1, [2, [3, 4]], 5]` -> `[1, 2, 3, 4, 5]`.

```python
def flatten(items: list) -> list:
    out = []
    for x in items:
        if isinstance(x, list):
            out.extend(flatten(x))   # recurse on sublist
        else:
            out.append(x)
    return out

assert flatten([1, [2, [3, 4]], 5]) == [1, 2, 3, 4, 5]
```

### 24. (H) Binary Search
**Q:** Find target index in a sorted list. Return -1 if missing.

```python
def binary_search(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

assert binary_search([1, 3, 5, 7, 9], 7) == 3
assert binary_search([1, 3, 5, 7, 9], 4) == -1
```

---

## Section 7: LangGraph and Agent Design (5)

### 25. (M) Define a LangGraph State Schema
**Q:** Design a TypedDict state for a triage agent that tracks the input log, parsed fields, intel, and verdict.

```python
from typing import TypedDict, Literal, Optional

class TriageState(TypedDict):
    log_entry: dict                                    # raw input
    parsed: dict                                       # normalized fields
    intel: dict                                        # tool results
    verdict: Literal["auto", "escalate", "blocked", ""]
    reasoning: str
    indicators: list[str]                              # what tripped the rule
    notified: bool                                     # did we page someone

# Why TypedDict: LangGraph reads/writes specific keys. Plain dict works
# but you lose IDE autocomplete and mypy can't catch typos.
```

### 26. (M) Build a Conditional Edge
**Q:** Add a conditional edge that routes to `notify` if verdict is "escalate", else to `auto_close`.

```python
from langgraph.graph import StateGraph, START, END

def route(state):
    return "notify" if state["verdict"] == "escalate" else "auto_close"

g = StateGraph(TriageState)
# ... add nodes ...
g.add_conditional_edges(
    "decide",
    route,
    {"notify": "notify", "auto_close": "auto_close"},
)
# The mapping turns the string returned by `route` into the next node name.
```

### 27. (M) Tool Node with Mocked Tools
**Q:** Wire a tool that looks up IP reputation. The tool receives state and returns updates.

```python
def lookup_ip_reputation(ip: str) -> dict:
    # Real version would call an API. This is mocked for tests.
    if ip in {"203.0.113.5"}:
        return {"reputation": "malicious", "confidence": 0.95}
    return {"reputation": "clean", "confidence": 0.9}

def tool_node(state):
    ip = state["parsed"]["ip"]
    intel = lookup_ip_reputation(ip)
    return {"intel": intel}

# In LangGraph 0.2+, you can also use the prebuilt ToolNode that wraps
# functions decorated with @tool. The pattern above is what you should
# reach for first because it's explicit and easy to test.
```

### 28. (H) Persistence with a Checkpointer
**Q:** Add a checkpointer so the graph can resume from where it stopped.

```python
from langgraph.checkpoint.memory import MemorySaver
# For real workloads:
# from langgraph.checkpoint.sqlite import SqliteSaver
# checkpointer = SqliteSaver.from_conn_string("/var/lib/agent/state.db")

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

# Each invoke needs a thread_id. State is keyed by thread_id.
config = {"configurable": {"thread_id": "incident-001"}}
app.invoke(initial_state, config=config)

# Resume later (e.g. after a crash) with the same thread_id:
state_now = app.get_state(config)
# Or continue execution if it was interrupted:
app.invoke(None, config=config)
```

### 29. (H) Human-in-the-Loop with interrupt_before
**Q:** Pause before the `notify` node so a human can approve.

```python
app = graph.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["notify"],   # pause BEFORE this node runs
)

config = {"configurable": {"thread_id": "incident-002"}}

# First invoke runs until just before `notify`
result = app.invoke(initial_state, config=config)

# Inspect what's about to happen
snapshot = app.get_state(config)
print("about to run:", snapshot.next)   # ('notify',)

# After human approval, resume by calling invoke with None
if human_says_yes():
    app.invoke(None, config=config)
# If human rejects, just don't resume. State stays paused.
```

### 30. (H) Prompt Injection Guard Inside an Agent
**Q:** Add a node that detects prompt injection in untrusted input before it touches the LLM.

```python
INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous",
    "you are now",
    "system prompt:",
    "</system>",
    "act as",
]

def injection_guard(state):
    """Treat all log content as untrusted DATA, not instructions.
    If we detect a prompt injection pattern, block the request and
    tag it for human review. Never pass the tainted content to the LLM."""
    msg = state["log_entry"]["message"].lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in msg:
            return {
                "verdict": "escalate",
                "indicators": ["prompt_injection", f"pattern:{pattern}"],
                "reasoning": f"injection pattern detected: {pattern!r}",
            }
    return {}

# Where to put this node: FIRST. Before any LLM call. Before any tool.
# Defense-in-depth: also escape/encode the message when it reaches the
# prompt template, never interpolate raw user content into the system msg.
```

---

## How to Use This File

1. Cover the answer with your hand. Try the question on paper or in a scratch file.
2. If you blank for more than 2 minutes, peek at the first comment.
3. Type out the solution from the file. Run it. Tweak it.
4. Tomorrow, redo 5 random ones from memory.
5. By interview day, every answer should be muscle memory.
