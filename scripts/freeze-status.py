#!/usr/bin/env python3
r"""freeze-status.py — the process layers are frozen; this says whether the freeze held.

Strategic review task 17. Both process layers are feature-frozen for a month, defect fixes
only, and capacity goes to reports. The review's argument was numeric: 167 commits on
`documentation/` and 159 on `scripts/` in the 21 days to 2026-08-27, against a report layer
that was already the product. The marginal report is worth more than the marginal process
improvement, and the freeze is the largest transfer of capacity available.

**Reporting, not refusing, on the split.** A defect fix is admitted and a script cannot tell
one from a feature; a check that refused process commits would refuse the work the freeze
explicitly allows, and one that argued about which is which would be adjudicating from the
commit message. So the split is measured and printed, in one line, and the rule that decides
what may be committed is in `CLAUDE.md` where a person reads it. What a meter is good for is
making the ratio visible every day rather than at the next review.

**Refusing, on one thing: the freeze outliving its own end date.** A window nobody reads
becomes permanent or is quietly forgotten, and both are worse than a decision. On the day
after `ENDS` this exits 1 and says so, which forces a renew-or-lapse call at the boundary
instead of leaving the freeze to lapse by silence.

Usage:  python scripts/freeze-status.py
        python scripts/freeze-status.py --on 2026-09-28    # for tests
        python scripts/freeze-status.py --root some/repo
Exit:   0 the freeze is running, 1 it has ended and needs a decision, 2 git is unreadable.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Declared 2026-08-28 on the strategic review of 2026-08-27. A month, stated as dates
# rather than a duration: "a month" from an unrecorded start is a freeze with no end.
BEGAN = dt.date(2026, 8, 28)
ENDS = dt.date(2026, 9, 27)

# The two layers, on the review's own definition, because comparability with the number it
# argued from matters more than a finer taxonomy would. `scripts/` is genuinely dual - a
# change to a renderer can be report work - and the review counted it as process anyway;
# splitting it here would make the freeze look better than it is.
PROCESS = ["documentation", "scripts", "BUILD.md", "RENDER.md", "CYCLE.md", "STATUS-INIT.md",
           "PROGRESS-FILLER.md", "BULLETIN-TOPUP.md", "CLAUDE.md"]
REPORT = ["outputs", "site", "content"]


def commits(root: str, paths: list[str], since: dt.date, until: dt.date) -> int:
    """Commits in `since..until` touching any of `paths`. -1 if git will not answer."""
    try:
        out = subprocess.run(
            ["git", "-C", root, "log", "--format=%H",
             f"--since={since:%Y-%m-%d} 00:00", f"--until={until:%Y-%m-%d} 23:59",
             "--", *paths],
            capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return -1
    if out.returncode:
        return -1
    return len([x for x in out.stdout.splitlines() if x.strip()])


def main() -> int:
    ap = argparse.ArgumentParser(description="Whether the process freeze is holding.")
    ap.add_argument("--root", default=ROOT, help="the repo to measure")
    ap.add_argument("--on", default=None, metavar="YYYY-MM-DD",
                    help="the date to report as of (default: today)")
    args = ap.parse_args()

    today = dt.date.today()
    if args.on:
        try:
            today = dt.datetime.strptime(args.on, "%Y-%m-%d").date()
        except ValueError:
            print(f"freeze-status: --on '{args.on}' is not YYYY-MM-DD.")
            return 2

    process = commits(args.root, PROCESS, BEGAN, today)
    report = commits(args.root, REPORT, BEGAN, today)
    if process < 0 or report < 0:
        print(f"freeze-status: git will not read {args.root} - no split available.")
        return 2

    days_in = (today - BEGAN).days + 1
    left = (ENDS - today).days
    total = process + report
    share = f"{100 * process / total:.0f}%" if total else "no commits yet"

    if today > ENDS:
        print(f"freeze-status: the freeze ended {ENDS:%Y-%m-%d}, {(today - ENDS).days} "
              f"day(s) ago. Over its month it took {process} process commit(s) against "
              f"{report} on the report layer ({share} process). Renew it with a new ENDS, "
              f"or let it lapse - but say which, because a window nobody closes is a rule "
              f"nobody keeps.")
        return 1

    print(f"freeze-status: day {days_in} of the freeze, {left} to go (ends "
          f"{ENDS:%Y-%m-%d}). {process} process commit(s), {report} report ({share} "
          f"process). Defect fixes only - CLAUDE.md -> The freeze.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
