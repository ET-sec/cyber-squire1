"""Job posting scraper. Extracts structured data from job posting URLs."""

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from rich.console import Console

console = Console(stderr=True)

# Common headers to mimic a browser
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# Patterns to detect JS-rendered pages
JS_RENDERED_INDICATORS = [
    "enable javascript",
    "javascript is required",
    "please enable javascript",
    "this page requires javascript",
    "noscript",
    "loading...",
    "__next",
    "react-root",
]

# Sites known to require authentication or heavy JS
AUTH_WALL_DOMAINS = ["linkedin.com", "glassdoor.com"]
JS_HEAVY_DOMAINS = ["lever.co", "greenhouse.io", "workday.com", "myworkdayjobs.com"]


@dataclass
class JobPosting:
    """Structured job posting data."""

    url: str = ""
    job_title: str = ""
    company_name: str = ""
    location: str = ""
    remote_status: str = ""  # Remote, Hybrid, On-site, or empty
    salary_range: str = ""
    years_experience: str = ""
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    required_certs: list[str] = field(default_factory=list)
    key_responsibilities: list[str] = field(default_factory=list)
    qualifications: list[str] = field(default_factory=list)
    description_text: str = ""  # Full text for LLM analysis
    raw_html: str = ""

    def is_valid(self) -> bool:
        """Check if minimum useful data was extracted."""
        return bool(self.job_title or self.description_text)


def scrape_job_posting(url: str) -> JobPosting:
    """Scrape a job posting URL and return structured data.

    Handles common job boards (Indeed, Dice, LinkedIn public, company pages).
    Prints warnings for JS-rendered or auth-walled pages.
    """
    posting = JobPosting(url=url)
    domain = urlparse(url).netloc.lower()

    # Warn about auth walls
    for auth_domain in AUTH_WALL_DOMAINS:
        if auth_domain in domain:
            console.print(
                f"[yellow]Warning:[/yellow] {auth_domain} often requires login. "
                "Extraction may be limited. Consider pasting the job description manually."
            )

    # Warn about JS-heavy sites
    for js_domain in JS_HEAVY_DOMAINS:
        if js_domain in domain:
            console.print(
                f"[yellow]Warning:[/yellow] {js_domain} relies heavily on JavaScript. "
                "Some content may not be available via static scraping."
            )

    # Fetch the page
    try:
        response = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        console.print("[red]Error:[/red] Request timed out after 30 seconds.")
        return posting
    except requests.exceptions.ConnectionError:
        console.print("[red]Error:[/red] Could not connect to the URL.")
        return posting
    except requests.exceptions.HTTPError as e:
        console.print(f"[red]Error:[/red] HTTP {e.response.status_code} returned.")
        if e.response.status_code == 403:
            console.print(
                "[yellow]Hint:[/yellow] The site may be blocking automated requests."
            )
        return posting
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error:[/red] Failed to fetch URL: {e}")
        return posting

    posting.raw_html = response.text
    soup = BeautifulSoup(response.text, "lxml")

    # Check for JS-rendered content
    body_text = soup.get_text(separator=" ", strip=True).lower()
    if len(body_text) < 200:
        for indicator in JS_RENDERED_INDICATORS:
            if indicator in body_text or indicator in response.text.lower():
                console.print(
                    "[yellow]Warning:[/yellow] Page appears to be JavaScript-rendered. "
                    "Extracted content may be incomplete."
                )
                break

    # Route to site-specific parser or generic parser
    if "indeed.com" in domain:
        _parse_indeed(soup, posting)
    elif "dice.com" in domain:
        _parse_dice(soup, posting)
    elif "linkedin.com" in domain:
        _parse_linkedin(soup, posting)
    else:
        _parse_generic(soup, posting)

    # Always run the text extraction as fallback/supplement
    _extract_from_text(posting)

    if not posting.is_valid():
        console.print(
            "[yellow]Warning:[/yellow] Could not extract structured data. "
            "The full page text is available for LLM analysis."
        )

    return posting


