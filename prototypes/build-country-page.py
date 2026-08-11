#!/usr/bin/env python3
"""build-country-page.py — mock-up of the country page (DESIGN.md §3).

Generates `prototypes/country-KEN.html` from `upstream/` alone. Nothing on the
page is typed by hand: the position statement is lifted from the status
report's own summary narrative, the counts come from the report frontmatter and
the catalogue, the report rows come from the filenames in `site/reports/{ISO3}/`,
and the finance table is `{ISO3}-nonstate.csv` rendered as rows.

    python prototypes/build-country-page.py KEN

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
from datetime import date
from pathlib import Path

import markdown

CORPUS = Path(__file__).resolve().parent.parent
UPSTREAM = CORPUS / "upstream"
SITE = CORPUS / "site"
OUT = CORPUS / "prototypes"

SITE_BASE = "https://corpus.data-landscapers.com"
NAMES = {"KEN": "Kenya"}

KIND = {
    "status": ("Status report", "Where every tracked system and instrument stands, dated."),
    "monthly": ("Monthly update", "What moved in the month, and only what moved."),
    "progress": ("Twelve-month progress report", "Position at each end of a year, and the movement between."),
}

csv.field_size_limit(10 ** 9)


# ── reading upstream ──────────────────────────────────────────────

def frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    head = text[3:text.find("\n---", 3)]
    return {k.strip(): v.strip() for k, v in
            (l.split(":", 1) for l in head.splitlines() if ":" in l)}


def narrative(text: str, key: str = "summary") -> str:
    m = re.search(rf"<!-- narrative: {key} -->\n(.*?)\n<!-- /narrative -->", text, re.S)
    return markdown.markdown(m.group(1)) if m else ""


def editions(iso: str) -> list[dict]:
    """The published editions, read off the rendered filenames.

    `{ISO3}-{kind}[-{period}]-{edition}.html` — the edition is always the last
    dated field, so the period survives in the middle for the two reports that
    carry one. Only the newest edition of each kind is offered; the rest are
    behind the quiet 'earlier editions' affordance (§1).
    """
    found: dict[str, list[tuple[str, str, str]]] = {}
    for f in sorted((SITE / "reports" / iso).glob(f"{iso}-*.html")):
        parts = f.stem.split("-")
        kind, edition = parts[1], "-".join(parts[-3:])
        period = "-".join(parts[2:-3])
        found.setdefault(kind, []).append((edition, period, f.name))
    rows = []
    for kind in ("status", "monthly", "progress"):
        if kind not in found:
            continue
        eds = sorted(found[kind], reverse=True)
        edition, period, name = eds[0]
        rows.append({
            "kind": kind, "label": KIND[kind][0], "blurb": KIND[kind][1],
            "edition": edition, "period": period,
            "html": name, "pdf": name[:-5] + ".pdf",
            "earlier": len(eds) - 1,
        })
    return rows


def report_meta(iso: str, kind: str) -> dict:
    for f in (UPSTREAM / "reports" / iso).glob(f"{iso}-{kind}*.md"):
        return frontmatter(f.read_text(encoding="utf-8"))
    return {}


def catalogue_count(iso: str) -> int:
    n = 0
    with open(UPSTREAM / "catalogue" / "raw-catalogue.csv", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            if iso in (row.get("places") or ""):
                n += 1
    return n


def finance(iso: str) -> list[dict]:
    f = UPSTREAM / "non-state-finance" / f"{iso}-nonstate.csv"
    with open(f, encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def built_from() -> str:
    return (UPSTREAM / "BUILT-FROM").read_text(encoding="utf-8").strip()


# ── rendering ─────────────────────────────────────────────────────

def e(s: str) -> str:
    return html.escape(s or "")


def money(v: str) -> str:
    if not v:
        return '<span class="unstated">not stated</span>'
    f = float(v)
    return f"{f:,.0f}" if f == int(f) else f"{f:,.1f}"


def years(r: dict) -> str:
    a, b = r.get("start_year", ""), r.get("end_year", "")
    return f"{a}&ndash;{b}" if b and b != a else (a or "&mdash;")


def finance_rows(rows: list[dict]) -> str:
    out = []
    for r in rows:
        url = r.get("url", "")
        title = e(r.get("title", ""))
        link = f'<a href="{e(url)}">{title}</a>' if url else title
        out.append(
            "<tr>"
            f'<td class="mono nowrap">{years(r)}</td>'
            f'<td>{e(r.get("financier"))}</td>'
            f'<td>{e(r.get("sector"))}</td>'
            f'<td class="mono num">{money(r.get("commitment_usd_m"))}</td>'
            f'<td class="mono">{e(r.get("amount_basis"))}</td>'
            f'<td>{link}</td>'
            "</tr>"
        )
    return "\n".join(out)


MONTHS = ("January February March April May June July August September "
          "October November December").split()


def period_label(kind: str, period: str) -> str:
    """`2026-07-01 to 2026-08-05` reads as a range on a progress report and as
    noise on a monthly one, where the month is the point."""
    if not period:
        return ""
    if kind == "monthly":
        y, m, _ = period.split(" ")[0].split("-")
        return f"{MONTHS[int(m) - 1]} {y}"
    return period.replace(" to ", " &ndash; ")


def report_cards(rows: list[dict], iso: str) -> str:
    out = []
    for r in rows:
        meta = report_meta(iso, r["kind"])
        counts = ""
        if meta.get("ledger_rows"):
            counts = (f'{meta["ledger_rows"]} tracked'
                      + (f', <span class="nh">{meta["not_held"]} not held</span>'
                         if meta.get("not_held") else ""))
        # The period comes from the report's frontmatter, not from the
        # filename: a progress report is named for the month it was cut in
        # but covers the twelve months before it, and the filename cannot say so.
        label = period_label(r["kind"], meta.get("period", ""))
        period = f' &nbsp;·&nbsp; {label}' if label else ""
        earlier = (f'<a class="quiet" href="#">{r["earlier"]} earlier edition'
                   f'{"s" if r["earlier"] > 1 else ""}</a>' if r["earlier"] else "")
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
          {earlier}
        </div>
      </div>""")
    return "\n".join(out)


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — Data Landscapers</title>
<meta name="description" content="{name}: digital transformation and data governance. Reports, non-state finance and sources, from the Data Landscapers base.">
<link rel="stylesheet" href="../site/assets/css/main.css">
<style>
/* Mock-up only — moves to site/assets/css/country.css when the build lands. */
.country-head {{ border-bottom: 1px solid var(--rule); padding-bottom: 1.5rem; margin-bottom: 2rem; }}
.crumb {{ font-family: var(--mono); font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.09em; color: var(--ink-faint); margin-bottom: 0.6rem; }}
.crumb a {{ color: var(--ink-faint); }}
.country-head h1 {{ font-size: 3rem; margin-bottom: 0.35rem; }}
.country-head__meta {{ font-family: var(--mono); font-size: 0.72rem; color: var(--ink-faint); letter-spacing: 0.03em; }}

