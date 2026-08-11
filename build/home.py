#!/usr/bin/env python3
"""home.py — the home page (DESIGN.md §3, §6).

    python build/home.py   ->  site/index.html

Promoted from prototypes/build-home-page.py once the wireframe was agreed.
The shape, in order: a two-line statement of what the corpus is; four cards
(Countries, Topics, Finance, Catalogue); documents by year and by the last
six months; a box per country; a box per Level-1 subject.

**Where the numbers come from.** `REPO-STATUS.md` will write nightly counts
into `outputs/catalogue/stats.json` (NOTES-FOR-OSINT.md #8). Until it does,
this reads `upstream/catalogue/raw-catalogue.csv` and counts the same things
itself — `load_stats()` prefers the published file and falls back, so the
page is right today and needs no rewrite when the file lands.

Two caveats are structural rather than decorative, and travel with their
numbers on the page because they are the numbers a reader would otherwise
misquote:

- **The month table measures capture, not activity.** Its shape is set by
  when the sweeps ran, not by how much happened in Africa (`REPO-STATUS.md`).
- **A document tagged with several places is counted under each**, so the
  country boxes sum to more than the document total. They measure coverage,
  not documents.

Country and topic boxes link to `{SITE_BASE}/countries/{ISO3}/` and
`{SITE_BASE}/topics/{slug}/` regardless of whether those pages exist yet —
pull exhaustively, publish selectively (DESIGN.md §8): the box is honest
about what the base holds even before the page that would serve it is
written.
"""

from __future__ import annotations

import csv
import html
import json
from collections import Counter
from datetime import date
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
UPSTREAM = CORPUS / "upstream"
SITE = CORPUS / "site"
SITE_BASE = "https://corpus.data-landscapers.com"
MAIN_SITE = "https://data-landscapers.com"

STATS_SHAPE = """{
  "generated": "YYYY-MM-DD",     # the run that wrote it
  "documents": 0,                # markdown sources in raw/, PDFs excluded
  "by_year":  {"2026": 0},       # publication year, from `published:`
  "by_month": {"2026-08": 0},    # year-month, same field; sums to <= the year
  "by_place": {"KEN": 0},        # places facet; multi-tagged, so sums high
  "by_topic": {"dpi.id": 0}      # topics facet; roll-up to Level 1 by prefix
}"""

# Level-1 labels from `lookups/taxonomy.md`, and country names from
# `lookups/countries.csv` — both in OSINT, neither in `outputs/`. The build is
# not allowed to read outside `outputs/` (NOTES-FOR-OSINT.md), so for now they
# are duplicated here. Two copies of one vocabulary is exactly the failure
# DESIGN.md §8 refuses elsewhere, so this is a note for OSINT (#9), not a
# pattern to repeat deliberately.
L1 = {
    "infra": "ICT Infrastructure", "dpi": "Digital public infrastructure",
    "gov": "Governance", "include": "Inclusion", "tech": "Technology",
    "geopol": "Geopolitics", "capacity": "Capacity", "digital": "Digitalisation",
    "data": "Data", "finance": "Finance",
}

CARDS = [
    ("Countries", "countries/", [
        "Fifty-four countries, each with a status report, a monthly update and a twelve-month progress report.",
        "Every system and instrument carries the date its position was established, because most of them change.",
        "Where the base holds no reliable statement, the country page says so and counts it.",
        "Coverage is deliberately uneven. The record goes deep where the work is, and stays thin elsewhere.",
    ]),
    ("Topics", "topics/", [
        "A controlled vocabulary in a strict single-parent tree, so a category rolls up to every topic beneath it.",
        "A source carries as many topics as it evidences, and is counted under each of them.",
        "Data protection, digital identity, cross-border data flows, connectivity, artificial intelligence and the rest.",
        "Each topic resolves to the documents that evidence it, not to a summary of them.",
    ]),
    ("Finance", "data/finance/", [
        "Commitments to the digital sector from financiers other than the state.",
        "Development finance institutions, foundations, vendors and operators, at one row per commitment.",
        "Amounts are given as announced, in the currency announced, converted at a dated rate.",
        "These are commitments rather than disbursements, and nothing here implies the money was spent.",
    ]),
    ("Catalogue", "catalogue/", [
        "Title, publisher, date, facets and the publisher's own link, for every source held.",
        "Metadata only. The catalogue points at the original and never republishes it.",
        "Filter by place, topic and year; a filtered view keeps its own address, so it can be cited.",
        "Access to the full base, source bodies included, is granted on request.",
    ]),
]

csv.field_size_limit(10 ** 9)


# ── stats ─────────────────────────────────────────────────────────

