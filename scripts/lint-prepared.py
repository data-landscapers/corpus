#!/usr/bin/env python3
r"""lint-prepared.py — handed-over work leaves the share when the job that wanted it closes.

    python scripts/lint-prepared.py
    python scripts/lint-prepared.py --share some/other/dir   # for tests

`prepared/` is work CORPUS hands OSINT ready to run: a patch series, or a script with its
input, with a `BRIEF.md` saying what it does. OSINT checks it and applies it itself. The
share's `README.md` said all of that and then stopped, so **nothing had ever been deleted
from `prepared/` since the repository began on 2026-08-20** — by 2026-09-20 it held 5.3 MB
across 33 items, every one of them spent. This is what stops that happening again.

**The rule is the notes rule, applied to a folder**: when the job that wanted the handover
closes, the handover goes, in the commit that records the close. Deleted rather than
archived — git holds every byte, and the register's done-note is the account of what the job
did. A numbered note is archived because a closed number still has to resolve for anything
citing it; a spent patch series has no such reader.

**CORPUS prunes, and it can tell without asking.** The closure signal lives in the share
itself — `housekeeping-jobs-resolved.md` for a job, the strategic review register for an
R-line, the `-drops-absorbed-` rename for an acquisition drop list — so establishing that a
handover is spent needs no OSINT process file and stays inside the interface. That is the
whole reason this is CORPUS's chore and not OSINT's.

What it resolves, and how:

- **`job-NN`, `job-NN-MM`** — every number in the name is looked up in the housekeeping
  registers. Spent when all of them are struck to the resolved file and none is still open.
- **`status-acquire-{ISO3}-drops-absorbed-*.csv`** — spent by its own name: `status-acquire.md`
  defines that rename as what OSINT does when the close absorbs the list. A `…-drops.csv`
  that has *not* been renamed is live and is left alone.
- **Anything else** — read `Closed by:` from its `BRIEF.md` (its own, or a sibling for a bare
  file) and resolve `job NN` against the housekeeping registers or `RNN` against the review
  register. **An item that names no closer is reported, not failed**: this cannot tell a
  handover nobody has got to from one whose closer was never written down, and guessing in
  either direction is worse than saying so.

Exit: 0 nothing spent is sitting there, 1 something spent is (the prune is owed), 2 no share.
"""
from __future__ import annotations

import argparse
import io
import os
import re
import sys

SHARE = os.environ.get("CORPUS_OSINT_XFER", r"C:\corpus-osint-xfer")

HOUSEKEEPING = "housekeeping-jobs.md"
RESOLVED = "housekeeping-jobs-resolved.md"
REGISTER = "strategic-review-register.md"

JOB_DIR = re.compile(r"^job-(\d+(?:-\d+)*)$")
DROPS_ABSORBED = re.compile(r"^status-acquire-[A-Z]{3}-drops-absorbed-\d{4}-\d{2}-\d{2}\.csv$")
DROPS_LIVE = re.compile(r"^status-acquire-[A-Z]{3}-drops\.csv$")
CLOSED_BY = re.compile(r"^\s*(?:\*\*)?Closed by:(?:\*\*)?\s*(.+?)\s*$", re.M | re.I)
REF_JOB = re.compile(r"\bjob\s*#?\s*(\d+)\b", re.I)
REF_R = re.compile(r"\bR(\d+[a-zA-Z]?)\b")


def _read(path: str) -> str:
    try:
        return io.open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def job_state(num: str, open_src: str, resolved_src: str) -> str:
    """`closed`, `open` or `unknown` for one housekeeping job number.

    The registers mark a struck job with an `x` prefix at the head of its line and leave the
    number alone, so the two tests are `^xNN.` in the resolved file and `^NN.` in the open
    one. Both are checked rather than one: a job present in neither is `unknown`, and an
    unknown is not the same as a closed one."""
    closed = re.search(rf"^x{num}\.\s", resolved_src, re.M) is not None
    still_open = re.search(rf"^{num}\.\s", open_src, re.M) is not None
    if still_open:
        return "open"
    return "closed" if closed else "unknown"


def r_state(ref: str, register_src: str) -> str:
    """`closed`, `open` or `unknown` for one review-register R-line."""
    if re.search(rf"^- \[x\] \*\*R{ref}\b", register_src, re.M | re.I):
        return "closed"
    if re.search(rf"^- \[ \] \*\*R{ref}\b", register_src, re.M | re.I):
        return "open"
    return "unknown"


