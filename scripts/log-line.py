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

Usage:  python scripts/log-line.py build  "catalogue 9,407, 20 ledgers updated — ok"
        python scripts/log-line.py render "241/241 rendered, leak gate clean — ok"
        python scripts/log-line.py render "..." --at "2026-08-16 13:00"
Exit:   0 written, 1 the log is missing its marker or is not where it should be.
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
MARKER = "<!-- newest first: a new entry goes directly below this line -->"

# Must stay in step with RUN_RE in scripts/lint-mirror-freshness.py, which finds the
# newest `· render ·` line by matching exactly this shape.
PASS_RE = re.compile(r"^\w[\w-]*$")


def main() -> int:
    ap = argparse.ArgumentParser(description="Write one line to logs/log.md, newest first.")
    ap.add_argument("job", help="the pass name, e.g. build or render")
    ap.add_argument("message", help="what happened, one terse line")
    ap.add_argument("--at", default=None, metavar="'YYYY-MM-DD HH:MM'",
                    help="timestamp to record (default: now)")
    args = ap.parse_args()

    if not PASS_RE.match(args.job):
        print(f"log-line: '{args.job}' is not a usable pass name (letters, digits, - and _).")
        return 1

    if args.at:
        try:
            when = dt.datetime.strptime(args.at, "%Y-%m-%d %H:%M")
        except ValueError:
            print(f"log-line: --at '{args.at}' is not 'YYYY-MM-DD HH:MM'.")
            return 1
    else:
        when = dt.datetime.now()

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

    entry = "{:%Y-%m-%d %H:%M} · {} · {}".format(when, args.job, args.message.strip())
    lines.insert(at + 1, entry)

    body = "\n".join(lines)
    if not body.endswith("\n"):
        body += "\n"
    with io.open(RUN_LOG, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)

    sys.stdout.reconfigure(errors="replace")
    print(f"log-line: wrote to the top of logs/log.md - {entry}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
