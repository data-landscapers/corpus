#!/usr/bin/env python3
r"""study-ladder-regionallaw.py — the regional law study's four questions, counted.

    python scripts/study-ladder-regionallaw.py --as-at 2026-09-30
    python scripts/study-ladder-regionallaw.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as
`study-ladder-regionalpolicy.py` does it. The ladder is
`maturity-study-regionallaw.md` §2 and §3:

1. **Signed or bound**: an `accepted` of `signed` or `ratified`, of any age.
2. **Ratified**: an `accepted` of `ratified`, of any age.
3. **In national law**: an `effect` of `in-law` or `in-use`, of any age.
4. **Applied across a border**: an `effect` of `in-use` dated inside three years of the as-at.

**A yes to a later question answers the earlier ones** (method §3.3): a national law passed
to carry out a community directive needs no ratification. Stage 1 is an `accepted` of `none`
dated inside three years where no signature, ratification or law of any date is on record:
not signing one text gives way to another the country has signed or is bound by. A fact
dated after the as-at sets nothing. A year or a month stands for its last day, and the as-at's own year for the
as-at.

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

STUDY = "regionallaw"
GAPS = {
    "5": "Nothing on the four questions.",
    "4": "No source found reports the shared law applied across a border in the last three "
         "years: a licence or signature recognised, a request between authorities answered, "
         "a ruling, or a regional finding that the country complies.",
    "3": "No source found says a national law or rule was passed to give effect to a shared text.",
    "2": "No source found dates a ratification or accession.",
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
    pick = lambda aspect, values, since=None, n=2: [  # noqa: E731
        r["row_id"] for d, r in live if r["aspect"] == aspect and r["value"] in values
        and (since is None or d >= since)][:n]
    in_use = pick("effect", ("in-use",), three)
    effect = pick("effect", ("in-law", "in-use"))
    ratified = pick("accepted", ("ratified",))
    signed = pick("accepted", ("signed", "ratified"))
    none = [] if signed or effect else [
        r["row_id"] for d, r in live
        if r["aspect"] == "accepted" and r["value"] == "none" and d >= three][:2]
    if not rows:
        return {"stage": "no evidence", "accepted": "", "effect": "", "sources": [],
                "gaps": "Nothing found names an African legal text on a digital matter that the "
                        "country has signed or is bound by, or says it has signed none."}
    if in_use:
        s, src = "5", in_use + [r for r in effect if r not in in_use][:1] + ratified[:1]
    elif effect:
        s, src = "4", effect + ratified[:1]
    elif ratified:
        s, src = "3", ratified
    elif signed:
        s, src = "2", signed
    elif none:
        s, src = "1", none
    else:
        return {"stage": "unplaced", "accepted": "", "effect": "", "sources": [],
                "gaps": "No signature, ratification or national law is on record, and no source "
                        "dated in the last three years says the country has not signed."}
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s],
            "accepted": "ratified" if ratified else "signed" if signed else "none" if s == "1" else "",
            "effect": "in-use" if s == "5" else "in-law" if s == "4" else ""}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the regional law study from its answers.")
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
        line = {"sub_indicator": "harmonisation", "stage": cell["stage"], "accepted": cell["accepted"],
                "effect": cell["effect"], "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-regionallaw.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "accepted", "effect", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "accepted", "effect", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
