#!/usr/bin/env python3
"""lint-messages.py — the two caps on logs/messages-for-bill.md, counted in code.

Strategic review task 4. The file's own preamble states both caps; this is what makes
them real, because a cap nobody counts drifts — that file once reached ten blocks and
102 lines with nothing measuring it.

- **At most five open blocks.** At the cap a run does not write a sixth: it takes the
  conservative option itself and logs it in `logs/log.md` (`CLAUDE.md` -> *Be decisive*).
- **At most 80 words per block**, heading excluded. Detail belongs in git or in
  `documentation/`; a block is what would have been asked, not the analysis behind it.

The word cap applies **forward only**, to blocks dated on or after 2026-08-28 — the day
it entered code. An older block a rule postdates is reported, never failed: failing it
would press for an edit to a message Bill may not have read, and only he clears this
file.

Run it after writing a block (both runbooks' ending sequences name it). Exit 0 clean,
1 a cap is broken, 2 the file or its marker is missing.

Usage:  python scripts/lint-messages.py
        python scripts/lint-messages.py --file some/other.md    # for tests
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MESSAGES = os.path.join(ROOT, "logs", "messages-for-bill.md")
MARKER = "<!-- newest first: a new block goes directly below this line -->"

BLOCK_CAP = 5
BLOCK_WORD_CAP = 80
CAP_FROM = dt.date(2026, 8, 28)

HEADING = re.compile(r"^## (\d{4}-\d{2}-\d{2})")


def blocks(text: str) -> list[tuple[str, dt.date | None, int]]:
    """[(heading, date-or-None, body word count), ...] for everything under the marker."""
    try:
        body = text.split(MARKER, 1)[1]
    except IndexError:
        raise ValueError("no newest-first marker")
    out = []
    heading, date, words = None, None, 0
    for line in body.splitlines():
        m = HEADING.match(line)
        if m:
            if heading is not None:
                out.append((heading, date, words))
            heading = line.strip()
            try:
                date = dt.date.fromisoformat(m.group(1))
            except ValueError:
                date = None
            words = 0
        elif heading is not None:
            words += len(line.split())
    if heading is not None:
        out.append((heading, date, words))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Count the caps on messages-for-bill.md.")
    ap.add_argument("--file", default=MESSAGES, help=argparse.SUPPRESS)
    args = ap.parse_args()

    if not os.path.exists(args.file):
        print(f"lint-messages: {args.file} does not exist.")
        return 2
    text = io.open(args.file, encoding="utf-8").read()
    try:
        found = blocks(text)
    except ValueError:
        print("lint-messages: the file carries no newest-first marker, so where the "
              "blocks begin cannot be established. Expected the line:")
        print(f"  {MARKER}")
        return 2

    failed = False

    if len(found) > BLOCK_CAP:
        failed = True
        print(f"lint-messages: {len(found)} open blocks against the cap of {BLOCK_CAP}. "
              f"At the cap a run does not write another - it takes the conservative "
              f"option and logs it in logs/log.md.")

    for heading, date, words in found:
        if words <= BLOCK_WORD_CAP:
            continue
        if date is not None and date < CAP_FROM:
            print(f"lint-messages: note - '{heading}' is {words} words against the cap "
                  f"of {BLOCK_WORD_CAP}, and predates the cap ({CAP_FROM}); left to "
                  f"Bill to clear.")
        else:
            failed = True
            print(f"lint-messages: '{heading}' is {words} words against the cap of "
                  f"{BLOCK_WORD_CAP}. Say what happened, what the run did, what the "
                  f"options are - the analysis belongs in documentation/, the detail "
                  f"in git.")

    if not failed:
        print(f"lint-messages: ok - {len(found)} block(s), cap {BLOCK_CAP}; word cap "
              f"{BLOCK_WORD_CAP} holds on every block it binds.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
