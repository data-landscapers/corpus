#!/usr/bin/env python3
"""lint-messages.py — the caps on logs/messages-for-bill.md, counted in code.

Strategic review task 4, and task 38 for the third check. The file's own preamble states
the caps; this is what makes them real, because a cap nobody counts drifts — that file
once reached ten blocks and 102 lines with nothing measuring it.

- **At most five open blocks.** At the cap a run does not write a sixth: it takes the
  conservative option itself and logs it in `logs/log.md` (`CLAUDE.md` -> *Be decisive*).
- **At most 80 words per block**, heading excluded. Detail belongs in git or in
  `documentation/`; a block is what would have been asked, not the analysis behind it.
- **A struck block is gone, not annotated.** The run that settles a block's subject
  deletes the block in the same commit; a block edited to say it is settled still reads
  as open to the next run and still counts against the five.

**Why the third check refuses an annotation rather than discounting it.** The obvious
alternative is to let a block say it is closed and stop counting it, which would be the
cheaper rule and the wrong one: this file is read by a person scanning for what is owed
him, and a settled block is noise in exactly the place the cap exists to keep clear. Git
holds what the block said and the commit that struck it holds why, so nothing is lost by
deletion — which is the same reasoning the share applies to a closed note, minus the
number, because a message carries no citable identity to preserve.

The word cap applies **forward only**, to blocks dated on or after 2026-08-28 — the day
it entered code. An older block a rule postdates is reported, never failed: failing it
would press for an edit to a message Bill may not have read, and only he clears this
file.

Run it after writing a block, and after striking one (both runbooks' ending sequences
name it). Exit 0 clean, 1 a cap is broken or a block is annotated rather than struck,
2 the file or its marker is missing.

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
ANY_HEADING = re.compile(r"^## ")

# **What a struck-but-present block looks like.** Two shapes, both of them an edit made
# instead of a deletion: a heading struck through or prefixed out of its dated form, and a
# body line opening with an assertion that the block is closed. The list is short on
# purpose — a word like *done* or *answered* opens a perfectly ordinary bullet about what
# a run did, and a check that fired on those would be one nobody could write a block past.
STRUCK_HEADING = re.compile(r"^## .*~~|^## +[x\u00d7]\b", re.I)
SETTLED_LINE = re.compile(
    r"^\s*(?:[-*]\s+)?(?:~~|\*{1,2}\s*(?:settled|closed|resolved|struck|superseded)\b)",
    re.I)


def blocks(text: str) -> list[tuple[str, dt.date | None, int, list[str]]]:
    """[(heading, date-or-None, body word count, struck lines), ...] under the marker.

    A heading is any `## ` line, not only a well-formed dated one: a block struck by
    editing its heading would otherwise be swallowed into the block above it and counted
    as that block's body, which is the opposite of what the third check is for.
    """
    try:
        body = text.split(MARKER, 1)[1]
    except IndexError:
        raise ValueError("no newest-first marker")
    out = []
    heading, date, words, struck = None, None, 0, []
    for line in body.splitlines():
        if ANY_HEADING.match(line):
            if heading is not None:
                out.append((heading, date, words, struck))
            heading = line.strip()
            m = HEADING.match(line)
            try:
                date = dt.date.fromisoformat(m.group(1)) if m else None
            except ValueError:
                date = None
            words, struck = 0, []
            if STRUCK_HEADING.match(line):
                struck.append(heading)
        elif heading is not None:
            words += len(line.split())
            if line.strip() and SETTLED_LINE.match(line):
                struck.append(line.strip())
    if heading is not None:
        out.append((heading, date, words, struck))
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

    for heading, date, words, struck in found:
        if not struck:
            continue
        failed = True
        print(f"lint-messages: '{heading}' is annotated as settled, not struck: "
              f"{struck[0][:60]!r}. A block whose subject is settled is deleted in the "
              f"commit that settles it - git holds what it said. An annotated block "
              f"still reads as open and still counts against the {BLOCK_CAP}.")

    for heading, date, words, _ in found:
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
              f"{BLOCK_WORD_CAP} holds on every block it binds; none annotated as "
              f"settled.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
