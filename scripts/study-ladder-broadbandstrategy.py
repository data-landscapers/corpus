#!/usr/bin/env python3
r"""study-ladder-broadbandstrategy.py — the broadband plan study's four questions, counted.

    python scripts/study-ladder-broadbandstrategy.py --as-at 2026-09-30
    python scripts/study-ladder-broadbandstrategy.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as
`study-ladder-cybersecuritylaw.py` does it. The ladder is
`maturity-study-broadbandstrategy.md` §2 and §3:

1. **A plan, or one being written**: a `standing` of `draft`, `adopted` or `ended`.
2. **Adopted and still running**: the newest of the `adopted` and `ended` facts is
   `adopted`, however old; an `ended` of the same date wins. A later `draft` does not undo
   it: a draft beside a running plan is its successor being written.
3. **Money committed in the last three years**: a `delivery` of `funded` dated inside
   them.
4. **Progress published in the last three years**: a `delivery` of `reported` dated inside
   them. **It does not answer question 3**: a review of a plan does not show that money was
   committed to it, so a country with a review and no money on record stays at stage 3 and
   its gap says so.

A `delivery` fact lifts nothing where the plan on record has ended or is only a draft: the
ladder puts both at stage 2. With no `standing` fact at all it answers the earlier
questions. Stage 1 is a `standing` of `none` dated inside three years with no plan or draft
on record. A fact dated after the as-at sets nothing. A year or a month stands for its last
day.

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

STUDY = "broadbandstrategy"
GAPS = {
    "5": "Nothing on the four questions.",
    "4": "No review or report from the last three years giving figures against the plan's own "
         "targets is held.",
    "3": "No budget line, universal service fund allocation or financed programme tied to the "
         "plan in the last three years is held.",
    "2": "No source found says a national broadband plan is adopted and still running.",
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
    live.sort(key=lambda p: (p[0], p[1]["value"] == "ended"), reverse=True)
    three = study_lib.months_back(as_at, 36)
    pick = lambda aspect, values, since=None, n=2: [  # noqa: E731
        r["row_id"] for d, r in live if r["aspect"] == aspect and r["value"] in values
        and (since is None or d >= since)][:n]
    settled = [r for d, r in live if r["aspect"] == "standing" and r["value"] in ("adopted", "ended")]
    running = bool(settled) and settled[0]["value"] == "adopted"
    plan = pick("standing", ("adopted",)) if running else []
    ended = [] if running else [r["row_id"] for r in settled][:2]
    draft = pick("standing", ("draft",))
    funded = pick("delivery", ("funded",), three)
    reported = pick("delivery", ("reported",), three)
    none = pick("standing", ("none",), three)
    lifts = running or not (settled or draft)
    if not rows:
        return {"stage": "no evidence", "standing": "", "delivery": "", "sources": [],
                "gaps": "Nothing found names a national broadband plan, or says there is none."}
    if reported and funded and lifts:
        s, src = "5", reported[:1] + funded[:1] + plan[:1]
    elif funded and lifts:
        s, src = "4", funded + plan[:1]
    elif running:
        s, src = "3", plan
    elif ended or draft:
        s, src = "2", (draft[:1] + ended[:1]) if draft else ended
    elif none:
        s, src = "1", none
    else:
        return {"stage": "unplaced", "standing": "", "delivery": "", "sources": [],
                "gaps": "No plan or draft is on record, and no source dated in the last three "
                        "years says the country has neither."}
    gaps = GAPS[s]
    if s == "3" and reported:
        gaps = "Progress against the plan is published. " + gaps
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": gaps,
            "standing": "adopted" if s in "345" else "none" if s == "1" else "draft" if draft else "ended",
            "delivery": "reported" if s == "5" else "funded" if s == "4" else ""}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the broadband plan study from its answers.")
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
        line = {"sub_indicator": "plan", "stage": cell["stage"], "standing": cell["standing"],
                "delivery": cell["delivery"], "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-broadbandstrategy.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "standing", "delivery", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "standing", "delivery", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
