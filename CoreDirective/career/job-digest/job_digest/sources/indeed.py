"""Indeed job scraper."""

import hashlib
import logging
import re
import urllib.parse
from typing import Optional

from bs4 import BeautifulSoup

from job_digest.sources._http import fetch_with_retry, random_delay

logger = logging.getLogger(__name__)

SOURCE_NAME = "indeed"
BASE_URL = "https://www.indeed.com"


def scrape(search_terms: list[str], locations: list[str]) -> list[dict]:
    """
    Scrape Indeed for job postings matching search terms and locations.

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
                postings = _search_indeed(term, location)
                all_postings.extend(postings)
                random_delay()
            except Exception as e:
                logger.warning("Indeed search failed for '%s' in '%s': %s", term, location, str(e)[:200])

    # Deduplicate within this scrape run by posting_id
    seen = set()
    unique = []
    for p in all_postings:
        if p["posting_id"] not in seen:
            seen.add(p["posting_id"])
            unique.append(p)

    logger.info("Indeed: scraped %d unique postings", len(unique))
    return unique


def _search_indeed(query: str, location: str) -> list[dict]:
    """Perform a single Indeed search and parse results."""
    params = {
        "q": query,
        "l": location,
        "sort": "date",
        "fromage": "1",  # Last 24 hours
    }
    url = f"{BASE_URL}/jobs?" + urllib.parse.urlencode(params)

    html = fetch_with_retry(url)
    if not html:
        return []

    return _parse_search_results(html)


def _parse_search_results(html: str) -> list[dict]:
    """Parse Indeed search results page HTML."""
    soup = BeautifulSoup(html, "html.parser")
    postings = []

    # Indeed uses multiple possible selectors for job cards
    job_cards = soup.select("div.job_seen_beacon") or \
                soup.select("div.jobsearch-SerpJobCard") or \
                soup.select("div[data-jk]") or \
                soup.select("li div.result")

    for card in job_cards:
        try:
            posting = _parse_card(card)
            if posting:
                postings.append(posting)
        except Exception as e:
            logger.debug("Failed to parse Indeed card: %s", str(e)[:100])

    # Fallback: try to extract from script tags (Indeed often embeds JSON)
    if not postings:
        postings = _parse_json_ld(soup)

    return postings


def _parse_card(card) -> Optional[dict]:
    """Parse a single job card element."""
    # Title
    title_el = card.select_one("h2.jobTitle a") or \
               card.select_one("a[data-jk]") or \
               card.select_one("h2 a") or \
               card.select_one("a.jcs-JobTitle")
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

    # Job key for dedup
    jk = card.get("data-jk") or title_el.get("data-jk") or ""
    if not jk:
        jk = hashlib.md5(f"{title}:{url}".encode()).hexdigest()[:12]

    # Company
    company_el = card.select_one("span[data-testid='company-name']") or \
                 card.select_one("span.companyName") or \
                 card.select_one("span.company")
    company = company_el.get_text(strip=True) if company_el else "Unknown"

    # Location
    location_el = card.select_one("div[data-testid='text-location']") or \
                  card.select_one("div.companyLocation") or \
                  card.select_one("span.location")
    location = location_el.get_text(strip=True) if location_el else ""

    # Salary
    salary_el = card.select_one("div.salary-snippet-container") or \
                card.select_one("div[data-testid='attribute_snippet_testid']") or \
                card.select_one("span.salaryText") or \
                card.select_one("div.metadata.salary-snippet-container")
    salary = salary_el.get_text(strip=True) if salary_el else ""

    # Description snippet
    desc_el = card.select_one("div.job-snippet") or \
              card.select_one("div[class*='job-snippet']") or \
              card.select_one("table td.snip")
    description = desc_el.get_text(strip=True) if desc_el else ""

    return {
        "source": SOURCE_NAME,
        "posting_id": f"indeed_{jk}",
        "title": title,
        "company": company,
        "location": location,
        "salary": salary,
        "url": url,
        "description": description,
    }


def _parse_json_ld(soup: BeautifulSoup) -> list[dict]:
    """Try to extract job postings from JSON-LD structured data."""
    import json

    postings = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            items = data if isinstance(data, list) else [data]
            for item in items:
                if item.get("@type") == "JobPosting":
                    salary = ""
                    base_salary = item.get("baseSalary", {})
                    if isinstance(base_salary, dict):
                        value = base_salary.get("value", {})
                        if isinstance(value, dict):
                            min_val = value.get("minValue", "")
                            max_val = value.get("maxValue", "")
                            if min_val and max_val:
                                salary = f"${min_val}-${max_val}"
                            elif min_val:
                                salary = f"${min_val}"

                    loc = item.get("jobLocation", {})
                    if isinstance(loc, dict):
                        addr = loc.get("address", {})
                        if isinstance(addr, dict):
                            location = f"{addr.get('addressLocality', '')}, {addr.get('addressRegion', '')}"
                        else:
                            location = ""
                    elif isinstance(loc, list) and loc:
                        addr = loc[0].get("address", {})
                        location = f"{addr.get('addressLocality', '')}, {addr.get('addressRegion', '')}"
                    else:
                        location = ""

                    jk = hashlib.md5(item.get("url", item.get("title", "")).encode()).hexdigest()[:12]

                    posting = {
                        "source": SOURCE_NAME,
                        "posting_id": f"indeed_{jk}",
                        "title": item.get("title", ""),
                        "company": item.get("hiringOrganization", {}).get("name", "Unknown"),
                        "location": location.strip(", "),
                        "salary": salary,
                        "url": item.get("url", ""),
                        "description": item.get("description", "")[:500],
                    }
                    if posting["title"]:
                        postings.append(posting)
        except (json.JSONDecodeError, AttributeError):
            continue

    return postings
