#!/usr/bin/env python3
r"""study-assess.py — a study's assessment.csv, assembled from each country's stage.json.

    python scripts/study-assess.py health --as-at 2026-09-30
    python scripts/study-assess.py health --as-at 2026-09-30 --dry

`maturity/documentation/maturity-study-method.md` §7 step 3. A stager writes one
`maturity/{id}/evidence/{ISO3}/stage.json` to `maturity/documentation/stager-brief.md`; this
folds the 54 into `outputs/maturity/{id}/assessment.csv`, one row per country per
sub-indicator, in the columns `lint-study.py` sets.

**It checks what it folds and writes nothing while a cell is wrong**: a missing file or
cell, a value off an aspect's closed list, a stage off the scale, a source row that is not
the country's own on that sub-indicator, a cell with no stage and no reason, and the cap
rule. The same tests are `lint-study.py`'s, run here so a bad cell goes back to its stager
and not into the file.

`short` is the writing step's (§8): a writer leaves `short.json` beside `stage.json`, to
`maturity/documentation/writer-brief.md`, and its line is folded in here. Without one, the
summary is carried over from an existing assessment.csv where the cell's stage has not
moved; a restaged cell loses its summary.

`--as-at` is the study's; a cell `study-update.py log` has stamped keeps its own, later one.

`systems.csv`, the typology, is each country's `evidence/{ISO3}/systems.csv` set end to end.

Exit: 0 written, 1 a cell is wrong, 2 the study cannot be read.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study_lib  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "lint_study", os.path.join(os.path.dirname(os.path.abspath(__file__)), "lint-study.py"))
lint_study = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lint_study)


def cells(study: dict, iso: str, doc: dict, evidence: list[dict], as_at: str,
          shorts: dict, written: dict | None = None) -> tuple[list[dict], list[str]]:
    """`(assessment rows, problems)` for one country's stage.json."""
    asp = study_lib.aspects(study)
    by_sub = {c.get("sub_indicator"): c for c in doc.get("cells") or []}
    excluded = study_lib.excluded(study)
    rows, problems = [], []
    for sub in study["sub_indicators"]:
        key, where = sub["key"], f"{iso} {sub['key']}"
        c = by_sub.get(key)
        if c is None:
            problems.append(f"{where}: no cell in stage.json")
            continue
        stage = str(c.get("stage", "")).strip()
        staged = stage.isdigit() and int(stage) in study_lib.STAGES
        if not staged and stage not in study_lib.NOT_STAGED:
            problems.append(f"{where}: stage `{stage}` is not 1 to 5, `unplaced` or `no evidence`")
            continue
        # A cell reassessed since the study carries its own as-at (`study-update.py log`).
        row = {"iso3": iso, "indicator_id": sub["indicator_id"],
               "as_at": str(c.get("as_at") or as_at), "stage": stage}
        for a in study["aspects"]:
            v = str(c.get(a["key"], "") or "").strip()
            bad = study_lib.value_problem(asp[a["key"]], key, v) if v else ""
            if bad:
                problems.append(f"{where}: {a['key']}: {bad}")
            row[a["key"]] = v
        for k in ("cap", "flags", "stage_sources", "gaps"):
            row[k] = str(c.get(k, "") or "").strip()
        was = shorts.get((iso, sub["indicator_id"]), {})
        row["short"] = " ".join(str((written or {}).get(key, "") or "").split()) or (
            was.get("short", "") if was.get("stage") == stage else "")
        for f in lint_study._flags(row):
            if f not in study["flags"]:
                problems.append(f"{where}: flag `{f}` is not one of {study['flags']}")
        mine = {e["row_id"] for e in evidence
                if e["sub_indicator"] == key and e["source_slug"] not in excluded}
        named = [s.strip() for s in row["stage_sources"].split(";") if s.strip()]
        if staged and not named:
            problems.append(f"{where}: stage {stage} with no `stage_sources`")
        for rid in named:
            if rid not in mine:
                problems.append(f"{where}: stage_sources names `{rid}`, not a {key} row of its "
                                f"evidence.csv, or one from an excluded source")
        if not staged and not row["gaps"]:
            problems.append(f"{where}: {stage} with no reason in `gaps`")
        bad = lint_study.cap_problem(study, row)
        if bad:
            problems.append(f"{where}: {bad}")
        rows.append(row)
    return rows, problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="assessment.csv from each country's stage.json.")
    ap.add_argument("study")
    ap.add_argument("--as-at", required=True, help="YYYY-MM-DD, the study's as-at")
    ap.add_argument("--dry", action="store_true", help="check, write nothing")
    a = ap.parse_args(argv)
    try:
        study = study_lib.load(a.study)
    except study_lib.StudyError as e:
        print(f"study-assess: {e}")
        return 2

    base = os.path.join(study_lib.study_dir(a.study), "evidence")
    out = os.path.join(study_lib.CORPUS, "outputs", "maturity", a.study, "assessment.csv")
    shorts = {(r["iso3"], r["indicator_id"]): r for r in study_lib.read_csv(out)}
    rows, problems, systems = [], [], []
    for iso in sorted(study_lib.countries()):
        path = os.path.join(base, iso, "stage.json")
        try:
            with open(path, encoding="utf-8") as fh:
                doc = json.load(fh)
        except (OSError, ValueError) as e:
            problems.append(f"{iso}: stage.json not readable ({e})")
            continue
        try:
            with open(os.path.join(base, iso, "short.json"), encoding="utf-8") as fh:
                written = json.load(fh)
        except OSError:
            written = None
        except ValueError as e:
            problems.append(f"{iso}: short.json not readable ({e})")
            written = None
        got, bad = cells(study, iso, doc, study_lib.read_csv(os.path.join(base, iso, "evidence.csv")),
                         a.as_at, shorts, written)
        rows += got
        problems += bad
        systems += study_lib.read_csv(os.path.join(base, iso, "systems.csv"))

    for p in problems:
        print(f"  {p}")
    if problems:
        print(f"study-assess: {a.study} - {len(problems)} problem(s); nothing written.")
        return 1
    fields = lint_study.assessment_fields(study)
    if not a.dry:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        study_lib.write_csv(out, fields, rows)
        study_lib.write_csv(os.path.join(os.path.dirname(out), "systems.csv"),
                            study_lib.SYSTEMS_FIELDS, systems)
    for sub in study["sub_indicators"]:
        mine = [r["stage"] for r in rows if r["indicator_id"] == sub["indicator_id"]]
        tally = ", ".join(f"{s} {mine.count(s)}" for s in ["5", "4", "3", "2", "1", *study_lib.NOT_STAGED])
        print(f"  {sub['label']}: {tally}")
    print(f"study-assess: {a.study} as at {a.as_at} - {len(rows)} cells"
          + (" (dry run, nothing written)." if a.dry else " written."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
