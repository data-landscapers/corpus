#!/usr/bin/env python3
r"""study-ladder-startups.py — the startups study's four questions, counted.

    python scripts/study-ladder-startups.py --as-at 2026-09-30
    python scripts/study-ladder-startups.py --as-at 2026-09-30 --dry

`maturity/startups/maturity-study-startups.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "startups"
SUB = "startuppolicy"
GAPS = {'4': 'No source found since October 2023 says a public fund under the startup law or strategy has financed startups.', '3': 'No source found since October 2023 says startups are labelled or registered under a startup law or strategy.', '2': 'No source found since October 2023 says: is a startup law or strategy adopted.', '1': 'No source found since October 2023 says: is a startup law or strategy being prepared.', '5': ''}
EMPTY = 'Nothing found says what the state does for tech startups.'
UNPLACED = 'Nothing found since October 2023 says whether a startup law or strategy is prepared or adopted.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
