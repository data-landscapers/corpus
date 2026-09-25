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

**Each cell carries the minutes as well**, from the same readings' timestamps, because the
points alone cannot be read. A stage costing 0 weekly points is either cheap or short, and
those are different facts: `rules` at 0 points in 1 minute says the stage is trivial, while
`backlog` at 0 points in 14 minutes says a job that used its 120-minute cap would not be. The
weekly limit's whole-percent resolution is coarse enough that a one- or two-point reading
carries an error bar as wide as itself, so the minutes are often the more honest number.

**Below the cost table, ingest's drop rate per sweep** *(strategic review 5, R71)*: from each
kept schema-3 manifest whose `drops` block has `ingest_coded`, the share of a sweep's items
that ingest deleted rather than admitted, for the last rotation's nights and pooled across
them. Pooled, not a mean of rates, so a sweep that staged three items does not weigh as much
as one that staged three hundred. A night before OSINT coded its drops (R69) has no rate and
is left out, never read as zero. This is the number review 6 reads.

Reads only Corpus's own archive; nothing here touches the mirror.

  python scripts/stage-cost.py
"""
import datetime
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


def drop_nights() -> list:
    """The last rotation's `drops` blocks with coded ingest drops, oldest first.

    One block per night, the newest manifest carrying it winning, since a later close on the
    same night counts the same batches with more of ingest done. A rotation is the last
    `len(DAYS)` such nights."""
    found = {}
    for path in sorted(glob.glob(os.path.join(osint_lib.ARCHIVE, "*.json"))):
        with open(path, encoding="utf-8") as fh:
            block = json.load(fh).get("drops") or {}
        if block.get("ingest_coded") and block.get("night"):
            found[block["night"]] = block
    return [found[n] for n in sorted(found)][-len(DAYS):]


def rate(dropped: int, admitted: int) -> str:
    total = dropped + admitted
    return f"{100 * dropped / total:.0f}% ({dropped}/{total})" if total else "—"


def print_drops() -> None:
    """Ingest drop rate per sweep per night, and pooled over the rotation."""
    blocks = drop_nights()
    if not blocks:
        print("\nIngest drop rate: no kept manifest carries coded ingest drops yet (R69).")
        return
    sweeps = sorted({s for b in blocks for s in b.get("sweeps", {})})
    rows = {s: [] for s in sweeps + ["all"]}
    pooled = {s: [0, 0] for s in sweeps + ["all"]}
    for b in blocks:
        night = [0, 0]
        for s in sweeps:
            e = b.get("sweeps", {}).get(s)
            if not e or "ingest" not in e:
                rows[s].append("—")
                continue
            n, a = sum(e["ingest"].values()), e.get("admitted", 0)
            rows[s].append(rate(n, a))
            for acc in (pooled[s], night, pooled["all"]):
                acc[0] += n
                acc[1] += a
        rows["all"].append(rate(*night))
    print("\n| ingest drop rate | " + " | ".join(b["night"] for b in blocks) + " | rotation |")
    print("|---|" + "---|" * (len(blocks) + 1))
    for s in sweeps + ["all"]:
        label = "**all sweeps**" if s == "all" else s
        print(f"| {label} | " + " | ".join(rows[s]) + f" | {rate(*pooled[s])} |")


def deltas(usage: dict) -> dict:
    """`{stage: (weekly points, 5-hour points or None on a roll, minutes)}`, no `start`."""
    out, prev = {}, None
    for stage, reading in usage.items():
        if prev is not None:
            week = reading["seven_day"] - prev["seven_day"]
            five = reading["five_hour"] - prev["five_hour"]
            out[stage] = (week, five if five >= 0 else None, minutes(prev, reading))
        prev = reading
    return out


def minutes(before: dict, after: dict):
    """Wall-clock minutes between two readings, or None where either has no timestamp."""
    a, b = before.get("time_utc"), after.get("time_utc")
    if not a or not b:
        return None
    fmt_ = "%Y-%m-%d %H:%M"
    return int((datetime.datetime.strptime(b, fmt_)
                - datetime.datetime.strptime(a, fmt_)).total_seconds() // 60)


def fmt(n) -> str:
    return "roll" if n is None else f"{n:g}"


def cell(cost) -> str:
    week, five, mins = cost
    return f"{fmt(week)} · {fmt(five)}" + ("" if mins is None else f" · {mins}m")


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
        cells = [cell(costs[d][s]) if s in costs[d] else "—" for d in days]
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
    print_drops()
    return 0


if __name__ == "__main__":
    sys.exit(main())
