#!/usr/bin/env python3
"""datasets.py — the Datasets section.

    python scripts/datasets.py
      -> site/datasets/index.html                             the index
      -> site/datasets/data-centres/index.html                the Data Centres table
      -> site/datasets/data-centres/data-centres-{edition}.csv   the download, a dated edition (§9)
      -> site/metadata/data-centres-metadata.csv              its field dictionary, undated
      -> site/datasets/metadata/index.html                    every dataset's field dictionary

**One metadata page for every dataset** *(Bill, 2026-09-21)*. The field dictionaries used to
sit at the foot of Methodology's process lookups, beside the vocabularies. They describe the
downloads, so they now live under Datasets, drawn from `content/datasets-metadata.md` by the
same `lookup_tables` the lookups page uses. Each dataset's Metadata button links its section.

**A dataset here is maintained, not compiled** (documentation/datasets.md). The master in
`outputs/datasets/{name}/` is edited record by record, and every edit is logged in
`logs/dataset-updates.csv`. This script only publishes: it cuts an edition when the master's bytes
move, and shows the latest changes from the log under the table.

The index lists the downloadable tables that already exist elsewhere on the site as well, Finance
and the Catalogue, so that it is not a page with one entry. Those pages keep their own URLs.

**The prose is in `content/datasets.md`**, not here (RENDER.md -> *The prose*).
"""
from __future__ import annotations
import csv, html, io, json, shutil, sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import datasets_lib as dl  # noqa: E402
import editions  # noqa: E402  - one implementation of the edition grammar (§9)
from copy_lib import copy, copy_md  # noqa: E402
import structured_data  # noqa: E402
from chrome_lib import chrome, external_links, feedback, foot, ga, script, styles  # noqa: E402
import methodology  # noqa: E402  - the table directive and the page shell, one copy

CORPUS = Path(__file__).resolve().parent.parent
SITE = CORPUS / "site"
OUT = SITE / "datasets"
SITE_BASE = "https://corpus.data-landscapers.io"
MAIN_SITE = "https://data-landscapers.io"
NAME = "data-centres"
METADATA_CSV = f"{NAME}-metadata.csv"
RECENT = 10        # log rows shown under the table

# The columns the table shows, and those the row panel adds. Everything else is in the CSV and
# searchable; twelve is what fits the page before the widths stop being readable.
COLS = ("country", "facility_name", "city", "operational_status", "year_operational", "facility_type",
        "operator_name", "ultimate_parent_company", "control_category", "it_capacity_mw",
        "hyperscaler_presence", "chinese_involvement")
FILTERS = ("country", "operational_status", "facility_type", "control_category", "ownership_type",
           "hyperscaler_presence", "chinese_involvement", "gpu_ai_capability")
NUMERIC = ("year_operational", "it_capacity_mw", "rack_capacity", "total_floor_space_sqm", "investment_usd")
DETAIL = ("services_offered", "govt_data_hosted", "ownership_type", "ownership_structure_type",
          "major_shareholders", "government_ownership_pct", "controlling_entities", "control_rationale",
          "dfi_involvement", "investment_usd", "recent_investments", "hyperscaler_relationships",
          "cloud_act_exposure", "chinese_entities", "data_residency_guarantee", "local_dp_compliance",
          "submarine_cable_access", "ixp_presence", "carrier_neutrality", "gpu_ai_capability",
          "security_certifications", "comments", "source_urls")
BADGES = {"control_category": {"African control": "green", "Joint African/foreign control": "blue",
                               "US control": "amber", "Other foreign control": "amber"}}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def notice() -> str:
    """The *still being finalised* notice, or nothing once its block is emptied."""
    text = copy("datasets", "data-centres-status").strip()
    return indent(f'<div class="callout">\n{text}\n</div>') if text else ""


def indent(block: str, spaces: int = 4) -> str:
    pad = " " * spaces
    return "\n".join(pad + ln if ln.strip() else ln for ln in block.splitlines())


def attr(obj) -> str:
    return html.escape(json.dumps(obj, ensure_ascii=False), quote=True)


def country_names() -> dict:
    with open(CORPUS / "lookups" / "countries.csv", encoding="utf-8-sig", newline="") as f:
        return {r["iso-3"]: r["country-name"] for r in csv.DictReader(f)}


ACTION_WORDS = {"add": "Added", "modify": "Updated", "retire": "Retired", "import": "Imported"}
CHANGES_HEADER = ["date", "facility_id", "facility_name", "change", "summary", "sources"]


