#!/usr/bin/env python3
r"""study-gridreliability-carry.py — the held outage figures, carried into the grid reliability study.

    python scripts/study-gridreliability-carry.py
    python scripts/study-gridreliability-carry.py --dry

`maturity/documentation/maturity-study-method.md` §4: **start from what is already paid
for**, as `study-gridreliability-carry.py` does. `reference/measures.csv` holds the World Bank
Enterprise Surveys' outages in a typical month, so `maturity-study-gridreliability.md`'s four
questions are answered for the countries it covers with no document opened:

- `outages` = `survey:{outages a month}`: one fact per country and survey year from `FROM`,
  or the country's latest where it has none since. A regulator's or utility's SAIFI comes
  from the documents the frame cites, read by drafters, not from here.

**The source is the reference series, which is data and not a record in `raw/`.** A fact is
filed under `ref:{dataset}@{release}`, as `study-mobile-carry.py` files its own.

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

STUDY = "gridreliability"
SUB, CLASS = "outages", "grid"
DATASET = "enterprise-surveys-outages"
FROM = 2013


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Carry the held outage figures into the study.")
    ap.add_argument("--dry", action="store_true", help="print the counts, write nothing")
    a = ap.parse_args(argv)
    try:
        study_lib.load(STUDY)
        slugs, urls = study_lib.reference_held()
    except study_lib.StudyError as e:
        print(f"study-gridreliability-carry: {e}")
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
            print(f"study-gridreliability-carry: {slug} is not a reference study_lib holds")
            return 2
        facts = []
        for r in mine_rows:
            value = round(float(r["value"]), 2)
            facts.append({"sub_indicator": SUB, "aspect": "outages", "value": f"survey:{value:g}",
                          "fact": f"Firms in {names[iso]['name']} reported {value:g} power outages "
                                  f"in a typical month in the World Bank's {r['year']} Enterprise Survey.",
                          "as_of": r["year"], "date_precision": "year",
                          "system": "World Bank Enterprise Surveys, outages in a typical month",
                          "class": CLASS})
            count["figures"] += 1
        count["countries"] += 1
        path = os.path.join(base, iso, "readlist.csv")
        rows = study_lib.read_csv(path)
        n = next((str(r["n"]) for r in rows if r.get("slug") == slug), "")
        if not n:
            n = str(max([int(r["n"]) for r in rows if str(r.get("n") or "").isdigit()] or [0]) + 1)
            rows.append({"n": n, "slice": "", "pass": "carried", "tier": "", "iso3": iso,
                         "kind": "raw", "slug": slug, "read": "", "path": "reference/measures.csv",
                         "url": urls[slug], "title": "World Bank Enterprise Surveys, power outages in a typical month",
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
    print("study-gridreliability-carry: " + ", ".join(f"{k}: {count[k]}" for k in ("countries", "figures"))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
