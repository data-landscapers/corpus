#!/usr/bin/env python3
r"""study-ladder-dataprotectionauthority.py — the authority study's four questions, counted.

    python scripts/study-ladder-dataprotectionauthority.py --as-at 2026-09-30
    python scripts/study-ladder-dataprotectionauthority.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7: **the stage follows from the answers,
so a script counts them** and writes each country's `stage.json`, in the shape
`study-assess.py` folds. The parent reads every fact that sets stage 4 or 5 before this
runs, and what that reading changed is in `maturity/dataprotectionauthority/corrections.csv`:
a row `removed` or `revalued: {value}`, applied to `evidence.csv` here, once.

The questions, as `maturity-study-dataprotectionauthority.md` §2 and §3 set them:

1. **Named in law**: a `standing` of `provided` or `constituted`. A body named only in a
   bill is not a yes, and whether the law is enacted is the law study's `standing`.
2. **Appointed**: a `standing` of `constituted`, however old; its year is printed. A later
   `none` reverses it. A later `provided` does not: it is one more source describing the law.
3. **Ruled in the last three years**: a `rulings` of `ruled` or `reported` dated inside them.
4. **Publishes yearly figures**: a `rulings` of `reported` for a period ending inside two
   years of the as-at and not after it.

Stage 1 is a `standing` of `none` dated inside three years, with no body named in an enacted
law. A fact dated after the as-at sets nothing. A year or a month stands for its last day.

Writes `maturity/dataprotectionauthority/ladder-test.csv` beside the stage files.

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

STUDY, LAW = "dataprotectionauthority", "dataprotectionlaw"
ENACTED = {"enacted", "transition", "in-force"}
GAPS = {
    "5": "Nothing on the four questions.",
    "4": "No count of the authority's decisions, fines or complaints settled, for a period "
         "ending in the last two years, is held.",
    "3": "No ruling of the authority against a named organisation in the last three years has been found.",
    "2": "No source found says the authority's head or members have been appointed.",
    "1": "",
}
# What the parent's reading adds to a cell's gaps: a fact the count cannot carry.
ADD = {
    "BFA": "A bill adopted on 3 August 2026 merges the commission into a new regulator whose "
           "members are not yet appointed; the commission is counted until a source says it has gone.",
    "NER": "A report of 13 June 2026 says a decree abolished the authority and split its powers "
           "between two ministries; the decree is not held, and nothing says the ministries are doing the job.",
    "TUN": "The members were appointed in April 2021 for three years and no renewal has been found; a "
           "source dated after the as-at says the authority is at a standstill.",
    "GHA": "The one decision held from the last three years is a court's, which belongs to the law row.",
    "KEN": "A count of 215 determinations runs to March 2025 with no period, and a commentator's "
           "'over 110 decisions in 2025' is not the authority's own figure.",
    "AGO": "The authority's register of fines by year was captured after the as-at.",
    "NAM": "An authority is named only in draft bills of 2020 and 2022.",
    "SLE": "An authority is named only in a bill of 2025.",
}


def last_day(as_of: str) -> dt.date:
    p = [int(x) for x in as_of.split("-")]
    if len(p) == 1:
        return dt.date(p[0], 12, 31)
    if len(p) == 2:
        return dt.date(p[0], p[1], calendar.monthrange(p[0], p[1])[1])
    return dt.date(*p)


def correct(rows: list[dict], fixes: list[dict]) -> tuple[list[dict], int]:
    """`evidence.csv` rows with the parent's corrections applied, and how many changed."""
    by_id = {f"{f['iso3']}-{f['n']}": f for f in fixes}
    out, changed = [], 0
    for r in rows:
        f = by_id.get(r["row_id"])
        if f and f["action"] == "removed":
            changed += 1
            continue
        if f and f["action"].startswith("revalued: "):
            new = f["action"].split(": ", 1)[1]
            if r["value"] != new:
                r, changed = {**r, "value": new}, changed + 1
        out.append(r)
    return out, changed


def stage(rows: list[dict], as_at: dt.date, law_enacted: bool) -> dict:
    """One country's cell from its evidence rows."""
    live = [(last_day(r["as_of"]), r) for r in rows if last_day(r["as_of"]) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    three, two = study_lib.months_back(as_at, 36), study_lib.months_back(as_at, 24)
    st = [(d, r) for d, r in live if r["aspect"] == "standing"]
    con = [(d, r) for d, r in st if r["value"] == "constituted"]
    pro = [(d, r) for d, r in st if r["value"] == "provided"]
    non = [(d, r) for d, r in st if r["value"] == "none"]
    reversed_ = bool(con and non and non[0][0] > con[0][0])
    appointed = bool(con) and not reversed_
    named = appointed or (bool(pro or con) and law_enacted)
    ru = [(d, r) for d, r in live if r["aspect"] == "rulings" and r["value"] in ("ruled", "reported")
          and d >= three]
    rep = [(d, r) for d, r in ru if r["value"] == "reported" and d >= two]
    ids = lambda pairs, n=2: [r["row_id"] for _, r in pairs[:n]]  # noqa: E731
    if not rows:
        return {"stage": "no evidence", "standing": "", "rulings": "", "sources": [],
                "gaps": "Nothing found names a data protection authority or says there is none."}
    if appointed and rep:
        s, src = "5", ids(rep) + ids(con, 1)
    elif appointed and ru:
        s, src = "4", ids(ru) + ids(con, 1)
    elif appointed:
        s, src = "3", ids(con)
    elif named:
        s, src = "2", ids(pro) + (ids(non, 1) if reversed_ else [])
    elif non and non[0][0] >= three:
        s, src = "1", ids(non)
    else:
        return {"stage": "unplaced", "standing": "", "rulings": "", "sources": [],
                "gaps": "No law held names an authority, and no source dated in the last three "
                        "years says the country has none."}
    return {"stage": s, "sources": src, "gaps": GAPS[s],
            "standing": "constituted" if appointed else "provided" if named else "none",
            "rulings": "reported" if s == "5" else "ruled" if s == "4" else ""}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the authority study from its answers.")
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
    law = {r["iso3"]: r["standing"] for r in study_lib.read_csv(
        os.path.join(study_lib.out_dir(LAW), "assessment.csv"))}
    test, count = [], {}
    for iso in sorted(study_lib.countries()):
        path = os.path.join(base, iso, "evidence.csv")
        rows, changed = correct(study_lib.read_csv(path), [f for f in fixes if f["iso3"] == iso])
        if changed and not a.dry:
            study_lib.write_csv(path, study_lib.EVIDENCE_FIELDS, rows)
        cell = stage(rows, study_lib.counted_at(os.path.join(base, iso, "stage.json"), as_at), law.get(iso, "") in ENACTED)
        gaps = " ".join(x for x in (cell["gaps"], ADD.get(iso, "")) if x)
        count[cell["stage"]] = count.get(cell["stage"], 0) + 1
        test.append({"iso3": iso, "stage": cell["stage"], "standing": cell["standing"],
                     "rulings": cell["rulings"], "stage_sources": ";".join(cell["sources"])})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [{
            "sub_indicator": "body", "stage": cell["stage"], "standing": cell["standing"],
            "rulings": cell["rulings"], "cap": "", "flags": "",
            "stage_sources": ";".join(cell["sources"]), "gaps": gaps,
            "note": "Counted from the four questions by study-ladder-dataprotectionauthority.py."}])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "standing", "rulings", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