.counts {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: var(--rule); border: 1px solid var(--rule); margin: 0 0 2.5rem; }}
.count {{ background: var(--paper); padding: 1rem 1.1rem; }}
.count__n {{ font-family: var(--display); font-size: 1.9rem; font-weight: 700; line-height: 1.1; }}
.count__n--red {{ color: var(--accent); }}
.count__l {{ font-family: var(--mono); font-size: 0.64rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--ink-faint); margin-top: 0.25rem; }}
.count__s {{ font-size: 0.78rem; color: var(--ink-light); margin-top: 0.3rem; line-height: 1.4; }}

.section-label {{ font-family: var(--mono); font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--ink-faint); border-top: 2px solid var(--ink); padding-top: 0.6rem; margin: 3rem 0 1rem; }}
.position p {{ font-size: 1.06rem; line-height: 1.8; }}
.provenance {{ font-size: 0.8rem; color: var(--ink-faint); font-style: italic; margin-top: -0.5rem; }}

.report-row {{ display: flex; gap: 1.5rem; align-items: center; justify-content: space-between; padding: 1.1rem 0; border-bottom: 1px solid var(--rule); }}
.report-row:first-of-type {{ border-top: 1px solid var(--rule); }}
.report-row__kind {{ font-family: var(--display); font-weight: 700; font-size: 1.12rem; }}
.report-row__blurb {{ font-size: 0.86rem; color: var(--ink-light); margin-top: 0.1rem; }}
.report-row__meta {{ font-family: var(--serif); font-size: 0.75rem; color: var(--ink-faint); margin-top: 0.4rem; }}
.report-row__meta .nh {{ color: var(--accent); }}
.report-row__acts {{ display: flex; gap: 0.5rem; align-items: center; flex-shrink: 0; }}
.report-row__acts .btn {{ padding: 0.4rem 1rem; }}
a.quiet {{ font-size: 0.72rem; color: var(--ink-faint); border-bottom: 1px dotted var(--rule); }}

