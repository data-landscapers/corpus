#!/usr/bin/env python3
"""finance.py — the Finance page.

    python scripts/finance.py
      -> site/finance/index.html                   non-state finance
      -> site/finance/budgets/index.html           national budgets: intro text only
      -> site/finance/all-nonstate-{edition}.csv   the full download, a dated edition (§9)

**Two pages under one toc bar, the Progress arrangement** *(Bill, 2026-09-22)*.
`/finance/` carries non-state finance and nothing else; `/finance/budgets/` carries
the intro to the budget work and no figures. The budget tables — the coverage table
and the line-level datatable, published from 2026-09-20 (R53) — came off the site the
same day, and no further `all-budgets` edition is cut; the editions already published
stay where they are (§9). Finance also left the nav bar that day: the home page and
the Datasets page are the ways in.

The table is the cross-country counterpart of each country's `finance.html` and uses
the same component: `site/assets/js/datatable.js` fetches the published CSV and draws
it in the browser. That is not a preference but the only option — 1,257 rows by 20
columns baked into HTML is a multi-megabyte page, where the CSV it reads instead is
1.1 MB and is a file the reader can keep. `recipient_country` is carried as an ISO-3
code in the data and shown as a country name in the table, through the `data-labels`
map built from `outputs/vocab/countries.csv`.

**The prose is in `content/finance.md`**, not here (RENDER.md -> *The prose*).

Reads `outputs/non-state-finance/all-nonstate.csv` (the deduped cross-country
partition — one row per deal). Vocabularies come from `outputs/vocab/` like the
catalogue, so the site still reads only `outputs/`.

The domestic-budget side is still compiled per country into `outputs/budgets/{ISO3}-budget.csv`;
nothing here reads it.
"""
from __future__ import annotations
import csv, html, json, sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import editions  # noqa: E402  - one implementation of the edition grammar (§9)
from copy_lib import copy, copy_md  # noqa: E402
import structured_data  # noqa: E402
from chrome_lib import chrome, external_links, feedback, foot, ga, script, styles  # noqa: E402

CORPUS = Path(__file__).resolve().parent.parent
OUTPUTS = CORPUS / "outputs"
SITE = CORPUS / "site"
VOCAB = CORPUS / "outputs" / "vocab"
SITE_BASE = "https://corpus.data-landscapers.io"
MAIN_SITE = "https://data-landscapers.io"

