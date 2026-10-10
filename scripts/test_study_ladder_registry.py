#!/usr/bin/env python3
"""test_study_ladder_registry.py — the registry ladder as `study-ladder-registry.py` counts it.

    python scripts/test_study_ladder_registry.py
"""
import datetime as dt
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("ladder", os.path.join(HERE, "study-ladder-registry.py"))
ladder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ladder)

AS_AT = dt.date(2026, 10, 10)
FAILED = []


def check(name, events, made, offices, as_of, want):
    got = ladder.rung(set(events.split(";")), made, offices, as_of, AS_AT)[0]
    print(f"  {'ok  ' if got == want else 'FAIL'}  {name}" + ("" if got == want else f": {got}, wanted {want}"))
    if got != want:
        FAILED.append(name)


check("nothing stated is unplaced", "", "", "", "", "unplaced")
check("paper alone is 1", "none", "paper", "", "", "1")
check("paper beside a pilot is 2", "B", "paper", "pilot", "2026", "2")
check("a pilot is 2", "B", "connected", "pilot", "2026", "2")
check("deaths only is 2", "D", "connected", "count:40", "2026", "2")
check("in service with no figure is 3", "B", "connected", "not-published", "", "3")
check("no event named reads as births", "", "local", "count:12", "2025", "3")
check("a count with no total is 3", "B;D", "connected", "count:400", "2026", "3")
check("a minority share is 3", "B", "connected", "share:38%", "2026", "3")
check("offices equipped are 3 however many", "B;D", "connected", "equipped:98%", "2026", "3")
check("a record that stays in the office is 3", "B;D", "local", "share:80%", "2026", "3")
check("keyed elsewhere is 3", "B;D", "keyed-elsewhere", "share:100%", "2026", "3")
check("over half, births alone, is 4", "B", "connected", "share:57%", "2025", "4")
check("90 per cent without deaths stays 4", "B", "connected", "share:95%", "2026", "4")
check("90 per cent on an old figure stays 4", "B;D", "connected", "share:100%", "2022", "4")
check("90 per cent with deaths inside two years is 5", "B;D", "connected", "share:100%", "2025", "5")

print("\nall ok" if not FAILED else f"\n{len(FAILED)} failed")
sys.exit(1 if FAILED else 0)