def load_stats() -> dict:
    """Prefer the published nightly stats; count the catalogue if absent."""
    published = UPSTREAM / "catalogue" / "stats.json"
    if published.exists():
        return json.loads(published.read_text(encoding="utf-8"))

    by_year, by_month, by_place, by_topic = Counter(), Counter(), Counter(), Counter()
    n = 0
    with open(UPSTREAM / "catalogue" / "raw-catalogue.csv", encoding="utf-8-sig") as fh:
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


def year_bands(by_year: dict[str, int], cut: int = 2022) -> list[tuple[str, int]]:
    """The wireframe's bands: everything before 2022, then a column a year.
    Older material is one band because it is a baseline, not a trend."""
    older = sum(v for y, v in by_year.items() if y.isdigit() and int(y) < cut)
    bands = [(f"&le;{cut - 1}", older)]
    for y in range(cut, max(int(y) for y in by_year if y.isdigit()) + 1):
        bands.append((str(y), by_year.get(str(y), 0)))
    return bands


def last_months(by_month: dict[str, int], n: int = 6) -> list[tuple[str, int]]:
    keys = sorted(k for k in by_month if len(k) == 7)[-n:]
    names = ("January February March April May June July August September "
             "October November December").split()
    return [(f"{names[int(k[5:]) - 1]} {k[:4]}", by_month[k]) for k in keys]


# ── rendering ─────────────────────────────────────────────────────

def e(s: str) -> str:
    return html.escape(str(s))


def bar_table(rows: list[tuple[str, int]], label: str) -> str:
    """A count table that also shows its own shape. The bar is a background on
    the row, not a chart: it needs no library and it degrades to a plain table."""
    top = max(v for _, v in rows) or 1
    body = "\n".join(
        f'<tr><th scope="row">{k}</th>'
        f'<td class="barcell"><span class="bar" style="width:{v / top * 100:.1f}%"></span>'
        f'<span class="barnum">{v:,}</span></td></tr>'
        for k, v in rows)
    return f"""<table class="bars">
        <caption>{label}</caption>
        <tbody>
{body}
        </tbody>
      </table>"""


def country_boxes(by_place: dict[str, int]) -> str:
    """Shaded by volume, so an uneven base looks uneven at a glance rather than
    presenting as even coverage. Every box links to its country page whether or
    not that page is built yet (DESIGN.md §8: pull exhaustively, publish
    selectively) — a live link that 404s until the page lands is honest about
    what the base holds; hiding it would not be."""
    codes = sorted(c for c in by_place if not c.startswith("X"))
    top = max(by_place[c] for c in codes) or 1
    return "\n".join(
        f'<a class="box" href="{SITE_BASE}/countries/{c}/"'
        f' style="--fill:{by_place[c] / top:.3f}">'
        f'<span class="box__k">{c}</span><span class="box__n">{by_place[c]:,}</span></a>'
        for c in codes)


