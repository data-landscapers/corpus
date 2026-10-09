#!/usr/bin/env python3
"""maturity-site.py — the Maturity Assessment's map, country reports and methodology page.

    python scripts/maturity-site.py   -> site/maturity/index.html
                                         site/maturity/data/maturity.json, africa.json
                                         site/maturity/countries/{iso3}/index.html
                                         site/methodology/maturity/index.html
                                         maturity/preview-downloads/*.csv  (Bill's check copies)

**The spec is `maturity/documentation/output-spec-v2.md`.** This builds what it describes from
the studies' issued files — every `outputs/maturity/{id}/assessment.csv`, `{ISO3}.md` and
`{indicator_id}.md` — and from `lookups/indicators.csv`. The map page holds no content of its
own: `maturity.json` carries everything it shows, and `site/assets/js/maturity-map.js` draws it.

**Soft launch** *(Bill, 2026-10-09)*. Every page carries `noindex` and the *Under construction*
band, and nothing links to them; `sitemap.py` already leaves a `noindex` page out. Draft stages
are shown. Launch is three edits here: `LAUNCHED = True` drops the band and the noindex and turns
the download buttons on, and the menu entry goes into data-landscapers `_data/site_menu.yml`.

**Downloads wait for launch** *(Bill)*. A dated CSV once downloaded is kept for ever (`design.md`
§9), so no draft is offered as one. Until launch the buttons are shown disabled, and the files they
will serve are written undated to `maturity/preview-downloads/` — outside `site/` — for Bill to check.

**A study replaces the frame rows it redraws.** Its sub-indicators are not in `indicators.csv`
until acceptance; `study.json` → `redraws` names the rows they stand in for, so the Indicator
dropdown shows the sub-indicators where the first redrawn row sat and drops the others.

**Writes no edition.** Safe to run alone. RENDER runs it after `methodology.py`, before `sitemap.py`.
"""
from __future__ import annotations

import csv
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

import markdown

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chrome_lib import SITE_BASE, MAIN_SITE, chrome, external_links, foot, ga, script, styles  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT = SITE / "maturity"
METHOD_OUT = SITE / "methodology" / "maturity"
STUDIES = ROOT / "maturity"
ISSUED = ROOT / "outputs" / "maturity"
PREVIEW = ROOT / "maturity" / "preview-downloads"
GEO = ROOT / "lookups" / "africa.geojson"   # africa-dpi's, copied 2026-10-09; Western Sahara is in it

LAUNCHED = False
# Before launch the reports and the methodology page carry the Under construction band; the map carries
# the words in its title instead, so the map page keeps its full depth (Bill, 2026-10-09). noindex stays.
SHOW_BAND = True

# The scale: documentation/archived/maturity-assessment.md §3, the instruments-and-systems column.
# Labels 2 and 3 renamed Preparing and Establishing (Bill, 2026-10-09); all five still under review.
# A study's own pages print the old labels in their ladders; `relabel()` rewrites them at build.
# Colours: red, orange, gold, sky, blue at even weight (Bill, 2026-10-09: RdYlBu's pale yellow read weaker
# than its orange). Every pair stays distinct under simulated deuteranopia, protanopia and tritanopia.
STAGES = [
    dict(n=1, label="Absent", color="#b2182b", ink="#ffffff",
         desc="Nothing of the kind exists, and a dated source says so."),
    dict(n=2, label="Preparing", color="#e66a2c", ink="#1a1a18",
         desc="Announced, drafted, piloted: an intention with an instrument or a pilot behind it."),
    dict(n=3, label="Establishing", color="#f2c12e", ink="#1a1a18",
         desc="In service, but limited in scope, coverage or use."),
    dict(n=4, label="Operating", color="#67a9cf", ink="#1a1a18",
         desc="In service at scale: funded, regulated, used, maintained."),
    dict(n=5, label="Leading", color="#2166ac", ink="#ffffff",
         desc="Embedded: interoperable, measured, sustained; at or beyond the continental norm."),
]
GREY = dict(label="No evidence", color="#d4d4d4", ink="#1a1a18",
            desc="Not staged: nothing held, or evidence held that meets no rung.")

UNDER_CONSTRUCTION = ('<div class="mat-construction" role="note"><strong>Under construction.</strong> '
                      'The Maturity Assessment is being built indicator by indicator; stages shown '
                      'here are drafts and will change before launch.</div>')


# ---------------------------------------------------------------------------
# Reading the studies
# ---------------------------------------------------------------------------

def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def md(text: str) -> str:
    return markdown.markdown(text, extensions=["tables", "sane_lists"])


