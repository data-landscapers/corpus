#!/usr/bin/env python3
"""test_osint_freshness.py — prove the OSINT freshness check fires.

Same principle as `test_mirror_freshness.py` and `test_leak_check.py`: this check reads `ok`
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
from contextlib import redirect_stdout
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

    print()
    if failures:
        print(f"{failures} of {len(CASES)} cases FAILED")
        return 1
    print(f"all {len(CASES)} cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(run())
