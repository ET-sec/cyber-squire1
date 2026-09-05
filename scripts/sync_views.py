#!/usr/bin/env python3
"""sync_views.py: publish the architecture views into the portfolio site.

Source of truth: docs/architecture/views/<slug>.html (listed in views.yaml).
Targets in the portfolio repo:
  views/<slug>.html                 standalone page (viewport, CSP, back link added)
  index.html  <!-- VIEW:slug -->...<!-- /VIEW -->   inline figure (svg + caption)

Usage:
  python3 scripts/sync_views.py            # dry run, report drift
  python3 scripts/sync_views.py --apply    # write targets
  python3 scripts/sync_views.py --check    # exit 1 on drift (CI)
Options: --portfolio PATH (default ~/portfolio)
"""
import argparse, html, os, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
VIEWS = ROOT / "docs" / "architecture" / "views"
FLOW_CSS = """.cd-packet { pointer-events: none; opacity: .9; stroke-dashoffset: var(--cdlen); }
@keyframes cdpacket { to { stroke-dashoffset: 0; } }
@media (prefers-reduced-motion: reduce) { .cd-packet { display: none; } }"""
FLOW_JS = """// ANIMATED FLOW: packets ride every arrow in the architecture views
(function() {
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.querySelectorAll('.cd-view-frame svg, figure > svg').forEach(function(svg) {
    svg.querySelectorAll('line[marker-end], path[marker-end], polyline[marker-end]').forEach(function(el, i) {
      var len = el.getTotalLength ? el.getTotalLength() : 0; if (!len || len < 24) return;
      var c = el.cloneNode(false);
      ['marker-end', 'marker-start', 'stroke-dasharray', 'id'].forEach(function(a) { c.removeAttribute(a); });
      c.setAttribute('class', 'cd-packet');
      c.setAttribute('stroke-width', String(parseFloat(el.getAttribute('stroke-width') || '1.5') + 1.2));
      c.setAttribute('stroke-linecap', 'round');
      c.setAttribute('stroke-dasharray', '5 ' + Math.ceil(len + 5));
      c.style.setProperty('--cdlen', String(Math.ceil(len + 10)));
      c.style.animation = 'cdpacket ' + Math.max(1.8, len / 80).toFixed(2) + 's linear ' + (-(i % 9) * 0.4).toFixed(2) + 's infinite';
      el.parentNode.insertBefore(c, el.nextSibling);
    });
  });
})();"""
CSP = ("default-src 'self'; script-src 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
       "font-src https://fonts.gstatic.com; img-src 'self' data:; base-uri 'none';")

def manifest():
    views, cur = [], None
    for line in (VIEWS / "views.yaml").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*-\s*slug:\s*(\S+)", line)
        if m:
            cur = {"slug": m.group(1)}; views.append(cur); continue
        m = re.match(r"^\s+(title|generator|section):\s*(.*)$", line)
        if m and cur is not None:
            cur[m.group(1)] = m.group(2).strip()
    for v in views:
        assert {"title", "generator"} <= v.keys(), f"views.yaml: {v['slug']} is missing title or generator"
    return [(v["slug"], v["title"]) for v in views]

def parse(slug):
    src = (VIEWS / f"{slug}.html").read_text(encoding="utf-8")
    assert "</style>" in src and "<title>" in src and 'class="tag"' in src, f"{slug}.html: missing head anchors"
    head_end = src.index("</style>") + len("</style>")
    head, body = src[:head_end], src[head_end:]
    m_sub = re.search(r'<div class="head">.*?<p>(.*?)</p>', body, re.S); assert m_sub, f"{slug}.html: no head subtitle"
    m_svg = re.search(r"<svg.*?</svg>", body, re.S); assert m_svg, f"{slug}.html: no <svg>"
    m_cap = re.search(r"<figcaption>(.*?)</figcaption>", body, re.S); assert m_cap, f"{slug}.html: no <figcaption>"
    return head, body, m_sub.group(1).strip(), m_svg.group(0), m_cap.group(1).strip()

