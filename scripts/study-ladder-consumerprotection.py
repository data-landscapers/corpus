#!/usr/bin/env python3
r"""study-ladder-consumerprotection.py — the consumerprotection study's four questions, counted.

    python scripts/study-ladder-consumerprotection.py --as-at 2026-09-30
    python scripts/study-ladder-consumerprotection.py --as-at 2026-09-30 --dry

`maturity/consumerprotection/maturity-study-consumerprotection.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "consumerprotection"
SUB = "protection"
GAPS = {'4': 'No source found since October 2023 reports a fine, sanction or complaint figures.', '3': 'No source found since October 2023 says a financial ombudsman or complaints unit takes complaints.', '2': 'No source found since October 2023 says: are such rules in force.', '1': 'No source found since October 2023 says: are consumer rules for digital finance being drafted.', '5': ''}
EMPTY = 'Nothing found says whether consumer-protection rules apply to digital finance.'
UNPLACED = 'Nothing found since October 2023 says whether consumer-protection rules apply to digital finance.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