def closer_of(path: str, share: str) -> str:
    """The `Closed by:` line of an item's brief, or an empty string.

    A folder carries its own `BRIEF.md`. A bare file handed over on its own — a JSONL batch,
    a drop list — has no folder to put one in, so a `BRIEF.md` sitting beside it in
    `prepared/` is read instead; that is the only place a bare file's closer can live."""
    for candidate in (os.path.join(path, "BRIEF.md"),
                      os.path.join(share, "prepared", "BRIEF.md")):
        m = CLOSED_BY.search(_read(candidate))
        if m:
            return m.group(1).strip()
    return ""


def verdict(name: str, path: str, share: str, src: dict) -> tuple[str, str]:
    """`(state, why)` for one entry in `prepared/`. State is spent, live or unresolved."""
    if DROPS_ABSORBED.match(name):
        return "spent", "renamed `-drops-absorbed-`, which is what OSINT's close does to it"
    if DROPS_LIVE.match(name):
        return "live", "an acquisition drop list not yet absorbed"

    m = JOB_DIR.match(name)
    if m:
        nums = m.group(1).split("-")
        states = {n: job_state(n, src["open"], src["resolved"]) for n in nums}
        if all(v == "closed" for v in states.values()):
            return "spent", "housekeeping job(s) " + ", ".join(nums) + " closed"
        openish = [n for n, v in states.items() if v == "open"]
        if openish:
            return "live", "housekeeping job(s) " + ", ".join(openish) + " still open"
        return "unresolved", ("housekeeping job(s) "
                              + ", ".join(n for n, v in states.items() if v == "unknown")
                              + " are in neither register")

    closer = closer_of(path, share)
    if not closer:
        return "unresolved", ("no `Closed by:` in a brief. Name the job or review line that "
                              "retires it, so a later run can tell spent from waiting")
    jm, rm = REF_JOB.search(closer), REF_R.search(closer)
    if jm:
        s = job_state(jm.group(1), src["open"], src["resolved"])
        return ({"closed": "spent", "open": "live"}.get(s, "unresolved"),
                f"brief says closed by housekeeping job {jm.group(1)}, which is {s}")
    if rm:
        s = r_state(rm.group(1), src["register"])
        return ({"closed": "spent", "open": "live"}.get(s, "unresolved"),
                f"brief says closed by review line R{rm.group(1)}, which is {s}")
    return "unresolved", f"`Closed by: {closer}` names neither a job number nor an R-line"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Spent handovers do not sit in the share.")
    ap.add_argument("--share", default=SHARE, help="the exchange folder")
    a = ap.parse_args(argv)

    if not os.path.isdir(a.share):
        print(f"lint-prepared: the share is not at {a.share}. Set CORPUS_OSINT_XFER or "
              f"pass --share.")
        return 2
    prepared = os.path.join(a.share, "prepared")
    if not os.path.isdir(prepared):
        print("lint-prepared: ok - no prepared/ folder, so nothing is waiting in it.")
        return 0

    src = {"open": _read(os.path.join(a.share, HOUSEKEEPING)),
           "resolved": _read(os.path.join(a.share, RESOLVED)),
           "register": _read(os.path.join(a.share, REGISTER))}

    spent, live, unresolved = [], [], []
    for name in sorted(os.listdir(prepared)):
        if name == "BRIEF.md":
            continue
        path = os.path.join(prepared, name)
        state, why = verdict(name, path, a.share, src)
        {"spent": spent, "live": live, "unresolved": unresolved}[state].append((name, why))

    for name, why in unresolved:
        print(f"lint-prepared: note - {name}: {why}.")
    for name, why in live:
        print(f"lint-prepared: waiting - {name}: {why}.")
    for name, why in spent:
        print(f"lint-prepared: FAIL - {name} is spent ({why}) and is still in the share. "
              f"Delete it in the commit that records the close - git holds it.")
    if spent:
        print(f"lint-prepared: {len(spent)} spent item(s) to prune, {len(live)} waiting, "
              f"{len(unresolved)} unresolved.")
        return 1
    print(f"lint-prepared: ok - nothing spent in prepared/; {len(live)} waiting, "
          f"{len(unresolved)} unresolved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
