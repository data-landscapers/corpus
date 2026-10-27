#!/usr/bin/env python3
r"""study-ladder-centralbank.py — the centralbank study's four questions, counted.

    python scripts/study-ladder-centralbank.py --as-at 2026-09-30
    python scripts/study-ladder-centralbank.py --as-at 2026-09-30 --dry

`maturity/centralbank/maturity-study-centralbank.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "centralbank"
SUB = "centralbank"
GAPS = {'4': 'No source found since October 2023 says the country is live on PAPSS.', '3': 'No source found since October 2023 says the central bank runs or oversees a national switch.', '2': 'No source found since October 2023 says: does the central bank license payment providers.', '1': 'No source found since October 2023 says: is a payments mandate being set up.', '5': ''}
EMPTY = 'Nothing found says what the central bank does over payments.'
UNPLACED = 'Nothing found since October 2023 says what the central bank does over payments.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
