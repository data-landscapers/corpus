#!/usr/bin/env python3
r"""study-ladder-digitaldivides.py — the digitaldivides study's four questions, counted.

    python scripts/study-ladder-digitaldivides.py --as-at 2026-09-30
    python scripts/study-ladder-digitaldivides.py --as-at 2026-09-30 --dry

`maturity/digitaldivides/maturity-study-digitaldivides.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "digitaldivides"
SUB = "ruralaccess"
GAPS = {'4': 'No source found since October 2023 gives rural internet use of 80 per cent or more of the urban rate.', '3': 'No source found since October 2023 gives internet use in rural and in urban areas.', '2': 'No source found since October 2023 says: is one delivering, with sites counted.', '1': 'No source found since October 2023 says: is a programme to connect rural areas under way.', '5': ''}
EMPTY = 'Nothing found says whether rural areas are being connected or how far rural internet use lags urban.'
UNPLACED = 'Nothing found since October 2023 says whether a programme to connect rural areas is under way.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