def sections(text: str, level: str) -> list[tuple[str, str]]:
    """Split markdown on headings of exactly `level` ('## ' or '### '): [(heading, body)]."""
    out, head, buf = [], None, []
    for ln in text.splitlines():
        if ln.startswith(level) and not ln.startswith(level + "#"):
            if head is not None:
                out.append((head, "\n".join(buf).strip()))
            head, buf = ln[len(level):].strip(), []
        elif head is not None:
            buf.append(ln)
    if head is not None:
        out.append((head, "\n".join(buf).strip()))
    return out


def ladder(text: str) -> tuple[list[str], list[list[str]]]:
    """The `## The ladder` table of an indicator page: (aspect headers, rows of cells)."""
    body = dict(sections(text, "## ")).get("The ladder", "")
    rows = [ln for ln in body.splitlines() if ln.startswith("|")]
    if len(rows) < 3:
        return [], []
    split = lambda ln: [c.strip() for c in ln.strip().strip("|").split("|")]
    return split(rows[0])[1:], [split(r) for r in rows[2:]]


def load_studies() -> list[dict]:
    studies = []
    for sj in sorted(STUDIES.glob("*/study.json")):
        spec = json.loads(sj.read_text(encoding="utf-8"))
        issued = ISSUED / spec["id"]
        if not (issued / "assessment.csv").exists():
            continue
        spec["rows"] = read_csv(issued / "assessment.csv")
        spec["issued"] = issued
        studies.append(spec)
    return studies


# ---------------------------------------------------------------------------
# The data the map reads
# ---------------------------------------------------------------------------

def stage_of(raw: str) -> tuple[int | None, str]:
    raw = (raw or "").strip().lower()
    if raw.isdigit():
        return int(raw), "staged"
    return None, ("unplaced" if raw == "unplaced" else "no evidence")


def month(iso: str) -> str:
    try:
        return date.fromisoformat(iso).strftime("%b %Y")
    except ValueError:
        return iso


def country_sections(issued: Path, iso3: str, labels: dict[str, str]) -> dict[str, str]:
    """{indicator_id: markdown of that sub-indicator's section} from `{ISO3}.md`."""
    path = issued / f"{iso3}.md"
    if not path.exists():
        return {}
    return {labels[h]: body for h, body in sections(path.read_text(encoding="utf-8"), "## ")
            if h in labels}


def sidebar_md(body: str) -> str:
    """The country's section for the sidebar: the aspect paragraphs and *Not held*, without the
    *Noted, not assessed* list, which belongs to the report."""
    keep = [p for p in re.split(r"\n\s*\n", body) if not p.startswith("***Noted")]
    return "\n\n".join(keep)


def build_data(studies, indicators, countries) -> dict:
    by_id = {s["id"]: s for s in studies}
    redrawn = {}
    for s in studies:
        for i, row in enumerate(s.get("redraws", [])):
            redrawn[row] = s["id"] if i == 0 else None

    topics, seen = [], {}
    for r in sorted((r for r in indicators if not r.get("retired")),
                    key=lambda r: (int(r["Topic Sort"]), int(r["Indicator Sort"]))):
        t = r["Topic"]
        if t not in seen:
            seen[t] = dict(name=t, group=r["Topic L1"], indicators=[])
            topics.append(seen[t])
        if r["indicator_id"] in redrawn:
            sid = redrawn[r["indicator_id"]]
            if sid:
                for sub in by_id[sid]["sub_indicators"]:
                    seen[t]["indicators"].append(dict(id=sub["indicator_id"], label=sub["text"], studied=True))
            continue
        seen[t]["indicators"].append(dict(id=r["indicator_id"], label=r["Progress indicator"], studied=False))
    for t in topics:
        t["studied"] = any(i["studied"] for i in t["indicators"])

    inds, cells, changes = {}, {}, {}
    for s in studies:
        labels = {sub["label"]: sub["indicator_id"] for sub in s["sub_indicators"]}
        for sub in s["sub_indicators"]:
            iid = sub["indicator_id"]
            page = s["issued"] / f"{iid}.md"
            text = page.read_text(encoding="utf-8") if page.exists() else ""
            heads, rows = ladder(text)
            lines = []
            for cells_ in rows:
                m = re.match(r"(\d)\s*(.*)", cells_[0])
                parts = [f"{h}: {c}" for h, c in zip(heads, cells_[1:]) if c]
                lines.append(dict(n=int(m.group(1)) if m else None, text="; ".join(parts)))
            topic = next((t["name"] for t in topics if any(i["id"] == iid for i in t["indicators"])), "")
            inds[iid] = dict(label=sub["text"], short_label=sub["label"], topic=topic, study=s["id"],
                             ladder=lines)
            cells[iid], changes[iid] = {}, []
        bodies = {}
        for r in s["rows"]:
            iid, iso = r["indicator_id"], r["iso3"]
            if iid not in cells:
                continue
            if iso not in bodies:
                bodies[iso] = country_sections(s["issued"], iso, labels)
            n, state = stage_of(r["stage"])
            cells[iid][iso] = dict(
                stage=n, state=state, short=r["short"].strip(),
                assessed=month(r["as_at"]),
                moved=None,  # no snapshot history yet: every cell is its first assessment
                reassessed=None,
                summary=external_links(md(sidebar_md(bodies[iso].get(iid, "")))))
    return dict(built=date.today().isoformat(), launched=LAUNCHED, stages=STAGES, grey=GREY,
                topics=topics, indicators=inds, cells=cells, changes=changes,
                countries={c["iso-3"]: c["country-name"] for c in countries
                           if not c["iso-3"].startswith("X")})


