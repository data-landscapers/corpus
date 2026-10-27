#!/usr/bin/env python3
r"""study-ladder-authentication.py — the authentication study's four questions, counted.

    python scripts/study-ladder-authentication.py --as-at 2026-09-30
    python scripts/study-ladder-authentication.py --as-at 2026-09-30 --dry

`maturity/authentication/maturity-study-authentication.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "authentication"
SUB = "authentication"
GAPS = {'4': 'No source found since October 2023 says a mobile ID, ID wallet or signed credential is in service.', '3': 'No source found since October 2023 says authentication is used across services or channels.', '2': 'No source found since October 2023 says: is one in service.', '1': 'No source found since October 2023 says: is an authentication service under way.', '5': ''}
EMPTY = 'Nothing found names a digital authentication service, or says there is none.'
UNPLACED = 'Nothing found since October 2023 names a digital authentication service.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
