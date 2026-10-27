#!/usr/bin/env python3
r"""study-ladder-socialregistry.py — the socialregistry study's four questions, counted.

    python scripts/study-ladder-socialregistry.py --as-at 2026-09-30
    python scripts/study-ladder-socialregistry.py --as-at 2026-09-30 --dry

`maturity/socialregistry/maturity-study-socialregistry.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "socialregistry"
SUB = "social"
GAPS = {'4': 'No source found since October 2023 says the social registry is linked to the national ID.', '3': 'No source found since October 2023 says two or more programmes use the social registry.', '2': 'No source found since October 2023 says: is a social registry in service.', '1': 'No source found since October 2023 says: is a social registry under way.', '5': ''}
EMPTY = 'Nothing found names a social registry, or says there is none.'
UNPLACED = 'Nothing found since October 2023 says whether a social registry is under way or in service.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
