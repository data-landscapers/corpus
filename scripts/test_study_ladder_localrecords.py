#!/usr/bin/env python3
"""test_study_ladder_localrecords.py — the localrecords ladder as `study-ladder-localrecords.py` counts it.

    python scripts/test_study_ladder_localrecords.py
"""
import datetime as dt
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("ladder", os.path.join(HERE, "study-ladder-localrecords.py"))
ladder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ladder)

AS_AT = dt.date(2026, 10, 10)
FAILED = []


def check(name, recorded, held, authorities, as_of, want):
    got = ladder.rung(recorded, held, authorities, as_of, AS_AT)[0]
    print(f"  {'ok  ' if got == want else 'FAIL'}  {name}" + ("" if got == want else f": {got}, wanted {want}"))
    if got != want:
        FAILED.append(name)


check("nothing stated is unplaced", "", "", "", "", "unplaced")
check("paper alone is 1", "none", "paper", "", "", "1")
check("paper beside a pilot is 2", "register", "paper", "pilot", "2026", "2")
check("a pilot is 2", "register", "shared", "pilot", "2026", "2")
check("a system with no local government using it is 2", "register", "local", "none", "2026", "2")
check("a system with no count is 2", "register", "shared", "", "", "2")
check("in service with no figure is 3", "register", "shared", "not-published", "", "3")
check("a count with no total is 3", "register", "local", "count:40", "2026", "3")
check("a minority share is 3", "register", "shared", "share:38%", "2026", "3")
check("a share given the system is 3 however many", "register", "shared", "equipped:98%", "2026", "3")
check("in use with the record not stated reads as receipts, 3", "", "", "count:30", "2026", "3")
check("paper in some beside a count in use is 3", "", "paper", "count:5", "2026", "3")
check("given the system with nothing else stated is 2", "", "", "equipped:40%", "2026", "2")
check("receipts alone stop at 3", "receipts", "shared", "share:100%", "2026", "3")
check("over half with a register is 4", "register", "local", "share:57%", "2025", "4")
check("90 per cent in a local system stays 4", "register", "local", "share:95%", "2026", "4")
check("90 per cent on an old figure stays 4", "register", "shared", "share:100%", "2022", "4")
check("90 per cent, shared, inside two years is 5", "register", "shared", "share:100%", "2025", "5")

print("\nall ok" if not FAILED else f"\n{len(FAILED)} failed")
sys.exit(1 if FAILED else 0)
