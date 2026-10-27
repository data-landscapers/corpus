#!/usr/bin/env python3
r"""study-ladder-policyresearch.py — the policyresearch study's four questions, counted.

    python scripts/study-ladder-policyresearch.py --as-at 2026-09-30
    python scripts/study-ladder-policyresearch.py --as-at 2026-09-30 --dry

`maturity/policyresearch/maturity-study-policyresearch.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "policyresearch"
SUB = "research"
GAPS = {'4': 'No source found since October 2023 says a local research institution holds a standing advisory role in digital policy.', '3': 'No source found since October 2023 says local research fed a digital policy, law or strategy.', '2': 'No source found since October 2023 says: does a local institution publish on it.', '1': 'No source found since October 2023 says: has research on digital policy begun.', '5': ''}
EMPTY = 'Nothing found says whether local institutions research digital policy.'
UNPLACED = 'Nothing found since October 2023 says whether a local institution researches digital policy.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
