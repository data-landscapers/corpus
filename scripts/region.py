#!/usr/bin/env python3
"""region.py — the region page (documentation/design.md §3), item 6 of Bill's
2026-09-02 list: "exactly the same as [the] countries page but without status
report."

    python scripts/region.py            builds every region
    python scripts/region.py XAF        builds one

**The region page is retired with the country page** *(Bill, 2026-10-17)*: `index.html`
forwards to the region's news page, and the finance table and CSVs stay.

A region issues one document, not four (`REPORT-REGION.md`): a monthly
update, never a status report and never a per-place
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
from chrome_lib import chrome, feedback, foot, ga, script, styles  # noqa: E402
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


# The finance page is `country.py`'s, with `unit="place"`. It was a copy of that
# template differing in three lines of wording until 2026-09-09; the header there
# records what the copy cost.
FINANCE = country.FINANCE


def build(code: str) -> list[Path]:
    name = REGION_NAMES.get(code, code)
    fin = country.finance(code)
    _, _, cat_cols, cat_rows = country.catalogue(code)
    built = date.today().isoformat()

    out_dir = OUT / code
    out_dir.mkdir(parents=True, exist_ok=True)
    cat_csv = country.publish_catalogue_cut(code, out_dir, cat_cols, cat_rows)

    common = dict(
        base=SITE_BASE, main_site=MAIN_SITE, iso=code, name=name,
        favicon=f"{MAIN_SITE}/assets/favicon.svg",
        chrome=CHROME, foot=FOOT,
        built=built, fin_n=len(fin),
        parent=country.place_url(code),      # a region has no finance report to name
    )

    csv_names: dict[str, str] = {}
    if fin:
        cols = list(fin[0].keys())
        ys = [y for y in (country.year(r.get("start_year")) for r in fin) if y is not None]
        amounts = [float(r["commitment_usd_m"]) for r in fin if r.get("commitment_usd_m")]
        csv_names = country.publish_finance_csvs(code, out_dir, cols)
    else:
        cols, ys, amounts = [], [], []

    country.retire_page(out_dir, code)

    written = [out_dir / "index.html", out_dir / cat_csv]

    if fin:
        (out_dir / "finance.html").write_text(country.table_page(out_dir, FINANCE.format(
            feedback=feedback(f"{name} — non-state finance",
                              f"{SITE_BASE}/countries/{code}/finance.html"),
            unit="place",
            jsonld=country.finance_dataset(code, name, out_dir, fin, csv_names["csv_name"],
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