def _parse_indeed(soup: BeautifulSoup, posting: JobPosting) -> None:
    """Parse Indeed job posting page."""
    # Job title
    title_el = soup.find("h1", class_=re.compile(r"jobsearch-JobInfoHeader-title"))
    if not title_el:
        title_el = soup.find("h1")
    if title_el:
        posting.job_title = title_el.get_text(strip=True)

    # Company name
    company_el = soup.find("div", {"data-company-name": True})
    if not company_el:
        company_el = soup.find("a", {"data-tn-element": "companyName"})
    if company_el:
        posting.company_name = company_el.get_text(strip=True)

    # Location
    location_el = soup.find("div", {"data-testid": re.compile(r"job-location|inlineHeader-companyLocation")})
    if not location_el:
        location_el = soup.find("div", class_=re.compile(r"companyLocation"))
    if location_el:
        posting.location = location_el.get_text(strip=True)

    # Salary
    salary_el = soup.find("div", {"id": "salaryInfoAndJobType"})
    if not salary_el:
        salary_el = soup.find("span", class_=re.compile(r"salary"))
    if salary_el:
        posting.salary_range = salary_el.get_text(strip=True)

    # Job description
    desc_el = soup.find("div", {"id": "jobDescriptionText"})
    if not desc_el:
        desc_el = soup.find("div", class_=re.compile(r"jobsearch-jobDescriptionText"))
    if desc_el:
        posting.description_text = desc_el.get_text(separator="\n", strip=True)


def _parse_dice(soup: BeautifulSoup, posting: JobPosting) -> None:
    """Parse Dice job posting page."""
    # Job title
    title_el = soup.find("h1", {"data-cy": "jobTitle"})
    if not title_el:
        title_el = soup.find("h1")
    if title_el:
        posting.job_title = title_el.get_text(strip=True)

    # Company name
    company_el = soup.find("a", {"data-cy": "companyNameLink"})
    if not company_el:
        company_el = soup.find("span", class_=re.compile(r"companyName"))
    if company_el:
        posting.company_name = company_el.get_text(strip=True)

    # Location
    location_el = soup.find("li", {"data-cy": "location"})
    if location_el:
        posting.location = location_el.get_text(strip=True)

    # Description
    desc_el = soup.find("div", {"data-testid": "jobDescriptionHtml"})
    if not desc_el:
        desc_el = soup.find("div", class_=re.compile(r"job-description"))
    if desc_el:
        posting.description_text = desc_el.get_text(separator="\n", strip=True)


def _parse_linkedin(soup: BeautifulSoup, posting: JobPosting) -> None:
    """Parse LinkedIn job posting (public/guest view)."""
    # Title
    title_el = soup.find("h1", class_=re.compile(r"top-card-layout__title"))
    if not title_el:
        title_el = soup.find("h1")
    if title_el:
        posting.job_title = title_el.get_text(strip=True)

    # Company
    company_el = soup.find("a", class_=re.compile(r"topcard__org-name-link"))
    if not company_el:
        company_el = soup.find("span", class_=re.compile(r"topcard__flavor"))
    if company_el:
        posting.company_name = company_el.get_text(strip=True)

    # Location
    location_el = soup.find("span", class_=re.compile(r"topcard__flavor--bullet"))
    if location_el:
        posting.location = location_el.get_text(strip=True)

    # Description
    desc_el = soup.find("div", class_=re.compile(r"show-more-less-html__markup"))
    if not desc_el:
        desc_el = soup.find("div", class_=re.compile(r"description__text"))
    if desc_el:
        posting.description_text = desc_el.get_text(separator="\n", strip=True)


