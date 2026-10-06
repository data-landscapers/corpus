#!/usr/bin/env python3
r"""study-ladder-health.py — the health study's two ladders applied to the Phase 1 profiles, strictly.

    python scripts/study-ladder-health.py            # the count per rung, and the test file
    python scripts/study-ladder-health.py --as-written

Task H4 of `maturity/health/maturity-study-health.md`: *count countries per rung on the Phase 1
profiles; rewrite any rung nothing reaches or that drafters read two ways*. This is the count.

**It is a test of the ladder, not a staging.** Phase 2 stages from the evidence rows with
their text in hand; this reads only each profile's closed values, which is the hardest
reading a rung can be given. So a rung that needs something no aspect value carries shows up
here as a rung nobody reaches, with the reason beside every country it stopped: that is the
list H4 rewrites from. Nothing here is published, and `assessment.csv` is not written.

The ladders are in the study file, where they are argued. **They are restated here as code
only because a count needs code**, and each test names the cell of the table it applies.
`--as-written` applies the tables as they stood before H4; the default applies them as H4
left them. The two counts side by side are the record of what the rewrite did.

Writes `maturity/health/ladder-test.csv`: one row per country and sub-indicator, with the
rung, the values it was read from and what kept it from the rung above.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402

FIELDS = ["iso3", "sub_indicator", "rung", "tiers", "digitised", "clinics", "clinics_as_of",
          "stopped_by"]
PRIMARY = {"T3", "T4"}
ALL = {"T1", "T2", "T3", "T4"}


def share(value: str) -> float | None:
    m = re.fullmatch(r"share:([\d.]+)%", value)
    return float(m.group(1)) if m else None


def rung(sub: str, cell: dict[str, dict], as_at: dt.date, as_written: bool) -> tuple[str, str]:
    """`(rung, what stopped it from the next)` for one country's coverage values."""
    tiers = {t for t in cell["tiers"]["value"].split(";") if t}
    where, clinics = cell["digitised"]["value"], cell["clinics"]["value"]
    if not (tiers or where or clinics):
        return study_lib.UNPLACED, "no coverage aspect stated"
    if (tiers <= {"none"}) and where in ("", "paper") and clinics in ("", "none"):
        if where == "paper":
            return "1", "a dated statement of paper only"
        if not where and not clinics and not tiers:
            return study_lib.UNPLACED, "no coverage aspect stated"

    # EMR rungs 4 and 5 ask for a record on a unique patient identifier, retrievable at another
    # facility. As written no value carried that, so `point-of-care` was all a profile could
    # show; H4 added `shared`.
    at_source = "facility" if sub == "hmis" else ("point-of-care" if as_written else "shared")
    pct = share(clinics)
    recent = study_lib.parse_as_of(cell["clinics"]["as_of"] or "1900") >= study_lib.months_back(as_at, 24)
    # Rungs 4 and 5, tiers cell. As written: "T1 to T4". As rewritten: the primary tier in use.
    tiers_top = (tiers >= ALL) if as_written else bool(tiers & PRIMARY)
    top = tiers_top and where == at_source

    if top and pct is not None and pct >= 90 and recent:
        return "5", ""
    if top and pct is not None and pct > 50:
        return "4", ("the share is older than two years" if pct >= 90 else "under 90 per cent")
    stop4 = ("tiers: not all of T1 to T4 stated" if as_written and not tiers >= ALL else
             "tiers: no primary tier stated" if not tiers_top else
             ("not entered at the facility" if sub == "hmis" else
              "not stated as shared between facilities on one identifier") if where != at_source else
             "no share of primary clinics over half")

    # Rung 3. HMIS: every district reports, keyed at district or below. EMR: most hospitals,
    # or primary clinics in some districts.
    if sub == "hmis":
        # As written the tiers cell reads "every district reports", which no value carries, so
        # the strict reading asks for a tier below the hospitals. As rewritten, a system keyed
        # at district or facility is taking the primary tier's reports whether or not a source
        # names the tier.
        reaches = where in ("district", "facility") and (bool(tiers & PRIMARY) or not as_written)
    else:
        reaches = bool(tiers & PRIMARY) or tiers >= {"T1", "T2"} or (pct is not None and pct > 0)
    if reaches:
        return "3", stop4
    stop3 = ("tiers: no tier below the hospitals stated" if sub == "hmis" and where in ("district", "facility")
             else "where data is digitised is not stated" if sub == "hmis" and not where
             else "no tier or share reaching beyond pilot sites")
    return "2", stop3


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="The health ladders, applied strictly to the profiles.")
    ap.add_argument("--as-written", action="store_true", help="the tables as they stood before H4")
    ap.add_argument("--as-at", help="YYYY-MM-DD; default today")
    a = ap.parse_args(argv)
    as_at = dt.date.fromisoformat(a.as_at) if a.as_at else dt.date.today()

    study = study_lib.load("health")
    base = os.path.join(study_lib.study_dir("health"), "evidence")
    barred = study_lib.excluded(study)
    out = []
    for iso in sorted(study_lib.countries()):
        prof = study_lib.read_csv(os.path.join(base, iso, "profile.csv"))
        held = [r for r in study_lib.read_csv(os.path.join(base, iso, "evidence.csv"))
                if r["source_slug"] not in barred]
        for s in study["sub_indicators"]:
            cell = {r["aspect"]: r for r in prof if r["sub_indicator"] == s["key"]}
            if not any(r["sub_indicator"] == s["key"] for r in held):
                got, why = study_lib.NO_EVIDENCE, "nothing held"
            else:
                got, why = rung(s["key"], cell, as_at, a.as_written)
            out.append({"iso3": iso, "sub_indicator": s["key"], "rung": got,
                        "tiers": cell["tiers"]["value"], "digitised": cell["digitised"]["value"],
                        "clinics": cell["clinics"]["value"],
                        "clinics_as_of": cell["clinics"]["as_of"], "stopped_by": why})

    if not a.as_written:
        study_lib.write_csv(os.path.join(study_lib.study_dir("health"), "ladder-test.csv"), FIELDS, out)
    order = ["5", "4", "3", "2", "1", study_lib.UNPLACED, study_lib.NO_EVIDENCE]
    for s in study["sub_indicators"]:
        mine = [r for r in out if r["sub_indicator"] == s["key"]]
        count = collections.Counter(r["rung"] for r in mine)
        print(f"{s['label']}: " + "  ".join(f"{k} {count.get(k, 0)}" for k in order))
        for k in order[:5]:
            names = " ".join(r["iso3"] for r in mine if r["rung"] == k)
            if names:
                print(f"    {k}: {names}")
        stops = collections.Counter(r["stopped_by"] for r in mine if r["rung"] in ("2", "3", "4"))
        for why, n in stops.most_common():
            print(f"    stopped, {n:2d}: {why}")
    print("study-ladder-health: " + ("the ladders as written before H4, nothing written."
                                     if a.as_written else "ladder-test.csv written."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