def all_changes(name: str) -> list[dict]:
    if not dl.LOG.exists():
        return []
    with open(dl.LOG, encoding="utf-8", newline="") as f:
        return [r for r in csv.DictReader(f) if r["dataset"] == name]


def facility_names(name: str) -> dict:
    """ID -> name over live and retired rows, so a retirement still names what went."""
    return {r["facility_id"]: r["facility_name"] for r in list(dl.retired(name)) + dl.read(name)}


def said(r: dict) -> str:
    """What the page says a change was: its reader summary, or, for rows logged before summaries
    existed, the working note (not back-filled, Bill 2026-09-21)."""
    return (r.get("summary") or "").strip() or r["details"]


def changes_csv(rows: list[dict], names: dict) -> bytes:
    """The whole change log for the dataset, newest first, in the page's own terms."""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=CHANGES_HEADER, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({"date": r["date"], "facility_id": r["record"],
                    "facility_name": "All records" if r["record"] == "ALL" else names.get(r["record"], ""),
                    "change": ACTION_WORDS.get(r["action"], r["action"]), "summary": said(r),
                    "sources": r["sources"]})
    return buf.getvalue().encode("utf-8")


def changes_html(rows: list[dict], names: dict) -> str:
    if not rows:
        return "<p>No changes yet.</p>"
    out = ['<table class="data-table">', "  <thead><tr><th>Date</th><th>Facility</th><th>Change</th>"
           "<th>What changed</th></tr></thead>", "  <tbody>"]
    for r in rows[:RECENT]:
        rec = ("All records" if r["record"] == "ALL"
               else f'{html.escape(names.get(r["record"], ""))} <span class="mono">{html.escape(r["record"])}</span>')
        out.append(f'    <tr><td class="mono">{html.escape(r["date"])}</td><td>{rec}</td>'
                   f'<td>{ACTION_WORDS.get(r["action"], html.escape(r["action"]))}</td>'
                   f'<td>{html.escape(said(r))}</td></tr>')
    out += ["  </tbody>", "</table>"]
    return "\n".join(out)


def publish_metadata(name: str) -> Path:
    """The field dictionary beside the other two in `site/metadata/`, undated like them: it
    describes columns, not findings. A build product — the master is `outputs/datasets/`."""
    dst = SITE / "metadata" / f"{name}-metadata.csv"
    body = (dl.DATASETS / name / "metadata.csv").read_bytes().replace(b"\r\n", b"\n")
    if not dst.exists() or dst.read_bytes() != body:
        dst.write_bytes(body)
    return dst


def fields(name: str) -> list[dict]:
    # structured_data.fields_from reads the capitalised headers the older dictionaries use.
    return structured_data.fields_from([{"Column": m["column"], "Definition": m["definition"]}
                                        for m in dl.metadata(name)])


CHROME = chrome("datasets", depth=2)
CHROME_INDEX = chrome("datasets", depth=1)

DC_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Data centres in Africa — Data Landscapers</title>
<meta name="description" content="Data centres across Africa, operational, under construction or planned: who operates each one, who ultimately controls it, and which hyperscalers and Chinese firms are involved. Searchable and downloadable.">
<link rel="canonical" href="{base}/datasets/data-centres/">
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
      <div class="article-header__crumb"><a href="{base}/datasets/">Datasets</a></div>
      <h1 class="article-header__title">Data centres</h1>
    </header>

{status}

    <div class="byline">{facilities} facilities &nbsp;·&nbsp; {countries} countries &nbsp;·&nbsp; {operational} operational, {pipeline} under construction or planned</div>

{intro}

