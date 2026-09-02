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
  - The two CSV downloads and the logo/CSS paths pointed at `../outputs/`
    and `../build/`, which is fine for a prototype opened by double-click but
    wrong once this is deployed: GitHub Pages serves `site/` only
    (`.github/workflows/deploy.yml`). Each country's non-state-finance CSV is
    now copied into its own page folder, and the catalogue CSV into one
    shared `site/catalogue/` copy, both by `build()` below.

Nothing is typed by hand: the counts come from the report frontmatter and the
catalogue, the report rows from the PDFs in `site/reports/{ISO3}/`, and both
finance tables from `{ISO3}-nonstate.csv`.

The two finance tables are built differently, on purpose *(2026-08-19)*. The
sector-by-year pivot on `index.html` is an aggregate of a few dozen cells and is
rendered here, into the HTML. The full commitment table on `finance.html` is not:
it is drawn in the browser by `site/assets/js/datatable.js` from the published
CSV, which is the same file the page already offers for download. Baking it in
cost 74 KB of HTML for South Africa's 54 rows and gave the reader neither
sorting-by-column nor filtering; the component gives both, and the all-Africa
table it is shared with (`scripts/finance.py`) could not be baked in at all at
1,257 rows. The cost is that `finance.html` shows nothing with JavaScript off,
which the `<noscript>` block answers with the CSV link.

Country and region names are duplicated from OSINT's `lookups/countries.csv`
because the build cannot read outside `outputs/` — the same duplication
`scripts/home.py` already carries, and osint-corpus-exchange/notes-for-osint.md #9 flags it as a
standing note rather than a pattern to repeat deliberately.

Budget work is suspended, so `{ISO3}-summary.csv` is not read and no budget figures appear. The
page nevertheless carries a *Public budgeting and expenditure* heading saying the work is under
way *(Bill, 2026-08-25)* — the same reasoning the wiki applies to a known vacuum: a reader who
finds nothing about budgets cannot tell an absent subject from an absent finding, and the heading
is what makes the difference visible. It states a horizon, not a placeholder, so it carries no
"coming soon" and no date.
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from copy_lib import copy_inline  # noqa: E402
from chrome_lib import chrome, external_links, foot, ga, styles  # noqa: E402
import editions  # noqa: E402  — §9's filename grammar has one implementation

CORPUS = Path(__file__).resolve().parent.parent
OUTPUTS = CORPUS / "outputs"
SITE = CORPUS / "site"
OUT = SITE / "countries"
CATALOGUE_DIR = SITE / "catalogue"

SITE_BASE = "https://corpus.data-landscapers.io"
MAIN_SITE = "https://data-landscapers.io"
FINANCE_CUTOFF = 2022  # years before this are aggregated into one pivot column

# The one field dictionary for every non-state finance table, in `site/metadata/`.
# Hand-maintained by Bill; nothing here writes it, and a build that cannot find it
# should say so rather than quietly link a 404.
METADATA_CSV = "non-state-finance-metadata.csv"

# ISO3 -> full country name, from lookups/countries.csv (see module docstring
# and osint-corpus-exchange/notes-for-osint.md #9). Two entries carry proper accents the source CSV
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
    "status": ("Status report", copy_inline("country", "report-status")),
    "monthly": ("Monthly update", copy_inline("country", "report-monthly")),
    # "Progress report", not "Twelve-month progress report" *(Bill, 2026-08-25)*. The window is
    # in the document's own title and in the row beneath this label, so the qualifier was saying
    # twice what the reader was about to read once — and it was the only one of the three labels
    # that did not read as a document type.
    "progress": ("Progress report", copy_inline("country", "report-progress")),
}

# The status report changes shape when `STATUS-INIT` has run on a country: a table of ledger rows
# becomes a narrative answering 37 questions about where the country actually stands, and the old
# blurb would describe the wrong document to a reader deciding whether to open it.
BASELINE_BLURB = copy_inline("country", "report-status-baseline")

# The field dictionary used to be generated here, from a FIELDS list duplicating the
# schema FINANCE-COMPILE.md defines. Retired 2026-08-19 (Bill): one hand-maintained
# file at site/metadata/non-state-finance-metadata.csv now serves every table, so the
# schema is stated once rather than in fifty-four generated copies plus a Python list
# that had already drifted from its stated authority — its definitions for instrument,
# status and beneficiary_type each cited FINANCE-COMPILE.md for vocabularies that file
# does not contain.

