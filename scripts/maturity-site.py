#!/usr/bin/env python3
"""maturity-site.py — the Maturity Assessment's map, country reports and methodology page.

    python scripts/maturity-site.py [--redesign]
                                      -> site/maturity/index.html
                                         site/maturity/data/maturity.json, africa.json
                                         site/maturity/countries/{iso3}/index.html
                                         site/methodology/maturity/index.html
                                         maturity/preview-downloads/*.csv  (Bill's check copies)

**The spec is `maturity/documentation/output-spec-v2.md`.** This builds what it describes from
the studies' issued files — every `outputs/maturity/{id}/assessment.csv`, `{ISO3}.md` and
`{indicator_id}.md` — and from `lookups/indicators.csv`. The map page holds no content of its
own: `maturity.json` carries everything it shows, and `site/assets/js/maturity-map.js` draws it.

**Launched 2026-10-19** *(Bill)*: `LAUNCHED = True` dropped the last *Under construction* labels
and turned the downloads on. The country reports had come out of hiding on 2026-10-17, and every
page dropped `noindex` that day (`INDEXED`).

**Downloads are editions** (`design.md` §9). `publish_downloads()` cuts each file as a dated edition
beside the map, through `editions.publish`, only when its bytes move, and the map page carries a
`dl-artefact` line for each. Before launch the buttons were disabled and the files went undated to
`maturity/preview-downloads/` instead; `LAUNCHED = False` restores that. **This writes editions, so
RENDER runs Step 6b again after it** when it has cut one.

**A build that would blank the map writes nothing.** `problems()` reads what was built and the map
already published; anything it finds is printed and the run exits 1 with `site/` untouched.

**A study replaces the frame rows it redraws.** Its sub-indicators are not in `indicators.csv`
until acceptance; `study.json` → `redraws` names the rows they stand in for, so the Indicator
dropdown shows the sub-indicators where the first redrawn row sat and drops the others.

**Writes editions.** Safe to run alone, followed by `r2-sync.py`. RENDER runs it after `methodology.py`,
before `sitemap.py`.
"""
from __future__ import annotations

import csv
import hashlib
import html
import io
import json
import math
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chrome_lib import SITE_BASE, MAIN_SITE, chrome, external_links, feedback, foot, ga, info, script, styles  # noqa: E402
from render import family_bar  # noqa: E402
import methodology  # noqa: E402  - the Methodology section's page bar
import editions  # noqa: E402
import maturity_words  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT = SITE / "maturity"
METHOD_OUT = SITE / "methodology" / "maturity"
STUDIES = ROOT / "maturity"
ISSUED = ROOT / "outputs" / "maturity"
NORM_SHORT_WORDS = 45   # what three lines of the map's criteria heading hold
PREVIEW = ROOT / "maturity" / "preview-downloads"
# africa-dpi's, copied 2026-10-09; Western Sahara is in it. `lookups/AFRICA-GEOJSON-FROM` names the
# commit and `lint-shared-assets.py` compares the bytes.
GEO = ROOT / "lookups" / "africa.geojson"
# How far a border may move when the map's copy is thinned, in degrees. The map draws about ten
# pixels to a degree, so this is a fifth of a pixel; it takes africa.json from 917 KB to about 210 KB.
GEO_TOLERANCE = 0.02

LAUNCHED = True
# A redesign cuts no edition: the reports are rewritten under the editions they already serve.
REDESIGN = "--redesign" in sys.argv
# The changes box counts only moves recorded from this day: everything before it was the baseline
# backfill, not change (Bill, 2026-10-19).
CHANGES_FROM = "2026-10-20"
# Indexed ahead of launch (Bill, 2026-10-17): it takes days to take effect.
INDEXED = True
# Before launch the reports and the methodology page carry the Under construction band; the map carries
# the words in its title instead, so the map page keeps its full depth (Bill, 2026-10-09).
SHOW_BAND = True

# The scale: documentation/archived/maturity-assessment.md §3, the instruments-and-systems column.
# Labels 2 and 3 renamed Preparing and Establishing (Bill, 2026-10-09); all five still under review.
# A study's own pages print the old labels in their ladders; every page built here prints these.
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
# Not staged. Unplaced keeps the grey; No evidence is left unfilled (Bill, 2026-10-19).
GREY = dict(label="Unplaced", color="#d4d4d4", ink="#1a1a18",
            desc=maturity_words.UNPLACED_DESC)
BLANK = dict(label="No evidence", color="#ffffff", ink="#1a1a18",
             desc=maturity_words.BLANK_DESC)

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
            print(f"maturity: study {spec['id']} has no issued assessment.csv, left out")
            continue
        spec["rows"] = read_csv(issued / "assessment.csv")
        # Every reassessment since the study, moved or not (`study-update.py log`).
        spec["history"] = read_csv(issued / "history.csv") if (issued / "history.csv").exists() else []
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


