"""Shared HTTP utilities: retry logic, rate limiting, User-Agent rotation."""

import logging
import random
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# User-Agent rotation pool (real browser user agents)
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
]


def get_random_ua() -> str:
    """Return a random User-Agent string."""
    return random.choice(USER_AGENTS)


def get_session() -> requests.Session:
    """Create a requests session with default headers."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": get_random_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "no-cache",
    })
    return session


def random_delay(min_s: float = 1.0, max_s: float = 3.0) -> None:
    """Sleep for a random interval to respect rate limits."""
    delay = random.uniform(min_s, max_s)
    time.sleep(delay)


def fetch_with_retry(
    url: str,
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    timeout: int = 15,
    params: dict = None,
    extra_headers: dict = None,
) -> Optional[str]:
    """
    Fetch a URL with exponential backoff retry logic.

    Args:
        url: The URL to fetch.
        max_retries: Maximum number of retry attempts.
        backoff_factor: Multiplier for exponential backoff.
        timeout: Request timeout in seconds.
        params: Optional query parameters.
        extra_headers: Optional additional headers.

    Returns:
        Response text on success, None on failure.
    """
    session = get_session()
    if extra_headers:
        session.headers.update(extra_headers)

    last_error = None

    for attempt in range(max_retries + 1):
        try:
            # Rotate User-Agent on each attempt
            session.headers["User-Agent"] = get_random_ua()

            response = session.get(url, params=params, timeout=timeout, allow_redirects=True)

            if response.status_code == 200:
                return response.text
            elif response.status_code == 429:
                # Rate limited - back off more aggressively
                wait = backoff_factor ** (attempt + 2) + random.uniform(1, 3)
                logger.warning("Rate limited (429) on %s, waiting %.1fs", url[:80], wait)
                time.sleep(wait)
                continue
            elif response.status_code == 403:
                logger.warning("Blocked (403) on %s", url[:80])
                return None
            elif response.status_code >= 500:
                logger.warning("Server error (%d) on %s", response.status_code, url[:80])
            else:
                logger.warning("HTTP %d on %s", response.status_code, url[:80])

        except requests.exceptions.Timeout:
            last_error = "timeout"
            logger.debug("Timeout on %s (attempt %d/%d)", url[:80], attempt + 1, max_retries + 1)
        except requests.exceptions.ConnectionError as e:
            last_error = str(e)[:100]
            logger.debug("Connection error on %s: %s", url[:80], last_error)
        except Exception as e:
            last_error = str(e)[:100]
            logger.debug("Request error on %s: %s", url[:80], last_error)

        if attempt < max_retries:
            wait = backoff_factor ** attempt + random.uniform(0.5, 1.5)
            time.sleep(wait)

    logger.warning("All %d attempts failed for %s (last error: %s)", max_retries + 1, url[:80], last_error)
    return None


def fetch_json_with_retry(
    url: str,
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    timeout: int = 15,
    params: dict = None,
    extra_headers: dict = None,
) -> Optional[dict]:
    """
    Fetch a JSON API endpoint with retry logic.

    Args:
        url: The API URL.
        max_retries: Maximum number of retry attempts.
        backoff_factor: Multiplier for exponential backoff.
        timeout: Request timeout in seconds.
        params: Optional query parameters.
        extra_headers: Optional additional headers.

    Returns:
        Parsed JSON dict on success, None on failure.
    """
    session = get_session()
    session.headers.update({
        "Accept": "application/json",
    })
    if extra_headers:
        session.headers.update(extra_headers)

    last_error = None

    for attempt in range(max_retries + 1):
        try:
            session.headers["User-Agent"] = get_random_ua()
            response = session.get(url, params=params, timeout=timeout)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                wait = backoff_factor ** (attempt + 2) + random.uniform(1, 3)
                logger.warning("Rate limited (429) on API %s, waiting %.1fs", url[:80], wait)
                time.sleep(wait)
                continue
            elif response.status_code == 403:
                logger.warning("Blocked (403) on API %s", url[:80])
                return None
            else:
                logger.warning("API HTTP %d on %s", response.status_code, url[:80])

        except requests.exceptions.Timeout:
            last_error = "timeout"
        except requests.exceptions.ConnectionError as e:
            last_error = str(e)[:100]
        except ValueError as e:
            last_error = f"JSON decode error: {str(e)[:50]}"
        except Exception as e:
            last_error = str(e)[:100]

        if attempt < max_retries:
            wait = backoff_factor ** attempt + random.uniform(0.5, 1.5)
            time.sleep(wait)

    logger.warning("All API attempts failed for %s (last error: %s)", url[:80], last_error)
    return None
