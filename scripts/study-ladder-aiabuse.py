#!/usr/bin/env python3
r"""study-ladder-aiabuse.py — the aiabuse study's four questions, counted.

    python scripts/study-ladder-aiabuse.py --as-at 2026-09-30
    python scripts/study-ladder-aiabuse.py --as-at 2026-09-30 --dry

`maturity/aiabuse/maturity-study-aiabuse.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "aiabuse"
SUB = "aiharm"
GAPS = {'4': 'No source found since October 2023 gives an enforcement or redress decision about a harm from AI.', '3': 'No source found since October 2023 says a body is designated with a mandate over AI.', '2': 'No source found since October 2023 says: is a rule on ai harms in force.', '1': 'No source found since October 2023 says: is a rule or authority on ai harms being drafted.', '5': ''}
EMPTY = 'Nothing found says whether anything addresses harms from AI.'
UNPLACED = 'Nothing found since October 2023 says whether a rule on harms from AI is drafted or in force.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
