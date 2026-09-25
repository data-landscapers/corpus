#!/usr/bin/env python3
"""test_report_scan_sections.py — the sub-section re-read owed after a pile of new sources (R76).

    python scripts/test_report_scan_sections.py

Runs on temporary files and a synthetic index; touches nothing real.
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


def src(slug, ingested, topics):
    return {"path": f"raw/{slug}.md", "d": {"kind": "source", "folder": "raw", "slug": slug},
            "fm": {"ingested": ingested, "topics": topics}}


with tempfile.TemporaryDirectory() as tmp:
    rs.REPORTS = os.path.join(tmp, "reports")
    os.makedirs(os.path.join(rs.REPORTS, "AAA"))
    with open(os.path.join(rs.REPORTS, "AAA", "AAA-status.md"), "w", encoding="utf-8") as f:
        f.write("### Policy\n<!-- gov.policy -->\n\n### Pay\n<!-- dpi.pay -->\r\n")
    rs.UNIT_REVIEW = os.path.join(tmp, "unit-review.csv")
    with open(rs.UNIT_REVIEW, "w", encoding="utf-8") as f:
        f.write("unit,name,kind,last_reviewed\nAAA,A,country,2026-10-01\n")
    rs.STATUS_INIT = os.path.join(tmp, "missing.csv")

    case("sub-section ids read in order, CRLF tolerated",
         rs.status_sections("AAA") == ["gov.policy", "dpi.pay"])
    case("the last whole read is the unit review", rs.last_whole_read("AAA") == "2026-10-01")

    rows = [src(f"p{i}", "2026-10-02", ["gov.policy"]) for i in range(15)]
    rows += [src("old", "2026-10-01", ["dpi.pay"]),              # the review read it
             src("budget", "2026-10-03", ["finance.budget"]),    # touches no sub-section
             src("undated", None, ["dpi.pay"]),                  # cannot be placed
             src("foreign", "2026-10-03", ["dpi.pay"])]          # another unit's
    by_place = {"AAA": {r["d"]["slug"] for r in rows if r["d"]["slug"] != "foreign"}}
    since, n, owed = rs.sections_owed("AAA", by_place, rows)
    case("15 is not past the threshold", (n, owed) == (15, {}))

    rows.append(src("pay1", "2026-10-03T08:00", ["dpi.pay", "gov.policy"]))
    by_place["AAA"].add("pay1")
    since, n, owed = rs.sections_owed("AAA", by_place, rows)
    case("16 is, and names each touched sub-section with its count",
         n == 16 and owed == {"gov.policy": 16, "dpi.pay": 1})

    with open(rs.sections_read_path("AAA"), "w", encoding="utf-8") as f:
        f.write("2026-10-03\n")
    since, n, owed = rs.sections_owed("AAA", by_place, rows)
    case("a sub-section re-read resets the clock", since == "2026-10-03" and n == 0)

    os.remove(rs.sections_read_path("AAA"))
    with open(rs.UNIT_REVIEW, "w", encoding="utf-8") as f:
        f.write("unit,name,kind,last_reviewed\nAAA,A,country,\n")
    case("the clock never starts before the floor", rs.last_whole_read("AAA") == rs.CLOCK_FLOOR)

print("\nall cases pass" if not failed else f"\n{failed} case(s) FAILED")
sys.exit(1 if failed else 0)
