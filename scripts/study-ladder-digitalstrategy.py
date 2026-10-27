#!/usr/bin/env python3
r"""study-ladder-digitalstrategy.py — the digitalstrategy study's ladder applied to the review's evidence, strictly.

    python scripts/study-ladder-digitalstrategy.py            # the count per rung, and the test file
    python scripts/study-ladder-digitalstrategy.py --as-at 2026-09-30

Task D3 of `maturity/digitalstrategy/maturity-study-digitalstrategy.md`: **a test of the ladder,
not a staging.** It reads only closed values, so a rung that needs something no value carries
shows up as a rung nobody reaches, with the reason beside every country it stopped.

**It reads `evidence.csv`, not `profile.csv`, because a country holds several instruments.** A
profile takes the newest value per aspect across every row, so an expired strategy's cost sits
beside its successor's drafting. Here the rows are grouped by `system`, which
`maturity/digitalstrategy/instruments.csv` has made one name per instrument, and the country is
placed on the instrument in force: adopted and inside its period, the newest where there are two.

**Fixed at D3**, and stated in the study file:

- a source's own word of approval or adoption is `adopted`; the act named is not required;
- a strategy whose text the government has published, and which no source calls a draft, is
  read as adopted, whether or not a launch or an act is on record;
- a statement of absence places a country at stage 1 only where nothing is on record as
  adopted, launched or in preparation;
- a published rate of execution of the strategy's own actions is `results`;
- the period is its end year, and whether the text is public is an aspect of its own.

Writes `maturity/digitalstrategy/ladder-test.csv`: one row per country, with the rung, the
instrument it was read from, that instrument's values and what kept it from the rung above.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402

STUDY = "digitalstrategy"
FIELDS = ["iso3", "sub_indicator", "rung", "instrument", "standing", "period", "text", "plan",
          "reporting", "governance", "flags", "stopped_by"]
PREPARING = ("validated", "drafting", "announced")
NONE = "No national digital strategy"


def _date(as_of: str) -> dt.date:
    return study_lib.parse_as_of(as_of or "1900") or dt.date(1900, 1, 1)


def instrument(rows: list[dict], as_at: dt.date) -> dict:
    """One instrument's values, from its evidence rows."""
    by = collections.defaultdict(list)
    for r in rows:
        by[r["aspect"]].append(r)
    newest = lambda a: max(by[a], key=lambda r: _date(r["as_of"]))  # noqa: E731
    out = {"standing": "", "standing_as_of": "", "period": "", "text": "", "plan": "",
           "reporting": "", "reporting_as_of": "", "governance": set()}
    stand = {r["value"] for r in by["standing"]}
    if "adopted" in stand:
        out["standing"] = "adopted"
        out["standing_as_of"] = min(r["as_of"] for r in by["standing"] if r["value"] == "adopted")
    elif by["standing"]:
        n = newest("standing")
        out["standing"], out["standing_as_of"] = n["value"], n["as_of"]
    ends = [int(r["value"][3:]) for r in by["period"] if r["value"].startswith("to:")]
    out["period"] = f"to:{max(ends)}" if ends else ("open" if by["period"] else "")
    texts = {r["value"] for r in by["text"]}
    out["text"] = "public" if "public" in texts else ("unpublished" if texts else "")
    plans = {r["value"] for r in by["plan"]}
    out["plan"] = next((v for v in ("costed", "actions", "none") if v in plans), "")
    reps = [r for r in by["reporting"] if r["value"] != "none"]
    if reps:
        best = min(reps, key=lambda r: (("results-all", "results", "activity").index(r["value"]),
                                        -_date(r["as_of"]).toordinal()))
        out["reporting"], out["reporting_as_of"] = best["value"], best["as_of"]
    elif by["reporting"]:
        out["reporting"] = "none"
    out["governance"] = {r["value"] for r in by["governance"]}
    out["advancing"] = any(r["value"] == "advancing" and _date(r["as_of"]) >= study_lib.months_back(as_at, 12)
                           for r in by["last12"])
    # D3: published by the government, and not called a draft, is read as adopted.
    out["in_force"] = out["standing"] == "adopted" or (out["standing"] in ("", "announced")
                                                       and out["text"] == "public")
    out["expired"] = out["period"].startswith("to:") and int(out["period"][3:]) < as_at.year
    out["date"] = _date(out["standing_as_of"])
    return out


