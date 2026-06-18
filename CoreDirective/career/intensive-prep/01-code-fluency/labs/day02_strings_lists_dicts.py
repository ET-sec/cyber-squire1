"""
Day 2 — Strings, Lists, Dicts, Sets
Run with: python3 day02_strings_lists_dicts.py
"""

# ============================================================
# 1. String methods
# ============================================================
line = "  2026-05-08 ERROR auth failed for user=root ip=10.0.0.5  "

print("raw:", repr(line))             # repr shows the string with whitespace visible
print("strip:", line.strip())         # remove leading/trailing whitespace
print("upper:", line.upper())
print("split:", line.strip().split())  # default splits on any whitespace
print("startswith 2026:", line.strip().startswith("2026"))
print("contains ERROR:", "ERROR" in line)


# ============================================================
# 2. Slicing
# ============================================================
s = "abcdefgh"
print("\ns[0]:", s[0])      # 'a'
print("s[-1]:", s[-1])      # 'h' (negative indexes from the end)
print("s[2:5]:", s[2:5])    # 'cde'
print("s[:3]:", s[:3])      # 'abc'
print("s[::2]:", s[::2])    # every 2nd char: 'aceg'
print("s[::-1]:", s[::-1])  # reversed


# ============================================================
# 3. Parsing a log line into a dict
# ============================================================
def parse_log(raw: str) -> dict:
    """Turn '2026-05-08 ERROR auth failed for user=root ip=10.0.0.5'
    into a dict with date, level, message, user, ip."""
    raw = raw.strip()
    parts = raw.split(maxsplit=2)  # only split first 2 spaces
    if len(parts) < 3:
        return {}
    date, level, rest = parts
    # Pull out key=value pairs
    user = None
    ip = None
    for token in rest.split():
        if token.startswith("user="):
            user = token.split("=", 1)[1]
        elif token.startswith("ip="):
            ip = token.split("=", 1)[1]
    return {
        "date": date,
        "level": level,
        "message": rest,
        "user": user,
        "ip": ip,
    }


parsed = parse_log("2026-05-08 ERROR auth failed for user=root ip=10.0.0.5")
print("\nparsed:", parsed)


# ============================================================
# 4. Counting with dicts
# ============================================================
# A dict maps keys to values. Use .get(key, default) to avoid KeyError.
events = [
    "user=alice", "user=bob", "user=alice", "user=root",
    "user=bob", "user=alice", "user=root", "user=root",
]

counts: dict = {}
for e in events:
    user = e.split("=")[1]
    counts[user] = counts.get(user, 0) + 1

print("\ncounts:", counts)

# Cleaner version using collections.Counter
from collections import Counter
counter = Counter(e.split("=")[1] for e in events)
print("Counter:", counter)
print("most_common(2):", counter.most_common(2))


# ============================================================
# 5. Sets for uniques
# ============================================================
ips = ["10.0.0.5", "10.0.0.5", "8.8.8.8", "1.1.1.1", "8.8.8.8"]
unique_ips = set(ips)
print("\nunique IPs:", unique_ips)
print("count of unique:", len(unique_ips))

# Set ops
allowed = {"10.0.0.5", "10.0.0.6"}
seen = set(ips)
unauthorized = seen - allowed   # set difference
print("unauthorized:", unauthorized)


# ============================================================
# 6. Sorting a list of dicts
# ============================================================
alerts = [
    {"id": 1, "severity": 3, "msg": "auth fail"},
    {"id": 2, "severity": 1, "msg": "info ping"},
    {"id": 3, "severity": 4, "msg": "exfil suspected"},
]

# sorted() returns a NEW list. .sort() mutates in place.
by_sev = sorted(alerts, key=lambda a: a["severity"], reverse=True)
print("\nsorted by severity desc:")
for a in by_sev:
    print(" ", a)


# ============================================================
# 7. Dict iteration patterns
# ============================================================
config = {"timeout": 30, "retries": 3, "verbose": True}

print("\nkeys:", list(config.keys()))
print("values:", list(config.values()))
print("items:")
for key, val in config.items():
    print(f"  {key} = {val}")


# ============================================================
# TRY THIS
# ============================================================
# 1. Extend parse_log to also extract "session_id=" if present.
# 2. Given the events list above, write a function top_user(events)
#    that returns the most common username.
# 3. Sort the alerts list by id ascending.
# 4. Build a dict that maps severity -> list of msgs at that severity.
# 5. Reverse the string "Emmanuel" without using slicing.
