#!/usr/bin/env python3
r"""study-ladder-opendatause.py — the opendatause study's four questions, counted.

    python scripts/study-ladder-opendatause.py --as-at 2026-09-30
    python scripts/study-ladder-opendatause.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-admindata.py` does it.
The ladder is `maturity-study-opendatause.md` §2 and §3, every window three years but stage 5's:

1. **Published**: an `access` of `published`, or a yes to any later question.
2. **Licensed**: an `access` of `licensed`.
3. **Several bodies**: a `breadth` of `several`.
4. **Four or more bodies**: a `breadth` of `many`, in a two-year window *(Bill, 2026-10-25: reuse
   is no longer asked, and a download or view count is not evidence of use)*.

**A later yes answers the earlier ones** (method §3.3). Stage 1 is an `access` of `none` with no
other yes. A fact dated after the as-at sets nothing. A year or a month stands for its last day.

`corrections.csv`, where the parent's reading removed or revalued a row (`revalued: aspect:value`
moves it to another aspect), is applied to
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

STUDY = "opendatause"
GAPS = {
    "5": "",
    "4": "No source found since October 2024 names or counts four or more public bodies publishing data.",
    "3": "No source found since October 2023 names two or more public bodies publishing data.",
    "2": "No source found since October 2023 states an open licence for the data.",
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
        if f and f["action"].startswith("revalued: "):
            to = f["action"].split(": ", 1)[1]
            aspect, value = to.split(":", 1) if ":" in to else (r["aspect"], to)   # a count of bodies tagged `access`
            if (r["aspect"], r["value"]) != (aspect, value):
                r, changed = {**r, "aspect": aspect, "value": value}, changed + 1
        out.append(r)
    return out, changed


def stage(rows: list[dict], as_at: dt.date) -> dict:
    live = [(last_day(r["as_of"]), r) for r in rows if r.get("as_of") and last_day(r["as_of"]) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    three = study_lib.months_back(as_at, 36)
    pick = lambda aspect, values: [  # noqa: E731
        r["row_id"] for d, r in live if r["aspect"] == aspect and r["value"] in values and d >= three]
    two = study_lib.months_back(as_at, 24)
    many = [r["row_id"] for d, r in live if r["aspect"] == "breadth" and r["value"] == "many" and d >= two]
    several = pick("breadth", ("several", "many"))
    licensed = pick("access", ("licensed",))
    published = pick("access", ("published",))
    none = pick("access", ("none",))
    if not rows:
        return {"stage": "no evidence", "sources": [],
                "gaps": "Nothing found names government data published for download, or says there is none."}
    if many:
        s, src = "5", many[:2]
    elif several:
        s, src = "4", several[:2]
    elif licensed:
        s, src = "3", licensed[:2]
    elif published:
        s, src = "2", published[:2]
    elif none:
        s, src = "1", none[:2]
    else:
        return {"stage": "unplaced", "sources": [],
                "gaps": "No government data published for download is on record since October 2023."}
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the opendatause study from its answers.")
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
        s = cell["stage"]
        line = {"sub_indicator": "use", "stage": s,
                "access": "licensed" if s in ("3", "4", "5") else "published" if s == "2" else "none" if s == "1" else "",
                "breadth": "many" if s == "5" else "several" if s == "4" else "", "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-opendatause.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "access", "breadth", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "access", "breadth", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
