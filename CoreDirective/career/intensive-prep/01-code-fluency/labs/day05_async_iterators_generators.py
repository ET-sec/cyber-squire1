"""
Day 5 — Async, Iterators, Generators
Run with: python3 day05_async_iterators_generators.py

Async lets you wait on slow things (network, disk) without blocking the
whole program. Generators let you produce values one at a time without
loading everything into memory.
"""

import asyncio
import time


# ============================================================
# 1. Sync baseline (slow)
# ============================================================
def fetch_threat_feed_sync(name: str) -> dict:
    """Pretend to call a threat intel API. Takes 1 second."""
    time.sleep(1)
    return {"feed": name, "indicators": 100}


def run_sync():
    start = time.perf_counter()
    feeds = ["abuseipdb", "alienvault", "misp"]
    results = [fetch_threat_feed_sync(f) for f in feeds]
    elapsed = time.perf_counter() - start
    print(f"sync: {len(results)} feeds in {elapsed:.2f}s")
    return results


# ============================================================
# 2. Async version (fast)
# ============================================================
async def fetch_threat_feed(name: str) -> dict:
    """async def makes this a coroutine. await pauses without blocking."""
    await asyncio.sleep(1)
    return {"feed": name, "indicators": 100}


async def run_async():
    start = time.perf_counter()
    feeds = ["abuseipdb", "alienvault", "misp"]
    # asyncio.gather runs them concurrently
    results = await asyncio.gather(*(fetch_threat_feed(f) for f in feeds))
    elapsed = time.perf_counter() - start
    print(f"async: {len(results)} feeds in {elapsed:.2f}s")
    return results


# ============================================================
# 3. Async with timeout and error handling
# ============================================================
async def fetch_with_timeout(name: str, timeout: float = 0.5) -> dict:
    try:
        async with asyncio.timeout(timeout):
            return await fetch_threat_feed(name)
    except TimeoutError:
        return {"feed": name, "error": "timeout"}


# ============================================================
# 4. Generators with yield
# ============================================================
def stream_logs(lines: list):
    """Yield one line at a time. Doesn't load all into memory."""
    for line in lines:
        # In real life this could be reading from a file or socket.
        yield line.strip()


# Generator expression (inline, no def needed)
errors_only = (line for line in ["INFO ok", "ERROR boom", "WARN soft"]
               if "ERROR" in line)


# ============================================================
# 5. Generator that filters and transforms
# ============================================================
def parse_and_filter(raw_lines):
    """Yield parsed dicts only for ERROR lines."""
    for line in raw_lines:
        parts = line.strip().split(maxsplit=2)
        if len(parts) < 3:
            continue
        date, level, msg = parts
        if level == "ERROR":
            yield {"date": date, "level": level, "msg": msg}


# ============================================================
# 6. Async generator (advanced but useful)
# ============================================================
async def stream_alerts(count: int):
    """Yield alerts over time. Use `async for` to consume."""
    for i in range(count):
        await asyncio.sleep(0.1)
        yield {"id": i, "severity": (i % 4) + 1}


async def consume_alerts():
    print("\nstreaming alerts:")
    async for alert in stream_alerts(3):
        print(" ", alert)


# ============================================================
# Main entry
# ============================================================
def main():
    # Sync demo (uncomment for the slow comparison; takes 3s)
    # run_sync()

    # Async demo
    asyncio.run(run_async())

    # Generator demo
    print("\nstream_logs:")
    for line in stream_logs(["  one  ", "  two  ", "  three  "]):
        print(" ", repr(line))

    print("\nerrors_only:")
    for e in errors_only:
        print(" ", e)

    # Parsed + filtered generator
    raw = [
        "2026-05-08 INFO ok",
        "2026-05-08 ERROR boom",
        "2026-05-08 WARN soft",
        "2026-05-08 ERROR again",
    ]
    print("\nparse_and_filter:")
    for parsed in parse_and_filter(raw):
        print(" ", parsed)

    # Async generator
    asyncio.run(consume_alerts())


if __name__ == "__main__":
    main()


# ============================================================
# TRY THIS
# ============================================================
# 1. Make fetch_threat_feed sometimes raise an exception (random.random()).
#    Use asyncio.gather(..., return_exceptions=True) to handle it.
# 2. Write an async function that races 3 threat feeds and returns the
#    first one to respond using asyncio.wait_for.
# 3. Build a generator that reads a real file line by line:
#    def read_lines(path): yield from open(path)
# 4. Convert run_sync vs run_async into a benchmark that prints both times.
# 5. Add a counter to consume_alerts so you can stop after N alerts.
