#!/usr/bin/env python3
r"""study-ladder-digitalskills.py — the digitalskills study's four questions, counted.

    python scripts/study-ladder-digitalskills.py --as-at 2026-09-30
    python scripts/study-ladder-digitalskills.py --as-at 2026-09-30 --dry

`maturity/digitalskills/maturity-study-digitalskills.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "digitalskills"
SUB = "publicskills"
GAPS = {'4': 'No source found since October 2023 gives a measured share of half or more of adults with basic digital skills.', '3': 'No source found since October 2023 gives a measured share of people with basic digital skills.', '2': 'No source found since October 2023 says: is one in service and counted.', '1': 'No source found since October 2023 says: is a national digital-skills programme under way.', '5': ''}
EMPTY = 'Nothing found says whether the public is taught digital skills.'
UNPLACED = 'Nothing found since October 2023 says whether a national digital-skills programme is under way or in service.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
