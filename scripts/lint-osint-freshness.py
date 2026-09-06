#!/usr/bin/env python3
r"""
lint-osint-freshness.py — is the evidence Corpus reads actually current?

**The gap this closes was named when it was opened.** OSINT's `LINT` #19 watched a mirror
for staleness and was retired with OSINT's own backup (`documentation/archived/
osint-migration.md` R8, run 2026-08-16). Since 2026-08-20 the same FreeFileSync pass has a
different job: `SWEEP-CYCLE.md` -> *Mirror* is the night's last act, and what it supplies is
**Corpus's copy of the vault**, not a backup. Nothing on either side then checked its
freshness. When it was a backup, a stale mirror meant a late backup; now it means Corpus
compiling, reporting and publishing from yesterday's evidence, silently. `notes-for-corpus.md`
note 5 is that finding, and this is its `[ACT]`: *a freshness check belongs on the reading
side, which is Corpus's.*

**Where the mirror actually is, because the note's own wording misleads.** OSINT works on its
machine's `C:\OSINT` and syncs to `O:\` = `\\bill-vivobook\osint`. This *is* bill-vivobook, and
that share resolves back to this machine's `C:\OSINT` — so from Corpus the mirror is the local
path `C:\OSINT`, `O:\` is not mapped here at all, and `scripts/.workroot/{raw,wiki,lookups}`
pointing into `C:\OSINT` are pointing at the mirror and are correct. `osint_lib.MIRROR` is the
one constant that says so (`CORPUS_OSINT_MIRROR` overrides).

**Four clocks, and the newest of them is the answer.** None is authoritative alone. Three
come out of `cycle-manifest.json` and one out of git; nothing here reads a log
*(2026-09-06, `notes-for-corpus` 16)*.

  1. **`collection.last_admission`** — when `raw/` last took anything in. The moment the
     corpus itself moved.
  1a. **`collection.sweep_closed`** — when collection last stopped, as OSINT states it rather
     than as Corpus infers it *(from 2026-08-26)*. The bulletin's byline, and read here as its
     own line because a manifest where admissions move and the stated closes do not is one
     where OSINT has stopped stamping, which no single reading would show.
  2. **`rotation.newest_close.end`** — when a cycle last closed. Cruder, a few minutes later
     than the ingest inside it, and it was the other half of the byline while the cycle path
     wrote no `sweep_closed`; kept as its own line for the same reason as 1a.
  3. **The mirror's `HEAD` commit date** — stamped by OSINT's clock at commit time and carried
     across by the sync, so it moves on *every* OSINT commit rather than only on a cycle. The
     tightest of the four, and the reading-side analogue of the `git -C O:\ rev-parse HEAD`
     assertion `SWEEP-CYCLE.md` already makes on the writing side.

**A mirror with no readable manifest now scores three of these `None`**, which is the
UNREADABLE state below rather than a quiet fallback — the whole point of retiring the log
reads is that Corpus should be loud about a mirror it cannot date, not resourceful.

**Two faults, and a third state that is not a fault.**

  - **Stale** — the newest of the three is past `--max-age-hours` (default 72, the same floor
    `lint-mirror-freshness.py` puts under the backup). 70 minutes behind is the normal state
    between cycles; 70 hours is the state nothing would otherwise report.
  - **Regressed** — the mirror's newest close is *older* than the close Corpus has already
    built, per the `done` watermark in `logs/.osint-cycle-seen`. A mirror that goes backwards
    is not a late sync, and it passes the age test whenever the rollback is recent.
  - **Unreadable** (exit 2) — no clock could be read at all. Distinct from stale on purpose:
    every reader in `osint_lib` returns `None` rather than guessing, so an unreadable mirror is
    the state in which Corpus's own fallbacks go quiet, which is exactly when a check should be
    loud.

**Reports, never fixes, and here it could not fix anything if it wanted to.** The repair runs
on OSINT's machine — `FreeFileSync.exe SyncSettings.ffs_batch`, by hand — and `C:\OSINT` is
read-only from Corpus, absolutely (`CLAUDE.md`). Nothing here writes, and the only OSINT git
call is `log -1`, which reads.

**Not a gate.** A cycle is run by hand and a quiet stretch is legitimate, so a build stopped by
this would be stopped by OSINT's schedule rather than by a defect. `BUILD.md` stage 0 runs it
and states what it found; the ceiling is where a quiet stretch stops being plausible.

Usage:  python scripts/lint-osint-freshness.py [--quiet] [--max-age-hours N]
Exit:   0 fresh, 1 stale or regressed, 2 nothing readable to judge against.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osint_lib  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WATERMARK = os.path.join(ROOT, "logs", ".osint-cycle-seen")

DEFAULT_MAX_AGE_HOURS = 72


def head_committed() -> dt.datetime | None:
    """The commit date of the mirror's `HEAD`, as naive local time.

    `%cI` rather than `%ct`: the committer date carries OSINT's own offset, and reading it as
    an aware datetime and converting is one line, where a Unix stamp would silently be right
    only while both machines agree about the zone. Returns `None` on any failure — a missing
    mirror, a tree with no `.git`, git absent from PATH — because a guess here would be a
    guess about another repository's clock.

    Read-only: `log -1` touches nothing, and `CLAUDE.md` allows read-only git against OSINT
    while allowing nothing else at all.
    """
    if not os.path.isdir(osint_lib.MIRROR):
        return None
    try:
        out = subprocess.run(
            ["git", "-C", osint_lib.MIRROR, "log", "-1", "--format=%cI"],
            capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0 or not out.stdout.strip():
        return None
    try:
        when = dt.datetime.fromisoformat(out.stdout.strip())
    except ValueError:
        return None
    return when.astimezone().replace(tzinfo=None) if when.tzinfo else when


def built_watermark() -> dt.datetime | None:
    """The close Corpus has already built, from `logs/.osint-cycle-seen`.

    Absent, unparseable or never yet set all read as `None`: a watermark that cannot be read
    is not evidence that the mirror regressed, and inventing one would turn a first run into
    a fault."""
    if not os.path.exists(WATERMARK):
        return None
    try:
        with open(WATERMARK, encoding="utf-8") as fh:
            state = json.load(fh)
    except (OSError, ValueError):
        return None
    try:
        return dt.datetime.strptime((state.get("done") or "").strip(), osint_lib.TS)
    except (ValueError, AttributeError):
        return None


def humanise(delta: dt.timedelta) -> str:
    hours = delta.total_seconds() / 3600
    if hours < 48:
        return f"{hours:.1f}h"
    return f"{hours / 24:.1f} days"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="OSINT mirror freshness, from the reading side. Reports, never fixes.")
    ap.add_argument("--quiet", action="store_true", help="print nothing when fresh")
    ap.add_argument("--max-age-hours", type=float, default=DEFAULT_MAX_AGE_HOURS,
                    help=f"stale beyond this many hours (default {DEFAULT_MAX_AGE_HOURS})")
    args = ap.parse_args()

    now = dt.datetime.now()

    # Which source answered, printed rather than inferred. Since the cycle manifest these
    # clocks come from one small JSON instead of four passes over OSINT's logs, and a run
    # that has quietly dropped back to the logs - a half-copied mirror, an unknown schema -
    # should say so on the line rather than look identical to one that has not.
    _data, source = osint_lib.read_manifest()
    print(f"osint freshness: reading {source}.")

    clocks = {
        "last ingest": osint_lib.last_ingest(),
        # The two halves of the bulletin's byline, read separately here because a mirror where
        # one of them has stopped moving and the other has not is worth seeing as two lines.
        "last sweep close": osint_lib.sweep_closed(),
        "last close": osint_lib.last_cycle_close(),
        "mirror HEAD": head_committed(),
    }
    readable = {name: when for name, when in clocks.items() if when is not None}

    if not readable:
        print(f"osint freshness: UNREADABLE - no clock could be read from {osint_lib.MIRROR}")
        for name in clocks:
            print(f"  - {name}: not readable")
        print("  Corpus's readers fall back silently when the mirror cannot be read "
              "(osint_lib), so this is the state in which a stale base looks like a fresh one.")
        print("  Check the mirror is present and populated, then re-run OSINT's "
              "`FreeFileSync.exe SyncSettings.ffs_batch` from OSINT's machine.")
        return 2

    newest_name, newest = max(readable.items(), key=lambda kv: kv[1])
    age = now - newest
    faults: list[str] = []

    if age.total_seconds() / 3600 > args.max_age_hours:
        faults.append(f"nothing on the mirror has moved for {humanise(age)}, past the "
                      f"{args.max_age_hours:g}h ceiling - Corpus would compile, report and "
                      f"publish from evidence that old without saying so")

    built = built_watermark()
    close = clocks["last close"]
    if built is not None and close is not None and close < built:
        faults.append(f"the mirror's newest close ({close:%Y-%m-%d %H:%M}) is older than the "
                      f"close Corpus has already built ({built:%Y-%m-%d %H:%M}) - the mirror "
                      f"has gone backwards, which no age test would catch")

    lines = [f"  - {name}: {when:%Y-%m-%d %H:%M} ({humanise(now - when)} ago)"
             for name, when in clocks.items() if when is not None]
    lines += [f"  - {name}: not readable" for name, when in clocks.items() if when is None]

    if faults:
        print(f"osint freshness: STALE - newest signal {newest_name} "
              f"{newest:%Y-%m-%d %H:%M} ({humanise(age)} ago)")
        for f in faults:
            print(f"  - {f}")
        print("  Repair runs on OSINT's machine: `FreeFileSync.exe SyncSettings.ffs_batch` "
              "(SWEEP-CYCLE.md -> Mirror). C:\\OSINT is read-only from here.")
        print("  Clocks read:")
        for ln in lines:
            print(f"  " + ln.lstrip())
        return 1

    if not args.quiet:
        print(f"osint freshness: ok - newest signal {newest_name} {newest:%Y-%m-%d %H:%M} "
              f"({humanise(age)} ago), mirror {osint_lib.MIRROR}")
        for ln in lines:
            print(ln)
    return 0


if __name__ == "__main__":
    sys.exit(main())
