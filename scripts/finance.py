#!/usr/bin/env python3
"""finance.py — the Finance page.

    python scripts/finance.py
      -> site/finance/index.html                   the page
      -> site/finance/all-nonstate-{edition}.csv   the full download, a dated edition (§9)
      -> site/finance/all-budgets-{edition}.csv    the same, for the domestic side

**One top-level page, two sections** *(Bill, 2026-08-19)*. Non-state finance, which
carries the whole cross-country table of commitments; and national budgets, which
from 2026-09-20 carries what the base holds of what states appropriate from their own
money (strategic review 4 R53 — it said for a year that nothing was published). It
replaces both the shell landing this file used to write and the separate `all.html`
the table briefly had — see `render()`.

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

The domestic-budget side is compiled per country into `outputs/budgets/{ISO3}-budget.csv`
and concatenated here into one published edition with `place` prepended. **It is not
aggregated and never will be by this script**: every row is in the announcing state's
own currency at whatever grain its budget document prints, so there is no total to
offer and the page says so. `{ISO3}-summary.csv` — which does carry US$m ball-park aggregates —
is still not read here, for the same reason.
"""
from __future__ import annotations
import csv, html, json, sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import editions  # noqa: E402  - one implementation of the edition grammar (§9)
from copy_lib import copy, copy_inline, copy_md  # noqa: E402
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


# ---------------------------------------------------------------- national budgets
BUDGET_DIR = OUTPUTS / "budgets"

# **What the budget download carries is narrower than what the compile holds**, on the
# precedent `design.md` set for the catalogue on 2026-09-09. `record` is a key into
# OSINT's tree and names a file only we hold. `doc_type` is populated on 197 of the 466
# budget-document lines and blank on the rest — a column mostly empty on the rows it
# belongs to tells a reader nothing and invites the inference that the source is unknown,
# when `doc_locator` names it on every one of them. Both stay in `outputs/`.
# `source_slug` joined them on 2026-09-20 (R54). It names the held document a Corpus
# extraction was read out of, which is a slug in OSINT's tree — and the published catalogue
# carries titles and URLs, never slugs, so publishing one here would be the first. What a
# reader needs is `doc_locator`, which names the page and table the figure is printed on in
# a document they can fetch themselves from the publisher.
BUDGET_DROP = ("record", "doc_type", "source_slug")

STAGES = ("proposed", "appropriated", "revised", "released", "actual", "audited")


def _fy_span(years: list[str]) -> str:
    """`2024, 2025, 2026` -> `2024–2026`, and the same for `2024/25 … 2026/27`.

    The column was the widest in the table and pushed Currency off the right edge of a
    1440px window. A run of consecutive years says the same thing as the list of them
    and says it in a quarter of the width; anything with a gap in it stays a list,
    because *2024, 2026* and *2024–2026* are different claims about what has been read."""
    if len(years) < 3:
        return ", ".join(years)
    heads = [int(y[:4]) for y in years]
    same_shape = len({len(y) for y in years}) == 1
    if same_shape and heads == list(range(heads[0], heads[0] + len(heads))):
        return f"{years[0]}–{years[-1]}"
    return ", ".join(years)


def _blank(v: str) -> bool:
    """A field the compile wrote as an em-dash is a stated absence, not a value.

    Records built from reporting leave `doc_locator` blank *by rule* (the driver: classification
    codes, scale and locator are left blank, not inferred) and several write the em-dash and a
    reason instead of nothing at all. Counting those as citations would have this page report
    475 traceable lines where it has 466."""
    v = (v or "").strip()
    return not v or v.startswith("—") or v in {"-", "n/a", "N/A"}


