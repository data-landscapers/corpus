#!/usr/bin/env python3
"""finance.py — the Finance page.

    python scripts/finance.py
      -> site/finance/index.html                   the page
      -> site/finance/all-nonstate-{edition}.csv   the full download, a dated edition (§9)

**One top-level page, two sections** *(Bill, 2026-08-19)*. Non-state finance, which
has data behind it and carries the whole cross-country table; and national budgets,
which does not yet and says so. It replaces both the shell landing this file used to
write and the separate `all.html` the table briefly had — see `render()`.

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

The domestic-budget side lives in the per-country `{ISO3}-budget.csv` /
`{ISO3}-summary.csv` and is not aggregated here; the *National budgets* block on the
page says why, and is the thing to change when it is.
"""
from __future__ import annotations
import csv, html, json, sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import editions  # noqa: E402  - one implementation of the edition grammar (§9)
from copy_lib import copy  # noqa: E402
from chrome_lib import chrome, foot, styles  # noqa: E402

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


# --- site chrome (Finance active). Kept in step with scripts/catalogue.py. -----
CHROME = chrome('finance', depth=1)

FOOT = foot(depth=1)


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Finance — Data Landscapers</title>
<meta name="description" content="Money committed to Africa's digital sector: every non-state commitment held in the Data Landscapers base, searchable and downloadable, plus the state of the domestic budget record.">
<link rel="canonical" href="{base}/finance/">
{styles}
<link rel="icon" href="{main}/assets/favicon.svg" type="image/svg+xml">
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container container--wide">

    <div class="country-head">
      <h1>Finance</h1>
    </div>

{page_intro}

    <h2 class="section-heading" id="non-state">Non-state finance</h2>
    <div class="country-head__meta">{deals} commitments &nbsp;·&nbsp; US${total}m &nbsp;·&nbsp; {financiers} financiers &nbsp;·&nbsp; {places} recipient countries &nbsp;·&nbsp; {yr}</div>

{non_state_intro}

{table_note}

    <div class="dl-datatable"
      data-src="{csv_name}"
      data-cols="recipient_country, start_year, financier, sector, instrument, commitment_usd_m, status, title, description, recipient_organisation, url"
      data-filters="recipient_country, sector, status, amount_quality, beneficiary_type"
      data-numeric="start_year, end_year, commitment_usd_m"
      data-links="url"
      data-labels="{labels}"
      data-detail="description"
      data-sort="start_year:desc"
      data-empty="No commitment matches those filters.">
      <div class="dt-controls">
        <span class="dt-title">Africa &mdash; non-state finance</span>
        <span class="dt-count">{deals} rows</span>
        <a class="btn" href="{csv_name}" download>&darr; CSV</a>
        <a class="btn" href="../metadata/{metadata}" download>&darr; Metadata</a>
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

    <h2 class="section-heading" id="budgets">National budgets</h2>

{budgets_intro}

  </div>
  </main>

{foot}

</div>
<script src="../assets/js/datatable.js"></script>
</body>
</html>
"""


def render(agg: dict, names: dict, csv_name: str) -> str:
    """The Finance page: non-state finance with its table, then national budgets
    with an explanation of why there is nothing under it yet.

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
        base=SITE_BASE, main=MAIN_SITE, chrome=CHROME, foot=FOOT,
        styles=styles(1, "home.css", "country.css", "datatable.css"),
        csv_name=csv_name, labels=labels, metadata=METADATA_CSV,
        page_intro=indent(copy("finance", "page-intro")),
        non_state_intro=indent(copy("finance", "non-state-intro")),
        table_note=indent(copy("finance", "non-state-table-note")),
        budgets_intro=indent(copy("finance", "budgets-intro")),
        deals=f"{agg['deals']:,}", total=f"{agg['total_usd_m']:,.0f}",
        financiers=f"{agg['financiers']:,}", places=agg["places"], yr=yr,
        built=date.today().isoformat(), edition=csv_name.rsplit("-", 1)[-1][:-4],
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
    csv_path, _ = editions.publish(
        (sdir / "all-nonstate.csv").read_bytes().replace(b"\r\n", b"\n"),
        out, "all-nonstate", ".csv")
    (out / "index.html").write_text(render(agg, names, csv_path.name), encoding="utf-8")
    stale = out / "all.html"
    if stale.exists():                 # the table's own page, folded into index.html
        stale.unlink()
        print("  removed site/finance/all.html — the table is on the page itself now")
    print(f"finance: {agg['deals']:,} deals, US${agg['total_usd_m']:,.0f}m "
          f"-> site/finance/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