def topic_boxes(by_topic: dict[str, int]) -> str:
    roll = Counter()
    for slug, n in by_topic.items():
        roll[slug.split(".")[0]] += n
    top = max(roll.values()) or 1
    return "\n".join(
        f'<a class="tbox" href="{SITE_BASE}/topics/{k}/" style="--fill:{roll[k] / top:.3f}">'
        f'<span class="tbox__l">{e(L1.get(k, k))}</span>'
        f'<span class="tbox__s">{k}.*</span>'
        f'<span class="tbox__n">{roll[k]:,}</span></a>'
        for k, _ in roll.most_common())


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Corpus — Data Landscapers</title>
<meta name="description" content="A working record of digital transformation and data governance across Africa: {docs} sources, country and topic reports, and the finance behind them.">
<link rel="canonical" href="{base}/">
<link rel="stylesheet" href="assets/css/main.css">
<link rel="stylesheet" href="assets/css/home.css">
<link rel="icon" href="{favicon}" type="image/svg+xml">
<meta property="og:title" content="Corpus — Data Landscapers">
<meta property="og:description" content="A working record of digital transformation and data governance across Africa.">
<meta property="og:url" content="{base}/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Data Landscapers">
</head>
<body>
<div class="site-wrap">

  <header class="site-header">
    <div class="site-header__inner">
      <a href="{base}/" class="site-logo">
        <img src="assets/logo.png" alt="Data Landscapers" class="site-logo__img">
        <span class="site-logo__text">Data Landscapers
          <span class="site-logo__sub">Mapping Africa&rsquo;s data landscape</span>
        </span>
      </a>
      <nav class="site-nav" aria-label="Main navigation">
        <a href="{base}/countries/">Countries</a>
        <a href="{base}/regions/">Regions</a>
        <a href="{base}/topics/">Topics</a>
        <a href="{base}/catalogue/">Catalogue</a>
        <a href="{base}/data/">Data</a>
        <a href="{base}/method/">Method</a>
      </nav>
    </div>
  </header>

  <main id="main">
  <div class="container">

    <div class="hero">
      <p>A working record of digital transformation and data governance across Africa, compiled from primary sources and published as it stands.</p>
      <p class="hero__sub"><span class="n">{docs}</span> sources behind three reports for every country, with every figure dated to when it was true and every gap counted rather than left silent.</p>
    </div>

    <div class="cards">
{cards}
    </div>

    <div class="section-label">What the base holds</div>
    <div class="two-up">
      <div>
{by_year}
        <p class="caveat">Publication year of each source. Everything published before {cut} is held as one band, because it is the baseline the record starts from rather than a trend.</p>
      </div>
      <div>
{by_month}
        <p class="caveat"><strong>This measures capture, not activity.</strong> The shape of it is set by when the sweeps ran and which countries were being initialised &mdash; a month with more documents is a month the base collected more, not a month in which more happened.</p>
      </div>
    </div>

    <div class="section-label">Countries</div>
    <div class="boxes">
{countries}
    </div>
    <p class="caveat">Sources held per country. A source tagged to several countries is counted under each, so these sum to more than the total above: they measure coverage, not documents. A further {regional} are tagged to a region or bloc rather than to a country.</p>

    <div class="section-label">Topics</div>
    <div class="tboxes">
{topics}
    </div>
    <p class="caveat">Level-1 categories, rolled up from the {ntopics} topics beneath them. A source carries as many topics as it evidences, so these also sum to more than the total.</p>

    <div class="colophon">
      <strong>About this page</strong>
      <dl>
        <dt>Built</dt><dd class="mono">{built}</dd>
        <dt>Counts</dt><dd>{counts_from}</dd>
        <dt>Derived from</dt><dd>Data Landscapers source base, commit <code>{commit}</code></dd>
        <dt>Licence</dt><dd><a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></dd>
      </dl>
    </div>

  </div>
  </main>

  <footer class="site-footer">
    <div class="site-footer__inner">
      <p class="site-footer__copy"><a href="https://creativecommons.org/licenses/by/4.0/" style="color:inherit;border-bottom:none;">CC BY 4.0</a> {year} Bill Anderson / Data Landscapers Ltd &nbsp;·&nbsp; Registered in the UK · Co. No. 16040544</p>
      <div class="site-footer__links">
        <a href="{main_site}/">data-landscapers.com</a>
        <a href="{base}/method/">Method</a>
        <a href="{base}/manifest.csv">Manifest</a>
      </div>
    </div>
  </footer>

</div>
</body>
</html>
"""


def build() -> Path:
    s = load_stats()
    by_place = s["by_place"]
    regional = sum(v for k, v in by_place.items() if k.startswith("X"))

    cards = "\n".join(
        f"""      <a class="card" href="{SITE_BASE}/{href}">
        <h2>{title}</h2>
        <div class="card__n">{sub}</div>
        <ul>{"".join(f"<li>{line}</li>" for line in lines)}</ul>
        <div class="card__go">Browse {title.lower()} &rarr;</div>
      </a>"""
        for (title, href, lines), sub in zip(CARDS, (
            f"{len([c for c in by_place if not c.startswith('X')])} countries",
            f"{len({t.split('.')[0] for t in s['by_topic']})} categories, "
            f"{len(s['by_topic'])} topics",
            "commitments, by country and sector",
            f"{s['documents']:,} records, metadata only")))

    commit = (UPSTREAM / "BUILT-FROM").read_text(encoding="utf-8").strip()[:12]
    built = date.today().isoformat()
    doc = TEMPLATE.format(
        base=SITE_BASE, main_site=MAIN_SITE, built=built, commit=commit,
        favicon=f"{MAIN_SITE}/assets/favicon.svg",
        docs=f"{s['documents']:,}", cut=2022, cards=cards, year=built[:4],
        by_year=bar_table(year_bands(s["by_year"]), "Sources by publication year"),
        by_month=bar_table(last_months(s["by_month"]), "Sources by month, last six months"),
        countries=country_boxes(by_place), topics=topic_boxes(s["by_topic"]),
        regional=f"{regional:,}", ntopics=len(s["by_topic"]),
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
    print("stats file the page will prefer, once REPO-STATUS writes it:")
    print("  upstream/catalogue/stats.json")
    print(STATS_SHAPE)
