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

**A verdict may leave `stage` empty: unplaced** *(CC, 2026-09-24, on the first real unit)*. The
mapped rows are held, but they satisfy no rung: they are not the thing itself, and they are not
the cited absence stage 1 requires. Stage 1 would then assert an absence the base cannot cite,
which is exactly the conflation §3 forbids. An unplaced row carries a `qualifier` saying why and
no `stage_rows`. It is kept in the snapshot so that the finding persists, and it prints as
unassessed. Entering a stage from it or leaving a stage for it is a change like any other and
passes the stability rule.

**Measures stand on a figure, not a row** *(CC, 2026-09-24, at the C3 review)*. Every measure is
due for every unit, because its figure may come from a reference dataset where the base holds
nothing (§4). The figure's `value_source` is dated (`SOURCE_AT`), and a new figure dated inside the
window is what moves a measure. The band is computed from the figure against the cuts in
`lookups/maturity-measures.csv` and caps the stage. A compound anchor may hold the stage below the
band; nothing lifts it above. With no verdict, a measure takes the reference figure
(`reference/measures.csv`, C5) at its band. A primary already standing is not displaced by a
reference, and it carries forward. With no figure at all, the measure is *No evidence*. This
replaces C4's budget exception, which was the first case of it.
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
import maturity_compile  # noqa: E402

CORPUS = HERE.parent
REPORTS = CORPUS / "outputs" / "reports"
RUBRIC = CORPUS / "lookups" / "maturity-rubric.csv"
NORMS = CORPUS / "lookups" / "maturity-norms.csv"
# The measures' specifications, cut from `maturity-rubric.md` (C3): method, direction and cuts.
MEASURES = CORPUS / "lookups" / "maturity-measures.csv"
# The quintile cuts actually taken: one row per measure per cut (the baseline, then each July),
# kept beside the draft-cut measures lookup so that lookup stays the draft's and a past snapshot's
# cuts stay reproducible.
QUINTILES = CORPUS / "lookups" / "maturity-quintiles.csv"
QUINTILE_FIELDS = ("indicator_id", "cut_as_at", "figures", "cuts")
MIN_FIGURES = 15
# The reference figures, one per unit and measure and release, pulled by C5.
REFERENCE = CORPUS / "reference" / "measures.csv"
# The first live snapshot (§7). The two before it are taken retrospectively "with what the base
# holds now about those dates", so they see every reference figure held, whatever its release; a
# live snapshot sees only what was released by its as-at.
LIVE_FROM = dt.date(2026, 9, 30)
# Measures whose stage 5 is its number and nothing else (maturity-rubric.md: 95 % use, 95 % rural
# access, a 0.98 ratio). A figure past it reaches 5 unaided; every other row's stage 5 carries a
# condition that only a drafter can find on record.
NUMERIC_FIVE = {"infra.connect--internet-usage", "infra.energy--rural-electrification",
                "include.divides--bridging-of-digital-divides"}
# How far back a country's own figure still outranks a newer estimate.
SURVEY_YEARS = 5
# A reference figure older than this is not a figure of record, and the measure is No evidence
# (CC, 2026-09-24): Findex 2014 or Libya's 2012 rural access say nothing about the as-at. A
# drafter's cited primary is not held to it; it carries its own year, and that year prints.
MAX_REFERENCE_AGE = 10

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
DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
# A measure's `value_source` (maturity-rubric.md, How to read a measure): a raw/ slug, which
# carries its date at the front, or a Corpus compile or reference with the date after `@`.
SOURCE_AT = re.compile(r"^(?:budgets/[A-Z]{3}/\S+|outputs/non-state-finance/[A-Z]{3}-nonstate\.csv|"
                       r"outputs/datasets/[a-z0-9-]+/[a-z0-9-]+\.csv|"
                       r"ref:[a-z0-9-]+)@(\d{4}-\d{2}-\d{2})$")


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


