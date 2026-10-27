#!/usr/bin/env python3
r"""study-ladder-aigovernment.py — the aigovernment study's four questions, counted.

    python scripts/study-ladder-aigovernment.py --as-at 2026-09-30
    python scripts/study-ladder-aigovernment.py --as-at 2026-09-30 --dry

`maturity/aigovernment/maturity-study-aigovernment.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "aigovernment"
SUB = "govai"
GAPS = {'4': 'No source found since October 2023 says the government has issued rules or a register for its own use of AI.', '3': 'No source found since October 2023 says AI is in service in two or more government bodies.', '2': 'No source found since October 2023 says: is an ai system in service in administration.', '1': 'No source found since October 2023 says: is ai in administration under way.', '5': ''}
EMPTY = 'Nothing found says whether government bodies use AI.'
UNPLACED = 'Nothing found since October 2023 says whether a government body uses an AI system.'

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
