#!/usr/bin/env python3
r"""study-ladder-idrobustness.py — the idrobustness study's four questions, counted.

    python scripts/study-ladder-idrobustness.py --as-at 2026-09-30
    python scripts/study-ladder-idrobustness.py --as-at 2026-09-30 --dry

`maturity/idrobustness/maturity-study-idrobustness.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "idrobustness"
SUB = "robustness"
GAPS = {'4': 'No source found since October 2023 reports a certification, audit or assurance level for the system.', '3': 'No source found since October 2023 says the system checks people by biometrics.', '2': 'No source found since October 2023 says: is it in service.', '1': 'No source found since October 2023 says: is a national id system under way.', '5': ''}
EMPTY = 'Nothing found names a national ID system, or says there is none.'
UNPLACED = 'Nothing found since October 2023 says whether a national ID system is under way or in service.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
