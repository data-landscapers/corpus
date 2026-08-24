#!/usr/bin/env python3
"""home.py — the home page (documentation/design.md §3, §6).

    python scripts/home.py   ->  site/index.html
                             ->  site/countries/index.html   (the 54-box matrix)
                             ->  site/topics/index.html      (the taxonomy matrix)

Promoted from prototypes/build-home-page.py once the wireframe was agreed;
revised 2026-08-11 to Bill's numbered change list. The shape, in order: the
header mirrors data-landscapers.io's own nav with Corpus added on the left;
a second nav bar for the corpus sections; a highlighted total/this-year/
this-month stat bar; a two-line statement of what the corpus is; then
Countries, Regions and Topics.

**Two of those three sections are now a heading, an intro and a link**
*(Bill, 2026-08-24)*. The country matrix and the topic matrix each moved to a
page of their own on the same day, for the same reason: between them they were
most of two viewports of boxes standing between a reader and everything below.
They are still built here, from the same `load_stats()` counts, because they
are the same object at a different address — `build_countries()` and
`build_topics()` beside `build()`.

**Where the numbers come from.** `REPO-STATUS.md` will write nightly counts
into `outputs/catalogue/stats.json` (osint-corpus-exchange/notes-for-osint.md #8). Until it does,
this reads `outputs/catalogue/raw-catalogue.csv` and counts the same things
itself — `load_stats()` prefers the published file and falls back, so the
page is right today and needs no rewrite when the file lands.

**A document tagged with several places is counted under each**, so the
country and region boxes sum to more than the document total — they measure
coverage, not documents, and the caveat travels with them on the page.

Country and topic boxes link to `{SITE_BASE}/countries/{ISO3}/` and
`{SITE_BASE}/topics/{slug-with-hyphens}/` regardless of whether those pages exist yet —
pull exhaustively, publish selectively (documentation/design.md §8): the box is accurate
about what the base holds even before the page that would serve it is
written.
"""

from __future__ import annotations

import csv
import html
import json
from collections import Counter
from datetime import date
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import taxonomy_lib  # noqa: E402
from copy_lib import copy_inline  # noqa: E402
from chrome_lib import chrome, foot, styles  # noqa: E402

CORPUS = Path(__file__).resolve().parent.parent
OUTPUTS = CORPUS / "outputs"
SITE = CORPUS / "site"
SITE_BASE = "https://corpus.data-landscapers.io"
MAIN_SITE = "https://data-landscapers.io"

STATS_SHAPE = """{
  "generated": "YYYY-MM-DD",     # the run that wrote it
  "documents": 0,                # markdown sources in raw/, PDFs excluded
  "by_year":  {"2026": 0},       # publication year, from `published:`
  "by_month": {"2026-08": 0},    # year-month, same field; sums to <= the year
  "by_place": {"KEN": 0},        # places facet; multi-tagged, so sums high
  "by_topic": {"dpi.id": 0}      # topics facet; roll-up to Level 1 by prefix
}"""

# Level-1 labels from `lookups/taxonomy.md`, and country/region names from
# `lookups/countries.csv` — both in OSINT, neither in `outputs/`. The build is
# not allowed to read outside `outputs/` (osint-corpus-exchange/notes-for-osint.md), so for now they
# are duplicated here. Two copies of one vocabulary is exactly the failure
# documentation/design.md §8 refuses elsewhere, so this is a note for OSINT (#9), not a
# pattern to repeat deliberately.
L1 = {
    "infra": "ICT Infrastructure", "dpi": "Digital public infrastructure",
    "gov": "Governance", "include": "Inclusion", "tech": "Technology",
    "geopol": "Geopolitics", "capacity": "Capacity", "digital": "Digitalisation",
    "data": "Data", "finance": "Finance",
}

