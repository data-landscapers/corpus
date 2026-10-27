#!/usr/bin/env python3
r"""study-ladder-regionalinfrastructure.py — the shared regional infrastructure study's four questions, counted.

    python scripts/study-ladder-regionalinfrastructure.py --as-at 2026-09-30
    python scripts/study-ladder-regionalinfrastructure.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as
`study-ladder-regionallaw.py` does it. The ladder is
`maturity-study-regionalinfrastructure.md` §2 and §3:

1. **Agreed**: a `built` of `agreed` or `building` dated inside three years of the as-at.
2. **Building**: a `built` of `building` dated inside three years.
3. **In service**: a `service` of `in-service` or `in-use`, of any age.
4. **Carrying another country's traffic**: a `service` of `in-use` dated inside three years.

**A yes to a later question answers the earlier ones** (method §3.3): a link in service was
agreed and built. Stage 1 is a `none` on either aspect dated inside three years where no
other answer stands. An agreement older than three years with nothing built since sets
nothing. A fact dated after the as-at sets nothing. A year or a month stands for its last
day, and the as-at's own year for the as-at.

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

STUDY = "regionalinfrastructure"
GAPS = {
    "5": "Nothing on the four questions.",
    "4": "No source found reports the link or facility carrying another country's traffic in "
         "the last three years: capacity sold or traffic carried across the border, or a user "
         "from the other country named.",
    "3": "No source found says a shared link or facility is in service.",
    "2": "No source found says building has started in the last three years.",
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
    in_use = pick("service", ("in-use",), three)
    service = pick("service", ("in-service", "in-use"))
    building = pick("built", ("building",), three)
    agreed = pick("built", ("agreed", "building"), three)
    none = [] if service or agreed else [
        r["row_id"] for d, r in live if r["value"] == "none" and d >= three][:2]
    if not rows:
        return {"stage": "no evidence", "built": "", "service": "", "sources": [],
                "gaps": "Nothing found names a digital link or facility the country shares with "
                        "another African country, or says it has none."}
    if in_use:
        s, src = "5", in_use + [r for r in service if r not in in_use][:1]
    elif service:
        s, src = "4", service + building[:1]
    elif building:
        s, src = "3", building + [r for r in agreed if r not in building][:1]
    elif agreed:
        s, src = "2", agreed
    elif none:
        s, src = "1", none
    else:
        return {"stage": "unplaced", "built": "", "service": "", "sources": [],
                "gaps": "No shared link or facility agreed or being built in the last three years, "
                        "or in service, is on record, and no source dated in the last three years "
                        "says the country has none."}
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s],
            "built": "building" if building else "agreed" if agreed else "",
            "service": "in-use" if s == "5" else "in-service" if s == "4" else ""}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the shared regional infrastructure study from its answers.")
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
        line = {"sub_indicator": "shared", "stage": cell["stage"], "built": cell["built"],
                "service": cell["service"], "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-regionalinfrastructure.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "built", "service", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "built", "service", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
