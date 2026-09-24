#!/usr/bin/env python3
r"""
maturity-assess.py — the maturity assessor's two mechanical halves (tasks D1 and D2).

    python scripts/maturity-assess.py packet {UNIT} --as-at 2026-07-31 [--out FILE]
    python scripts/maturity-assess.py apply  {UNIT} --as-at 2026-07-31 --verdicts FILE [--replace]

`documentation/maturity-assessment.md` §6 is the spec. **The stage is a drafter's judgement, and
everything around it is this script's.** The model reads a packet and writes a verdict per
indicator. It does not get to decide which evidence existed on the as-at date, whether a change
of stage is allowed, or what the file looks like. Those are the rules the series rests on, and a
rule the drafter can forget is not a rule.

**packet** writes the brief for one unit and one as-at date. It covers every assessed indicator
that has a mapped ledger row visible on that date, and for each one gives the norm, the five
anchors, the prior snapshot's stage and the mapped rows. A row carries only its sources dated on
or before the as-at date. A row that also has later sources is flagged, because its `status` and
`position_end` then describe a later position than the one being assessed. The indicator's
`summary` prose is left out for the same reason.

**apply** reads the verdicts CSV the drafter wrote and refuses it outright if a rule is broken:
a stage outside 1–5; a verdict on an indicator that is not assessed or has no row visible;
`stage_rows` naming a row outside the mapping or one not yet visible; a measure without all four
value columns, or with `value_year` later than the as-at year; a value on an instrument or a
system; a missing verdict for an indicator that needs one.

It then applies **the stability rule** (§6; task D2) against the prior snapshot, meaning the latest
edition dated before this as-at. A stage may differ from the prior one only if:

- a row in `stage_rows` has a source dated inside the window (prior as-at, as-at]; or
- `reassessed = 1`, meaning a rubric change or a corrected re-read, which is reported apart from
  country movement; or
- an anchor on either stage reads *the 12 months to the as-at date*, and `cause` gives the dated
  event that left the period (the rubric review's exception, 2026-09-23).

Otherwise the prior stage, values and qualifier carry forward whatever the verdict says, and the
run reports the verdict it held back. That is a result, not an error: it is how re-reading drift
is kept out of the series.

apply writes two things. The first is the snapshot, `outputs/reports/{unit}/maturity/{YYYY-MM}.csv`.
It is an edition (`design.md` §9): if the file already exists, the new content must be
byte-identical, which is D2's "assessed twice against the same rows yields identical stages".
`--replace` overrides that for a snapshot not yet published, and only then (task D6). The second
is the stage columns of `outputs/reports/{unit}/indicators.csv`, the current position, and it is
written only when this as-at is the latest snapshot.

**One exception to "a stage needs a mapped row".** The financial-sustainability indicator may
stand on a `budgets/` country-year named in `value_source`, with `row_ids` empty
(`indicator-financial-sustainability.md` §5; C4).
"""
from __future__ import annotations

import argparse
import calendar
import csv
import datetime as dt
import io
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import indicators_lib  # noqa: E402

CORPUS = HERE.parent
REPORTS = CORPUS / "outputs" / "reports"
RUBRIC = CORPUS / "lookups" / "maturity-rubric.csv"
NORMS = CORPUS / "lookups" / "maturity-norms.csv"

# The snapshot's columns, in file order: §6's stage columns plus `stage_rows` (the mapped rows that
# satisfy the anchor, a subset of `row_ids`) and `moved_by`, which apply derives and nobody writes.
# `moved_by` is the dated slug, `reassessed`, or the look-back cause, and it is what the movement
# note (F1) cites.
SNAPSHOT_FIELDS = ("indicator_id",) + indicators_lib.STAGE_FIELDS + ("moved_by",)
# What the drafter writes. `cause` exists only to claim the look-back exception.
VERDICT_FIELDS = ("indicator_id", "stage", "stage_rows", "value", "unit", "value_year",
                  "value_source", "next_milestone", "due", "qualifier", "reassessed", "cause")
VALUE_FIELDS = ("value", "unit", "value_year", "value_source")
LOOKBACK = "12 months to the as-at date"
BUDGET_EXCEPTION = "finance.sustain--financial-sustainability-of-digital-systems"
DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})")


class Refused(Exception):
    pass


# ---------------------------------------------------------------------------------------------
# Reading

def month_end(s: str) -> dt.date:
    d = dt.date.fromisoformat(s)
    if d.day != calendar.monthrange(d.year, d.month)[1]:
        raise SystemExit(f"--as-at {s} is not a month end; a snapshot is taken as at the last day "
                         f"of a month (maturity-assessment.md §7)")
    return d


