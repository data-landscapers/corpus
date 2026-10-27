#!/usr/bin/env python3
r"""study-ladder-refugees.py — the refugees study's four questions, counted.

    python scripts/study-ladder-refugees.py --as-at 2026-09-30
    python scripts/study-ladder-refugees.py --as-at 2026-09-30 --dry

`maturity/refugees/maturity-study-refugees.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "refugees"
SUB = "displaced"
GAPS = {'4': 'No source found since October 2023 counts refugees or displaced people with a SIM, an account or a digital ID.', '3': 'No source found since October 2023 says refugees or displaced people may use SIM cards, mobile money or digital ID.', '2': 'No source found since October 2023 says: are they registered and documented.', '1': 'No source found since October 2023 says: is registration or digital inclusion under way.', '5': ''}
EMPTY = 'Nothing found says whether refugees or displaced people are registered or can use digital services.'
UNPLACED = 'Nothing found since October 2023 says whether refugees or displaced people are registered or can use digital services.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
