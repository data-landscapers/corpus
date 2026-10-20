#!/usr/bin/env python3
"""test_unit_review.py — the review rotation picks the right unit, at the right time.

    python scripts/test_unit_review.py

Runs on a temporary rotation file and touches nothing real.
"""
from __future__ import annotations
import contextlib, datetime as dt, importlib.util, io, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("unit_review", os.path.join(HERE, "unit-review.py"))
ur = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ur)

EXPECTED = [
    {"unit": "AGO", "name": "Angola", "kind": "country", "last_reviewed": ""},
    {"unit": "BEN", "name": "Benin", "kind": "country", "last_reviewed": ""},
    {"unit": "XWA", "name": "West Africa", "kind": "region", "last_reviewed": ""},
]
NIGHT = dt.datetime(2026, 9, 17, 23, 30)
EARLY = dt.datetime(2026, 9, 18, 4, 59)
DAY = dt.datetime(2026, 9, 17, 14, 0)
failed = 0


def run(path, argv, now):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = ur.main(argv, now=now, path=path, expected=EXPECTED)
    return code, out.getvalue()


def case(name, ok):
    global failed
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    failed += not ok


with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, "unit-review.csv")

    code, out = run(p, ["next"], DAY)
    case("daytime without --poll is not owed (exit 1)", code == 1)
    code, out = run(p, ["next", "--poll"], DAY)
    case("--poll is owed at any hour", code == 0 and out.startswith("AGO"))
    case("two units a night", [l.split("\t")[0] for l in out.splitlines()] == ["AGO", "BEN"])
    code, out = run(p, ["next"], NIGHT)
    case("23:30 is owed", code == 0)
    code, out = run(p, ["next"], EARLY)
    case("04:59 is owed", code == 0)
    case("05:00 is not owed", run(p, ["next"], dt.datetime(2026, 9, 18, 5, 0))[0] == 1)
    case("21:00 is owed", run(p, ["next"], dt.datetime(2026, 9, 17, 21, 0))[0] == 0)

    run(p, ["done", "AGO"], NIGHT)
    code, out = run(p, ["next"], NIGHT)
    case("a reviewed unit goes to the back; never-reviewed first", out.startswith("BEN"))
    run(p, ["done", "BEN"], NIGHT)
    code, out = run(p, ["next"], NIGHT)
    case("a region follows the countries", out.startswith("XWA"))
    run(p, ["done", "XWA"], dt.datetime(2026, 9, 19, 23, 0))
    code, out = run(p, ["next"], NIGHT)
    case("then the oldest date, ties alphabetical", out.startswith("AGO"))

    code, out = run(p, ["list"], NIGHT)
    case("no counts recorded yet says so", "no review has recorded its counts yet" in out)
    run(p, ["done", "AGO", "--status", "3", "--progress", "10"], dt.datetime(2026, 9, 20, 23, 0))
    code, out = run(p, ["done", "BEN", "--status", "0", "--progress", "4"], dt.datetime(2026, 9, 21, 23, 0))
    case("done prints the rolling mean over reviews with counts",
         "last 2 reviews: status 1.5 sections, progress 7.0 cells" in out and "holding" in out
         and "not holding" not in out)
    code, out = run(p, ["done", "XWA"], dt.datetime(2026, 9, 22, 23, 0))
    case("a done without counts records blanks, not zeros, and is left out of the mean",
         "last 2 reviews" in out and "XWA,West Africa,region,2026-09-22,," in open(p).read())
    m = ur.rolling_mean(ur.load(p, EXPECTED), n=1)
    case("the mean rolls: only the latest n reviews count", m == (1, 0.0, 4.0))
    run(p, ["done", "AGO", "--status", "5", "--progress", "1"], dt.datetime(2026, 9, 23, 23, 0))
    code, out = run(p, ["list"], NIGHT)
    case("a status mean of two or more is not holding", "status 2.5 sections" in out and "not holding" in out)

    case("done on an unknown unit is exit 2", run(p, ["done", "ZZZ"], NIGHT)[0] == 2)
    with open(p, "a", encoding="utf-8") as f:
        f.write("ZZZ,Nowhere,country,\n")
    case("a stray unit in the file is exit 2", run(p, ["next", "--poll"], NIGHT)[0] == 2)

    with open(p, "w", encoding="utf-8") as f:
        f.write("unit,name,kind,last_reviewed\nAGO,Angola,country,17/09/2026\n")
    case("a malformed date is exit 2", run(p, ["next", "--poll"], NIGHT)[0] == 2)

    with open(p, "w", encoding="utf-8") as f:
        f.write("unit,name,kind,last_reviewed,status_revised,progress_revised\n"
                "AGO,Angola,country,2026-09-17,five,\n")
    case("a count that is not a whole number is exit 2", run(p, ["next", "--poll"], NIGHT)[0] == 2)

print("\nall cases pass" if not failed else f"\n{failed} case(s) FAILED")
sys.exit(1 if failed else 0)
