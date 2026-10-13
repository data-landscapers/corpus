#!/usr/bin/env python3
r"""study-internet-carry.py — the held internet-use figures, carried into the internet usage study.

    python scripts/study-internet-carry.py
    python scripts/study-internet-carry.py --dry

`maturity/documentation/maturity-study-method.md` §4: **start from what is already paid
for**, as `study-nonstate-carry.py` does for the finance tables and `study-mobile-carry.py`
for phone ownership. `reference/measures.csv` holds the International Telecommunication
Union's series of people who use the internet (SDG 17.8.1), so
`maturity-study-internetusage.md`'s four questions are answered for the countries it covers
with no document opened:

- `users` = `survey:{per cent}` or `estimate:{per cent}`: one fact per country and year
  from `FROM`, dated by the figure's own year, or the country's latest where it has none
  since. `nature` in the file says which it is; a figure the file marks `suspect` is not
  carried.

**The source is the reference series, which is data and not a record in `raw/`.** A fact is
filed under `ref:{dataset}@{release}`, the form `maturity-assess.py` cites the same figure
in, with the dataset's address from `maturity-render.py`; `study_lib.reference_held()` is
what lets `lint-study.py` pass it as held.

Each country's facts go in one file, `evidence/{ISO3}/facts/{n}.json`, under a row appended
to `readlist.csv` as `why = carried`. Run it after `study-select.py` and before the
drafters. A facts file already there is left alone.

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

STUDY = "internetusage"
SUB, CLASS = "use", "use"
DATASET = "itu-sdg-17-8-1-internet-use"
FROM = 2021
SAID = {"survey": "a survey figure the country reported to the International Telecommunication Union",
        "estimate": "an estimate by the International Telecommunication Union"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Carry the held internet-use figures into the study.")
    ap.add_argument("--dry", action="store_true", help="print the counts, write nothing")
    a = ap.parse_args(argv)
    try:
        study_lib.load(STUDY)
        slugs, urls = study_lib.reference_held()
    except study_lib.StudyError as e:
        print(f"study-internet-carry: {e}")
        return 2
    held = [r for r in study_lib.read_csv(os.path.join(study_lib.CORPUS, "reference", "measures.csv"))
            if r["dataset"] == DATASET and r["nature"] != "suspect"]
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
            print(f"study-internet-carry: {slug} is not a reference study_lib holds")
            return 2
        facts = []
        for r in mine_rows:
            nature = r["nature"] if r["nature"] in SAID else "estimate"
            facts.append({"sub_indicator": SUB, "aspect": "users", "value": f"{nature}:{r['value']}",
                          "fact": f"{r['value']} per cent of the population of "
                                  f"{names[iso]['name']} used the internet in {r['year']}, "
                                  f"{SAID[nature]}.",
                          "as_of": r["year"], "date_precision": "year",
                          "system": "People who use the internet (SDG 17.8.1)", "class": CLASS})
            count[nature] += 1
        count["countries"] += 1
        path = os.path.join(base, iso, "readlist.csv")
        rows = study_lib.read_csv(path)
        n = next((str(r["n"]) for r in rows if r.get("slug") == slug), "")
        if not n:
            n = str(max([int(r["n"]) for r in rows if str(r.get("n") or "").isdigit()] or [0]) + 1)
            rows.append({"n": n, "slice": "", "pass": "carried", "tier": "", "iso3": iso,
                         "kind": "raw", "slug": slug, "read": "", "path": "reference/measures.csv",
                         "url": urls[slug], "title": "ITU, internet use (SDG 17.8.1)",
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
    print("study-internet-carry: " + ", ".join(f"{k}: {count[k]}" for k in ("countries", "survey", "estimate"))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
