#!/usr/bin/env python3
"""test_study_ladder_schools.py — the schools ladder as `study-ladder-schools.py` counts it.

    python scripts/test_study_ladder_schools.py
"""
import datetime as dt
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("ladder", os.path.join(HERE, "study-ladder-schools.py"))
ladder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ladder)

AS_AT = dt.date(2026, 10, 9)
FAILED = []


def check(name, levels, kept, schools, as_of, want):
    got = ladder.rung(set(levels.split(";")), kept, schools, as_of, AS_AT)[0]
    print(f"  {'ok  ' if got == want else 'FAIL'}  {name}" + ("" if got == want else f": {got}, wanted {want}"))
    if got != want:
        FAILED.append(name)


check("nothing stated is unplaced", "", "", "", "", "unplaced")
check("paper alone is 1", "", "paper", "", "", "1")
check("a pilot in primary schools is 2", "P", "routine", "pilot", "2026", "2")
check("secondary only is 2", "S", "routine", "share:80%", "2026", "2")
check("routine entry in service with no figure is 3", "P", "routine", "not-published", "", "3")
check("a register still at its pilot is 2", "P", "enrolment", "pilot", "2026", "2")
check("no level named reads as primary", "", "routine", "not-published", "", "3")
check("a count with no total is live use, 3", "P", "routine", "count:400", "2025", "3")
check("a minority share is 3", "P", "routine", "share:20%", "2025", "3")
check("a learner register is 3 whatever its share", "P", "enrolment", "share:95%", "2026", "3")
check("a register keyed elsewhere is 3", "P;S", "keyed-elsewhere", "not-published", "", "3")
check("over half entering routinely is 4", "P", "routine", "share:60%", "2025", "4")
check("90 per cent on an old figure stays 4", "P", "routine", "share:92%", "2022", "4")
check("90 per cent inside two years is 5", "P", "routine", "share:92%", "2026-01", "5")

print("\nall ok" if not FAILED else f"\n{len(FAILED)} failed")
sys.exit(1 if FAILED else 0)