def africa_geo() -> dict:
    g = json.loads(GEO.read_text(encoding="utf-8"))

    def rnd(x):
        return [rnd(v) for v in x] if isinstance(x, list) else round(x, 3)

    feats = []
    for f in g["features"]:
        p = f["properties"]
        feats.append(dict(type="Feature", properties=dict(iso3=p.get("iso3") or p.get("ISO3166-1-Alpha-3"),
                                                          name=p.get("name")),
                          geometry=dict(type=f["geometry"]["type"],
                                        coordinates=rnd(f["geometry"]["coordinates"]))))
    return dict(type="FeatureCollection", features=feats)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Data Landscapers</title>
<meta name="description" content="{description}">
{robots}<link rel="canonical" href="{canonical}">
{styles}
<link rel="icon" href="{main}/assets/favicon.svg" type="image/svg+xml">
{ga}
</head>
<body class="{body_class}">
<div class="site-wrap">

{chrome}
"""

TAIL = """
{foot}

</div>
{scripts}
</body>
</html>
"""


def page(*, title, description, canonical, depth, body, body_class, sheets=(), scripts="",
         active=None, band: bool = True) -> str:
    """`band=False` for the map, which says *Under construction* in its title instead (Bill, 2026-10-09)."""
    robots = "" if LAUNCHED else '<meta name="robots" content="noindex">\n'
    band = UNDER_CONSTRUCTION if band and SHOW_BAND and not LAUNCHED else ""
    return external_links(
        HEAD.format(title=html.escape(title), description=html.escape(description), robots=robots,
                    canonical=canonical, styles=styles(depth, *sheets), main=MAIN_SITE, ga=ga(),
                    body_class=body_class, chrome=chrome(active, depth=depth))
        + f'  <main id="main">\n  {band}\n{body}\n  </main>\n'
        + TAIL.format(foot=foot(depth=depth), scripts=scripts))


def map_page() -> str:
    dl = "" if LAUNCHED else ' disabled title="Available at launch"'
    note = "" if LAUNCHED else '<span class="mat-dl-note">Downloads available at launch</span>'
    uc = "" if LAUNCHED else ' <span class="mat-title__uc">Under construction</span>'
    body = f"""  <div class="mat-wrap">
    <div class="mat-head">
      <h1 class="mat-title">Maturity Assessment{uc}</h1>
      <div class="mat-buttons">
        <a class="mat-btn" id="mat-method" href="../methodology/maturity/">Methodology</a>
        <button class="mat-btn" id="mat-dl-one" type="button"{dl}>Download this indicator (CSV)</button>
        <button class="mat-btn" id="mat-dl-all" type="button"{dl}>Download all (CSV)</button>
        {note}
      </div>
    </div>
    <div class="mat-controls">
      <label class="mat-field"><span>Topic</span><select id="mat-topic"></select></label>
      <label class="mat-field mat-field--wide"><span>Indicator</span><select id="mat-indicator"></select></label>
    </div>
    <div class="mat-body">
      <div class="mat-mapcol">
        <div class="mat-map" id="mat-map">
          <aside class="mat-changes" id="mat-changes" aria-live="polite"></aside>
        </div>
        <div class="mat-legend" id="mat-legend"></div>
      </div>
      <aside class="mat-side">
        <section class="mat-side__top" id="mat-side-indicator"></section>
        <section class="mat-side__bottom" id="mat-side-country" aria-live="polite"></section>
      </aside>
    </div>
    <div class="mat-tooltip" id="mat-tooltip" role="tooltip" hidden></div>
    <noscript><p>The map needs JavaScript. Each country's report is at <code>/maturity/countries/&lt;ISO3&gt;/</code>.</p></noscript>
  </div>"""
    return page(title="Maturity Assessment",
                description="Where each African country stands on each studied indicator, on a five-stage scale.",
                canonical=f"{SITE_BASE}/maturity/", depth=1, body=body, body_class="mat-page", band=False,
                sheets=("maturity.css",),
                scripts=script("d3-7.9.0.min.js", 1) + "\n" + script("maturity-map.js", 1))


def chip(cell: dict | None) -> str:
    if not cell or cell["stage"] is None:
        state = cell["state"] if cell else "no evidence"
        return f'<span class="mat-chip" style="background:{GREY["color"]};color:{GREY["ink"]}">{state.capitalize()}</span>'
    s = STAGES[cell["stage"] - 1]
    return f'<span class="mat-chip" style="background:{s["color"]};color:{s["ink"]}">{s["n"]} {s["label"]}</span>'


def country_page(iso3: str, name: str, data: dict, bodies: dict[str, str]) -> str:
    parts, unstudied = [], []
    for t in data["topics"]:
        studied = [i for i in t["indicators"] if i["studied"]]
        for i in t["indicators"]:
            if not i["studied"]:
                unstudied.append((t["name"], i["label"]))
        if not studied:
            continue
        parts.append(f'    <h2 class="mat-report__topic">{html.escape(t["name"])}</h2>')
        for i in studied:
            iid = i["id"]
            cell = data["cells"].get(iid, {}).get(iso3)
            moved = (cell or {}).get("moved") or "First assessment"
            parts.append(f'''    <section class="mat-report__ind" id="{iid}">
      <h3>{html.escape(i["label"])}</h3>
      <p class="mat-report__meta">{chip(cell)}
        <span><b>Last assessed</b> {html.escape((cell or {}).get("assessed", "—"))}</span>
        <span><b>Stage last moved</b> {html.escape(moved)}</span>
        <a href="../../../methodology/maturity/#{iid}">Methodology</a> ·
        <a href="../../#{iid}|{iso3}">On the map</a></p>
      <p class="mat-report__short">{html.escape((cell or {}).get("short", ""))}</p>
      <div class="mat-report__long">
{md(bodies.get(iid, "*Nothing held for this country yet.*"))}
      </div>
    </section>''')
    if unstudied:
        rows, last = [], None
        for t, label in unstudied:
            if t != last:
                if last is not None:
                    rows.append("</ul>")
                rows.append(f"<h3>{html.escape(t)}</h3><ul>")
                last = t
            rows.append(f"<li>{html.escape(label)}</li>")
        rows.append("</ul>")
        parts.append('    <section class="mat-report__pending" id="not-yet-studied">\n'
                     '      <h2 class="mat-report__topic">Not yet studied</h2>\n      '
                     + "\n      ".join(rows) + "\n    </section>")
    body = f"""  <div class="container mat-report">
    <header class="article-header">
      <p class="mat-report__kicker"><a href="../../">Maturity Assessment</a></p>
      <h1 class="article-header__title">{html.escape(name)}</h1>
    </header>
    <article class="article-body">
{chr(10).join(parts)}
    </article>
  </div>"""
    return page(title=f"{name} — Maturity Assessment",
                description=f"{name}: stage, summary and evidence for each studied maturity indicator.",
                canonical=f"{SITE_BASE}/maturity/countries/{iso3.lower()}/", depth=3, body=body,
                body_class="mat-report-page", sheets=("maturity.css",))


METHOD_INTRO = """## The scale

