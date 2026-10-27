#!/usr/bin/env python3
r"""study-ladder-metsatellite.py — the metsatellite study's four questions, counted.

    python scripts/study-ladder-metsatellite.py --as-at 2026-09-30
    python scripts/study-ladder-metsatellite.py --as-at 2026-09-30 --dry

`maturity/metsatellite/maturity-study-metsatellite.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "metsatellite"
SUB = "metsat"
GAPS = {'4': 'No source found since October 2023 says the weather service holds ISO 9001 certification.', '3': 'No source found since October 2023 says the weather service issues warnings drawing on satellite data.', '2': 'No source found since October 2023 says: does it use it in forecasts.', '1': 'No source found since October 2023 says: does the weather service receive satellite data.', '5': ''}
EMPTY = 'Nothing found says whether the national weather service uses satellite data.'
UNPLACED = 'Nothing found since October 2023 says whether the national weather service receives or uses satellite data.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
