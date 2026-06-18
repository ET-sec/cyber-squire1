"""LinkedIn public job listings scraper."""

import hashlib
import logging
import urllib.parse
from typing import Optional

from bs4 import BeautifulSoup

from job_digest.sources._http import fetch_with_retry, random_delay

logger = logging.getLogger(__name__)

SOURCE_NAME = "linkedin"
BASE_URL = "https://www.linkedin.com"
# LinkedIn guest job search endpoint (no auth required)
SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"


def scrape(search_terms: list[str], locations: list[str]) -> list[dict]:
    """
    Scrape LinkedIn public job listings.

    LinkedIn aggressively blocks scrapers. This handles failures gracefully
    by printing a warning and returning an empty list.

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
                postings = _search_linkedin(term, location)
                all_postings.extend(postings)
                random_delay(min_s=2.0, max_s=5.0)  # Extra cautious with LinkedIn
            except Exception as e:
                logger.warning(
                    "LinkedIn search failed for '%s' in '%s': %s",
                    term, location, str(e)[:200],
                )

    if not all_postings:
        logger.info(
            "LinkedIn: no results (may be blocked). "
            "This is expected behavior -- LinkedIn actively blocks scrapers."
        )

    # Deduplicate
    seen = set()
    unique = []
    for p in all_postings:
        if p["posting_id"] not in seen:
            seen.add(p["posting_id"])
            unique.append(p)

    logger.info("LinkedIn: scraped %d unique postings", len(unique))
    return unique


def _search_linkedin(query: str, location: str) -> list[dict]:
    """Search LinkedIn's public jobs endpoint."""
    # Map common locations to LinkedIn geo IDs
    geo_id = _get_geo_id(location)

    params = {
        "keywords": query,
        "location": location,
        "f_TPR": "r86400",  # Last 24 hours
        "start": "0",
    }
    if geo_id:
        params["geoId"] = geo_id

    url = f"{SEARCH_URL}?" + urllib.parse.urlencode(params)

    html = fetch_with_retry(url, max_retries=2)  # Fewer retries for LinkedIn
    if not html:
        # Try the regular search page as fallback
        return _search_linkedin_fallback(query, location)

    return _parse_results(html)


def _search_linkedin_fallback(query: str, location: str) -> list[dict]:
    """Fallback: try the regular LinkedIn jobs search page."""
    params = {
        "keywords": query,
        "location": location,
        "f_TPR": "r86400",
    }
    url = f"https://www.linkedin.com/jobs/search/?" + urllib.parse.urlencode(params)

    html = fetch_with_retry(url, max_retries=1)
    if not html:
        return []

    return _parse_results(html)


def _parse_results(html: str) -> list[dict]:
    """Parse LinkedIn job listing HTML."""
    soup = BeautifulSoup(html, "html.parser")
    postings = []

    # LinkedIn guest API returns a list of job cards
    cards = soup.select("li") or soup.select("div.base-card")

    for card in cards:
        try:
            posting = _parse_card(card)
            if posting:
                postings.append(posting)
        except Exception as e:
            logger.debug("Failed to parse LinkedIn card: %s", str(e)[:100])

    return postings


def _parse_card(card) -> Optional[dict]:
    """Parse a single LinkedIn job card."""
    # Title
    title_el = card.select_one("h3.base-search-card__title") or \
               card.select_one("a.base-card__full-link") or \
               card.select_one("h3") or \
               card.select_one("a[data-tracking-control-name='public_jobs_jserp-result_search-card']")

    if not title_el:
        return None

    title = title_el.get_text(strip=True)
    if not title or len(title) < 3:
        return None

    # URL
    link_el = card.select_one("a.base-card__full-link") or \
              card.find("a", href=True)
    href = ""
    if link_el:
        href = link_el.get("href", "")
        if href and not href.startswith("http"):
            href = BASE_URL + href

    # Extract job ID from URL
    job_id = ""
    if "/view/" in href:
        parts = href.split("/view/")
        if len(parts) > 1:
            job_id = parts[1].split("/")[0].split("?")[0]
    if not job_id:
        job_id = hashlib.md5(f"{title}:{href}".encode()).hexdigest()[:12]

    # Company
    company_el = card.select_one("h4.base-search-card__subtitle") or \
                 card.select_one("a.hidden-nested-link") or \
                 card.select_one("h4")
    company = company_el.get_text(strip=True) if company_el else "Unknown"

    # Location
    location_el = card.select_one("span.job-search-card__location") or \
                  card.select_one("span.base-search-card__metadata")
    location = location_el.get_text(strip=True) if location_el else ""

    # Salary (LinkedIn rarely shows this in search results)
    salary_el = card.select_one("span.job-search-card__salary-info")
    salary = salary_el.get_text(strip=True) if salary_el else ""

    # Date
    date_el = card.select_one("time")
    posted = date_el.get_text(strip=True) if date_el else ""

    return {
        "source": SOURCE_NAME,
        "posting_id": f"linkedin_{job_id}",
        "title": title,
        "company": company,
        "location": location,
        "salary": salary,
        "url": href,
        "description": f"Posted: {posted}" if posted else "",
    }


def _get_geo_id(location: str) -> str:
    """Map common location strings to LinkedIn geo IDs."""
    geo_map = {
        "atlanta": "103644278",
        "atlanta, ga": "103644278",
        "remote": "",
        "georgia": "105765218",
    }
    return geo_map.get(location.lower().strip(), "")
