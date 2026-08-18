#!/usr/bin/env python3
"""home.py — the home page (documentation/design.md §3, §6).

    python scripts/home.py   ->  site/index.html

Promoted from prototypes/build-home-page.py once the wireframe was agreed;
revised 2026-08-11 to Bill's numbered change list. The shape, in order: the
header mirrors data-landscapers.com's own nav with Corpus added on the left;
a second nav bar for the corpus sections; a highlighted total/this-year/
this-month stat bar; a two-line statement of what the corpus is; Countries,
Regions and Topics as heading, intro text and a box matrix each.

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
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
OUTPUTS = CORPUS / "outputs"
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

# Level-2 display names for the sub-topic rows that open under each topic tile
# (Bill, 2026-08-13, item 7). Same provenance caveat as L1 above: the canonical
# labels live in `lookups/taxonomy.md` in OSINT, outside `outputs/`, so these
# are a provisional working copy derived from the slugs — edit here to match
# the taxonomy, or fold both into the stats file once it publishes (OSINT #9).
# A slug with no entry falls back to its own Level-2 segment, title-cased.
SUBTOPIC_NAMES = {
    "dpi.govtech": "GovTech", "dpi.pay": "Payments", "dpi.id": "Digital ID",
    "dpi.exchange": "Data exchange", "dpi.registry": "Registries",
    "dpi.mis": "Management info systems",
    "gov.policy": "Policy & strategy", "gov.legislate": "Legislation",
    "gov.protect": "Data protection", "gov.regional": "Regional governance",
    "gov.standards": "Standards", "gov.discourse": "Public discourse",
    "infra.connect": "Connectivity", "infra.cybersec": "Cybersecurity",
    "infra.store": "Data centres & storage", "infra.energy": "Energy",
    "infra.capacity": "Network capacity",
    "finance.new": "New investment", "finance.budget": "Public budgets",
    "finance.mou": "MoUs & commitments",
    "tech.ai": "Artificial intelligence", "tech.industry": "Industry",
    "tech.innovate": "Innovation",
    "include.access": "Access", "include.divides": "Digital divides",
    "capacity.training": "Training", "capacity.research": "Research",
    "capacity.literacy": "Digital literacy",
    "data.statistics": "Statistics", "data.open": "Open data",
    "data.satellite": "Satellite & geospatial",
    "geopol.usa": "United States", "geopol.china": "China",
    "geopol.eu": "European Union", "geopol.india": "India",
    "geopol.gulf": "Gulf states",
    "digital.rural": "Rural digitalisation", "digital.localgov": "Local government",
}


def subtopic_label(slug: str) -> str:
    """Readable name for a Level-2 slug, falling back to its own segment."""
    if slug in SUBTOPIC_NAMES:
        return SUBTOPIC_NAMES[slug]
    tail = slug.split(".", 1)[-1]
    return tail.replace("-", " ").replace("_", " ").title()

# Intro copy under each heading. Topics still carries the text that used to
# sit in its card, unchanged. Countries is Bill's rewrite, edited straight in
# site/index.html on 2026-08-11 and copied back here so a rebuild doesn't
# revert it. Regions had no prior card to draw from, so that paragraph is CC's.
COUNTRIES_INTRO = (
    "Each country page contains four reports: A status summary; A breakdown "
    "of progress recorded over the past twelve months; a summary of news "
    "reported in the last month; and a financial record of investments or "
    "commitments made by non-state institutions since 2015."
)
REGIONS_INTRO = (
    "Sources tagged to a region, a bloc or the continent as a whole, rather "
    "than to a single named country — the African Union, ECOWAS, SADC and "
    "the other regional bodies, plus the broader continental and cross-"
    "regional tags. A source is filed under a country whenever it names one; "
    "these are what is left. Eight groupings are tracked here, from the four "
    "sub-regions to the continental and global tags."
)
TOPICS_INTRO = (
    "A controlled vocabulary in a strict single-parent tree, so a category "
    "rolls up to every topic beneath it. A source carries as many topics as "
    "it evidences, and is counted under each of them. Data protection, "
    "digital identity, cross-border data flows, connectivity, artificial "
    "intelligence and the rest. Each topic resolves to the documents that "
    "evidence it, not to a summary of them."
)

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
    codes rather than countries (Bill, 2026-08-11, item 8)."""
    codes = sorted(c for c in by_place if c.startswith("X"))
    top = max(by_place[c] for c in codes) or 1
    return "\n".join(
        f'<a class="box" href="{SITE_BASE}/regions/{c}/" title="{c}"'
        f' style="--fill:{by_place[c] / top:.3f}">'
        f'<span class="box__k">{e(REGION_NAMES.get(c, c))}</span>'
        f'<span class="box__n">{by_place[c]:,}</span></a>'
        for c in codes)


