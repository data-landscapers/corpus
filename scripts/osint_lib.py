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

**One file answers all of it, and it is not a log.** `cycle-manifest.json` is OSINT's own
machine-readable account of a close, written after the final commit and before the mirror by
every pass that mirrors (`notes-for-corpus` 16, strategic review task 14). Until 2026-09-06
this module also parsed `logs/ingested_log.md` and `logs/sweep-cycle_log.md` as a fallback for
a mirror carrying no manifest, and most of its length was the forensics that took: a heading
format that changed under it, a mistyped stamp four hours in the reader's future, a clustering
constant that guessed at OSINT's working day. **That fallback is retired** — a manifest has
been read on the mirror, note 16's condition is met, and reading another repository's internal
logs is outside the interface `lint-interface.py` asserts. Where the manifest cannot be read
the answer is `None`, and the reason comes back with it.

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
import subprocess

# Seen from this machine. `SWEEP-CYCLE.md` -> *Mirror* syncs `C:\OSINT` onto `O:\`, and this is
# the machine that share resolves back to.
MIRROR = os.environ.get("CORPUS_OSINT_MIRROR", r"C:\OSINT")

# The cycle manifest, written after the final commit and before the mirror by every pass that
# mirrors (note 16, strategic review task 14). It is the whole of what Corpus needs to know
# about a close, and since 2026-09-06 the whole of what it reads. `UPDATE-WIKI` does not
# mirror and writes none; its material arrives at the next pass that does.
MANIFEST = os.path.join(MIRROR, "cycle-manifest.json")

# A reader that meets a schema it does not know stops rather than guesses (note 16). A field
# that changed meaning under the same number is the one failure a fallback cannot catch,
# because both readings parse.
MANIFEST_SCHEMA = 1

TS = "%Y-%m-%d %H:%M"

# How far past the clock a stamp may sit and still be believed. The mirror is written by a
# machine that is not this one, so a stamp a minute or two ahead is skew rather than error;
# anything further ahead is a claim about work that has not happened yet.
SKEW = dt.timedelta(minutes=5)


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
    tree are not the same repository*. Only a mirroring pass writes a manifest, and OSINT
    commits from passes that do not mirror, so a manifest naming an earlier commit than HEAD
    is the ordinary state and not a fault - it was measured firing within minutes of this
    reader being written. A commit that is *not* an ancestor is the real fault: a tree and an
    account of it that arrived from different histories."""
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

    **Absent.** No longer the ordinary case and no longer covered by a fallback: since
    2026-09-06 this is the state in which Corpus has no reading of OSINT's clocks at all, and
    every reader below answers `None` and says why.

    **Unparseable.** The manifest is written before the mirror copies, so a truncated file is
    a copy caught in the middle, not a corrupt source.

    **A schema this does not know.** Refused outright (note 16). Guessing at an unknown
    schema is the one failure a fallback could not have caught either, because a field that
    changed meaning under a new number still parses under the old reading.

    **`head` naming a commit the mirror's history does not contain.** A tree and an account
    of it that arrived from different histories. Note 16 asks for a plain equality check
    here, and equality is too strict: only a mirroring pass writes a manifest and OSINT
    commits from passes that do not, so `head` trailing HEAD is the ordinary state -
    measured firing within minutes of this being written. A manifest whose `head` is an
    **ancestor** of HEAD is accepted and says so, because its stamps then understate
    freshness, which is the direction this repo prefers to be wrong in.

    Where git cannot answer at all the head check is skipped rather than failed — an absent
    git is not evidence of a bad copy, and the schema and shape checks have already run.
    """
    path = path or MANIFEST
    if not os.path.exists(path):
        return None, "no cycle manifest on the mirror"
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
    *(measured 2026-08-28; `notes-for-osint` 55)*. They are copied verbatim out of OSINT's own
    logs, which are local: the manifest of 2026-08-28 08:36 reported `rotation.newest_close`
    as `19:07`/`21:31` where that day's rotation row carried `19:07`/`21:31`, and
    `collection.last_admission` as `20:36` against the same number in OSINT's newest ingest
    heading. The two fields that do come from a clock rather than a log —
    `head_committed_utc` and `written_utc`, both `08:36` — are true UTC, against a `git log`
    on the mirror putting that commit at 09:36 +0100. So the manifest carries two clocks
    under one name.

    Reading these as local is the conservative half. Converting would move the published
    byline an hour **later** than the moment collection actually stopped, which is a claim
    about work that had not happened; reading them as local is at worst the same value the
    retired log path published. When OSINT settles the field, this is the one place to
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
    """When OSINT's ingest last admitted anything to `raw/` — `collection.last_admission`.

    **This is the moment the corpus last moved**, which is what *when was this page last
    updated* is asking. The build clock answers *when did we last run*, and on a day when
    nothing came in those are different claims and only one of them is about the reader's
    material.

    Returns `None` where the manifest cannot be read — never a guess, and never today's date
    standing in for a fact about another repository.
    """
    return _manifest_stamp("collection", "last_admission")