def rung(insts: dict[str, dict], absent: list[dict], as_at: dt.date) -> tuple[str, str, list[str], str]:
    """`(rung, instrument, flags, what stopped it from the next)` for one country."""
    live = {k: v for k, v in insts.items() if v["in_force"] and not v["expired"]}
    lapsed = {k: v for k, v in insts.items() if v["in_force"] and v["expired"]}
    prep = {k: v for k, v in insts.items() if v["standing"] in PREPARING and not v["in_force"]}
    if live:
        name, v = max(live.items(), key=lambda kv: (kv[1]["text"] == "public", kv[1]["date"]))
        if v["text"] != "public":
            return "2", name, ["text unpublished"], "adopted, and no public text has been found"
        flags = []
        if v["period"] == "open" or not v["period"]:
            return "3", name, flags, "no stated period: an open strategy stops at stage 3"
        if v["plan"] not in ("costed", "actions"):
            return "3", name, flags, "no delivery plan stated"
        rep_age = _date(v["reporting_as_of"])
        if v["reporting"] not in ("results", "results-all") or rep_age < study_lib.months_back(as_at, 36):
            return "3", name, flags, ("reporting is of activity, not against the strategy's targets"
                                      if v["reporting"] == "activity" else "no published reporting")
        met = {"body:mandated", "finance:domestic"} <= v["governance"]
        top = v["plan"] == "costed" and v["reporting"] == "results-all" \
            and rep_age >= study_lib.months_back(as_at, 24)
        if not met:
            return "3", name, ["no budget or body"], f"capped from {'5' if top else '4'}"
        if top:
            return "5", name, flags, ""
        return "4", name, flags, ("the plan is not costed" if v["plan"] != "costed"
                                  else "results do not cover every pillar inside two years")
    if prep:
        name, v = max(prep.items(), key=lambda kv: kv[1]["date"])
        return "2", name, (["lapsed"] if lapsed else []), f"{v['standing']}, not adopted"
    if lapsed:
        name = max(lapsed, key=lambda k: lapsed[k]["date"])
        return study_lib.UNPLACED, name, ["lapsed"], "its period has ended and no successor is on record"
    if absent and not any(v["standing"] for v in insts.values()):
        return "1", NONE, [], "a dated statement that there is none"
    if insts:
        name = max(insts, key=lambda k: len(insts[k]["governance"]))
        return study_lib.UNPLACED, name, [], "no standing stated for it"
    return study_lib.NO_EVIDENCE, "", [], "nothing found on a national strategy"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-at", default="2026-09-30")
    args = ap.parse_args(argv)
    as_at = dt.date.fromisoformat(args.as_at)
    base = study_lib.study_dir(STUDY)
    rows, count = [], collections.Counter()
    for iso in sorted(os.listdir(os.path.join(base, "evidence"))):
        path = os.path.join(base, "evidence", iso, "evidence.csv")
        if not os.path.isdir(os.path.dirname(path)):
            continue
        ev = []
        if os.path.exists(path):
            with open(path, encoding="utf-8", newline="") as fh:
                ev = [r for r in csv.DictReader(fh) if r["class"] == "national"]
        groups = collections.defaultdict(list)
        for r in ev:
            groups[r["system"]].append(r)
        absent = [r for r in groups.pop(NONE, []) if r["aspect"] == "standing" and r["value"] == "none"]
        absent += [r for g in groups.values() for r in g if r["aspect"] == "standing" and r["value"] == "none"]
        insts = {k: instrument(g, as_at) for k, g in groups.items()}
        got, name, flags, why = rung(insts, absent, as_at)
        v = insts.get(name, {})
        if v.get("advancing"):
            flags.append("advancing")
        count[got] += 1
        rows.append({"iso3": iso, "sub_indicator": "national", "rung": got, "instrument": name,
                     "standing": v.get("standing", ""), "period": v.get("period", ""),
                     "text": v.get("text", ""), "plan": v.get("plan", ""),
                     "reporting": v.get("reporting", ""),
                     "governance": ";".join(sorted(v.get("governance", ()))),
                     "flags": ";".join(flags), "stopped_by": why})
    with open(os.path.join(base, "ladder-test.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print("study-ladder-digitalstrategy:", ", ".join(f"{k}: {count[k]}" for k in
                                                     ("5", "4", "3", "2", "1", study_lib.UNPLACED,
                                                      study_lib.NO_EVIDENCE)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
