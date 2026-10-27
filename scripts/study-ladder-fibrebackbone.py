#!/usr/bin/env python3
r"""study-ladder-fibrebackbone.py — the national fibre backbone study's four questions, counted.

    python scripts/study-ladder-fibrebackbone.py --as-at 2026-09-30
    python scripts/study-ladder-fibrebackbone.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as
`study-ladder-regionalinfrastructure.py` does it. The ladder is
`maturity-study-fibrebackbone.md` §2 and §3:

1. **Being built**: a `reach` of `building` dated inside three years of the as-at.
2. **In service**: a `reach` of `in-service` or `every-region`, of any age.
3. **Every region**: a `reach` of `every-region`, of any age.
4. **Capacity sold**: an `access` of `open`, of any age, where question 3 is a yes.

**A yes to a later question answers the earlier ones** (method §3.3), except that question 4
needs question 3: open access on a backbone that reaches some regions only leaves stage 3.
**A later dated `none` reverses** (method §3.5): a `reach` of `none` dated after every
positive `reach` row, and inside three years, sets stage 1; an `access` of `none` after
every `open` row withdraws question 4. A fact dated after the as-at sets nothing. A year or
a month stands for its last day, and the as-at's own year for the as-at.

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
import study_lib  # noqa: E402

STUDY = "fibrebackbone"
GAPS = {
    "5": "",
    "4": "No source found says other operators buy capacity on the backbone, or that it runs "
         "on open-access or wholesale terms.",
    "3": "No source found says the backbone reaches every province or region.",
    "2": "No source found says any of the backbone is in service between the capital and "
         "another region.",
    "1": "",
}


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
    # A year alone, in the as-at's own year, stands for the as-at: the source was published by it.
    day = lambda a: as_at if a == str(as_at.year) else last_day(a)  # noqa: E731
    live = [(day(r["as_of"]), r) for r in rows if day(r["as_of"]) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    three = study_lib.months_back(as_at, 36)
    if not rows:
        return {"stage": "no evidence", "reach": "", "access": "", "sources": [],
                "gaps": "Nothing found names a national fibre backbone, or says there is none."}
    pick = lambda aspect, values, since=None, n=2: [  # noqa: E731
        (d, r["row_id"]) for d, r in live if r["aspect"] == aspect and r["value"] in values
        and (since is None or d >= since)][:n]
    ids = lambda ps: [i for _, i in ps]  # noqa: E731
    every = pick("reach", ("every-region",))
    service = pick("reach", ("in-service", "every-region"))
    building = pick("reach", ("building",), three)
    positive = pick("reach", ("every-region", "in-service", "building"), n=1)
    none = pick("reach", ("none",), three)
    if none and (not positive or none[0][0] > positive[0][0]):
        return {"stage": "1", "reach": "none", "access": "", "sources": ids(none), "gaps": ""}
    opened = pick("access", ("open",))
    closed = pick("access", ("none",), n=1)
    if opened and closed and closed[0][0] > opened[0][0]:
        opened = []
    if every and opened:
        s, src = "5", ids(every)[:1] + ids(opened)[:1]
    elif every:
        s, src = "4", ids(every)
    elif service:
        s, src = "3", ids(service)
    elif building:
        s, src = "2", ids(building)
    else:
        return {"stage": "unplaced", "reach": "", "access": "", "sources": [],
                "gaps": "No source found says a national fibre backbone is being built, or is in "
                        "service, and none dated in the last three years says there is none."}
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s],
            "reach": {"5": "every-region", "4": "every-region", "3": "in-service", "2": "building"}[s],
            "access": "open" if s == "5" else ""}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the national fibre backbone study from its answers.")
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
        cell = stage(rows, study_lib.counted_at(os.path.join(base, iso, "stage.json"), as_at))
        count[cell["stage"]] = count.get(cell["stage"], 0) + 1
        line = {"sub_indicator": "backbone", "stage": cell["stage"], "reach": cell["reach"],
                "access": cell["access"], "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-fibrebackbone.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "reach", "access", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "reach", "access", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
