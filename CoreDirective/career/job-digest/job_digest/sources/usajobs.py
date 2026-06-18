"""USAJobs API scraper (free, public API)."""

import logging
from typing import Optional

from job_digest.sources._http import fetch_json_with_retry, random_delay

logger = logging.getLogger(__name__)

SOURCE_NAME = "usajobs"
API_BASE = "https://data.usajobs.gov/api/Search"


def scrape(search_terms: list[str], locations: list[str], config: dict = None) -> list[dict]:
    """
    Query USAJobs API for cybersecurity/IT positions.

    USAJobs API is free and requires only a User-Agent header with an email.
    No API key needed.

    Args:
        search_terms: List of search queries.
        locations: List of location strings.
        config: Full config dict for USAJobs-specific settings.

    Returns:
        List of posting dicts.
    """
    if config is None:
        config = {}

    usajobs_cfg = config.get("usajobs", {})
    email = usajobs_cfg.get("email", "job-digest@example.com")
    job_series = usajobs_cfg.get("job_series", "2210")
    min_grade = usajobs_cfg.get("min_grade", 9)
    max_grade = usajobs_cfg.get("max_grade", 13)

    all_postings = []

    for term in search_terms:
        for location in locations:
            try:
                postings = _search_usajobs(
                    term, location, email, job_series, min_grade, max_grade
                )
                all_postings.extend(postings)
                random_delay()
            except Exception as e:
                logger.warning(
                    "USAJobs search failed for '%s' in '%s': %s",
                    term, location, str(e)[:200],
                )

    # Deduplicate
    seen = set()
    unique = []
    for p in all_postings:
        if p["posting_id"] not in seen:
            seen.add(p["posting_id"])
            unique.append(p)

    logger.info("USAJobs: scraped %d unique postings", len(unique))
    return unique


def _search_usajobs(
    query: str,
    location: str,
    email: str,
    job_series: str,
    min_grade: int,
    max_grade: int,
) -> list[dict]:
    """Query the USAJobs Search API."""
    headers = {
        "Host": "data.usajobs.gov",
        "User-Agent": email,
    }

    params = {
        "Keyword": query,
        "LocationName": location,
        "JobCategoryCode": job_series,
        "PayGradeLow": str(min_grade),
        "PayGradeHigh": str(max_grade),
        "DatePosted": "1",  # Last 24 hours
        "ResultsPerPage": "25",
    }

    data = fetch_json_with_retry(API_BASE, params=params, extra_headers=headers)
    if not data:
        return []

    return _parse_results(data)


def _parse_results(data: dict) -> list[dict]:
    """Parse USAJobs API response."""
    postings = []

    search_result = data.get("SearchResult", {})
    items = search_result.get("SearchResultItems", [])

    for item in items:
        try:
            matched = item.get("MatchedObjectDescriptor", {})
            posting = _parse_item(matched)
            if posting:
                postings.append(posting)
        except Exception as e:
            logger.debug("Failed to parse USAJobs item: %s", str(e)[:100])

    return postings


def _parse_item(matched: dict) -> Optional[dict]:
    """Parse a single USAJobs search result item."""
    if not matched:
        return None

    # Control number is the unique ID
    control_number = matched.get("PositionID", "")
    if not control_number:
        return None

    title = matched.get("PositionTitle", "")
    if not title:
        return None

    # Organization (agency)
    org = matched.get("OrganizationName", "")
    department = matched.get("DepartmentName", "")
    company = org if org else department

    # Location
    locations = matched.get("PositionLocation", [])
    if locations:
        loc_parts = []
        for loc in locations[:3]:  # Limit to 3 locations
            city = loc.get("CityName", "")
            state = loc.get("CountrySubDivisionCode", "")
            if city and state:
                loc_parts.append(f"{city}, {state}")
            elif city:
                loc_parts.append(city)
        location = " | ".join(loc_parts)
    else:
        location = ""

    # Check for remote/telework
    position_offering = matched.get("PositionOfferingType", [])
    user_area = matched.get("UserArea", {}).get("Details", {})
    telework = user_area.get("TeleworkEligible", "")
    if telework and "yes" in str(telework).lower():
        location += " (Telework eligible)"

    # Salary
    remuneration = matched.get("PositionRemuneration", [])
    salary = ""
    if remuneration:
        rem = remuneration[0]
        min_range = rem.get("MinimumRange", "")
        max_range = rem.get("MaximumRange", "")
        rate_type = rem.get("RateIntervalCode", "")
        if min_range and max_range:
            salary = f"${min_range}-${max_range}"
            if rate_type:
                salary += f" {rate_type}"

    # URL
    url = matched.get("PositionURI", "")
    apply_url = matched.get("ApplyURI", [""])[0] if matched.get("ApplyURI") else ""
    final_url = apply_url or url

    # Qualifications
    qualifications = matched.get("QualificationSummary", "")

    # Description
    description = matched.get("UserArea", {}).get("Details", {}).get("MajorDuties", [""])
    if isinstance(description, list):
        description = " ".join(description)
    if not description:
        description = qualifications

    return {
        "source": SOURCE_NAME,
        "posting_id": f"usajobs_{control_number}",
        "title": title,
        "company": company,
        "location": location.strip(),
        "salary": salary,
        "url": final_url,
        "description": description[:500] if description else "",
        "qualifications": qualifications[:500] if qualifications else "",
    }
