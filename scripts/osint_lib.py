#!/usr/bin/env python3
r"""
osint_lib.py — the read-only facts Corpus takes from the OSINT mirror.

`C:\OSINT` is a **mirror** of a master repository on OSINT's own drive, refreshed whenever a
`SWEEP-CYCLE` completes or by hand after a manual run. Corpus reads it and never writes to it
(`CLAUDE.md`, absolute since 2026-08-20). Two things follow and both are load-bearing here.

**A file read from a mirror reads as whatever the last sync left**, which is not the same as
what the master holds — so every reader in this module returns `None` rather than raising when
what it wants is absent, and every caller is expected to say which it got. A silent fallback to
a plausible-looking substitute is the failure this repo keeps finding in its own past.

**The mirror path is one constant.** `osint-cycle-ready.py` held its own copy until this module
existed and `bulletin.py` was about to hold a second; `CORPUS_OSINT_XFER` in `status_lib.py` is
the same arrangement for the exchange folder, and for the same reason — a move onto a mapped
share should be an environment variable, not an edit in three files.
"""

from __future__ import annotations

import datetime as dt
import os
import re

# Seen from this machine. `SWEEP-CYCLE.md` -> *Mirror* syncs `C:\OSINT` onto `O:\`, and this is
# the machine that share resolves back to.
MIRROR = os.environ.get("CORPUS_OSINT_MIRROR", r"C:\OSINT")

INGESTED_LOG = os.path.join(MIRROR, "logs", "ingested_log.md")
CYCLE_LOG = os.path.join(MIRROR, "logs", "sweep-cycle_log.md")

TS = "%Y-%m-%d %H:%M"

# `## 2026-08-21 00:05 (ingest Phase A, slice 4/10 — 10 items in, 8 admitted, …)`
_INGEST_HEAD = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\b")


def last_ingest() -> dt.datetime | None:
    """When OSINT's ingest last admitted anything to `raw/`, from `logs/ingested_log.md`.

    **This is the moment the corpus last moved**, which is what *when was this page last
    updated* is asking. The build clock answers *when did we last run*, and on a day when
    nothing came in those are different claims and only one of them is about the reader's
    material.

    The file is newest-first and every batch writes a `## {timestamp} (ingest …)` heading, so
    the first heading is the answer. It is read as the maximum rather than the first line
    anyway: the ordering is a convention OSINT keeps by hand, and a file that has slipped out
    of order should give a late answer rather than a wrong one.

    Returns `None` if the mirror is absent, the log is missing, or nothing in it parses — never
    a guess, and never today's date standing in for a fact about another repository.
    """
    return _newest_stamp(INGESTED_LOG, _INGEST_HEAD)


def last_cycle_close() -> dt.datetime | None:
    """When a sweep cycle last closed, from the rotation table's `End` column.

    A few minutes after the ingest that ran inside it — 00:05 against 00:14 on 2026-08-21 — so
    it is the cruder of the two and is here as a second opinion rather than a fallback. Nothing
    calls it yet; `osint-cycle-ready.py` reads the same table for its own purposes and needs the
    whole row, not just the stamp.
    """
    if not os.path.exists(CYCLE_LOG):
        return None
    header, best = None, None
    with open(CYCLE_LOG, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if header is None:
                header = cells
                if "End" not in header:
                    return None
                continue
            if len(cells) != len(header):
                continue
            when = _parse(dict(zip(header, cells)).get("End", ""))
            if when and (best is None or when > best):
                best = when
    return best


def _newest_stamp(path: str, pattern: re.Pattern) -> dt.datetime | None:
    if not os.path.exists(path):
        return None
    best = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = pattern.match(line)
            if not m:
                continue
            when = _parse(m.group(1))
            if when and (best is None or when > best):
                best = when
    return best


def _parse(text: str) -> dt.datetime | None:
    try:
        return dt.datetime.strptime(text.strip(), TS)
    except (ValueError, AttributeError):
        return None


if __name__ == "__main__":
    print(f"mirror        {MIRROR}")
    print(f"last ingest   {last_ingest() or '— not readable'}")
    print(f"last close    {last_cycle_close() or '— not readable'}")