def last_change(history: list[dict], iid: str, iso: str) -> tuple[str | None, str | None]:
    """`(moved, reassessed)` for a cell, as months. A stage **moves** on a new fact; a change the
    rotation or a rewritten rung made is a **reassessment**, shown only while it is the cell's
    latest change (spec section 6). A reassessment that left the stage alone is neither."""
    changes = [h for h in sorted(history, key=lambda h: h["date"])
               if h["indicator_id"] == iid and h["iso3"] == iso and h["from"] != h["to"]]
    facts = [h for h in changes if h["kind"] == "fact"]
    return (month(facts[-1]["date"]) if facts else None,
            month(changes[-1]["date"]) if changes and changes[-1]["kind"] != "fact" else None)


def recent_moves(history: list[dict], iid: str, today: date) -> list[dict]:
    """The changes box: stage moves on evidence in the past six months, newest first."""
    since = max((today - timedelta(days=183)).isoformat(), CHANGES_FROM)
    return [dict(iso3=h["iso3"], month=month(h["date"]), **{"from": h["from"], "to": h["to"]})
            for h in sorted(history, key=lambda h: h["date"], reverse=True)
            if h["indicator_id"] == iid and h["kind"] == "fact" and h["from"] != h["to"]
            and h["date"] >= since]


def country_sections(issued: Path, iso3: str, labels: dict[str, str]) -> dict[str, str]:
    """{indicator_id: markdown of that sub-indicator's section} from `{ISO3}.md`."""
    path = issued / f"{iso3}.md"
    if not path.exists():
        return {}
    return {labels[h]: body for h, body in sections(path.read_text(encoding="utf-8"), "## ")
            if h in labels}


def sidebar_md(body: str) -> str:
    """The country's section for the sidebar: the aspect paragraphs and *Not found*, without the
    *Also on file* list, which belongs to the report."""
    keep = [p for p in re.split(r"\n\s*\n", body) if not p.startswith(maturity_words.ALSO_ON_FILE_LABEL)]
    return "\n\n".join(keep)


def build_data(studies, indicators, countries) -> dict:
    """`downloads` is filled by `main()` at launch: `{indicator_id: file, "all": file}`."""
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
                    seen[t]["indicators"].append(dict(id=sub["indicator_id"], label=indicator_name(by_id[sid], sub), studied=True))
            continue
        seen[t]["indicators"].append(dict(id=r["indicator_id"], label=r["Progress indicator"], studied=False))
    for t in topics:
        t["studied"] = any(i["studied"] for i in t["indicators"])

    inds, cells, changes = {}, {}, {}
    for s in studies:
        labels = {sub["label"]: sub["indicator_id"] for sub in s["sub_indicators"]}
        for sub in s["sub_indicators"]:
            iid = sub["indicator_id"]
            # The sidebar's ladder is the methodology page's: the criteria sentences (Bill, 2026-10-09).
            lines = [dict(n=n, text=text) for n, text in enumerate(sub.get("criteria", []), 1)]
            topic = next((t["name"] for t in topics if any(i["id"] == iid for i in t["indicators"])), "")
            # The sidebar's norm is `norm_short`, written by hand for the map; the methodology page
            # prints the study's own, at its own length (Bill, 2026-10-13).
            inds[iid] = dict(label=indicator_name(s, sub), short_label=sub["label"], topic=topic, study=s["id"],
                             ladder=lines, norm=md(sub.get("norm_short", "")))
            cells[iid], changes[iid] = {}, recent_moves(s["history"], iid, date.today())
        bodies = {}
        for r in s["rows"]:
            iid, iso = r["indicator_id"], r["iso3"]
            if iid not in cells:
                continue
            if iso not in bodies:
                bodies[iso] = country_sections(s["issued"], iso, labels)
            n, state = stage_of(r["stage"])
            cells[iid][iso] = dict(
                # R136: an issued assessment.csv keeps the words it was cut with until its study
                # re-issues it, so the page takes R130's words here rather than cutting an edition.
                stage=n, state=state, short=maturity_words.rewrite(r["short"].strip()),
                assessed=month(r["as_at"]),
                **dict(zip(("moved", "reassessed"), last_change(s["history"], iid, iso))),
                summary=external_links(md(sidebar_md(bodies[iso].get(iid, "")))))
    # The sidebar's second button opens the country's status report at the indicator's topic
    # (Bill, 2026-10-21). The anchor is the heading's id as `render.py`'s `toc` extension mints
    # it, and it is offered only where that report holds the topic: a status report prints only
    # the sections it has rows for, so the link otherwise opens the topic's chapter, or the top.
    group = {t["name"]: t["group"] for t in topics}
    for i in inds.values():
        i["anchor"] = slugify(i["topic"], "-") if i["topic"] else ""
        i["chapter"] = slugify(group.get(i["topic"], ""), "-")
    wanted = {a for i in inds.values() for a in (i["anchor"], i["chapter"]) if a}
    status = {}
    for c in countries:
        iso = c["iso-3"]
        page = SITE / "reports" / iso / f"{iso}-status.html"
        if not iso.startswith("X") and page.exists():
            status[iso] = sorted(wanted & set(re.findall(r' id="([^"]+)"', page.read_text(encoding="utf-8"))))
    # No build date: nothing read it, and it rewrote the file on every day's render.
    return dict(launched=LAUNCHED, stages=STAGES, grey=GREY, blank=BLANK, downloads={},
                topics=topics, indicators=inds, cells=cells, changes=changes, status=status,
                countries={c["iso-3"]: c["country-name"] for c in countries
                           if not c["iso-3"].startswith("X")})


