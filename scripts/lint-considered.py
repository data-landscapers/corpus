#!/usr/bin/env python3
r"""lint-considered.py — evidence read, marked, and left no trace.

    python scripts/lint-considered.py            # every unit
    python scripts/lint-considered.py --unit BEN # one
    python scripts/lint-considered.py --json

**The finding is one sentence: a source the ledger has marked considered, whose
indicator the progress report calls ***No evidence***, and which no ledger row
cites.** Stage 4 read it, decided nothing, and marked it — and `BUILD.md` step 200
says an item already considered is never reopened, so the mark is what makes the
loss permanent. The report then publishes *the base holds nothing on this
indicator at all* over a base that holds a document answering it.

It returned **467 rows over 22 units** the day it was written *(2026-09-10,
`documentation/considered-not-carried.md`)*. Nothing else in the estate could see
them. That is the whole argument for this file.

**Why no existing check finds it.** Checks G, I, J, L and M all test the frame
against the ledger, and `report-render.py`'s check I asserts *No evidence* iff no
row maps to the indicator — which is *true* in every one of these cases, and is
why the run that created them passed. **The frame is consistent with a ledger that
is missing the evidence**, and consistency with the ledger is the only property
anything downstream tests. The missing axis is the one this file adds: the ledger
against the sources it has already claimed to have read.

**It needs no model and no catalogue.** Four files per unit, all of them Corpus's
own — the report, `considered.txt`, `ledger.csv`, and the filler manifest in
`logs/progress-filler/` that names which indicator each staged document was found
for. That last file is what makes the check decidable: without it, "this source
would have answered that indicator" is a judgement, and with it the pairing is
recorded by the pass that made it.

**Run it at the end of stage 4, per unit.** A finding here is not advisory — it
means the run has just discarded evidence it will never see again, and the repair
is to reopen those slugs before the run ends rather than to note it.

Exit 1 on any finding, 0 on none. The `--json` shape is `{unit: [{indicator,
slug}]}` for a caller that wants to do the reopening itself.
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
REPORTS = CORPUS / "outputs" / "reports"
FILLER = CORPUS / "logs" / "progress-filler"
NO_EVIDENCE = "No evidence"


def frame_pairs():
    """`(Topic, Progress indicator) -> indicator_id`, the frame's own spine."""
    rows = csv.DictReader((CORPUS / "lookups" / "indicators.csv").read_text(
        encoding="utf-8-sig").splitlines())
    return {(r["Topic"], r["Progress indicator"]): r["indicator_id"] for r in rows}


def no_evidence(md_path: Path, pairs) -> set[str]:
    """The indicators this report answers with ***No evidence***.

    Read off the published table rather than `indicators.csv`, for the reason the
    progress pages are: the table is what a reader is told, and an absent row in
    `indicators.csv` is the same thing said by omission."""
    lines = md_path.read_text(encoding="utf-8").split("\n")
    i, out = 0, set()
    while i < len(lines) - 1:
        rule = lines[i + 1].strip().strip("|").replace("|", "")
        if lines[i].startswith("|") and rule and set(rule) <= set("-: "):
            head = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            i += 2
            if head[-1] == "Progress":
                while i < len(lines) and lines[i].startswith("|"):
                    c = [x.strip() for x in lines[i].strip().strip("|").split("|")]
                    if c[-1].split(",")[0].strip().strip("*") == NO_EVIDENCE:
                        key = pairs.get((c[0], c[1]))
                        if key:
                            out.add(key)
                    i += 1
            continue
        i += 1
    return out


def cited(ledger: Path) -> set[str]:
    """Every source slug any row of the ledger stands on."""
    if not ledger.exists():
        return set()
    out = set()
    for r in csv.DictReader(ledger.read_text(encoding="utf-8-sig").splitlines()):
        for s in (r.get("sources") or "").replace(";", "|").split("|"):
            if s.strip():
                out.add(s.strip())
    return out


def staged(iso: str):
    """`(indicator_id, slug)` from the unit's filler manifests.

    Two header shapes are in the wild — `staged_file` on three units and `file` on
    the rest — and both are read rather than one being normalised, because the
    manifests are a written record of a pass that has been archived and rewriting
    them would be editing evidence."""
    for path in sorted(FILLER.glob(f"{iso}-*-selected.csv")):
        for r in csv.DictReader(path.read_text(encoding="utf-8-sig").splitlines()):
            iid = (r.get("indicator_id") or "").strip()
            f = (r.get("staged_file") or r.get("file") or "").strip()
            if iid and f:
                yield iid, os.path.basename(f)[:-3] if f.endswith(".md") else os.path.basename(f)


def audit(units=None):
    pairs = frame_pairs()
    found = defaultdict(list)
    for md in sorted(REPORTS.glob("*/*-progress.md")):
        iso = md.parent.name
        if units and iso not in units:
            continue
        empty = no_evidence(md, pairs)
        if not empty:
            continue
        marks = set()
        cpath = md.parent / "considered.txt"
        if cpath.exists():
            marks = {l.strip() for l in cpath.read_text(encoding="utf-8").splitlines() if l.strip()}
        used = cited(md.parent / "ledger.csv")
        seen = set()
        for iid, slug in staged(iso):
            if iid in empty and slug in marks and slug not in used and (iid, slug) not in seen:
                seen.add((iid, slug))
                found[iso].append({"indicator": iid, "slug": slug})
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", action="append", help="limit to this unit; repeatable")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    found = audit(set(args.unit) if args.unit else None)
    if args.json:
        print(json.dumps(found, indent=2, sort_keys=True))
        return 1 if found else 0

    if not found:
        print("lint-considered: ok — no source is marked considered over an indicator "
              "the report calls No evidence.")
        return 0

    rows = sum(len(v) for v in found.values())
    inds = sum(len({d["indicator"] for d in v}) for v in found.values())
    print(f"lint-considered: {rows} source(s) read, marked and left no trace, over "
          f"{inds} indicator(s) reporting No evidence, in {len(found)} unit(s).")
    print("  The mark is why nothing will read them again (BUILD.md stage 4, step 4).")
    for iso in sorted(found, key=lambda k: -len(found[k])):
        v = found[iso]
        print(f"  {iso}: {len(v)} source(s) over {len({d['indicator'] for d in v})} indicator(s)")
        for d in sorted(v, key=lambda d: d["indicator"])[:3]:
            print(f"      {d['indicator']}  <-  {d['slug']}")
        if len(v) > 3:
            print(f"      … and {len(v) - 3} more")
    print("\n  Repair: reopen these slugs in the unit's considered.txt and re-read them "
          "under\n  BUILD.md stage 4 step 2 as corrected on 2026-09-10 — a source "
          "establishing a\n  standing position the ledger lacks mints a row, it does not "
          "default to nothing.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
