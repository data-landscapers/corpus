#!/usr/bin/env python3
"""country.py — a country's finance table pages and CSVs (documentation/design.md §3).

    python scripts/country.py            builds every country
    python scripts/country.py KEN        builds one

**The country page itself is retired** *(Bill, 2026-10-17)*: `index.html` is a stub forwarding
to the country's news page (`retire_page`), and the history below is of the page it was. What
stays is `finance.html`, `budgets.html`, `all-finance.html` and the CSVs, which the finance
report links and readers cite.

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
catalogue, the report rows from the PDFs in `site/reports/{ISO3}/`, both
finance tables from `{ISO3}-nonstate.csv`, and both budget tables from
`budgets/budgets-{ISO3}.csv`.

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

**The budget section is the non-state section again** *(Bill, 2026-10-01)*: a topic-by-year
pivot on `index.html`, the full table on `budgets.html`, and the country's CSV beside them. It
reads `budgets/budgets-{ISO3}.csv`, Corpus's own source, as `finance.py` reads the all-countries
file. A place with no budget file keeps the *Public
budgeting and expenditure* heading and one sentence saying the work is under way *(Bill,
2026-08-25)*: a reader who finds nothing about budgets cannot tell an absent subject from an
absent finding, and the heading is what makes the difference visible.
"""

from __future__ import annotations

import csv
import io
import html
import json
import re
import shutil
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from copy_lib import copy_inline, copy_md  # noqa: E402
import structured_data  # noqa: E402
from datatable_bake import table_page  # noqa: E402  - a table's first rows, written into its page
from chrome_lib import chrome, feedback, foot, ga, info, script, styles  # noqa: E402
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

# Corpus's own budget extractions, one file per country, and their dictionary.
BUDGETS = CORPUS / "budgets"
BUDGETS_META = BUDGETS / "budgets-metadata.csv"
BUDGETS_METADATA_CSV = "budgets-metadata.csv"
BUDGET_TABLE_COLS = 9
# **No dated editions until the launch is announced** *(Bill, 2026-09-30)*. Until then each
# budget download is one undated file, rewritten whenever the data moves — a deliberate,
# time-boxed exception to design.md §9, for tables nobody has been told of yet. Set True at
# launch: `editions.publish` then cuts the first dated editions and retires the undated files
# itself (`editions.retire_undated`). One flag, for `finance.py`'s all-Africa file and every
# country's here.
BUDGETS_DATED = False
# `doc_locator` and `notes` are in the download and not in a table *(Bill, 2026-09-30)*,
# which is what the metadata page says of them.
BUDGET_TABLE_OMIT = ("doc_locator", "notes")
BUDGET_NUMERIC = ("report_year", "budget_usd", "proposed", "appropriated", "revised",
                  "released", "actual", "audited", "exec_vs_voted", "exec_vs_revised")

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
    #
    # **`page=` is how `publish` sees the previous edition once the tree has been pruned**
    # *(2026-09-09)*. `finance.html` is written after this returns, because it links the CSV
    # by name — so at this moment it is still last run's page, carrying last run's record,
    # which is exactly the comparison the deleted file used to provide. Without it every
    # render minted a fresh edition of all 61 CSVs, not one differing by a byte.
    src = (OUTPUTS / "non-state-finance" / f"{iso}-nonstate.csv").read_bytes()
    body = src.replace(b"\r\n", b"\n")
    data, _ = editions.publish(body, out_dir, f"{iso}-nonstate", ".csv",
                               page=out_dir / "finance.html")
    edition = editions.edition_of(data.stem) or ""
    # The table's Metadata button opens the dictionary as a table on the lookups page, which
    # offers the CSV itself; the noscript and colophon links still name the file (Bill, 2026-09-11).
    return {"csv_name": data.name, "fields_name": f"../../metadata/{METADATA_CSV}",
            "fields_page": "../../datasets/metadata/#non-state-finance",
            "csv_edition": edition, "csv_bytes": len(body),
            "artefacts": editions.artefact_meta(f"{iso}-nonstate", edition,
                                                editions.digest(body))}


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


def budgets(iso: str) -> tuple[list[str], list[dict]]:
    """The place's budget lines and their columns, or `([], [])` where no document has
    been read — a region, and the two states `budgets/` holds no file for."""
    f = BUDGETS / f"budgets-{iso}.csv"
    if not f.exists():
        return [], []
    with open(f, encoding="utf-8-sig", newline="") as fh:
        rdr = csv.DictReader(fh)
        return list(rdr.fieldnames or []), list(rdr)


