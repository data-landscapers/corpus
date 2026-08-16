#!/usr/bin/env python3
"""finance.py — the /finance/ landing page (SHELL, not the finished design).

    python scripts/finance.py
      -> site/finance/index.html          the non-state finance landing
      -> site/finance/all-nonstate.csv    the full download (published from source)

Status: SHELL. The aggregation below is real and runnable; the page LAYOUT is a
placeholder for Cowork to design. It exists so the nav link `{base}/finance/`
(build/country.py, scripts/catalogue.py) stops 404ing and so there is a scaffold
to flesh out — headline totals, top financiers, by-sector and by-place tables,
links down to each country's finance page.

Reads `outputs/non-state-finance/all-nonstate.csv` (the deduped cross-country
partition — one row per deal). Vocabularies come from `outputs/vocab/` like the
catalogue, so the site still reads only `outputs/`.

Non-state only, deliberately: the domestic-budget side lives in the per-country
`{ISO3}-budget.csv` / `{ISO3}-summary.csv` and is not aggregated here yet (TODO).
"""
from __future__ import annotations
import csv, shutil, sys
from collections import Counter, defaultdict
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
OUTPUTS = CORPUS / "outputs"
SITE = CORPUS / "site"
VOCAB = CORPUS / "outputs" / "vocab"
SITE_BASE = "https://corpus.data-landscapers.com"
MAIN_SITE = "https://data-landscapers.com"

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


def render(agg: dict, names: dict) -> str:
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
  <p><a href="all-nonstate.csv" download>Download all-nonstate.csv</a> — one row per deal.</p>

  <h2>Top financiers by commitment</h2>
  <table><thead><tr><th>Financier</th><th>Committed</th></tr></thead><tbody>{rows}</tbody></table>

  <!-- TODO (Cowork design): by-sector breakdown; a place matrix linking to each
       country's finance page; the domestic-budget side; caveats on amount_quality. -->
</main>
</body>
</html>
"""


def main() -> int:
    sdir = source_dir()
    agg = load_finance(sdir)
    names = place_names()
    out = SITE / "finance"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(render(agg, names), encoding="utf-8")
    shutil.copyfile(sdir / "all-nonstate.csv", out / "all-nonstate.csv")
    print(f"finance (SHELL): {agg['deals']:,} deals, US${agg['total_usd_m']:,.0f}m "
          f"-> site/finance/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
