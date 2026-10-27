"""study-ladder-dataprotectionlaw.py — the dataprotectionlaw study's ladder applied to the review's evidence, strictly.

    python scripts/study-ladder-dataprotectionlaw.py            # the count per rung, and the test file
    python scripts/study-ladder-dataprotectionlaw.py --as-at 2026-09-30

Task D3 of `maturity/dataprotectionlaw/maturity-study-dataprotectionlaw.md`: **a test of the
ladder, not a staging.** `study-ladder-ictstrategy.py` is its model.

**The country is placed, not the instrument.** A law is not replaced by a strategy's kind of
succession: the act in force stands until another is in force, and a bill beside it is the
flag *under revision*. So the strongest standing any `general` row states is the country's,
and what is said of its application, regulations and authority is read across every row,
whichever name the source gave the law or the body.

**Read strictly**:

- `in-force` beats `transition` beats `enacted`; a dated decision under the law is itself
  evidence that it is in force (study file §4);
- application counts when dated inside three years of the as-at, and for rung 5 a `reported`
  year ending inside two;
- stage 1 needs a `standing` of `none` and no row stating any other standing.

Writes `maturity/dataprotectionlaw/ladder-test.csv`.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402

STUDY = "dataprotectionlaw"
FIELDS = ["iso3", "sub_indicator", "rung", "instrument", "standing", "regulations", "application",
          "application_as_of", "authority", "flags", "stopped_by"]
LAW = ("in-force", "transition", "enacted")
BILL = ("passed", "tabled", "drafting", "announced")


def _date(as_of: str) -> dt.date:
    return study_lib.parse_as_of(as_of or "1900") or dt.date(1900, 1, 1)


def country(ev: list[dict], systems: list[dict], as_at: dt.date) -> dict:
    by = collections.defaultdict(list)
    for r in ev:
        by[r["aspect"]].append(r)
    out = {"instrument": "", "standing": "", "regulations": "", "application": "",
           "application_as_of": "", "authority": "", "flags": []}
    stands = by["standing"]
    law = [r for r in stands if r["value"] in LAW]
    bill = [r for r in stands if r["value"] in BILL]
    recent = [r for r in by["application"] if r["value"] in ("reported", "applied")
              and _date(r["as_of"]) >= study_lib.months_back(as_at, 36)]
    if law:
        best = min(law, key=lambda r: (LAW.index(r["value"]), -_date(r["as_of"]).toordinal()))
        out["standing"], out["instrument"] = best["value"], best["system"]
        if recent and out["standing"] != "in-force":
            out["standing"] = "in-force"
        newest_law = max(_date(r["as_of"]) for r in law)
        if any(_date(r["as_of"]) > newest_law and r["system"] != out["instrument"] for r in bill):
            out["flags"].append("under revision")
    elif bill:
        best = max(bill, key=lambda r: (_date(r["as_of"]), -BILL.index(r["value"])))
        out["standing"], out["instrument"] = best["value"], best["system"]
    elif stands:
        out["standing"] = "none"
    regs = {r["value"] for r in by["regulations"]}
    out["regulations"] = "issued" if "issued" in regs else ("none" if regs else "")
    if out["regulations"] == "none" and law:
        out["flags"].append("regulations pending")
    if recent:
        best = min(recent, key=lambda r: (("reported", "applied").index(r["value"]),
                                          -_date(r["as_of"]).toordinal()))
        out["application"], out["application_as_of"] = best["value"], best["as_of"]
    elif by["application"]:
        n = max(by["application"], key=lambda r: _date(r["as_of"]))
        out["application"], out["application_as_of"] = n["value"], n["as_of"]
    auth = [r for r in by["authority"] if r["value"] != "none"] or by["authority"]
    if auth:
        out["authority"] = max(auth, key=lambda r: _date(r["as_of"]))["value"]
    if any(r["value"] == "advancing" and _date(r["as_of"]) >= study_lib.months_back(as_at, 12)
           for r in by["last12"]):
        out["flags"].append("advancing")
    out["sectoral"] = any(s["class"] in ("sectoral", "constitutional") for s in systems)
    out["recent"] = bool(recent)
    out["reported"] = any(r["value"] == "reported" and _date(r["as_of"]) >= study_lib.months_back(as_at, 24)
                          for r in by["application"])
    return out


def rung(v: dict) -> tuple[str, str]:
    """`(rung, what stopped it from the next)` for one country."""
    s = v["standing"]
    if s in BILL:
        return "2", f"{s}, not enacted"
    if s in LAW:
        if s != "in-force":
            return "3", f"{s}: not yet in force in full"
        if not v["recent"]:
            return "3", ("activity under the law, and no decision" if v["application"] == "activity"
                         else "no dated decision under the law inside three years")
        top = v["reported"] and v["regulations"] == "issued"
        if v["authority"] != "constituted":
            v["flags"].append("no authority")
            return "3", f"capped from {'5' if top else '4'}"
        if top:
            return "5", ""
        return "4", ("no published year of figures inside two years" if not v["reported"]
                     else "no regulation under the law on record")
    if s == "none":
        return "1", "a dated statement that there is none"
    if v["sectoral"]:
        v["flags"].append("sectoral only")
        return study_lib.UNPLACED, "only sectoral or constitutional provisions are held"
    if v["application"] or v["authority"] or v["regulations"]:
        return study_lib.UNPLACED, "no standing stated for the law"
    return study_lib.NO_EVIDENCE, "nothing found on a data protection law"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-at", default="2026-09-30")
    args = ap.parse_args(argv)
    as_at = dt.date.fromisoformat(args.as_at)
    base = study_lib.study_dir(STUDY)
    rows, count = [], collections.Counter()
    for iso in sorted(os.listdir(os.path.join(base, "evidence"))):
        folder = os.path.join(base, "evidence", iso)
        if not os.path.isdir(folder):
            continue
        ev = study_lib.read_csv(os.path.join(folder, "evidence.csv")) \
            if os.path.exists(os.path.join(folder, "evidence.csv")) else []
        systems = study_lib.read_csv(os.path.join(folder, "systems.csv")) \
            if os.path.exists(os.path.join(folder, "systems.csv")) else []
        v = country([r for r in ev if r["class"] == "general"], systems, as_at)
        got, why = rung(v)
        count[got] += 1
        rows.append({"iso3": iso, "sub_indicator": "general", "rung": got,
                     **{k: v[k] for k in FIELDS[3:9]}, "flags": ";".join(v["flags"]),
                     "stopped_by": why})
    study_lib.write_csv(os.path.join(base, "ladder-test.csv"), FIELDS, rows)
    print("study-ladder-dataprotectionlaw:", ", ".join(
        f"{k}: {count[k]}" for k in ("5", "4", "3", "2", "1", study_lib.UNPLACED, study_lib.NO_EVIDENCE)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
