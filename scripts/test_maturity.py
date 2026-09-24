#!/usr/bin/env python3
r"""test_maturity.py — the maturity assessment's checks (task D3), starting with the rubric.

    python scripts/test_maturity.py

Each rule in `lint-maturity-rubric.py` is exercised on a fixture frame of four indicators in two
chapters, so a failure here names the rule and not the state of the live lookups.
"""
from __future__ import annotations

import csv
import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("lr", HERE / "lint-maturity-rubric.py")
lr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lr)

fails: list[str] = []


def check(label, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
    if not ok:
        print(f"          got  {got!r}\n          want {want!r}")
        fails.append(label)


FRAME = [
    {"indicator_id": "gov.policy--a", "chapter": "Governance", "kind": "instrument"},
    {"indicator_id": "gov.policy--b", "chapter": "Governance", "kind": "instrument"},
    {"indicator_id": "gov.policy--e", "chapter": "Governance", "kind": "measure"},
    {"indicator_id": "infra.connect--c", "chapter": "ICT Infrastructure", "kind": "measure"},
    {"indicator_id": "digital.rural--d", "chapter": "Digitalisation", "kind": "system"},
]
NORMS = [
    {"indicator_id": "gov.policy--a", "tier": "AU", "instrument": "DTS", "fixes": "top"},
    {"indicator_id": "gov.policy--b", "tier": "AU", "instrument": "DPF", "fixes": "rungs"},
    {"indicator_id": "infra.connect--c", "tier": "AU", "instrument": "STYIP",
     "fixes": "target (80 % / 2033)"},
    {"indicator_id": "digital.rural--d", "tier": "corpus", "instrument": "(none)", "fixes": "—"},
]
TOP = ["yes", "yes", "yes", "yes", "no"]
RUNGS = ["yes", "no", "no", "yes", "no"]


def rows(iid, interp, anchor="a mapped row shows X"):
    return [{"indicator_id": iid, "stage": str(s), "anchor": anchor, "interpolated": v}
            for s, v in zip(range(1, 6), interp)]


def write(d: Path, rubric_rows, header=lr.COLUMNS):
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "rubric.csv", "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(header), extrasaction="ignore")
        w.writeheader()
        w.writerows(rubric_rows)
    with open(d / "norms.csv", "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["indicator_id", "tier", "instrument", "fixes"])
        w.writeheader()
        w.writerows(NORMS)


def run(d: Path, **kw):
    return lr.check(str(d / "rubric.csv"), str(d / "norms.csv"), frame=FRAME, **kw)


def has(msgs, text):
    return any(text in m for m in msgs)


tmp = Path(tempfile.mkdtemp(prefix="maturity-test-"))
try:
    print("a clean chapter")
    d = tmp / "clean"
    write(d, rows("gov.policy--a", TOP) + rows("gov.policy--b", RUNGS))
    f, w, st = run(d)
    check("passes", f, [])
    check("no warnings", w, [])
    check("counts interpolated rungs", st["interpolated"], 6)
    check("an undrafted kind is pending, not failed — gov.policy--e is a measure",
          st["chapters"], {"Governance instruments": 2})
    f, _, _ = run(d, complete=True)
    check("but --complete wants every indicator",
          has(f, "infra.connect--c has no rubric rows"), True)

    print("\nstructure")
    d = tmp / "hdr"
    write(d, rows("gov.policy--a", TOP), header=("indicator_id", "stage", "anchor"))
    check("a wrong header fails first", has(run(d)[0], "header is"), True)
    d = tmp / "part"
    write(d, rows("gov.policy--a", TOP))
    check("a chapter drafted in part fails",
          has(run(d)[0], "Governance instruments drafted in part"), True)
    d = tmp / "four"
    write(d, rows("gov.policy--a", TOP)[:4] + rows("gov.policy--b", RUNGS))
    check("a missing stage fails", has(run(d)[0], "stage(s) [5] missing"), True)
    d = tmp / "dup"
    write(d, rows("gov.policy--a", TOP) + rows("gov.policy--a", TOP)[:1]
          + rows("gov.policy--b", RUNGS))
    check("a repeated stage fails", has(run(d)[0], "stage 1 is already"), True)
    d = tmp / "six"
    r = rows("gov.policy--a", TOP) + rows("gov.policy--b", RUNGS)
    r[0]["stage"] = "6"
    write(d, r)
    check("a stage outside 1-5 fails", has(run(d)[0], "is not 1-5"), True)
    d = tmp / "alien"
    write(d, rows("gov.policy--zzz", TOP))
    check("an id outside the assessed frame fails", has(run(d)[0], "not an assessed"), True)
    d = tmp / "blank"
    r = rows("gov.policy--a", TOP) + rows("gov.policy--b", RUNGS)
    r[2]["anchor"] = " "
    write(d, r)
    check("an empty anchor fails", has(run(d)[0], "has no anchor"), True)
    d = tmp / "interp"
    r = rows("gov.policy--a", TOP) + rows("gov.policy--b", RUNGS)
    r[1]["interpolated"] = "maybe"
    write(d, r)
    check("an interpolated cell not yes/no/partly fails", has(run(d)[0], "does not open"), True)

    print("\nthe fixes rules")
    d = tmp / "topyes"
    write(d, rows("gov.policy--a", ["yes"] * 5) + rows("gov.policy--b", RUNGS))
    f, _, _ = run(d)
    check("top: stage 5 interpolated fails", has(f, "stage 5 is not interpolated"), True)
    check("and all-yes on a norm-anchored row fails", has(f, "every rung interpolated"), True)
    d = tmp / "toplow"
    write(d, rows("gov.policy--a", ["yes", "no", "yes", "yes", "no"])
          + rows("gov.policy--b", RUNGS))
    check("top only, a lower rung claimed: warning",
          has(run(d)[1], "is top only, yet stage(s) [2]"), True)
    d = tmp / "rungsthin"
    write(d, rows("gov.policy--a", TOP) + rows("gov.policy--b", TOP))
    check("rungs with one stated stage: warning", has(run(d)[1], "supplies rungs"), True)
    d = tmp / "target"
    write(d, rows("infra.connect--c", ["yes", "yes", "yes", "yes", "yes"]))
    check("target with stages 4 and 5 interpolated fails",
          has(run(d)[0], "states a target"), True)
    write(d, rows("infra.connect--c", ["yes", "yes", "yes", "no", "partly"]))
    check("target stated at stage 4 passes", run(d)[0], [])
    d = tmp / "corpus"
    write(d, rows("digital.rural--d", ["yes", "yes", "no", "yes", "yes"]))
    check("Corpus-defined with a rung claimed fails", has(run(d)[0], "Corpus-defined"), True)
    write(d, rows("digital.rural--d", ["yes"] * 5))
    check("Corpus-defined all interpolated passes", run(d)[0], [])

    print("\nwording")
    d = tmp / "vague"
    write(d, rows("gov.policy--a", TOP, anchor="An adequate strategy") + rows("gov.policy--b", RUNGS))
    check("a judgement word warns", has(run(d)[1], "leans on 'adequate'"), True)

    print("\nexit codes")
    check("no rubric exits 2", lr.main(["--rubric", str(tmp / "none.csv")]), 2)
finally:
    shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------------------------
# The assessor (D1) and the as-at and stability rules (D2), on a fixture unit over the real frame.
# The rubric is a fixture too, so the cases do not move when a chapter is re-cut.

_spec = importlib.util.spec_from_file_location("ma", HERE / "maturity-assess.py")
ma = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ma)
import datetime as dt  # noqa: E402
import indicators_lib as il  # noqa: E402

STRAT = "gov.policy--digital-transformation-strategy"          # instrument
TALK = "gov.discourse--open-discussion-of-government-policy"   # instrument, look-back anchors
MEAS = "finance.new--development-partner-project-financing"    # measure
FIX_RUBRIC = {iid: {s: {"anchor": f"stage {s} anchor", "interpolated": "yes"} for s in range(1, 6)}
              for iid in (STRAT, TALK, MEAS)}
FIX_RUBRIC[TALK][2]["anchor"] = "restrictions on record in the 12 months to the as-at date"
ma.rubric = lambda: FIX_RUBRIC
# The measure bands on fixed cuts 5 / 10 / 20 (US$m, higher is better), stage 5 a condition.
FIX_SPEC = {MEAS: {"indicator_id": MEAS, "method": "fixed", "direction": "higher",
                   "cuts": [5.0, 10.0, 20.0], "provisional": "0", "value": "", "unit": "US$m"}}
ma.measures = lambda: FIX_SPEC
JUL, AUG = dt.date(2026, 7, 31), dt.date(2026, 8, 31)
LEDGER = [
    ("XXX-gov.policy-strategy", "2026-05-01-strategy-drafted"),
    ("XXX-gov.policy-strategy-2", "2026-08-10-strategy-adopted"),
    ("XXX-gov.discourse-shutdown", "2025-08-15-shutdown"),
    ("XXX-finance.new-dp", "2026-06-01-dp-figures"),
    ("XXX-gov.policy-late", "2026-09-02-late-source"),
]
MAPPING = {STRAT: "XXX-gov.policy-strategy|XXX-gov.policy-strategy-2|XXX-gov.policy-late",
           TALK: "XXX-gov.discourse-shutdown", MEAS: "XXX-finance.new-dp"}


def unit_dir(root: Path) -> Path:
    u = root / "XXX"
    u.mkdir(parents=True)
    with open(u / "ledger.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\r\n")
        w.writerow(["row_id", "name", "status", "milestone", "position_end", "note", "sources"])
        for rid, src in LEDGER:
            w.writerow([rid, rid, "Implemented", "", "", "", src])
    with open(u / "indicators.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["indicator_id", "progress", "summary", "developments", "row_ids"])
        for iid, rids in MAPPING.items():
            w.writerow([iid, "No change", "s", "d", rids])
    return u


def verdicts(root: Path, name: str, rows: list[dict]) -> Path:
    p = root / f"{name}.csv"
    with open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=ma.VERDICT_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in ma.VERDICT_FIELDS})
    return p


