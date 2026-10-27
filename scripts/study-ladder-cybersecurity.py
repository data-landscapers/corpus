#!/usr/bin/env python3
r"""study-ladder-cybersecurity.py — the national cyber response study's four questions, counted.

    python scripts/study-ladder-cybersecurity.py --as-at 2026-09-30
    python scripts/study-ladder-cybersecurity.py --as-at 2026-09-30 --dry
    python scripts/study-ladder-cybersecurity.py --as-at 2026-09-30 --show KEN

`maturity/documentation/maturity-study-method.md` §7. The ladder is
`maturity-study-cybersecurity.md` §2 and §3:

1. **A strategy or a body**: a `foundation` row of `body`, no window, or of `strategy` while
   its period runs: a strategy whose fact names a period ending before the as-at's year is
   spent.
2. **Responding**: a `response` row of `responded` inside three years.
3. **Critical infrastructure**: a `cii` row of `designated`, no window.
4. **Figures**: a `figures` row of `published` whose period ends inside two years.

A yes to a later question answers the earlier ones (§3.3). A `foundation` row of `none`
inside three years places a country at stage 1, and only where nothing answers yes.

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
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402

STUDY = "cybersecurity"
QS = (("foundation", ("body", "strategy"), 0), ("response", ("responded",), 36),
      ("cii", ("designated",), 0), ("figures", ("published",), 24))
GAPS = {
    "5": "",
    "4": "No source found says the national body published a count of incidents for a period ending since September 2024.",
    "3": "No source found says the country has designated its critical information infrastructure.",
    "2": "No source found says the national body handled an incident or issued a public alert since October 2023.",
    "1": "",
}
PERIOD = re.compile(r"\b(20\d\d)\s*(?:-|–|to)\s*(20\d\d)\b")
ASPECTS = tuple(k for k, _, _ in QS)


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


def spent(r: dict, as_at: dt.date) -> bool:
    """A strategy whose stated period ended before the as-at's year no longer counts."""
    if r["aspect"] != "foundation" or r["value"] != "strategy":
        return False
    m = PERIOD.search(r["fact"])
    return bool(m) and int(m.group(2)) < as_at.year


def stage(rows: list[dict], as_at: dt.date) -> dict:
    day = lambda a: as_at if a == str(as_at.year) else last_day(a)  # noqa: E731
    live = sorted(((day(r["as_of"]), r) for r in rows if day(r["as_of"]) <= as_at),
                  key=lambda p: p[0], reverse=True)
    if not live:
        return {"stage": "no evidence", "sources": [], "values": {},
                "gaps": "Nothing found says whether the country has a cybersecurity strategy or a national cyber body."}
    hit = {}
    for k, vals, months in QS:
        floor = study_lib.months_back(as_at, months) if months else dt.date.min
        hit[k] = next((r for d, r in live if r["aspect"] == k and r["value"] in vals
                       and d >= floor and not spent(r, as_at)), None)
    values = {k: (hit[k]["value"] if hit[k] else "") for k, _, _ in QS}
    top = max((i + 1 for i, (k, _, _) in enumerate(QS) if hit[k]), default=0)
    if top == 0:
        three = study_lib.months_back(as_at, 36)
        none = next((r for d, r in live if r["aspect"] == "foundation" and r["value"] == "none"
                     and d >= three), None)
        if none:
            values["foundation"] = "none"
            return {"stage": "1", "sources": [none["row_id"]], "values": values, "gaps": ""}
        return {"stage": "unplaced", "sources": [], "values": values,
                "gaps": "No source found says the country adopted a cybersecurity strategy or created a national "
                        "cyber body, or that it has neither."}
    sources = [hit[k]["row_id"] for k, _, _ in reversed(QS[:top]) if hit[k]][:3]
    return {"stage": str(top + 1), "sources": sources, "values": values, "gaps": GAPS[str(top + 1)]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the national cyber response study from its answers.")
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
        line = {"sub_indicator": "readiness", "stage": cell["stage"],
                **{k: cell["values"].get(k, "") for k, _, _ in QS},
                "cap": "", "flags": "", "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-cybersecurity.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", *ASPECTS, "stage_sources")}})
        if a.dry or a.show:
            continue
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry and not a.show:
        study_lib.write_csv(os.path.join(here, "ladder-test.csv"),
                            ["iso3", "stage", *ASPECTS, "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry or a.show else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
