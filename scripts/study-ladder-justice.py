#!/usr/bin/env python3
r"""study-ladder-justice.py — the justice study's four questions, counted.

    python scripts/study-ladder-justice.py --as-at 2026-09-30
    python scripts/study-ladder-justice.py --as-at 2026-09-30 --dry

`maturity/justice/maturity-study-justice.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "justice"
SUB = "justice"
GAPS = {'4': 'No source found since October 2023 says judgments are published or case status can be looked up online.', '3': 'No source found since October 2023 says cases can be filed with the courts online.', '2': 'No source found since October 2023 says: do courts manage cases electronically.', '1': 'No source found since October 2023 says: is a court case management system under way.', '5': ''}
EMPTY = 'Nothing found says how courts manage their cases.'
UNPLACED = 'Nothing found since October 2023 says whether courts manage cases electronically.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
