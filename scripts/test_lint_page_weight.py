#!/usr/bin/env python3
"""test_lint_page_weight.py — the element ceiling is the arithmetic datatable.js commits to.

    python scripts/test_lint_page_weight.py

`lint-page-weight.py` does not run the table; it counts what the table would draw. So the
count is only as good as its agreement with `site/assets/js/datatable.js`, and these cases
pin the parts of that agreement a change to either file would break without saying so: the
frame, the filter that is not drawn for a one-value column, the blank cell that costs one
element fewer, the 100-row draw, and the `<noscript>` a scripting browser reads as text.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "lint_page_weight", Path(__file__).resolve().parent / "lint-page-weight.py")
pw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pw)

failures: list[str] = []


def check(name: str, got, want) -> None:
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got:  {got!r}\n         want: {want!r}")
        failures.append(name)


HEADERS = ["country", "year", "note", "url"]
TABLE = {"data-src": "x.csv", "data-cols": "country, year, note", "data-filters": "country,year"}

# Frame for three columns: 15 + 3 * (3 + 1) = 27. Search box: 1.
FRAME = 27 + 1

# Two rows, one blank cell. `country` has two values and gets a filter (select, the "all"
# option, two options); `year` has one and gets none.
rows = [["KEN", "2025", "a", "u"], ["NGA", "2025", "", "u"]]
check("two rows: frame, one filter, rows and filled cells",
      pw.table_elements(TABLE, True, HEADERS, rows),
      FRAME + 4 + 2 * (2 + 3) + (3 + 2))

check("no rows: the frame and the 'nothing matches' row",
      pw.table_elements(TABLE, True, HEADERS, []), FRAME + 2)

check("no data-cols: every column is drawn",
      pw.table_elements({"data-src": "x.csv"}, True, HEADERS, rows[:1]),
      15 + 3 * 5 + 1 + (2 + 4) + 4)

check("no toolbar on the page: the script builds the bar, the count and one download",
      pw.table_elements({"data-src": "x.csv"}, False, HEADERS, rows[:1]),
      15 + 3 * 5 + 1 + (2 + 4) + 4 + 3)

# 250 rows, of which 120 are full and 130 hold a blank: the draw is 100, and the ceiling
# takes the fullest 100 whatever order the file is in.
many = [["KEN", "2025", "", "u"]] * 130 + [["KEN", "2025", "a", "u"]] * 120
check("the draw is 100 rows, and the fullest 100",
      pw.table_elements({"data-src": "x.csv", "data-cols": "country,year,note"}, True, HEADERS, many),
      FRAME + 100 * (2 + 3) + 100 * 3)

check("a header is matched the way the script matches it",
      pw.table_elements({"data-src": "x.csv", "data-cols": "Report Year"}, True, ["report_year"], [["2025"]]),
      15 + 3 * 2 + 1 + (2 + 1) + 1)

page = pw._Page()
page.feed('<html><head><meta charset="utf-8"></head><body><div class="dl-datatable" data-src="x.csv">'
          '<div class="dt-controls"><span class="dt-count"></span></div>'
          '<noscript><p>Get the <a href="x.csv">CSV</a>.</p></noscript></div></body></html>')
check("a page's own elements: noscript counts once, its contents not at all", page.elements, 8)
check("the table's attributes are kept", page.table["data-src"], "x.csv")
check("a toolbar the page supplies is seen", page.has_controls, True)

headers, recs = pw.parse('﻿a,b\r\n" x ","multi\nline"\r\n,\r\n'.encode("utf-8"))
check("the CSV reads as the script reads it: BOM off, cells trimmed, empty record dropped",
      (headers, recs), (["a", "b"], [["x", "multi\nline"]]))

m = {"page": "p.html", "rows": 10, "bytes_gz": 10, "elements": pw.MAX_ELEMENTS}
check("at the ceiling passes", pw.findings(m), [])
check("one over fails", len(pw.findings({**m, "elements": pw.MAX_ELEMENTS + 1})), 1)
check("a data file over 2 MB compressed fails", len(pw.findings({**m, "bytes_gz": pw.MAX_GZ + 1})), 1)
check("100,000 rows fails once, as the query-service line",
      [("query service" in f) for f in pw.findings({**m, "rows": pw.SERVICE_ROWS, "bytes_gz": pw.MAX_GZ + 1})],
      [True])

print(f"\n{len(failures)} failure(s)" if failures else "\nall checks passed")
sys.exit(1 if failures else 0)
