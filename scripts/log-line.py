#!/usr/bin/env python3
r"""log-line.py — write one run line into logs/log.md, newest first.

`logs/log.md` reads **newest first** (flipped 2026-08-16). A run's line therefore has
to be *inserted* under the marker, not appended, and this exists so that neither
runbook has to hand-roll the insert.

**Why not `>> logs/log.md`.** That was the old recipe and it still works — it just puts
the newest run at the bottom of a file that now reads top-down, which is the one failure
mode nobody notices, because the line is present and correct and only its position is
wrong. The next run appends under it and the log is quietly half-sorted.

**Why not a `sed` insert after the marker.** Run lines carry `·`, em-dashes, slashes,
ampersands and backticks as ordinary content; all of those mean something to `sed`'s
replacement text. This takes the message as an argv string and never re-parses it.

The marker is the anchor rather than a line count, so the header can grow without
breaking this. If it is missing, this fails rather than guessing where the entries start
— a wrong guess writes a run line into the frontmatter.

**Every line carries how long the run took** *(Bill, 2026-08-17)*, as a third field:
`YYYY-MM-DD HH:MM · job · 3h02m · what happened`. The duration is **measured, not
remembered** — a run stamps the clock into `logs/.run-start-{job}` when it begins and the
closing call reads it back, so the number is not a session's recollection of when it
started. `--since` and `--took` state it by hand where no stamp was taken.

A run with no stamp and no override writes `unclocked` rather than dropping the field.
Omitting it would let the practice lapse invisibly: the line would still be present and
correct, and only a comparison against every other line would show that a run had stopped
recording it. `unclocked` is a fact about the run and reads as one.

The stamp file is per job, so two passes can be in flight at once, and a `--start` always
overwrites — a run that dies without logging leaves a stale stamp, and the next run of
that job clears it rather than inheriting it.

**The first two fields must not move.** `RUN_RE` in `scripts/lint-mirror-freshness.py`
finds the newest `· render ·` line by matching the timestamp and pass name, and stops
there; the duration sits after it, which is why it goes third rather than second.

**The message is capped at 40 words and an over-cap line is refused** (strategic review
task 4; the same cap OSINT's `log-append.py` enforces). The log is a skim of what
happened — detail belongs in git, and anything owed a decision in
`logs/messages-for-bill.md`. A cap nobody counts drifts, so this one is counted here,
at the door.

Usage:  python scripts/log-line.py --start build
        python scripts/log-line.py build  "catalogue 9,407, 20 ledgers updated — ok"
        python scripts/log-line.py render "241/241 rendered, catalogue 10,731 — ok"
        python scripts/log-line.py render "..." --at "2026-08-16 13:00"
        python scripts/log-line.py build  "..." --since "2026-08-17 06:41"
        python scripts/log-line.py build  "..." --took 3h02m
Exit:   0 written, 1 the log is missing its marker, is not where it should be, or an
        argument does not parse.
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN_LOG = os.path.join(ROOT, "logs", "log.md")
LOGS = os.path.join(ROOT, "logs")
MARKER = "<!-- newest first: a new entry goes directly below this line -->"
UNCLOCKED = "unclocked"

# One terse line per run. Refused, not warned: a warning on a cap is a cap nobody keeps.
ENTRY_WORD_CAP = 40

# Must stay in step with RUN_RE in scripts/lint-mirror-freshness.py, which finds the
# newest `· render ·` line by matching exactly this shape.
PASS_RE = re.compile(r"^\w[\w-]*$")

STAMP_FMT = "%Y-%m-%d %H:%M"
TOOK_RE = re.compile(r"^(?:(\d+)d)?\s*(?:(\d+)h)?\s*(?:(\d+)m)?$")


def stamp_path(job: str) -> str:
    """Where a run of `job` records the clock it started on.

    One file per job rather than one file for all of them: BUILD and a status-init pass
    can be in flight together, and a shared file would have the second `--start` erase
    the first run's start time and hand it the wrong duration."""
    return os.path.join(LOGS, f".run-start-{job}")


def format_took(delta: dt.timedelta) -> str:
    """A duration a reader can take in at a glance, not a precise interval.

    Minutes are the floor: these are jobs measured in hours, and a run line reporting
    seconds would be claiming a precision the clock stamp does not have — the start is
    recorded to the minute, so the error bar is already about a minute wide."""
    total = int(delta.total_seconds())
    if total < 60:
        return "<1m"
    minutes = total // 60
    days, minutes = divmod(minutes, 60 * 24)
    hours, minutes = divmod(minutes, 60)
    if days:
        return f"{days}d {hours:02d}h"
    if hours:
        return f"{hours}h{minutes:02d}m"
    return f"{minutes}m"


def parse_took(text: str) -> dt.timedelta | None:
    """`--took` in the shapes this script writes, plus a bare number meaning minutes.

    Validated rather than passed through: the field is meant to be comparable across
    lines, and a free-text duration ("about three hours") is one nobody can sort on."""
    text = text.strip()
    if text.isdigit():
        return dt.timedelta(minutes=int(text))
    m = TOOK_RE.match(text)
    if not m or not any(m.groups()):
        return None
    d, h, mi = (int(g) if g else 0 for g in m.groups())
    return dt.timedelta(days=d, hours=h, minutes=mi)


