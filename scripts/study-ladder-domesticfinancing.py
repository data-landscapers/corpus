#!/usr/bin/env python3
r"""study-ladder-domesticfinancing.py — the domestic financing study's four questions, counted.

    python scripts/study-ladder-domesticfinancing.py --as-at 2026-09-30
    python scripts/study-ladder-domesticfinancing.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-opendiscussion.py`
does it. The ladder is `maturity-study-domesticfinancing.md` §2 and §3, every answer inside
three years:

1. **The state budget gives money to digital transformation**: a `budget` of `allocated`,
   or anything that shows money given: `rose`, `fell`, `spent`, or a `commitment` of `acted`.
2. **The money is higher in the latest budget than the one before**: the deciding `budget`
   row is `rose`. `fell` is a no and stops the count.
3. **The government committed to paying at home and acted**: a `commitment` of `acted` with
   no `abolished` after it.
4. **What was spent is published**: a `budget` of `spent`.

**Each of questions 2 and 3 is answered on its own evidence**: no later yes answers them, so
the count stops at the first of them nothing found answers. **Question 2 is set by a source
that gives the digital ministry's budget for both years, where one is held for the latest
budget; otherwise by the budget tables' lines**: a drafted `rose` or `fell` stands over the
tables' own (a fact that opens *Budget tables:*) unless it is more than `SAME_BUDGET` days
older than theirs, which makes it news of an earlier budget. **Stage 1** needs a `budget` of
`none` and nothing newer that shows money given.

A fact dated after the as-at sets nothing. A year or a month stands for its last day, or for
the as-at where that day falls after it and the source was published by it.

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

STUDY = "domesticfinancing"
ASPECTS = ("budget", "commitment")
SAME_BUDGET = 183           # a story this much older than the tables' fact is of the budget before
TABLES = "Budget tables:"
GAPS = {
    "5": "All four questions are answered.",
    "4": "No budget execution report, settlement law, audited accounts or fund account from "
         "the last three years gives what was actually spent.",
    "3": "No source from the last three years has the government both saying digital "
         "transformation must be paid for from the country's own resources and acting on it: "
         "no fund, levy or assigned tax is shown created, collecting or paying.",
    "3 abolished": "The fund or levy that paid for digital programmes was abolished, repealed "
                   "or moved to the general treasury, and nothing found replaces it.",
    "2 no": "The money for digital transformation was lower in the latest budget than in the "
            "one before, or the same.",
    "2": "Nothing found gives the money for digital transformation in two budget years "
         "running, so no source found says whether it rose.",
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
        d = last_day(r["as_of"])
        if (d > as_at and r["date_precision"] != "day" and r["source_slug"][:10] <= as_at.isoformat()
                and r["as_of"] <= as_at.isoformat()[:len(r["as_of"])]):
            return as_at
        return d
    since = study_lib.months_back(as_at, 36)
    live = sorted(((when(r), r) for r in rows if since <= when(r) <= as_at),
                  key=lambda p: p[0], reverse=True)
    of = lambda aspect, *values: [(d, r) for d, r in live  # noqa: E731
                                  if r["aspect"] == aspect and r["value"] in values]
    ids = lambda pairs, n=2: [r["row_id"] for _, r in pairs][:n]  # noqa: E731
    blank = {a: "" for a in ASPECTS} | {"sources": []}
    if not rows:
        return {"stage": "no evidence", **blank,
                "gaps": "Nothing found says whether the state budget gives money to digital "
                        "transformation, or that a fund or levy pays for it."}

    # Question 2: a source giving the ministry's budget for both years, unless it is of an
    # earlier budget than the tables hold.
    moved = of("budget", "rose", "fell")
    tables = [(d, r) for d, r in moved if r["fact"].startswith(TABLES)]
    drafted = [(d, r) for d, r in moved if not r["fact"].startswith(TABLES)]
    if drafted and (not tables or (tables[0][0] - drafted[0][0]).days <= SAME_BUDGET):
        deciding = drafted[0]
    else:
        deciding = tables[0] if tables else None

    acted, abolished = of("commitment", "acted"), of("commitment", "abolished")
    if abolished:
        acted = [(d, r) for d, r in acted if d > abolished[0][0]]
    spent, none = of("budget", "spent"), of("budget", "none")
    given = of("budget", "allocated", "rose", "fell", "spent")
    values = {"budget": "spent" if spent else deciding[1]["value"] if deciding
              else "allocated" if given else "none" if none else "",
              "commitment": "acted" if acted else "abolished" if abolished
              else "stated" if of("commitment", "stated") else ""}
    if none and not (given and given[0][0] >= none[0][0]) and not acted:
        return {"stage": "1", **values, "sources": ids(none, 1), "gaps": ""}
    if not (given or acted):
        return {"stage": "unplaced", **values, "sources": [],
                "gaps": "No source dated in the last three years names money in the state budget "
                        "for a digital ministry, agency or programme."}
    first = ids(of("budget", "allocated"), 1) or ids(given, 1) or ids(acted, 1)
    if not deciding:
        s, src, gap = "2", first, GAPS["2"]
    elif deciding[1]["value"] == "fell":
        s, src, gap = "2", first + [deciding[1]["row_id"]], GAPS["2 no"]
    elif not acted:
        s, src, gap = "3", [deciding[1]["row_id"]] + first, GAPS["3 abolished" if abolished else "3"]
    elif not spent:
        s, src, gap = "4", ids(acted) + [deciding[1]["row_id"]], GAPS["4"]
    else:
        s, src, gap = "5", ids(spent, 1) + ids(acted) + [deciding[1]["row_id"]], GAPS["5"]
    return {"stage": s, **values, "sources": list(dict.fromkeys(src)), "gaps": gap}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the domestic financing study from its answers.")
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
        line = {"sub_indicator": "financing", "stage": cell["stage"],
                **{k: cell[k] for k in ASPECTS}, "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-domesticfinancing.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", *ASPECTS, "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", *ASPECTS, "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
