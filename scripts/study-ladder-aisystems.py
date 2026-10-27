#!/usr/bin/env python3
r"""study-ladder-aisystems.py — the aisystems study's four questions, counted.

    python scripts/study-ladder-aisystems.py --as-at 2026-09-30
    python scripts/study-ladder-aisystems.py --as-at 2026-09-30 --dry

`maturity/aisystems/maturity-study-aisystems.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "aisystems"
SUB = "localai"
GAPS = {'4': 'No source found since October 2023 says national AI computing, models or datasets are open to named users.', '3': 'No source found since October 2023 says a facility with GPUs or AI accelerators is in service in the country.', '2': 'No source found since October 2023 says: is one in service.', '1': 'No source found since October 2023 says: is a national ai model, dataset or ai computing facility under way.', '5': ''}
EMPTY = 'Nothing found says whether AI is built or hosted in the country.'
UNPLACED = 'Nothing found since October 2023 says whether an AI model, dataset or computing facility is in service in the country.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
