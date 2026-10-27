#!/usr/bin/env python3
r"""study-ladder-healthmis.py — the healthmis study's four questions, counted.

    python scripts/study-ladder-healthmis.py --as-at 2026-09-30
    python scripts/study-ladder-healthmis.py --as-at 2026-09-30 --dry

`maturity/healthmis/maturity-study-healthmis.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "healthmis"
SUB = "hmis"
GAPS = {'4': "No source found since October 2023 gives the system's reporting completeness or timeliness.", '3': 'No source found since October 2023 says the system is linked to surveillance, supply chain or a register.', '2': 'No source found since October 2023 says: is a national one in service.', '1': 'No source found since October 2023 says: is a health information system under way.', '5': ''}
EMPTY = 'Nothing found says whether health reporting runs through a national information system.'
UNPLACED = 'Nothing found since October 2023 says whether a health information system is under way or in service.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