def src_date(slug: str) -> dt.date | None:
    m = DATE.match(slug.strip())
    return dt.date.fromisoformat(m.group(1)) if m else None


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        r = csv.DictReader(fh)
        return list(r.fieldnames or []), list(r)


def ledger(reports: Path, unit: str) -> dict[str, dict]:
    _, rows = read_csv(reports / unit / "ledger.csv")
    out = {}
    for r in rows:
        srcs = [s.strip() for s in (r.get("sources") or "").split("|") if s.strip()]
        r["_sources"] = [(src_date(s), s) for s in srcs]
        out[r["row_id"].strip()] = r
    return out


def visible(row: dict, as_at: dt.date) -> list[tuple[dt.date, str]]:
    """The row's sources dated on or before the as-at date. Empty means the row did not exist yet."""
    return [(d, s) for d, s in row["_sources"] if d and d <= as_at]


def rubric() -> dict[str, dict[int, dict]]:
    out: dict[str, dict[int, dict]] = {}
    for r in read_csv(RUBRIC)[1]:
        out.setdefault(r["indicator_id"].strip(), {})[int(r["stage"])] = r
    return out


def norms() -> dict[str, dict]:
    return {r["indicator_id"].strip(): r for r in read_csv(NORMS)[1]}


def snapshot_path(reports: Path, unit: str, as_at: dt.date) -> Path:
    return reports / unit / "maturity" / f"{as_at:%Y-%m}.csv"


def prior_snapshot(reports: Path, unit: str, as_at: dt.date) -> tuple[dt.date | None, dict[str, dict]]:
    """The latest edition before this as-at, as (its as-at date, {indicator_id: row})."""
    d = reports / unit / "maturity"
    months = sorted(p.stem for p in d.glob("????-??.csv")) if d.exists() else []
    earlier = [m for m in months if m < f"{as_at:%Y-%m}"]
    if not earlier:
        return None, {}
    m = earlier[-1]
    y, mo = map(int, m.split("-"))
    prev = dt.date(y, mo, calendar.monthrange(y, mo)[1])
    return prev, {r["indicator_id"]: r for r in read_csv(d / f"{m}.csv")[1]}


def due_at(unit_view: dict[str, dict], led: dict[str, dict], as_at: dt.date,
           pending: list | None = None) -> dict[str, list[str]]:
    """{indicator_id: [row_ids visible at the as-at]} for every assessed indicator that needs a verdict.

    An indicator whose rubric is not yet cut cannot be assessed and is not due: it goes on
    `pending` instead. That is what lets a unit run while C3's measures are still drafting. D3's
    completeness check is what stops a baseline running with anything still pending.
    """
    out = {}
    rub = rubric()
    for ind in indicators_lib.assessed():
        iid = ind["indicator_id"]
        rids = indicators_lib.row_ids(unit_view.get(iid))
        seen = [r for r in rids if r in led and visible(led[r], as_at)]
        if not (seen or iid == BUDGET_EXCEPTION and iid in unit_view):
            continue
        if len(rub.get(iid, {})) != 5:
            if pending is not None:
                pending.append(iid)
            continue
        out[iid] = seen
    return out


# ---------------------------------------------------------------------------------------------
# packet

def packet(unit: str, as_at: dt.date, reports: Path = REPORTS) -> str:
    view = indicators_lib.load_unit(str(reports), unit)
    if view is None:
        raise SystemExit(f"{unit}: no indicators.csv — the mapping pass has not reached this unit")
    led = ledger(reports, unit)
    rub, nrm = rubric(), norms()
    prev_at, prev = prior_snapshot(reports, unit, as_at)
    pending: list[str] = []
    need = due_at(view, led, as_at, pending)
    frame = {r["indicator_id"]: r for r in indicators_lib.frame()}
    o = io.StringIO()
    w = o.write
    w(f"# Maturity packet — {unit}, as at {as_at}\n\n")
    w(f"Prior snapshot: {prev_at or 'none (this is the baseline)'}. "
      f"Window: ({prev_at or 'beginning'}, {as_at}]. {len(need)} indicators to assess")
    w(f"; {len(pending)} with evidence but no rubric yet, not assessed.\n\n" if pending else ".\n\n")
    w("Write one verdict row per indicator below, columns: " + ", ".join(VERDICT_FIELDS) + ".\n"
      "Cite in `stage_rows` the rows that satisfy the anchor. Assess only from the sources listed; "
      "a row flagged LATER has status fields that may post-date the as-at.\n\n")
    for iid, rids in need.items():
        f = frame[iid]
        n = nrm.get(iid, {})
        w(f"## {iid}\n\n{f['indicator']} — *{f['kind']}*, {f['chapter']}\n\n")
        if n:
            w(f"Norm: {n.get('instrument')} ({n.get('tier')}), fixes {n.get('fixes')}. "
              f"{n.get('provision')}\n\n")
        anchors = rub.get(iid, {})
        for s in sorted(anchors):
            a = anchors[s]
            w(f"- **{s}** {a['anchor']} *(interpolated: {a['interpolated']})*\n")
        p = prev.get(iid)
        w(f"\nPrior: {'stage ' + p['stage'] + ' on ' + p['stage_rows'] if p else '—'}\n\n")
        if iid == BUDGET_EXCEPTION:
            w(f"Budget exception: may cite `budgets/{unit}/…` in value_source with no row.\n\n")
        for rid in rids:
            r = led[rid]
            vis = visible(r, as_at)
            later = len(r["_sources"]) - len(vis)
            w(f"- `{rid}` — {r['name']} — {r['status']}"
              f"{' — LATER: +' + str(later) + ' source(s) after the as-at' if later else ''}\n")
            if r.get("milestone"):
                w(f"  - milestone: {r['milestone']}\n")
            if r.get("position_end"):
                w(f"  - position: {r['position_end']}\n")
            if r.get("note"):
                w(f"  - note: {r['note']}\n")
            for d, s in vis:
                mark = " ▲ in window" if prev_at and d > prev_at else ""
                w(f"  - {s}{mark}\n")
        w("\n")
    return o.getvalue()


