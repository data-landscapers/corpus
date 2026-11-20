#!/usr/bin/env python3
"""whos-who-publish.py — the Who's Who page, its search data and its download.

    python scripts/whos-who-publish.py          -> outputs/whos-who/whos-who.csv
                                                   site/whos-who/index.html
                                                   site/whos-who/whos-who.csv, -metadata.csv
                                                   site/whos-who/data/index.json, src-NNN.json
    python scripts/whos-who-publish.py --check  # build in memory, report, write nothing

`documentation/whos-who.md` §8 and §8a are the design; stage 5 is this file. It reads
`build/whos-who/positions.csv` (written by `whos-who-people.py`) and the lookups beside it,
and runs after them in `rebuild.py` stage 2e.

**A published row is six fields** — `name`, `year`, `position`, `organisation`, `country`,
`source_url` — and this is the one place they are cut. `country` is the organisation's, never
the person's (Bill asked for it, 2026-11-20). `year` is the attested year, or
`2015–2019` where the source states a term. A `held` row without a stated term reads
*Minister of Finance (former)*, §5. Suppressed people and pairs are dropped here again,
whatever `positions.csv` holds.

**The page shows nothing until the reader searches** *(Bill, 2026-11-20)*, so the search
data is fetched on first use, not with the page. It is the catalogue's split:

- `data/index.json`, everything a search, a filter or a row needs except the source URL:
  people (published name and every alias), organisations (name, place, lineage group),
  positions, and the rows as columns of offsets.
- `data/src-NNN.json`, the source URLs, keyed by the catalogue's append-only document id
  in blocks of 1,000. A block changes only when a source in its range is first cited, so a
  nightly build rewrites one or two of them rather than all. The page fetches the blocks a
  row panel or a filtered download needs.

**No `person_id` reaches the site.** People are listed in name order and a row points at
a position in that list, which is renumbered by every build and means nothing outside it
(§8a). The chunk files are internal and carry no stability promise; `whos-who.csv` is the
supported download, undated and current-only, `design.md` §9's named exception.

**The page is `noindex` and in no navigation** until Bill launches it *(Bill, 2026-11-20)*;
`sitemap.py` leaves a `noindex` page out. Launch drops `ROBOTS` and adds the nav item,
the method section and the change-log entry.
"""
from __future__ import annotations

import argparse
import collections
import csv
import gzip
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import whos_who_lib as W  # noqa: E402
from chrome_lib import (MAIN_SITE, SITE_BASE, chrome, external_links, feedback,  # noqa: E402
                        feedback_href, foot, ga, info, script, styles)

ROOT = W.ROOT
POSITIONS = ROOT / "build" / "whos-who" / "positions.csv"
PEOPLE = ROOT / "lookups" / "people.csv"
ALIASES = ROOT / "lookups" / "person-aliases.csv"
SUPPRESS = ROOT / "lookups" / "whos-who-suppress.csv"
DOC_IDS = ROOT / "outputs" / "catalogue" / "doc-ids.csv"
OUT = ROOT / "outputs" / "whos-who" / "whos-who.csv"
SITE = ROOT / "site" / "whos-who"
DATA = SITE / "data"

COLS = ["name", "year", "position", "organisation", "country", "source_url"]
BLOCK = 1000                       # source ids per src-NNN.json
SEP = "; "                         # between the source URLs of one published row
URL = f"{SITE_BASE}/whos-who/"
ROBOTS = '<meta name="robots" content="noindex, nofollow">\n'

# What every view and the download say the rows are (§8a). One copy: the page, the
# metadata file and, at launch, the method section all quote it.
CAUTION = ("Each row is what one or more sources say for one year. The list holds what our sources "
           "happen to say, with gaps: a missing row is not a vacant post, and an "
           "organisation's rows are not a line of succession.")

FIELDS = [
    ("name", "The person's name, in the fullest form the sources give."),
    ("year", "The year the source attests, or the term it states (2015–2019). "
             "Not a term of office."),
    ("position", "The title as the source gives it. (former) marks a source describing "
                 "a past holder."),
    ("organisation", "The organisation, under the name it had. Government bodies carry "
                     "their country."),
    ("country", "The organisation's country, or its region for a regional or global body. "
                "Not the person's nationality."),
    ("source_url", "The publisher's own pages making the statement, separated by '; '."),
]