def thin(pts: list, tol: float) -> list:
    """Douglas-Peucker: the points of a line that keep it within `tol` of where it was."""
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        (ax, ay), (bx, by) = pts[a], pts[b]
        dx, dy = bx - ax, by - ay
        span = dx * dx + dy * dy
        far, at = -1.0, a
        for i in range(a + 1, b):
            px, py = pts[i]
            t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / span)) if span else 0.0
            d = math.hypot(px - ax - t * dx, py - ay - t * dy)
            if d > far:
                far, at = d, i
        if far > tol:
            keep[at] = True
            stack += [(a, at), (at, b)]
    return [p for p, k in zip(pts, keep) if k]


def area(ring: list) -> float:
    """Signed area of a closed ring, in square degrees: the sign is the way it winds."""
    return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(ring, ring[1:])) / 2


def thin_ring(ring: list, tol: float) -> list:
    """A closed ring thinned in two halves, split at the point farthest from its start, so neither
    half is measured against a chord of no length. Empty for a ring too small to draw.

    **A thinned ring that winds the other way, or has lost half its area, is put back whole.**
    d3 reads the winding to tell a shape's inside from its outside, so a sliver thinned flat or
    inside out paints the whole map with its country's colour."""
    was = area(ring)
    if abs(was) < tol * tol:
        return []
    if abs(was) < 1:    # an island: a few pixels across, where the tolerance is a real share of it
        return [[round(x, 3), round(y, 3)] for x, y in ring]
    far =max(range(len(ring)), key=lambda i: (ring[i][0] - ring[0][0]) ** 2 + (ring[i][1] - ring[0][1]) ** 2)
    out = thin(ring[:far + 1], tol)[:-1] + thin(ring[far:], tol)
    now = area(out)
    if len(out) < 4 or now * was <= 0 or abs(now) < abs(was) / 2:
        out = ring
    return [[round(x, 3), round(y, 3)] for x, y in out]


