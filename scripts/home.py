#!/usr/bin/env python3
"""home.py — the home page (documentation/design.md §3, §6).

    python scripts/home.py   ->  site/index.html
                             ->  site/countries/index.html   (the 54-box matrix, then the region matrix)
                             ->  site/topics/index.html      (the taxonomy matrix)

**The home page is one screen mapping the site** *(Bill, 2026-10-20)*: the
masthead and Corpus nav row, a banner, then News, Reports and Datasets
as rounded boxes of links (`TEMPLATE`, styled by `home.css`). It replaced the
stat bar and the run of section intros that stood there since 2026-08-11.

**The country and topic matrices are now a heading, an intro and a link**
*(Bill, 2026-08-24)*. Each moved to a page of their own on the same day, for
the same reason: between them they were most of two viewports of boxes
standing between a reader and everything below. They are still built here,
from the same `load_stats()` counts, because they are the same object at a
different address — `build_countries()` and `build_topics()` beside `build()`.

**The region matrix followed the country one to `/countries/` on 2026-09-02**
*(Bill)*, to the bottom of the page rather than a heading of its own on the
home page: Countries and Regions are one nav item and one section now, and
`build_countries()` writes both matrices, country boxes first.

**Where the numbers come from.** `REPO-STATUS.md` will write nightly counts
into `outputs/catalogue/stats.json` (osint-corpus-exchange/notes-for-osint.md #8). Until it does,
this reads `outputs/catalogue/raw-catalogue.csv` and counts the same things
itself — `load_stats()` prefers the published file and falls back, so the
page is right today and needs no rewrite when the file lands.

**A document tagged with several places is counted under each**, so the
country and region boxes sum to more than the document total — they measure
coverage, not documents, and the caveat travels with them on the page.

Country and region boxes link to the place's news page (`box_href`), and topic boxes to the topic's
news page (`topic_href`). A box prints whether or not a page serves it — pull exhaustively,
publish selectively (documentation/design.md §8): the box is accurate about what the base
holds even before the page that would serve it is written.
"""

from __future__ import annotations

import csv
import html
import json
import re
from collections import Counter
from datetime import date
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import taxonomy_lib  # noqa: E402
from copy_lib import copy, copy_inline  # noqa: E402
from chrome_lib import chrome, external_links, feedback, foot, ga, info, styles  # noqa: E402

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


def box_href(code: str) -> str:
    """Where a place box goes: **the top of that place's news page** *(Bill, 2026-10-16)*. Not a
    section inside it: a reader landing mid-page would not see that they had changed country.
    Every box on the site uses it since the country pages retired *(Bill, 2026-10-17)*; the two
    regions that issue no reports go to the catalogue cut to them."""
    if (OUTPUTS / "reports" / code / f"{code}-monthly.md").exists():
        return f"{SITE_BASE}/reports/{code}/{code}-monthly.html"
    return f"{SITE_BASE}/catalogue/#places={code}"


def topic_href(slug: str) -> str | None:
    """Where a topic box goes: **the topic's news page** *(Bill, 2026-10-20)*, its progress
    report where it issues no news, or nowhere where it issues neither. The topic landing pages
    are retired (`topic-page.py`)."""
    s = slug.replace(".", "-")
    for kind in ("monthly", "progress"):
        if (OUTPUTS / "topics" / s / f"{s}-{kind}.md").exists():
            return f"{SITE_BASE}/topics/{s}/{s}-{kind}.html"
    return None


def country_boxes(by_place: dict[str, int]) -> str:
    """Shaded by volume, so an uneven base looks uneven at a glance rather than
    presenting as even coverage. Every box links to the country's news page
    (`box_href`). Labelled with the short name
    (Bill, 2026-08-11); the ISO3 survives as a `title` attribute. Sorted by
    that displayed name, not the code (Bill, 2026-08-11) — a code-sorted grid
    of names reads as shuffled once the box no longer shows the code."""
    codes = sorted((c for c in by_place if not c.startswith("X")),
                   key=lambda c: COUNTRY_NAMES.get(c, c))
    top = max(by_place[c] for c in codes) or 1
    return "\n".join(
        f'<a class="box" href="{box_href(c)}" title="{c}"'
        f' style="--fill:{by_place[c] / top:.3f}">'
        f'<span class="box__k">{e(COUNTRY_NAMES.get(c, c))}</span>'
        f'<span class="box__n">{by_place[c]:,}</span></a>'
        for c in codes)


