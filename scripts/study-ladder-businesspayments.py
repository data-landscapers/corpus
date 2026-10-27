#!/usr/bin/env python3
r"""study-ladder-businesspayments.py — the businesspayments study's four questions, counted.

    python scripts/study-ladder-businesspayments.py --as-at 2026-09-30
    python scripts/study-ladder-businesspayments.py --as-at 2026-09-30 --dry

`maturity/businesspayments/maturity-study-businesspayments.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "businesspayments"
SUB = "business"
GAPS = {'4': 'No source found since October 2023 gives a figure for e-procurement.', '3': 'No source found since October 2023 says e-procurement runs end to end or is required of all public bodies.', '2': 'No source found since October 2023 says: is an e-procurement system in service.', '1': 'No source found since October 2023 says: is e-procurement under way.', '5': ''}
EMPTY = 'Nothing found names a government e-procurement system, or says there is none.'
UNPLACED = 'Nothing found since October 2023 says whether government e-procurement is under way or in service.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