def budget_counted(r: dict) -> bool:
    """A line the summary may add up: spent where it is printed, and stated as a total.
    Scope does not exclude a line: a `partial` or `unclear` one is in at half its value,
    which `budget_usd` already carries *(Bill's ruling, 2026-10-01)*."""
    return (r.get("is_transfer") != "true"
            and r.get("supplementary_basis") != "unclear" and bool(r.get("budget_usd")))


def publish_budget_csv(iso: str, out_dir: Path) -> dict[str, str]:
    """Publish the country's budget lines beside its page: `{ISO3}-budgets.csv`, undated until
    `BUDGETS_DATED`, a dated edition after. LF on the way out and `page=` for the comparison,
    both for the reasons `publish_finance_csvs` gives."""
    body = (BUDGETS / f"budgets-{iso}.csv").read_bytes().replace(b"\r\n", b"\n")
    stem = f"{iso}-budgets"
    if BUDGETS_DATED:
        path, _ = editions.publish(body, out_dir, stem, ".csv", page=out_dir / "budgets.html")
        edition = editions.edition_of(path.stem) or ""
        rows = (f'        <dt>Edition</dt><dd class="mono">{edition}</dd>\n'
                f'        <dt>This file</dt><dd><a href="{path.name}">{path.name}</a>'
                f' &mdash; a dated edition, kept as published and never revised</dd>')
        artefacts = editions.artefact_meta(stem, edition, editions.digest(body))
    else:
        path, edition, artefacts = out_dir / f"{stem}.csv", "", ""
        if not path.exists() or path.read_bytes() != body:
            path.write_bytes(body)
        rows = (f'        <dt>This file</dt><dd><a href="{path.name}">{path.name}</a>'
                f' &mdash; updated as the data changes</dd>')
    return {"csv_name": path.name, "csv_src": editions.versioned(path.name, body),
            "csv_edition": edition, "csv_bytes": len(body),
            "edition_rows": rows, "artefacts": artefacts}


# ── rendering ─────────────────────────────────────────────────────

def e(s: str) -> str:
    return html.escape(s or "")


def num(v: float) -> str:
    """Whole US$m, as the site states money everywhere else. A sum of floats is never
    exactly whole, so the old whole-or-one-decimal test printed `530.0` beside `605`;
    and a commitment under half a million prints `<1`, because `0` reads as none."""
    return "&lt;1" if 0 < v < 0.5 else f"{v:,.0f}"


def year(v: str) -> int | None:
    """Most `start_year`/`end_year` cells are a bare year; a few carry a
    parenthetical like `2015 (2015-07-06)`. The leading four digits are the
    year in every case observed, so read those rather than fail the page."""
    m = re.match(r"\s*(\d{4})", v or "")
    return int(m.group(1)) if m else None


def usd_m(r: dict) -> float:
    return float(r.get("commitment_usd_m") or 0)


def pivot(rows: list[dict], year_col: str = "start_year", amount=usd_m,
          cutoff: int | None = FINANCE_CUTOFF) -> str:
    """Topic by year, US$m: committed, or with `year_col` and `amount` set, budgeted.

    An empty cell is a year in which nothing was committed to that sector, and
    is left empty rather than zeroed: a zero reads as a measured quantity.
    Sectors are ordered by total, so the table opens with what the money went
    to rather than with an alphabet.

    Years before FINANCE_CUTOFF are aggregated into one leading '-2022'
    column: those early years each carry few commitments, so a column per
    year back to a country's first was mostly empty cells (Bill, 2026-08-11).
    `cutoff=None` gives every year its own column, which is what three budget years want.
    """
    first = cutoff if cutoff is not None else 0

    def col(y: int) -> str:
        return str(y) if y >= first else f"-{first}"

    yrs = {y for y in (year(r.get(year_col)) for r in rows) if y is not None}
    cols = ([f"-{first}"] if any(y < first for y in yrs) else []) \
        + [str(y) for y in sorted(y for y in yrs if y >= first)]
    cell: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for r in rows:
        y = year(r.get(year_col))
        if y is None:
            continue
        cell[r.get("primary_topic") or "(unstated)"][col(y)] += amount(r)
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

    # **"Topic", not "Sector"** *(Bill, 2026-08-25)*: a reader arriving from the Topics tab reads
    # these rows as topics, and "sector" collides with the economic sense the finance vocabulary
    # uses elsewhere. The CSV column followed on 2026-09-30 and is `primary_topic` (Bill: one word,
    # topic, across the site); editions before that date carry `sector`. The unit rides in the
    # corner cell, which every copy of the table carries (Bill, 2026-10-30).
    return f"""<div class="table-scroll"><table class="pivot">
        <thead><tr><th scope="col">Topic (USDm)</th>{head}<th class="num total">Total</th></tr></thead>
        <tbody>
{chr(10).join(body)}
        </tbody>
        <tfoot><tr><th scope="row">All topics</th>{foot}<td class="num total">{grand}</td></tr></tfoot>
      </table></div>"""


