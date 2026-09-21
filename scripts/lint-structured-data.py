#!/usr/bin/env python3
"""lint-structured-data.py — the `application/ld+json` block on every page that carries one.

RENDER Step 7, beside `lint-external-links.py`, and for the same reason: this is a page-wide
property that nothing else asserts and that no one will ever notice going wrong. A structured
data block is invisible on the page, invisible in the PDF and invisible in a diff anyone reads
— the only consumer is a crawler, and a crawler does not report back. The builders write it
from each page's own facts, so the failures worth catching are the ones where those facts and
the block stop agreeing.

**Two shapes, dispatched on `@type`.** A document — report, update or bulletin — from
`render.py`; a `Dataset` — the catalogue and each place's cut of it — from `catalogue.py` and
`country.py`. Both go through `structured_data.py`, and a third shape appearing here without
one is the finding that matters most: it means a builder has grown its own implementation.

**What it asserts, and why each one:**

- **Every rendered document carries a block, and it is valid JSON.** A `</script` in a title
  would end the element early and spill the rest onto the page as text; `structured_data.block`
  escapes `</` against exactly that, and this is the test that the escape is still there.
- **`datePublished` is a date.** An edition may be `2026-09-16-2` (design.md §9) and that is
  not one. Emitted raw it is invalid structured data on whichever handful of documents moved
  twice in a day — a silent failure on a rotating subset, which is the worst kind.
- **`datePublished` equals `dateModified`** on a document: §9's *a published edition is never
  revised*, in the vocabulary a crawler reads.
- **`url`, `mainEntityOfPage` and the page's `<link rel=canonical>` are one address.** Three
  claims about where this page lives, from two builders; a crawler given two answers picks
  one, and it is not always ours.
- **The description in a document's block is the description in its meta tag.** They are built
  from one string and this is what keeps them that way.
- **A download the block names is a download the page offers, at the size it really is.** The
  filename is checked against the page with the block cut out — inside it, the URL would match
  itself, and a page links its own downloads relatively — and the `contentSize` against the
  file on disk. A dataset entry whose size is a build old is the kind of wrong nothing else on
  the site would ever surface.
- **A dataset says what is in it**: `variableMeasured` from the published field dictionary, a
  `temporalCoverage` that runs forwards, a `spatialCoverage` with a name, and a description
  inside the 50–5,000 characters a dataset search will accept.
- **A slice says whose slice it is.** `isPartOf` on a place cut must name a dataset `@id` that
  something on this site actually publishes, or 62 place cuts are 62 unrelated tables that
  share a schema — the shape that gets a site's entries suppressed rather than listed.

Nothing here is a style opinion. Every assertion is *this page disagrees with itself*, *this
page disagrees with another page* or *this value is not the type it claims to be*.

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
SITE_BASE = "https://corpus.data-landscapers.io"

BLOCK = re.compile(r'<script type="application/ld\+json">\n(.*?)\n</script>', re.S)
CANONICAL = re.compile(r'<link rel="canonical" href="([^"]+)"')
DESCRIPTION = re.compile(r'<meta name="description" content="([^"]*)"')
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# A `temporalCoverage` bound: a whole year or a day. The catalogue's records carry publication
# dates and span days; the finance table is dated to the year a commitment was approved and no
# finer, and padding that to a January the 1st would invent a precision the source lacks.
BOUND = re.compile(r"^\d{4}(-\d{2}-\d{2})?$")

EDITION = re.compile(r"^\d{4}-\d{2}-\d{2}(-\d+)?$")

# A dated edition (design.md §9) — `…-2026-09-18.csv`, or `-2` where two were cut in a day.
# These are pruned out of the tree once R2 has them, so their absence here is a successful
# sync rather than a missing file. An undated download is served from this tree and must be in
# it.
EDITION_FILE = re.compile(r"-\d{4}-\d{2}-\d{2}(-\d+)?\.[a-z]+$")

# The page's own record of the dated artefact it is offering: `stem|edition|digest`.
ARTEFACT = re.compile(r'<meta name="dl-artefact" content="([^"|]+)\|([^"|]+)\|([0-9a-f]+)">')

# The two whole datasets a cut may be part of: the document catalogue and the finance table.
PARENTS = {f"{SITE_BASE}/catalogue/#dataset", f"{SITE_BASE}/finance/#dataset"}

# The pages `render.py` writes — the ones that must carry a document block. Everything else is
# linted if it has one and not demanded to have one: the finance pages publish dated CSVs and
# have no block yet, and a linter that failed over work nobody has done is a linter that gets
# switched off.
DOCUMENT_PAGE = re.compile(
    r"^(reports/[^/]+/[^/]+|topics/[^/]+/[^/]+-(monthly|progress)|bulletin/index)\.html$")

DOC_REQUIRED = ("@context", "@type", "headline", "description", "url",
                "datePublished", "dateModified", "author", "publisher", "about")
SET_REQUIRED = ("@context", "@type", "@id", "name", "description", "url", "license",
                "creator", "publisher", "distribution", "dateModified")

SUBJECTS = ["Digital transformation", "Digital public infrastructure", "Data governance"]

# Google Dataset Search will not index a description outside this range, and a `Dataset` whose
# description is three words is not describing anything.
DESC_MIN, DESC_MAX = 50, 5000


def unescape(s: str) -> str:
    """The two entities `render.py`'s `attr()` writes, back to what they stand for."""
    return s.replace("&quot;", '"').replace("&amp;", "&")