# The one field dictionary for every non-state finance table (country.py writes the
# same link). Hand-maintained; nothing generates it.
METADATA_CSV = "non-state-finance-metadata.csv"


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
    by_place: Counter = Counter()              # deal count by recipient_country
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
            if r.get("recipient_country"):
                by_place[r["recipient_country"]] += 1
            if r.get("sector"):
                by_sector[r["sector"]] += 1
            for y in (r.get("start_year"), r.get("end_year")):
                if y and y.isdigit():
                    years.append(int(y))
    return {
        "deals": deals,
        "total_usd_m": total_usd_m,
        "financiers": len(by_financier),
        "places": len(by_place),
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
    """NON-STATE FINANCE · BUDGETS, the bar `progress.py` → `toc` puts over its two
    views. Both items are links, the current one pointing at itself with
    `aria-current`, for the reason given there: `.article-toc a` styles the whole bar."""
    items = [("non-state", "Non-state finance", "./" if current == "non-state" else "../"),
             ("budgets", "Budgets", "budgets/" if current == "non-state" else "./")]
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

    <h2 class="section-heading" id="non-state">Non-state finance</h2>
    <div class="byline">{deals} commitments &nbsp;·&nbsp; US${total}m &nbsp;·&nbsp; {financiers} financiers &nbsp;·&nbsp; {places} recipient countries &nbsp;·&nbsp; {yr}</div>

{non_state_intro}

{table_note}

    <div class="dl-datatable"
      data-src="{csv_name}"
      data-cols="recipient_country, start_year, financier, sector, instrument, commitment_usd_m, status, title, description, recipient_organisation, url"
      data-filters="recipient_country, sector, instrument, status, amount_quality, beneficiary_type"
      data-numeric="start_year, end_year, commitment_usd_m"
      data-links="url"
      data-labels="{labels}"
      data-detail="description"
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
        <dt>Country</dt><dd><code>recipient_country</code> is an ISO-3 code in the file and a country name in the table; the two are the same thing</dd>
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
<meta name="description" content="What African states spend from their own budgets on digital transformation: work in progress.">
<link rel="canonical" href="{base}/finance/budgets/">
{styles}
<link rel="icon" href="{main}/assets/favicon.svg" type="image/svg+xml">
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
    <h2 class="section-heading" id="budgets">National budgets</h2>

{budgets_intro}

  </div>
  </main>

{foot}

</div>
</body>
</html>
"""


def render_budgets() -> str:
    """The budgets page: the intro and nothing under it *(Bill, 2026-09-22)*."""
    return BUDGETS_PAGE.format(
        feedback=feedback("National budgets", f"{SITE_BASE}/finance/budgets/"),
        base=SITE_BASE, main=MAIN_SITE, chrome=chrome('finance', depth=2),
        foot=foot(depth=2), styles=styles(2, "country.css"), ga=ga(),
        toc=toc("budgets"), budgets_intro=indent(copy("finance", "budgets-intro")))


def field_dictionary() -> list[dict]:
    """`variableMeasured` for the finance table, from the dictionary every finance page links as
    *what each column means* — twenty columns described in one hand-maintained file, which is
    the arrangement `publish_finance_csvs` chose deliberately over fifty-four copies of it."""
    fd = SITE / "metadata" / METADATA_CSV
    if not fd.exists():
        return []
    with open(fd, encoding="utf-8-sig", newline="") as fh:
        return structured_data.fields_from(list(csv.DictReader(fh)))


def dataset(agg: dict, csv_name: str, edition: str) -> str:
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
        csv_bytes=structured_data.bytes_of(SITE / "finance" / csv_name),
        records=agg["deals"],
        fields=field_dictionary(),
        entity={"@type": "Place", "name": "Africa"},
        temporal=structured_data.year_span([agg.get("year_min"), agg.get("year_max")]),
        modified=edition or None,
        version=edition or None,
        extra_keywords=("Development finance", "Non-state finance", "Digital infrastructure"))


def render(agg: dict, names: dict, csv_name: str, edition: str,
           artefacts: str = "") -> str:
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
    labels = html.escape(json.dumps({"recipient_country": used}, ensure_ascii=False), quote=True)
    yr = f"{agg['year_min']}–{agg['year_max']}" if agg["year_min"] else "n/a"
    return PAGE.format(
        feedback=feedback("Finance", f"{SITE_BASE}/finance/"),
        base=SITE_BASE, main=MAIN_SITE, chrome=CHROME, foot=FOOT,
        styles=styles(1, "country.css", "datatable.css"), ga=ga(),
        datatable=script("datatable.js", 1),
        csv_name=csv_name, labels=labels, metadata=METADATA_CSV,
        artefacts=artefacts, toc=toc("non-state"),
        non_state_intro=indent(copy("finance", "non-state-intro")),
        table_note=indent(copy("finance", "non-state-table-note")),
        deals=f"{agg['deals']:,}", total=f"{agg['total_usd_m']:,.0f}",
        financiers=f"{agg['financiers']:,}", places=agg["places"], yr=yr,
        jsonld=dataset(agg, csv_name, edition),
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
    page.write_text(external_links(render(agg, names, csv_path.name, edition, artefacts)),
                    encoding="utf-8")
    (out / "budgets").mkdir(exist_ok=True)
    (out / "budgets" / "index.html").write_text(external_links(render_budgets()),
                                                 encoding="utf-8")
    stale = out / "all.html"
    if stale.exists():                 # the table's own page, folded into index.html
        stale.unlink()
        print("  removed site/finance/all.html — the table is on the page itself now")
    print(f"finance: {agg['deals']:,} deals, US${agg['total_usd_m']:,.0f}m "
          f"-> site/finance/index.html, site/finance/budgets/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