def v(iid, stage, rows, **kw):
    return {"indicator_id": iid, "stage": str(stage), "stage_rows": rows, **kw}


MEAS_VALUE = dict(value="12.5", unit="US$m", value_year="2025", value_source="2026-06-01-dp-figures")
BASE = [v(STRAT, 2, "XXX-gov.policy-strategy"), v(TALK, 2, "XXX-gov.discourse-shutdown"),
        v(MEAS, 2, "XXX-finance.new-dp", **MEAS_VALUE)]


def refused(root, as_at, rows, name):
    try:
        ma.apply("XXX", as_at, verdicts(root, name, rows), reports=root)
    except ma.Refused as e:
        return str(e)
    return ""


def snap(root, as_at):
    with open(ma.snapshot_path(root, "XXX", as_at), encoding="utf-8", newline="") as fh:
        return {r["indicator_id"]: r for r in csv.DictReader(fh)}


tmp = Path(tempfile.mkdtemp(prefix="maturity-assess-test-"))
try:
    print("\nthe assessor: the baseline")
    unit_dir(tmp)
    need = ma.due_at(il.load_unit(str(tmp), "XXX"), ma.ledger(tmp, "XXX"), JUL)
    check("a row whose every source post-dates the as-at is not visible",
          need[STRAT], ["XXX-gov.policy-strategy"])
    pk = ma.packet("XXX", JUL, reports=tmp)
    check("the packet leaves out sources after the as-at", "2026-08-10" in pk, False)
    ma.apply("XXX", JUL, verdicts(tmp, "jul", BASE), reports=tmp)
    s = snap(tmp, JUL)
    check("the snapshot stages every indicator with a visible row", sorted(s), sorted(MAPPING))
    view = il.load_unit(str(tmp), "XXX")
    check("indicators.csv round-trips through load_unit with the stage", view[STRAT]["stage"], "2")
    check("and keeps the mapping's own columns", view[STRAT]["progress"], "No change")
    check("assessed_on is the as-at", view[MEAS]["assessed_on"], "2026-07-31")
    before = ma.snapshot_path(tmp, "XXX", JUL).read_bytes()
    ma.apply("XXX", JUL, verdicts(tmp, "jul", BASE), reports=tmp)
    check("assessed twice against the same rows: byte-identical",
          ma.snapshot_path(tmp, "XXX", JUL).read_bytes(), before)
    check("an edition is not revised",
          "is not revised" in refused(tmp, JUL, [v(STRAT, 3, "XXX-gov.policy-strategy")] + BASE[1:],
                                      "jul-b"), True)

    print("\nthe assessor: refusals")
    for label, rows, want in [
        ("a stage outside 1-5", [v(STRAT, 6, "XXX-gov.policy-strategy")] + BASE[1:], "not 1–5"),
        ("a stage row not yet visible", [v(STRAT, 3, "XXX-gov.policy-strategy-2")] + BASE[1:],
         "not mapped or not visible"),
        ("a stage with no row cited", [v(STRAT, 2, "")] + BASE[1:], "cites no row"),
        ("a measure with no figure", BASE[:2] + [v(MEAS, 2, "XXX-finance.new-dp")], "measure without"),
        ("a measure dated after the as-at",
         BASE[:2] + [v(MEAS, 2, "XXX-finance.new-dp", **{**MEAS_VALUE, "value_year": "2027"})],
         "value_year"),
        ("an instrument with a figure",
         [v(STRAT, 2, "XXX-gov.policy-strategy", value="3")] + BASE[1:], "carries value columns"),
        ("a missing first verdict", BASE[1:], "no verdict and no prior stage"),
        ("an indicator that is not assessed",
         BASE + [v("geopol.china--china", 2, "XXX-gov.policy-strategy")], "not an assessed"),
    ]:
        root = tmp / label.replace(" ", "-")
        unit_dir(root)
        check(label + " is refused", want in refused(root, JUL, rows, "r"), True)

    print("\nthe stability rule")
    notes = ma.apply("XXX", AUG, verdicts(tmp, "aug", [
        v(STRAT, 3, "XXX-gov.policy-strategy|XXX-gov.policy-strategy-2"),   # new row in window
        v(TALK, 3, "XXX-gov.discourse-shutdown"),                           # re-read, no new row
        v(MEAS, 3, "XXX-finance.new-dp", **MEAS_VALUE, reassessed="1"),     # rubric change
    ]), reports=tmp)
    s = snap(tmp, AUG)
    check("a row dated inside the window moves the stage", s[STRAT]["stage"], "3")
    check("and names the dated source", s[STRAT]["moved_by"], "2026-08-10-strategy-adopted")
    check("a re-read with no dated row is held at the prior stage", s[TALK]["stage"], "2")
    check("and the run says so", any(TALK in n and "held at 2" in n for n in notes), True)
    check("reassessed moves it and says why", (s[MEAS]["stage"], s[MEAS]["moved_by"]),
          ("3", "reassessed"))
    check("the July edition is untouched", ma.snapshot_path(tmp, "XXX", JUL).read_bytes(), before)
    check("indicators.csv carries the latest snapshot",
          il.load_unit(str(tmp), "XXX")[STRAT]["stage"], "3")

    root = tmp / "lookback"
    unit_dir(root)
    ma.apply("XXX", JUL, verdicts(root, "jul", BASE), reports=root)
    ma.apply("XXX", AUG, verdicts(root, "aug", [
        v(TALK, 3, "XXX-gov.discourse-shutdown",
          cause="2026-08-15 the 2025 shutdown left the period")]), reports=root)
    s = snap(root, AUG)
    check("a look-back anchor moves on a dated cause", s[TALK]["stage"], "3")
    check("an indicator the drafter left alone carries forward", s[STRAT]["stage"], "2")

    root = tmp / "order"
    unit_dir(root)
    ma.apply("XXX", AUG, verdicts(root, "aug", [v(STRAT, 3, "XXX-gov.policy-strategy-2")]
                                              + BASE[1:]), reports=root)
    ma.apply("XXX", JUL, verdicts(root, "jul", BASE), reports=root)
    check("an earlier snapshot never overwrites the current position",
          il.load_unit(str(root), "XXX")[STRAT]["stage"], "3")
