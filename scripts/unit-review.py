#!/usr/bin/env python3
r"""unit-review.py — which place the cycle reviews tonight, and the record of when each was last.

    python scripts/unit-review.py next [--poll]   print tonight's units, one a line; exit 1 if none is owed now
    python scripts/unit-review.py done UNIT --status N --progress N
                                                  stamp UNIT reviewed today, with what it revised
    python scripts/unit-review.py list            the rotation, most overdue first

`UNIT-REVIEW.md` is the procedure. This does the mechanical half: it keeps
`logs/unit-review.csv` — one row per country and region, with the date each was last
reviewed — and answers two questions the runbook must not answer by judgement.

**Which units.** The two reviewed longest ago *(Bill, 2026-09-17: two a night, so the 62 come
round about once a month)*; a unit never reviewed comes before any that
has been, and a tie goes to the unit code in alphabetical order, so the first pass runs the
54 countries A to Z and then the eight regions. That puts a region after the countries it
aggregates, which is the order the reports themselves are built in.

**Whether now.** A review is model authoring over a whole unit, and it runs inside a cycle
only when the cycle is unattended: called from `/poll` (the loop prompt passes `--poll`), or
started between 21:00 and 05:00 local time *(Bill, 2026-09-17)*. A cycle typed by hand in
the working day skips it, because someone is waiting on that render. Exit **1** means *not
owed now* and is the normal daytime answer, not a failure; exit **2** means the rotation
file is wrong and needs repairing before it can answer.

**The rotation covers exactly the places the site publishes.** The regions come from `region.py`'s
`REGION_NAMES` and the countries are the rest of `lookups/countries.csv`, which lists both; a unit added to
either joins the rotation unreviewed on the next call, and a row naming a unit in neither
is an error rather than a silent survivor.

**What each review revised** *(strategic review 5, R75)*. `done` records the status sections
and progress cells the review changed, the same two counts its log line carries, and prints
their mean over the last `ROLLING` reviews. That mean is how much of a report drifted between
whole reads: under two status sections a unit, BUILD stage 4 is holding. A unit's counts are
those of its latest review; a `done` without them leaves the counts blank, never zero.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROTATION = os.path.join(ROOT, "logs", "unit-review.csv")
COUNTRIES = os.path.join(ROOT, "lookups", "countries.csv")
FIELDS = ["unit", "name", "kind", "last_reviewed", "status_revised", "progress_revised"]
COUNTS = ("status_revised", "progress_revised")
NIGHT_FROM, NIGHT_TO = 21, 5          # local hours: owed from 21:00 until 04:59
PER_NIGHT = 2                         # units reviewed per cycle; 62 units -> about a month a round
ROLLING = 14                          # reviews in the rolling mean: a week at two a night
HOLDING = 2                           # status sections a unit under which stage 4 is holding

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class RotationError(Exception):
    pass


def region_names() -> dict[str, str]:
    spec = importlib.util.spec_from_file_location("region", os.path.join(ROOT, "scripts", "region.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return dict(mod.REGION_NAMES)


def places(countries_path: str = COUNTRIES, regions: dict[str, str] | None = None) -> list[dict]:
    """Every unit the rotation must hold, as blank rows."""
    regions = region_names() if regions is None else regions
    blank = {"last_reviewed": "", "status_revised": "", "progress_revised": ""}
    with open(countries_path, encoding="utf-8-sig", newline="") as f:
        rows = [{"unit": r["iso-3"], "name": r["country-name"], "kind": "country", **blank}
                for r in csv.DictReader(f) if r["iso-3"] not in regions]
    rows += [{"unit": k, "name": v, "kind": "region", **blank} for k, v in regions.items()]
    return rows


def load(path: str, expected: list[dict]) -> list[dict]:
    """The rotation, reconciled against the places published: new units join unreviewed."""
    held = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                d = (r.get("last_reviewed") or "").strip()
                if d:
                    try:
                        dt.date.fromisoformat(d)
                    except ValueError:
                        raise RotationError(f"{r.get('unit')}: last_reviewed {d!r} is not YYYY-MM-DD")
                counts = {k: (r.get(k) or "").strip() for k in COUNTS}
                for k, v in counts.items():
                    if v and not v.isdigit():
                        raise RotationError(f"{r.get('unit')}: {k} {v!r} is not a whole number")
                held[r["unit"]] = {"last_reviewed": d, **counts}
    known = {e["unit"] for e in expected}
    stray = sorted(set(held) - known)
    if stray:
        raise RotationError(f"rotation names units the site does not publish: {', '.join(stray)}")
    blank = {"last_reviewed": "", "status_revised": "", "progress_revised": ""}
    return [dict(e, **held.get(e["unit"], blank)) for e in expected]


def save(path: str, rows: list[dict]) -> None:
    rows = sorted(rows, key=lambda r: (r["kind"] != "country", r["unit"]))
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def overdue_order(rows: list[dict]) -> list[dict]:
    return sorted(rows, key=lambda r: (r["last_reviewed"] != "", r["last_reviewed"], r["unit"]))


def rolling_mean(rows: list[dict], n: int = ROLLING) -> tuple[int, float, float] | None:
    """`(reviews counted, status mean, progress mean)` over the `n` latest reviews with counts."""
    done = [r for r in rows if r["last_reviewed"] and all(r.get(k) for k in COUNTS)]
    done = sorted(done, key=lambda r: (r["last_reviewed"], r["unit"]))[-n:]
    if not done:
        return None
    return (len(done), sum(int(r["status_revised"]) for r in done) / len(done),
            sum(int(r["progress_revised"]) for r in done) / len(done))


def mean_line(rows: list[dict]) -> str:
    m = rolling_mean(rows)
    if m is None:
        return "rolling mean: no review has recorded its counts yet"
    k, st, pr = m
    verdict = "stage 4 holding" if st < HOLDING else f"stage 4 not holding (under {HOLDING} is)"
    return (f"rolling mean over the last {k} reviews: status {st:.1f} sections, "
            f"progress {pr:.1f} cells a unit - {verdict}")


def owed_now(poll: bool, now: dt.datetime) -> bool:
    return poll or now.hour >= NIGHT_FROM or now.hour < NIGHT_TO


def main(argv=None, now: dt.datetime | None = None, path: str = ROTATION,
         expected: list[dict] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("next")
    n.add_argument("--poll", action="store_true", help="the cycle was started by /poll")
    d = sub.add_parser("done")
    d.add_argument("unit")
    d.add_argument("--status", type=int, help="status sections the review revised")
    d.add_argument("--progress", type=int, help="progress cells the review revised")
    sub.add_parser("list")
    a = ap.parse_args(argv)
    now = now or dt.datetime.now()

    try:
        rows = load(path, places() if expected is None else expected)
    except RotationError as e:
        print(f"unit-review: {e}")
        return 2

    if a.cmd == "next":
        if not owed_now(a.poll, now):
            print(f"not owed: {now:%H:%M} is outside {NIGHT_FROM:02d}:00-{NIGHT_TO:02d}:00 and the cycle is not from /poll")
            return 1
        for r in overdue_order(rows)[:PER_NIGHT]:
            print(f"{r['unit']}\t{r['kind']}\t{r['name']}\tlast reviewed {r['last_reviewed'] or 'never'}")
        return 0

    if a.cmd == "done":
        unit = a.unit.upper()
        hit = [r for r in rows if r["unit"] == unit]
        if not hit:
            print(f"unit-review: {unit} is not in the rotation")
            return 2
        hit[0]["last_reviewed"] = now.date().isoformat()
        hit[0]["status_revised"] = "" if a.status is None else str(a.status)
        hit[0]["progress_revised"] = "" if a.progress is None else str(a.progress)
        save(path, rows)
        print(f"{unit} reviewed {hit[0]['last_reviewed']}")
        print(mean_line(rows))
        return 0

    save(path, rows)
    for r in overdue_order(rows):
        revised = (f"status {r['status_revised'] or '-':>2}  progress {r['progress_revised'] or '-':>2}"
                   if r["last_reviewed"] else "")
        print(f"{r['unit']}  {r['kind']:<7}  {r['last_reviewed'] or 'never':<10}  {r['name']:<26}  {revised}".rstrip())
    print(mean_line(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
