"""Direct company career page scrapers."""

import hashlib
import json
import logging
import urllib.parse
from typing import Optional

from bs4 import BeautifulSoup

from job_digest.sources._http import fetch_with_retry, fetch_json_with_retry, random_delay

logger = logging.getLogger(__name__)

SOURCE_NAME = "company_page"


def scrape(company_pages: list[dict]) -> list[dict]:
    """
    Scrape job listings from configured company career pages.

    Args:
        company_pages: List of dicts with 'name', 'url', 'search_terms'.

    Returns:
        List of posting dicts.
    """
    all_postings = []

    scrapers = {
        "truist": _scrape_truist,
        "southern company": _scrape_southern_company,
        "ey": _scrape_ey,
        "insight global": _scrape_insight_global,
    }

    for page in company_pages:
        name = page.get("name", "").lower()
        url = page.get("url", "")
        terms = page.get("search_terms", [])

        scraper_fn = scrapers.get(name)
        if scraper_fn:
            try:
                postings = scraper_fn(url, terms)
                all_postings.extend(postings)
                logger.info("%s: found %d postings", page["name"], len(postings))
            except Exception as e:
                logger.warning("Company scrape failed for %s: %s", page["name"], str(e)[:200])
        else:
            # Generic scraper fallback
            try:
                postings = _scrape_generic(page["name"], url, terms)
                all_postings.extend(postings)
            except Exception as e:
                logger.warning("Generic scrape failed for %s: %s", page["name"], str(e)[:200])

        random_delay()

    # Deduplicate
    seen = set()
    unique = []
    for p in all_postings:
        if p["posting_id"] not in seen:
            seen.add(p["posting_id"])
            unique.append(p)

    logger.info("Company pages: scraped %d unique postings total", len(unique))
    return unique


def _scrape_truist(base_url: str, search_terms: list[str]) -> list[dict]:
    """Scrape Truist Financial career page."""
    postings = []

    for term in search_terms:
        # Truist uses Workday-based career site
        search_url = f"{base_url}/search/?q={urllib.parse.quote(term)}&sortColumn=relevancerank"

        html = fetch_with_retry(search_url)
        if not html:
            # Try alternative URL patterns
            alt_url = f"{base_url}/search/jobs?q={urllib.parse.quote(term)}"
            html = fetch_with_retry(alt_url)

        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")

        # Workday pattern: look for job listing elements
        job_links = soup.select("a[data-automation-id='jobTitle']") or \
                    soup.select("a.job-title") or \
                    soup.select("td.colTitle a") or \
                    soup.select("div.job-listing a") or \
                    soup.select("li.jobs-list-item a")

        for link in job_links:
            title = link.get_text(strip=True)
            href = link.get("href", "")
            if href and not href.startswith("http"):
                href = base_url.rstrip("/") + "/" + href.lstrip("/")

            if not title or not _is_security_related(title, term):
                continue

            # Try to get location from sibling/parent elements
            parent = link.find_parent(["tr", "li", "div"])
            location = ""
            if parent:
                loc_el = parent.select_one("span.job-location") or \
                         parent.select_one("td.colLocation") or \
                         parent.select_one("span[data-automation-id='jobLocation']")
                if loc_el:
                    location = loc_el.get_text(strip=True)

            pid = hashlib.md5(f"truist:{title}:{href}".encode()).hexdigest()[:12]

            postings.append({
                "source": f"{SOURCE_NAME}_truist",
                "posting_id": f"truist_{pid}",
                "title": title,
                "company": "Truist Financial",
                "location": location,
                "salary": "",
                "url": href,
                "description": "",
            })

        # Also try JSON-LD extraction
        postings.extend(_extract_json_ld(soup, "Truist Financial", f"{SOURCE_NAME}_truist", "truist"))

        random_delay()

    return postings