def africa_geo() -> dict:
    """The map's copy of the geography, thinned to `GEO_TOLERANCE`. An islet that thins to nothing
    is dropped; a country that would lose every polygon keeps them all as they were."""
    g = json.loads(GEO.read_text(encoding="utf-8"))
    feats = []
    for f in g["features"]:
        p, geom = f["properties"], f["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        thinned = []
        for poly in polys:
            outer = thin_ring(poly[0], GEO_TOLERANCE)
            if not outer:
                continue
            thinned.append([outer] + [h for h in (thin_ring(r, GEO_TOLERANCE) for r in poly[1:]) if h])
        if not thinned:
            thinned = [[[[round(x, 3), round(y, 3)] for x, y in r] for r in poly] for poly in polys]
        feats.append(dict(type="Feature", properties=dict(iso3=p.get("iso3") or p.get("ISO3166-1-Alpha-3"),
                                                          name=p.get("name")),
                          geometry=dict(type="MultiPolygon", coordinates=thinned)))
    return dict(type="FeatureCollection", features=feats)


# ---------------------------------------------------------------------------
# The check: a build that would blank the map is not written
# ---------------------------------------------------------------------------

def problems(data: dict, geo: dict, studies: list[dict], indicators: list[dict],
             published: dict | None) -> list[str]:
    """What is wrong with this build, as lines. Each of these used to build quietly: a missing
    page printed *Not yet written*, a missing country printed *Nothing found*, and a row under an
    unknown indicator was dropped."""
    out = []
    if not studies:
        out.append("no study has an issued assessment.csv: the map would have nothing to open on")
    frame = {r["indicator_id"] for r in indicators}
    listed = {i["id"] for t in data["topics"] for i in t["indicators"] if i["studied"]}
    drawn = {f["properties"]["iso3"] for f in geo["features"]}
    for iso in sorted(set(data["countries"]) - drawn):
        out.append(f"{iso}: no shape in {GEO.name}")
    for s in studies:
        subs = {sub["indicator_id"] for sub in s["sub_indicators"]}
        for row in s.get("redraws", []):
            if row not in frame:
                out.append(f"{s['id']}: redraws `{row}`, which is not in indicators.csv")
        stray = sorted({r["indicator_id"] for r in s["rows"]} - subs)
        if stray:
            out.append(f"{s['id']}: assessment.csv rows under {stray}, not a sub-indicator of the study")
        latest = {}
        for h in sorted(s.get("history", []), key=lambda h: h["date"]):
            if h["indicator_id"] not in subs or h["iso3"] not in data["countries"] \
                    or h["kind"] not in ("fact", "review", "ladder"):
                out.append(f"{s['id']}: history.csv row {h['date']} {h['iso3']} {h['indicator_id']} "
                           f"{h['kind']} names no cell or no kind")
            latest[(h["indicator_id"], h["iso3"])] = h
        now = {(r["indicator_id"], r["iso3"]): r["stage"] for r in s["rows"]}
        for cell, h in sorted(latest.items()):
            if cell in now and h["to"] != now[cell]:
                out.append(f"{cell[1]} {cell[0]}: stage {now[cell]}, but its last logged reassessment "
                           f"({h['date']}) left it at {h['to']}; a restaging was not logged")
        for sub in s["sub_indicators"]:
            iid = sub["indicator_id"]
            page = s["issued"] / f"{iid}.md"
            if not page.exists():
                out.append(f"{iid}: no indicator page {page.name}")
            else:
                if not dict(sections(page.read_text(encoding="utf-8"), "## ")).get("The norm"):
                    out.append(f"{iid}: {page.name} has no norm")
                if [c[0][:1] for c in ladder(page.read_text(encoding="utf-8"))[1]] != list("12345"):
                    out.append(f"{iid}: {page.name}'s ladder does not read as rungs 1 to 5")
            short = sub.get("norm_short", "")
            if not short.strip():
                out.append(f"{iid}: study.json holds no `norm_short` for the map's criteria box")
            elif len(short.split()) > NORM_SHORT_WORDS:
                out.append(f"{iid}: `norm_short` is {len(short.split())} words; the map's heading holds "
                           f"{NORM_SHORT_WORDS}")
            if len(sub.get("criteria", [])) != 5:
                out.append(f"{iid}: study.json holds no five `criteria` for the methodology page")
            elif page.exists() and sub.get("criteria_of") != ladder_digest(
                    dict(sections(page.read_text(encoding="utf-8"), "## ")).get("The ladder", "")):
                out.append(f"{iid}: the ladder has moved since its `criteria` were written; rewrite them "
                           f"and set `criteria_of`")
            if iid not in listed:
                out.append(f"{iid}: in no topic's list, so the map cannot select it (check `redraws`)")
            cells = data["cells"][iid]
            missing = sorted(set(data["countries"]) - set(cells))
            if missing:
                out.append(f"{iid}: no row for {len(missing)} countries: {' '.join(missing)}")
            for iso, c in sorted(cells.items()):
                if iso not in data["countries"]:
                    out.append(f"{iid}: row for {iso}, which is not one of the countries")
                if c["state"] == "staged" and c["stage"] not in (1, 2, 3, 4, 5):
                    out.append(f"{iid} {iso}: stage {c['stage']}")
                if not c["short"]:
                    out.append(f"{iid} {iso}: no short summary")
                if c["state"] == "staged" and not c["summary"].strip():
                    out.append(f"{iid} {iso}: staged, and no section in {iso}.md")
    for iid in sorted(set((published or {}).get("indicators", {})) - set(data["indicators"])):
        # Sub-indicator ids lost their description suffix on 2026-10-19 (Bill): a renamed one is not lost.
        if any(iid.startswith(b + "-") for b in data["indicators"]):
            continue
        out.append(f"{iid}: on the published map and not in this build")
    return out


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
{robots}{head}<link rel="canonical" href="{canonical}">
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
         active=None, band: bool = True, head: str = "") -> str:
    """`band=False` for the map, which says *Under construction* in its title instead (Bill, 2026-10-09).
    `head` is the map's `dl-artefact` lines once it publishes editions."""
    robots = "" if LAUNCHED or INDEXED else '<meta name="robots" content="noindex">\n'
    band = UNDER_CONSTRUCTION if band and SHOW_BAND and not LAUNCHED else ""
    return external_links(
        HEAD.format(title=html.escape(title), description=html.escape(description), robots=robots, head=head,
                    canonical=canonical, styles=styles(depth, *sheets), main=MAIN_SITE, ga=ga(),
                    body_class=body_class, chrome=chrome(active, depth=depth))
        + f'  <main id="main">\n  {band}\n{body}\n  </main>\n'
        + TAIL.format(foot=foot(depth=depth), scripts=scripts))