def measures(as_at: dt.date | None = None) -> dict[str, dict]:
    """{indicator_id: {method, direction, cuts: [float], ...}}; empty until the lookup is cut.

    With an as-at, a quintile row takes the latest cut in `maturity-quintiles.csv` on or before it
    in place of its provisional cuts, and `cut_as_at` says which."""
    if not MEASURES.exists():
        return {}
    out = {}
    for r in read_csv(MEASURES)[1]:
        r = {k: (v or "").strip() for k, v in r.items()}
        r["cuts"] = [float(c) for c in r["cuts"].split("|") if c.strip()]
        r["cut_as_at"] = ""
        out[r["indicator_id"]] = r
    if as_at and QUINTILES.exists():
        for q in sorted(read_csv(QUINTILES)[1], key=lambda q: q["cut_as_at"]):
            if q["indicator_id"] in out and dt.date.fromisoformat(q["cut_as_at"]) <= as_at:
                out[q["indicator_id"]]["cuts"] = [float(c) for c in q["cuts"].split("|")]
                out[q["indicator_id"]]["cut_as_at"] = q["cut_as_at"]
    return out


def band(value: float, spec: dict) -> int:
    """The stage a figure's band allows, at most: 1 plus the cuts it passes.

    `cuts` are the lower bounds of stages 2–5 (the upper bounds for a lower-is-better measure).
    With three cuts, stage 5 is a condition and not a number: the band tops out at 4, and a
    figure in it may reach 5 if the drafter finds the condition on record, so the ceiling is 5.
    """
    cuts = spec["cuts"]
    lower = spec["direction"] == "lower"
    n = sum(1 for c in cuts if (value <= c if lower else value >= c))
    b = 1 + n
    return 5 if len(cuts) == 3 and b == 4 else b


def source_date(value_source: str) -> dt.date | None:
    """The date a measure's figure became known: a slug's own, or the one after `@`."""
    s = value_source.strip()
    m = SOURCE_AT.match(s)
    return dt.date.fromisoformat(m.group(1)) if m else src_date(s)


def reference(unit: str, as_at: dt.date, path: Path | None = None) -> dict[str, dict]:
    """{indicator_id: row}: the reference figure for a unit as at a date.

    **A country's own figure from the last `SURVEY_YEARS` years outranks a newer estimate** *(Bill,
    2026-09-24: not much respect for ITU numbers)*. Most of ITU's series are its own models where no
    survey exists, and the SDG database marks which. A survey two years old says more than a model
    of last year. Otherwise the latest data year up to the as-at's year is taken. From the first
    live snapshot a release after the as-at is invisible, as a later source is to a row; the
    retrospective two see what is held (`LIVE_FROM`)."""
    path = path or REFERENCE
    if not path.exists():
        return {}
    pool: dict[str, list[dict]] = {}
    for r in read_csv(path)[1]:
        if r["iso3"] != unit or not as_at.year - MAX_REFERENCE_AGE <= int(r["year"]) <= as_at.year:
            continue
        if as_at >= LIVE_FROM and dt.date.fromisoformat(r["release"]) > as_at:
            continue
        pool.setdefault(r["indicator_id"], []).append(r)
    best = {}
    for k, rows in pool.items():
        rank = lambda r: (int(r["year"]), r["release"])
        own = [r for r in rows if r.get("nature") != "estimate"
               and int(r["year"]) >= as_at.year - SURVEY_YEARS]
        best[k] = max(own or rows, key=rank)
    return best


def from_reference(r: dict) -> dict:
    """A verdict built from a reference figure alone: the value and its source, stage left to the band."""
    return {"indicator_id": r["indicator_id"], "value": r["value"], "unit": r["unit"],
            "value_year": r["year"], "value_source": f"ref:{r['dataset']}@{r['release']}",
            "qualifier": nature_note(r)}


