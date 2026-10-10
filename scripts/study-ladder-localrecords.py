#!/usr/bin/env python3
"""study-ladder-localrecords.py — the localrecords study's ladder applied to the review's profiles, strictly.

    python scripts/study-ladder-localrecords.py            # the count per rung, and the test file

Task R3 of `maturity/localrecords/maturity-study-localrecords.md`, and
`study-ladder-localgov.py`'s counterpart: **a test of the ladder, not a staging.** It reads
only each profile's closed values, so a rung that needs something no value carries shows up
as a rung nobody reaches, with the reason beside every country it stopped.

**Fixed at R3**: a revenue system in use in a counted local government, with what it records
not stated, is read as `receipts` and reaches rung 3.

Two things no value carries, and the count says so instead of guessing: whether the local
governments a rung 3 system is live in lie outside the capital, and whether a count is of
local governments or of their offices. An `equipped:` share counts local governments given
the system or trained on it, not recording in it, and places by the lower rung.

Writes `maturity/localrecords/ladder-test.csv`: one row per country, with the rung, the
values it was read from and what kept it from the rung above.
"""
from __future__ import annotations

import collections
import datetime as dt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402

FIELDS = ["iso3", "sub_indicator", "rung", "recorded", "held", "authorities", "authorities_as_of",
          "stopped_by"]


def share(value: str) -> float | None:
    m = re.fullmatch(r"share:([\d.]+)%", value)
    return float(m.group(1)) if m else None


def rung(recorded: str, held: str, authorities: str, as_of: str, as_at: dt.date) -> tuple[str, str]:
    """`(rung, what stopped it from the next)` for one country's coverage values."""
    if not (recorded or held or authorities):
        return study_lib.UNPLACED, "no coverage aspect stated"
    if held in ("paper", "") and recorded in ("", "none") and authorities in ("", "none"):
        if held == "paper" or recorded == "none":
            return "1", "a dated statement of records on paper"
        return study_lib.UNPLACED, "no coverage aspect stated"

    # R3: a system in use with what it records not stated is read as `receipts`.
    in_use = authorities not in ("pilot", "none", "") and not authorities.startswith("equipped:")
    digital = held in ("shared", "local") or recorded in ("register", "receipts")         or in_use
    pct = share(authorities)
    recent = (study_lib.parse_as_of(as_of or "1900") or dt.date(1900, 1, 1)) \
        >= study_lib.months_back(as_at, 24)
    if digital and recorded == "register" and pct is not None and pct > 50:
        if pct >= 90 and recent and held == "shared":
            return "5", ""
        return "4", ("the record is not in a shared system" if pct >= 90 and recent else
                     "the share is older than two years" if pct >= 90 else "under 90 per cent")

    # Rung 3: past the pilot and live in some local governments. `pilot` and `none` are not live.
    live = authorities not in ("pilot", "none", "")
    if live and digital:
        return "3", ("a share given the system or trained, not recording" if authorities.startswith("equipped:") else
                     "receipts with no register of payers" if recorded == "receipts" else
                     "what is recorded is not stated" if recorded != "register" else
                     "no share of local governments over half")
    return "2", ("a pilot, or no local government said to record" if authorities in ("pilot", "none") else
                 "no count or share of local governments" if not authorities else
                 "no system stated")


def main(argv=None) -> int:
    as_at = dt.date.fromisoformat(argv[0]) if argv else dt.date.today()
    study = study_lib.load("localrecords")
    base = os.path.join(study_lib.study_dir("localrecords"), "evidence")
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
                got, why = rung(val("recorded"), val("held"), val("authorities"),
                                cell.get("authorities", {}).get("as_of", ""), as_at)
            out.append({"iso3": iso, "sub_indicator": s["key"], "rung": got, "recorded": val("recorded"),
                        "held": val("held"), "authorities": val("authorities"),
                        "authorities_as_of": cell.get("authorities", {}).get("as_of", ""),
                        "stopped_by": why})

    study_lib.write_csv(os.path.join(study_lib.study_dir("localrecords"), "ladder-test.csv"), FIELDS, out)
    order = ["5", "4", "3", "2", "1", study_lib.UNPLACED, study_lib.NO_EVIDENCE]
    count = collections.Counter(r["rung"] for r in out)
    print("Revenue records: " + "  ".join(f"{k} {count.get(k, 0)}" for k in order))
    for k in order[:6]:
        names = " ".join(r["iso3"] for r in out if r["rung"] == k)
        if names:
            print(f"    {k}: {names}")
    for why, n in collections.Counter(r["stopped_by"] for r in out if r["rung"] in "234").most_common():
        print(f"    stopped, {n:2d}: {why}")
    print("study-ladder-localrecords: ladder-test.csv written.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
