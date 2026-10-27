#!/usr/bin/env python3
r"""study-ladder-qualitystandards.py — the quality standards study's four questions, counted.

    python scripts/study-ladder-qualitystandards.py --as-at 2026-09-30
    python scripts/study-ladder-qualitystandards.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-datatransfers.py`
does it. The ladder is `maturity-study-qualitystandards.md` §2 and §3:

1. **A national standards body**: a `standing` of `body` or `published`, however old.
2. **A national standard on information technology or data**: a `standing` of `published`,
   however old.
3. **Certification against one on offer in the country**: a `certification` of `offered`,
   of any age.
4. **A public body certified in the last three years**: a `certification` of `public-body`
   dated inside them. An older one answers question 3 and nothing more.

A yes to a later question answers the earlier ones. Stage 1 is a `standing` of `none` dated
inside three years with no body on record. A fact dated after the as-at sets nothing. A year
or a month stands for its last day, or for the as-at where that day falls after it and the
source was published by it.

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

STUDY = "qualitystandards"
GAPS = {
    "5": "All four questions are answered.",
    "4": "No source from the last three years naming a public body certified against a "
         "national standard on information technology or data, by the standards body or a "
         "certifier accredited in the country, is held.",
    "3": "No source found says the standards body or a certifier accredited in the country "
         "offers certification against a national standard on information technology or data.",
    "2": "No source found names a national standard on information technology or data.",
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
        if d > as_at and r["date_precision"] != "day" and r["source_slug"][:10] <= as_at.isoformat()                 and r["as_of"] <= as_at.isoformat()[:len(r["as_of"])]:
            return as_at
        return d
    live = [(when(r), r) for r in rows if when(r) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    three = study_lib.months_back(as_at, 36)
    pick = lambda aspect, values, since=None, n=2: [  # noqa: E731
        r["row_id"] for d, r in live if r["aspect"] == aspect and r["value"] in values
        and (since is None or d >= since)][:n]
    issued = pick("standing", ("published",))
    body = pick("standing", ("body",))
    offered = pick("certification", ("offered", "public-body"))
    public = pick("certification", ("public-body",), three)
    none = pick("standing", ("none",), three)
    if not rows:
        return {"stage": "no evidence", "standing": "", "certification": "", "sources": [],
                "gaps": "Nothing found names a national standards body, or says there is none."}
    if public:
        s, src = "5", public + issued[:1]
    elif offered:
        s, src = "4", offered + issued[:1]
    elif issued:
        s, src = "3", issued + body[:1]
    elif body:
        s, src = "2", body
    elif none:
        s, src = "1", none
    else:
        return {"stage": "unplaced", "standing": "", "certification": "", "sources": [],
                "gaps": "No standards body is on record, and no source dated in the last "
                        "three years says the country has none."}
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s],
            "standing": "published" if s in "345" else "none" if s == "1" else "body",
            "certification": "public-body" if s == "5" else "offered" if s == "4" else ""}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the quality standards study from its answers.")
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
        line = {"sub_indicator": "standards", "stage": cell["stage"], "standing": cell["standing"],
                "certification": cell["certification"], "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-qualitystandards.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "standing", "certification", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "standing", "certification", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
