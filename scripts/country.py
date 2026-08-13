#!/usr/bin/env python3
"""country.py — the country page (documentation/design.md §3).

    python scripts/country.py            builds every country
    python scripts/country.py KEN        builds one

Promoted from prototypes/build-country-page.py once Bill approved the KEN
mock-up (2026-08-11 commit "Country page: add nav, drop crumb, stat-bar in
place of the 4 boxes, ..."). Three things changed on promotion, beyond
generalising from one country to all of them:

  - Output moved from a flat `prototypes/country-{ISO}.html` to
    `site/countries/{ISO}/index.html` (+ `finance.html` alongside it), to
    match the URL `{SITE_BASE}/countries/{ISO}/` the home page already links
    every country box to (`scripts/home.py`).
  - The report rows now read the edition off the *PDF* filename, which
    carries the date, and link the "Read" button at the undated HTML
    permalink `render.py` now produces (Bill, 2026-08-11: report HTML has no
    date in it, so the page has a permanent URL).
  - The two CSV downloads and the logo/CSS paths pointed at `../upstream/`
    and `../build/`, which is fine for a prototype opened by double-click but
    wrong once this is deployed: GitHub Pages serves `site/` only
    (`.github/workflows/deploy.yml`). Each country's non-state-finance CSV is
    now copied into its own page folder, and the catalogue CSV into one
    shared `site/catalogue/` copy, both by `build()` below.

Nothing is typed by hand: the counts come from the report frontmatter and the
catalogue, the report rows from the PDFs in `site/reports/{ISO3}/`, and both
finance tables from `{ISO3}-nonstate.csv`.

Country and region names are duplicated from OSINT's `lookups/countries.csv`
because the build cannot read outside `outputs/` — the same duplication
`scripts/home.py` already carries, and logs/notes-for-osint.md #9 flags it as a
standing note rather than a pattern to repeat deliberately.

Budget work is suspended, so `{ISO3}-summary.csv` is not read and no budget
block appears.
"""

from __future__ import annotations

import csv
import html
import re
import shutil
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
UPSTREAM = CORPUS / "upstream"
SITE = CORPUS / "site"
OUT = SITE / "countries"
CATALOGUE_DIR = SITE / "catalogue"

SITE_BASE = "https://corpus.data-landscapers.com"
MAIN_SITE = "https://data-landscapers.com"
FINANCE_CUTOFF = 2022  # years before this are aggregated into one pivot column

# ISO3 -> full country name, from lookups/countries.csv (see module docstring
# and logs/notes-for-osint.md #9). Two entries carry proper accents the source CSV
# doesn't (Côte d'Ivoire, São Tomé and Príncipe) — a typographic fix, not a
# different name.
FULL_NAMES = {
    "AGO": "Angola", "BDI": "Burundi", "BEN": "Benin", "BFA": "Burkina Faso",
    "BWA": "Botswana", "CAF": "Central African Republic",
    "CIV": "Côte d'Ivoire", "CMR": "Cameroon", "COD": "DR Congo",
    "COG": "Congo", "COM": "Comoros", "CPV": "Cape Verde", "DJI": "Djibouti",
    "DZA": "Algeria", "EGY": "Egypt", "ERI": "Eritrea", "ETH": "Ethiopia",
    "GAB": "Gabon", "GHA": "Ghana", "GIN": "Guinea", "GMB": "Gambia",
    "GNB": "Guinea-Bissau", "GNQ": "Equatorial Guinea", "KEN": "Kenya",
    "LBR": "Liberia", "LBY": "Libya", "LSO": "Lesotho", "MAR": "Morocco",
    "MDG": "Madagascar", "MLI": "Mali", "MOZ": "Mozambique",
    "MRT": "Mauritania", "MUS": "Mauritius", "MWI": "Malawi", "NAM": "Namibia",
    "NER": "Niger", "NGA": "Nigeria", "RWA": "Rwanda", "SDN": "Sudan",
    "SEN": "Senegal", "SLE": "Sierra Leone", "SOM": "Somalia",
    "SSD": "South Sudan", "STP": "São Tomé and Príncipe", "SWZ": "Eswatini",
    "SYC": "Seychelles", "TCD": "Chad", "TGO": "Togo", "TUN": "Tunisia",
    "TZA": "Tanzania", "UGA": "Uganda", "ZAF": "South Africa", "ZMB": "Zambia",
    "ZWE": "Zimbabwe",
}