def local_path(url: str) -> Path | None:
    """The file on disk a site URL names, or None if it is not one of ours."""
    if not url.startswith(SITE_BASE + "/"):
        return None
    return SITE / url[len(SITE_BASE) + 1:]


def size_label(n_bytes: int) -> str:
    """`structured_data.size_label`, restated — deliberately, because a linter that imports the
    thing it is checking cannot catch that thing changing. If these two ever disagree the build
    is wrong or this is, and either is worth knowing."""
    return f"{n_bytes / 1e6:.1f} MB" if n_bytes >= 1e6 else f"{n_bytes / 1e3:.0f} KB"


def check(rel: str, html: str) -> list[str]:
    """Every finding on one page."""
    m = BLOCK.search(html)
    if m is None:
        return [f"{rel}: no structured data block"]
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        return [f"{rel}: block is not valid JSON ({e})"]

    out: list[str] = []
    outside = html[:m.start()] + html[m.end():]
    types = data.get("@type") or []
    types = [types] if isinstance(types, str) else list(types)

    def fail(msg: str) -> None:
        out.append(f"{rel}: {msg}")

    # The page's own address, asserted once for either shape.
    canon = CANONICAL.search(html)
    if canon and data.get("url") and canon.group(1) != data["url"]:
        fail(f"url {data['url']} != canonical {canon.group(1)}")

    if "Dataset" in types:
        out += check_dataset(rel, data, outside)
    elif {"Article", "Report", "NewsArticle"} & set(types):
        out += check_document(rel, data, html, outside)
    else:
        fail(f"@type {types} is neither a document nor a Dataset — has a builder grown its "
             f"own structured data instead of using structured_data.py?")
    return out


def check_document(rel: str, d: dict, html: str, outside: str) -> list[str]:
    """`html` is the whole page, for the meta tag; `outside` is the page with the block
    cut out, for the download check — which asserts nothing at all against the whole page,
    because the URL it is looking for is inside the block it came from."""
    out: list[str] = []

    def fail(msg: str) -> None:
        out.append(f"{rel}: {msg}")

    for key in DOC_REQUIRED:
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

    meta = DESCRIPTION.search(html)
    if meta and unescape(meta.group(1)) != d["description"]:
        fail("description in the block is not the description in the meta tag")

    if len(d["headline"]) > 110:
        fail(f"headline is {len(d['headline'])} characters; search truncates at 110")

    names = [a.get("name") for a in d["about"]]
    if names[1:] != SUBJECTS:
        fail(f"about does not end in the corpus subjects: {names[1:]}")
    if not names[0]:
        fail("about names no place or subject of its own")

    out += check_downloads(rel, [d["encoding"]] if d.get("encoding") else [], outside)
    return out


