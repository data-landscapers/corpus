#!/usr/bin/env python3
r"""
lint-mirror-freshness.py — is the backup of record actually current?

`RENDER.md` -> *Mirror* carried this as owed and unbuilt (2026-08-16). All backups are
Corpus's now: OSINT runs none, and its own `LINT` #19 retires with its mirror
(`documentation/osint-migration.md` R8). #19 existed because the mirror once went a week
stale in silence, and it was the only automated guard either repo has ever had. One
`mirror.bat` now covers **both** repos, so a silent lapse loses both at once — and what
replaced #19 was a line of prose asking a human to eyeball a timestamp, in the same
breath as explaining that `mirror.bat`'s exit code cannot be trusted.

**Why the exit code cannot be trusted, which is the whole reason this reads a log.**
Run as a bare `mirror.bat` from a shell not sitting in the repo root, or with the
backslashes eaten by bash, `cmd` consumes no command, opens an interactive shell and
exits **0** having backed up nothing (`RENDER.md`, 2026-08-14). A green exit is not
evidence. The dated line in `logs/mirror_log.md` is, because only a run that reached the
end writes one.

**Three ways the backup can be stale, and this checks all three.**

  1. **The newest run recorded `FAIL`.** A fresh line is not a good line: `mirror.bat`
     writes one whatever happened, and a leg that failed still stamps the time.
  2. **The mirror is older than the newest render.** RENDER is the last job in the
     pipeline and mirroring is its final step, so a mirror older than the last render
     means the render's own artefacts are not backed up.
  3. **The mirror is simply old.** Checks 1 and 2 both compare against *something having
     happened*. A quiet fortnight with no render passes them both while the backup ages,
     which is precisely the week-of-silence #19 was written for. `--max-age-hours`
     (default 72) is the floor under that, and it is the check that fires when nothing
     else is moving.

Committed work newer than the mirror is **reported, not gated**. It is the true measure
of exposure — a commit is work that exists only here until a mirror leg copies it — but
it goes stale the moment anyone commits, and a check that fails all the way through an
ordinary working session is a check that gets ignored.

**Reports, never fixes.** Firing a `/MIR` is Bill's: `mirror.bat` mirrors *onto* the
Dropbox copies, so running it is a destructive write on the destination, and a script
that decided that for itself would be making a backup policy decision on its own
authority. This prints what it found and returns a code.

Usage:  python scripts/lint-mirror-freshness.py [--quiet] [--max-age-hours N]
Exit:   0 clean, 1 stale or failed, 2 nothing recorded to judge against.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR_LOG = os.path.join(ROOT, "logs", "mirror_log.md")
RUN_LOG = os.path.join(ROOT, "logs", "log.md")

# `- **2026-08-16 12:54** - ok - osint(robocopy=3 bundle=0) corpus(...) ffs=0`
MIRROR_RE = re.compile(r"^-\s+\*\*(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\*\*\s*-\s*(\S+)\s*-\s*(.*)$")
# `2026-08-16 12:50 · render · ...`
RUN_RE = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\s+·\s+(\w[\w-]*)\s+·")

DEFAULT_MAX_AGE_HOURS = 72


def parse(ts: str) -> dt.datetime:
    return dt.datetime.strptime(ts, "%Y-%m-%d %H:%M")


def newest_mirror() -> tuple[dt.datetime, str, str] | None:
    """The newest mirror line, whatever its status.

    Newest by *timestamp*, not by position: the log has read newest-first since
    2026-08-16 and was append-ordered before that, so no fixed end of the file is the
    right one to trust across its own history — and a hand-edit or a merge could reorder
    it either way. Taking a position on faith would read an older run as current, which
    is the one direction of error that matters here. Because this sorts, the flip of
    2026-08-16 needed no change to it."""
    if not os.path.exists(MIRROR_LOG):
        return None
    best = None
    with open(MIRROR_LOG, encoding="utf-8") as fh:
        for line in fh:
            m = MIRROR_RE.match(line.strip())
            if not m:
                continue
            when = parse(m.group(1))
            if best is None or when > best[0]:
                best = (when, m.group(2), m.group(3))
    return best


def newest_run(pass_name: str) -> dt.datetime | None:
    """The newest `· {pass} ·` line in logs/log.md."""
    if not os.path.exists(RUN_LOG):
        return None
    best = None
    with open(RUN_LOG, encoding="utf-8") as fh:
        for line in fh:
            m = RUN_RE.match(line.strip())
            if m and m.group(2) == pass_name:
                when = parse(m.group(1))
                if best is None or when > best:
                    best = when
    return best


def commits_since(when: dt.datetime) -> int | None:
    """How many commits landed after the mirror ran. None if git cannot answer."""
    try:
        out = subprocess.run(
            ["git", "-C", ROOT, "log", "--since", when.strftime("%Y-%m-%d %H:%M:%S"),
             "--oneline"],
            capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return len([ln for ln in out.stdout.splitlines() if ln.strip()])


def humanise(delta: dt.timedelta) -> str:
    hours = delta.total_seconds() / 3600
    if hours < 48:
        return f"{hours:.1f}h"
    return f"{hours / 24:.1f} days"


def main() -> int:
    ap = argparse.ArgumentParser(description="Mirror freshness — reports, never fixes.")
    ap.add_argument("--quiet", action="store_true", help="print nothing when clean")
    ap.add_argument("--max-age-hours", type=float, default=DEFAULT_MAX_AGE_HOURS,
                    help=f"stale beyond this many hours (default {DEFAULT_MAX_AGE_HOURS})")
    args = ap.parse_args()

    newest = newest_mirror()
    if newest is None:
        print("mirror freshness: NO MIRROR RECORDED - logs/mirror_log.md is missing, "
              "empty, or in an unexpected shape.")
        print("  Nothing here can say whether either repo is backed up. Run "
              "`& cmd /c \"C:\\CORPUS\\mirror.bat\"` from PowerShell.")
        return 2

    when, status, detail = newest
    now = dt.datetime.now()
    age = now - when
    render = newest_run("render")

    faults: list[str] = []

    if status.lower() != "ok":
        faults.append(f"the newest run recorded {status} - {detail}")

    if render is not None and when < render:
        faults.append(f"older than the newest render ({render:%Y-%m-%d %H:%M}), so that "
                      f"render's artefacts are not in the backup")

    if age.total_seconds() / 3600 > args.max_age_hours:
        faults.append(f"{humanise(age)} old, past the {args.max_age_hours:g}h ceiling")

    commits = commits_since(when)
    exposure = ""
    if commits:
        exposure = (f"  {commits} commit(s) have landed since - work that exists only on "
                    f"this machine until a mirror leg copies it.")

    if faults:
        print(f"mirror freshness: STALE - last run {when:%Y-%m-%d %H:%M} ({humanise(age)} ago)")
        for f in faults:
            print(f"  - {f}")
        if exposure:
            print(exposure)
        print("  Fix: `& cmd /c \"C:\\CORPUS\\mirror.bat\"` from PowerShell, then check "
              "logs/mirror_log.md carries a fresh line - the exit code cannot be trusted.")
        return 1

    if not args.quiet:
        against = f", newer than the last render {render:%Y-%m-%d %H:%M}" if render else ""
        print(f"mirror freshness: ok - last run {when:%Y-%m-%d %H:%M} "
              f"({humanise(age)} ago){against}")
        if exposure:
            print(exposure)
    return 0


if __name__ == "__main__":
    sys.exit(main())
