#!/usr/bin/env python3
"""lint-csv-bom.py — every CSV the site publishes starts with a UTF-8 byte-order mark.

**A global rule** *(Bill, 2026-11-20)*: Excel opens a CSV without a BOM in the local code
page and garbles every accented name. Writers call `chrome_lib.with_bom`; a browser download
is cut with `'\\ufeff' +`. This lint is what notices a writer that forgot. RENDER Step 7.

A dated edition published before the rule is never revised (`design.md` §9), so one found
without a BOM is reported and not failed; every other file fails.

    python scripts/lint-csv-bom.py      # 0 clean · 1 a site CSV without a BOM
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOM = b"\xef\xbb\xbf"
DATED = re.compile(r"-\d{4}-\d{2}-\d{2}(?:-[a-z0-9]+)?\.csv$")


def main() -> int:
    bad, old = [], []
    for p in sorted((ROOT / "site").rglob("*.csv")):
        with open(p, "rb") as fh:
            if fh.read(3) == BOM:
                continue
        (old if DATED.search(p.name) else bad).append(str(p.relative_to(ROOT)))
    for p in bad[:20]:
        print(f"no BOM: {p}")
    if old:
        print(f"{len(old)} dated edition(s) from before the rule, left as published")
    print(f"lint-csv-bom: {len(bad)} site CSV(s) without a BOM")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