csv.field_size_limit(10 ** 9)


# ── reading upstream ──────────────────────────────────────────────

def frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    head = text[3:text.find("\n---", 3)]
    return {k.strip(): v.strip() for k, v in
            (l.split(":", 1) for l in head.splitlines() if ":" in l)}


def publish_finance_csvs(iso: str, out_dir: Path, cols: list[str]) -> dict[str, str]:
    """Publish the country's finance CSV as a dated edition (§9).

    **The finance CSVs are editions; the catalogue is not** *(Bill, 2026-08-18)*. These are a
    compiled finding of ours that a reader may quote a figure out of, so they carry the same
    discipline as the reports — dated in the filename, retained edition over edition, a new one
    only when the content changes, and no undated URL for a citation to slip off. The catalogue
    is a browse index over other people's records, and nobody cites it as of a date.

    **The per-country field dictionary is not written any more** *(Bill, 2026-08-19)*. Fifty-four
    `{ISO3}-nonstate-fields-{edition}.csv` files described one schema fifty-four times, and a
    schema described in fifty-four places is a schema that will eventually disagree with itself.
    One file now serves every non-state finance table — `site/metadata/{METADATA_CSV}`, which is
    Bill's and hand-maintained, not generated — and every page links it. It carries no edition
    date because it is not a finding: it is the description of a shape, and describing the same
    shape again in September is not a new edition of anything."""
    # **Published with LF endings, whatever the build machine writes** *(2026-08-24)*.
    # `editions.publish` mints a new edition when the bytes move, and CRLF-vs-LF moves
    # the bytes without moving a single value. `csv.writer` emits `\r\n`; git on Windows
    # normalises that away on commit and git on Linux does not, so the compiled source in
    # `outputs/` and the published copy in `site/` can disagree on line endings alone —
    # and then *every* run mints an edition for all 54 countries. That is exactly what a
    # CSS-only rebuild did on 2026-08-24: 53 new dated CSVs, not one of which differed
    # from its predecessor by a character. §9 says a published file is never revised; it
    # follows that a new edition has to mean new content, so the comparison must not be
    # able to see the line endings. Normalising here rather than in `editions.publish`
    # keeps that function byte-exact for the PDFs it also publishes.
    src = (OUTPUTS / "non-state-finance" / f"{iso}-nonstate.csv").read_bytes()
    data, _ = editions.publish(src.replace(b"\r\n", b"\n"),
                               out_dir, f"{iso}-nonstate", ".csv")
    return {"csv_name": data.name, "fields_name": f"../../metadata/{METADATA_CSV}",
            "csv_edition": editions.edition_of(data.stem) or ""}


def report_editions(iso: str) -> list[dict]:
    """The published editions, read off the *PDF* filenames — the PDF is the
    dated artefact (`render.py`, 2026-08-11), so it is the one whose name
    tells a reader which edition is current. The HTML link is derived from
    it by dropping the trailing `-{edition}`, which is exactly how `render.py`
    names the undated permalink. Only the newest edition of each kind is
    offered; earlier PDFs stay on disk (retained editions, §9) but are not
    linked from the country page.

    **The edition is parsed and ordered by `editions.py`** *(2026-08-18)*.
    This used to take the last three hyphen-separated parts of the stem and sort the strings,
    which was right for exactly one filename grammar: §9's same-day `-2` suffix reads as
    `08-18-2` under that rule, and sorts wrong under it too. A country page that offers a
    superseded PDF looks completely normal, so this could only ever have been found by reading
    it."""
    found: dict[str, list[tuple[str, str, str]]] = {}
    for f in sorted((SITE / "reports" / iso).glob(f"{iso}-*.pdf")):
        parts = f.stem.split("-")
        edition = editions.edition_of(f.stem)
        if len(parts) < 2 or edition is None:
            continue
        kind = parts[1]
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
        edition, pdf_name, html_name = max(found[kind],
                                           key=lambda row: editions.edition_key(row[0]))
        rows.append({
            "kind": kind, "label": KIND[kind][0], "blurb": KIND[kind][1],
            "edition": edition, "html": html_name, "pdf": pdf_name,
        })
    return rows