def check_dataset(rel: str, d: dict, outside: str) -> list[str]:
    out: list[str] = []

    def fail(msg: str) -> None:
        out.append(f"{rel}: {msg}")

    for key in SET_REQUIRED:
        if not d.get(key):
            fail(f"missing {key}")
    if out:
        return out

    if d["@id"] != d["url"] + "#dataset":
        fail(f"@id {d['@id']} is not the landing page's dataset id ({d['url']}#dataset)")

    n = len(d["description"])
    if not DESC_MIN <= n <= DESC_MAX:
        fail(f"description is {n} characters; a dataset search takes {DESC_MIN}–{DESC_MAX}")

    if not ISO.match(d["dateModified"]):
        fail(f"dateModified is not a date: {d['dateModified']!r}")
    elif d["dateModified"] > date.today().isoformat():
        fail(f"dateModified is in the future: {d['dateModified']}")

    tc = d.get("temporalCoverage")
    if tc:
        parts = tc.split("/")
        if len(parts) != 2 or not all(BOUND.match(p) for p in parts):
            fail(f"temporalCoverage is not a date interval: {tc!r}")
        elif parts[0][:4] > parts[1][:4] or (parts[0][:4] == parts[1][:4]
                                             and parts[0] > parts[1]):
            fail(f"temporalCoverage runs backwards: {tc}")

    sc = d.get("spatialCoverage") or {}
    if not sc.get("name"):
        fail("spatialCoverage names no place")
    if sc.get("@type") != "Place":
        fail(f"spatialCoverage is a {sc.get('@type')} — Google's Dataset validator accepts "
             f"only Place and reports a subtype as an invalid object type")
    if not d.get("variableMeasured"):
        fail("variableMeasured describes no columns — is the field dictionary missing?")
    else:
        blank = [v for v in d["variableMeasured"] if not v.get("name") or not v.get("description")]
        if blank:
            fail(f"{len(blank)} column(s) in variableMeasured have no name or no definition")

    missing = [s for s in SUBJECTS if s not in (d.get("keywords") or [])]
    if missing:
        fail(f"keywords do not name the corpus subjects: {missing}")

    cat = (d.get("includedInDataCatalog") or {}).get("url")
    if cat != f"{SITE_BASE}/":
        fail(f"includedInDataCatalog names {cat}, not the site — `/catalogue/` is one dataset "
             f"in the catalogue of datasets, not the catalogue itself")

    # A URL string. A nested object is what Search Console failed on 2026-09-21: Google
    # validates it as a Dataset of its own, and a stub has none of the required fields.
    part = d.get("isPartOf")
    if isinstance(part, dict):
        fail("isPartOf is an object — Google validates it as a Dataset missing name, "
             "description, creator and license; give the parent's URL instead")
        part = part.get("@id")
    if part and part not in PARENTS:
        fail(f"isPartOf names {part}, which is no whole dataset this site publishes {PARENTS}")
    if part == d["@id"]:
        fail("isPartOf names the dataset itself")

    # **An edition dates itself, and the page says which one two screens below.** `version`,
    # `dateModified` and the colophon's `dl-artefact` are three statements of one fact from two
    # builders; a page whose structured data offers one edition while its Edition row names
    # another has no defensible answer to *what am I looking at*. `finance.py` printed `19` in
    # that row until 2026-09-20, from a second parse of a filename grammar `editions.py` owns.
    if d.get("version"):
        if not ISO.match(d["version"]) and not EDITION.match(d["version"]):
            fail(f"version is not an edition: {d['version']!r}")
        if d.get("datePublished") != d["dateModified"]:
            fail("a dated edition's datePublished and dateModified are the same day")
        art = ARTEFACT.search(outside)
        if art and art.group(2) != d["version"]:
            fail(f"version {d['version']} is not the edition the page says it is offering "
                 f"({art.group(2)})")
        if art and f"{art.group(1)}-{art.group(2)}." not in d["distribution"][0]["contentUrl"]:
            fail(f"the download named is not the artefact the page records "
                 f"({art.group(1)}-{art.group(2)})")

    out += check_downloads(rel, d["distribution"], outside)
    return out


def check_downloads(rel: str, items: list[dict], outside: str) -> list[str]:
    """A file the block names is a file the page offers, at the size it really is.

    **Against the page with the block cut out of it.** Tested against the whole page the first
    half asserts nothing: the URL is inside the block, the block is inside the page, so
    `contentUrl in html` is true however wrong the URL is. What is being asked is whether the
    *page* offers that file — the download button, the `This file` row, the CSV link — and
    those are the part of the page the block is not."""
    out: list[str] = []
    for item in items:
        url = item.get("contentUrl")
        if not url:
            out.append(f"{rel}: a download in the block has no contentUrl")
            continue
        # **Matched on the filename, not the whole URL.** Structured data has to name a file
        # absolutely; a page links its own downloads relatively — `href="AGO-catalogue.csv"`.
        # Demanding the absolute form here fails every page that is doing the right thing.
        # The filename is the part that can be wrong in a way that matters: a stale edition, a
        # renamed cut, a file that was never written.
        if url.rsplit("/", 1)[-1] not in outside:
            out.append(f"{rel}: the block names {url}, which the page itself does not offer")
        path = local_path(url)
        # A dated PDF is pruned from the tree once R2 has it (RENDER Step 6b), so its absence
        # here carries no information and is not a finding. A CSV is served from this tree and
        # its absence is a 404 waiting to happen.
        # A dated edition is pruned once R2 has it, so its absence is a successful sync. An
        # undated download — the catalogue and its cuts — is served from this tree, and its
        # absence is a 404 waiting to happen.
        if path is not None and url.endswith(".csv"):
            if not path.exists():
                if not EDITION_FILE.search(url):
                    out.append(f"{rel}: the block names {url}, which is not in the built tree")
            elif item.get("contentSize") and item["contentSize"] != size_label(
                    path.stat().st_size):
                out.append(f"{rel}: contentSize says {item['contentSize']} for "
                           f"{path.name}, which is {size_label(path.stat().st_size)}")
    return out


def main() -> int:
    pages = sorted(SITE.rglob("*.html"))
    carries, findings = [], []
    for p in pages:
        rel = p.relative_to(SITE).as_posix()
        html = p.read_text(encoding="utf-8")
        if BLOCK.search(html):
            carries.append(rel)
            findings += check(rel, html)
        elif DOCUMENT_PAGE.match(rel):
            findings.append(f"{rel}: no structured data block")

    docs = [r for r in carries if DOCUMENT_PAGE.match(r)]
    print(f"lint-structured-data: {len(carries)} page(s) with a block "
          f"({len(docs)} document, {len(carries) - len(docs)} dataset)")
    if not carries:
        print("  nothing to check — has the site been rendered?")
        return 1
    if findings:
        print(f"  {len(findings)} finding(s):")
        for f in findings:
            print(f"    {f}")
        return 1
    print("  ok — every page describes itself, and agrees with itself")
    return 0


if __name__ == "__main__":
    sys.exit(main())
