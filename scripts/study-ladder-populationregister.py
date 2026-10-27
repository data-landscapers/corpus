#!/usr/bin/env python3
r"""study-ladder-populationregister.py — the populationregister study's four questions, counted.

    python scripts/study-ladder-populationregister.py --as-at 2026-09-30
    python scripts/study-ladder-populationregister.py --as-at 2026-09-30 --dry

`maturity/populationregister/maturity-study-populationregister.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "populationregister"
SUB = "population"
GAPS = {'4': 'No source found since October 2023 says other systems take records from the population register.', '3': 'No source found since October 2023 says births or deaths are entered in the population register.', '2': 'No source found since October 2023 says: is a population register in service.', '1': 'No source found since October 2023 says: is a population register under way.', '5': ''}
EMPTY = 'Nothing found names a population register, or says there is none.'
UNPLACED = 'Nothing found since October 2023 says whether a population register is under way or in service.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
