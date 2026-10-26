#!/usr/bin/env python3
r"""study_first_ladder.py — the ladder of a first-pass study whose four questions are three aspects.

    python scripts/study-ladder-dataexchange.py --as-at 2026-09-30

`maturity/documentation/first-pass-batch.md`. The Data Exchange batch of 2026-10-16 asks the
same shape of question five times, so one counter serves the five studies and each
`study-ladder-{id}.py` names its own aspects:

1. **Under way**: the first aspect at `underway`, or a yes to any later question.
2. **In service**: the first aspect at `inservice`.

The first aspect's values are read from `study.json` in that order, top first: `inservice`,
`underway`, `none` unless a study names its own (the ID coverage study's are population shares).
3. The second aspect's one value.
4. The third aspect's one value.

**A later yes answers the earlier ones** (method §3.3), unless `study.json` -> `"later_yes": false`
*(Bill, 2026-10-23: birthidlink, idregisters, taxregister)*: then stage 4 needs the first aspect
at its top value as well, and stage 5 needs that and the second aspect, each shown by its own row
in the window. `inservice` still answers `underway`: they are one aspect. **`"must_show": [n, ...]`**
*(Bill, 2026-10-23: a nationwide criterion is observed)* is the finer setting: a later yes does not
answer the questions it lists, and answers the rest; the stage is the last question answered in an
unbroken run from question 1, and its sources that question's own rows, else the later yes that
answered it. Stage 1 is the first aspect at `none` with no other yes. Every window is three years; a fact dated after the as-at
sets nothing, and a year or a month stands for its last day. `corrections.csv` (`removed`, or `revalued: aspect:value`)
is applied to `evidence.csv` first, once, as `study-ladder-opendatause.py` does. Writes each
`stage.json` and `ladder-test.csv`.

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


def seen(study: dict, r: dict) -> dt.date:
    """The date the window is counted from: the fact's, or for an aspect `"source_dated"` names the
    later of the fact's and its source's *(Bill, 2026-10-26, message 34: "a source from the last
    three years says rules are in force" dates by the source, not by when the rule was adopted)*.
    Only a standing state is named: an event, a fine or a year's complaint count, keeps its own date."""
    d = last_day(r["as_of"])
    if r["aspect"] in study.get("source_dated", []):
        m = re.match(r"(\d{4}-\d{2}-\d{2})-", r.get("source_slug") or "")
        if m:
            d = max(d, dt.date.fromisoformat(m.group(1)))
    return d


def keys(study: dict) -> tuple[str, str, str, str, str]:
    """`(first, second, third, second's value, third's value)` from `study.json`."""
    a1, a2, a3 = study["aspects"]
    return a1["key"], a2["key"], a3["key"], a2["values"][0], a3["values"][0]


def firsts(study: dict) -> tuple[str, str, str]:
    """The first aspect's values for stages 3, 2 and 1."""
    top, mid, low = study["aspects"][0]["values"][:3]
    return top, mid, low


def stage(study: dict, rows: list[dict], as_at: dt.date, gaps: dict, empty: str, unplaced: str) -> dict:
    k1, k2, k3, v2, v3 = keys(study)
    top, mid, low = firsts(study)
    live = [(seen(study, r), r) for r in rows if r.get("as_of") and last_day(r["as_of"]) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    three = study_lib.months_back(as_at, 36)
    pick = lambda aspect, value: [  # noqa: E731
        r["row_id"] for d, r in live if r["aspect"] == aspect and r["value"] == value and d >= three]
    if not rows:
        return {"stage": "no evidence", "sources": [], "gaps": empty}
    p3 = pick(k1, top)
    # The direct yes to each question; `inservice` answers `underway`, being one aspect.
    yes = {1: pick(k1, mid) or p3, 2: p3, 3: pick(k2, v2), 4: pick(k3, v3)}
    must = must_show(study)
    answered = lambda q: yes[q] or (q not in must and any(yes[r] for r in range(q + 1, 5)))  # noqa: E731
    n = 0
    while n < 4 and answered(n + 1):
        n += 1
    if n:
        src = yes[n] or next(yes[r] for r in range(n + 1, 5) if yes[r])
        return {"stage": str(n + 1), "sources": src[:2], "gaps": gaps[str(n + 1)]}
    low_rows = pick(k1, low)
    if low_rows:
        return {"stage": "1", "sources": low_rows[:2], "gaps": gaps["1"]}
    return {"stage": "unplaced", "sources": [], "gaps": unplaced}


def must_show(study: dict) -> set[int]:
    """The questions a later yes does not answer: `must_show`, or all three under `later_yes: false`."""
    if study.get("later_yes", True) is False:   # Bill, 2026-10-23: every lower rung shown
        return {1, 2, 3}
    return {int(q) for q in study.get("must_show", [])}   # Bill, 2026-10-23: nationwide is shown


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
    top, mid, low = firsts(study)
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
        cell = stage(study, rows, study_lib.counted_at(os.path.join(base, iso, "stage.json"), as_at, sub), gaps, empty, unplaced)
        s = cell["stage"]
        count[s] = count.get(s, 0) + 1
        line = {"sub_indicator": sub, "stage": s,
                k1: top if s in ("3", "4", "5") else mid if s == "2" else low if s == "1" else "",
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
