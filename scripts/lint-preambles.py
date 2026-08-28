#!/usr/bin/env python3
r"""lint-preambles.py — a channel file carries a pointer, not a copy of the rules.

Strategic review task 13. The conventions governing the exchange live in one place, the
share's `README.md` -> *Conventions*; the ones governing `logs/messages-for-bill.md` live
in `CLAUDE.md` -> *Be decisive*. Every other file carries a link and its own content.

Two things go wrong without a check, and both had happened. **Preambles grow**:
`notes-for-osint.md` carried 1,150 words above its first heading and 2,585 above its first
note, against 2,795 words of notes; `messages-for-bill.md` was 407 words of preamble over
one block. **Rules get restated**, and a rule stated twice is
one that will eventually disagree with itself - worse than a rule stated nowhere, because
both copies read as authoritative.

So this counts two things:

- **Preamble length**, capped at PREAMBLE_CAP words, measured down to the line where that
  file's content starts. Content below the boundary is the file's own substance and is not
  counted: `notes-for-osint.md`'s standing constraints are what the file is for.
- **Rules stated away from home.** Each phrase in RULES is distinctive enough to identify
  the rule it belongs to. It must appear in its home file and nowhere else. A note that is
  genuinely *about* a rule cites it by pointer.

**`CLAUDE.md` is not a duplicate and is not governed.** It carries the share's operating
rules because a CORPUS session loads it and may never open the share at all; the README is
the share's own documentation, written for both sides. Two files addressed to two readers
are not two copies of one rule, and a later pass should not "fix" this by deleting either.
The channel files are different: their reader is already in the folder and can follow a
link.

**A file the run cannot edit is reported, never failed.** `housekeeping-jobs.md` is OSINT's
register and `messages-from-bill.md` is Bill's; CORPUS reads both and fixes neither, and a
lint that fails on a file you may not touch is a lint that gets skipped. OSINT carries the
same assertion over its own files from `LINT.md` #24.

Usage:  python scripts/lint-preambles.py
        python scripts/lint-preambles.py --share some/other/dir   # for tests
Exit:   0 clean (advisories may still print), 1 a cap or a duplicate is broken in a file
        CORPUS owns, 2 a governed file or the share itself is missing.
"""
from __future__ import annotations

import argparse
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARE = os.environ.get("CORPUS_OSINT_XFER", r"C:\corpus-osint-xfer")

# Generous against what these files were (2,585 and 947 words), tight against what a
# pointer needs. The cap is on the preamble alone, so a file with a lot to say says it
# below its boundary.
PREAMBLE_CAP = 250

# Where a file's preamble stops, stated per file because the files are not one shape. A
# generic "first heading" rule reads `housekeeping-jobs.md`'s counter as the whole preamble
# and lets a thousand words of rules below it through unmeasured; a generic "first entry"
# rule counts `notes-for-osint.md`'s standing constraints, which are that file's substance,
# as preamble. Naming the boundary is shorter than a heuristic that gets both right.
HEADING = r"^## "
MARKER = r"^<!-- newest first:"
NOTE = r"^\*\*\d+\*\* |^## \d+ "
JOB = r"^x?\d+\. "
INDEX = r"^\| *Note *\|"

# (name, owned, where the preamble stops) - owned files fail, the rest are advisory.
SHARE_FILES = [
    ("README.md", True, HEADING),
    ("notes-for-osint.md", True, HEADING),
    ("notes-for-corpus.md", True, HEADING),
    ("notes-for-osint-resolved.md", True, INDEX + "|" + NOTE),
    ("notes-for-corpus-resolved.md", True, NOTE),
    ("housekeeping-jobs.md", False, JOB),           # OSINT's register
    ("housekeeping-jobs-resolved.md", False, JOB),  # OSINT's archive
    ("messages-from-bill.md", False, HEADING),      # Bill's channel
]
CORPUS_FILES = [(os.path.join("logs", "messages-for-bill.md"), True, MARKER)]

