#!/usr/bin/env python3
r"""hyperscaler-combine.py — the 54 countries' scan files as one nodes file and one organisations file.

    python scripts/hyperscaler-combine.py

Writes `R&D/Hyperscaler-dependence/scan/all-nodes.csv` and `all-organisations.csv`, countries in
`progress.csv` order and each country's rows in its own order. A row with every field blank (what a
spreadsheet save leaves) is dropped. The columns are explained in `all-nodes-metadata.csv` and
`all-organisations-metadata.csv` beside them, which are kept by hand. Re-run after any scan.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

RD = Path(__file__).resolve().parent.parent / "R&D" / "Hyperscaler-dependence"
SCAN = RD / "scan"


def main() -> int:
    with open(RD / "progress.csv", encoding="utf-8-sig", newline="") as f:
        order = [r["iso3"] for r in csv.DictReader(f)]
    for name in ("nodes", "organisations"):
        header, n = None, 0
        with open(SCAN / f"all-{name}.csv", "w", encoding="utf-8", newline="") as out:
            w = csv.writer(out, lineterminator="\n")
            for iso in order:
                p = SCAN / iso / f"{name}.csv"
                if not p.exists():
                    continue
                with open(p, encoding="utf-8-sig", newline="") as f:
                    r = csv.reader(f)
                    h = next(r)
                    if header is None:
                        header = h
                        w.writerow(h)
                    elif h != header:
                        sys.exit(f"{p}: columns differ from the first file")
                    for row in r:
                        if any(x.strip() for x in row):
                            w.writerow(row)
                            n += 1
        print(f"all-{name}.csv: {n} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
