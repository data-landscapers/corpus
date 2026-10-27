#!/usr/bin/env python3
r"""study-ladder-digitalsovereignty.py — the digitalsovereignty study's four questions, counted.

    python scripts/study-ladder-digitalsovereignty.py --as-at 2026-09-30
    python scripts/study-ladder-digitalsovereignty.py --as-at 2026-09-30 --dry

`maturity/digitalsovereignty/maturity-study-digitalsovereignty.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "digitalsovereignty"
SUB = "sovereignty"
GAPS = {'4': 'No source found since October 2023 says a government contract carries terms on data jurisdiction, portability or exit.', '3': 'No source found since October 2023 says government data or a core system is hosted in a national data centre or cloud.', '2': 'No source found since October 2023 says: is a rule on state data in force.', '1': 'No source found since October 2023 says: is control of state data a stated goal.', '5': ''}
EMPTY = 'Nothing found says whether the state keeps its data and systems under its own control.'
UNPLACED = 'Nothing found since October 2023 says whether control of state data is a stated goal or a rule.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
