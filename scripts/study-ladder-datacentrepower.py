#!/usr/bin/env python3
r"""study-ladder-datacentrepower.py — the data-centre power study's four questions, counted.

    python scripts/study-ladder-datacentrepower.py --as-at 2026-09-30
    python scripts/study-ladder-datacentrepower.py --as-at 2026-09-30 --dry
    python scripts/study-ladder-datacentrepower.py --as-at 2026-09-30 --show KEN

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-offsitebackup.py` does
it. The ladder is `maturity-study-datacentrepower.md` §2 and §3.

1. **A secured supply**: a `supply` row of `secured` or `reserved`.
2. **Power set aside**: a `supply` row of `reserved`.
3. **A PUE of 1.6 or less**: a `pue` row of `low`, dated inside three years.
4. **Water published**: a `water` row of `published`, dated inside three years.

**Each question needs the one before** (method §3.6): the four are separate facts, so a
PUE or a water figure does not answer the supply questions. Power set aside answers question
1 as well: a drafter records `reserved` only for a data centre or arrangement in service, and
a plant or contract built for a data centre is a supply of its own. A `supply` of `none` dated inside three years sets
stage 1 where no question is answered. A fact dated after the as-at sets nothing; a year or a
month stands for its last day, and the as-at's own year for the as-at. `corrections.csv` is
applied to `evidence.csv` first, once. Writes each `stage.json` and `ladder-test.csv`.

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

STUDY = "datacentrepower"
GAPS = {
    "5": "",
    "4": "No source found from the past three years says a data centre in service publishes its water use or cools without water.",
    "3": "No source found from the past three years says a data centre in service states a PUE of 1.6 or less.",
    "2": "No source found says power is set aside for data centres by a signed contract, a plant built for them or a tariff or zone in force.",
    "1": "No source found says a data centre in service has two grid feeds, its own substation or line, or its own power plant.",
    "0": "No source found says a data centre in service has two grid feeds, its own substation or line, or its own power plant, and none from the past three years says one went short of power or water.",
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
    day = lambda a: as_at if a == str(as_at.year) else last_day(a)  # noqa: E731
    live = [(day(r["as_of"]), r) for r in rows if day(r["as_of"]) <= as_at]
    live.sort(key=lambda p: (p[0], p[1]["row_id"]), reverse=True)
    if not rows:
        return {"stage": "no evidence", "sources": [],
                "gaps": "Nothing found says how any data centre is supplied with power or water."}
    three = study_lib.months_back(as_at, 36)
    pick = lambda asp, vals, window=False: [r for d, r in live  # noqa: E731
                                            if r["aspect"] == asp and r["value"] in vals and (not window or d >= three)]
    secured, reserved = pick("supply", ("secured", "reserved")), pick("supply", ("reserved",))
    pue, water = pick("pue", ("low",), True), pick("water", ("published",), True)
    none = pick("supply", ("none",), True)
    if not secured:
        if none:
            return {"stage": "1", "sources": [none[0]["row_id"]], "gaps": GAPS["1"]}
        return {"stage": "unplaced", "sources": [], "gaps": GAPS["0"]}
    s, src = "2", [secured[0]["row_id"]]
    if reserved:
        s, src = "3", [reserved[0]["row_id"]]
        if pue:
            s, src = "4", src + [pue[0]["row_id"]]
            if water:
                s, src = "5", src + [water[0]["row_id"]]
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the data-centre power study from its answers.")
    ap.add_argument("--as-at", required=True)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--show", help="print one country's facts and its cell")
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
        s = cell["stage"]
        line = {"sub_indicator": "power", "stage": s,
                "supply": {"5": "reserved", "4": "reserved", "3": "reserved", "2": "secured", "1": "none"}.get(s, ""),
                "pue": "low" if s in ("4", "5") else "",
                "water": "published" if s == "5" else "", "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-datacentrepower.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "supply", "pue", "stage_sources")}})
        if a.dry or a.show:
            continue
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry and not a.show:
        study_lib.write_csv(os.path.join(here, "ladder-test.csv"),
                            ["iso3", "stage", "supply", "pue", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry or a.show else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