# Short display names for the country matrix (Bill, 2026-08-11 — "replace
# ISO-3 with short country names (eg DRC)"). Full names come from
# `lookups/countries.csv`; a handful are shortened further so they fit a box
# the width of a code. The ISO3 stays as a `title` attribute on each box.
COUNTRY_NAMES = {
    "AGO": "Angola", "BDI": "Burundi", "BEN": "Benin", "BFA": "Burkina Faso",
    "BWA": "Botswana", "CAF": "CAR", "CIV": "Côte d'Ivoire", "CMR": "Cameroon",
    "COD": "DRC", "COG": "Congo", "COM": "Comoros", "CPV": "Cape Verde",
    "DJI": "Djibouti", "DZA": "Algeria", "EGY": "Egypt", "ERI": "Eritrea",
    "ETH": "Ethiopia", "GAB": "Gabon", "GHA": "Ghana", "GIN": "Guinea",
    "GMB": "Gambia", "GNB": "Guinea-Bissau", "GNQ": "Eq. Guinea", "KEN": "Kenya",
    "LBR": "Liberia", "LBY": "Libya", "LSO": "Lesotho", "MAR": "Morocco",
    "MDG": "Madagascar", "MLI": "Mali", "MOZ": "Mozambique", "MRT": "Mauritania",
    "MUS": "Mauritius", "MWI": "Malawi", "NAM": "Namibia", "NER": "Niger",
    "NGA": "Nigeria", "RWA": "Rwanda", "SDN": "Sudan", "SEN": "Senegal",
    "SLE": "Sierra Leone", "SOM": "Somalia", "SSD": "South Sudan",
    "STP": "São Tomé", "SWZ": "Eswatini", "SYC": "Seychelles", "TCD": "Chad",
    "TGO": "Togo", "TUN": "Tunisia", "TZA": "Tanzania", "UGA": "Uganda",
    "ZAF": "South Africa", "ZMB": "Zambia", "ZWE": "Zimbabwe",
}

# Region and bloc codes (the `X`-prefixed places) — same source and caveat.
REGION_NAMES = {
    "XAF": "Africa", "XCA": "Central Africa", "XEA": "East Africa",
    "XGL": "Global", "XNA": "North Africa", "XSA": "Southern Africa",
    "XSS": "Sub-Saharan Africa", "XWA": "West Africa",
}

# Intro copy under each heading. Topics still carries the text that used to
# sit in its card, unchanged. Countries is Bill's rewrite, edited straight in
# site/index.html on 2026-08-11 and copied back here so a rebuild doesn't
# revert it. Regions had no prior card to draw from, so that paragraph is CC's.
# The section intros, the caveats under each set of boxes and the hero standfirst
# live in `content/home.md` now (Bill, 2026-08-19). `copy_inline` because each
# sits inside a <p> the template already classes.

csv.field_size_limit(10 ** 9)


# ── stats ─────────────────────────────────────────────────────────