def sweep_closed() -> dt.datetime | None:
    """When collection stopped, as OSINT states it — `collection.sweep_closed`.

    **This is the bulletin's *Last updated*, and it is a fact rather than a derivation**
    *(OSINT `notes-for-corpus.md` note 13, 2026-08-26, closing its own note 45)*. What a
    reader is being told is *how recent is the material here*, and the defensible answer is
    the point after which nothing more could have been caught. Corpus had no artefact
    recording that, so it derived one — from the start of the newest ingest run, found by
    clustering headings — and the derivation failed twice in three days in opposite
    directions. Every path that admits anything to `raw/` now stamps the moment itself and
    the manifest carries it, so there is nothing left to infer and nothing left to parse.
    """
    return _manifest_stamp("collection", "sweep_closed")


def last_cycle_close() -> dt.datetime | None:
    """When a sweep cycle last closed — `rotation.newest_close.end`.

    A few minutes after the ingest that ran inside it — 00:05 against 00:14 on 2026-08-21 —
    and that is not crudeness, it is the same fact recorded a step later. It was half of the
    bulletin's *Last updated* while the cycle path did not stamp `sweep_closed` and the two
    runs that did wrote no rotation row; the manifest is written by every pass that mirrors,
    so it covers what each half was missing and `collected_to()` no longer compares the two.
    `lint-osint-freshness.py` still reads it as one of four clocks, because a mirror where one
    of them has stopped moving and the others have not is worth seeing as separate lines.
    """
    return _manifest_stamp("rotation", "newest_close", "end")


def collected_to(now: dt.datetime | None = None) -> tuple[dt.datetime | None, str]:
    """`(the moment after which nothing more could have been caught, where it came from)`.

    The bulletin byline's one claim, and the one place the policy behind it lives.

    **`sweep_closed` answers on its own** (note 16): it is collection, and collection is what
    the byline claims. The later-of-two reading this used to do existed because neither source
    covered every path — `sweep_closed` was stamped by `@UPDATE-WIKI` and `SWEEP-BULLETIN` but
    not by the cycle, and the cycle's `End` said nothing about the two runs that write no
    rotation row. The manifest is written by every pass that mirrors, so it covers both and
    the comparison has nothing left to do.

    A stated close in the future is refused: the mirror is written by another machine, so
    `SKEW` of it is clock drift and anything past that is a claim about work that has not
    happened. Where the manifest cannot be read at all the answer is `None` with the reason,
    and the caller decides what to publish instead — `bulletin.stamps_for()` falls to the
    newest ingest heading and then to the build clock, and says which it used."""
    ceiling = (now or dt.datetime.now()) + SKEW

    data, why = read_manifest()
    if data is None:
        return None, why
    swept = _stamp((data.get("collection") or {}).get("sweep_closed"))
    if swept is None:
        return None, f"{why}, which carries no collection.sweep_closed"
    if swept > ceiling:
        return None, (f"{why}, whose sweep_closed {swept:%Y-%m-%d %H:%M} is in the future — "
                      f"refused rather than published")
    return swept, why


if __name__ == "__main__":
    _data, _why = read_manifest()
    print(f"mirror        {MIRROR}")
    print(f"reading       {_why}")
    print(f"sweep closed  {sweep_closed() or '— not readable'}")
    print(f"last ingest   {last_ingest() or '— not readable'}")
    print(f"last close    {last_cycle_close() or '— not readable'}")
