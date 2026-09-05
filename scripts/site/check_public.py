#!/usr/bin/env python3
"""check_public.py: mechanical checks on the public portfolio files. Exit 1 on any hit.

Runs against a portfolio checkout (default ~/portfolio) and this repo. Files: index.html, views/*.html, README.md, sitemap.xml.
  1. OPSEC patterns: addresses, ports, internal hostnames, container and host names, local paths, cloud ids, long hex ids, phone numbers
  2. Writing and design tells: em and en dashes, middle dots, Inter, gradients, backdrop-filter, box-shadow outside a hover rule, buzzwords
  3. Every NIST 800-53 ID printed on the page has a row in SSP section 5
  4. Every repo path cited on the page (yaml, yml, tf, py, md, rego) exists on main (git ls-files)
  5. --links: every external href answers (2xx or 3xx; 429 and 999 accepted from LinkedIn)
These checks match patterns and compare sets. Anything that needs reading for meaning (a claim against the repo, a duplicated
section, a stale number) is a review job, not this script's.

Usage: python3 scripts/site/check_public.py [--portfolio PATH] [--links] [--links-only]
"""
import argparse, http.client, os, pathlib, re, subprocess, sys, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[2]
SSP = ROOT / "docs" / "grc" / "SSP_SYSTEM_SECURITY_PLAN.md"
FAMILIES = "AC|AT|AU|CA|CM|CP|IA|IR|MA|MP|PE|PL|PM|PS|PT|RA|SA|SC|SI|SR"
CONTROL_RE = re.compile(rf"\b(?:{FAMILIES})-\d+(?:\(\d+\))?\b")
PATH_RE = re.compile(r"(?<![\w/.@-])((?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.(?:yaml|yml|tf|py|md|rego))\b")
URL_RE = re.compile(r"""(?:href|src)=["'][^"']*["']|https?://[^\s"'<>)]+""")

# Documented gaps. Each entry is tracked in the site handoff; remove the entry when the gap closes.
KNOWN_CONTROL_GAPS = {"CA-8": "cited on the pen test card, no SSP row yet", "SA-12": "Rev 4 id cited on the supply chain card, SSP has no SR family yet", "SA-15": "cited on the SDLC card, no SSP row yet"}
KNOWN_PATH_GAPS = {"falco-rules/n8n-outbound.yaml": "Falco showcase card cites a path that is not in the repo; rule text lives in docs/grc/PLAYBOOK_COMPROMISED_CONTAINER.md"}

OPSEC = [
    ("ipv4", re.compile(r"\b(?!0\.0\.0\.0\b)\d{1,3}(?:\.\d{1,3}){3}\b")),
    ("port", re.compile(r"(?<![\w:])(?:localhost|127\.0\.0\.1|[a-z0-9.-]+):\d{4,5}\b")),
    ("internal hostname", re.compile(r"\b[a-z0-9-]+\.tigouetheory\.com\b")),
    ("container or host name", re.compile(r"\b(?:cd-service|tunnel-cyber-squire|cd-alpha|cd-oci(?!-infrastructure))\b")),
    ("local path", re.compile(r"(?:/Users/|/opt/|/root/|/home/[a-z])")),
    ("cloud id", re.compile(r"\bocid1\.|\barn:aws:|\b\d{12}\b")),
    ("long hex id", re.compile(r"\b[0-9a-f]{32,}\b|\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")),
    ("phone", re.compile(r"(?<!\d)\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)")),
]
TELLS = [
    ("em dash", re.compile("—")), ("en dash", re.compile("–")), ("middle dot", re.compile("·")),
    ("Inter font", re.compile(r"font-family:[^;\"']*\bInter\b|['\"]Inter['\"]")),
    ("gradient", re.compile(r"\b(?:linear|radial|conic)-gradient\(|<(?:linear|radial)Gradient\b")),
    ("backdrop-filter", re.compile(r"backdrop-filter")),
    ("buzzword", re.compile(r"\b(?:seamless(?:ly)?|robust|leverag(?:e|es|ed|ing)|elegant|cutting-edge|empower(?:s|ed|ing)?|unlock(?:s|ed|ing)?\s+(?:the\s+)?(?:value|potential|power)|supercharge|delve|tapestry|synergy|holistic|state-of-the-art)\b", re.I)),
]
BOX_SHADOW = re.compile(r"box-shadow")

def files(pf):
    out = [pf / "index.html", pf / "README.md", pf / "sitemap.xml"] + sorted((pf / "views").glob("*.html"))
    return [f for f in out if f.exists()]

def hits(pattern, text, allow=None):
    """(line number, match, context) per hit; allow(match, line, rule) skips a hit, rule = the last line that opened a CSS block."""
    out, rule = [], ""
    for n, line in enumerate(text.splitlines(), 1):
        if "{" in line: rule = line
        for m in pattern.finditer(line):
            if allow and allow(m.group(0), line, rule): continue
            out.append((n, m.group(0), line.strip()[:110]))
    return out

