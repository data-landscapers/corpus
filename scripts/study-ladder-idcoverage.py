#!/usr/bin/env python3
r"""study-ladder-idcoverage.py — the idcoverage study's four questions, counted.

    python scripts/study-ladder-idcoverage.py --as-at 2026-09-30
    python scripts/study-ladder-idcoverage.py --as-at 2026-09-30 --dry

`maturity/idcoverage/maturity-study-idcoverage.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "idcoverage"
SUB = "coverage"
GAPS = {'4': 'No source found since October 2023 puts birth registration at all births and deaths at 80% or more.', '3': 'No source found since October 2023 counts 99.9% of the population or more holding a national ID.', '2': 'No source found since October 2023 says: do two-thirds hold one.', '1': 'No source found since October 2023 says: does a third of the population hold a national id.', '5': ''}
EMPTY = 'Nothing found counts the people holding a national ID.'
UNPLACED = 'Nothing found since October 2023 counts the people holding a national ID.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
