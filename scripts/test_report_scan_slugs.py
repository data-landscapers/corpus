#!/usr/bin/env python3
"""test_report_scan_slugs.py — `--slugs` holds still while a pass cites (housekeeping 30).

    python scripts/test_report_scan_slugs.py

Runs on temporary files and a synthetic source map; touches nothing real.
"""
from __future__ import annotations
import importlib.util, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("report_scan", os.path.join(HERE, "report-scan.py"))
rs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rs)
failed = 0


def case(name, ok):
    global failed
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    failed += not ok


def ledger(*sources):
    with open(os.path.join(rs.REPORTS, "AAA", "ledger.csv"), "w", encoding="utf-8") as f:
        f.write("id,sources\n" + "".join(f"r{i},{s}\n" for i, s in enumerate(sources)))


with tempfile.TemporaryDirectory() as tmp:
    rs.REPORTS = os.path.join(tmp, "reports")
    os.makedirs(os.path.join(rs.REPORTS, "AAA"))
    by_place = {"AAA": {"a", "b", "c", "old", "held"}}
    rs.sources_by_place = lambda: by_place
    rs.held_slugs = lambda: {"held"}

    ledger("old")
    case("a cited but unmarked slug is listed", rs.unconsidered("AAA", by_place) == {"a", "b", "c", "old"})
    case("a held source is listed nowhere", "held" not in rs.unconsidered("AAA", by_place))
    start = rs.unconsidered("AAA", by_place)

    ledger("old", "a|b")                       # the pass cites before it marks
    case("citing does not shrink the list", rs.unconsidered("AAA", by_place) == start)

    n = rs.mark("AAA", ["c", "held"])        # a hand list that forgot the cited ones
    case("--mark records what the ledger cites as well", n == 4
         and rs.considered("AAA") == {"a", "b", "c", "old"})
    case("nothing is left once marked", rs.unconsidered("AAA", by_place) == set())

    ledger("old", "a|b", "zzz")                # a citation outside the unit's source set
    case("--mark with no slugs writes nothing foreign", rs.mark("AAA", []) == 0)

print("\nall cases pass" if not failed else f"\n{failed} case(s) FAILED")
sys.exit(1 if failed else 0)