def load_budgets(names: dict) -> tuple[list[dict], bytes, dict]:
    """Per-country coverage, the combined table, and the counts for the byline.

    **Coverage is the publication, and the figures come with it** *(strategic review 4 R53)*.
    The section said for a year that nothing was published because a table of 26 countries
    side by side would be read as a comparison it cannot support. That is still true of the
    figures and is why every row carries its own currency and no total is offered anywhere:
    these are unconverted amounts at whatever grain each state's own budget document prints,
    and the byline counts the currencies on the run that wrote it rather than carrying a
    number here that will be wrong the first time a country is added. What changes is that
    stating the coverage per country is what makes the figures
    publishable rather than what has to happen before they are — a reader who can see that
    Ghana is two years of appropriations and South Africa is three years with an audited
    outturn is not going to read one against the other as like for like."""
    rows, out, cols = [], [], None
    for path in sorted(BUDGET_DIR.glob("*-budget.csv")):
        iso = path.name[:3]
        with open(path, encoding="utf-8-sig", newline="") as fh:
            rdr = csv.DictReader(fh)
            src = list(rdr)
            if cols is None:
                cols = ["place"] + [c for c in (rdr.fieldnames or []) if c not in BUDGET_DROP]
        if not src:
            continue
        for r in src:
            out.append({"place": iso, **{c: r.get(c, "") for c in cols if c != "place"}})
        fys = sorted({(r.get("fy") or "").strip() for r in src} - {""})
        years = sorted(f for f in fys if f[:4].isdigit())
        labels = [f for f in fys if not f[:4].isdigit()]
        scope = Counter((r.get("scope_confidence") or "").strip() for r in src)
        stages = [s for s in STAGES if any((r.get(s) or "").strip() for r in src)]
        rows.append({
            "place": iso,
            "name": names.get(iso, iso),
            "years": years,
            "fys": _fy_span(years) + (" + unstated" if labels else ""),
            "lines": len(src),
            "scope": " · ".join(f"{n} {k}" for k, n in scope.most_common() if k),
            "stages": " · ".join(stages) or "none stated",
            "currency": ", ".join(sorted({(r.get("currency") or "").strip() for r in src} - {""})),
            "cited": sum(1 for r in src if not _blank(r.get("doc_locator"))),
        })

    buf = []
    w = csv.writer(_Sink(buf), lineterminator="\n")
    w.writerow(cols or [])
    for r in out:
        w.writerow([r.get(c, "") for c in (cols or [])])
    body = "".join(buf).encode("utf-8-sig")

    yrs = [int(y[:4]) for r in rows for y in r["years"]]
    agg = {"countries": len(rows), "lines": len(out),
           "cited": sum(r["cited"] for r in rows),
           "currencies": len({c for r in rows for c in r["currency"].split(", ") if c}),
           "yr": f"FY{min(yrs)}–FY{max(yrs)}" if yrs else "n/a"}
    return rows, body, agg


class _Sink:
    """`csv.writer` wants a file; this collects the rows so the bytes can be hashed
    and handed to `editions.publish` without a temporary file on the way."""

    def __init__(self, buf: list):
        self.buf = buf

    def write(self, s: str) -> int:
        self.buf.append(s)
        return len(s)


def budget_table(rows: list[dict]) -> str:
    """The coverage table: one row per country, no money in it.

    Baked into the page rather than drawn by the datatable component, which is the
    opposite of the call one section up. Twenty-six rows by six columns is a few
    kilobytes of HTML and reads with JavaScript off; 494 rows of figures is the one
    below, and that is the table the component exists for."""
    body = "\n".join(
        f'        <tr><th scope="row">{html.escape(r["name"])} '
        f'<span class="mono">({r["place"]})</span></th>'
        f'<td>{html.escape(r["fys"])}</td>'
        f'<td class="num">{r["lines"]}</td>'
        f'<td>{html.escape(r["scope"])}</td>'
        f'<td>{html.escape(r["stages"])}</td>'
        f'<td class="mono">{html.escape(r["currency"])}</td></tr>'
        for r in rows)
    return f"""<div class="table-scroll"><table class="pivot">
        <thead><tr><th scope="col">Country</th><th scope="col">Fiscal years</th>
          <th scope="col" class="num">Lines</th><th scope="col">Scope</th>
          <th scope="col">Stages held</th><th scope="col">Currency</th></tr></thead>
        <tbody>
{body}
        </tbody>
      </table></div>"""


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
<meta name="description" content="Money committed to Africa's digital sector: every non-state commitment held in the Data Landscapers base, searchable and downloadable, plus every national budget line read out of a state budget document so far.">
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

{page_intro}

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
        <a class="btn btn--sm" href="../methodology/lookups/#non-state-finance-metadata">Metadata</a>
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
    <div class="byline">{b_countries} countries &nbsp;·&nbsp; {b_lines} budget lines &nbsp;·&nbsp; {b_currencies} currencies, unconverted &nbsp;·&nbsp; {b_yr}</div>

{budgets_intro}

{budget_coverage}

    <p class="table-note">{budget_coverage_note}</p>

