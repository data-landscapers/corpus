#!/usr/bin/env python3
r"""study-ladder-aisectoral.py — the aisectoral study's four questions, counted.

    python scripts/study-ladder-aisectoral.py --as-at 2026-09-30
    python scripts/study-ladder-aisectoral.py --as-at 2026-09-30 --dry

`maturity/aisectoral/maturity-study-aisectoral.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "aisectoral"
SUB = "sectorai"
GAPS = {'4': 'No source found since October 2023 reports measured results of a sectoral AI system.', '3': 'No source found since October 2023 says AI is in service in the public systems of two or more sectors.', '2': 'No source found since October 2023 says: is one in service.', '1': 'No source found since October 2023 says: is a sectoral ai tool under way.', '5': ''}
EMPTY = "Nothing found says whether a public sector's system uses AI."
UNPLACED = "Nothing found since October 2023 says whether an AI tool is in service in a public sector's system."

if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED))
