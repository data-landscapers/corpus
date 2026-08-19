#!/usr/bin/env python3
"""finance.py — the /finance/ landing page (SHELL) and the all-Africa table.

    python scripts/finance.py
      -> site/finance/index.html          the non-state finance landing
      -> site/finance/all.html            every commitment, all countries, one table
      -> site/finance/all-nonstate-{edition}.csv   the full download, a dated edition (§9)

Status: the LANDING is still a SHELL. The aggregation below is real and runnable;
the landing's LAYOUT is a placeholder for Cowork to design. It exists so the nav
link `{base}/finance/` (build/country.py, scripts/catalogue.py) stops 404ing and
so there is a scaffold to flesh out — headline totals, by-sector and by-place
tables, links down to each country's finance page.

`all.html` is not a shell *(2026-08-19)*. It is the cross-country counterpart of
each country's `finance.html`, and uses the same component:
`site/assets/js/datatable.js` fetches the published CSV and draws the table in
the browser. That is not a preference here but the only option — 1,257 rows by 20
columns baked into HTML is a multi-megabyte page, where the CSV it reads instead
is 1.1 MB and is a file the reader can keep. `recipient_country` is carried as an
ISO-3 code in the data and shown as a country name in the table, through the
`data-labels` map built from `outputs/vocab/countries.csv`.

Reads `outputs/non-state-finance/all-nonstate.csv` (the deduped cross-country
partition — one row per deal). Vocabularies come from `outputs/vocab/` like the
catalogue, so the site still reads only `outputs/`.

Non-state only, deliberately: the domestic-budget side lives in the per-country
`{ISO3}-budget.csv` / `{ISO3}-summary.csv` and is not aggregated here yet (TODO).
"""
from __future__ import annotations
import csv, html, json, sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import editions  # noqa: E402  - one implementation of the edition grammar (§9)

CORPUS = Path(__file__).resolve().parent.parent
OUTPUTS = CORPUS / "outputs"
SITE = CORPUS / "site"
VOCAB = CORPUS / "outputs" / "vocab"
SITE_BASE = "https://corpus.data-landscapers.io"
MAIN_SITE = "https://data-landscapers.io"

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
CHROME = """  <header class="site-header">
    <div class="site-header__inner">
      <a href="{main}/" class="site-logo"><img src="../assets/logo.png" alt="Data Landscapers" class="site-logo__img"></a>
      <nav class="site-nav" aria-label="Main navigation"><a href="{base}/" class="active">Corpus</a></nav>
    </div>
  </header>
  <nav class="corpus-nav" aria-label="Corpus navigation">
    <div class="corpus-nav__inner">
      <a href="{base}/#countries">Countries</a>
      <a href="{base}/#regions">Regions</a>
      <a href="{base}/#topics">Topics</a>
      <a href="{base}/finance/" class="active">Finance</a>
      <a href="{base}/catalogue/">Catalogue</a>
      <a href="{base}/method/">Method</a>
    </div>
  </nav>""".format(base=SITE_BASE, main=MAIN_SITE)


