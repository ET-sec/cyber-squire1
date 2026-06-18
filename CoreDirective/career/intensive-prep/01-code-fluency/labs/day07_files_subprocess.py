"""
Day 7 — Files, Pathlib, OS, Subprocess
Run with: python3 day07_files_subprocess.py

Real security tooling reads files, walks directories, and shells out.
Use pathlib (modern) and subprocess.run with a list of args (safe).
"""

import json
import os
import subprocess
from pathlib import Path


# ============================================================
# 1. Reading a file
# ============================================================
# Use a context manager (with) so the file closes even on error.
sample_path = Path("/tmp/sample.log")
sample_path.write_text(
    "2026-05-08 INFO ok\n"
    "2026-05-08 ERROR auth fail user=root\n"
    "2026-05-08 WARN slow disk\n"
    "2026-05-08 ERROR auth fail user=admin\n"
)

with open(sample_path) as f:
    contents = f.read()
print("file contents:")
print(contents)


# ============================================================
# 2. Reading line by line (memory friendly)
# ============================================================
error_count = 0
with open(sample_path) as f:
    for line in f:        # iterates lazily
        if "ERROR" in line:
            error_count += 1
print("ERROR lines:", error_count)


# ============================================================
# 3. Writing a file
# ============================================================
report_path = Path("/tmp/report.txt")
with open(report_path, "w") as f:
    f.write(f"Total ERROR lines: {error_count}\n")
    f.write("Source: /tmp/sample.log\n")
print("\nwrote:", report_path, "->", report_path.read_text())


# ============================================================
# 4. JSON read/write
# ============================================================
data = {"alert_id": "ALR-001", "severity": 4, "tags": ["auth", "brute-force"]}

json_path = Path("/tmp/alert.json")
with open(json_path, "w") as f:
    json.dump(data, f, indent=2)

with open(json_path) as f:
    loaded = json.load(f)

print("\nloaded:", loaded)


# ============================================================
# 5. Pathlib basics
# ============================================================
here = Path(__file__).parent
print("\nthis file's directory:", here)

# List Python files in this directory
py_files = list(here.glob("*.py"))
print("py files:", [p.name for p in py_files])

# Walk recursively
all_md = list(here.parent.rglob("*.md"))
print("md files in parent tree:", len(all_md))

# Path math
sample_copy = here / "sample_copy.log"
print("would write to:", sample_copy)

# Properties
print("name:", sample_path.name)
print("stem:", sample_path.stem)
print("suffix:", sample_path.suffix)
print("exists?", sample_path.exists())


# ============================================================
# 6. OS environment
# ============================================================
# Read env vars (with default to avoid KeyError)
home = os.environ.get("HOME", "/tmp")
print("\nHOME:", home)

# Set an env var for child processes
os.environ["MY_FLAG"] = "1"


# ============================================================
# 7. Subprocess (the safe way)
# ============================================================
# ALWAYS pass args as a list. NEVER use shell=True with user input.
# capture_output=True puts stdout/stderr on the result.
result = subprocess.run(
    ["echo", "hello from subprocess"],
    capture_output=True,
    text=True,             # decode bytes to str
    check=False,           # don't raise on non-zero exit
)
print("\nstdout:", result.stdout.strip())
print("returncode:", result.returncode)

# Real tool example: who is logged in
try:
    who = subprocess.run(["whoami"], capture_output=True, text=True, timeout=5)
    print("whoami:", who.stdout.strip())
except FileNotFoundError:
    print("whoami not found")


# ============================================================
# 8. Subprocess with check=True for fail-loud
# ============================================================
try:
    subprocess.run(["false"], check=True)  # exits 1 -> CalledProcessError
except subprocess.CalledProcessError as e:
    print("expected failure:", e.returncode)


# ============================================================
# 9. Putting it together: parse a log file
# ============================================================
def count_by_level(path: Path) -> dict:
    counts: dict = {}
    with open(path) as f:
        for line in f:
            parts = line.strip().split(maxsplit=2)
            if len(parts) < 2:
                continue
            level = parts[1]
            counts[level] = counts.get(level, 0) + 1
    return counts


print("\ncounts by level:", count_by_level(sample_path))


# ============================================================
# TRY THIS
# ============================================================
# 1. Write a function that reads sample.log and returns lines with "user=root".
# 2. Use pathlib to find all .py files larger than 1KB in this folder.
# 3. Run `uname -a` via subprocess and parse out the kernel name.
# 4. Write a JSON file with 3 alerts then read and count by severity.
# 5. Make subprocess call timeout after 2 seconds for a hung command.
