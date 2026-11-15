#!/usr/bin/env python3
r"""study-ladder-startups.py — the startups study's four questions, counted.

    python scripts/study-ladder-startups.py --as-at 2026-09-30
    python scripts/study-ladder-startups.py --as-at 2026-09-30 --dry

`maturity/startups/maturity-study-startups.md` §2 and §3, counted by `study_first_ladder.py`.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "startups"
SUB = "startuppolicy"
GAPS = {'4': 'No source found since October 2023 says a public fund under the startup law or strategy has financed startups.', '3': 'No source found since October 2023 says startups are labelled or registered under a startup law or strategy.', '2': 'No source found since October 2023 says: is a startup law or strategy adopted.', '1': 'No source found since October 2023 says: is a startup law or strategy being prepared.', '5': ''}
EMPTY = 'Nothing found says what the state does for tech startups.'
UNPLACED = 'Nothing found since October 2023 says whether a startup law or strategy is prepared or adopted.'



def stage(study: dict, rows: list[dict], as_at: dt.date, gaps: dict, empty: str, unplaced: str) -> dict:
    """Stage 1 needs no startup law, strategy *or public support* (§3): a source saying only that no
    act exists does not place a country whose evidence holds a public fund backing startups
    (housekeeping 73: South Africa's DSTI Innovation Fund, ZAF-001, beside Business Day's ZAF-003)."""
    cell = study_first_ladder.stage(study, rows, as_at, gaps, empty, unplaced)
    if cell["stage"] == "1" and any(
            r["aspect"] == "funded" and r.get("as_of") and r.get("class") != "other"
            and study_first_ladder.held(study, r, as_at) for r in rows):
        return {"stage": "unplaced", "sources": [], "gaps": unplaced}
    return cell


if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED, stager=stage))