def bulletin_section() -> str:
    """The daily bulletin, at the top of the page because it is the one thing here that is about
    today *(2026-08-17)*.

    Built from the two documents' own frontmatter rather than from a count of its own: the bulletin
    states the window it covers and how many sources it found, and a second implementation of that
    would be a second answer. The section is omitted entirely where the documents do not exist —
    unlike the country and topic boxes, which link ahead of the pages they open (design.md §8),
    there is nothing here to be accurate *about* until a build has written one."""
    meta = {}
    for kind in ("country", "topic"):
        path = OUTPUTS / "bulletins" / f"{kind}-bulletin.md"
        if not path.exists():
            return ""
        head = {}
        for line in path.read_text(encoding="utf-8").split("---", 2)[1].splitlines():
            k, _, v = line.partition(":")
            head[k.strip()] = v.strip()
        meta[kind] = head

    window = f"{meta['country'].get('window_start', '')} to {meta['country'].get('window_end', '')}"
    intro =(f"Sources published in the last two days &mdash; {e(window)}. "
             f"Each item is summarised once and cross-referenced from every other country, "
             f"region or topic it touches. The bulletin is rewritten at every build and keeps "
             f"nothing: what it reports is kept by the country, region and topic reports.")
    boxes = "\n".join(
        f'<a class="box" href="{SITE_BASE}/bulletins/{kind}-bulletin.html" style="--fill:0.6">'
        f'<span class="box__k">By {kind}</span>'
        f'<span class="box__n">{e(meta[kind].get("items", "0"))}</span></a>'
        for kind in ("country", "topic"))
    return (f'\n    <h2 class="section-heading" id="bulletin">Daily bulletin</h2>\n'
            f'    <p class="section-intro">{intro}</p>\n'
            f'    <div class="boxes boxes--regions">\n{boxes}\n    </div>\n'
            f'    <p class="caveat">The count is the sources in the window, and both bulletins '
            f'cover the same ones. The corpus acquires in batches, so a quiet bulletin means '
            f'nothing was published on those two days rather than that nothing arrived.</p>\n')


def topic_boxes(by_topic: dict[str, int]) -> str:
    """Each Level-1 tile is a toggle that opens a full-width row of its Level-2
    sub-topics beneath it (Bill, 2026-08-13, item 7). The sub-topic boxes link
    to `/topics/{slug}/` pages whether or not those pages are built yet — the
    same pull-exhaustively/publish-selectively rule as the country boxes. Since
    2026-08-14 they are built: `scripts/topic-page.py` writes the landing page
    each box opens, and the *All {category}* box at the end of the row opens the
    Level-1 index page it also writes.

    The panel is a sibling of its tile inside the same `.tboxes` grid. A hidden
    panel carries the `hidden` attribute and so is `display:none` and takes no
    grid space; an open panel spans every column (`grid-column: 1 / -1`), so it
    lands on the row directly under the tile that opened it and pushes the rest
    of the matrix down. That keeps the tile matrix a plain CSS grid — the only
    script is the click handler that flips `hidden` and `aria-expanded`."""
    roll = Counter()
    children: dict[str, list[tuple[str, int]]] = {}
    for slug, n in by_topic.items():
        k = slug.split(".")[0]
        roll[k] += n
        children.setdefault(k, []).append((slug, n))

    top = max(roll.values()) or 1
    out = []
    for k, _ in roll.most_common():
        pid = f"topic-{k}"
        label = e(L1.get(k, k))
        tile = (
            f'<button type="button" class="tbox" aria-expanded="false"'
            f' aria-controls="{pid}" style="--fill:{roll[k] / top:.3f}">'
            f'<span class="tbox__l">{label}</span>'
            f'<span class="tbox__s">{k}.*</span>'
            f'<span class="tbox__n">{roll[k]:,}</span>'
            f'<span class="tbox__x" aria-hidden="true"></span></button>'
        )
        kids = sorted(children.get(k, []), key=lambda x: -x[1])
        ktop = max((n for _, n in kids), default=1) or 1
        # The dot survives in the vocabulary, where it means something, and does not go into a
        # path, where it reads as an extension — so the link says `dpi-pay`, as the built tree
        # does. Until 2026-08-14 it said `dpi.pay` and every sub-topic box 404'd; nothing caught
        # it because nothing was published under either name.
        subboxes = "\n".join(
            f'<a class="sbox" href="{SITE_BASE}/topics/{slug.replace(".", "-")}/" title="{slug}"'
            f' style="--fill:{n / ktop:.3f}">'
            f'<span class="sbox__l">{e(subtopic_label(slug))}</span>'
            f'<span class="sbox__n">{n:,}</span></a>'
            for slug, n in kids)
        panel = (
            f'<div class="tsub" id="{pid}" role="region"'
            f' aria-label="{label} sub-topics">\n'
            f'<div class="tsub__inner">\n{subboxes}\n'
            f'<a class="sbox sbox--all" href="{SITE_BASE}/topics/{k}/">'
            f'<span class="sbox__l">All {label}</span>'
            f'<span class="sbox__n" aria-hidden="true">&rarr;</span></a>\n'
            f'</div>\n</div>'
        )
        out.append(tile + "\n" + panel)
    return "\n".join(out)


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<script>document.documentElement.classList.add('js');</script>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Corpus — Data Landscapers</title>
<meta name="description" content="A living record of digital transformation and data governance across Africa: {docs} sources, country and topic reports, and the finance behind them.">
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
      <a href="{main_site}/" class="site-logo">
        <img src="assets/logo.png" alt="Data Landscapers" class="site-logo__img">
        <span class="site-logo__text">Data Landscapers
          <span class="site-logo__sub">Mapping Africa&rsquo;s data landscape</span>
        </span>
      </a>
      <nav class="site-nav" aria-label="Main navigation">
        <a href="{base}/" class="active">Corpus</a>
        <a href="{main_site}/writing/">Writing</a>
        <a href="{main_site}/lab/">Lab</a>
        <a href="{main_site}/portfolio/">Portfolio</a>
        <a href="{main_site}/about/">About</a>
        <a href="{main_site}/contact/">Contact</a>
        <a href="{main_site}/search/">Search</a>
      </nav>
    </div>
  </header>

  <nav class="corpus-nav" aria-label="Corpus navigation">
    <div class="corpus-nav__inner">
      <a href="{base}/#bulletin">Bulletin</a>
      <a href="{base}/#countries">Countries</a>
      <a href="{base}/#regions">Regions</a>
      <a href="{base}/#topics">Topics</a>
      <a href="{base}/#finance">Finance</a>
      <a href="{base}/#catalogue">Catalogue</a>
      <a href="{base}/#methodology">Methodology</a>
    </div>
  </nav>

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
      <p>A living record of digital transformation and data governance across Africa. Compiled from primary sources. Updated daily.</p>
    </div>