def read(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def year_of(r: dict) -> str:
    y, z = r["year"], r["year_to"]
    return f"{y}–{z}" if z and z != y else y


def position_of(r: dict) -> str:
    p = r["position"]
    return f"{p} (former)" if r["tense"] == "held" and not r["year_to"] else p


def position_key(p: str) -> str:
    """What two written forms of one title share: no case, accents, hyphens or extra spaces.
    *Secretary-General*, *Secretary General* and *secretary‑general* are one title;
    *secrétaire général* is French and stays its own (§5)."""
    return " ".join(re.sub(r"[-‐‑‒–—]", " ", W.fold(p)).split())


def lineage_groups(slugs: set[str]) -> dict[str, str]:
    """canonical slug -> the slug its lineage group is known by, so selecting any name a
    ministry has had selects them all (§8a). Union-find over `org-lineage.csv`."""
    parent = {s: s for s in slugs}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for r in read(W.LINEAGE):
        a, b = find(r["slug"]), find(r["successor_slug"])
        if a != b:
            parent[max(a, b)] = min(a, b)
    return {s: find(s) for s in slugs}


def build() -> dict:
    orgs = {r["slug"]: r for r in read(W.ORGS)}
    people = {r["person_id"]: r["name"] for r in read(PEOPLE) if r["name"]}
    aliases = collections.defaultdict(set)
    for r in read(ALIASES):
        aliases[r["person_id"]].add(r["alias"])
    gone_people, gone_pairs = set(), set()
    for r in read(SUPPRESS):
        (gone_pairs.add((r["person_id"], r["slug"])) if r["slug"]
         else gone_people.add(r["person_id"]))
    cat = W.catalogue()
    doc_id = {r["slug"]: int(r["id"]) for r in read(DOC_IDS)}
    places = W.countries()
    person_names = {W.fold(n) for n in people.values()} | {W.fold(a) for s in aliases.values() for a in s}

    facts, dropped = [], collections.Counter()
    for r in read(POSITIONS):
        pid = r["person_id"]
        canon = orgs.get(r["slug"], {}).get("canonical_slug") or r["slug"]
        if pid in gone_people or (pid, r["slug"]) in gone_pairs or (pid, canon) in gone_pairs:
            dropped["suppressed"] += 1
            continue
        if pid not in people:
            dropped["no published name"] += 1
            continue
        if canon not in orgs:
            dropped["organisation not in organisations.csv"] += 1
            continue
        if W.fold(orgs[canon]["name"]) in person_names:
            dropped["organisation is a person's tag"] += 1      # *Abdelmadjid Tebboune*
            continue
        item = cat.get(r["source_url"])
        if not item or item.get("slug") not in doc_id:
            dropped["source not in the catalogue"] += 1
            continue
        facts.append((pid, canon, year_of(r), int(r["year"]), position_of(r),
                      r["source_url"], doc_id[item["slug"]]))

    # One row per person, position, organisation and year, its sources joined (Bill,
    # 2026-11-20). The cache and positions.csv stay one row a source, which is what ids
    # anchor on; only the published row is collapsed. Positions group on case, accents,
    # hyphens and spacing, and publish under the form the sources use most.
    grouped = collections.defaultdict(list)
    for f in facts:
        grouped[(f[0], f[1], f[2])].append(f)
    rows = []
    for (pid, canon, year), fs in grouped.items():
        for fs, forms, parts in same_titles(fs, orgs[canon]["name"]):
            position = min(forms, key=lambda t: (
                not W.is_english(t), -len(parts[t]), not t[:1].isupper(),
                sum(1 for w in re.findall(r"\w+", t) if len(w) > 1 and w.isupper()),
                len(t.split()), -forms[t], t))
            rows.append(row_of(pid, canon, year, position, fs, people, orgs, places))
    rows.sort(key=lambda x: (W.fold(x["name"]), x["y0"], W.fold(x["organisation"]),
                             W.fold(x["position"])))
    return finish(rows, people, aliases, orgs, places, dropped)


def same_titles(fs: list, organisation: str):
    """Split one person's facts at one organisation in one year into titles: two written
    positions are one title when they share a part (`W.title_parts`), and the sharing
    chains, so *DG* and *CEO* meet through *Director General and CEO*. Yields each title's
    facts, its written forms counted, and each form's parts."""
    ow = W.org_words(organisation)
    forms = collections.Counter(f[4] for f in fs)
    parts = {t: W.title_parts(t, owords=ow) or frozenset({position_key(t)}) for t in forms}
    up = {t: t for t in forms}

    def find(t):
        while up[t] != t:
            t = up[t]
        return t
    owner = {}
    for t in sorted(forms):
        for k in parts[t]:
            if k in owner:
                a, b = find(owner[k]), find(t)
                if a != b:
                    up[max(a, b)] = min(a, b)
            else:
                owner[k] = t
    groups = collections.defaultdict(list)
    for f in fs:
        groups[find(f[4])].append(f)
    for g in groups.values():
        fc = collections.Counter(f[4] for f in g)
        yield g, fc, {t: parts[t] for t in fc}


def row_of(pid, canon, year, position, fs, people, orgs, places) -> dict:
    src = sorted({(f[6], f[5]) for f in fs})
    return {"pid": pid, "org": canon, "name": people[pid], "year": year,
            "y0": fs[0][3], "position": position,
            "organisation": orgs[canon]["name"],
            "country": places.get(orgs[canon]["place"], orgs[canon]["place"]),
            "source_url": SEP.join(u for _, u in src), "sids": [i for i, _ in src],
            "urls": dict(src)}


def finish(rows, people, aliases, orgs, places, dropped) -> dict:
    # People in name order; the index is all a row carries, and it is renumbered every build.
    pids = sorted({x["pid"] for x in rows}, key=lambda p: (W.fold(people[p]), p))
    p_ix = {p: i for i, p in enumerate(pids)}
    org_slugs = sorted({x["org"] for x in rows}, key=lambda s: (W.fold(orgs[s]["name"]), s))
    o_ix = {s: i for i, s in enumerate(org_slugs)}
    group = lineage_groups(set(org_slugs))
    abbrev = collections.defaultdict(list)            # searched, never shown
    for r in W.read_csv(W.ABBREV, W.ABBREV_COLS):
        c = orgs.get(r["slug"], {}).get("canonical_slug", r["slug"])
        if r["abbreviation"] not in abbrev[c]:
            abbrev[c].append(r["abbreviation"])
    positions = sorted({x["position"] for x in rows}, key=W.fold)
    t_ix = {p: i for i, p in enumerate(positions)}
    used_places = sorted({orgs[s]["place"] for s in org_slugs if orgs[s]["place"]},
                         key=lambda c: places.get(c, c))

    index = {
        "block": BLOCK,
        "places": {c: places.get(c, c) for c in used_places},
        "orgs": [[orgs[s]["name"], orgs[s]["place"], o_ix.get(group[s], o_ix[s])]
                 + ([abbrev[s]] if abbrev.get(s) else []) for s in org_slugs],
        "people": [[people[p], sorted(a for a in aliases[p] if a != people[p])] for p in pids],
        "positions": positions,
        "rows": {"p": [p_ix[x["pid"]] for x in rows], "o": [o_ix[x["org"]] for x in rows],
                 "t": [t_ix[x["position"]] for x in rows], "y": [x["year"] for x in rows],
                 "s": [x["sids"] for x in rows]},
        "count": len(rows),
    }
    blocks = collections.defaultdict(dict)
    for x in rows:
        for sid, url in x["urls"].items():
            blocks[sid // BLOCK][str(sid)] = url
    return {"rows": rows, "index": index, "blocks": blocks, "dropped": dropped,
            "people": len(pids), "orgs": len(org_slugs), "sources": len({i for x in rows for i in x["sids"]})}


def csv_text(cols, rows) -> str:
    import io
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(cols)
    w.writerows(rows)
    return buf.getvalue()


def write_if_changed(path: Path, text: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return True


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Who's Who — Data Landscapers</title>
<meta name="description" content="Who held which position at which organisation in Africa's digital public sector, with the source that says so.">
<link rel="canonical" href="{url}">
{robots}{styles}
<link rel="icon" href="{main}/assets/favicon.svg" type="image/svg+xml">
{ga}
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container whos-who">
    <header class="article-header">
      {feedback}
      <div class="ww-head">
        <h1 class="article-header__title">Who's Who{info_btn}</h1>
        <p class="ww-stats">{people:,} people · {orgs:,} organisations · {count:,} rows · {sources:,} sources</p>
      </div>
    </header>
    {info_panel}

    <p class="ww-caution">{caution}</p>

    <!-- The search bar and the status stay put while the rows scroll; the table parks
         its header beneath them (`data-dt-above`, datatable v6). -->
    <div class="ww-bar" data-dt-above>
    <form class="ww-search dt-controls" role="search" onsubmit="return false">
      <input type="search" id="ww-q" class="dt-search" placeholder="Name, position or organisation" aria-label="Search names, positions and organisations" autocomplete="off">
      <select id="ww-place" aria-label="Country"><option value="">All countries</option>{place_opts}</select>
      <input type="search" id="ww-org" list="ww-orgs" placeholder="Organisation" aria-label="Organisation" autocomplete="off">
      <datalist id="ww-orgs"></datalist>
      <a class="btn btn--sm" href="whos-who.csv" download>&darr; All rows</a>
      <button type="button" class="btn btn--sm" id="ww-dl" disabled>&darr; These rows</button>
      <a class="btn btn--sm" href="whos-who-metadata.csv" download>&darr; Metadata</a>
    </form>

    <p class="ww-status" id="ww-status" aria-live="polite">Search at least three letters, or choose a country or an organisation.</p>
    </div>
    <div id="ww-results" class="ww-results"></div>

    <p class="ww-correct">Something wrong, or a row about you that you want removed? <a href="{correct}">Write to us</a>.</p>

    <noscript><p>The search needs JavaScript. Every row is in the <a href="whos-who.csv">full download</a>.</p></noscript>
  </div>
  </main>

{foot}

{datatable_js}
{whos_who_js}
</div>
</body>
</html>
"""


def page(b: dict) -> str:
    opts = "".join(f'<option value="{html.escape(c)}">{html.escape(n)}</option>'
                   for c, n in b["index"]["places"].items())
    return external_links(PAGE.format(
        url=URL, robots=ROBOTS, styles=styles(1, "datatable.css", "whos-who.css"),
        main=MAIN_SITE, ga=ga(), chrome=chrome(None, depth=1),
        feedback=feedback("Who's Who", URL), caution=html.escape(CAUTION),
        info_btn=info("Who's Who")[0], info_panel=info("Who's Who")[1],
        people=b["people"], orgs=b["orgs"], count=len(b["rows"]), sources=b["sources"],
        place_opts=opts,
        correct=feedback_href("Who's Who correction or removal", URL),
        foot=foot(depth=1), datatable_js=script("datatable.js", 1),
        whos_who_js=script("whos-who.js", 1)))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="build in memory and report")
    a = ap.parse_args(argv)
    b = build()
    out = csv_text(COLS, [[x[c] for c in COLS] for x in b["rows"]])
    idx = json.dumps(b["index"], ensure_ascii=False, separators=(",", ":"))
    print(f"whos-who-publish: {len(b['rows']):,} rows, {b['people']:,} people, "
          f"{b['orgs']:,} organisations, {b['sources']:,} sources; "
          f"index {len(gzip.compress(idx.encode())):,} bytes compressed")
    for why, n in b["dropped"].most_common():
        print(f"  dropped {n:,}: {why}")
    if a.check:
        return 0
    meta = csv_text(["field", "meaning"], FIELDS + [("(all)", CAUTION)])
    wrote = [p for p, t in ((OUT, out), (SITE / "whos-who.csv", out),
                            (SITE / "whos-who-metadata.csv", meta),
                            (DATA / "index.json", idx), (SITE / "index.html", page(b)))
             if write_if_changed(p, t)]
    keep = set()
    for k, urls in b["blocks"].items():
        p = DATA / f"src-{k:03d}.json"
        keep.add(p.name)
        if write_if_changed(p, json.dumps(dict(sorted(urls.items(), key=lambda kv: int(kv[0]))),
                                          ensure_ascii=False, separators=(",", ":"))):
            wrote.append(p)
    for p in DATA.glob("src-*.json"):
        if p.name not in keep:
            p.unlink()
            wrote.append(p)
    print(f"  wrote {len(wrote)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
