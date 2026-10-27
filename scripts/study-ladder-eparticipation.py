#!/usr/bin/env python3
r"""study-ladder-eparticipation.py — the eparticipation study's four questions, counted.

    python scripts/study-ladder-eparticipation.py --as-at 2026-09-30
    python scripts/study-ladder-eparticipation.py --as-at 2026-09-30 --dry

`maturity/eparticipation/maturity-study-eparticipation.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "eparticipation"
SUB = "eparticipation"
GAPS = {'4': 'No source found since October 2023 says a rule requires drafts to be put online for public comment.', '3': 'No source found since October 2023 says the government published what it was told in an online consultation.', '2': 'No source found since October 2023 says: is a standing online channel in service.', '1': 'No source found since October 2023 says: has the government asked the public for views online.', '5': ''}
EMPTY = 'Nothing found says whether the public takes part in making policy online.'
UNPLACED = 'Nothing found since October 2023 says whether the government has asked the public for views online.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
