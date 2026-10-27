#!/usr/bin/env python3
r"""study-ladder-agrisatellite.py — the agrisatellite study's four questions, counted.

    python scripts/study-ladder-agrisatellite.py --as-at 2026-09-30
    python scripts/study-ladder-agrisatellite.py --as-at 2026-09-30 --dry

`maturity/agrisatellite/maturity-study-agrisatellite.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "agrisatellite"
SUB = "agrisat"
GAPS = {'4': 'No source found since October 2023 counts farmers or districts reached by satellite-based advice or alerts.', '3': 'No source found since October 2023 says a satellite-based farming service publishes on a schedule.', '2': 'No source found since October 2023 says: is a service in use.', '1': 'No source found since October 2023 says: is satellite data being put to use in farming.', '5': ''}
EMPTY = 'Nothing found says whether satellite data is used in farming.'
UNPLACED = 'Nothing found since October 2023 says whether satellite data is used in farming.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
