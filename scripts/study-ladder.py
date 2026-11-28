#!/usr/bin/env python3
r"""study-ladder.py — a maturity study's ladder, counted: the one entry point (R172, housekeeping 90).

    python scripts/study-ladder.py {id} --as-at 2026-09-30
    python scripts/study-ladder.py {id} --as-at 2026-09-30 --dry

The ladder is data where it can be (`maturity/documentation/ladders-as-data.md`). The `ladder`
block of `maturity/{id}/study.json` names its `counter`:

- `first` — `study_first_ladder.py` counts the study's questions and aspects; the block carries
  `sub`, `gaps` (one line a stage), `empty` and `unplaced`, the texts a cell takes when nothing
  answers or nothing places;
- `figure` — `study_figure.py` counts a measure the reference file holds, from its own table;
- `own` — the rule needs more than the question-and-aspect form holds, and
  `scripts/study-ladder-{id}.py` is the code; the block's `why` says what.

Exit: 0 written, 2 the study cannot be read or names no counter.
"""
from __future__ import annotations

import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import study_lib  # noqa: E402


def spec(sid: str) -> dict:
    """The study's `ladder` block; raises `study_lib.StudyError` when there is none."""
    block = study_lib.load(sid).get("ladder") or {}
    if block.get("counter") not in ("first", "figure", "own"):
        raise study_lib.StudyError(f"maturity/{sid}/study.json names no ladder counter")
    return block


def own_path(sid: str) -> str:
    return os.path.join(HERE, f"study-ladder-{sid}.py")


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 2
    sid, rest = argv[0], argv[1:]
    try:
        block = spec(sid)
    except study_lib.StudyError as e:
        print(f"study-ladder: {e}")
        return 2
    if block["counter"] == "first":
        import study_first_ladder
        return study_first_ladder.run(sid, block["sub"], block["gaps"], block["empty"],
                                      block["unplaced"], rest)
    if block["counter"] == "figure":
        import study_figure
        return study_figure.main([sid, "ladder", *rest])
    sys.argv = [own_path(sid), *rest]
    try:
        runpy.run_path(own_path(sid), run_name="__main__")
    except SystemExit as e:
        return int(e.code or 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