def render(agg: dict, names: dict, csv_name: str) -> str:
    yr = f"{agg['year_min']}–{agg['year_max']}" if agg["year_min"] else "n/a"
    # SHELL body: headline stats + a top-financiers list. The full design
    # (by-sector, by-place matrix, links to country finance pages) is TODO.
    rows = "".join(
        f"<tr><td>{f}</td><td>US${v:,.0f}m</td></tr>" for f, v in agg["top_financiers"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Non-state finance — Data Landscapers</title>
<link rel="stylesheet" href="../assets/css/main.css">
<link rel="stylesheet" href="../assets/css/home.css">
</head>
<body>
{CHROME}
<main style="max-width:1000px;margin:0 auto;padding:26px 22px 90px">
  <h1>Non-state finance</h1>
  <p>Deals financed by non-state actors across the base — {agg['deals']:,} deals,
     US${agg['total_usd_m']:,.0f}m committed, {agg['financiers']:,} financiers,
     {agg['places']} recipient countries, {yr}.</p>
  <p><a href="{csv_name}" download>Download {csv_name}</a> — one row per deal. A dated edition (§9): retained as published, and never revised.</p>

  <p><a class="btn" href="all.html">Browse every commitment as a table &rarr;</a> &mdash; sortable, filterable by country, sector and status.</p>

  <h2>Top financiers by commitment</h2>
  <table><thead><tr><th>Financier</th><th>Committed</th></tr></thead><tbody>{rows}</tbody></table>

  <!-- TODO (Cowork design): by-sector breakdown; a place matrix linking to each
       country's finance page; the domestic-budget side; caveats on amount_quality. -->
</main>
</body>
</html>
"""


# --- the all-Africa table. Not a shell: the counterpart of each country's -----
#     finance.html, sharing site/assets/js/datatable.js.
ALL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Non-state finance — every commitment — Data Landscapers</title>
<meta name="description" content="Every non-state commitment to the digital sector across Africa held in the Data Landscapers base, all fields, searchable and downloadable.">
<link rel="canonical" href="{base}/finance/all.html">
<link rel="stylesheet" href="../assets/css/main.css">
<link rel="stylesheet" href="../assets/css/home.css">
<link rel="stylesheet" href="../assets/css/country.css">
<link rel="stylesheet" href="../assets/css/datatable.css">
<link rel="icon" href="{main}/assets/favicon.svg" type="image/svg+xml">
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container container--wide">

    <div class="country-head">
      <div class="crumb"><a href="{base}/finance/">Non-state finance</a> &nbsp;/&nbsp; Every commitment</div>
      <h1>Every commitment</h1>
      <div class="country-head__meta">{deals} commitments &nbsp;·&nbsp; US${total}m &nbsp;·&nbsp; {financiers} financiers &nbsp;·&nbsp; {places} recipient countries &nbsp;·&nbsp; {yr}</div>
    </div>

    <p>Every non-state commitment the base holds, across every country, every field, exactly as the CSV carries it. One row per commitment, and each is tagged to one country only, so totals sum without double-counting &mdash; the regional codes are recipients in their own right, not aggregates of the countries beside them. Figures are the amount announced, in the year announced, converted from the announcing party&rsquo;s own currency at a dated rate; they are commitments, not disbursements, and a multi-year commitment sits wholly in its start year. Each country&rsquo;s own table is linked from its <a href="{base}/#countries">country page</a>.</p>

    <div class="dl-datatable"
      data-src="{csv_name}"
      data-filters="recipient_country, sector, status, amount_quality, beneficiary_type"
      data-numeric="start_year, end_year, commitment_usd_m"
      data-links="url"
      data-labels="{labels}"
      data-sort="start_year:desc"
      data-empty="No commitment matches those filters.">
      <div class="dt-controls">
        <span class="dt-title">Africa &mdash; non-state finance</span>
        <span class="dt-count">{deals} rows</span>
        <a class="btn" href="{csv_name}" download>&darr; CSV</a>
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
        <dt>Country</dt><dd><code>recipient_country</code> is an ISO-3 code in the file and a country name in the table; the two are the same thing</dd>
        <dt>Licence</dt><dd><a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></dd>
      </dl>
    </div>

  </div>
  </main>

</div>
<script src="../assets/js/datatable.js"></script>
</body>
</html>
"""


def render_all(agg: dict, names: dict, csv_name: str) -> str:
    """The cross-country table page.

    The label map is the whole of `countries.csv` narrowed to the codes that
    actually appear, so the attribute carries 59 pairs rather than 250 — an
    attribute the browser parses on every page load is not the place to ship a
    vocabulary most of which this table never shows."""
    used = {c: names[c] for c in agg["by_place"] if c in names}
    labels = html.escape(json.dumps({"recipient_country": used}, ensure_ascii=False), quote=True)
    yr = f"{agg['year_min']}–{agg['year_max']}" if agg["year_min"] else "n/a"
    return ALL.format(
        base=SITE_BASE, main=MAIN_SITE, chrome=CHROME,
        csv_name=csv_name, labels=labels,
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
    csv_path, _ = editions.publish((sdir / "all-nonstate.csv").read_bytes(),
                                   out, "all-nonstate", ".csv")
    (out / "index.html").write_text(render(agg, names, csv_path.name), encoding="utf-8")
    (out / "all.html").write_text(render_all(agg, names, csv_path.name), encoding="utf-8")
    print(f"finance: {agg['deals']:,} deals, US${agg['total_usd_m']:,.0f}m "
          f"-> site/finance/index.html (SHELL) + all.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
