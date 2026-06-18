"""
Day 8 — HTTP with requests, JSON parsing, mocking
Setup: pip install requests
Run with: python3 day08_http_requests.py

requests is the standard HTTP client. httpbin.org echoes whatever
you send so you can test without a real backend.
"""

import json
import time
from unittest.mock import patch, MagicMock

try:
    import requests
except ImportError:
    print("pip install requests")
    raise SystemExit(1)


# ============================================================
# 1. Basic GET
# ============================================================
def basic_get():
    r = requests.get("https://httpbin.org/get", timeout=5)
    r.raise_for_status()  # raise on 4xx/5xx
    print("status:", r.status_code)
    print("response keys:", list(r.json().keys()))


# ============================================================
# 2. POST with JSON body
# ============================================================
def basic_post():
    payload = {"alert_id": "ALR-001", "verdict": "escalate"}
    r = requests.post(
        "https://httpbin.org/post",
        json=payload,           # serializes to JSON, sets Content-Type
        timeout=5,
    )
    r.raise_for_status()
    echoed = r.json()["json"]
    print("\nechoed back:", echoed)


# ============================================================
# 3. Custom headers
# ============================================================
def with_headers():
    r = requests.get(
        "https://httpbin.org/headers",
        headers={
            "User-Agent": "coredirective-triage/1.0",
            "X-Tenant": "tigouetheory",
        },
        timeout=5,
    )
    print("\nheaders sent:", r.json()["headers"].get("User-Agent"))


# ============================================================
# 4. Retry with backoff (manual, no library)
# ============================================================
def safe_get(url: str, retries: int = 3, backoff: float = 0.5) -> dict | None:
    """Retry on connection errors and 5xx with exponential backoff."""
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=5)
            if r.status_code >= 500:
                raise requests.HTTPError(f"server {r.status_code}")
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, requests.HTTPError) as e:
            wait = backoff * (2 ** attempt)
            print(f"  attempt {attempt + 1} failed: {e}. retry in {wait}s")
            time.sleep(wait)
    return None


# ============================================================
# 5. Session for connection pooling
# ============================================================
def with_session():
    """A Session reuses TCP connections. Faster for multiple calls."""
    with requests.Session() as s:
        s.headers.update({"User-Agent": "coredirective-triage/1.0"})
        for i in range(3):
            r = s.get("https://httpbin.org/get", timeout=5)
            print(f"\ncall {i + 1}: {r.status_code}")


# ============================================================
# 6. Mocking requests for offline tests
# ============================================================
def get_threat_intel(ip: str) -> dict:
    """Real function we want to test without hitting the network."""
    r = requests.get(f"https://intel.example.com/lookup/{ip}", timeout=5)
    r.raise_for_status()
    return r.json()


def test_get_threat_intel_mocked():
    """Use unittest.mock.patch to replace requests.get."""
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"ip": "8.8.8.8", "rep": "clean"}
    fake_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=fake_response) as mocked:
        result = get_threat_intel("8.8.8.8")
        assert result == {"ip": "8.8.8.8", "rep": "clean"}
        mocked.assert_called_once()
        print("\nmocked test passed:", result)


# ============================================================
# Main
# ============================================================
def main():
    try:
        basic_get()
        basic_post()
        with_headers()
        with_session()
    except requests.RequestException as e:
        print(f"network call failed: {e}")
        print("(this is fine if you are offline)")

    # Mock-based test always works offline
    test_get_threat_intel_mocked()


if __name__ == "__main__":
    main()


# ============================================================
# TRY THIS
# ============================================================
# 1. Modify safe_get to retry on 429 (rate limit) with longer backoff.
# 2. Write a function that POSTs an alert dict to httpbin and asserts
#    the response echo matches what you sent.
# 3. Add an Authorization: Bearer header from os.environ["API_TOKEN"].
# 4. Mock get_threat_intel to RAISE a ConnectionError, verify your
#    code handles it gracefully.
# 5. Build a bulk_lookup(ips: list) that uses Session and returns a dict
#    of ip -> result.
