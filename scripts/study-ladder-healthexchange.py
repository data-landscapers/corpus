#!/usr/bin/env python3
r"""study-ladder-healthexchange.py — the healthexchange study's four questions, counted.

    python scripts/study-ladder-healthexchange.py --as-at 2026-09-30
    python scripts/study-ladder-healthexchange.py --as-at 2026-09-30 --dry

`maturity/healthexchange/maturity-study-healthexchange.md` §2 and §3, counted by `study_first_ladder.py`.
**A national exchange in service is taken to link three or more systems** *(Bill, 2026-11-09,
message 81)*: that is read from the text of an `exchange` fact, so a row that is one is named in
`NATIONAL` (housekeeping 73) and answers question 3 as well as question 2.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "healthexchange"
SUB = "exchange"
GAPS = {'4': 'No source found since October 2023 says patient records are linked through the national ID or a national health identifier.', '3': 'No source found since October 2023 says three or more health systems exchange data, or a national exchange is in service.', '2': 'No source found since October 2023 says two health systems exchange data in routine use.', '1': 'No source found since October 2023 says an exchange between health systems is under way.', '5': ''}
EMPTY = "Nothing found names health systems exchanging data, or says there is none."
UNPLACED = "Nothing found since October 2023 names health systems exchanging data."
NATIONAL = {"GNB-001", "SLE-001", "UGA-003"}   # a national exchange or warehouse in service (message 81)


def stage(study: dict, rows: list[dict], as_at: dt.date, gaps: dict, empty: str, unplaced: str) -> dict:
    extra = [{**r, "aspect": "breadth", "value": "wide"} for r in rows
             if r["row_id"] in NATIONAL and (r["aspect"], r["value"]) == ("exchange", "inservice")]
    return study_first_ladder.stage(study, rows + extra, as_at, gaps, empty, unplaced)


if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED, stager=stage))