# ---------------------------------------------------------------------------------------------
# apply

def validate(v: dict, iid: str, kind: str, rids: list[str], led: dict, as_at: dt.date,
             anchors: dict) -> list[str]:
    errs = []
    st = (v.get("stage") or "").strip()
    if st not in {"1", "2", "3", "4", "5"}:
        errs.append(f"stage {st!r} is not 1–5")
    srows = [s.strip() for s in (v.get("stage_rows") or "").split("|") if s.strip()]
    stray = [s for s in srows if s not in rids]
    if stray:
        errs.append(f"stage_rows names rows not mapped or not visible at {as_at}: {', '.join(stray)}")
    budget = iid == BUDGET_EXCEPTION and (v.get("value_source") or "").startswith("budgets/")
    if not srows and not budget:
        errs.append("cites no row in stage_rows")
    vals = {k: (v.get(k) or "").strip() for k in VALUE_FIELDS}
    if kind == "measure":
        missing = [k for k, x in vals.items() if not x]
        if missing:
            errs.append(f"measure without {', '.join(missing)}")
        elif not re.fullmatch(r"\d{4}", vals["value_year"]) or int(vals["value_year"]) > as_at.year:
            errs.append(f"value_year {vals['value_year']!r} is not a year on or before {as_at.year}")
    elif any(vals.values()):
        errs.append(f"a {kind} carries value columns")
    if (v.get("reassessed") or "0").strip() not in ("0", "1"):
        errs.append("reassessed is not 0 or 1")
    return errs


def decide(v: dict, p: dict | None, prev_at: dt.date | None, as_at: dt.date, led: dict,
           anchors: dict) -> tuple[dict, str]:
    """The stability rule. Returns (the row to write, a note: '' / 'moved' / 'held …')."""
    stage = v["stage"].strip()
    if not p or p["stage"] == stage:
        return v, ""
    if (v.get("reassessed") or "0").strip() == "1":
        v["moved_by"] = "reassessed"
        return v, "reassessed"
    srows = [s.strip() for s in v["stage_rows"].split("|") if s.strip()]
    hits = sorted({s for rid in srows for d, s in led[rid]["_sources"]
                   if d and prev_at < d <= as_at})
    if hits:
        v["moved_by"] = hits[-1]
        return v, "moved"
    look = any(LOOKBACK in anchors[int(s)]["anchor"] for s in (p["stage"], stage) if int(s) in anchors)
    cause = (v.get("cause") or "").strip()
    if look and DATE.match(cause):
        v["moved_by"] = cause
        return v, "moved (look-back)"
    held = {k: p.get(k, "") for k in SNAPSHOT_FIELDS}
    held["moved_by"] = ""
    return held, f"held at {p['stage']}: verdict {stage} has no dated row in the window"


