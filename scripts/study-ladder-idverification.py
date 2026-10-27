#!/usr/bin/env python3
r"""study-ladder-idverification.py — the idverification study's four questions, counted.

    python scripts/study-ladder-idverification.py --as-at 2026-09-30
    python scripts/study-ladder-idverification.py --as-at 2026-09-30 --dry

`maturity/idverification/maturity-study-idverification.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "idverification"
SUB = "use"
GAPS = {'4': 'No source found since October 2023 gives a figure for verifications or counts the services relying on the ID.', '3': 'No source found since October 2023 shows services in two or more sectors checking against the ID.', '2': 'No source found since October 2023 says a service in use checks people against the ID.', '1': "No source found since October 2023 says another system's use of the national ID is under way.", '5': ''}
EMPTY = "Nothing found names another system checking people against the national ID, or says there is none."
UNPLACED = "Nothing found since October 2023 names another system checking people against the national ID."

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
