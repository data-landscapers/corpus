#!/usr/bin/env python3
r"""study-ladder-healthexchange.py — the healthexchange study's four questions, counted.

    python scripts/study-ladder-healthexchange.py --as-at 2026-09-30
    python scripts/study-ladder-healthexchange.py --as-at 2026-09-30 --dry

`maturity/healthexchange/maturity-study-healthexchange.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "healthexchange"
SUB = "exchange"
GAPS = {'4': 'No source found since October 2023 says patient records are linked through the national ID or a national health identifier.', '3': 'No source found since October 2023 says three or more health systems exchange data, or a national exchange is in service.', '2': 'No source found since October 2023 says two health systems exchange data in routine use.', '1': 'No source found since October 2023 says an exchange between health systems is under way.', '5': ''}
EMPTY = "Nothing found names health systems exchanging data, or says there is none."
UNPLACED = "Nothing found since October 2023 names health systems exchanging data."

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
