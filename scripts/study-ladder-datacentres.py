#!/usr/bin/env python3
r"""study-ladder-datacentres.py — the data centres study's four questions, counted.

    python scripts/study-ladder-datacentres.py --as-at 2026-09-30
    python scripts/study-ladder-datacentres.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-exchangepoints.py`
does it. The ladder is `maturity-study-datacentres.md` §2 and §3, and no question has a
window:

1. **For hire, in service**: a `centre` row of `service`, `tier3` or `two`, or a `cloud` row
   of `region`.
2. **Tier III**: a `centre` row of `tier3` or `two`.
3. **Two at Tier III**: a `centre` row of `two`, or `tier3` rows for two facilities whose
   names differ once the generic words are dropped.
4. **A cloud region**: a `cloud` row of `region`, not reversed by a later `cloud` of `none`.

**An unanswered question stops the count** (method §3.6). **A later dated `none` reverses**
(§3.5): a `centre` of `none` dated after every positive row, and inside three years, sets
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

STUDY = "datacentres"
GAPS = {
    "5": "",
    "4": "No source found says a global cloud provider sells its services from a cloud region "
         "in the country.",
    "3": "No source found names a second data centre for hire at Tier III or above.",
    "2": "No source found says a data centre for hire in the country is Tier III or above.",
    "1": "",
}
NOISE = re.compile(r"\b(data|centres?|centers?|datacenters?|datacentres?|dc|the|campus|facility|tier|"
                   r"iii|iv|de|du|d|l|la|le|s\.?a|ltd|limited|plc)\b", re.I)


# The parent's reading (method §7.2): rows that name one facility under different names, so
# question 3 does not count it twice. Raxio runs one data centre in each country it is in.
SAME = {
    "raxio": "AGO-002 AGO-004 AGO-010 AGO-013 AGO-020 AGO-022 AGO-025 CIV-003 CIV-012 CIV-014 "
             "CIV-024 CIV-026 CIV-032 CIV-034 CIV-039 CIV-042 ETH-005 ETH-009 ETH-018 ETH-020 "
             "ETH-025 MOZ-002 MOZ-004 MOZ-008 MOZ-012 MOZ-019 MOZ-023 MOZ-024 UGA-002 UGA-005 "
             "UGA-007 UGA-011 UGA-013 UGA-016 UGA-021 UGA-023 UGA-031 UGA-032",
    "paratus": "AGO-006 AGO-017",
    "camtel": "CMR-001 CMR-008 CMR-010 CMR-011 CMR-013",
    "stdigital": "CMR-003 CMR-017 CMR-020 CMR-025 CMR-028 CIV-017 CIV-019 CIV-021",
    "wingu": "ETH-002 ETH-012 ETH-022 ETH-023 DJI-002 DJI-005",
    "nkok": "GAB-002 GAB-004 GAB-006 GAB-008 GAB-010 GAB-012 GAB-013 GAB-015",
    "onix": "GHA-008 GHA-012 GHA-021 GHA-022 GHA-024",
    "adc": "KEN-011 KEN-048",
    "ixafrica": "KEN-033 KEN-037",
    "vodacom": "MOZ-006 MOZ-016",
    # The state's national data centre and the Data Hub cannot be told apart from what is held.
    "nouakchott": "MRT-002 MRT-004 MRT-006",
    # ST Digital's colocation in Lomé is sold from the SIN's Lomé Data Centre.
    "lome": "TGO-002 TGO-006 TGO-008 TGO-010 TGO-015",
    "kalaa": "TUN-003 TUN-013 TUN-015",
    "dataxion": "TUN-005 TUN-021",
    "rdh": "EGY-004 EGY-019",
}
SAME_OF = {rid: key for key, ids in SAME.items() for rid in ids.split()}


def facility_key(system: str, row_id: str = "") -> str:
    """A facility's name with the generic words dropped, so `the Rack Centre DC` and `Rack Centre` agree."""
    if row_id in SAME_OF:
        return SAME_OF[row_id]
    name = re.sub(r"\(.*?\)", "", study_lib.fold(system or "")).lower()
    return re.sub(r"[^a-z0-9]", "", NOISE.sub("", name))


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
        return {"stage": "no evidence", "sources": [],
                "gaps": "Nothing found names a data centre for hire, or says there is none."}
    pick = lambda aspect, values, since=None, n=2: [  # noqa: E731
        (d, r["row_id"]) for d, r in live if r["aspect"] == aspect and r["value"] in values
        and (since is None or d >= since)][:n]
    ids = lambda ps: [i for _, i in ps]  # noqa: E731
    working = ("service", "tier3", "two")
    service = pick("centre", working) or pick("cloud", ("region",))
    positive = sorted(pick("centre", working, n=1) + pick("cloud", ("region",), n=1), reverse=True)
    none = pick("centre", ("none",), three)
    if none and (not positive or none[0][0] > positive[0][0]):
        return {"stage": "1", "sources": ids(none), "gaps": ""}
    if not service:
        return {"stage": "unplaced", "sources": [],
                "gaps": "No source found says a data centre in the country rents space or "
                        "computing to others, and none dated in the last three years says "
                        "there is none."}
    tier = [(d, r) for d, r in live if r["aspect"] == "centre" and r["value"] in ("tier3", "two")]
    two = [r["row_id"] for _, r in tier if r["value"] == "two"][:1]
    if not two:
        seen = {}
        for _, r in tier:
            seen.setdefault(facility_key(r.get("system", ""), r["row_id"]), r["row_id"])
        if len(seen) >= 2:
            two = list(seen.values())[:2]
    region = pick("cloud", ("region",), n=1)
    gone = pick("cloud", ("none",), n=1)
    if region and gone and gone[0][0] > region[0][0]:
        region = []
    s, src = "2", ids(service)[:1]
    if tier:
        s, src = "3", [tier[0][1]["row_id"]]
        if two:
            s, src = "4", two
            if region:
                s, src = "5", src + ids(region)
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the data centres study from its answers.")
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
        line = {"sub_indicator": "datacentre", "stage": s,
                "centre": {"5": "two", "4": "two", "3": "tier3", "2": "service",
                           "1": "none"}.get(s, ""),
                "cloud": "region" if s == "5" else "", "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-datacentres.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "centre", "cloud", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "centre", "cloud", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
