#!/usr/bin/env python3
r"""study-ladder-paymentsuptake.py — the paymentsuptake study's four questions, counted.

    python scripts/study-ladder-paymentsuptake.py --as-at 2026-09-30
    python scripts/study-ladder-paymentsuptake.py --as-at 2026-09-30 --dry

`maturity/paymentsuptake/maturity-study-paymentsuptake.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "paymentsuptake"
SUB = "uptake"
GAPS = {'4': 'No survey held since October 2023 puts adults paying digitally at 79% or more.', '3': 'No survey held since October 2023 puts adults with an account at 79% or more.', '2': 'No source found since October 2023 says: do over half hold one.', '1': 'No source found since October 2023 says: does a quarter of adults hold an account.', '5': ''}
EMPTY = 'Nothing found gives a survey share of adults with an account.'
UNPLACED = 'Nothing found since October 2023 gives a survey share of adults with an account.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