def report_meta(iso: str, kind: str) -> dict:
    for f in (OUTPUTS / "reports" / iso).glob(f"{iso}-{kind}*.md"):
        return frontmatter(f.read_text(encoding="utf-8"))
    return {}


def catalogue(iso: str) -> tuple[int, int, list[str], list[dict]]:
    """Records held for the place, records held in all, the catalogue's column
    spec, and the place's own rows.

    **The rows come back because the page now publishes them** *(Bill, 2026-08-25,
    item 9)*. The country cut is the published catalogue with rows removed and
    nothing else — same columns, same order, cut by the same `places` test the
    count above is made with, so the number in the paragraph and the number of
    lines in the file cannot disagree.

    The commonest-publishers tally went at the same time: it was a ranking of who
    files the most press releases, which is a fact about the newswire rather than
    about the country, and it sat on the page as though it were a finding."""
    n = total = 0
    rows: list[dict] = []
    with open(OUTPUTS / "catalogue" / "raw-catalogue.csv", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        cols = list(reader.fieldnames or [])
        for row in reader:
            total += 1
            if iso in (row.get("places") or ""):
                n += 1
                rows.append(row)
    return n, total, cols, rows


def publish_catalogue_cut(iso: str, out_dir: Path, cols: list[str], rows: list[dict]) -> str:
    """Write `{ISO3}-catalogue.csv` beside the page and return its filename.

    **Not an edition, for the same reason the whole catalogue is not one** (`design.md` §9): it
    is an index over other people's records rather than a compiled finding of ours, so it lives
    at an undated URL and is republished wholesale on every build. That is the one place this
    file differs from the non-state finance CSV beside it, which *is* an edition and is dated.

    Written `utf-8-sig` with CRLF, which is `csv.DictWriter`'s own default and what
    `build-catalogue.py` writes — a country cut that opened worse in Excel than the whole file it
    came from would be the same mojibake `documentation/archived/catalogue-filtered-download.md` records
    against the large download on 2026-08-25, reintroduced one file down."""
    path = out_dir / f"{iso}-catalogue.csv"
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)
    return path.name


def finance(iso: str) -> list[dict]:
    """Non-state commitments for the place, or [] if the base holds none —
    SDN currently has no `{ISO3}-nonstate.csv` at all, and an absent file is
    the same fact as an empty one from the page's point of view."""
    f = OUTPUTS / "non-state-finance" / f"{iso}-nonstate.csv"
    if not f.exists():
        return []
    with open(f, encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


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

    # **"Topic", not "Sector"** *(Bill, 2026-08-25)*. The underlying CSV column is still `sector`
    # and is not renamed — it is the compiled field, and every published edition carries it — but
    # the word on the page was doing a different job from the word in the schema: a reader arriving
    # from the Topics tab reads these rows as topics, and "sector" collides with the economic sense
    # the finance vocabulary uses elsewhere.
    return f"""<table class="pivot">
        <thead><tr><th scope="col">Topic</th>{head}<th class="num total">Total</th></tr></thead>
        <tbody>
{chr(10).join(body)}
        </tbody>
        <tfoot><tr><th scope="row">All sectors</th>{foot}<td class="num total">{grand}</td></tr></tfoot>
      </table>"""


# `full_rows` retired 2026-08-19: the finance table is now drawn in the browser
# by assets/js/datatable.js from the published CSV, so the page no longer bakes
# a <tr> per commitment into its HTML. The rendering rules it carried — `url` as
# a link, the three numeric columns right-aligned, `description` allowed to wrap
# — moved to the `data-links`, `data-numeric` and clamp behaviour of the
# component, which applies them by column name rather than by position.


# `period_label()` and its month names retired 2026-08-25 (Bill). The row printed the window a
# second time — "Edition of 2026-08-25 · July 2026 · 102 tracked" against a document whose own
# title is "monthly update, July 2026", and "2025-08-01 – 2026-08-25" against a progress report
# that says the same in its heading. The blurb beside it now carries the window in words ("since
# the beginning of last month"), which is what a reader choosing between four documents needs;
# the exact dates belong in the document, not in the index to it.


def tracked(iso: str) -> tuple[str, str]:
    """Systems and instruments on this unit's ledger, and how many are ***Not held***.

    **Read from `ledger.csv`, not from the status report's frontmatter** *(2026-08-15)*. It was
    taken from the status report because that was where a ledger count happened to be written
    down; but the quantity is a property of the ledger, and once `STATUS-INIT` has run on a unit
    its status report is a narrative baseline that carries no such count. Taking it from the
    document would have emptied this tile on every country as initialisation reached it — quietly,
    because the read already had an em-dash fallback and would not have failed.

    Measures are excluded, exactly as `report-render.py` excludes them: a measure moves but has no
    current state to inventory, so it is not a system or an instrument and the tile does not say
    it is."""
    path = OUTPUTS / "reports" / iso / "ledger.csv"
    if not path.exists():
        return "&mdash;", ""
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if (r.get("kind") or "instrument") != "measure"]
    held = sum(1 for r in rows if (r.get("status") or "").split(",")[0].strip() == "Not held")
    return f"{len(rows):,}", (f"{held:,}" if held else "")


