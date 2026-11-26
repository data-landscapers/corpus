#!/usr/bin/env python3
"""lint-inventory.py — every object in the inventory states its purpose, and every orphan is listed.

    python scripts/lint-inventory.py            # read the share's inventory-corpus.csv
    python scripts/lint-inventory.py --csv PATH

**Strategic review 9, R168**, over what `inventory.py` (R166) writes. Two checks:

- **No purpose fails.** The fix is at the object: a script's docstring, a markdown file's heading, or a
  line in `lookups/README.md` or `logs/README.md` for a data file.
- **An orphan is listed, never failed**: an object no script, runbook or document names. A test is
  not an orphan; pytest finds it. Each orphan is deleted, or named by whatever keeps it.

Exit 0 clean, 1 on an object without a purpose, 2 when the inventory cannot be read.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from status_lib import EXCHANGE  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=Path(EXCHANGE) / "documentation" / "inventory-corpus.csv")
    args = ap.parse_args()
    try:
        rows = list(csv.DictReader(args.csv.open(encoding="utf-8")))
    except OSError as e:
        print(f"lint-inventory: cannot read {args.csv}: {e}")
        return 2
    missing = [r["object"] for r in rows if not r["purpose"].strip()]
    orphans = [r["object"] for r in rows
               if r["kind"] != "test" and not r["read_by"].strip() and not r["written_by"].strip()]
    for o in missing:
        print(f"lint-inventory: no purpose: {o}")
    for o in orphans:
        print(f"lint-inventory: orphan (listed): {o}")
    verdict = "FAIL" if missing else "ok"
    print(f"lint-inventory: {verdict} - {len(rows)} objects, {len(missing)} without a purpose, "
          f"{len(orphans)} orphan(s)")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
