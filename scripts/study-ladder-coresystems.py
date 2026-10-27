#!/usr/bin/env python3
r"""study-ladder-coresystems.py — the core government systems study's four questions, counted.

    python scripts/study-ladder-coresystems.py --as-at 2026-09-30
    python scripts/study-ladder-coresystems.py --as-at 2026-09-30 --dry
    python scripts/study-ladder-coresystems.py --as-at 2026-09-30 --show KEN

`maturity/documentation/maturity-study-method.md` §7. The ladder is
`maturity-study-coresystems.md` §2 and §3:

1. **The money**: the newest `finance` row inside three years is `inuse`.
2. **Tax and payroll**: the newest `revenue` and `payroll` rows inside three years are `inuse`.
3. **Renewed**: a `renewed` row of `live` inside three years.
4. **Mapped**: an `architecture` row of `published`, no window.

**A system out of action is not in use**: a `down` row inside twelve months, newer than the
newest `inuse` on that aspect, answers its question no. A `none` inside three years and newer
than any `inuse` does the same. A yes to a later question answers the earlier ones (§3.3)
unless one of them is answered no, which stops the count there. A `finance` of `none` with no
yes at all is stage 1.

A fact dated after the as-at sets nothing; a year or a month stands for its last day, and the
as-at's own year for the as-at. `corrections.csv` is applied to `evidence.csv` first, once.
Writes each `stage.json` and `ladder-test.csv`.

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

STUDY = "coresystems"
CORE = ("finance", "revenue", "payroll")
NAMES = {"finance": "financial management system", "revenue": "tax system", "payroll": "payroll"}
GAPS = {
    "5": "",
    "4": "No source found says the government has published an enterprise architecture or an "
         "inventory of its systems.",
    "3": "No source found says the financial, tax or payroll system went live on a new or "
         "upgraded system since October 2023.",
    "2": "No source found from 2023 or later says both the tax system and the payroll are in use.",
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


def answer(live: list, aspect: str, three: dt.date, twelve: dt.date) -> tuple[str, str]:
    """`(yes|no|"", row_id)` for one of the three systems, from the newest rows first."""
    inuse = next(((d, r) for d, r in live if r["aspect"] == aspect and r["value"] == "inuse"), None)
    down = next(((d, r) for d, r in live if r["aspect"] == aspect and r["value"] == "down"
                 and d >= twelve), None)
    none = next(((d, r) for d, r in live if r["aspect"] == aspect and r["value"] == "none"
                 and d >= three), None)
    for neg in (down, none):
        if neg and (not inuse or neg[0] > inuse[0]):
            return "no", neg[1]["row_id"]
    if inuse and inuse[0] >= three:
        return "yes", inuse[1]["row_id"]
    return "", ""


def stage(rows: list[dict], as_at: dt.date) -> dict:
    day = lambda a: as_at if a == str(as_at.year) else last_day(a)  # noqa: E731
    live = sorted(((day(r["as_of"]), r) for r in rows if day(r["as_of"]) <= as_at),
                  key=lambda p: p[0], reverse=True)
    if not live:
        return {"stage": "no evidence", "sources": [], "values": {},
                "gaps": "Nothing found says whether the government's finance, tax or payroll "
                        "systems are in use."}
    three, twelve = study_lib.months_back(as_at, 36), study_lib.months_back(as_at, 12)
    a = {k: answer(live, k, three, twelve) for k in CORE}
    renewed = next((r for d, r in live if r["aspect"] == "renewed" and r["value"] == "live" and d >= three), None)
    mapped = next((r for d, r in live if r["aspect"] == "architecture" and r["value"] == "published"), None)
    q = [a["finance"][0],
         "no" if "no" in (a["revenue"][0], a["payroll"][0])
         else "yes" if a["revenue"][0] == a["payroll"][0] == "yes" else "",
         "yes" if renewed else "", "yes" if mapped else ""]
    top = max((i + 1 for i, v in enumerate(q) if v == "yes"), default=0)
    stop = next((i for i, v in enumerate(q) if v == "no"), None)
    if stop is not None and stop < top:
        top = stop                          # an answered no stops the count there
    src = {1: [a["finance"][1]], 2: [a["revenue"][1], a["payroll"][1]],
           3: [renewed["row_id"]] if renewed else [], 4: [mapped["row_id"]] if mapped else []}
    said = {r["row_id"]: r["value"] for _, r in live}
    values = {k: ("inuse" if a[k][0] == "yes" else said[a[k][1]] if a[k][0] == "no" else "") for k in CORE}
    values.update(renewed="live" if renewed else "", architecture="published" if mapped else "")
    if top == 0:
        fin = a["finance"]
        if fin[0] == "no" and said[fin[1]] == "none":
            return {"stage": "1", "sources": [fin[1]], "values": values, "gaps": ""}
        gap = ("A source found says the government's financial system is out of action; none says it is back."
               if fin[0] == "no" else
               "No source found from 2023 or later says the government's financial management system is in use.")
        return {"stage": "unplaced", "sources": [], "values": values, "gaps": gap}
    sources = [s for i in range(top, 0, -1) for s in src[i] if s][:3]
    gap = GAPS[str(top + 1)]
    if stop is not None and stop == top:
        k = next(k for k in CORE[top - 1:] if a[k][0] == "no")
        gap = (f"A source found says the {NAMES[k]} is out of action; none says it is back."
               if said[a[k][1]] == "down" else f"A source found says the {NAMES[k]} is run largely by hand.")
    return {"stage": str(top + 1), "sources": list(dict.fromkeys(sources)), "values": values, "gaps": gap}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the core systems study from its answers.")
    ap.add_argument("--as-at", required=True)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--show", help="print one country's rows and its cell")
    a = ap.parse_args(argv)
    try:
        study_lib.load(STUDY)
    except study_lib.StudyError as e:
        print(f"study-ladder: {e}")
        return 2
    as_at = dt.date.fromisoformat(a.as_at)
    here = study_lib.study_dir(STUDY)
    base = os.path.join(here, "evidence")
    fixes = study_lib.read_csv(os.path.join(here, "corrections.csv"))
    test, count = [], {}
    for iso in sorted(study_lib.countries()):
        path = os.path.join(base, iso, "evidence.csv")
        rows, changed = correct(study_lib.read_csv(path), [f for f in fixes if f["iso3"] == iso])
        if changed and not a.dry and not a.show:
            study_lib.write_csv(path, study_lib.EVIDENCE_FIELDS, rows)
        cell = stage(rows, study_lib.counted_at(os.path.join(base, iso, "stage.json"), as_at))
        if a.show and a.show == iso:
            for r in rows:
                print(r["row_id"], r["aspect"], r["value"], r["as_of"], "|", r["system"])
            print(cell)
        count[cell["stage"]] = count.get(cell["stage"], 0) + 1
        line = {"sub_indicator": "core", "stage": cell["stage"],
                **{k: cell["values"].get(k, "") for k in (*CORE, "renewed", "architecture")},
                "cap": "", "flags": "", "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-coresystems.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", *CORE, "renewed", "architecture", "stage_sources")}})
        if a.dry or a.show:
            continue
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry and not a.show:
        study_lib.write_csv(os.path.join(here, "ladder-test.csv"),
                            ["iso3", "stage", *CORE, "renewed", "architecture", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry or a.show else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
