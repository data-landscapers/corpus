#!/usr/bin/env python3
r"""hyperscaler-combine.py — the 54 countries' scan files as one nodes file and one organisations file.

    python scripts/hyperscaler-combine.py

Writes `R&D/Hyperscaler-dependence/institution-hosting.csv` (one row per institution) and
`institution-hosting-nodes.csv` (one row per DNS record), countries in
`progress.csv` order and each country's rows in its own order. A row with every field blank (what a
spreadsheet save leaves) is dropped. The columns are explained in the two `-metadata.csv` files beside them, which
are kept by hand. Re-run after any scan.

**The combined organisations file carries five shares the per-country files do not** *(2026-09-30)*:
telecoms, African data centres and IT firms, other foreign hosting, Chinese cloud, and private or
unusable. The scan's roll-up reports only the categories its fact sheets headline, which left half
of the average institution's addresses unaccounted for on the published dataset. They are counted
here from the nodes file on the scan's own rule (A, AAAA, MX and NS rows that resolved), which
reproduces every existing share exactly; with them, the shares and `unattributed` account for
every working address. `institution-hosting.csv` is published as a dataset by
`scripts/datasets.py`.
"""

from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

RD = Path(__file__).resolve().parent.parent / "R&D" / "Hyperscaler-dependence"
SCAN = RD / "scan"
ROUTABLE_TYPES = {"A", "AAAA", "MX", "NS"}  # as hyperscaler-scan.py
EXTRA = {"telco_share": ("telco-isp",), "african_dc_share": ("african-colo",),
         "foreign_host_share": ("commercial-host",), "chinese_cloud_share": ("chinese-cloud",),
         "unusable_share": ("unresolved",)}
AFTER = "national_or_self_share"   # the extra columns go after this one


def key(rec: dict) -> tuple:
    return rec["iso3"], rec["type"], rec["institution"]


def widen(h: list[str]) -> list[str]:
    i = h.index(AFTER) + 1
    return h[:i] + list(EXTRA) + h[i:]


def extra(h: list[str], row: list[str], rec: dict, c: Counter) -> list[str]:
    n = sum(c.values())
    if n != int(rec["routable"] or 0):
        sys.exit(f"{key(rec)}: nodes give {n} working addresses, organisations say {rec['routable']}")
    pct = lambda k: str(round(100 * k / n, 1) if n else 0.0)  # noqa: E731
    i = h.index(AFTER) + 1
    return row[:i] + [pct(sum(c[x] for x in cats)) for cats in EXTRA.values()] + row[i:]


def main() -> int:
    with open(RD / "progress.csv", encoding="utf-8-sig", newline="") as f:
        order = [r["iso3"] for r in csv.DictReader(f)]
    counts: dict[tuple, Counter] = defaultdict(Counter)
    for name, dest in (("nodes", "institution-hosting-nodes"), ("organisations", "institution-hosting")):
        header, n = None, 0
        with open(RD / f"{dest}.csv", "w", encoding="utf-8", newline="") as out:
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
                        w.writerow(widen(h) if name == "organisations" else h)
                    elif h != header:
                        sys.exit(f"{p}: columns differ from the first file")
                    for row in r:
                        if not any(x.strip() for x in row):
                            continue
                        rec = dict(zip(h, row))
                        if name == "nodes":
                            if rec["rr_type"] in ROUTABLE_TYPES and rec["rr_status"] == "ok":
                                counts[key(rec)][rec["category"]] += 1
                        else:
                            row = extra(h, row, rec, counts[key(rec)])
                        w.writerow(row)
                        n += 1
        print(f"{dest}.csv: {n} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