def report_rows(rows: list[dict], iso: str) -> str:
    n_tracked, n_not_held = tracked(iso)
    out = []
    for r in rows:
        meta = report_meta(iso, r["kind"])
        counts = ""
        if r["kind"] == "status" and meta.get("built_by") == "STATUS-INIT":
            # The baseline is not a ledger view, so a ledger count would describe the wrong
            # document. Its own scale is the question set it answers and the evidence behind it.
            counts = (f'{meta.get("sections_written", "&mdash;")} sections'
                      + (f', {meta["sources_cited"]} sources'
                         if meta.get("sources_cited") else ""))
            r = {**r, "blurb": BASELINE_BLURB}
        elif meta.get("ledger_rows"):
            # **The not-held count comes off the row** *(Bill, 2026-08-25)*. It is a fact about
            # the ledger's own completeness, which belongs inside the document where the marked
            # rows are visible and countable; on an index row it was a number with nothing to
            # attach to and read as a defect notice on the report a reader had not yet opened.
            counts = f'{meta["ledger_rows"]} sources tracked'
        out.append(f"""
      <div class="report-row">
        <div class="report-row__main">
          <div class="report-row__kind">{r['label']}</div>
          <div class="report-row__blurb">{r['blurb']}</div>
          <div class="report-row__meta">Edition of <span class="mono">{r['edition']}</span>
            {' &nbsp;·&nbsp; ' + counts if counts else ''}</div>
        </div>
        <div class="report-row__acts">
          <a class="btn" href="../../reports/{iso}/{r['html']}">Read</a>
          <a class="btn btn--accent" href="../../reports/{iso}/{r['pdf']}">&darr; PDF</a>
        </div>
      </div>""")
    if not out:
        return f'<p class="table-note">{copy_inline("country", "no-reports")}</p>'
    return "\n".join(out)


# ── chrome (site header/footer — matches scripts/home.py exactly) ────

CHROME = chrome("countries", depth=2)

FOOT = foot(depth=2)


COUNTRY = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — Data Landscapers</title>
<meta name="description" content="{name}: digital transformation and data governance. Reports, sources and non-state finance, from the Data Landscapers base.">
<link rel="canonical" href="{base}/countries/{iso}/">
{styles}
<link rel="icon" href="{favicon}" type="image/svg+xml">
<meta property="og:title" content="{name} — Data Landscapers">
<meta property="og:description" content="{name}: digital transformation and data governance, from the Data Landscapers base.">
<meta property="og:url" content="{base}/countries/{iso}/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Data Landscapers">
{ga}
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container">

    <div class="country-head">
      <h1>{name}</h1>
      <div class="country-head__meta">{iso} &nbsp;·&nbsp; last updated {built}</div>
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

    <h2 class="section-heading">Catalogue</h2>
    <p>{catalogue_intro}</p>
    <div class="table-acts">
      <a class="btn" href="{base}/catalogue/#places={iso}">Browse {name} in the catalogue &rarr;</a>
      <a class="btn btn--accent" href="{cat_csv}" download>&darr; {name} catalogue CSV</a>
    </div>

    <h2 class="section-heading">Non-state finance</h2>
{finance_section}

    <h2 class="section-heading">Public budgeting and expenditure</h2>
    <p>{budget_intro}</p>

    <div class="colophon">
      <strong>About this page</strong>
      <dl>
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