def nature_note(r: dict) -> str:
    """What kind of figure a reference is, in the words the qualifier prints."""
    return {"estimate": f"on the compiler's modelled estimate ({r['dataset']}), no survey since "
                        f"{int(r['year']) - SURVEY_YEARS}",
            "survey": f"on a survey figure via {r['dataset']}",
            "country": f"on the country's reported figure via {r['dataset']}",
            "tariffs": f"on published tariffs collected by {r['dataset']}",
            "official": f"on official statistics via {r['dataset']}"}.get(
        r.get("nature", ""), f"reference figure ({r['dataset']}); no primary held")


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

    An instrument or a system is due when a mapped row is visible. **A measure is always due.**
    Its evidence is a figure, and the figure may come from a reference dataset where the base holds
    nothing, so there may be no row at all (§4). A measure with no figure anywhere is *No evidence*;
    apply settles that, not this.

    An indicator whose rubric or measure specification is not yet cut cannot be assessed and is not
    due: it goes on `pending` instead. D3's completeness check (R) is what stops a baseline running
    with anything still pending.
    """
    out = {}
    rub, spec = rubric(), measures()
    for ind in indicators_lib.assessed():
        iid = ind["indicator_id"]
        rids = indicators_lib.row_ids(unit_view.get(iid))
        seen = [r for r in rids if r in led and visible(led[r], as_at)]
        measure = ind["kind"] == "measure"
        if not (seen or measure):
            continue
        if len(rub.get(iid, {})) != 5 or measure and iid not in spec:
            if pending is not None:
                pending.append(iid)
            continue
        out[iid] = seen
    return out


# ---------------------------------------------------------------------------------------------
# cut: the Africa quintiles

def quintile_cuts(spec: dict, figures: list[float]) -> list[float] | None:
    """The row's cuts from the figures, or None where fewer than `MIN_FIGURES` hold one.

    Quintiles replace as many cuts as the provisional line has, from the bottom: three cuts put
    the top two quintiles on stage 4, four give the top quintile its own band. A row whose
    provisional line says *for stages 2–4* keeps its stage-5 number, which is the norm's (95 %
    ownership, parity). A lower-is-better row counts its quintiles from the worst end. The
    non-state row is cut over its non-zero figures, and zero stays stage 1 (C3)."""
    if spec["indicator_id"] == "finance.new--mobilisation-of-non-state-finance":
        figures = [f for f in figures if f > 0]
    if len(figures) < MIN_FIGURES:
        return None
    import statistics
    q = statistics.quantiles(figures, n=5, method="inclusive")         # q20, q40, q60, q80
    keep_top = "stages 2–4" in spec.get("cut_note", "") or "stages 2-4" in spec.get("cut_note", "")
    n = 3 if keep_top else len(spec["cuts"])
    new = (q if spec["direction"] == "higher" else q[::-1])[:n]
    cuts = [round(c, 4) for c in new] + (spec["cuts"][3:] if keep_top else [])
    order = cuts if spec["direction"] == "higher" else [-c for c in cuts]
    return cuts if order == sorted(order) else None


def figures_at(as_at: dt.date, verdicts_dir: Path | None, ref_path: Path | None = None,
               units: list[str] | None = None) -> dict[str, dict[str, float]]:
    """{indicator_id: {unit: value}}: the figure each unit carries as at the date, in the order
    the assessment takes it: a drafter's verdict, Corpus's compile, the reference."""
    units = units or sorted(p.name for p in REPORTS.iterdir()
                            if (p / "indicators.csv").exists() and not p.name.startswith("X"))
    out: dict[str, dict[str, float]] = {}
    for u in units:
        mine = {}
        vf = verdicts_dir / f"{u}-{as_at:%Y-%m}.csv" if verdicts_dir else None
        if vf and vf.exists():
            mine = {r["indicator_id"]: r for r in read_csv(vf)[1] if (r.get("value") or "").strip()}
        comp = maturity_compile.compiled(u, as_at, LIVE_FROM)
        ref = reference(u, as_at, ref_path)
        for iid in set(mine) | set(comp) | set(ref):
            src = mine.get(iid) or comp.get(iid) or ref.get(iid)
            try:
                out.setdefault(iid, {})[u] = float(src["value"])
            except (TypeError, ValueError):
                pass
    return out


def cut(as_at: dt.date, verdicts_dir: Path | None, write: bool) -> list[str]:
    if (as_at.month, as_at.day) != (7, 31):
        raise SystemExit("quintiles are cut at the baseline and recut each July: --as-at YYYY-07-31")
    spec = measures()
    figs = figures_at(as_at, verdicts_dir)
    lines, rows = [], []
    for iid, sp in spec.items():
        if sp["method"] != "quintiles":
            continue
        vals = sorted(figs.get(iid, {}).values())
        cuts = quintile_cuts(sp, vals)
        if cuts is None:
            lines.append(f"{iid}: {len(vals)} figure(s); provisional cuts stand "
                         f"({' · '.join(f'{c:g}' for c in sp['cuts'])})")
            continue
        dist = {}
        for v in vals:
            b = band(v, {**sp, "cuts": cuts})
            dist[b] = dist.get(b, 0) + 1
        lines.append(f"{iid}: {len(vals)} figures; cuts {' · '.join(f'{c:g}' for c in cuts)}; "
                     f"bands {dict(sorted(dist.items()))}")
        rows.append({"indicator_id": iid, "cut_as_at": as_at.isoformat(), "figures": len(vals),
                     "cuts": "|".join(f"{c:g}" for c in cuts)})
    if write:
        kept = [r for r in (read_csv(QUINTILES)[1] if QUINTILES.exists() else [])
                if r["cut_as_at"] != as_at.isoformat()]
        with open(QUINTILES, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=QUINTILE_FIELDS, lineterminator="\n")
            w.writeheader()
            w.writerows(sorted(kept + rows, key=lambda r: (r["cut_as_at"], r["indicator_id"])))
    return lines


# ---------------------------------------------------------------------------------------------
# packet

def packet(unit: str, as_at: dt.date, reports: Path = REPORTS, ref_path: Path | None = None) -> str:
    view = indicators_lib.load_unit(str(reports), unit)
    if view is None:
        raise SystemExit(f"{unit}: no indicators.csv — the mapping pass has not reached this unit")
    led = ledger(reports, unit)
    rub, nrm, spec = rubric(), norms(), measures(as_at)
    ref = reference(unit, as_at, ref_path)
    comp = maturity_compile.compiled(unit, as_at, LIVE_FROM)
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
        w(f"\nPrior: {'stage ' + p['stage'] + ' on ' + (p['stage_rows'] or p['value_source']) if p else '—'}\n\n")
        if f["kind"] == "measure":
            sp = spec[iid]
            w(f"Measure: {sp.get('value', '')} ({sp.get('unit', '')}, {sp['direction']} is better). "
              f"Band: {sp['method']}, cuts {' · '.join(f'{c:g}' for c in sp['cuts'])}"
              f"{' (provisional)' if sp.get('provisional') == '1' else ''}. The band is computed from "
              f"the figure and caps the stage.\n\n")
            c = comp.get(iid)
            if c:
                w(f"Corpus's own figure: {c['value']} {c['unit']} ({c['value_year']}; {c['qualifier']}"
                  f"{'; stage ' + c['stage'] + ' by the row' + chr(39) + 's rule' if c.get('stage') else ''})"
                  f" — used if you give no verdict. It outranks any reference.\n\n")
            r = ref.get(iid)
            w(f"Reference figure: {r['value']} {r['unit']} ({r['year']}, {r['dataset']}, released "
              f"{r['release']}; {nature_note(r)}) — used if you give no verdict and the base holds "
              f"no primary.{' **An estimate: look hard for a survey primary in the rows.**' if r.get('nature') == 'estimate' else ''}\n\n"
              if r else "Reference figure: none held. With no primary either, leave it out: No evidence.\n\n")
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
             anchors: dict, spec: dict | None = None) -> list[str]:
    errs = []
    st = (v.get("stage") or "").strip()
    srows = [s.strip() for s in (v.get("stage_rows") or "").split("|") if s.strip()]
    if st == "":
        # Unplaced: the mapped rows are held but satisfy no rung, stage 1's cited absence
        # included. It is said, not left blank by accident, so it has to say why and cite nothing.
        if not (v.get("qualifier") or "").strip():
            errs.append("unplaced (no stage) without a qualifier saying why")
        if srows or any((v.get(k) or "").strip() for k in VALUE_FIELDS):
            errs.append("unplaced (no stage) but cites rows or carries a value")
        return errs
    if st not in {"1", "2", "3", "4", "5"}:
        errs.append(f"stage {st!r} is not 1–5")
    stray = [s for s in srows if s not in rids]
    if stray:
        errs.append(f"stage_rows names rows not mapped or not visible at {as_at}: {', '.join(stray)}")
    # A measure stands on its figure, which may come with no row at all (§4).
    if not srows and kind != "measure":
        errs.append("cites no row in stage_rows")
    vals = {k: (v.get(k) or "").strip() for k in VALUE_FIELDS}
    if kind == "measure":
        errs += measure_errors(vals, st, as_at, spec)
    elif any(vals.values()):
        errs.append(f"a {kind} carries value columns")
    if (v.get("reassessed") or "0").strip() not in ("0", "1"):
        errs.append("reassessed is not 0 or 1")
    return errs


def measure_errors(vals: dict, st: str, as_at: dt.date, spec: dict | None) -> list[str]:
    """A measure's figure, its source's date and its band. Shared with lint-maturity.py check Q."""
    missing = [k for k, x in vals.items() if not x]
    if missing:
        return [f"measure without {', '.join(missing)}"]
    errs = []
    if not re.fullmatch(r"\d{4}", vals["value_year"]) or int(vals["value_year"]) > as_at.year:
        errs.append(f"value_year {vals['value_year']!r} is not a year on or before {as_at.year}")
    d = source_date(vals["value_source"])
    if d is None:
        errs.append(f"value_source {vals['value_source']!r} is not a dated slug, compile or reference")
    elif d > as_at and not (SOURCE_AT.match(vals["value_source"]) and as_at < LIVE_FROM):
        errs.append(f"value_source is dated {d}, after the as-at")
    try:
        value = float(vals["value"])
    except ValueError:
        return errs + [f"value {vals['value']!r} is not a number"]
    if spec and st.isdigit():
        ceiling = band(value, spec)
        if int(st) > ceiling:
            errs.append(f"stage {st} is above the band the figure allows ({ceiling})")
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
    # A measure moves on a new figure: a different source, dated inside the window.
    src = (v.get("value_source") or "").strip()
    d = source_date(src) if src else None
    if src and src != (p.get("value_source") or "").strip() and d and prev_at < d <= as_at:
        v["moved_by"] = src
        return v, "moved (new figure)"
    look = any(LOOKBACK in anchors[int(s)]["anchor"] for s in (p["stage"], stage)
               if s.isdigit() and int(s) in anchors)
    cause = (v.get("cause") or "").strip()
    if look and DATE.match(cause):
        v["moved_by"] = cause
        return v, "moved (look-back)"
    held = {k: p.get(k, "") for k in SNAPSHOT_FIELDS}
    held["moved_by"] = ""
    return held, (f"held at {p['stage'] or 'unplaced'}: verdict {stage or 'unplaced'} has no "
                  f"dated row in the window")


def apply(unit: str, as_at: dt.date, verdicts: Path, replace: bool = False,
          reports: Path = REPORTS, ref_path: Path | None = None,
          compile_fn=maturity_compile.compiled, dry_run: bool = False) -> list[str]:
    view = indicators_lib.load_unit(str(reports), unit)
    if view is None:
        raise Refused(f"{unit}: no indicators.csv")
    led = ledger(reports, unit)
    rub, spec = rubric(), measures(as_at)
    ref = reference(unit, as_at, ref_path)
    comp = compile_fn(unit, as_at, LIVE_FROM)
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
            # A measure verdict that sets a stage by an anchor's condition need not copy the
            # figure: with none given, it stands on Corpus's compile or the reference, and the
            # stage is still held to that figure's band.
            if (frame[iid]["kind"] == "measure" and (v.get("stage") or "").strip()
                    and not any((v.get(k) or "").strip() for k in VALUE_FIELDS)):
                fill = comp.get(iid) or (from_reference(ref[iid]) if iid in ref else None)
                if fill:
                    v = {**v, **{k: fill[k] for k in VALUE_FIELDS},
                         "qualifier": "; ".join(x for x in ((v.get("qualifier") or "").strip(),
                                                           fill["qualifier"]) if x)}
            errs += [f"{iid}: {e}" for e in validate(v, iid, frame[iid]["kind"], need[iid], led,
                                                      as_at, rub.get(iid, {}), spec.get(iid))]
        got[iid] = v
    # An indicator the prior snapshot staged and the drafter left alone carries forward; one that
    # needs its first stage has to have a verdict. A measure is the exception. With no verdict it
    # takes Corpus's own compiled figure, else the reference figure, at its band (4 at most, since
    # a condition-only 5 is a judgement) or at the stage the row's rule computes. Both are
    # recomputed every run. Only a drafter's cited primary carries forward, and it outranks both.
    # With nothing at all, it is No evidence.
    for iid in need:
        primary = iid in prev and not SOURCE_AT.match((prev[iid].get("value_source") or "").strip())
        if iid in got or iid in prev and (primary or frame[iid]["kind"] != "measure"):
            continue
        if frame[iid]["kind"] == "measure":
            auto = dict(comp[iid]) if iid in comp else from_reference(ref[iid]) if iid in ref else None
            if auto:
                ceiling = band(float(auto["value"]), spec[iid])
                top = 5 if iid in NUMERIC_FIVE else 4
                auto["stage"] = str(min(int(auto.get("stage") or top), ceiling, top))
                # A July recut moves a stage with no new figure behind it: that is a rubric
                # change, flagged `reassessed`, never a country's movement (§5).
                if (spec[iid].get("cut_as_at") == as_at.isoformat() and iid in prev
                        and prev[iid].get("stage") != auto["stage"]):
                    auto["reassessed"] = "1"
                # What the script writes for itself passes the drafter's checks too: a failure
                # here is a fault in a compile or the reference, and it stops the run.
                errs += [f"{iid} (from {auto['value_source']}): {e}" for e in measure_errors(
                    {k: str(auto.get(k, "")) for k in VALUE_FIELDS}, auto["stage"], as_at, spec[iid])]
                got[iid] = auto
            elif iid in prev:
                got[iid] = {k: prev[iid].get(k, "") for k in VERDICT_FIELDS}
        elif iid not in prev:
            errs.append(f"{iid}: no verdict and no prior stage")
    for iid in prev:
        if iid not in need:
            errs.append(f"{iid}: staged at {prev_at} but has no row visible at {as_at}")
    if errs:
        raise Refused("\n".join(errs))

    out, notes = [], []
    for iid in [r["indicator_id"] for r in indicators_lib.assessed()]:
        if iid not in need or iid not in got and iid not in prev:
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
    if dry_run:
        # Everything checked, nothing written: how a drafted file is vetted before the cut.
        stages = [r["stage"] or "unplaced" for r in out]
        notes.append("dry run: " + ", ".join(f"{k} {stages.count(k)}" for k in
                                             ("1", "2", "3", "4", "5", "unplaced")))
        return notes

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
    c = sub.add_parser("cut", help="cut the Africa quintiles as at a 31 July")
    c.add_argument("--as-at", required=True)
    c.add_argument("--verdicts-dir", help="the drafted verdicts, {UNIT}-{YYYY-MM}.csv")
    c.add_argument("--write", action="store_true")
    for name in ("packet", "apply"):
        s = sub.add_parser(name)
        s.add_argument("unit")
        s.add_argument("--as-at", required=True)
        if name == "packet":
            s.add_argument("--out")
        else:
            s.add_argument("--verdicts", required=True)
            s.add_argument("--replace", action="store_true")
            s.add_argument("--dry-run", action="store_true", help="check the verdicts, write nothing")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    as_at = month_end(a.as_at)
    if a.cmd == "cut":
        for line in cut(as_at, Path(a.verdicts_dir) if a.verdicts_dir else None, a.write):
            print(line)
        print(f"{'written to' if a.write else 'dry run; --write to record in'} "
              f"lookups/maturity-quintiles.csv")
        return 0
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
        notes = apply(unit, as_at, Path(a.verdicts), a.replace, dry_run=a.dry_run)
    except Refused as e:
        print(f"{unit}: refused\n{e}", file=sys.stderr)
        return 1
    print(f"{unit}: {'verdicts check clean' if a.dry_run else f'snapshot as at {as_at} written'}")
    for n in notes:
        print(f"  {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
