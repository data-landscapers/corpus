#!/usr/bin/env python3
r"""study-ladder-itcapacity.py — the in-house capacity study's four questions, counted.

    python scripts/study-ladder-itcapacity.py --as-at 2026-09-30
    python scripts/study-ladder-itcapacity.py --as-at 2026-09-30 --dry
    python scripts/study-ladder-itcapacity.py --as-at 2026-09-30 --show KEN

`maturity/documentation/maturity-study-method.md` §7. The ladder is
`maturity-study-itcapacity.md` §2 and §3:

1. **Staff**: an `inhouse` row of `yes` inside three years.
2. **A technology body**: an `agency` row of `operating` inside three years.
3. **Built in-house**: a `built` row of `live` inside three years.
4. **Run wholly in-house**: `own` rows of `entire` naming three or more systems, inside three
   years *(Bill, 2026-10-26, message 31: the cadre is no longer asked)*.

A yes to a later question answers the earlier ones (§3.3). No question is answered no: one
body's systems run by a supplier says nothing of another's staff, so an `outsourced` row only
places a country at stage 1, and only where nothing answers yes.

A fact dated after the as-at sets nothing; a year or a month stands for its last day, and the
as-at's own year for the as-at. `corrections.csv` is applied to `evidence.csv` first, once.
Writes each `stage.json` and `ladder-test.csv`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import argparse
import calendar
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402

STUDY = "itcapacity"
QS = (("inhouse", "yes", True), ("agency", "operating", True), ("built", "live", True),
      ("own", "entire", True))
OWN = 3   # systems an `own` answer needs
GAPS = {
    "5": "",
    "4": "No sources held since October 2023 name three systems run wholly by government staff.",
    "3": "No source held says a system built by government staff went live since October 2023.",
    "2": "No source held from 2023 or later says a government body builds or runs systems for the "
         "rest of government.",
    "1": "",
}
ASPECTS = tuple(k for k, _, _ in QS)


def last_day(as_of: str) -> dt.date:
    p = [int(x) for x in as_of.split("-")]
    if len(p) == 1:
        return dt.date(p[0], 12, 31)
    if len(p) == 2:
        return dt.date(p[0], p[1], calendar.monthrange(p[0], p[1])[1])
    return dt.date(*p)


def correct(rows: list[dict], fixes: list[dict]) -> tuple[list[dict], int]:
    by_id = {f"{f['iso3']}-{f['n']}": f for f in fixes}
    out, changed = [], 0
    for r in rows:
        f = by_id.get(r["row_id"])
        if f and f["action"] == "removed":
            changed += 1
            continue
        if f and f["action"].startswith("revalued: ") and r["value"] != f["action"].split(": ", 1)[1]:
            r, changed = {**r, "value": f["action"].split(": ", 1)[1]}, changed + 1
        out.append(r)
    return out, changed


def stage(rows: list[dict], as_at: dt.date) -> dict:
    day = lambda a: as_at if a == str(as_at.year) else last_day(a)  # noqa: E731
    live = sorted(((day(r["as_of"]), r) for r in rows if day(r["as_of"]) <= as_at),
                  key=lambda p: p[0], reverse=True)
    if not live:
        return {"stage": "no evidence", "sources": [], "values": {},
                "gaps": "Nothing held says who builds or runs the government's computer systems."}
    three = study_lib.months_back(as_at, 36)
    hit = {k: next((r for d, r in live if r["aspect"] == k and r["value"] == v
                    and (not windowed or d >= three)), None) for k, v, windowed in QS}
    own = {}
    for d, r in live:
        if r["aspect"] == "own" and r["value"] == "entire" and d >= three:
            own.setdefault(r["system"].strip().lower(), r)
    if len(own) < OWN:
        hit["own"] = None
    values = {k: (v if hit[k] else "") for k, v, _ in QS}
    top = max((i + 1 for i, (k, _, _) in enumerate(QS) if hit[k]), default=0)
    if top == 0:
        out = next((r for d, r in live if r["aspect"] == "inhouse" and r["value"] == "outsourced"
                    and d >= three), None)
        if out:
            values["inhouse"] = "outsourced"
            return {"stage": "1", "sources": [out["row_id"]], "values": values, "gaps": ""}
        return {"stage": "unplaced", "sources": [], "values": values,
                "gaps": "No source held from 2023 or later says government staff run or maintain "
                        "any of its systems."}
    sources = ([r["row_id"] for r in own.values()][:OWN] if top == 4
               else [hit[k]["row_id"] for k, _, _ in reversed(QS[:top]) if hit[k]][:3])
    return {"stage": str(top + 1), "sources": sources, "values": values, "gaps": GAPS[str(top + 1)]}




def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the in-house capacity study from its answers.")
    ap.add_argument("--as-at", required=True)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--show", help="print one country's rows and its cell")
    a = ap.parse_args(argv)
    try:
        study_lib.load(STUDY)
    except study_lib.StudyError as e:
        print(f"study-ladder: {e}")
        return 2
    as_at = dt.date.fromisoformat(a.as_at)
    here = study_lib.study_dir(STUDY)
    base = os.path.join(here, "evidence")
    fixes = study_lib.read_csv(os.path.join(here, "corrections.csv"))
    test, count = [], {}
    for iso in sorted(study_lib.countries()):
        path = os.path.join(base, iso, "evidence.csv")
        rows, changed = correct(study_lib.read_csv(path), [f for f in fixes if f["iso3"] == iso])
        if changed and not a.dry and not a.show:
            study_lib.write_csv(path, study_lib.EVIDENCE_FIELDS, rows)
        cell = stage(rows, study_lib.counted_at(os.path.join(base, iso, "stage.json"), as_at))
        if a.show and a.show == iso:
            for r in rows:
                print(r["row_id"], r["aspect"], r["value"], r["as_of"], "|", r["system"])
            print(cell)
        count[cell["stage"]] = count.get(cell["stage"], 0) + 1
        line = {"sub_indicator": "inhouse", "stage": cell["stage"],
                **{k: cell["values"].get(k, "") for k, _, _ in QS},
                "cap": "", "flags": "", "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-itcapacity.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", *ASPECTS, "stage_sources")}})
        if a.dry or a.show:
            continue
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry and not a.show:
        study_lib.write_csv(os.path.join(here, "ladder-test.csv"),
                            ["iso3", "stage", *ASPECTS, "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry or a.show else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
