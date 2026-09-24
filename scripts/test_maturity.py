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


MEAS_VALUE = dict(value="12.5", unit="US$m", value_year="2025", value_source="XXX-finance.new-dp")
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

print()
print("all cases pass" if not fails else f"{len(fails)} of the cases FAILED")
sys.exit(1 if fails else 0)
