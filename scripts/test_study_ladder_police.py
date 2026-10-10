#!/usr/bin/env python3
"""test_study_ladder_police.py — the police ladder as `study-ladder-police.py` counts it.

    python scripts/test_study_ladder_police.py
"""
import datetime as dt
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("ladder", os.path.join(HERE, "study-ladder-police.py"))
ladder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ladder)

AS_AT = dt.date(2026, 10, 10)
FAILED = []


def check(name, records, made, stations, as_of, want):
    got = ladder.rung(set(records.split(";")), made, stations, as_of, AS_AT)[0]
    print(f"  {'ok  ' if got == want else 'FAIL'}  {name}" + ("" if got == want else f": {got}, wanted {want}"))
    if got != want:
        FAILED.append(name)


check("nothing stated is unplaced", "", "", "", "", "unplaced")
check("paper alone is 1", "none", "paper", "", "", "1")
check("paper beside a pilot is 2", "O", "paper", "pilot", "2026", "2")
check("a pilot is 2", "O;C", "connected", "pilot", "2026", "2")
check("a system with no station using it is 2", "C", "connected", "none", "2026", "2")
check("in service with no figure is 3", "C", "connected", "not-published", "", "3")
check("no record named reads as O", "", "local", "count:12", "2025", "3")
check("a count with no total is 3", "O;C", "connected", "count:400", "2026", "3")
check("a minority share is 3", "O", "connected", "share:38%", "2026", "3")
check("stations equipped are 3 however many", "O;C", "connected", "equipped:98%", "2026", "3")
check("a record that stays in the station is 3", "O;C", "local", "share:80%", "2026", "3")
check("keyed elsewhere is 3", "O;C", "keyed-elsewhere", "share:100%", "2026", "3")
check("over half, either record, is 4", "C", "connected", "share:57%", "2025", "4")
check("90 per cent on one record stays 4", "O", "connected", "share:95%", "2026", "4")
check("90 per cent on an old figure stays 4", "O;C", "connected", "share:100%", "2022", "4")
check("90 per cent with both inside two years is 5", "O;C", "connected", "share:100%", "2025", "5")

print("\nall ok" if not FAILED else f"\n{len(FAILED)} failed")
sys.exit(1 if FAILED else 0)
