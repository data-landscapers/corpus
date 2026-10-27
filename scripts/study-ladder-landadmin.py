#!/usr/bin/env python3
r"""study-ladder-landadmin.py — the landadmin study's four questions, counted.

    python scripts/study-ladder-landadmin.py --as-at 2026-09-30
    python scripts/study-ladder-landadmin.py --as-at 2026-09-30 --dry

`maturity/landadmin/maturity-study-landadmin.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "landadmin"
SUB = "landmis"
GAPS = {'4': 'No source found since October 2023 says land or property tax is assessed or paid through the land system.', '3': 'No source found since October 2023 says the land system joins records to survey maps or valuation.', '2': 'No source found since October 2023 says: are land transactions processed electronically.', '1': 'No source found since October 2023 says: is a land information system under way.', '5': ''}
EMPTY = 'Nothing found says how land transactions are processed.'
UNPLACED = 'Nothing found since October 2023 says whether land transactions are processed electronically.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
