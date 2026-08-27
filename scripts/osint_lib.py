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

# `sweep_closed: 2026-08-26 11:49 · ingest_started: 2026-08-26 11:50`, one line under the run's
# heading — usually with a blank line between, which is why this is matched against the file
# rather than against the line immediately following. OSINT stamps it on every path that admits
# anything to `raw/` (`wiki/reference.md` §6a, from 2026-08-26).
_SWEEP_CLOSED = re.compile(r"^sweep_closed:\s*(\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2})?)\b")


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


def sweep_closed() -> dt.datetime | None:
    """When collection stopped, as OSINT states it — `sweep_closed` in `logs/ingested_log.md`.

    **This is the bulletin's *Last updated*, and it is now a fact rather than a derivation**
    *(OSINT `notes-for-corpus.md` note 13, 2026-08-26, closing its own note 45)*. What a reader
    is being told is *how recent is the material here*, and the defensible answer is the point
    after which nothing more could have been caught. Corpus had no artefact recording that, so
    it derived one — from the start of the newest ingest run, found by clustering headings — and
    the derivation failed twice in three days in opposite directions. From 2026-08-26 every path
    that admits anything to `raw/` stamps the moment itself, so there is nothing left to infer.

    **Retired with the derivation: `ingest_started()` and `INGEST_RUN_GAP`.** A run was the
    newest cluster of headings with no gap wider than four hours, and the answer the earliest
    heading in it. On 2026-08-25 an unbroken stretch from a 15:30 top-up into the 21:12 nightly
    sweep had no gap that wide, so the walk merged them and answered 15:30 for material that
    stopped moving at 22:57; on 2026-08-26 three runs separated by 3h04 merged the same way and
    answered 08:04 for a page built on material collected to 12:20. Both are the same fault —
    the clustering constant is a guess about OSINT's working day — and note 13 asks for it to go
    rather than stand as a silent second answer.

    **`last_cycle_close()` is kept beside this, and not as a fallback: the sweep-cycle path does
    not stamp** *(2026-08-27, checked against the mirror)*. Note 13 says every path that admits
    to `raw/` now carries the fields, and names `reference.md` §6a, `SWEEP-BULLETIN.md` and
    `UPDATE-WIKI.md` — which is where the rule was written, and the cycle is not among them.
    Every `@UPDATE-WIKI` and `SWEEP-BULLETIN` run since 2026-08-26 12:20 is stamped; the five
    nightly-cycle slices of 2026-08-26 21:17 through 2026-08-27 03:25 are not. That is the path
    that matters most to a nightly build, and on that night reading `sweep_closed` alone would
    have answered 17:22 for material collected until after three in the morning. So
    `bulletin.stamps_for()` takes the **later of this and the cycle's own `End`**, which is the
    artefact the unstamped path does write. Both are stated facts about when collection stopped;
    neither is derived. `notes-for-osint.md` note 49 asks OSINT to stamp the cycle path too, at
    which point the close becomes redundant rather than wrong.

    **The maximum is taken, not the newest run's own value**, and the difference is not
    theoretical: where a run only drained a queue others staged, its `sweep_closed` is the newest
    `retrieved:` across what it admitted, which can be days older than the run before it. That is
    a true statement about *that* run's material and a false one about the page, which carries
    every run's. The maximum is the point after which nothing in the base could have been caught,
    which is what the byline claims.

    Returns `None` where the log carries no such line at all — a mirror synced before 2026-08-26
    — and that is the only case the old readings are kept for. A file carrying some stamped runs
    and an unstamped newest one says so on stderr and still answers from the stamped ones, which
    understates freshness rather than overstating it.
    """
    runs = _runs()
    stamped = [closed for _, closed in runs if closed is not None]
    if not stamped:
        return None
    newest_head = max(head for head, _ in runs)
    if any(head == newest_head and closed is None for head, closed in runs):
        print(f"note: {os.path.basename(INGESTED_LOG)}'s newest heading "
              f"({newest_head:%Y-%m-%d %H:%M}) carries no sweep_closed line - answering from "
              f"the newest run that does, which understates freshness rather than overstating "
              f"it", file=sys.stderr)
    return max(stamped)


def last_cycle_close() -> dt.datetime | None:
    """When a sweep cycle last closed, from the rotation table's `End` column.

    A few minutes after the ingest that ran inside it — 00:05 against 00:14 on 2026-08-21 — and
    that is not crudeness, it is the same fact recorded a step later. **It is half of the
    bulletin's *Last updated*** *(2026-08-27)*: `sweep_closed()` is the other half, and
    `bulletin.stamps_for()` takes whichever is later, because the cycle path does not stamp
    `sweep_closed` and the two runs that do stamp it write no rotation row. Between them they
    cover every path that admits to `raw/`; neither does alone. `lint-osint-freshness.py` reads
    this as one of four clocks; `osint-cycle-ready.py` reads the same table for its own purposes
    and needs the whole row, not just the stamp.

    Unguarded in two ways its callers must handle, both of which follow from this being a mirror.
    A table synced before the closing row was written returns an **older** close than the ingest
    inside the same cycle, and a mistyped `End` is not checked against the clock here the way
    `_newest_stamp` checks an ingest stamp — there is one row to be wrong, so a maximum over the
    column is no protection.
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


def _runs() -> list[tuple[dt.datetime, dt.datetime | None]]:
    """Every believable ingest run in `ingested_log.md` as `(heading, sweep_closed | None)`.

    Pairing is what `_stamps` cannot do, and it is needed for one thing only: to tell a log with
    no `sweep_closed` anywhere (a mirror from before 2026-08-26) from one whose *newest* run
    happens not to carry it. The first is the fallback case; the second is a path OSINT has not
    covered, and the two want different things said about them.

    A `sweep_closed` line belongs to the heading above it, so the file is walked in order rather
    than scanned. Both stamps are filtered against the clock on the same terms as everywhere else
    here, and a `sweep_closed` later than its own heading is dropped: collection cannot have
    stopped after the ingest that read it, so that pairing is a typo rather than a fact.
    """
    if not os.path.exists(INGESTED_LOG):
        return []
    horizon = dt.datetime.now() + SKEW
    runs: list[tuple[dt.datetime, dt.datetime | None]] = []
    head: dt.datetime | None = None
    with open(INGESTED_LOG, encoding="utf-8") as fh:
        for line in fh:
            m = _INGEST_HEAD.match(line)
            if m:
                when = _parse(m.group(1))
                head = when if when is not None and when <= horizon else None
                if head is not None:
                    runs.append((head, None))
                continue
            m = _SWEEP_CLOSED.match(line)
            if m and head is not None and runs and runs[-1][1] is None:
                closed = _parse(m.group(1))
                if closed is None or closed > horizon:
                    continue
                if closed > head + SKEW:
                    print(f"note: {os.path.basename(INGESTED_LOG)} pairs sweep_closed "
                          f"{closed:%Y-%m-%d %H:%M} with an earlier heading "
                          f"{head:%Y-%m-%d %H:%M} - ignored", file=sys.stderr)
                    continue
                runs[-1] = (head, closed)
    return runs


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
    print(f"sweep closed  {sweep_closed() or '— not readable'}")
    print(f"last ingest   {last_ingest() or '— not readable'}")
    print(f"last close    {last_cycle_close() or '— not readable'}")
