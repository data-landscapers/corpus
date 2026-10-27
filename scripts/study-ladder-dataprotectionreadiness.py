#!/usr/bin/env python3
r"""study-ladder-dataprotectionreadiness.py — the readiness study's four questions, counted.

    python scripts/study-ladder-dataprotectionreadiness.py --as-at 2026-09-30
    python scripts/study-ladder-dataprotectionreadiness.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as
`study-ladder-dataprotectionauthority.py` does it for the authority row. The ladder is
`maturity-study-dataprotectionreadiness.md` §2 and §3 *(Bill, 2026-10-11: the ability to
act, with the Malabo Convention at stage 3 and never needed above it)*:

1. **Law in force**: the law study's `standing` of `in-force` or `transition`.
2. **Ratified or appointed**: a `treaty` fact of `ratified`, or the authority study's
   `standing` of `constituted`.
3. **Implementing**: a `practice` fact dated inside three years, where an authority is
   appointed: what a ministry does with no authority in place is not the authority's work.
4. **Acting**: the authority study's `rulings`, which already leaves out courts.

**Questions 1, 2 and 4 take the two studies' issued answers**, so the three rows cannot
disagree; this study's own rows are what `stage_sources` cites. Stage 1 is the law study
finding no law in force. A country the law study could not place has no evidence here.

`corrections.csv`, where the parent's reading removed or revalued a row, is applied to
`evidence.csv` first, once. Writes each `stage.json` and `ladder-test.csv`.

Like every ladder, it counts a country at `study_lib.counted_at` and leaves a cell staged
by hand, which `study_lib.write_stage` keeps.

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

STUDY, LAW, BODY = "dataprotectionreadiness", "dataprotectionlaw", "dataprotectionauthority"
GAPS = {
    "5": "Nothing on the four questions.",
    "4": "No ruling of the authority against a named organisation in the last three years has been found.",
    "3": "No source dated in the last three years shows an appointed authority registering "
         "organisations, taking breach reports, issuing guidance or inspecting.",
    "2": "The country has not ratified the Malabo Convention, and no source found says an "
         "authority has been appointed.",
    "1": "",
}
NOTE = "Counted from the four questions by study-ladder-dataprotectionreadiness.py."


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


def stage(rows: list[dict], as_at: dt.date, law: str, body: dict) -> dict:
    live = [(last_day(r["as_of"]), r) for r in rows if last_day(r["as_of"]) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    three = study_lib.months_back(as_at, 36)
    pick = lambda aspect, values, since=None, n=2: [  # noqa: E731
        r["row_id"] for d, r in live if r["aspect"] == aspect and r["value"] in values
        and (since is None or d >= since)][:n]
    in_force = law in ("in-force", "transition")
    appointed = body.get("standing") == "constituted"
    ratified = pick("treaty", ("ratified",), n=1)
    signed = pick("treaty", ("signed",), n=1)
    acting = body.get("rulings") in ("ruled", "reported")
    working = pick("practice", ("implementing", "ruling"), three)
    cols = {"law": "in-force" if in_force else ("not-yet" if law and law != "none" else law),
            "treaty": "ratified" if ratified else "signed" if signed else
                      ("none" if pick("treaty", ("none",)) else ""),
            "authority": "appointed" if appointed else ("none" if body.get("standing") else ""),
            "practice": ""}
    if not law:
        return {**cols, "law": "", "stage": "no evidence", "sources": [],
                "gaps": "Nothing found says whether a data protection law is in force."}
    if not in_force:
        s, src = "1", pick("law", ("not-yet", "none")) + ratified
    elif appointed and acting:
        s, src = "5", (pick("practice", ("ruling",), three) or working) + pick("authority", ("appointed",), n=1)
        cols["practice"] = "ruling"
    elif appointed and working:
        s, src = "4", working + pick("authority", ("appointed",), n=1)
        cols["practice"] = "implementing"
    elif appointed or ratified:
        s, src = "3", pick("law", ("in-force",), n=1) + ratified + pick("authority", ("appointed",), n=1)
    else:
        s, src = "2", pick("law", ("in-force",))
    gaps = GAPS[s]
    if s == "1" and ratified:
        gaps = "The country has ratified the Malabo Convention and has no data protection law in force."
    if s == "3" and working and not appointed:
        gaps += " Activity under the law is on record, with no authority appointed to carry it out."
    return {**cols, "stage": s, "sources": list(dict.fromkeys(src)), "gaps": gaps}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the readiness study from its answers.")
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
    law = {r["iso3"]: r["standing"] for r in study_lib.read_csv(
        os.path.join(study_lib.out_dir(LAW), "assessment.csv"))}
    body = {r["iso3"]: r for r in study_lib.read_csv(
        os.path.join(study_lib.out_dir(BODY), "assessment.csv"))}
    test, count = [], {}
    for iso in sorted(study_lib.countries()):
        path = os.path.join(base, iso, "evidence.csv")
        rows, changed = correct(study_lib.read_csv(path), [f for f in fixes if f["iso3"] == iso])
        if changed and not a.dry:
            study_lib.write_csv(path, study_lib.EVIDENCE_FIELDS, rows)
        cell = stage(rows, study_lib.counted_at(os.path.join(base, iso, "stage.json"), as_at),
                     law.get(iso, ""), body.get(iso, {}))
        count[cell["stage"]] = count.get(cell["stage"], 0) + 1
        line = {"sub_indicator": "system", "stage": cell["stage"], "law": cell["law"],
                "treaty": cell["treaty"], "authority": cell["authority"], "practice": cell["practice"],
                "cap": "", "flags": "", "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": NOTE}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "law", "treaty", "authority",
                                                         "practice", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "law", "treaty", "authority", "practice", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
