#!/usr/bin/env python3
"""build-country-page.py — mock-up of the country page (DESIGN.md §3).

Generates two pages from `upstream/` alone, plus a field dictionary:

    prototypes/country-KEN.html            the country page
    prototypes/finance-KEN.html            the full non-state finance table
    prototypes/KEN-nonstate-fields.csv     the dictionary the table links to

    python prototypes/build-country-page.py KEN

Nothing is typed by hand: the counts come from the report frontmatter and the
catalogue, the report rows from the filenames in `site/reports/{ISO3}/`, and
both finance tables from `{ISO3}-nonstate.csv` — the country page carries the
sector-by-year summary, the full table carries every column of every row, in
the house data-table pattern used by the cable factsheet on data-landscapers.com
(title and row count, search, Download CSV, Download metadata, sortable headers).

Disposable scaffolding (§5). When the real build lands this becomes a renderer
in `build/` and the page-specific CSS moves into a stylesheet.

Budget work is suspended, so `{ISO3}-summary.csv` is not read and no budget
block appears.
"""

from __future__ import annotations

import csv
import html
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import markdown

CORPUS = Path(__file__).resolve().parent.parent
UPSTREAM = CORPUS / "upstream"
SITE = CORPUS / "site"
OUT = CORPUS / "prototypes"

SITE_BASE = "https://corpus.data-landscapers.com"
NAMES = {"KEN": "Kenya"}
REGION = {"KEN": "Eastern Africa"}
FINANCE_CUTOFF = 2022  # years before this are aggregated into one pivot column

KIND = {
    "status": ("Status report", "A summary of the status of all known systems and instruments"),
    "monthly": ("Monthly update", "A summary of news reported in the last month"),
    "progress": ("Twelve-month progress report", "A breakdown of progress recorded over the past twelve months"),
}

# Column definitions for the dictionary the full table offers, from
# FINANCE-COMPILE.md § "CSV export". Two columns the CSV carries are not
# described there — see NOTES-FOR-OSINT.md — and are marked as read off the data.
FIELDS = [
    ("recipient_country", "ISO-3 code of the country the commitment is tagged to. The join key.", "FINANCE-COMPILE.md"),
    ("start_year", "Year the commitment starts, or the year it was announced where no start is stated.", "FINANCE-COMPILE.md"),
    ("end_year", "Year the commitment ends, where one is stated.", "FINANCE-COMPILE.md"),
    ("financier", "Canonical financier name, resolved from financier_slug. Never key analysis on this field.", "FINANCE-COMPILE.md"),
    ("sector", "Subject slug's display name, from the wiki taxonomy.", "FINANCE-COMPILE.md"),
    ("instrument", "Loan, grant, equity, guarantee or other form the money takes.", "FINANCE-COMPILE.md"),
    ("commitment_usd_m", "Amount committed, US$ millions, converted from the announcing party's own currency at a dated rate.", "FINANCE-COMPILE.md"),
    ("amount_basis", "What the figure is: commitment, disbursement, or other.", "read off the data"),
    ("amount_quality", "How firm the figure is: exact, rounded, estimated, reported, imputed, stated.", "read off the data"),
    ("status", "Status of the commitment as last reported — approved, launched, signed, completed.", "FINANCE-COMPILE.md"),
    ("title", "Record title: financier, what, and year.", "FINANCE-COMPILE.md"),
    ("description", "The full record block, including quoted source text.", "FINANCE-COMPILE.md"),
    ("beneficiary_type", "Government, private sector, civil society or other.", "FINANCE-COMPILE.md"),
    ("recipient_organisation", "Name of the receiving organisation, where stated.", "FINANCE-COMPILE.md"),
    ("original_amount", "The amount as announced, in the currency announced.", "FINANCE-COMPILE.md"),
    ("project_id", "Financier's own project identifier, where one is published.", "FINANCE-COMPILE.md"),
    ("iati_activity_id", "IATI activity identifier, where the financier publishes to IATI.", "FINANCE-COMPILE.md"),
    ("url", "The publisher's own link to the source the record was read from.", "FINANCE-COMPILE.md"),
    ("financier_slug", "Canonical financier identifier. The key to group or join financiers on.", "FINANCE-COMPILE.md"),
    ("record", "Slug of the wiki record this row was compiled from.", "FINANCE-COMPILE.md"),
]

csv.field_size_limit(10 ** 9)


# ── reading upstream ──────────────────────────────────────────────

def frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    head = text[3:text.find("\n---", 3)]
    return {k.strip(): v.strip() for k, v in
            (l.split(":", 1) for l in head.splitlines() if ":" in l)}


def editions(iso: str) -> list[dict]:
    """The published editions, read off the rendered filenames.

    `{ISO3}-{kind}[-{period}]-{edition}.html` — the edition is always the last
    dated field. Only the newest edition of each kind is offered. Read and
    Download always line up between rows, so nothing else renders in the row.
    """
    found: dict[str, list[tuple[str, str]]] = {}
    for f in sorted((SITE / "reports" / iso).glob(f"{iso}-*.html")):
        parts = f.stem.split("-")
        kind, edition = parts[1], "-".join(parts[-3:])
        found.setdefault(kind, []).append((edition, f.name))
    rows = []
    for kind in ("status", "monthly", "progress"):
        if kind not in found:
            continue
        eds = sorted(found[kind], reverse=True)
        edition, name = eds[0]
        rows.append({
            "kind": kind, "label": KIND[kind][0], "blurb": KIND[kind][1],
            "edition": edition, "html": name, "pdf": name[:-5] + ".pdf",
        })
    return rows


def report_meta(iso: str, kind: str) -> dict:
    for f in (UPSTREAM / "reports" / iso).glob(f"{iso}-{kind}*.md"):
        return frontmatter(f.read_text(encoding="utf-8"))
    return {}


