#!/usr/bin/env python3
r"""reopen-considered.py — put discarded evidence back in stage 4's way.

    python scripts/reopen-considered.py --unit BEN            # show
    python scripts/reopen-considered.py --unit BEN --apply    # do it

**`lint-considered.py` finds them; this is the only thing that can undo them.** A
slug in `considered.txt` is invisible to stage 4 for ever — it reads a set
difference and `BUILD.md` step 200 says an item already considered is never
reopened — so a source read and discarded cannot be reached by any amount of
re-running. Striking the line is the whole of the repair's mechanical half.

**It is a narrow instrument on purpose.** It removes only what
`lint-considered.py` reports: filler-staged, marked, cited by no ledger row, and
over an indicator the report calls ***No evidence***. Every other *nothing moves*
judgement stays judged, including ones that may be equally wrong and that this
query cannot see (Bill, 2026-09-10).

**Reopening without the corrected rule is worse than useless** — it sends the
sources back through the judgement that discarded them and burns the run. Read
`BUILD.md` stage 4 step 2 as corrected on 2026-09-10 first: a source establishing
a standing position the ledger lacks **mints a row**, it does not default.

`--apply` writes; without it nothing is touched. A backup of each file is left
beside it as `considered.txt.before-reopen` on the first apply only, so a second
run cannot overwrite the original state with an already-repaired one.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
REPORTS = CORPUS / "outputs" / "reports"

_spec = importlib.util.spec_from_file_location(
    "lc", CORPUS / "scripts" / "lint-considered.py")
lc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lc)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", action="append", required=True,
                    help="unit to reopen; repeatable")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    found = lc.audit(set(args.unit))
    if not found:
        print("reopen-considered: nothing to reopen in " + ", ".join(sorted(args.unit)))
        return 0

    total = 0
    for iso in sorted(found):
        slugs = {d["slug"] for d in found[iso]}
        path = REPORTS / iso / "considered.txt"
        lines = path.read_text(encoding="utf-8").splitlines()
        keep = [l for l in lines if l.strip() not in slugs]
        cut = len(lines) - len(keep)
        inds = len({d["indicator"] for d in found[iso]})
        print(f"  {iso}: {cut} slug(s) reopened over {inds} indicator(s) "
              f"({len(lines)} -> {len(keep)} considered)")
        total += cut
        if args.apply:
            backup = path.with_suffix(".txt.before-reopen")
            if not backup.exists():
                backup.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
            path.write_text("\n".join(keep) + "\n", encoding="utf-8", newline="\n")

    verb = "reopened" if args.apply else "would reopen"
    print(f"reopen-considered: {verb} {total} slug(s) across {len(found)} unit(s)."
          + ("" if args.apply else "  Re-run with --apply."))
    if args.apply:
        print("  Next: `report-scan.py --slugs {ISO}` from scripts/.workroot/ now lists "
              "them,\n  and stage 4 step 2's corrected rule is what they must be read "
              "under.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