# A phrase, and the one file allowed to state it. Distinctive enough that a match is the
# rule and not an accident of ordinary prose - checked in both directions, so a phrase that
# stops appearing at home fails too rather than quietly disarming its own check.
RULES = [
    ("Numbers are never reused", "README.md"),
    ("Closing means moving", "README.md"),
    ("re-read before editing", "README.md"),
    ("does the committing here", "README.md"),
    ("as invisible as an uncommitted edit", "README.md"),
    ("Neither path is more correct", "README.md"),
    ("Reasoning lives in the repo that owns it", "README.md"),
    ("does not let you assign work in it", "README.md"),
    ("If a later run can undo it", "README.md"),
    ("the irreversible and the already-public", "CLAUDE.md"),
]

# The archives quote note text verbatim, including notes that were about a rule. Rewriting
# an archive to satisfy a lint would be falsifying it, so they are held to the preamble cap
# and nothing else.
NO_DUPLICATE_CHECK = {"notes-for-osint-resolved.md", "notes-for-corpus-resolved.md",
                      "housekeeping-jobs-resolved.md"}


def preamble_of(text: str, stop: str) -> str:
    """Everything above the line `stop` first matches.

    A file with no such line is all preamble, which is the right reading: an empty register
    that is nothing but rules is exactly the case the cap is for."""
    rx = re.compile(stop)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if rx.match(line):
            return "\n".join(lines[:i])
    return text


def flat(text: str) -> str:
    """The text with every run of whitespace collapsed to one space.

    These files are hard-wrapped, so a rule sits across a line break as often as not and a
    literal search for it finds nothing - which would leave the check reporting that a home
    file had dropped a rule it states perfectly well."""
    return re.sub(r"\s+", " ", text)


def read(path: str) -> str | None:
    try:
        return io.open(path, encoding="utf-8").read()
    except OSError:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Channel preambles are pointers, not copies.")
    ap.add_argument("--share", default=SHARE, help="the exchange folder")
    ap.add_argument("--root", default=ROOT, help="the CORPUS repo")
    args = ap.parse_args()

    if not os.path.isdir(args.share):
        print(f"lint-preambles: the share is not at {args.share}. Set CORPUS_OSINT_XFER "
              f"or pass --share.")
        return 2

    files = ([(os.path.join(args.share, n), n, owned, stop)
              for n, owned, stop in SHARE_FILES] +
             [(os.path.join(args.root, n), os.path.basename(n), owned, stop)
              for n, owned, stop in CORPUS_FILES])
    texts: dict[str, str] = {}
    failures: list[str] = []
    advisories: list[str] = []

    for path, name, owned, stop in files:
        text = read(path)
        if text is None:
            if owned:
                print(f"lint-preambles: {path} is missing.")
                return 2
            advisories.append(f"{name} is not present; nothing checked")
            continue
        texts[name] = flat(text)
        words = len(preamble_of(text, stop).split())
        if words > PREAMBLE_CAP:
            msg = (f"{name}: preamble is {words} words against the cap of {PREAMBLE_CAP}. "
                   f"State the rule once where it lives and leave a pointer here.")
            (failures if owned else advisories).append(msg)

    # The home file has to still say it, or the check is guarding an empty seat.
    home_texts = dict(texts)
    claude = read(os.path.join(args.root, "CLAUDE.md"))
    if claude is not None:
        home_texts["CLAUDE.md"] = flat(claude)

    for phrase, home in RULES:
        if home not in home_texts:
            advisories.append(f"cannot check '{phrase}': {home} was not read")
            continue
        if phrase not in home_texts[home]:
            failures.append(f"{home} no longer states '{phrase}'. Either it moved and this "
                            f"check needs its new home, or a rule was dropped.")
            continue
        for _path, name, owned, _stop in files:
            if name == home or name not in texts or name in NO_DUPLICATE_CHECK:
                continue
            if phrase in texts[name]:
                msg = (f"{name} restates '{phrase}', which belongs in {home}. Cite it as a "
                       f"pointer; two copies of a rule eventually disagree.")
                (failures if owned else advisories).append(msg)

    for msg in advisories:
        print(f"lint-preambles: note - {msg}")
    for msg in failures:
        print(f"lint-preambles: FAIL - {msg}")
    if failures:
        return 1
    print(f"lint-preambles: ok - {len(texts)} file(s), preambles within {PREAMBLE_CAP} "
          f"words, {len(RULES)} rule(s) stated once.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
