#!/usr/bin/env python3
r"""study-ladder-idregisters.py — the idregisters study's four questions, counted.

    python scripts/study-ladder-idregisters.py --as-at 2026-09-30
    python scripts/study-ladder-idregisters.py --as-at 2026-09-30 --dry

`maturity/idregisters/maturity-study-idregisters.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "idregisters"
SUB = "registers"
GAPS = {'4': 'No source found since October 2023 gives a figure from checking a register against the ID.', '3': 'No source found since October 2023 shows three or more main public registers using the national ID number.', '2': 'No source found since October 2023 says: is one public register keyed on it.', '1': "No source found since October 2023 says: is another register's use of the id number under way.", '5': ''}
EMPTY = 'Nothing found says whether public registers use the national ID number.'
UNPLACED = 'Nothing found since October 2023 says whether public registers use the national ID number.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