def ssp_ids():
    text = SSP.read_text(encoding="utf-8")
    start = text.index("\n## 5."); end = text.index("\n## 6.", start)
    return set(re.findall(r"^\| \**((?:%s)-\d+(?:\(\d+\))?)\**" % FAMILIES, text[start:end], re.M))

def tracked():
    return set(subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n"))

def strip_urls(text):
    return URL_RE.sub(" ", text)

def host_of(url):
    return (urllib.parse.urlsplit(url).hostname or "").lower()

def on_domain(url, domain):
    h = host_of(url); return h == domain or h.endswith("." + domain)

def fetch_status(url):
    """Status code for an http(s) URL, HEAD then GET, no redirects followed (3xx counts as answered)."""
    u = urllib.parse.urlsplit(url)
    if u.scheme not in ("http", "https") or not u.hostname: return "error: not http(s)"
    conn_cls = http.client.HTTPSConnection if u.scheme == "https" else http.client.HTTPConnection
    path = (u.path or "/") + (("?" + u.query) if u.query else "")
    code = None
    for method in ("HEAD", "GET"):
        try:
            conn = conn_cls(u.hostname, u.port, timeout=20)
            conn.request(method, path, headers={"User-Agent": "Mozilla/5.0 (portfolio link check)", "Host": u.netloc})
            code = conn.getresponse().status; conn.close()
            if 200 <= code < 400: break
        except Exception as e:
            code = f"error: {e.__class__.__name__}"
    return code

def check_links(pf):
    urls = set()
    for f in files(pf):
        t = f.read_text(encoding="utf-8")
        urls.update(re.findall(r"""href=["'](https?://[^"']+)["']""", t))
        urls.update(re.findall(r"<loc>(https?://[^<]+)</loc>", t))
    urls = sorted(u for u in urls if re.search(r"https?://[^/]+/.+", u))  # skip bare preconnect origins
    bad = []
    for u in urls:
        code = fetch_status(u)
        ok = isinstance(code, int) and (200 <= code < 400 or (on_domain(u, "linkedin.com") and code in (429, 999)))
        if not ok: bad.append((u, code))
    return len(urls), bad

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--portfolio", default=os.path.expanduser("~/portfolio"))
    ap.add_argument("--links", action="store_true"); ap.add_argument("--links-only", action="store_true")
    a = ap.parse_args(); pf = pathlib.Path(a.portfolio); fails = 0
    if not (pf / "index.html").exists(): print(f"config error: no index.html under {pf}", file=sys.stderr); sys.exit(2)
    if not a.links_only:
        ids, repo = ssp_ids(), tracked()
        for f in files(pf):
            text = f.read_text(encoding="utf-8"); rel = f.relative_to(pf)
            # 1. OPSEC over the whole file, Credly badge ids excluded from the hex check
            for name, pat in OPSEC:
                allow = (lambda m, line, rule: any(on_domain(h, "credly.com") for h in re.findall(r'href="([^"]+)"', line))) if name == "long hex id" else None
                for n, m, ctx in hits(pat, text, allow): print(f"FAIL opsec {name}: {rel}:{n}: {m}   | {ctx}"); fails += 1
            # 2. tells over the whole file; box-shadow allowed only on a hover rule (brand-motion exception)
            # brand-motion exception (ROE 2026-09-05): the cursor glow gradient and the hover glow shadow stay
            for name, pat in TELLS:
                allow = (lambda m, line, rule: "glow" in rule) if name == "gradient" else None
                for n, m, ctx in hits(pat, text, allow): print(f"FAIL tell {name}: {rel}:{n}: {m}   | {ctx}"); fails += 1
            for n, m, ctx in hits(BOX_SHADOW, text, lambda m, line, rule: ":hover" in line): print(f"FAIL tell box-shadow outside hover: {rel}:{n}   | {ctx}"); fails += 1
            if f.suffix != ".html": continue
            # 3. control ids
            for cid in sorted(set(CONTROL_RE.findall(text))):
                if cid in ids: continue
                if cid in KNOWN_CONTROL_GAPS: print(f"known gap control {cid} on {rel}: {KNOWN_CONTROL_GAPS[cid]}"); continue
                print(f"FAIL control {cid} on {rel} has no row in SSP section 5"); fails += 1
            # 4. repo paths
            for p in sorted(set(PATH_RE.findall(strip_urls(text)))):
                base = p.rsplit("/", 1)[-1]
                if p in repo or ("/" not in p and any(t.endswith("/" + base) or t == base for t in repo)): continue
                if p in KNOWN_PATH_GAPS: print(f"known gap path {p} on {rel}: {KNOWN_PATH_GAPS[p]}"); continue
                print(f"FAIL path {p} cited on {rel} is not tracked on main"); fails += 1
        print(f"checks 1-4: {'ok' if not fails else str(fails) + ' hit(s)'} over {len(files(pf))} files")
    if a.links or a.links_only:
        n, bad = check_links(pf)
        for u, code in bad: print(f"FAIL link {code}: {u}"); fails += 1
        print(f"check 5 links: {n} urls, {len(bad)} failing")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
