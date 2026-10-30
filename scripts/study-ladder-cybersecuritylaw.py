#!/usr/bin/env python3
r"""study-ladder-cybersecuritylaw.py — the cybersecurity law study's four questions, counted.

    python scripts/study-ladder-cybersecuritylaw.py --as-at 2026-09-30
    python scripts/study-ladder-cybersecuritylaw.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as
`study-ladder-dataprotectionauthority.py` does it. The ladder is
`maturity-study-cybersecuritylaw.md` §2 and §3:

1. **A bill or a law**: a `standing` of `bill` or `in-force`.
2. **In force**: a `standing` of `in-force`, however old; its year is printed. A later
   `bill` does not undo it: a bill beside a law in force is a revision.
3. **Used in the last three years**: a `use` of `used` or `regular` dated inside them. A count
   that does not name the law is `unnamed` and stages nothing *(Bill, 2026-10-30)*.
4. **Regular use**: a `use` of `regular` dated inside two years of the as-at and not after it,
   set by corrections.csv on the stager's case-by-case reading *(Bill, 2026-10-30)*.

Stage 1 is a `standing` of `none` dated inside three years with no bill or law on record.
A fact dated after the as-at sets nothing. A year or a month stands for its last day.

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

STUDY = "cybersecuritylaw"
GAPS = {
    "5": "Nothing on the four questions.",
    "4": "No source found shows the law in regular use in the last two years.",
    "3": "No arrest, charge, prosecution, conviction or penalty under the law in the last three "
         "years is held.",
    "2": "No source found says a cybercrime or cybersecurity law is in force.",
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
    three, two = study_lib.months_back(as_at, 36), study_lib.months_back(as_at, 24)
    pick = lambda aspect, values, since=None, n=2: [  # noqa: E731
        r["row_id"] for d, r in live if r["aspect"] == aspect and r["value"] in values
        and (since is None or d >= since)][:n]
    law, bill = pick("standing", ("in-force",)), pick("standing", ("bill",))
    used = pick("use", ("used", "regular"), three)
    reported = pick("use", ("regular",), two)
    none = pick("standing", ("none",), three)
    if not rows:
        return {"stage": "no evidence", "standing": "", "use": "", "sources": [],
                "gaps": "Nothing found names a cybercrime or cybersecurity law or bill, or says there is none."}
    if reported:
        s, src = "5", reported + law[:1]
    elif used:
        s, src = "4", used + law[:1]
    elif law:
        s, src = "3", law
    elif bill:
        s, src = "2", bill
    elif none:
        s, src = "1", none
    else:
        return {"stage": "unplaced", "standing": "", "use": "", "sources": [],
                "gaps": "No law or bill is on record, and no source dated in the last three years "
                        "says the country has neither."}
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s],
            "standing": "in-force" if s in "345" else "bill" if s == "2" else "none",
            "use": "regular" if s == "5" else "used" if s == "4" else ""}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the cybersecurity law study from its answers.")
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
                "use": cell["use"], "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-cybersecuritylaw.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "standing", "use", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "standing", "use", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