def _parse_generic(soup: BeautifulSoup, posting: JobPosting) -> None:
    """Generic parser for company career pages and other job boards."""
    # Remove script and style elements
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # Try to find the job title from h1 or title tag
    h1 = soup.find("h1")
    if h1:
        posting.job_title = h1.get_text(strip=True)
    elif soup.title:
        posting.job_title = soup.title.get_text(strip=True)

    # Try to find company name from meta tags or structured data
    og_site = soup.find("meta", property="og:site_name")
    if og_site and og_site.get("content"):
        posting.company_name = og_site["content"]

    # Look for JSON-LD structured data
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            import json
            data = json.loads(script.string or "")
            if isinstance(data, list):
                data = data[0]
            if isinstance(data, dict):
                if data.get("@type") == "JobPosting":
                    posting.job_title = posting.job_title or data.get("title", "")
                    posting.description_text = data.get("description", "")
                    hiring_org = data.get("hiringOrganization", {})
                    if isinstance(hiring_org, dict):
                        posting.company_name = posting.company_name or hiring_org.get("name", "")
                    job_location = data.get("jobLocation", {})
                    if isinstance(job_location, dict):
                        address = job_location.get("address", {})
                        if isinstance(address, dict):
                            parts = [
                                address.get("addressLocality", ""),
                                address.get("addressRegion", ""),
                            ]
                            posting.location = ", ".join(p for p in parts if p)
                    base_salary = data.get("baseSalary", {})
                    if isinstance(base_salary, dict):
                        value = base_salary.get("value", {})
                        if isinstance(value, dict):
                            min_val = value.get("minValue", "")
                            max_val = value.get("maxValue", "")
                            if min_val and max_val:
                                posting.salary_range = f"${min_val:,} - ${max_val:,}" if isinstance(min_val, (int, float)) else f"{min_val} - {max_val}"
                            elif min_val:
                                posting.salary_range = str(min_val)
        except (json.JSONDecodeError, TypeError, KeyError):
            continue

    # Extract main content area
    main_content = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile(r"job|posting|description|content", re.I))
    if main_content:
        posting.description_text = posting.description_text or main_content.get_text(separator="\n", strip=True)
    else:
        body = soup.find("body")
        if body:
            posting.description_text = posting.description_text or body.get_text(separator="\n", strip=True)


