#!/usr/bin/env python3
"""test_osint_freshness.py — prove the OSINT freshness check fires.

Same principle as `test_mirror_freshness.py`: this check reads `ok`
for weeks at a time in normal use, and a check that has only ever passed is not evidence of
anything. What it guards is worse than a late backup — a stale mirror means Corpus compiles,
reports and publishes from old evidence without saying so — so the fault paths are the part
that has to be shown working.

Each case builds a synthetic mirror in a temp directory: `logs/ingested_log.md`,
`logs/sweep-cycle_log.md`, a watermark file, and a stubbed `HEAD` commit date standing in for
the one git would report. The module's constants are repointed at it and the exit code
asserted.

    python scripts/test_osint_freshness.py
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import io
import json
import shutil
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(_here))
import osint_lib  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "lint_osint_freshness", _here / "lint-osint-freshness.py")
of = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(of)

TS = "%Y-%m-%d %H:%M"


def ago(hours: float) -> dt.datetime:
    return dt.datetime.now() - dt.timedelta(hours=hours)


def stamp(hours: float) -> str:
    return ago(hours).strftime(TS)


def ingest_log(hours: float) -> str:
    """Newest-first, as OSINT writes it — so the second heading is deliberately older."""
    return (f"## {stamp(hours)} (ingest Phase A, slice 4/10 — 10 items in, 8 admitted)\n"
            f"- something\n\n"
            f"## {stamp(hours + 48)} (ingest Phase A, slice 3/10)\n")


def cycle_table(*ends: float) -> str:
    rows = "".join(
        f"| {n + 1} | SWEEP-X | {stamp(h + 1)} | {stamp(h)} | 1h | |\n"
        for n, h in enumerate(ends))
    return ("| Day | Process | Start | End | Duration | New-Start |\n"
            "|-----|---------|-------|-----|----------|-----------|\n" + rows)


# (name, ingest hours ago | None, cycle End hours ago tuple, HEAD hours ago | None,
#  watermark hours ago | None, argv extras, expected exit)
CASES: list[tuple[str, float | None, tuple[float, ...], float | None, float | None,
                  list[str], int]] = [
    (
        "everything fresh",
        1.0, (2.0,), 0.5, 2.0, [], 0,
    ),
    (
        "quiet between cycles — 70 minutes behind is the normal state",
        1.2, (1.2,), 1.2, 1.2, [], 0,
    ),
    (
        "the whole mirror is three days old",
        24 * 3.5, (24 * 3.5,), 24 * 3.5, 24 * 3.5, [], 1,
    ),
    (
        "old, but inside a raised ceiling",
        24 * 3.5, (24 * 3.5,), 24 * 3.5, 24 * 3.5, ["--max-age-hours", "200"], 0,
    ),
    (
        "HEAD alone is fresh — an OSINT commit outside a cycle still counts",
        24 * 5, (24 * 5,), 1.0, 24 * 5, [], 0,
    ),
    (
        "ingest alone is fresh, git unreadable",
        1.0, (24 * 5,), None, 24 * 5, [], 0,
    ),
    (
        "regressed — the mirror's newest close predates the one Corpus built",
        1.0, (30.0,), 0.5, 2.0, [], 1,
    ),
    (
        "not regressed — the newest close is the one Corpus built",
        1.0, (2.0,), 0.5, 2.0, [], 0,
    ),
    (
        "regression is read from the newest close, not the last row",
        1.0, (2.0, 30.0), 0.5, 2.0, [], 0,
    ),
    (
        "no watermark yet — a first run is not a regression",
        1.0, (2.0,), 0.5, None, [], 0,
    ),
    (
        "nothing readable at all",
        None, (), None, 2.0, [], 2,
    ),
    (
        "an unreadable mirror is not reported as merely stale",
        None, (), None, 24 * 9, ["--max-age-hours", "1"], 2,
    ),
]


def ahead(**delta) -> str:
    """A heading stamped `delta` in the future, as a mistyped one reads."""
    when = dt.datetime.now() + dt.timedelta(**delta)
    return f"## {when:%Y-%m-%d %H:%M} (ingest Phase A slice ingest-33)" + chr(10)


def dateless(hours: float) -> str:
    """A heading carrying a date and no time, as OSINT has written them since 2026-08-23."""
    return (f"## {ago(hours):%Y-%m-%d} (ingest Phase A - bulletin sweep, slice 1 of 3; "
            f"10 items in, 6 admitted)" + chr(10))


def midnight(hours: float) -> str:
    """Midnight of the day `hours` ago — what `dateless(hours)` is expected to read as."""
    return ago(hours).replace(hour=0, minute=0).strftime(TS)


def stamp_cases() -> int:
    """`last_ingest()` takes the maximum, so one mistyped heading outranks every correct one.

    2026-08-23: `ingest-33` ran at 01:12 and was written into `ingested_log.md` as `12:00`, and
    the bulletin byline then told readers the page had last been updated four hours into the
    reader's future. The reading is dropped and the newest true stamp stands in its place — a
    slightly stale answer rather than a false one."""
    failures = 0
    saved = osint_lib.INGESTED_LOG
    tmp = Path(tempfile.mkdtemp(prefix="osint-stamp-test-"))
    try:
        (tmp / "logs").mkdir()
        osint_lib.INGESTED_LOG = str(tmp / "logs" / "ingested_log.md")
        log = Path(osint_lib.INGESTED_LOG)
        skew = dt.datetime.now() + dt.timedelta(minutes=2)

        cases: list[tuple[str, str, str | None]] = [
            ("the newest true stamp wins",
             ingest_log(1.0), stamp(1.0)),
            ("a stamp four hours into the future is ignored",
             ahead(hours=4) + ingest_log(1.0), stamp(1.0)),
            ("skew of a minute or two is believed, not thrown away",
             f"## {skew:%Y-%m-%d %H:%M} (ingest 33)" + chr(10), skew.strftime(TS)),
            ("a file of nothing but future stamps reads as unreadable, not as fresh",
             ahead(days=1), None),
            # 2026-08-24. OSINT dropped the time from the heading on 2026-08-23 and 21 of the
            # 63 headings then carried a date alone. Unread, they were not a gap in the answer
            # but a wrong one: both readers fell back to the newest heading that still had a
            # time on it, `2026-08-23 10:20`, on an afternoon when that morning's sweep had
            # admitted 16 records — and the bulletin byline states this file as fact.
            ("a heading dated with no time is read, at midnight",
             dateless(1.0), midnight(1.0)),
            ("a date-only heading cannot outrank a timed one later the same day",
             dateless(1.0) + f"## {stamp(1.0)} (ingest Phase A slice 2)" + chr(10), stamp(1.0)),
            ("today's date-only heading still beats yesterday's timed one",
             dateless(1.0) + f"## {stamp(25.0)} (ingest Phase A slice 1)" + chr(10),
             midnight(1.0)),
        ]
        for name, text, expected in cases:
            log.write_text(text, encoding="utf-8")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                got = osint_lib.last_ingest()
            got_s = got.strftime(TS) if got else None
            ok = got_s == expected
            failures += not ok
            verdict = "ok  " if ok else "FAIL"
            print(f"  {verdict} {name}  (expected {expected}, got {got_s})")
    finally:
        osint_lib.INGESTED_LOG = saved
        shutil.rmtree(tmp, ignore_errors=True)
    return failures, len(cases)


def heads(*hours_ago: float) -> str:
    """An ingest log of nothing but headings, newest first as OSINT writes it."""
    return "".join(f"## {stamp(h)} (ingest Phase A slice {n})" + chr(10) + chr(10)
                   for n, h in enumerate(sorted(hours_ago)))


def run_start_cases() -> int:
    """`ingest_started()` is the bulletin's byline: when collection stopped.

    Bill, 2026-08-23. Ingest reads what the night's sweeps staged, so its **start** bounds
    collection, and it runs on for hours afterwards writing up a catch that has already stopped
    growing. The cases below are the three ways that reading can go wrong: taking the end of the
    run, taking the start of a run that is not the current one, and letting one bad heading move
    the answer."""
    failures = 0
    saved = osint_lib.INGESTED_LOG
    tmp = Path(tempfile.mkdtemp(prefix="osint-run-test-"))
    try:
        (tmp / "logs").mkdir()
        osint_lib.INGESTED_LOG = str(tmp / "logs" / "ingested_log.md")
        log = Path(osint_lib.INGESTED_LOG)

        # A night's run: slices over five and a half hours, the widest internal gap 75 minutes.
        night = (7.5, 7.0, 6.5, 6.4, 6.0, 5.5, 4.0, 2.75)
        cases: list[tuple[str, str, str | None]] = [
            ("the start of the run, not its newest stamp",
             heads(*night), stamp(7.5)),
            ("a 75-minute gap inside a run does not split it",
             heads(6.0, 4.5), stamp(6.0)),
            ("yesterday's run is a different run",
             heads(30.0, 29.0, *night), stamp(7.5)),
            ("a mistyped late heading extends the tail and cannot move the start",
             heads(*night, 3.1), stamp(7.5)),
            ("one heading is a run of one",
             heads(3.0), stamp(3.0)),
            ("nothing readable is None, not today",
             "", None),
        ]
        for name, text, expected in cases:
            log.write_text(text, encoding="utf-8")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                got = osint_lib.ingest_started()
            got_s = got.strftime(TS) if got else None
            ok = got_s == expected
            failures += not ok
            verdict = "ok  " if ok else "FAIL"
            print(f"  {verdict} {name}  (expected {expected}, got {got_s})")
    finally:
        osint_lib.INGESTED_LOG = saved
        shutil.rmtree(tmp, ignore_errors=True)
    return failures, len(cases)


def run() -> int:
    failures = 0
    argv = sys.argv
    saved = (osint_lib.INGESTED_LOG, osint_lib.CYCLE_LOG, osint_lib.MIRROR,
             of.WATERMARK, of.head_committed)
    try:
        for name, ing, ends, head, mark, extra, expected in CASES:
            tmp = Path(tempfile.mkdtemp(prefix="osint-fresh-test-"))
            try:
                (tmp / "logs").mkdir()
                osint_lib.MIRROR = str(tmp)
                osint_lib.INGESTED_LOG = str(tmp / "logs" / "ingested_log.md")
                osint_lib.CYCLE_LOG = str(tmp / "logs" / "sweep-cycle_log.md")
                of.WATERMARK = str(tmp / ".osint-cycle-seen")

                if ing is not None:
                    Path(osint_lib.INGESTED_LOG).write_text(ingest_log(ing), encoding="utf-8")
                if ends:
                    Path(osint_lib.CYCLE_LOG).write_text(cycle_table(*ends), encoding="utf-8")
                if mark is not None:
                    Path(of.WATERMARK).write_text(json.dumps(
                        {"done": stamp(mark), "done_by": "built"}), encoding="utf-8")

                of.head_committed = (lambda h=head: None if h is None else ago(h))

                sys.argv = ["lint-osint-freshness.py", *extra]
                buf = io.StringIO()
                with redirect_stdout(buf):
                    got = of.main()

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
        sys.argv = argv
        (osint_lib.INGESTED_LOG, osint_lib.CYCLE_LOG, osint_lib.MIRROR,
         of.WATERMARK, of.head_committed) = saved

    stamp_failures, stamp_ran = stamp_cases()
    start_failures, start_ran = run_start_cases()
    failures += stamp_failures + start_failures
    # Counted off the case lists, not added up by hand. It read `len(CASES) + 4 + 6` until
    # 2026-08-24, when three cases were added to `stamp_cases()` and the run went on reporting
    # 22 — a suite that miscounts itself is a suite that can quietly stop running something.
    total = len(CASES) + stamp_ran + start_ran

    print()
    if failures:
        print(f"{failures} of {total} cases FAILED")
        return 1
    print(f"all {total} cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(run())
