#!/usr/bin/env python3
r"""study-ladder-mobileaffordability.py — the mobile affordability study's four questions, counted.

    python scripts/study-ladder-mobileaffordability.py --as-at 2026-09-30
    python scripts/study-ladder-mobileaffordability.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-internetusage.py`
does it. The ladder is `maturity-study-mobileaffordability.md` §2 and §3. **One figure sets
the stage**: the newest cost of 5 GB of mobile data for a month as a share of average monthly
income, dated 2024 or later and by the as-at.

- **No source outranks another** *(Bill, 2026-10-13)*: the newest figure stands, whether the
  International Telecommunication Union's, a regulator's or a news story's.
- **A figure dated only to a year counts as mid-year**, 1 July; a month as its last day.
- **The lines are 10, 5, 2 and 1 per cent**: each one the figure is at or under is a yes and a
  stage. Above 10 is stage 1, which the figure itself states.
- **A rise is a rise**: an earlier, lower figure sets nothing.

A `cost` value is `share:{per cent}` or `price:{currency}:{amount}:{gigabytes}`, and
`study_afford.share()` turns either into the per cent. A price it cannot set against income
sets nothing. A fact dated after the as-at sets nothing.

`corrections.csv`, where the parent's reading removed or revalued a row, is applied to
`evidence.csv` first, once. Writes each `stage.json` and `ladder-test.csv`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import argparse
import calendar
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_afford  # noqa: E402
import study_lib  # noqa: E402

STUDY = "mobileaffordability"
SUB = "price"
ASPECTS = ("cost",)
FROM = dt.date(2024, 1, 1)
LINES = (10.0, 5.0, 2.0, 1.0)


def when(as_of: str) -> dt.date:
    p = [int(x) for x in as_of.split("-")]
    if len(p) == 1:
        return dt.date(p[0], 7, 1)
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


def stage(iso: str, rows: list[dict], as_at: dt.date) -> dict:
    if not rows:
        return {"stage": "no evidence", "cost": "", "share": "", "sources": [],
                "gaps": "Nothing found gives what a month of mobile data costs against income."}
    live = []
    for r in rows:
        if r["aspect"] != "cost" or not r["as_of"]:
            continue
        figure = study_afford.share(iso, r["value"])
        if figure is not None and FROM <= when(r["as_of"]) <= as_at:
            live.append((when(r["as_of"]), figure, r))
    if not live:
        return {"stage": "unplaced", "cost": "", "share": "", "sources": [],
                "gaps": "No figure for 2024 or later has been found for what a month of mobile data costs "
                        "against income."}
    # Two figures for the same day: the dearer stands, so a stage is never set on the kinder reading.
    _, figure, best = max(live, key=lambda p: (p[0], p[1], p[2]["row_id"]))
    cleared = sum(1 for line in LINES if figure <= line)
    if cleared == len(LINES):
        gap = "All four questions are answered."
    elif cleared == 0:
        gap = ""
    else:
        gap = (f"The newest figure, {figure:g} per cent for {best['as_of'][:4]}, is above "
               f"{LINES[cleared]:g} per cent.")
    return {"stage": str(cleared + 1), "cost": best["value"], "share": f"{figure:g}",
            "sources": [best["row_id"]], "gaps": gap}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the mobile affordability study from its figures.")
    ap.add_argument("--as-at", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    try:
        study_lib.load(STUDY)
    except study_lib.StudyError as e:
        print(f"study-ladder: {e}")
        return 2
    as_at = dt.date.fromisoformat(a.as_at)
    base = os.path.join(study_lib.study_dir(STUDY), "evidence")
    fixes = study_lib.read_csv(os.path.join(study_lib.study_dir(STUDY), "corrections.csv"))
    test, count = [], {}
    for iso in sorted(study_lib.countries()):
        path = os.path.join(base, iso, "evidence.csv")
        rows, changed = correct(study_lib.read_csv(path), [f for f in fixes if f["iso3"] == iso])
        if changed and not a.dry:
            study_lib.write_csv(path, study_lib.EVIDENCE_FIELDS, rows)
        cell = stage(iso, rows, study_lib.counted_at(os.path.join(base, iso, "stage.json"), as_at))
        count[cell["stage"]] = count.get(cell["stage"], 0) + 1
        line = {"sub_indicator": SUB, "stage": cell["stage"], "cost": cell["cost"],
                "cap": "", "flags": "", "stage_sources": ";".join(cell["sources"]),
                "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-mobileaffordability.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", *ASPECTS, "stage_sources")},
                     "share": cell["share"]})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", *ASPECTS, "stage_sources", "share"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
