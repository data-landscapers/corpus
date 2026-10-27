#!/usr/bin/env python3
r"""study-ladder-socialprotection.py — the socialprotection study's four questions, counted.

    python scripts/study-ladder-socialprotection.py --as-at 2026-09-30
    python scripts/study-ladder-socialprotection.py --as-at 2026-09-30 --dry

`maturity/socialprotection/maturity-study-socialprotection.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "socialprotection"
SUB = "socialmis"
GAPS = {'4': 'No source found since October 2023 says one information system serves several social programmes.', '3': "No source found since October 2023 says the programme's system pays beneficiaries electronically.", '2': 'No source found since October 2023 says: is a programme run on one.', '1': 'No source found since October 2023 says: is a programme management information system under way.', '5': ''}
EMPTY = 'Nothing found says how social programmes are administered.'
UNPLACED = 'Nothing found since October 2023 says whether a social programme runs on an information system.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