def catalogue(iso: str) -> tuple[int, int, list[tuple[str, int]]]:
    """Records held for the place, records held in all, and the commonest
    publishers for the place."""
    n = total = 0
    pubs: dict[str, int] = defaultdict(int)
    with open(UPSTREAM / "catalogue" / "raw-catalogue.csv", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            total += 1
            if iso in (row.get("places") or ""):
                n += 1
                pubs[(row.get("publisher") or "").strip()] += 1
    top = sorted(((p, c) for p, c in pubs.items() if p), key=lambda x: -x[1])[:6]
    return n, total, top


def finance(iso: str) -> list[dict]:
    with open(UPSTREAM / "non-state-finance" / f"{iso}-nonstate.csv",
              encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def built_from() -> str:
    return (UPSTREAM / "BUILT-FROM").read_text(encoding="utf-8").strip()


# ── rendering ─────────────────────────────────────────────────────

def e(s: str) -> str:
    return html.escape(s or "")


def num(v: float) -> str:
    return f"{v:,.0f}" if v == int(v) else f"{v:,.1f}"


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
    def col(y: str) -> str:
        return y if int(y) >= FINANCE_CUTOFF else f"-{FINANCE_CUTOFF}"

    yrs = {r["start_year"] for r in rows if r.get("start_year")}
    cols = ([f"-{FINANCE_CUTOFF}"] if any(int(y) < FINANCE_CUTOFF for y in yrs) else []) \
        + sorted(y for y in yrs if int(y) >= FINANCE_CUTOFF)
    cell: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for r in rows:
        if not r.get("start_year"):
            continue
        cell[r.get("sector") or "(unstated)"][col(r["start_year"])] += float(r.get("commitment_usd_m") or 0)
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

    return f"""<table class="pivot">
        <thead><tr><th scope="col">Sector</th>{head}<th class="num total">Total</th></tr></thead>
        <tbody>
{chr(10).join(body)}
        </tbody>
        <tfoot><tr><th scope="row">All sectors</th>{foot}<td class="num total">{grand}</td></tr></tfoot>
      </table>"""


def full_rows(rows: list[dict], cols: list[str]) -> str:
    """Every column of every row, the factsheet's shape. `url` renders as a
    link on the publisher's own domain, because a bare URL in a cell is
    unreadable and the domain is the part a reader judges."""
    out = []
    for r in rows:
        tds = []
        for c in cols:
            v = r.get(c, "") or ""
            if c == "url" and v:
                dom = re.sub(r"^https?://(www\.)?", "", v).split("/")[0]
                tds.append(f'<td><a href="{e(v)}">{e(dom)}</a></td>')
            elif c in ("commitment_usd_m", "start_year", "end_year"):
                tds.append(f'<td class="num mono">{e(v)}</td>')
            elif c == "description":
                tds.append(f'<td class="wrapcell">{e(v)}</td>')
            else:
                tds.append(f"<td>{e(v)}</td>")
        out.append("<tr>" + "".join(tds) + "</tr>")
    return "\n".join(out)


MONTHS = ("January February March April May June July August September "
          "October November December").split()


def period_label(kind: str, period: str) -> str:
    """`2026-07-01 to 2026-08-05` reads as a range on a progress report and as
    noise on a monthly one, where the month is the point. Taken from the
    frontmatter, not the filename: a progress report is named for the month it
    was cut in but covers the twelve months before it."""
    if not period:
        return ""
    if kind == "monthly":
        y, m, _ = period.split(" ")[0].split("-")
        return f"{MONTHS[int(m) - 1]} {y}"
    return period.replace(" to ", " &ndash; ")


def report_rows(rows: list[dict], iso: str) -> str:
    out = []
    for r in rows:
        meta = report_meta(iso, r["kind"])
        counts = ""
        if meta.get("ledger_rows"):
            counts = (f'{meta["ledger_rows"]} tracked'
                      + (f', <span class="nh">{meta["not_held"]} not held</span>'
                         if meta.get("not_held") else ""))
        label = period_label(r["kind"], meta.get("period", ""))
        period = f' &nbsp;·&nbsp; {label}' if label else ""
        out.append(f"""
      <div class="report-row">
        <div class="report-row__main">
          <div class="report-row__kind">{r['label']}</div>
          <div class="report-row__blurb">{r['blurb']}</div>
          <div class="report-row__meta">Edition of <span class="mono">{r['edition']}</span>{period}
            {' &nbsp;·&nbsp; ' + counts if counts else ''}</div>
        </div>
        <div class="report-row__acts">
          <a class="btn" href="../site/reports/{iso}/{r['html']}">Read</a>
          <a class="btn btn--accent" href="../site/reports/{iso}/{r['pdf']}">&darr; PDF</a>
        </div>
      </div>""")
    return "\n".join(out)


# ── page CSS (mock-up only; moves to site/assets/css/country.css) ──

PAGE_CSS = """
.country-head { border-bottom: 1px solid var(--rule); padding-bottom: 1.5rem; margin-bottom: 2rem; }
.country-head h1 { font-size: 3rem; margin-bottom: 0.35rem; }
.country-head__meta { font-family: var(--mono); font-size: 0.72rem; color: var(--ink-faint); letter-spacing: 0.03em; }

/* Still used by the full non-state-finance table's breadcrumb (finance-{iso}.html). */
.crumb { font-family: var(--mono); font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.09em; color: var(--ink-faint); margin-bottom: 0.6rem; }
.crumb a { color: var(--ink-faint); }

/* The shared .stat-bar (main.css) is a full-bleed strip on the home page;
   here it sits inside the content column, so it takes its own border and
   corners rather than the home page's border-bottom-only treatment. */
.stat-bar { margin: 0 0 2.5rem; border: 1px solid var(--rule); border-radius: 3px; }
.stat-bar__inner { gap: 0.35rem 2.5rem; }

.report-row { display: flex; gap: 1.5rem; align-items: center; justify-content: space-between; padding: 1.1rem 0; border-bottom: 1px solid var(--rule); }
.report-row:first-of-type { border-top: 1px solid var(--rule); }
.report-row__kind { font-family: var(--display); font-weight: 700; font-size: 1.12rem; }
.report-row__blurb { font-size: 0.86rem; color: var(--ink-light); margin-top: 0.1rem; }
.report-row__meta { font-size: 0.75rem; color: var(--ink-faint); margin-top: 0.4rem; }
.report-row__meta .nh { color: var(--accent); }
.report-row__acts { display: flex; gap: 0.5rem; align-items: center; flex-shrink: 0; }
.report-row__acts .btn { padding: 0.4rem 1rem; }

table.pivot { width: 100%; border-collapse: collapse; font-size: 0.78rem; margin: 1.5rem 0 0.5rem; }
table.pivot th, table.pivot td { padding: 0.4rem 0.5rem; border-bottom: 1px solid var(--rule); }
table.pivot thead th { font-family: var(--mono); font-size: 0.66rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; color: var(--ink-faint); background: var(--paper-warm); border-bottom: 1px solid var(--rule); }
table.pivot tbody th, table.pivot tfoot th { text-align: left; font-weight: 400; font-size: 0.8rem; }
table.pivot tfoot th, table.pivot tfoot td { font-weight: 700; border-top: 2px solid var(--ink); border-bottom: none; }
table.pivot .num { text-align: right; font-family: var(--mono); font-size: 0.74rem; white-space: nowrap; }
table.pivot .total { color: var(--ink); font-weight: 700; border-left: 1px solid var(--rule); }
table.pivot tbody tr:hover { background: var(--paper-warm); }
.table-note { font-size: 0.75rem; color: var(--ink-faint); margin-top: 0.5rem; }
.table-acts { display: flex; gap: 0.6rem; align-items: center; margin-top: 1.25rem; }

.pubs { font-size: 0.82rem; color: var(--ink-light); }
.pubs span { white-space: nowrap; }

.callout { border-left: 3px solid var(--accent); padding: 0.2rem 0 0.2rem 1.25rem; margin: 1.5rem 0; font-size: 0.9rem; color: var(--ink-light); }
.colophon { margin: 3.5rem 0 2rem; padding: 1.25rem 1.5rem; background: var(--paper-warm); border: 1px solid var(--rule); font-size: 0.8rem; }
.colophon dl { display: grid; grid-template-columns: 9rem 1fr; gap: 0.3rem 1rem; margin: 0.5rem 0 0; }
.colophon dt { font-family: var(--mono); font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.07em; color: var(--ink-faint); }
.colophon dd { margin: 0; }

.dt-title { font-family: var(--display); font-weight: 700; font-size: 0.95rem; }
.dt-rows { font-family: var(--mono); font-size: 0.7rem; color: var(--ink-faint); }
table.data-table td.num { text-align: right; }
table.data-table td.wrapcell { min-width: 32rem; white-space: normal; }
table.data-table td { white-space: nowrap; }
@media (max-width: 720px) {
  .report-row { flex-direction: column; align-items: flex-start; }
}
"""

CHROME = """  <header class="site-header">
    <div class="site-header__inner">
      <a href="https://data-landscapers.com/" class="site-logo">
        <img src="../build/assets/logo.png" alt="Data Landscapers" class="site-logo__img">
        <span class="site-logo__text">Data Landscapers
          <span class="site-logo__sub">Mapping Africa&rsquo;s data landscape</span>
        </span>
      </a>
      <nav class="site-nav" aria-label="Main navigation">
        <a href="{base}/" class="active">Corpus</a>
        <a href="https://data-landscapers.com/writing/">Writing</a>
        <a href="https://data-landscapers.com/lab/">Lab</a>
        <a href="https://data-landscapers.com/portfolio/">Portfolio</a>
        <a href="https://data-landscapers.com/about/">About</a>
        <a href="https://data-landscapers.com/contact/">Contact</a>
        <a href="https://data-landscapers.com/search/">Search</a>
      </nav>
    </div>
  </header>

  <nav class="corpus-nav" aria-label="Corpus navigation">
    <div class="corpus-nav__inner">
      <a href="{base}/countries/" class="active">Countries</a>
      <a href="{base}/regions/">Regions</a>
      <a href="{base}/topics/">Topics</a>
      <a href="{base}/finance/">Finance</a>
      <a href="{base}/catalogue/">Catalogue</a>
      <a href="{base}/method/">Method</a>
    </div>
  </nav>"""

FOOT = """  <footer class="site-footer">
    <div class="site-footer__inner">
      <p class="site-footer__copy"><a href="https://creativecommons.org/licenses/by/4.0/" style="color:inherit;border-bottom:none;">CC BY 4.0</a> 2026 Bill Anderson / Data Landscapers Ltd &nbsp;·&nbsp; Registered in the UK · Co. No. 16040544</p>
      <div class="site-footer__links">
        <a href="https://data-landscapers.com/">data-landscapers.com</a>
        <a href="{base}/method/">Method</a>
        <a href="{base}/manifest.csv">Manifest</a>
      </div>
    </div>
  </footer>"""


COUNTRY = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — Data Landscapers</title>
<meta name="description" content="{name}: digital transformation and data governance. Reports, sources and non-state finance, from the Data Landscapers base.">
<link rel="stylesheet" href="../site/assets/css/main.css">
<style>/* Mock-up only — moves to site/assets/css/country.css when the build lands. */{css}</style>
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container">

    <div class="country-head">
      <h1>{name}</h1>
      <div class="country-head__meta">{iso} &nbsp;·&nbsp; page built {built} &nbsp;·&nbsp; base at commit {commit}</div>
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

    <h2 class="section-heading">Sources</h2>
    <p>The base holds <strong>{sources} records</strong> for {name}, of {cat_total} in all. The catalogue is metadata &mdash; title, publisher, date, facets and the publisher&rsquo;s own link &mdash; never the source body. Every figure in the reports above resolves to one of these records.</p>
    <p class="pubs">Most frequent publishers: {publishers}</p>
    <div class="table-acts">
      <a class="btn" href="catalogue-prototype.html#places={iso}">Browse {name} in the catalogue &rarr;</a>
      <a class="btn" href="../upstream/catalogue/raw-catalogue.csv" download>&darr; Catalogue CSV</a>
    </div>

    <h2 class="section-heading">Non-state finance</h2>
    <p>Commitments to {name}&rsquo;s digital sector from financiers other than the state &mdash; development finance, foundations, vendors and operators. Figures are the amount announced, in the year announced, converted from the announcing party&rsquo;s own currency at a dated rate. They are commitments, not disbursements, and a multi-year commitment sits wholly in its start year.</p>

{pivot}
    <p class="table-note">US$m committed, by sector and year of commitment. &lsquo;-{cutoff}&rsquo; aggregates every year before {cutoff}. An empty cell is a year with no commitment recorded, not a zero.</p>

    <div class="table-acts">
      <a class="btn" href="finance-{iso}.html">Full table &mdash; {fin_n} commitments, all {ncols} fields &rarr;</a>
      <a class="btn btn--accent" href="../upstream/non-state-finance/{iso}-nonstate.csv" download>&darr; Download CSV</a>
    </div>

    <div class="callout">
      Vault access, source bodies included, is granted on request. <a href="{base}/method/">How this base is built &rarr;</a>
    </div>

    <div class="colophon">
      <strong>About this page</strong>
      <dl>
        <dt>Built</dt><dd class="mono">{built}</dd>
        <dt>Derived from</dt><dd>Data Landscapers source base, commit <code>{commit}</code></dd>
        <dt>Verify</dt><dd>Hash any file above and look it up in <a href="{base}/manifest.csv">manifest.csv</a></dd>
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
<link rel="stylesheet" href="../site/assets/css/main.css">
<style>/* Mock-up only. */{css}</style>
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container container--wide">

    <div class="country-head">
      <div class="crumb"><a href="{base}/countries/">Countries</a> &nbsp;/&nbsp; <a href="country-{iso}.html">{name}</a> &nbsp;/&nbsp; Non-state finance</div>
      <h1>Non-state finance</h1>
      <div class="country-head__meta">{name} &nbsp;·&nbsp; {fin_n} commitments &nbsp;·&nbsp; US${fin_total}m &nbsp;·&nbsp; {y0}&ndash;{y1} &nbsp;·&nbsp; base at commit {commit}</div>
    </div>

    <p>Every non-state commitment the base holds for {name}, every field, exactly as the CSV carries it. One row per commitment; each is tagged to one country only, so per-country totals sum without double-counting. The <code>url</code> column is the publisher&rsquo;s own link to the source the row was read from.</p>

    <div class="data-table-wrap">
      <div class="data-table-controls">
        <span class="dt-title">{name} &mdash; non-state finance</span>
        <input type="search" id="q" placeholder="Search&hellip;" aria-label="Search the table">
        <span class="data-table-count" id="count">{fin_n} rows</span>
        <a class="btn" href="../upstream/non-state-finance/{iso}-nonstate.csv" download style="padding:0.35rem 0.9rem;">&darr; Download CSV</a>
        <a class="btn" href="{iso}-nonstate-fields.csv" download style="padding:0.35rem 0.9rem;">&darr; Download metadata</a>
      </div>
      <div class="data-table-scroll">
        <table class="data-table" id="fin">
          <thead><tr>{head}</tr></thead>
          <tbody>
{rows}
          </tbody>
        </table>
      </div>
    </div>

    <div class="colophon">
      <strong>About this table</strong>
      <dl>
        <dt>Built</dt><dd class="mono">{built}</dd>
        <dt>Source</dt><dd><code>outputs/non-state-finance/{iso}-nonstate.csv</code>, compiled by the finance pass</dd>
        <dt>Derived from</dt><dd>Data Landscapers source base, commit <code>{commit}</code></dd>
        <dt>Fields</dt><dd><a href="{iso}-nonstate-fields.csv">{iso}-nonstate-fields.csv</a> &mdash; what each column means</dd>
        <dt>Licence</dt><dd><a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></dd>
      </dl>
    </div>

  </div>
  </main>

{foot}

</div>

<script>
(function () {{
  var tbody = document.querySelector('#fin tbody');
  var rows = Array.prototype.slice.call(tbody.rows);
  var q = document.getElementById('q'), count = document.getElementById('count');
  var total = rows.length;

  q.addEventListener('input', function () {{
    var term = q.value.toLowerCase(), shown = 0;
    rows.forEach(function (r) {{
      var ok = !term || r.textContent.toLowerCase().indexOf(term) > -1;
      r.style.display = ok ? '' : 'none';
      if (ok) shown++;
    }});
    count.textContent = (term ? shown + ' of ' + total : total) + ' rows';
  }});

  var dir = {{}};
  document.querySelectorAll('#fin thead th').forEach(function (th, i) {{
    th.addEventListener('click', function () {{
      dir[i] = !dir[i];
      var s = dir[i] ? 1 : -1, num = th.dataset.sort === 'num';
      rows.sort(function (a, b) {{
        var x = a.cells[i].textContent.trim(), y = b.cells[i].textContent.trim();
        if (num) {{
          var nx = parseFloat(x) , ny = parseFloat(y);
          return ((isNaN(nx) ? -Infinity : nx) - (isNaN(ny) ? -Infinity : ny)) * s;
        }}
        return x.localeCompare(y) * s;
      }});
      rows.forEach(function (r) {{ tbody.appendChild(r); }});
      document.querySelectorAll('#fin thead th').forEach(function (o) {{
        o.classList.remove('sort-asc', 'sort-desc');
      }});
      th.classList.add(dir[i] ? 'sort-asc' : 'sort-desc');
    }});
  }});
}})();
</script>
</body>
</html>
"""


def build(iso: str) -> list[Path]:
    name, region = NAMES.get(iso, iso), REGION.get(iso, "")
    meta = frontmatter((UPSTREAM / "reports" / iso / f"{iso}-status.md")
                       .read_text(encoding="utf-8"))
    fin = finance(iso)
    cols = list(fin[0].keys())
    ys = [int(r["start_year"]) for r in fin if r.get("start_year")]
    amounts = [float(r["commitment_usd_m"]) for r in fin if r.get("commitment_usd_m")]
    n_place, n_all, pubs = catalogue(iso)

    common = dict(
        base=SITE_BASE, iso=iso, name=name, region=region, css=PAGE_CSS,
        chrome=CHROME.format(base=SITE_BASE), foot=FOOT.format(base=SITE_BASE),
        built=date.today().isoformat(), commit=built_from()[:12],
        fin_n=len(fin), fin_total=f"{sum(amounts):,.0f}",
        financiers=len({r["financier"] for r in fin}),
        y0=min(ys), y1=max(ys), cutoff=FINANCE_CUTOFF,
    )

    (OUT / f"country-{iso}.html").write_text(COUNTRY.format(
        tracked=meta.get("ledger_rows", "&mdash;"),
        not_held=meta.get("not_held", "&mdash;"),
        sources=f"{n_place:,}", cat_total=f"{n_all:,}",
        publishers=", ".join(f"<span>{e(p)} ({c})</span>" for p, c in pubs),
        reports=report_rows(editions(iso), iso),
        pivot=pivot(fin), ncols=len(cols),
        **common), encoding="utf-8")

    numeric = ("commitment_usd_m", "start_year", "end_year")
    head = "".join(
        "<th{}>{} &#8597;</th>".format(
            ' data-sort="num"' if c in numeric else "",
            c.replace("_", "_<wbr>"))
        for c in cols)
    (OUT / f"finance-{iso}.html").write_text(FINANCE.format(
        head=head,
        rows=full_rows(sorted(fin, key=lambda r: r.get("start_year", ""), reverse=True), cols),
        **common), encoding="utf-8")

    with open(OUT / f"{iso}-nonstate-fields.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["field", "definition", "defined_in"])
        known = {f[0] for f in FIELDS}
        w.writerows([f for f in FIELDS if f[0] in cols]
                    + [[c, "", "not documented"] for c in cols if c not in known])

    return [OUT / f"country-{iso}.html", OUT / f"finance-{iso}.html",
            OUT / f"{iso}-nonstate-fields.csv"]


if __name__ == "__main__":
    for p in build(sys.argv[1] if len(sys.argv) > 1 else "KEN"):
        print(p)
