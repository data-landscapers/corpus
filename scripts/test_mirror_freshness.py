#!/usr/bin/env python3
"""test_mirror_freshness.py — prove the mirror freshness check fires.

Same principle as `test_leak_check.py`: a check that has only ever passed is not evidence
of anything, and this one will sit at `ok` for weeks at a time in normal use, which is
exactly the condition under which a broken check goes unnoticed.

Each case builds a synthetic `mirror_log.md` and `log.md` in a temp directory, points the
module's two path constants at them, and asserts the exit code.

    python scripts/test_mirror_freshness.py
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import io
import shutil
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "lint_mirror_freshness", Path(__file__).resolve().parent / "lint-mirror-freshness.py")
mf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mf)


def stamp(hours_ago: float) -> str:
    return (dt.datetime.now() - dt.timedelta(hours=hours_ago)).strftime("%Y-%m-%d %H:%M")


def mirror_line(hours_ago: float, status: str = "ok") -> str:
    return (f"- **{stamp(hours_ago)}** - {status} - "
            f"osint(robocopy=3 bundle=0) corpus(robocopy=3 bundle=0) ffs=0\n")


def run_line(hours_ago: float, pass_name: str = "render") -> str:
    return f"{stamp(hours_ago)} · {pass_name} · something happened — ok\n"


# (name, mirror_log text or None, log.md text or None, argv extras, expected exit)
CASES: list[tuple[str, str | None, str | None, list[str], int]] = [
    (
        "fresh, ok, newer than the render",
        mirror_line(1), run_line(2), [], 0,
    ),
    (
        "newest run recorded FAIL",
        mirror_line(2, "ok") + mirror_line(1, "FAIL"), run_line(3), [], 1,
    ),
    (
        "older than the newest render",
        mirror_line(5), run_line(1), [], 1,
    ),
    (
        "simply old, with nothing else moving",
        mirror_line(24 * 8), run_line(24 * 9), [], 1,
    ),
    (
        "old but inside a raised ceiling",
        mirror_line(24 * 8), run_line(24 * 9), ["--max-age-hours", "300"], 0,
    ),
    (
        "fresh with no render ever recorded",
        mirror_line(1), "", [], 0,
    ),
    (
        "no mirror log at all",
        None, run_line(1), [], 2,
    ),
    (
        "mirror log present but unparseable",
        "nothing here looks like a mirror line\n", run_line(1), [], 2,
    ),
    (
        "newest by timestamp, not last in file",
        mirror_line(1) + mirror_line(30, "FAIL"), run_line(2), [], 0,
    ),
    (
        "a FAIL that is also the newest, listed first",
        mirror_line(1, "FAIL") + mirror_line(30), run_line(2), [], 1,
    ),
    (
        "a build line is not a render line",
        mirror_line(5), run_line(1, "build"), [], 0,
    ),
]


def run() -> int:
    failures = 0
    argv, mlog, rlog = sys.argv, mf.MIRROR_LOG, mf.RUN_LOG
    try:
        for name, mirror_text, run_text, extra, expected in CASES:
            tmp = Path(tempfile.mkdtemp(prefix="mirror-test-"))
            try:
                mf.MIRROR_LOG = str(tmp / "mirror_log.md")
                mf.RUN_LOG = str(tmp / "log.md")
                if mirror_text is not None:
                    Path(mf.MIRROR_LOG).write_text(mirror_text, encoding="utf-8")
                if run_text is not None:
                    Path(mf.RUN_LOG).write_text(run_text, encoding="utf-8")

                sys.argv = ["lint-mirror-freshness.py", *extra]
                buf = io.StringIO()
                with redirect_stdout(buf):
                    got = mf.main()

                ok = got == expected
                failures += not ok
                verdict = "ok  " if ok else "FAIL"
                print(f"  {verdict} {name}  (expected {expected}, got {got})")
                if not ok:
                    for ln in buf.getvalue().splitlines():
                        print(f"       {ln}")
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
    finally:
        sys.argv, mf.MIRROR_LOG, mf.RUN_LOG = argv, mlog, rlog

    print()
    if failures:
        print(f"{failures} of {len(CASES)} cases FAILED")
        return 1
    print(f"all {len(CASES)} cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(run())
