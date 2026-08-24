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
import sys

# Seen from this machine. `SWEEP-CYCLE.md` -> *Mirror* syncs `C:\OSINT` onto `O:\`, and this is
# the machine that share resolves back to.
MIRROR = os.environ.get("CORPUS_OSINT_MIRROR", r"C:\OSINT")

INGESTED_LOG = os.path.join(MIRROR, "logs", "ingested_log.md")
CYCLE_LOG = os.path.join(MIRROR, "logs", "sweep-cycle_log.md")

TS = "%Y-%m-%d %H:%M"
DATE = "%Y-%m-%d"

# `## 2026-08-21 00:05 (ingest Phase A, slice 4/10 — 10 items in, 8 admitted, …)`, and since
# 2026-08-23 the time is often simply absent: `## 2026-08-24 (ingest Phase A - bulletin-2026-08-24,
# slice 1 of 3; …)`. Both forms are read, and a date on its own is taken as midnight — `_parse`
# carries why, and why midnight rather than the end of the day.
_INGEST_HEAD = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2})?)\b")


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


# How long a quiet stretch has to be before it separates one ingest run from the next. A run is
# a night's worth of slices written over several hours, so the gaps *inside* one are minutes: on
# 2026-08-22/23 the widest was 75 minutes (04:05 to 05:20) and the run held 40-odd slices. The
# gaps *between* runs are the hours OSINT is not sweeping - 9h46m between the 21st's run and the
# 22nd's top-up, 14h20m between that top-up and the 22nd's nightly. Four hours sits well clear of
# both, and the failure it courts is merging two runs, which reports an earlier start: stale
# rather than false, which is the direction everything in this module errs in.
INGEST_RUN_GAP = dt.timedelta(hours=4)


def ingest_started() -> dt.datetime | None:
    """When OSINT's most recent ingest run **began**, from `logs/ingested_log.md`.

    **This is the bulletin's *Last updated*, because it is the moment collection stopped**
    *(Bill, 2026-08-23)*. What a reader is being told is *how recent is the material here*, and
    the honest answer is the point after which nothing more could have been caught - the end of
    the last sweep, `SWEEP-COUNTRY-DEEP` on a nightly cycle. Ingest is the step that follows
    collection and reads what it staged, so **the start of ingest is the proxy for the end of
    collection**, and the two are minutes apart: on 2026-08-22 the last country-deep batch closed
    at 23:29 and the first slice ingested at 23:55.

    `last_ingest()` - the *newest* stamp - answers a different question and gets it wrong for
    this one. Ingest of a night's catch runs for hours after collection has finished, so on
    2026-08-23 it read 05:20 for material that stopped moving at 23:55 the evening before,
    overstating the freshness of the page by five and a half hours. Nothing was collected in
    those hours; they were spent writing up what already had been.

    A run is the newest cluster of headings with no gap longer than `INGEST_RUN_GAP` in it, and
    the answer is the earliest heading in that cluster. Clustering also makes this the more
    robust of the two readings: a single mistyped heading can only extend a run's tail, where
    under `last_ingest()`'s maximum it became the answer outright - which is exactly what a
    header mistyped `12:00` did to this byline on 2026-08-23.

    Returns `None` on the same terms as everything else here: an absent mirror, a missing log or
    nothing parseable, never a guess.
    """
    stamps = _stamps(INGESTED_LOG, _INGEST_HEAD)
    if not stamps:
        return None
    start = stamps[-1]
    for newer, older in zip(stamps[-1:0:-1], stamps[-2::-1]):
        if newer - older > INGEST_RUN_GAP:
            break
        start = older
    return start


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


# How far past the clock a stamp may sit and still be believed. The mirror is written by a
# machine that is not this one, so a stamp a minute or two ahead is skew rather than error;
# anything further ahead is a claim about work that has not happened yet.
SKEW = dt.timedelta(minutes=5)


def _newest_stamp(path: str, pattern: re.Pattern) -> dt.datetime | None:
    """The newest stamp in the file, ignoring any that is in the future.

    **The maximum is taken because the file's newest-first ordering is a convention kept by
    hand**, so a file that has slipped out of order gives a late answer rather than a wrong one.
    The cost of that is a single mistyped heading outranking every correct one, and on
    2026-08-23 one did: `ingest-33` ran at 01:12 by `logs/log.md` and was written into
    `ingested_log.md` as `12:00`, so the bulletin's byline said the page had last been updated
    four hours into the reader's future. Every other reading of the file was correct and the
    wrong one won by being the largest.

    A stamp later than now cannot be a moment the material moved, whatever else it is, so it is
    dropped and the run says so on stderr — the next-newest true reading is a slightly stale
    answer, which is a different thing from a false one. `SKEW` keeps a stamp written seconds
    ahead by another machine's clock from being thrown away."""
    stamps = _stamps(path, pattern)
    return stamps[-1] if stamps else None


def _stamps(path: str, pattern: re.Pattern) -> list[dt.datetime]:
    """Every believable stamp in the file, oldest first. Future stamps are dropped here so that
    both readers get the same view of the file and neither has to remember to filter."""
    if not os.path.exists(path):
        return []
    found, dateless = [], 0
    horizon = dt.datetime.now() + SKEW
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = pattern.match(line)
            if not m:
                continue
            raw = m.group(1).strip()
            when = _parse(raw)
            if when is None:
                continue
            if when > horizon:
                print(f"note: {os.path.basename(path)} carries a stamp in the future "
                      f"({when:%Y-%m-%d %H:%M}) - ignored", file=sys.stderr)
                continue
            dateless += len(raw) == len("0000-00-00")
            found.append(when)
    # Said rather than absorbed, on the same terms as the future stamp above. Reading a whole
    # day at midnight is the right answer at the wrong precision, and the run that stops
    # noticing is the run that publishes it as though it were the time OSINT wrote.
    if dateless:
        print(f"note: {os.path.basename(path)} carries {dateless} heading(s) dated with no time "
              f"- read as 00:00, which understates freshness rather than overstating it",
              file=sys.stderr)
    return sorted(found)


def _parse(text: str) -> dt.datetime | None:
    """A heading’s stamp, from `YYYY-MM-DD HH:MM` or from a bare `YYYY-MM-DD`.

    **A date with no time is read as midnight** *(2026-08-24)*. OSINT stopped writing the time
    into `ingested_log.md` headings on 2026-08-23 — 19 of the 63 headings there carry a date
    alone — and until this was read the whole of both days failed to parse, so every reader
    here answered from the newest heading that still had a time on it: `2026-08-23 10:20`, on an
    afternoon when 16 records had already been admitted that morning. The bulletin’s byline
    takes both its stamps from this file, so that would have been published as fact, and a
    format the reader silently cannot see is exactly the stale-looking-fresh failure the rest of
    this module is built to refuse.

    Midnight rather than the end of the day, because the answer feeds *how recent is the
    material here*: a run that admitted at 13:18 reported as `00:00` is stale by thirteen hours,
    where the same run reported as `23:59` is a claim about collection that had not happened
    yet. Stale rather than false, which is the direction everything here errs in.
    """
    text = (text or "").strip()
    for fmt in (TS, DATE):
        try:
            return dt.datetime.strptime(text, fmt)
        except (ValueError, AttributeError):
            continue
    return None


if __name__ == "__main__":
    print(f"mirror        {MIRROR}")
    print(f"ingest began  {ingest_started() or '— not readable'}")
    print(f"last ingest   {last_ingest() or '— not readable'}")
    print(f"last close    {last_cycle_close() or '— not readable'}")
