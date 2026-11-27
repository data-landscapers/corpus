#!/usr/bin/env python3
r"""study-ladder-aisectoral.py — the aisectoral study's four questions, counted.

    python scripts/study-ladder-aisectoral.py --as-at 2026-09-30
    python scripts/study-ladder-aisectoral.py --as-at 2026-09-30 --dry

`maturity/aisectoral/maturity-study-aisectoral.md` §2 and §3, counted by `study_first_ladder.py`.
**Sectors are counted across sources** *(Bill, 2026-11-27, message 170)*: question 3 is a yes where
the in-service rows in the window, and any `several` row, name two or more sectors between them,
and stage 5 also needs three or more. A row's sector is read from its text, so it is named in
`SECTOR`; a row not in it counts no sector (`--dry` names it). Tax and customs are two sectors,
even under one authority; one system shared by several bodies is one (Togo's DMI, Côte d'Ivoire's
joint reporting).

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_first_ladder  # noqa: E402

STUDY = "aisectoral"
SUB = "sectorai"
GAPS = {'4': 'No source found since October 2023 reports measured results of a sectoral AI system.', '3': 'No source found since October 2023 says AI is in service in the public systems of two or more sectors.', '2': 'No source found since October 2023 says: is one in service.', '1': 'No source found since October 2023 says: is a sectoral ai tool under way.', '5': ''}
EMPTY = "Nothing found says whether a public sector's system uses AI."
UNPLACED = "Nothing found since October 2023 says whether an AI tool is in service in a public sector's system."

SECTOR = {
    "AGO-002": "tax", "AGO-004": "tax", "AGO-006": "tax", "AGO-007": "customs", "AGO-008": "tax",
    "AGO-010": "mining;environment", "AGO-011": "mining;environment;agriculture",
    "BEN-005": "customs", "BFA-002": "health", "BWA-004": "health", "CAF-002": "health",
    "CIV-001": "tax", "CIV-002": "agriculture", "CIV-003": "health", "CIV-008": "tax",
    "CMR-001": "education", "CMR-002": "social protection", "CMR-003": "social protection",
    "CMR-005": "climate",
    "COD-001": "education", "COD-003": "education", "COD-005": "education", "COD-007": "education",
    "COD-008": "health", "COD-011": "health", "CPV-001": "health",
    "DJI-001": "climate", "DJI-002": "transport", "DJI-003": "transport",
    "DZA-005": "trade", "DZA-007": "education", "DZA-009": "customs",
    "EGY-001": "justice", "EGY-003": "agriculture", "EGY-006": "customs", "EGY-007": "health",
    "EGY-009": "social protection", "EGY-010": "agriculture", "EGY-011": "justice",
    "EGY-016": "agriculture", "EGY-018": "agriculture", "EGY-019": "health;land", "EGY-020": "tax",
    "EGY-021": "tax", "ERI-002": "health",
    "ETH-003": "customs", "ETH-006": "customs", "ETH-007": "health", "ETH-012": "agriculture",
    "ETH-015": "health", "ETH-017": "justice;public administration;health",
    "GHA-002": "tax", "GHA-003": "customs", "GHA-004": "customs", "GHA-007": "health",
    "GHA-009": "health", "GHA-011": "health", "GHA-013": "agriculture;health",
    "GMB-001": "tax", "GMB-002": "education",
    "KEN-003": "tax", "KEN-004": "health", "KEN-006": "health", "KEN-008": "health",
    "KEN-009": "health", "KEN-011": "education", "KEN-012": "education;agriculture;health",
    "LBR-002": "health", "LBR-003": "health", "LSO-002": "health", "LSO-005": "health",
    "MAR-005": "health", "MAR-006": "education", "MAR-008": "customs", "MAR-012": "customs",
    "MAR-013": "customs;tax", "MAR-014": "agriculture", "MAR-015": "agriculture",
    "MDG-001": "customs", "MDG-004": "customs", "MDG-005": "customs", "MDG-008": "customs",
    "MRT-001": "climate", "MRT-002": "climate", "MUS-003": "water",
    "MWI-003": "agriculture", "MWI-004": "tax", "MWI-006": "health",
    "NAM-005": "health", "NAM-006": "education", "NER-002": "agriculture",
    "NGA-001": "customs", "NGA-002": "customs", "NGA-003": "social protection", "NGA-009": "customs",
    "RWA-006": "health", "RWA-007": "health", "SEN-002": "tax", "SEN-006": "health",
    "SLE-001": "health", "SOM-001": "climate", "SOM-002": "climate",
    "SSD-001": "health", "SSD-002": "health",
    "SWZ-002": "health", "SWZ-004": "health", "SWZ-006": "health", "SYC-004": "customs",
    "TGO-002": "tax", "TGO-004": "tax", "TGO-006": "social protection", "TGO-008": "tax",
    "TZA-001": "health", "TZA-004": "tax", "TZA-006": "health", "TZA-007": "health",
    "TZA-009": "procurement",
    "UGA-002": "health", "UGA-005": "tax", "UGA-007": "justice", "UGA-009": "customs",
    "UGA-010": "customs;climate",
    "ZAF-001": "tax", "ZAF-002": "tax", "ZAF-004": "tax", "ZAF-007": "tax", "ZAF-009": "tax",
    "ZMB-003": "tax",
    "ZWE-001": "police", "ZWE-006": "health", "ZWE-007": "police",
    "ZWE-009": "",   # FAO names no operating body, so no public sector is shown
}


def stage(study: dict, rows: list[dict], as_at: dt.date, gaps: dict, empty: str, unplaced: str) -> dict:
    """Question 3 from the sectors the window's rows name between them; stage 5 needs three."""
    k1, k2, k3, v2, v3 = study_first_ladder.keys(study)
    top = study_first_ladder.firsts(study)[0]
    three = study_first_ladder.study_lib.months_back(as_at, 36)
    live = sorted(((study_first_ladder.seen(study, r), r) for r in rows
                   if r.get("as_of") and r.get("class") != "other"
                   and study_first_ladder.held(study, r, as_at)), key=lambda p: p[0], reverse=True)
    first: dict[str, dict] = {}   # each sector's newest row
    for d, r in live:
        if (r["aspect"], r["value"]) in ((k1, top), (k2, v2)) and (d >= three or r.get("carried")):
            if r["row_id"] not in SECTOR:
                print(f"study-ladder-aisectoral: {r['row_id']} names no sector in SECTOR")
            for s in filter(None, SECTOR.get(r["row_id"], "").split(";")):
                first.setdefault(s, r)
    base = [r for r in rows if r["aspect"] != k2]
    if len(first) >= 2:
        base += [{**r, "aspect": k2, "value": v2}
                 for r in {r["row_id"]: r for r in first.values()}.values()]
    if len(first) < 3:
        base = [r for r in base if r["aspect"] != k3]
    return study_first_ladder.stage(study, base, as_at, gaps, empty, unplaced)


if __name__ == "__main__":
    sys.exit(study_first_ladder.run(STUDY, SUB, GAPS, EMPTY, UNPLACED, stager=stage))