# `full_rows` retired 2026-08-19: the finance table is now drawn in the browser
# by assets/js/datatable.js from the published CSV, so the page no longer bakes
# a <tr> per commitment into its HTML. The rendering rules it carried — `url` as
# a link, the three numeric columns right-aligned, `description` allowed to wrap
# — moved to the `data-links`, `data-numeric` and clamp behaviour of the
# component, which applies them by column name rather than by position.


# ── chrome (site header/footer — matches scripts/home.py exactly) ────

def place_url(code: str) -> str:
    """Where a place's name leads now its page is retired: its news page *(Bill, 2026-10-17)*,
    or the catalogue cut to it for the two regions that issue no reports. `home.box_href`
    is the one statement of that rule."""
    from home import box_href
    return box_href(code)


def retire_page(out_dir: Path, code: str) -> None:
    """**The place page is retired; its address forwards to the place's news** *(Bill,
    2026-10-17)*. The page was an index to the reports, which the news page's report bar now
    carries. The table pages and CSVs beside it stay, because their addresses are cited; a stub
    rather than a deletion, because `/countries/{code}/` is linked from pages already out."""
    url = place_url(code)
    (out_dir / "index.html").write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Moved — Data Landscapers</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={url}">
<link rel="canonical" href="{url}">
</head>
<body>
<p>This page has moved <a href="{url}">here</a>.</p>
</body>
</html>
""", encoding="utf-8", newline="")


CHROME = chrome("countries", depth=2)
# The ⓘ by each finance table's title, from info.md → Finance (Bill, 2026-10-22). Braces
# doubled because the templates it is spliced into go through `str.format`.
ABOUT, PANEL = (s.replace("{", "{{").replace("}", "}}") for s in info("Finance"))

FOOT = foot(depth=2)


# The explanation is the ⓘ, from info.md → Finance (Bill, 2026-10-22): no prose round the pivot.
FINANCE_BLOCK = """{pivot}

    <div class="table-acts">
      <a class="btn" href="finance.html">Full table &mdash; {fin_n} commitments, all {ncols} fields &rarr;</a>
      <a class="btn btn--accent" href="{csv_name}" download>&darr; Download CSV</a>
    </div>"""

FINANCE_EMPTY = """    <p>No non-state finance commitments are currently held for {name}.</p>"""

# The budget section, in the shape of the finance one above it. `{summary}` is the pivot, or
# one sentence where no line read so far can be added up.
BUDGET_BLOCK = """{summary}

    <div class="table-acts">
      <a class="btn" href="budgets.html">Full table &mdash; {bud_n} budget lines, all {ncols} fields &rarr;</a>
      <a class="btn btn--accent" href="{csv_name}" download>&darr; Download CSV</a>
    </div>"""

BUDGET_SUMMARY = """{pivot}"""

# A place with no budget file: the sentence saying the work is under way.
BUDGET_EMPTY = """    <p>{intro}</p>"""


def budget_section(name: str, header: list[str], rows: list[dict], csv_name: str) -> str:
    """The country page's budget block: the intro, the topic-by-year pivot of the lines
    `budget_counted` passes, and the way in to the full table and the CSV."""
    counted = [r for r in rows if budget_counted(r)]
    if counted:
        summary = BUDGET_SUMMARY.format(
            pivot=pivot(counted, "report_year",
                        lambda r: float(r["budget_usd"]) / 1e6, cutoff=None))
    else:
        summary = f'    <p class="table-note">{copy_inline("datasets", "budget-none-counted")}</p>'
    return BUDGET_BLOCK.format(
        summary=summary,
        bud_n=f"{len(rows):,}", ncols=len(header), csv_name=csv_name)


# The non-state finance table, for a country page and a region page alike.
#
# **One template, not two** *(2026-09-09)*. `region.py` carried a copy of this that differed in
# three lines of wording, and a copy is a place for the two to disagree — which they already
# had: the crumb here still said "Countries" after `/countries/` was renamed *Countries &
# Regions* on 2026-09-02, and the copy had been corrected. It cost a defect the same day this
# was merged, too: the `dl-artefact` record was added here and the region pages went on
# minting an edition every render until the copy was found.
#
# `{unit}` is the whole of the difference — "country" on a country page, "place" on a region's,
# where the rows are the countries beneath it. `region.py` imports this rather than holding
# its own, the way it already imports `FINANCE_BLOCK`, `pivot` and `report_rows`.
# The row panel carries every field, shown columns included (Bill, 2026-09-27): the panel is
# where a reader reads one deal whole, and a field missing there because it is also a column
# is missing. `finance.py` imports this for the all-Africa table.
FINANCE_DETAIL = ("recipient, start_year, end_year, published_date, financier, african, primary_topic, "
                  "instrument, aid, commitment_usd_m, amount_basis, amount_quality, scope, scope_basis, "
                  "status, title, "
                  "description, beneficiary_type, recipient_organisation, original_amount, "
                  "project_id, iati_activity_id, url, financier_slug, deal_id, record")

# **The aid filter reads in words** *(Bill, 2026-09-30)*: the column holds `true`/`false`,
# which is what a tool reading the CSV wants, and the table shows them as Aid and Not aid.
# The unfiltered option says "Aid and non-aid", where the default "All aid" read as a choice.
# `finance.py` imports both for the all-Africa table.
AID_LABELS = {"aid": {"true": "Aid", "false": "Not aid"}}
FILTER_ALL = {"aid": "Aid and non-aid", "african": "African and non-African"}


def attr_json(obj) -> str:
    """A JSON object as an HTML attribute value."""
    return html.escape(json.dumps(obj, ensure_ascii=False), quote=True)


FINANCE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — non-state finance — Data Landscapers</title>
<meta name="description" content="Every non-state commitment to {name}'s digital sector held in the Data Landscapers base, all fields, searchable and downloadable.">
<link rel="canonical" href="{base}/countries/{iso}/finance.html">
{artefacts}
{styles}
<link rel="icon" href="{favicon}" type="image/svg+xml">
{jsonld}
{ga}
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container container--wide">

    <header class="article-header">
      <div class="article-header__crumb"><a href="{base}/countries/">Countries &amp; Regions</a> &nbsp;/&nbsp; <a href="{parent}">{name}</a></div>
      {feedback}
      <h1 class="article-header__title">Non-state finance""" + ABOUT + """</h1>
      <div class="article-header__byline">{name} &nbsp;·&nbsp; {fin_n} commitments &nbsp;·&nbsp; US${fin_total}m &nbsp;·&nbsp; {y0}&ndash;{y1}</div>
    </header>
""" + PANEL + """

    <div class="dl-datatable"
      data-src="{csv_name}"
      data-cols="start_year, published_date, financier, primary_topic, instrument, commitment_usd_m, status, title, description, recipient_organisation, url"
      data-filters="financier, african, primary_topic, instrument, aid, scope, status, beneficiary_type"
      data-numeric="start_year, end_year, commitment_usd_m"
      data-links="url"
      data-detail=\"""" + FINANCE_DETAIL + """\"
      data-labels=\"""" + attr_json(AID_LABELS).replace("{", "{{").replace("}", "}}") + """\"
      data-filter-all=\"""" + attr_json(FILTER_ALL).replace("{", "{{").replace("}", "}}") + """\"
      data-sort="start_year:desc"
      data-empty="No commitment matches those filters.">
      <div class="dt-controls">
        <span class="dt-title">{name} &mdash; non-state finance</span>
        <span class="dt-count">{fin_n} rows</span>
        <a class="btn btn--sm" href="{csv_name}" download>&darr; CSV</a>
        <a class="btn btn--sm" href="{fields_page}">Metadata</a>
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
        <dt>Fields</dt><dd><a href="{fields_name}">non-state-finance-metadata.csv</a> &mdash; what each column means. One dictionary for every {unit}&rsquo;s table, not a copy per {unit}</dd>
        <dt>Licence</dt><dd><a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></dd>
      </dl>
    </div>

  </div>
  </main>

{foot}

</div>

{datatable}
</body>
</html>
"""


