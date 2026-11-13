#!/usr/bin/env python3
r"""study-ladder-socialregistry.py — the socialregistry study's five questions, counted.

    python scripts/study-ladder-socialregistry.py --as-at 2026-09-30
    python scripts/study-ladder-socialregistry.py --as-at 2026-09-30 --dry

`maturity/socialregistry/maturity-study-socialregistry.md` §2 and §3. **Ruling 106** *(Bill,
2026-11-09)*: stage 4 is a registry in service that two or more programmes use **or** that is
linked to the national ID; stage 5 is linked **and** paying benefits digitally. The `linked`
aspect holds `linked`, `checked` and `paid`, several joined by `;`: `checked` (an ID check at
enrolment) answers nothing, `paid` answers question 5. The shared counter in
`study_first_ladder.py` reads one value per aspect and set 5 on a link alone (housekeeping 64),
so this study stages with its own function and the shared runner.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder as sfl  # noqa: E402
import study_lib  # noqa: E402

STUDY = "socialregistry"
SUB = "social"
GAPS = {'5': '', '4': 'No source found since October 2023 says a programme that selects from the social registry pays benefits digitally, or that the registry is linked to the national ID.', '3': 'No source found since October 2023 says two or more programmes use the social registry, or that it is linked to the national ID.', '2': 'No source found since October 2023 says: is a social registry in service.', '1': 'No source found since October 2023 says: is a social registry under way.'}
EMPTY = 'Nothing found names a social registry, or says there is none.'
UNPLACED = 'Nothing found since October 2023 says whether a social registry is under way or in service.'


def stage(study: dict, rows: list[dict], as_at: dt.date, gaps: dict, empty: str, unplaced: str) -> dict:
    if not rows:
        return {"stage": "no evidence", "sources": [], "gaps": empty}
    three = study_lib.months_back(as_at, 36)
    live = sorted(((sfl.seen(study, r), r) for r in rows if r.get("as_of") and sfl.held(study, r, as_at)),
                  key=lambda p: p[0], reverse=True)

    def pick(aspect: str, token: str) -> list[str]:
        return [r["row_id"] for d, r in live if (d >= three or r.get("carried")) and r["aspect"] == aspect
                and token in {t.strip() for t in r["value"].split(";")}]
    inservice, underway, none = pick("registry", "inservice"), pick("registry", "underway"), pick("registry", "none")
    several, linked, paid = pick("programmes", "several"), pick("linked", "linked"), pick("linked", "paid")
    aspects = {"programmes": "several" if several else "",
               "linked": ";".join(v for v, ok in (("linked", linked), ("paid", paid)) if ok)}
    # Each rung is shown by its own rows (message 114); in service answers under way, being one aspect.
    if inservice and linked and paid:
        n, src = "5", linked + paid
    elif inservice and (several or linked):
        n, src = "4", several + linked
    elif inservice:
        n, src = "3", inservice
    elif underway:
        n, src = "2", underway
    elif none:
        n, src = "1", none
    else:
        return {"stage": "unplaced", "sources": [], "gaps": unplaced}
    if n in ("1", "2"):
        aspects = {"programmes": "", "linked": ""}
    return {"stage": n, "sources": list(dict.fromkeys(src))[:3], "gaps": gaps[n], "aspects": aspects}


if __name__ == "__main__":
    sys.exit(sfl.run(STUDY, SUB, GAPS, EMPTY, UNPLACED, stager=stage))