{budgets_table_note}

    <div class="dl-datatable"
      data-src="{b_csv}"
      data-cols="place, fy, admin_head, programme, sub_programme, proposed, appropriated, revised, actual, audited, currency, scope_confidence, source_tier, doc_locator"
      data-filters="place, fy, current_stage, scope_confidence, source_tier, currency"
      data-numeric="proposed, appropriated, revised, released, actual, audited"
      data-labels="{b_labels}"
      data-detail="doc_locator"
      data-sort="place:asc"
      data-empty="No budget line matches those filters.">
      <div class="dt-controls">
        <span class="dt-title">Africa &mdash; national budget lines</span>
        <span class="dt-count">{b_lines} rows</span>
        <a class="btn btn--sm" href="{b_csv}" download>&darr; CSV</a>
      </div>
      <noscript>
        <p>The table is drawn in the browser from <a href="{b_csv}">{b_csv}</a>. With JavaScript off, download that file &mdash; it is the same data, every row and every field.</p>
      </noscript>
    </div>

    <div class="colophon">
      <strong>About this table</strong>
      <dl>
        <dt>Built</dt><dd class="mono">{built}</dd>
        <dt>Edition</dt><dd class="mono">{b_edition}</dd>
        <dt>This file</dt><dd><a href="{b_csv}">{b_csv}</a> &mdash; a dated edition, retained as published and never revised</dd>
        <dt>Source</dt><dd><code>outputs/budgets/{{ISO3}}-budget.csv</code>, compiled from the records each line rests on</dd>
        <dt>Amounts</dt><dd>In the state&rsquo;s own currency, as its budget document prints them, with no conversion and no total. A figure is an appropriation, a revision or an outturn &mdash; the columns say which</dd>
        <dt>Citation</dt><dd><code>doc_locator</code> names the page, table and line in the budget document the figure is printed in. It is blank on lines built from reporting, where the driver leaves it blank rather than inferring one</dd>
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
           artefacts: str = "", budgets: tuple | None = None) -> str:
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
    brows, bagg, b_csv, b_edition = budgets or ([], {}, "", "")
    b_used = {r["place"]: r["name"] for r in brows}
    b_labels = html.escape(json.dumps({"place": b_used}, ensure_ascii=False), quote=True)
    return PAGE.format(
        feedback=feedback("Finance", f"{SITE_BASE}/finance/"),
        base=SITE_BASE, main=MAIN_SITE, chrome=CHROME, foot=FOOT,
        styles=styles(1, "country.css", "datatable.css"), ga=ga(),
        datatable=script("datatable.js", 1),
        csv_name=csv_name, labels=labels, metadata=METADATA_CSV,
        artefacts=artefacts,
        page_intro=indent(copy("finance", "page-intro")),
        non_state_intro=indent(copy("finance", "non-state-intro")),
        table_note=indent(copy("finance", "non-state-table-note")),
        budgets_intro=indent(copy("finance", "budgets-intro")),
        budgets_table_note=indent(copy("finance", "budgets-table-note")),
        budget_coverage=indent(budget_table(brows)),
        budget_coverage_note=copy_inline("finance", "budgets-coverage-note"),
        b_countries=bagg.get("countries", 0), b_lines=f"{bagg.get('lines', 0):,}",
        b_currencies=bagg.get("currencies", 0), b_yr=bagg.get("yr", "n/a"),
        b_csv=b_csv, b_edition=b_edition, b_labels=b_labels,
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
    # The budget table publishes the same way and for the same reason (§9): a compiled
    # finding of ours that a reader may quote a figure out of, so it is dated, retained
    # and never revised, and the page links whichever edition `publish` settled on.
    brows, bbody, bagg = load_budgets(names)
    b_path, _ = editions.publish(bbody, out, "all-budgets", ".csv", page=page)
    b_edition = editions.edition_of(b_path.stem) or ""
    artefacts += editions.artefact_meta("all-budgets", b_edition, editions.digest(bbody))
    page.write_text(external_links(render(agg, names, csv_path.name, edition, artefacts,
                                          (brows, bagg, b_path.name, b_edition))),
                    encoding="utf-8")
    stale = out / "all.html"
    if stale.exists():                 # the table's own page, folded into index.html
        stale.unlink()
        print("  removed site/finance/all.html — the table is on the page itself now")
    print(f"finance: {agg['deals']:,} deals, US${agg['total_usd_m']:,.0f}m "
          f"-> site/finance/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
