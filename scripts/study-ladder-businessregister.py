#!/usr/bin/env python3
r"""study-ladder-businessregister.py — the businessregister study's four questions, counted.

    python scripts/study-ladder-businessregister.py --as-at 2026-09-30
    python scripts/study-ladder-businessregister.py --as-at 2026-09-30 --dry

`maturity/businessregister/maturity-study-businessregister.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "businessregister"
SUB = "business"
GAPS = {'4': 'No source found since October 2023 says the register holds the beneficial owners of every company.', '3': 'No source found since October 2023 says registration gives one number shared with tax or social security.', '2': 'No source found since October 2023 says: can firms register online.', '1': 'No source found since October 2023 says: is a digital business register under way.', '5': ''}
EMPTY = 'Nothing found says how firms are registered.'
UNPLACED = 'Nothing found since October 2023 says whether firms can register online.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
