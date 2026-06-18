"""Multi-source scraper orchestrator."""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from job_digest.sources import indeed, dice, usajobs, linkedin, company_pages
from job_digest.scorer import score_posting, get_matched_certs

logger = logging.getLogger(__name__)


def scrape_all(config: dict) -> tuple[list[dict], int]:
    """
    Run all scrapers, score results, and return filtered postings.

    Args:
        config: Full config dict from config.yaml.

    Returns:
        Tuple of (scored_postings sorted by score desc, total_scraped count).
    """
    search_terms = config.get("search_terms", [])
    locations = config.get("locations", [])
    company_page_configs = config.get("company_pages", [])
    min_score = config.get("scoring", {}).get("min_score", 50)

    all_postings = []
    source_stats = {}

    # Define scraper tasks
    tasks: list[tuple[str, Callable, tuple]] = [
        ("Indeed", indeed.scrape, (search_terms, locations)),
        ("Dice", dice.scrape, (search_terms, locations)),
        ("USAJobs", usajobs.scrape, (search_terms, locations, config)),
        ("LinkedIn", linkedin.scrape, (search_terms, locations)),
        ("Company Pages", company_pages.scrape, (company_page_configs,)),
    ]

    # Run scrapers with thread pool for parallelism
    # Each scraper handles its own rate limiting internally
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_source = {}
        for name, fn, args in tasks:
            future = executor.submit(_run_scraper, name, fn, args)
            future_to_source[future] = name

        for future in as_completed(future_to_source):
            source_name = future_to_source[future]
            try:
                postings = future.result()
                source_stats[source_name] = len(postings)
                all_postings.extend(postings)
            except Exception as e:
                logger.error("Scraper %s crashed: %s", source_name, str(e)[:200])
                source_stats[source_name] = 0

    total_scraped = len(all_postings)
    logger.info("Total scraped: %d postings from %d sources", total_scraped, len(source_stats))

    # Log per-source stats
    for name, count in sorted(source_stats.items()):
        logger.info("  %s: %d postings", name, count)

    # Score all postings
    scored = _score_all(all_postings, config)

    # Filter by min_score
    filtered = [p for p in scored if p.get("score", 0) >= min_score]

    # Sort by score descending
    filtered.sort(key=lambda p: p.get("score", 0), reverse=True)

    logger.info(
        "After scoring: %d of %d postings scored %d+",
        len(filtered), total_scraped, min_score,
    )

    return filtered, total_scraped


def scrape_source(source_name: str, config: dict) -> tuple[list[dict], int]:
    """
    Run a single source scraper by name.

    Args:
        source_name: One of 'indeed', 'dice', 'usajobs', 'linkedin', 'company_pages'.
        config: Full config dict.

    Returns:
        Tuple of (scored_postings, total_scraped).
    """
    search_terms = config.get("search_terms", [])
    locations = config.get("locations", [])
    min_score = config.get("scoring", {}).get("min_score", 50)

    source_map = {
        "indeed": lambda: indeed.scrape(search_terms, locations),
        "dice": lambda: dice.scrape(search_terms, locations),
        "usajobs": lambda: usajobs.scrape(search_terms, locations, config),
        "linkedin": lambda: linkedin.scrape(search_terms, locations),
        "company_pages": lambda: company_pages.scrape(config.get("company_pages", [])),
    }

    fn = source_map.get(source_name.lower())
    if not fn:
        logger.error("Unknown source: %s", source_name)
        return [], 0

    postings = fn()
    total = len(postings)

    scored = _score_all(postings, config)
    filtered = [p for p in scored if p.get("score", 0) >= min_score]
    filtered.sort(key=lambda p: p.get("score", 0), reverse=True)

    return filtered, total


def _run_scraper(name: str, fn: Callable, args: tuple) -> list[dict]:
    """Run a single scraper with error handling."""
    logger.info("Starting scraper: %s", name)
    try:
        postings = fn(*args)
        logger.info("Scraper %s completed: %d postings", name, len(postings))
        return postings
    except Exception as e:
        logger.error("Scraper %s failed: %s", name, str(e)[:200])
        return []


def _score_all(postings: list[dict], config: dict) -> list[dict]:
    """Score all postings and attach matched cert info."""
    for p in postings:
        p["score"] = score_posting(p, config)
        p["matched_certs"] = get_matched_certs(p, config)
    return postings
