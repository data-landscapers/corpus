#!/usr/bin/env python3
"""region.py — the region page (documentation/design.md §3), item 6 of Bill's
2026-09-02 list: "exactly the same as [the] countries page but without status
report."

    python scripts/region.py            builds every region
    python scripts/region.py XAF        builds one

A region issues two documents, not four (`REPORT-REGION.md`): a monthly
update and a progress report, never a status report and never a per-place
budget line — so there is no `{code}-status.md` to open the way `country.py`
opens one for every country it builds. Everything else on the page — the
Reports list, the catalogue cut, the non-state finance pivot and table, the
colophon — is `country.py`'s own machinery, reused wholesale rather than
re-derived: `report_editions()` already omits a document kind that was never
rendered, so a region simply never offers a status row, without either module
knowing about the other's document set.

Output lands in the same tree country.py writes to — `site/countries/{code}/`
— because that is the URL `scripts/home.py`'s region boxes link to as of
2026-09-02 (item 7): one directory of place pages, ISO3 codes and `X`-codes
side by side, exactly as `outputs/reports/` and `outputs/non-state-finance/`
already hold both.

Region names are duplicated from `lookups/countries.csv` because the build
cannot read outside `outputs/` — the same trade-off `country.py`'s
`FULL_NAMES` and `home.py`'s `REGION_NAMES` already carry
(osint-corpus-exchange/notes-for-osint.md #9); this is a third copy of the same
eight names; kept identical to `home.py`'s spelling so a box and its page
never disagree on the region's name.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from copy_lib import copy_inline  # noqa: E402
from chrome_lib import chrome, external_links, foot, ga, styles  # noqa: E402
import country  # noqa: E402 — the per-page machinery this reuses wholesale

CORPUS = Path(__file__).resolve().parent.parent
OUTPUTS = CORPUS / "outputs"
SITE = CORPUS / "site"
OUT = SITE / "countries"

SITE_BASE = "https://corpus.data-landscapers.io"
MAIN_SITE = "https://data-landscapers.io"

# Region and bloc codes -> display name — home.py's REGION_NAMES, duplicated
# rather than imported so a CSS-only change to one page never has to import
# the other's build script to get a paragraph.
REGION_NAMES = {
    "XAF": "Africa", "XCA": "Central Africa", "XEA": "East Africa",
    "XGL": "Global", "XNA": "North Africa", "XSA": "Southern Africa",
    "XSS": "Sub-Saharan Africa", "XWA": "West Africa",
}

CHROME = chrome("countries", depth=2)
FOOT = foot(depth=2)


# Same shape as country.py's COUNTRY template, with one crumb-level change:
# the nav section a region belongs to is "Countries & Regions", not
# "Countries", so the finance sub-page's breadcrumb says so rather than
# naming the section a region is not a member of.
REGION = """<!DOCTYPE html>
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
      <div class="crumb"><a href="{base}/countries/">Countries &amp; Regions</a> &nbsp;/&nbsp; <a href="index.html">{name}</a> &nbsp;/&nbsp; Non-state finance</div>
      <h1>Non-state finance</h1>
      <div class="country-head__meta">{name} &nbsp;·&nbsp; {fin_n} commitments &nbsp;·&nbsp; US${fin_total}m &nbsp;·&nbsp; {y0}&ndash;{y1}</div>
    </div>

    <p>Every non-state commitment the base holds for {name}. One row per commitment; each is tagged to one place only, so per-place totals sum without double-counting. <strong>Click any row to open the full record</strong> &mdash; the columns show what a reader scans by, and the rest of the fields sit underneath rather than four screens to the right. Sort on any column heading, filter with the dropdowns, and search across every field whether or not it is shown. The <code>url</code> column is the publisher&rsquo;s own link to the source the row was read from.</p>

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
        <dt>Fields</dt><dd><a href="{fields_name}">non-state-finance-metadata.csv</a> &mdash; what each column means. One dictionary for every place's table, not a copy per place</dd>
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


def build(code: str) -> list[Path]:
    name = REGION_NAMES.get(code, code)
    fin = country.finance(code)
    n_place, n_all, cat_cols, cat_rows = country.catalogue(code)
    built = date.today().isoformat()

    out_dir = OUT / code
    out_dir.mkdir(parents=True, exist_ok=True)
    cat_csv = country.publish_catalogue_cut(code, out_dir, cat_cols, cat_rows)

    common = dict(
        base=SITE_BASE, main_site=MAIN_SITE, iso=code, name=name,
        favicon=f"{MAIN_SITE}/assets/favicon.svg",
        chrome=CHROME, foot=FOOT,
        built=built, fin_n=len(fin),
    )

    csv_names: dict[str, str] = {}
    if fin:
        cols = list(fin[0].keys())
        ys = [y for y in (country.year(r.get("start_year")) for r in fin) if y is not None]
        amounts = [float(r["commitment_usd_m"]) for r in fin if r.get("commitment_usd_m")]
        csv_names = country.publish_finance_csvs(code, out_dir, cols)
        finance_section = country.FINANCE_BLOCK.format(
            name=name, iso=code, pivot=country.pivot(fin), cutoff=country.FINANCE_CUTOFF,
            fin_n=len(fin), ncols=len(cols), **csv_names)
    else:
        cols, ys, amounts = [], [], []
        finance_section = country.FINANCE_EMPTY.format(name=name)

    (out_dir / "index.html").write_text(external_links(REGION.format(
        tracked=country.tracked(code)[0],
        sources=f"{n_place:,}", cat_total=f"{n_all:,}", cat_csv=cat_csv,
        catalogue_intro=copy_inline("country", "catalogue-intro",
                                    sources=f"{n_place:,}", name=name),
        budget_intro=copy_inline("country", "budget-intro"),
        reports=country.report_rows(country.report_editions(code), code),
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


def main() -> int:
    country.check_metadata()
    codes = sys.argv[1:] or sorted(REGION_NAMES)
    for code in codes:
        paths = build(code)
        print(f"{code}  {len(paths)} files  ->  {paths[0].parent.relative_to(CORPUS)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
