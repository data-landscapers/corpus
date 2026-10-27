#!/usr/bin/env python3
r"""study-ladder-statisticsstrategy.py — the statistics strategy study's four questions, counted.

    python scripts/study-ladder-statisticsstrategy.py --as-at 2026-09-30
    python scripts/study-ladder-statisticsstrategy.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-statisticslaw.py`
does it. The ladder is `maturity-study-statisticsstrategy.md` §2 and §3:

1. **Preparing or adopted**: a `standing` of `preparing` dated inside three years of the
   as-at, or of `adopted` whose stated period opens inside them. A status table that lists a
   2017-2021 strategy in 2026 dates the listing, not the adoption. An extension issued inside them
   is an adoption inside them, whatever period the strategy it extends was given.
2. **Current**: a `standing` of `adopted` whose stated period includes the as-at. The period
   is read from the row's `system`, then its `fact`: a range such as `2021-2025` or
   `2022/23-2026/27` runs to the last day of its final year. An adoption with no period
   stated counts for five years from its date.
3. **Reviewed**: a `review` of `reviewed` dated inside three years.
4. **Evaluated**: an `evaluation` of `evaluated` dated inside three years.

**A later yes answers the earlier ones** (method §3.3): a review shows a strategy was
adopted. An evaluation counts where a current strategy is held, or where none is held at
all; the final evaluation of a strategy that has ended, beside no current successor, is
noted and sets nothing. Stage 1 is a `standing` of `none` dated inside three years with no
other yes. A fact dated after the as-at sets nothing. A year or a month stands for its last
day.

`corrections.csv`, where the parent's reading removed or revalued a row, is applied to
`evidence.csv` first, once. Writes each `stage.json` and `ladder-test.csv`.

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

STUDY = "statisticsstrategy"
NO_PERIOD_YEARS = 5
GAPS = {
    "5": "",
    "4": "No source found reports an evaluation of the strategy completed in the last three years.",
    "3": "No source found dates a review of progress on the strategy in the last three years.",
    "2": "No source found shows an adopted strategy whose period is still running.",
    "1": "",
}
RANGE = re.compile(r"((?:19|20)\d{2})(?:\s*/\s*\d{2,4})?\s*(?:-|–|—|to|à|a)\s*((?:19|20)\d{2})(?:\s*/\s*(\d{2}))?")


def last_day(as_of: str) -> dt.date:
    p = [int(x) for x in as_of.split("-")]
    if len(p) == 1:
        return dt.date(p[0], 12, 31)
    if len(p) == 2:
        return dt.date(p[0], p[1], calendar.monthrange(p[0], p[1])[1])
    return dt.date(*p)


def period_start(r: dict) -> dt.date | None:
    """The first day of the strategy's stated period, where one is stated."""
    for text in (r.get("system", ""), r.get("fact", "")):
        m = RANGE.search(text or "")
        if m and int(m.group(2)) >= int(m.group(1)):
            return dt.date(int(m.group(1)), 1, 1)
    return None


def period_end(r: dict, adopted: dt.date) -> dt.date:
    """The last day of the strategy's stated period, or five years from adoption."""
    for text in (r.get("system", ""), r.get("fact", "")):
        m = RANGE.search(text or "")
        if m and int(m.group(2)) >= int(m.group(1)):
            year = int(m.group(2))
            if m.group(3):
                year = year // 100 * 100 + int(m.group(3))
            return dt.date(year, 12, 31)
    try:
        return adopted.replace(year=adopted.year + NO_PERIOD_YEARS)
    except ValueError:
        return adopted.replace(year=adopted.year + NO_PERIOD_YEARS, day=28)


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
    live = [(last_day(r["as_of"]), r) for r in rows if r.get("as_of") and last_day(r["as_of"]) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    three = study_lib.months_back(as_at, 36)
    pick = lambda aspect, values, since=None: [  # noqa: E731
        r["row_id"] for d, r in live if r["aspect"] == aspect and r["value"] in values
        and (since is None or d >= since)]
    adopted = [(d, r) for d, r in live if r["aspect"] == "standing" and r["value"] == "adopted"]
    current = [r["row_id"] for d, r in adopted if period_end(r, d) >= as_at]
    recent = pick("standing", ("preparing",), three) + [
        r["row_id"] for d, r in adopted if d >= three
        and ((period_start(r) or d) >= three or "extend" in r["fact"].lower())]
    reviewed = pick("review", ("reviewed",), three)
    evaluated = pick("evaluation", ("evaluated",), three) if (current or not adopted) else []
    none = pick("standing", ("none",), three)
    if not rows:
        return {"stage": "no evidence", "standing": "", "sources": [],
                "gaps": "Nothing found names a national statistics strategy, or says there is none."}
    if evaluated:
        s, src = "5", evaluated[:2] + current[:1]
    elif reviewed:
        s, src = "4", reviewed[:2] + current[:1]
    elif current:
        s, src = "3", current[:2]
    elif recent:
        s, src = "2", recent[:2]
    elif none:
        s, src = "1", none[:2]
    else:
        return {"stage": "unplaced", "standing": "", "sources": [],
                "gaps": "No strategy current or in preparation is on record, and no source dated "
                        "in the last three years says the country has none."}
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s],
            "standing": "adopted" if s in "345" else "preparing" if s == "2" else "none"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the statistics strategy study from its answers.")
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
        s = cell["stage"]
        line = {"sub_indicator": "strategy", "stage": s, "standing": cell["standing"],
                "review": "reviewed" if s in "45" and s.isdigit() else "",
                "evaluation": "evaluated" if s == "5" else "", "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-statisticsstrategy.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "standing", "review", "evaluation", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "standing", "review", "evaluation", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
