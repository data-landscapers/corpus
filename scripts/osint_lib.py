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
import io
import json
import os
import re
import subprocess
import sys

# Seen from this machine. `SWEEP-CYCLE.md` -> *Mirror* syncs `C:\OSINT` onto `O:\`, and this is
# the machine that share resolves back to.
MIRROR = os.environ.get("CORPUS_OSINT_MIRROR", r"C:\OSINT")

# The cycle manifest, written by `SWEEP-CYCLE` and `SWEEP-BULLETIN` after the final commit
# and before the mirror (OSINT `notes-for-corpus` 16, strategic review task 14). It is the
# whole of what Corpus needs to know about a close, and it is why the two log reads below
# are now a fallback rather than the source. `UPDATE-WIKI` does not mirror and writes none;
# its material arrives at the next cycle close, which does.
MANIFEST = os.path.join(MIRROR, "cycle-manifest.json")

# A reader that meets a schema it does not know stops rather than guesses (note 16). A
# field that changed meaning under the same number is the one failure a fallback cannot
# catch, because both readings parse.
MANIFEST_SCHEMA = 1

# Retired in favour of the manifest and kept only until one has been read on the mirror.
# `scripts/lint-interface.py` lists both as exceptions to the interface and fails when they
# go, so the list cannot outlive them.
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


