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

A cycle already running reads as exit 1 while its claim is younger than the trigger's
`LIVE_HOURS`, so a tick beside it is a quiet one. What the alert prompt needs to quote goes
in `ALERT`, outside the repository.

Usage:  python scripts/poll-loop.py               # in the CORPUS-POLL tab
        python scripts/poll-loop.py --once        # one tick, then stop
        python scripts/poll-loop.py --interval 15
"""
from __future__ import annotations

import argparse
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
# the machine is Bill's, and a close waits for the night.
START, STOP = dt.time(22, 0), dt.time(6, 0)

DEPLOY_BLOCK = re.compile(r"^## \d+ · .* · deploy\s*$", re.M)


def run(*args: str) -> tuple[int, str]:
    p = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout + p.stderr).strip()


def in_window(t: dt.time) -> bool:
    return t >= START or t < STOP


def open_claude(title: str, prompt: str) -> None:
    """A new tab in the main Terminal window, running an interactive session on `prompt`."""
    subprocess.Popen(["wt.exe", "-w", "main", "new-tab", "--title", title, "-d", ROOT,
                      "pwsh", "-NoExit", "-Command",
                      f"claude -n {title.lower()} --dangerously-skip-permissions '{prompt}'"])


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
    """The next tick on the interval's grid, moved to START if it falls outside the window."""
    t = now.replace(second=0, microsecond=0)
    t += dt.timedelta(minutes=minutes - t.minute % minutes)
    if not in_window(t.time()):
        t = t.replace(hour=START.hour, minute=START.minute)
    return t


def main() -> int:
    ap = argparse.ArgumentParser(description="The poll: build each closed sweep cycle.")
    ap.add_argument("--interval", type=int, default=30, help="minutes between ticks")
    ap.add_argument("--once", action="store_true", help="one tick, then stop")
    args = ap.parse_args()
    print(f"poll: every {args.interval} min, {START:%H:%M}-{STOP:%H:%M}. Ctrl+C stops it.")
    now = dt.datetime.now()
    when = now if in_window(now.time()) else next_slot(now, args.interval)
    while True:
        wait = (when - dt.datetime.now()).total_seconds()
        if wait > 0:
            if wait > (args.interval + 1) * 60:
                print(f"{dt.datetime.now():%H:%M}  paused until {when:%H:%M}", flush=True)
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
