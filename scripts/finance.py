#!/usr/bin/env python3
"""finance.py — the Finance page.

    python scripts/finance.py
      -> site/finance/index.html                   non-state finance
      -> site/finance/budgets/index.html           national budgets, with their table
      -> site/finance/all-nonstate-{edition}.csv   the full download, a dated edition (§9)
      -> site/finance/budgets/budgets-all-countries-{edition}.csv   likewise, for budgets
      -> site/finance/all/index.html               the two joined: all finance, with its table

**Two pages under one toc bar, the Progress arrangement** *(Bill, 2026-09-22)*.
`/finance/` carries non-state finance and nothing else; `/finance/budgets/` carries the
budget work. Its table came off the site on 2026-09-22 and returned on 2026-09-30 (Bill)
as `budgets/budgets-all-countries.csv`, every line Corpus has read from a state's own budget
document, published as a dated `budgets-all-countries` edition. The `all-budgets` editions
published before 2026-09-22 stay where they are (§9). Finance also left the nav bar on
2026-09-22: the home page and the Datasets page are the ways in.

**The budget table shows the first nine columns and the row panel shows all of them**
*(Bill, 2026-09-30)*. The file's column order is the schema's (`budget_source.COLUMNS`),
which puts the reader's columns first, so "the first nine" is read off the file's own header
rather than listed here. The field dictionary is `budgets/budgets-metadata.csv`, which
`datasets.py` publishes beside the others.

The table is the cross-country counterpart of each country's `finance.html` and uses
the same component: `site/assets/js/datatable.js` fetches the published CSV and draws
it in the browser. That is not a preference but the only option — 1,257 rows by 20
columns baked into HTML is a multi-megabyte page, where the CSV it reads instead is
1.1 MB and is a file the reader can keep. `recipient` is carried as an ISO-3
code in the data and shown as a country name in the table, through the `data-labels`
map built from `outputs/vocab/countries.csv`.

**All finance is the two tables in one** *(Bill, 2026-10-01)*: `/finance/all/`, every
non-state commitment from 2024 and every budget line in the twelve columns of `ALL_COLUMNS`, joined
here at render from the two files the other pages publish. `documentation/joined-up-finance-spec.csv`
is Bill's mapping; `lookups/all-finance-metadata.csv` is the dictionary. It follows
`BUDGETS_DATED`, because half of it is the budget table.

**The prose is in `content/finance.md`**, not here (RENDER.md -> *The prose*).

Reads `outputs/non-state-finance/all-nonstate.csv` (the deduped cross-country
partition — one row per deal). Vocabularies come from `outputs/vocab/` like the
catalogue, so the site still reads only `outputs/`.

The domestic-budget side is still compiled per country into `outputs/budgets/{ISO3}-budget.csv`;
nothing here reads it. The budgets page reads `budgets/budgets-all-countries.csv` directly: it
is Corpus's own source, not a compile of OSINT's, so there is no `outputs/` copy to read.
"""
from __future__ import annotations
import csv, html, io, json, sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import editions  # noqa: E402  - one implementation of the edition grammar (§9)
from copy_lib import copy, copy_md  # noqa: E402
import structured_data  # noqa: E402
from chrome_lib import chrome, external_links, feedback, foot, ga, script, styles  # noqa: E402
from country import AID_LABELS, FILTER_ALL, FINANCE_DETAIL, attr_json  # noqa: E402  - the row panel's fields, one list for every finance table
# `BUDGETS_DATED` is the launch switch, set in `country.py`: one flag for this page's file
# and every country's. `BUDGET_TABLE_OMIT` keeps `doc_locator` and `notes` out of the table,
# here by writing a lighter file for it to read.
from country import (BUDGETS_DATED, BUDGET_NUMERIC, BUDGET_TABLE_COLS,  # noqa: E402
                     BUDGET_TABLE_OMIT)

CORPUS = Path(__file__).resolve().parent.parent
OUTPUTS = CORPUS / "outputs"
SITE = CORPUS / "site"
VOCAB = CORPUS / "outputs" / "vocab"
SITE_BASE = "https://corpus.data-landscapers.io"
MAIN_SITE = "https://data-landscapers.io"