def _extract_from_text(posting: JobPosting) -> None:
    """Extract structured fields from the raw description text."""
    text = posting.description_text
    if not text:
        return

    text_lower = text.lower()

    # Remote status detection
    if not posting.remote_status:
        if re.search(r"\bfully?\s*remote\b", text_lower):
            posting.remote_status = "Remote"
        elif re.search(r"\bhybrid\b", text_lower):
            posting.remote_status = "Hybrid"
        elif re.search(r"\bon[- ]?site\b|\bin[- ]?office\b", text_lower):
            posting.remote_status = "On-site"

    # Salary extraction
    if not posting.salary_range:
        salary_match = re.search(
            r"\$[\d,]+(?:\.\d{2})?\s*(?:[-\u2013]\s*\$[\d,]+(?:\.\d{2})?)?(?:\s*(?:per\s+)?(?:year|yr|annually|annual|hour|hr))?",
            text,
            re.IGNORECASE,
        )
        if salary_match:
            posting.salary_range = salary_match.group(0).strip()

    # Years of experience extraction
    if not posting.years_experience:
        exp_match = re.search(
            r"(\d+)\+?\s*(?:[-\u2013]\s*\d+\+?\s*)?years?\s*(?:of\s+)?(?:experience|exp)",
            text_lower,
        )
        if exp_match:
            posting.years_experience = exp_match.group(0).strip()

    # Certification extraction
    known_certs = [
        "CISSP", "CISM", "CISA", "CASP+", "CASP", "SecurityX",
        "Security+", "CompTIA Security+", "Network+", "CompTIA Network+",
        "CCNA", "CCNP", "CCIE", "CCSP",
        "AWS Certified", "AWS Solutions Architect", "AWS Security",
        "Azure", "AZ-500", "AZ-900", "AZ-104",
        "GCP", "Google Cloud",
        "CEH", "OSCP", "GIAC", "GSEC", "GCIH", "GPEN", "SSCP",
        "ITIL", "PMP", "CRISC",
        "CKA", "CKS", "CKAD",
        "DoD 8140", "DoD 8570",
    ]
    if not posting.required_certs:
        for cert in known_certs:
            if cert.lower() in text_lower:
                posting.required_certs.append(cert)

    # Extract bullet points as responsibilities/qualifications
    lines = text.split("\n")
    current_section = ""
    for line in lines:
        stripped = line.strip()
        stripped_lower = stripped.lower()

        # Detect section headers
        if re.match(r"^(responsibilities|duties|what you.?ll do|the role|key responsibilities)", stripped_lower):
            current_section = "responsibilities"
            continue
        elif re.match(r"^(requirements|qualifications|what we.?re looking|what you.?ll need|must have|minimum)", stripped_lower):
            current_section = "qualifications"
            continue
        elif re.match(r"^(preferred|nice to have|bonus|desired)", stripped_lower):
            current_section = "preferred"
            continue
        elif re.match(r"^(skills|technical skills|required skills)", stripped_lower):
            current_section = "skills"
            continue

        # Extract bullet items
        bullet_match = re.match(r"^[\u2022\u2023\u25e6\u2043\u2219*\-]\s*(.+)", stripped)
        if bullet_match:
            content = bullet_match.group(1).strip()
            if len(content) > 15:  # Skip very short fragments
                if current_section == "responsibilities":
                    posting.key_responsibilities.append(content)
                elif current_section in ("qualifications", "skills"):
                    posting.qualifications.append(content)
                elif current_section == "preferred":
                    posting.preferred_skills.append(content)

    # Extract skills from text (common technology keywords)
    if not posting.required_skills:
        skill_patterns = [
            r"\bPython\b", r"\bJava\b", r"\bAWS\b", r"\bAzure\b", r"\bGCP\b",
            r"\bDocker\b", r"\bKubernetes\b", r"\bTerraform\b", r"\bAnsible\b",
            r"\bCI/CD\b", r"\bJenkins\b", r"\bGitHub Actions\b",
            r"\bSIEM\b", r"\bSplunk\b", r"\bCrowdStrike\b", r"\bSentinelOne\b",
            r"\bIDS\b", r"\bIPS\b", r"\bFirewall\b",
            r"\bActive Directory\b", r"\bOkta\b", r"\bSAML\b", r"\bOAuth\b",
            r"\bNIST\b", r"\bISO 27001\b", r"\bSOC\s*2\b", r"\bPCI[- ]DSS\b",
            r"\bHIPAA\b", r"\bFedRAMP\b",
            r"\bZero Trust\b", r"\bIAM\b",
            r"\bLinux\b", r"\bWindows Server\b",
            r"\bWireshark\b", r"\bNmap\b", r"\bBurp Suite\b", r"\bMetasploit\b",
            r"\bPowerShell\b", r"\bBash\b",
            r"\bVPN\b", r"\bVLAN\b", r"\bTCP/IP\b", r"\bDNS\b",
            r"\bCloudFormation\b", r"\bSCIM\b", r"\bLDAP\b",
            r"\bEntra\s*ID\b", r"\bCyberArk\b", r"\bSailPoint\b",
        ]
        for pattern in skill_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                skill_name = re.sub(r"\\b", "", pattern).strip()
                posting.required_skills.append(skill_name)


def posting_to_dict(posting: JobPosting) -> dict:
    """Convert a JobPosting to a dictionary for serialization."""
    return {
        "url": posting.url,
        "job_title": posting.job_title,
        "company_name": posting.company_name,
        "location": posting.location,
        "remote_status": posting.remote_status,
        "salary_range": posting.salary_range,
        "years_experience": posting.years_experience,
        "required_skills": posting.required_skills,
        "preferred_skills": posting.preferred_skills,
        "required_certs": posting.required_certs,
        "key_responsibilities": posting.key_responsibilities,
        "qualifications": posting.qualifications,
        "description_text": posting.description_text,
    }
