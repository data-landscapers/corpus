#!/usr/bin/env python3
r"""study-ladder-internationalstandards.py — the international standards study's four questions, counted.

    python scripts/study-ladder-internationalstandards.py --as-at 2026-09-30
    python scripts/study-ladder-internationalstandards.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-qualitystandards.py`
does it. The ladder is `maturity-study-internationalstandards.md` §2 and §3:

1. **Membership of ISO or IEC**: a `standing` of `member` or `adopted`, however old.
2. **An international standard on information technology or data adopted as a national
   one**: a `standing` of `adopted`, however old.
3. **Public bodies must meet a named international standard**: a `use` of `required`, of
   any age.
4. **Taking part in writing such standards in the last three years**: a `use` of `writes`
   dated inside them. An older one is outside its window and answers nothing.

A yes to a later question answers the earlier ones. Stage 1 is a `standing` of `none` dated
inside three years with no membership on record. A fact dated after the as-at sets nothing. A
year or a month stands for its last day, or for the as-at where that day falls after it and
the source was published by it.

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

STUDY = "internationalstandards"
GAPS = {
    "5": "All four questions are answered.",
    "4": "No source from the last three years naming the standards body or a public body as "
         "a participating member, chair or secretariat of an ISO or IEC committee on "
         "information technology or data is held.",
    "3": "No source found names a law, decree, regulation, directive or circular requiring "
         "public bodies to meet a named international standard on information technology or data.",
    "2": "No source found names an international standard on information technology or data "
         "adopted as a national standard.",
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
    def when(r: dict) -> dt.date:
        # A year or a month from a source published by the as-at is inside it (stager brief).
        d = last_day(r["as_of"])
        if (d > as_at and r["date_precision"] != "day" and r["source_slug"][:10] <= as_at.isoformat()
                and r["as_of"] <= as_at.isoformat()[:len(r["as_of"])]):
            return as_at
        return d
    live = [(when(r), r) for r in rows if when(r) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    three = study_lib.months_back(as_at, 36)
    pick = lambda aspect, values, since=None, n=2: [  # noqa: E731
        r["row_id"] for d, r in live if r["aspect"] == aspect and r["value"] in values
        and (since is None or d >= since)][:n]
    adopted = pick("standing", ("adopted",))
    member = pick("standing", ("member",))
    required = pick("use", ("required",))
    writes = pick("use", ("writes",), three)
    none = pick("standing", ("none",), three)
    blank = {"standing": "", "use": "", "sources": []}
    if not rows:
        return {"stage": "no evidence", **blank,
                "gaps": "Nothing found names the country's standards body as a member of ISO or "
                        "IEC, or says it belongs to neither."}
    if writes:
        s, src = "5", writes + required[:1] + adopted[:1]
    elif required:
        s, src = "4", required + adopted[:1]
    elif adopted:
        s, src = "3", adopted + member[:1]
    elif member:
        s, src = "2", member
    elif none:
        s, src = "1", none
    else:
        return {"stage": "unplaced", **blank,
                "gaps": "No membership of ISO or IEC is on record, and no source dated in the "
                        "last three years says the country belongs to neither."}
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s],
            "standing": "adopted" if s in "345" else "none" if s == "1" else "member",
            "use": "writes" if s == "5" else "required" if s == "4" else ""}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the international standards study from its answers.")
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
        line = {"sub_indicator": "international", "stage": cell["stage"], "standing": cell["standing"],
                "use": cell["use"], "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-internationalstandards.py."}
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
