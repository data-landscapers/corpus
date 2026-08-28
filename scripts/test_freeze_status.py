#!/usr/bin/env python3
"""test_freeze_status.py — prove the freeze closes itself rather than lapsing by silence.

The one thing this script refuses is the freeze outliving its own end date, so that is the
case worth proving: on the last day it runs, on the day after it stops. Each case builds a
throwaway repo with commits on both layers, so the split is measured rather than assumed.

    python scripts/test_freeze_status.py
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import io
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "freeze_status", Path(__file__).resolve().parent / "freeze-status.py")
fs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fs)

failures: list[str] = []


def check(name: str, got, want) -> None:
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got:  {got!r}\n         want: {want!r}")
        failures.append(name)


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=False)


def build(tmp: Path, process: int, report: int, when: dt.date) -> Path:
    """A repo with `process` commits under scripts/ and `report` under outputs/, on `when`."""
    repo = tmp / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "t")
    stamp = f"{when:%Y-%m-%d} 12:00:00 +0000"
    for kind, n, sub in (("p", process, "scripts"), ("r", report, "outputs")):
        (repo / sub).mkdir(exist_ok=True)
        for i in range(n):
            (repo / sub / f"{kind}{i}.txt").write_text(str(i), encoding="utf-8")
            git(repo, "add", "-A")
            subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", f"{kind}{i}",
                            "--date", stamp],
                           capture_output=True, check=False,
                           env={**__import__("os").environ,
                                "GIT_COMMITTER_DATE": stamp})
    return repo


def run(repo: Path, on: str) -> tuple[int, str]:
    argv_before = sys.argv
    sys.argv = ["freeze-status.py", "--root", str(repo), "--on", on]
    out = io.StringIO()
    try:
        with redirect_stdout(out):
            rc = fs.main()
    finally:
        sys.argv = argv_before
    return rc, out.getvalue()


print("the window is dates, not a duration — a freeze with no end is not a freeze")
check("it has a start", isinstance(fs.BEGAN, dt.date), True)
check("it has an end", isinstance(fs.ENDS, dt.date), True)
check("the end is after the start", fs.ENDS > fs.BEGAN, True)
check("scripts/ counts as process, on the review's own definition",
      "scripts" in fs.PROCESS, True)
check("outputs/ counts as report", "outputs" in fs.REPORT, True)

with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    repo = build(tmp, process=2, report=3, when=fs.BEGAN)

    print("inside the window it reports the split and does not refuse")
    rc, out = run(repo, f"{fs.BEGAN:%Y-%m-%d}")
    check("exit 0", rc, 0)
    check("counts the process commits", "2 process commit(s)" in out, True)
    check("counts the report commits", "3 report" in out, True)
    check("states the share", "40% process" in out, True)
    check("says how long is left", f"ends {fs.ENDS:%Y-%m-%d}" in out, True)

    print("the last day still runs; the day after refuses")
    rc, out = run(repo, f"{fs.ENDS:%Y-%m-%d}")
    check("the last day is inside", rc, 0)
    rc, out = run(repo, f"{fs.ENDS + dt.timedelta(days=1):%Y-%m-%d}")
    check("the day after exits 1", rc, 1)
    check("and asks for the decision", "Renew it with a new ENDS, or let it lapse" in out,
          True)

    print("a repo with commits but none in either layer says so, not 0%")
    # Committed on a path in neither list, which is the real shape of this case: git
    # answers, and answers nothing. A repo with no commits at all is the unreadable case
    # below, because a `git log` that fails and a window that is empty must not look alike.
    empty = build(tmp / "empty", process=0, report=0, when=fs.BEGAN)
    (empty / "README.md").write_text("x", encoding="utf-8")
    git(empty, "add", "-A")
    subprocess.run(["git", "-C", str(empty), "commit", "-q", "-m", "init",
                    "--date", f"{fs.BEGAN:%Y-%m-%d} 12:00:00 +0000"],
                   capture_output=True, check=False)
    rc, out = run(empty, f"{fs.BEGAN:%Y-%m-%d}")
    check("exit 0", rc, 0)
    check("no commits is stated, not computed", "no commits yet" in out, True)

    print("an unreadable repo is a 2, not a clean freeze")
    rc, out = run(tmp / "nowhere", f"{fs.BEGAN:%Y-%m-%d}")
    check("exit 2", rc, 2)

    print("a malformed --on is refused rather than read as today")
    rc, out = run(repo, "the 3rd")
    check("exit 2", rc, 2)

print()
if failures:
    print(f"FAILED: {len(failures)} case(s) — {', '.join(failures)}")
    sys.exit(1)
print("all cases pass")