finally:
    shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------------------------
# The checks (D3): clean on a unit apply wrote, failing on a deliberately broken copy of it.

_spec = importlib.util.spec_from_file_location("lm", HERE / "lint-maturity.py")
lm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lm)
lm.ma = ma                      # the fixture rubric, not the live one


def edit_csv(path: Path, iid: str, **cells):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rdr = csv.DictReader(fh)
        fields, rows = rdr.fieldnames, list(rdr)
    for r in rows:
        if r["indicator_id"] == iid:
            r.update(cells)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def fails_on(root) -> str:
    return "".join(k for k, v in sorted(lm.unit_checks("XXX", root).items()) if v)


tmp = Path(tempfile.mkdtemp(prefix="maturity-lint-test-"))
try:
    print("\nthe checks")

    def fresh(name):
        root = tmp / name
        unit_dir(root)
        ma.apply("XXX", JUL, verdicts(root, "jul", BASE), reports=root)
        ma.apply("XXX", AUG, verdicts(root, "aug", [
            v(STRAT, 3, "XXX-gov.policy-strategy|XXX-gov.policy-strategy-2")]), reports=root)
        return root

    root = fresh("clean")
    check("a unit apply wrote passes every check", fails_on(root), "")
    check("a unit with no snapshot is skipped", lm.unit_checks("XXX", tmp / "none"), {})

    root = fresh("n")
    edit_csv(ma.snapshot_path(root, "XXX", AUG), TALK, stage="7")
    edit_csv(root / "XXX" / "indicators.csv", TALK, stage="7")
    check("a stage outside 1-5 fails N (and O, for the move)", fails_on(root), "NO")
    root = fresh("n2")
    edit_csv(ma.snapshot_path(root, "XXX", JUL), STRAT, stage_rows="XXX-gov.policy-strategy-2")
    check("a July stage citing an August row fails N", "N" in fails_on(root), True)
    root = fresh("o")
    edit_csv(ma.snapshot_path(root, "XXX", AUG), TALK, stage="3")
    edit_csv(root / "XXX" / "indicators.csv", TALK, stage="3")
    check("a hand-moved stage with nothing dated behind it fails O", fails_on(root), "O")
    root = fresh("p")
    edit_csv(ma.snapshot_path(root, "XXX", AUG), TALK, stage="1", stage_rows="")
    edit_csv(root / "XXX" / "indicators.csv", TALK, stage="1", stage_rows="")
    check("a stage 1 with no citation fails P (and O, for the move)", fails_on(root), "OP")
    root = fresh("q")
    edit_csv(ma.snapshot_path(root, "XXX", AUG), MEAS, value="")
    edit_csv(root / "XXX" / "indicators.csv", MEAS, value="")
    check("a measure with a figure missing fails Q", fails_on(root), "Q")
    root = fresh("s")
    edit_csv(root / "XXX" / "indicators.csv", STRAT, stage="4")
    check("indicators.csv edited away from the edition fails S", fails_on(root), "S")

    print("\nunplaced: rows held, no rung met")
    root = tmp / "unplaced"
    unit_dir(root)
    unplaced = {"indicator_id": TALK, "stage": "", "qualifier": "rows do not bear on the anchor"}
    ma.apply("XXX", JUL, verdicts(root, "jul", [BASE[0], unplaced, BASE[2]]), reports=root)
    check("is written to the snapshot with no stage", snap(root, JUL)[TALK]["stage"], "")
    check("and passes the checks", fails_on(root), "")
    unit_dir(tmp / "unplaced-2")
    check("without a reason it is refused", "without a qualifier" in refused(
        tmp / "unplaced-2", JUL, [BASE[0], {**unplaced, "qualifier": ""}, BASE[2]], "r"), True)
    notes = ma.apply("XXX", AUG, verdicts(root, "aug", [
        v(STRAT, "", "", qualifier="re-read: nothing on record")]), reports=root)
    check("leaving a stage for unplaced with nothing dated is held",
          snap(root, AUG)[STRAT]["stage"], "2")

    print("\nthe estate checks")
    d = tmp / "scripts"
    d.mkdir()
    (d / "ok.py").write_text('"""The frame has 117 assessed rows."""\n# 121 before B3\nn = len(x)\n',
                             encoding="utf-8")
    check("a frame count in prose passes T", lm.check_frame_count(d), [])
    (d / "bad.py").write_text("if len(rows) != 117:\n    pass\n", encoding="utf-8")
    check("a frame count in logic fails T", lm.check_frame_count(d), ["bad.py:1: 117"])
