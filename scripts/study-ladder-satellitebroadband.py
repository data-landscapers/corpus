#!/usr/bin/env python3
r"""study-ladder-satellitebroadband.py — the satellite broadband study's four questions, counted.

    python scripts/study-ladder-satellitebroadband.py --as-at 2026-09-30
    python scripts/study-ladder-satellitebroadband.py --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7, as `study-ladder-exchangepoints.py`
does it. The ladder is `maturity-study-satellitebroadband.md` §2 and §3:

1. **Licensed**: a `service` row of `licensed`, `sale` or `choice`, or a `counted` row of
   `counted`, of any age.
2. **On sale**: a `service` row of `sale` or `choice`, of any age.
3. **Two networks**: a `service` row of `choice`, or `sale` rows naming two different
   satellite networks in `system` (`network()` folds a reseller's name onto its network).
4. **Counted**: a `counted` row of `counted` dated in the last three years.

**An unanswered question stops the count** (method §3.6). **A later dated `none` reverses**
(§3.5), **but only for the network it names**: "Starlink is not licensed" says nothing of a
YahClick service sold beside it, so a `none` cancels the older positive rows of its own network,
and every older row only where it names none. One that says sales were suspended leaves the
licence standing (study file §3), and one about illegal resale or unregistered kits of a
licensed network cancels nothing. Where no positive row survives, a `none` inside three years
sets stage 1: the leading network not licensed and no other held. A fact dated after the as-at
sets nothing; a year or a month stands for its last day, and the as-at's own year for the as-at,
except against a reversal, where a year alone stands for its first day.

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

STUDY = "satellitebroadband"
GAPS = {
    "5": "",
    "4": "No source found gives a subscriber count for satellite broadband published by the "
         "regulator in the last three years.",
    "3": "No source found says services on two different satellite networks are on sale.",
    "2": "No source found says households or businesses can buy satellite broadband from a "
         "licensed provider.",
    "1": "",
}
# A satellite network, by the words a drafter's `system` uses for it or for its resellers.
NETWORKS = [
    ("starlink", re.compile(r"starlink", re.I)),
    ("oneweb", re.compile(r"one\s*web", re.I)),
    ("konnect", re.compile(r"konnect|eutelsat(?!.*one\s*web)", re.I)),
    ("yahsat", re.compile(r"yah\s*(?:click|sat)|thuraya", re.I)),
    ("kuiper", re.compile(r"kuiper|amazon", re.I)),
    ("viasat", re.compile(r"viasat|inmarsat", re.I)),
    ("avanti", re.compile(r"avanti|hylas", re.I)),
    ("intelsat", re.compile(r"intelsat|ses\b|o3b", re.I)),
    ("angosat", re.compile(r"angosat", re.I)),
    ("nigcomsat", re.compile(r"nigcomsat|nigeriasat", re.I)),
    ("arabsat", re.compile(r"arabsat|nilesat", re.I)),
    ("rascom", re.compile(r"rascom", re.I)),
    ("alcomsat", re.compile(r"alcomsat", re.I)),
]
SUSPENDED = re.compile(r"suspen", re.I)
ILLEGAL = re.compile(r"illegal|unlicen[cs]ed (?:re)?sel|unregistered|wi-?fi|seiz|smuggl|resale", re.I)
POSITIVE = ("licensed", "sale", "choice")


def network(system: str) -> str:
    """The satellite network a `system` names, or '' where it names none this knows."""
    for key, pat in NETWORKS:
        if pat.search(system or ""):
            return key
    return ""


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
    day = lambda a: as_at if a == str(as_at.year) else last_day(a)  # noqa: E731
    live = [(day(r["as_of"]), r) for r in rows if day(r["as_of"]) <= as_at]
    live.sort(key=lambda p: (p[0], p[1]["row_id"]), reverse=True)
    three = study_lib.months_back(as_at, 36)
    if not rows:
        return {"stage": "no evidence", "sources": [],
                "gaps": "Nothing found says a satellite broadband provider is licensed, or that none is."}
    nones = [(d, r) for d, r in live if r["aspect"] == "service" and r["value"] == "none"]
    licensed_nets = {network(r.get("system", "")) for _, r in live
                     if r["aspect"] == "service" and r["value"] in POSITIVE}

    def cancelled(d: dt.date, r: dict) -> bool:
        """Whether a later `none` of the same network, or of none named, unsays this row."""
        net = network(r.get("system", ""))
        if len(r["as_of"]) == 4:  # a year alone is weighed against a reversal from its start
            d = dt.date(int(r["as_of"]), 1, 1)
        for dn, n in nones:
            if dn <= d:
                continue
            nnet = network(n.get("system", "")) or network(n["fact"])
            if nnet and nnet != net:
                continue
            if nnet and nnet in licensed_nets and ILLEGAL.search(n["fact"]):
                continue
            if SUSPENDED.search(n["fact"]) and r["value"] == "licensed":
                continue
            return True
        return False

    live = [(d, r) for d, r in live if r["value"] == "none" or not cancelled(d, r)]
    pick = lambda aspect, values, since=None, n=2: [  # noqa: E731
        (d, r) for d, r in live if r["aspect"] == aspect and r["value"] in values
        and (since is None or d >= since)][:n]
    ids = lambda ps: [r["row_id"] for _, r in ps]  # noqa: E731
    licensed = pick("service", POSITIVE) or pick("counted", ("counted",))
    none = pick("service", ("none",), three)
    if none and not licensed:
        return {"stage": "1", "sources": ids(none[:1]), "gaps": ""}
    if not licensed:
        return {"stage": "unplaced", "sources": [],
                "gaps": "No source found says a satellite broadband provider is licensed, and none "
                        "dated in the last three years says none is."}
    sale = pick("service", ("sale", "choice"), n=99)
    choice = pick("service", ("choice",), n=1)
    if not choice:
        seen = {}
        for d, r in sale:
            seen.setdefault(network(r.get("system", "")), (d, r))
        seen.pop("", None)
        if len(seen) >= 2:
            choice = list(seen.values())[:2]
    counted = pick("counted", ("counted",), three, n=1)
    s, src = "2", ids(licensed)[:1]
    if sale:
        s, src = "3", ids(sale)[:1]
        if choice:
            s, src = "4", ids(choice)
            if counted:
                s, src = "5", src + ids(counted)
    return {"stage": s, "sources": list(dict.fromkeys(src)), "gaps": GAPS[s]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stage the satellite broadband study from its answers.")
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
    fixes = study_lib.read_csv(os.path.join(study_lib.study_dir(STUDY), "corrections.csv")) \
        if os.path.exists(os.path.join(study_lib.study_dir(STUDY), "corrections.csv")) else []
    test, count = [], {}
    for iso in sorted(study_lib.countries()):
        path = os.path.join(base, iso, "evidence.csv")
        rows = study_lib.read_csv(path) if os.path.exists(path) else []
        rows, changed = correct(rows, [f for f in fixes if f["iso3"] == iso])
        if changed and not a.dry:
            study_lib.write_csv(path, study_lib.EVIDENCE_FIELDS, rows)
        cell = stage(rows, study_lib.counted_at(os.path.join(base, iso, "stage.json"), as_at))
        count[cell["stage"]] = count.get(cell["stage"], 0) + 1
        s = cell["stage"]
        line = {"sub_indicator": "satellite", "stage": s,
                "service": {"5": "choice", "4": "choice", "3": "sale", "2": "licensed",
                            "1": "none"}.get(s, ""),
                "counted": "counted" if s == "5" else "", "cap": "", "flags": "",
                "stage_sources": ";".join(cell["sources"]), "gaps": cell["gaps"],
                "note": "Counted from the four questions by study-ladder-satellitebroadband.py."}
        test.append({"iso3": iso, **{k: line[k] for k in ("stage", "service", "counted", "stage_sources")}})
        if a.dry:
            continue
        os.makedirs(os.path.join(base, iso), exist_ok=True)
        study_lib.write_stage(os.path.join(base, iso, "stage.json"), iso, [line])
    if not a.dry:
        study_lib.write_csv(os.path.join(study_lib.study_dir(STUDY), "ladder-test.csv"),
                            ["iso3", "stage", "service", "counted", "stage_sources"], test)
    print("study-ladder: " + ", ".join(f"{k}: {count[k]}" for k in sorted(count, reverse=True))
          + (" (dry run, nothing written)." if a.dry else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