# The one field dictionary for every non-state finance table (country.py writes the
# same link). Hand-maintained; nothing generates it.
METADATA_CSV = "non-state-finance-metadata.csv"

# The budgets table: Corpus's own extractions, every country in one file, and its dictionary.
BUDGETS_CSV = CORPUS / "budgets" / "budgets-all-countries.csv"
BUDGETS_META = CORPUS / "budgets" / "budgets-metadata.csv"
BUDGETS_METADATA_CSV = "budgets-metadata.csv"
# **The table reads a lighter file than the download** *(Bill, 2026-09-30)*. `doc_locator` and
# `notes` are long prose and nearly half the bytes, and the browser parses every byte of
# `data-src` before it draws a row, so the table was sluggish. They stay in the download and
# the metadata says so; the table's file is undated working material, like the data centres'
# display file, and is rewritten whenever the download is.
BUDGET_TABLE_CSV = "budgets-all-countries-table.csv"

# All finance: the joined table's columns, in the spec's order, and its dictionary.
ALL_COLUMNS = ("country", "year", "primary_topic", "type", "financier", "recipient", "title",
               "description", "value_usd", "deal_id", "scope", "scope_basis")
ALL_META = CORPUS / "lookups" / "all-finance-metadata.csv"
# **Both sides from 2024** *(Bill, 2026-10-01)*: the budget lines start there, and a joined
# table that set eleven years of commitments beside three of budgets would compare nothing.
# Earlier non-state commitments stay in the non-state table.
ALL_FIRST_YEAR = 2024
ALL_METADATA_CSV = "all-finance-metadata.csv"
ALL_TABLE_COLS = ("country", "year", "primary_topic", "type", "value_usd", "financier",
                  "recipient", "title", "description")


def indent(html_block: str, spaces: int = 4) -> str:
    """A content block sits inside a page whose HTML is indented; matching it keeps
    the generated source readable, which matters when the thing you are checking is
    whether a paragraph came out where you meant it to."""
    pad = " " * spaces
    return "\n".join(pad + ln if ln.strip() else ln for ln in html_block.splitlines())

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def source_dir() -> Path:
    for base in (OUTPUTS,):
        if (base / "non-state-finance" / "all-nonstate.csv").exists():
            return base / "non-state-finance"
    raise SystemExit("no all-nonstate.csv in outputs/ — run scripts/rebuild.py --finance")


