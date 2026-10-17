#!/usr/bin/env python3
"""finance-report.py — a country's finance report, `outputs/reports/{ISO3}/{ISO3}-finance.md`.

    python scripts/finance-report.py            every country
    python scripts/finance-report.py KEN GHA    the ones named

**One document over both sides of a country's digital money** *(Bill, 2026-10-16)*: *All
finance* first, then *Public budgeting and expenditure* and *Non-state finance* as the country
page draws them. `render.py` publishes it as `site/reports/{ISO3}/{ISO3}-finance.html` with the
heading, sibling links and contents every place report carries; run this before RENDER Step 2.

**Nothing here is a second copy of the country page.** The two sections are `country.py`'s own
blocks, built by its own functions from the same files, with their links made absolute because
the page lands in `reports/` rather than `countries/`. *All finance* is the same topic-by-year
pivot over both sets of rows added together: budget lines at their counted US dollar value by
the year the fiscal year starts in, commitments by the year they were made.

The download links are the ones the table pages are serving, read off them, so the report never
names a CSV edition `country.py` did not publish; a country with none gets no download button.
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import country as c  # noqa: E402
from copy_lib import copy_inline  # noqa: E402

COUNTRIES = c.SITE / "countries"


def absolute(block: str, iso: str) -> str:
    """The table pages' relative links, made to work from `reports/{ISO3}/` and from a PDF.

    The CSVs are read off the table pages that serve them, since the country page that also
    listed them is retired (`country.retire_page`)."""
    base = f"{c.SITE_BASE}/countries/{iso}"
    page = "".join(p.read_text(encoding="utf-8")
                   for p in (COUNTRIES / iso / n for n in ("finance.html", "budgets.html"))
                   if p.exists())
    published = re.findall(r'href="([^"/]+\.csv)" download', page)

    def fix(m: re.Match) -> str:
        stem = m.group(1)[:-4]                       # `KEN-nonstate`, `KEN-budgets`
        served = [p for p in published if p == f"{stem}.csv" or p.startswith(f"{stem}-")]
        if not served:
            return ""            # a CSV no table page is offering: no button
        return f'<a class="btn btn--accent" href="{base}/{served[0]}"{m.group(2)}'

    block = re.sub(r'<a class="btn btn--accent" href="([^"/]+\.csv)"([^>]*>.*?</a>)', fix, block)
    block = re.sub(r'href="((?:finance|budgets)\.html)"', rf'href="{base}/\1"', block)
    return flush(block.replace('href="../../', f'href="{c.SITE_BASE}/'))


def flush(block: str) -> str:
    """Every line to the margin: an indented line after a blank one is a Markdown code block."""
    return "\n".join(line.strip() for line in block.splitlines())


def all_finance(iso: str, name: str, fin: list[dict], bud: list[dict]) -> str:
    rows = [{"primary_topic": r.get("primary_topic"), "yr": r.get("report_year"),
             "amt": float(r["budget_usd"]) / 1e6} for r in bud if c.budget_counted(r)]
    rows += [{"primary_topic": r.get("primary_topic"), "yr": r.get("start_year"),
              "amt": c.usd_m(r)} for r in fin]
    if not rows:
        return f"<p>{copy_inline('country', 'finance-all-none', name=name)}</p>"
    return flush(f"<p>{copy_inline('country', 'finance-all-intro', name=name)}</p>\n\n"
            + c.pivot(rows, "yr", lambda r: r["amt"])
            + f'\n<p class="table-note">'
              f'{copy_inline("country", "finance-all-note", cutoff=c.FINANCE_CUTOFF)}</p>'
            + all_buttons(iso, len(rows)))


def all_buttons(iso: str, n: int) -> str:
    """The way in to the rows behind the pivot: `country.py`'s `all-finance.html` and the CSV it
    is serving, read off that page so the button names a file that was published."""
    page = COUNTRIES / iso / "all-finance.html"
    if not page.exists():
        return ""
    base = f"{c.SITE_BASE}/countries/{iso}"
    served = re.search(r'href="([^"/]+\.csv)" download', page.read_text(encoding="utf-8"))
    csv_btn = (f'\n<a class="btn btn--accent" href="{base}/{served.group(1)}" download>'
               f'&darr; Download CSV</a>' if served else "")
    return (f'\n<div class="table-acts">\n<a class="btn" href="{base}/all-finance.html">'
            f'Full table &mdash; {n:,} rows, all {len(c.ALL_FIELDS)} fields &rarr;</a>'
            f'{csv_btn}\n</div>')


def build(iso: str) -> Path:
    name = c.FULL_NAMES.get(iso, iso)
    fin = c.finance(iso)
    bud_cols, bud = c.budgets(iso)

    if fin:
        cols = list(fin[0].keys())
        nonstate = c.FINANCE_BLOCK.format(
            name=name, iso=iso, pivot=c.pivot(fin), cutoff=c.FINANCE_CUTOFF,
            fin_n=len(fin), ncols=len(cols), csv_name=f"{iso}-nonstate.csv")
    else:
        nonstate = c.FINANCE_EMPTY.format(name=name)
    if bud:
        budget = c.budget_section(name, bud_cols, bud, f"{iso}-budgets.csv")
    else:
        budget = c.BUDGET_EMPTY.format(intro=copy_inline("country", "budget-intro"))

    # Raw HTML between Markdown headings: `render.py` runs `md_in_html`, and a blank line on each
    # side keeps every block whole. The headings are Markdown so the contents bar finds them.
    out = [
        "---",
        f"title: {name}: finance",
        f"compiled: {date.today().isoformat()}",
        f"place: {iso}",
        "---",
        "",
        "## All finance", "", all_finance(iso, name, fin, bud), "",
        "## Public budgeting and expenditure", "", absolute(budget, iso), "",
        "## Non-state finance", "", absolute(nonstate, iso), "",
    ]
    path = c.OUTPUTS / "reports" / iso / f"{iso}-finance.md"
    text = "\n".join(out)
    old = path.read_text(encoding="utf-8") if path.exists() else None
    # `compiled:` moves only when the content does, as every report's does.
    if old is not None and re.sub(r"^compiled: .*$", "", old, flags=re.M) == \
            re.sub(r"^compiled: .*$", "", text, flags=re.M):
        print(f"{iso}: unchanged")
        return path
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"{iso}: wrote {path.relative_to(c.CORPUS)}")
    return path


def main(argv: list[str]) -> int:
    codes = argv or sorted(p.name for p in (c.OUTPUTS / "reports").iterdir()
                           if p.is_dir() and len(p.name) == 3 and not p.name.startswith("X"))
    for iso in codes:
        build(iso)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
