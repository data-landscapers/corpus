#!/usr/bin/env python3
r"""study-ladder-internetusage.py — the internet usage study's four questions, counted.

    python scripts/study-ladder-internetusage.py --as-at 2026-09-30
    python scripts/study-ladder-internetusage.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-mobilepenetration.py`
does it. The ladder is `maturity-study-internetusage.md` §2 and §3. **One figure sets
the stage**: the latest share of the population who use the internet, for 2024 or later and by
the as-at.

- **A survey or census figure in the window is used in place of an estimate**, and the
  newest survey in place of an older one. With no survey, the newest estimate.
- **The lines are 25, 50, 80 and 95 per cent**: each one cleared is a yes and a stage.
  Below 25 is stage 1, which the figure itself states.
- **A fall is a fall**: an earlier, higher figure sets nothing.

A `users` value is `survey:{per cent}` or `estimate:{per cent}`. A fact dated after the
as-at sets nothing. A year or a month stands for its last day, or for the as-at where that
day falls after it and the source was published by it.

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

STUDY = "internetusage"
SUB = "use"
ASPECTS = ("users",)
FROM = dt.date(2024, 1, 1)
LINES = (25.0, 50.0, 80.0, 95.0)


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
    def when(r: dict) -> dt.date:
        d = last_day(r["as_of"])
        # A reference series is cited by its release date, a record by a slug that opens on its own.
        published = r["source_slug"].rsplit("@", 1)[-1] if r["source_slug"].startswith("ref:") \
            else r["source_slug"][:10]
        if (d > as_at and r["date_precision"] != "day" and published <= as_at.isoformat()
                and r["as_of"] <= as_at.isoformat()[:len(r["as_of"])]):
            return as_at
        return d
    if not rows:
        return {"stage": "no evidence", "users": "", "sources": [],
                "gaps": "Nothing found gives the share of the population who use the internet."}
    live = [(when(r), r) for r in rows if r["aspect"] == "users" and r["as_of"]
            and FROM <= when(r) <= as_at]
    if not live:
        return {"stage": "unplaced", "users": "", "sources": [],
                "gaps": "No figure for 2024 or later has been found for the share of the population who "
                        "use the internet."}
    surveys = [p for p in live if p[1]["value"].startswith("survey:")]
    # Where a story and the series give the same year, the series' row stands for both.
    _, best = max(surveys or live, key=lambda p: (p[0], p[1]["source_slug"].startswith("ref:"),
                                                  p[1]["row_id"]))
    figure = float(best["value"].split(":", 1)[1])
    cleared = sum(1 for line in LINES if figure >= line)
    if cleared == len(LINES):
        gap = "All four questions are answered."
    elif cleared == 0:
        gap = ""
    else:
        gap = (f"The latest figure, {figure:g} per cent for {best['as_of'][:4]}, is below "
               f"{LINES[cleared]:g} per cent.")
    return {"stage": str(cleared + 1), "users": best["value"], "sources": [best["row_id"]],
            "gaps": gap}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the internet usage study from its figures.")
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
        line = {"sub_indicator": SUB, "stage": cell["stage"], "users": cell["users"],
                "cap": "", "flags": "", "stage_sources": ";".join(cell["sources"]),
                "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-internetusage.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", *ASPECTS, "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", *ASPECTS, "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