def apply(unit: str, as_at: dt.date, verdicts: Path, replace: bool = False,
          reports: Path = REPORTS) -> list[str]:
    view = indicators_lib.load_unit(str(reports), unit)
    if view is None:
        raise Refused(f"{unit}: no indicators.csv")
    led = ledger(reports, unit)
    rub = rubric()
    frame = {r["indicator_id"]: r for r in indicators_lib.frame()}
    pending: list[str] = []
    need = due_at(view, led, as_at, pending)
    prev_at, prev = prior_snapshot(reports, unit, as_at)
    _, vrows = read_csv(verdicts)
    got: dict[str, dict] = {}
    errs = []
    for v in vrows:
        iid = (v.get("indicator_id") or "").strip()
        if not iid:
            continue
        if iid in got:
            errs.append(f"{iid}: two verdicts")
        elif iid not in frame or not frame[iid]["assessed"]:
            errs.append(f"{iid}: not an assessed indicator")
        elif iid in pending:
            errs.append(f"{iid}: has no five-row rubric yet")
        elif iid not in need:
            errs.append(f"{iid}: no mapped row is visible at {as_at}, so it is No evidence")
        else:
            errs += [f"{iid}: {e}" for e in validate(v, iid, frame[iid]["kind"], need[iid], led,
                                                      as_at, rub.get(iid, {}))]
        got[iid] = v
    # An indicator the prior snapshot staged and the drafter left alone carries forward; one that
    # needs its first stage has to have a verdict.
    for iid in need:
        if iid not in got and iid not in prev:
            errs.append(f"{iid}: no verdict and no prior stage")
    for iid in prev:
        if iid not in need:
            errs.append(f"{iid}: staged at {prev_at} but has no row visible at {as_at}")
    if errs:
        raise Refused("\n".join(errs))

    out, notes = [], []
    for iid in [r["indicator_id"] for r in indicators_lib.assessed()]:
        if iid not in need:
            continue
        if iid in got:
            v = {k: (got[iid].get(k) or "").strip() for k in VERDICT_FIELDS}
            v["reassessed"] = v["reassessed"] or "0"
            row, note = decide(v, prev.get(iid), prev_at, as_at, led, rub.get(iid, {}))
        else:
            row, note = dict(prev[iid]), ""
            row["moved_by"] = ""
        row["assessed_on"] = as_at.isoformat()
        if note:
            notes.append(f"{iid}: {note}" + (f" ({row['moved_by']})" if row.get("moved_by") else ""))
        out.append({k: row.get(k, "") for k in SNAPSHOT_FIELDS})
    if pending:
        notes.append(f"{len(pending)} indicator(s) with evidence have no rubric yet and were not "
                     f"assessed")

    path = snapshot_path(reports, unit, as_at)
    body = io.StringIO()
    w = csv.DictWriter(body, fieldnames=SNAPSHOT_FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(out)
    text = body.getvalue()
    if path.exists() and not replace:
        with open(path, encoding="utf-8", newline="") as fh:
            if fh.read() != text:
                raise Refused(f"{path.relative_to(reports.parent.parent)} exists and this run "
                              f"differs from it; an edition is not revised (--replace only before "
                              f"it is published)")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)

    latest = max(p.stem for p in path.parent.glob("????-??.csv"))
    if latest == f"{as_at:%Y-%m}":
        write_current(reports, unit, {r["indicator_id"]: r for r in out})
    return notes


def write_current(reports: Path, unit: str, staged: dict[str, dict]) -> None:
    """The stage columns of indicators.csv, set to this snapshot. Every other column is kept as it is."""
    path = Path(indicators_lib.unit_path(str(reports), unit))
    with open(path, encoding="utf-8-sig", newline="") as fh:
        raw = fh.read()
    eol = "\r\n" if "\r\n" in raw else "\n"
    rdr = csv.DictReader(io.StringIO(raw))
    fields = list(rdr.fieldnames or [])
    rows = list(rdr)
    cols = list(indicators_lib.STAGE_FIELDS)
    fields += [c for c in cols if c not in fields]
    for r in rows:
        s = staged.get((r.get("indicator_id") or "").strip())
        for c in cols:
            r[c] = s.get(c, "") if s else ""
    body = io.StringIO()
    w = csv.DictWriter(body, fieldnames=fields, lineterminator=eol)
    w.writeheader()
    w.writerows(rows)
    if body.getvalue() != raw:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(body.getvalue())


# ---------------------------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("packet", "apply"):
        s = sub.add_parser(name)
        s.add_argument("unit")
        s.add_argument("--as-at", required=True)
        if name == "packet":
            s.add_argument("--out")
        else:
            s.add_argument("--verdicts", required=True)
            s.add_argument("--replace", action="store_true")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    as_at = month_end(a.as_at)
    unit = a.unit.upper()
    if a.cmd == "packet":
        text = packet(unit, as_at)
        if a.out:
            Path(a.out).write_text(text, encoding="utf-8")
            print(f"{unit}: packet as at {as_at} → {a.out}")
        else:
            sys.stdout.write(text)
        return 0
    try:
        notes = apply(unit, as_at, Path(a.verdicts), a.replace)
    except Refused as e:
        print(f"{unit}: refused\n{e}", file=sys.stderr)
        return 1
    print(f"{unit}: snapshot as at {as_at} written")
    for n in notes:
        print(f"  {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
