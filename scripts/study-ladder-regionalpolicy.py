#!/usr/bin/env python3
r"""study-ladder-regionalpolicy.py — the regional policy study's four questions, counted.

    python scripts/study-ladder-regionalpolicy.py --as-at 2026-09-30
    python scripts/study-ladder-regionalpolicy.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as
`study-ladder-accesstoinformationlaw.py` does it. The ladder is
`maturity-study-regionalpolicy.md` §2 and §3:

1. **Belongs**: a `part` of `member` or `active`, of any age.
2. **Active part**: a `part` of `active` dated inside three years of the as-at.
3. **Put into effect**: an `effect` of `in-effect` or `in-use`, of any age.
4. **In use**: an `effect` of `in-use` dated inside three years of the as-at.

**A yes to a later question answers the earlier ones** (method §3.3): a thing agreed and
put into effect shows an agreement and a membership. An `active` older than three years
still shows the country belongs, and no more. Stage 1 is a `part` of `none` dated inside
three years with no `part` or `effect` fact dated after it: a suspension from one body
gives way to a membership or an agreement reported since. A fact dated after the as-at
sets nothing. A year or a month stands for its last day.

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

STUDY = "regionalpolicy"
GAPS = {
    "5": "Nothing on the four questions.",
    "4": "No source found gives figures of use, a decision of a joint body, or a review of what "
         "an agreement has delivered, in the last three years.",
    "3": "No source found says a thing the country agreed has been put into effect.",
    "2": "No source found dates an agreement signed, a meeting hosted or chaired, or a seat won, "
         "in the last three years.",
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
    in_use = pick("effect", ("in-use",), three)
    effect = pick("effect", ("in-effect", "in-use"))
    active = pick("part", ("active",), three)
    member = pick("part", ("member", "active"))
    out = [(d, r) for d, r in live if r["aspect"] == "part" and r["value"] == "none" and d >= three]
    none = [r["row_id"] for d, r in out
            if not any(e > d for e, x in live if x["value"] != "none")][:2]
    if not rows:
        return {"stage": "no evidence", "part": "", "effect": "", "sources": [],
                "gaps": "Nothing found names the country's part in an African body that makes "
                        "digital policy, or an agreement, or says it stands outside."}
    if none:
        s, src = "1", none
    elif in_use:
        s, src = "5", in_use + [r for r in effect if r not in in_use][:1] + active[:1]
    elif effect:
        s, src = "4", effect + active[:1]
    elif active:
        s, src = "3", active
    elif member:
        s, src = "2", member
    else:
        return {"stage": "unplaced", "part": "", "effect": "", "sources": [],
                "gaps": "No membership or agreement is on record, and no source dated in the last "
                        "three years says the country stands outside."}
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s],
            "part": "active" if s in "345" else "member" if s == "2" else "none",
            "effect": "in-use" if s == "5" else "in-effect" if s == "4" else ""}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the regional policy study from its answers.")
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
        line = {"sub_indicator": "cooperation", "stage": cell["stage"], "part": cell["part"],
                "effect": cell["effect"], "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-regionalpolicy.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "part", "effect", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "part", "effect", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
