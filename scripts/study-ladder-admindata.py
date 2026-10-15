#!/usr/bin/env python3
r"""study-ladder-admindata.py — the admindata study's four questions, counted.

    python scripts/study-ladder-admindata.py --as-at 2026-09-30
    python scripts/study-ladder-admindata.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-censuses.py` does it.
The ladder is `maturity-study-admindata.md` §2 and §3, every window three years:

1. **Preparing**: a `use` of `preparing`, or a yes to any later question.
2. **Published**: a `use` of `published`.
3. **Vital statistics**: a `vital` of `published`.
4. **Every year**: a `series` of `annual`, or two `vital` rows naming editions of successive
   years (read from `system`, then `fact`), above a yes to question 3.

**A later yes answers the earlier ones** (method §3.3). Stage 1 is a `use` of `none` with no
other yes. A fact dated after the as-at sets nothing. A year or a month stands for its last day.

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

STUDY = "admindata"
GAPS = {
    "5": "",
    "4": "No source held reports vital statistics published for two successive years.",
    "3": "No source held reports vital statistics from civil registration published since October 2023.",
    "2": "No source held reports statistics from administrative records published since October 2023.",
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


def edition(r: dict) -> int | None:
    """The year a vital statistics row's edition names, where it names one."""
    for text in (r.get("system", ""), r.get("fact", "")):
        m = YEAR.search(text or "")
        if m:
            return int(m.group(1))
    return None


def stage(rows: list[dict], as_at: dt.date) -> dict:
    live = [(last_day(r["as_of"]), r) for r in rows if r.get("as_of") and last_day(r["as_of"]) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    three = study_lib.months_back(as_at, 36)
    pick = lambda aspect, values: [  # noqa: E731
        r["row_id"] for d, r in live if r["aspect"] == aspect and r["value"] in values and d >= three]
    vital = pick("vital", ("published",))
    annual = pick("series", ("annual",))
    years = {}
    for d, r in live:
        if r["aspect"] == "vital" and r["value"] == "published" and d >= study_lib.months_back(as_at, 60):
            y = edition(r)
            if y:
                years.setdefault(y, r["row_id"])
    pairs = [(years[y + 1], years[y]) for y in sorted(years, reverse=True) if y + 1 in years]
    published = pick("use", ("published",))
    preparing = pick("use", ("preparing",))
    none = pick("use", ("none",))
    if not rows:
        return {"stage": "no evidence", "sources": [],
                "gaps": "Nothing held names statistics drawn from administrative records, or says there are none."}
    if vital and (annual or pairs):
        s, src = "5", (annual[:1] + vital[:1]) if annual else list(pairs[0])
    elif vital:
        s, src = "4", vital[:2]
    elif published:
        s, src = "3", published[:2]
    elif preparing:
        s, src = "2", preparing[:2]
    elif none:
        s, src = "1", none[:2]
    else:
        return {"stage": "unplaced", "sources": [],
                "gaps": "No statistics from administrative records published, and no work towards them, "
                        "is on record since October 2023."}
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the admindata study from its answers.")
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
        cell = stage(rows, as_at)
        count[cell["stage"]] = count.get(cell["stage"], 0) + 1
        s = cell["stage"]
        line = {"sub_indicator": "admin", "stage": s,
                "use": "published" if s in ("3", "4", "5") else "preparing" if s == "2" else "none" if s == "1" else "",
                "vital": "published" if s in ("4", "5") else "",
                "series": "annual" if s == "5" else "", "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-admindata.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "use", "vital", "series", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "use", "vital", "series", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