{table_note}

    <div class="dl-datatable"
      data-src="{csv_name}"
      data-cols="{cols}"
      data-filters="{filters}"
      data-numeric="{numeric}"
      data-labels="{labels}"
      data-badges="{badges}"
      data-detail="{detail}"
      data-sort="country:asc"
      data-empty="No facility matches those filters.">
      <div class="dt-controls">
        <span class="dt-title">Africa &mdash; data centres</span>
        <span class="dt-count">{facilities} rows</span>
        <a class="btn btn--sm" href="{csv_name}" download>&darr; CSV</a>
        <a class="btn btn--sm" href="../metadata/#data-centres">Metadata</a>
      </div>
      <noscript>
        <p>The table is drawn in the browser from <a href="{csv_name}">{csv_name}</a>. With JavaScript off, download that file. It holds the same data, every row and every field.</p>
      </noscript>
    </div>

    <div class="colophon">
      <strong>About this table</strong>
      <dl>
        <dt>Built</dt><dd class="mono">{built}</dd>
        <dt>Edition</dt><dd class="mono">{edition}</dd>
        <dt>This file</dt><dd><a href="{csv_name}">{csv_name}</a> &mdash; a dated edition, kept as published and never revised</dd>
        <dt>Fields</dt><dd><a href="../metadata/#data-centres">What each column means</a>, its allowed values, and how the derived columns are worked out &mdash; also as <a href="../../metadata/{metadata}">{metadata}</a></dd>
        <dt>Changes</dt><dd>Every addition and correction is logged, with its sources. The latest are below; all of them are in <a href="{changes_csv}">{changes_csv}</a></dd>
        <dt>Licence</dt><dd><a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></dd>
      </dl>
    </div>

    <h2 class="section-heading" id="changes">Recent changes</h2>
    <p class="table-note">The latest {recent} of {n_changes} change{changes_s}. <a class="btn btn--sm" href="{changes_csv}" download>&darr; All changes (CSV)</a></p>

{changes}

  </div>
  </main>

{foot}

</div>
{datatable}
<script>
/* The table is drawn after load and is tens of thousands of pixels tall, so a jump to an anchor
   below it (#changes) lands before the table exists and is then pushed off screen. Re-seat the
   anchor as the table grows, until the reader scrolls for themselves or five seconds pass. */
(function () {{
  var t = document.querySelector('.dl-datatable');
  if (!t || !window.ResizeObserver) return;
  var ro = new ResizeObserver(function () {{
    var h = location.hash && document.getElementById(location.hash.slice(1));
    if (h && (t.compareDocumentPosition(h) & Node.DOCUMENT_POSITION_FOLLOWING)) h.scrollIntoView();
  }});
  ro.observe(t);
  function stop() {{ ro.disconnect(); }}
  ['wheel', 'touchstart', 'keydown'].forEach(function (e) {{ addEventListener(e, stop, {{ once: true, passive: true }}); }});
  addEventListener('hashchange', function () {{ var h = document.getElementById(location.hash.slice(1)); if (h) h.scrollIntoView(); }});
  setTimeout(stop, 5000);
}})();
</script>
</body>
</html>
"""

INDEX_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Datasets — Data Landscapers</title>
<meta name="description" content="Downloadable datasets on Africa's digital transformation: data centres, non-state finance, and the catalogue of every source we hold.">
<link rel="canonical" href="{base}/datasets/">
{styles}
<link rel="icon" href="{main}/assets/favicon.svg" type="image/svg+xml">
{ga}
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container">

    <header class="article-header">
      {feedback}
      <h1 class="article-header__title">Datasets</h1>
    </header>

{intro}

    <h2 class="section-heading"><a href="../finance/">Finance</a></h2>
{finance}

    <h2 class="section-heading"><a href="data-centres/">Data centres</a></h2>
    <div class="byline">{facilities} facilities &nbsp;·&nbsp; {countries} countries &nbsp;·&nbsp; edition {edition}</div>
{dc}
{status}

    <h2 class="section-heading"><a href="../catalogue/">Catalogue</a></h2>
{catalogue}

    <h2 class="section-heading"><a href="metadata/">Metadata</a></h2>
{metadata}

  </div>
  </main>

{foot}

</div>
</body>
</html>
"""


def dc_dataset(rows, csv_name, edition, n_countries) -> str:
    return structured_data.dataset(
        name="Data Landscapers data centres — Africa",
        description=copy_md("datasets", "dataset-data-centres"),
        url=f"{SITE_BASE}/datasets/data-centres/",
        csv_url=f"{SITE_BASE}/datasets/data-centres/{csv_name}",
        csv_bytes=structured_data.bytes_of(OUT / NAME / csv_name),
        records=len(rows),
        fields=fields(NAME),
        entity={"@type": "Place", "name": "Africa"},
        modified=edition or None,
        version=edition or None,
        extra_keywords=("Data centres", "Digital infrastructure", "Data sovereignty"))