KIND = {
    "status": ("Status report", "A summary of the status of all known systems and instruments"),
    "monthly": ("Monthly update", "A summary of news reported in the last month"),
    "progress": ("Twelve-month progress report", "A breakdown of progress recorded over the past twelve months"),
}

# Column definitions for the dictionary the full table offers, from
# FINANCE-COMPILE.md § "CSV export". Two columns the CSV carries are not
# described there — see logs/notes-for-osint.md #7 — and are marked as read off
# the data.
FIELDS = [
    ("recipient_country", "ISO-3 code of the country the commitment is tagged to. The join key.", "FINANCE-COMPILE.md"),
    ("start_year", "Year the commitment starts, or the year it was announced where no start is stated.", "FINANCE-COMPILE.md"),
    ("end_year", "Year the commitment ends, where one is stated.", "FINANCE-COMPILE.md"),
    ("financier", "Canonical financier name, resolved from financier_slug. Never key analysis on this field.", "FINANCE-COMPILE.md"),
    ("sector", "Subject slug's display name, from the wiki taxonomy.", "FINANCE-COMPILE.md"),
    ("instrument", "Loan, grant, equity, guarantee or other form the money takes.", "FINANCE-COMPILE.md"),
    ("commitment_usd_m", "Amount committed, US$ millions, converted from the announcing party's own currency at a dated rate.", "FINANCE-COMPILE.md"),
    ("amount_basis", "What the figure is: commitment, disbursement, or other.", "read off the data"),
    ("amount_quality", "How firm the figure is: exact, rounded, estimated, reported, imputed, stated.", "read off the data"),
    ("status", "Status of the commitment as last reported — approved, launched, signed, completed.", "FINANCE-COMPILE.md"),
    ("title", "Record title: financier, what, and year.", "FINANCE-COMPILE.md"),
    ("description", "The full record block, including quoted source text.", "FINANCE-COMPILE.md"),
    ("beneficiary_type", "Government, private sector, civil society or other.", "FINANCE-COMPILE.md"),
    ("recipient_organisation", "Name of the receiving organisation, where stated.", "FINANCE-COMPILE.md"),
    ("original_amount", "The amount as announced, in the currency announced.", "FINANCE-COMPILE.md"),
    ("project_id", "Financier's own project identifier, where one is published.", "FINANCE-COMPILE.md"),
    ("iati_activity_id", "IATI activity identifier, where the financier publishes to IATI.", "FINANCE-COMPILE.md"),
    ("url", "The publisher's own link to the source the record was read from.", "FINANCE-COMPILE.md"),
    ("financier_slug", "Canonical financier identifier. The key to group or join financiers on.", "FINANCE-COMPILE.md"),
    ("record", "Slug of the wiki record this row was compiled from.", "FINANCE-COMPILE.md"),
]

csv.field_size_limit(10 ** 9)


# ── reading upstream ──────────────────────────────────────────────

def frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    head = text[3:text.find("\n---", 3)]
    return {k.strip(): v.strip() for k, v in
            (l.split(":", 1) for l in head.splitlines() if ":" in l)}


def editions(iso: str) -> list[dict]:
    """The published editions, read off the *PDF* filenames — the PDF is the
    dated artefact (`render.py`, 2026-08-11), so it is the one whose name
    tells a reader which edition is current. The HTML link is derived from
    it by dropping the trailing `-{edition}`, which is exactly how `render.py`
    names the undated permalink. Only the newest edition of each kind is
    offered; earlier PDFs stay on disk (retained editions, §9) but are not
    linked from the country page.
    """
    found: dict[str, list[tuple[str, str, str]]] = {}
    for f in sorted((SITE / "reports" / iso).glob(f"{iso}-*.pdf")):
        parts = f.stem.split("-")
        if len(parts) < 2:
            continue
        kind = parts[1]
        edition = "-".join(parts[-3:])
        # The HTML permalink is {iso}-{kind}.html, with no period — it is always
        # the current document (render.py, Bill 2026-08-13). Deriving it by
        # stripping the edition off the PDF stem used to leave the period in
        # (`AGO-monthly-2026-07.html`) and would now link to a file that no
        # longer exists.
        found.setdefault(kind, []).append((edition, f.name, f"{iso}-{kind}.html"))
    rows = []
    for kind in ("status", "monthly", "progress"):
        if kind not in found:
            continue
        edition, pdf_name, html_name = sorted(found[kind], reverse=True)[0]
        rows.append({
            "kind": kind, "label": KIND[kind][0], "blurb": KIND[kind][1],
            "edition": edition, "html": html_name, "pdf": pdf_name,
        })
    return rows


