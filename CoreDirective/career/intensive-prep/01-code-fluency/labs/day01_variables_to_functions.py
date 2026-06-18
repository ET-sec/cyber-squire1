"""
Day 1 — Variables, Types, Control Flow, Functions
Run with: python3 day01_variables_to_functions.py

Read every comment. Every line is a lesson.
"""

# ============================================================
# 1. Print and variables
# ============================================================
# Variables hold values. No type declaration needed (Python infers it).
name = "Emmanuel"           # str
age = 33                    # int
is_engineer = True          # bool
salary_target = 200_000.0   # float (underscores are just for readability)

print("Hello,", name)
print(f"Age: {age}, target: ${salary_target:,.0f}")  # f-strings format inline


# ============================================================
# 2. If / elif / else
# ============================================================
# Indentation matters in Python. 4 spaces, no exceptions.
def severity_score(level: str) -> int:
    """Map a log level string to a numeric score."""
    if level == "INFO":
        return 1
    elif level == "WARN":
        return 2
    elif level == "ERROR":
        return 3
    elif level == "CRITICAL":
        return 4
    else:
        return 0  # unknown level


print("CRITICAL ->", severity_score("CRITICAL"))
print("DEBUG ->", severity_score("DEBUG"))


# ============================================================
# 3. Lists and for loops
# ============================================================
# A list holds an ordered sequence. Index from 0.
log_lines = [
    "2026-05-08 INFO user=alice login success",
    "2026-05-08 ERROR user=root login denied",
    "2026-05-08 WARN user=bob suspicious activity",
    "2026-05-08 ERROR user=admin login denied",
]

# Loop and filter
print("\nDenied attempts:")
for line in log_lines:
    if "denied" in line:
        print(" ", line)


# ============================================================
# 4. While loops and counters
# ============================================================
# while runs as long as the condition is true. Break out when needed.
attempts = 0
max_attempts = 3
while attempts < max_attempts:
    print(f"Attempt {attempts + 1}")
    attempts += 1   # always update your counter or you get an infinite loop


# ============================================================
# 5. Functions with type hints
# ============================================================
# Type hints (the `-> bool` and `: str`) are not enforced at runtime.
# They document intent and let editors catch mistakes.
def is_private_ip(ip: str) -> bool:
    """Return True if the IP is in a private RFC1918 range (rough check)."""
    return ip.startswith("10.") or ip.startswith("192.168.") or ip.startswith("172.")


print("\n10.0.0.5 private?", is_private_ip("10.0.0.5"))
print("8.8.8.8 private?", is_private_ip("8.8.8.8"))


# ============================================================
# 6. FizzBuzz (interview muscle memory)
# ============================================================
# Classic warmup. Multiples of 3 -> Fizz, 5 -> Buzz, both -> FizzBuzz.
def fizzbuzz(n: int) -> None:
    for i in range(1, n + 1):
        if i % 15 == 0:
            print("FizzBuzz")
        elif i % 3 == 0:
            print("Fizz")
        elif i % 5 == 0:
            print("Buzz")
        else:
            print(i)


# Uncomment to run:
# fizzbuzz(15)


# ============================================================
# 7. Manual max (no built-in)
# ============================================================
def my_max(numbers: list) -> int:
    """Return the largest integer in a list without using max()."""
    if not numbers:
        return 0  # could also raise ValueError
    biggest = numbers[0]
    for n in numbers:
        if n > biggest:
            biggest = n
    return biggest


print("\nmax of [3, 7, 2, 9, 4]:", my_max([3, 7, 2, 9, 4]))


# ============================================================
# TRY THIS (do these in this same file, run after each change)
# ============================================================
# 1. Add a function `count_errors(lines: list) -> int` that returns
#    how many of the log_lines contain "ERROR".
# 2. Modify severity_score to return -1 for unknown levels.
# 3. Write a function that takes a list and returns it reversed
#    without using [::-1] or .reverse().
# 4. Add an "is_public_ip" function that returns True if NOT private.
# 5. Time yourself solving fizzbuzz from a blank file. Goal: under 3 minutes.