def region_boxes(by_place: dict[str, int]) -> str:
    """Same shape as country_boxes, over the `X`-prefixed region and bloc
    codes rather than countries (Bill, 2026-08-11, item 8).

    The box opens the region's news page, like a country box (`box_href`)."""
    codes = sorted(c for c in by_place if c.startswith("X"))
    top = max(by_place[c] for c in codes) or 1
    return "\n".join(
        f'<a class="box" href="{box_href(c)}" title="{c}"'
        f' style="--fill:{by_place[c] / top:.3f}">'
        f'<span class="box__k">{e(REGION_NAMES.get(c, c))}</span>'
        f'<span class="box__n">{by_place[c]:,}</span></a>'
        for c in codes)


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
    and the taxonomy does not still gets a box too, at the end of its category —
    the count is real, and a page that silently disagrees with the catalogue is
    worse than one showing a slug for its own label.

    **Only Level-2 subjects get a box** *(Bill, 2026-08-24)*. Each row opened with
    an *All {category}* box carrying the roll-up, as the home page's sub-topic
    rows did, and it went to `/topics/{key}/` — which is an index of the topics
    beneath it and not a report, so every box on the page but that one led to
    documents. A box that looks like the others and behaves differently is worse
    than no box: the roll-up is a number, so it is printed in the heading, where
    nobody will read it as a way in. The category pages `topic-page.py` writes are
    left alone; nothing links to them from here now.

    Boxes are shaded within their own row and open the topic's news page. The
    dot survives in the vocabulary, where it means something, and not in the path,
    where it reads as an extension — so `dpi.pay` links as `dpi-pay`."""
    order: list[str] = []
    groups: dict[str, list[str]] = {}
    known = set(taxonomy_lib.keys())

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
        # The count precedes the label because it is floated right and a float
        # only affects the content after it — see home.css. Four boxes to a row
        # means the label needs every line but the first at full width, or three
        # of the taxonomy's labels run to three lines.
        #
        # **A box is a link only where there is a page behind it**: the topic's news
        # (`topic_href`). A slug with no report, or one the catalogue holds and the
        # taxonomy does not, has no page — linking it puts a 404 on a published page.
        # The box still prints, with its real count, which is what the paragraph
        # above asks for; only the anchor goes.
        def box(s: str) -> str:
            inner = (f'<span class="sbox__n">{by_topic.get(s, 0):,}</span>'
                     f'<span class="sbox__l">{e(taxonomy_lib.label(s))}</span>')
            attrs = f'title="{s}" style="--fill:{by_topic.get(s, 0) / top:.3f}"'
            href = topic_href(s) if s in known else None
            if href:
                return f'      <a class="sbox" href="{href}" {attrs}>{inner}</a>'
            return f'      <span class="sbox sbox--nopage" {attrs}>{inner}</span>'

        boxes = [box(s) for s in slugs]
        out.append(f'    <h3 class="topic-group" id="{k}">{e(name)}'
                   f' <span class="topic-group__k">{k}.*</span>'
                   f'<span class="topic-group__n">{roll:,}</span></h3>\n'
                   f'    <div class="tsub__inner">\n'
                   + "\n".join(boxes)
                   + '\n    </div>')
    return "\n".join(out)


# **The home page is a map of the site** *(Bill, 2026-10-20)*: the masthead, then one screen of
# rounded boxes, News, Reports and Datasets, each linking to what it names. It replaced the
# stat bar and the run of section intros; the Corpus nav row stays above it.
# The sample links (Algeria's news, Angola's status, Benin's progress) are Bill's choice.
TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Corpus — Data Landscapers</title>
<meta name="description" content="Real-time research on African digital transformation: daily news, country and topic reports, maturity and progress assessments, finance and other datasets.">
<link rel="canonical" href="{base}/">
{styles}
<link rel="icon" href="{favicon}" type="image/svg+xml">
<meta property="og:title" content="Corpus — Data Landscapers">
<meta property="og:description" content="Real-time research on African digital transformation.">
<meta property="og:url" content="{base}/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Data Landscapers">
{ga}
</head>
<body>
<div class="site-wrap">
{chrome}
  <main id="main" class="map">

    <header class="map__head">
      <h1 class="map__title">Corpus</h1>
      <p class="map__sub">Real-time research on African digital transformation</p>
    </header>

    <div class="map__cols">

      <section class="col" aria-labelledby="col-news">
        <h2 class="col__title" id="col-news">News</h2>
        <a class="card" href="{base}/bulletin/">
          <span class="card__name">Bulletin</span>
          <span class="card__text">Yesterday&rsquo;s news stories, collected overnight.</span>
        </a>
        <a class="card" href="{base}/reports/DZA/DZA-monthly.html">
          <span class="card__name">Country &amp; region</span>
          <span class="card__text">Every story published since the start of last month: a report for each country and region, grouped by topic and story.</span>
        </a>
        <a class="card" href="{base}/topics/gov-policy/gov-policy-monthly.html">
          <span class="card__name">Topic</span>
          <span class="card__text">The same stories, in a report for each of the {ntopics} topics, grouped by country.</span>
        </a>
        <a class="card" href="{base}/alerts/">
          <span class="card__name">Custom alerts</span>
          <span class="card__text">Weekly emails or RSS feeds built from your own choice of countries and topics.</span>
        </a>
      </section>

      <section class="col" aria-labelledby="col-reports">
        <h2 class="col__title" id="col-reports">Reports</h2>
        <a class="card" href="{base}/reports/AGO/AGO-status.html">
          <span class="card__name">Status</span>
          <span class="card__text">An overall assessment of each country&rsquo;s digital transformation.</span>
        </a>
        <a class="card" href="{base}/reports/BEN/BEN-progress.html">
          <span class="card__name">Progress</span>
          <span class="card__text">For each country and indicator, the progress made over the past twelve months.</span>
        </a>
        <a class="card" href="{base}/maturity/#gov.policy--digital-transformation-strategy">
          <span class="card__name">Maturity</span>
          <span class="card__text">Progress compared across all countries, by topic and indicator.</span>
        </a>
      </section>

      <section class="col" aria-labelledby="col-data">
        <h2 class="col__title" id="col-data">Datasets</h2>
        <div class="card">
          <a class="card__name" href="{base}/finance/all/">Finance</a>
          <span class="card__text">The financing of digital transformation, by country and topic.</span>
          <span class="chips">
            <a href="{base}/finance/budgets/">National budgets</a>
            <a href="{base}/finance/">Non-state finance</a>
            <a href="{base}/finance/all/">The two combined</a>
          </span>
        </div>
        <a class="card" href="{base}/catalogue/">
          <span class="card__name">Catalogue</span>
          <span class="card__text">A searchable index of over {catalogue_n} news stories and other documents held in Corpus.</span>
        </a>
        <div class="card">
          <a class="card__name" href="{base}/datasets/">Ad hoc datasets</a>
          <span class="card__text">Compiled for standalone research projects.</span>
          <span class="chips">
            <a href="{base}/datasets/data-centres/">Data centres</a>
            <a href="{base}/datasets/institution-hosting/">Hosting of state institutions</a>
          </span>
        </div>
      </section>

    </div>

    <p class="map__foot">Corpus is a public good for all analysts, planners and practitioners working towards the digital transformation of Africa.</p>

  </main>
  <script>
    // The vh-scaled sizes fit most screens; this catches the rest by stepping the
    // map's font size down until it no longer overflows (floor 75%); the masthead keeps its size.
    (function () {{
      var map = document.getElementById('main'), cols = document.querySelectorAll('.col');
      function over() {{
        for (var i = 0; i < cols.length; i++) if (cols[i].scrollHeight > cols[i].clientHeight + 1) return true;
        return false;
      }}
      function fit() {{
        map.style.fontSize = '';
        if (getComputedStyle(document.querySelector('.site-wrap')).overflow !== 'hidden') return;
        for (var pct = 100; pct > 75 && over(); pct -= 2.5) {{
          map.style.fontSize = pct - 2.5 + '%';
        }}
      }}
      fit();
      addEventListener('resize', fit);
      if (document.fonts) document.fonts.ready.then(fit);
    }})();
  </script>

{foot}
</div>
</body>
</html>
"""




