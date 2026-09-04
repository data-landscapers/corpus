#!/usr/bin/env python3
"""Gap list for the progress filler — documentation/archived/PROGRESS-FILLER.md sec 1.

The gap set is a set difference: every indicator_id in the frame
(lookups/indicators.csv) that is absent from a unit's held view
(outputs/reports/{ISO}/indicators.csv), or present there with a blank
`progress` — the renderer treats a blank as *No evidence* too, so a held
row with nothing in that column is a gap the plain difference would miss.

Read-only. Prints one row per gap: indicator_id, Topic L1, Topic, Topic L2,
Progress indicator — the fields the briefs at sec 2 compose from and the
grouping at sec 6 batches by.

    python scripts/progress-filler-gaps.py AGO [--csv out.csv] [--counts]
"""
import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRAME = ROOT / "lookups" / "indicators.csv"
FIELDS = ["indicator_id", "Topic L1", "Topic", "Topic L2", "Progress indicator"]


def gaps(iso):
    held = {}
    path = ROOT / "outputs" / "reports" / iso / "indicators.csv"
    if path.exists():
        with path.open(encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                held[row["indicator_id"]] = (row.get("progress") or "").strip()
    with FRAME.open(encoding="utf-8-sig", newline="") as fh:
        frame = list(csv.DictReader(fh))
    out = [r for r in frame if not held.get(r["indicator_id"])]
    return frame, held, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("iso")
    ap.add_argument("--csv", help="write the gap list to this path")
    ap.add_argument("--counts", action="store_true", help="frame/held/gap counts only")
    args = ap.parse_args()
    iso = args.iso.upper()

    frame, held, out = gaps(iso)
    if args.counts:
        print(f"{iso}: frame {len(frame)}, held {len([v for v in held.values() if v])}, gaps {len(out)}")
        return
    rows = [{k: r[k] for k in FIELDS} for r in out]
    if args.csv:
        with open(args.csv, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
        print(f"{len(rows)} gaps -> {args.csv}")
    else:
        w = csv.DictWriter(sys.stdout, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
