#!/usr/bin/env python3
r"""lint-notes.py — a note names the output it bears on, or it is not a note.

Strategic review task 16. The template is one line, `Affects:`, directly under a note's
title, and it names an artefact or a piece of work already commissioned. The review's
finding is what it is for: around a third of the notes in the archive were about the other
side's internal housekeeping — repo size, the wording of a process file, sub-agent spend —
and one said of itself that nothing in the reader's repo depended on the answer. None of
them could have filled this line in.

**What a lint can and cannot do here.** It cannot judge whether an `Affects:` line is true;
a writer determined to fill it falsely is a different failure and a different fix. What it
can do is make the field compulsory and refuse the evasions, and that is most of the value:
the rule works by forcing the question *before* the note is written, not by adjudicating the
answer afterwards. So this checks that every open note carries the line, that it names
something concrete, and that it does not say `n/a`.

Checked on every open note in both directions, and on the shape of a note too, because the
number, tag and date are what the closing rule and the reviews cite by hand.

**Hard on `notes-for-osint.md`, advisory on `notes-for-corpus.md`.** CORPUS writes the
first and OSINT the second; the same ownership split `lint-preambles.py` uses, for the same
reason — a lint that fails on a file the run may not edit is one that gets skipped. OSINT
asserts the mirror image over its own outbox.

Usage:  python scripts/lint-notes.py
        python scripts/lint-notes.py --share some/other/dir   # for tests
Exit:   0 clean (advisories may still print), 1 a note CORPUS wrote is missing the line or
        malformed, 2 the share or a notes file is missing.
"""
from __future__ import annotations

import argparse
import io
import os
import re
import sys

SHARE = os.environ.get("CORPUS_OSINT_XFER", r"C:\corpus-osint-xfer")

# (file, does a failure here fail the run). CORPUS writes its outbox; OSINT writes the other.
FILES = [("notes-for-osint.md", True), ("notes-for-corpus.md", False)]

# `**49** [ACT] (2026-08-27) - **Title.**` — the shape every note in both archives uses.
NOTE_RE = re.compile(r"^\*\*(\d+)\*\*\s*(?:\[(\w+)\])?\s*(?:\((\d{4}-\d{2}-\d{2})\))?")
AFFECTS_RE = re.compile(r"^\s*(?:\*\*)?Affects:(?:\*\*)?\s*(.*)$", re.I)
TAGS = {"CRITICAL", "ACT", "FYI"}

# How far below the title the line may sit. One blank line and the `Affects:` line is the
# whole allowance: a field the reader has to hunt for is not a template, and a note that
# buries it three paragraphs down has written a sentence, not filled in a field.
LOOKAHEAD = 4

# What counts as naming something. Deliberately broad — the field is a forcing function, not
# a taxonomy — but each alternative names a thing that exists somewhere a reader can go.
CONCRETE = re.compile(
    r"site/|outputs/|raw/|wiki/|lookups/|new-queue"          # a path in either repo
    r"|\.md\b|\.csv\b|\.py\b|\.json\b|\.pdf\b"               # a file
    r"|\breview task \d|\bnote \d|\bjob \d"                  # commissioned work, by number
    r"|\b[A-Z]{3}-(?:status|progress|monthly)\b"             # a named report
    r"|\bbulletin\b|\bcatalogue\b|\bfinance\b|\bhome page\b",  # a named published surface
    re.I)

# The ways a compulsory field gets filled in with nothing. Matched against the whole value,
# so a line that says only this is refused and one that mentions it in passing is not.
EVASIONS = re.compile(
    r"^(?:-|—|n/?a|none|nothing|tbd|tbc|unknown|various|general|"
    r"housekeeping|internal|no output|not applicable)\.?$", re.I)


def notes(text: str) -> list[tuple[int, str, str | None, str | None, list[str]]]:
    """(line, number, tag, date, the lines from the title to the next note) per note."""
    lines = text.split("\n")
    starts = [(i, NOTE_RE.match(l)) for i, l in enumerate(lines)]
    starts = [(i, m) for i, m in starts if m]
    out = []
    for k, (i, m) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        out.append((i + 1, m.group(1), m.group(2), m.group(3), lines[i:end]))
    return out


def affects_of(body: list[str]) -> str | None:
    """The `Affects:` value, or None. Only the first few lines count — see LOOKAHEAD."""
    for line in body[:LOOKAHEAD]:
        m = AFFECTS_RE.match(line)
        if m:
            return m.group(1).strip()
    return None


def problems(number: str, tag: str | None, date: str | None,
             body: list[str]) -> list[str]:
    """Everything wrong with one note, in the order a writer would fix it."""
    found = []
    if tag not in TAGS:
        found.append(f"note {number} carries no tag - one of {sorted(TAGS)} goes after the "
                     f"number, and which one is the reversibility test")
    if not date:
        found.append(f"note {number} carries no (YYYY-MM-DD) date")
    value = affects_of(body)
    if value is None:
        found.append(f"note {number} has no `Affects:` line in its first {LOOKAHEAD} lines. "
                     f"Name the artefact or the commissioned work it bears on; a note that "
                     f"would have to say nothing is not a note")
    elif not value:
        found.append(f"note {number}'s `Affects:` line is empty")
    elif EVASIONS.match(value):
        found.append(f"note {number}'s `Affects:` says '{value}', which is the field filled "
                     f"in with nothing. If there is no output, there is no note")
    elif not CONCRETE.search(value):
        found.append(f"note {number}'s `Affects:` names nothing a reader can go to: "
                     f"'{value}'. A path, a file, a named report, or work already "
                     f"commissioned cited by number")
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description="A note names the output it bears on.")
    ap.add_argument("--share", default=SHARE, help="the exchange folder")
    args = ap.parse_args()

    if not os.path.isdir(args.share):
        print(f"lint-notes: the share is not at {args.share}. Set CORPUS_OSINT_XFER or "
              f"pass --share.")
        return 2

    failures: list[str] = []
    advisories: list[str] = []
    counted = 0

    for name, owned in FILES:
        path = os.path.join(args.share, name)
        if not os.path.exists(path):
            print(f"lint-notes: {path} is missing.")
            return 2
        text = io.open(path, encoding="utf-8").read()
        for line, number, tag, date, body in notes(text):
            counted += 1
            for msg in problems(number, tag, date, body):
                (failures if owned else advisories).append(f"{name}:{line} {msg}")

    for msg in advisories:
        print(f"lint-notes: note - {msg}")
    for msg in failures:
        print(f"lint-notes: FAIL - {msg}")
    if failures:
        return 1
    print(f"lint-notes: ok - {counted} open note(s), each naming what it bears on.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
