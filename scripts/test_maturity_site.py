#!/usr/bin/env python3
r"""test_maturity_site.py — the maturity map's build: its check, its geography and its launch.

    python scripts/test_maturity_site.py

Runs `maturity-site.py` against the live studies but writes only to a temporary folder. Three
things are exercised: `problems()` is silent on the build as it stands and speaks when a piece
is taken away; the thinned geography keeps every country and the way each ring winds; and with
`LAUNCHED` set the downloads are cut as dated editions once, not on every run.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
_spec = importlib.util.spec_from_file_location("ms", HERE / "maturity-site.py")
ms = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ms)

fails: list[str] = []


def check(label, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
    if not ok:
        fails.append(label)
        if detail:
            print(f"          {detail}")


def build():
    studies = ms.load_studies()
    indicators = ms.read_csv(ms.ROOT / "lookups" / "indicators.csv")
    countries = ms.read_csv(ms.ROOT / "lookups" / "countries.csv")
    return studies, indicators, ms.build_data(studies, indicators, countries)


def main() -> int:
    studies, indicators, data = build()
    geo = ms.africa_geo()

    print("the check")
    found = ms.problems(data, geo, studies, indicators, data)
    check("the build as it stands has no problems", not found, "; ".join(found[:3]))
    iid = next(iter(data["indicators"]))
    iso = next(iter(data["cells"][iid]))

    d = copy.deepcopy(data)
    del d["cells"][iid][iso]
    check("a country without a row is named", any(iso in p for p in ms.problems(d, geo, studies, indicators, data)))

    bare = copy.deepcopy(studies)
    del bare[0]["sub_indicators"][0]["criteria"]
    check("an indicator without criteria is named",
          any("criteria" in p for p in ms.problems(data, geo, bare, indicators, data)))
    check("the sidebar's ladder is the criteria",
          all([l["text"] for l in data["indicators"][sub["indicator_id"]]["ladder"]] == sub["criteria"]
              for s in studies for sub in s["sub_indicators"]))

    d = copy.deepcopy(data)
    staged = next(k for k, c in d["cells"][iid].items() if c["state"] == "staged")
    d["cells"][iid][staged]["summary"] = ""
    check("a staged country with no section is named",
          any(staged in p for p in ms.problems(d, geo, studies, indicators, data)))

    d = copy.deepcopy(data)
    for t in d["topics"]:
        t["indicators"] = [i for i in t["indicators"] if i["id"] != iid]
    check("an indicator in no topic is named",
          any("no topic" in p for p in ms.problems(d, geo, studies, indicators, data)))

    published = copy.deepcopy(data)
    published["indicators"]["gone--indicator"] = {}
    check("an indicator dropped from the published map is named",
          any("gone--indicator" in p for p in ms.problems(data, geo, studies, indicators, published)))

    moved = copy.deepcopy(studies)
    moved[0]["sub_indicators"][0]["criteria_of"] = "0" * 12
    check("criteria written from an earlier ladder are named",
          any("criteria" in p for p in ms.problems(data, geo, moved, indicators, data)))
    page = ms.method_page(data, studies)
    check("the methodology ladder is Stage and Criteria only",
          page.count("<th>Criteria</th>") == len(data["indicators"]) and "<th>Tiers</th>" not in page)
    check("the norm prints its statement and not the argument", "It does not measure" not in page)

    check("no study at all is a problem", bool(ms.problems(data, geo, [], indicators, None)))

    g = copy.deepcopy(geo)
    g["features"] = [f for f in g["features"] if f["properties"]["iso3"] != iso]
    check("a country with no shape is named", any(iso in p for p in ms.problems(data, g, studies, indicators, data)))

    print("the geography")
    source = {(f["properties"].get("iso3") or f["properties"].get("ISO3166-1-Alpha-3")): f["geometry"]
              for f in json.loads(ms.GEO.read_text(encoding="utf-8"))["features"]}
    check("every country keeps a shape", all(f["geometry"]["coordinates"] for f in geo["features"]))
    turned, shrunk = [], []
    for f in geo["features"]:
        code, src = f["properties"]["iso3"], source[f["properties"]["iso3"]]
        polys = src["coordinates"] if src["type"] == "MultiPolygon" else [src["coordinates"]]
        sign = {ms.area(p[0]) > 0 for p in polys if abs(ms.area(p[0])) >= ms.GEO_TOLERANCE ** 2}
        if {ms.area(p[0]) > 0 for p in f["geometry"]["coordinates"]} - sign:
            turned.append(code)
        was = sum(abs(ms.area(p[0])) for p in polys if abs(ms.area(p[0])) >= ms.GEO_TOLERANCE ** 2)
        now = sum(abs(ms.area(p[0])) for p in f["geometry"]["coordinates"])
        if abs(now - was) > 0.01 * was:
            shrunk.append(code)
    check("no ring winds the other way", not turned, " ".join(turned))
    check("no country's drawable area moves by more than 1%", not shrunk, " ".join(shrunk))
    check("a ring too small to draw is dropped", ms.thin_ring([[0, 0], [0.001, 0], [0, 0.001], [0, 0]], 0.02) == [])

    print("the launch")
    with tempfile.TemporaryDirectory() as tmp:
        ms.OUT, ms.LAUNCHED = Path(tmp), True
        try:
            names, metas = ms.publish_downloads(studies)
            page = ms.map_page(names, metas)
            (ms.OUT / "index.html").write_text(page, encoding="utf-8")
            check("an edition per indicator and one for all",
                  set(names) == set(data["indicators"]) | {"all"}, str(sorted(names)))
            check("every name is dated", all(ms.editions.edition_of(Path(n).stem) for n in names.values()))
            body = (ms.OUT / names["all"]).read_bytes()
            check("the files are LF", b"\r" not in body)
            check("the all file holds every row", body.count(b"\n") - 1 == sum(len(s["rows"]) for s in studies))
            check("the page records each edition", all(f"{Path(n).stem.rsplit('-', 3)[0]}|" in page
                                                       for n in names.values()))
            check("the page links the all file and has no disabled button",
                  f'href="{names["all"]}"' in page and "disabled" not in page)
            check("the page is indexable at launch", "noindex" not in page)

            again, _ = ms.publish_downloads(studies)
            check("a second run cuts no new edition", again == names, str(again))
            for f in ms.OUT.glob("*.csv"):
                f.unlink()      # as `r2-sync.py --prune-local` leaves the tree
            pruned, _ = ms.publish_downloads(studies)
            check("nor does a run after the tree is pruned", pruned == names and not list(ms.OUT.glob("*.csv")),
                  str(pruned))
        finally:
            ms.LAUNCHED = False

    print(f"\n{len(fails)} failed" if fails else "\nall ok")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
