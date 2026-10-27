#!/usr/bin/env python3
r"""study-ladder-statisticslaw.py — the statistics law study's four questions, counted.

    python scripts/study-ladder-statisticslaw.py --as-at 2026-09-30
    python scripts/study-ladder-statisticslaw.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as
`study-ladder-ecommercelaw.py` does it. The ladder is
`maturity-study-statisticslaw.md` §2 and §3:

1. **A draft or a law**: a `standing` of `draft` or `in-force`.
2. **In force**: a `standing` of `in-force`, however old; its year is printed. A later
   `draft` does not undo it: a bill beside a law in force is its replacement being written.
3. **Rules made under it**: a `reach` of `rules`, of any age.
4. **Applied**: a `reach` of `applied`, or of `rules`, dated inside three years of the
   as-at: a rule made under the law in that time is the law applied.

**A yes to a later question answers the earlier ones** (method §3.3): a council appointed
under the law shows the law is in force. An `applied` older than three years
is not a yes to question 4; it still shows a law in force, and no more. Stage 1
is a `standing` of `none` dated inside three years with no draft or law on record. A fact
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
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402

STUDY = "statisticslaw"
GAPS = {
    "5": "Nothing on the four questions.",
    "4": "No source found dates an act done under the law in the last three years: its council "
         "or board appointed or meeting, a standard or calendar issued, a rule made or a penalty.",
    "3": "No source found names a decree, regulation or order made under the law.",
    "2": "No source found says a statistics law is in force.",
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
    live = [(last_day(r["as_of"]), r) for r in rows if last_day(r["as_of"]) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    three = study_lib.months_back(as_at, 36)
    pick = lambda aspect, values, since=None, n=2: [  # noqa: E731
        r["row_id"] for d, r in live if r["aspect"] == aspect and r["value"] in values
        and (since is None or d >= since)][:n]
    law, draft = pick("standing", ("in-force",)), pick("standing", ("draft",))
    applied = pick("reach", ("applied", "rules"), three)
    rules, old = pick("reach", ("rules",)), pick("reach", ("applied",))
    none = pick("standing", ("none",), three)
    if not rows:
        return {"stage": "no evidence", "standing": "", "reach": "", "sources": [],
                "gaps": "Nothing found names a statistics law or a draft of one, or says there is "
                        "none."}
    if applied:
        s, src = "5", applied + [r for r in rules if r not in applied][:1] + law[:1]
    elif rules:
        s, src = "4", rules[:2] + law[:1]
    elif law or old:
        s, src = "3", law or old
    elif draft:
        s, src = "2", draft
    elif none:
        s, src = "1", none
    else:
        return {"stage": "unplaced", "standing": "", "reach": "", "sources": [],
                "gaps": "No law or draft is on record, and no source dated in the last "
                        "three years says the country has none."}
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s],
            "standing": "in-force" if s in "345" else "draft" if s == "2" else "none",
            "reach": "applied" if s == "5" else "rules" if s == "4" else ""}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the statistics law study from its answers.")
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
        line = {"sub_indicator": "law", "stage": cell["stage"], "standing": cell["standing"],
                "reach": cell["reach"], "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-statisticslaw.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "standing", "reach", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "standing", "reach", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