def map_page(downloads: dict | None = None, artefacts: str = "") -> str:
    """Before launch the download buttons are disabled. After it they are links: *all* is set
    here, and `maturity-map.js` points *this indicator* at the selected indicator's edition."""
    if LAUNCHED:
        # *This indicator* starts hidden with no href: a `download` link to "#" saves the page
        # itself as download.html, which a cached pre-launch maturity.json would leave in place.
        every = html.escape((downloads or {}).get("all", "#"))
        buttons = ('<a class="mat-btn" id="mat-dl-one" download hidden>Download this indicator (CSV)</a>\n'
                   f'        <a class="mat-btn" id="mat-dl-all" href="{every}" download>Download all (CSV)</a>')
        uc = ""
    else:
        dl = ' disabled title="Available at launch"'
        buttons = (f'<button class="mat-btn" id="mat-dl-one" type="button"{dl}>Download this indicator (CSV)</button>\n'
                   f'        <button class="mat-btn" id="mat-dl-all" type="button"{dl}>Download all (CSV)</button>\n'
                   '        <span class="mat-dl-note">Downloads available at launch</span>')
        uc = ' <span class="mat-title__uc">Under construction</span>'
    about, panel = info("Maturity assessment")
    body = f"""  <div class="mat-wrap">
    <div class="mat-head">
      <h1 class="mat-title">Maturity Assessment{about}{uc}</h1>
      {panel}
      <div class="mat-buttons">
        <a class="mat-btn" id="mat-method" href="../methodology/maturity/">Methodology</a>
        {buttons}
      </div>
    </div>
    <div class="mat-controls">
      <label class="mat-field"><span>Chapter</span><select id="mat-chapter"></select></label>
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
        <section class="mat-side__top" id="mat-side-country" aria-live="polite"></section>
        <section class="mat-side__bottom" id="mat-side-indicator"></section>
      </aside>
    </div>
    <div class="mat-tooltip" id="mat-tooltip" role="tooltip" hidden></div>
    <noscript><p>The map needs JavaScript. Each country's report is at <code>/maturity/countries/&lt;ISO3&gt;/</code>.</p></noscript>
  </div>"""
    return page(title="Maturity Assessment",
                description="Where each African country stands on each studied indicator, on a five-stage scale.",
                canonical=f"{SITE_BASE}/maturity/", depth=1, body=body, body_class="mat-page", band=False,
                active="maturity", head=artefacts,
                sheets=("maturity.css",),
                scripts=script("d3-7.9.0.min.js", 1) + "\n" + script("maturity-map.js", 1))


def chip(cell: dict | None) -> str:
    if not cell or cell["stage"] is None:
        state = cell["state"] if cell else "no evidence"
        if state == "unplaced":
            return f'<span class="mat-chip" style="background:{GREY["color"]};color:{GREY["ink"]}">Unplaced</span>'
        return f'<span class="mat-chip mat-chip--blank" style="background:{BLANK["color"]};color:{BLANK["ink"]}">No evidence</span>'
    s = STAGES[cell["stage"] - 1]
    return f'<span class="mat-chip" style="background:{s["color"]};color:{s["ink"]}">{s["n"]} {s["label"]}</span>'


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def toc(label: str, items: list[tuple[str, str | None]], cls: str = "article-toc") -> str:
    """A jump bar in the house idiom (`.article-toc`): `(text, anchor)`, and an item with no anchor
    is printed greyed out and unlinked, as the map's dropdowns grey what is not yet studied."""
    return (f'    <nav class="{cls}" aria-label="{label}">\n      '
            + '\n      <span class="article-toc__sep" aria-hidden="true">&middot;</span>\n      '.join(
                f'<a href="#{a}">{html.escape(t)}</a>' if a else f'<span class="mat-toc__off">{html.escape(t)}</span>'
                for t, a in items) + "\n    </nav>")


