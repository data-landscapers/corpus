#!/usr/bin/env python3
r"""study-ladder-landregister.py — the landregister study's four questions, counted.

    python scripts/study-ladder-landregister.py --as-at 2026-09-30
    python scripts/study-ladder-landregister.py --as-at 2026-09-30 --dry

`maturity/landregister/maturity-study-landregister.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "landregister"
SUB = "land"
GAPS = {'4': 'No source found since October 2023 says land can be searched or registered online.', '3': 'No source found since October 2023 says the digital land register covers the whole country.', '2': 'No source found since October 2023 says: is a digital land register in service.', '1': 'No source found since October 2023 says: is digital land registration under way.', '5': ''}
EMPTY = 'Nothing found says how land rights are recorded.'
UNPLACED = 'Nothing found since October 2023 says whether land rights are registered digitally.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
