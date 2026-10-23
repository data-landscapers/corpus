#!/usr/bin/env python3
r"""
osint-cycle-ready.py — has a sweep cycle closed since Corpus last built?

**The signal is the closed row, not the file copy** *(Bill, 2026-08-20)*. `SWEEP-CYCLE.md`
-> *Mirror* makes FreeFileSync the night's last act, so every completed cycle refreshes the
whole of `C:\OSINT` — but so does a manual FFS run Bill fires at four in the afternoon while
he and Corpus are working on something else. Mtimes cannot tell those apart, and a trigger
built on them would start a three-hour build in the middle of a conversation.

What can tell them apart is already written and already crosses. The cycle's closing
sequence sets the rotation row's `Start`, `End` and `Duration`, clears `New-Start`, writes
the whole of it into **`cycle-manifest.json`** as `rotation`, and only then mirrors. So:

  - **`rotation.newest_close.end` advances on a cycle close and on nothing else.** A manual
    mirror carries the same manifest across, the watermark here does not move, and this
    exits 1. A pass that mirrors without closing a rotation day rewrites the manifest and
    carries the same `newest_close` forward, which is the same non-event.
  - **Reading the new close from the mirror is itself the proof the mirror carried it.** An
    `end` visible here cannot have arrived except by a mirroring run that started after the
    manifest carrying it was written. That is why nothing in this file reads FreeFileSync's
    exit code or its session logs in `logs/mirror-ffs/` — which is just as well, because
    `SWEEP-CYCLE.md` says plainly that nothing gates on that exit code.
  - **The manifest is not a committed file** *(measured 2026-09-08; `notes-for-osint` 133)*.
    This docstring used to say the closing sequence commits it, and the bullet above used to
    rest the guarantee on "the commit that wrote it". Neither is so: OSINT's `.gitignore`
    names `cycle-manifest.json` and no commit has ever touched it. The guarantee survives
    unchanged — it never needed the commit, only that the manifest is written before the
    mirroring pass that carries it — but two things follow that cost a night on 2026-09-07:
    nothing in OSINT's history restores the file if a pass removes it, and its `head` field
    and the history that field names are captured independently, so `head` can land either
    side of HEAD. `osint_lib.read_manifest` already refuses the second case; the first is
    what note 133 asks OSINT to close.
  - **Nothing is asked of OSINT's writing.** OSINT writes this signal for its own reasons and
    has done since long before Corpus read it: no new file, no new field, nothing to poll —
    which is the only version of this that respects the read-only rule rather than working
    around it. **What is asked, once, is that the file survive** — note 133, after it did not
    on 2026-09-07. That is a smaller thing than a dependency to honour on every pass, but it
    is not nothing, and this bullet used to claim it was.

**It reads the manifest, not `logs/sweep-cycle_log.md`** *(2026-09-06, `notes-for-corpus`
16)*. Until then this parsed OSINT's rotation table directly, header-asserted, because
nothing else stated a close. The manifest states one, it is inside the interface
`lint-interface.py` asserts and the log is not, and OSINT computes `newest_close` itself — so
the maximum this used to take over the `End` column, and the header assertion that guarded
the column order, go with the parse.

**Every close fires** *(Bill, 2026-08-20)*. The table closed twice on 2026-08-20 and will
again while the rotation is run by hand; each close is a night's evidence genuinely landed
in `raw/`, so each earns a build. There is no minimum-interval guard, at Bill's word: *"If I
do it is my responsibility to ensure that i don't interfere with your protocol."*

**Under `/poll`, only a critical error stops a cycle** *(Bill, 2026-10-23, after two nights
lost to a held tree)*. Critical means the trigger cannot judge at all: the mirror absent, the
manifest unreadable, the watermark unreadable, or no row ever closed. Those exit 2. Everything
that used to hold is now resolved and the cycle runs:

- **Tracked changes in the working tree are committed** by `--claim`, one commit naming the
  files, before the build starts. A bare run says it will. A line-ending flip with no content
  change is re-staged instead, since there is nothing to commit. Untracked files are not
  touched: BUILD's own ending sequence takes what is its.
- **A day OSINT has open does not hold.** The catalogue is the pin (`CYCLE.md`), so a build
  can run while OSINT works beside it; what arrives after stage 2 is the next cycle's.
- **A claim or a build sentinel older than `LIVE_HOURS` is a dead run, and is resumed**: the
  claim is taken over and the sentinel left for BUILD stage 0 to restamp, which is the repair
  `CYCLE.md` step 2 names. Younger than that, a cycle is running now, and this exits 1 —
  that is the cycle running, not a stop.
- **`logs/.hold-cycle` still holds**: it is Bill's own switch, flipped by hand. `scripts/status.py`
  names it as a gate at the end of every job, so it cannot be forgotten silently.

**A hold does not advance the watermark**, so a held close runs when the hold clears.

**`--skip` passes a close over without building it, and loses nothing** *(2026-08-20)*. `BUILD.md`
works off a set difference over slugs rather than a window, so a close that is never built is
covered whole by the next one; the only thing skipping costs is the delay. Two occasions call
for it: a close whose catch is not worth a cycle — *"sweep-iati never returns much work for
you"* — and a close superseded by a cycle starting **now**, where firing would put a build and
OSINT's writes over `raw/` at the same time. The watermark records which of `built` or
`skipped` put it there, so the log of what Corpus did with each night stays truthful.

**A claim that never reported done is resumed, once it is old enough to be dead.** `--claim`
records the `End` a run is about to build and `--done` advances the watermark to it. An
outstanding claim younger than `LIVE_HOURS` is a cycle still running, and exits 1. An older
one is a cycle that died: `--claim` takes it over, counts the takeover in the state file, and
the stages resume on their own set differences. **The loop guard is the count**: a claim taken
over `MAX_RESUMES` times without a `--done` is the same fault recurring, and that is critical,
exit 2 — a poll re-firing a failing cycle every half hour is the fault `documentation/cycle.md`
warns of, with a clock on it. `--release` clears a claim by hand.

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

# **Refuse to run from inside the workroot** *(2026-09-11)*. Reached through the workroot's own
# `scripts` junction, `__file__` puts ROOT at `.workroot`, so `STATE`, `HOLD` and `SENTINEL` all
# resolve to files that do not exist there. The state file is the watermark: read as absent, the
# trigger reports a close it has already built as **ready**, and `--claim` then dies writing to a
# `logs/` directory the workroot has none of. A trigger that answers differently depending on the
# directory it was invoked from is worse than one that fails, because the wrong answer is the one
# that starts a duplicate cycle. Same guard, and the same reason, as `rebuild.py`.
if os.path.basename(ROOT) == ".workroot" or os.sep + ".workroot" + os.sep in ROOT + os.sep:
    raise SystemExit(
        "osint-cycle-ready.py: refusing to run from inside scripts/.workroot/ — the watermark "
        "lives in the repo's own logs/, and from here it reads as absent, which reports an "
        "already-built close as ready. Run it from the repo root.")

# The mirror `SWEEP-CYCLE.md` -> *Mirror* writes to, seen from this machine: OSINT syncs
# `C:\OSINT` onto `O:\` = `\\bill-vivobook\osint`, and this *is* bill-vivobook, so the share
# resolves back to a local path. Overridable for the same reason `status_lib.EXCHANGE` is — a
# move onto a mapped drive should need no code change.
#
# **It lives in `osint_lib.py` now** *(2026-08-21)*, because `bulletin.py` needs the mirror too
# — it takes the bulletin's *last updated* stamp from the cycle manifest — and a path to
# another repository stated in two files is a path that will one day be moved in one of them.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osint_lib  # noqa: E402
from osint_lib import MIRROR  # noqa: E402

# Untracked, like `logs/.build-in-progress` and OSINT's own `mirror_log.md`: it changes on
# OSINT's schedule rather than on any commit of Corpus's, and a tracked one would dirty the
# tree on every trigger — which the dirty-tree hold below would then read as *someone is
# working*, so the trigger would fire once and hold for ever after.
STATE = os.path.join(ROOT, "logs", ".osint-cycle-seen")

HOLD = os.path.join(ROOT, "logs", ".hold-cycle")
SENTINEL = os.path.join(ROOT, "logs", ".build-in-progress")

TS = "%Y-%m-%d %H:%M"

# A full cycle has run 3h40m at its longest so far; a claim or sentinel past this is a run that
# died, not one that is slow.
LIVE_HOURS = 8
MAX_RESUMES = 2


class Incoherent(Exception):
    """The mirror cannot be read as a rotation. Never a quiet 'not yet'."""


def rotation() -> dict:
    """The manifest's `rotation` block. Never a quiet "not yet" — see `Incoherent`.

    The manifest is refused rather than guessed at when its schema is one this does not know,
    or its `head` names a commit the mirror's history does not hold.
    `osint_lib.read_manifest` decides that and says why, and the reason it gives is what the
    run is told: *this reader is out of date* and *this mirror is half-copied* want different
    repairs."""
    if not os.path.isdir(MIRROR):
        raise Incoherent(f"mirror not present at {MIRROR}")
    data, why = osint_lib.read_manifest()
    if data is None:
        raise Incoherent(why)
    rot = data.get("rotation")
    if not isinstance(rot, dict):
        raise Incoherent("the cycle manifest carries no rotation block")
    return rot


def parse(ts: str):
    try:
        return dt.datetime.strptime(ts.strip(), TS)
    except (ValueError, AttributeError):
        return None


def newest_close(rot: dict):
    """The most recently closed row: (end, day, jobs). None if nothing has ever closed.

    OSINT names which row that is; this used to take the maximum over the whole `End` column
    itself. The maximum was protection against a table that had slipped out of its hand-kept
    order, and the manifest is written by the pass that closes the row rather than read back
    off a file somebody edits."""
    close = rot.get("newest_close")
    if not isinstance(close, dict):
        return None
    end = parse(str(close.get("end") or ""))
    if not end:
        return None
    jobs = close.get("jobs")
    if isinstance(jobs, list):
        jobs = ", ".join(str(j) for j in jobs)
    return end, str(close.get("day", "?")), str(jobs or "")


def in_flight(rot: dict) -> list[str]:
    """Days the manifest reports open — a cycle running now, or one that did not finish.

    Either way Corpus does not build: the first is OSINT writing the vault this run would
    read, and the second is a night that stopped part-way. `rotation.in_progress` is OSINT's
    own list of the days whose `New-Start` is populated; where the newest close also carries
    `in_progress`, that day counts too, because a row can be re-opened after it closed."""
    days = [str(d) for d in (rot.get("in_progress") or []) if str(d).strip()]
    close = rot.get("newest_close")
    if isinstance(close, dict) and close.get("in_progress"):
        day = str(close.get("day", "?"))
        if day not in days:
            days.append(day)
    return days


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
        # Scoped to the evidence, and only the evidence (strategic review task 15). This
        # used to count every changed file and report the total alongside the raw/wiki
        # figure, which read OSINT's logs, reviews and process files to produce a number
        # nothing here acts on - and inflated the one number that is acted on with OSINT's
        # own housekeeping. What Corpus is entitled to know is how much of the base moved.
        base = subprocess.run(["git", "-C", MIRROR, "diff", "--name-only", rng,
                               "--", "raw", "wiki"],
                              capture_output=True, text=True, timeout=60)
        if base.returncode:
            return ""
        nb = len([x for x in base.stdout.splitlines() if x.strip()])
        if not nb:
            return ""
        return (f"; the base has moved since: {nb} file(s) under raw/ or wiki/ "
                f"(OSINT {since_head[:8]}..{head[:8]})")
    except (OSError, subprocess.SubprocessError):
        return ""


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True,
                          timeout=120)


def dirty_paths() -> list[str]:
    """Tracked paths whose content differs from HEAD — see the module docstring.

    A file `git status` flags but `git diff HEAD` does not is a line-ending flip under
    autocrlf, not work: it is re-staged, which clears it. Two nights were lost to five such
    files on 2026-10-22 and 2026-10-23."""
    try:
        flagged = {line[3:].strip() for line in
                   git("status", "--porcelain", "-uno").stdout.splitlines() if line.strip()}
        if not flagged:
            return []
        changed = sorted(p.strip() for p in git("diff", "--name-only", "HEAD").stdout.splitlines()
                         if p.strip())
        phantom = sorted(flagged - set(changed))
        if phantom:
            git("add", "--", *phantom)
        return changed
    except (OSError, subprocess.SubprocessError):
        return []


def commit_outstanding(paths: list[str]) -> str:
    """Commit the tracked changes a cycle found waiting, so the build starts from a clean tree.

    Explicit paths, so nothing staged by anyone else rides along. Returns the short hash, or
    raises `Incoherent` — a tree that cannot be committed is one the build cannot start from."""
    shown = ", ".join(paths[:6]) + (f" and {len(paths) - 6} more" if len(paths) > 6 else "")
    msg = (f"Outstanding work committed before the cycle: {len(paths)} file(s)\n\n"
           f"Found uncommitted when /poll claimed a close: {shown}.\n")
    add = git("add", "--", *paths)
    done = git("commit", "-q", "-m", msg, "--", *paths) if add.returncode == 0 else add
    if done.returncode:
        raise Incoherent(f"the outstanding changes could not be committed: "
                         f"{(done.stderr or done.stdout).strip()[:200]}")
    return git("rev-parse", "--short", "HEAD").stdout.strip()


def age_hours(stamp) -> float:
    return (dt.datetime.now() - stamp).total_seconds() / 3600 if stamp else 0.0


def sentinel_age() -> float:
    try:
        return (dt.datetime.now().timestamp() - os.path.getmtime(SENTINEL)) / 3600
    except OSError:
        return 0.0


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
    rot = rotation()
    state = load()
    done = parse(state.get("done") or "")
    claimed = parse(state.get("claimed") or "")
    notes = []

    if claimed and (not done or claimed > done):
        since = parse(state.get("claimed_at") or "")
        if age_hours(since) < LIVE_HOURS:
            return 1, (f"a cycle is running — claimed {claimed:%Y-%m-%d %H:%M} at "
                       f"{state.get('claimed_at', '?')}"), {}
        resumes = int(state.get("resumes") or 0)
        if resumes >= MAX_RESUMES:
            return 2, (f"the cycle claimed {claimed:%Y-%m-%d %H:%M} has died {resumes + 1} times "
                       "without reporting done — the same fault is recurring; look at the newest "
                       "BUILD and RENDER lines, then --release"), {}
        notes.append(f"resuming the cycle claimed {claimed:%Y-%m-%d %H:%M} at "
                     f"{state.get('claimed_at', '?')}, which never reported done")

    close = newest_close(rot)
    if not close:
        return 2, "no row in the rotation has ever closed", {}
    end, day, jobs = close

    if not notes and done and end <= done:
        # Worded off `done_by`, because "already built" over a close that was skipped is the
        # kind of small untruth a log accumulates until nobody trusts any line in it.
        was = "passed over" if state.get("done_by") == "skipped" else "already built"
        moved = base_moved(str(state.get("done_head") or ""))
        return 1, f"nothing new — newest close {end:%Y-%m-%d %H:%M} (day {day}) {was}{moved}", {}

    if os.path.exists(HOLD):
        return 1, f"held — logs/.hold-cycle is present (day {day} waiting)", {}
    if os.path.exists(SENTINEL):
        if sentinel_age() < LIVE_HOURS and not notes:
            return 1, f"a build is running (logs/.build-in-progress; day {day} waiting)", {}
        notes.append("an earlier build died — this run is its repair")

    flight = in_flight(rot)
    if flight:
        notes.append(f"OSINT has day {', '.join(flight)} open; the catalogue pins the base")

    dirty = dirty_paths()
    if dirty:
        notes.append(f"{len(dirty)} uncommitted tracked file(s), which --claim commits first")

    head = mirror_head()
    tail = "".join(f"; {n}" for n in notes)
    return 0, (f"ready — day {day} closed {end:%Y-%m-%d %H:%M} ({jobs}); OSINT HEAD {head[:12]}"
               f"{tail}"), \
        {"end": end.strftime(TS), "head": head, "day": day, "jobs": jobs, "dirty": dirty,
         "resumed": claimed.strftime(TS) if claimed and notes and notes[0].startswith("resuming")
         else None}


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
            state["resumes"] = 0
            save(state)
            say(f"built through {state['done']} (OSINT {str(state['done_head'])[:12]})")
            return 0

        if args.skip:
            state = load()
            if state.get("claimed"):
                say(f"a claim on {state['claimed']} is outstanding — --release it first")
                return 2
            close = newest_close(rotation())
            if not close:
                say("no row in the rotation has ever closed")
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
            state["resumes"] = 0
            save(state)
            say(f"claim on {was} released — watermark left at {state.get('done')}" if was
                else "no claim outstanding")
            return 0

        code, line, facts = decide()
        say(line)
        if args.claim and code == 0:
            if facts["dirty"]:
                say(f"committed the outstanding work as {commit_outstanding(facts['dirty'])}")
            state = load()
            state["resumes"] = (int(state.get("resumes") or 0) + 1) if facts["resumed"] else 0
            # A resumed run keeps the close it was building; a newer close arrives with it.
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
