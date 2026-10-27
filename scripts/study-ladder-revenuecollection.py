#!/usr/bin/env python3
r"""study-ladder-revenuecollection.py — the revenuecollection study's four questions, counted.

    python scripts/study-ladder-revenuecollection.py --as-at 2026-09-30
    python scripts/study-ladder-revenuecollection.py --as-at 2026-09-30 --dry

`maturity/revenuecollection/maturity-study-revenuecollection.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "revenuecollection"
SUB = "revenue"
GAPS = {'4': 'No source found since October 2023 gives a figure for revenue paid electronically.', '3': 'No source found since October 2023 says the main taxes and customs duties are filed and paid electronically.', '2': 'No source found since October 2023 says: can some taxes or fees be paid electronically.', '1': 'No source found since October 2023 says: is electronic payment of taxes or fees under way.', '5': ''}
EMPTY = 'Nothing found says how taxes and fees are paid.'
UNPLACED = 'Nothing found since October 2023 says whether taxes or fees can be paid electronically.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
