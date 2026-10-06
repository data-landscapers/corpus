#!/usr/bin/env python3
r"""study-profile.py — each country's profile from its evidence, and the draw for the agreement check.

    python scripts/study-profile.py health                    # every profile.csv
    python scripts/study-profile.py health --as-at 2026-09-30
    python scripts/study-profile.py health --draw 20           # method §7 step 4: the cells
    python scripts/study-profile.py health --score             # ...and the count that agree

`maturity/documentation/maturity-study-method.md` §4, §5 and §7. A drafter writes
`evidence.csv`, one row per stated fact; **what the facts add up to is arithmetic, so a script
does it**, and does it the same way for 54 countries.

`maturity/{id}/evidence/{ISO3}/profile.csv` holds one row per sub-indicator and aspect:

- `value`   — the newest fact's. Where the aspect has facets, the newest per facet; where it
  is `multi`, every value stated inside the window; where it names a `prefer` order (a share
  over a count over *not published*), the best-ranked kind first and the newest of that.
- `sources` — the `row_id`s that carry that value.
- `others`  — the rows that say something else. The newest stands and both are kept.
- `gap`     — what is not established: nothing held, or nothing dated inside the window. A
  coverage aspect's window is three years; a qualifier's is its own. **A gap is what Phase 1
  searches for**, so this column is the search list.

An invalid `evidence.csv` is reported and its country is not profiled: a profile built over
a value outside the closed list would carry it into a stage.

**The agreement check draws from the staged cells only.** `--draw N` writes
`maturity/{id}/agreement.csv` with an empty `second_stage` for the second drafter, who stages
blind from `evidence.csv`; `--score` counts the cells where the two agree and exits 1 below
the method's 16 in 20, pro rata for another N.

Exit: 0 clean, 1 invalid evidence or agreement below the bar, 2 the study cannot be read.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402

AGREEMENT_FIELDS = ["iso3", "indicator_id", "second_stage"]
AGREE_BAR = 0.8    # 16 of 20


def _rank(aspect: dict, value: str) -> int:
    for i, prefix in enumerate(aspect.get("prefer", ())):
        if value.startswith(prefix):
            return i
    return len(aspect.get("prefer", ()))


def profile_cell(aspect: dict, rows: list[dict], as_at: dt.date) -> dict:
    """One aspect of one sub-indicator, from its evidence rows."""
    window = aspect.get("window_months", study_lib.COVERAGE_WINDOW_MONTHS)
    cutoff = study_lib.months_back(as_at, window)
    dated = sorted(((study_lib.parse_as_of(r["as_of"]), r) for r in rows),
                   key=lambda p: p[0], reverse=True)
    if not dated:
        return {"value": "", "as_of": "", "sources": "", "others": "", "gap": "nothing held"}
    inside = [p for p in dated if p[0] >= cutoff]
    gap = "" if inside else f"nothing dated since {cutoff.isoformat()}"

    if "facets" in aspect:
        chosen = {}
        for _, r in dated:
            for part in r["value"].split(";"):
                chosen.setdefault(part.split(":")[0].strip(), (part.strip(), r))
        picked = [chosen[f] for f in aspect["facets"] if f in chosen]
        missing = [f for f in aspect["facets"] if f not in chosen]
        if missing and not gap:
            gap = "not stated: " + ", ".join(missing)
        value = ";".join(v for v, _ in picked)
        winners = {r["row_id"] for _, r in picked}
    elif aspect.get("multi"):
        pool = inside or dated[:1]
        seen = []
        for _, r in pool:
            seen += [v.strip() for v in r["value"].split(";") if v.strip() not in seen]
        order = aspect["values"] if isinstance(aspect.get("values"), list) else seen
        value = ";".join(sorted(seen, key=lambda v: order.index(v) if v in order else 99))
        winners = {r["row_id"] for _, r in pool}
    else:
        best = min(dated, key=lambda p: (_rank(aspect, p[1]["value"]), -p[0].toordinal()))[1]
        value = best["value"]
        winners = {r["row_id"] for _, r in dated if r["value"] == value}
        picked = [(value, best)]

    newest = max(d for d, r in dated if r["row_id"] in winners)
    as_of = next(r["as_of"] for d, r in dated if r["row_id"] in winners and d == newest)
    others = [f"{r['row_id']}={r['value']}" for _, r in dated if r["row_id"] not in winners]
    return {"value": value, "as_of": as_of, "sources": ";".join(sorted(winners)),
            "others": ";".join(others), "gap": gap}


def profile(study: dict, iso: str, rows: list[dict], as_at: dt.date) -> list[dict]:
    out = []
    for sub in study["sub_indicators"]:
        for aspect in study["aspects"]:
            mine = [r for r in rows
                    if r["sub_indicator"] == sub["key"] and r["aspect"] == aspect["key"]]
            cell = profile_cell(aspect, mine, as_at)
            out.append({"iso3": iso, "sub_indicator": sub["key"], "aspect": aspect["key"],
                        "role": aspect["role"], **cell})
    return out


def draw(cells: list[tuple[str, str]], n: int, seed: int) -> list[tuple[str, str]]:
    """`n` cells, or all of them where fewer are staged. Seeded, so the draw can be shown."""
    cells = sorted(cells)
    return sorted(random.Random(seed).sample(cells, min(n, len(cells))))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Profiles from evidence; the agreement draw.")
    ap.add_argument("study")
    ap.add_argument("--as-at", help="YYYY-MM-DD; default today")
    ap.add_argument("--draw", type=int, metavar="N", help="draw N staged cells for a second drafter")
    ap.add_argument("--seed", type=int, help="the draw's seed; default the as-at's ordinal")
    ap.add_argument("--score", action="store_true", help="count agreement in agreement.csv")
    a = ap.parse_args(argv)

    try:
        study = study_lib.load(a.study)
    except study_lib.StudyError as e:
        print(f"study-profile: {e}")
        return 2
    as_at = dt.date.fromisoformat(a.as_at) if a.as_at else dt.date.today()
    agreement = os.path.join(study_lib.study_dir(a.study), "agreement.csv")
    assessment = study_lib.read_csv(os.path.join(study_lib.out_dir(a.study), "assessment.csv"))

    if a.draw:
        staged = [(r["iso3"], r["indicator_id"]) for r in assessment if r["stage"].isdigit()]
        if not staged:
            print("study-profile: assessment.csv holds no staged cell to draw from.")
            return 2
        seed = a.seed if a.seed is not None else as_at.toordinal()
        picked = draw(staged, a.draw, seed)
        study_lib.write_csv(agreement, AGREEMENT_FIELDS,
                            [{"iso3": i, "indicator_id": c, "second_stage": ""} for i, c in picked])
        print(f"study-profile: drew {len(picked)} of {len(staged)} staged cells, seed {seed}, "
              f"to {os.path.relpath(agreement, study_lib.CORPUS)}.")
        return 0

    if a.score:
        first = {(r["iso3"], r["indicator_id"]): r["stage"] for r in assessment}
        rows = study_lib.read_csv(agreement)
        blank = [r for r in rows if not r["second_stage"].strip()]
        if not rows or blank:
            print(f"study-profile: agreement.csv has {len(blank)} of {len(rows)} cells unstaged.")
            return 2
        split = [r for r in rows if first.get((r["iso3"], r["indicator_id"])) != r["second_stage"].strip()]
        for r in split:
            print(f"  {r['iso3']} {r['indicator_id']}: first "
                  f"{first.get((r['iso3'], r['indicator_id']))}, second {r['second_stage']}")
        agree = len(rows) - len(split)
        ok = agree >= AGREE_BAR * len(rows)
        print(f"study-profile: {agree} of {len(rows)} cells agree - "
              + ("the ladder holds." if ok else "below the bar: rewrite the rung that split "
                                                "them and restage every country."))
        return 0 if ok else 1

    bad = 0
    base = os.path.join(study_lib.study_dir(a.study), "evidence")
    for iso, rows in study_lib.evidence(a.study).items():
        problems = study_lib.evidence_problems(study, iso, rows)
        if problems:
            bad += 1
            for p in problems:
                print(f"study-profile: FAIL - {p}")
            continue
        out = profile(study, iso, rows, as_at)
        study_lib.write_csv(os.path.join(base, iso, "profile.csv"), study_lib.PROFILE_FIELDS, out)
        print(f"  {iso}  {len(rows):3d} facts  {sum(1 for r in out if r['gap']):2d} gaps")
    print(f"study-profile: {a.study} as at {as_at.isoformat()} - "
          + (f"{bad} country file(s) invalid and not profiled." if bad else "profiles written."))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
