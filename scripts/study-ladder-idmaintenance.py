#!/usr/bin/env python3
r"""study-ladder-idmaintenance.py — the idmaintenance study's four questions, counted.

    python scripts/study-ladder-idmaintenance.py --as-at 2026-09-30
    python scripts/study-ladder-idmaintenance.py --as-at 2026-09-30 --dry

`maturity/idmaintenance/maturity-study-idmaintenance.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "idmaintenance"
SUB = "maintenance"
GAPS = {'4': 'No source found since October 2023 says the system runs on code the state owns.', '3': 'No source found since October 2023 says national staff maintain the system or the foreign contract has ended.', '2': 'No source found since October 2023 says: does a national authority run it day to day.', '1': 'No source found since October 2023 says: is national operation under way.', '5': ''}
EMPTY = 'Nothing found says who operates the national ID system.'
UNPLACED = 'Nothing found since October 2023 says who operates the national ID system.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
