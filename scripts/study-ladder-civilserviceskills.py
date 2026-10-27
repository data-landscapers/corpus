#!/usr/bin/env python3
r"""study-ladder-civilserviceskills.py — the civilserviceskills study's four questions, counted.

    python scripts/study-ladder-civilserviceskills.py --as-at 2026-09-30
    python scripts/study-ladder-civilserviceskills.py --as-at 2026-09-30 --dry

`maturity/civilserviceskills/maturity-study-civilserviceskills.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "civilserviceskills"
SUB = "csskills"
GAPS = {'4': 'No source found since October 2023 gives the share of the civil service trained in digital skills.', '3': 'No source found since October 2023 says digital-skills training reaches civil servants across government.', '2': 'No source found since October 2023 says: is a standing programme in service.', '1': 'No source found since October 2023 says: is digital-skills training for civil servants under way.', '5': ''}
EMPTY = 'Nothing found says whether civil servants are trained in digital skills.'
UNPLACED = 'Nothing found since October 2023 says whether civil servants are trained in digital skills.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