Each studied indicator places each of the 54 countries on one five-stage scale. The stages are ordinal: 4 is above 3, not twice 2. The assessment is not a score or a ranking, and nothing is averaged.

{scale}

## No evidence and unplaced

**No evidence** means nothing held states any of the facts the ladder tests. **Unplaced** means evidence is held but it meets no rung, so no stage is set. Both are shown in grey. Neither is stage 1: *Absent* needs a dated source that says the thing does not exist.

## How a stage is set

Each indicator is studied whole, across all 54 countries. A study first settles what the indicator covers and splits it into sub-indicators where one label hides two things. It then fixes a ladder: for each stage, the value each coverage aspect must reach. A country is placed on the highest rung whose every test its evidence meets; between two rungs it takes the lower. Every fact carries its date, and a fact older than three years at the as-at date prints its year. A second drafter restages a sample blind, and a rung read two ways is rewritten.

Stages are taken as at the end of a month. A stage changes only on a dated source inside the window; a change from a re-read or a corrected ladder is marked *reassessed* and is not counted as movement.
"""


def relabel(text: str) -> str:
    """A ladder row's first cell is `| N Label |`; print the label the scale holds now."""
    return re.sub(r"^\|\s*([1-5])\s+[A-Za-z]+\s*\|",
                  lambda m: f"| {m.group(1)} {STAGES[int(m.group(1)) - 1]['label']} |", text, flags=re.M)


