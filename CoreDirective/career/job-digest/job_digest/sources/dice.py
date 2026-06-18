"""Dice.com job scraper."""

import hashlib
import json
import logging
import urllib.parse
from typing import Optional

from bs4 import BeautifulSoup

from job_digest.sources._http import fetch_with_retry, random_delay

logger = logging.getLogger(__name__)

SOURCE_NAME = "dice"
BASE_URL = "https://www.dice.com"
SEARCH_URL = "https://www.dice.com/jobs"


def scrape(search_terms: list[str], locations: list[str]) -> list[dict]:
    """
    Scrape Dice for job postings matching search terms and locations.

    Args:
        search_terms: List of search queries.
        locations: List of location strings.

    Returns:
        List of posting dicts.
    """
    all_postings = []

    for term in search_terms:
        for location in locations:
            try:
                postings = _search_dice(term, location)
                all_postings.extend(postings)
                random_delay()
            except Exception as e:
                logger.warning("Dice search failed for '%s' in '%s': %s", term, location, str(e)[:200])

    # Deduplicate within this scrape run
    seen = set()
    unique = []
    for p in all_postings:
        if p["posting_id"] not in seen:
            seen.add(p["posting_id"])
            unique.append(p)

    logger.info("Dice: scraped %d unique postings", len(unique))
    return unique


def _search_dice(query: str, location: str) -> list[dict]:
    """Perform a Dice search and parse results."""
    params = {
        "q": query,
        "location": location,
        "radius": "30",
        "pageSize": "20",
        "page": "1",
        "postedDate": "ONE",  # Last 24 hours
    }
    url = f"{SEARCH_URL}?" + urllib.parse.urlencode(params)

    html = fetch_with_retry(url)
    if not html:
        return []

    return _parse_search_results(html)


def _parse_search_results(html: str) -> list[dict]:
    """Parse Dice search results page."""
    soup = BeautifulSoup(html, "html.parser")
    postings = []

    # Dice uses custom web components and shadow DOM, so we try multiple strategies

    # Strategy 1: Look for dhi-search-card elements
    cards = soup.select("dhi-search-card") or \
            soup.select("div.card.search-card") or \
            soup.select("a[data-cy='card-title-link']")

    for card in cards:
        try:
            posting = _parse_card(card)
            if posting:
                postings.append(posting)
        except Exception as e:
            logger.debug("Failed to parse Dice card: %s", str(e)[:100])

    # Strategy 2: Try to find JSON data in script tags
    if not postings:
        postings = _parse_embedded_json(soup)

    # Strategy 3: Parse generic link structure
    if not postings:
        postings = _parse_link_fallback(soup)

    return postings


def _parse_card(card) -> Optional[dict]:
    """Parse a single Dice job card."""
    # Title
    title_el = card.select_one("a[data-cy='card-title-link']") or \
               card.select_one("a.card-title-link") or \
               card.select_one("h5 a") or \
               card.find("a", href=True)
    if not title_el:
        return None

    title = title_el.get_text(strip=True)
    if not title:
        return None

    # URL
    href = title_el.get("href", "")
    if href and not href.startswith("http"):
        href = BASE_URL + href
    url = href

    # Posting ID
    pid = href.split("/")[-1] if href else ""
    if not pid:
        pid = hashlib.md5(f"{title}:{url}".encode()).hexdigest()[:12]

    # Company
    company_el = card.select_one("a[data-cy='search-result-company-name']") or \
                 card.select_one("span.card-company") or \
                 card.select_one("a.companyName")
    company = company_el.get_text(strip=True) if company_el else "Unknown"

    # Location
    location_el = card.select_one("span[data-cy='search-result-location']") or \
                  card.select_one("span.card-location") or \
                  card.select_one("span.location")
    location = location_el.get_text(strip=True) if location_el else ""

    # Salary (Dice often doesn't show salary in search results)
    salary = ""

    # Description snippet
    desc_el = card.select_one("div.card-description") or \
              card.select_one("div[data-cy='card-summary']")
    description = desc_el.get_text(strip=True) if desc_el else ""

    return {
        "source": SOURCE_NAME,
        "posting_id": f"dice_{pid}",
        "title": title,
        "company": company,
        "location": location,
        "salary": salary,
        "url": url,
        "description": description,
    }


def _parse_embedded_json(soup: BeautifulSoup) -> list[dict]:
    """Try to extract jobs from embedded JSON/script data."""
    postings = []

    for script in soup.find_all("script"):
        text = script.string or ""
        if "jobPosting" in text or "searchResults" in text or "jobResults" in text:
            try:
                # Try to find JSON object in script
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    data = json.loads(text[start:end])
                    jobs = _extract_jobs_from_json(data)
                    postings.extend(jobs)
            except (json.JSONDecodeError, ValueError):
                continue

    return postings


def _extract_jobs_from_json(data: dict) -> list[dict]:
    """Recursively extract job data from a nested JSON structure."""
    postings = []

    if isinstance(data, dict):
        # Check if this looks like a job object
        if "title" in data and ("company" in data or "companyName" in data):
            pid = data.get("id", data.get("detailsId", ""))
            if not pid:
                pid = hashlib.md5(data.get("title", "").encode()).hexdigest()[:12]
            postings.append({
                "source": SOURCE_NAME,
                "posting_id": f"dice_{pid}",
                "title": data.get("title", ""),
                "company": data.get("company", data.get("companyName", "Unknown")),
                "location": data.get("location", data.get("jobLocation", "")),
                "salary": data.get("salary", data.get("compensation", "")),
                "url": data.get("detailsPageUrl", data.get("url", "")),
                "description": data.get("summary", data.get("description", ""))[:500],
            })

        # Recurse into values
        for v in data.values():
            if isinstance(v, (dict, list)):
                postings.extend(_extract_jobs_from_json(v))

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                postings.extend(_extract_jobs_from_json(item))

    return postings


def _parse_link_fallback(soup: BeautifulSoup) -> list[dict]:
    """Last resort: extract any links that look like job detail pages."""
    postings = []
    seen_urls = set()

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "/job-detail/" in href or "/jobs/detail/" in href:
            if href in seen_urls:
                continue
            seen_urls.add(href)

            title = link.get_text(strip=True)
            if not title or len(title) < 5:
                continue

            if not href.startswith("http"):
                href = BASE_URL + href

            pid = href.split("/")[-1] or hashlib.md5(href.encode()).hexdigest()[:12]

            postings.append({
                "source": SOURCE_NAME,
                "posting_id": f"dice_{pid}",
                "title": title,
                "company": "Unknown",
                "location": "",
                "salary": "",
                "url": href,
                "description": "",
            })

    return postings