def build_metadata() -> None:
    """`/datasets/metadata/`: each field dictionary as a table with its CSV, through Methodology's
    page shell so the tables look the same wherever the site prints one."""
    src = CORPUS / "content" / "datasets-metadata.md"
    out = OUT / "metadata"
    out.mkdir(parents=True, exist_ok=True)
    text = methodology.lookup_tables(src.read_text(encoding="utf-8"), out)
    canonical = f"{SITE_BASE}/datasets/metadata/"
    (out / "index.html").write_text(external_links(methodology.PAGE.format(
        feedback=feedback("Datasets — metadata", canonical),
        h1="Metadata", title="Datasets — metadata",
        description="What each column in the Data Landscapers datasets means: data centres, "
                    "non-state finance and the catalogue.",
        canonical=canonical, base=SITE_BASE, main=MAIN_SITE, body_class="",
        chrome=chrome("datasets", depth=2), foot=foot(depth=2),
        styles=styles(2, "methodology.css"), ga=ga(),
        body=methodology.indent(methodology.contents_strip(src) + methodology.convert(src, text)),
        source=src.relative_to(CORPUS).as_posix(), built=date.today().isoformat(),
    )), encoding="utf-8")


def main() -> int:
    rows = dl.read(NAME)
    names = country_names()
    out = OUT / NAME
    out.mkdir(parents=True, exist_ok=True)
    publish_metadata(NAME)
    build_metadata()

    # Published before the page, which links it by name (finance.py sets out why, and why LF).
    body = dl.master_path(NAME).read_bytes().replace(b"\r\n", b"\n")
    page = out / "index.html"
    csv_path, _ = editions.publish(body, out, NAME, ".csv", page=page)
    edition = editions.edition_of(csv_path.stem) or ""
    artefacts = editions.artefact_meta(NAME, edition, editions.digest(body))
    # The change log as a download, a dated edition like the table: it only ever grows, and a
    # file a reader may cite is not revised in place (§9).
    changes, fnames = all_changes(NAME), facility_names(NAME)
    cbody = changes_csv(changes, fnames)
    c_path, _ = editions.publish(cbody, out, f"{NAME}-changes", ".csv", page=page)
    artefacts += "\n" + editions.artefact_meta(f"{NAME}-changes", editions.edition_of(c_path.stem) or "",
                                               editions.digest(cbody))

    used = sorted({r["country"] for r in rows})
    status = [r["operational_status"] for r in rows]
    counts = dict(facilities=f"{len(rows):,}", countries=len(used),
                  operational=status.count("Operational"),
                  pipeline=status.count("Under construction") + status.count("Planned"))
    page.write_text(external_links(DC_PAGE.format(
        feedback=feedback("Data centres", f"{SITE_BASE}/datasets/data-centres/"),
        base=SITE_BASE, main=MAIN_SITE, chrome=CHROME, foot=foot(depth=2),
        styles=styles(2, "country.css", "datatable.css"), ga=ga(),
        datatable=script("datatable.js", 2), artefacts=artefacts,
        jsonld=dc_dataset(rows, csv_path.name, edition, len(used)),
        intro=indent(copy("datasets", "data-centres-intro")),
        table_note=indent(copy("datasets", "data-centres-table-note")),
        csv_name=csv_path.name, metadata=METADATA_CSV,
        cols=", ".join(COLS), filters=", ".join(FILTERS), numeric=", ".join(NUMERIC),
        detail=", ".join(DETAIL), badges=attr(BADGES),
        labels=attr({"country": {c: names.get(c, c) for c in used}}),
        changes=indent(changes_html(changes, fnames)), status=notice(),
        changes_csv=c_path.name, recent=min(RECENT, len(changes)), n_changes=f"{len(changes):,}", changes_s="" if len(changes) == 1 else "s",
        built=date.today().isoformat(), edition=edition, **counts)), encoding="utf-8")

    (OUT / "index.html").write_text(external_links(INDEX_PAGE.format(
        feedback=feedback("Datasets", f"{SITE_BASE}/datasets/"),
        base=SITE_BASE, main=MAIN_SITE, chrome=CHROME_INDEX, foot=foot(depth=1),
        styles=styles(1, "country.css"), ga=ga(), status=notice(),
        intro=indent(copy("datasets", "index-intro")),
        dc=indent(copy("datasets", "index-data-centres")),
        finance=indent(copy("datasets", "index-finance")),
        catalogue=indent(copy("datasets", "index-catalogue")),
        metadata=indent(copy("datasets", "index-metadata")),
        edition=edition, **counts)), encoding="utf-8")
    print(f"datasets: {NAME} {len(rows)} rows, edition {edition} -> site/datasets/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
