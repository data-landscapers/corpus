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
    {"indicator_id": "gov.policy--a", "chapter": "Governance"},
    {"indicator_id": "gov.policy--b", "chapter": "Governance"},
    {"indicator_id": "infra.connect--c", "chapter": "ICT Infrastructure"},
    {"indicator_id": "digital.rural--d", "chapter": "Digitalisation"},
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
    check("an undrafted chapter is pending, not failed", st["chapters"], {"Governance": 2})
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
          has(run(d)[0], "chapter Governance is drafted in part"), True)
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

print()
print("all cases pass" if not fails else f"{len(fails)} of the cases FAILED")
sys.exit(1 if fails else 0)