def country_page(iso3: str, name: str, data: dict, bodies: dict[str, str]) -> str:
    """Chapter, then topic, then indicator *(Bill, 2026-10-09)*: the page opens on a bar of every
    chapter and each chapter opens on a bar of its topics. Only what is studied has a section; what is not is
    greyed out in the bars and listed nowhere else."""
    parts, chapters = [], {}
    for t in data["topics"]:
        chapters.setdefault(t["group"], []).append(t)
    bar = toc("Sections in this report",
              [(c, f"chapter-{slug(c)}" if any(t["studied"] for t in ts) else None)
               for c, ts in chapters.items()], "article-toc monthly-toc")
    for t in data["topics"]:
        studied = [i for i in t["indicators"] if i["studied"]]
        if not studied:
            continue
        first = next(o for o in chapters[t["group"]] if o["studied"])
        if t is first:
            parts.append(f'    <h2 class="mat-report__chapter" id="chapter-{slug(t["group"])}">'
                         f'{html.escape(t["group"])}</h2>')
            parts.append(toc(f"Topics under {html.escape(t['group'])}",
                             [(o["name"], f"topic-{slug(o['name'])}" if o["studied"] else None)
                              for o in chapters[t["group"]]], "article-toc monthly-subnav"))
        parts.append(f'    <h3 class="mat-report__topic" id="topic-{slug(t["name"])}">{html.escape(t["name"])}</h3>')
        for i in studied:
            iid = i["id"]
            cell = data["cells"].get(iid, {}).get(iso3)
            moved = (f'Reassessed {cell["reassessed"]}' if (cell or {}).get("reassessed")
                     else (cell or {}).get("moved") or "First assessment")
            parts.append(f'''    <section class="mat-report__ind" id="{iid}">
      <h4>{html.escape(i["label"])}</h4>
      <p class="mat-report__meta">{chip(cell)}
        <span><b>Last assessed</b> {html.escape((cell or {}).get("assessed", "—"))}</span>
        <span><b>Stage last moved</b> {html.escape(moved)}</span>
        <a href="../../../methodology/maturity/#{iid}">Methodology</a> ·
        <a href="../../#{iid}|{iso3}">On the map</a></p>
      <p class="mat-report__short">{html.escape((cell or {}).get("short", ""))}</p>
      <div class="mat-report__long">
{md(bodies.get(iid, f"*{maturity_words.NOTHING_YET}*"))}
      </div>
    </section>''')
    # **Headed as the place's other reports are** *(Bill, 2026-10-17)*: the family bar, the title
    # with its actions and the sections bar, pinned under the site chrome by `report-head.js`. The
    # PDF button stands where the others' does *(Bill, 2026-10-17)*. No Under construction band.
    canonical = f"{SITE_BASE}/maturity/countries/{iso3.lower()}/"
    article = "\n".join(parts)
    rec = hashlib.sha1(article.encode("utf-8")).hexdigest()[:12]
    edition, cut = report_edition(iso3, rec)
    pdf_url = f"{SITE_BASE}/reports/{iso3}/{iso3}-maturity-{edition}.pdf"

    def build(for_pdf: bool) -> str:
        actions = (feedback(f"{name} — Maturity Assessment", canonical)
                   + f'<a href="{pdf_url}" class="btn btn--accent">&darr; PDF</a>')
        # The ⓘ from info.md's Maturity assessment entry (Bill, 2026-10-22); the PDF carries none.
        about, panel = ("", "") if for_pdf else info("Maturity assessment")
        body = f"""  <div class="container mat-report">
      <div class="print-masthead">
        <img src="../../../assets/logo.png" alt="Data Landscapers">
        <div class="tagline">Mapping Africa&rsquo;s data landscape</div>
      </div>
      <div class="report-head">
{family_bar(iso3, "maturity")}<header class="article-header">
        <div class="article-header__meta report-head__row">
          <h1 class="article-header__title">Maturity Assessment{about}</h1>
          <div class="article-header__actions screen-only">{actions}</div>
        </div>
        {panel}
        <div class="article-header__byline mat-report__edition" data-edition="{edition}">{name} &middot; edition of {edition}</div>
      </header>
{bar}
      </div>
    <article class="article-body">
{article}
    </article>
  </div>"""
        return page(title=f"{name} — Maturity Assessment",
                    description=f"{name}: stage, summary and evidence for each studied maturity indicator.",
                    canonical=canonical, depth=3, body=body, body_class="mat-report-page", band=False,
                    active="countries", head=f'<meta name="dl-record" content="{rec}">\n',
                    sheets=("report.css", "maturity.css") if for_pdf else ("maturity.css",),
                    scripts="" if for_pdf else script("report-head.js", 3))

    if cut:
        write_pdf(iso3, edition, build(True), canonical)
    return build(False)


PRIOR_RECORD = re.compile(r'<meta name="dl-record" content="([0-9a-f]+)">')


def report_edition(iso3: str, rec: str) -> tuple[str, bool]:
    """The PDF edition a country's maturity report offers, and whether this run cuts it.

    A dated edition is never revised (design.md §9), so a new one is cut only when the report's
    content moves: `rec` digests the article, not the chrome, so a redesign cuts nothing. The
    served page records both, and is what survives `r2-sync.py --prune-local`."""
    prior = OUT / "countries" / iso3.lower() / "index.html"
    held = editions.edition_on_page(prior)
    if held and prior.exists():
        m = PRIOR_RECORD.search(prior.read_text(encoding="utf-8"))
        # `--redesign`: the chrome or the markup moved and the material did not (Bill, 2026-10-16).
        if m and (m.group(1) == rec or REDESIGN):
            return held, False
    out_dir = SITE / "reports" / iso3
    return editions.next_edition(out_dir, f"{iso3}-maturity", date.today().isoformat(),
                                 current=held), True


def write_pdf(iso3: str, edition: str, page_html: str, canonical: str) -> None:
    """Beside the place's other report PDFs, under `reports/`, where `r2-sync.py` and the Worker
    already take dated editions. Relative links are made absolute: a PDF has no site around it."""
    from urllib.parse import urljoin
    from weasyprint import HTML  # imported late: only a cut needs it
    page_html = re.sub(r'(<a\b[^>]*?\bhref=")(?!https?:|mailto:|#)([^"]*)"',
                       lambda m: f'{m.group(1)}{urljoin(canonical, m.group(2))}"', page_html)
    out = SITE / "reports" / iso3 / f"{iso3}-maturity-{edition}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    base = (OUT / "countries" / iso3.lower()).as_uri() + "/"
    HTML(string=page_html, base_url=base).write_pdf(out)


METHOD_CHAPTER = "Method"

