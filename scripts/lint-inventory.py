#!/usr/bin/env python3
"""lint-inventory.py — every object in the inventory states its purpose, and every orphan is listed.

    python scripts/lint-inventory.py            # read the share's inventory-corpus.csv
    python scripts/lint-inventory.py --csv PATH

**Strategic review 9, R168**, over what `inventory.py` (R166) writes. Three checks:

- **No purpose fails.** The fix is at the object: a script's docstring, a markdown file's heading, or a
  line in `lookups/README.md` or `logs/README.md` for a data file.
- **An orphan is listed, never failed**: an object no script, runbook or document names. A test is
  not an orphan; pytest finds it. Each orphan is deleted, or named by whatever keeps it.
- **The published process inventory names only what exists** *(R170)*. Every file named in the
  publishing half of `content/process-inventory.md` (from *Notice a cycle has closed* on) must be an
  object in the inventory, or a file on the share; a stale name fails. A runbook the page does not
  name is listed.

Exit 0 clean, 1 on an object without a purpose or a stale name, 2 when the inventory cannot be read.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "content" / "process-inventory.md"
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
    stale, unnamed = page_check(rows)
    for o in stale:
        print(f"lint-inventory: process-inventory.md names what does not exist: {o}")
    for o in unnamed:
        print(f"lint-inventory: runbook not on process-inventory.md (listed): {o}")
    bad = missing or stale
    print(f"lint-inventory: {'FAIL' if bad else 'ok'} - {len(rows)} objects, {len(missing)} without a "
          f"purpose, {len(orphans)} orphan(s), {len(stale)} stale name(s) on the process inventory")
    return 1 if bad else 0


def page_check(rows: list[dict]) -> tuple[list[str], list[str]]:
    """Names in the publishing half of the process inventory that are no object, and runbooks it
    does not name. A name is a backticked file; a template (`{unit}`) is not checked."""
    text = PAGE.read_text(encoding="utf-8")
    half = text[text.index("**Notice a cycle has closed**"):]
    objects = {r["object"].rstrip("/") for r in rows}
    bases = {o.rsplit("/", 1)[-1] for o in objects}
    stale = []
    for name in sorted(set(re.findall(r"`([^`\s{}]+\.(?:py|md|csv|yml))`", half))):
        if name in objects or name.rsplit("/", 1)[-1] in bases:
            continue
        if (ROOT / name).exists() or (Path(EXCHANGE) / name).exists():
            continue
        stale.append(name)
    unnamed = [r["object"] for r in rows if r["kind"] == "process" and r["object"] not in text]
    return stale, unnamed


if __name__ == "__main__":
    sys.exit(main())