# The countries page — the 54-box matrix, moved off the home page on 2026-08-24
# (Bill).
#
# **Why it is a page and not a section.** The matrix is the largest single object
# on the site — 54 boxes, most of a viewport — and it sat above Regions and
# Topics, which meant a reader who wanted either had to scroll past all of it.
# It also gives `{SITE_BASE}/countries/` something to be: that URL held the 54
# per-country directories and no index, so it 404'd, and it was one of the three
# dead links the nav carried until this morning. The nav points at it properly
# now instead of at the home page's `#countries` anchor.
#
# **The region matrix joined it at the foot of the page on 2026-09-02** (Bill),
# off the home page — see `build_countries()`. Same reasoning, one step later:
# eight boxes are not worth an address of their own, but they were still most
# of a viewport sitting between a reader and Topics on the home page. The nav
# label became "Countries & Regions" the same day, the URL did not.
COUNTRIES_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Countries &amp; Regions — Data Landscapers</title>
<meta name="description" content="Every African country in the Data Landscapers corpus, and the eight regions and blocs, with the number of primary sources held for each.">
<link rel="canonical" href="{base}/countries/">
{styles}
<link rel="icon" href="{favicon}" type="image/svg+xml">
<meta property="og:title" content="Countries &amp; Regions — Data Landscapers">
<meta property="og:description" content="Every African country in the Data Landscapers corpus, and the eight regions and blocs, with the number of primary sources held for each.">
<meta property="og:url" content="{base}/countries/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Data Landscapers">
{ga}
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container">

    <!-- h2, matching Regions below (Bill, 2026-09-02) — both are sections of one
         page, not a page title, so neither takes an h1. The page title above them
         is the house page head (2026-09-11), which every page carries. -->
    <header class="article-header">
      {feedback}
      <h1 class="article-header__title">Countries &amp; Regions{about}</h1>
    </header>
    {panel}
    <h2 class="section-heading section-heading--sc" id="countries">Countries</h2>
    <div class="boxes">
{countries}
    </div>

    <!-- The region matrix, moved off the home page on 2026-09-02 (Bill) to sit
         below the countries it does not overlap with, rather than above them
         where a reader wanting a country had to scroll past it. Same heading
         level as Countries above (Bill, 2026-09-02) — the two are sections of
         one page, not a page and a sub-page. -->
    <h2 class="section-heading section-heading--sc" id="regions">Regions</h2>
    <div class="boxes boxes--regions">
{regions}
    </div>

    <div class="colophon">
      <strong>About this page</strong>
      <dl>
        <!-- **"Last updated", not "Built"** *(Bill, 2026-08-25)*. The date is the same date
             either way, but the two words say different things to a reader: "built" describes
             what the machine did, and reads as scaffolding leaking onto the page; "last updated"
             answers the question the reader actually has, which is how current this is. The
             country pages carry the same change, in the colophon and in the subtitle. -->
        <dt>Last updated</dt><dd class="mono">{built}</dd>
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
    """`site/countries/index.html` — the country matrix, and the region matrix
    beneath it (moved off the home page on 2026-09-02, Bill).

    Written into the directory that already holds the 54 per-country folders, so
    `/countries/` resolves and `/countries/AGO/` goes on resolving beneath it."""
    by_place = load_stats()["by_place"]
    built = date.today().isoformat()
    # The intros and caveats gave way to the ⓘ by the title, from content/info.md (Bill, 2026-10-22).
    about, panel = info("Countries & Regions")
    doc = COUNTRIES_TEMPLATE.format(
        about=about, panel=panel,
        feedback=feedback("Countries & Regions", f"{SITE_BASE}/countries/"),
        base=SITE_BASE, built=built,
        favicon=f"{MAIN_SITE}/assets/favicon.svg",
        chrome=chrome("countries", depth=1), foot=foot(depth=1),
        styles=styles(1), ga=ga(),
        countries=country_boxes(by_place),
        regions=region_boxes(by_place),
    )
    out = SITE / "countries"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(external_links(doc), encoding="utf-8")
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
{ga}
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container">

    <header class="article-header">
      {feedback}
      <h1 class="article-header__title">Topics</h1>
    </header>
    <p class="section-intro">{topics_intro}</p>

