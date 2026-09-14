#!/usr/bin/env python3
"""sitemap.py — site/sitemap.xml and site/robots.txt, drawn from the built tree.

    python scripts/sitemap.py        -> site/sitemap.xml, site/robots.txt

**The list is whatever pages `site/` holds, read after every builder has run**, so it
is RENDER's last writer before the verify step and never a list anyone keeps. A page
is in it under its own `rel="canonical"` address. A page whose canonical names some
other address is a copy or a redirect and is left out — `site/method/` is the one
today. A page with no canonical is listed at the address its path gives it.

**HTML only.** The dated PDFs and CSVs are served from R2 and are not in the tree
(RENDER Step 6b); the pages that offer them are listed and a crawler follows the link.

**No `<lastmod>`.** A render rewrites pages whose content has not moved, so a file's
mtime would say *changed* every day, and a crawler that finds lastmod unreliable
ignores it anyway. Leaving it out is the honest version.

**Both files are written only when their bytes change**, so a render that added no
page adds nothing to the commit. `robots.txt` lives here rather than as a hand-kept
file because `site/` is generated end to end (`site/README.md`). It carries the
`Sitemap:` line and nothing else: Cloudflare prepends its managed block, crawler
rules included, so a `User-agent` group here would repeat Cloudflare's.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
SITE_BASE = "https://corpus.data-landscapers.io"

CANONICAL = re.compile(r'<link\s+rel="canonical"\s+href="([^"]+)"', re.I)
REFRESH = re.compile(r'<meta\s+http-equiv="refresh"', re.I)
NOINDEX = re.compile(r'<meta\s+name="robots"\s+content="[^"]*noindex', re.I)


def own_url(page: Path) -> str:
    rel = page.relative_to(SITE).as_posix()
    if rel == "index.html":
        return f"{SITE_BASE}/"
    if rel.endswith("/index.html"):
        return f"{SITE_BASE}/{rel[:-len('index.html')]}"
    return f"{SITE_BASE}/{rel}"


def urls() -> tuple[list[str], list[str]]:
    listed, skipped = [], []
    for page in sorted(SITE.rglob("*.html")):
        head = page.read_text(encoding="utf-8", errors="replace")[:8000]
        url = own_url(page)
        m = CANONICAL.search(head)
        if REFRESH.search(head) or NOINDEX.search(head) or (m and m.group(1) != url):
            skipped.append(page.relative_to(SITE).as_posix())
            continue
        listed.append(url)
    return listed, skipped


def write_if_changed(path: Path, text: str) -> bool:
    if path.exists() and path.read_bytes() == text.encode("utf-8"):
        return False
    path.write_bytes(text.encode("utf-8"))
    return True


def main() -> int:
    listed, skipped = urls()
    if not listed:
        print("sitemap: no pages under site/ — nothing written", file=sys.stderr)
        return 1
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "".join(f"  <url><loc>{escape(u)}</loc></url>\n" for u in listed)
           + "</urlset>\n")
    robots = f"Sitemap: {SITE_BASE}/sitemap.xml\n"
    wrote = [name for name, text in (("sitemap.xml", xml), ("robots.txt", robots))
             if write_if_changed(SITE / name, text)]
    print(f"sitemap: {len(listed)} pages, {len(skipped)} left out ({', '.join(skipped) or 'none'})"
          f" — {'wrote ' + ', '.join(wrote) if wrote else 'unchanged'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