def _scrape_southern_company(base_url: str, search_terms: list[str]) -> list[dict]:
    """Scrape Southern Company career page."""
    postings = []

    for term in search_terms:
        search_url = f"{base_url}/search/?q={urllib.parse.quote(term)}&sortColumn=relevancerank"

        html = fetch_with_retry(search_url)
        if not html:
            alt_url = f"{base_url}/search/jobs?q={urllib.parse.quote(term)}"
            html = fetch_with_retry(alt_url)

        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")

        # Look for job cards/listings
        cards = soup.select("div.job-listing") or \
                soup.select("tr.data-row") or \
                soup.select("li.jobs-list-item") or \
                soup.select("a[data-automation-id='jobTitle']")

        for card in cards:
            if card.name == "a":
                title = card.get_text(strip=True)
                href = card.get("href", "")
            else:
                title_el = card.select_one("a") or card.select_one("h3") or card.select_one("h2")
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                href = title_el.get("href", "") if title_el.name == "a" else ""

            if not title or not _is_security_related(title, term):
                continue

            if href and not href.startswith("http"):
                href = base_url.rstrip("/") + "/" + href.lstrip("/")

            location = ""
            loc_el = card.select_one("span.location") or card.select_one("td.colLocation")
            if loc_el:
                location = loc_el.get_text(strip=True)

            pid = hashlib.md5(f"soco:{title}:{href}".encode()).hexdigest()[:12]

            postings.append({
                "source": f"{SOURCE_NAME}_southern_company",
                "posting_id": f"soco_{pid}",
                "title": title,
                "company": "Southern Company",
                "location": location,
                "salary": "",
                "url": href,
                "description": "",
            })

        postings.extend(
            _extract_json_ld(soup, "Southern Company", f"{SOURCE_NAME}_southern_company", "soco")
        )
        random_delay()

    return postings


def _scrape_ey(base_url: str, search_terms: list[str]) -> list[dict]:
    """Scrape EY career page."""
    postings = []

    for term in search_terms:
        # EY uses a search API-style URL
        search_url = f"{base_url}/search/?q={urllib.parse.quote(term)}"

        html = fetch_with_retry(search_url)
        if not html:
            # Try EY's job search with different URL patterns
            alt_url = f"https://careers.ey.com/search/?searchby=location&q={urllib.parse.quote(term)}"
            html = fetch_with_retry(alt_url)

        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")

        cards = soup.select("div.search-results-job") or \
                soup.select("div.card.job-card") or \
                soup.select("a[data-job-id]") or \
                soup.select("tr.data-row")

        for card in cards:
            if card.name == "a":
                title = card.get_text(strip=True)
                href = card.get("href", "")
                job_id = card.get("data-job-id", "")
            else:
                title_el = card.select_one("a.job-title") or card.select_one("a") or card.select_one("h3")
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                href = title_el.get("href", "") if title_el.name == "a" else ""
                job_id = card.get("data-job-id", "")

            if not title:
                continue

            if href and not href.startswith("http"):
                href = base_url.rstrip("/") + "/" + href.lstrip("/")

            if not job_id:
                job_id = hashlib.md5(f"ey:{title}:{href}".encode()).hexdigest()[:12]

            location = ""
            loc_el = card.select_one("span.job-location") or card.select_one("span.location")
            if loc_el:
                location = loc_el.get_text(strip=True)

            postings.append({
                "source": f"{SOURCE_NAME}_ey",
                "posting_id": f"ey_{job_id}",
                "title": title,
                "company": "EY (Ernst & Young)",
                "location": location,
                "salary": "",
                "url": href,
                "description": "",
            })

        postings.extend(_extract_json_ld(soup, "EY", f"{SOURCE_NAME}_ey", "ey"))
        random_delay()

    return postings


def _scrape_insight_global(base_url: str, search_terms: list[str]) -> list[dict]:
    """Scrape Insight Global job listings."""
    postings = []

    for term in search_terms:
        # Insight Global uses a different URL structure
        search_url = f"{base_url}?k={urllib.parse.quote(term)}"

        html = fetch_with_retry(search_url)
        if not html:
            alt_url = f"https://www.insightglobal.com/jobs/?k={urllib.parse.quote(term)}&l=Atlanta%2C+GA"
            html = fetch_with_retry(alt_url)

        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")

        cards = soup.select("div.job-card") or \
                soup.select("div.job-listing") or \
                soup.select("a.job-link") or \
                soup.select("div[data-job-id]")

        for card in cards:
            if card.name == "a":
                title = card.get_text(strip=True)
                href = card.get("href", "")
            else:
                title_el = card.select_one("a.job-title") or card.select_one("h3 a") or card.select_one("a")
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                href = title_el.get("href", "") if title_el.name == "a" else ""

            if not title:
                continue

            if href and not href.startswith("http"):
                href = base_url.rstrip("/") + "/" + href.lstrip("/")

            job_id = card.get("data-job-id", "")
            if not job_id:
                job_id = hashlib.md5(f"ig:{title}:{href}".encode()).hexdigest()[:12]

            location = ""
            loc_el = card.select_one("span.location") or card.select_one("div.job-location")
            if loc_el:
                location = loc_el.get_text(strip=True)

            salary = ""
            sal_el = card.select_one("span.salary") or card.select_one("div.job-salary")
            if sal_el:
                salary = sal_el.get_text(strip=True)

            desc = ""
            desc_el = card.select_one("div.job-description") or card.select_one("p.description")
            if desc_el:
                desc = desc_el.get_text(strip=True)[:300]

            postings.append({
                "source": f"{SOURCE_NAME}_insight_global",
                "posting_id": f"ig_{job_id}",
                "title": title,
                "company": "Insight Global",
                "location": location,
                "salary": salary,
                "url": href,
                "description": desc,
            })

        postings.extend(
            _extract_json_ld(soup, "Insight Global", f"{SOURCE_NAME}_insight_global", "ig")
        )
        random_delay()

    return postings


