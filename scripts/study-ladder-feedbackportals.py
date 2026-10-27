#!/usr/bin/env python3
r"""study-ladder-feedbackportals.py — the feedbackportals study's four questions, counted.

    python scripts/study-ladder-feedbackportals.py --as-at 2026-09-30
    python scripts/study-ladder-feedbackportals.py --as-at 2026-09-30 --dry

`maturity/feedbackportals/maturity-study-feedbackportals.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "feedbackportals"
SUB = "feedback"
GAPS = {'4': 'No source found since October 2023 gives resolution rates, response times or a report of the cases handled.', '3': 'No source found since October 2023 says a complaints channel reaches services across government.', '2': 'No source found since October 2023 says: is one in service with cases on record.', '1': 'No source found since October 2023 says: is a digital feedback channel under way.', '5': ''}
EMPTY = 'Nothing found says whether people can complain about public services online.'
UNPLACED = 'Nothing found since October 2023 says whether a digital channel for complaints about public services is under way or in service.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