def report_meta(iso: str, kind: str) -> dict:
    for f in (UPSTREAM / "reports" / iso).glob(f"{iso}-{kind}*.md"):
        return frontmatter(f.read_text(encoding="utf-8"))
    return {}


def catalogue(iso: str) -> tuple[int, int, list[tuple[str, int]]]:
    """Records held for the place, records held in all, and the commonest
    publishers for the place."""
    n = total = 0
    pubs: dict[str, int] = defaultdict(int)
    with open(UPSTREAM / "catalogue" / "raw-catalogue.csv", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            total += 1
            if iso in (row.get("places") or ""):
                n += 1
                pubs[(row.get("publisher") or "").strip()] += 1
    top = sorted(((p, c) for p, c in pubs.items() if p), key=lambda x: -x[1])[:6]
    return n, total, top


def finance(iso: str) -> list[dict]:
    """Non-state commitments for the place, or [] if the base holds none —
    SDN currently has no `{ISO3}-nonstate.csv` at all, and an absent file is
    the same fact as an empty one from the page's point of view."""
    f = UPSTREAM / "non-state-finance" / f"{iso}-nonstate.csv"
    if not f.exists():
        return []
    with open(f, encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def built_from() -> str:
    return (UPSTREAM / "BUILT-FROM").read_text(encoding="utf-8").strip()


# ── rendering ─────────────────────────────────────────────────────

def e(s: str) -> str:
    return html.escape(s or "")


def num(v: float) -> str:
    return f"{v:,.0f}" if v == int(v) else f"{v:,.1f}"


def year(v: str) -> int | None:
    """Most `start_year`/`end_year` cells are a bare year; a few carry a
    parenthetical like `2015 (2015-07-06)`. The leading four digits are the
    year in every case observed, so read those rather than fail the page."""
    m = re.match(r"\s*(\d{4})", v or "")
    return int(m.group(1)) if m else None


def pivot(rows: list[dict]) -> str:
    """Sector by year, US$m committed.

    An empty cell is a year in which nothing was committed to that sector, and
    is left empty rather than zeroed: a zero reads as a measured quantity.
    Sectors are ordered by total, so the table opens with what the money went
    to rather than with an alphabet.

    Years before FINANCE_CUTOFF are aggregated into one leading '-2022'
    column: those early years each carry few commitments, so a column per
    year back to a country's first was mostly empty cells (Bill, 2026-08-11).
    """
    def col(y: int) -> str:
        return str(y) if y >= FINANCE_CUTOFF else f"-{FINANCE_CUTOFF}"

    yrs = {y for y in (year(r.get("start_year")) for r in rows) if y is not None}
    cols = ([f"-{FINANCE_CUTOFF}"] if any(y < FINANCE_CUTOFF for y in yrs) else []) \
        + [str(y) for y in sorted(y for y in yrs if y >= FINANCE_CUTOFF)]
    cell: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for r in rows:
        y = year(r.get("start_year"))
        if y is None:
            continue
        cell[r.get("sector") or "(unstated)"][col(y)] += float(r.get("commitment_usd_m") or 0)
    order = sorted(cell, key=lambda s: -sum(cell[s].values()))

    head = "".join(f'<th class="num">{c}</th>' for c in cols)
    body = []
    for s in order:
        cells = "".join(
            f'<td class="num">{num(cell[s][c])}</td>' if cell[s].get(c) else '<td class="num zero"></td>'
            for c in cols)
        body.append(f'<tr><th scope="row">{e(s)}</th>{cells}'
                    f'<td class="num total">{num(sum(cell[s].values()))}</td></tr>')
    foot = "".join(
        f'<td class="num">{num(sum(cell[s][c] for s in order))}</td>' for c in cols)
    grand = num(sum(v for s in order for v in cell[s].values()))

    return f"""<table class="pivot">
        <thead><tr><th scope="col">Sector</th>{head}<th class="num total">Total</th></tr></thead>
        <tbody>
{chr(10).join(body)}
        </tbody>
        <tfoot><tr><th scope="row">All sectors</th>{foot}<td class="num total">{grand}</td></tr></tfoot>
      </table>"""


def full_rows(rows: list[dict], cols: list[str]) -> str:
    """Every column of every row, the factsheet's shape. `url` renders as a
    link on the publisher's own domain, because a bare URL in a cell is
    unreadable and the domain is the part a reader judges."""
    out = []
    for r in rows:
        tds = []
        for c in cols:
            v = r.get(c, "") or ""
            if c == "url" and v:
                dom = re.sub(r"^https?://(www\.)?", "", v).split("/")[0]
                tds.append(f'<td><a href="{e(v)}">{e(dom)}</a></td>')
            elif c in ("commitment_usd_m", "start_year", "end_year"):
                tds.append(f'<td class="num mono">{e(v)}</td>')
            elif c == "description":
                tds.append(f'<td class="wrapcell">{e(v)}</td>')
            else:
                tds.append(f"<td>{e(v)}</td>")
        out.append("<tr>" + "".join(tds) + "</tr>")
    return "\n".join(out)


MONTHS = ("January February March April May June July August September "
          "October November December").split()


def period_label(kind: str, period: str) -> str:
    """`2026-07-01 to 2026-08-05` reads as a range on a progress report and as
    noise on a monthly one, where the month is the point. Taken from the
    frontmatter, not the filename: a progress report is named for the month it
    was cut in but covers the twelve months before it."""
    if not period:
        return ""
    if kind == "monthly":
        y, m, _ = period.split(" ")[0].split("-")
        return f"{MONTHS[int(m) - 1]} {y}"
    return period.replace(" to ", " &ndash; ")


def report_rows(rows: list[dict], iso: str) -> str:
    out = []
    for r in rows:
        meta = report_meta(iso, r["kind"])
        counts = ""
        if meta.get("ledger_rows"):
            counts = (f'{meta["ledger_rows"]} tracked'
                      + (f', <span class="nh">{meta["not_held"]} not held</span>'
                         if meta.get("not_held") else ""))
        label = period_label(r["kind"], meta.get("period", ""))
        period = f' &nbsp;·&nbsp; {label}' if label else ""
        out.append(f"""
      <div class="report-row">
        <div class="report-row__main">
          <div class="report-row__kind">{r['label']}</div>
          <div class="report-row__blurb">{r['blurb']}</div>
          <div class="report-row__meta">Edition of <span class="mono">{r['edition']}</span>{period}
            {' &nbsp;·&nbsp; ' + counts if counts else ''}</div>
        </div>
        <div class="report-row__acts">
          <a class="btn" href="../../reports/{iso}/{r['html']}">Read</a>
          <a class="btn btn--accent" href="../../reports/{iso}/{r['pdf']}">&darr; PDF</a>
        </div>
      </div>""")
    if not out:
        return '<p class="table-note">No reports are yet published for this place.</p>'
    return "\n".join(out)


# ── chrome (site header/footer — matches scripts/home.py exactly) ────

CHROME = """  <header class="site-header">
    <div class="site-header__inner">
      <a href="{main_site}/" class="site-logo">
        <img src="../../assets/logo.png" alt="Data Landscapers" class="site-logo__img">
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
      <a href="{base}/#countries" class="active">Countries</a>
      <a href="{base}/#regions">Regions</a>
      <a href="{base}/#topics">Topics</a>
      <a href="{base}/finance/">Finance</a>
      <a href="{base}/catalogue/">Catalogue</a>
      <a href="{base}/method/">Method</a>
    </div>
  </nav>"""

FOOT = """  <footer class="site-footer">
    <div class="site-footer__inner">
      <p class="site-footer__copy"><a href="https://creativecommons.org/licenses/by/4.0/" style="color:inherit;border-bottom:none;">CC BY 4.0</a> {year} Bill Anderson / Data Landscapers Ltd &nbsp;·&nbsp; Registered in the UK · Co. No. 16040544</p>
      <div class="site-footer__links">
        <a href="{main_site}/">data-landscapers.com</a>
        <a href="{base}/method/">Method</a>
        <a href="{base}/manifest.csv">Manifest</a>
      </div>
    </div>
  </footer>"""


COUNTRY = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — Data Landscapers</title>
<meta name="description" content="{name}: digital transformation and data governance. Reports, sources and non-state finance, from the Data Landscapers base.">
<link rel="canonical" href="{base}/countries/{iso}/">
<link rel="stylesheet" href="../../assets/css/main.css">
<link rel="stylesheet" href="../../assets/css/home.css">
<link rel="stylesheet" href="../../assets/css/country.css">
<link rel="icon" href="{favicon}" type="image/svg+xml">
<meta property="og:title" content="{name} — Data Landscapers">
<meta property="og:description" content="{name}: digital transformation and data governance, from the Data Landscapers base.">
<meta property="og:url" content="{base}/countries/{iso}/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Data Landscapers">
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container">

    <div class="country-head">
      <h1>{name}</h1>
      <div class="country-head__meta">{iso} &nbsp;·&nbsp; page built {built} &nbsp;·&nbsp; base at commit {commit}</div>
    </div>

    <div class="stat-bar">
      <div class="stat-bar__inner">
        <span class="stat-bar__item">Systems &amp; instruments <strong>{tracked}</strong></span>
        <span class="stat-bar__item">Primary sources held <strong>{sources}</strong></span>
        <span class="stat-bar__item">Financial commitments <strong>{fin_n}</strong></span>
      </div>
    </div>

    <h2 class="section-heading">Reports</h2>
{reports}

    <h2 class="section-heading">Sources</h2>
    <p>The base holds <strong>{sources} records</strong> for {name}, of {cat_total} in all. The catalogue is metadata &mdash; title, publisher, date, facets and the publisher&rsquo;s own link &mdash; never the source body. Every figure in the reports above resolves to one of these records.</p>
    <p class="pubs">Most frequent publishers: {publishers}</p>
    <div class="table-acts">
      <a class="btn" href="{base}/catalogue/#places={iso}">Browse {name} in the catalogue &rarr;</a>
      <a class="btn" href="../../catalogue/raw-catalogue.csv" download>&darr; Catalogue CSV</a>
    </div>

    <h2 class="section-heading">Non-state finance</h2>
{finance_section}

    <div class="callout">
      Vault access, source bodies included, is granted on request. <a href="{base}/method/">How this base is built &rarr;</a>
    </div>

    <div class="colophon">
      <strong>About this page</strong>
      <dl>
        <dt>Built</dt><dd class="mono">{built}</dd>
        <dt>Derived from</dt><dd>Data Landscapers source base, commit <code>{commit}</code></dd>
        <dt>Verify</dt><dd>Hash any file above and look it up in <a href="{base}/manifest.csv">manifest.csv</a></dd>
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

FINANCE_BLOCK = """    <p>Commitments to {name}&rsquo;s digital sector from financiers other than the state &mdash; development finance, foundations, vendors and operators. Figures are the amount announced, in the year announced, converted from the announcing party&rsquo;s own currency at a dated rate. They are commitments, not disbursements, and a multi-year commitment sits wholly in its start year.</p>

{pivot}
    <p class="table-note">US$m committed, by sector and year of commitment. &lsquo;-{cutoff}&rsquo; aggregates every year before {cutoff}. An empty cell is a year with no commitment recorded, not a zero.</p>

    <div class="table-acts">
      <a class="btn" href="finance.html">Full table &mdash; {fin_n} commitments, all {ncols} fields &rarr;</a>
      <a class="btn btn--accent" href="{iso}-nonstate.csv" download>&darr; Download CSV</a>
    </div>"""

FINANCE_EMPTY = """    <p>No non-state finance commitments are currently held for {name}.</p>"""


FINANCE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — non-state finance — Data Landscapers</title>
<meta name="description" content="Every non-state commitment to {name}'s digital sector held in the Data Landscapers base, all fields, searchable and downloadable.">
<link rel="canonical" href="{base}/countries/{iso}/finance.html">
<link rel="stylesheet" href="../../assets/css/main.css">
<link rel="stylesheet" href="../../assets/css/home.css">
<link rel="stylesheet" href="../../assets/css/country.css">
<link rel="icon" href="{favicon}" type="image/svg+xml">
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container container--wide">

    <div class="country-head">
      <div class="crumb"><a href="{base}/#countries">Countries</a> &nbsp;/&nbsp; <a href="index.html">{name}</a> &nbsp;/&nbsp; Non-state finance</div>
      <h1>Non-state finance</h1>
      <div class="country-head__meta">{name} &nbsp;·&nbsp; {fin_n} commitments &nbsp;·&nbsp; US${fin_total}m &nbsp;·&nbsp; {y0}&ndash;{y1} &nbsp;·&nbsp; base at commit {commit}</div>
    </div>

    <p>Every non-state commitment the base holds for {name}, every field, exactly as the CSV carries it. One row per commitment; each is tagged to one country only, so per-country totals sum without double-counting. The <code>url</code> column is the publisher&rsquo;s own link to the source the row was read from.</p>

    <div class="data-table-wrap">
      <div class="data-table-controls">
        <span class="dt-title">{name} &mdash; non-state finance</span>
        <input type="search" id="q" placeholder="Search&hellip;" aria-label="Search the table">
        <span class="data-table-count" id="count">{fin_n} rows</span>
        <a class="btn" href="{iso}-nonstate.csv" download style="padding:0.35rem 0.9rem;">&darr; Download CSV</a>
        <a class="btn" href="{iso}-nonstate-fields.csv" download style="padding:0.35rem 0.9rem;">&darr; Download metadata</a>
      </div>
      <div class="data-table-scroll">
        <table class="data-table" id="fin">
          <thead><tr>{head}</tr></thead>
          <tbody>
{rows}
          </tbody>
        </table>
      </div>
    </div>

    <div class="colophon">
      <strong>About this table</strong>
      <dl>
        <dt>Built</dt><dd class="mono">{built}</dd>
        <dt>Source</dt><dd><code>outputs/non-state-finance/{iso}-nonstate.csv</code>, compiled by the finance pass</dd>
        <dt>Derived from</dt><dd>Data Landscapers source base, commit <code>{commit}</code></dd>
        <dt>Fields</dt><dd><a href="{iso}-nonstate-fields.csv">{iso}-nonstate-fields.csv</a> &mdash; what each column means</dd>
        <dt>Licence</dt><dd><a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></dd>
      </dl>
    </div>

  </div>
  </main>

{foot}

</div>

<script>
(function () {{
  var tbody = document.querySelector('#fin tbody');
  var rows = Array.prototype.slice.call(tbody.rows);
  var q = document.getElementById('q'), count = document.getElementById('count');
  var total = rows.length;

  q.addEventListener('input', function () {{
    var term = q.value.toLowerCase(), shown = 0;
    rows.forEach(function (r) {{
      var ok = !term || r.textContent.toLowerCase().indexOf(term) > -1;
      r.style.display = ok ? '' : 'none';
      if (ok) shown++;
    }});
    count.textContent = (term ? shown + ' of ' + total : total) + ' rows';
  }});

  var dir = {{}};
  document.querySelectorAll('#fin thead th').forEach(function (th, i) {{
    th.addEventListener('click', function () {{
      dir[i] = !dir[i];
      var s = dir[i] ? 1 : -1, num = th.dataset.sort === 'num';
      rows.sort(function (a, b) {{
        var x = a.cells[i].textContent.trim(), y = b.cells[i].textContent.trim();
        if (num) {{
          var nx = parseFloat(x) , ny = parseFloat(y);
          return ((isNaN(nx) ? -Infinity : nx) - (isNaN(ny) ? -Infinity : ny)) * s;
        }}
        return x.localeCompare(y) * s;
      }});
      rows.forEach(function (r) {{ tbody.appendChild(r); }});
      document.querySelectorAll('#fin thead th').forEach(function (o) {{
        o.classList.remove('sort-asc', 'sort-desc');
      }});
      th.classList.add(dir[i] ? 'sort-asc' : 'sort-desc');
    }});
  }});
}})();
</script>
</body>
</html>
"""


def ensure_catalogue_csv() -> None:
    """One shared copy for every country's "Catalogue CSV" download —
    5.9 MB duplicated 54 times is real weight for nothing (§7's PDF-growth
    reasoning applies equally here); one copy under site/catalogue/ is what
    the {base}/catalogue/ nav link already points a reader towards."""
    CATALOGUE_DIR.mkdir(parents=True, exist_ok=True)
    src = UPSTREAM / "catalogue" / "raw-catalogue.csv"
    dst = CATALOGUE_DIR / "raw-catalogue.csv"
    if dst.exists():
        dst.unlink()
    shutil.copyfile(src, dst)


def build(iso: str) -> list[Path]:
    name = FULL_NAMES.get(iso, iso)
    meta = frontmatter((UPSTREAM / "reports" / iso / f"{iso}-status.md")
                       .read_text(encoding="utf-8"))
    fin = finance(iso)
    n_place, n_all, pubs = catalogue(iso)
    commit = built_from()[:12]
    built = date.today().isoformat()

    out_dir = OUT / iso
    out_dir.mkdir(parents=True, exist_ok=True)

    common = dict(
        base=SITE_BASE, main_site=MAIN_SITE, iso=iso, name=name,
        favicon=f"{MAIN_SITE}/assets/favicon.svg",
        chrome=CHROME.format(base=SITE_BASE, main_site=MAIN_SITE),
        foot=FOOT.format(base=SITE_BASE, main_site=MAIN_SITE, year=built[:4]),
        built=built, commit=commit, fin_n=len(fin),
    )

    if fin:
        cols = list(fin[0].keys())
        ys = [y for y in (year(r.get("start_year")) for r in fin) if y is not None]
        amounts = [float(r["commitment_usd_m"]) for r in fin if r.get("commitment_usd_m")]
        finance_section = FINANCE_BLOCK.format(
            name=name, iso=iso, pivot=pivot(fin), cutoff=FINANCE_CUTOFF,
            fin_n=len(fin), ncols=len(cols))
    else:
        cols, ys, amounts = [], [], []
        finance_section = FINANCE_EMPTY.format(name=name)

    (out_dir / "index.html").write_text(COUNTRY.format(
        tracked=meta.get("ledger_rows", "&mdash;"),
        sources=f"{n_place:,}", cat_total=f"{n_all:,}",
        publishers=", ".join(f"<span>{e(p)} ({c})</span>" for p, c in pubs),
        reports=report_rows(editions(iso), iso),
        finance_section=finance_section,
        **common), encoding="utf-8")

    written = [out_dir / "index.html"]

    if fin:
        numeric = ("commitment_usd_m", "start_year", "end_year")
        head = "".join(
            "<th{}>{} &#8597;</th>".format(
                ' data-sort="num"' if c in numeric else "",
                c.replace("_", "_<wbr>"))
            for c in cols)
        (out_dir / "finance.html").write_text(FINANCE.format(
            head=head,
            rows=full_rows(sorted(fin, key=lambda r: r.get("start_year", ""), reverse=True), cols),
            fin_total=f"{sum(amounts):,.0f}",
            y0=(min(ys) if ys else "&mdash;"), y1=(max(ys) if ys else "&mdash;"),
            **common), encoding="utf-8")
        written.append(out_dir / "finance.html")

        fin_csv = UPSTREAM / "non-state-finance" / f"{iso}-nonstate.csv"
        dst = out_dir / f"{iso}-nonstate.csv"
        if dst.exists():
            dst.unlink()
        shutil.copyfile(fin_csv, dst)
        written.append(dst)

        fields_path = out_dir / f"{iso}-nonstate-fields.csv"
        with open(fields_path, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["field", "definition", "defined_in"])
            known = {f[0] for f in FIELDS}
            w.writerows([f for f in FIELDS if f[0] in cols]
                        + [[c, "", "not documented"] for c in cols if c not in known])
        written.append(fields_path)

    return written


def main() -> int:
    ensure_catalogue_csv()
    isos = sys.argv[1:] or sorted(
        d.name for d in (UPSTREAM / "reports").iterdir()
        if d.is_dir() and d.name in FULL_NAMES
    )
    for iso in isos:
        paths = build(iso)
        print(f"{iso}  {len(paths)} files  ->  {paths[0].parent.relative_to(CORPUS)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