table.data-table td.num {{ text-align: right; }}
table.data-table td.nowrap {{ white-space: nowrap; }}
.unstated {{ color: var(--ink-faint); font-style: italic; }}
.table-foot {{ display: flex; justify-content: space-between; align-items: center; gap: 1rem; padding: 0.75rem 1rem; border-top: 1px solid var(--rule); background: var(--paper-warm); font-size: 0.75rem; color: var(--ink-faint); }}

.callout {{ border-left: 3px solid var(--accent); padding: 0.2rem 0 0.2rem 1.25rem; margin: 1.5rem 0; font-size: 0.9rem; color: var(--ink-light); }}
.colophon {{ margin: 3.5rem 0 2rem; padding: 1.25rem 1.5rem; background: var(--paper-warm); border: 1px solid var(--rule); font-size: 0.8rem; }}
.colophon dl {{ display: grid; grid-template-columns: 9rem 1fr; gap: 0.3rem 1rem; margin: 0.5rem 0 0; }}
.colophon dt {{ font-family: var(--mono); font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.07em; color: var(--ink-faint); }}
.colophon dd {{ margin: 0; }}
@media (max-width: 720px) {{
  .counts {{ grid-template-columns: repeat(2, 1fr); }}
  .report-row {{ flex-direction: column; align-items: flex-start; }}
}}
</style>
</head>
<body>
<div class="site-wrap">

  <header class="site-header">
    <div class="site-header__inner">
      <a href="{base}/" class="site-logo">
        <img src="../build/assets/logo.png" alt="Data Landscapers" class="site-logo__img">
        <span class="site-logo__text">Data Landscapers
          <span class="site-logo__sub">Mapping Africa&rsquo;s data landscape</span>
        </span>
      </a>
      <nav class="site-nav" aria-label="Main navigation">
        <a href="{base}/countries/" class="active">Countries</a>
        <a href="{base}/regions/">Regions</a>
        <a href="{base}/topics/">Topics</a>
        <a href="{base}/catalogue/">Catalogue</a>
        <a href="{base}/data/">Data</a>
        <a href="{base}/method/">Method</a>
      </nav>
    </div>
  </header>

  <main id="main">
  <div class="container">

    <div class="country-head">
      <div class="crumb"><a href="{base}/countries/">Countries</a> &nbsp;/&nbsp; Eastern Africa</div>
      <h1>{name}</h1>
      <div class="country-head__meta">{iso} &nbsp;·&nbsp; page built {built} &nbsp;·&nbsp; base at commit {commit}</div>
    </div>

    <div class="counts">
      <div class="count">
        <div class="count__n">{tracked}</div>
        <div class="count__l">Systems &amp; instruments</div>
        <div class="count__s">Tracked on {name}&rsquo;s ledger.</div>
      </div>
      <div class="count">
        <div class="count__n count__n--red">{not_held}</div>
        <div class="count__l">Not held</div>
        <div class="count__s">Gaps the base states rather than hides.</div>
      </div>
      <div class="count">
        <div class="count__n">{sources}</div>
        <div class="count__l">Sources held</div>
        <div class="count__s">Every figure is one click from one of them.</div>
      </div>
      <div class="count">
        <div class="count__n">{fin_n}</div>
        <div class="count__l">Non-state commitments</div>
        <div class="count__s">US${fin_total}m across {financiers} financiers, {y0}&ndash;{y1}.</div>
      </div>
    </div>

    <div class="section-label">Position</div>
    <div class="position">
{summary}
    </div>
    <p class="provenance">Summary of position, from the status report of {status_edition}. Compiled, not written for this page.</p>

    <div class="section-label">Reports</div>
{reports}

    <div class="section-label">Non-state finance</div>
    <p>Commitments to {name}&rsquo;s digital sector from financiers other than the state &mdash; development finance, foundations, vendors and operators. One row per commitment, each linked to the record it was read from. Figures are the amount announced, in the currency announced, converted at a dated rate; they are not disbursements.</p>

    <div class="data-table-wrap">
      <div class="data-table-controls">
        <input type="search" id="q" placeholder="Search financier, sector, title&hellip;" aria-label="Search the table">
        <label for="sector">Sector</label>
        <select id="sector"><option value="">All</option>{sector_opts}</select>
        <span class="data-table-count" id="count">{fin_n} of {fin_n} rows</span>
      </div>
      <div class="data-table-scroll">
        <table class="data-table" id="fin">
          <thead><tr>
            <th data-sort="num">Years</th><th>Financier</th><th>Sector</th>
            <th data-sort="num">US$m</th><th>Basis</th><th>Commitment</th>
          </tr></thead>
          <tbody>
{fin_rows}
          </tbody>
        </table>
      </div>
      <div class="table-foot">
        <span>Full table, all columns &mdash; 20 fields including instrument, status, recipient organisation and original currency.</span>
        <a class="btn" href="../upstream/non-state-finance/{iso}-nonstate.csv" download>&darr; CSV</a>
      </div>
    </div>

    <div class="section-label">Sources</div>
    <p>The base holds <strong>{sources} records</strong> for {name}, of {cat_total} in all. The catalogue is metadata &mdash; title, publisher, date, facets and the publisher&rsquo;s own link &mdash; never the source body.</p>
    <p><a class="btn" href="catalogue-prototype.html#places={iso}">Browse {name} in the catalogue &rarr;</a></p>

    <div class="callout">
      Vault access, bodies included, is granted on request. <a href="{base}/method/">How this base is built &rarr;</a>
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

  <footer class="site-footer">
    <div class="site-footer__inner">
      <p class="site-footer__copy"><a href="https://creativecommons.org/licenses/by/4.0/" style="color:inherit;border-bottom:none;">CC BY 4.0</a> 2026 Bill Anderson / Data Landscapers Ltd &nbsp;·&nbsp; Registered in the UK · Co. No. 16040544</p>
      <div class="site-footer__links">
        <a href="https://data-landscapers.com/">data-landscapers.com</a>
        <a href="{base}/method/">Method</a>
        <a href="{base}/manifest.csv">Manifest</a>
      </div>
    </div>
  </footer>

