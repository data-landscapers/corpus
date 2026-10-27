#!/usr/bin/env python3
r"""study-ladder-addressregister.py — the addressregister study's four questions, counted.

    python scripts/study-ladder-addressregister.py --as-at 2026-09-30
    python scripts/study-ladder-addressregister.py --as-at 2026-09-30 --dry

`maturity/addressregister/maturity-study-addressregister.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "addressregister"
SUB = "address"
GAPS = {'4': 'No source found since October 2023 says other services use the address system.', '3': 'No source found since October 2023 says the addressing system covers the whole country.', '2': 'No source found since October 2023 says: is an address register or digital addressing system in service.', '1': 'No source found since October 2023 says: is an addressing system under way.', '5': ''}
EMPTY = 'Nothing found names an addressing system, or says there is none.'
UNPLACED = 'Nothing found since October 2023 says whether an addressing system is under way or in service.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
