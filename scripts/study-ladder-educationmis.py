#!/usr/bin/env python3
r"""study-ladder-educationmis.py — the educationmis study's four questions, counted.

    python scripts/study-ladder-educationmis.py --as-at 2026-09-30
    python scripts/study-ladder-educationmis.py --as-at 2026-09-30 --dry

`maturity/educationmis/maturity-study-educationmis.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "educationmis"
SUB = "emis"
GAPS = {'4': 'No source found since October 2023 says learner records are linked to the national ID or another government system.', '3': 'No source found since October 2023 says the system holds a record for each learner.', '2': 'No source found since October 2023 says: is the school census run through it.', '1': 'No source found since October 2023 says: is an education information system under way.', '5': ''}
EMPTY = 'Nothing found says whether the education ministry holds its statistics in an information system.'
UNPLACED = 'Nothing found since October 2023 says whether an education information system is under way or in service.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