{bulletin}
    <h2 class="section-heading" id="countries">Countries</h2>
    <p class="section-intro">{countries_intro}</p>
    <div class="boxes">
{countries}
    </div>
    <p class="caveat">Sources held per country. A source tagged to several countries is counted under each, so these sum to more than the country total above: they measure coverage, not documents.</p>

    <h2 class="section-heading" id="regions">Regions</h2>
    <p class="section-intro">{regions_intro}</p>
    <div class="boxes boxes--regions">
{regions}
    </div>
    <p class="caveat">{regional} sources are tagged to a region or bloc rather than to a country, and are not counted in the Countries figures above.</p>

    <h2 class="section-heading" id="topics">Topics</h2>
    <p class="section-intro">{topics_intro}</p>
    <div class="tboxes">
{topics}
    </div>
    <p class="caveat">Level-1 categories, rolled up from the {ntopics} topics beneath them. A source carries as many topics as it evidences, so these also sum to more than the total. Click a topic to open its sub-topics.</p>

    <h2 class="section-heading" id="finance">Finance</h2>
    <p class="section-intro section-intro--todo">The finance behind the corpus &mdash; investments, budgets and commitments recorded across the source base. This section is still to be written; content to follow.</p>

    <h2 class="section-heading" id="catalogue">Catalogue</h2>
    <p class="section-intro section-intro--todo">The full browse-and-filter view over every source in the corpus. This section is still to be written; content to follow.</p>

    <h2 class="section-heading" id="methodology">Methodology</h2>
    <p class="section-intro section-intro--todo">How the corpus is built, tagged and kept current &mdash; the taxonomy, the sources and the editions. This section is still to be written; content to follow.</p>

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
        <a href="{main_site}/">data-landscapers.com</a>
        <a href="{base}/method/">Method</a>
      </div>
    </div>
  </footer>

</div>

{script}
</body>
</html>
"""


# Topic tiles: click a Level-1 tile to open a row of its sub-topics beneath it.
# Progressive enhancement — the panels are plain visible markup, so with no JS
# every sub-topic link is reachable. The `js` class on <html> (set in <head>
# before first paint) hands the CSS the collapsed default; from there the only
# job of this script is to flip `aria-expanded`, which the CSS turns into the
# open/closed state. One tile open at a time. Kept out of TEMPLATE.format so
# its braces are not read as format fields.
SCRIPT = """<script>
(function () {
  var tiles = Array.prototype.slice.call(
    document.querySelectorAll('.tbox[aria-controls]'));
  tiles.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var isOpen = btn.getAttribute('aria-expanded') === 'true';
      tiles.forEach(function (other) {
        other.setAttribute('aria-expanded',
          (other === btn && !isOpen) ? 'true' : 'false');
      });
    });
  });
})();
</script>"""


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
        countries=country_boxes(by_place), countries_intro=e(COUNTRIES_INTRO),
        regions=region_boxes(by_place), regions_intro=e(REGIONS_INTRO),
        topics=topic_boxes(s["by_topic"]), topics_intro=e(TOPICS_INTRO),
        regional=f"{regional:,}", ntopics=len(s["by_topic"]), script=SCRIPT,
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
    print("  outputs/catalogue/stats.json")
    print(STATS_SHAPE)
