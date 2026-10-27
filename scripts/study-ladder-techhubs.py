#!/usr/bin/env python3
r"""study-ladder-techhubs.py — the techhubs study's four questions, counted.

    python scripts/study-ladder-techhubs.py --as-at 2026-09-30
    python scripts/study-ladder-techhubs.py --as-at 2026-09-30 --dry

`maturity/techhubs/maturity-study-techhubs.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "techhubs"
SUB = "hub"
GAPS = {'4': 'No source found since October 2023 says a science or technology park is in service with tenants.', '3': 'No source found since October 2023 says hubs with programmes are in service in two or more cities.', '2': 'No source found since October 2023 says: does a hub run programmes for startups.', '1': 'No source found since October 2023 says: is a hub or technology park under way.', '5': ''}
EMPTY = 'Nothing found says whether technology hubs operate in the country.'
UNPLACED = 'Nothing found since October 2023 says whether a technology hub runs programmes for startups.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
