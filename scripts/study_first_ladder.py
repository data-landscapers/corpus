#!/usr/bin/env python3
r"""study_first_ladder.py — the ladder of a first-pass study whose four questions are three aspects.

    python scripts/study-ladder-dataexchange.py --as-at 2026-09-30

`maturity/documentation/first-pass-batch.md`. The Data Exchange batch of 2026-10-16 asks the
same shape of question five times, so one counter serves the five studies and each
`study-ladder-{id}.py` names its own aspects:

1. **Under way**: the first aspect at `underway`, or a yes to any later question.
2. **In service**: the first aspect at `inservice`.
3. The second aspect's one value.
4. The third aspect's one value.

**A later yes answers the earlier ones** (method §3.3). Stage 1 is the first aspect at `none`
with no other yes. Every window is three years; a fact dated after the as-at sets nothing, and a
year or a month stands for its last day. `corrections.csv` (`removed`, or `revalued: aspect:value`)
is applied to `evidence.csv` first, once, as `study-ladder-opendatause.py` does. Writes each
`stage.json` and `ladder-test.csv`.

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
        if f and f["action"].startswith("revalued: "):
            to = f["action"].split(": ", 1)[1]
            aspect, value = to.split(":", 1) if ":" in to else (r["aspect"], to)
            if (r["aspect"], r["value"]) != (aspect, value):
                r, changed = {**r, "aspect": aspect, "value": value}, changed + 1
        out.append(r)
    return out, changed


def keys(study: dict) -> tuple[str, str, str, str, str]:
    """`(first, second, third, second's value, third's value)` from `study.json`."""
    a1, a2, a3 = study["aspects"]
    return a1["key"], a2["key"], a3["key"], a2["values"][0], a3["values"][0]


def stage(study: dict, rows: list[dict], as_at: dt.date, gaps: dict, empty: str, unplaced: str) -> dict:
    k1, k2, k3, v2, v3 = keys(study)
    live = [(last_day(r["as_of"]), r) for r in rows if r.get("as_of") and last_day(r["as_of"]) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    three = study_lib.months_back(as_at, 36)
    pick = lambda aspect, value: [  # noqa: E731
        r["row_id"] for d, r in live if r["aspect"] == aspect and r["value"] == value and d >= three]
    if not rows:
        return {"stage": "no evidence", "sources": [], "gaps": empty}
    for s, src in (("5", pick(k3, v3)), ("4", pick(k2, v2)), ("3", pick(k1, "inservice")),
                   ("2", pick(k1, "underway")), ("1", pick(k1, "none"))):
        if src:
            return {"stage": s, "sources": src[:2], "gaps": gaps[s]}
    return {"stage": "unplaced", "sources": [], "gaps": unplaced}


def run(study_id: str, sub: str, gaps: dict, empty: str, unplaced: str, argv=None) -> int:
    ap = argparse.ArgumentParser(description=f"Stage the {study_id} study from its answers.")
    ap.add_argument("--as-at", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    try:
        study = study_lib.load(study_id)
    except study_lib.StudyError as e:
        print(f"study-ladder: {e}")
        return 2
    k1, k2, k3, v2, v3 = keys(study)
    as_at = dt.date.fromisoformat(a.as_at)
    here = study_lib.study_dir(study_id)
    base = os.path.join(here, "evidence")
    fixes = study_lib.read_csv(os.path.join(here, "corrections.csv"))
    test, count = [], {}
    for iso in sorted(study_lib.countries()):
        path = os.path.join(base, iso, "evidence.csv")
        rows, changed = correct(study_lib.read_csv(path), [f for f in fixes if f["iso3"] == iso])
        if changed and not a.dry:
            study_lib.write_csv(path, study_lib.EVIDENCE_FIELDS, rows)
        cell = stage(study, rows, as_at, gaps, empty, unplaced)
        s = cell["stage"]
        count[s] = count.get(s, 0) + 1
        line = {"sub_indicator": sub, "stage": s,
                k1: "inservice" if s in ("3", "4", "5") else "underway" if s == "2" else "none" if s == "1" else "",
                k2: v2 if s in ("4", "5") else "", k3: v3 if s == "5" else "", "cap": "", "flags": "",
                "stage_sources": ";".join(dict.fromkeys(cell["sources"])), "gaps": cell["gaps"],
                "note": f"First pass: counted from the four questions by study-ladder-{study_id}.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", k1, k2, k3, "stage_sources")}})
        if not a.dry:
            os.makedirs(os.path.join(base, iso), exist_ok=True)
            study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(here, "ladder-test.csv"), ["iso3", "stage", k1, k2, k3, "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0
