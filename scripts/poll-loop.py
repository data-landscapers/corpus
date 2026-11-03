#!/usr/bin/env python3
r"""poll-loop.py — the poll: watch for a closed sweep cycle and open a Claude session to build it.

*(Bill, 2026-10-29.)* Replaces arming `/poll` by hand. It runs in the `CORPUS-POLL` terminal
tab, which starts it, and ticks every half hour from 22:00 to 06:00. **A tick costs no model
turn**: the checks are scripts, and a tick that finds nothing prints one line. Claude is
opened only for work, in a new tab:

- **a close to build** — `osint-cycle-ready.py --claim` exit 0 — runs `/cycle`;
- **a deploy block owed or spent** — `deploy-state.py --fix` exit 2 with no block quoting
  its line, or exit 0 with a `· deploy` block still open — runs `/poll-alert deploy`;
- **a critical error** — `--claim` exit 2 — runs `/poll-alert critical` and stops the loop,
  the one thing that does.

Each tick also runs `traffic.py pull`, which keeps Cloudflare's request log; it needs no turn.

A cycle already running reads as exit 1 while its claim is younger than the trigger's
`LIVE_HOURS`, so a tick beside it is a quiet one. What the alert prompt needs to quote goes
in `ALERT`, outside the repository.

**A night's hours can be moved** *(Bill, 2026-11-03)*: a row in `lookups/poll-window.csv`
(`night`, the date the evening falls on; `start`; `stop`; `reason`) replaces 22:00-06:00 for
that night only. The file is read at every tick and every pause, so an edit needs no restart
of a loop running this version. A night with no row keeps the default.

Usage:  python scripts/poll-loop.py               # in the CORPUS-POLL tab
        python scripts/poll-loop.py --once        # one tick now, whatever the hour, then stop
        python scripts/poll-loop.py --interval 15
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import re
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARE = os.environ.get("CORPUS_OSINT_XFER", r"C:\corpus-osint-xfer")
MESSAGES = os.path.join(SHARE, "messages-for-bill.md")
ALERT = os.path.join(tempfile.gettempdir(), "corpus-poll-alert.txt")

# The window: ticks run from START to STOP, across midnight (Bill, 2026-10-29). Outside it
# the machine is Bill's, and a close waits for the night. WINDOWS moves one night's hours.
START, STOP = dt.time(22, 0), dt.time(6, 0)
WINDOWS = os.path.join(ROOT, "lookups", "poll-window.csv")

DEPLOY_BLOCK = re.compile(r"^## \d+ · .* · deploy\s*$", re.M)


def run(*args: str) -> tuple[int, str]:
    p = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout + p.stderr).strip()


def night(day: dt.date) -> tuple[dt.datetime, dt.datetime]:
    """The window of the night that begins on `day`: its row in WINDOWS, else the default.
    A stop at or before the start is the next morning's."""
    start, stop = START, STOP
    try:
        with open(WINDOWS, encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                if r.get("night", "").strip() == day.isoformat():
                    start = dt.time.fromisoformat(r["start"].strip())
                    stop = dt.time.fromisoformat(r["stop"].strip())
    except (OSError, ValueError, KeyError) as e:
        print(f"poll: {WINDOWS} unreadable ({e}); default hours", flush=True)
    a = dt.datetime.combine(day, start)
    b = dt.datetime.combine(day if stop > start else day + dt.timedelta(days=1), stop)
    return a, b


def in_window(now: dt.datetime) -> bool:
    return any(a <= now < b for a, b in (night(now.date() - dt.timedelta(days=1)), night(now.date())))


def open_claude(title: str, prompt: str) -> None:
    """A new tab in the main Terminal window, running an interactive session on `prompt`.

    The session name carries the start time, so /resume tells one night's cycle from another."""
    name = f"{title.lower()}-{dt.datetime.now():%m%d-%H%M}"
    subprocess.Popen(["wt.exe", "-w", "main", "new-tab", "--title", title, "-d", ROOT,
                      "pwsh", "-NoExit", "-Command",
                      f"claude -n {name} --dangerously-skip-permissions '{prompt}'"])


def alert(kind: str, line: str) -> None:
    with open(ALERT, "w", encoding="utf-8") as fh:
        fh.write(line + "\n")
    open_claude("CORPUS-ALERT", f"/poll-alert {kind}")


def deploy_messages() -> str:
    try:
        with open(MESSAGES, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def tick() -> tuple[str, bool]:
    """One poll. Returns the line to print and whether the loop goes on."""
    code, line = run("scripts/deploy-state.py", "--fix", "--quiet")
    text = deploy_messages()
    if code == 2 and line and line not in text:
        alert("deploy", line)
        note = " · deploy stuck, alert opened"
    elif code == 0 and DEPLOY_BLOCK.search(text):
        alert("deploy-cleared", "")
        note = " · deploy cleared, alert opened"
    else:
        note = ""

    # The site's request log: a complete day not yet held is pulled, which the night's first
    # tick does; every later tick finds it held and costs nothing. Its trouble is a note, not a stop.
    _, traffic = run("scripts/traffic.py", "pull", "--quiet")
    if traffic:
        note += f" · {traffic.splitlines()[-1]}"

    code, out = run("scripts/osint-cycle-ready.py", "--claim")
    first = out.splitlines()[0] if out else ""
    if code == 0:
        open_claude("CORPUS-CYCLE", "/cycle")
        return f"cycle started in a new tab — {first}{note}", True
    if code == 2:
        alert("critical", out)
        return f"critical, poll stopped — {first}{note}", False
    _, gates = run("scripts/corpus-status.py", "--gates")
    gates = " · ".join(l.strip() for l in gates.splitlines() if l.strip())
    return "nothing to do" + (f" · {gates}" if gates else "") + note, True


def next_slot(now: dt.datetime, minutes: int) -> dt.datetime:
    """The next tick on the interval's grid, moved to the next night's start if it falls outside."""
    t = now.replace(second=0, microsecond=0)
    t += dt.timedelta(minutes=minutes - t.minute % minutes)
    if not in_window(t):
        t = min(a for a, _ in (night(now.date()), night(now.date() + dt.timedelta(days=1))) if a > now)
    return t


def main() -> int:
    ap = argparse.ArgumentParser(description="The poll: build each closed sweep cycle.")
    ap.add_argument("--interval", type=int, default=30, help="minutes between ticks")
    ap.add_argument("--once", action="store_true", help="one tick, then stop")
    args = ap.parse_args()
    a, b = night(dt.date.today())
    print(f"poll: every {args.interval} min, tonight {a:%H:%M}-{b:%H:%M} "
          f"(default {START:%H:%M}-{STOP:%H:%M}). Ctrl+C stops it.")
    now = dt.datetime.now()
    when = now if args.once or in_window(now) else next_slot(now, args.interval)
    announced = None
    while True:
        wait = (when - dt.datetime.now()).total_seconds()
        if wait > 0:
            if wait > (args.interval + 1) * 60:
                if announced != when:
                    print(f"{dt.datetime.now():%H:%M}  paused until {when:%H:%M}", flush=True)
                    announced = when
                # A long pause wakes every five minutes to re-read the night's hours, so an
                # edit to poll-window.csv moves it without a restart.
                time.sleep(min(wait, 300))
                now = dt.datetime.now()
                new = now if in_window(now) else next_slot(now, args.interval)
                when = new
                continue
            time.sleep(wait)
        line, going = tick()
        print(f"{dt.datetime.now():%H:%M}  {line}", flush=True)
        if args.once or not going:
            return 0 if going else 2
        when = next_slot(dt.datetime.now(), args.interval)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\npoll: stopped")
        sys.exit(0)
