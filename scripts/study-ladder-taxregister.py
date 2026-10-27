#!/usr/bin/env python3
r"""study-ladder-taxregister.py — the taxregister study's four questions, counted.

    python scripts/study-ladder-taxregister.py --as-at 2026-09-30
    python scripts/study-ladder-taxregister.py --as-at 2026-09-30 --dry

`maturity/taxregister/maturity-study-taxregister.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "taxregister"
SUB = "taxpayers"
GAPS = {'4': 'No source found since October 2023 says the taxpayer number is tied to the national ID.', '3': 'No source found since October 2023 says the taxpayer number is shared with business registration or customs.', '2': 'No source found since October 2023 says: are taxpayers registered on computer.', '1': 'No source found since October 2023 says: is a computerised taxpayer register under way.', '5': ''}
EMPTY = 'Nothing found says how taxpayers are registered.'
UNPLACED = 'Nothing found since October 2023 says whether taxpayers are registered on computer.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
