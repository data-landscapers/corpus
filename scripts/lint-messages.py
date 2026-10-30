#!/usr/bin/env python3
"""lint-messages.py — the rules on the share's messages-for-bill.md, counted in code.

The file moved from `logs/` to the share on 2026-10-02 *(Bill)*, beside the notes he
already reads there. It is still CORPUS's file, CORPUS to Bill; `CORPUS_OSINT_XFER`
overrides where the share is.

**There is no cap on the number of blocks** *(Bill, 2026-10-23)*. Five used to be the
limit, and at five a run took the conservative option and logged it instead; on 2026-10-23
that sent eight ladder questions to `logs/log.md`, where nobody reads them. Bill reads this
file, and what is owed him goes in it. What still binds:

- **At most 80 words per block**, heading excluded. Detail belongs in git or in
  `documentation/`; a block is what would have been asked, not the analysis behind it.
- **A struck block is gone, not annotated.** The run that settles a block's subject
  deletes the block in the same commit; a block edited to say it is settled still reads
  as open to the next run.
- **Every block carries a number, and a number is never reused** *(Bill, 2026-10-23)*:
  `## 12 · 2026-10-23 13:32 · job`. Bill replies by number. The preamble's *Next message
  takes **N*** issues them, as the notes' counters do; a closed number stays retired.
  The `· deploy` block is a state, not a message, and goes unnumbered.
- **At most one `· deploy` block.** A stuck deploy is a state, not a history: the newer
  replaces the older; `scripts/deploy-state.py` exit 0 is what settles it.
- **Every indicator id a block names exists** *(Bill, 2026-10-30, message 49)*: in
  `lookups/indicators.csv` or as a study's sub-indicator. Bill looks an id up; one that
  resolves nowhere costs him a question.

**Why the strike check refuses an annotation rather than discounting it.** This file is
read by a person scanning for what is owed him, and a settled block is noise in exactly
that place. Git holds what the block said and the commit that struck it holds why, so
nothing is lost by deletion — the reasoning the share applies to a closed note, minus the
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
import csv
import datetime as dt
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARE = os.environ.get("CORPUS_OSINT_XFER", r"C:\corpus-osint-xfer")
MESSAGES = os.path.join(SHARE, "messages-for-bill.md")
MARKER = "<!-- newest first: a new block goes directly below this line -->"

BLOCK_WORD_CAP = 80
CAP_FROM = dt.date(2026, 8, 28)

HEADING = re.compile(r"^## (?:(\d+) · )?(\d{4}-\d{2}-\d{2})")
NEXT = re.compile(r"Next message takes \*\*(\d+)\*\*")
ANY_HEADING = re.compile(r"^## ")
# `## 2026-10-02 08:10 · deploy` — a state, so at most one is open.
DEPLOY_HEADING = re.compile(r"^## (?:\d+ · )?\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2})? · deploy\s*$")

# **What a struck-but-present block looks like.** Two shapes, both of them an edit made
# instead of a deletion: a heading struck through or prefixed out of its dated form, and a
# body line opening with an assertion that the block is closed. The list is short on
# purpose — a word like *done* or *answered* opens a perfectly ordinary bullet about what
# a run did, and a check that fired on those would be one nobody could write a block past.
INDICATOR = re.compile(r"`([a-z]+\.[a-z0-9.]+--[a-z0-9-]+)`")


def known_ids() -> set[str]:
    """Every indicator id Bill can look up: the lookup's rows and the studies' sub-indicators."""
    with io.open(os.path.join(ROOT, "lookups", "indicators.csv"), encoding="utf-8") as f:
        ids = {r["indicator_id"] for r in csv.DictReader(f)}
    for p in glob.glob(os.path.join(ROOT, "maturity", "*", "study.json")):
        with io.open(p, encoding="utf-8") as f:
            ids.update(s["indicator_id"] for s in json.load(f).get("sub_indicators", []))
    return ids


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
                date = dt.date.fromisoformat(m.group(2)) if m else None
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
    ap = argparse.ArgumentParser(description="Check the rules on messages-for-bill.md.")
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

    deploys = sum(1 for heading, *_ in found if DEPLOY_HEADING.match(heading))

    numbers = []
    for heading, *_ in found:
        if DEPLOY_HEADING.match(heading):
            continue
        m = HEADING.match(heading)
        if not m or not m.group(1):
            failed = True
            print(f"lint-messages: '{heading}' carries no number. Take the preamble's "
                  f"'Next message takes **N**', write it as '## N · date · job', and "
                  f"increment the counter.")
        else:
            numbers.append(int(m.group(1)))
    dupes = sorted({n for n in numbers if numbers.count(n) > 1})
    if dupes:
        failed = True
        print(f"lint-messages: message number(s) {dupes} used twice. A number is issued "
              f"once and never reused.")
    nxt = NEXT.search(text.split(MARKER, 1)[0])
    if numbers and (not nxt or int(nxt.group(1)) <= max(numbers)):
        failed = True
        print(f"lint-messages: the preamble's 'Next message takes **N**' must exceed the "
              f"highest number in use ({max(numbers)}).")

    ids = known_ids()
    for bad in sorted({m.group(1) for m in INDICATOR.finditer(text.split(MARKER, 1)[1])} - ids):
        failed = True
        print(f"lint-messages: `{bad}` is no indicator id: not in lookups/indicators.csv or "
              f"any study's sub-indicators. Copy the id from study.json.")

    if deploys > 1:
        failed = True
        print(f"lint-messages: {deploys} deploy blocks. A stuck deploy is one state - "
              f"the newer replaces the older, it does not join it.")

    for heading, date, words, struck in found:
        if not struck:
            continue
        failed = True
        print(f"lint-messages: '{heading}' is annotated as settled, not struck: "
              f"{struck[0][:60]!r}. A block whose subject is settled is deleted in the "
              f"commit that settles it - git holds what it said. An annotated block "
              f"still reads as open.")

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
        print(f"lint-messages: ok - {len(found)} open block(s); word cap "
              f"{BLOCK_WORD_CAP} holds on every block it binds; none annotated as "
              f"settled.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
