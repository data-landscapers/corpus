#!/usr/bin/env python3
r"""study-ladder-internationalbandwidth.py — the international routes study's four questions, counted.

    python scripts/study-ladder-internationalbandwidth.py --as-at 2026-09-30
    python scripts/study-ladder-internationalbandwidth.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-fibrebackbone.py`
does it. The ladder is `maturity-study-internationalbandwidth.md` §2 and §3:

1. **One route**: a `routes` row of `one`, `two` or `independent`, of any age.
2. **Two routes**: a `routes` row of `two` or `independent`, or `one` rows naming two
   different routes, "on one source or two".
3. **Two independent**: a `routes` row of `independent`, of any age.
4. **Capacity sold**: an `access` of `open`, of any age, where question 3 is a yes.

**A yes to a later question answers the earlier ones** (method §3.3); question 4 needs
question 3. **A later dated `none` reverses** (method §3.5): a `routes` of `none` dated after
every positive `routes` row, and inside three years, sets stage 1; an `access` of `none`
after every `open` row withdraws question 4. A fact dated after the as-at sets nothing. A
year or a month stands for its last day, and the as-at's own year for the as-at.

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

STUDY = "internationalbandwidth"
GAPS = {
    "5": "",
    "4": "No source found says other operators buy capacity at the landing station or on the "
         "international routes, or that they run on open-access or wholesale terms.",
    "3": "No source found says two of the routes land at different stations, or run through "
         "two different neighbours.",
    "2": "No source found names a second international fibre route in service.",
    "1": "",
}
NOISE = re.compile(r"\b(submarine|subsea|undersea|cable|cables|system|fibre|fiber|optic|link|"
                   r"the|c[aâ]ble|sous-marin|cabo|submarino)\b", re.I)


def route_key(system: str) -> str:
    """A route's name with the generic words dropped, so `the WACS cable` and `WACS` agree. A
    route a source leaves unnamed gives no key: "the country's single cable" is not a second."""
    if "unnamed" in (system or "").lower():
        return ""
    name = re.sub(r"\(.*?\)", "", study_lib.fold(system or ""))
    return re.sub(r"[^a-z0-9]", "", NOISE.sub("", name).lower())


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
    # A year alone, in the as-at's own year, stands for the as-at: the source was published by it.
    day = lambda a: as_at if a == str(as_at.year) else last_day(a)  # noqa: E731
    live = [(day(r["as_of"]), r) for r in rows if day(r["as_of"]) <= as_at]
    live.sort(key=lambda p: p[0], reverse=True)
    three = study_lib.months_back(as_at, 36)
    if not rows:
        return {"stage": "no evidence", "routes": "", "access": "", "sources": [],
                "gaps": "Nothing found names an international fibre route, or says there is none."}
    pick = lambda aspect, values, since=None, n=2: [  # noqa: E731
        (d, r["row_id"]) for d, r in live if r["aspect"] == aspect and r["value"] in values
        and (since is None or d >= since)][:n]
    ids = lambda ps: [i for _, i in ps]  # noqa: E731
    independent = pick("routes", ("independent",))
    two = pick("routes", ("two", "independent"))
    if not two:
        named = {}
        for _, r in live:
            k = route_key(r.get("system", ""))
            if r["aspect"] == "routes" and r["value"] == "one" and k and k not in named:
                named[k] = r["row_id"]
        if len(named) >= 2:
            two = [(None, i) for i in list(named.values())[:2]]
    one = pick("routes", ("one", "two", "independent"))
    positive = pick("routes", ("independent", "two", "one"), n=1)
    none = pick("routes", ("none",), three)
    if none and (not positive or none[0][0] > positive[0][0]):
        return {"stage": "1", "routes": "none", "access": "", "sources": ids(none), "gaps": ""}
    opened = pick("access", ("open",))
    closed = pick("access", ("none",), n=1)
    if opened and closed and closed[0][0] > opened[0][0]:
        opened = []
    if independent and opened:
        s, src = "5", ids(independent)[:1] + ids(opened)[:1]
    elif independent:
        s, src = "4", ids(independent)
    elif two:
        s, src = "3", ids(two)
    elif one:
        s, src = "2", ids(one)
    else:
        return {"stage": "unplaced", "routes": "", "access": "", "sources": [],
                "gaps": "No source found names an international fibre route in service, and none "
                        "dated in the last three years says there is none."}
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s],
            "routes": {"5": "independent", "4": "independent", "3": "two", "2": "one"}[s],
            "access": "open" if s == "5" else ""}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the international routes study from its answers.")
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
        line = {"sub_indicator": "routes", "stage": cell["stage"], "routes": cell["routes"],
                "access": cell["access"], "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-internationalbandwidth.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "routes", "access", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "routes", "access", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
