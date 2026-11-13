#!/usr/bin/env python3
r"""study-ladder-idrobustness.py — the idrobustness study's four questions, counted.

    python scripts/study-ladder-idrobustness.py --as-at 2026-09-30
    python scripts/study-ladder-idrobustness.py --as-at 2026-09-30 --dry

`maturity/idrobustness/maturity-study-idrobustness.md` §2 and §3, counted by `study_first_ladder.py`.
**Rung 5 needs the whole population** *(Bill, 2026-11-09, message 108)*: question 5 has no aspect
and is read from the text of the `system` facts, so a fact that answers it is named by row in
`WHOLE` (housekeeping 73: none yet), and a certified ID without one stops at 4 on its other rows.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "idrobustness"
SUB = "robustness"
GAPS = {'4': 'No source found since October 2023 reports a certification, audit or assurance level for the system.', '3': 'No source found since October 2023 says the system checks people by biometrics.', '2': 'No source found since October 2023 says: is it in service.', '1': 'No source found since October 2023 says: is a national id system under way.', '5': ''}
EMPTY = 'Nothing found names a national ID system, or says there is none.'
UNPLACED = 'Nothing found since October 2023 says whether a national ID system is under way or in service.'
WHOLE: set[str] = set()   # `system` rows showing the ID held by all or nearly all (question 5)


def stage(study: dict, rows: list[dict], as_at: dt.date, gaps: dict, empty: str, unplaced: str) -> dict:
    cell = study_first_ladder.stage(study, rows, as_at, gaps, empty, unplaced)
    if cell["stage"] == "5" and not any(r["row_id"] in WHOLE for r in rows):
        # a yes to 4 without a yes to 5 answers no earlier question (message 108)
        cell = study_first_ladder.stage(study, [r for r in rows if r["aspect"] != "assurance"],
                                        as_at, gaps, empty, unplaced)
    return cell


if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED, stager=stage))
