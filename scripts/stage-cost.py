#!/usr/bin/env python3
r"""
stage-cost.py — what each stage of a sweep-cycle night costs, from the kept manifests.

**Strategic review 4, register R22.** The mirror's `cycle-manifest.json` is overwritten at
every close, so `osint_lib` keeps a dated copy of each schema-2 manifest it reads under
`logs/manifests/`. This reads those copies and prints, as Markdown, the latest night kept for
each rotation day (`1`, `2`, `B`): points of the weekly limit and of the 5-hour limit spent
per stage, with the night's screening and ingest counts beside them.

**A stage's cost is its reading minus the one before it.** `usage-log.py` writes a reading at
every stage boundary, keyed by the stage just finished, in order; `start` is the baseline.
The weekly figure is a whole percent, so a stage under one point reads 0. The 5-hour window
rolls, so a stage across a roll reads negative and is printed as `roll` rather than as a
number.

Reads only Corpus's own archive; nothing here touches the mirror.

  python scripts/stage-cost.py
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osint_lib  # noqa: E402

DAYS = ("1", "2", "B")


def nights() -> dict:
    """The newest kept schema-2 manifest carrying a `usage` block, per rotation day."""
    found = {}
    for path in sorted(glob.glob(os.path.join(osint_lib.ARCHIVE, "*.json"))):
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        day = (data.get("rotation") or {}).get("newest_close", {}).get("day")
        if day in DAYS and data.get("usage"):
            found[day] = data   # sorted by written_utc, so the last one wins
    return found


def deltas(usage: dict) -> dict:
    """`{stage: (weekly points, 5-hour points or None on a roll)}`, `start` excluded."""
    out, prev = {}, None
    for stage, reading in usage.items():
        if prev is not None:
            week = reading["seven_day"] - prev["seven_day"]
            five = reading["five_hour"] - prev["five_hour"]
            out[stage] = (week, five if five >= 0 else None)
        prev = reading
    return out


def fmt(n) -> str:
    return "roll" if n is None else f"{n:g}"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    found = nights()
    days = [d for d in DAYS if d in found]
    if not days:
        print("No schema-2 manifest with a usage block is kept.", file=sys.stderr)
        return 1
    costs = {d: deltas(found[d]["usage"]) for d in days}
    stages = []   # the fullest night's order first, so the Day B close keeps its place
    for d in sorted(days, key=lambda d: -len(costs[d])):
        stages += [s for s in costs[d] if s not in stages]

    head = [f"Day {d} ({found[d]['rotation']['newest_close']['start'][:10]})" for d in days]
    print("| stage | " + " | ".join(head) + " |")
    print("|---|" + "---|" * len(days))
    for s in stages:
        cells = [f"{fmt(costs[d][s][0])} · {fmt(costs[d][s][1])}" if s in costs[d] else "—"
                 for d in days]
        print(f"| {s} | " + " | ".join(cells) + " |")
    whole = []
    for d in days:
        u = list(found[d]["usage"].values())
        whole.append(f"**{u[-1]['seven_day'] - u[0]['seven_day']:g}**")
    print("| **night, weekly** | " + " | ".join(whole) + " |")
    for key in ("screened", "screen_dropped", "items_in", "admitted", "dropped"):
        print(f"| *{key}* | " + " | ".join(str(found[d]["counts"].get(key, "—"))
                                          for d in days) + " |")
    print("| *duration* | " + " | ".join(found[d]["rotation"]["newest_close"]["duration"]
                                       for d in days) + " |")
    missing = [d for d in DAYS if d not in found]
    if missing:
        print(f"\nNot yet kept: Day {', Day '.join(missing)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
