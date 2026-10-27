#!/usr/bin/env python3
r"""study-ladder-paymentslaw.py — the payments law study's four questions, counted.

    python scripts/study-ladder-paymentslaw.py --as-at 2026-09-30
    python scripts/study-ladder-paymentslaw.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as
`study-ladder-digitalidlaw.py` does it. The ladder is
`maturity-study-paymentslaw.md` §2 and §3:

1. **A draft or a law**: a `standing` of `draft` or `in-force`.
2. **In force**: a `standing` of `in-force`, however old; its year is printed. A later
   `draft` does not undo it: a bill beside a law in force is its replacement being written.
3. **Non-banks licensed under it**: a `reach` of `non-bank`, of any age.
4. **Providers required to connect**: a `reach` of `connect`, of any age.

**A yes to a later question answers the earlier ones** (method §3.3): a non-bank licensed
under the rules shows the rules are in force, and a rule that mobile money providers must
connect shows they are licensed. Stage 1 is a `standing` of `none` dated inside three years
with no draft or law on record. A fact dated after the as-at sets nothing. A year or a
month stands for its last day.

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

STUDY = "paymentslaw"
GAPS = {
    "5": "Nothing on the four questions.",
    "4": "No rule held requires mobile money providers and banks to connect to each other or "
         "to a national or regional switch.",
    "3": "No source found says the law or rules in force license payment providers or e-money "
         "issuers that are not banks, or names one licensed under them.",
    "2": "No source found says a payments law or e-money rules are in force.",
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
    live = [(last_day(r["as_of"]), r) for r in rows if last_day(r["as_of"]) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    three = study_lib.months_back(as_at, 36)
    pick = lambda aspect, values, since=None, n=2: [  # noqa: E731
        r["row_id"] for d, r in live if r["aspect"] == aspect and r["value"] in values
        and (since is None or d >= since)][:n]
    law, draft = pick("standing", ("in-force",)), pick("standing", ("draft",))
    nonbank, connect = pick("reach", ("non-bank",)), pick("reach", ("connect",))
    none = pick("standing", ("none",), three)
    if not rows:
        return {"stage": "no evidence", "standing": "", "reach": "", "sources": [],
                "gaps": "Nothing found names a payments law, e-money rules or a draft of either, "
                        "or says there is none."}
    if connect:
        s, src = "5", connect + nonbank[:1] + law[:1]
    elif nonbank:
        s, src = "4", nonbank + law[:1]
    elif law:
        s, src = "3", law
    elif draft:
        s, src = "2", draft
    elif none:
        s, src = "1", none
    else:
        return {"stage": "unplaced", "standing": "", "reach": "", "sources": [],
                "gaps": "No law, rules or draft is on record, and no source dated in the last "
                        "three years says the country has none."}
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s],
            "standing": "in-force" if s in "345" else "draft" if s == "2" else "none",
            "reach": "connect" if s == "5" else "non-bank" if s == "4" else ""}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the payments law study from its answers.")
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
        line = {"sub_indicator": "law", "stage": cell["stage"], "standing": cell["standing"],
                "reach": cell["reach"], "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-paymentslaw.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "standing", "reach", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "standing", "reach", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