METHOD_INTRO = """## The scale

Each studied indicator places each of the 54 countries on one five-stage scale. The stages are ordinal: 4 is above 3, not twice 2. The assessment is not a score or a ranking, and nothing is averaged.

{scale}

## No evidence and unplaced

**No evidence** means nothing found states any of the facts the ladder tests. **Unplaced** means evidence was found but it meets no rung, so no stage is set. On the map *no evidence* is left unfilled and *unplaced* is grey. Neither is stage 1: *Absent* needs a dated source that says the thing does not exist.

## How a stage is set

Each indicator is studied whole, across all 54 countries. A study first settles what the indicator covers and splits it into sub-indicators where one label hides two things. It then fixes a ladder: for each stage, the value each coverage aspect must reach. A country is placed on the highest rung whose every test its evidence meets; between two rungs it takes the lower. Every fact carries its date, and a fact older than three years at the as-at date prints its year. A second drafter restages a sample blind, and a rung read two ways is rewritten.

Stages are taken as at the end of a month. A stage changes only on a dated source inside the window; a change from a re-read or a corrected ladder is marked *reassessed* and is not counted as movement.
"""


def indicator_name(study: dict, sub: dict) -> str:
    """What the map and the methodology page call a sub-indicator: the indicator's own name, the
    part of `text` before the colon *(Bill, 2026-10-16)*. A study of several sub-indicators keeps
    the sub-indicator's label after it, or its rows would read alike."""
    name = sub["text"].split(": ", 1)[0]
    return f"{name}: {sub['label']}" if len(study["sub_indicators"]) > 1 else name


def ladder_digest(section: str) -> str:
    """What a sub-indicator's `criteria_of` records: the study's ladder its criteria were written from."""
    lines = "\n".join(ln.strip() for ln in section.strip().splitlines())
    return hashlib.sha256(lines.encode("utf-8")).hexdigest()[:12]


def criteria_table(sub: dict) -> str:
    """The ladder as the methodology page prints it *(Bill, 2026-10-09)*: Stage and Criteria, a
    sentence or two a stage. The sentences are `study.json` -> `criteria`, written by hand from the
    study's three-aspect ladder, which stays the instrument the stagers work from; the map's sidebar
    prints the same sentences. `problems()` stops the build when that ladder has moved since they
    were written."""
    return "| Stage | Criteria |\n|---|---|\n" + "\n".join(
        f'| {s["n"]} {s["label"]} | {text} |' for s, text in zip(STAGES, sub["criteria"]))


def norm_statement(norm: str) -> str:
    """The norm's first paragraph: what the norm is. The study's argument about what it fails to
    measure follows it in the study file and is not printed *(Bill, 2026-10-09)*."""
    return re.split(r"\n\s*\n", norm.strip())[0]


def method_page(data: dict, studies: list[dict]) -> str:
    """The country report's order *(Bill, 2026-10-13)*: a bar of every chapter, and each chapter
    opens on a bar of its topics. The method itself is the first chapter; an indicator's anchor is
    its id, which the map and the country reports link to."""
    scale = "| Stage | Label | Meaning |\n|---|---|---|\n" + "\n".join(
        f'| {s["n"]} | {s["label"]} | {s["desc"]} |' for s in STAGES)
    intro = sections(METHOD_INTRO.format(scale=scale), "## ")
    subs = {sub["indicator_id"]: (s, sub) for s in studies for sub in s["sub_indicators"]}
    chapters = {}
    for t in data["topics"]:
        chapters.setdefault(t["group"], []).append(t)
    chapter_bar = toc("Chapters", [(METHOD_CHAPTER, f"chapter-{slug(METHOD_CHAPTER)}")]
                      + [(c, f"chapter-{slug(c)}" if any(t["studied"] for t in ts) else None)
                         for c, ts in chapters.items()])
    parts = [f'    <h2 class="mat-report__chapter" id="chapter-{slug(METHOD_CHAPTER)}">{METHOD_CHAPTER}</h2>',
             toc("Topics", [(h, f"topic-{slug(h)}") for h, _ in intro])]
    for h, text in intro:
        parts.append(f'    <h3 class="mat-report__topic" id="topic-{slug(h)}">{html.escape(h)}</h3>\n{md(text)}')
    for t in data["topics"]:
        studied = [i for i in t["indicators"] if i["studied"] and i["id"] in subs]
        if not studied:
            continue
        first = next(o for o in chapters[t["group"]] if o["studied"])
        if t is first:
            parts.append(f'    <h2 class="mat-report__chapter" id="chapter-{slug(t["group"])}">'
                         f'{html.escape(t["group"])}</h2>')
            parts.append(toc("Topics", [(o["name"], f"topic-{slug(o['name'])}" if o["studied"] else None)
                                        for o in chapters[t["group"]]]))
        parts.append(f'    <h3 class="mat-report__topic" id="topic-{slug(t["name"])}">{html.escape(t["name"])}</h3>')
        for i in studied:
            iid = i["id"]
            s, sub = subs[iid]
            p = s["issued"] / f"{iid}.md"
            text = p.read_text(encoding="utf-8") if p.exists() else ""
            secs = dict(sections(text, "## "))
            parts.append(f'<section class="mat-method__ind" id="{iid}">\n<h4>{html.escape(indicator_name(s, sub))}</h4>\n'
                         + md("##### The norm\n\n" + norm_statement(secs.get("The norm", "Not yet written."))
                              + "\n\n##### The ladder\n\n" + criteria_table(sub))
                         + "\n</section>")
    about, panel = info("Methodology")   # the section's one ⓘ (Bill, 2026-10-22)
    # The title, the section bar and the chapters pin under the site chrome, as on every
    # Methodology page (Bill, 2026-10-22).
    body = f"""  <div class="container">
    <div class="report-head report-head--page">
    <header class="article-header">
      <h1 class="article-header__title">Maturity Assessment: methodology{about}</h1>
    </header>
    {panel}
{methodology.see_also("methodology/maturity/")}
{chapter_bar}
    </div>
    <article class="article-body mat-method">
{chr(10).join(parts)}
    </article>
  </div>"""
    return page(title="Methodology — Maturity Assessment",
                description="How the Maturity Assessment places countries on its five-stage scale, indicator by indicator.",
                canonical=f"{SITE_BASE}/methodology/maturity/", depth=2, body=body,
                body_class="mat-method-page", sheets=("methodology.css", "maturity.css"),
                scripts=script("report-head.js", 2),
                active="methodology")


