#!/usr/bin/env python3
r"""study-ladder-civilregister.py — the civilregister study's four questions, counted.

    python scripts/study-ladder-civilregister.py --as-at 2026-09-30
    python scripts/study-ladder-civilregister.py --as-at 2026-09-30 --dry

`maturity/civilregister/maturity-study-civilregister.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "civilregister"
SUB = "civil"
GAPS = {'4': 'No source found since October 2023 puts birth registration at 90% or more.', '3': 'No source found since October 2023 says deaths are registered in the digital system.', '2': 'No source found since October 2023 says: are births registered digitally across the country.', '1': 'No source found since October 2023 says: is digital civil registration under way.', '5': ''}
EMPTY = 'Nothing found says how births and deaths are registered.'
UNPLACED = 'Nothing found since October 2023 says whether births are registered digitally.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
