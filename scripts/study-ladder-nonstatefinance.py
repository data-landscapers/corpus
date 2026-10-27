#!/usr/bin/env python3
r"""study-ladder-nonstatefinance.py — the non-state finance study's four questions, counted.

    python scripts/study-ladder-nonstatefinance.py --as-at 2026-09-30
    python scripts/study-ladder-nonstatefinance.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-domesticfinancing.py`
does it. The ladder is `maturity-study-nonstatefinance.md` §2 and §3, every answer dated
from 2024 and by the as-at:

1. **Private money has been put into a digital business**: a `money` of `committed`, or a
   `home` of `raised` or a `state` of `brought`, which are such money too.
2. **In more than one year**: those facts fall in two different years. Two in one year is a
   no and stops the count; a later yes does not answer it.
3. **Some of it was raised inside the country**: a `home` of `raised`.
4. **The government brought private money into a public digital project**: a `state` of
   `brought`.

**Stage 1** needs a `money` of `none` and nothing newer that shows money put in.

A fact dated after the as-at sets nothing. A year or a month stands for its last day, or for
the as-at where that day falls after it and the source was published by it. **The year
question 2 counts is the fact's own**, the year the deal was signed or started.

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

STUDY = "nonstatefinance"
SUB = "private"
ASPECTS = ("money", "home", "state")
FROM = dt.date(2024, 1, 1)
GAPS = {
    "5": "All four questions are answered.",
    "4": "No source from 2024 on has a signed public-private partnership, concession or joint "
         "venture in which a private partner puts a named amount into a public digital "
         "project, or a state fund that private investors have paid into.",
    "3": "No source from 2024 on names an amount put in by a bank, pension fund, insurer, "
         "investor or company of the country itself, or raised on the country's own market.",
    "2 no": "Every amount held from 2024 on was signed or started in the same year.",
    "2": "Only one amount is held from 2024 on, so no source found says whether private money "
         "came in more than one year.",
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
    live = sorted(((when(r), r) for r in rows if r["as_of"] and FROM <= when(r) <= as_at),
                  key=lambda p: p[0], reverse=True)
    of = lambda aspect, value: [(d, r) for d, r in live  # noqa: E731
                                if r["aspect"] == aspect and r["value"] == value]
    ids = lambda pairs, n=2: [r["row_id"] for _, r in pairs][:n]  # noqa: E731
    blank = {a: "" for a in ASPECTS} | {"sources": []}
    if not rows:
        return {"stage": "no evidence", **blank,
                "gaps": "Nothing found names private money put into a digital business in the "
                        "country, or says there is none."}
    committed, none = of("money", "committed"), of("money", "none")
    raised, brought = of("home", "raised"), of("state", "brought")
    put = sorted(committed + raised + brought, key=lambda p: p[0], reverse=True)
    values = {"money": "committed" if put else "none" if none else "",
              "home": "raised" if raised else "", "state": "brought" if brought else ""}
    if none and not (put and put[0][0] >= none[0][0]):
        return {"stage": "1", **values, "sources": ids(none, 1), "gaps": ""}
    if not put:
        return {"stage": "unplaced", **values, "sources": [],
                "gaps": "No source dated from 2024 names an amount of private money put into a "
                        "digital business in the country."}
    years: dict[int, str] = {}
    for _, r in put:
        years.setdefault(int(r["as_of"][:4]), r["row_id"])
    two = [years[y] for y in sorted(years, reverse=True)][:2]
    if len(years) < 2:
        s, src = "2", two
        gap = GAPS["2 no"] if len({r["source_slug"] for _, r in put}) > 1 else GAPS["2"]
    elif not raised:
        s, src, gap = "3", two, GAPS["3"]
    elif not brought:
        s, src, gap = "4", ids(raised) + two, GAPS["4"]
    else:
        s, src, gap = "5", ids(brought, 1) + ids(raised, 1) + two, GAPS["5"]
    return {"stage": s, **values, "sources": list(dict.fromkeys(src)), "gaps": gap}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the non-state finance study from its answers.")
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
        line = {"sub_indicator": SUB, "stage": cell["stage"],
                **{k: cell[k] for k in ASPECTS}, "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-nonstatefinance.py."}
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
