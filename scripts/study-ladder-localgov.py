#!/usr/bin/env python3
r"""study-ladder-localgov.py — the localgov study's ladder applied to the review's profiles, strictly.

    python scripts/study-ladder-localgov.py            # the count per rung, and the test file

Task L3 of `maturity/localgov/maturity-study-localgov.md`, and `study-ladder-police.py`'s
counterpart: **a test of the ladder, not a staging.** It reads only each profile's closed
values, so a rung that needs something no value carries shows up as a rung nobody reaches,
with the reason beside every country it stopped.

One thing here reads past the profile, because the study file's L3 fix asks it: **a share
places above rung 3 only where its own source states the institutional connection.** The
share's `sources` rows are looked up in `evidence.csv`, and the rung holds at 3 unless one of
those documents also carries `connected = institutional`.

Three things no value carries, and the count says so instead of guessing: rung 5's rural
share, whether the local governments a rung 3 connection is live in lie outside the capital,
and whether a count is of local governments or of their offices. An `equipped:` share counts
local governments covered or given equipment, not connected, and places by the lower rung.

Writes `maturity/localgov/ladder-test.csv`: one row per country, with the rung, the values it
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

FIELDS = ["iso3", "sub_indicator", "rung", "use", "connected", "authorities", "authorities_as_of",
          "stopped_by"]


def share(value: str) -> float | None:
    m = re.fullmatch(r"share:([\d.]+)%", value)
    return float(m.group(1)) if m else None


def rung(use: str, connected: str, authorities: str, as_of: str, same_source: bool,
         as_at: dt.date) -> tuple[str, str]:
    """`(rung, what stopped it from the next)` for one country's coverage values."""
    if not (use or connected or authorities):
        return study_lib.UNPLACED, "no coverage aspect stated"
    if connected in ("personal", "none") and use in ("", "none") and authorities in ("", "none"):
        return "1", "a dated statement of no connection of their own"

    pct = share(authorities)
    recent = (study_lib.parse_as_of(as_of or "1900") or dt.date(1900, 1, 1)) \
        >= study_lib.months_back(as_at, 24)
    if connected == "institutional" and pct is not None and pct > 50:
        if not same_source:
            return "3", "the share's source does not state the institutional connection"
        if pct >= 90 and recent and use == "systems":
            return "5", "the rural share is not carried by a value"
        return "4", ("no work in a national system stated" if pct >= 90 and recent else
                     "the share is older than two years" if pct >= 90 else "under 90 per cent")

    # Rung 3: past the pilot and live in some local governments. `pilot` and `none` are not live.
    live = authorities not in ("pilot", "none", "")
    if live and (connected == "institutional" or use in ("systems", "internet")):
        return "3", ("a share covered or equipped, not connected" if authorities.startswith("equipped:") else
                     "how the office is connected is not stated" if connected != "institutional" else
                     "no share of local governments over half")
    return "2", ("a pilot, or no local government said to be connected" if authorities in ("pilot", "none") else
                 "no count or share of local governments" if not authorities else
                 "neither a connection nor a use stated")


def main(argv=None) -> int:
    as_at = dt.date.fromisoformat(argv[0]) if argv else dt.date.today()
    study = study_lib.load("localgov")
    base = os.path.join(study_lib.study_dir("localgov"), "evidence")
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
                ids = set(cell.get("authorities", {}).get("sources", "").split(";"))
                slugs = {r["source_slug"] for r in held if r["row_id"] in ids}
                same = any(r["source_slug"] in slugs and r["aspect"] == "connected"
                           and r["value"] == "institutional" for r in held)
                got, why = rung(val("use"), val("connected"), val("authorities"),
                                cell.get("authorities", {}).get("as_of", ""), same, as_at)
            out.append({"iso3": iso, "sub_indicator": s["key"], "rung": got, "use": val("use"),
                        "connected": val("connected"), "authorities": val("authorities"),
                        "authorities_as_of": cell.get("authorities", {}).get("as_of", ""),
                        "stopped_by": why})

    study_lib.write_csv(os.path.join(study_lib.study_dir("localgov"), "ladder-test.csv"), FIELDS, out)
    order = ["5", "4", "3", "2", "1", study_lib.UNPLACED, study_lib.NO_EVIDENCE]
    count = collections.Counter(r["rung"] for r in out)
    print("Office connection: " + "  ".join(f"{k} {count.get(k, 0)}" for k in order))
    for k in order[:6]:
        names = " ".join(r["iso3"] for r in out if r["rung"] == k)
        if names:
            print(f"    {k}: {names}")
    for why, n in collections.Counter(r["stopped_by"] for r in out if r["rung"] in "2345").most_common():
        print(f"    stopped, {n:2d}: {why}")
    print("study-ladder-localgov: ladder-test.csv written.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
