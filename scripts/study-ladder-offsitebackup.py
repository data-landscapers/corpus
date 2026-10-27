#!/usr/bin/env python3
r"""study-ladder-offsitebackup.py — the off-site backup study's four questions, counted.

    python scripts/study-ladder-offsitebackup.py --as-at 2026-09-30
    python scripts/study-ladder-offsitebackup.py --as-at 2026-09-30 --dry
    python scripts/study-ladder-offsitebackup.py --as-at 2026-09-30 --show KEN

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-nationaldatacentres.py`
does it. The ladder is `maturity-study-offsitebackup.md` §2 and §3. **A backup site counts only
where `maturity/offsitebackup/sites.csv` marks it `far`** (the parent's reading, method §7.2):
200 km or more from the main site, or abroad, measured from the places the facts name. A site
the table leaves out or marks `near` or `unnamed` answers no question.

1. **A backup site in service**: a `site` row of `service` or `shared` on a far site.
2. **For the shared systems**: a `site` row of `shared` on a far site.
3. **A plan or test**: a `plan` row of `plan` or `tested`, dated inside three years.
4. **Both Tier III**: a `tier` row of `both`. Each question needs the one before.

A `site` of `none` dated after every positive row and inside three years sets stage 1. A fact
dated after the as-at sets nothing; a year or a month stands for its last day, and the as-at's
own year for the as-at. `corrections.csv` is applied to `evidence.csv` first, once. Writes
each `stage.json` and `ladder-test.csv`.

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

STUDY = "offsitebackup"
GAPS = {
    "5": "",
    "4": "No source found says the government's main data centre and its backup site are both Tier III or above.",
    "3": "No source found from the past three years states a recovery plan or test for the government's backup site.",
    "2": "No source found says a backup site 200 km or more away serves the government's shared systems.",
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


def stage(rows: list[dict], as_at: dt.date, far: dict[str, str]) -> dict:
    day = lambda a: as_at if a == str(as_at.year) else last_day(a)  # noqa: E731
    live = [(day(r["as_of"]), r) for r in rows if day(r["as_of"]) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    if not rows:
        return {"stage": "no evidence", "sources": [],
                "gaps": "Nothing found names a backup site for government systems, or says there is none."}
    three = study_lib.months_back(as_at, 36)
    sites = [(d, r) for d, r in live if r["aspect"] == "site" and r["value"] in ("service", "shared")]
    service = [(d, r) for d, r in sites if far.get(r["row_id"]) == "far"]
    none = [(d, r) for d, r in live if r["aspect"] == "site" and r["value"] == "none" and d >= three]
    if none and (not sites or none[0][0] > sites[0][0]):
        return {"stage": "1", "sources": [none[0][1]["row_id"]], "gaps": ""}
    if not service:
        why = {"near": "is less than 200 km from the main site",
               "unnamed": "is in no place a held source names"}
        held = sorted({why[far[r["row_id"]]] for _, r in sites if far.get(r["row_id"]) in why})
        gap = ("No source found names a backup site 200 km or more from the main site"
               + (f"; the backup site held {' or '.join(held)}" if held else "")
               + ", and none dated in the last three years says there is none.")
        return {"stage": "unplaced", "sources": [], "gaps": gap}
    shared = [(d, r) for d, r in service if r["value"] == "shared"]
    plan = [(d, r) for d, r in live if r["aspect"] == "plan" and r["value"] in ("plan", "tested") and d >= three]
    tier = [(d, r) for d, r in live if r["aspect"] == "tier" and r["value"] == "both"]
    s, src = "2", [service[0][1]["row_id"]]
    if shared:
        s, src = "3", [shared[0][1]["row_id"]]
        if plan:
            s, src = "4", src + [plan[0][1]["row_id"]]
            if tier:
                s, src = "5", src + [tier[0][1]["row_id"]]
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the off-site backup study from its answers.")
    ap.add_argument("--as-at", required=True)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--show", help="print one country's backup facts and its cell")
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
    far = {r["row_id"]: r["distance"] for r in study_lib.read_csv(os.path.join(here, "sites.csv"))}
    test, count = [], {}
    for iso in sorted(study_lib.countries()):
        path = os.path.join(base, iso, "evidence.csv")
        rows, changed = correct(study_lib.read_csv(path), [f for f in fixes if f["iso3"] == iso])
        if changed and not a.dry and not a.show:
            study_lib.write_csv(path, study_lib.EVIDENCE_FIELDS, rows)
        cell = stage(rows, study_lib.counted_at(os.path.join(base, iso, "stage.json"), as_at), far)
        if a.show and a.show == iso:
            for r in rows:
                print(r["row_id"], r["aspect"], r["value"], r["as_of"], far.get(r["row_id"], "?"), "|", r["system"])
            print(cell)
        count[cell["stage"]] = count.get(cell["stage"], 0) + 1
        s = cell["stage"]
        line = {"sub_indicator": "backup", "stage": s,
                "site": {"5": "shared", "4": "shared", "3": "shared", "2": "service", "1": "none"}.get(s, ""),
                "plan": "plan" if s in ("4", "5") else "",
                "tier": "both" if s == "5" else "", "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-offsitebackup.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "site", "plan", "stage_sources")}})
        if a.dry or a.show:
            continue
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry and not a.show:
        study_lib.write_csv(os.path.join(here, "ladder-test.csv"),
                            ["iso3", "stage", "site", "plan", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry or a.show else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
