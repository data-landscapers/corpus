#!/usr/bin/env python3
r"""study-ladder-censuses.py — the censuses study's four questions, counted.

    python scripts/study-ladder-censuses.py --as-at 2026-09-30
    python scripts/study-ladder-censuses.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-statisticsstrategy.py`
does it. The ladder is `maturity-study-censuses.md` §2 and §3:

1. **Preparing or taken**: a `census` of `preparing` dated inside three years of the as-at,
   or a yes to question 2.
2. **Counted**: a `census` of `taken` dated inside ten years, the UN's census decade.
3. **Results**: a `results` of `final` or `preliminary` for a census counted inside ten years
   *(Bill, 2026-10-25: preliminary results answer it as well as final ones)*. The
   census's year is read from the row's `system`, then its `fact`; where neither names one,
   the release must fall inside the ten years.
4. **Survey**: a `survey` of `published` dated inside three years. **It counts only above
   published results** (study §3): on its own it is noted and sets nothing.

**A later yes answers the earlier ones** (method §3.3): final results show a census was
counted. Stage 1 is a `census` of `none` dated inside three years with no other yes. A fact
dated after the as-at sets nothing. A year or a month stands for its last day.

`corrections.csv`, where the parent's reading removed or revalued a row, is applied to
`evidence.csv` first, once. Writes each `stage.json` and `ladder-test.csv`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import argparse
import calendar
import datetime as dt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402

STUDY = "censuses"
GAPS = {
    "5": "",
    "4": "No source found reports results of a national household survey published since October 2023.",
    "3": "No source found reports preliminary or final results of the census published.",
    "2": "No source found reports a census counted since October 2016.",
    "1": "",
}
YEAR = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")


def last_day(as_of: str) -> dt.date:
    p = [int(x) for x in as_of.split("-")]
    if len(p) == 1:
        return dt.date(p[0], 12, 31)
    if len(p) == 2:
        return dt.date(p[0], p[1], calendar.monthrange(p[0], p[1])[1])
    return dt.date(*p)


def census_year(r: dict) -> int | None:
    """The year of the census a results row is about, where the row names one."""
    for text in (r.get("system", ""), r.get("fact", "")):
        m = YEAR.search(text or "")
        if m:
            return int(m.group(1))
    return None


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
            aspect, value = to.split(":", 1) if ":" in to else (r["aspect"], to)   # a preliminary release tagged `census`
            if (r["aspect"], r["value"]) != (aspect, value):
                r, changed = {**r, "aspect": aspect, "value": value}, changed + 1
        out.append(r)
    return out, changed


def stage(rows: list[dict], as_at: dt.date) -> dict:
    live = [(last_day(r["as_of"]), r) for r in rows if r.get("as_of") and last_day(r["as_of"]) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    three = study_lib.months_back(as_at, 36)
    ten = study_lib.months_back(as_at, 120)
    pick = lambda aspect, values, since: [  # noqa: E731
        r["row_id"] for d, r in live if r["aspect"] == aspect and r["value"] in values and d >= since]
    final = [r["row_id"] for d, r in live if r["aspect"] == "results" and r["value"] in ("final", "preliminary")
             and d >= ten and (census_year(r) or ten.year + 1) > ten.year]
    taken = pick("census", ("taken",), ten)
    preparing = pick("census", ("preparing",), three)
    surveyed = pick("survey", ("published",), three)
    none = pick("census", ("none",), three)
    if not rows:
        return {"stage": "no evidence", "sources": [],
                "gaps": "Nothing found names a population census or a household survey, or says there is none."}
    first = final[::-1]   # the first release of final results dates them, not a later regional one
    if final and surveyed:
        s, src = "5", surveyed[:1] + first[:1]
    elif final:
        s, src = "4", first[:2]
    elif taken:
        s, src = "3", taken[:2]
    elif preparing:
        s, src = "2", preparing[:2]
    elif none:
        s, src = "1", none[:2]
    else:
        return {"stage": "unplaced", "sources": [],
                "gaps": "No census counted since October 2016 or in preparation since October 2023 is on "
                        "record, and no source dated in the last three years says there is none."}
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the censuses study from its answers.")
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
        line = {"sub_indicator": "census", "stage": s,
                "census": "taken" if s in ("3", "4", "5") else "preparing" if s == "2" else "none" if s == "1" else "",
                "results": "final" if s in ("4", "5") else "",
                "survey": "published" if s == "5" else "", "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-censuses.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "census", "results", "survey", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "census", "results", "survey", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
