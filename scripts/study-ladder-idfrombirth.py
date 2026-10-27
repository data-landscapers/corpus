#!/usr/bin/env python3
r"""study-ladder-idfrombirth.py — the idfrombirth study's four questions, counted.

    python scripts/study-ladder-idfrombirth.py --as-at 2026-09-30
    python scripts/study-ladder-idfrombirth.py --as-at 2026-09-30 --dry

`maturity/idfrombirth/maturity-study-idfrombirth.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "idfrombirth"
SUB = "frombirth"
GAPS = {'4': 'No source found since October 2023 puts birth registration at all births and deaths at 80% or more.', '3': 'No source found since October 2023 says every registered birth across the country receives the number.', '2': 'No source found since October 2023 says: is a number given at birth in part of the country.', '1': 'No source found since October 2023 says: is a number at birth provided for or piloted.', '5': ''}
EMPTY = 'Nothing found says whether a birth is given an identity number.'
UNPLACED = 'Nothing found since October 2023 says whether a birth is given an identity number.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