def place_names() -> dict:
    names = {}
    with open(VOCAB / "countries.csv", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            names[r["iso-3"]] = r["country-name"]
    return names


def load_finance(sdir: Path) -> dict:
    """Aggregate all-nonstate.csv. Real; the page that presents it is the TODO."""
    total_usd_m = 0.0
    deals = 0
    by_financier: Counter = Counter()          # commitment US$m by financier
    by_place: Counter = Counter()              # deal count by recipient
    by_sector: Counter = Counter()             # deal count by sector
    years = []
    with open(sdir / "all-nonstate.csv", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            deals += 1
            try:
                amt = float(r.get("commitment_usd_m") or 0)
            except ValueError:
                amt = 0.0
            total_usd_m += amt
            if r.get("financier"):
                by_financier[r["financier"]] += amt
            if r.get("recipient"):
                by_place[r["recipient"]] += 1
            if r.get("primary_topic"):
                by_sector[r["primary_topic"]] += 1
            for y in (r.get("start_year"), r.get("end_year")):
                if y and y.isdigit():
                    years.append(int(y))
    return {
        "deals": deals,
        "total_usd_m": total_usd_m,
        "financiers": len(by_financier),
        # X-codes are regions (XAF, XSS, XGL…), not countries: the byline counts them apart.
        "places": sum(1 for p in by_place if not p.startswith("X")),
        "regions": sum(1 for p in by_place if p.startswith("X")),
        "year_min": min(years) if years else None,
        "year_max": max(years) if years else None,
        "top_financiers": by_financier.most_common(15),
        "by_place": by_place,
        "by_sector": by_sector.most_common(),
    }


# --- site chrome. Kept in step with scripts/catalogue.py. Finance has not been in the
# nav bar since 2026-09-22, so `active` lights nothing; it is passed for the day it returns.
CHROME = chrome('finance', depth=1)

FOOT = foot(depth=1)


def toc(current: str) -> str:
    """NON-STATE FINANCE · BUDGETS · ALL FINANCE, the bar `progress.py` → `toc` puts over
    its views. Every item is a link, the current one pointing at itself with
    `aria-current`, for the reason given there: `.article-toc a` styles the whole bar."""
    up = "" if current == "non-state" else "../"      # `/finance/` is the non-state page
    items = [(key, label, "./" if key == current else (up + path or "./"))
             for key, label, path in (("non-state", "Non-state finance", ""),
                                      ("budgets", "Budgets", "budgets/"),
                                      ("all", "All finance", "all/"))]
    sep = '\n<span class="article-toc__sep" aria-hidden="true">&middot;</span>\n'
    here = ' aria-current="page"'
    body = sep.join(
        f'<a href="{href}"{here if key == current else ""}>{label}</a>'
        for key, label, href in items)
    return indent(f'<nav class="article-toc" aria-label="Finance views">\n{body}\n</nav>')


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Finance — Data Landscapers</title>
<meta name="description" content="Money committed to Africa's digital sector: every non-state commitment held in the Data Landscapers base, searchable and downloadable.">
<link rel="canonical" href="{base}/finance/">
{artefacts}
{styles}
<link rel="icon" href="{main}/assets/favicon.svg" type="image/svg+xml">
{jsonld}
{ga}
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container container--wide">

    <header class="article-header">
      {feedback}
      <h1 class="article-header__title">Finance</h1>
    </header>

{toc}

    <div class="byline">{deals} commitments &nbsp;·&nbsp; US${total}m &nbsp;·&nbsp; {financiers} financiers &nbsp;·&nbsp; {places} countries &nbsp;·&nbsp; {regions} regions &nbsp;·&nbsp; {yr}</div>

{non_state_intro}

{table_note}

    <div class="dl-datatable"
      data-src="{csv_name}"
      data-cols="recipient, start_year, published_date, financier, primary_topic, instrument, commitment_usd_m, status, title, description, recipient_organisation, url"
      data-filters="recipient, african, primary_topic, instrument, aid, scope, status, beneficiary_type"
      data-numeric="start_year, end_year, commitment_usd_m"
      data-links="url"
      data-labels="{labels}"
      data-filter-all="{filter_all}"
      data-detail="{detail}"
      data-sort="start_year:desc"
      data-empty="No commitment matches those filters.">
      <div class="dt-controls">
        <span class="dt-title">Africa &mdash; non-state finance</span>
        <span class="dt-count">{deals} rows</span>
        <a class="btn btn--sm" href="{csv_name}" download>&darr; CSV</a>
        <a class="btn btn--sm" href="../datasets/metadata/#non-state-finance">Metadata</a>
      </div>
      <noscript>
        <p>The table is drawn in the browser from <a href="{csv_name}">{csv_name}</a>. With JavaScript off, download that file &mdash; it is the same data, every row and every field. At {deals} rows it is the one table on this site that could not sensibly be written into the page itself.</p>
      </noscript>
    </div>

    <div class="colophon">
      <strong>About this table</strong>
      <dl>
        <dt>Built</dt><dd class="mono">{built}</dd>
        <dt>Edition</dt><dd class="mono">{edition}</dd>
        <dt>This file</dt><dd><a href="{csv_name}">{csv_name}</a> &mdash; a dated edition, retained as published and never revised</dd>
        <dt>Source</dt><dd><code>outputs/non-state-finance/all-nonstate.csv</code>, compiled by the finance pass</dd>
        <dt>Fields</dt><dd><a href="../metadata/{metadata}">{metadata}</a> &mdash; what each column means. The same dictionary every country&rsquo;s finance table uses</dd>
        <dt>Recipient</dt><dd><code>recipient</code> is an ISO-3 code in the file and a country or region name in the table; the two are the same thing</dd>
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


BUDGETS_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>National budgets — Data Landscapers</title>
<meta name="description" content="What African states budget for digital transformation from their own money: every digital line read from their budget documents, searchable and downloadable.">
<link rel="canonical" href="{base}/finance/budgets/">
{artefacts}
{styles}
<link rel="icon" href="{main}/assets/favicon.svg" type="image/svg+xml">
{jsonld}
{ga}
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container container--wide">

    <header class="article-header">
      {feedback}
      <h1 class="article-header__title">Finance</h1>
    </header>

{toc}

    <div class="byline">{lines} budget lines &nbsp;·&nbsp; {countries} countries &nbsp;·&nbsp; fiscal years {yr}</div>

{budgets_intro}

    <div class="dl-datatable"
      data-src="{table_csv}"
      data-cols="{cols}"
      data-filters="country, report_year, primary_topic, scope_confidence"
      data-numeric="{numeric}"
      data-thousands="budget_usd"
      data-labels="{labels}"
      data-tips="{tips}"
      data-detail="{detail}"
      data-sort="country:asc"
      data-empty="No budget line matches those filters.">
      <div class="dt-controls">
        <span class="dt-title">Africa &mdash; national budgets</span>
        <span class="dt-count">{lines} rows</span>
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


def read_rows(path: Path) -> tuple[list[str], list[dict]]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rdr = csv.DictReader(fh)
        return list(rdr.fieldnames or []), list(rdr)


def budgets_dataset(rows: list[dict], meta: list[dict], csv_path: Path, edition: str,
                    years: list[int]) -> str:
    """The budgets table described as data, dated to its edition like the non-state one."""
    return structured_data.dataset(
        name="Data Landscapers national budgets — Africa",
        description=copy_md("finance", "dataset-budgets"),
        url=f"{SITE_BASE}/finance/budgets/",
        csv_url=f"{SITE_BASE}/finance/budgets/{csv_path.name}",
        csv_bytes=structured_data.bytes_of(csv_path),
        records=len(rows),
        fields=structured_data.fields_from([{"Column": m["column"], "Definition": m["definition"]}
                                            for m in meta]),
        entity={"@type": "Place", "name": "Africa"},
        temporal=structured_data.year_span([min(years), max(years)] if years else [None, None]),
        modified=edition or None,
        version=edition or None,
        extra_keywords=("Government budgets", "Public finance", "Digital transformation"))


def publish_budgets(out: Path, names: dict) -> None:
    """`/finance/budgets/`: the intro, then every budget line in one table *(Bill, 2026-09-30)*.

    The CSV is cut as a dated edition like every other download here, so the file a reader
    keeps is never revised under them. The table shows the file's first nine columns and the
    row panel every column; tooltips are the dictionary's definitions."""
    page = out / "index.html"
    header, rows = read_rows(BUDGETS_CSV)
    _, meta = read_rows(BUDGETS_META)
    body = BUDGETS_CSV.read_bytes().replace(b"\r\n", b"\n")
    if BUDGETS_DATED:
        csv_path, _ = editions.publish(body, out, "budgets-all-countries", ".csv", page=page)
        edition = editions.edition_of(csv_path.stem) or ""
        edition_rows = (f'        <dt>Edition</dt><dd class="mono">{edition}</dd>\n'
                        f'        <dt>This file</dt><dd><a href="{csv_path.name}">{csv_path.name}</a>'
                        f' &mdash; a dated edition, kept as published and never revised</dd>')
    else:
        csv_path, edition = out / "budgets-all-countries.csv", ""
        if not csv_path.exists() or csv_path.read_bytes() != body:
            csv_path.write_bytes(body)
        edition_rows = (f'        <dt>This file</dt><dd><a href="{csv_path.name}">{csv_path.name}</a>'
                        f' &mdash; updated as the data changes</dd>')
    shown = [c for c in header if c not in BUDGET_TABLE_OMIT]
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=shown, lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
    table = ("\ufeff" + buf.getvalue()).encode("utf-8")
    if not (out / BUDGET_TABLE_CSV).exists() or (out / BUDGET_TABLE_CSV).read_bytes() != table:
        (out / BUDGET_TABLE_CSV).write_bytes(table)
    used = sorted({r["country"] for r in rows})
    years = sorted({int(r["report_year"]) for r in rows if r["report_year"].isdigit()})
    numeric = [c for c in header if c in BUDGET_NUMERIC]
    page.write_text(external_links(BUDGETS_PAGE.format(
        feedback=feedback("National budgets", f"{SITE_BASE}/finance/budgets/"),
        base=SITE_BASE, main=MAIN_SITE, chrome=chrome('finance', depth=2),
        foot=foot(depth=2), styles=styles(2, "country.css", "datatable.css"), ga=ga(),
        datatable=script("datatable.js", 2),
        artefacts=(editions.artefact_meta("budgets-all-countries", edition, editions.digest(body))
                   if BUDGETS_DATED else ""),
        edition_rows=edition_rows,
        jsonld=budgets_dataset(rows, meta, csv_path, edition, years),
        toc=toc("budgets"), budgets_intro=indent(copy("finance", "budgets-intro")),
        csv_name=csv_path.name, metadata=BUDGETS_METADATA_CSV,
        cols=", ".join(shown[:BUDGET_TABLE_COLS]), detail=", ".join(shown),
        table_csv=editions.versioned(BUDGET_TABLE_CSV, table),
        numeric=", ".join(numeric),
        labels=html.escape(json.dumps({"country": {c: names.get(c, c) for c in used}},
                                      ensure_ascii=False), quote=True),
        tips=html.escape(json.dumps({m["column"]: m["definition"] for m in meta
                                     if m.get("definition")}, ensure_ascii=False), quote=True),
        lines=f"{len(rows):,}", countries=len(used),
        yr=f"{years[0]}–{years[-1]}" if years else "n/a",
        built=date.today().isoformat())), encoding="utf-8")
    print(f"finance: budgets {len(rows):,} lines, {len(used)} countries, edition {edition or 'undated'} "
          f"-> site/finance/budgets/")


ALL_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>All finance — Data Landscapers</title>
<meta name="description" content="Non-state commitments and national budget lines for Africa's digital transformation in one table, searchable and downloadable.">
<link rel="canonical" href="{base}/finance/all/">
{artefacts}
{styles}
<link rel="icon" href="{main}/assets/favicon.svg" type="image/svg+xml">
{jsonld}
{ga}
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container container--wide">

    <header class="article-header">
      {feedback}
      <h1 class="article-header__title">Finance</h1>
    </header>

{toc}

    <div class="byline">{rows} rows &nbsp;·&nbsp; {deals} non-state commitments &nbsp;·&nbsp; {lines} budget lines &nbsp;·&nbsp; {countries} countries &nbsp;·&nbsp; {regions} regions &nbsp;·&nbsp; {yr}</div>

{all_intro}

    <div class="dl-datatable"
      data-src="{csv_src}"
      data-cols="{cols}"
      data-filters="country, year, primary_topic, type, scope"
      data-numeric="year, value_usd"
      data-thousands="value_usd"
      data-labels="{labels}"
      data-tips="{tips}"
      data-detail="{detail}"
      data-sort="year:desc"
      data-empty="No row matches those filters.">
      <div class="dt-controls">
        <span class="dt-title">Africa &mdash; all finance</span>
        <span class="dt-count">{rows} rows</span>
        <a class="btn btn--sm" href="{csv_name}" download>&darr; CSV</a>
        <a class="btn btn--sm" href="../../datasets/metadata/#all-finance">Metadata</a>
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
        <dt>Fields</dt><dd><a href="../../datasets/metadata/#all-finance">What each column means</a> and its allowed values &mdash; also as <a href="../../metadata/{metadata}">{metadata}</a></dd>
        <dt>Joined from</dt><dd><a href="../">Non-state finance</a> and <a href="../budgets/">National budgets</a>, which carry every other field under the same <code>deal_id</code></dd>
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


def budget_title(r: dict) -> str:
    """Programme : sub-programme : line, each said once. Budgets repeat a name down the
    chain where they print no finer level — the programme is the line on 4,659 rows."""
    parts: list[str] = []
    for key in ("programme", "sub_programme", "line_name"):
        v = (r.get(key) or "").strip()
        if v and v.casefold() not in (p.casefold() for p in parts):
            parts.append(v)
    return " : ".join(parts)


def finance_type(r: dict) -> str:
    """A non-state row's `type`: aid, or other finance split by whether the financier is
    African *(Bill, 2026-10-03)*. A financier the lookup does not place stays `other finance`."""
    if r.get("aid") == "true":
        return "aid"
    where = (r.get("african") or "").strip()
    return f"other {where} finance" if where else "other finance"


def all_finance_rows(nonstate: list[dict], budget: list[dict]) -> list[dict]:
    """The two tables as one, in `ALL_COLUMNS`: Bill's mapping in
    `documentation/joined-up-finance-spec.csv`, plus `scope` and `scope_basis`, which both
    sides carry. `value_usd` is whole dollars on both sides, and already at half on a row
    whose scope is partial or unclear: each source table halves its own."""
    out = []
    for r in nonstate:
        year = (r.get("start_year") or "").strip()[:4]
        if not year.isdigit() or int(year) < ALL_FIRST_YEAR:
            continue
        m = r.get("commitment_usd_m") or ""
        out.append({
            "country": r["recipient"], "year": year,
            "primary_topic": r["primary_topic"],
            "type": finance_type(r),
            "financier": r["financier"], "recipient": r["recipient_organisation"],
            "title": r["title"], "description": r["description"],
            "value_usd": f"{float(m) * 1e6:.0f}" if m else "",
            "deal_id": r["deal_id"], "scope": r["scope"], "scope_basis": r["scope_basis"]})
    for r in budget:
        out.append({
            "country": r["country"], "year": r["report_year"],
            "primary_topic": r["primary_topic"], "type": "budget",
            "financier": r["admin_head"], "recipient": r["spending_entity"],
            "title": budget_title(r), "description": r["purpose"],
            "value_usd": r["budget_usd"], "deal_id": r["deal_id"],
            "scope": r["scope_confidence"], "scope_basis": r["scope_basis"]})
    out.sort(key=lambda r: (r["country"], r["year"], r["type"], r["deal_id"]))
    return out


def publish_all_finance(out: Path, sdir: Path, names: dict) -> None:
    """`/finance/all/`: the joined table, its CSV beside it. Undated until `BUDGETS_DATED`,
    a dated edition after, as the budget table it is half made of."""
    page = out / "index.html"
    _, nonstate = read_rows(sdir / "all-nonstate.csv")
    _, budget = read_rows(BUDGETS_CSV)
    _, meta = read_rows(ALL_META)
    if [m["column"] for m in meta] != list(ALL_COLUMNS):
        raise SystemExit(f"finance: {ALL_META.relative_to(CORPUS)} does not describe ALL_COLUMNS")
    rows = all_finance_rows(nonstate, budget)
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=ALL_COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    body = ("\ufeff" + buf.getvalue()).encode("utf-8")
    if BUDGETS_DATED:
        csv_path, _ = editions.publish(body, out, "all-finance", ".csv", page=page)
        edition = editions.edition_of(csv_path.stem) or ""
        edition_rows = (f'        <dt>Edition</dt><dd class="mono">{edition}</dd>\n'
                        f'        <dt>This file</dt><dd><a href="{csv_path.name}">{csv_path.name}</a>'
                        f' &mdash; a dated edition, kept as published and never revised</dd>')
    else:
        csv_path, edition = out / "all-finance.csv", ""
        if not csv_path.exists() or csv_path.read_bytes() != body:
            csv_path.write_bytes(body)
        edition_rows = (f'        <dt>This file</dt><dd><a href="{csv_path.name}">{csv_path.name}</a>'
                        f' &mdash; updated as the data changes</dd>')
    used = sorted({r["country"] for r in rows})
    years = sorted({int(r["year"]) for r in rows if r["year"].isdigit()})
    page.write_text(external_links(ALL_PAGE.format(
        feedback=feedback("All finance", f"{SITE_BASE}/finance/all/"),
        base=SITE_BASE, main=MAIN_SITE, chrome=chrome('finance', depth=2),
        foot=foot(depth=2), styles=styles(2, "country.css", "datatable.css"), ga=ga(),
        datatable=script("datatable.js", 2),
        artefacts=(editions.artefact_meta("all-finance", edition, editions.digest(body))
                   if BUDGETS_DATED else ""),
        edition_rows=edition_rows,
        jsonld=structured_data.dataset(
            name="Data Landscapers all finance — Africa",
            description=copy_md("finance", "dataset-all-finance"),
            url=f"{SITE_BASE}/finance/all/",
            csv_url=f"{SITE_BASE}/finance/all/{csv_path.name}",
            csv_bytes=structured_data.bytes_of(csv_path) or len(body),
            records=len(rows),
            fields=structured_data.fields_from(
                [{"Column": m["column"], "Definition": m["definition"]} for m in meta]),
            entity={"@type": "Place", "name": "Africa"},
            temporal=structured_data.year_span([years[0], years[-1]] if years else [None, None]),
            modified=edition or None, version=edition or None,
            extra_keywords=("Development finance", "Government budgets", "Public finance")),
        toc=toc("all"), all_intro=indent(copy("finance", "all-intro")),
        csv_name=csv_path.name, csv_src=editions.versioned(csv_path.name, body),
        metadata=ALL_METADATA_CSV,
        cols=", ".join(ALL_TABLE_COLS),
        detail=", ".join(ALL_COLUMNS),
        labels=attr_json({"country": {c: names.get(c, c) for c in used}}),
        tips=attr_json({m["column"]: m["definition"] for m in meta if m.get("definition")}),
        rows=f"{len(rows):,}", deals=f"{len(rows) - len(budget):,}", lines=f"{len(budget):,}",
        countries=sum(1 for c in used if not c.startswith("X")),
        regions=sum(1 for c in used if c.startswith("X")),
        yr=f"{years[0]}–{years[-1]}" if years else "n/a",
        built=date.today().isoformat())), encoding="utf-8")
    print(f"finance: all finance {len(rows):,} rows, edition {edition or 'undated'} "
          f"-> site/finance/all/")


def field_dictionary() -> list[dict]:
    """`variableMeasured` for the finance table, from the dictionary every finance page links as
    *what each column means* — twenty columns described in one hand-maintained file, which is
    the arrangement `publish_finance_csvs` chose deliberately over fifty-four copies of it."""
    fd = SITE / "metadata" / METADATA_CSV
    if not fd.exists():
        return []
    with open(fd, encoding="utf-8-sig", newline="") as fh:
        return structured_data.fields_from(list(csv.DictReader(fh)))


def dataset(agg: dict, csv_name: str, edition: str, size: int | None = None) -> str:
    """The whole non-state finance table, described as data *(Bill, 2026-09-20)*.

    **This one is an edition, and the catalogue is not** — which is the whole difference between
    the two dataset blocks on this site. The page offers one dated file, cut on one day and
    never revised (design.md §9), so `version` is that edition and `dateModified` is its date.
    Dating it to the build instead would assert a change on every render of a table nobody has
    touched since the edition was cut, to the one audience that reads `dateModified` literally.

    `temporalCoverage` is the years the *money* covers rather than the years the rows were
    written, because that is the question anyone searching for finance data is asking, and the
    table carries no finer date than the year."""
    return structured_data.dataset(
        name="Data Landscapers non-state finance — Africa",
        description=copy_md("finance", "dataset-all"),
        url=f"{SITE_BASE}/finance/",
        csv_url=f"{SITE_BASE}/finance/{csv_name}",
        # The bytes this build published, where the edition itself has already gone to R2:
        # a re-render after `--prune-local` would otherwise drop the size it knows.
        csv_bytes=structured_data.bytes_of(SITE / "finance" / csv_name) or size,
        records=agg["deals"],
        fields=field_dictionary(),
        entity={"@type": "Place", "name": "Africa"},
        temporal=structured_data.year_span([agg.get("year_min"), agg.get("year_max")]),
        modified=edition or None,
        version=edition or None,
        extra_keywords=("Development finance", "Non-state finance", "Digital infrastructure"))


def render(agg: dict, names: dict, csv_name: str, edition: str,
           artefacts: str = "", size: int | None = None) -> str:
    """The Finance page: non-state finance with its table.

    **One page, not two** *(Bill, 2026-08-19)*. The table had its own URL at
    `all.html` for a few hours; a landing page whose whole job was to link to the
    thing a reader came for is a click charged for nothing. The headline counts
    survive the merge because they say how big the table is before a reader
    scrolls into 1,257 rows; the top-financiers list does not, because it was a
    finding the table produces by sorting one column.

    The label map is the whole of `countries.csv` narrowed to the codes that
    actually appear, so the attribute carries 59 pairs rather than 250 — an
    attribute the browser parses on every page load is not the place to ship a
    vocabulary most of which this table never shows."""
    used = {c: names[c] for c in agg["by_place"] if c in names}
    labels = attr_json({"recipient": used, **AID_LABELS})
    yr = f"{agg['year_min']}–{agg['year_max']}" if agg["year_min"] else "n/a"
    return PAGE.format(
        feedback=feedback("Finance", f"{SITE_BASE}/finance/"),
        base=SITE_BASE, main=MAIN_SITE, chrome=CHROME, foot=FOOT,
        styles=styles(1, "country.css", "datatable.css"), ga=ga(),
        datatable=script("datatable.js", 1),
        csv_name=csv_name, labels=labels, metadata=METADATA_CSV, detail=FINANCE_DETAIL,
        filter_all=attr_json(FILTER_ALL),
        artefacts=artefacts, toc=toc("non-state"),
        non_state_intro=indent(copy("finance", "non-state-intro")
                               + "\n" + copy("finance", "non-state-scope")),
        table_note=indent(copy("finance", "non-state-table-note")),
        deals=f"{agg['deals']:,}", total=f"{agg['total_usd_m']:,.0f}",
        financiers=f"{agg['financiers']:,}", places=agg["places"], regions=agg["regions"], yr=yr,
        jsonld=dataset(agg, csv_name, edition, size),
        built=date.today().isoformat(), edition=edition,
    )


def main() -> int:
    sdir = source_dir()
    agg = load_finance(sdir)
    names = place_names()
    out = SITE / "finance"
    out.mkdir(parents=True, exist_ok=True)
    # Published before the page, because the page links it by name, and which name that is
    # depends on whether `publish` cut a new edition or kept the standing one (§9).
    # LF on the way out, for the reason `country.py` sets out at its own `publish` call:
    # a line-ending difference moves the bytes without moving a value, and would mint an
    # edition that revises nothing.
    #
    # **`page=` carries the comparison the pruned file used to make** *(2026-09-09)*. The
    # page is written on the line below, so here it is still last run's and still holds
    # last run's digest — the only local record of what is published once `--prune-local`
    # has taken the CSV out of the tree.
    body = (sdir / "all-nonstate.csv").read_bytes().replace(b"\r\n", b"\n")
    page = out / "index.html"
    csv_path, _ = editions.publish(body, out, "all-nonstate", ".csv", page=page)
    # **The edition is parsed once, by `editions`, and passed down.** `render()` used to split
    # the filename itself — `csv_name.rsplit("-", 1)[-1][:-4]` — which on
    # `all-nonstate-2026-09-19.csv` yields `19`, and that is what the colophon's Edition row has
    # been showing. The country finance pages beside it read `2026-09-18`, because `country.py`
    # asks `editions.edition_of`. A second parse of a filename grammar that has one owner is
    # how one page comes to disagree with sixty-one others about what it is offering.
    edition = editions.edition_of(csv_path.stem) or ""
    artefacts = editions.artefact_meta("all-nonstate", edition, editions.digest(body))
    page.write_text(external_links(render(agg, names, csv_path.name, edition, artefacts, len(body))),
                    encoding="utf-8")
    (out / "budgets").mkdir(exist_ok=True)
    publish_budgets(out / "budgets", names)
    (out / "all").mkdir(exist_ok=True)
    publish_all_finance(out / "all", sdir, names)
    stale = out / "all.html"
    if stale.exists():                 # the table's own page, folded into index.html
        stale.unlink()
        print("  removed site/finance/all.html — the table is on the page itself now")
    print(f"finance: {agg['deals']:,} deals, US${agg['total_usd_m']:,.0f}m "
          f"-> site/finance/index.html, site/finance/budgets/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
