#!/usr/bin/env python3
"""test_datatable_bake.py — the rows written into a page are the rows the script would draw.

    python scripts/test_datatable_bake.py

`datatable_bake.py` is a port of `site/assets/js/datatable.js`, and the whole-site check
that the two agree (`prototypes/datatable-test.mjs`) needs node. These are the rules of the
script that a port gets wrong quietly, pinned where every machine can run them: blanks last
in both directions, a number read off the front of a value, ties left in file order, a label
shown for a code, and the cell markup character for character.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import datatable_bake as db  # noqa: E402
import editions  # noqa: E402

failures: list[str] = []


def check(name: str, got, want) -> None:
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got:  {got!r}\n         want: {want!r}")
        failures.append(name)


def column(html: str, i: int) -> list[str]:
    """Column `i` of the body, as text."""
    rows = re.findall(r"<tr>(.*?)</tr>", html.split("<tbody>")[1], re.S)
    return [re.sub(r"<[^>]+>", "", re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)[i]) for r in rows]


HEADERS = ["country", "year", "amount", "url", "note"]
ROWS = [
    ["KEN", "2024", "1500.5", "https://example.org/a/", "first"],
    ["DZA", "", "20", "", "blank year"],
    ["CIV", "2026 (revised)", "", "", "[[x|linked]] text"],
    ["KEN", "2026", "3", "", "second"],
    ["COD", "2025", "1234567", "", "a < b"],
]
A = {"data-src": "x.csv", "data-cols": "country, year, amount, url, note",
     "data-numeric": "year, amount", "data-thousands": "amount", "data-links": "url",
     "data-labels": '{"country":{"KEN":"Kenya","DZA":"Algeria","CIV":"Côte d\'Ivoire","COD":"Congo, Dem. Rep."}}'}

desc = db.table_html({**A, "data-sort": "year:desc"}, HEADERS, ROWS)
check("numeric, descending: the number at the front of a value, ties in file order, blank last",
      column(desc, 4), ["linked text", "second", "a &lt; b", "first", "blank year"])
asc = db.table_html({**A, "data-sort": "year:asc"}, HEADERS, ROWS)
check("ascending: the blank is still last", column(asc, 1), ["2024", "2025", "2026 (revised)", "2026", ""])

names = db.table_html({**A, "data-sort": "country:asc"}, HEADERS, ROWS)
check("text sorts on the label shown, accents set aside",
      column(names, 0), ["Algeria", "Congo, Dem. Rep.", "Côte d'Ivoire", "Kenya", "Kenya"])

check("no data-sort: file order", column(db.table_html(A, HEADERS, ROWS), 0)[0], "Kenya")
check("thousands on a plain number, and nothing in a blank cell",
      column(desc, 2), ["", "3", "1,234,567", "1,500.5", "20"])
check("a link cell, as the script writes it",
      '<td><a href="https://example.org/a/" target="_blank" rel="noopener noreferrer" '
      'title="https://example.org/a/">example.org/a</a></td>' in desc, True)
check("a numeric cell carries its class", '<td class="num"><span class="dt-cell">1,500.5</span></td>' in desc, True)
check("the sorted header says so", '<th class="num sort-desc">year</th>' in desc, True)
check("one <col> a column, and the table as wide as they are",
      sum(int(w) for w in re.findall(r'<col style="width:(\d+)px">', desc)),
      int(re.search(r'style="width:(\d+)px"', desc).group(1)))

many = [["KEN", str(2000 + i % 30), "1", "", "n"] for i in range(250)]
check("the first hundred rows and no more", len(column(db.table_html(A, HEADERS, many), 0)), db.PAGE)

badge = db.table_html({"data-src": "x.csv", "data-badges": '{"note":{"first":"green"}}'}, HEADERS, ROWS[:1])
check("a badge where the page names a tone", '<span class="dt-badge dt-badge--green">first</span>' in badge, True)

check("thousands follows toLocaleString: three places at most", db.thousands("1234.56789"), "1,234.568")
check("parseFloat reads past a comma and stops at a letter", db.num_of("1,250 m"), 1250.0)
check("and finds nothing in a word", db.num_of("n/a"), None)

PAGE_HTML = ('<div class="dl-datatable"\n  data-src="{src}"\n  data-labels="{{&quot;a&quot;:{{&quot;1&quot;:&quot;one&quot;}}}}">\n'
             '  <div class="dt-controls"></div>\n  <noscript>\n    <p>old</p>\n  </noscript>\n</div>')
with tempfile.TemporaryDirectory() as tmp:
    d = Path(tmp)
    (d / "local.csv").write_bytes("﻿a,b\n1,x\n".encode("utf-8"))
    out = db.bake(PAGE_HTML.format(src="local.csv?v=abc"), d)
    check("a CSV in the tree is read past its ?v= stamp, and its labels through the attribute's entities",
          '<span class="dt-cell">one</span>' in out, True)
    check("the old <noscript> is replaced, not added to", (out.count("<noscript>"), "old" in out), (1, False))
    check("a table that fits says what JavaScript adds", "Sorting and filters need JavaScript." in out, True)

    editions.PUBLISHED[(d / "gone-2026-10-03.csv").resolve()] = b"a,b\n" + b"1,x\n" * 150
    out = db.bake(PAGE_HTML.format(src="gone-2026-10-03.csv"), d)
    check("an edition not in the tree is read from what this run published",
          "The first 100 of 150 rows." in out, True)
    try:
        db.bake(PAGE_HTML.format(src="nowhere.csv"), d)
        check("a CSV that is nowhere stops the build", "returned", "SystemExit")
    except SystemExit:
        check("a CSV that is nowhere stops the build", "SystemExit", "SystemExit")
    check("a page with no table is left alone", db.bake("<p>plain</p>", d), "<p>plain</p>")

print(f"\n{len(failures)} failure(s)" if failures else "\nall checks passed")
sys.exit(1 if failures else 0)
