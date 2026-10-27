#!/usr/bin/env python3
r"""study-ladder-g2ppayments.py — the g2ppayments study's four questions, counted.

    python scripts/study-ladder-g2ppayments.py --as-at 2026-09-30
    python scripts/study-ladder-g2ppayments.py --as-at 2026-09-30 --dry

`maturity/g2ppayments/maturity-study-g2ppayments.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "g2ppayments"
SUB = "g2p"
GAPS = {'4': 'No source found since October 2023 says government payments are checked against the ID or a social registry.', '3': 'No source found since October 2023 shows two or more main government payment streams paid digitally.', '2': 'No source found since October 2023 says: does one government programme pay people digitally.', '1': 'No source found since October 2023 says: is digital government payment under way.', '5': ''}
EMPTY = 'Nothing found says how government pays people.'
UNPLACED = 'Nothing found since October 2023 says whether government pays people digitally.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
