#!/usr/bin/env python3
r"""study-ladder-police.py — the police study's ladder applied to the review's profiles, strictly.

    python scripts/study-ladder-police.py            # the count per rung, and the test file

Task P3 of `maturity/police/maturity-study-police.md`, and `study-ladder-registry.py`'s
counterpart: **a test of the ladder, not a staging.** It reads only each profile's closed
values, so a rung that needs something no value carries shows up as a rung nobody reaches,
with the reason beside every country it stopped.

Three things no value carries, and the count says so instead of guessing: rung 5's rural
share, whether a rung 4 share was published with its numerator and denominator, and whether
the stations a rung 3 system is live in lie outside the capital. An `equipped:` share counts
stations given or connected to a system, not stations recording, and places by the lower rung
however high it is.

Writes `maturity/police/ladder-test.csv`: one row per country, with the rung, the values it
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

FIELDS = ["iso3", "sub_indicator", "rung", "records", "made", "stations", "stations_as_of", "stopped_by"]
DIGITAL = ("connected", "local", "keyed-elsewhere")


def share(value: str) -> float | None:
    m = re.fullmatch(r"share:([\d.]+)%", value)
    return float(m.group(1)) if m else None


def rung(records: set[str], made: str, stations: str, stations_as_of: str, as_at: dt.date) -> tuple[str, str]:
    """`(rung, what stopped it from the next)` for one country's coverage values."""
    records = records - {""}
    if not (records or made or stations):
        return study_lib.UNPLACED, "no coverage aspect stated"
    if made == "paper" and records <= {"none"} and stations in ("", "none"):
        return "1", "a dated statement of paper only"

    # No record named beside a stated digital record: read as O, as the study file rules.
    named = records - {"none"}
    either = bool(named) or made in DIGITAL
    both = {"O", "C"} <= named
    pct = share(stations)
    recent = (study_lib.parse_as_of(stations_as_of or "1900") or dt.date(1900, 1, 1))         >= study_lib.months_back(as_at, 24)
    if either and made == "connected" and pct is not None and pct > 50:
        if pct >= 90 and recent and both:
            return "5", "the rural share is not carried by a value"
        return "4", ("one record only" if pct >= 90 and recent and not both else
                     "the share is older than two years" if pct >= 90 else "under 90 per cent")

    # Rung 3: past the pilot and live in some stations. `pilot` and `none` are not live;
    # a share, an equipped share, a count or *not published* is.
    live = stations not in ("pilot", "none", "")
    if either and made in DIGITAL and live:
        return "3", ("a share of stations equipped, not recording" if stations.startswith("equipped:") else
                     "the record is not held in the national system" if made != "connected" else
                     "no share of stations over half")
    return "2", ("how the record is made is not stated" if not made else
                 "paper at stations beside a system elsewhere" if made == "paper" else
                 "a pilot, or no station said to be using it")


def main(argv=None) -> int:
    as_at = dt.date.fromisoformat(argv[0]) if argv else dt.date.today()
    study = study_lib.load("police")
    base = os.path.join(study_lib.study_dir("police"), "evidence")
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
                got, why = rung(set(val("records").split(";")), val("made"), val("stations"),
                                cell.get("stations", {}).get("as_of", ""), as_at)
            out.append({"iso3": iso, "sub_indicator": s["key"], "rung": got, "records": val("records"),
                        "made": val("made"), "stations": val("stations"),
                        "stations_as_of": cell.get("stations", {}).get("as_of", ""), "stopped_by": why})

    study_lib.write_csv(os.path.join(study_lib.study_dir("police"), "ladder-test.csv"), FIELDS, out)
    order = ["5", "4", "3", "2", "1", study_lib.UNPLACED, study_lib.NO_EVIDENCE]
    count = collections.Counter(r["rung"] for r in out)
    print("Station records: " + "  ".join(f"{k} {count.get(k, 0)}" for k in order))
    for k in order[:6]:
        names = " ".join(r["iso3"] for r in out if r["rung"] == k)
        if names:
            print(f"    {k}: {names}")
    for why, n in collections.Counter(r["stopped_by"] for r in out if r["rung"] in "2345").most_common():
        print(f"    stopped, {n:2d}: {why}")
    print("study-ladder-police: ladder-test.csv written.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