def method_page(data: dict, studies: list[dict]) -> str:
    scale = "| Stage | Label | Meaning |\n|---|---|---|\n" + "\n".join(
        f'| {s["n"]} | {s["label"]} | {s["desc"]} |' for s in STAGES)
    blocks = [md(METHOD_INTRO.format(scale=scale))]
    toc = []
    for s in studies:
        for sub in s["sub_indicators"]:
            iid = sub["indicator_id"]
            p = s["issued"] / f"{iid}.md"
            text = p.read_text(encoding="utf-8") if p.exists() else ""
            secs = dict(sections(text, "## "))
            toc.append((iid, sub["text"]))
            blocks.append(f'<section class="mat-method__ind" id="{iid}">\n<h2>{html.escape(sub["text"])}</h2>\n'
                          + md("### The norm\n\n" + secs.get("The norm", "Not yet written.")
                               + "\n\n### The ladder\n\n" + relabel(secs.get("The ladder", "Not yet written.")))
                          + "\n</section>")
    strip = ('<nav class="article-toc" aria-label="Indicators">\n'
             + '\n<span class="article-toc__sep" aria-hidden="true">&middot;</span>\n'.join(
                 f'<a href="#{i}">{html.escape(t)}</a>' for i, t in toc) + "\n</nav>\n")
    body = f"""  <div class="container">
    <header class="article-header">
      <p class="mat-report__kicker"><a href="../../maturity/">Maturity Assessment</a></p>
      <h1 class="article-header__title">Maturity Assessment: methodology</h1>
    </header>
    <article class="article-body mat-method">
{strip}
{chr(10).join(blocks)}
    </article>
  </div>"""
    return page(title="Methodology — Maturity Assessment",
                description="How the Maturity Assessment places countries on its five-stage scale, indicator by indicator.",
                canonical=f"{SITE_BASE}/methodology/maturity/", depth=2, body=body,
                body_class="mat-method-page", sheets=("methodology.css", "maturity.css"),
                active="methodology")


# ---------------------------------------------------------------------------

def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return
    path.write_text(text, encoding="utf-8", newline="\n")


def preview_downloads(studies: list[dict]) -> int:
    PREVIEW.mkdir(parents=True, exist_ok=True)
    allrows, n = [], 0
    for s in studies:
        for sub in s["sub_indicators"]:
            rows = [r for r in s["rows"] if r["indicator_id"] == sub["indicator_id"]]
            allrows += rows
            if rows:
                with (PREVIEW / f'{sub["indicator_id"]}.csv').open("w", encoding="utf-8", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                    w.writeheader(); w.writerows(rows)
                n += 1
    if allrows:
        fields = list(dict.fromkeys(k for r in allrows for k in r))
        with (PREVIEW / "maturity-all.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, restval="")
            w.writeheader(); w.writerows(allrows)
        n += 1
    return n


def main() -> int:
    studies = load_studies()
    indicators = read_csv(ROOT / "lookups" / "indicators.csv")
    countries = read_csv(ROOT / "lookups" / "countries.csv")
    data = build_data(studies, indicators, countries)

    write(OUT / "data" / "maturity.json", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    write(OUT / "data" / "africa.json", json.dumps(africa_geo(), separators=(",", ":")))
    write(OUT / "index.html", map_page())

    iso_names = {c["iso-3"]: c["country-name"] for c in countries}
    n = 0
    for iso in sorted(data["countries"]):
        bodies = {}
        for s in studies:
            labels = {sub["label"]: sub["indicator_id"] for sub in s["sub_indicators"]}
            bodies.update(country_sections(s["issued"], iso, labels))
        write(OUT / "countries" / iso.lower() / "index.html",
              country_page(iso, iso_names.get(iso, iso), data, bodies))
        n += 1
    write(METHOD_OUT / "index.html", method_page(data, studies))
    k = preview_downloads(studies)
    ids = sum(len(s["sub_indicators"]) for s in studies)
    print(f"maturity: {len(studies)} study, {ids} indicators -> site/maturity/ + {n} country reports"
          f" + site/methodology/maturity/; {k} preview CSVs -> maturity/preview-downloads/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