FINANCE_BLOCK = """    <p>Commitments to {name}&rsquo;s digital sector from financiers other than the state &mdash; development finance, foundations, vendors and operators. Figures are in US Dollars, converted from the announcing party&rsquo;s own currency at a rate dated to the year of announcement. They are commitments, not disbursements, and a multi-year commitment sits wholly in its start year.</p>

{pivot}
    <p class="table-note">US$m committed, by topic and year of commitment. &lsquo;-{cutoff}&rsquo; aggregates every year before {cutoff}. An empty cell is a year with no commitment recorded, not a zero.</p>

    <div class="table-acts">
      <a class="btn" href="finance.html">Full table &mdash; {fin_n} commitments, all {ncols} fields &rarr;</a>
      <a class="btn btn--accent" href="{csv_name}" download>&darr; Download CSV</a>
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
{styles}
<link rel="icon" href="{favicon}" type="image/svg+xml">
{ga}
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container container--wide">

    <div class="country-head">
      <div class="crumb"><a href="{base}/countries/">Countries</a> &nbsp;/&nbsp; <a href="index.html">{name}</a> &nbsp;/&nbsp; Non-state finance</div>
      <h1>Non-state finance</h1>
      <div class="country-head__meta">{name} &nbsp;·&nbsp; {fin_n} commitments &nbsp;·&nbsp; US${fin_total}m &nbsp;·&nbsp; {y0}&ndash;{y1}</div>
    </div>

    <p>Every non-state commitment the base holds for {name}. One row per commitment; each is tagged to one country only, so per-country totals sum without double-counting. <strong>Click any row to open the full record</strong> &mdash; the columns show what a reader scans by, and the rest of the fields sit underneath rather than four screens to the right. Sort on any column heading, filter with the dropdowns, and search across every field whether or not it is shown. The <code>url</code> column is the publisher&rsquo;s own link to the source the row was read from.</p>

    <div class="dl-datatable"
      data-src="{csv_name}"
      data-cols="start_year, financier, sector, instrument, commitment_usd_m, status, title, description, recipient_organisation, url"
      data-filters="financier, sector, instrument, status, beneficiary_type"
      data-numeric="start_year, end_year, commitment_usd_m"
      data-links="url"
      data-detail="description"
      data-sort="start_year:desc"
      data-empty="No commitment matches those filters.">
      <div class="dt-controls">
        <span class="dt-title">{name} &mdash; non-state finance</span>
        <span class="dt-count">{fin_n} rows</span>
        <a class="btn" href="{csv_name}" download>&darr; CSV</a>
        <a class="btn" href="{fields_name}" download>&darr; Metadata</a>
      </div>
      <noscript>
        <p>The table is drawn in the browser from <a href="{csv_name}">{csv_name}</a>. With JavaScript off, download that file &mdash; it is the same data, every row and every field, and the <a href="{fields_name}">field dictionary</a> says what each column means.</p>
      </noscript>
    </div>

    <div class="colophon">
      <strong>About this table</strong>
      <dl>
        <dt>Built</dt><dd class="mono">{built}</dd>
        <dt>Edition</dt><dd class="mono">{csv_edition}</dd>
        <dt>This file</dt><dd><a href="{csv_name}">{csv_name}</a> &mdash; a dated edition, retained as published and never revised</dd>
        <dt>Source</dt><dd><code>outputs/non-state-finance/{iso}-nonstate.csv</code>, compiled by the finance pass</dd>
        <dt>Fields</dt><dd><a href="{fields_name}">non-state-finance-metadata.csv</a> &mdash; what each column means. One dictionary for every country&rsquo;s table, not a copy per country</dd>
        <dt>Licence</dt><dd><a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></dd>
      </dl>
    </div>

  </div>
  </main>

{foot}

</div>

<script src="../../assets/js/datatable.js"></script>
</body>
</html>
"""


def ensure_catalogue_csv() -> None:
    """One shared copy for every country's "Catalogue CSV" download —
    5.9 MB duplicated 54 times is real weight for nothing (§7's PDF-growth
    reasoning applies equally here); one copy under site/catalogue/ is what
    the {base}/catalogue/ nav link already points a reader towards."""
    CATALOGUE_DIR.mkdir(parents=True, exist_ok=True)
    src = OUTPUTS / "catalogue" / "raw-catalogue.csv"
    dst = CATALOGUE_DIR / "raw-catalogue.csv"
    if dst.exists():
        dst.unlink()
    shutil.copyfile(src, dst)


