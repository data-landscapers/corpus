#!/usr/bin/env python3
r"""test_lint_prepared.py — spent, waiting and unresolved are three answers, not two.

    python scripts/test_lint_prepared.py

The failure that matters is not a false alarm, it is a false clear: a handover this passes
over stays in the share for ever, which is exactly how `prepared/` reached 5.3 MB across 33
spent items without anyone noticing. So every route to *spent* is exercised, and so is every
route that must **not** reach it — an open job, a drop list not yet absorbed, and the case
this deliberately refuses to guess at, an item naming no closer at all.

The three-way verdict is the point. A checker that answered only spent-or-not would have to
call an unresolvable item one of the two, and both are wrong: calling it spent deletes work
somebody is waiting on, and calling it waiting is how silt accumulates while the check
reports clean.
"""
from __future__ import annotations

import importlib.util
import io
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("lp", HERE / "lint-prepared.py")
lp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lp)

fails: list[str] = []


def check(label, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
    if not ok:
        print(f"          got {got!r}\n          want {want!r}")
        fails.append(label)


def build(root: Path, *, open_jobs=(), closed_jobs=(), open_r=(), closed_r=(),
          open_notes=(), closed_notes=()):
    root.mkdir(parents=True, exist_ok=True)
    (root / "prepared").mkdir(exist_ok=True)
    io.open(root / "housekeeping-jobs.md", "w", encoding="utf-8").write(
        "# register\n\n" + "".join(f"{n}. **still owed**\n\n" for n in open_jobs))
    io.open(root / "housekeeping-jobs-resolved.md", "w", encoding="utf-8").write(
        "# resolved\n\n" + "".join(f"x{n}. **done**\n\n" for n in closed_jobs))
    lines = [f"- [ ] **R{r} [OSINT]** - owed" for r in open_r]
    lines += [f"- [x] **R{r} [OSINT]** - done" for r in closed_r]
    io.open(root / "strategic-review-register.md", "w", encoding="utf-8").write(
        "# register\n\n" + "\n".join(lines) + "\n")
    io.open(root / "notes-for-osint.md", "w", encoding="utf-8").write(
        "# notes\n\n" + "".join(f"**{n}** [ACT] (2026-09-23) - owed\n\n" for n in open_notes))
    io.open(root / "notes-for-osint-resolved.md", "w", encoding="utf-8").write(
        "# resolved\n\n" + "".join(f"### {n}. `[ACT]` done\n\n" for n in closed_notes))


def item(root: Path, name: str, closer: str | None = None, folder=True):
    p = root / "prepared" / name
    if folder:
        p.mkdir(parents=True, exist_ok=True)
        body = "# brief\n\nWhat it does.\n"
        if closer:
            body += f"\n**Closed by:** {closer}\n"
        io.open(p / "BRIEF.md", "w", encoding="utf-8").write(body)
    else:
        io.open(p, "w", encoding="utf-8").write("payload\n")
    return p


def states(root: Path) -> dict:
    src = {"open": lp._read(str(root / "housekeeping-jobs.md")),
           "resolved": lp._read(str(root / "housekeeping-jobs-resolved.md")),
           "register": lp._read(str(root / "strategic-review-register.md"))}
    out = {}
    for name in sorted(os.listdir(root / "prepared")):
        if name == "BRIEF.md":
            continue
        out[name] = lp.verdict(name, str(root / "prepared" / name), str(root), src)[0]
    return out


tmp = Path(tempfile.mkdtemp(prefix="lint-prepared-test-"))
try:
    print("\na job folder resolves itself")
    r = tmp / "jobs"
    build(r, open_jobs=(77,), closed_jobs=(88, 89, 117))
    for n in ("job-88", "job-89-117", "job-77", "job-88-77", "job-999"):
        item(r, n)
    s = states(r)
    check("a closed job is spent", s["job-88"], "spent")
    check("every number in the name has to be closed", s["job-89-117"], "spent")
    check("an open job is waiting", s["job-77"], "live")
    check("one open number keeps the whole folder", s["job-88-77"], "live")
    check("a number in neither register is unresolved", s["job-999"], "unresolved")

    print("\na closed name is not enough on its own")
    # Note 40: the first prune deleted two folders whose names were struck jobs and whose files
    # were the only copy of an open job's input. A name-only test cannot see that.
    r = tmp / "still-needed"
    build(r, open_jobs=(121,), closed_jobs=(96, 105, 107, 116))
    for n in ("job-96-116", "job-105", "job-107"):
        item(r, n)
    io.open(r / "housekeeping-jobs.md", "w", encoding="utf-8").write(
        "# register\n\n121. **an open job whose input is `prepared\\job-105\\"
        "entity-fragments.csv` and `prepared/job-96-116/entity-variants.csv`**\n\n")
    s = states(r)
    check("a folder an open job still names is waiting", s["job-96-116"], "live")
    check("with a backslash path too", s["job-105"], "live")
    check("and a folder nobody names stays spent", s["job-107"], "spent")

    r = tmp / "closed-mention"
    build(r, closed_jobs=(107,))
    item(r, "job-107")
    io.open(r / "housekeeping-jobs-resolved.md", "w", encoding="utf-8").write(
        "# resolved\n\nx107. **done; its input was `prepared/job-107/x.csv`**\n\n")
    check("a closed job naming it does not save it", states(r)["job-107"], "spent")

    print("\nthe drop lists, which carry their own answer")
    r = tmp / "drops"
    build(r)
    item(r, "status-acquire-TUN-drops-absorbed-2026-09-19.csv", folder=False)
    item(r, "status-acquire-KEN-drops.csv", folder=False)
    s = states(r)
    check("absorbed is spent", s["status-acquire-TUN-drops-absorbed-2026-09-19.csv"], "spent")
    check("not yet absorbed is waiting", s["status-acquire-KEN-drops.csv"], "live")

    print("\nanything else says who closes it")
    r = tmp / "briefs"
    build(r, open_jobs=(50,), closed_jobs=(60,), open_r=("49",), closed_r=("31", "35"))
    item(r, "hero-batch", closer="review 4 register R31")
    item(r, "lens", closer="R35")
    item(r, "owed-r", closer="R49")
    item(r, "owed-job", closer="housekeeping job 50")
    item(r, "done-job", closer="job 60")
    item(r, "silent")
    item(r, "vague", closer="Bill says so")
    item(r, "unknown-r", closer="R404")
    s = states(r)
    check("a closed review line is spent", s["hero-batch"], "spent")
    check("a bare R-number works too", s["lens"], "spent")
    check("an open review line is waiting", s["owed-r"], "live")
    check("an open job named in a brief is waiting", s["owed-job"], "live")
    check("a closed job named in a brief is spent", s["done-job"], "spent")
    check("no Closed by line is unresolved, not spent", s["silent"], "unresolved")
    check("a closer naming nothing citable is unresolved", s["vague"], "unresolved")
    check("an R-line in no register is unresolved", s["unknown-r"], "unresolved")

    print("\na bare file takes the folder's brief")
    r = tmp / "bare"
    build(r, closed_r=("31",))
    io.open(r / "prepared" / "BRIEF.md", "w", encoding="utf-8").write(
        "# the hero series\n\n**Closed by:** R31\n")
    item(r, "hero-00.jsonl", folder=False)
    check("resolved from the sibling brief", states(r)["hero-00.jsonl"], "spent")
    check("and the shared brief is not itself an item", "BRIEF.md" in states(r), False)

    print("\nexit codes")
    r = tmp / "exit-clean"
    build(r, open_jobs=(1,))
    item(r, "job-1")
    check("nothing spent exits 0", lp.main(["--share", str(r)]), 0)
    r = tmp / "exit-dirty"
    build(r, closed_jobs=(1,))
    item(r, "job-1")
    check("something spent exits 1", lp.main(["--share", str(r)]), 1)
    r = tmp / "exit-empty"
    build(r)
    check("an empty prepared/ exits 0", lp.main(["--share", str(r)]), 0)
    r = tmp / "exit-none"
    r.mkdir()
    io.open(r / "housekeeping-jobs.md", "w", encoding="utf-8").write("# x\n")
    check("no prepared/ at all exits 0", lp.main(["--share", str(r)]), 0)
    check("no share exits 2", lp.main(["--share", str(tmp / "nope")]), 2)

    print("\nnote-NNN resolves against the notes files")
    r = tmp / "notes"
    build(r, open_notes=(164,), closed_notes=(150,))
    for n in ("note-164", "note-150", "note-999"):
        item(r, n)
    src = {"open": "", "resolved": "", "register": "",
           "notes": lp._read(r / "notes-for-osint.md"),
           "notes_resolved": lp._read(r / "notes-for-osint-resolved.md")}
    check("an open note is waiting",
          lp.verdict("note-164", str(r / "prepared" / "note-164"), str(r), src)[0], "live")
    check("a resolved note is spent",
          lp.verdict("note-150", str(r / "prepared" / "note-150"), str(r), src)[0], "spent")
    check("a note in neither file is unresolved",
          lp.verdict("note-999", str(r / "prepared" / "note-999"), str(r), src)[0], "unresolved")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# An open entry ends at the next entry of any state: a closed line below an open one is not part of it.
_reg = ("- [ ] **R80 [X]** open thing\n- [x] **R87 [C]** deliver prepared/R87 here\n"
        "- [ ] **R90 [X]** uses prepared/R99/x\n")
check("a closed line is not folded into the open entry above it",
      lp.cited_by_open("R87", {"open": "", "register": _reg}), "")
check("an open line naming the folder still holds it",
      lp.cited_by_open("R99", {"open": "", "register": _reg}), "review line R90")

print()
print("all cases pass" if not fails else f"{len(fails)} of the cases FAILED")
sys.exit(1 if fails else 0)