# ---------------------------------------------------------------------------

def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return
    path.write_text(text, encoding="utf-8", newline="\n")


def csv_bytes(rows: list[dict], fields: list[str]) -> bytes:
    """LF whatever the platform: these become editions, and a file differing only in its line
    endings is still a new edition (RENDER.md -> The finance tables)."""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, restval="", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


def download_files(studies: list[dict]) -> dict[str, bytes]:
    """{stem: bytes}: one file per studied indicator that has rows, and `maturity-all`."""
    files, allrows = {}, []
    for s in studies:
        for sub in s["sub_indicators"]:
            rows = [r for r in s["rows"] if r["indicator_id"] == sub["indicator_id"]]
            allrows += rows
            if rows:
                files[sub["indicator_id"]] = csv_bytes(rows, list(rows[0].keys()))
    if allrows:
        files["maturity-all"] = csv_bytes(allrows, list(dict.fromkeys(k for r in allrows for k in r)))
    return files


def preview_downloads(studies: list[dict]) -> int:
    """Before launch: the same files, undated, outside `site/`, for Bill to check. Compared without
    regard to line endings, so a checkout that holds them with CRLF is not rewritten."""
    files = download_files(studies)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    for stem, body in files.items():
        path = PREVIEW / f"{stem}.csv"
        if not path.exists() or path.read_bytes().replace(b"\r\n", b"\n") != body:
            try:
                path.write_bytes(body)
            except PermissionError:   # open in Excel for checking: a check copy, so it waits for the next run
                print(f"maturity: {path.name} is locked (open elsewhere?); left as it was")
    return len(files)


def publish_downloads(studies: list[dict]) -> tuple[dict[str, str], str]:
    """At launch: each file as a dated edition beside the map (`design.md` §9). Returns the names
    the page links, `{indicator_id: file, "all": file}`, and the map page's `dl-artefact` lines.
    A new edition is cut only when the bytes have moved, and the map page is the record of the
    last one, so this runs before that page is rewritten."""
    names, metas = {}, []
    for stem, body in download_files(studies).items():
        path, _ = editions.publish(body, OUT, stem, ".csv", page=OUT / "index.html")
        names["all" if stem == "maturity-all" else stem] = path.name
        metas.append(editions.artefact_meta(stem, editions.edition_of(path.stem) or "", editions.digest(body)))
    return names, "".join(m + "\n" for m in metas)


def main() -> int:
    studies = load_studies()
    indicators = read_csv(ROOT / "lookups" / "indicators.csv")
    countries = read_csv(ROOT / "lookups" / "countries.csv")
    data = build_data(studies, indicators, countries)
    geo = africa_geo()

    live = OUT / "data" / "maturity.json"
    wrong = problems(data, geo, studies, indicators,
                     json.loads(live.read_text(encoding="utf-8")) if live.exists() else None)
    if wrong:
        print(f"maturity: {len(wrong)} problem(s), nothing written:")
        for line in wrong:
            print(f"  {line}")
        return 1

    if LAUNCHED:
        data["downloads"], artefacts = publish_downloads(studies)
        k, where = len(data["downloads"]), "editions -> site/maturity/"
    else:
        artefacts = ""
        k, where = preview_downloads(studies), "preview CSVs -> maturity/preview-downloads/"

    write(live, json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    write(OUT / "data" / "africa.json", json.dumps(geo, separators=(",", ":")))
    write(OUT / "index.html", map_page(data["downloads"], artefacts))

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
    ids = sum(len(s["sub_indicators"]) for s in studies)
    print(f"maturity: {len(studies)} study, {ids} indicators -> site/maturity/ + {n} country reports"
          f" + site/methodology/maturity/; {k} {where}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
