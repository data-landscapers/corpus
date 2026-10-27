"""study-ladder-ictstrategy.py — the ictstrategy study's ladder applied to the review's evidence, strictly.

    python scripts/study-ladder-ictstrategy.py            # the count per rung, and the test file
    python scripts/study-ladder-ictstrategy.py --as-at 2026-09-30

Task D3 of `maturity/ictstrategy/maturity-study-ictstrategy.md`: **a test of the ladder, not a
staging.** `study-ladder-digitalstrategy.py` is its model and its docstring holds the reasons:
rows are grouped by `system`, which `maturity/ictstrategy/instruments.csv` has made one name per
instrument, and the country is placed on the sector policy in force.

**What this ladder adds is the neighbouring row.** A country with no sector policy in force
or in preparation, whose national digital strategy `digitalstrategy` has staged or left
unplaced, is unplaced here and flagged *under the national strategy*; stage 1 needs that row
to hold nothing as well. An open policy adopted more than ten years before the as-at is
flagged *dated*, and a noted development plan held in place of a policy is flagged *in the
national plan*.

**Fixed at D3**, and stated in the study file:

- the country is placed on its newest adopted sector policy; an older one is read as replaced;
- an open policy that a source says a national digital strategy replaced has ended in the year
  `instruments.csv` gives under `replaced`, and is *lapsed*;
- *text unpublished* is flagged only where a source says there is no public text; a text
  nobody has found stops the cell at stage 2 without the flag.

**Fixed at step 5**: an instrument still `validated`, `drafting` or `announced` whose own period
has ended is not in preparation and places nothing.

Writes `maturity/ictstrategy/ladder-test.csv`, in the columns of the model's.
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

STUDY = "ictstrategy"
NEIGHBOUR = "digitalstrategy"
FIELDS = ["iso3", "sub_indicator", "rung", "instrument", "standing", "period", "text", "plan",
          "reporting", "governance", "flags", "stopped_by"]
PREPARING = ("validated", "drafting", "announced")
NONE = "No ICT sector policy"
UNDER, PLAN, LAPSED, DATED = "under the national strategy", "in the national plan", "lapsed", "dated"


def _date(as_of: str) -> dt.date:
    return study_lib.parse_as_of(as_of or "1900") or dt.date(1900, 1, 1)


def instrument(rows: list[dict], as_at: dt.date, replaced: str = "") -> dict:
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
    # digitalstrategy's D3: published by the government, and not called a draft, is read as adopted.
    out["in_force"] = out["standing"] == "adopted" or (out["standing"] in ("", "announced")
                                                       and out["text"] == "public")
    out["expired"] = bool(replaced) or (out["period"].startswith("to:")
                                        and int(out["period"][3:]) < as_at.year)
    out["date"] = _date(out["standing_as_of"])
    return out


def rung(insts: dict[str, dict], absent: list[dict], as_at: dt.date, national: bool,
         in_plan: bool) -> tuple[str, str, list[str], str]:
    """`(rung, instrument, flags, what stopped it from the next)` for one country."""
    force = {k: v for k, v in insts.items() if v["in_force"]}
    if force:   # D3: the newest adopted policy is the country's; an older one is read as replaced
        newest = max(force, key=lambda k: force[k]["date"])
        force = {newest: force[newest]}
    live = {k: v for k, v in force.items() if not v["expired"]}
    lapsed = {k: v for k, v in force.items() if v["expired"]}
    # Step 5: a draft whose own period has ended, or that was replaced, is not in preparation.
    prep = {k: v for k, v in insts.items() if v["standing"] in PREPARING and not v["in_force"]
            and not v["expired"]}
    noted = ([UNDER] if national else []) + ([PLAN] if in_plan else [])
    if live:
        name, v = max(live.items(), key=lambda kv: (kv[1]["text"] == "public", kv[1]["date"]))
        if v["text"] != "public":
            return "2", name, (["text unpublished"] if v["text"] == "unpublished" else []),                 "adopted, and no public text has been found"
        if v["period"] == "open" or not v["period"]:
            old = 1900 < v["date"].year < as_at.year - 10
            return "3", name, ([DATED] if old else []), "no stated period: an open policy stops at stage 3"
        if v["plan"] not in ("costed", "actions"):
            return "3", name, [], "no delivery plan stated"
        rep_age = _date(v["reporting_as_of"])
        if v["reporting"] not in ("results", "results-all") or rep_age < study_lib.months_back(as_at, 36):
            return "3", name, [], ("reporting is of activity, not against the policy's targets"
                                   if v["reporting"] == "activity" else "no published reporting")
        met = {"body:mandated", "finance:domestic"} <= v["governance"]
        top = v["plan"] == "costed" and v["reporting"] == "results-all" \
            and rep_age >= study_lib.months_back(as_at, 24)
        if not met:
            return "3", name, ["no budget or body"], f"capped from {'5' if top else '4'}"
        if top:
            return "5", name, [], ""
        return "4", name, [], ("the plan is not costed" if v["plan"] != "costed"
                               else "results do not cover every objective inside two years")
    if prep:
        name, v = max(prep.items(), key=lambda kv: kv[1]["date"])
        return "2", name, ([LAPSED] if lapsed else []), f"{v['standing']}, not adopted"
    if lapsed:
        name = max(lapsed, key=lambda k: lapsed[k]["date"])
        return study_lib.UNPLACED, name, [LAPSED] + noted, \
            "its period has ended and no sector policy is on record as its successor"
    if national:
        name = max(insts, key=lambda k: len(insts[k]["governance"])) if insts else ""
        return study_lib.UNPLACED, name, noted, "no sector policy in force; the national digital strategy is staged on its own row"
    if absent and not any(v["standing"] for v in insts.values()):
        return "1", NONE, [], "a dated statement that there is none"
    if insts:
        name = max(insts, key=lambda k: len(insts[k]["governance"]))
        return study_lib.UNPLACED, name, noted, "no standing stated for it"
    if in_plan:
        return study_lib.UNPLACED, "", noted, "only a chapter of a national plan is held"
    return study_lib.NO_EVIDENCE, "", [], "nothing found on a sector policy"


def neighbour() -> set[str]:
    """Countries whose national digital strategy the neighbouring study holds."""
    path = os.path.join(study_lib.out_dir(NEIGHBOUR), "assessment.csv")
    with open(path, encoding="utf-8", newline="") as fh:
        return {r["iso3"] for r in csv.DictReader(fh)
                if r["stage"] in ("2", "3", "4", "5", study_lib.UNPLACED)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-at", default="2026-09-30")
    args = ap.parse_args(argv)
    as_at = dt.date.fromisoformat(args.as_at)
    base = study_lib.study_dir(STUDY)
    held = neighbour()
    replaced = {(r["iso3"], r["instrument"]): r["replaced"]
                for r in study_lib.read_csv(os.path.join(base, "instruments.csv")) if r["replaced"]}
    rows, count = [], collections.Counter()
    for iso in sorted(os.listdir(os.path.join(base, "evidence"))):
        folder = os.path.join(base, "evidence", iso)
        if not os.path.isdir(folder):
            continue
        ev, systems = [], []
        if os.path.exists(os.path.join(folder, "evidence.csv")):
            ev = [r for r in study_lib.read_csv(os.path.join(folder, "evidence.csv")) if r["class"] == "sector"]
        if os.path.exists(os.path.join(folder, "systems.csv")):
            systems = study_lib.read_csv(os.path.join(folder, "systems.csv"))
        groups = collections.defaultdict(list)
        for r in ev:
            groups[r["system"]].append(r)
        absent = [r for r in groups.pop(NONE, []) if r["aspect"] == "standing" and r["value"] == "none"]
        absent += [r for g in groups.values() for r in g if r["aspect"] == "standing" and r["value"] == "none"]
        insts = {k: instrument(g, as_at, replaced.get((iso, k), "")) for k, g in groups.items()}
        in_plan = not insts and any(s["class"] == "development-plan" for s in systems)
        got, name, flags, why = rung(insts, absent, as_at, iso in held, in_plan)
        v = insts.get(name, {})
        if v.get("advancing"):
            flags.append("advancing")
        count[got] += 1
        rows.append({"iso3": iso, "sub_indicator": "sector", "rung": got, "instrument": name,
                     "standing": v.get("standing", ""), "period": v.get("period", ""),
                     "text": v.get("text", ""), "plan": v.get("plan", ""),
                     "reporting": v.get("reporting", ""),
                     "governance": ";".join(sorted(v.get("governance", ()))),
                     "flags": ";".join(flags), "stopped_by": why})
    study_lib.write_csv(os.path.join(base, "ladder-test.csv"), FIELDS, rows)
    print("study-ladder-ictstrategy:", ", ".join(f"{k}: {count[k]}" for k in
                                                 ("5", "4", "3", "2", "1", study_lib.UNPLACED,
                                                  study_lib.NO_EVIDENCE)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
