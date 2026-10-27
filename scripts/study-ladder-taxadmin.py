#!/usr/bin/env python3
r"""study-ladder-taxadmin.py — the taxadmin study's four questions, counted.

    python scripts/study-ladder-taxadmin.py --as-at 2026-09-30
    python scripts/study-ladder-taxadmin.py --as-at 2026-09-30 --dry

`maturity/taxadmin/maturity-study-taxadmin.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "taxadmin"
SUB = "taxsystem"
GAPS = {'4': 'No source found since October 2023 says online filing is mandatory or used for half or more of returns.', '3': "No source found since October 2023 says taxes can be paid electronically through the tax authority's system.", '2': 'No source found since October 2023 says: can tax returns be filed online.', '1': 'No source found since October 2023 says: is an electronic tax system under way.', '5': ''}
EMPTY = 'Nothing found says how taxes are filed and paid.'
UNPLACED = 'Nothing found since October 2023 says whether tax returns can be filed online.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