finally:
    shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------------------------
# Measures: the band, the reference figure, and a new figure as the dated cause.

print("\nmeasures: the band")
T = {"direction": "higher", "cuts": [27.0, 53.0, 80.0, 95.0]}
L = {"direction": "lower", "cuts": [30.0, 20.0, 10.0]}
check("target, higher: 50 is band 2", ma.band(50, T), 2)
check("a lower bound is inclusive: 80 is band 4", ma.band(80, T), 4)
check("a numeric stage 5: 96 is band 5", ma.band(96, T), 5)
check("lower is better: 35 is band 1", ma.band(35, L), 1)
check("lower is better: 15 is band 3", ma.band(15, L), 3)
check("a condition-only 5 leaves the ceiling at 5 from band 4", ma.band(10, L), 5)
check("dates: a slug", ma.source_date("2026-06-01-dp-figures"), dt.date(2026, 6, 1))
check("dates: a reference", ma.source_date("ref:itu-datahub@2026-06-30"), dt.date(2026, 6, 30))
check("dates: a compile", ma.source_date("outputs/non-state-finance/XXX-nonstate.csv@2026-07-02"),
      dt.date(2026, 7, 2))
check("an undated source is not a source", ma.source_date("ITU 2025"), None)


def ref_file(root: Path, rows) -> Path:
    p = root / "reference.csv"
    with open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["iso3", "indicator_id", "dataset", "value", "unit", "year", "release"])
        w.writerows(rows)
    return p