</div>

<script>
// Mock-up behaviour: filter, search and sort in the page. The real build
// serves the same markup; this script is what the catalogue prototype already
// does, cut down to one table.
(function () {{
  var tbody = document.querySelector('#fin tbody');
  var rows = Array.prototype.slice.call(tbody.rows);
  var q = document.getElementById('q'), sector = document.getElementById('sector');
  var count = document.getElementById('count'), total = rows.length;

  function apply() {{
    var term = q.value.toLowerCase(), sec = sector.value, shown = 0;
    rows.forEach(function (r) {{
      var ok = (!sec || r.cells[2].textContent === sec) &&
               (!term || r.textContent.toLowerCase().indexOf(term) > -1);
      r.style.display = ok ? '' : 'none';
      if (ok) shown++;
    }});
    count.textContent = shown + ' of ' + total + ' rows';
  }}
  q.addEventListener('input', apply);
  sector.addEventListener('change', apply);

  var dir = {{}};
  document.querySelectorAll('#fin thead th').forEach(function (th, i) {{
    th.addEventListener('click', function () {{
      var num = th.dataset.sort === 'num';
      dir[i] = !dir[i];
      var s = dir[i] ? 1 : -1;
      rows.sort(function (a, b) {{
        var x = a.cells[i].textContent.trim(), y = b.cells[i].textContent.trim();
        if (num) return (parseFloat(x.replace(/[^0-9.]/g, '')) || 0) >
                        (parseFloat(y.replace(/[^0-9.]/g, '')) || 0) ? s : -s;
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


def build(iso: str) -> Path:
    name = NAMES.get(iso, iso)
    status_md = (UPSTREAM / "reports" / iso / f"{iso}-status.md").read_text(encoding="utf-8")
    meta = frontmatter(status_md)
    fin = finance(iso)
    ys = [int(r["start_year"]) for r in fin if r.get("start_year")]
    amounts = [float(r["commitment_usd_m"]) for r in fin if r.get("commitment_usd_m")]
    sectors = sorted({r.get("sector", "") for r in fin} - {""})
    n_cat = sum(1 for _ in csv.DictReader(
        open(UPSTREAM / "catalogue" / "raw-catalogue.csv", encoding="utf-8-sig")))

    doc = TEMPLATE.format(
        base=SITE_BASE, iso=iso, name=name,
        built=date.today().isoformat(), commit=built_from()[:12],
        tracked=meta.get("ledger_rows", "&mdash;"),
        not_held=meta.get("not_held", "&mdash;"),
        status_edition=meta.get("compiled", ""),
        sources=f"{catalogue_count(iso):,}", cat_total=f"{n_cat:,}",
        fin_n=len(fin), fin_total=f"{sum(amounts):,.0f}",
        financiers=len({r["financier"] for r in fin}),
        y0=min(ys), y1=max(ys),
        summary=narrative(status_md),
        reports=report_cards(editions(iso), iso),
        sector_opts="".join(f'<option>{e(s)}</option>' for s in sectors),
        fin_rows=finance_rows(sorted(fin, key=lambda r: r.get("start_year", ""), reverse=True)),
    )
    out = OUT / f"country-{iso}.html"
    out.write_text(doc, encoding="utf-8")
    return out


if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else "KEN"))