def _scrape_generic(company_name: str, base_url: str, search_terms: list[str]) -> list[dict]:
    """Generic career page scraper fallback."""
    postings = []

    for term in search_terms:
        search_url = f"{base_url}?q={urllib.parse.quote(term)}"
        html = fetch_with_retry(search_url)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")

        # Try JSON-LD first
        ld_postings = _extract_json_ld(
            soup, company_name, f"{SOURCE_NAME}_{company_name.lower()}", company_name.lower()[:4]
        )
        postings.extend(ld_postings)

        # Try to find job links heuristically
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            href = link.get("href", "")

            # Heuristic: looks like a job title (reasonable length, contains keywords)
            if 10 < len(text) < 100 and _is_security_related(text, term):
                if href and not href.startswith("http"):
                    href = base_url.rstrip("/") + "/" + href.lstrip("/")

                pid = hashlib.md5(f"{company_name}:{text}:{href}".encode()).hexdigest()[:12]
                postings.append({
                    "source": f"{SOURCE_NAME}_{company_name.lower()}",
                    "posting_id": f"{company_name.lower()[:4]}_{pid}",
                    "title": text,
                    "company": company_name,
                    "location": "",
                    "salary": "",
                    "url": href,
                    "description": "",
                })

        random_delay()

    return postings


def _extract_json_ld(soup: BeautifulSoup, company_name: str, source: str, prefix: str) -> list[dict]:
    """Extract job postings from JSON-LD structured data on the page."""
    postings = []

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            items = data if isinstance(data, list) else [data]
            for item in items:
                if item.get("@type") == "JobPosting":
                    title = item.get("title", "")
                    if not title:
                        continue

                    loc = item.get("jobLocation", {})
                    location = ""
                    if isinstance(loc, dict):
                        addr = loc.get("address", {})
                        if isinstance(addr, dict):
                            location = f"{addr.get('addressLocality', '')}, {addr.get('addressRegion', '')}"
                    elif isinstance(loc, list) and loc:
                        addr = loc[0].get("address", {})
                        location = f"{addr.get('addressLocality', '')}, {addr.get('addressRegion', '')}"

                    salary = ""
                    base_salary = item.get("baseSalary", {})
                    if isinstance(base_salary, dict):
                        value = base_salary.get("value", {})
                        if isinstance(value, dict):
                            min_v = value.get("minValue", "")
                            max_v = value.get("maxValue", "")
                            if min_v and max_v:
                                salary = f"${min_v}-${max_v}"

                    url = item.get("url", "")
                    pid = hashlib.md5(f"{prefix}:{title}:{url}".encode()).hexdigest()[:12]

                    org = item.get("hiringOrganization", {})
                    org_name = org.get("name", company_name) if isinstance(org, dict) else company_name

                    postings.append({
                        "source": source,
                        "posting_id": f"{prefix}_{pid}",
                        "title": title,
                        "company": org_name,
                        "location": location.strip(", "),
                        "salary": salary,
                        "url": url,
                        "description": (item.get("description", "") or "")[:500],
                    })
        except (json.JSONDecodeError, AttributeError, TypeError):
            continue

    return postings


def _is_security_related(title: str, search_term: str) -> bool:
    """Check if a job title is related to the search term."""
    title_lower = title.lower()
    term_lower = search_term.lower()

    # Direct term match
    if term_lower in title_lower:
        return True

    # Related security keywords
    security_keywords = [
        "security", "cyber", "soc", "iam", "infosec", "information security",
        "cloud security", "network security", "threat", "vulnerability",
        "penetration", "incident response", "compliance", "grc",
        "risk", "audit", "forensic",
    ]

    return any(kw in title_lower for kw in security_keywords)