tmp = Path(tempfile.mkdtemp(prefix="maturity-measure-test-"))
try:
    print("\nmeasures: refusals")
    for label, meas, want in [
        ("a stage above its band", v(MEAS, 4, "", **MEAS_VALUE), "above the band"),
        ("an undated source", v(MEAS, 2, "", **{**MEAS_VALUE, "value_source": "World Bank"}),
         "not a dated"),
        ("a source dated after the as-at",
         v(MEAS, 2, "", **{**MEAS_VALUE, "value_source": "2026-08-02-dp-figures"}), "after the as-at"),
        ("a value that is not a number", v(MEAS, 2, "", **{**MEAS_VALUE, "value": "about 12"}),
         "not a number"),
    ]:
        root = tmp / label.replace(" ", "-")
        unit_dir(root)
        check(label + " is refused", want in refused(root, JUL, BASE[:2] + [meas], "r"), True)
    root = tmp / "no-row"
    unit_dir(root)
    ma.apply("XXX", JUL, verdicts(root, "jul", BASE[:2] + [v(MEAS, 3, "", **MEAS_VALUE)]),
             reports=root)
    check("a measure stands on its figure with no row cited", snap(root, JUL)[MEAS]["stage"], "3")

    print("\nmeasures: the reference figure")
    root = tmp / "ref"
    unit_dir(root)
    rp = ref_file(root, [
        ["XXX", MEAS, "wdi", "7", "US$m", "2025", "2026-07-01"],
        ["XXX", MEAS, "wdi", "30", "US$m", "2025", "2026-08-15"],     # a later release
        ["YYY", MEAS, "wdi", "30", "US$m", "2025", "2026-07-01"],
    ])
    ma.apply("XXX", JUL, verdicts(root, "jul", BASE[:2]), reports=root, ref_path=rp)
    s = snap(root, JUL)
    check("with no verdict, the reference figure is taken at its band", s[MEAS]["stage"], "2")
    check("and cited with its release", s[MEAS]["value_source"], "ref:wdi@2026-07-01")
    check("a release after the as-at is not visible", s[MEAS]["value"], "7")
    check("and the packet shows it", "Reference figure: 7 US$m" in
          ma.packet("XXX", JUL, reports=root, ref_path=rp), True)
    notes = ma.apply("XXX", AUG, verdicts(root, "aug", []), reports=root, ref_path=rp)
    s = snap(root, AUG)
    check("a new release in the window moves it, capped at 4 without the condition",
          (s[MEAS]["stage"], s[MEAS]["moved_by"]), ("4", "ref:wdi@2026-08-15"))
    check("and lint agrees", fails_on(root), "")

    root = tmp / "primary"
    unit_dir(root)
    ma.apply("XXX", JUL, verdicts(root, "jul", BASE), reports=root, ref_path=rp)
    ma.apply("XXX", AUG, verdicts(root, "aug", []), reports=root, ref_path=rp)
    check("a primary standing is not displaced by a reference",
          snap(root, AUG)[MEAS]["value_source"], "2026-06-01-dp-figures")

    root = tmp / "none"
    unit_dir(root)
    ma.apply("XXX", JUL, verdicts(root, "jul", BASE[:2]), reports=root, ref_path=tmp / "nope.csv")
    check("with no figure anywhere it is No evidence", MEAS in snap(root, JUL), False)

    root = tmp / "drift"
    unit_dir(root)
    ma.apply("XXX", JUL, verdicts(root, "jul", BASE), reports=root)
    ma.apply("XXX", AUG, verdicts(root, "aug", [v(MEAS, 1, "", **MEAS_VALUE)]), reports=root)
    check("the same figure re-read to a new stage is held", snap(root, AUG)[MEAS]["stage"], "2")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print()
print("all cases pass" if not fails else f"{len(fails)} of the cases FAILED")
sys.exit(1 if fails else 0)
