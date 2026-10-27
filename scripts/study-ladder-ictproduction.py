#!/usr/bin/env python3
r"""study-ladder-ictproduction.py — the ICT production study's four questions, counted.

    python scripts/study-ladder-ictproduction.py --as-at 2026-09-30
    python scripts/study-ladder-ictproduction.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-mobilepenetration.py`
does it. The ladder is `maturity-study-ictproduction.md` §2 and §3. **One figure sets stages 1
to 4**: the latest ICT service exports over GDP, for 2023 or later and by the as-at, against
lines of 0.05, 0.2 and 0.5 per cent, the frame's own cuts. **Stage 5 adds a plant**: a fact
from the last three years that ICT equipment is assembled or made in the country, counted only
where the figure has cleared 0.5; a plant alone sets no stage, since it is not a step beyond
the figure but the frame's condition beside it.

`corrections.csv` is applied to `evidence.csv` first, once. Writes each `stage.json` and
`ladder-test.csv`.

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

STUDY = "ictproduction"
SUB = "production"
ASPECTS = ("exports", "plant")
FROM = dt.date(2023, 1, 1)
PLANT_FROM = dt.date(2023, 10, 1)
LINES = (0.05, 0.2, 0.5)


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
        d = last_day(r["as_of"])
        # A reference series is cited by its release date, a record by a slug that opens on its own.
        published = r["source_slug"].rsplit("@", 1)[-1] if r["source_slug"].startswith("ref:") \
            else r["source_slug"][:10]
        if (d > as_at and r["date_precision"] != "day" and published <= as_at.isoformat()
                and r["as_of"] <= as_at.isoformat()[:len(r["as_of"])]):
            return as_at
        return d
    if not [r for r in rows if r["aspect"] == "exports"]:
        return {"stage": "no evidence", "exports": "", "plant": "", "sources": [],
                "gaps": "Nothing found gives ICT service exports as a share of GDP."}
    live = [(when(r), r) for r in rows if r["aspect"] == "exports" and r["as_of"]
            and FROM <= when(r) <= as_at]
    if not live:
        return {"stage": "unplaced", "exports": "", "plant": "", "sources": [],
                "gaps": "No figure for 2023 or later has been found for ICT service exports as a share of GDP."}
    _, best = max(live, key=lambda p: (p[0], p[1]["source_slug"].startswith("ref:"), p[1]["row_id"]))
    figure = float(best["value"].split(":", 1)[1])
    cleared = sum(1 for line in LINES if figure >= line)
    sources, plant = [best["row_id"]], ""
    plants = sorted(((when(r), r) for r in rows if r["aspect"] == "plant" and r["value"] == "production"
                     and r["as_of"] and PLANT_FROM <= when(r) <= as_at), key=lambda p: p[0])
    if cleared == len(LINES) and plants:
        plant = "production"
        sources.append(plants[-1][1]["row_id"])
        gap = "All four questions are answered."
        return {"stage": "5", "exports": best["value"], "plant": plant, "sources": sources, "gaps": gap}
    if cleared == len(LINES):
        gap = "No source found since October 2023 says ICT equipment is assembled or made in the country."
    elif cleared == 0:
        gap = ""
    else:
        gap = (f"The latest figure, {figure:g} per cent of GDP for {best['as_of'][:4]}, is below "
               f"{LINES[cleared]:g} per cent.")
    return {"stage": str(cleared + 1), "exports": best["value"], "plant": "", "sources": sources,
            "gaps": gap}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the ICT production study from its figures.")
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
        line = {"sub_indicator": SUB, "stage": cell["stage"], "exports": cell["exports"], "plant": cell["plant"],
                "cap": "", "flags": "", "stage_sources": ";".join(cell["sources"]),
                "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-ictproduction.py."}
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