def mirror_head(path: str | None = None) -> str | None:
    """The commit the mirror is holding, or None if git will not say."""
    try:
        out = subprocess.run(["git", "-C", path or MIRROR, "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None if out.returncode == 0 else None


def _is_ancestor(commit: str, repo: str | None = None) -> bool:
    """Whether `commit` is in the history the mirror is holding.

    This is what separates *the manifest is older than the tree* from *the manifest and the
    tree are not the same repository*. Only `SWEEP-CYCLE` and `SWEEP-BULLETIN` write a
    manifest, and OSINT commits from passes that do neither, so a manifest naming an earlier
    commit than HEAD is the ordinary state and not a fault - it was measured firing within
    minutes of this reader being written. A commit that is *not* an ancestor is the real
    fault: a tree and an account of it that arrived from different histories."""
    try:
        out = subprocess.run(
            ["git", "-C", repo or MIRROR, "merge-base", "--is-ancestor", commit, "HEAD"],
            capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return False
    return out.returncode == 0


def read_manifest(path: str | None = None) -> tuple[dict | None, str]:
    """`(the manifest, why it is or is not usable)`.

    Four ways it is refused, and the reason is returned rather than logged because every
    caller has somewhere better to put it than this module does:

    **Absent.** The ordinary case until the next cycle close, and not an error — the two
    passes that write it are the two that mirror.

    **Unparseable.** The manifest is written before the mirror copies, so a truncated file
    is a copy caught in the middle, not a corrupt source.

    **A schema this does not know.** Refused outright (note 16). Guessing at an unknown
    schema is the one failure the fallback cannot catch, because a field that changed
    meaning under a new number still parses under the old reading.

    **`head` naming a commit the mirror's history does not contain.** A tree and an account
    of it that arrived from different histories. Note 16 asks for a plain equality check
    here, and equality is too strict: only the two mirroring passes write a manifest and
    OSINT commits from passes that do neither, so `head` trailing HEAD is the ordinary
    state - measured firing within minutes of this being written. A manifest whose `head`
    is an **ancestor** of HEAD is accepted and says so, because its stamps then understate
    freshness, which is the direction this repo prefers to be wrong in.

    Where git cannot answer at all the head check is skipped rather than failed — an absent
    git is not evidence of a bad copy, and the schema and shape checks have already run.
    """
    path = path or MANIFEST
    if not os.path.exists(path):
        return None, "no cycle manifest on the mirror yet"
    try:
        data = json.loads(io.open(path, encoding="utf-8").read())
    except (OSError, ValueError) as exc:
        return None, f"the cycle manifest will not parse ({exc}) - a half-copied mirror"
    if not isinstance(data, dict):
        return None, "the cycle manifest is not an object"
    if data.get("schema") != MANIFEST_SCHEMA:
        return None, (f"the cycle manifest is schema {data.get('schema')!r}, and this reads "
                      f"{MANIFEST_SCHEMA}. A schema this does not know is refused rather "
                      f"than guessed at")
    head = data.get("head")
    repo = os.path.dirname(path) or None
    here = mirror_head(repo)
    if head and here and head != here:
        if _is_ancestor(head, repo):
            return data, (f"the cycle manifest, written at {head[:8]} and the mirror since "
                          f"moved to {here[:8]} - its stamps understate, which is the safe "
                          f"direction")
        return None, (f"the cycle manifest names {head[:8]}, which is not in the history the "
                      f"mirror is holding at {here[:8]} - a half-copied mirror, not a stale "
                      f"manifest")
    return data, "the cycle manifest"


def _stamp(text) -> dt.datetime | None:
    r"""A manifest collection or rotation stamp, read as naive local time.

    **The manifest says every stamp is UTC, and its collection and rotation stamps are not**
    *(measured 2026-08-28; `notes-for-osint` 55)*. They are copied verbatim out of OSINT's
    own logs, which are local: the manifest of 2026-08-28 08:36 reports
    `rotation.newest_close` as `19:07`/`21:31` and `logs/sweep-cycle_log.md` carries that row
    as `19:07`/`21:31`, and it reports `collection.last_admission` as `20:36` against the same
    number in the newest `ingested_log.md` heading. The two fields that do come from a clock
    rather than a log — `head_committed_utc` and `written_utc`, both `08:36` — are true UTC,
    against a `git log` on the mirror putting that commit at 09:36 +0100. So the manifest
    carries two clocks under one name.

    Reading these as local is the conservative half. Converting would move the published
    byline an hour **later** than the moment collection actually stopped, which is a claim
    about work that had not happened; reading them as local is at worst the same value the
    log path already published. When OSINT settles the field, this is the one place to
    change."""
    if not isinstance(text, str) or not text.strip():
        return None
    try:
        return dt.datetime.strptime(text.strip(), TS)
    except ValueError:
        return None


def _manifest_stamp(*keys: str) -> dt.datetime | None:
    """One stamp out of the manifest by its path of keys, or None if it is not there."""
    data, _why = read_manifest()
    for key in keys:
        if not isinstance(data, dict):
            return None
        data = data.get(key)
    return _stamp(data)


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
    return (_manifest_stamp("collection", "last_admission")
            or _newest_stamp(INGESTED_LOG, _INGEST_HEAD))


def collected_to(now: dt.datetime | None = None) -> tuple[dt.datetime | None, str]:
    """`(the moment after which nothing more could have been caught, where it came from)`.

    The bulletin byline's one claim, and the one place the policy behind it lives.

    **With a manifest, `sweep_closed` answers on its own** (note 16): it is collection, and
    collection is what the byline claims. The later-of-two reading below existed because
    neither source covered every path — `sweep_closed` was stamped by `@UPDATE-WIKI` and
    `SWEEP-BULLETIN` but not by the cycle, and the cycle's `End` said nothing about the two
    runs that write no rotation row. The manifest is written by both passes that mirror, so
    it covers what each half was missing and the comparison has nothing left to do.

    **Without one, the legacy reading stands** and says so. It is the whole of what the
    fallback is for, and it goes when the manifest has been read once on the mirror."""
    ceiling = (now or dt.datetime.now()) + SKEW
    ahead = lambda when: when is not None and when > ceiling

    data, why = read_manifest()
    if data is not None:
        swept = _stamp((data.get("collection") or {}).get("sweep_closed"))
        if swept is not None and not ahead(swept):
            return swept, why

    # The guard sits here, before the comparison, and not on the answer. There is one
    # closing row, so a mistyped `End` is the whole column - and dropping it afterwards
    # would let a fat-fingered year suppress a `sweep_closed` that was perfectly good.
    closed = last_cycle_close()
    if ahead(closed):
        closed = None
    swept = sweep_closed()
    if ahead(swept):
        swept = None

    if swept is not None and (closed is None or swept >= closed):
        return swept, "OSINT sweep_closed (no manifest)"
    if closed is not None:
        return closed, ("OSINT sweep cycle close (no manifest)" if swept is None
                        else "OSINT sweep cycle close, newer than any sweep_closed "
                             "(no manifest)")
    return None, why


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
    swept = _manifest_stamp("collection", "sweep_closed")
    if swept is not None:
        return swept

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
    closed = _manifest_stamp("rotation", "newest_close", "end")
    if closed is not None:
        return closed

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