def load_stats() -> dict:
    """Prefer the published nightly stats; count the catalogue if absent."""
    published = OUTPUTS / "catalogue" / "stats.json"
    if published.exists():
        return json.loads(published.read_text(encoding="utf-8"))

    by_year, by_month, by_place, by_topic = Counter(), Counter(), Counter(), Counter()
    n = 0
    with open(OUTPUTS / "catalogue" / "raw-catalogue.csv", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            n += 1
            pub = (row.get("published") or "").strip()
            if len(pub) >= 4:
                by_year[pub[:4]] += 1
            if len(pub) >= 7:
                by_month[pub[:7]] += 1
            for p in (row.get("places") or "").split(";"):
                if p.strip():
                    by_place[p.strip()] += 1
            for t in (row.get("topics") or "").split(";"):
                if t.strip():
                    by_topic[t.strip()] += 1
    return {
        "generated": date.today().isoformat(), "documents": n,
        "by_year": dict(by_year), "by_month": dict(by_month),
        "by_place": dict(by_place), "by_topic": dict(by_topic),
        "source": "counted from raw-catalogue.csv",
    }


# ── rendering ─────────────────────────────────────────────────────

def e(s: str) -> str:
    return html.escape(str(s))


def country_boxes(by_place: dict[str, int]) -> str:
    """Shaded by volume, so an uneven base looks uneven at a glance rather than
    presenting as even coverage. Every box links to its country page whether or
    not that page is built yet (documentation/design.md §8: pull exhaustively, publish
    selectively) — a live link that 404s until the page lands is accurate about
    what the base holds; hiding it would not be. Labelled with the short name
    (Bill, 2026-08-11); the ISO3 survives as a `title` attribute. Sorted by
    that displayed name, not the code (Bill, 2026-08-11) — a code-sorted grid
    of names reads as shuffled once the box no longer shows the code."""
    codes = sorted((c for c in by_place if not c.startswith("X")),
                   key=lambda c: COUNTRY_NAMES.get(c, c))
    top = max(by_place[c] for c in codes) or 1
    return "\n".join(
        f'<a class="box" href="{SITE_BASE}/countries/{c}/" title="{c}"'
        f' style="--fill:{by_place[c] / top:.3f}">'
        f'<span class="box__k">{e(COUNTRY_NAMES.get(c, c))}</span>'
        f'<span class="box__n">{by_place[c]:,}</span></a>'
        for c in codes)


def region_boxes(by_place: dict[str, int]) -> str:
    """Same shape as country_boxes, over the `X`-prefixed region and bloc
    codes rather than countries (Bill, 2026-08-11, item 8).

    **The box opens the catalogue filtered to that place, not a landing page**
    *(2026-08-21)*. It used to link `/regions/{code}/`, and nothing has ever
    written that tree — `country.py` builds the 54 countries and `RENDER.md`
    Step 4 says in as many words that the regions do not get a country-style
    page. All eight boxes 404'd on the live home page. The catalogue reads its
    filter state off the URL hash, so `#places={code}` lands on exactly the
    records the box is counting, which is also the closer match: the number on
    the box is a catalogue count, not a report."""
    codes = sorted(c for c in by_place if c.startswith("X"))
    top = max(by_place[c] for c in codes) or 1
    return "\n".join(
        f'<a class="box" href="{SITE_BASE}/catalogue/#places={c}" title="{c}"'
        f' style="--fill:{by_place[c] / top:.3f}">'
        f'<span class="box__k">{e(REGION_NAMES.get(c, c))}</span>'
        f'<span class="box__n">{by_place[c]:,}</span></a>'
        for c in codes)


def bulletin_section() -> str:
    """The bulletin, at the top of the page because it is the one thing here that is about today
    *(2026-08-17)*.

    **Heading and one paragraph** *(Bill, 2026-08-21)*. It used to carry two boxes — *By country*
    and *By topic*, each showing the window's item count — and a caveat under them explaining
    that both counted the same sources. The country bulletin is retired, which leaves one box
    counting one document, and a box matrix of one is a link wearing a costume. So the heading
    is the link, and the paragraph beneath it is the section.

    The section is omitted entirely where the document does not exist — unlike the country and
    topic boxes, which link ahead of the pages they open (design.md §8), there is nothing here to
    be accurate *about* until a build has written one."""
    if not (OUTPUTS / "bulletins" / "corpus-bulletin.md").exists():
        return ""
    return (f'\n    <h2 class="section-heading" id="bulletin">'
            f'<a href="{SITE_BASE}/bulletin/">Bulletin</a></h2>\n'
            f'    <p class="section-intro">{copy_inline("home", "bulletin-intro")}</p>\n')


def topic_grid(by_topic: dict[str, int]) -> str:
    """The topic matrix, for `site/topics/`: an h3 per Level-1 category, and a row
    of boxes beneath it with the category's own box first.

    **Order, grouping and wording all come from `lookups/taxonomy.csv`**, through
    `taxonomy_lib` *(Bill, 2026-08-24)* — not from the counts, and not from the
    label dictionaries this file used to carry for want of anywhere better. The
    home page's tiles sorted by volume, which is the right answer for a matrix a
    reader scans for size and the wrong one for a page that *is* the taxonomy: a
    two-tier vocabulary printed out of its own order is not the vocabulary. It
    also retires `SUBTOPIC_NAMES` and `L1` as authorities here — they were a
    working copy of labels that live in the taxonomy file now, and a second copy
    of a vocabulary is the failure design.md refuses everywhere else.

    **Every subject in the file gets a box, whether or not the base holds one for
    it.** A topic with nothing on record reads as thin coverage, which is what it
    is; dropping it would make the page a picture of the corpus rather than of
    the taxonomy, and the two are different objects. A slug the catalogue holds
    and the taxonomy does not still gets a box too, after its category's own — the
    count is real, and a page that silently disagrees with the catalogue is worse
    than one showing a slug for its own label.

    The first box of each row is the category itself: the roll-up count, opening
    `/topics/{key}/`, which `topic-page.py` writes. The rest are its Level-2
    subjects, shaded within the row and opening `/topics/{key-subject}/`. The dot
    survives in the vocabulary, where it means something, and not in the path,
    where it reads as an extension — so `dpi.pay` links as `dpi-pay`."""
    order: list[str] = []
    groups: dict[str, list[str]] = {}

    def place(slug: str) -> None:
        k = slug.split(".")[0]
        if k not in groups:
            order.append(k)
            groups[k] = []
        groups[k].append(slug)

    for slug in taxonomy_lib.keys():
        place(slug)
    for slug in taxonomy_lib.unknown(list(by_topic)):
        place(slug)

    out = []
    for k in order:
        slugs = groups[k]
        name = next((taxonomy_lib.level1(s) for s in slugs if taxonomy_lib.level1(s)),
                    L1.get(k, k))
        roll = sum(by_topic.get(s, 0) for s in slugs)
        top = max((by_topic.get(s, 0) for s in slugs), default=1) or 1
        boxes = [
            f'      <a class="sbox sbox--all" href="{SITE_BASE}/topics/{k}/"'
            f' title="{k}.*">'
            f'<span class="sbox__l">All {e(name)}</span>'
            f'<span class="sbox__n">{roll:,}</span></a>'
        ]
        boxes += [
            f'      <a class="sbox" href="{SITE_BASE}/topics/{s.replace(".", "-")}/"'
            f' title="{s}" style="--fill:{by_topic.get(s, 0) / top:.3f}">'
            f'<span class="sbox__l">{e(taxonomy_lib.label(s))}</span>'
            f'<span class="sbox__n">{by_topic.get(s, 0):,}</span></a>'
            for s in slugs]
        out.append(f'    <h3 class="topic-group" id="{k}">{e(name)}'
                   f' <span class="topic-group__k">{k}.*</span></h3>\n'
                   f'    <div class="tsub__inner">\n'
                   + "\n".join(boxes)
                   + '\n    </div>')
    return "\n".join(out)


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Corpus — Data Landscapers</title>
<meta name="description" content="A living record of digital transformation and data governance across Africa: {docs} sources, country and topic reports, and the finance behind them.">
<link rel="canonical" href="{base}/">
{styles}
<link rel="icon" href="{favicon}" type="image/svg+xml">
<meta property="og:title" content="Corpus — Data Landscapers">
<meta property="og:description" content="A working record of digital transformation and data governance across Africa.">
<meta property="og:url" content="{base}/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Data Landscapers">
</head>
<body>
<div class="site-wrap">

{chrome}

  <div class="stat-bar">
    <div class="stat-bar__inner">
      <span class="stat-bar__label">Primary sources in corpus</span>
      <span class="stat-bar__item">Total <strong>{docs}</strong></span>
      <span class="stat-bar__item">Published this year <strong>{docs_year}</strong></span>
      <span class="stat-bar__item">Published this month <strong>{docs_month}</strong></span>
    </div>
  </div>

  <main id="main">
  <div class="container">

    <div class="hero">
      <p>{hero}</p>
    </div>

{bulletin}
    <h2 class="section-heading" id="countries"><a href="{base}/countries/">Countries</a></h2>
    <p class="section-intro">{countries_intro}</p>
    <p class="section-intro"><a href="{base}/countries/">Browse all 54 countries &rarr;</a></p>

    <h2 class="section-heading" id="regions">Regions</h2>
    <p class="section-intro">{regions_intro}</p>
    <div class="boxes boxes--regions">
{regions}
    </div>
    <p class="caveat">{regional} sources are tagged to a region or bloc rather than to a country, and are not counted in the Countries figures above.</p>

    <h2 class="section-heading" id="topics"><a href="{base}/topics/">Topics</a></h2>
    <p class="section-intro">{topics_intro}</p>
    <p class="section-intro"><a href="{base}/topics/">Browse all {ntopics} topics &rarr;</a></p>

    <div class="colophon">
      <strong>About this page</strong>
      <dl>
        <dt>Built</dt><dd class="mono">{built}</dd>
        <dt>Counts</dt><dd>{counts_from}</dd>
        <dt>Licence</dt><dd><a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></dd>
      </dl>
    </div>

  </div>
  </main>

  <footer class="site-footer">
    <div class="site-footer__inner">
      <p class="site-footer__copy"><a href="https://creativecommons.org/licenses/by/4.0/" style="color:inherit;border-bottom:none;">CC BY 4.0</a> {year} Bill Anderson / Data Landscapers Ltd &nbsp;·&nbsp; Registered in the UK · Co. No. 16040544</p>
      <div class="site-footer__links">
        <a href="{main_site}/">data-landscapers.io</a>
        <a href="{base}/method/">Method</a>
      </div>
    </div>
  </footer>

</div>
</body>
</html>
"""




# The countries page — the 54-box matrix, moved off the home page on 2026-08-24
# (Bill). The home page keeps the heading and `countries-intro` and links here.
#
# **Why it is a page and not a section.** The matrix is the largest single object
# on the site — 54 boxes, most of a viewport — and it sat above Regions and
# Topics, which meant a reader who wanted either had to scroll past all of it.
# It also gives `{SITE_BASE}/countries/` something to be: that URL held the 54
# per-country directories and no index, so it 404'd, and it was one of the three
# dead links the nav carried until this morning. The nav points at it properly
# now instead of at the home page's `#countries` anchor.
COUNTRIES_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Countries — Data Landscapers</title>
<meta name="description" content="Every African country in the Data Landscapers corpus, with the number of primary sources held for each.">
<link rel="canonical" href="{base}/countries/">
{styles}
<link rel="icon" href="{favicon}" type="image/svg+xml">
<meta property="og:title" content="Countries — Data Landscapers">
<meta property="og:description" content="Every African country in the Data Landscapers corpus, with the number of primary sources held for each.">
<meta property="og:url" content="{base}/countries/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Data Landscapers">
</head>
<body>
<div class="site-wrap">

{chrome}

  <div class="stat-bar">
    <div class="stat-bar__inner">
      <span class="stat-bar__label">Primary sources in corpus</span>
      <span class="stat-bar__item">Total <strong>{docs}</strong></span>
      <span class="stat-bar__item">Countries covered <strong>{ncountries}</strong></span>
    </div>
  </div>

  <main id="main">
  <div class="container">

    <!-- An h1, not the h2.section-heading the home page uses. This is the page's
         own title rather than one section of several, so it takes the page-title
         type and none of the section rule — which was drawing a terracotta line
         above the first thing on the page, where there is nothing to divide it
         from. It also gives the page the h1 it was missing. -->
    <h1>Countries</h1>
    <p class="section-intro">{countries_intro}</p>
    <div class="boxes">
{countries}
    </div>
    <p class="caveat">{countries_caveat}</p>

    <div class="colophon">
      <strong>About this page</strong>
      <dl>
        <dt>Built</dt><dd class="mono">{built}</dd>
        <dt>Licence</dt><dd><a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></dd>
      </dl>
    </div>

  </div>
  </main>

{foot}

</div>
</body>
</html>
"""


def build_countries() -> Path:
    """`site/countries/index.html` — the matrix on a page of its own.

    Written into the directory that already holds the 54 per-country folders, so
    `/countries/` resolves and `/countries/AGO/` goes on resolving beneath it."""
    s = load_stats()
    by_place = s["by_place"]
    built = date.today().isoformat()
    doc = COUNTRIES_TEMPLATE.format(
        base=SITE_BASE, built=built,
        favicon=f"{MAIN_SITE}/assets/favicon.svg",
        chrome=chrome("countries", depth=1), foot=foot(depth=1),
        styles=styles(1, "home.css"),
        docs=f"{s['documents']:,}",
        ncountries=sum(1 for k, v in by_place.items() if not k.startswith("X") and v),
        countries=country_boxes(by_place),
        countries_intro=copy_inline("home", "countries-intro"),
        countries_caveat=copy_inline("countries", "caveat"),
    )
    out = SITE / "countries"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(doc, encoding="utf-8")
    return out / "index.html"


# The topics page — the taxonomy matrix, moved off the home page on 2026-08-24
# (Bill), a few hours after the countries matrix and for the same reasons. The
# home page keeps the heading, `topics-intro` and a link here.
#
# **What changed besides its address.** The home page showed ten Level-1 tiles
# and opened one row of sub-topics at a time, sorted by volume, behind a click.
# A page of its own has room to print the whole taxonomy at once, so it does:
# every category, every subject beneath it, in the file's own order, with no
# JavaScript and nothing hidden. That is also why the tile toggle and its script
# have gone from this file — there is no longer a matrix on the home page for
# them to open.
TOPICS_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Topics — Data Landscapers</title>
<meta name="description" content="The Data Landscapers taxonomy: {ntopics} subjects in ten categories, each with the number of primary sources held for it.">
<link rel="canonical" href="{base}/topics/">
{styles}
<link rel="icon" href="{favicon}" type="image/svg+xml">
<meta property="og:title" content="Topics — Data Landscapers">
<meta property="og:description" content="The Data Landscapers taxonomy: {ntopics} subjects in ten categories, each with the number of primary sources held for it.">
<meta property="og:url" content="{base}/topics/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Data Landscapers">
</head>
<body>
<div class="site-wrap">

{chrome}

  <div class="stat-bar">
    <div class="stat-bar__inner">
      <span class="stat-bar__label">Primary sources in corpus</span>
      <span class="stat-bar__item">Total <strong>{docs}</strong></span>
      <span class="stat-bar__item">Subjects tracked <strong>{ntopics}</strong></span>
    </div>
  </div>

  <main id="main">
  <div class="container">

    <h1>Topics</h1>
    <p class="section-intro">{topics_intro}</p>

{topics}

    <p class="caveat">{topics_caveat}</p>

    <div class="colophon">
      <strong>About this page</strong>
      <dl>
        <dt>Built</dt><dd class="mono">{built}</dd>
        <dt>Vocabulary</dt><dd class="mono">lookups/taxonomy.csv</dd>
        <dt>Licence</dt><dd><a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></dd>
      </dl>
    </div>

  </div>
  </main>

{foot}

</div>
</body>
</html>
"""


def build_topics() -> Path:
    """`site/topics/index.html` — the taxonomy, with counts, on a page of its own.

    Written into the directory that already holds the 48 topic and category
    folders `topic-page.py` builds, so `/topics/` resolves and every
    `/topics/{slug}/` goes on resolving beneath it. `ntopics` counts the
    taxonomy rather than the catalogue's distinct topics: the page prints a box
    per subject in the file, so the number in the stat bar and the number of
    boxes are the same number, which they were not while one counted what had
    been tagged."""
    s = load_stats()
    built = date.today().isoformat()
    ntopics = len(taxonomy_lib.keys())
    doc = TOPICS_TEMPLATE.format(
        base=SITE_BASE, built=built,
        favicon=f"{MAIN_SITE}/assets/favicon.svg",
        chrome=chrome("topics", depth=1), foot=foot(depth=1),
        styles=styles(1, "home.css"),
        docs=f"{s['documents']:,}", ntopics=ntopics,
        topics=topic_grid(s["by_topic"]),
        topics_intro=copy_inline("home", "topics-intro"),
        topics_caveat=copy_inline("topics", "caveat", n=f"{ntopics}"),
    )
    out = SITE / "topics"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(doc, encoding="utf-8")
    return out / "index.html"


def build() -> Path:
    s = load_stats()
    by_place = s["by_place"]
    regional = sum(v for k, v in by_place.items() if k.startswith("X"))

    built = date.today().isoformat()
    this_year, this_month = built[:4], built[:7]
    doc = TEMPLATE.format(
        base=SITE_BASE, main_site=MAIN_SITE, built=built,
        favicon=f"{MAIN_SITE}/assets/favicon.svg",
        docs=f"{s['documents']:,}", year=built[:4],
        docs_year=f"{s['by_year'].get(this_year, 0):,}",
        docs_month=f"{s['by_month'].get(this_month, 0):,}",
        bulletin=bulletin_section(),
        chrome=chrome(None, depth=0),
        styles=styles(0, "home.css"),
        hero=copy_inline("home", "hero"),
        countries_intro=copy_inline("home", "countries-intro"),
        regions=region_boxes(by_place), regions_intro=copy_inline("home", "regions-intro"),
        topics_intro=copy_inline("home", "topics-intro"),
        regional=f"{regional:,}", ntopics=len(taxonomy_lib.keys()),
        counts_from=("<code>outputs/catalogue/stats.json</code>, generated "
                     + s.get("generated", "")
                     if "source" not in s else
                     "counted from <code>raw-catalogue.csv</code> &mdash; "
                     "<code>outputs/catalogue/stats.json</code> not yet published"),
    )
    SITE.mkdir(parents=True, exist_ok=True)
    out = SITE / "index.html"
    out.write_text(doc, encoding="utf-8")
    return out


if __name__ == "__main__":
    print(build())
    print(build_countries())
    print(build_topics())
    print("stats file the page will prefer, once REPO-STATUS writes it:")
    print("  outputs/catalogue/stats.json")
    print(STATS_SHAPE)
