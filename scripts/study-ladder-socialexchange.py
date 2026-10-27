#!/usr/bin/env python3
r"""study-ladder-socialexchange.py — the socialexchange study's four questions, counted.

    python scripts/study-ladder-socialexchange.py --as-at 2026-09-30
    python scripts/study-ladder-socialexchange.py --as-at 2026-09-30 --dry

`maturity/socialexchange/maturity-study-socialexchange.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "socialexchange"
SUB = "exchange"
GAPS = {'4': 'No source found since October 2023 says the registry is linked to the national ID and to another sector.', '3': 'No source found since October 2023 says two or more programmes share one registry.', '2': 'No source found since October 2023 says a registry or programme exchanges data in use.', '1': 'No source found since October 2023 says a link between social protection systems is under way.', '5': ''}
EMPTY = "Nothing found names social protection systems exchanging data, or says there is none."
UNPLACED = "Nothing found since October 2023 names social protection systems exchanging data."

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
