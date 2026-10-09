#!/usr/bin/env python3
r"""study-ladder-schools.py — the schools study's ladder applied to the Phase 1 profiles, strictly.

    python scripts/study-ladder-schools.py            # the count per rung, and the test file

Task S3 of `maturity/schools/maturity-study-schools.md`, and `study-ladder-health.py`'s
counterpart: **a test of the ladder, not a staging.** It reads only each profile's closed
values, the hardest reading a rung can be given, so a rung that needs something no value
carries shows up as a rung nobody reaches, with the reason beside every country it stopped.

The ladder is in the study file, where it is argued; it is restated here only because a
count needs code. Two things no value carries, and the count says so instead of guessing:
rung 5's daily attendance and its rural share. A cell that meets rung 5 on the share is
printed as 5 with both named as still to be read from the evidence rows.

Writes `maturity/schools/ladder-test.csv`: one row per country, with the rung, the values it
was read from and what kept it from the rung above.
"""
from __future__ import annotations

import collections
import datetime as dt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402

FIELDS = ["iso3", "sub_indicator", "rung", "levels", "kept", "schools", "schools_as_of", "stopped_by"]
REGISTER = ("enrolment", "keyed-elsewhere")


def share(value: str) -> float | None:
    m = re.fullmatch(r"share:([\d.]+)%", value)
    return float(m.group(1)) if m else None


def rung(levels: set[str], kept: str, schools: str, schools_as_of: str, as_at: dt.date) -> tuple[str, str]:
    """`(rung, what stopped it from the next)` for one country's coverage values."""
    levels = levels - {""}
    if not (levels or kept or schools):
        return study_lib.UNPLACED, "no coverage aspect stated"
    if kept == "paper" and levels <= {"none"} and schools in ("", "none"):
        return "1", "a dated statement of paper only"

    # No level named beside a stated record: read as primary, as the study file rules.
    primary = "P" in levels or (not levels and bool(kept) and kept != "paper")
    pct = share(schools)
    recent = (study_lib.parse_as_of(schools_as_of or "1900") or dt.date(1900, 1, 1))         >= study_lib.months_back(as_at, 24)
    if primary and kept == "routine" and pct is not None and pct > 50:
        if pct >= 90 and recent:
            return "5", "daily attendance and the rural share are not carried by a value"
        return "4", ("the share is older than two years" if pct >= 90 else "under 90 per cent")

    # Rung 3: live past the pilot in some primary schools, for routine entry or as a learner
    # register. `pilot` and `none` are not live; a count, a share or *not published* is.
    live = schools not in ("pilot", "none", "")
    if primary and kept in REGISTER + ("routine",) and live:
        return "3", ("not routine entry: a learner register" if kept in REGISTER
                     else "no share of primary schools over half")
    return "2", ("levels: secondary only" if not primary and levels else
                 "how the record is kept is not stated" if not kept else
                 "paper at primary beside a system elsewhere" if kept == "paper" else
                 "a pilot, or no school said to be using it")


def main(argv=None) -> int:
    as_at = dt.date.fromisoformat(argv[0]) if argv else dt.date.today()
    study = study_lib.load("schools")
    base = os.path.join(study_lib.study_dir("schools"), "evidence")
    barred = study_lib.excluded(study)
    out = []
    for iso in sorted(study_lib.countries()):
        prof = study_lib.read_csv(os.path.join(base, iso, "profile.csv"))
        held = [r for r in study_lib.read_csv(os.path.join(base, iso, "evidence.csv"))
                if r["source_slug"] not in barred]
        for s in study["sub_indicators"]:
            cell = {r["aspect"]: r for r in prof if r["sub_indicator"] == s["key"]}
            val = lambda k: cell.get(k, {}).get("value", "")
            if not any(r["sub_indicator"] == s["key"] for r in held):
                got, why = study_lib.NO_EVIDENCE, "nothing held"
            else:
                got, why = rung(set(val("levels").split(";")), val("kept"), val("schools"),
                                cell.get("schools", {}).get("as_of", ""), as_at)
            out.append({"iso3": iso, "sub_indicator": s["key"], "rung": got, "levels": val("levels"),
                        "kept": val("kept"), "schools": val("schools"),
                        "schools_as_of": cell.get("schools", {}).get("as_of", ""), "stopped_by": why})

    study_lib.write_csv(os.path.join(study_lib.study_dir("schools"), "ladder-test.csv"), FIELDS, out)
    order = ["5", "4", "3", "2", "1", study_lib.UNPLACED, study_lib.NO_EVIDENCE]
    count = collections.Counter(r["rung"] for r in out)
    print("EMIS: " + "  ".join(f"{k} {count.get(k, 0)}" for k in order))
    for k in order[:6]:
        names = " ".join(r["iso3"] for r in out if r["rung"] == k)
        if names:
            print(f"    {k}: {names}")
    for why, n in collections.Counter(r["stopped_by"] for r in out if r["rung"] in "2345").most_common():
        print(f"    stopped, {n:2d}: {why}")
    print("study-ladder-schools: ladder-test.csv written.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
