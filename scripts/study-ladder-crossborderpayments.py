#!/usr/bin/env python3
r"""study-ladder-crossborderpayments.py — the crossborderpayments study's four questions, counted.

    python scripts/study-ladder-crossborderpayments.py --as-at 2026-09-30
    python scripts/study-ladder-crossborderpayments.py --as-at 2026-09-30 --dry

`maturity/crossborderpayments/maturity-study-crossborderpayments.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "crossborderpayments"
SUB = "crossborder"
GAPS = {'4': 'No source found since October 2023 gives a figure for cross-border digital payments.', '3': 'No source found since October 2023 says the country takes part in PAPSS or a regional payment system.', '2': 'No source found since October 2023 says: is a corridor in service.', '1': 'No source found since October 2023 says: is a cross-border corridor under way.', '5': ''}
EMPTY = 'Nothing found names a cross-border digital payment channel, or says there is none.'
UNPLACED = 'Nothing found since October 2023 says whether a cross-border digital payment channel is in service.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
