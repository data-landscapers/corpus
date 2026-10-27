#!/usr/bin/env python3
r"""study-ladder-educationexchange.py — the educationexchange study's four questions, counted.

    python scripts/study-ladder-educationexchange.py --as-at 2026-09-30
    python scripts/study-ladder-educationexchange.py --as-at 2026-09-30 --dry

`maturity/educationexchange/maturity-study-educationexchange.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "educationexchange"
SUB = "exchange"
GAPS = {'4': 'No source found since October 2023 says learner records are linked to the national ID or another sector.', '3': 'No source found since October 2023 says one learner identifier is used across education systems.', '2': 'No source found since October 2023 says two education systems exchange data in use.', '1': 'No source found since October 2023 says a link between education systems is under way.', '5': ''}
EMPTY = "Nothing found names education systems exchanging data, or says there is none."
UNPLACED = "Nothing found since October 2023 names education systems exchanging data."

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
