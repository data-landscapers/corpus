#!/usr/bin/env python3
r"""study-ictproduction-carry.py — the held ICT service export figures, carried into the ICT production study.

    python scripts/study-ictproduction-carry.py
    python scripts/study-ictproduction-carry.py --dry

`maturity/documentation/maturity-study-method.md` §4, as `study-mobile-carry.py` does it.
`reference/measures.csv` holds the World Bank's ICT service exports over GDP, so the first
three of `maturity-study-ictproduction.md`'s questions are answered with no document opened:

- `exports` = `official:{per cent of GDP}`: one fact per country and year from `FROM`, dated by
  the figure's own year, or the country's latest where it has none since.

A fact is filed under `ref:{dataset}@{release}`, as `study-mobile-carry.py` files it. Run it
after `study-select.py` and before the drafters. A facts file already there is left alone.

Exit: 0 written, 2 the study or the reference file cannot be read.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402

STUDY = "ictproduction"
SUB, CLASS = "production", "ictproduction"
DATASET = "wdi-ict-service-exports-gdp"
FROM = 2021



def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Carry the held ICT export figures into the study.")
    ap.add_argument("--dry", action="store_true", help="print the counts, write nothing")
    a = ap.parse_args(argv)
    try:
        study_lib.load(STUDY)
        slugs, urls = study_lib.reference_held()
    except study_lib.StudyError as e:
        print(f"study-ictproduction-carry: {e}")
        return 2
    held = [r for r in study_lib.read_csv(os.path.join(study_lib.CORPUS, "reference", "measures.csv"))
            if r["dataset"] == DATASET]
    names = study_lib.countries()
    base = os.path.join(study_lib.study_dir(STUDY), "evidence")
    count: collections.Counter = collections.Counter()
    for iso in sorted(names):
        mine_rows = sorted((r for r in held if r["iso3"] == iso), key=lambda r: r["year"])
        mine_rows = [r for r in mine_rows if int(r["year"]) >= FROM] or mine_rows[-1:]
        if not mine_rows:
            continue
        slug = f"ref:{DATASET}@{mine_rows[-1]['release']}"
        if slug not in slugs:
            print(f"study-ictproduction-carry: {slug} is not a reference study_lib holds")
            return 2
        facts = []
        for r in mine_rows:
            facts.append({"sub_indicator": SUB, "aspect": "exports", "value": f"official:{r['value']}",
                          "fact": f"ICT service exports from {names[iso]['name']} were {float(r['value']):g} "
                                  f"per cent of GDP in {r['year']}, by the World Bank's series.",
                          "as_of": r["year"], "date_precision": "year",
                          "system": "ICT service exports over GDP (WDI)", "class": CLASS})
            count["figures"] += 1
        count["countries"] += 1
        path = os.path.join(base, iso, "readlist.csv")
        rows = study_lib.read_csv(path)
        n = next((str(r["n"]) for r in rows if r.get("slug") == slug), "")
        if not n:
            n = str(max([int(r["n"]) for r in rows if str(r.get("n") or "").isdigit()] or [0]) + 1)
            rows.append({"n": n, "slice": "", "pass": "carried", "tier": "", "iso3": iso,
                         "kind": "raw", "slug": slug, "read": "", "path": "reference/measures.csv",
                         "url": urls[slug], "title": "World Bank WDI, ICT service exports over GDP",
                         "published": mine_rows[-1]["release"], "places": iso, "why": "carried",
                         "terms": "", "hits": 0, "words": 0})
            if not a.dry:
                study_lib.write_csv(path, study_lib.READLIST_FIELDS, rows)
        out = os.path.join(base, iso, "facts", f"{n}.json")
        if a.dry or os.path.exists(out):
            continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"slug": slug, "facts": facts, "systems": [],
                       "note": "carried from reference/measures.csv; no document opened"},
                      fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    print("study-ictproduction-carry: " + ", ".join(f"{k}: {count[k]}" for k in ("countries", "figures"))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
