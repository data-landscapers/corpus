#!/usr/bin/env python3
r"""study-ladder-birthidlink.py — the birthidlink study's four questions, counted.

    python scripts/study-ladder-birthidlink.py --as-at 2026-09-30
    python scripts/study-ladder-birthidlink.py --as-at 2026-09-30 --dry

`maturity/birthidlink/maturity-study-birthidlink.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "birthidlink"
SUB = "link"
GAPS = {'4': 'No source found since October 2023 gives a figure for records exchanged between the two.', '3': 'No source found since October 2023 says births enrol people in the ID system and deaths retire their numbers.', '2': 'No source found since October 2023 says: is one link in service.', '1': 'No source found since October 2023 says: is a link under way.', '5': ''}
EMPTY = 'Nothing found says whether the civil register and the ID system are linked.'
UNPLACED = 'Nothing found since October 2023 says whether the civil register and the ID system are linked.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