{topics}

    <p class="caveat">{topics_caveat}</p>

    <div class="colophon">
      <strong>About this page</strong>
      <dl>
        <dt>Built</dt><dd class="mono">{built}</dd>
        <dt>Vocabulary</dt><dd><a href="{base}/methodology/lookups/#topics">{base}/methodology/lookups/#topics</a></dd>
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

    Written into the directory that holds the topic folders, so `/topics/`
    resolves; the retired `/topics/{slug}/` beneath it forward (`topic-page.py`). `ntopics` counts the
    taxonomy rather than the catalogue's distinct topics: the page prints a box
    per subject in the file, so the count in the page description and the number
    of boxes are the same number, which they were not while one counted what had
    been tagged.

    **The stat bar came off on 2026-09-09** *(Bill)*. Two totals over a page whose
    whole content is the same counts, broken out by subject."""
    s = load_stats()
    built = date.today().isoformat()
    ntopics = len(taxonomy_lib.keys())
    doc = TOPICS_TEMPLATE.format(
        feedback=feedback("Topics", f"{SITE_BASE}/topics/"),
        base=SITE_BASE, built=built,
        favicon=f"{MAIN_SITE}/assets/favicon.svg",
        chrome=chrome("topics", depth=1), foot=foot(depth=1),
        styles=styles(1), ga=ga(),
        ntopics=ntopics,
        topics=topic_grid(s["by_topic"]),
        topics_intro=copy_inline("home", "topics-intro"),
        topics_caveat=copy_inline("topics", "caveat", n=f"{ntopics}"),
    )
    out = SITE / "topics"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(external_links(doc), encoding="utf-8")
    return out / "index.html"


def build() -> Path:
    s = load_stats()
    # Floored to the ten thousand, so the box does not move with every night's ingest.
    catalogue_n = f"{s['documents'] // 10_000 * 10_000:,}"
    ntopics = sum(1 for slug in taxonomy_lib.keys()
                  if (OUTPUTS / "topics" / slug.replace(".", "-")
                      / f"{slug.replace('.', '-')}-monthly.md").exists())
    doc = TEMPLATE.format(
        base=SITE_BASE, favicon=f"{MAIN_SITE}/assets/favicon.svg",
        catalogue_n=catalogue_n, ntopics=ntopics,
        chrome=chrome(None, depth=0), foot=foot(depth=0),
        styles=styles(0, "home.css"), ga=ga(),
    )
    SITE.mkdir(parents=True, exist_ok=True)
    out = SITE / "index.html"
    out.write_text(external_links(doc), encoding="utf-8")
    return out


if __name__ == "__main__":
    print(build())
    print(build_countries())
    print(build_topics())
    print("stats file the page will prefer, once REPO-STATUS writes it:")
    print("  outputs/catalogue/stats.json")
    print(STATS_SHAPE)
