#!/usr/bin/env python3
r"""study-ladder-exchangepoints.py — the exchange points study's four questions, counted.

    python scripts/study-ladder-exchangepoints.py --as-at 2026-09-30
    python scripts/study-ladder-exchangepoints.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-internationalbandwidth.py`
does it. The ladder is `maturity-study-exchangepoints.md` §2 and §3:

1. **In service**: an `exchange` row of `service`, `traffic`, `content` or `growing`, or a
   `reach` of `wider`, of any age.
2. **A content network**: an `exchange` row of `content`, of any age.
3. **Traffic growing**: an `exchange` row of `growing` dated in the last three years, or two
   `traffic` rows for the same exchange at least twelve months apart, the later one higher
   and in the last three years. A `traffic` fact opens "Traffic: <figure> <unit>", which is
   what is compared, in Gb/s.
4. **Beyond one city**: a `reach` row of `wider`, of any age.

**An unanswered question stops the count** (method §3.6). **A later dated `none` reverses**
(§3.5): an `exchange` of `none` dated after every positive row, and inside three years, sets
stage 1. A fact dated after the as-at sets nothing; a year or a month stands for its last
day, and the as-at's own year for the as-at.

`corrections.csv` is applied to `evidence.csv` first, once. Writes each `stage.json` and
`ladder-test.csv`.

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

STUDY = "exchangepoints"
GAPS = {
    "5": "",
    "4": "No source found names a second exchange in another city, or networks from other "
         "countries peering at the exchange.",
    "3": "No source found gives the exchange's traffic at two dates a year apart showing growth.",
    "2": "No source found says a global content network has a cache at the exchange or peers there.",
    "1": "",
}
FIGURE = re.compile(r"Traffic:\s*(?:about |around |over |more than |nearly |up to |some )?"
                    r"(\d[\d.,]*)\s*([TGMK])\s*(?:bit/?s|bps|b/s|bits)", re.I)
SCALE = {"t": 1000.0, "g": 1.0, "m": 0.001, "k": 0.000001}
NOISE = re.compile(r"\b(internet|exchange|point|ixp|the|national|de|d|l|ix)\b", re.I)


def exchange_key(system: str) -> str:
    """An exchange's name with the generic words dropped, so `the KIXP` and `KIXP` agree."""
    name = re.sub(r"\(.*?\)", "", study_lib.fold(system or "")).lower()
    return re.sub(r"[^a-z0-9]", "", NOISE.sub("", name))


def gbps(fact: str) -> float | None:
    m = FIGURE.search(fact or "")
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", "")) * SCALE[m.group(2).lower()]
    except ValueError:
        return None


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


def growth(live: list, three: dt.date) -> list[str]:
    """Two traffic figures for one exchange a year apart, the later higher and recent."""
    figs = [(d, exchange_key(r.get("system", "")), gbps(r["fact"]), r["row_id"])
            for d, r in live if r["aspect"] == "exchange" and r["value"] == "traffic"]
    figs = [f for f in figs if f[2] is not None]
    for d2, k2, v2, i2 in sorted(figs, reverse=True):
        if d2 < three:
            continue
        for d1, k1, v1, i1 in figs:
            if k1 == k2 and (d2 - d1).days >= 365 and v2 > v1:
                return [i2, i1]
    return []


def stage(rows: list[dict], as_at: dt.date) -> dict:
    # A year alone, in the as-at's own year, stands for the as-at: the source was published by it.
    day = lambda a: as_at if a == str(as_at.year) else last_day(a)  # noqa: E731
    live = [(day(r["as_of"]), r) for r in rows if day(r["as_of"]) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    three = study_lib.months_back(as_at, 36)
    if not rows:
        return {"stage": "no evidence", "sources": [],
                "gaps": "Nothing found names an exchange point, or says there is none."}
    pick = lambda aspect, values, since=None, n=2: [  # noqa: E731
        (d, r["row_id"]) for d, r in live if r["aspect"] == aspect and r["value"] in values
        and (since is None or d >= since)][:n]
    ids = lambda ps: [i for _, i in ps]  # noqa: E731
    working = ("service", "traffic", "content", "growing")
    service = pick("exchange", working) or pick("reach", ("wider",))
    positive = sorted(pick("exchange", working, n=1) + pick("reach", ("wider",), n=1), reverse=True)
    none = pick("exchange", ("none",), three)
    if none and (not positive or none[0][0] > positive[0][0]):
        return {"stage": "1", "sources": ids(none), "gaps": ""}
    if not service:
        return {"stage": "unplaced", "sources": [],
                "gaps": "No source found says networks exchange traffic at an exchange point in "
                        "the country, and none dated in the last three years says there is none."}
    content = pick("exchange", ("content",))
    grown = ids(pick("exchange", ("growing",), three, n=1)) or growth(live, three)
    wider = pick("reach", ("wider",))
    s, src = "2", ids(service)[:1]
    if content:
        s, src = "3", ids(content)[:1]
        if grown:
            s, src = "4", src + grown
            if wider:
                s, src = "5", src + ids(wider)[:1]
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the exchange points study from its answers.")
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
        line = {"sub_indicator": "exchange", "stage": s,
                "exchange": {"5": "growing", "4": "growing", "3": "content", "2": "service",
                             "1": "none"}.get(s, ""),
                "reach": "wider" if s == "5" else "", "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-exchangepoints.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "exchange", "reach", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "exchange", "reach", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
