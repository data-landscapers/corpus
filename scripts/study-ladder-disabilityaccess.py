#!/usr/bin/env python3
r"""study-ladder-disabilityaccess.py — the disabilityaccess study's four questions, counted.

    python scripts/study-ladder-disabilityaccess.py --as-at 2026-09-30
    python scripts/study-ladder-disabilityaccess.py --as-at 2026-09-30 --dry

`maturity/disabilityaccess/maturity-study-disabilityaccess.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "disabilityaccess"
SUB = "accessibility"
GAPS = {'4': 'No source found since October 2023 gives the results of an accessibility audit of public websites or digital services.', '3': 'No source found since October 2023 says accessible digital services or assistive technology were delivered.', '2': 'No source found since October 2023 says: is a rule in force.', '1': 'No source found since October 2023 says: is digital accessibility under way.', '5': ''}
EMPTY = 'Nothing found says whether information and digital services are made accessible to persons with disabilities.'
UNPLACED = 'Nothing found since October 2023 says whether information or digital services are being made accessible to persons with disabilities.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
