#!/usr/bin/env python3
r"""study-ladder-customs.py — the customs study's four questions, counted.

    python scripts/study-ladder-customs.py --as-at 2026-09-30
    python scripts/study-ladder-customs.py --as-at 2026-09-30 --dry

`maturity/customs/maturity-study-customs.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "customs"
SUB = "customs"
GAPS = {'4': 'No source held since October 2023 says customs exchanges data through a system open to its whole regional community.', '3': 'No source held since October 2023 says a trade single window is in service.', '2': 'No source held since October 2023 says: are declarations processed electronically.', '1': 'No source held since October 2023 says: is an automated customs system under way.', '5': ''}
EMPTY = 'Nothing held says how customs declarations are processed.'
UNPLACED = 'Nothing held since October 2023 says whether customs declarations are processed electronically.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
