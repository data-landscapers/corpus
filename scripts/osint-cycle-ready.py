#!/usr/bin/env python3
r"""
osint-cycle-ready.py — has a sweep cycle closed since Corpus last built?

**The signal is the closed row, not the file copy** *(Bill, 2026-08-20)*. `SWEEP-CYCLE.md`
-> *Mirror* makes FreeFileSync the night's last act, so every completed cycle refreshes the
whole of `C:\OSINT` — but so does a manual FFS run Bill fires at four in the afternoon while
he and Corpus are working on something else. Mtimes cannot tell those apart, and a trigger
built on them would start a three-hour build in the middle of a conversation.

What can tell them apart is already written and already crosses. The cycle's closing
sequence sets `Start`, `End`, `Duration` and clears `New-Start` in
`logs/sweep-cycle_log.md`, **commits**, and only then mirrors. So:

  - **`max(End)` over the rotation table advances on a cycle close and on nothing else.**
    A manual mirror carries the same table across, the watermark here does not move, and
    this exits 1.
  - **Reading the new `End` from the mirror is itself the proof the mirror carried it.**
    An `End` visible here cannot have arrived except by an FFS run that started after the
    commit that wrote it. That is why nothing in this file reads FreeFileSync's exit code
    or its session logs in `logs/mirror-ffs/` — which is just as well, because
    `SWEEP-CYCLE.md` says plainly that nothing gates on that exit code.
  - **Nothing changes on the OSINT side.** OSINT writes this signal for its own reasons and
    has done since long before Corpus read it. There is no note to send, no new file, and no
    dependency for OSINT to honour — which is the only version of this that respects the
    read-only rule rather than working around it.

**Every close fires** *(Bill, 2026-08-20)*. The table closed twice on 2026-08-20 and will
again while the rotation is run by hand; each close is a night's evidence genuinely landed
in `raw/`, so each earns a build. There is no minimum-interval guard, at Bill's word: *"If I
do it is my responsibility to ensure that i don't interfere with your protocol."*

**Three things hold a ready cycle back, and none of them is an error.** A build in flight
(`logs/.build-in-progress`), tracked changes in the working tree, or `logs/.hold-cycle` —
the switch Bill flips when he sits down to work. **A hold does not advance the watermark**,
so the run happens when the hold clears rather than being lost. Untracked files deliberately
do not count: a stray file nobody remembers would wedge the trigger for ever, and the state
this is testing for is *a session is part-way through something*.

**`--skip` passes a close over without building it, and loses nothing** *(2026-08-20)*. `BUILD.md`
works off a set difference over slugs rather than a window, so a close that is never built is
covered whole by the next one; the only thing skipping costs is the delay. Two occasions call
for it: a close whose catch is not worth a cycle — *"sweep-iati never returns much work for
you"* — and a close superseded by a cycle starting **now**, where firing would put a build and
OSINT's writes over `raw/` at the same time. The watermark records which of `built` or
`skipped` put it there, so the log of what Corpus did with each night stays truthful.

**A claim that never reported done is the one state that needs a human.** `--claim` records
the `End` a run is about to build and `--done` advances the watermark to it. If a claim is
outstanding and newer than `done`, a cycle started and did not finish, and this exits 2
rather than firing again: `CYCLE.md` — *a retry inside the same run is how a job starts
looping on the fault that stopped it* — and a poll loop re-firing a failing cycle every
twenty minutes is that fault with a clock on it. `--release` clears it once a human has
looked.

Usage:  python scripts/osint-cycle-ready.py [--claim | --done | --skip | --release | --status]
                                            [--quiet]
Exit:   0 ready (or the bookkeeping flag succeeded), 1 not ready, 2 needs attention.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys

# The em-dashes below reach a cp1252 console otherwise, and a trigger that dies inside a
# print is a trigger that fails silently for a night. Same guard as `bulletin.py`.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The mirror `SWEEP-CYCLE.md` -> *Mirror* writes to, seen from this machine: OSINT syncs
# `C:\OSINT` onto `O:\` = `\\bill-vivobook\osint`, and this *is* bill-vivobook, so the share
# resolves back to a local path. Overridable for the same reason `status_lib.EXCHANGE` is — a
# move onto a mapped drive should need no code change.
#
# **It lives in `osint_lib.py` now** *(2026-08-21)*, because `bulletin.py` needs the mirror too
# — it takes the bulletin's *last updated* stamp from `logs/ingested_log.md` — and a path to
# another repository stated in two files is a path that will one day be moved in one of them.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osint_lib import MIRROR  # noqa: E402

CYCLE_LOG = os.path.join(MIRROR, "logs", "sweep-cycle_log.md")

# Untracked, like `logs/.build-in-progress` and OSINT's own `mirror_log.md`: it changes on
# OSINT's schedule rather than on any commit of Corpus's, and a tracked one would dirty the
# tree on every trigger — which the dirty-tree hold below would then read as *someone is
# working*, so the trigger would fire once and hold for ever after.
STATE = os.path.join(ROOT, "logs", ".osint-cycle-seen")

HOLD = os.path.join(ROOT, "logs", ".hold-cycle")
SENTINEL = os.path.join(ROOT, "logs", ".build-in-progress")

TS = "%Y-%m-%d %H:%M"


class Incoherent(Exception):
    """The mirror cannot be read as a rotation table. Never a quiet 'not yet'."""


def rows() -> list[dict]:
    """The rotation table, one dict per day row.

    Read against the header rather than by position, and the header is asserted: a rename
    there should stop this dead rather than have it read `Start` where it means `End`."""
    if not os.path.isdir(MIRROR):
        raise Incoherent(f"mirror not present at {MIRROR}")
    if not os.path.exists(CYCLE_LOG):
        raise Incoherent(f"no rotation table at {CYCLE_LOG}")
    header, out = None, []
    with open(CYCLE_LOG, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if header is None:
                header = cells
                if "End" not in header or "New-Start" not in header:
                    raise Incoherent(f"rotation table header is not the one this reads: {header}")
                continue
            if set("".join(cells)) <= set("-"):
                continue  # the --- separator
            if len(cells) != len(header):
                continue
            out.append(dict(zip(header, cells)))
    if not out:
        raise Incoherent("rotation table has a header and no rows")
    return out


def parse(ts: str):
    try:
        return dt.datetime.strptime(ts.strip(), TS)
    except (ValueError, AttributeError):
        return None


def newest_close(table: list[dict]):
    """The most recently closed row: (End, Day, Jobs). None if nothing has ever closed."""
    closed = [(parse(r.get("End", "")), r) for r in table]
    closed = [(e, r) for e, r in closed if e]
    if not closed:
        return None
    end, row = max(closed, key=lambda pair: pair[0])
    return end, row.get("Day", "?"), row.get("Jobs", "")


def in_flight(table: list[dict]) -> list[str]:
    """Days with `New-Start` populated — a cycle running now, or one that did not finish.

    Either way Corpus does not build: the first is OSINT writing the vault this run would
    read, and the second is a night that stopped part-way."""
    return [r.get("Day", "?") for r in table if r.get("New-Start", "").strip()]


def mirror_head() -> str:
    """The mirror's `HEAD`, for the provenance stamp. Non-fatal: the FFS filter is `*` so
    `.git` travels, but a trigger is not the place to die over a missing one."""
    try:
        out = subprocess.run(["git", "-C", MIRROR, "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=30)
        return out.stdout.strip() if out.returncode == 0 else "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def base_moved(since_head: str) -> str:
    """How far the base has moved since the commit Corpus last built, as a clause or "".

    **This reports; it never fires** *(2026-08-21)*. A second trigger condition on base
    movement was considered and rejected: OSINT commits to `raw/` all through its own working
    day, so a movement trigger would fire mid-session repeatedly — the exact failure the
    closed-row discriminator was chosen to avoid, and a size threshold only delays it. The
    close row stays the only thing that starts a cycle.

    What it fixes is that the quiet answer was *too* quiet. On 2026-08-21 this printed
    `nothing new — newest close 00:14 (day 1) already built` while OSINT's housekeeping had
    moved 205 files under it: 38 duplicate records retired, an OCR layer put on every
    image-only PDF in `raw/`, `pdftotext` re-run under UTF-8. Every one of the 38 was cited
    in Corpus's published layer and `report-render.py`'s check M was already failing on
    three of them. The trigger was right that no cycle was *owed* and unhelpful about
    whether one was *wanted*, and answering that took a hand-written diff against `git log`.

    Non-fatal for the same reason as `mirror_head()`, and silent when the diff is empty, so
    the ordinary quiet answer stays one line."""
    if not since_head or since_head == "unknown":
        return ""
    try:
        head = mirror_head()
        if head in ("unknown", since_head):
            return ""
        rng = f"{since_head}..{head}"
        allf = subprocess.run(["git", "-C", MIRROR, "diff", "--name-only", rng],
                              capture_output=True, text=True, timeout=60)
        base = subprocess.run(["git", "-C", MIRROR, "diff", "--name-only", rng, "--", "raw", "wiki"],
                              capture_output=True, text=True, timeout=60)
        if allf.returncode or base.returncode:
            return ""
        n = len([x for x in allf.stdout.splitlines() if x.strip()])
        nb = len([x for x in base.stdout.splitlines() if x.strip()])
        if not n:
            return ""
        return (f"; the base has moved since: {n} file(s), {nb} of them under raw/ or wiki/ "
                f"(OSINT {since_head[:8]}..{head[:8]})")
    except (OSError, subprocess.SubprocessError):
        return ""


def tree_dirty() -> bool:
    """Tracked changes only — see the module docstring on why untracked files do not count."""
    try:
        out = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "-uno"],
                             capture_output=True, text=True, timeout=60)
        return bool(out.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        return False


def load() -> dict:
    if not os.path.exists(STATE):
        return {}
    try:
        with open(STATE, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        raise Incoherent(f"{STATE} is not readable JSON; --release rewrites it")


def save(state: dict) -> None:
    with open(STATE, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)
        fh.write("\n")


def decide() -> tuple[int, str, dict]:
    """(exit code, one line, facts). The whole of the judgement in one place, so a bare run
    and a `--claim` cannot drift apart."""
    table = rows()
    state = load()
    done = parse(state.get("done") or "")
    claimed = parse(state.get("claimed") or "")

    if claimed and (not done or claimed > done):
        return 2, (f"a cycle claimed {claimed:%Y-%m-%d %H:%M} at {state.get('claimed_at', '?')} "
                   "and never reported done — run CYCLE.md by hand, or --release"), {}

    close = newest_close(table)
    if not close:
        return 2, "no row in the rotation table has ever closed", {}
    end, day, jobs = close

    if done and end <= done:
        # Worded off `done_by`, because "already built" over a close that was skipped is the
        # kind of small untruth a log accumulates until nobody trusts any line in it.
        was = "passed over" if state.get("done_by") == "skipped" else "already built"
        moved = base_moved(str(state.get("done_head") or ""))
        return 1, f"nothing new — newest close {end:%Y-%m-%d %H:%M} (day {day}) {was}{moved}", {}

    flight = in_flight(table)
    if flight:
        return 1, f"day {', '.join(flight)} has New-Start set — a cycle is in flight", {}

    if os.path.exists(HOLD):
        return 1, f"held — logs/.hold-cycle is present (day {day} waiting)", {}
    if os.path.exists(SENTINEL):
        return 1, f"held — a build is in flight (logs/.build-in-progress; day {day} waiting)", {}
    if tree_dirty():
        return 1, f"held — Corpus has uncommitted tracked changes (day {day} waiting)", {}

    head = mirror_head()
    return 0, f"ready — day {day} closed {end:%Y-%m-%d %H:%M} ({jobs}); OSINT HEAD {head[:12]}", \
        {"end": end.strftime(TS), "head": head, "day": day, "jobs": jobs}


def main() -> int:
    ap = argparse.ArgumentParser(description="Has a sweep cycle closed since Corpus last built?")
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--claim", action="store_true",
                       help="on ready, record the close this run is about to build")
    group.add_argument("--done", action="store_true",
                       help="advance the watermark to the outstanding claim")
    group.add_argument("--skip", action="store_true",
                       help="advance the watermark past the newest close without building it")
    group.add_argument("--release", action="store_true",
                       help="clear an outstanding claim without advancing the watermark")
    group.add_argument("--status", action="store_true", help="print the watermark and stop")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    def say(msg):
        if not args.quiet:
            print(msg)

    try:
        if args.status:
            state = load()
            say(json.dumps(state, indent=2, sort_keys=True) if state else "no watermark yet")
            return 0

        if args.done:
            state = load()
            if not state.get("claimed"):
                say("no claim outstanding — nothing to mark done")
                return 2
            state["done"] = state["claimed"]
            state["done_head"] = state.get("claimed_head", "unknown")
            state["done_by"] = "built"
            state["claimed"] = state["claimed_at"] = state["claimed_head"] = None
            save(state)
            say(f"built through {state['done']} (OSINT {str(state['done_head'])[:12]})")
            return 0

        if args.skip:
            state = load()
            if state.get("claimed"):
                say(f"a claim on {state['claimed']} is outstanding — --release it first")
                return 2
            close = newest_close(rows())
            if not close:
                say("no row in the rotation table has ever closed")
                return 2
            end, day, _ = close
            state["done"] = end.strftime(TS)
            state["done_head"] = mirror_head()
            state["done_by"] = "skipped"
            save(state)
            say(f"skipped — day {day}'s close at {state['done']} will not be built; "
                "the next close covers it")
            return 0

        if args.release:
            state = load()
            was = state.get("claimed")
            state["claimed"] = state["claimed_at"] = state["claimed_head"] = None
            save(state)
            say(f"claim on {was} released — watermark left at {state.get('done')}" if was
                else "no claim outstanding")
            return 0

        code, line, facts = decide()
        say(line)
        if args.claim and code == 0:
            state = load()
            state["claimed"] = facts["end"]
            state["claimed_head"] = facts["head"]
            state["claimed_at"] = dt.datetime.now().strftime(TS)
            save(state)
            say(f"claimed {facts['end']}")
        return code
    except Incoherent as exc:
        say(f"cannot judge: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