# The country's budget lines as a table: `finance.py`'s `BUDGETS_PAGE` for one country, as
# `FINANCE` above is its `PAGE` for one place. The table reads the download itself — one
# country's file is small enough that the lighter table file the all-Africa page needs is
# not — and leaves `BUDGET_TABLE_OMIT` out of the row panel.
BUDGETS_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — national budget — Data Landscapers</title>
<meta name="description" content="Every digital line read from {name}'s own budget documents, all fields, searchable and downloadable.">
<link rel="canonical" href="{base}/countries/{iso}/budgets.html">
{artefacts}
{styles}
<link rel="icon" href="{favicon}" type="image/svg+xml">
{jsonld}
{ga}
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container container--wide">

    <header class="article-header">
      <div class="article-header__crumb"><a href="{base}/countries/">Countries &amp; Regions</a> &nbsp;/&nbsp; <a href="{parent}">{name}</a></div>
      {feedback}
      <h1 class="article-header__title">National budget""" + ABOUT + """</h1>
      <div class="article-header__byline">{name} &nbsp;·&nbsp; {bud_n} budget lines &nbsp;·&nbsp; fiscal years {yr}</div>
    </header>
""" + PANEL + """

    <div class="dl-datatable"
      data-src="{csv_src}"
      data-cols="{cols}"
      data-filters="report_year, primary_topic, scope_confidence"
      data-numeric="{numeric}"
      data-thousands="budget_usd"
      data-labels="{labels}"
      data-tips="{tips}"
      data-detail="{detail}"
      data-sort="report_year:desc"
      data-empty="No budget line matches those filters.">
      <div class="dt-controls">
        <span class="dt-title">{name} &mdash; national budget</span>
        <span class="dt-count">{bud_n} rows</span>
        <a class="btn btn--sm" href="{csv_name}" download>&darr; CSV</a>
        <a class="btn btn--sm" href="../../datasets/metadata/#national-budgets">Metadata</a>
      </div>
      <noscript>
        <p>The table is drawn in the browser from <a href="{csv_name}">{csv_name}</a>. With JavaScript off, download that file. It holds the same data, every row and every field.</p>
      </noscript>
    </div>

    <div class="colophon">
      <strong>About this table</strong>
      <dl>
        <dt>Built</dt><dd class="mono">{built}</dd>
{edition_rows}
        <dt>Fields</dt><dd><a href="../../datasets/metadata/#national-budgets">What each column means</a> and its allowed values &mdash; also as <a href="../../metadata/{metadata}">{metadata}</a></dd>
        <dt>All countries</dt><dd><a href="../../finance/budgets/">National budgets</a></dd>
        <dt>Licence</dt><dd><a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></dd>
      </dl>
    </div>

  </div>
  </main>

