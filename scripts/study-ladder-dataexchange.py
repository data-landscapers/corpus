#!/usr/bin/env python3
r"""study-ladder-dataexchange.py — the dataexchange study's four questions, counted.

    python scripts/study-ladder-dataexchange.py --as-at 2026-09-30
    python scripts/study-ladder-dataexchange.py --as-at 2026-09-30 --dry

`maturity/dataexchange/maturity-study-dataexchange.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "dataexchange"
SUB = "exchange"
GAPS = {'4': 'No source found since October 2023 gives a figure for the exchanges through the platform.', '3': 'No source found since October 2023 counts ten or more institutions or systems connected.', '2': 'No source found since October 2023 says the platform is in service.', '1': 'No source found since October 2023 says a government data exchange platform is under way.', '5': ''}
EMPTY = "Nothing found names a government data exchange platform, or says there is none."
UNPLACED = "Nothing found since October 2023 names a government data exchange platform."

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