def build(iso: str) -> list[Path]:
    name = FULL_NAMES.get(iso, iso)
    meta = frontmatter((OUTPUTS / "reports" / iso / f"{iso}-status.md")
                       .read_text(encoding="utf-8"))
    fin = finance(iso)
    n_place, n_all, cat_cols, cat_rows = catalogue(iso)
    built = date.today().isoformat()

    out_dir = OUT / iso
    out_dir.mkdir(parents=True, exist_ok=True)
    cat_csv = publish_catalogue_cut(iso, out_dir, cat_cols, cat_rows)

    common = dict(
        base=SITE_BASE, main_site=MAIN_SITE, iso=iso, name=name,
        favicon=f"{MAIN_SITE}/assets/favicon.svg",
        chrome=CHROME, foot=FOOT,
        built=built, fin_n=len(fin),
    )

    csv_names: dict[str, str] = {}
    if fin:
        cols = list(fin[0].keys())
        ys = [y for y in (year(r.get("start_year")) for r in fin) if y is not None]
        amounts = [float(r["commitment_usd_m"]) for r in fin if r.get("commitment_usd_m")]
        # **The CSVs are published before the pages, because the pages link them by name**
        # *(2026-08-18)*. Which name that is depends on what `publish` decided — a new edition
        # if the data moved, the standing one if it did not — so writing the HTML first would
        # be guessing at it, and a download link is the one thing on the page that cannot be
        # approximately right.
        csv_names = publish_finance_csvs(iso, out_dir, cols)
        finance_section = FINANCE_BLOCK.format(
            name=name, iso=iso, pivot=pivot(fin), cutoff=FINANCE_CUTOFF,
            fin_n=len(fin), ncols=len(cols), **csv_names)
    else:
        cols, ys, amounts = [], [], []
        finance_section = FINANCE_EMPTY.format(name=name)

    (out_dir / "index.html").write_text(external_links(COUNTRY.format(
        tracked=tracked(iso)[0],
        sources=f"{n_place:,}", cat_total=f"{n_all:,}", cat_csv=cat_csv,
        catalogue_intro=copy_inline("country", "catalogue-intro",
                                    sources=f"{n_place:,}", name=name),
        budget_intro=copy_inline("country", "budget-intro"),
        reports=report_rows(report_editions(iso), iso),
        finance_section=finance_section,
        styles=styles(2, "home.css", "country.css"), ga=ga(),
        **common)), encoding="utf-8")

    written = [out_dir / "index.html", out_dir / cat_csv]

    if fin:
        (out_dir / "finance.html").write_text(external_links(FINANCE.format(
            fin_total=f"{sum(amounts):,.0f}",
            y0=(min(ys) if ys else "&mdash;"), y1=(max(ys) if ys else "&mdash;"),
            styles=styles(2, "home.css", "country.css", "datatable.css"),
            ga=ga(), **csv_names, **common)), encoding="utf-8")
        written.append(out_dir / "finance.html")
        written.append(out_dir / csv_names["csv_name"])

    return written


def check_metadata() -> None:
    """The field dictionary is Bill's file, not a build product, so the build cannot
    make one if it is missing — it can only refuse to link a 404. Every finance page
    points at it, so an absence here is 54 broken links, and worth stopping for."""
    p = SITE / "metadata" / METADATA_CSV
    if not p.exists():
        raise SystemExit(
            f"country.py: {p.relative_to(CORPUS)} is missing.\n"
            "  Every country's finance page links it as the field dictionary for the\n"
            "  non-state finance CSV. It is hand-maintained and not generated, so put\n"
            "  it back rather than expecting a rebuild to restore it.")


def main() -> int:
    check_metadata()
    ensure_catalogue_csv()
    isos = sys.argv[1:] or sorted(
        d.name for d in (OUTPUTS / "reports").iterdir()
        if d.is_dir() and d.name in FULL_NAMES
    )
    for iso in isos:
        paths = build(iso)
        print(f"{iso}  {len(paths)} files  ->  {paths[0].parent.relative_to(CORPUS)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
