#!/usr/bin/env python3
r"""study-ladder-retailpayments.py — the retailpayments study's four questions, counted.

    python scripts/study-ladder-retailpayments.py --as-at 2026-09-30
    python scripts/study-ladder-retailpayments.py --as-at 2026-09-30 --dry

`maturity/retailpayments/maturity-study-retailpayments.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "retailpayments"
SUB = "retail"
GAPS = {'4': 'No source found since October 2023 says a national switch connects wallets and bank accounts.', '3': 'No source found since October 2023 says payments between providers, or between wallets and banks, are in service.', '2': 'No source found since October 2023 says: are people paying by mobile money or e-money.', '1': 'No source found since October 2023 says: is a mobile money service starting.', '5': ''}
EMPTY = 'Nothing found names a mobile money service, or says there is none.'
UNPLACED = 'Nothing found since October 2023 says whether mobile money is in service.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
