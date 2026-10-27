#!/usr/bin/env python3
r"""study-ladder-admindata.py — the admindata study's four questions, counted.

    python scripts/study-ladder-admindata.py --as-at 2026-09-30
    python scripts/study-ladder-admindata.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-censuses.py` does it.
The ladder is `maturity-study-admindata.md` §2 and §3 as changed on 2026-10-19 *(Bill)*, every
window three years:

1. **Preparing**: a `use` of `preparing`, or a yes to any later question.
2. **Published**: a `use` of `published`, or any `source` or `series` row.
3. **Operating**: one administrative source published twice.
4. **Leading**: three administrative sources, each published twice.

**A publication is a `source` row's product**, `system` read as its set of words, so one report
named two ways or carried by two rows counts once. A `series` row, a dated statement that a
product is published regularly, counts as two for each source it names. A `use` of `published`
names no source; its product, `system` without its years, counts towards question 3 only.

**A later yes answers the earlier ones** (method §3.3). Stage 1 is a `use` of `none` with no
other yes. A fact dated after the as-at sets nothing. A year or a month stands for its last day.

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

STUDY = "admindata"
SOURCES = ["civil-registration", "education", "health", "customs", "tax", "social-security", "justice",
           "police", "transport", "other"]   # study.json -> aspects, source
GAPS = {
    "5": "",
    "4": "No source found shows statistics from three administrative sources, each published twice since October 2023.",
    "3": "No source found shows statistics from one administrative source published twice since October 2023.",
    "2": "No source found reports statistics from administrative records published since October 2023.",
    "1": "",
}
YEAR = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")


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


def words(r: dict, years: bool = True) -> frozenset:
    """A publication as its set of words: `2022 Vital Statistics Report` is `Vital Statistics Report 2022`."""
    w = re.findall(r"[a-z0-9]+", (r.get("system") or r.get("fact", "")[:80]).lower())
    return frozenset(x for x in w if years or not x.isdigit())


def stage(rows: list[dict], as_at: dt.date) -> dict:
    three = study_lib.months_back(as_at, 36)
    live = [(last_day(r["as_of"]), r) for r in rows if r.get("as_of") and three <= last_day(r["as_of"]) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    pick = lambda aspect, values: [  # noqa: E731
        r["row_id"] for d, r in live if r["aspect"] == aspect and r["value"] in values]
    if not rows:
        return {"stage": "no evidence", "sources": [], "source": "", "series": "",
                "gaps": "Nothing found names statistics drawn from administrative records, or says there are none."}
    pubs, series = {}, {}   # source -> {publication: first row}, source -> first row
    for d, r in live:
        names = [v.strip() for v in r["value"].split(";") if v.strip()]
        if r["aspect"] == "source":
            for s in names:
                pubs.setdefault(s, {}).setdefault(words(r), r["row_id"])
        elif r["aspect"] == "series":
            for s in names:
                series.setdefault(s, r["row_id"])
        elif r["aspect"] == "use" and r["value"] == "published":
            pubs.setdefault(("unnamed", words(r, years=False)), {}).setdefault(words(r), r["row_id"])
    twice = {}   # source -> the rows that show it published twice
    for s in set(pubs) | set(series):
        if len(pubs.get(s, {})) >= 2:   # two editions held are named before a statement of a series
            twice[s] = list(pubs[s].values())[:2]
        elif s in series:
            twice[s] = [series[s]]
    named = [s for s in twice if isinstance(s, str)]
    order = lambda ss: sorted(ss, key=lambda s: SOURCES.index(s) if s in SOURCES else len(SOURCES))  # noqa: E731
    published = [i for k, p in pubs.items() if isinstance(k, str) for i in p.values()] + list(series.values())         + pick("use", ("published",))   # a named source first
    preparing, none = pick("use", ("preparing",)), pick("use", ("none",))
    if len(named) >= 3:
        s, src = "5", [i for k in order(named)[:3] for i in twice[k]]
    elif twice:
        s, src = "4", twice[order(named)[0]] if named else next(iter(twice.values()))
    elif published:
        s, src = "3", published[:2]
    elif preparing:
        s, src = "2", preparing[:2]
    elif none:
        s, src = "1", none[:2]
    else:
        return {"stage": "unplaced", "sources": [], "source": "", "series": "",
                "gaps": "No statistics from administrative records published, and no work towards them, "
                        "is on record since October 2023."}
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s],
            "source": ";".join(order(k for k in pubs if isinstance(k, str))),
            "series": ";".join(order(series))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the admindata study from its answers.")
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
        line = {"sub_indicator": "admin", "stage": s,
                "use": "published" if s in ("3", "4", "5") else "preparing" if s == "2" else "none" if s == "1" else "",
                "source": cell["source"], "series": cell["series"], "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-admindata.py, on the ladder of 2026-10-19."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "use", "source", "series", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "use", "source", "series", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
