#!/usr/bin/env python3
r"""study-ladder-opendiscussion.py — the open discussion study's four questions, counted.

    python scripts/study-ladder-opendiscussion.py --as-at 2026-09-30
    python scripts/study-ladder-opendiscussion.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-publicconsultation.py`
does it. The ladder is `maturity-study-opendiscussion.md` §2 and §3. Cuts and punishments
count for twelve months, every other answer for three years:

1. **Policy criticised in public inside the country**: a `debate` of `criticised`.
2. **Twelve months with no one punished for speech**: a `penalty` of `unpunished`, and no
   `punished` inside the twelve months.
3. **A law that punishes speech repealed or struck down**: a `penalty` of `repealed`.
4. **The government barred from cutting the internet**: a `connection` of `barred`.

**Stage 1 outranks a yes**: a `connection` of `cut` inside the twelve months, or a `debate`
of `silenced` inside the three years, places a country there whatever else is held. **A
`punished` inside the twelve months is a no to question 2 and stops the count.** A later yes
answers an earlier question nothing found answers. A fact dated after the as-at sets nothing.
A year or a month stands for its last day, or for the as-at where that day falls after it
and the source was published by it. **A cut or a punishment dated only to a year that began
before the twelve months sets nothing**: the year does not show it inside them. A `silenced`
is dated by its source, which states the ban as standing.

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

STUDY = "opendiscussion"
ASPECTS = ("debate", "connection", "penalty")
GAPS = {
    "5": "All four questions are answered.",
    "4": "No law, ruling of the country's own court or undertaking given in court in the last "
         "three years bars the government from cutting the internet.",
    "3": "No source from the last three years says a law that punishes speech was repealed or "
         "struck down.",
    "2 no": "A person was arrested, charged or jailed, or an outlet suspended or closed, for "
            "what was said or published, inside the last twelve months.",
    "2": "No source says the country went the last twelve months with no one punished for "
         "what they said or published.",
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
        if r["value"] == "silenced":
            # A ban stated as still standing is dated by the source that says so.
            d = max(d, min(dt.date.fromisoformat(r["source_slug"][:10]), as_at))
        if (d > as_at and r["date_precision"] != "day" and r["source_slug"][:10] <= as_at.isoformat()
                and r["as_of"] <= as_at.isoformat()[:len(r["as_of"])]):
            return as_at
        return d
    live = [(when(r), r) for r in rows if when(r) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    three, twelve = study_lib.months_back(as_at, 36), study_lib.months_back(as_at, 12)
    pick = lambda aspect, value, since, n=2: [  # noqa: E731
        r["row_id"] for d, r in live if r["aspect"] == aspect and r["value"] == value
        and d >= since][:n]
    # A year that began before the twelve months does not show its event inside them.
    recent = lambda r: r["date_precision"] != "year" or dt.date(int(r["as_of"][:4]), 1, 1) >= twelve  # noqa: E731
    live = [(d, r) for d, r in live if recent(r) or r["value"] not in ("cut", "punished", "unpunished")]
    cut = pick("connection", "cut", twelve)
    barred = pick("connection", "barred", three)
    silenced = pick("debate", "silenced", three)
    criticised = pick("debate", "criticised", three)
    punished = pick("penalty", "punished", twelve)
    unpunished = pick("penalty", "unpunished", twelve)
    repealed = pick("penalty", "repealed", three)
    blank = {a: "" for a in ASPECTS} | {"sources": []}
    if not rows:
        return {"stage": "no evidence", **blank,
                "gaps": "Nothing found says government policy is criticised in public inside the "
                        "country, that the internet was cut, or that anyone was punished for "
                        "what they said."}
    values = {"debate": "silenced" if silenced else "criticised" if criticised else "",
              "connection": "cut" if cut else "barred" if barred else "",
              "penalty": "punished" if punished else "repealed" if repealed
              else "unpunished" if unpunished else ""}
    if cut or silenced:
        return {"stage": "1", **values, "sources": list(dict.fromkeys(cut + silenced[:1])), "gaps": ""}
    if not (criticised or unpunished or repealed or barred):
        return {"stage": "unplaced", **values, "sources": [],
                "gaps": "No source dated in the last three years says a newspaper, broadcaster, "
                        "party or group inside the country criticised a government policy in "
                        "public, and none says the internet was cut in the last twelve months."}
    if punished:
        s, src, gap = "2", criticised[:1] + punished, GAPS["2 no"]
    elif barred:
        s, src, gap = "5", barred + repealed[:1] + unpunished[:1], GAPS["5"]
    elif repealed:
        s, src, gap = "4", repealed + unpunished[:1], GAPS["4"]
    elif unpunished:
        s, src, gap = "3", unpunished + criticised[:1], GAPS["3"]
    else:
        s, src, gap = "2", criticised, GAPS["2"]
    return {"stage": s, **values, "sources": list(dict.fromkeys(src)), "gaps": gap}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the open discussion study from its answers.")
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
        line = {"sub_indicator": "discussion", "stage": cell["stage"],
                **{k: cell[k] for k in ASPECTS}, "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-opendiscussion.py."}
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
