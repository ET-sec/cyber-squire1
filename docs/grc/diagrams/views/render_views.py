#!/usr/bin/env python3
"""Regenerate every architecture view listed in views.yaml.

Each gen_<slug>.py holds the view's data (nodes, arrows, labels) and writes
<slug>.html beside itself. topology.html is hand-authored (generator: null).
Run from anywhere: python3 docs/grc/diagrams/views/render_views.py
"""
import re, subprocess, sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent

def manifest():
    views, cur = [], None
    for line in (HERE / "views.yaml").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*-\s*slug:\s*(\S+)", line)
        if m:
            cur = {"slug": m.group(1)}; views.append(cur); continue
        m = re.match(r"^\s+(title|generator|section):\s*(.*)$", line)
        if m and cur is not None:
            cur[m.group(1)] = m.group(2).strip()
    for v in views:
        assert {"title", "generator"} <= v.keys(), f"views.yaml: {v['slug']} is missing title or generator"
    return views

rc = 0
for v in manifest():
    slug, gen = v["slug"], v["generator"]
    out = HERE / f"{slug}.html"
    if gen == "null":
        print(f"{slug:24} hand-authored  {'ok' if out.exists() else 'MISSING'}")
        rc |= 0 if out.exists() else 1
        continue
    before = out.stat().st_mtime_ns if out.exists() else -1
    r = subprocess.run([sys.executable, str(HERE / gen)], capture_output=True, text=True)
    ok = r.returncode == 0 and out.exists() and out.stat().st_mtime_ns != before
    print(f"{slug:24} {gen:32} {'ok' if ok else 'FAILED'}")
    if not ok:
        print(r.stdout, r.stderr); rc = 1
sys.exit(rc)