def resolve_took(args, when: dt.datetime):
    """How long the run took, and the stamp file to clear once the line is written.

    Returns `(took, stamp_or_None, warning_or_None)`, or `(None, ...)` when an argument
    does not parse and the caller should exit 1. Precedence is explicit over measured:
    a `--took` or `--since` on the command line is someone stating a duration they know,
    and it beats a stamp that may belong to an abandoned run."""
    if args.took is not None:
        delta = parse_took(args.took)
        if delta is None:
            print(f"log-line: --took '{args.took}' is not a duration. Use 3h02m, 47m, "
                  f"'2d 04h', or a bare number of minutes.")
            return None, None, None
        return format_took(delta), None, None

    began = None
    stamp = None
    if args.since:
        try:
            began = dt.datetime.strptime(args.since, STAMP_FMT)
        except ValueError:
            print(f"log-line: --since '{args.since}' is not 'YYYY-MM-DD HH:MM'.")
            return None, None, None
    else:
        path = stamp_path(args.job)
        if os.path.exists(path):
            raw = io.open(path, encoding="utf-8").read().strip()
            try:
                began = dt.datetime.strptime(raw, STAMP_FMT)
                stamp = path
            except ValueError:
                # A stamp nobody can read is worse than none: it would silently produce
                # `unclocked` for every future run of this job until someone noticed.
                return UNCLOCKED, path, (
                    f"{path} holds '{raw}', which is not 'YYYY-MM-DD HH:MM' - logging "
                    f"this run as {UNCLOCKED} and clearing the stamp.")

    if began is None:
        return UNCLOCKED, None, None

    delta = when - began
    if delta < dt.timedelta(0):
        # The run cannot have finished before it started. Reporting a negative duration
        # would be reporting the clock, not the job.
        return UNCLOCKED, stamp, (
            f"the start recorded for '{args.job}' ({began:%Y-%m-%d %H:%M}) is after this "
            f"line's own time ({when:%Y-%m-%d %H:%M}) - logging as {UNCLOCKED}.")
    return format_took(delta), stamp, None


def main() -> int:
    ap = argparse.ArgumentParser(description="Write one line to logs/log.md, newest first.")
    ap.add_argument("job", help="the pass name, e.g. build or render")
    ap.add_argument("message", nargs="?", help="what happened, one terse line")
    ap.add_argument("--at", default=None, metavar="'YYYY-MM-DD HH:MM'",
                    help="timestamp to record (default: now)")
    ap.add_argument("--start", action="store_true",
                    help="stamp the clock for this job and exit; the closing call reads "
                         "it back as the run's duration")
    ap.add_argument("--since", default=None, metavar="'YYYY-MM-DD HH:MM'",
                    help="when the run began, where no --start stamp was taken")
    ap.add_argument("--took", default=None, metavar="3h02m",
                    help="the duration outright, e.g. 3h02m, 47m, '2d 04h' (a bare "
                         "number is minutes)")
    args = ap.parse_args()

    if not PASS_RE.match(args.job):
        print(f"log-line: '{args.job}' is not a usable pass name (letters, digits, - and _).")
        return 1

    if args.start:
        if args.message:
            print("log-line: --start takes the job only - the message belongs on the "
                  "closing call, when there is something to report.")
            return 1
        began = dt.datetime.now()
        if args.at:
            try:
                began = dt.datetime.strptime(args.at, STAMP_FMT)
            except ValueError:
                print(f"log-line: --at '{args.at}' is not 'YYYY-MM-DD HH:MM'.")
                return 1
        os.makedirs(LOGS, exist_ok=True)
        with io.open(stamp_path(args.job), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(began.strftime(STAMP_FMT) + "\n")
        print(f"log-line: {args.job} run started {began:%Y-%m-%d %H:%M} - the closing "
              f"call will report how long it took.")
        return 0

    if args.message is None:
        ap.error("a message is required unless --start is given")

    words = len(args.message.split())
    if words > ENTRY_WORD_CAP:
        print(f"log-line: the message is {words} words against the cap of "
              f"{ENTRY_WORD_CAP}. The log line is a skim - detail belongs in git, and "
              f"anything owed a decision in logs/messages-for-bill.md. Trim and rerun.")
        return 1

    if args.since and args.took:
        print("log-line: --since and --took both state the same thing; give one.")
        return 1

    if args.at:
        try:
            when = dt.datetime.strptime(args.at, "%Y-%m-%d %H:%M")
        except ValueError:
            print(f"log-line: --at '{args.at}' is not 'YYYY-MM-DD HH:MM'.")
            return 1
    else:
        when = dt.datetime.now()

    took, stamp, warning = resolve_took(args, when)
    if took is None:
        return 1
    if warning:
        print(f"log-line: {warning}")

    if not os.path.exists(RUN_LOG):
        print(f"log-line: {RUN_LOG} does not exist - nothing to write into.")
        return 1

    with io.open(RUN_LOG, encoding="utf-8") as fh:
        lines = fh.read().split("\n")

    try:
        at = lines.index(MARKER)
    except ValueError:
        print("log-line: logs/log.md carries no newest-first marker, so where the "
              "entries begin cannot be established. Expected the line:")
        print(f"  {MARKER}")
        return 1

    entry = "{:%Y-%m-%d %H:%M} · {} · {} · {}".format(
        when, args.job, took, args.message.strip())
    lines.insert(at + 1, entry)

    body = "\n".join(lines)
    if not body.endswith("\n"):
        body += "\n"
    with io.open(RUN_LOG, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)

    # Only now: a stamp consumed before the write is lost if the write fails, and the
    # retry would then report `unclocked` for a run whose start time was on disk.
    if stamp:
        try:
            os.remove(stamp)
        except OSError as exc:
            print(f"log-line: wrote the line but could not clear {stamp} ({exc}); the "
                  f"next --start for this job overwrites it.")

    # Guarded: the run line holds `·` and em-dashes, and a console that cannot encode
    # them would otherwise take down a job that has already done its work and written
    # its line. A captured stdout has no reconfigure at all, which is how the tests run.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    print(f"log-line: wrote to the top of logs/log.md - {entry}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
