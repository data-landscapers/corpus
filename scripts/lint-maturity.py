#!/usr/bin/env python3
r"""
lint-maturity.py — the maturity assessment's checks (task D3; `maturity-assessment.md` §11).

    python scripts/lint-maturity.py                 every unit, and the estate checks
    python scripts/lint-maturity.py --unit STP      one unit's checks only
    python scripts/lint-maturity.py --estate        the estate checks only

**It re-verifies what `maturity-assess.py apply` enforces, from the files alone.** apply refuses
a bad verdict at write time. These checks read the editions and `indicators.csv` as they stand,
so a hand edit, a stray merge or a copy from somewhere else is caught the same way. A checker that
trusted the writer would only be checking the writer's intentions. The rules are imported from
`maturity-assess.py`, not restated, for the reason `report-lint.py`'s `load()` gives.

Letters continue the report sequence (A–F `report-lint.py`, G I J L M `report-render.py`).
The unit checks also run under `report-render.py --check`.

  N  stage domain      every stage is 1–5 on an assessed indicator, and every row it cites is in
                       the ledger with a source on or before the snapshot's as-at
  O  stability         a stage that differs from the prior edition's is moved by a source dated
                       in the window on a cited row, by `reassessed`, or by a dated look-back cause
  P  citation          every stage cites a row, stage 1 included (budget measure: value_source)
  Q  measure values    a measure carries value, unit, value_year <= as-at year, value_source;
                       an instrument or a system carries none
  S  current position  indicators.csv's stage columns equal the latest edition's
  R  lookups (estate)  every assessed indicator has one norms row and five rubric rows
  T  frame count       no frame count (117, 121, 123) as a number in any script's logic

Some §11 checks are not here yet, because they check outputs that do not exist yet: no count
crossing kinds, published counts matching the lookups, and status/assessment agreement. They
arrive with the renderers (F1, F3, F4).

Exit 1 if any check fails.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import datetime as dt
import importlib.util
import io
import re
import sys
import tokenize
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import indicators_lib  # noqa: E402

_spec = importlib.util.spec_from_file_location("ma", HERE / "maturity-assess.py")
ma = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ma)

FRAME_COUNTS = {"117", "121", "123"}


def editions(reports: Path, unit: str) -> list[tuple[dt.date, dict[str, dict]]]:
    d = reports / unit / "maturity"
    out = []
    for p in sorted(d.glob("????-??.csv")) if d.exists() else []:
        y, m = map(int, p.stem.split("-"))
        at = dt.date(y, m, calendar.monthrange(y, m)[1])
        out.append((at, {r["indicator_id"]: r for r in ma.read_csv(p)[1]}))
    return out


def split(s: str | None) -> list[str]:
    return [x.strip() for x in (s or "").split("|") if x.strip()]


def unit_checks(unit: str, reports: Path = ma.REPORTS) -> dict[str, list[str]]:
    """{letter: [problem, ...]} for one unit. An empty dict means the unit has no snapshot yet."""
    eds = editions(reports, unit)
    if not eds:
        return {}
    frame = {r["indicator_id"]: r for r in indicators_lib.frame()}
    led = ma.ledger(reports, unit)
    rub = ma.rubric()
    bad: dict[str, list[str]] = {k: [] for k in "NOPQS"}
    prev_at, prev = None, {}
    for at, snap in eds:
        tag = f"{at:%Y-%m}"
        for iid, r in snap.items():
            f = frame.get(iid)
            st = (r.get("stage") or "").strip()
            if not f or not f["assessed"]:
                bad["N"].append(f"{tag} {iid}: staged but not an assessed indicator")
                continue
            if st not in {"1", "2", "3", "4", "5"}:
                bad["N"].append(f"{tag} {iid}: stage {st!r}")
            rows = split(r.get("stage_rows"))
            for rid in rows:
                if rid not in led:
                    bad["N"].append(f"{tag} {iid}: cites {rid}, not in the ledger")
                elif not ma.visible(led[rid], at):
                    bad["N"].append(f"{tag} {iid}: cites {rid}, which has no source by {at}")
            budget = iid == ma.BUDGET_EXCEPTION and (r.get("value_source") or "").startswith("budgets/")
            if not rows and not budget:
                bad["P"].append(f"{tag} {iid}: stage {st} cites no row")
            vals = [(r.get(k) or "").strip() for k in ma.VALUE_FIELDS]
            if f["kind"] == "measure":
                if not all(vals):
                    bad["Q"].append(f"{tag} {iid}: measure missing a value column")
                elif not re.fullmatch(r"\d{4}", vals[2]) or int(vals[2]) > at.year:
                    bad["Q"].append(f"{tag} {iid}: value_year {vals[2]!r} after {at.year}")
            elif any(vals):
                bad["Q"].append(f"{tag} {iid}: a {f['kind']} carries value columns")
            p = prev.get(iid)
            if p and p.get("stage") != st:
                why = (r.get("moved_by") or "").strip()
                ok = False
                if why == "reassessed":
                    ok = (r.get("reassessed") or "").strip() == "1"
                elif why:
                    d = ma.src_date(why)
                    in_window = d is not None and prev_at < d <= at
                    on_row = any(why == s for rid in rows if rid in led for _, s in led[rid]["_sources"])
                    anchors = rub.get(iid, {})
                    look = any(ma.LOOKBACK in anchors.get(int(s), {}).get("anchor", "")
                               for s in (p["stage"], st) if s.isdigit())
                    ok = in_window and (on_row or look)
                if not ok:
                    bad["O"].append(f"{tag} {iid}: {p['stage']} -> {st} with nothing dated in "
                                    f"({prev_at}, {at}] behind it (moved_by {why!r})")
        prev_at, prev = at, snap
    latest = eds[-1][1]
    view = indicators_lib.load_unit(str(reports), unit) or {}
    for iid in sorted(set(view) | set(latest)):
        cur = view.get(iid, {})
        want = latest.get(iid, {})
        diff = [c for c in indicators_lib.STAGE_FIELDS
                if (cur.get(c) or "").strip() != (want.get(c) or "").strip()]
        if diff:
            bad["S"].append(f"{iid}: indicators.csv differs from {eds[-1][0]:%Y-%m} in "
                            f"{', '.join(diff)}")
    return bad


def check_lookups() -> list[str]:
    """R: every assessed indicator has one norms row and five rubric rows."""
    norms = {}
    for r in ma.read_csv(ma.NORMS)[1]:
        norms[r["indicator_id"].strip()] = norms.get(r["indicator_id"].strip(), 0) + 1
    rub = ma.rubric()
    bad = []
    for f in indicators_lib.assessed():
        iid = f["indicator_id"]
        if norms.get(iid) != 1:
            bad.append(f"{iid}: {norms.get(iid, 0)} norms row(s)")
        if sorted(rub.get(iid, {})) != [1, 2, 3, 4, 5]:
            bad.append(f"{iid} ({f['kind']}): rubric stages {sorted(rub.get(iid, {})) or 'none'}")
    return bad


def check_frame_count(scripts: Path = HERE) -> list[str]:
    """T: a frame count written as a number in code. Comments and docstrings are prose, and are
    B3's grep's business; this looks only at NUMBER tokens, which is where a count breaks logic."""
    bad = []
    for p in sorted(scripts.glob("*.py")):
        if p.name.startswith("test_") or p.name == Path(__file__).name:
            continue
        try:
            toks = tokenize.generate_tokens(io.StringIO(p.read_text(encoding="utf-8")).readline)
            for t in toks:
                if t.type == tokenize.NUMBER and t.string in FRAME_COUNTS:
                    bad.append(f"{p.name}:{t.start[0]}: {t.string}")
        except (tokenize.TokenError, SyntaxError, UnicodeDecodeError):
            continue
    return bad


TITLE = {"N": "stage domain", "O": "stability", "P": "citation", "Q": "measure values",
         "S": "current position", "R": "lookups", "T": "frame count"}


def report(letter: str, problems: list[str], scope: str = "") -> int:
    head = f"check {letter} ({TITLE[letter]}){' ' + scope if scope else ''}"
    print(f"{head}: {'PASS' if not problems else 'FAIL — ' + str(len(problems)) + ' problem(s)'}")
    for p in problems[:20]:
        print(f"     {p}")
    if len(problems) > 20:
        print(f"     … and {len(problems) - 20} more")
    return 1 if problems else 0


def check_unit(unit: str, reports: Path = ma.REPORTS) -> int:
    """The unit checks, printed in the house form; called by `report-render.py --check`."""
    res = unit_checks(unit, reports)
    if not res:
        print("check N-S (maturity): SKIP — no snapshot for this unit yet")
        return 0
    return max(report(k, res[k]) for k in "NOPQS")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--unit")
    ap.add_argument("--estate", action="store_true")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    rc = 0
    if a.unit:
        return check_unit(a.unit.upper())
    if not a.estate:
        units = sorted(p.parent.parent.name for p in ma.REPORTS.glob("*/maturity/????-??.csv"))
        for u in sorted(set(units)):
            res = unit_checks(u)
            fails = {k: v for k, v in res.items() if v}
            print(f"{u}: {'PASS' if not fails else 'FAIL ' + ''.join(sorted(fails))}")
            for k in sorted(fails):
                rc |= report(k, fails[k], u)
        if not units:
            print("check N-S (maturity): no unit has a snapshot yet")
    rc |= report("R", check_lookups())
    rc |= report("T", check_frame_count())
    return rc


if __name__ == "__main__":
    sys.exit(main())