def standalone(slug, title, head, body):
    head = head.replace("<title>", '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
                        f'<meta http-equiv="Content-Security-Policy" content="{CSP}">\n<link rel="icon" href="../favicon.svg">\n<title>', 1)
    extra = ("\n  .head .back{margin-left:18px;font-family:var(--mono);font-size:12px;color:var(--green);text-decoration:none;letter-spacing:.02em;display:inline-block;padding:12px 0}"
             "\n  .head .back:hover{text-decoration:underline}"
             "\n  @media (max-width:900px){svg{max-height:none;min-width:1100px} figure{overflow-x:auto;-webkit-overflow-scrolling:touch} .head{gap:6px 14px} .head p::after{content:\". Scroll sideways to see the whole drawing.\";color:var(--bone)}}"
             "\n  @media (max-width:600px){figcaption{grid-template-columns:1fr}}\n")
    head = head.replace("</style>", extra + FLOW_CSS + "\n</style>")
    body = re.sub(r'(<span class="tag">[^<]*</span>)', r'\1<a class="back" href="../#view-' + slug + '">Back to portfolio</a>', body, count=1)
    return f'<!doctype html>\n<html lang="en">\n<head>\n{head}\n</head>\n<body>{body}\n<script>\n{FLOW_JS}\n</script>\n</body>\n</html>\n'

def figure(slug, title, sub, svg, cap):
    href = f"views/{slug}.html"
    sub_clean = re.sub(r",?\s*sanitized,\s*no [a-z, ]+$", "", sub)
    # six views share marker ids (m-green, m-red, ...); prefix per view so one page holds them all
    svg = svg.replace('id="m-', f'id="m-{slug}-').replace('url(#m-', f'url(#m-{slug}-')
    return (f'<!-- VIEW:{slug} -->\n<figure class="cd-view" id="view-{slug}">\n'
            f'  <div class="cd-view-head"><h3 class="cd-view-title">{html.escape(title)}</h3>'
            f'<span class="cd-view-sub">{sub_clean}</span>'
            f'<a class="cd-view-open" href="{href}">Open full view</a></div>\n'
            f'  <a class="cd-view-frame" href="{href}" aria-label="Open the {html.escape(title.lower())} view full size">\n{svg}\n  </a>\n'
            f'  <figcaption class="cd-view-cap">\n{cap}\n  </figcaption>\n</figure>\n<!-- /VIEW -->')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true"); ap.add_argument("--check", action="store_true")
    ap.add_argument("--portfolio", default=os.path.expanduser("~/portfolio"))
    a = ap.parse_args()
    pf = pathlib.Path(a.portfolio); index = pf / "index.html"
    views = manifest()
    missing = [slug for slug, _ in views if not (VIEWS / f"{slug}.html").exists()]
    if missing or not index.exists():
        print(f"config error: missing rendered view(s) {missing} or index {index}", file=sys.stderr); sys.exit(2)
    if a.check: a.apply = False
    site = index.read_text(encoding="utf-8"); drift = 0
    if a.apply: (pf / "views").mkdir(exist_ok=True)
    for slug, title in views:
        head, body, sub, svg, cap = parse(slug)
        page = standalone(slug, title, head, body); target = pf / "views" / f"{slug}.html"
        if not target.exists() or target.read_text(encoding="utf-8") != page:
            drift += 1; print(f"drift: views/{slug}.html")
            if a.apply: target.write_text(page, encoding="utf-8")
        block = figure(slug, title, sub, svg, cap)
        pat = re.compile(rf"<!-- VIEW:{re.escape(slug)} -->.*?<!-- /VIEW -->", re.S)
        m = pat.search(site)
        if not m:
            print(f"missing marker in index.html: <!-- VIEW:{slug} -->"); drift += 1; continue
        if m.group(0) != block:
            drift += 1; print(f"drift: index.html VIEW:{slug}")
            site = site[:m.start()] + block + site[m.end():]
    if a.apply and site != index.read_text(encoding="utf-8"):
        index.write_text(site, encoding="utf-8")
    print(f"summary: {len(views)} views, {drift} drift(s){' written' if a.apply else ''}")
    if a.check and drift: sys.exit(1)

if __name__ == "__main__":
    main()
