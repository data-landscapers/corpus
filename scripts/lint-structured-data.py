#!/usr/bin/env python3
"""lint-structured-data.py — the `application/ld+json` block on every report, checked.

RENDER Step 7, beside `lint-external-links.py`, and for the same reason: this is a page-wide
property that nothing else asserts and that no one will ever notice going wrong. A structured
data block is invisible on the page, invisible in the PDF and invisible in a diff anyone reads
— the only consumer is a crawler, and a crawler does not report back. `render.py` builds it
from the document's own facts, so the failures worth catching are the ones where those facts
and the block stop agreeing.

**What it asserts, and why each one:**

- **Every report carries a block, and it is valid JSON.** A `</script` in a title would end the
  element early and spill the rest onto the page as text; `render.py` escapes `</` against
  exactly that, and this is the test that the escape is still there.
- **`datePublished` is a date.** An edition may be `2026-09-16-2` (design.md §9) and that is
  not one. Emitted raw it is invalid structured data on whichever handful of documents moved
  twice in a day — a silent failure on a rotating subset, which is the worst kind.
- **`datePublished` equals `dateModified`.** §9's *a published edition is never revised*, stated
  in the vocabulary a crawler reads. If these ever disagree, either §9 broke or the builder did.
- **`url`, `mainEntityOfPage` and the page's own `<link rel=canonical>` are one address.** Three
  claims about where this document lives, from two builders; a crawler that gets two answers
  picks one, and it is not always ours.
- **The description in the block is the description in the meta tag.** They are built from one
  string in `render.py` and this is what keeps them that way — a document that says two
  different things about itself to two readers of the same page has no defensible version.
- **`headline` is at most 110 characters**, which is the length search engines truncate at.
- **`encoding` names a PDF the page itself offers.** A document rendered without a PDF must not
  advertise one — the same rule the download button and the `This file` row follow.
- **The three corpus subjects are still there**, in order, after the document's own. They are
  what the block is for: the reports are about digital transformation, digital public
  infrastructure and data governance, and before 2026-09-20 no page said so anywhere a machine
  could read it.

Nothing here is a style opinion. Every assertion is *this page disagrees with itself* or *this
value is not the type it claims to be*, which is what makes a finding here worth stopping for.

    python scripts/lint-structured-data.py     # 0 clean · 1 findings
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
SITE = CORPUS / "site"

BLOCK = re.compile(r'<script type="application/ld\+json">\n(.*?)\n</script>', re.S)
CANONICAL = re.compile(r'<link rel="canonical" href="([^"]+)"')
DESCRIPTION = re.compile(r'<meta name="description" content="([^"]*)"')
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# A page is expected to carry a block if it is a rendered document. Everything else on the site
# — the country pages, the catalogue, the methodology — is built by another script and has none
# yet; this lints what exists rather than demanding what was never written.
DOCUMENT = re.compile(r"^(reports/[^/]+/[^/]+|topics/[^/]+/[^/]+-(monthly|progress)|bulletin/index)\.html$")

REQUIRED = ("@context", "@type", "headline", "description", "url",
            "datePublished", "dateModified", "author", "publisher", "about")

SUBJECTS = ["Digital transformation", "Digital public infrastructure", "Data governance"]


def unescape(s: str) -> str:
    """The two entities `render.py`'s `attr()` writes, back to the characters they stand for."""
    return s.replace("&quot;", '"').replace("&amp;", "&")


def check(rel: str, html: str) -> list[str]:
    """Every finding on one page."""
    out: list[str] = []
    m = BLOCK.search(html)
    if m is None:
        return [f"{rel}: no structured data block"]
    try:
        d = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        return [f"{rel}: block is not valid JSON ({e})"]

    def fail(msg: str) -> None:
        out.append(f"{rel}: {msg}")

    for key in REQUIRED:
        if not d.get(key):
            fail(f"missing {key}")
    if out:                                   # no point testing values that are not there
        return out

    today = date.today().isoformat()
    for key in ("datePublished", "dateModified"):
        if not ISO.match(d[key]):
            fail(f"{key} is not a date: {d[key]!r} — an edition's same-day suffix is not one")
        elif d[key] > today:
            fail(f"{key} is in the future: {d[key]}")
    if d["datePublished"] != d["dateModified"]:
        fail(f"datePublished {d['datePublished']} != dateModified {d['dateModified']} — "
             f"a published edition is not revised (design.md §9)")

    if d["url"] != d.get("mainEntityOfPage", {}).get("@id"):
        fail(f"url {d['url']} != mainEntityOfPage {d.get('mainEntityOfPage')}")
    canon = CANONICAL.search(html)
    if canon and canon.group(1) != d["url"]:
        fail(f"url {d['url']} != canonical {canon.group(1)}")

    meta = DESCRIPTION.search(html)
    if meta and unescape(meta.group(1)) != d["description"]:
        fail("description in the block is not the description in the meta tag")

    if len(d["headline"]) > 110:
        fail(f"headline is {len(d['headline'])} characters; search truncates at 110")

    # **Against the page with the block cut out of it.** Tested against the whole page this
    # asserts nothing at all: the URL is inside the block, the block is inside the page, so
    # `contentUrl in html` is true however wrong the URL is. What is being asked is whether the
    # *document* offers that file — the download button and the `This file` row — and those are
    # the part of the page the block is not.
    pdf = (d.get("encoding") or {}).get("contentUrl")
    if pdf and pdf not in html[:m.start()] + html[m.end():]:
        fail(f"encoding names {pdf}, which the page itself does not offer")

    names = [a.get("name") for a in d["about"]]
    if names[1:] != SUBJECTS:
        fail(f"about does not end in the corpus subjects: {names[1:]}")
    if not names[:1] or not names[0]:
        fail("about names no place or subject of its own")

    return out


def main() -> int:
    pages = sorted(SITE.rglob("*.html"))
    documents = [p for p in pages if DOCUMENT.match(p.relative_to(SITE).as_posix())]
    findings: list[str] = []
    for p in documents:
        findings += check(p.relative_to(SITE).as_posix(), p.read_text(encoding="utf-8"))

    # A page outside the document set that carries a block is linted too rather than skipped:
    # another builder growing one is the moment to start holding it to the same rules, and
    # silently ignoring it is how the second implementation gets away with disagreeing.
    others = [p for p in pages
              if p not in documents and BLOCK.search(p.read_text(encoding="utf-8"))]
    for p in others:
        findings += check(p.relative_to(SITE).as_posix(), p.read_text(encoding="utf-8"))

    print(f"lint-structured-data: {len(documents)} document page(s)"
          + (f", {len(others)} other page(s) with a block" if others else ""))
    if not documents:
        print("  nothing to check — has the site been rendered?")
        return 1
    if findings:
        print(f"  {len(findings)} finding(s):")
        for f in findings:
            print(f"    {f}")
        return 1
    print("  ok — every document describes itself, and agrees with itself")
    return 0


if __name__ == "__main__":
    sys.exit(main())
