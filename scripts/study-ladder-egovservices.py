#!/usr/bin/env python3
r"""study-ladder-egovservices.py — the egovservices study's four questions, counted.

    python scripts/study-ladder-egovservices.py --as-at 2026-09-30
    python scripts/study-ladder-egovservices.py --as-at 2026-09-30 --dry

`maturity/egovservices/maturity-study-egovservices.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "egovservices"
SUB = "eservices"
GAPS = {'4': 'No source found since October 2023 gives users, applications or transactions through the national portal.', '3': "No source found since October 2023 says one national portal carries several ministries' services with shared sign-in.", '2': 'No source found since October 2023 says: are ten or more services online.', '1': 'No source found since October 2023 says: are government services going online.', '5': ''}
EMPTY = 'Nothing found says whether government services can be used online.'
UNPLACED = 'Nothing found since October 2023 says whether government services can be used online.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
