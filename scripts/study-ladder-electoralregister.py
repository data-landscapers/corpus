#!/usr/bin/env python3
r"""study-ladder-electoralregister.py — the electoralregister study's four questions, counted.

    python scripts/study-ladder-electoralregister.py --as-at 2026-09-30
    python scripts/study-ladder-electoralregister.py --as-at 2026-09-30 --dry

`maturity/electoralregister/maturity-study-electoralregister.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "electoralregister"
SUB = "electoral"
GAPS = {'4': 'No source found since October 2023 says the roll is drawn from or checked against the ID or civil register.', '3': 'No source found since October 2023 says voters could check the roll.', '2': 'No source found since October 2023 says: is the roll held digitally.', '1': "No source found since October 2023 says: is a digital voters' roll under way.", '5': ''}
EMPTY = "Nothing found says how the voters' roll is held."
UNPLACED = "Nothing found since October 2023 says whether the voters' roll is held digitally."

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
