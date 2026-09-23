#!/usr/bin/env python3
r"""maturity-rubric-cut.py — cut reviewed chapters of the rubric draft into the lookup.

    python scripts/maturity-rubric-cut.py --chapter Governance --kind instrument --kind system
    python scripts/maturity-rubric-cut.py --check      # every cut row still equals the draft

**The draft is the source until the lookup exists** (task C2). Cowork drafts
`documentation/maturity-rubric.md` a chapter's kind at a time; CC reviews it
(`documentation/maturity-rubric-review.md`) and, on acceptance, cuts exactly what was accepted —
named by chapter and kind — into `lookups/maturity-rubric.csv`. Rows already in the lookup for
other indicators are kept, so the lookup grows chapter by chapter and never takes a row that
has not been reviewed, even when the draft already holds the next chapter.

**Nothing is cut that the checker refuses.** `lint-maturity-rubric.py` runs over the draft
first, limited to what is being cut; a failure stops the cut.

**`--check` is the drift test**: every indicator in the lookup must still read, row for row,
as the draft does. A later edit to an accepted chapter is a re-review and a re-cut, not a quiet
divergence between the two files.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import indicators_lib  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DRAFT = os.path.join(ROOT, "documentation", "maturity-rubric.md")
LOOKUP = os.path.join(ROOT, "lookups", "maturity-rubric.csv")

_spec = importlib.util.spec_from_file_location("lr", os.path.join(HERE, "lint-maturity-rubric.py"))
lr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lr)
COLUMNS = lr.COLUMNS


def clean(r: dict) -> dict:
    return {"indicator_id": r["indicator_id"].strip(), "stage": str(int(r["stage"])),
            "anchor": r["anchor"].strip(), "interpolated": r["interpolated"].strip()}


def held() -> list[dict]:
    return [clean(r) for r in lr.read(LOOKUP)[1]] if os.path.exists(LOOKUP) else []


def render(rows: list[dict]) -> str:
    order = {r["indicator_id"]: n for n, r in enumerate(indicators_lib.frame())}
    rows = sorted(rows, key=lambda r: (order.get(r["indicator_id"], 10**6), int(r["stage"])))
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Cut reviewed rubric chapters into the lookup.")
    ap.add_argument("--chapter", action="append", default=[], help="a frame chapter, repeatable")
    ap.add_argument("--kind", action="append", default=[],
                    help="instrument, system or measure, repeatable; all kinds when omitted")
    ap.add_argument("--check", action="store_true", help="compare the lookup with the draft")
    a = ap.parse_args(argv)

    draft = [clean(r) for r in lr.read(DRAFT)[1]]
    by_id = {r["indicator_id"]: r for r in indicators_lib.assessed()}

    if a.check:
        lookup = held()
        cut_ids = {r["indicator_id"] for r in lookup}
        want = [r for r in draft if r["indicator_id"] in cut_ids]
        if render(lookup) != render(want):
            print("maturity-rubric-cut: the lookup and the draft disagree for an indicator "
                  "already cut — re-review the change and re-cut its chapter")
            return 1
        print(f"maturity-rubric-cut: ok — {len(cut_ids)} indicator(s) in the lookup read as "
              f"the draft does")
        return 0

    if not a.chapter:
        ap.error("name the accepted chapter(s) with --chapter")
    pick = {i for i, r in by_id.items()
            if r["chapter"] in a.chapter and (not a.kind or r["kind"] in a.kind)}
    rows = [r for r in draft if r["indicator_id"] in pick]
    for ch in a.chapter:
        fails, warns, st = lr.check(DRAFT, chapter=ch)
        mine = [f for f in fails
                if any(i in f for i in pick) or (f"{ch} " in f and "drafted in part" in f)]
        if mine:
            print("maturity-rubric-cut: the checker refuses what would be cut:\n  "
                  + "\n  ".join(mine))
            return 1
    missing = sorted(pick - {r["indicator_id"] for r in rows})
    if missing:
        print(f"maturity-rubric-cut: no draft rows for {', '.join(missing)} — nothing cut")
        return 1
    kept = [r for r in held() if r["indicator_id"] not in pick]
    text = render(kept + rows)
    with open(LOOKUP, "w", encoding="utf-8-sig", newline="") as fh:
        fh.write(text)
    ids = len({r["indicator_id"] for r in kept + rows})
    print(f"maturity-rubric-cut: {len(pick)} indicator(s), {len(rows)} row(s) cut from "
          f"{', '.join(a.chapter)}{' (' + ', '.join(a.kind) + ')' if a.kind else ''}; "
          f"the lookup now holds {ids} indicator(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