{foot}

</div>

{datatable}
</body>
</html>
"""


def budget_dictionary() -> list[dict]:
    """`budgets/budgets-metadata.csv`: the column tooltips and `variableMeasured`."""
    with open(BUDGETS_META, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def budgets_dataset(code: str, name: str, rows: list[dict], meta: list[dict],
                    pub: dict[str, str]) -> str:
    """The country's budget lines described as data: `finance_dataset` for the other table,
    and a slice of the all-Africa one at `/finance/budgets/`. Undated, it dates itself to
    the build; as an edition, to the edition."""
    years = [year(r.get("report_year")) for r in rows]
    return structured_data.dataset(
        name=f"Data Landscapers national budgets — {name}",
        description=copy_md("datasets", "dataset-budgets-place", name=name),
        url=f"{SITE_BASE}/countries/{code}/budgets.html",
        csv_url=f"{SITE_BASE}/countries/{code}/{pub['csv_name']}",
        csv_bytes=pub["csv_bytes"],
        records=len(rows),
        fields=structured_data.fields_from([{"Column": m["column"], "Definition": m["definition"]}
                                            for m in meta]),
        entity=structured_data.place(code, name),
        temporal=structured_data.year_span([y for y in years if y is not None]),
        modified=pub["csv_edition"] or None,
        version=pub["csv_edition"] or None,
        part_of=f"{SITE_BASE}/finance/budgets/",
        extra_keywords=("Government budgets", "Public finance", "Digital transformation"))


# ── all finance: both sides in one table (Bill, 2026-10-16) ─────────
#
# The rows the finance report's *All finance* pivot adds up, one per budget line or commitment,
# in the columns the two have in common. Every value is copied from the budgets or non-state
# table, never re-derived: `usd_m` is the figure the pivot counts (a budget line's `budget_usd`,
# already halved where partly digital, in millions; a commitment's `commitment_usd_m`), and
# `deal_id` finds the row in its own table, where every other field is.
ALL_FIELDS = (
    ("side", "Public budget, or non-state finance"),
    ("year", "A budget line: the year its fiscal year starts in. A commitment: the year it was made"),
    ("primary_topic", "The topic the money is for"),
    ("usd_m", "US$m as the All finance table counts it. A budget line at its latest stage; a "
              "commitment at its counted amount. Partly digital or unclear: 50%"),
    ("payer", "The state, or the financier"),
    ("recipient", "The spending entity, or the recipient organisation"),
    ("title", "The budget line's name, or the commitment's title"),
    ("description", "The line's purpose, or the commitment's description"),
    ("stage", "A budget line: the latest stage held. A commitment: its status"),
    ("scope", "How much of it is digital: whole or full, partial, or unclear"),
    ("url", "A commitment's source, the publisher's own link. A budget line's document is in "
            "the budgets table"),
    ("deal_id", "The row's identifier in the budgets or non-state finance table"),
)


def all_finance_rows(name: str, fin: list[dict], bud: list[dict]) -> list[dict]:
    rows = [{
        "side": "Public budget", "year": r.get("report_year", ""),
        "primary_topic": r.get("primary_topic", ""),
        "usd_m": f"{float(r['budget_usd']) / 1e6:.3f}",
        "payer": f"{name} (state budget)", "recipient": r.get("spending_entity", ""),
        "title": r.get("line_name", ""), "description": r.get("purpose", ""),
        "stage": r.get("current_stage", ""), "scope": r.get("scope_confidence", ""),
        "url": "", "deal_id": r.get("deal_id", ""),
    } for r in bud if budget_counted(r)]
    rows += [{
        "side": "Non-state finance", "year": r.get("start_year", ""),
        "primary_topic": r.get("primary_topic", ""), "usd_m": r.get("commitment_usd_m", ""),
        "payer": r.get("financier", ""), "recipient": r.get("recipient_organisation", ""),
        "title": r.get("title", ""), "description": r.get("description", ""),
        "stage": r.get("status", ""), "scope": r.get("scope", ""),
        "url": r.get("url", ""), "deal_id": r.get("deal_id", ""),
    } for r in fin]
    return sorted(rows, key=lambda r: (r["year"], r["side"], r["primary_topic"]), reverse=True)


def publish_all_finance_csv(iso: str, out_dir: Path, rows: list[dict]) -> dict[str, str]:
    """`{ISO3}-all-finance.csv`, on the budgets CSV's terms: it carries budget lines, so it is
    undated until `BUDGETS_DATED` and an edition after, LF on the way out either way."""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=[f for f, _ in ALL_FIELDS], lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    body = buf.getvalue().encode("utf-8")
    stem = f"{iso}-all-finance"
    if BUDGETS_DATED:
        path, _ = editions.publish(body, out_dir, stem, ".csv", page=out_dir / "all-finance.html")
        edition = editions.edition_of(path.stem) or ""
        artefacts = editions.artefact_meta(stem, edition, editions.digest(body))
    else:
        path, edition, artefacts = out_dir / f"{stem}.csv", "", ""
        if not path.exists() or path.read_bytes() != body:
            path.write_bytes(body)
    return {"csv_name": path.name, "csv_edition": edition, "csv_bytes": len(body),
            "artefacts": artefacts}


def all_finance_dataset(code: str, name: str, rows: list[dict], pub: dict[str, str]) -> str:
    return structured_data.dataset(
        name=f"Data Landscapers digital finance, budgets and non-state — {name}",
        description=copy_md("datasets", "all-finance-dataset", name=name),
        url=f"{SITE_BASE}/countries/{code}/all-finance.html",
        csv_url=f"{SITE_BASE}/countries/{code}/{pub['csv_name']}",
        csv_bytes=pub["csv_bytes"],
        records=len(rows),
        fields=structured_data.fields_from([{"Column": f, "Definition": d}
                                            for f, d in ALL_FIELDS]),
        entity=structured_data.place(code, name),
        temporal=structured_data.year_span([y for y in (year(r["year"]) for r in rows)
                                            if y is not None]),
        modified=pub["csv_edition"] or None,
        version=pub["csv_edition"] or None,
        part_of=f"{SITE_BASE}/finance/",
        extra_keywords=("Government budgets", "Development finance", "Digital transformation"))


ALL_FINANCE_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — all finance — Data Landscapers</title>
<meta name="description" content="Every digital budget line and non-state commitment counted for {name}, in one table, searchable and downloadable.">
<link rel="canonical" href="{base}/countries/{iso}/all-finance.html">
{artefacts}
{styles}
<link rel="icon" href="{favicon}" type="image/svg+xml">
{jsonld}
{ga}
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container container--wide">

    <header class="article-header">
      <div class="article-header__crumb"><a href="{base}/countries/">Countries &amp; Regions</a> &nbsp;/&nbsp; <a href="{parent}">{name}</a></div>
      {feedback}
      <h1 class="article-header__title">All finance""" + ABOUT + """</h1>
      <div class="article-header__byline">{name} &nbsp;·&nbsp; {n} rows &nbsp;·&nbsp; US${total}m</div>
    </header>
""" + PANEL + """

    <div class="dl-datatable"
      data-src="{csv_name}"
      data-cols="year, side, primary_topic, usd_m, payer, recipient, title, stage, scope, url"
      data-filters="side, primary_topic, stage, scope"
      data-numeric="year, usd_m"
      data-links="url"
      data-detail="{detail}"
      data-tips="{tips}"
      data-filter-all="{filter_all}"
      data-sort="year:desc"
      data-empty="No row matches those filters.">
      <div class="dt-controls">
        <span class="dt-title">{name} &mdash; all finance</span>
        <span class="dt-count">{n} rows</span>
        <a class="btn btn--sm" href="{csv_name}" download>&darr; CSV</a>
      </div>
      <noscript>
        <p>The table is drawn in the browser from <a href="{csv_name}">{csv_name}</a>. With JavaScript off, download that file &mdash; it is the same data, every row and every field.</p>
      </noscript>
    </div>

    <div class="colophon">
      <strong>About this table</strong>
      <dl>
        <dt>Built</dt><dd class="mono">{built}</dd>
        <dt>This file</dt><dd><a href="{csv_name}">{csv_name}</a></dd>
        <dt>Source</dt><dd><a href="budgets.html">Budgets</a> and <a href="finance.html">non-state finance</a> for {name}: each row is copied from one of them, and its <code>deal_id</code> finds it there</dd>
        <dt>Licence</dt><dd><a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></dd>
      </dl>
    </div>

  </div>
  </main>

{foot}

</div>

{datatable}
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


def finance_dataset(code: str, name: str, out_dir: Path, fin: list[dict],
                    csv_name: str, edition: str, size: int | None = None) -> str:
    """The place's non-state finance table, described as data *(Bill, 2026-09-20)*.

    **This one is an edition and the catalogue cut beside it is not**, which is the only real
    difference between the two blocks these pages now carry. The page offers one dated file,
    cut on one day and never revised (design.md §9): `version` is that edition and
    `dateModified` is its date, not the build's. Dating it to the build would assert a change
    on every render of a table nobody has touched since August, to the one audience that reads
    `dateModified` literally — and the colophon two screens below would be saying the opposite.

    **`contentSize` is measured this run, never carried over.** `--prune-local` takes the file
    out of the tree once R2 has it, so the size comes from the bytes this run published
    (`size`), which `editions.publish` only keeps as the standing edition when they are that
    edition byte for byte; a size remembered from an earlier build would be a claim rather
    than a measurement.

    `temporalCoverage` is the years the money covers, not the years the rows were written — the
    table carries no finer date than the year, and it is the question anyone searching for
    finance data is asking."""
    years = [year(r.get("start_year")) for r in fin] + [year(r.get("end_year")) for r in fin]
    return structured_data.dataset(
        name=f"Data Landscapers non-state finance — {name}",
        description=copy_md("datasets", "dataset-place", name=name),
        url=f"{SITE_BASE}/countries/{code}/finance.html",
        csv_url=f"{SITE_BASE}/countries/{code}/{csv_name}",
        csv_bytes=structured_data.bytes_of(out_dir / csv_name) or size,
        records=len(fin),
        fields=finance_field_dictionary(),
        entity=structured_data.place(code, name),
        temporal=structured_data.year_span([y for y in years if y is not None]),
        modified=edition or None,
        version=edition or None,
        part_of=f"{SITE_BASE}/finance/",
        extra_keywords=("Development finance", "Non-state finance", "Digital infrastructure"))


def finance_field_dictionary() -> list[dict]:
    """`variableMeasured` for a finance table, from the one hand-maintained dictionary every
    finance page links — the arrangement `publish_finance_csvs` chose deliberately over
    fifty-four copies of one schema."""
    fd = SITE / "metadata" / METADATA_CSV
    if not fd.exists():
        return []
    with open(fd, encoding="utf-8-sig", newline="") as fh:
        return structured_data.fields_from(list(csv.DictReader(fh)))


def build(iso: str) -> list[Path]:
    name = FULL_NAMES.get(iso, iso)
    fin = finance(iso)
    _, _, cat_cols, cat_rows = catalogue(iso)
    built = date.today().isoformat()

    out_dir = OUT / iso
    out_dir.mkdir(parents=True, exist_ok=True)
    cat_csv = publish_catalogue_cut(iso, out_dir, cat_cols, cat_rows)

    common = dict(
        base=SITE_BASE, main_site=MAIN_SITE, iso=iso, name=name,
        favicon=f"{MAIN_SITE}/assets/favicon.svg",
        chrome=CHROME, foot=FOOT,
        built=built, fin_n=len(fin),
        # The crumb's place link: the country page it named is retired (`retire_page`).
        parent=f"{SITE_BASE}/reports/{iso}/{iso}-finance.html",
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
    else:
        cols, ys, amounts = [], [], []

    bud_cols, bud = budgets(iso)
    if bud:
        bud_pub = publish_budget_csv(iso, out_dir)     # before the pages, which link it by name

    retire_page(out_dir, iso)

    written = [out_dir / "index.html", out_dir / cat_csv]

    if fin:
        (out_dir / "finance.html").write_text(table_page(out_dir, FINANCE.format(
            feedback=feedback(f"{name} — non-state finance",
                              f"{SITE_BASE}/countries/{iso}/finance.html"),
            unit="country",
            jsonld=finance_dataset(iso, name, out_dir, fin, csv_names["csv_name"],
                                   csv_names["csv_edition"], csv_names["csv_bytes"]),
            fin_total=f"{sum(amounts):,.0f}",
            y0=(min(ys) if ys else "&mdash;"), y1=(max(ys) if ys else "&mdash;"),
            styles=styles(2, "country.css", "datatable.css"),
            datatable=script("datatable.js", 2),
            ga=ga(), **csv_names, **common)), encoding="utf-8")
        written.append(out_dir / "finance.html")
        written.append(out_dir / csv_names["csv_name"])

    if not fin and (out_dir / "finance.html").exists():
        # The place's last deal left the dataset: `site/` is never purged, so the table
        # page would go on being served with nothing behind it.
        (out_dir / "finance.html").unlink()

    if bud:
        meta = budget_dictionary()
        shown = [c for c in bud_cols if c not in BUDGET_TABLE_OMIT]
        bud_ys = sorted({y for y in (year(r.get("report_year")) for r in bud) if y is not None})
        (out_dir / "budgets.html").write_text(table_page(out_dir, BUDGETS_PAGE.format(
            feedback=feedback(f"{name} — national budget",
                              f"{SITE_BASE}/countries/{iso}/budgets.html"),
            jsonld=budgets_dataset(iso, name, bud, meta, bud_pub),
            # The file's own order puts the reader's columns first (`budget_source.COLUMNS`);
            # `country` is the one this page has no use for as a column.
            cols=", ".join([c for c in shown if c != "country"][:BUDGET_TABLE_COLS]),
            detail=", ".join(shown),
            numeric=", ".join(c for c in bud_cols if c in BUDGET_NUMERIC),
            labels=attr_json({"country": {iso: name}}),
            tips=attr_json({m["column"]: m["definition"] for m in meta if m.get("definition")}),
            bud_n=f"{len(bud):,}",
            yr=(f"{bud_ys[0]}&ndash;{bud_ys[-1]}" if bud_ys else "&mdash;"),
            metadata=BUDGETS_METADATA_CSV,
            styles=styles(2, "country.css", "datatable.css"),
            datatable=script("datatable.js", 2),
            ga=ga(), **bud_pub, **common)), encoding="utf-8")
        written.append(out_dir / "budgets.html")
        written.append(out_dir / bud_pub["csv_name"])

    every = all_finance_rows(name, fin, bud)
    if every:
        all_pub = publish_all_finance_csv(iso, out_dir, every)
        (out_dir / "all-finance.html").write_text(table_page(out_dir, ALL_FINANCE_PAGE.format(
            feedback=feedback(f"{name} — all finance",
                              f"{SITE_BASE}/countries/{iso}/all-finance.html"),
            jsonld=all_finance_dataset(iso, name, every, all_pub),
            n=f"{len(every):,}",
            total=f"{sum(float(r['usd_m'] or 0) for r in every):,.0f}",
            detail=", ".join(f for f, _ in ALL_FIELDS),
            tips=attr_json(dict(ALL_FIELDS)),
            filter_all=attr_json({"side": "Both sides", "primary_topic": "All topics",
                                  "stage": "All stages", "scope": "All scopes"}),
            styles=styles(2, "country.css", "datatable.css"),
            datatable=script("datatable.js", 2),
            ga=ga(), **all_pub, **common)), encoding="utf-8")
        written += [out_dir / "all-finance.html", out_dir / all_pub["csv_name"]]
    elif (out_dir / "all-finance.html").exists():
        (out_dir / "all-finance.html").unlink()   # `site/` is never purged; see finance.html

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
